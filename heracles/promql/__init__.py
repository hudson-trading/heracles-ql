"""PromQL dialect for building queries accepted by Prometheus."""

from heracles.ql import duration as _duration
from heracles.ql.factory import Selector as Selector
from heracles.ql.prelude import *  # noqa: F403

from .functions import *  # noqa: F403
from .functions import PROMQL_AGGREGATORS, PROMQL_FUNCTIONS

Millisecond = _duration.Millisecond
Second = _duration.Second
Minute = _duration.Minute
Hour = _duration.Hour
Day = _duration.Day
Week = _duration.Week
Year = _duration.Year


class PromQLValidationError(ValueError):
    """Raised when an expression contains syntax outside the PromQL dialect."""


class _PromQLValidator(TimeseriesVisitor):  # type: ignore[name-defined]  # noqa: F405
    def visit_builtin_function(
        self,
        function: BuiltinFunc,  # type: ignore[name-defined]  # noqa: F405
    ) -> VisitorAction | None:  # type: ignore[name-defined]  # noqa: F405
        if function.name not in PROMQL_FUNCTIONS:
            raise PromQLValidationError(
                f"function {function.name!r} is not supported by PromQL"
            )
        return VisitorAction.RECURSE  # type: ignore[name-defined]  # noqa: F405

    def visit_aggr_function(
        self,
        function: AggrFunc,  # type: ignore[name-defined]  # noqa: F405
    ) -> VisitorAction | None:  # type: ignore[name-defined]  # noqa: F405
        if function.name not in PROMQL_AGGREGATORS:
            raise PromQLValidationError(
                f"aggregator {function.name!r} is not supported by PromQL"
            )
        return VisitorAction.RECURSE  # type: ignore[name-defined]  # noqa: F405


def validate(expression: Timeseries) -> None:  # type: ignore[name-defined]  # noqa: F405
    """Validate that an expression only uses PromQL functions and aggregators."""
    expression.accept_visitor(_PromQLValidator())


def render(expression: Timeseries) -> str:  # type: ignore[name-defined]  # noqa: F405
    """Validate and render an expression as PromQL."""
    validate(expression)
    return expression.render()
