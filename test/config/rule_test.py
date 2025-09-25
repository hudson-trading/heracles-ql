from heracles import config, ql


def test_serialization_has_expected_fields() -> None:
    rules = config.RuleBundle(name="test_bundle")

    @rules.alert()
    def TestingRule() -> config.Alert:
        return config.SimpleAlert(
            expr=rules.vectors().example_metric * 42,
            for_=5 * ql.Minute,
            fire_for=10 * ql.Minute,
            labels={
                "severity": "warning",
                "some_other_label": "foobar",
            },
            annotations={
                "example": "example",
            },
        )

    @rules.alert()
    def TestingRuleWithNulls() -> config.Alert:
        return config.SimpleAlert(
            expr=rules.vectors().example_metric * 42,
        )

    @rules.record("some:recording:rule")
    def testing_recording_rule() -> config.Recording:
        return config.SimpleRecording(
            expr=ql.rate(rules.vectors().example_metric[7 * ql.Minute]),
            labels={"foo": "bar"},
        )

    result = rules.record(rules.vectors().test_metric * 2, "test:adhoc:rule")
    assert isinstance(result, ql.SelectedInstantVector)
    assert result.render() == "test:adhoc:rule{}"

    dumped_rules = list(rules.dump())
    assert len(dumped_rules) == 4

    assert dumped_rules[0].name == "TestingRule"
    assert type(dumped_rules[0]) is config.RealizedAlert
    assert dumped_rules[1].name == "TestingRuleWithNulls"
    assert type(dumped_rules[1]) is config.RealizedAlert
    assert dumped_rules[2].name == "some:recording:rule"
    assert type(dumped_rules[2]) is config.RealizedRecording
    assert dumped_rules[3].name == "test:adhoc:rule"
    assert type(dumped_rules[3]) is config.RealizedRecording

    assert dumped_rules[0].model_dump(serialize_as_any=True, exclude_none=True) == {
        "alert": "TestingRule",
        "expr": "example_metric * 42.0",
        "for": "5m",
        "fire_for": "10m",
        "labels": {
            "severity": "warning",
            "some_other_label": "foobar",
        },
        "annotations": {
            "example": "example",
        },
    }

    assert dumped_rules[1].model_dump(serialize_as_any=True, exclude_none=True) == {
        "alert": "TestingRuleWithNulls",
        "expr": "example_metric * 42.0",
    }

    assert dumped_rules[2].model_dump(serialize_as_any=True, exclude_none=True) == {
        "record": "some:recording:rule",
        "expr": "rate(example_metric[7m])",
        "labels": {
            "foo": "bar",
        },
    }

    assert dumped_rules[3].model_dump(serialize_as_any=True, exclude_none=True) == {
        "record": "test:adhoc:rule",
        "expr": "test_metric * 2.0",
    }


def test_rename_alert_rule() -> None:
    assert config.RuleBundle._rename_alert_rule("simple") == "Simple"
    assert config.RuleBundle._rename_alert_rule("multiple_words") == "MultipleWords"
    assert (
        config.RuleBundle._rename_alert_rule("many_under_scores") == "ManyUnderScores"
    )
    assert config.RuleBundle._rename_alert_rule("a_b_c") == "ABC"
    assert config.RuleBundle._rename_alert_rule("CamelCase") == "CamelCase"


def test_rename_recording_rule() -> None:
    assert config.RuleBundle._rename_recording_rule("simple") == "simple"
    assert (
        config.RuleBundle._rename_recording_rule("multiple_words") == "multiple:words"
    )
    assert (
        config.RuleBundle._rename_recording_rule("many_under_scores")
        == "many:under:scores"
    )
    assert config.RuleBundle._rename_recording_rule("a_b_c") == "a:b:c"
