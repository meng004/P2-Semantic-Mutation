#!/usr/bin/env python3
"""Build data/results/syntactic_overlap_v2.json from the existing v4 AST audit.

Reuses scripts/p2_vs_syntactic_ast_diff_batch.py output
(data/results/cosmic_ray_12put_ast_diff.json). v5 addendum deferred until
POOL-SEM v5 lands.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "results" / "cosmic_ray_12put_ast_diff.json"
OUT = ROOT / "data" / "results" / "syntactic_overlap_v2.json"
NORMALISER_SRC = ROOT / "scripts" / "p2_vs_syntactic_ast_diff_batch.py"


def normaliser_id() -> str:
    """Pin the AST normaliser: ast.dump(annotate_fields=False, include_attributes=False)."""
    text = NORMALISER_SRC.read_text()
    h = hashlib.sha256(text.encode()).hexdigest()[:16]
    return f"ast.dump(annotate_fields=False,include_attributes=False)#sha256={h}"


def main() -> None:
    src = json.loads(SRC.read_text())
    agg = src["aggregated"]
    per = agg["per_class_aggregated"]
    n_p2 = agg["n_p2_total"]
    n_overlap = agg["n_overlap_total"]
    rate = agg["overlap_rate_overall"]

    doc = {
        "schema": "syntactic_overlap_v2",
        "engine": "cosmic-ray",
        "engine_version_pin": (
            "cosmic-ray default operator plugin set as recorded in the existing "
            "session DBs data/results/cosmic_ray_{put}.sqlite (engine package not "
            "installed in this PASS-1 environment; pin = artifact lineage of the "
            "1,250-mutant pool, n_cosmic_ray_total=1250). Operator families: "
            "core/NumberReplacer, binary_operator_replacement, "
            "comparison_operator_replacement, unary_operator_replacement, "
            "boolean_replacer, break_continue, exception_replacer, keyword_replacer, "
            "remove_decorator, variable_inserter, variable_replacer, "
            "zero_iteration_for_loop, no_op "
            "(https://github.com/sixty-north/cosmic-ray/tree/master/src/cosmic_ray/operators)."
        ),
        "normaliser_id": normaliser_id(),
        "pool_sem": "v4 (data/mutants/*_pool_v4)",
        "overall": {
            "n_sem": n_p2,
            "n_syn": agg["n_cosmic_ray_total"],
            "n_overlap": n_overlap,
            "overlap_rate": rate,
            "overlap_fraction_str": f"{n_overlap}/{n_p2}",
            "overlap_pct": round(100.0 * rate, 2),
        },
        "per_operator_family": {
            fam: {
                "n_p2": per[fam]["n_p2"],
                "n_overlap": per[fam]["n_overlap"],
                "overlap_rate": per[fam]["rate"],
            }
            for fam in ("HP", "SI", "TF", "CE", "OS", "CF")
            if fam in per
        },
        "headline": (
            f"v4 AST-normalised overlap vs cosmic-ray default = "
            f"{n_overlap}/{n_p2} = {100.0*rate:.2f}%; "
            "HP/SI/TF = 0-overlap; CE/OS/CF partial."
        ),
        "v5_addendum": "pending POOL-SEM v5",
        "source_audit": str(SRC.relative_to(ROOT)),
        "reach_doc": "docs/review_20260728/syntactic_reach.md",
    }
    OUT.write_text(json.dumps(doc, indent=2))
    print(json.dumps(doc["overall"], indent=2))
    print("headline:", doc["headline"])
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
