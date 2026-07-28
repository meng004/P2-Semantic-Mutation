#!/usr/bin/env python3
"""Manuscript ↔ SSOT numeric consistency gate (Phase 0 Task 0.2).

Extracts decimal statistics near keywords (delta / CI / p / mean) from a
LaTeX manuscript and checks each against values present in the SSOT JSON.
Unknown manuscript numbers that look like claimed cliffs-delta / CI / mean
statistics fail the gate.

Schema notes (R-7):
  - ``SMS_strict`` / ``SMS_cons`` keys are reserved for theory Task T5.2;
    their absence or null is allowed until the key-migration gate lands.
  - v4 H2 dual estimands: ``rq2`` = MP1/v3b sensitivity; ``rq2_primary_mp5``
    = frozen-MP5 primary (see docs/review_20260728/ssot_reconciliation.md).

Usage:
  python scripts/check_ssot_consistency.py \\
      submission/TOSEM_fastimpact_20260707/main.tex \\
      data/results/paper_numbers_v4.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable

# Keyword tokens matched as whole words / TeX macros to cut false hits
# (e.g. LaTeX column `p{0.24`, DOI fragments, package versions).
KEYWORDS = ("delta", "cliff", "mean", "median", "sms")
KEYWORD_RES: list[tuple[str, re.Pattern[str]]] = [
    ("delta", re.compile(r"(?<![a-zA-Z])delta(?![a-zA-Z])", re.I)),
    ("cliff", re.compile(r"(?<![a-zA-Z])cliff(?:'?s)?(?![a-zA-Z])", re.I)),
    ("mean", re.compile(r"(?<![a-zA-Z])mean(?![a-zA-Z])", re.I)),
    ("median", re.compile(r"(?<![a-zA-Z])median(?![a-zA-Z])", re.I)),
    ("sms", re.compile(r"(?<![a-zA-Z])sms(?![a-zA-Z])", re.I)),
    # "95% CI" / "CI [" but not bare "ci" inside words
    ("CI", re.compile(r"(?:95\s*\\?%\s*)?CI\s*(?:\{\[\}|\[|:)", re.I)),
    # p-values: "p =", "p<", "p-value", not TeX `p{...}`
    ("p", re.compile(r"(?<![a-zA-Z\\])p\s*(?:=|<|>|\\le|\\ge|\\lt|\\gt|-?value)", re.I)),
]
# Window (chars) around a number within which a keyword must appear.
WINDOW = 64
# Absolute tolerance for float compare after rounding to reported precision.
ABS_TOL = 5e-4

# Explicit headline bindings that MUST match (manuscript primary narrative).
# Each entry: (SSOT dotted key, manuscript regex, decimals for display).
# TOSEM v4 primary sentence shape (allowing LaTeX {[}/{]} wrappers + newlines):
#   v4 (cross-source, c-class held at partial-order): delta = \textbf{0.314},
#   95\% CI {[}0.014, 0.622{]}.
_V4_PRIMARY_BLOCK = re.compile(
    # Label may be wrapped as \textbf{v4 (...):} with the closing brace
    # before "delta ="; value may sit on the next line inside \textbf{}.
    r"v4\s*\([^)]*partial-order[^)]*\)\s*:\}?\s*delta\s*=\s*"
    r"(?:\\textbf\{)?(?P<delta>\d+\.\d{2,4})(?:\})?\s*,\s*"
    r"95\\%\s*CI\s*(?:\{\[\}|\[)(?P<lo>\d+\.\d{2,4}),\s*"
    r"(?P<hi>\d+\.\d{2,4})(?:\{\]\}|\])",
    re.IGNORECASE | re.DOTALL,
)
REQUIRED_BINDINGS = [
    ("rq2_primary_mp5.cliffs_delta", "delta", 3),
    ("rq2_primary_mp5.delta_ci_95_lo", "lo", 3),
    ("rq2_primary_mp5.delta_ci_95_hi", "hi", 3),
]

NUM_RE = re.compile(r"(?<![\w.])(\d+\.\d{2,4})(?![\w.])")


def _flatten(obj: Any, prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.update(_flatten(v, key))
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return out
        out[prefix] = float(obj)
    return out


def _get_dotted(ssot: dict[str, Any], dotted: str) -> Any:
    cur: Any = ssot
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(dotted)
        cur = cur[part]
    return cur


def _nearby_keyword(text: str, start: int, end: int) -> str | None:
    lo = max(0, start - WINDOW)
    hi = min(len(text), end + WINDOW)
    ctx = text[lo:hi]
    for label, rx in KEYWORD_RES:
        if rx.search(ctx):
            return label
    return None


def _matches_ssot(val: float, ssot_vals: Iterable[float]) -> bool:
    for s in ssot_vals:
        # Compare at the manuscript's apparent precision (2–4 dp).
        for nd in (2, 3, 4):
            if abs(round(val, nd) - round(s, nd)) <= ABS_TOL:
                return True
        if abs(val - s) <= ABS_TOL:
            return True
    return False


def extract_keyword_numbers(tex: str) -> list[tuple[float, str, int, str]]:
    """Return (value, keyword, line_no, context) for keyword-adjacent decimals."""
    hits: list[tuple[float, str, int, str]] = []
    for m in NUM_RE.finditer(tex):
        kw = _nearby_keyword(tex, m.start(), m.end())
        if kw is None:
            continue
        val = float(m.group(1))
        line_no = tex.count("\n", 0, m.start()) + 1
        ctx = tex[max(0, m.start() - 24) : m.end() + 24].replace("\n", " ")
        hits.append((val, kw, line_no, ctx))
    return hits


def check_required_bindings(
    tex: str, ssot: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    m = _V4_PRIMARY_BLOCK.search(tex)
    if not m:
        errors.append(
            "REQUIRED BINDING BLOCK NOT FOUND: v4 (…partial-order…): "
            "delta = <val>, 95% CI [<lo>, <hi>]"
        )
        return errors
    for key, group, nd in REQUIRED_BINDINGS:
        try:
            expected = float(_get_dotted(ssot, key))
        except KeyError:
            errors.append(f"MISSING SSOT KEY for required binding: {key}")
            continue
        got = float(m.group(group))
        if abs(round(got, nd) - round(expected, nd)) > ABS_TOL:
            errors.append(
                f"BINDING MISMATCH {key}: manuscript={got} "
                f"SSOT={round(expected, nd)}"
            )
    return errors


def check_schema_reserved(ssot: dict[str, Any]) -> list[str]:
    """Ensure dual-equivalence keys exist (null allowed until T5.2)."""
    warns: list[str] = []
    for key in ("SMS_strict", "SMS_cons"):
        if key not in ssot:
            warns.append(
                f"SCHEMA: reserved key '{key}' missing "
                "(add null placeholder; populate after theory T5.2)"
            )
    return warns


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tex", type=Path, help="Path to main.tex")
    ap.add_argument("ssot", type=Path, help="Path to paper_numbers_*.json")
    ap.add_argument(
        "--strict-orphan",
        action="store_true",
        help=(
            "Fail on keyword-adjacent decimals that match no SSOT value "
            "(default: report as warnings; required bindings still hard-fail)"
        ),
    )
    args = ap.parse_args(argv)

    tex = args.tex.read_text(encoding="utf-8")
    ssot = json.loads(args.ssot.read_text(encoding="utf-8"))
    flat = _flatten(ssot)
    ssot_vals = list(flat.values())

    errors: list[str] = []
    warnings: list[str] = []

    warnings.extend(check_schema_reserved(ssot))
    errors.extend(check_required_bindings(tex, ssot))

    # Dual-estimand presence for v4 SSOT.
    if "rq2" in ssot and "rq2_primary_mp5" not in ssot:
        errors.append(
            "SSOT missing rq2_primary_mp5 (H2 frozen-MP5 primary). "
            "Rebuild with scripts/build_paper_numbers.py SMS_VERSION=v4 "
            "after rq2_cliffs_delta_v4_mp5.json exists."
        )

    orphans: list[tuple[float, str, int, str]] = []
    matched = 0
    for val, kw, line_no, ctx in extract_keyword_numbers(tex):
        if _matches_ssot(val, ssot_vals):
            matched += 1
        else:
            orphans.append((val, kw, line_no, ctx))

    print(f"SSOT file: {args.ssot}")
    print(f"Manuscript: {args.tex}")
    print(f"SSOT numeric leaves: {len(flat)}")
    print(f"Keyword-adjacent decimals matched: {matched}")
    print(f"Keyword-adjacent decimals unmatched: {len(orphans)}")

    if "rq2" in ssot and "rq2_primary_mp5" in ssot:
        d_sens = ssot["rq2"].get("cliffs_delta")
        d_pri = ssot["rq2_primary_mp5"].get("cliffs_delta")
        print(
            f"Dual estimands: rq2 (sensitivity MP1) δ={d_sens}; "
            f"rq2_primary_mp5 (H2 primary) δ={d_pri}"
        )
        if d_sens is not None and d_pri is not None and abs(d_sens - d_pri) < ABS_TOL:
            errors.append(
                "rq2 and rq2_primary_mp5 cliffs_delta are identical; "
                "dual-estimand separation collapsed"
            )

    if orphans:
        print("\n--- unmatched keyword-adjacent decimals ---")
        for val, kw, line_no, ctx in orphans[:40]:
            msg = f"L{line_no} ({kw}) {val}: …{ctx}…"
            print(msg)
            if args.strict_orphan:
                errors.append(msg)
            else:
                warnings.append(msg)
        if len(orphans) > 40:
            print(f"… ({len(orphans) - 40} more)")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print(f"\nDIFF TABLE / ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print("\nFAIL: manuscript–SSOT consistency gate")
        return 1

    print("\nPASS: manuscript–SSOT consistency gate (exit 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
