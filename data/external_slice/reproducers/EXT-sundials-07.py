#!/usr/bin/env python3
"""Dual-arm trigger wrapper for EXT-sundials-07 (SUNDIALS PR #763).

Invokes a prebuilt harness binary with identical arguments on both arms.
Issue-described behaviour: under MRIHTol with SUM fast-error accumulation and
strong scale separation, the relative accuracy (error/tolerance overshoot)
stays within a bounded healthy range rather than growing unbounded.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path


def parse_relative_accuracy(text: str) -> float | None:
    for pattern in (
        r"Relative accuracy\s*[:=]\s*([0-9.eE+-]+)",
        r"relative accuracy\s*[:=]\s*([0-9.eE+-]+)",
    ):
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
    return None


def evaluate(seed: int, harness: Path) -> dict:
    # Seed reserved for harnesses that accept RNG; this unit test is deterministic.
    _ = seed
    cmd = [
        str(harness),
        "--scontrol",
        "5",
        "--faccum",
        "1",
        "--w",
        "100000",
        "--rtol",
        "1e-5",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    rel = parse_relative_accuracy(proc.stdout + "\n" + proc.stderr)
    # Healthy fixed-arm order is O(10-100); decisive buggy observation was ~7228.
    # Bound chosen from the verification report's healthy band with margin.
    bound = 500.0
    property_holds = rel is not None and rel <= bound and proc.returncode == 0
    return {
        "neutral_id": "EXT-sundials-07",
        "seed": seed,
        "input": {
            "harness": str(harness),
            "args": cmd[1:],
            "relative_accuracy_bound": bound,
        },
        "observed_output": {
            "returncode": proc.returncode,
            "relative_accuracy": rel,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-2000:],
        },
        "expected_property": (
            "MRIHTol with SUM accumulation at w=1e5, rtol=1e-5 keeps relative "
            f"accuracy <= {bound} (bounded tolerance tracking)."
        ),
        "property_holds": bool(property_holds),
        "package_version": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "harness_env": {
                "SUNDIALS_INSTALL": os.environ.get("SUNDIALS_INSTALL", ""),
                "HARNESS_BIN": str(harness),
            },
        },
        "exit_status": 0 if property_holds else 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument(
        "--harness",
        type=Path,
        default=Path(os.environ.get("SUNDIALS_HARNESS", "")),
        help="Path to ark_test_kpr_mriadapt harness binary for this arm",
    )
    args = parser.parse_args()
    if not args.harness or not args.harness.is_file():
        raise SystemExit(
            "SUNDIALS harness binary missing; set --harness or SUNDIALS_HARNESS"
        )
    payload = evaluate(args.seed, args.harness)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"property_holds": payload["property_holds"], "package_version": payload["package_version"]}))
    return int(payload["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
