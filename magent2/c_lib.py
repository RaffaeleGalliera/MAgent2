"""Utility helpers for calling the compiled MAgent2 C/C++ library."""

import ctypes
import multiprocessing
import os
import pathlib
import platform
import sysconfig


def _load_lib() -> ctypes.CDLL:
    """
    Locate and load the compiled shared library, covering these cases:

    1. Modern builds or wheels   → magent2/libmagent{ext_suffix}
    2. Legacy in-package builds  → magent2/libmagent.so|dylib|dll
    3. **Parent-dir builds**      → libmagent.* next to the package dir
    4. Farama wheels             → venv/Lib/site-packages/magent2/libmagent.so
    """
    here = pathlib.Path(__file__).parent
    parent = here.parent

    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ""

    candidates = [
        here / f"libmagent{ext_suffix}",             # modern build
        here / "libmagent.so",                       # old Linux in-package
        here / "libmagent.dylib",                    # old macOS in-package
        here / "magent.dll",                         # old Windows in-package
        parent / f"libmagent{ext_suffix}",           # ← parent-dir build
        parent / "libmagent.so",                     # fallback parent Linux
        parent / "libmagent.dylib",                  # fallback parent macOS
        parent / "magent.dll",                       # fallback parent Windows
        here / ".." / "venv" / "Lib" / "site-packages" / "magent2" / "libmagent.so",
    ]

    for path in candidates:
        if path.exists():
            return ctypes.CDLL(path.resolve(), ctypes.RTLD_GLOBAL)

    tried = "\n  ".join(str(p) for p in candidates)
    raise FileNotFoundError(
        "Could not locate the compiled MAgent2 shared library.\n"
        "Paths tried:\n  " + tried
    )


def as_float_c_array(buf):
    """Convert a NumPy float32 array to a ctypes pointer."""
    return buf.ctypes.data_as(ctypes.POINTER(ctypes.c_float))


def as_int32_c_array(buf):
    """Convert a NumPy int32 array to a ctypes pointer."""
    return buf.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))


def as_bool_c_array(buf):
    """Convert a NumPy bool array to a ctypes pointer."""
    return buf.ctypes.data_as(ctypes.POINTER(ctypes.c_bool))


# Cap OpenMP threads to half the logical CPUs unless the user overrides
if "OMP_NUM_THREADS" not in os.environ:
    os.environ["OMP_NUM_THREADS"] = str(max(1, multiprocessing.cpu_count() // 2))

# Load the shared library once at import-time
_LIB = _load_lib()

