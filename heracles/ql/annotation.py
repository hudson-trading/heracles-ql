import abc
from collections.abc import Callable
from typing import Generic, TypeVar

from heracles import ql

_T = TypeVar("_T", contravariant=True)


class AssertionAnnotation(Generic[_T], ql.Annotation[_T]):
    @abc.abstractmethod
    def assertion(self) -> ql.InstantVector: ...


_AT = TypeVar("_AT")


def assertion() -> (
    Callable[
        [Callable[[_AT], ql.InstantVector]], Callable[[_AT], AssertionAnnotation[_AT]]
    ]
):
    def annotation_func(
        f: Callable[[_AT], ql.InstantVector],
    ) -> Callable[[_AT], AssertionAnnotation[_AT]]:
        class Wrapper(AssertionAnnotation):
            def assertion(self) -> ql.InstantVector:
                return f(self.target)

        return Wrapper

    return annotation_func
