from __future__ import annotations

import abc
import copy
import enum
import inspect
import json
import operator
from collections.abc import Callable, Generator, Iterable
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar


class UnopKind(str, enum.Enum):
    neg = "-"


class BinopKind(str, enum.Enum):
    add = "+"
    sub = "-"
    mul = "*"
    truediv = "/"
    mod = "%"
    pow = "^"

    eq = "=="
    ne = "!="
    gt = ">"
    ge = ">="
    lt = "<"
    le = "<="

    and_ = "and"
    or_ = "or"

    unless = "unless"

    atan2 = "atan2"


class VisitorAction(enum.Enum):
    """
    Visitor recursion control.
    RECURSE causes traversal to recurse depth first through the tree.
        It is the default behavior. RECURSE is fasley so that None and RECURSE have
        the same meaning.
    STOP causes traversal to stop immediately without visiting more nodes.
    CONTINUE causes traversal to continue to the next sibling node.
    """

    RECURSE = 0
    STOP = 1
    CONTINUE = 2


class TimeseriesVisitor(abc.ABC):
    """
    TimeseriesVisitor is the base visitor class for heracles expression trees.
    Implementations of this class can be used to traverse an expression tree and perform
    operations on it. Implementations only need to implement the visit_* methods for the
    types they're interested in visiting. It is required to override at least one
    method.

    Most ad-hoc visitors will use the _VisitorFuncWrapper and VisitorFunc to implement
    this class using a function. For simple cases, this reduces boilerplate. However,
    for complicated cases it can be difficult to express visitor logic as a single
    function.
    """

    def visit_node(self, v: Any) -> VisitorAction | None:
        return None

    def visit_scalar_literal(self, v: ScalarLiteral) -> VisitorAction | None:
        return self.visit_instant_vector(v)

    def visit_instant_vector(self, v: InstantVector) -> VisitorAction | None:
        return self.visit_node(v)

    def visit_range_vector(self, v: RangeVector) -> VisitorAction | None:
        return self.visit_node(v)

    def visit_selected_instant_vector(
        self, v: SelectedInstantVector
    ) -> VisitorAction | None:
        return self.visit_instant_vector(v)

    def visit_selected_range_vector(
        self, v: SelectedRangeVector
    ) -> VisitorAction | None:
        return self.visit_range_vector(v)

    def visit_subquery_range_vector(
        self, v: SubqueryRangeVector
    ) -> VisitorAction | None:
        return self.visit_range_vector(v)

    def visit_binary_op(self, v: BinaryOp) -> VisitorAction | None:
        return self.visit_instant_vector(v)

    def visit_unary_op(self, v: UnaryOp) -> VisitorAction | None:
        return self.visit_instant_vector(v)

    def visit_builtin_function(self, v: BuiltinFunc) -> VisitorAction | None:
        return self.visit_instant_vector(v)

    def visit_aggr_function(self, v: AggrFunc) -> VisitorAction | None:
        return self.visit_builtin_function(v)

    def visit_at_op(self, v: AtOp) -> VisitorAction | None:
        return self.visit_node(v)

    def visit_offset_op(self, v: OffsetOp) -> VisitorAction | None:
        return self.visit_node(v)


_T = TypeVar("_T", bound="AcceptsVisitor")
VisitorFunc = Callable[[_T], VisitorAction | None]


class _VisitorFuncWrapper(TimeseriesVisitor):
    """
    _VisitorFuncWrapper wraps a VisitorFunc as a TimeseriesVisitor. It's used
    to avoid the need to distinguish between VisitorFunc and TimeseriesVisitor
    internally.
    """

    def __init__(self, func: VisitorFunc) -> None:
        super().__init__()
        self.func = func

        sig = inspect.signature(func, eval_str=True)
        (param,) = sig.parameters.values()
        self.accepted_type: type | None = param.annotation

    def visit_node(self, v: Any) -> VisitorAction | None:
        if not self.accepted_type or isinstance(v, self.accepted_type):
            return self.func(v)
        return None


def _wrap_visitor(v: TimeseriesVisitor | VisitorFunc) -> TimeseriesVisitor:
    if callable(v):
        return _VisitorFuncWrapper(v)
    return v


class AcceptsVisitor(abc.ABC):
    def accept_visitor(
        self, visitor: TimeseriesVisitor | VisitorFunc
    ) -> VisitorAction | None:
        visitor = _wrap_visitor(visitor)
        if action := self._accept_self_visitor(visitor):
            return action
        for child in self._children_to_visit():
            if isinstance(child, AcceptsVisitor):
                action = child.accept_visitor(visitor)
            else:
                # hack to avoid wrapping float, int, str, etc in AcceptsVisitor
                action = visitor.visit_node(child)
            if action == VisitorAction.STOP:
                # propogate STOP up the stack
                return VisitorAction.STOP
            if action == VisitorAction.CONTINUE:
                # do not propogate CONTINUE from child nodes
                continue
        return VisitorAction.RECURSE

    @abc.abstractmethod
    def _accept_self_visitor(
        self, visitor: TimeseriesVisitor
    ) -> VisitorAction | None: ...

    def _children_to_visit(self) -> Generator[Any]:
        return
        yield


class Renderable(abc.ABC):
    @abc.abstractmethod
    def render(self) -> str: ...


_TARGET = TypeVar("_TARGET", contravariant=True)


class Annotation(Generic[_TARGET], abc.ABC):
    def __init__(self, target: _TARGET) -> None:
        self.target = target


class Timeseries(AcceptsVisitor, Renderable, abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        self.annotations: list[Annotation[Self]] = []

    def annotate(self, annotation: Callable[[Self], Annotation[Self]]) -> Self:
        self.annotations.append(annotation(self))
        return self

    def is_annotated(self) -> bool:
        return bool(self.annotations)

    def without_annotations(self) -> Self:
        copied = copy.copy(self)
        copied.annotations = []
        return copied

    pass


if TYPE_CHECKING:
    SubquerySliceExpr = slice["Duration", "Duration | None", None]  # type: ignore
else:
    SubquerySliceExpr = slice


class Subquery:
    def __init__(self, lookback: Duration, step: Duration | None) -> None:
        self.lookback = lookback
        self.step = step

    def render(self) -> str:
        res = self.lookback.render()
        if self.step:
            res = f"{res}:{self.step.render()}"
        return res


class InstantVector(Timeseries, abc.ABC):
    def __add__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.add)

    def __radd__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(o, self, BinopKind.add)

    def __sub__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.sub)

    def __rsub__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(o, self, BinopKind.sub)

    def __mul__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.mul)

    def __rmul__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(o, self, BinopKind.mul)

    def __truediv__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.truediv)

    def __rtruediv__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(o, self, BinopKind.truediv)

    def __mod__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.mod)

    def __rmod__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(o, self, BinopKind.mod)

    def __pow__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.pow)

    def __rpow__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(o, self, BinopKind.pow)

    def __eq__(self, o: InstantVector | float | int) -> BinaryOp:  # type: ignore
        return _instant_vector_binop(self, o, BinopKind.eq)

    def __ne__(self, o: InstantVector | float | int) -> BinaryOp:  # type: ignore
        return _instant_vector_binop(self, o, BinopKind.ne)

    def __gt__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.gt)

    def __ge__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.ge)

    def __lt__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.lt)

    def __le__(self, o: InstantVector | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.le)

    def __matmul__(self, o: InstantVector | float | int) -> InstantVectorAt:
        if isinstance(o, _scalar_promotion_types):
            o = _promote_scaler(o)
        # o is refined to InstantVector | Scalar now
        return InstantVectorAt(self, o)

    def __and__(self, o: Timeseries | float | int) -> BinaryOp:
        return self.and_(o)

    def and_(self, o: Timeseries | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.and_)

    def __or__(self, o: Timeseries | float | int) -> BinaryOp:
        return self.or_(o)

    def or_(self, o: Timeseries | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.or_)

    def unless(self, o: Timeseries | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.unless)

    def atan2(self, o: Timeseries | float | int) -> BinaryOp:
        return _instant_vector_binop(self, o, BinopKind.atan2)

    def offset(self, offset: Duration) -> OffsetInstantVector:
        return OffsetInstantVector(self, offset)

    def __getitem__(self, subquery: SubquerySliceExpr) -> RangeVector:
        return SubqueryRangeVector(self, subquery.start, subquery.stop)


def _instant_vector_binop(
    left: Timeseries | float | int, right: Timeseries | float | int, op: BinopKind
) -> BinaryOp:
    if isinstance(left, _scalar_promotion_types):
        promoted_left: Timeseries = _promote_scaler(left)
    else:
        promoted_left = left
    if isinstance(right, _scalar_promotion_types):
        promoted_right: Timeseries = _promote_scaler(right)
    else:
        promoted_right = right
    return BinaryOp(promoted_left, promoted_right, op)


class SelectedInstantVector(InstantVector):
    def __init__(self, /, *, name: str | None, **kwargs: MatcherExpr) -> None:
        super().__init__()
        self._selectors: dict[str, MatcherExpr] = {}
        self.name = name
        for name, value in kwargs.items():
            self._selectors[name] = value

    def __getitem__(self, lookback: Duration | SubquerySliceExpr) -> RangeVector:
        if type(lookback) is Duration:
            return SelectedRangeVector(self, lookback)
        elif type(lookback) is SubquerySliceExpr:
            return super().__getitem__(lookback)
        else:
            raise Exception("not a legal range")

    def __call__(self, **kwargs: Any) -> SelectedInstantVector:
        res_vec = SelectedInstantVector(name=self.name, **self._selectors)
        for name, value in kwargs.items():
            res_vec._selectors[name] = value
        return res_vec

    def render(self) -> str:
        selectors = []
        for k, v in self._selectors.items():
            op = "="
            if isinstance(v, Matcher):
                op = v.kind.value
                v = v.value
            selectors.append(f"{k}{op}{json.dumps(v)}")
        matchers = f'{{{ ",".join(selectors)}}}'
        if self.name:
            return self.name + matchers
        else:
            return matchers

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_selected_instant_vector(self)


class RangeVector(Timeseries, abc.ABC):
    def __matmul__(self, o: InstantVector | float | int) -> RangeVectorAt:
        if isinstance(o, _scalar_promotion_types):
            o = _promote_scaler(o)
        return RangeVectorAt(self, o)

    def offset(self, offset: Duration) -> OffsetRangeVector:
        return OffsetRangeVector(self, offset)


class SelectedRangeVector(RangeVector):
    def __init__(self, instant: InstantVector, lookback: Duration) -> None:
        super().__init__()
        self.instant_vector = instant
        self.lookback = lookback

    def render(self) -> str:
        return f"{self.instant_vector.render()}[{self.lookback.render()}]"

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_selected_range_vector(self)

    def _children_to_visit(self) -> Generator[Any]:
        yield self.instant_vector


class SubqueryRangeVector(RangeVector):
    def __init__(
        self,
        subquery_expr: InstantVector,
        lookback: Duration,
        resolution: Duration | None,
    ) -> None:
        super().__init__()
        self.subquery_expr = subquery_expr
        self.lookback = lookback
        self.resolution = resolution

    def render(self) -> str:
        resolution_str = self.resolution.render() if self.resolution else ""
        return (
            f"({self.subquery_expr.render()})"
            f"[{self.lookback.render()}:{resolution_str}]"
        )

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_subquery_range_vector(self)

    def _children_to_visit(self) -> Generator[Any]:
        yield self.subquery_expr


class ScalarLiteral(InstantVector):
    def __init__(self, v: float | int) -> None:
        super().__init__()
        self.v = float(v)

    def render(self) -> str:
        return str(self.v)

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_scalar_literal(self)


class BinaryOp(InstantVector):
    def __init__(self, left: Any, right: Any, op: str) -> None:
        super().__init__()
        self.left = left
        self.right = right
        self.op = op
        self.on_labels: list[str] = []
        self.ignoring_labels: list[str] = []
        self.group_by: tuple[str, Iterable[str]] | None = None

    def on(self, *labels: str) -> Self:
        copied = copy.copy(self)
        copied.on_labels.extend(labels)
        return copied

    def ignoring(self, *labels: str) -> Self:
        copied = copy.copy(self)
        copied.ignoring_labels.extend(labels)
        return copied

    def group_left(self, *labels: str) -> Self:
        copied = copy.copy(self)
        copied.group_by = ("group_left", labels)
        return copied

    def group_right(self, *labels: str) -> Self:
        copied = copy.copy(self)
        copied.group_by = ("group_right", labels)
        return copied

    def render(self) -> str:
        exprs = [self.left.render(), self.op]
        if self.on_labels:
            on_expr = f"on ({','.join(self.on_labels)})"
            exprs.append(on_expr)
        elif self.ignoring_labels:
            ignoring_expr = f"ignoring ({','.join(self.ignoring_labels)})"
            exprs.append(ignoring_expr)

        if self.group_by:
            group_by_expr = f"{self.group_by[0]}({','.join(self.group_by[1])})"
            exprs.append(group_by_expr)

        exprs.append(self.right.render())

        return "(" + " ".join(exprs) + ")"

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_binary_op(self)

    def _children_to_visit(self) -> Generator[Any]:
        yield self.left
        yield self.right


class UnaryOp(InstantVector):
    def __init__(self, arg: Any, op: UnopKind) -> None:
        super().__init__()
        self.arg = arg
        self.op = op

    def render(self) -> str:
        return f"{self.op}{self.arg.render()}"

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_unary_op(self)

    def _children_to_visit(self) -> Generator[Any]:
        yield self.arg


class InstantUnaryOp(UnaryOp, InstantVector):
    pass


class AtOp(Timeseries, abc.ABC):
    def __init__(self, vector: Timeseries, timestamp: Any) -> None:
        super().__init__()
        self.vector = vector
        self.timestamp = timestamp

    def render(self) -> str:
        return f"({self.vector.render()} @ {_render_any(self.timestamp)})"

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_at_op(self)

    def _children_to_visit(self) -> Generator[Any]:
        yield self.vector
        yield self.timestamp


class InstantVectorAt(AtOp, InstantVector):
    pass


class RangeVectorAt(AtOp, RangeVector):
    pass


class OffsetOp(Timeseries, abc.ABC):
    def __init__(self, vector: Timeseries, offset: Duration) -> None:
        super().__init__()
        self.vector = vector
        self.offset_duration = offset

    def render(self) -> str:
        return f"({self.vector.render()} offset {self.offset_duration.render()})"

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_offset_op(self)

    def _children_to_visit(self) -> Generator[Any]:
        yield self.vector


class OffsetInstantVector(OffsetOp, InstantVector):
    pass


class OffsetRangeVector(OffsetOp, RangeVector):
    pass


class BuiltinFunc(InstantVector, abc.ABC):
    def __init__(self, name: str, *args: Any) -> None:
        super().__init__()
        self.name = name
        self.args = args

    def render(self) -> str:
        rendered_args = []
        for a in self.args:
            rendered_args.append(_render_any(a))
        return f"{self.name}({', '.join(rendered_args)})"

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_builtin_function(self)

    def _children_to_visit(self) -> Generator[Any]:
        yield from self.args


class RollupFunc(BuiltinFunc):
    pass


class TransformFunc(BuiltinFunc):
    pass


class LabelManipulationFunc(BuiltinFunc):
    pass


class BaseAggrFunc(BuiltinFunc):
    pass


class AggrFunc(BaseAggrFunc):
    def __init__(self, name: str, *args: Any) -> None:
        super().__init__(name, *args)
        self._by_labels: Iterable[str] = []
        self._without_labels: Iterable[str] = []

    def by(self, *labels: str) -> InstantVector:
        return FinalizedAggrFunc(
            self.name, self.args, by_labels=labels, without_labels=None
        )

    def without(self, *labels: str) -> InstantVector:
        return FinalizedAggrFunc(
            self.name,
            self.args,
            by_labels=None,
            without_labels=labels,
        )

    def render(self) -> str:
        rendered_args = []
        for a in self.args:
            rendered_args.append(_render_any(a))
        res = f"{self.name}({', '.join(rendered_args)})"
        if self._by_labels:
            res += f" by ({','.join(self._by_labels)})"
        return res

    def _accept_self_visitor(self, visitor: TimeseriesVisitor) -> VisitorAction | None:
        return visitor.visit_aggr_function(self)


class FinalizedAggrFunc(BaseAggrFunc):
    def __init__(
        self,
        name: str,
        args: Iterable[str],
        by_labels: Iterable[str] | None,
        without_labels: Iterable[str] | None,
    ) -> None:
        super().__init__(name, *args)
        self._by_labels = by_labels
        self._without_labels = without_labels

    def render(self) -> str:
        main_call = super().render()
        if self._by_labels:
            return main_call + f" by ({','.join(self._by_labels)})"
        if self._without_labels:
            return main_call + f" without ({','.join(self._without_labels)})"
        raise Exception("poorly constructed aggr func")


def _render_any(a: Any) -> str:
    if isinstance(a, Renderable):
        return a.render()
    if isinstance(a, str):
        return json.dumps(a)
    return str(a)


class DurationUnit(tuple[float, str], enum.Enum):
    millisecond = (1, "ms")
    second = (millisecond[0] * 1000, "s")
    minute = (second[0] * 60, "m")
    hour = (minute[0] * 60, "h")
    day = (hour[0] * 24, "d")
    week = (day[0] * 7, "w")
    year = (day[0] * 365, "y")

    def unit_name(self) -> str:
        return self[1]

    def unit_factor(self) -> float:
        return self[0]


class Duration(Renderable):
    def __init__(self, time_value: float, interval_value: float) -> None:
        self.time_value = time_value
        self.interval_value = interval_value

    @staticmethod
    def from_units(value: float, unit: DurationUnit) -> Duration:
        return Duration(value * unit[0], 0)

    @staticmethod
    def from_interval(interval: float) -> Duration:
        return Duration(0, interval)

    def __add__(self, o: Duration) -> Duration:
        return self._binop(o, operator.add)

    def __sub__(self, o: Duration) -> Duration:
        return self._binop(o, operator.sub)

    def __eq__(self, o: Any) -> bool:
        if not isinstance(o, Duration):
            return False
        return (
            self.time_value == o.time_value and self.interval_value == o.interval_value
        )

    def _binop(self, o: Duration, op: Callable[[float, float], float]) -> Duration:
        return Duration(
            op(self.time_value, o.time_value), op(self.interval_value, o.interval_value)
        )

    # math with scalars
    def __mul__(self, o: float | int) -> Duration:
        return Duration._scalar_binop(self, o, operator.mul)

    def __rmul__(self, o: float | int) -> Duration:
        return Duration._scalar_binop(o, self, operator.mul)

    def __truediv__(self, o: Duration) -> Duration:
        return self._binop(o, operator.truediv)

    def __rtruediv__(self, o: Duration) -> Duration:
        return Duration._scalar_binop(o, self, operator.truediv)

    def __floordiv__(self, o: Duration) -> Duration:
        return Duration._scalar_binop(self, o, operator.floordiv)

    def __rfloordiv__(self, o: Duration) -> Duration:
        return Duration._scalar_binop(o, self, operator.floordiv)

    def __pow__(self, o: Duration) -> Duration:
        return Duration._scalar_binop(self, o, operator.pow)

    def __rpow__(self, o: Duration) -> Duration:
        return Duration._scalar_binop(o, self, operator.pow)

    @staticmethod
    def _scalar_binop(
        left: Duration | float | int,
        right: Duration | float | int,
        op: Callable[[float, float], float],
    ) -> Duration:
        if isinstance(left, Duration) and not isinstance(right, Duration):
            return Duration(op(left.time_value, right), op(left.interval_value, right))
        if not isinstance(left, Duration) and isinstance(right, Duration):
            return Duration(op(left, right.time_value), op(left, right.interval_value))
        raise Exception("invalid arguments")

    if TYPE_CHECKING:

        def __index__(self) -> int:
            # This is needed to implement the SupportsIndex protocol. That's needed
            # to allow subquery expression using the python slice syntax.
            # For some reason, MyPy thinks that the type parameters for slice
            # must implement SupportsIndex, despite this not being true. The user
            # could write type: ignore on every line where they do a subquery, but
            # that's kinda awful.
            #
            # This method is never ever expected to be called, it's only needed to make
            # MyPy happy.
            raise NotImplementedError("don't call __index__ on Duration")

    def render(self) -> str:
        if self.interval_value:
            interval = f"{self.interval_value}i"
        else:
            interval = ""
        if self.time_value:
            remainder = self.time_value
            parts = []

            # this needs a type annotation because mypy can't seem
            # to figure out that it's not a DurationUnit | str | float
            sorted_duration_units: Iterable[DurationUnit] = sorted(
                DurationUnit, key=lambda u: u.unit_factor(), reverse=True
            )
            for unit in sorted_duration_units:
                res, new_remainder = divmod(remainder, unit.unit_factor())
                if res > 0 and unit != DurationUnit.millisecond:
                    parts.append(f"{res}{unit.unit_name()}")
                elif unit == DurationUnit.millisecond and remainder != 0:
                    parts.append(f"{remainder}ms")
                remainder = new_remainder

            time = "".join(parts)
        else:
            time = ""
        if not time and not interval:
            # this duration is 0. Return 0ms.
            return "0ms"
        return "".join((time, interval))

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return self.render()


InstantOrRangeVector = TypeVar("InstantOrRangeVector", InstantVector, RangeVector)


def _promote_scaler(v: InstantVector | float | int) -> InstantVector:
    if isinstance(v, InstantVector):
        return v
    if isinstance(v, float):
        return ScalarLiteral(v)
    if isinstance(v, int):
        return ScalarLiteral(float(v))


_scalar_promotion_types = (InstantVector, float, int)

Constant = InstantVector | float | int
ConstantOrVector = InstantVector | Constant


class MatcherKind(str, enum.Enum):
    Equal = "="
    Regex = "=~"
    NotEqual = "!="
    NotRegex = "!~"


class Matcher:
    def __init__(self, value: str, kind: MatcherKind) -> None:
        self.value = value
        self.kind = kind

    def is_negative(self) -> bool:
        return self.kind in (MatcherKind.NotRegex, MatcherKind.NotEqual)

    def invert(self) -> Matcher:
        match self.kind:
            case MatcherKind.Equal:
                return NE(self.value)
            case MatcherKind.Regex:
                return NR(self.value)
            case MatcherKind.NotEqual:
                return EQ(self.value)
            case MatcherKind.NotRegex:
                return RE(self.value)


def EQ(value: str) -> Matcher:
    return Matcher(value, MatcherKind.Equal)


def RE(value: str) -> Matcher:
    return Matcher(value, MatcherKind.Regex)


def NE(value: str) -> Matcher:
    return Matcher(value, MatcherKind.NotEqual)


def NR(value: str) -> Matcher:
    return Matcher(value, MatcherKind.NotRegex)


MatcherExpr = str | Matcher
