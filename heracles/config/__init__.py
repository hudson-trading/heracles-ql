import importlib.util

_required_deps = ("pydantic", "yaml")

if any(not importlib.util.find_spec(dep) for dep in _required_deps):
    raise ImportError(
        "missing required dependency. Make sure to install the alerts extra to use"
        " this module. "
    )


from heracles.config.rule import *  # noqa
from heracles.config.contexts import *  # noqa
from heracles.config.generation import *  # noqa
from heracles.config import utils  # noqa
