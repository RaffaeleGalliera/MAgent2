import ctypes, pathlib, sysconfig

def _load_lib():
    here = pathlib.Path(__file__).parent
    ext  = sysconfig.get_config_var("EXT_SUFFIX")      # ".cpython-39-…so", ".pyd", …
    lib  = here / f"libmagent{ext}"
    if not lib.exists():
        raise FileNotFoundError(f"Compiled library not found at {lib}")
    return ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)

_LIB = _load_lib()

