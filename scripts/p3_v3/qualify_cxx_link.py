#!/usr/bin/env python3
"""Zero-argument C++ compile-link-run qualification CLI."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import EvidenceError  # noqa: E402
from p3_v3.toolchain_qualification import (  # noqa: E402
    FROZEN_ROOT,
    run_qualification,
)


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(prog="qualify_cxx_link")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    try:
        result = run_qualification(
            repo_root=ROOT,
            qualification_root=FROZEN_ROOT,
            env=dict(os.environ),
        )
    except EvidenceError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(f"{result['terminal_status']} {FROZEN_ROOT}")
    if result["terminal_status"] == "PASS":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
