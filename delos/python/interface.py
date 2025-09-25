# pure python interface because it's a little easier to reason about than
# a template and exec'ing makes the user's execution environment a bit cleaner
import inspect
import sys

from heracles import ql


def main():
    global_dict = {"ql": ql}
    exec(sys.argv[1], global_dict)

    vector = global_dict["VECTOR"]

    if inspect.isfunction(vector):
        res = vector()
    else:
        res = vector

    if not isinstance(res, ql.Timeseries):
        sys.exit(1)

    rendered_result = ql.format(res.render())

    # simple interface to go code - anything on stdout after
    # __DELOS_QUERY_STARTS: is the query. All function calls
    # (including render()) are made before this to avoid polluting
    # stdout
    print("__DELOS_QUERY_STARTS:", end="")
    print(rendered_result, end="")


if __name__ == "__main__":
    main()
