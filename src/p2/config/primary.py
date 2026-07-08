"""Single source of truth for per-PUT primary MP assignments.

Used across scripts/sms_campaign.py, scripts/run_lrca.py, scripts/compute_rq*.py,
scripts/build_paper_numbers.py, scripts/calibrate_lrca.py, etc.

Phase B (2026-05-01) data-driven c-class primary MP override is set via
env var P2_PRIMARY_VERSION:
  - "v3" (default): original P1-derived assignments (c1/c2/c3 → MP5)
  - "v3b":           c1/c2/c3 reassigned per data/results/c_class_mp_ranking.json

Resolution at import time: callers should re-import or read PRIMARY_CELLS
fresh after changing the env var.
"""
import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]

PRIMARY_CELLS_V3 = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
    # Study-2 expansion (18 new PUTs). Same deterministic class→MP rule:
    # A→MP1 (conservation), B→MP2 (monotonicity), C→MP5 (partial-order),
    # D→MP2 (monotonicity). Authored blind to mutation outcomes; final
    # primary designation is owned by the E1 pre-registration agent.
    "a4": 1, "a5": 1, "a6": 1, "a7": 1, "a8": 1,
    "b4": 2, "b5": 2, "b6": 2, "b7": 2,
    "c4": 5, "c5": 5, "c6": 5, "c7": 5,
    "d4": 2, "d5": 2, "d6": 2, "d7": 2, "d8": 2,
}


def _load_v3b():
    """Read data-driven c-class primary from c_class_mp_ranking.json if present."""
    f = _ROOT / "data/results/c_class_mp_ranking.json"
    if not f.exists():
        return PRIMARY_CELLS_V3
    try:
        d = json.loads(f.read_text())
        new_mp = int(d["new_primary_recommended"].replace("MP", ""))
        out = dict(PRIMARY_CELLS_V3)
        for c in ("c1", "c2", "c3"):
            out[c] = new_mp
        return out
    except (KeyError, ValueError, json.JSONDecodeError):
        return PRIMARY_CELLS_V3


_VERSION = os.environ.get("P2_PRIMARY_VERSION", "v3")
PRIMARY_CELLS = _load_v3b() if _VERSION == "v3b" else PRIMARY_CELLS_V3
