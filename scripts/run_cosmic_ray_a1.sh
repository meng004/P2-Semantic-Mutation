#!/usr/bin/env bash
# R-15 (P2): cosmic-ray ablation on a single PUT (a1) as future-work hook.
# Demonstrates that first-order syntactic mutation tools generate mutants
# whose structure stays AST-local and does NOT cover P2's OS/HP/TF/SI
# operator classes (per §3.2.6.1 operator-level cross-table).
#
# Wall-clock estimate: 5–15 min on a 4-core laptop, depending on
# baseline test runtime.
#
# Run from repo root:
#   bash scripts/run_cosmic_ray_a1.sh
#
# Output:
#   data/results/cosmic_ray_a1_summary.json
#   data/results/cosmic_ray_a1_console.log
#
# This script is gated behind explicit invocation (not part of CI) because:
# (a) cosmic-ray is not in requirements-frozen.txt by default;
# (b) the result is supplementary to §3.2.6.1 which already closes R-15
#     at the operator-level argument.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  echo "ERROR: .venv not found; run pyhon3.12 -m venv .venv first" >&2
  exit 1
fi

# 1. Install cosmic-ray into the venv (one-time)
.venv/bin/pip install -q "cosmic-ray>=8" || {
  echo "pip install cosmic-ray failed" >&2
  exit 1
}

# 2. Write a minimal cosmic-ray TOML config targeting a1.py
CONF=".cr-a1.toml"
cat > "$CONF" <<'TOML'
[cosmic-ray]
module-path = "src/p2/puts/a1.py"
timeout = 30
excluded-modules = []
test-command = "bash scripts/_cr_a1_pytest.sh"

[cosmic-ray.distributor]
name = "local"
TOML

# 3. Initialize session and execute mutants
SESSION="data/results/cosmic_ray_a1.sqlite"
LOG="data/results/cosmic_ray_a1_console.log"
SUMMARY="data/results/cosmic_ray_a1_summary.json"

mkdir -p data/results
rm -f "$SESSION"

{
  echo "=== cosmic-ray init ==="
  .venv/bin/cosmic-ray init "$CONF" "$SESSION"
  echo
  echo "=== cosmic-ray baseline ==="
  .venv/bin/cosmic-ray --verbosity=INFO baseline "$CONF" || {
    echo "BASELINE FAILED: tests don't pass on the unmutated module"
    exit 2
  }
  echo
  echo "=== cosmic-ray exec ==="
  .venv/bin/cosmic-ray exec "$CONF" "$SESSION"
  echo
  echo "=== cosmic-ray dump ==="
  .venv/bin/cr-rate "$SESSION"
  echo
  echo "=== Per-operator counts ==="
  .venv/bin/cr-report "$SESSION" --show-output > /dev/null
  .venv/bin/cr-report "$SESSION" 2>&1 | head -200
} 2>&1 | tee "$LOG"

# 4. Build a JSON summary suitable for paper §3.2.6.2
.venv/bin/python - <<'PY'
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent if "__file__" in dir() else Path.cwd()
LOG = Path("data/results/cosmic_ray_a1_console.log").read_text()

# cr-rate prints e.g. "Survival rate: 42.86%"
m = re.search(r"Survival rate:\s*([0-9.]+)%", LOG)
survival = float(m.group(1)) / 100 if m else None

# Total / killed / survived / incompetent: cr-rate prints them in stderr-ish form
# Be lenient: parse what's available.
def grab(pat):
    m = re.search(pat, LOG)
    return int(m.group(1)) if m else None

total = grab(r"total\s+jobs:\s*(\d+)") or grab(r"(\d+)\s+total")
killed = grab(r"killed:\s*(\d+)") or grab(r"(\d+)\s+killed")
survived = grab(r"surviv\w*:\s*(\d+)") or grab(r"(\d+)\s+survived")
incompetent = grab(r"incompetent:\s*(\d+)")

summary = {
    "tool": "cosmic-ray",
    "target_put": "src/p2/puts/a1.py",
    "test_suite": "tests/puts/test_a1.py + tests/puts/test_a1_scalar_interface.py",
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

Path("data/results/cosmic_ray_a1_summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False))
print(json.dumps(summary, indent=2, ensure_ascii=False))
PY

echo
echo "Summary saved -> data/results/cosmic_ray_a1_summary.json"
echo "Full log     -> data/results/cosmic_ray_a1_console.log"
