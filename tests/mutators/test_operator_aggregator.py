import json
import tempfile
from pathlib import Path

from p2.mutators.operator_aggregator import (
    compute_r_sem, compute_d_impl, aggregate_operator_metrics,
)


def test_compute_r_sem_basic():
    trials = [
        {"is_confirmed": True, "operator_match": "Yes"},
        {"is_confirmed": True, "operator_match": "No"},
        {"is_confirmed": False, "operator_match": "Yes"},
        {"is_confirmed": True, "operator_match": "Yes"},
    ]
    # confirmed AND match: 2/4 = 0.5
    assert compute_r_sem(trials) == 0.5


def test_compute_r_sem_no_trials():
    assert compute_r_sem([]) == 0.0


def test_compute_d_impl_with_two_distinct_codes():
    codes = [
        "def program(x):\n    return float(x)\n",
        "def program(x):\n    return float(x) + 1\n",
    ]
    score = compute_d_impl(codes)
    assert 0.0 < score <= 1.0


def test_aggregate_writes_metrics(tmp_path):
    raw = tmp_path / "raw"; raw.mkdir()
    (raw / "a2_OS1.json").write_text(json.dumps([
        {"op_id": "a2_OS1", "attempt_idx": 0, "code": "def program(x):\n    return float(x)\n",
         "v1": True, "v2": "Yes", "v3": "Yes", "v4": "Yes",
         "v5": "Yes", "v6": "Yes", "operator_match": "Yes",
         "overall": "CONFIRMED", "reason": "ok"},
        {"op_id": "a2_OS1", "attempt_idx": 1, "code": "def program(x):\n    return float(x) + 1\n",
         "v1": True, "v2": "Yes", "v3": "Yes", "v4": "Yes",
         "v5": "Yes", "v6": "Yes", "operator_match": "Yes",
         "overall": "CONFIRMED", "reason": "ok"},
    ]))
    out = tmp_path / "out.json"
    metrics = aggregate_operator_metrics(raw_dir=raw, out_path=out, run_avp=False)
    assert "a2_OS1" in metrics
    assert metrics["a2_OS1"]["r_sem"] == 1.0
    assert metrics["a2_OS1"]["d_impl"] >= 0.0
    assert out.exists()
