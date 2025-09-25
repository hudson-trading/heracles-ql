import ctypes
import os

try:
    _formatter_so = ctypes.cdll.LoadLibrary(
        os.path.join(os.path.dirname(__file__), "../../pkg/formatter.so")
    )
    _format_func = _formatter_so.Format
    _format_func.argtypes = [ctypes.c_char_p]
    _format_func.restype = ctypes.c_void_p

    _free_func = _formatter_so.FreeStr
    _free_func.argtypes = [ctypes.c_char_p]

    def format(input: str) -> str | None:
        res: ctypes.c_char_p = _format_func(input.encode())
        if not res:
            return None
        cast_result = ctypes.cast(res, ctypes.c_char_p)
        try:
            real_result = cast_result.value.decode()  # type: ignore
        except:  # noqa
            return None
        finally:
            _free_func(cast_result)
        return real_result

except:  # noqa
    # if we can't load the so, just make format a no-op

    def format(input: str) -> str | None:
        return input
