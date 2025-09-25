# Use this file to define the query which Delos will display!
# This script executes inside the provided venv, so code from your project is directly
# callable.
#
# Delos expects a variable named 'VECTOR' which contains a query. `VECTOR` can also be
# a function.

from heracles import ql

VECTOR = ql.ScalarLiteral(42)
