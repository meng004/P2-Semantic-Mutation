"""Regenerate cosmic_ray_${PUT}_summary.json from sqlite directly.

The bash wrapper run_cosmic_ray_put.sh exits 120 for some PUTs because
`cr-report ... | head -200` triggers SIGPIPE in pipefail mode AFTER the
sqlite is complete. The data is fine; only the summary write is missing.

This script reads each cosmic_ray_${PUT}.sqlite and emits a
cosmic_ray_${PUT}_summary.json with mutants_total / killed / survived /
incompetent / survival_rate, replacing the regex-based parser whose
fields are often null.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data/results"

PUTS = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3", "d1", "d2", "d3"]


def summarize(put_id: str) -> dict | None:
    db = RESULTS / f"cosmic_ray_{put_id}.sqlite"
    if not db.exists():
        print(f"  {put_id}: sqlite missing -> SKIP")
        return None

    con = sqlite3.connect(str(db))
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}

    total = killed = survived = incompetent = None
    if "work_results" in tables:
        cur.execute("SELECT COUNT(*) FROM work_items")
        total = cur.fetchone()[0]
        cur.execute("SELECT test_outcome, COUNT(*) FROM work_results GROUP BY test_outcome")
        outcomes = {k.upper() if k else k: v for k, v in cur.fetchall()}
        killed = outcomes.get("KILLED", 0)
        survived = outcomes.get("SURVIVED", 0)
        incompetent = outcomes.get("INCOMPETENT", 0)
    con.close()

    if total and (killed is not None) and (survived is not None):
        denom = total - (incompetent or 0)
        survival = (survived / denom) if denom else None
    else:
        survival = None

    test_files_str = (
        "tests/puts/test_a1.py + tests/puts/test_a1_scalar_interface.py"
        if put_id == "a1"
        else f"tests/puts/test_{put_id}.py"
    )

    summary = {
        "tool": "cosmic-ray",
        "put_id": put_id,
        "target_put": f"src/p2/puts/{put_id}.py",
        "test_suite": test_files_str,
        "mutants_total": total,
        "killed": killed,
        "survived": survived,
        "incompetent": incompetent,
        "survival_rate": survival,
        "interpretation": (
            "Per §3.2.6.1, cosmic-ray's default operators are AST-local "
            "(BinOp/Compare/BoolOp/etc.); none can express OS/HP/TF/SI. The "
            "mutant kill rate observed here reflects only that subset of P2's "
            "five operator classes that maps to CE-style literal edits. The "
            "qualitative implication — syntactic tools cover at most 1/5 of "
            "P2's semantic operator space — is robust to the specific kill "
            "rate value observed."
        ),
    }
    out = RESULTS / f"cosmic_ray_{put_id}_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(
        f"  {put_id}: total={total} killed={killed} survived={survived} "
        f"incompetent={incompetent} survival={survival}"
    )
    return summary


def main():
    print("Regenerating cosmic-ray summaries from sqlite ...")
    rows = []
    for put in PUTS:
        s = summarize(put)
        if s:
            rows.append(s)
    print(f"\nTotal PUTs summarized: {len(rows)}/{len(PUTS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
