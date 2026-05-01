"""R2-T5 (Layer 3 application): AST-level traceability of P2 mutants
vs cosmic-ray syntactic mutants on a1 PUT.

Question: Are P2's a1 mutants reproducible by cosmic-ray's default
operator set? Or are they genuinely outside the syntactic-tool's
reachable mutant space?

Method:
- For each P2 a1 mutant in data/mutants/a1_pool_v4/ (or a1_pool_v3/
  fallback), parse the source to a normalized AST string.
- For each cosmic-ray-generated a1 mutant (extract from the .sqlite
  session), do the same.
- Compute pairwise AST equality + per-P2-mutant lookup: does any
  cosmic-ray mutant match this P2 mutant in normalized AST?
- Report: |P2|, |syn|, overlap count, overlap rate, per-class breakdown
  (CE / OS / HP / TF / SI: how many P2 mutants in each class have
  a syntactic counterpart).

Output: data/results/cosmic_ray_a1_ast_diff.json

Run:
  PYTHONPATH=src .venv/bin/python scripts/p2_vs_syntactic_ast_diff.py
"""
from __future__ import annotations
import ast
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
P2_POOL_CANDIDATES = [
    ROOT / "data/mutants/a1_pool_v4",
    ROOT / "data/mutants/a1_pool_v3",
    ROOT / "data/mutants/a1_pool",
]
CR_DB = ROOT / "data/results/cosmic_ray_a1.sqlite"
OUT = ROOT / "data/results/cosmic_ray_a1_ast_diff.json"

p2_pool = next((p for p in P2_POOL_CANDIDATES if p.exists()), None)
if p2_pool is None:
    print("FATAL: no P2 a1 mutant pool found", file=sys.stderr)
    sys.exit(2)


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


p2_mutants = {}
for f in p2_pool.glob("*.py"):
    src = f.read_text()
    p2_mutants[f.name] = {
        "source": src,
        "ast_norm": normalize_source(src),
        "op_class": operator_class_of_p2_mutant(f.name),
    }
print(f"P2 a1 mutants loaded: {len(p2_mutants)}")

# Reconstruct cosmic-ray syntactic mutants: cosmic-ray stores a `diff`
# (unified-diff text) per work_result. We need to APPLY each diff to
# the original a1.py source and AST-normalize the result. The original
# source is preserved in the same diff (via `--- a` and `+++ b` headers).
ORIG_PUT = ROOT / "src/p2/puts/a1.py"
orig_source = ORIG_PUT.read_text() if ORIG_PUT.exists() else ""


def apply_unified_diff(orig: str, diff_text: str) -> str | None:
    """Lightweight unified-diff applier. Returns mutated source or None."""
    if not diff_text or not diff_text.strip():
        return None
    orig_lines = orig.splitlines(keepends=True)
    out_lines: list[str] = []
    cursor = 0  # index into orig_lines
    diff_lines = diff_text.splitlines(keepends=False)
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        if line.startswith("---") or line.startswith("+++"):
            i += 1
            continue
        if line.startswith("@@"):
            # parse @@ -a,b +c,d @@
            try:
                hdr = line.split("@@")[1].strip()
                minus = hdr.split(" ")[0]  # -a,b
                start = int(minus.split(",")[0].lstrip("-")) - 1
            except Exception:
                return None
            # copy any orig lines before hunk start
            while cursor < start:
                if cursor >= len(orig_lines):
                    break
                out_lines.append(orig_lines[cursor])
                cursor += 1
            i += 1
            # process hunk body
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
                    # unknown line type — bail
                    i += 1
            continue
        i += 1
    # copy remaining orig lines
    while cursor < len(orig_lines):
        out_lines.append(orig_lines[cursor])
        cursor += 1
    return "".join(out_lines)


syntactic_ast_norms: set[str] = set()
n_cr = 0
n_cr_parse_failed = 0
n_cr_diff_apply_failed = 0
cr_outcome_counts: dict[str, int] = {}

if CR_DB.exists():
    conn = sqlite3.connect(CR_DB)
    try:
        cur = conn.execute(
            "SELECT diff, test_outcome FROM work_results"
        )
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
                # still index the parse-error fingerprint so we can
                # detect identical parse-error mutants
            syntactic_ast_norms.add(norm)
            n_cr += 1
    finally:
        conn.close()

print(f"cosmic-ray syntactic mutants loaded: {n_cr}")
print(f"  cr outcome breakdown: {cr_outcome_counts}")
print(f"  cr unique normalized ASTs: {len(syntactic_ast_norms)}")
print(f"  cr diff-apply failures: {n_cr_diff_apply_failed}")
print(f"  cr post-mutation parse failures: {n_cr_parse_failed}")

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

report = {
    "p2_pool_dir": str(p2_pool.relative_to(ROOT)),
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
    "interpretation": (
        "overlap_rate_overall is the fraction of P2 a1 mutants whose "
        "normalized AST is also produced by cosmic-ray's default "
        "operators on the same source. Low overall rate (<0.5) indicates "
        "P2 mutants are NOT a subset of syntactic mutants."
    ),
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(f"overall overlap rate: {report['overlap_rate_overall']:.4f}")
print(f"per-class: {report['per_operator_class']}")
print(f"-> {OUT}")
