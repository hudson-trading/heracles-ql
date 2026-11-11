from collections.abc import Callable

import pytest

from heracles import ql

STRING_CASES = [
    ("ascii", '"ascii"'),
    ('quote" slash\\', r'"quote\" slash\\"'),
    ("\n\t\r\b\f\0\x1f", r'"\n\t\r\b\f\u0000\u001f"'),
    ("café", '"café"'),
    ("東京", '"東京"'),
    ("🚀", '"🚀"'),
    ("𝄞", '"𝄞"'),
    ("\U0010ffff", '"\U0010ffff"'),
]


@pytest.mark.parametrize("value,literal", STRING_CASES)
def test_selector_string_literals(value: str, literal: str) -> None:
    assert ql.Selector().up(target=value).render() == f"up{{target={literal}}}"


@pytest.mark.parametrize("value,literal", STRING_CASES)
def test_function_string_literals(value: str, literal: str) -> None:
    expr = ql.label_set(ql.Selector().up, target=value)
    assert expr.render() == f'label_set(up{{}}, "target", {literal})'


@pytest.mark.parametrize(
    "matcher,operator",
    [(ql.EQ, "="), (ql.NE, "!="), (ql.RE, "=~"), (ql.NR, "!~")],
)
def test_matcher_string_literals(
    matcher: Callable[[str], ql.Matcher], operator: str
) -> None:
    expr = ql.Selector().up(target=matcher("🚀"))
    assert expr.render() == f'up{{target{operator}"🚀"}}'


def test_tuple_matcher_string_literals() -> None:
    expr = ql.Selector().up(target=(ql.RE("🚀.*"), ql.NE("🚀test")))
    assert expr.render() == 'up{target=~"🚀.*",target!="🚀test"}'
