from p2.stats.rq1_rates import compute_rates


def test_rates_normalize_against_inst():
    r = compute_rates(inst=20, equiv=5, killed=10, survive=5, n_target=15)
    assert r["inst_rate"] == 20 / 15
    assert r["equiv_rate"] == 5 / 20
    assert r["survive_rate"] == 5 / 20
