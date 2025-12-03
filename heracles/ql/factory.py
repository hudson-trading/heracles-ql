from heracles.ql import assertions, prelude


class Selector:
    """
    Selector provides nicer syntax for selecting instant vectors.
    """

    def get(
        self, name: str | None, must: bool = False
    ) -> prelude.SelectedInstantVector:
        """
        Returns a new SelectedInstantVector with the provieded name. If name is None,
        the vector will not use the named vector shorthand syntax (so an explicit
        __name__ matcher may be necessary).
        """
        vec = prelude.SelectedInstantVector(name=name)
        if must:
            vec.annotate(assertions.assert_exists)

        return vec

    @property
    def must(self) -> "Selector":
        """
        Return a selector that automatically asserts the existence of selections.

        This is useful when vectors are used in a context where assertions can be
        evaluated, such as when writing alerts. Since the assertion is added via vector
        annotations, a 'must' selected vector is no different from a regular vector
        in contexts where annotations aren't evaluated.
        """
        return _MustSelectorDelegate(self)

    def __getattr__(self, name: str, /) -> prelude.SelectedInstantVector:
        """
        Returns a SelectedInstantVector with __name__ equal to the name of the
        attribute.
        """
        return self.get(name)


class _MustSelectorDelegate(Selector):
    _parent: Selector

    def __init__(self, parent: Selector) -> None:
        self._parent = parent

    def __getattr__(self, name: str, /) -> prelude.SelectedInstantVector:
        return self._parent.get(name, must=True)
