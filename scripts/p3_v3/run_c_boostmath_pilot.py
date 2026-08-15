#!/usr/bin/env python3
"""Run the isolated C-BOOSTMATH-001 PILOT_ONLY replay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.pilot_c_boostmath import run_pilot  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--p12-root",
        type=Path,
        default=ROOT / ".pilot-work" / "P12-Defect4MR",
    )
    parser.add_argument(
        "--boost-git",
        type=Path,
        default=ROOT / ".pilot-work" / "boost-math",
    )
    parser.add_argument(
        "--boost-fixed",
        type=Path,
        default=ROOT / ".pilot-work" / "boost-math-fixed",
    )
    parser.add_argument(
        "--boost-buggy",
        type=Path,
        default=ROOT / ".pilot-work" / "boost-math-buggy",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "data" / "p3_v3" / "pilots" / "c-boostmath-001",
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=ROOT / ".pilot-work" / "builds",
    )
    parser.add_argument(
        "--research-dir",
        type=Path,
        default=ROOT / "research" / "p3_v3" / "pilots" / "c-boostmath-001",
    )
    parser.add_argument(
        "--historical-sealed",
        type=Path,
        default=ROOT / ".pilot-work" / "p12-historical-sealed" / "results-partial.jsonl",
    )
    args = parser.parse_args()
    result = run_pilot(
        repo_root=args.repo_root,
        p12_root=args.p12_root,
        boost_git=args.boost_git,
        boost_fixed=args.boost_fixed,
        boost_buggy=args.boost_buggy,
        out_dir=args.out_dir,
        work_dir=args.work_dir,
        research_dir=args.research_dir,
        historical_sealed=args.historical_sealed if args.historical_sealed.exists() else None,
        install_record={
            "commands": [
                "sudo apt-get update -qq",
                "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libboost-dev python3-pytest python3-yaml python3-pip",
            ],
            "packages": {
                "g++": "13.3.0-6ubuntu2~24.04.1",
                "libboost-dev": "1.83.0.1ubuntu2",
                "libboost1.83-dev": "1.83.0-2.1ubuntu3.2",
                "python3-pytest": "7.4.4-1",
            },
            "reason": "ordinary build and test dependencies; compiler and optimization were not changed to chase an outcome",
        },
    )
    summary = {
        "certifications": {
            item["fixture_id"]: item["terminal_state"]
            for item in result["certifications"]
        },
        "comparison_sha256": result["comparison"]["artifact_sha256"],
        "contract_sha256": result["contract_sha256"],
        "ledger_sha256": result["ledger_sha256"],
        "observed_single_case_mr_difference": result["comparison"][
            "observed_single_case_mr_difference"
        ],
        "row_count": len(result["atomic_rows"]),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
