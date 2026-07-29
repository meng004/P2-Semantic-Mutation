from p2.stats.tosem_revision import (
    gap_premise_support,
    put_cluster_bootstrap,
    split_aligned_cross,
    summarize_lrca,
)


PRIMARY = {"a1": 1, "b1": 2}


def _cell(sms, files):
    return {
        "sms": sms,
        "outcomes": [{"file": file, "label": "KILLED"} for file in files],
    }


def test_split_uses_explicit_frozen_primary():
    sms = {
        "A1_MP1": _cell(0.8, ["a1_CE1.py"]),
        "A1_MP2": _cell(0.1, ["a1_CE1.py"]),
        "B1_MP1": _cell(0.2, ["b1_OS1.py"]),
        "B1_MP2": _cell(0.7, ["b1_OS1.py"]),
    }
    aligned, cross = split_aligned_cross(sms, PRIMARY)
    assert aligned == [0.8, 0.7]
    assert cross == [0.1, 0.2]


def test_lrca_macro_excludes_zero_kill_cells():
    lrca = {
        "A1_MP1": {
            "n_killed": 2,
            "c1_share": 0.5,
            "suspect_share": 0.5,
            "labels": {"C1_legit_fault": 1},
        },
        "A1_MP2": {
            "n_killed": 0,
            "c1_share": 0.0,
            "suspect_share": 1.0,
            "labels": {"C1_legit_fault": 0},
        },
    }
    out = summarize_lrca(lrca)
    assert out["cells_evaluable"] == 1
    assert out["cells_zero_kill_NA"] == 1
    assert out["macro_mean_c1_share"] == 0.5
    assert out["macro_mean_suspect_share"] == 0.5


def test_gap_premise_support_counts_absent_positive_fiber():
    sms = {
        "A1_MP1": _cell(0.5, ["a1_CE1.py"]),
        "A1_MP2": _cell(0.0, ["a1_CE1.py"]),
        "B1_MP1": _cell(0.3, ["b1_HP1.py"]),
        "B1_MP2": _cell(0.0, ["b1_HP1.py"]),
    }
    out = gap_premise_support(sms, PRIMARY)
    assert out["antecedent_holds"] == 3
    assert out["antecedent_holds_zero_sms"] == 2
    assert out["antecedent_holds_nonzero_sms"] == 1
    assert out["antecedent_cells"] == ["A1_MP2", "B1_MP1", "B1_MP2"]


def test_put_cluster_bootstrap_preserves_one_to_one_cluster_draws():
    sms = {
        "A1_MP1": _cell(0.8, ["a1_CE1.py"]),
        "A1_MP2": _cell(0.1, ["a1_CE1.py"]),
        "B1_MP1": _cell(0.2, ["b1_OS1.py"]),
        "B1_MP2": _cell(0.7, ["b1_OS1.py"]),
    }
    out = put_cluster_bootstrap(sms, PRIMARY, n_boot=200, seed=7)
    assert out["n_put_clusters"] == 2
    assert out["n_aligned"] == 2
    assert out["n_cross"] == 2
    assert out["n_bootstrap"] == 200
    assert out["resampling_unit"] == "PUT"
    assert len(out["ci_95"]) == 2
