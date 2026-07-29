"""Deterministic statistics used by the TOSEM M1--M8 revision."""

from __future__ import annotations

import re
from collections.abc import Mapping

import numpy as np

from p2.stats.cliffs_delta import cliffs_delta

CAT2MP = {"CE": 1, "OS": 2, "HP": 3, "TF": 4, "SI": 5}
CAT_RE = re.compile(r"_(CE|OS|HP|TF|SI|CF)\d")


def cell_key(cell: str) -> tuple[str, int]:
    """Return the lower-case PUT identifier and integer MP index."""
    put, mp = cell.split("_MP")
    return put.lower(), int(mp)


def split_aligned_cross(
    sms: Mapping[str, Mapping[str, object]],
    primary: Mapping[str, int],
) -> tuple[list[float], list[float]]:
    """Split SMS values under an explicit, caller-supplied primary map."""
    aligned: list[float] = []
    cross: list[float] = []
    for cell in sorted(sms):
        put, mp = cell_key(cell)
        target = aligned if mp == primary[put] else cross
        target.append(float(sms[cell]["sms"]))
    return aligned, cross


def summarize_lrca(
    lrca: Mapping[str, Mapping[str, object]],
) -> dict[str, float | int]:
    """Summarize LRCA shares under the zero-kill-is-NA convention."""
    evaluable = [row for row in lrca.values() if int(row["n_killed"]) > 0]
    total_kills = sum(int(row["n_killed"]) for row in evaluable)
    c1_kills = sum(
        int(row["labels"]["C1_legit_fault"])  # type: ignore[index]
        for row in evaluable
    )
    return {
        "cells_total": len(lrca),
        "cells_evaluable": len(evaluable),
        "cells_zero_kill_NA": len(lrca) - len(evaluable),
        "macro_mean_c1_share": round(
            float(np.mean([float(row["c1_share"]) for row in evaluable])), 4
        ),
        "macro_mean_suspect_share": round(
            float(np.mean([float(row["suspect_share"]) for row in evaluable])), 4
        ),
        "pooled_c1_share": round(c1_kills / total_kills, 4),
        "pooled_suspect_share": round((total_kills - c1_kills) / total_kills, 4),
        "total_kills": total_kills,
        "c1_kills": c1_kills,
    }


def gap_premise_support(
    sms: Mapping[str, Mapping[str, object]],
    primary: Mapping[str, int],
) -> dict[str, object]:
    """Audit the observable support antecedent of the cross-zero corollary."""
    rows = []
    for cell in sorted(sms):
        put, mp = cell_key(cell)
        positive = set()
        for outcome in sms[cell]["outcomes"]:  # type: ignore[union-attr]
            match = CAT_RE.search(str(outcome["file"]))
            if match and match.group(1) in CAT2MP:
                positive.add(CAT2MP[match.group(1)])
        holds = mp not in positive
        rows.append(
            {
                "cell": cell,
                "aligned": mp == primary[put],
                "sms": float(sms[cell]["sms"]),
                "positive_weight_strata": sorted(positive),
                "antecedent_holds": holds,
            }
        )
    subset = [row for row in rows if row["antecedent_holds"]]
    return {
        "definition": (
            "observable antecedent Cov(R) intersect {j:w_j>0} is empty"
        ),
        "antecedent_holds": len(subset),
        "antecedent_fails": len(rows) - len(subset),
        "antecedent_holds_aligned": sum(bool(row["aligned"]) for row in subset),
        "antecedent_holds_cross": sum(not bool(row["aligned"]) for row in subset),
        "antecedent_holds_zero_sms": sum(row["sms"] == 0 for row in subset),
        "antecedent_holds_nonzero_sms": sum(row["sms"] > 0 for row in subset),
        "antecedent_cells": [row["cell"] for row in subset],
        "per_cell": rows,
    }


def put_cluster_bootstrap(
    sms: Mapping[str, Mapping[str, object]],
    primary: Mapping[str, int],
    *,
    n_boot: int,
    seed: int,
    excluded_cells: set[str] | None = None,
) -> dict[str, object]:
    """Bootstrap Cliff's delta by sampling PUT clusters with replacement."""
    excluded = excluded_cells or set()
    by_put: dict[str, list[tuple[int, float]]] = {}
    for cell in sorted(sms):
        if cell in excluded:
            continue
        put, mp = cell_key(cell)
        by_put.setdefault(put, []).append((mp, float(sms[cell]["sms"])))
    puts = sorted(by_put)

    def materialize(sampled_puts):
        aligned, cross = [], []
        for put in sampled_puts:
            for mp, value in by_put[put]:
                (aligned if mp == primary[put] else cross).append(value)
        return aligned, cross

    observed_aligned, observed_cross = materialize(puts)
    point = cliffs_delta(observed_aligned, observed_cross)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot)
    for index in range(n_boot):
        sampled = rng.choice(puts, size=len(puts), replace=True)
        aligned, cross = materialize(sampled)
        draws[index] = cliffs_delta(aligned, cross)
    return {
        "resampling_unit": "PUT",
        "seed": seed,
        "n_bootstrap": n_boot,
        "n_put_clusters": len(puts),
        "n_aligned": len(observed_aligned),
        "n_cross": len(observed_cross),
        "point_estimate": point,
        "ci_95": [
            float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975)),
        ],
        "bootstrap_fraction_delta_le_zero": float(np.mean(draws <= 0)),
        "bootstrap_median": float(np.median(draws)),
    }
