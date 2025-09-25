from __future__ import annotations

import abc
import contextlib
import dataclasses
import functools
import inspect
from collections.abc import Callable, Generator, Iterable
from typing import (
    Annotated,
    Any,
    Generic,
    ParamSpec,
    Self,
    TypeAlias,
    TypeVar,
    overload,
)

import pydantic

from heracles import ql

_Rule = TypeVar("_Rule", bound="Rule")
_RealizedRule = TypeVar("_RealizedRule", bound="RealizedRule")

ExprFunc = Callable[[_RealizedRule], ql.InstantVector]

Expr = ql.InstantVector | ExprFunc[_RealizedRule]


class Rule(abc.ABC, Generic[_RealizedRule]):  # type: ignore
    @property
    @abc.abstractmethod
    def name(self) -> str | None: ...

    @property
    @abc.abstractmethod
    def expr(self) -> Expr[_RealizedRule] | None: ...

    @property
    @abc.abstractmethod
    def labels(self) -> dict[str, str]: ...

    @abc.abstractmethod
    def realize(self, **kwargs: Any) -> _RealizedRule:
        raise NotImplementedError


class RealizedRule(pydantic.BaseModel, abc.ABC):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        serialize_by_alias=True,
    )
    name: str
    raw_expr: Annotated[Expr[Self], pydantic.Field(exclude=True)]
    labels: dict[str, str] = {}

    @pydantic.computed_field()  # type: ignore[misc]
    @property
    def expr(self: Self) -> ql.InstantVector:
        # without the self: Self annotation, mypy doesn't think
        # self is a Self...
        if isinstance(self.raw_expr, ql.InstantVector):
            return self.raw_expr
        else:
            return self.raw_expr(self)

    @expr.setter
    def expr(self, v: Expr[Self]) -> None:
        self.raw_expr = v

    @pydantic.field_serializer("expr")
    def _serialize_expr(self, expr: ql.InstantVector) -> str:
        rendered = expr.render()
        return ql.format(rendered) or rendered

    @abc.abstractmethod
    def _field_order(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def _exlcude_if_falsey(self) -> set[str]:
        raise NotImplementedError

    @pydantic.model_serializer(mode="wrap")
    def with_sorted_fields(
        self,
        handler: Callable[..., dict[str, Any]],
        info: pydantic.SerializationInfo,
    ) -> dict[str, Any]:
        # this is needed to produce consistently ordered fields in the output

        unsorted = handler(self, info)
        exlcude_if_falsey = self._exlcude_if_falsey()

        def include_field(k: str) -> bool:
            if k not in unsorted:
                return False
            if k in exlcude_if_falsey and not unsorted[k]:
                return False
            return True

        output = {k: unsorted[k] for k in self._field_order() if include_field(k)}
        return output


class RuleMerger(abc.ABC, Generic[_Rule, _RealizedRule]):
    @abc.abstractmethod
    def merge(self, *rules: _Rule | _RealizedRule) -> _Rule:
        raise NotImplementedError


_G = TypeVar("_G")


class _TypedKwargs:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def get(self, key: str, t: type[_G]) -> _G | None:
        if key not in self.kwargs:
            return None
        v = self.kwargs[key]
        if not isinstance(v, t):
            return None
        return v


class Alert(Rule["RealizedAlert"], abc.ABC):
    @property
    @abc.abstractmethod
    def for_(self) -> ql.Duration | None: ...

    @property
    @abc.abstractmethod
    def fire_for(self) -> ql.Duration | None: ...

    @property
    @abc.abstractmethod
    def annotations(self) -> dict[str, str]: ...


@dataclasses.dataclass(init=False)
class SimpleAlert(Alert):
    _expr: Expr[RealizedAlert]
    _name: str | None
    _for_: ql.Duration | None
    _fire_for: ql.Duration | None
    _labels: dict[str, str]
    _annotations: dict[str, str]

    def __init__(
        self,
        /,
        *,
        expr: Expr[RealizedAlert],
        name: str | None = None,
        for_: ql.Duration | None = None,
        fire_for: ql.Duration | None = None,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
    ) -> None:
        self._expr = expr
        self._name = name
        self._for_ = for_
        self._fire_for = fire_for
        self._labels = labels or {}
        self._annotations = annotations or {}

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def expr(self) -> Expr[RealizedAlert] | None:
        return self._expr

    @expr.setter
    def expr(self, v: ql.InstantVector) -> None:
        self._expr = v

    @property
    def for_(self) -> ql.Duration | None:
        return self._for_

    @property
    def fire_for(self) -> ql.Duration | None:
        return self._fire_for

    @property
    def labels(self) -> dict[str, str]:
        return self._labels

    @property
    def annotations(self) -> dict[str, str]:
        return self._annotations

    def realize(
        self,
        **kwargs: Any,
    ) -> RealizedAlert:
        typed_args = _TypedKwargs(**kwargs)

        if not self.expr and not typed_args.get("expr", Expr[RealizedAlert]):  # type: ignore
            raise ValueError("expression must be present to realize alert")

        labels = self.labels or {}
        if override_labels := typed_args.get("labels", dict[str, str]):
            labels.update(override_labels)

        annotations = self.annotations or {}
        if override_annotations := typed_args.get("annotations", dict[str, str]):
            annotations.update(override_annotations)

        override_name = typed_args.get("name", str)
        if self.name and not override_name:
            name = self.name
        elif self.name and override_name:
            name = self.name + override_name
        elif override_name:
            name = override_name
        else:
            raise ValueError("name must be present to realize alert")

        return RealizedAlert(
            name=name,
            raw_expr=typed_args.get("expr", Expr[RealizedAlert]) or self.expr,  # type: ignore
            for_=typed_args.get("for_", ql.Duration) or self.for_,
            fire_for=typed_args.get("fire_for", ql.Duration) or self.fire_for,
            labels=labels,
            annotations=annotations,
        )


class RealizedAlert(RealizedRule):
    name: Annotated[str, pydantic.Field(serialization_alias="alert")]
    raw_expr: Annotated[Expr, pydantic.Field(exclude=True)]
    for_: Annotated[ql.Duration | None, pydantic.Field(serialization_alias="for")] = (
        None
    )
    fire_for: ql.Duration | None = None
    labels: dict[str, str] = {}
    annotations: dict[str, str] = {}

    @pydantic.field_serializer("for_", "fire_for")
    def _serialize_renderable(self, expr: ql.Renderable | None) -> str | None:
        if expr is None:
            return None
        return expr.render()

    def _exlcude_if_falsey(self) -> set[str]:
        return {"labels", "annotations"}

    def _field_order(self) -> list[str]:
        return ["alert", "expr", "for", "fire_for", "labels", "annotations"]


class Recording(Rule["RealizedRecording"], abc.ABC):
    pass


@dataclasses.dataclass(init=False)
class SimpleRecording(Recording):
    _name: str | None
    _expr: Expr[RealizedRecording]
    _labels: dict[str, str]

    def __init__(
        self,
        /,
        *,
        name: str | None = None,
        expr: Expr[RealizedRecording],
        labels: dict[str, str] | None = None,
    ) -> None:
        self._name = name
        self._expr = expr
        self._labels = labels or {}

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def expr(self) -> Expr[RealizedRecording]:
        return self._expr

    @property
    def labels(self) -> dict[str, str]:
        return self._labels

    def realize(self, **kwargs: Any) -> RealizedRecording:
        typed_args = _TypedKwargs(**kwargs)
        if not self.name and not typed_args.get("name", str):
            raise ValueError("name must be present to realize recording rule")
        if not self.expr and not typed_args.get("expr", Expr[RealizedRecording]):  # type: ignore
            raise ValueError("expression must be present to realize recording rule")

        labels = self.labels or {}
        if override_labels := typed_args.get("labels", dict[str, str]):
            labels.update(override_labels)

        return RealizedRecording(
            name=typed_args.get("name", str) or self.name,  # type: ignore
            raw_expr=typed_args.get("expr", Expr[RealizedAlert]) or self.expr,  # type: ignore
            labels=labels,
        )


class RealizedRecording(RealizedRule):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        serialize_by_alias=True,
    )

    name: Annotated[str, pydantic.Field(serialization_alias="record")]

    def _exlcude_if_falsey(self) -> set[str]:
        return {"labels"}

    def _field_order(self) -> list[str]:
        return ["record", "expr", "labels"]


class BundleReference:
    """
    BundleReference allows hooks to make changes to the bundle being processed.
    """

    def __init__(self) -> None:
        self.realized_alerts: list[RealizedAlert] = []

    def add_realized_alert(self, alert: RealizedAlert) -> None:
        self.realized_alerts.append(alert)


class AfterRealizeHookMixin(abc.ABC, Generic[_RealizedRule]):
    @abc.abstractmethod
    def after_realize(self, bundle: BundleReference, rule: _RealizedRule) -> None:
        raise NotImplementedError

    def accepted_type(self) -> type[RealizedRule]:
        sig = inspect.signature(self.after_realize, eval_str=True)

        rule_param = sig.parameters.get("rule")
        if not rule_param:
            raise ValueError("this is a bug, why did you do that")

        return rule_param.annotation


@dataclasses.dataclass
class Hooks:
    hooks: list[Any]

    def after_realize(self, rules: list[RealizedRule]) -> None:
        for h in self.hooks:
            if isinstance(h, AfterRealizeHookMixin):
                bunlde_ref = BundleReference()
                for r in rules:
                    if isinstance(r, h.accepted_type()):
                        h.after_realize(bunlde_ref, r)

                # any new realized_alerts should get all future hooks applied.
                # Any previous hooks are assumed to be 'baked in' at this point
                rules.extend(bunlde_ref.realized_alerts)

    def _validate_signature(
        self, fn: Any, expect_args: list[type], expect_ret: type
    ) -> bool:
        if callable(fn):
            return False
        sig = inspect.signature(fn)
        if not issubclass(sig.return_annotation, expect_ret):
            return False
        if len(sig.parameters) != len(expect_args):
            return False
        for real_param, expected_type in zip(sig.parameters.values(), expect_args):
            if not issubclass(real_param.annotation, expected_type):
                return False
        return True


class RuleContext(abc.ABC):
    def __init__(self) -> None:
        self.alert_rules: list[Callable[..., RealizedAlert]] = []
        self._contextvars: dict[str, Any] = {}

    def _set_contextvars(self, **kwargs: Any) -> None:
        self._contextvars.update(kwargs)

    def get_contextvar(self, name: str, typ: type) -> Any | None:
        if name not in self._contextvars:
            return None
        value = self._contextvars[name]
        if not isinstance(value, typ):
            return None
        return value


# _P and _ParameterizableAlertReturn can be used to write
# Callable[_P, _ParameterizableAlertReturn] which (for practical purposes) represents
# a ParameterizableAlert as a generic. This allows writing functions which indicate
# to type checkers that they return a Callable with exactly the same signature as they
# accept while also ensuring that the Callable is constrained to be compatible with
# ParameterizableAlert.
_P = ParamSpec("_P")


AnyRule: TypeAlias = _Rule | _RealizedRule
AnyRuleList: TypeAlias = (
    list[_Rule] | list[_RealizedRule] | list[AnyRule[_Rule, _RealizedRule]]
)
AnyRuleOrList: TypeAlias = (
    AnyRule[_Rule, _RealizedRule] | AnyRuleList[_Rule, _RealizedRule]
)


_ParameterizableAlertReturn = TypeVar(
    "_ParameterizableAlertReturn",
    bound=AnyRuleOrList[Alert, RealizedAlert],
)
_ParameterizableRecordingReturn = TypeVar(
    "_ParameterizableRecordingReturn",
    bound=AnyRuleOrList[Recording, RealizedRecording],
)

ParameterizableRule = (
    Callable[..., list[_Rule]]
    | Callable[..., list[_RealizedRule]]
    | Callable[..., AnyRuleList[_Rule, _RealizedRule]]
    | Callable[..., _RealizedRule]
    | Callable[..., _Rule]
    | Callable[..., AnyRule[_Rule, _RealizedRule]]
    | Callable[..., AnyRuleOrList[_Rule, _RealizedRule]]
)


ParameterizableAlert = ParameterizableRule[Alert, RealizedAlert]
ParameterizableRecording = ParameterizableRule[Recording, RealizedRecording]

ExtendRuleFn = functools.partial[AnyRuleOrList[_Rule, _RealizedRule]]

ExtendAlertFn = ExtendRuleFn[Alert, RealizedAlert]
ExtendRecordingFn = ExtendRuleFn[Recording, RealizedRecording]

ExtendedRuleFn = (
    functools.partial[AnyRuleOrList[_Rule, _RealizedRule]]
    | functools.partial[list[_RealizedRule]]
    | functools.partial[list[_Rule]]
    | functools.partial[list[AnyRule[_Rule, _RealizedRule]]]
    | functools.partial[_RealizedRule]
    | functools.partial[_Rule]
)

ExtendedAlertFn = ExtendedRuleFn[Alert, RealizedAlert]
ExtendedRecordingFn = ExtendedRuleFn[Recording, RealizedRecording]

ContextRuleFunc = Callable[[list[_RealizedRule]], list[_RealizedRule]]
ContextAlertFunc = ContextRuleFunc[RealizedAlert]
ContextRecordingFunc = ContextRuleFunc[RealizedRecording]


@dataclasses.dataclass
class WrappedRule(Generic[_Rule, _RealizedRule]):
    partial_fn: ParameterizableRule[_Rule, _RealizedRule]
    overrides: dict[str, Any]
    hooks: Hooks

    @functools.cached_property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.partial_fn, eval_str=True)

    def is_thunkish(self) -> bool:
        """
        returns True if there are no more required parameters. There may still
        be optional parameters.
        """
        for param in self.signature.parameters.values():
            if (
                param.kind == inspect.Parameter.VAR_KEYWORD
                or param.kind == inspect.Parameter.VAR_POSITIONAL
            ):
                # variadic arguments are optional, so it's ok for them to be empty
                continue
            if param.default is inspect.Parameter.empty:
                return False
        return True

    def update(self, **kwargs: Any) -> WrappedRule:
        new_fn = functools.partial(self.partial_fn, **kwargs)
        return WrappedRule(
            partial_fn=new_fn,  # type: ignore
            overrides=self.overrides,
            hooks=self.hooks,
        )

    @overload
    def find_bindable_param(
        self, *, name: str, typ: type | None
    ) -> inspect.Parameter | None: ...

    @overload
    def find_bindable_param(
        self,
        *,
        typ: type,
    ) -> list[inspect.Parameter] | None: ...

    def find_bindable_param(
        self, *, name: str | None = None, typ: type | None = None
    ) -> list[inspect.Parameter] | inspect.Parameter | None:
        if name is None and typ is None:
            raise ValueError("name and type cannot both be none")
        sig = self.signature

        potential_matches: list[inspect.Parameter] = []
        if name:
            if match := sig.parameters.get(name):
                potential_matches.append(match)
            else:
                return None
        else:
            potential_matches.extend(sig.parameters.values())

        if typ:
            potential_matches = [
                p
                for p in potential_matches
                if p.annotation and issubclass(typ, p.annotation)
            ]

        return potential_matches

    def __call__(self) -> list[RealizedRule]:
        if not self.is_thunkish():
            raise ValueError("wrapper is not a thunk, it can't be called")
        res = self.partial_fn()
        if not isinstance(res, list):
            res = [res]

        realized: list[RealizedRule] = []
        for r in res:
            if isinstance(r, RealizedRule):
                realized.append(r)
            else:
                realized.append(r.realize(**self.overrides))

        self.hooks.after_realize(realized)

        return realized


class RuleBundle:
    def __init__(
        self,
        name: str,
        *context: RuleContext,
        evaluation_interval: ql.Duration | None = None,
    ) -> None:
        self.name: str = name
        self.evaluation_interval = evaluation_interval
        self._rules: list[WrappedRule] = []
        self._context_stack: list[RuleContext] = [*context]
        pass

    extends: type[ExtendAlertFn] = functools.partial
    extends_recording: type[ExtendRecordingFn] = functools.partial

    def get(self, name: str) -> RealizedRule | None:
        for a in self._rules:
            try:
                rules = a()
                for r in rules:
                    if r.name == name:
                        return r
            except:  # noqa
                pass
        return None

    def _curry_wrapper(self, wrapper: WrappedRule) -> WrappedRule:
        return self._apply_context(self._add_vectors(wrapper))

    def _apply_context(self, wrapper: WrappedRule) -> WrappedRule:
        kwargs = {}
        for ctx in self._context_stack:
            for name, arg in ctx._contextvars.items():
                if wrapper.find_bindable_param(name=name, typ=type(arg)):
                    kwargs[name] = arg
        return wrapper.update(**kwargs)

    def _add_vectors(self, wrapper: WrappedRule) -> WrappedRule:
        vectors_param = wrapper.find_bindable_param(typ=ql.Selector)
        if vectors_param and len(vectors_param) == 1:
            return wrapper.update(**{vectors_param[0].name: self.vectors()})
        return wrapper

    @contextlib.contextmanager
    def context(self, *context: RuleContext) -> Generator:
        added = len(context)
        self._context_stack.extend(context)
        try:
            yield
        finally:
            if added:
                self._context_stack = self._context_stack[:-added]

    def _hooks(self) -> Hooks:
        return Hooks(hooks=self._context_stack)

    def dump(self) -> Iterable[RealizedRule]:
        for wrapper in self._rules:
            if not wrapper.is_thunkish():
                raise Exception(
                    f"there's a wrapper which isn't fully applied: {wrapper.overrides}"
                )
            yield from wrapper()

    def vectors(self) -> ql.Selector:
        return ql.Selector()

    def _extend_alert(
        self, name: str, extend_fn: ParameterizableAlert, **kwargs: Any
    ) -> None:
        named_args = {
            "name": name,
            **kwargs,
        }
        wrapper = WrappedRule(
            partial_fn=extend_fn,
            overrides=named_args,
            hooks=self._hooks(),
        )
        self._rules.append(self._curry_wrapper(wrapper))

    @classmethod
    def _rename_alert_rule(cls, name: str) -> str:
        return "".join(c[0].upper() + c[1:] for c in name.split("_"))

    def _alert_annotation(self, name: str | None, **kwargs: Any) -> Callable[
        [Callable[_P, _ParameterizableAlertReturn]],
        Callable[_P, _ParameterizableAlertReturn],
    ]:
        def annotation(
            f: Callable[_P, _ParameterizableAlertReturn],
        ) -> Callable[_P, _ParameterizableAlertReturn]:
            partial = self.extends(f, **kwargs)
            self._extend_alert(
                name if name else self._rename_alert_rule(f.__name__), partial
            )
            # return the original function as this annotation can be applied
            # multiple times
            return f

        return annotation

    @overload
    def alert(self, name: str | None = None, /, **kwargs: Any) -> Callable[
        [Callable[_P, _ParameterizableAlertReturn]],
        Callable[_P, _ParameterizableAlertReturn],
    ]: ...

    @overload
    def alert(
        self,
        name: str,
        extends: ExtendedAlertFn,
        /,
        *,
        expr: ql.InstantVector | None = None,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        for_: ql.Duration | None = None,
        fire_for: ql.Duration | None = None,
    ) -> None:
        pass

    def alert(
        self,
        name: str | None = None,
        extends: ExtendedAlertFn | None = None,
        /,
        **kwargs: Any,
    ) -> (
        Callable[
            [Callable[_P, _ParameterizableAlertReturn]],
            Callable[_P, _ParameterizableAlertReturn],
        ]
        | None
    ):
        """Register a new alert.

        If used as a decorator, the function name will be used as the alertname unless
        the optional 'name' parameter is used. Keyword arguments are bound the
        parameters they reference in the decorated function. Using the decorator
        multiple times on the same function will reigster multiple alerts. This
        is useful for registering multiple variants of the same local alert.

        If used as a regular function, expects exactly two positional arguments:
        'name' and 'extends'. When used with Bundle.extends, this syntax will register
        an existing function as an alert with optional overrides provided as kwargs.
        """
        if name and extends:
            # extends case
            self._extend_alert(name, extends, **kwargs)
            return None
        elif not extends:
            # direct definition case
            name = name if name else None
            return self._alert_annotation(name, **kwargs)
        else:
            raise ValueError("invalid combination of parameters")

    def _extend_recording(
        self, name: str, extend_fn: ParameterizableRecording, **kwargs: Any
    ) -> None:
        named_args = {
            "name": name,
            **kwargs,
        }
        wrapper = WrappedRule(
            partial_fn=extend_fn,
            overrides=named_args,
            hooks=self._hooks(),
        )
        self._rules.append(self._curry_wrapper(wrapper))

    @classmethod
    def _rename_recording_rule(cls, name: str) -> str:
        return name.replace("_", ":")

    def _recording_annotation(self, name: str | None, **kwargs: Any) -> Callable[
        [Callable[_P, _ParameterizableRecordingReturn]],
        Callable[_P, _ParameterizableRecordingReturn],
    ]:
        def annotation(
            f: Callable[_P, _ParameterizableRecordingReturn],
        ) -> Callable[_P, _ParameterizableRecordingReturn]:
            partial = self.extends_recording(f, **kwargs)
            self._extend_recording(
                name if name else self._rename_recording_rule(f.__name__), partial
            )
            # return the original function as this annotation can be applied
            # multiple times
            return f

        return annotation

    def _wrap_recording(self, expr: ql.InstantVector, name: str) -> None:
        def partial_rule() -> Recording:
            return SimpleRecording(name=name, expr=expr)

        wrapper: WrappedRule[Recording, RealizedRecording] = WrappedRule(
            partial_fn=partial_rule,
            overrides={},
            hooks=self._hooks(),
        )

        self._rules.append(self._curry_wrapper(wrapper))

    @overload
    def record(self, name: str | None = None, /, **kwargs: Any) -> Callable[
        [Callable[_P, _ParameterizableRecordingReturn]],
        Callable[_P, _ParameterizableRecordingReturn],
    ]: ...

    @overload
    def record(
        self,
        name: str,
        extends: ExtendedRecordingFn,
        /,
        *,
        expr: ql.InstantVector | None = None,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        for_: ql.Duration | None = None,
        fire_for: ql.Duration | None = None,
    ) -> None:
        pass

    @overload
    def record(self, expr: ql.InstantVector, /, name: str) -> ql.SelectedInstantVector:
        pass

    def record(  # type: ignore
        self,
        *args: Any,
        **kwargs: Any,
    ) -> (
        Callable[
            [Callable[_P, _ParameterizableRecordingReturn]],
            Callable[_P, _ParameterizableRecordingReturn],
        ]
        | ql.SelectedInstantVector
        | None
    ):
        """Register a new recording.

        If used as a decorator, the function name will be used as the recording
        unless the optional 'name' parameter is used. Keyword arguments are bound the
        parameters they reference in the decorated function. Using the decorator
        multiple times on the same function will reigster multiple recordings. This
        is useful for registering multiple variants of the same local recording.

        If used as a regular function, expects exactly two positional arguments:
        'name' and 'extends'. When used with Bundle.extends_recording, this syntax will
        register an existing function as an recording with optional overrides provided
        as kwargs.
        """
        if (
            len(args) == 2
            and isinstance(args[0], str)
            and isinstance(args[1], functools.partial)
        ):
            # extends case
            self._extend_recording(args[0], args[1], **kwargs)
            return None
        elif (len(args) == 1 and isinstance(args[0], str)) or len(args) == 0:
            # direct definition case
            name = args[0] if args else None
            return self._recording_annotation(name, **kwargs)
        elif len(args) <= 2 and isinstance(args[0], ql.InstantVector):
            if len(args) == 2:
                name = args[1]
            elif "name" in kwargs:
                name = kwargs["name"]
            else:
                raise ValueError("name must be defined for adhoc recording rules")

            self._wrap_recording(args[0], name)
            return ql.SelectedInstantVector(name=name)
        else:
            raise ValueError("invalid combination of parameters")
