"""Python-side reference for XL program 'rungekutta' (frozen aux per
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

_mod = _load("third_party/thealgorithms-python/maths/numerical_analysis/runge_kutta.py",
             "xl_ta_rungekutta")


def program(x) -> float:
    y = _mod.runge_kutta(lambda t, yv: (t - yv) / 2.0, float(x), 0.0,
                         1.0 / 64.0, 2.0)
    return float(y[-1])
