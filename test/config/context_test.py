import pytest

from heracles import config, ql


def register_rule(bundle: config.RuleBundle, name: str, recording: bool) -> None:
    if recording:

        @bundle.record(name)
        def recording_rule() -> config.Recording:
            return config.SimpleRecording(expr=ql.Selector().up)

    else:

        @bundle.alert(name)
        def alert_rule() -> config.Alert:
            return config.SimpleAlert(expr=ql.Selector().up)


@pytest.mark.parametrize("recording", [False, True])
def test_context_membership_is_captured_at_registration(recording: bool) -> None:
    bundle = config.RuleBundle("scoped", config.ConstLabelContext(root="yes"))
    register_rule(bundle, "before", recording)
    with bundle.context(config.ConstLabelContext(team="first")):
        register_rule(bundle, "outer", recording)
        with bundle.context(config.ConstLabelContext(zone="east")):
            register_rule(bundle, "inner", recording)
        register_rule(bundle, "outer_after", recording)
    with bundle.context(config.ConstLabelContext(team="second")):
        register_rule(bundle, "sibling", recording)
    register_rule(bundle, "after", recording)

    expected = {
        "before": {"root": "yes"},
        "outer": {"root": "yes", "team": "first"},
        "inner": {"root": "yes", "team": "first", "zone": "east"},
        "outer_after": {"root": "yes", "team": "first"},
        "sibling": {"root": "yes", "team": "second"},
        "after": {"root": "yes"},
    }
    for _ in range(2):
        assert {rule.name: rule.labels for rule in bundle.dump()} == expected


@pytest.mark.parametrize("recording", [False, True])
def test_context_exit_after_exception_preserves_registered_rules(
    recording: bool,
) -> None:
    bundle = config.RuleBundle("exception")
    register_rule(bundle, "before", recording)
    with pytest.raises(RuntimeError, match="stop"):
        with bundle.context(config.ConstLabelContext(team="inside")):
            register_rule(bundle, "inside", recording)
            raise RuntimeError("stop")
    register_rule(bundle, "after", recording)

    assert {rule.name: rule.labels for rule in bundle.dump()} == {
        "before": {},
        "inside": {"team": "inside"},
        "after": {},
    }


@pytest.mark.parametrize("recording", [False, True])
def test_context_snapshot_preserves_context_objects(recording: bool) -> None:
    context = config.ConstLabelContext(owner="original")
    bundle = config.RuleBundle("shared_context")
    with bundle.context(context):
        register_rule(bundle, "inside", recording)
    context.labels["owner"] = "updated"

    assert next(iter(bundle.dump())).labels == {"owner": "updated"}


def test_later_context_does_not_generate_alerts_for_earlier_rules() -> None:
    bundle = config.RuleBundle("generated")
    register_rule(bundle, "before", recording=False)
    with bundle.context(config.AlertForMissingData()):
        register_rule(bundle, "inside", recording=False)
    register_rule(bundle, "after", recording=False)

    assert [rule.name for rule in bundle.dump()] == [
        "before",
        "inside",
        "insideDataMissing",
        "after",
    ]
