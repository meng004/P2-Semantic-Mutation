# P2 Experiments

Experimental infrastructure for P2 paper: Domain-Semantic Mutation Operators and Semantic Mutation Score.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Project Structure

- `src/p2/avp/` — Automated Verification Pipeline (P1 reuse)
- `src/p2/mutators/` — Dual-LLM mutator pipeline
- `src/p2/equiv/` — Equiv judge (E1 ∧ E2)
- `src/p2/lrca/` — Likely Root Cause Analysis
- `src/p2/stats/` — Statistical analysis (SMS, RQ1-4)
- `src/p2/pipeline/` — End-to-end orchestration
- `tests/` — Test suite
- `data/` — Experiment data
- `configs/` — Hydra configuration
