"""TDD: the inv.eqv strong MR must separate the real scipy version pair.

correct version (1.13.1) -> pass (not killed);  buggy version (1.13.0) -> fail (killed).
Requires `uv` on PATH; first run provisions two cached scipy venvs.
"""
import case_inv_eqv as c


def test_correct_version_passes_strong_mr():
    assert c.verdict(c.CORRECT_VER) == "pass"


def test_buggy_version_killed_by_strong_mr():
    assert c.verdict(c.BUGGY_VER) == "fail"


def test_epsilon_tol_is_explicit_factor():
    # tightening/loosening tolerance is exposed, not hard-wired
    assert c.verdict(c.CORRECT_VER, epsilon_tol=1e-9) == "pass"
    assert c.verdict(c.BUGGY_VER, epsilon_tol=1e-9) == "fail"
