import operator
from typing import Any

import pytest

from heracles import ql

comparison_ops = {
    ql.BinopKind.eq,
    ql.BinopKind.ne,
    ql.BinopKind.gt,
    ql.BinopKind.ge,
    ql.BinopKind.lt,
    ql.BinopKind.le,
}

set_ops = {ql.BinopKind.and_, ql.BinopKind.or_, ql.BinopKind.unless}

# wrapper_only_ops support float but only exist on wrapper types (e.g. ScalarLiteral)
wrapper_only_ops = {ql.BinopKind.atan2}


@pytest.mark.parametrize(
    "left,right,exclude",
    [
        pytest.param(
            ql.ScalarLiteral(42),
            ql.ScalarLiteral(5),
            set(),
        ),
        pytest.param(ql.ScalarLiteral(42), 5.0, set()),
        pytest.param(
            5.0, ql.ScalarLiteral(5), comparison_ops | set_ops | wrapper_only_ops
        ),
        pytest.param(
            ql.SelectedInstantVector(name="test"),
            ql.ScalarLiteral(42),
            set(),
        ),
        pytest.param(
            ql.ScalarLiteral(42),
            ql.SelectedInstantVector(name="test"),
            set(),
        ),
        pytest.param(
            ql.SelectedInstantVector(name="left"),
            ql.SelectedInstantVector(name="right"),
            set(),
        ),
        pytest.param(
            ql.SelectedInstantVector(name="left"),
            42.0,
            set(),
        ),
        pytest.param(
            42.0,
            ql.SelectedInstantVector(name="right"),
            comparison_ops | set_ops | wrapper_only_ops,
        ),
    ],
    ids=lambda v: (
        type(v).__name__
        if not isinstance(v, set)
        else f"excluding:'{','.join(op for op in v)}'"
    ),
)
def test_all_binops_implemented(
    left: Any, right: Any, exclude: set[ql.BinopKind]
) -> None:
    for op in ql.BinopKind:
        if op in exclude:
            continue
        if pyop := getattr(operator, op.name, None):
            print(f"{op} appears to be the python operator '{op.name}'")
            result: ql.Timeseries = pyop(left, right)
        elif pyop := getattr(left, op.name, None):
            print(
                f"{op} appears to be implemented as a method"
                f"' {type(left).__name__}.{op.name}'"
            )
            result = pyop(right)
        else:
            pytest.fail(
                f"no operator implementation found for"
                f" {type(left).__name__} {op} {type(right).__name__}"
            )
        rendered_left = left.render() if hasattr(left, "render") else str(left)
        rendered_right = right.render() if hasattr(right, "render") else str(right)
        assert result.render() == f"({rendered_left} {op.value} {rendered_right})", op


@pytest.mark.parametrize(
    "expr,result",
    [
        (
            ql.SelectedInstantVector(name="example_vector")(instance="foo"),
            'example_vector{instance="foo"}',
        ),
        (
            ql.SelectedInstantVector(name="example_vector")(instance="foo")[
                4 * ql.Minute
            ],
            'example_vector{instance="foo"}[4m]',
        ),
        (
            ql.SelectedInstantVector(name="example_vector")(instance="foo")[
                4 * ql.Minute
            ],
            'example_vector{instance="foo"}[4m]',
        ),
        (
            ql.rate(
                ql.SelectedInstantVector(name="example_vector")(instance="foo")[
                    4 * ql.Minute
                ]
            ),
            'rate(example_vector{instance="foo"}[4m])',
        ),
        (
            ql.rate(
                ql.SelectedInstantVector(name="example_vector")(instance="foo")[
                    4 * ql.Minute
                ]
            )
            * 42,
            'rate(example_vector{instance="foo"}[4m]) * 42.0',
        ),
        (
            ql.rate(
                ql.SelectedInstantVector(name="example_vector")(instance="foo")[
                    4 * ql.Minute
                ]
            )
            * ql.ScalarLiteral(42),
            'rate(example_vector{instance="foo"}[4m]) * 42.0',
        ),
        (
            (
                ql.rate(
                    ql.SelectedInstantVector(name="example_vector")(instance="foo")[
                        4 * ql.Minute
                    ]
                )
                * ql.ScalarLiteral(42)
            ).on("hostname"),
            'rate(example_vector{instance="foo"}[4m]) * on(hostname) 42.0',
        ),
        (
            (
                ql.avg(ql.SelectedInstantVector(name="example_vector")(instance="foo"))
            ).by("hostname", "colo"),
            'avg(example_vector{instance="foo"}) by(hostname,colo)',
        ),
        (
            (
                ql.avg(ql.SelectedInstantVector(name="example_vector")(instance="foo"))
            ).without("hostname", "colo"),
            'avg(example_vector{instance="foo"}) without(hostname,colo)',
        ),
        (
            ql.rate(
                (
                    ql.SelectedInstantVector(name="left")(instance="foo")
                    * ql.SelectedInstantVector(name="right")
                )[4 * ql.Minute : 1 * ql.Second]
            ),
            'rate((left{instance="foo"} * right)[4m:1s])',
        ),
        (
            ql.SelectedInstantVector(name="test") @ 7,
            "test @ 7.0",
        ),
        (
            ql.SelectedInstantVector(name="test")
            @ ql.SelectedInstantVector(name="offset_vector")(something="foo"),
            'test @ offset_vector{something="foo"}',
        ),
        (
            ql.rate(
                (
                    ql.SelectedInstantVector(name="test")
                    @ ql.SelectedInstantVector(name="offset_vector")(something="foo")
                )[4 * ql.Minute : 1 * ql.Second]
            ),
            'rate((test @ offset_vector{something="foo"})[4m:1s])',
        ),
        (
            ql.SelectedInstantVector(name="test").offset(7 * ql.Second),
            "test offset 7s",
        ),
        (
            ql.rate(
                (
                    ql.SelectedInstantVector(name="test")
                    @ ql.SelectedInstantVector(name="offset_vector")(something="foo")
                )[4 * ql.Minute : 1 * ql.Second]
            ).offset(10 * ql.Minute + 5 * ql.Second),
            'rate((test @ offset_vector{something="foo"})[4m:1s]) offset 10m5s',
        ),
        (
            ql.label_replace(
                ql.SelectedInstantVector(name="test"), "dest", "bar", "source", ".*"
            ),
            'label_replace(test, "dest", "bar", "source", ".*")',
        ),
        (
            ql.SelectedInstantVector(name="example_vector")(instance=r'"fo\.o'),
            r'example_vector{instance="\"fo\\.o"}',
        ),
        (5 * ql.Minute, "5m"),
        (0 * ql.Second, "0ms"),
        (
            ql.label_match(ql.SelectedInstantVector(name="test"), "foo", r"foo\|bar"),
            r'label_match(test, "foo", "foo\\|bar")',
        ),
    ],
)
def test_expressions(expr: ql.Timeseries, result: str) -> None:
    assert ql.format(expr.render()) == result
