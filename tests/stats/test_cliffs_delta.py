"""Tests for Cliff's delta + bootstrap CI used in RQ2 H2 evidence."""
import math

from p2.stats.cliffs_delta import bootstrap_delta_ci, cliffs_delta, odds_ratio


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


def test_negative_delta_when_b_dominates_a():
    a = [0.7, 0.8, 0.9]
    b = [0.1, 0.2, 0.3]
    assert cliffs_delta(a, b) > 0  # a > b -> positive delta
    assert cliffs_delta(b, a) < 0  # b dominated by a -> negative


def test_empty_inputs_return_zero():
    assert cliffs_delta([], [1.0, 2.0]) == 0.0
    assert cliffs_delta([1.0, 2.0], []) == 0.0
    assert cliffs_delta([], []) == 0.0
    assert bootstrap_delta_ci([], [1.0, 2.0]) == (0.0, 0.0)


def test_bootstrap_reproducible_with_same_seed():
    a = [0.1, 0.4, 0.5, 0.6]
    b = [0.2, 0.3, 0.7, 0.8]
    ci_1 = bootstrap_delta_ci(a, b, n_boot=200, alpha=0.05, seed=123)
    ci_2 = bootstrap_delta_ci(a, b, n_boot=200, alpha=0.05, seed=123)
    assert ci_1 == ci_2  # exact match required


def test_odds_ratio_positive_when_a_larger():
    assert odds_ratio([0.5, 0.6, 0.7], [0.1, 0.2, 0.3]) > 1.0


def test_odds_ratio_inf_when_b_median_zero_and_a_positive():
    assert math.isinf(odds_ratio([0.5, 0.6], [0.0, 0.0]))


def test_odds_ratio_zero_when_both_medians_zero():
    assert odds_ratio([0.0, 0.0], [0.0, 0.0]) == 0.0


def test_odds_ratio_handles_empty_inputs():
    assert odds_ratio([], [1.0, 2.0]) == 0.0
    assert odds_ratio([1.0], []) == 0.0
