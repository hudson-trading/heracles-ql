import inspect
from collections.abc import Callable
from typing import Annotated, Any, Literal, Union

import pytest

from heracles import config, ql


@pytest.mark.parametrize(
    "annotation,expected",
    [
        (ql.Selector, True),
        (object, True),
        (str, False),
        (list[str], False),
        (dict[str, str], False),
        (Callable[[str], str], False),
        (Literal["prod"], False),
        (Any, False),
        (inspect.Parameter.empty, False),
        (Annotated[ql.Selector, "selector"], True),
        (Annotated[list[str], "hosts"], False),
        (ql.Selector | None, True),
        (Union[list[str], ql.Selector], True),  # noqa: UP007 - cover typing.Union
        (Union[ql.Selector, list[str]], True),  # noqa: UP007 - cover both orders
        (list[str] | None, False),
    ],
)
def test_parameter_discovery_handles_typing_annotations(
    annotation: Any, expected: bool
) -> None:
    def factory(value: Any = None) -> config.Alert:
        return config.SimpleAlert(expr=ql.Selector().up)

    factory.__annotations__["value"] = annotation
    wrapper = config.WrappedRule(
        partial_fn=factory, overrides={}, hooks=config.Hooks(hooks=[])
    )
    parameters = wrapper.find_bindable_param(typ=ql.Selector)
    assert [p.name for p in parameters or []] == (["value"] if expected else [])
    assert bool(wrapper.find_bindable_param(name="value", typ=ql.Selector)) == expected


def test_generic_parameters_do_not_block_selector_injection() -> None:
    bundle = config.RuleBundle("generic")

    @bundle.alert()
    def alert(
        vectors: ql.Selector,
        hosts: list[str] | None = None,
        metadata: dict[str, int] | None = None,
    ) -> config.Alert:
        assert isinstance(vectors, ql.Selector)
        assert metadata is None
        return config.SimpleAlert(expr=vectors.up(host=(hosts or ["prod"])[0]))

    assert next(iter(bundle.dump())).expr.render() == 'up{host="prod"}'


def test_annotated_selectors_work_with_recording_factories() -> None:
    bundle = config.RuleBundle("annotated")

    @bundle.record()
    def recording(
        vectors: Annotated[ql.Selector, "selector"],
        transform: Callable[[str], str] = str,
    ) -> config.Recording:
        return config.SimpleRecording(expr=vectors.up(host=transform("prod")))

    assert next(iter(bundle.dump())).expr.render() == 'up{host="prod"}'


def test_named_context_injection_preserves_type_matching() -> None:
    bundle = config.RuleBundle("context", config.ServiceContext("prod"))

    @bundle.alert()
    def alert(
        vectors: ql.Selector, service_name: Annotated[str, "service"]
    ) -> config.Alert:
        return config.SimpleAlert(expr=vectors.up(service=service_name))

    rule = next(iter(bundle.dump()))
    assert rule.expr.render() == 'up{service="prod"}'
    assert rule.labels == {"service": "prod"}


def test_required_generic_parameter_remains_unbound() -> None:
    bundle = config.RuleBundle("required")

    @bundle.alert()
    def alert(hosts: list[str]) -> config.Alert:
        return config.SimpleAlert(expr=ql.Selector().up(host=hosts[0]))

    with pytest.raises(Exception, match="isn't fully applied"):
        list(bundle.dump())
