"""Unit tests for the DVE sign-flip inference primitives.

These validate the *real single-dataset analysis path* (exact enumeration)
used by the pre-registered DVE-W primary test, independently of the vectorized
Monte-Carlo used inside the power loop.
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dve"))
import power_simulation as ps  # noqa: E402


def test_exact_pvalue_matches_bruteforce_definition():
    # small hand case: exact one-sided sign-flip p-value == fraction of the
    # 2**n sign assignments whose mean >= observed mean.
    d = np.array([0.2, 0.1, -0.05, 0.3])
    n = len(d)
    obs = d.mean()
    signs = np.array(list(itertools.product([1.0, -1.0], repeat=n)))
    expected = np.mean((signs * d).mean(axis=1) >= obs - 1e-12)
    assert ps.signflip_pvalue_exact(d) == pytest.approx(expected)


def test_all_positive_gives_smallest_pvalue():
    # when every PUT difference is positive, the observed all-plus config is
    # the unique maximum, so p = 1/2**n.
    d = np.array([0.1, 0.2, 0.3, 0.15, 0.05])
    assert ps.signflip_pvalue_exact(d) == pytest.approx(1.0 / 2 ** len(d))


def test_symmetric_data_pvalue_half():
    # a single PUT: two sign assignments (+,-); observed(+) ties itself and
    # beats (-) when d>0 -> p = 1/2.
    d = np.array([0.4])
    assert ps.signflip_pvalue_exact(d) == pytest.approx(0.5)


def test_exact_and_sampled_agree_for_moderate_n():
    rng = np.random.default_rng(7)
    d = rng.normal(0.1, 0.2, size=12)
    exact = ps.signflip_pvalue_exact(d)
    sampled = ps.signflip_pvalue_sampled(d, n_perm=200000, rng=np.random.default_rng(1))
    assert sampled == pytest.approx(exact, abs=0.01)


def test_type1_error_controlled_under_null():
    # end-to-end: at mu=0 the empirical rejection rate must sit near alpha.
    sc = ps.Scenario(mu=0.0, sigma_diff=0.20, icc=0.2, n_put=15, n_fam=3)
    power = ps.power_of(sc, n_sim=4000, seed=123, n_perm=2000)
    assert power <= 0.075, f"type-I inflated: {power}"


def test_power_increases_with_effect():
    base = ps.Scenario(0.0, 0.20, 0.2, 15, 3)
    strong = ps.Scenario(0.15, 0.20, 0.2, 15, 3)
    p0 = ps.power_of(base, n_sim=3000, seed=5, n_perm=1500)
    p1 = ps.power_of(strong, n_sim=3000, seed=5, n_perm=1500)
    assert p1 > p0 + 0.5
