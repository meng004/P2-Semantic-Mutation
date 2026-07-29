#!/usr/bin/env python3
"""Compute the dependence-aware PUT-cluster interval for RQ4/H2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2.config.primary import PRIMARY_CELLS_V3  # noqa: E402
from p2.stats.tosem_revision import put_cluster_bootstrap  # noqa: E402

RESULTS = ROOT / "data/results"
VACANT = {
    "A1_MP5",
    "A2_MP2",
    "A3_MP5",
    "B1_MP3",
    "B1_MP4",
    "B3_MP2",
    "B3_MP5",
    "D2_MP4",
    "D3_MP4",
}


def main() -> None:
    sms = json.loads((RESULTS / "sms_track2_v4.json").read_text())
    report = {
        "method": "percentile PUT-cluster bootstrap of Cliff's delta",
        "cluster_definition": {
            "resampling_unit": "PUT",
            "cells_carried_together": (
                "one aligned and four cross cells before sensitivity exclusions"
            ),
        },
        "input_sms": "sms_track2_v4.json",
        "primary_map": PRIMARY_CELLS_V3,
        "primary_map_source": "p2.config.primary.PRIMARY_CELLS_V3",
        "primary": put_cluster_bootstrap(
            sms, PRIMARY_CELLS_V3, n_boot=100_000, seed=42
        ),
        "vacant_cell_sensitivity": put_cluster_bootstrap(
            sms,
            PRIMARY_CELLS_V3,
            n_boot=100_000,
            seed=42,
            excluded_cells=VACANT,
        ),
        "vacant_cells_excluded": sorted(VACANT),
        "interpretation": (
            "PUT identifiers are sampled with replacement; every sampled "
            "cluster carries its retained aligned and cross cells together."
        ),
    }
    (RESULTS / "rq2_cluster_bootstrap_v4.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )


if __name__ == "__main__":
    main()
