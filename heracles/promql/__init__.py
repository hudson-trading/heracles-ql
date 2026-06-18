"""PromQL dialect for building queries accepted by Prometheus.

The function and aggregator constructors in ``heracles.promql.funcs`` are generated
from the Prometheus documentation by ``codegen/promql.py`` (see ``make
generate_promql_funcs``). This module wraps them with validation that rejects any
expression node using a function or aggregator outside the PromQL dialect.
"""

from heracles.ql import duration as _duration
from heracles.ql.factory import Selector as Selector
from heracles.ql.prelude import *  # noqa: F403

from .funcs import *  # noqa: F403
from .funcs import PROMQL_AGGREGATORS, PROMQL_FUNCTIONS

Millisecond = _duration.Millisecond
Second = _duration.Second
Minute = _duration.Minute
Hour = _duration.Hour
Day = _duration.Day
Week = _duration.Week
Year = _duration.Year


class PromQLValidationError(ValueError):
    """Raised when an expression contains syntax outside the PromQL dialect."""


def _reject_interval_duration(
    duration: Duration,  # type: ignore[name-defined]  # noqa: F405
) -> None:
    # interval ("step") durations such as 5i are a MetricsQL extension; PromQL only
    # accepts time durations such as 5m.
    if duration.interval_value:
        raise PromQLValidationError(
            f"interval duration {duration.render()!r} is not supported by PromQL"
        )


class _PromQLValidator(TimeseriesVisitor):  # type: ignore[name-defined]  # noqa: F405
    # every visit_* method returns None (not VisitorAction.RECURSE) so traversal keeps
    # descending: accept_visitor stops on any truthy return, and the RECURSE member is
    # truthy despite its 0 value.
    def visit_builtin_function(
        self,
        function: BuiltinFunc,  # type: ignore[name-defined]  # noqa: F405
    ) -> VisitorAction | None:  # type: ignore[name-defined]  # noqa: F405
        if function.name not in PROMQL_FUNCTIONS:
            raise PromQLValidationError(
                f"function {function.name!r} is not supported by PromQL"
            )
        return None

    def visit_aggr_function(
        self,
        function: AggrFunc,  # type: ignore[name-defined]  # noqa: F405
    ) -> VisitorAction | None:  # type: ignore[name-defined]  # noqa: F405
        if function.name not in PROMQL_AGGREGATORS:
            raise PromQLValidationError(
                f"aggregator {function.name!r} is not supported by PromQL"
            )
        return None

    def visit_selected_range_vector(
        self,
        v: SelectedRangeVector,  # type: ignore[name-defined]  # noqa: F405
    ) -> VisitorAction | None:  # type: ignore[name-defined]  # noqa: F405
        _reject_interval_duration(v.lookback)
        return None

    def visit_subquery_range_vector(
        self,
        v: SubqueryRangeVector,  # type: ignore[name-defined]  # noqa: F405
    ) -> VisitorAction | None:  # type: ignore[name-defined]  # noqa: F405
        _reject_interval_duration(v.lookback)
        if v.resolution is not None:
            _reject_interval_duration(v.resolution)
        return None

    def visit_offset_op(
        self,
        v: OffsetOp,  # type: ignore[name-defined]  # noqa: F405
    ) -> VisitorAction | None:  # type: ignore[name-defined]  # noqa: F405
        _reject_interval_duration(v.offset_duration)
        return None


def validate(expression: Timeseries) -> None:  # type: ignore[name-defined]  # noqa: F405
    """Validate that an expression only uses PromQL functions, aggregators and
    durations."""
    expression.accept_visitor(_PromQLValidator())


def render(expression: Timeseries) -> str:  # type: ignore[name-defined]  # noqa: F405
    """Validate and render an expression as PromQL."""
    validate(expression)
    return expression.render()
