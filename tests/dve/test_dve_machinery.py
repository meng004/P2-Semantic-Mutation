"""Unit tests for the frozen DVE machinery (registry, split, strategies, endpoint)."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from p2.dve import endpoint as ep
from p2.dve import strategies as st
from p2.dve.family_registry import FamilyRegistry, FaultCard, Provenance
from p2.dve.split import Splitter


# ---------- endpoint ----------

def test_family_detection_score_is_proportion():
    assert ep.family_detection_score([True, False, False, False]) == pytest.approx(0.25)
    assert ep.family_detection_score([True, True]) == 1.0
    with pytest.raises(ValueError):
        ep.family_detection_score([])


def test_fds_family_equal_weight_ignores_family_size():
    # two families, one large one small: FDS weights them equally.
    fams = [ep.FamilyDetection("p", "f1", 0.2, 100),
            ep.FamilyDetection("p", "f2", 0.8, 2)]
    assert ep.fds(fams) == pytest.approx(0.5)


def test_signflip_all_positive_is_min_pvalue():
    d = np.array([0.1, 0.2, 0.15, 0.3, 0.05])
    r = ep.signflip_test(d)
    assert r["exact"] is True
    assert r["p_value"] == pytest.approx(1 / 2 ** 5)


def test_signflip_mid_shift_raises_pvalue():
    d = np.array([0.12, 0.11, 0.13, 0.09, 0.10, 0.14])
    p0 = ep.signflip_test(d, shift=0.0)["p_value"]
    pmid = ep.signflip_test(d, shift=0.10)["p_value"]
    assert pmid > p0  # harder to beat MID than to beat 0


def test_bootstrap_ci_covers_point():
    by_put = {"p1": [0.1, 0.2, 0.15], "p2": [0.05, 0.25], "p3": [0.2, 0.1, 0.3]}
    ci = ep.two_level_bootstrap_ci(by_put, n_boot=2000, seed=1)
    assert ci["ci_lo"] <= ci["point"] <= ci["ci_hi"]
    assert ci["one_sided_lo"] >= ci["ci_lo"]


# ---------- strategies ----------

def test_s1_covers_most_dev_residual_families():
    valid = ["mrA", "mrB", "mrC"]
    dev_kill = {"mrA": {"f1", "f2"}, "mrB": {"f2", "f3"}, "mrC": {"f9"}}
    residual = {"f1", "f2", "f3"}
    picked = st.s1_residual_guided(valid, dev_kill, residual, k=1)
    assert picked == ["mrA"] or picked == ["mrB"]  # both cover 2 residual families
    picked2 = st.s1_residual_guided(valid, dev_kill, residual, k=2)
    assert set(picked2) == {"mrA", "mrB"}  # together cover f1,f2,f3


def test_s1_counts_families_not_instances():
    # mrA kills one big family; mrB kills two small families -> mrB wins on family count
    valid = ["mrA", "mrB"]
    dev_kill = {"mrA": {"fbig"}, "mrB": {"fs1", "fs2"}}
    residual = {"fbig", "fs1", "fs2"}
    assert st.s1_residual_guided(valid, dev_kill, residual, k=1) == ["mrB"]


def test_s3_uses_no_mutant_info():
    valid = ["m1", "m2"]
    coverage = {"m1": {"transformA", "cov1"}, "m2": {"cov1"}}
    picked = st.s3_coverage_guided(valid, coverage, r0_coverage={"cov1"}, k=1)
    assert picked == ["m1"]  # only m1 adds new coverage


def test_s4_random_deterministic_under_seed():
    valid = [f"mr{i}" for i in range(10)]
    a = st.s4_random(valid, k=4, seed=42)
    b = st.s4_random(valid, k=4, seed=42)
    assert a == b and len(a) == 4


# ---------- registry ----------

def _prov():
    return Provenance("historical_fault", "https://github.com/x/y/commit/abc",
                      "2026-07-10", "certifier")


def test_family_ids_nested_in_put():
    reg = FamilyRegistry()
    reg.add_card(FaultCard("c1", "putA", "off_by_one", _prov(), "B", ["m1", "m2"]))
    reg.add_card(FaultCard("c2", "putB", "off_by_one", _prov(), "B", ["m3"]))
    fams = reg.primary_families()
    # same mechanism, different PUTs -> different families
    assert "putA::off_by_one" in fams and "putB::off_by_one" in fams
    # but same mechanism class
    assert set(reg.mechanism_classes()) == {"off_by_one"}


def test_registry_rejects_bad_provenance():
    reg = FamilyRegistry()
    bad = Provenance("author_intuition", "", "2026-07-10", "gen")
    with pytest.raises(ValueError):
        reg.add_card(FaultCard("c1", "p", "m", bad, "B"))


def test_frozen_registry_forbids_boundary_change():
    reg = FamilyRegistry()
    reg.add_card(FaultCard("c1", "p", "m", _prov(), "B", ["m1"]))
    h = reg.freeze()
    assert len(h) == 64
    with pytest.raises(RuntimeError):
        reg.add_card(FaultCard("c2", "p", "m", _prov(), "B"))
    with pytest.raises(RuntimeError):
        reg.merge_or_split({"c1": "other"})


# ---------- split committer ----------

def test_split_commitment_and_one_shot_open():
    sp = Splitter(registry_hash="deadbeef")
    strata = {"s1": [f"f{i}" for i in range(6)], "s2": [f"g{i}" for i in range(4)]}
    commit = sp.commit(strata, salt="secret-salt", seed=7)
    assert commit.n_dev + commit.n_holdout == 10
    assert commit.registry_hash == "deadbeef"
    # dev visible; holdout guarded until sealed
    assert len(sp.dev_families) == commit.n_dev
    with pytest.raises(RuntimeError):
        sp.open_holdout(strategy_outputs_sealed=False)
    holdout = sp.open_holdout(strategy_outputs_sealed=True)
    with pytest.raises(RuntimeError):
        sp.open_holdout(strategy_outputs_sealed=True)  # one-shot
    assert sp.verify_commitment(holdout, "secret-salt", commit.commit_hash)
    assert not sp.verify_commitment(holdout, "wrong-salt", commit.commit_hash)


def test_split_is_balanced_within_strata():
    sp = Splitter(registry_hash="h")
    strata = {"s": [f"f{i}" for i in range(8)]}
    commit = sp.commit(strata, salt="s", seed=1)
    assert commit.n_holdout == 4 and commit.n_dev == 4
