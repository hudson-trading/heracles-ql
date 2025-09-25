from heracles.ql import prelude


class Selector:
    """
    Selector provides nicer syntax for selecting instant vectors.
    """

    def get(self, name: str | None) -> prelude.SelectedInstantVector:
        """
        Returns a new SelectedInstantVector with the provieded name. If name is None,
        the vector will not use the named vector shorthand syntax (so an explicit
        __name__ matcher may be necessary).
        """
        return prelude.SelectedInstantVector(name=name)

    def __getattr__(self, name: str, /) -> prelude.SelectedInstantVector:
        return self.get(name)
