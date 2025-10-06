import datetime
from collections.abc import Callable, Iterable

from heracles.unittest import hermes


def zero_time() -> datetime.datetime:
    return datetime.datetime.fromtimestamp(0, tz=datetime.UTC)


def drain(i: Iterable[hermes.Sample], count: int) -> list[hermes.Sample]:
    return [s for (_, s) in zip(range(count), i)]


def square_wave(
    high: float,
    low: float,
    period: datetime.timedelta,
    interval: datetime.timedelta,
    start_time: datetime.datetime | None = None,
    start_low: bool = False,
) -> Iterable[hermes.Sample]:
    if period / 2 < interval:
        raise ValueError("period must be at least 2x interval")

    def f(t: datetime.datetime) -> float:
        period_half = ((t - zero_time()) // (period // 2)) % 2
        if period_half == 0:
            sample = low if start_low else high
        else:
            sample = high if start_low else low
        return sample

    return sample(f, interval, start_time=start_time)


def sample(
    f: Callable[[datetime.datetime], float],
    interval: datetime.timedelta,
    start_time: datetime.datetime | None = None,
) -> Iterable[hermes.Sample]:
    if start_time is None:
        start_time = zero_time()
    relative_time = zero_time()
    real_time = start_time
    while True:
        yield hermes.Sample(value=f(relative_time), timestamp=real_time)
        relative_time += interval
        real_time += interval
