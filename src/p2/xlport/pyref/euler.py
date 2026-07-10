"""Python-side reference for XL program 'euler' (frozen aux per
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

_mod = _load("third_party/thealgorithms-python/maths/euler_method.py",
             "xl_ta_euler")


def program(x) -> float:
    y0 = 0.05 + 0.9 * float(x)
    y = _mod.explicit_euler(lambda t, yv: yv * (1.0 - yv), y0, 0.0,
                            0.0078125, 2.0)
    return float(y[-1])
