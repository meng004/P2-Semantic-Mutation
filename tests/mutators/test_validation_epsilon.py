"""V3 should treat output diffs ≤ 1e-6 as equivalent (matches AVP)."""
import numpy as np
from p2.mutators.validation import validate_mutant


def _orig(x):
    return float(x) ** 2


def test_v3_uses_1e6_threshold():
    # mutant differs by exactly 5e-7 — should be flagged equiv (NOT pass V3)
    mutant_code = (
        "def program(x):\n"
        "    return float(x) ** 2 + 5e-7\n"
    )
    res = validate_mutant(mutant_code, _orig)
    assert not res.nontrivial, (
        f"5e-7 diff must be < 1e-6 ε, expected nontrivial=False, got {res!r}"
    )


def test_v3_passes_when_diff_above_threshold():
    mutant_code = (
        "def program(x):\n"
        "    return float(x) ** 2 + 1e-3\n"
    )
    res = validate_mutant(mutant_code, _orig)
    assert res.nontrivial, f"1e-3 diff is well above 1e-6, expected nontrivial=True, got {res!r}"
