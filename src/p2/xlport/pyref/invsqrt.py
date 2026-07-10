"""Python-side reference for XL program 'invsqrt' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). external Python implementation (TheAlgorithms/Python)."""

import importlib.util as _ilu
from pathlib import Path as _Path

_ROOT = _Path(__file__).resolve().parents[4]


def _load(rel, name):
    p = _ROOT / rel
    spec = _ilu.spec_from_file_location(name, p)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_mod = _load("third_party/thealgorithms-python/maths/fast_inverse_sqrt.py",
             "xl_ta_invsqrt")


def program(x) -> float:
    u = 4.0 ** (2.0 * float(x) - 1.0)
    return float(_mod.fast_inverse_sqrt(u))
