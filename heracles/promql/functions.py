"""Typed constructors for functions and aggregators supported by PromQL."""

from heracles.ql import prelude

Scalar = int | float | prelude.InstantVector


def _transform(name: str, *args: object) -> prelude.TransformFunc:
    return prelude.TransformFunc(name, *args)


def _rollup(name: str, *args: object) -> prelude.RollupFunc:
    return prelude.RollupFunc(name, *args)


def _aggregate(name: str, *args: object) -> prelude.AggrFunc:
    return prelude.AggrFunc(name, *args)


# Functions taking one instant vector.
def abs(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("abs", vector)


def absent(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("absent", vector)


def acos(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("acos", vector)


def acosh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("acosh", vector)


def asin(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("asin", vector)


def asinh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("asinh", vector)


def atan(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("atan", vector)


def atanh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("atanh", vector)


def ceil(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("ceil", vector)


def cos(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("cos", vector)


def cosh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("cosh", vector)


def deg(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("deg", vector)


def exp(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("exp", vector)


def floor(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("floor", vector)


def histogram_avg(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("histogram_avg", vector)


def histogram_count(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("histogram_count", vector)


def histogram_stddev(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("histogram_stddev", vector)


def histogram_stdvar(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("histogram_stdvar", vector)


def histogram_sum(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("histogram_sum", vector)


def ln(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("ln", vector)


def log2(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("log2", vector)


def log10(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("log10", vector)


def rad(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("rad", vector)


def scalar(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("scalar", vector)


def sgn(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("sgn", vector)


def sin(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("sin", vector)


def sinh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("sinh", vector)


def sort(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("sort", vector)


def sort_desc(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("sort_desc", vector)


def sqrt(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("sqrt", vector)


def tan(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("tan", vector)


def tanh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("tanh", vector)


def timestamp(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return _transform("timestamp", vector)


# Calendar functions accept no argument in PromQL and default to vector(time()).
def _optional_vector(
    name: str, vector: prelude.InstantVector | None
) -> prelude.TransformFunc:
    return _transform(name, *(() if vector is None else (vector,)))


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


def clamp(
    vector: prelude.InstantVector, minimum: Scalar, maximum: Scalar
) -> prelude.TransformFunc:
    return _transform("clamp", vector, minimum, maximum)


def clamp_max(vector: prelude.InstantVector, maximum: Scalar) -> prelude.TransformFunc:
    return _transform("clamp_max", vector, maximum)


def clamp_min(vector: prelude.InstantVector, minimum: Scalar) -> prelude.TransformFunc:
    return _transform("clamp_min", vector, minimum)


def histogram_fraction(
    lower: Scalar, upper: Scalar, vector: prelude.InstantVector
) -> prelude.TransformFunc:
    return _transform("histogram_fraction", lower, upper, vector)


def histogram_quantile(
    phi: Scalar, vector: prelude.InstantVector
) -> prelude.TransformFunc:
    return _transform("histogram_quantile", phi, vector)


def label_join(
    vector: prelude.InstantVector, destination: str, separator: str, *source: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc(
        "label_join", vector, destination, separator, *source
    )


def label_replace(
    vector: prelude.InstantVector,
    destination: str,
    replacement: str,
    source: str,
    regex: str,
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc(
        "label_replace", vector, destination, replacement, source, regex
    )


def round(
    vector: prelude.InstantVector, nearest: Scalar | None = None
) -> prelude.TransformFunc:
    return _transform("round", vector, *((nearest,) if nearest is not None else ()))


def vector(scalar: Scalar) -> prelude.TransformFunc:
    return _transform("vector", scalar)


def pi() -> prelude.TransformFunc:
    return _transform("pi")


def time() -> prelude.TransformFunc:
    return _transform("time")


# Range-vector functions.
def absent_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("absent_over_time", vector)


def avg_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("avg_over_time", vector)


def changes(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("changes", vector)


def count_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("count_over_time", vector)


def delta(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("delta", vector)


def deriv(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("deriv", vector)


def idelta(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("idelta", vector)


def increase(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("increase", vector)


def irate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("irate", vector)


def last_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("last_over_time", vector)


def max_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("max_over_time", vector)


def min_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("min_over_time", vector)


def present_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("present_over_time", vector)


def rate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("rate", vector)


def resets(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("resets", vector)


def stddev_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("stddev_over_time", vector)


def stdvar_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("stdvar_over_time", vector)


def sum_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("sum_over_time", vector)


def predict_linear(vector: prelude.RangeVector, seconds: Scalar) -> prelude.RollupFunc:
    return _rollup("predict_linear", vector, seconds)


def quantile_over_time(phi: Scalar, vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("quantile_over_time", phi, vector)


# Aggregation operators. PromQL accepts exactly one input vector.
def avg(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("avg", vector)


def bottomk(k: Scalar, vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("bottomk", k, vector)


def count(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("count", vector)


def count_values(label: str, vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("count_values", label, vector)


def group(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("group", vector)


def limit_ratio(ratio: Scalar, vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("limit_ratio", ratio, vector)


def limitk(k: Scalar, vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("limitk", k, vector)


def max(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("max", vector)


def min(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("min", vector)


def quantile(phi: Scalar, vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("quantile", phi, vector)


def stddev(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("stddev", vector)


def stdvar(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("stdvar", vector)


def sum(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("sum", vector)


def topk(k: Scalar, vector: prelude.InstantVector) -> prelude.AggrFunc:
    return _aggregate("topk", k, vector)


# Functions requiring --enable-feature=promql-experimental-functions.
def double_exponential_smoothing(
    vector: prelude.RangeVector, smoothing_factor: Scalar, trend_factor: Scalar
) -> prelude.RollupFunc:
    return _rollup(
        "double_exponential_smoothing", vector, smoothing_factor, trend_factor
    )


def end() -> prelude.TransformFunc:
    return _transform("end")


def first_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("first_over_time", vector)


def histogram_quantiles(
    vector: prelude.InstantVector, label: str, *phi: Scalar
) -> prelude.TransformFunc:
    return _transform("histogram_quantiles", vector, label, *phi)


def info(
    vector: prelude.InstantVector,
    data_selector: prelude.InstantVector | None = None,
) -> prelude.TransformFunc:
    return _transform("info", vector, *((data_selector,) if data_selector else ()))


def mad_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("mad_over_time", vector)


def max_of(left: Scalar, right: Scalar) -> prelude.TransformFunc:
    return _transform("max_of", left, right)


def min_of(left: Scalar, right: Scalar) -> prelude.TransformFunc:
    return _transform("min_of", left, right)


def range() -> prelude.TransformFunc:
    return _transform("range")


def sort_by_label(vector: prelude.InstantVector, *labels: str) -> prelude.TransformFunc:
    return _transform("sort_by_label", vector, *labels)


def sort_by_label_desc(
    vector: prelude.InstantVector, *labels: str
) -> prelude.TransformFunc:
    return _transform("sort_by_label_desc", vector, *labels)


def start() -> prelude.TransformFunc:
    return _transform("start")


def step() -> prelude.TransformFunc:
    return _transform("step")


def ts_of_first_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("ts_of_first_over_time", vector)


def ts_of_last_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("ts_of_last_over_time", vector)


def ts_of_max_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("ts_of_max_over_time", vector)


def ts_of_min_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return _rollup("ts_of_min_over_time", vector)


PROMQL_FUNCTIONS = frozenset(
    name
    for name, value in globals().items()
    if callable(value) and not name.startswith("_") and name not in {"Scalar"}
)

PROMQL_AGGREGATORS = frozenset(
    {
        "avg",
        "bottomk",
        "count",
        "count_values",
        "group",
        "limit_ratio",
        "limitk",
        "max",
        "min",
        "quantile",
        "stddev",
        "stdvar",
        "sum",
        "topk",
    }
)

__all__ = sorted(PROMQL_FUNCTIONS)
