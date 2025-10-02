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


## Example

HeraclesQL lets you write MetricsQL queries as Python. For example,

```python
from heracles import ql

v = ql.Selector()

my_query = ql.rate(v.my_interesting_metric(useful="label")[5 * ql.Minute])

print(ql.format(my_query.render()))

# rate(my_interesting_metric{useful="label"}[5m])
```
