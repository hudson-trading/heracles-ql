# HeraclesQL - A Python DSL for writing VictoriaMetrics Queries

### 🚧 HeraclesQL is available now, but this repo is still under construction! 🚧

HeraclesQL is a Python package which provides a type-safe embedded domain specific language for
writing VictoriaMetrics MetricsQL queries.

Highlights include:
  - MetricsQL-like syntax - HeraclesQL will be immediately familiar to anyone who's written MetricsQL or PromQL!
  - Custom Functions and Parameterizable Expressions - No more copy and pasting behavior between alerts!
  - Static Type Safety - MyPy and your editor will catch common problems before they occur!
  - Variables - Complicated alerts can be expressed imperatively!
  - Meta-alerts - Generate alerts about your alerts to avoid common pitfalls!

## Installation

HeraclesQL is available on PyPi. Just `pip install heracles-ql`

HeraclesQL depends on native code in a few places. Right now, we provide binaries for `manylinux_2_34_x86_64`.

Otherwise, we provide an sdist that includes the native source code. In order to build the sdist, you'll need a
modern Go compiler.

## Example

HeraclesQL lets you write MetricsQL queries as Python. For example,

```python
from heracles import ql

v = ql.Selector()

my_query = ql.rate(v.my_interesting_metric(useful="label")[5 * ql.Minute])

print(ql.format(my_query.render()))

# rate(my_interesting_metric{useful="label"}[5m])
```

## PromQL

HeraclesQL also speaks Prometheus' PromQL. Import `heracles.promql` instead of
`heracles.ql`: it exposes the same query-building API restricted to the functions and
aggregators Prometheus supports, and `promql.render` validates that an expression stays
within the PromQL dialect before rendering it.

```python
from heracles import promql

v = promql.Selector()

my_query = promql.sum(
    promql.rate(v.http_requests_total(code="500")[5 * promql.Minute])
).by("job")

print(promql.render(my_query))

# sum(rate(http_requests_total{code="500"}[5m])) by (job)
```

The PromQL function and aggregator bindings are generated from the Prometheus
documentation (`make generate_promql_funcs`), so they track a pinned Prometheus release.
