#!/usr/bin/env python3
"""Foundation-only CLI for the Boost.Math pilot plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import EvidenceError, read_canonical_json  # noqa: E402
from p3_v3.pilot import validate_pilot_plan, write_pilot_plan  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pilot")
    sub = parser.add_subparsers(dest="command", required=True)
    write = sub.add_parser("write-plan")
    write.add_argument("--markdown", required=True)
    write.add_argument("--output", required=True)
    validate = sub.add_parser("validate-plan")
    validate.add_argument("--plan", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "write-plan":
            write_pilot_plan(args.markdown, args.output)
        elif args.command == "validate-plan":
            validate_pilot_plan(read_canonical_json(args.plan))
        else:
            raise EvidenceError("E_CLI_COMMAND", f"unsupported command: {args.command}")
    except EvidenceError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
