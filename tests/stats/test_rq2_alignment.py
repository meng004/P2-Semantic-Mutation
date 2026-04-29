import numpy as np
from p2.stats.rq2_alignment import cliffs_delta, alignment_odds_ratio


def test_cliffs_delta_positive_when_aligned_higher():
    aligned = np.array([0.8, 0.9, 0.85])
    cross = np.array([0.2, 0.3, 0.1])
    delta = cliffs_delta(aligned, cross)
    assert delta > 0.474


def test_odds_ratio_basic():
    or_val = alignment_odds_ratio(aligned_high=8, aligned_low=2, cross_high=2, cross_low=8)
    assert or_val > 3.0
