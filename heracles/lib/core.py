from heracles import ql


def join(left: ql.InstantVector, right: ql.InstantVector) -> ql.BinaryOp:
    """Pure join.

    Implements a pure join by using + as the join operator. The right side of the join
    is multiplied by 0 to ensure that the left side data is unchanged.

    Returns a ql.BinaryOp, which allows the caller to use 'on' and 'group_' to manipulte
    which labels are preserved in the join.
    """
    return left + (right * 0)
