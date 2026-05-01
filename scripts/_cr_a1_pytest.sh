#!/usr/bin/env bash
# Wrapper to set PYTHONPATH for cosmic-ray's subprocess.run() invocation
# (cosmic-ray uses shlex.split which doesn't honor VAR=val command prefixes).
cd "$(dirname "$0")/.."
PYTHONPATH=src exec .venv/bin/pytest -q tests/puts/test_a1.py tests/puts/test_a1_scalar_interface.py
