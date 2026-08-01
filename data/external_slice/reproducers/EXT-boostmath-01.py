#!/usr/bin/env python3
"""Dual-arm trigger wrapper for EXT-boostmath-01.

skew_normal quantile is finite and monotone near the issue probability.
Invokes a prebuilt harness binary (or interpreter script) with identical
arguments on both arms. Exit 0 iff the issue-described property holds.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def evaluate(seed: int, harness: Path, harness_args: list[str]) -> dict:
    _ = seed
    cmd = [str(harness), *harness_args]
    if harness.suffix in {".py"}:
        cmd = [sys.executable, str(harness), *harness_args]
    elif harness.suffix in {".jl"}:
        julia = os.environ.get("JULIA_BIN", "julia")
        cmd = [julia, str(harness), *harness_args]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    # Prefer explicit OVERALL/VERDICT markers; else use process exit.
    property_holds = proc.returncode == 0
    for marker in ("OVERALL: PASS", "### VERDICT: PASS", "VERDICT: PASS", "=> ok"):
        if marker in text:
            property_holds = True
    for marker in ("OVERALL: FAIL", "### VERDICT: VIOLATED", "VERDICT: VIOLATED", "VIOLATED"):
        if marker in text and "PASS" not in text.split(marker)[0][-40:]:
            property_holds = False
    return {
        "neutral_id": "EXT-boostmath-01",
        "seed": seed,
        "input": {"harness": str(harness), "args": harness_args},
        "observed_output": {
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-4000:],
            "stderr_tail": (proc.stderr or "")[-2000:],
        },
        "expected_property": """skew_normal quantile is finite and monotone near the issue probability.""",
        "property_holds": bool(property_holds),
        "package_version": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "harness_env": {
                "HARNESS_BIN": str(harness),
                "SUNDIALS_INSTALL": os.environ.get("SUNDIALS_INSTALL", ""),
                "PKG_CONFIG_PATH": os.environ.get("PKG_CONFIG_PATH", ""),
            },
        },
        "exit_status": 0 if property_holds else 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--harness", type=Path, default=Path(os.environ.get("HARNESS_BIN", "")))
    parser.add_argument("harness_args", nargs="*")
    args = parser.parse_args()
    if not args.harness or not args.harness.exists():
        raise SystemExit("harness missing; set --harness or HARNESS_BIN")
    payload = evaluate(args.seed, args.harness, args.harness_args)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"property_holds": payload["property_holds"]}))
    return int(payload["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
