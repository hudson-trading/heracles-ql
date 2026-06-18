import pytest

from heracles import promql
from heracles import ql as metricsql


def test_common_promql_expression() -> None:
    vectors = promql.Selector()
    expression = promql.sum(
        promql.rate(vectors.http_requests_total(method="GET")[5 * promql.Minute])
    ).by("service")

    assert (
        promql.render(expression)
        == 'sum(rate(http_requests_total{method="GET"}[5m])) by (service)'
    )


def test_promql_specific_signatures() -> None:
    vectors = promql.Selector()

    assert promql.day_of_week().render() == "day_of_week()"
    assert promql.timestamp(vectors.up).render() == "timestamp(up{})"
    assert (
        promql.histogram_fraction(0, 0.2, vectors.request_duration).render()
        == "histogram_fraction(0, 0.2, request_duration{})"
    )
    assert promql.limit_ratio(0.1, vectors.up).render() == "limit_ratio(0.1, up{})"


def test_metricsql_function_is_rejected() -> None:
    expression = metricsql.running_sum(promql.Selector().requests)

    with pytest.raises(
        promql.PromQLValidationError,
        match="function 'running_sum' is not supported by PromQL",
    ):
        promql.render(expression)


def test_metricsql_aggregator_is_rejected() -> None:
    expression = metricsql.median(promql.Selector().requests)

    with pytest.raises(
        promql.PromQLValidationError,
        match="aggregator 'median' is not supported by PromQL",
    ):
        promql.render(expression)


def test_nested_metricsql_function_is_rejected() -> None:
    # the offending function is nested inside a valid PromQL aggregator, so the
    # validator must descend through the whole tree rather than only check the root.
    vectors = promql.Selector()
    expression = promql.sum(metricsql.running_sum(vectors.up))

    with pytest.raises(
        promql.PromQLValidationError,
        match="function 'running_sum' is not supported by PromQL",
    ):
        promql.render(expression)


def test_nested_metricsql_function_inside_finalized_aggregator_is_rejected() -> None:
    vectors = promql.Selector()
    expression = promql.sum(metricsql.running_sum(vectors.up)).by("job")

    with pytest.raises(
        promql.PromQLValidationError,
        match="function 'running_sum' is not supported by PromQL",
    ):
        promql.render(expression)


def test_aggregators_are_a_subset_of_functions() -> None:
    # every aggregator name must also be a known function, both so validation of a
    # finalized aggregator (sum(...).by(...)) succeeds and so the two sets can't drift.
    assert promql.PROMQL_AGGREGATORS <= promql.PROMQL_FUNCTIONS


def test_time_durations_are_accepted() -> None:
    vectors = promql.Selector()
    assert promql.render(promql.rate(vectors.up[5 * promql.Minute])) == "rate(up{}[5m])"


def test_interval_range_duration_is_rejected() -> None:
    # the `Ni` step-duration syntax is a MetricsQL extension, invalid in PromQL.
    vectors = promql.Selector()
    with pytest.raises(promql.PromQLValidationError, match="interval duration '5i'"):
        promql.render(promql.rate(vectors.up[5 * metricsql.I]))


def test_interval_offset_duration_is_rejected() -> None:
    vectors = promql.Selector()
    with pytest.raises(promql.PromQLValidationError, match="interval duration"):
        promql.render(vectors.up.offset(5 * metricsql.I))


def test_interval_subquery_resolution_is_rejected() -> None:
    vectors = promql.Selector()
    expression = promql.rate(vectors.up[5 * promql.Minute : 1 * metricsql.I])
    with pytest.raises(promql.PromQLValidationError, match="interval duration"):
        promql.render(expression)


def test_histogram_quantiles_requires_a_quantile() -> None:
    vectors = promql.Selector()
    assert (
        promql.render(promql.histogram_quantiles(vectors.up, "quantile", 0.9, 0.99))
        == 'histogram_quantiles(up{}, "quantile", 0.9, 0.99)'
    )
    with pytest.raises(TypeError):
        promql.histogram_quantiles(vectors.up, "quantile")
