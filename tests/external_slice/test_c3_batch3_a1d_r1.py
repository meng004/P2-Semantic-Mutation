"""Targeted Gate A1d-r1 checks for C3 Batch 3 repetition matrix."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "external_slice" / "batch3_a1d_r1.py"
MATRIX = ROOT / "data" / "external_slice" / "BATCH3_EXECUTION_MATRIX.json"
MEMBERSHIP = ROOT / "data" / "external_slice" / "BATCH3_MEMBERSHIP.json"
HANDOFF = ROOT / "data" / "external_slice" / "HANDOFF_REPRO_BATCH3.json"
SM03 = ROOT / "data" / "external_slice" / "reproducers" / "EXT-statsmodels-03.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def helpers():
    return _load(HELPER, "batch3_a1d_r1_under_test")


@pytest.fixture(scope="module")
def sm03():
    return _load(SM03, "ext_statsmodels_03_under_test")


def test_execution_matrix_smoke_and_formal_seeds(helpers):
    matrix = helpers.load_execution_matrix(MATRIX)
    assert matrix["smoke"]["seeds"] == [0]
    assert matrix["formal_repetitions"]["seeds"] == [0, 1, 2, 3, 4]
    assert matrix["members"] == helpers.EXPECTED_MEMBERS


def test_exact_membership_byte_identity(helpers):
    digest = helpers.assert_membership_byte_identical(MEMBERSHIP)
    expected = json.loads(MATRIX.read_text(encoding="utf-8"))[
        "membership_sha256_expected"
    ]
    assert digest == expected
    assert digest == hashlib.sha256(MEMBERSHIP.read_bytes()).hexdigest()


def test_per_seed_arm_parity_helper(helpers):
    buggy = {"seed": 2, "input": {"x": [1, 2], "value": None}}
    fixed = {"seed": 2, "input": {"x": [1, 2], "value": None}}
    assert helpers.assert_arm_input_parity(buggy, fixed, 2) is True
    fixed_bad = {"seed": 2, "input": {"x": [1, 3], "value": None}}
    assert helpers.assert_arm_input_parity(buggy, fixed_bad, 2) is False
    assert helpers.assert_arm_input_parity(buggy, fixed, 1) is False


def test_full_verdict_aggregation_requires_every_seed(helpers):
    good = {
        seed: {
            "buggy_property_holds": False,
            "fixed_property_holds": True,
            "buggy_raw_return_code": 1,
            "fixed_raw_return_code": 0,
            "input_parity_ok": True,
        }
        for seed in [0, 1, 2, 3, 4]
    }
    ok = helpers.aggregate_formal_verdict(good)
    assert ok["proposed_crit_dual_arm_repro"] == "PASS"
    assert ok["failing_seeds"] == []
    assert ok["all_seeds_contrasted"] is True

    bad = dict(good)
    bad[3] = {
        "buggy_property_holds": True,
        "fixed_property_holds": True,
        "buggy_raw_return_code": 0,
        "fixed_raw_return_code": 0,
        "input_parity_ok": True,
    }
    failed = helpers.aggregate_formal_verdict(bad)
    assert failed["proposed_crit_dual_arm_repro"] == "REPRO_FAILED"
    assert failed["failing_seeds"] == [3]
    # Failed seeds remain visible; not dropped from the report.
    assert [row["seed"] for row in failed["seed_rows"]] == [0, 1, 2, 3, 4]


def test_aggregation_rejects_missing_seed(helpers):
    partial = {
        0: {
            "buggy_property_holds": False,
            "fixed_property_holds": True,
            "input_parity_ok": True,
        }
    }
    out = helpers.aggregate_formal_verdict(partial)
    assert out["proposed_crit_dual_arm_repro"] == "REPRO_FAILED"
    assert out["failing_seeds"] == [1, 2, 3, 4] or 0 not in out["failing_seeds"]
    assert set(out["failing_seeds"]) >= {1, 2, 3, 4}


def test_statsmodels_03_exit_zero_escape(sm03, monkeypatch):
    import types

    pytest.importorskip("numpy")

    def _fake_ztest(count, nobs, value=None, **kwargs):
        # two-sample succeeds; one-sample incorrectly accepts None.
        return 1.0, 0.2

    sm = types.ModuleType("statsmodels")
    sm.__version__ = "test-stub"
    stats = types.ModuleType("statsmodels.stats")
    prop = types.ModuleType("statsmodels.stats.proportion")
    prop.proportions_ztest = _fake_ztest
    monkeypatch.setitem(sys.modules, "statsmodels", sm)
    monkeypatch.setitem(sys.modules, "statsmodels.stats", stats)
    monkeypatch.setitem(sys.modules, "statsmodels.stats.proportion", prop)

    payload = sm03.evaluate(0)
    assert payload["observed_output"]["two_sample_ok"] is True
    assert payload["observed_output"]["one_sample_requires_value"] is False
    assert payload["property_holds"] is False
    assert payload["exit_status"] == 1
    assert "one-sample" in payload["expected_property"]
    assert "two-sample" in payload["expected_property"]


def test_handoff_artifact_tamper_rejection():
    if not HANDOFF.is_file():
        pytest.skip("handoff not regenerated yet")
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    files = handoff.get("outputs", {}).get("files", {})
    if "BATCH3_EXECUTION_MATRIX.json" not in files:
        pytest.skip("A1d-r1 handoff outputs not regenerated yet")
    runner = ROOT / "scripts" / "external_slice" / "run_c3_batch3_readiness.py"
    runner_mod = _load(runner, "run_c3_batch3_readiness_under_test")
    target = ROOT / "data" / "external_slice" / "readiness_batch3.json"
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n", encoding="utf-8")
        assert runner_mod.handoff_hash_checker(HANDOFF) == 1
    finally:
        target.write_text(original, encoding="utf-8")
    assert runner_mod.handoff_hash_checker(HANDOFF) == 0
