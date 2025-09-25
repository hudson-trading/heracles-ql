"""A marvelously evil script to generate Python implementions of Victoria Metrics
functions from the documentation."""

from __future__ import annotations

import dataclasses
import pathlib
import re

import marko
import pydantic
import typer

cli = typer.Typer()

MQL_FUNCTIONS_SUPER_HEADER = "MetricsQL functions"
ROLLUP_HEADER = "Rollup functions"
AGGR_FUNCTIONS_HEADER = "Aggregate functions"
TRANSFORM_FUNCTIONS_HEADER = "Transform functions"
LABEL_MANIPULATION_FUNCTIONS_HEADER = "Label manipulation functions"


@dataclasses.dataclass
class Heading:
    level: int
    text: str
    parent: Heading | None = None
    children: list[Heading] = dataclasses.field(default_factory=list)
    code: str | None = None


@cli.command()
def generate_funcs(input_file: str, python_module: str) -> None:
    """
    generate_funcs generates the python implementions for Victoria Metrics builtin
    functions from the Victoria Metrics markdown documentation.

    The input_file for this function should be the markdown source of
    https://docs.victoriametrics.com/metricsql/.

    This function works by parsing the markdown docs and building a document tree
    from the headers. We then scan the document tree and find sub-headers of the
    pre-defined sections for various MetricsQL functions.

    For all functionsin the docs, definition of the of the function is provided as
    a code block in the text. parse_function_definition parses this code block and
    returns a function definition if successful. For a small set of complicated
    functions, the simple heuristics implemented here don't work. For those functions,
    we record that parsing didn't work.

    Finally, we generate 2 files in the python_module directory:
    1. generated.py with the generated python functions
    2. __init__.py with imports for each of the generated functions and each of the
    functions we failed to parse

    By generating imports for the functions we couldn't parse, we force the user
    to hand write those functions or the main package unit tests will fail. They must
    be written in a file called handwritten.py in the python_module directory.
    """
    with open(input_file) as file:
        document = marko.parse(file.read())

    root_headers: list[Heading] = []
    cur_header: Heading | None = None
    for child in document.children:
        if child.get_type() == "Heading":
            h = Heading(child.level, child.children[0].children)
            if not root_headers:
                root_headers.append(h)
                cur_header = h
            elif cur_header:
                if not climb_headers_and_insert(cur_header, h):
                    root_headers.append(h)
                cur_header = h
        elif cur_header and not cur_header.code:
            code = find_first_codespan(child)
            if code:
                cur_header.code = code

    (function_docs,) = (h for h in root_headers if h.text == MQL_FUNCTIONS_SUPER_HEADER)
    (rollup_funcs,) = (h for h in function_docs.children if h.text == ROLLUP_HEADER)
    (aggregation_funcs,) = (
        h for h in function_docs.children if h.text == AGGR_FUNCTIONS_HEADER
    )
    (transformation_funcs,) = (
        h for h in function_docs.children if h.text == TRANSFORM_FUNCTIONS_HEADER
    )

    (label_manipulation_funcs,) = (
        h
        for h in function_docs.children
        if h.text == LABEL_MANIPULATION_FUNCTIONS_HEADER
    )

    specs = FunctionSpecs(funcs=[])

    for r in rollup_funcs.children:
        if r.code:
            specs.funcs.append(parse_function_definition(r.code, "prelude.RollupFunc"))

    for r in aggregation_funcs.children:
        if r.code:
            specs.funcs.append(
                parse_function_definition(
                    r.code, "prelude.AggrFunc", vector_args_are_variadic=True
                )
            )
    for r in transformation_funcs.children:
        if r.code:
            specs.funcs.append(
                parse_function_definition(r.code, "prelude.TransformFunc")
            )

    for r in label_manipulation_funcs.children:
        if r.code:
            specs.funcs.append(
                parse_function_definition(r.code, "prelude.LabelManipulationFunc")
            )

    output_dir = pathlib.Path(python_module)
    if not output_dir.is_dir():
        output_dir.mkdir()

    init_file = output_dir.joinpath("__init__.py")
    generated_file = output_dir.joinpath("generated.py")

    all_defined_func_names = [f.name for f in specs.all_defined()]

    with init_file.open("w") as file:
        import_names = ",".join(all_defined_func_names)
        import_all_generated = f"from .generated import {import_names}\n"

        hand_written_imports = ",".join(f.name for f in specs.al_undefined())
        import_all_hand_written = f"from .handwritten import {hand_written_imports}\n"

        all_entries = ",\n    ".join(f'"{f.name}"' for f in specs.funcs)
        all_defn = f"__all__ = [{all_entries}\n]\n"
        file.writelines((import_all_generated, import_all_hand_written, all_defn))

    with generated_file.open("w") as file:
        file.write("from heracles.ql import prelude\n")
        for f in specs.all_defined():
            file.write(f.as_python())
            file.write("\n")


class FunctionArg(pydantic.BaseModel):
    name: str
    py_type: str
    variadic: bool = False

    def as_python(self) -> str:
        res = f"{self.name}: {self.py_type}"
        if self.variadic:
            res = "*" + res
        return res

    def as_python_reference(self) -> str:
        if self.variadic:
            return f"*{self.name}"
        return self.name


class FunctionDef(pydantic.BaseModel):
    name: str
    args: list[FunctionArg]
    return_type: str

    def as_python(self) -> str:
        args = ", ".join(f"{arg.as_python()}" for arg in self.args)
        params = ", ".join(arg.as_python_reference() for arg in self.args)
        return (
            f"def {self.name}({args}) -> {self.return_type}:\n"
            + f'    return {self.return_type}("{self.name}", {params})'
        )


class FailedFunctionDef(pydantic.BaseModel):
    name: str


class FunctionSpecs(pydantic.BaseModel):
    funcs: list[FunctionDef | FailedFunctionDef]

    def all_defined(self) -> list[FunctionDef]:
        return [f for f in self.funcs if isinstance(f, FunctionDef)]

    def al_undefined(self) -> list[FailedFunctionDef]:
        return [f for f in self.funcs if isinstance(f, FailedFunctionDef)]


# FUNCTION_REGEX matches the part of the usage example which contains the function
# pattern. Some usage examples contain extra text
FUNCTION_REGEX = re.compile(r"([^(]*)\(([^)]*)\).*")

# INSTANT_VECOTR_REGEX matches the part of the usage example which refers to an
# instant vector. This usually is "q", but sometimes is q<number> or qN
# for explicitly variadic cases.
INSTANT_VECOTR_REGEX = re.compile(r"q[1-9N]?")

# ALPHANUMERIC_REGEX matches names which do not contain special syntax
ALPHANUMERIC_REGEX = re.compile(r"[a-zA-Z0-9_]+")


def parse_function_definition(
    code: str, return_type: str, vector_args_are_variadic: bool = False
) -> FunctionDef | FailedFunctionDef:
    """
    parse_function_definition parses the usage example of a function from the
    Victoria Metrics MetricsQL docs.
    """
    match = FUNCTION_REGEX.match(code)
    if not match:
        raise Exception()
    (name, args) = match.groups()

    if not args.strip():
        return FunctionDef(name=name, return_type=return_type, args=[])

    if name.startswith("topk") or name.startswith("bottomk"):
        vector_args_are_variadic = False

    parsed_args = []
    skip_next_arg = False
    for a in args.split(","):
        if skip_next_arg:
            skip_next_arg = False
            continue
        a = a.strip()
        if a == "series_selector[d]":
            # series_selector[d] is always used to represent a range vector
            parsed_args.append(
                FunctionArg(
                    name="vector",
                    py_type="prelude.RangeVector",
                    variadic=vector_args_are_variadic,
                )
            )
            continue
        if (
            a.startswith('"')
            and a.endswith('"')
            and ALPHANUMERIC_REGEX.fullmatch(a[1:-1])
        ):
            # an alphanumeric name surrounded by quotes is always used to represent a
            # string literal
            parsed_args.append(FunctionArg(name=a[1:-1], py_type="str"))
            continue
        if INSTANT_VECOTR_REGEX.match(a):
            # normal instant vector case
            parsed_args.append(
                FunctionArg(
                    name="vector",
                    py_type="prelude.InstantOrRangeVector",
                    variadic=vector_args_are_variadic,
                )
            )
            continue
        if ALPHANUMERIC_REGEX.fullmatch(a):
            # other named variables refer to a scalar-like. Since scalars are
            # instant vectors with no labels, we model this as an int, float, or
            # InstantVector to represent boxable literals or an instant vector.
            parsed_args.append(
                FunctionArg(name=a, py_type="int | float | prelude.InstantVector")
            )
            continue
        if a == '"other_label=other_value"':
            # matches some functions which can take a label name and value as a
            # single string parameter.
            # TODO: this isn't handled right - we should treat these as kwargs if we
            # can
            parsed_args.append(FunctionArg(name="other_label", py_type="str | None"))
            continue
        if a.startswith("..."):
            # explicit variadic case
            # sometimes variadic arguments are given explicitly as a1,...,aN or
            # some variation. Sometimes the ... is preceded and followed by commas,
            # sometimes it is not. There are a few cases where there's an extra '.'
            # (which is a typo)
            if a == "..." or a == "....":
                # sometimes the docs write q1, ..., qN
                # other times, q1, ... qN
                skip_next_arg = True
            prev = parsed_args[-1]
            prev.variadic = True
            continue
        print(f"codegen failed for {name} because of unknown arg '{a}'")
        return FailedFunctionDef(name=name)

    for i, a in enumerate(parsed_args):
        if a.variadic and i != len(parsed_args) - 1:
            print(
                f"codegen failed for {name} because of illegal variadic"
                f"argument: {a.name}"
            )
            return FailedFunctionDef(name=name)
    return FunctionDef(name=name, return_type=return_type, args=parsed_args)


def find_first_codespan(ele: marko.block.BlockElement) -> str | None:
    if ele.get_type() == "CodeSpan":
        return ele.children  # type: ignore
    if isinstance(ele.children, list):
        for c in ele.children:
            res = find_first_codespan(c)
            if res:
                return res
    return None


def climb_headers_and_insert(cur_header: Heading, new: Heading) -> bool:
    if new.level > cur_header.level:
        cur_header.children.append(new)
        new.parent = cur_header
        return True
    elif cur_header.parent:
        return climb_headers_and_insert(cur_header.parent, new)
    else:
        return False


if __name__ == "__main__":
    cli()
