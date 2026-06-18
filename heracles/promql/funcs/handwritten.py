from heracles.ql import prelude

# this file contains function definitions which couldn't be extracted from the
# Prometheus markdown docs


# Calendar functions take an optional instant vector and default to vector(time()).
def _optional_vector(
    name: str, vector: prelude.InstantVector | None
) -> prelude.TransformFunc:
    return prelude.TransformFunc(name, *(() if vector is None else (vector,)))


def day_of_month(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("day_of_month", vector)


def day_of_week(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("day_of_week", vector)


def day_of_year(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("day_of_year", vector)


def days_in_month(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("days_in_month", vector)


def hour(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("hour", vector)


def minute(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("minute", vector)


def month(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("month", vector)


def year(vector: prelude.InstantVector | None = None) -> prelude.TransformFunc:
    return _optional_vector("year", vector)


def round(
    vector: prelude.InstantVector,
    to_nearest: int | float | prelude.InstantVector | None = None,
) -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "round", vector, *(() if to_nearest is None else (to_nearest,))
    )


def info(
    vector: prelude.InstantVector,
    data_label_selector: prelude.InstantVector | None = None,
) -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "info", vector, *(() if data_label_selector is None else (data_label_selector,))
    )


def label_join(
    vector: prelude.InstantVector, dst_label: str, separator: str, *src_label: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc(
        "label_join", vector, dst_label, separator, *src_label
    )


def histogram_quantiles(
    vector: prelude.InstantVector,
    quantile_label: str,
    phi: int | float | prelude.InstantVector,
    *phis: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    # PromQL requires between 1 and 10 quantiles, so the first phi is mandatory.
    return prelude.TransformFunc(
        "histogram_quantiles", vector, quantile_label, phi, *phis
    )
