import pytest

from heracles import ql


@pytest.mark.parametrize(
    "duration,expected",
    [
        (-5 * ql.Minute, "-5m"),
        (-1 * (ql.Hour + 30 * ql.Minute), "-1h30m"),
        (-1 * ql.Millisecond, "-1ms"),
        (-1.5 * ql.Millisecond, "-1.5ms"),
        (ql.Minute - ql.Hour, "-59m"),
        (ql.Hour + 30 * ql.Minute, "1h30m"),
        (0 * ql.Minute, "0ms"),
        (2 * ql.I, "2i"),
        (-2 * ql.I, "-2i"),
        (5 * ql.Minute + 2 * ql.I, "5m2i"),
        (5 * ql.Minute - 2 * ql.I, "5m-2i"),
        (2 * ql.I - 5 * ql.Minute, "2i-5m"),
        (-5 * ql.Minute - 2 * ql.I, "-5m-2i"),
    ],
)
def test_duration_rendering_preserves_signs(
    duration: ql.Duration, expected: str
) -> None:
    assert duration.render() == expected


def test_negative_duration_offsets() -> None:
    vector = ql.SelectedInstantVector(name="metric")
    offset = -5 * ql.Minute
    assert vector.offset(offset).render() == "(metric{} offset -5m)"
    assert vector[ql.Hour].offset(offset).render() == "(metric{}[1h] offset -5m)"
