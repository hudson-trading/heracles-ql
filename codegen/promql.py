"""A marvelously evil script to generate Python implementations of PromQL functions
from the Prometheus documentation.

This is the PromQL sibling of ``codegen/markdown.py`` (which does the same job for
VictoriaMetrics MetricsQL). The two share the ``FunctionDef``/``FunctionArg``/
``FunctionSpecs`` machinery, but Prometheus documents its functions very differently
from VictoriaMetrics, so the parsing lives here.

Prometheus describes each function with a typed signature rendered as inline code, for
example ``clamp(v instant-vector, min scalar, max scalar)``. Argument types are one of
``instant-vector``, ``range-vector``, ``scalar`` or ``string``. Aggregation operators
live in a separate document (``operators.md``) and are written with single-letter,
untyped parameters such as ``topk(k, v)``.

As in the MetricsQL generator, signatures the simple heuristics here can't model
(default arguments, optional ``[bracketed]`` arguments, enumerated variadics such as
``φ_1, φ_2, ...``) are emitted as failed definitions. Their names are imported from a
hand-written ``handwritten.py`` instead, so a missing implementation fails the build.
"""

from __future__ import annotations

import pathlib
import re

import typer
from markdown import FailedFunctionDef, FunctionArg, FunctionDef, FunctionSpecs

cli = typer.Typer()

# Prometheus signature argument types -> python types. Scalars are modelled as
# ``int | float | prelude.InstantVector`` to match the MetricsQL generator: a scalar is
# just an instant vector with no labels, and python literals are boxed automatically.
SCALAR_TYPE = "int | float | prelude.InstantVector"
TYPE_TOKENS = {
    "instant-vector": "prelude.InstantVector",
    "range-vector": "prelude.RangeVector",
    "scalar": SCALAR_TYPE,
    "string": "str",
}

# Aggregation operators use single-letter, untyped parameters in operators.md.
AGGREGATOR_PARAMS = {
    "v": ("vector", "prelude.InstantVector"),
    "k": ("k", SCALAR_TYPE),
    "r": ("ratio", SCALAR_TYPE),
    "l": ("label", "str"),
    "phi": ("phi", SCALAR_TYPE),
}

# matches an inline-code function signature like `clamp(v instant-vector, min scalar)`
SIGNATURE_REGEX = re.compile(r"`([a-z_][a-z0-9_]*)\(([^`]*)\)`")
# a function defined purely by reference, e.g. sort_desc: "Same as `sort`, ..."
SAME_AS_REGEX = re.compile(r"[Ss]ame as `([a-z_][a-z0-9_]*)`")
# an enumerated argument name (φ_1, src_label_2, ...) signals a doc-shorthand variadic
# that the simple template can't express; defer to handwritten.py.
ENUMERATED_ARG_REGEX = re.compile(r"_\d+$")
IDENTIFIER_REGEX = re.compile(r"[a-z_][a-z0-9_]*$")


def _return_type(name: str, arg_types: list[str]) -> str:
    if name.startswith("label_"):
        return "prelude.LabelManipulationFunc"
    if "prelude.RangeVector" in arg_types:
        return "prelude.RollupFunc"
    return "prelude.TransformFunc"


def _is_definitional(args: str) -> bool:
    """A signature is a definition (rather than a usage example) if it takes no
    arguments or names at least one argument type."""
    return not args.strip() or any(token in args for token in TYPE_TOKENS)


def _synthesize_name(token: str, used: dict[str, int]) -> str:
    """Some signatures give a bare type with no argument name, e.g.
    ``avg_over_time(range-vector)``. Synthesize a stable, readable name."""
    base = {
        "instant-vector": "vector",
        "range-vector": "vector",
        "scalar": "s",
        "string": "label",
    }[token]
    used[base] = used.get(base, 0) + 1
    return base if used[base] == 1 else f"{base}{used[base]}"


def parse_signature(name: str, raw_args: str) -> FunctionDef | FailedFunctionDef:
    """Parse the argument list of a typed Prometheus signature into a FunctionDef.

    Returns a FailedFunctionDef (to be hand-written) for signatures the simple
    template cannot represent: default values, optional bracketed arguments, or
    enumerated variadics.
    """
    args = raw_args.replace("φ", "phi").strip()
    if not args:
        return FunctionDef(name=name, return_type="prelude.TransformFunc", args=[])

    parsed: list[FunctionArg] = []
    used_names: dict[str, int] = {}
    for raw in args.split(","):
        token = raw.strip()
        if not token:
            continue
        if token == "...":
            if not parsed:
                return FailedFunctionDef(name=name)
            parsed[-1].variadic = True
            continue
        if "=" in token or "[" in token or "]" in token:
            # default argument (`v=vector(time())`) or optional argument (`[...]`)
            return FailedFunctionDef(name=name)
        parts = token.split()
        if len(parts) == 1:
            (type_token,) = parts
            if type_token not in TYPE_TOKENS:
                return FailedFunctionDef(name=name)
            parsed.append(
                FunctionArg(
                    name=_synthesize_name(type_token, used_names),
                    py_type=TYPE_TOKENS[type_token],
                )
            )
        elif len(parts) == 2:
            arg_name, type_token = parts
            if type_token not in TYPE_TOKENS:
                return FailedFunctionDef(name=name)
            if type_token in ("instant-vector", "range-vector"):
                # name every vector argument `vector`, as the MetricsQL generator does
                arg_name = "vector"
            elif not IDENTIFIER_REGEX.fullmatch(
                arg_name
            ) or ENUMERATED_ARG_REGEX.search(arg_name):
                return FailedFunctionDef(name=name)
            parsed.append(FunctionArg(name=arg_name, py_type=TYPE_TOKENS[type_token]))
        else:
            return FailedFunctionDef(name=name)

    for i, arg in enumerate(parsed):
        if arg.variadic and i != len(parsed) - 1:
            return FailedFunctionDef(name=name)

    return_type = _return_type(name, [a.py_type for a in parsed])
    return FunctionDef(name=name, return_type=return_type, args=parsed)


def _split_sections(markdown: str) -> list[tuple[str, str]]:
    """Split a functions document into (header, body) pairs on level-two headers."""
    sections: list[tuple[str, str]] = []
    header: str | None = None
    body: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if header is not None:
                sections.append((header, "\n".join(body)))
            header = line[3:].strip()
            body = []
        elif header is not None:
            body.append(line)
    if header is not None:
        sections.append((header, "\n".join(body)))
    return sections


def _header_names(header: str) -> list[str] | None:
    """Extract function names from a header. Returns None for special sections whose
    functions are described as bullet lists (trigonometric, <aggregation>_over_time)."""
    tokens = re.findall(r"`([^`]+)`", header)
    names = []
    for token in tokens:
        candidate = token.removesuffix("()")
        if IDENTIFIER_REGEX.fullmatch(candidate):
            names.append(candidate)
    return names or None


def parse_functions(markdown: str) -> FunctionSpecs:
    # the chosen signature args for each function name. A name is documented many
    # times (definition, examples, prose); prefer a typed signature over a bare
    # `name()` mention so e.g. the prose "`sum_over_time()` acts on histograms..."
    # doesn't shadow the real `sum_over_time(range-vector)` bullet.
    chosen: dict[str, str] = {}
    aliases: dict[str, str] = {}

    def offer(name: str, args: str) -> None:
        if name not in chosen or (not chosen[name].strip() and args.strip()):
            chosen[name] = args

    for header, body in _split_sections(markdown):
        names = _header_names(header)
        signatures = [
            (n, a) for n, a in SIGNATURE_REGEX.findall(body) if _is_definitional(a)
        ]
        if names is None:
            # special section (trigonometric, <aggregation>_over_time): every
            # function is described by a bullet-list signature.
            for name, args in signatures:
                offer(name, args)
            continue
        documented = {n for n, _ in signatures}
        for name in names:
            if name in documented:
                for n, a in signatures:
                    if n == name:
                        offer(name, a)
            elif same_as := SAME_AS_REGEX.search(body):
                aliases[name] = same_as.group(1)
            else:
                raise Exception(f"no signature found for function {name!r}")

    for name, target in aliases.items():
        if target not in chosen:
            raise Exception(f"{name!r} aliases unknown function {target!r}")
        offer(name, chosen[target])

    specs = FunctionSpecs(funcs=[])
    for name in sorted(chosen):
        specs.funcs.append(parse_signature(name, chosen[name]))
    return specs


def parse_aggregators(markdown: str) -> tuple[list[FunctionDef], set[str]]:
    """Parse the aggregation-operator bullet list from operators.md."""
    section = markdown.split("## Aggregation operators", 1)[1].split(
        "### Detailed explanations", 1
    )[0]

    defs: list[FunctionDef] = []
    names: set[str] = set()
    for match_name, raw_args in SIGNATURE_REGEX.findall(section):
        parsed: list[FunctionArg] = []
        for raw in raw_args.replace("φ", "phi").split(","):
            param = raw.strip()
            if not param:
                continue
            if param not in AGGREGATOR_PARAMS:
                raise Exception(
                    f"unknown aggregator parameter {param!r} in {match_name!r}"
                )
            py_name, py_type = AGGREGATOR_PARAMS[param]
            parsed.append(FunctionArg(name=py_name, py_type=py_type))
        defs.append(
            FunctionDef(name=match_name, return_type="prelude.AggrFunc", args=parsed)
        )
        names.add(match_name)
    return defs, names


@cli.command()
def generate_promql_funcs(
    functions_doc: str, operators_doc: str, python_module: str
) -> None:
    """Generate python implementations of PromQL builtin functions from the Prometheus
    markdown documentation.

    The inputs are the markdown sources of
    https://prometheus.io/docs/prometheus/latest/querying/functions/ and
    https://prometheus.io/docs/prometheus/latest/querying/operators/.

    Two files are generated in python_module: generated.py (the parsed functions) and
    __init__.py (imports plus the PROMQL_FUNCTIONS / PROMQL_AGGREGATORS sets used by the
    dialect validator). Functions the parser can't model are imported from a
    hand-written handwritten.py, forcing the user to implement them or fail the build.
    """
    specs = parse_functions(pathlib.Path(functions_doc).read_text())

    aggregator_defs, aggregator_names = parse_aggregators(
        pathlib.Path(operators_doc).read_text()
    )
    specs.funcs.extend(aggregator_defs)

    output_dir = pathlib.Path(python_module)
    output_dir.mkdir(parents=True, exist_ok=True)

    defined = sorted(specs.all_defined(), key=lambda f: f.name)
    undefined = sorted(specs.al_undefined(), key=lambda f: f.name)
    all_names = sorted(f.name for f in specs.funcs)

    with output_dir.joinpath("generated.py").open("w") as file:
        file.write("from heracles.ql import prelude\n\n\n")
        file.write("\n\n\n".join(f.as_python() for f in defined))
        file.write("\n")

    with output_dir.joinpath("__init__.py").open("w") as file:
        defined_imports = ", ".join(f.name for f in defined)
        file.write(f"from .generated import {defined_imports}\n")
        if undefined:
            undefined_imports = ", ".join(f.name for f in undefined)
            file.write(f"from .handwritten import {undefined_imports}\n")
        file.write("\n")
        all_entries = ", ".join(f'"{n}"' for n in all_names)
        file.write(f"__all__ = [{all_entries}]\n\n")
        aggregator_entries = ", ".join(f'"{n}"' for n in sorted(aggregator_names))
        file.write(f"PROMQL_AGGREGATORS = frozenset({{{aggregator_entries}}})\n\n")
        file.write("PROMQL_FUNCTIONS = frozenset(__all__)\n")


if __name__ == "__main__":
    cli()
