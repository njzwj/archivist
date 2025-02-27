from tqdm.contrib import DummyTqdmFile
from typing import List
import contextlib
import sys
from .cache import get_cache

@contextlib.contextmanager
def std_out_err_redirect_tqdm():
    orig_out_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = map(DummyTqdmFile, orig_out_err)
        yield orig_out_err[0]
    # Relay exceptions
    except Exception as exc:
        raise exc
    # Always restore sys.stdout/err if necessary
    finally:
        sys.stdout, sys.stderr = orig_out_err

def parse_arguments(args: List[str]) -> dict:
    cache = get_cache()
    cached_args = cache.read("kwargs")
    args = dict(arg.split("=", 1) for arg in args)
    if len(args) == 0:
        args = cached_args or {}
        print(f"Using cached arguments:\n{args}")
    cache.write("kwargs", args)
    return args
