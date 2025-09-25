from heracles.ql import prelude

# Time constants
Millisecond = prelude.Duration.from_units(1, prelude.DurationUnit.millisecond)
Second = prelude.Duration.from_units(1, prelude.DurationUnit.second)
Minute = prelude.Duration.from_units(1, prelude.DurationUnit.minute)
Hour = prelude.Duration.from_units(1, prelude.DurationUnit.hour)
Day = prelude.Duration.from_units(1, prelude.DurationUnit.day)
Week = prelude.Duration.from_units(1, prelude.DurationUnit.week)
Year = prelude.Duration.from_units(1, prelude.DurationUnit.year)

I = prelude.Duration.from_interval(1)  # noqa E741
