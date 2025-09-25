from heracles.ql import prelude


def absent_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("absent_over_time", vector)


def ascent_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("ascent_over_time", vector)


def avg_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("avg_over_time", vector)


def changes(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("changes", vector)


def changes_prometheus(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("changes_prometheus", vector)


def count_eq_over_time(
    vector: prelude.RangeVector, eq: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("count_eq_over_time", vector, eq)


def count_gt_over_time(
    vector: prelude.RangeVector, gt: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("count_gt_over_time", vector, gt)


def count_le_over_time(
    vector: prelude.RangeVector, le: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("count_le_over_time", vector, le)


def count_ne_over_time(
    vector: prelude.RangeVector, ne: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("count_ne_over_time", vector, ne)


def count_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("count_over_time", vector)


def count_values_over_time(
    label: str, vector: prelude.RangeVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("count_values_over_time", label, vector)


def decreases_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("decreases_over_time", vector)


def default_rollup(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("default_rollup", vector)


def delta(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("delta", vector)


def delta_prometheus(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("delta_prometheus", vector)


def deriv(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("deriv", vector)


def deriv_fast(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("deriv_fast", vector)


def descent_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("descent_over_time", vector)


def distinct_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("distinct_over_time", vector)


def duration_over_time(
    vector: prelude.RangeVector, max_interval: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("duration_over_time", vector, max_interval)


def first_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("first_over_time", vector)


def geomean_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("geomean_over_time", vector)


def histogram_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("histogram_over_time", vector)


def hoeffding_bound_lower(
    phi: int | float | prelude.InstantVector, vector: prelude.RangeVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("hoeffding_bound_lower", phi, vector)


def hoeffding_bound_upper(
    phi: int | float | prelude.InstantVector, vector: prelude.RangeVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("hoeffding_bound_upper", phi, vector)


def holt_winters(
    vector: prelude.RangeVector,
    sf: int | float | prelude.InstantVector,
    tf: int | float | prelude.InstantVector,
) -> prelude.RollupFunc:
    return prelude.RollupFunc("holt_winters", vector, sf, tf)


def idelta(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("idelta", vector)


def ideriv(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("ideriv", vector)


def increase(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("increase", vector)


def increase_prometheus(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("increase_prometheus", vector)


def increase_pure(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("increase_pure", vector)


def increases_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("increases_over_time", vector)


def integrate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("integrate", vector)


def irate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("irate", vector)


def lag(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("lag", vector)


def last_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("last_over_time", vector)


def lifetime(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("lifetime", vector)


def mad_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("mad_over_time", vector)


def max_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("max_over_time", vector)


def median_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("median_over_time", vector)


def min_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("min_over_time", vector)


def mode_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("mode_over_time", vector)


def outlier_iqr_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("outlier_iqr_over_time", vector)


def predict_linear(
    vector: prelude.RangeVector, t: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("predict_linear", vector, t)


def present_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("present_over_time", vector)


def quantile_over_time(
    phi: int | float | prelude.InstantVector, vector: prelude.RangeVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("quantile_over_time", phi, vector)


def range_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("range_over_time", vector)


def rate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rate", vector)


def rate_over_sum(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rate_over_sum", vector)


def resets(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("resets", vector)


def rollup(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rollup", vector)


def rollup_candlestick(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rollup_candlestick", vector)


def rollup_delta(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rollup_delta", vector)


def rollup_deriv(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rollup_deriv", vector)


def rollup_increase(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rollup_increase", vector)


def rollup_rate(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rollup_rate", vector)


def rollup_scrape_interval(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("rollup_scrape_interval", vector)


def scrape_interval(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("scrape_interval", vector)


def share_gt_over_time(
    vector: prelude.RangeVector, gt: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("share_gt_over_time", vector, gt)


def share_le_over_time(
    vector: prelude.RangeVector, le: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("share_le_over_time", vector, le)


def share_eq_over_time(
    vector: prelude.RangeVector, eq: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("share_eq_over_time", vector, eq)


def stale_samples_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("stale_samples_over_time", vector)


def stddev_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("stddev_over_time", vector)


def stdvar_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("stdvar_over_time", vector)


def sum_eq_over_time(
    vector: prelude.RangeVector, eq: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("sum_eq_over_time", vector, eq)


def sum_gt_over_time(
    vector: prelude.RangeVector, gt: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("sum_gt_over_time", vector, gt)


def sum_le_over_time(
    vector: prelude.RangeVector, le: int | float | prelude.InstantVector
) -> prelude.RollupFunc:
    return prelude.RollupFunc("sum_le_over_time", vector, le)


def sum_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("sum_over_time", vector)


def sum2_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("sum2_over_time", vector)


def timestamp(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("timestamp", vector)


def timestamp_with_name(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("timestamp_with_name", vector)


def tfirst_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("tfirst_over_time", vector)


def tlast_change_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("tlast_change_over_time", vector)


def tlast_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("tlast_over_time", vector)


def tmax_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("tmax_over_time", vector)


def tmin_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("tmin_over_time", vector)


def zscore_over_time(vector: prelude.RangeVector) -> prelude.RollupFunc:
    return prelude.RollupFunc("zscore_over_time", vector)


def any(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("any", *vector)


def avg(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("avg", *vector)


def bottomk(
    k: int | float | prelude.InstantVector, vector: prelude.InstantOrRangeVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("bottomk", k, vector)


def bottomk_avg(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("bottomk_avg", k, vector, other_label)


def bottomk_last(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("bottomk_last", k, vector, other_label)


def bottomk_max(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("bottomk_max", k, vector, other_label)


def bottomk_median(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("bottomk_median", k, vector, other_label)


def bottomk_min(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("bottomk_min", k, vector, other_label)


def count(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("count", *vector)


def count_values(label: str, *vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("count_values", label, *vector)


def distinct(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("distinct", *vector)


def geomean(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("geomean", *vector)


def group(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("group", *vector)


def histogram(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("histogram", *vector)


def limitk(
    k: int | float | prelude.InstantVector, *vector: prelude.InstantOrRangeVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("limitk", k, *vector)


def mad(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("mad", *vector)


def max(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("max", *vector)


def median(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("median", *vector)


def min(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("min", *vector)


def mode(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("mode", *vector)


def outliers_iqr(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("outliers_iqr", *vector)


def outliers_mad(
    tolerance: int | float | prelude.InstantVector,
    *vector: prelude.InstantOrRangeVector,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("outliers_mad", tolerance, *vector)


def outliersk(
    k: int | float | prelude.InstantVector, *vector: prelude.InstantOrRangeVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("outliersk", k, *vector)


def quantile(
    phi: int | float | prelude.InstantVector, *vector: prelude.InstantOrRangeVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("quantile", phi, *vector)


def share(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("share", *vector)


def stddev(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("stddev", *vector)


def stdvar(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("stdvar", *vector)


def sum(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("sum", *vector)


def sum2(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("sum2", *vector)


def topk(
    k: int | float | prelude.InstantVector, vector: prelude.InstantOrRangeVector
) -> prelude.AggrFunc:
    return prelude.AggrFunc("topk", k, vector)


def topk_avg(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("topk_avg", k, vector, other_label)


def topk_last(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("topk_last", k, vector, other_label)


def topk_max(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("topk_max", k, vector, other_label)


def topk_median(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("topk_median", k, vector, other_label)


def topk_min(
    k: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
    other_label: str | None,
) -> prelude.AggrFunc:
    return prelude.AggrFunc("topk_min", k, vector, other_label)


def zscore(*vector: prelude.InstantOrRangeVector) -> prelude.AggrFunc:
    return prelude.AggrFunc("zscore", *vector)


def abs(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("abs", vector)


def absent(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("absent", vector)


def acos(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("acos", vector)


def acosh(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("acosh", vector)


def asin(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("asin", vector)


def asinh(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("asinh", vector)


def atan(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("atan", vector)


def atanh(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("atanh", vector)


def bitmap_and(
    vector: prelude.InstantOrRangeVector, mask: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("bitmap_and", vector, mask)


def bitmap_or(
    vector: prelude.InstantOrRangeVector, mask: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("bitmap_or", vector, mask)


def bitmap_xor(
    vector: prelude.InstantOrRangeVector, mask: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("bitmap_xor", vector, mask)


def buckets_limit(
    limit: int | float | prelude.InstantVector,
    buckets: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("buckets_limit", limit, buckets)


def ceil(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("ceil", vector)


def clamp(
    vector: prelude.InstantOrRangeVector,
    min: int | float | prelude.InstantVector,
    max: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("clamp", vector, min, max)


def clamp_max(
    vector: prelude.InstantOrRangeVector, max: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("clamp_max", vector, max)


def clamp_min(
    vector: prelude.InstantOrRangeVector, min: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("clamp_min", vector, min)


def cos(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("cos", vector)


def cosh(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("cosh", vector)


def day_of_month(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("day_of_month", vector)


def day_of_week(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("day_of_week", vector)


def day_of_year(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("day_of_year", vector)


def days_in_month(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("days_in_month", vector)


def deg(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("deg", vector)


def drop_empty_series(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("drop_empty_series", vector)


def end() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "end",
    )


def exp(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("exp", vector)


def floor(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("floor", vector)


def histogram_avg(
    buckets: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_avg", buckets)


def histogram_quantile(
    phi: int | float | prelude.InstantVector,
    buckets: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_quantile", phi, buckets)


def histogram_share(
    le: int | float | prelude.InstantVector,
    buckets: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_share", le, buckets)


def histogram_stddev(
    buckets: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_stddev", buckets)


def histogram_stdvar(
    buckets: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("histogram_stdvar", buckets)


def hour(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("hour", vector)


def interpolate(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("interpolate", vector)


def keep_last_value(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("keep_last_value", vector)


def keep_next_value(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("keep_next_value", vector)


def limit_offset(
    limit: int | float | prelude.InstantVector,
    offset: int | float | prelude.InstantVector,
    vector: prelude.InstantOrRangeVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("limit_offset", limit, offset, vector)


def ln(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("ln", vector)


def log2(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("log2", vector)


def log10(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("log10", vector)


def minute(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("minute", vector)


def month(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("month", vector)


def now() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "now",
    )


def pi() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "pi",
    )


def rad(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("rad", vector)


def prometheus_buckets(
    buckets: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("prometheus_buckets", buckets)


def rand(seed: int | float | prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("rand", seed)


def rand_exponential(
    seed: int | float | prelude.InstantVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("rand_exponential", seed)


def rand_normal(seed: int | float | prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("rand_normal", seed)


def range_avg(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_avg", vector)


def range_first(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_first", vector)


def range_last(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_last", vector)


def range_linear_regression(
    vector: prelude.InstantOrRangeVector,
) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_linear_regression", vector)


def range_mad(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_mad", vector)


def range_max(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_max", vector)


def range_median(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_median", vector)


def range_min(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_min", vector)


def range_normalize(*vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_normalize", *vector)


def range_quantile(
    phi: int | float | prelude.InstantVector, vector: prelude.InstantOrRangeVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_quantile", phi, vector)


def range_stddev(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_stddev", vector)


def range_stdvar(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_stdvar", vector)


def range_sum(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_sum", vector)


def range_trim_outliers(
    k: int | float | prelude.InstantVector, vector: prelude.InstantOrRangeVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_trim_outliers", k, vector)


def range_trim_spikes(
    phi: int | float | prelude.InstantVector, vector: prelude.InstantOrRangeVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_trim_spikes", phi, vector)


def range_trim_zscore(
    z: int | float | prelude.InstantVector, vector: prelude.InstantOrRangeVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_trim_zscore", z, vector)


def range_zscore(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("range_zscore", vector)


def remove_resets(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("remove_resets", vector)


def round(
    vector: prelude.InstantOrRangeVector, nearest: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("round", vector, nearest)


def ru(
    free: int | float | prelude.InstantVector, max: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("ru", free, max)


def running_avg(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("running_avg", vector)


def running_max(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("running_max", vector)


def running_min(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("running_min", vector)


def running_sum(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("running_sum", vector)


def scalar(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("scalar", vector)


def sgn(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sgn", vector)


def sin(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sin", vector)


def sinh(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sinh", vector)


def tan(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("tan", vector)


def tanh(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("tanh", vector)


def smooth_exponential(
    vector: prelude.InstantOrRangeVector, sf: int | float | prelude.InstantVector
) -> prelude.TransformFunc:
    return prelude.TransformFunc("smooth_exponential", vector, sf)


def sort(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sort", vector)


def sort_desc(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sort_desc", vector)


def sqrt(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("sqrt", vector)


def start() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "start",
    )


def step() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "step",
    )


def time() -> prelude.TransformFunc:
    return prelude.TransformFunc(
        "time",
    )


def timezone_offset(tz: int | float | prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("timezone_offset", tz)


def ttf(free: int | float | prelude.InstantVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("ttf", free)


def union(*vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("union", *vector)


def vector(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("vector", vector)


def year(vector: prelude.InstantOrRangeVector) -> prelude.TransformFunc:
    return prelude.TransformFunc("year", vector)


def alias(
    vector: prelude.InstantOrRangeVector, name: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("alias", vector, name)


def drop_common_labels(
    *vector: prelude.InstantOrRangeVector,
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("drop_common_labels", *vector)


def label_del(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_del", vector, *label1)


def label_graphite_group(
    vector: prelude.InstantOrRangeVector,
    *groupNum1: int | float | prelude.InstantVector,
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_graphite_group", vector, *groupNum1)


def label_join(
    vector: prelude.InstantOrRangeVector,
    dst_label: str,
    separator: str,
    *src_label1: str,
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc(
        "label_join", vector, dst_label, separator, *src_label1
    )


def label_keep(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_keep", vector, *label1)


def label_lowercase(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_lowercase", vector, *label1)


def label_match(
    vector: prelude.InstantOrRangeVector, label: str, regexp: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_match", vector, label, regexp)


def label_mismatch(
    vector: prelude.InstantOrRangeVector, label: str, regexp: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_mismatch", vector, label, regexp)


def label_replace(
    vector: prelude.InstantOrRangeVector,
    dst_label: str,
    replacement: str,
    src_label: str,
    regex: str,
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc(
        "label_replace", vector, dst_label, replacement, src_label, regex
    )


def label_transform(
    vector: prelude.InstantOrRangeVector, label: str, regexp: str, replacement: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc(
        "label_transform", vector, label, regexp, replacement
    )


def label_uppercase(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_uppercase", vector, *label1)


def label_value(
    vector: prelude.InstantOrRangeVector, label: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("label_value", vector, label)


def labels_equal(
    vector: prelude.InstantOrRangeVector, label1: str, *label2: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("labels_equal", vector, label1, *label2)


def sort_by_label(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("sort_by_label", vector, *label1)


def sort_by_label_desc(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("sort_by_label_desc", vector, *label1)


def sort_by_label_numeric(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("sort_by_label_numeric", vector, *label1)


def sort_by_label_numeric_desc(
    vector: prelude.InstantOrRangeVector, *label1: str
) -> prelude.LabelManipulationFunc:
    return prelude.LabelManipulationFunc("sort_by_label_numeric_desc", vector, *label1)
