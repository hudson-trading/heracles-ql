from heracles import config

from . import fixtures


def test_project_finds_rules() -> None:
    proj = config.HeraclesProject(fixtures)

    bundles = sorted(
        [x.name for bundles in proj.rules_bundles.values() for x in bundles]
    )

    assert bundles == ["test.rules_a", "test.rules_b"]
