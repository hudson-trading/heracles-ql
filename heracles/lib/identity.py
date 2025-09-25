from collections.abc import Callable, Iterable

from heracles import ql
from heracles.ql import assertions


def reduce(
    vector: ql.InstantVector,
    *,
    to: Iterable[str],
    func: Callable[[ql.InstantVector], ql.AggrFunc] | None = None,
) -> ql.InstantVector:
    if not func:
        return ql.max(vector.annotate(assertions.assert_exactly_one(*to))).by(*to)
    else:
        return func(vector).by(*to)
