"""Python-side reference for XL program 'tanh' (frozen aux per
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

import numpy as np

_mod = _load("third_party/thealgorithms-python/maths/tanh.py", "xl_ta_tanh")


def program(x) -> float:
    return float(_mod.tangent_hyperbolic(np.array([4.0 * float(x) - 2.0]))[0])
