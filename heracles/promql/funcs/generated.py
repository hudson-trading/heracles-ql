from heracles.ql import prelude


def abs(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("abs", vector)


def absent(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("absent", vector)


def absent_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("absent_over_time", vector)


def acos(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("acos", vector)


def acosh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("acosh", vector)


def asin(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("asin", vector)


def asinh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("asinh", vector)


def atan(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("atan", vector)


def atanh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("atanh", vector)


def avg(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("avg", vector)


def avg_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("avg_over_time", vector)


def bottomk(
    k: int | float | prelude.InstantVector, vector: prelude.InstantVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("bottomk", k, vector)


def ceil(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("ceil", vector)


def changes(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("changes", vector)


def clamp(
    vector: prelude.InstantVector,
    min: int | float | prelude.InstantVector,
    max: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("clamp", vector, min, max)


def clamp_max(
    vector: prelude.InstantVector, max: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("clamp_max", vector, max)


def clamp_min(
    vector: prelude.InstantVector, min: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("clamp_min", vector, min)


def cos(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("cos", vector)


def cosh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("cosh", vector)


def count(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("count", vector)


def count_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("count_over_time", vector)


def count_values(label: str, vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("count_values", label, vector)


def deg(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("deg", vector)


def delta(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("delta", vector)


def deriv(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("deriv", vector)


def double_exponential_smoothing(
    vector: prelude.RangeVector,
    sf: int | float | prelude.InstantVector,
    tf: int | float | prelude.InstantVector,
) -> prelude.RollupFunc:
    return prelude.RollupFunc("double_exponential_smoothing", vector, sf, tf)


def end() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "end",
    )


def exp(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("exp", vector)


def first_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("first_over_time", vector)


def floor(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("floor", vector)


def group(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("group", vector)


def histogram_avg(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_avg", vector)


def histogram_count(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_count", vector)


def histogram_fraction(
    lower: int | float | prelude.InstantVector,
    upper: int | float | prelude.InstantVector,
    vector: prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_fraction", lower, upper, vector)


def histogram_quantile(
    phi: int | float | prelude.InstantVector, vector: prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_quantile", phi, vector)


def histogram_stddev(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_stddev", vector)


def histogram_stdvar(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_stdvar", vector)


def histogram_sum(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_sum", vector)


def idelta(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("idelta", vector)


def increase(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("increase", vector)


def irate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("irate", vector)


def label_replace(
    vector: prelude.InstantVector,
    dst_label: str,
    replacement: str,
    src_label: str,
    regex: str,
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc(
        "label_replace", vector, dst_label, replacement, src_label, regex
    )


def last_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("last_over_time", vector)


def limit_ratio(
    ratio: int | float | prelude.InstantVector, vector: prelude.InstantVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("limit_ratio", ratio, vector)


def limitk(
    k: int | float | prelude.InstantVector, vector: prelude.InstantVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("limitk", k, vector)


def ln(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("ln", vector)


def log10(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("log10", vector)


def log2(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("log2", vector)


def mad_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("mad_over_time", vector)


def max(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("max", vector)


def max_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("max_over_time", vector)


def min(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("min", vector)


def min_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("min_over_time", vector)


def pi() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "pi",
    )


def predict_linear(
    vector: prelude.RangeVector, t: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("predict_linear", vector, t)


def present_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("present_over_time", vector)


def quantile(
    phi: int | float | prelude.InstantVector, vector: prelude.InstantVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("quantile", phi, vector)


def quantile_over_time(
    s: int | float | prelude.InstantVector, vector: prelude.RangeVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("quantile_over_time", s, vector)


def rad(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("rad", vector)


def range() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "range",
    )


def rate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rate", vector)


def resets(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("resets", vector)


def scalar(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("scalar", vector)


def sgn(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sgn", vector)


def sin(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sin", vector)


def sinh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sinh", vector)


def sort(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sort", vector)


def sort_by_label(vector: prelude.InstantVector, *label: str) -> prelude.TransformFunc:
    return prelude.TransformFunc("sort_by_label", vector, *label)


def sort_by_label_desc(
    vector: prelude.InstantVector, *label: str
) -> prelude.TransformFunc:
    return prelude.TransformFunc("sort_by_label_desc", vector, *label)


def sort_desc(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sort_desc", vector)


def sqrt(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sqrt", vector)


def start() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "start",
    )


def stddev(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("stddev", vector)


def stddev_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("stddev_over_time", vector)


def stdvar(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("stdvar", vector)


def stdvar_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("stdvar_over_time", vector)


def step() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "step",
    )


def sum(vector: prelude.InstantVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("sum", vector)


def sum_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("sum_over_time", vector)


def tan(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("tan", vector)


def tanh(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("tanh", vector)


def time() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "time",
    )


def timestamp(vector: prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("timestamp", vector)


def topk(
    k: int | float | prelude.InstantVector, vector: prelude.InstantVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("topk", k, vector)


def ts_of_first_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("ts_of_first_over_time", vector)


def ts_of_last_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("ts_of_last_over_time", vector)


def ts_of_max_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("ts_of_max_over_time", vector)


def ts_of_min_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("ts_of_min_over_time", vector)


def vector(s: int | float | prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("vector", s)
