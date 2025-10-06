import datetime

from heracles.unittest import generators


def test_square_wave() -> None:
    wave = generators.drain(
        generators.square_wave(
            1, 0, datetime.timedelta(seconds=20), datetime.timedelta(seconds=5)
        ),
        10,
    )

    assert [s.value for s in wave] == [1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]
