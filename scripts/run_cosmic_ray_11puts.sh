#!/usr/bin/env bash
# Batch driver for cosmic-ray on 11 PUTs (a1 already done).
# Logs each PUT's progress; continues on failure.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data/results
BATCH_LOG="data/results/cosmic_ray_11puts_batch.log"
echo "=== cosmic-ray 11-PUT batch started: $(date) ===" > "$BATCH_LOG"
PUTS=(a2 a3 b1 b2 b3 c1 c2 c3 d1 d2 d3)
for put in "${PUTS[@]}"; do
  echo "=== [$put] start: $(date) ===" | tee -a "$BATCH_LOG"
  if bash scripts/run_cosmic_ray_put.sh "$put" >> "$BATCH_LOG" 2>&1; then
    echo "=== [$put] DONE: $(date) ===" | tee -a "$BATCH_LOG"
  else
    echo "=== [$put] FAILED (exit $?): $(date) ===" | tee -a "$BATCH_LOG"
  fi
done
echo "=== cosmic-ray 11-PUT batch finished: $(date) ===" | tee -a "$BATCH_LOG"
