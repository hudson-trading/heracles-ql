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
