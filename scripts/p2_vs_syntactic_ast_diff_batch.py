"""R2-T5 (Layer 3 application) NEW-MAJOR-1 batch generalization:
AST-level traceability of P2 mutants vs cosmic-ray syntactic mutants
across all 12 PUTs (a1, a2, a3, b1, ..., d3).

This is the batch generalization of scripts/p2_vs_syntactic_ast_diff.py.
For each PUT it:
  - Finds the P2 mutant pool dir (preferring _pool_v4 -> _pool_v3 -> _pool).
  - Looks for data/results/cosmic_ray_<PUT_ID>.sqlite. If absent, the
    PUT's per-PUT entry is recorded as null and counted toward
    n_puts_without_cr_data (because the user has not yet invoked
    scripts/run_cosmic_ray_put.sh on that PUT).
  - If present, runs the same AST diff logic as the a1 script.

Aggregated: per-class overlap rate across all PUTs that DO have
cosmic-ray data (weighted-sum union of per-class numerators &
denominators), plus overall overlap rate.

Output: data/results/cosmic_ray_12put_ast_diff.json

Run:
  PYTHONPATH=src .venv/bin/python scripts/p2_vs_syntactic_ast_diff_batch.py
"""
from __future__ import annotations
import ast
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ALL_PUTS = [
    "a1", "a2", "a3",
    "b1", "b2", "b3",
    "c1", "c2", "c3",
    "d1", "d2", "d3",
]


def normalize_source(source: str) -> str:
    try:
        tree = ast.parse(source)
        return ast.dump(tree, annotate_fields=False, include_attributes=False)
    except SyntaxError:
        return f"__PARSE_ERROR__:{hash(source)}"


def operator_class_of_p2_mutant(filename: str) -> str:
    parts = filename.split("_")
    if len(parts) < 2:
        return "unknown"
    op = parts[2] if len(parts) >= 3 else parts[1]
    for cls in ("CE", "OS", "HP", "TF", "SI", "CF"):
        if op.startswith(cls):
            return cls
    return "unknown"


def apply_unified_diff(orig: str, diff_text: str) -> str | None:
    """Lightweight unified-diff applier. Returns mutated source or None."""
    if not diff_text or not diff_text.strip():
        return None
    orig_lines = orig.splitlines(keepends=True)
    out_lines: list[str] = []
    cursor = 0
    diff_lines = diff_text.splitlines(keepends=False)
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        if line.startswith("---") or line.startswith("+++"):
            i += 1
            continue
        if line.startswith("@@"):
            try:
                hdr = line.split("@@")[1].strip()
                minus = hdr.split(" ")[0]
                start = int(minus.split(",")[0].lstrip("-")) - 1
            except Exception:
                return None
            while cursor < start:
                if cursor >= len(orig_lines):
                    break
                out_lines.append(orig_lines[cursor])
                cursor += 1
            i += 1
            while i < len(diff_lines) and not diff_lines[i].startswith("@@"):
                hl = diff_lines[i]
                if hl.startswith("---") or hl.startswith("+++"):
                    i += 1
                    continue
                if hl.startswith(" "):
                    if cursor < len(orig_lines):
                        out_lines.append(orig_lines[cursor])
                        cursor += 1
                    i += 1
                elif hl.startswith("-"):
                    cursor += 1
                    i += 1
                elif hl.startswith("+"):
                    out_lines.append(hl[1:] + "\n")
                    i += 1
                else:
                    i += 1
            continue
        i += 1
    while cursor < len(orig_lines):
        out_lines.append(orig_lines[cursor])
        cursor += 1
    return "".join(out_lines)


def find_pool_dir(put_id: str) -> Path | None:
    candidates = [
        ROOT / f"data/mutants/{put_id}_pool_v4",
        ROOT / f"data/mutants/{put_id}_pool_v3",
        ROOT / f"data/mutants/{put_id}_pool",
    ]
    return next((p for p in candidates if p.exists()), None)


def analyze_put(put_id: str) -> dict | None:
    """Return per-PUT AST-diff record, or None if cosmic-ray data missing."""
    cr_db = ROOT / f"data/results/cosmic_ray_{put_id}.sqlite"
    pool_dir = find_pool_dir(put_id)
    orig_put = ROOT / f"src/p2/puts/{put_id}.py"

    if not cr_db.exists():
        return None
    if pool_dir is None:
        # Pool missing too — still null (cannot compare without P2 mutants)
        return None

    # Load P2 mutants
    p2_mutants: dict[str, dict] = {}
    for f in pool_dir.glob("*.py"):
        src = f.read_text()
        p2_mutants[f.name] = {
            "source": src,
            "ast_norm": normalize_source(src),
            "op_class": operator_class_of_p2_mutant(f.name),
        }

    orig_source = orig_put.read_text() if orig_put.exists() else ""

    syntactic_ast_norms: set[str] = set()
    n_cr = 0
    n_cr_parse_failed = 0
    n_cr_diff_apply_failed = 0
    cr_outcome_counts: dict[str, int] = {}

    conn = sqlite3.connect(cr_db)
    try:
        cur = conn.execute("SELECT diff, test_outcome FROM work_results")
        for diff, outcome in cur.fetchall():
            cr_outcome_counts[outcome] = cr_outcome_counts.get(outcome, 0) + 1
            if not isinstance(diff, str) or len(diff) < 10:
                continue
            mutated = apply_unified_diff(orig_source, diff)
            if mutated is None:
                n_cr_diff_apply_failed += 1
                continue
            norm = normalize_source(mutated)
            if norm.startswith("__PARSE_ERROR__"):
                n_cr_parse_failed += 1
            syntactic_ast_norms.add(norm)
            n_cr += 1
    finally:
        conn.close()

    overlap_count = 0
    per_class_total: dict[str, int] = {}
    per_class_overlap: dict[str, int] = {}
    overlap_files: list[str] = []

    for fname, m in p2_mutants.items():
        cls = m["op_class"]
        per_class_total[cls] = per_class_total.get(cls, 0) + 1
        if m["ast_norm"] in syntactic_ast_norms:
            overlap_count += 1
            per_class_overlap[cls] = per_class_overlap.get(cls, 0) + 1
            overlap_files.append(fname)

    per_class_rate = {
        cls: per_class_overlap.get(cls, 0) / per_class_total[cls]
        for cls in per_class_total
    }

    return {
        "put_id": put_id,
        "p2_pool_dir": str(pool_dir.relative_to(ROOT)),
        "n_p2_mutants": len(p2_mutants),
        "n_cosmic_ray_mutants": n_cr,
        "n_cosmic_ray_unique_asts": len(syntactic_ast_norms),
        "n_cosmic_ray_diff_apply_failed": n_cr_diff_apply_failed,
        "n_cosmic_ray_post_mutation_parse_failed": n_cr_parse_failed,
        "cosmic_ray_outcome_counts": cr_outcome_counts,
        "n_overlap": overlap_count,
        "overlap_rate_overall": (
            overlap_count / len(p2_mutants) if p2_mutants else 0
        ),
        "per_operator_class": {
            cls: {
                "n_p2": per_class_total[cls],
                "n_overlap": per_class_overlap.get(cls, 0),
                "overlap_rate": per_class_rate[cls],
            }
            for cls in sorted(per_class_total)
        },
        "overlap_files": overlap_files,
    }


def main() -> int:
    per_put: dict[str, dict | None] = {}
    n_with = 0
    n_without = 0
    puts_with_data: list[str] = []
    puts_without_data: list[str] = []

    for put_id in ALL_PUTS:
        rec = analyze_put(put_id)
        per_put[put_id] = rec
        if rec is None:
            n_without += 1
            puts_without_data.append(put_id)
            print(f"  {put_id}: SKIP (no cosmic_ray_{put_id}.sqlite)")
        else:
            n_with += 1
            puts_with_data.append(put_id)
            print(
                f"  {put_id}: |P2|={rec['n_p2_mutants']}, "
                f"|CR|={rec['n_cosmic_ray_mutants']}, "
                f"overlap={rec['n_overlap']} "
                f"({rec['overlap_rate_overall']:.4f})"
            )

    # Aggregate (only over PUTs that have cosmic-ray data)
    n_p2_total = 0
    n_cr_total = 0
    n_overlap_total = 0
    per_class_agg: dict[str, dict[str, int]] = {}

    for put_id in puts_with_data:
        rec = per_put[put_id]
        assert rec is not None
        n_p2_total += rec["n_p2_mutants"]
        n_cr_total += rec["n_cosmic_ray_mutants"]
        n_overlap_total += rec["n_overlap"]
        for cls, stats in rec["per_operator_class"].items():
            agg = per_class_agg.setdefault(cls, {"n_p2": 0, "n_overlap": 0})
            agg["n_p2"] += stats["n_p2"]
            agg["n_overlap"] += stats["n_overlap"]

    per_class_aggregated = {
        cls: {
            "n_p2": agg["n_p2"],
            "n_overlap": agg["n_overlap"],
            "rate": (agg["n_overlap"] / agg["n_p2"]) if agg["n_p2"] else 0.0,
        }
        for cls, agg in sorted(per_class_agg.items())
    }

    overlap_rate_overall = (
        n_overlap_total / n_p2_total if n_p2_total else 0.0
    )

    report = {
        "n_puts_with_cr_data": n_with,
        "n_puts_without_cr_data": n_without,
        "puts_with_cr_data": puts_with_data,
        "puts_without_cr_data": puts_without_data,
        "per_put": per_put,
        "aggregated": {
            "n_p2_total": n_p2_total,
            "n_cosmic_ray_total": n_cr_total,
            "n_overlap_total": n_overlap_total,
            "overlap_rate_overall": overlap_rate_overall,
            "per_class_aggregated": per_class_aggregated,
        },
        "interpretation": (
            "Per-PUT records are null when cosmic-ray has not yet been "
            "run on that PUT (i.e., data/results/cosmic_ray_<PUT_ID>.sqlite "
            "is absent). Run scripts/run_cosmic_ray_put.sh <PUT_ID> for "
            "each missing PUT then re-run this batch script. Aggregation "
            "is computed only over PUTs with cosmic-ray data; per-class "
            "rate is the union ratio (sum of overlap counts over sum of "
            "P2 mutants) across PUTs in scope."
        ),
    }

    out = ROOT / "data/results/cosmic_ray_12put_ast_diff.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print()
    print(
        f"PUTs with cosmic-ray data: {n_with}/{len(ALL_PUTS)} "
        f"({puts_with_data})"
    )
    print(
        f"PUTs awaiting cosmic-ray run: {n_without}/{len(ALL_PUTS)} "
        f"({puts_without_data})"
    )
    print(f"Aggregated overall overlap rate: {overlap_rate_overall:.4f}")
    print(f"Per-class aggregated: {per_class_aggregated}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
