from collections.abc import Callable
from typing import Any

from heracles.ql import prelude

# this file contains function definitions which couldn't be extracted from Victoria
# Metrics markdown docs


def aggr_over_time(
    vector: prelude.RangeVector, *rollups: Callable[..., prelude.RollupFunc]
) -> prelude.AggrFunc:
    rollup_names = [r.__name__ for r in rollups]
    return prelude.AggrFunc("aggr_over_time", *rollup_names, vector)


def quantiles_over_time(
    phi_label: str,
    *phi: int | float | prelude.InstantVector,
    vector: prelude.RangeVector,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("quantiles_over_time", phi_label, *phi, vector)


def quantiles(
    phi_label: str,
    *phi: int | float | prelude.InstantVector,
    vector: prelude.RangeVector,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("quantiles", phi_label, *phi, vector)


def histogram_quantiles(
    phi_label: str,
    *phi: int | float | prelude.InstantVector,
    vector: prelude.InstantVector,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("histogram_quantiles", phi_label, *phi, vector)


def label_copy(
    vector: prelude.InstantVector, *labels: tuple[str, str]
) -> prelude.LabelManipulationFunc:
    args: list[Any] = [vector]
    for pair in labels:
        args.extend(pair)
    return prelude.LabelManipulationFunc("label_copy", *args)


def label_map(
    vector: prelude.InstantVector, label: str, *label_pairs: tuple[str, str]
) -> prelude.LabelManipulationFunc:
    args: list[Any] = [vector, label]
    for pair in label_pairs:
        args.extend(pair)
    return prelude.LabelManipulationFunc("label_map", *args)


def label_move(
    vector: prelude.InstantVector, *labels: tuple[str, str]
) -> prelude.LabelManipulationFunc:
    args: list[Any] = [vector]
    for pair in labels:
        args.extend(pair)
    return prelude.LabelManipulationFunc("label_move", *args)


def label_set(
    vector: prelude.InstantVector, **labels: str
) -> prelude.LabelManipulationFunc:
    args: list[Any] = [vector]
    for k, v in labels.items():
        args.extend((k, v))
    return prelude.LabelManipulationFunc("label_set", *args)
