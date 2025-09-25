import enum
from collections.abc import Callable

from heracles import ql
from heracles.ql import annotation


class BinaryOpAssociation(str, enum.Enum):
    Left = "left"
    Right = "right"


@annotation.assertion()
def no_cardinality_change(
    vector: ql.BinaryOp, association: BinaryOpAssociation = BinaryOpAssociation.Left
) -> ql.InstantVector:
    base_count = (
        vector.left if association == BinaryOpAssociation.Left else vector.right
    )
    return ql.absent(ql.count(base_count) == ql.count(vector))


def assert_exactly_one(
    *by_labels: str,
) -> Callable[[ql.InstantVector], annotation.AssertionAnnotation[ql.InstantVector]]:
    @annotation.assertion()
    def assert_exactly_one(vector: ql.InstantVector) -> ql.InstantVector:
        return ql.count(vector).by(*by_labels) != 1

    return assert_exactly_one
