from p2.stats.pattern_coverage import compute_pattern_coverage


def test_full_coverage_on_all_mp_passes():
    # 5 MPs × 2 outcomes (pass/fail) = 10 cells; suite covers all
    outcomes = [(mp, ok) for mp in (1, 2, 3, 4, 5) for ok in (True, False)]
    cov = compute_pattern_coverage(outcomes, n_mps=5)
    assert cov == 1.0


def test_zero_coverage_on_empty_suite():
    cov = compute_pattern_coverage([], n_mps=5)
    assert cov == 0.0


def test_partial_coverage():
    outcomes = [(1, True), (2, True), (3, True)]  # 3 of 10 cells
    cov = compute_pattern_coverage(outcomes, n_mps=5)
    assert abs(cov - 0.3) < 1e-9
