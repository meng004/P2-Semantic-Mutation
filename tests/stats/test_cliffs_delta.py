"""Tests for Cliff's delta + bootstrap CI used in RQ2 H2 evidence."""
from p2.stats.cliffs_delta import cliffs_delta, bootstrap_delta_ci


def test_identical_distributions_have_zero_delta():
    a = [0.5, 0.5, 0.5, 0.5]
    b = [0.5, 0.5, 0.5, 0.5]
    d = cliffs_delta(a, b)
    assert abs(d) < 1e-9


def test_completely_separated_distributions_have_one_delta():
    a = [0.1, 0.2, 0.3]
    b = [0.7, 0.8, 0.9]
    d = cliffs_delta(b, a)
    assert abs(d - 1.0) < 1e-9


def test_bootstrap_ci_brackets_point_estimate():
    a = [0.1, 0.2, 0.3, 0.4, 0.5]
    b = [0.4, 0.5, 0.6, 0.7, 0.8]
    point = cliffs_delta(b, a)
    lo, hi = bootstrap_delta_ci(b, a, n_boot=500, alpha=0.05, seed=42)
    assert lo <= point <= hi
    assert lo > 0
