import dataclasses
import functools

from heracles import config, ql
from heracles.config.rule import RealizedAlert
from heracles.ql import annotation


@dataclasses.dataclass
class ConstLabelContext(
    config.RuleContext, config.AfterRealizeHookMixin[config.RealizedRule]
):
    def __init__(
        self,
        **labels: str,
    ) -> None:
        super().__init__()
        self.labels = labels

    def after_realize(
        self, bundle: config.BundleReference, rule: config.RealizedRule
    ) -> None:
        for name, value in self.labels.items():
            if not rule.labels:
                rule.labels = {name: value}
            elif name not in rule.labels:
                rule.labels[name] = value


@dataclasses.dataclass
class ServiceContext(ConstLabelContext):
    def __init__(
        self, service_name: str, expected_count: ql.ConstantOrVector | None = None
    ) -> None:
        super().__init__(service=service_name)
        self._set_contextvars(service_name=service_name, expected_count=expected_count)


class AlertForMissingData(
    config.RuleContext, config.AfterRealizeHookMixin[RealizedAlert]
):
    def after_realize(
        self, bundle: config.BundleReference, rule: config.RealizedAlert
    ) -> None:
        bundle.add_realized_alert(self._make_data_missing_alert(rule))

    def _make_data_missing_alert(
        self, rule: config.RealizedAlert
    ) -> config.RealizedAlert:
        selected_vecs = []

        def visitor(t: ql.SelectedInstantVector) -> None:
            selected_vecs.append(t.without_annotations())

        rule.expr.accept_visitor(visitor)

        meta_expr = functools.reduce(
            lambda x, y: x.or_(y),  # type: ignore
            [ql.absent(vec) for vec in selected_vecs],  # type: ignore
        )

        return config.RealizedAlert(
            name=rule.name + "DataMissing",
            raw_expr=meta_expr,
            labels=rule.labels,
            annotations=rule.annotations,
        )


class AlertsForAssertions(config.RuleContext):
    def after_realize(
        self, bundle: config.BundleReference, rule: config.RealizedAlert
    ) -> None:
        result = self._make_rule_from_annotations(rule)
        if result:
            bundle.add_realized_alert(result)

    def _make_rule_from_annotations(
        self,
        r: config.RealizedAlert,
    ) -> config.RealizedAlert | None:
        annotations = self._get_assertions(r)
        if not annotations:
            return None
        expr = functools.reduce(
            lambda x, y: x.or_(y), [a.assertion() for a in annotations]
        )

        return config.RealizedAlert(
            name=r.name + "InvalidData",
            raw_expr=expr,
            labels=r.labels,
            annotations=r.annotations,
        )

    def _get_assertions(
        self, r: config.RealizedAlert
    ) -> list[annotation.AssertionAnnotation]:
        annotations: list[annotation.AssertionAnnotation] = []

        def visitor(t: ql.Timeseries) -> None:
            if t.annotations:
                annotations.extend(
                    a
                    for a in t.annotations
                    if isinstance(a, annotation.AssertionAnnotation)
                )

        r.expr.accept_visitor(visitor)

        return annotations
