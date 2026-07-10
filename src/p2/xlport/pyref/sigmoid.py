"""Python-side reference for XL program 'sigmoid' (frozen aux per
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

_mod = _load("third_party/thealgorithms-python/maths/sigmoid.py", "xl_ta_sigmoid")


def program(x) -> float:
    return float(_mod.sigmoid(np.array([8.0 * float(x) - 4.0]))[0])
