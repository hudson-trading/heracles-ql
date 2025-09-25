from collections.abc import Callable
from typing import (
    TypeVar,
)

T = TypeVar("T")
ReduceFunc = Callable[[T | None, T | None], T | None]


def merge_labelset(
    left: dict[str, str] | None, right: dict[str, str] | None
) -> dict[str, str] | None:
    if not right:
        return left
    if not left:
        return right

    res = {}
    res.update(left)
    res.update(right)
    return res


def push_suffix(left: str | None, right: str | None) -> str | None:
    if left and right:
        return f"{right}{left}"
    if not right:
        return left
    return right


def replace(left: T | None, right: T | None) -> T | None:
    return right if right is not None else left
