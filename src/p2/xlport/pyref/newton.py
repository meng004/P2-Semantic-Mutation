"""Python-side reference for XL program 'newton' (frozen aux per
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

_mod = _load("third_party/thealgorithms-python/maths/numerical_analysis/newton_raphson.py",
             "xl_ta_newton")


def program(x) -> float:
    a = 4.0 ** (2.0 * float(x) - 1.0)
    root, _err, _steps = _mod.newton_raphson(lambda t: t * t - a, x0=1.5)
    return float(root)
