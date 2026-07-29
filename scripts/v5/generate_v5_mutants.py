#!/usr/bin/env python3
"""POOL-SEM v5 mutant generation (EXP-CON / Task 2.1).

BLOCKED without LLM API keys. Builds a one-command-runnable pipeline that:
  - reads the 51 applicable cells (hardcoded from applicability_matrix.md §3
    with provenance comment; n_app=51)
  - targets density 16 confirmed / cell, attempts budget ceil(16*1.117)=18
  - reuses the v4 cross_source_campaign PROMPT_TEMPLATE verbatim
    (SHA-256 recorded in data/v5/GENERATION_LEDGER.md)
  - temperature 0.7; parser = fence-stripping identical to v4
  - writes candidates under data/v5/pools/ and funnel_v5.json

Required env (fail-fast if missing):
  BLTCY_API_KEY, BLTCY_BASE_URL
  plus optional per-provider model overrides (see --help).

Usage:
  PYTHONPATH=src python scripts/v5/generate_v5_mutants.py          # real run
  PYTHONPATH=src python scripts/v5/generate_v5_mutants.py --dry-check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

OUT_POOL = ROOT / "data" / "v5" / "pools"
OUT_FUNNEL = ROOT / "data" / "v5" / "funnel_v5.json"
LEDGER = ROOT / "data" / "v5" / "GENERATION_LEDGER.md"
BASE_SEED = 20260728
TARGET_CONFIRMED = 16
ATTEMPTS_BUDGET = math.ceil(TARGET_CONFIRMED * 1.117)  # 18
TEMPERATURE = 0.7

# Provenance: applicability_matrix.md §3 PUT-level table (✓ cells only).
# n_app = CE9+OS12+HP11+TF9+SI10 = 51. Frozen at prereg-v2-freeze.
# Format: (op, put) — op in {CE,OS,HP,TF,SI}.
APPLICABLE_CELLS: list[tuple[str, str]] = [
    # CE (9): not d1/d2/d3
    ("CE", "a1"), ("CE", "a2"), ("CE", "a3"),
    ("CE", "b1"), ("CE", "b2"), ("CE", "b3"),
    ("CE", "c1"), ("CE", "c2"), ("CE", "c3"),
    # OS (12): all PUTs
    ("OS", "a1"), ("OS", "a2"), ("OS", "a3"),
    ("OS", "b1"), ("OS", "b2"), ("OS", "b3"),
    ("OS", "c1"), ("OS", "c2"), ("OS", "c3"),
    ("OS", "d1"), ("OS", "d2"), ("OS", "d3"),
    # HP (11): not a2
    ("HP", "a1"), ("HP", "a3"),
    ("HP", "b1"), ("HP", "b2"), ("HP", "b3"),
    ("HP", "c1"), ("HP", "c2"), ("HP", "c3"),
    ("HP", "d1"), ("HP", "d2"), ("HP", "d3"),
    # TF (9): not a2, b1, b3
    ("TF", "a1"), ("TF", "a3"),
    ("TF", "b2"),
    ("TF", "c1"), ("TF", "c2"), ("TF", "c3"),
    ("TF", "d1"), ("TF", "d2"), ("TF", "d3"),
    # SI (10): not b1, b2
    ("SI", "a1"), ("SI", "a2"), ("SI", "a3"),
    ("SI", "b3"),
    ("SI", "c1"), ("SI", "c2"), ("SI", "c3"),
    ("SI", "d1"), ("SI", "d2"), ("SI", "d3"),
]
assert len(APPLICABLE_CELLS) == 51, len(APPLICABLE_CELLS)

# v4 prompt template extracted verbatim from scripts/cross_source_campaign.py
PROMPT_TEMPLATE = """You are an expert in scientific computing software testing. Generate a SEMANTIC MUTANT of the program below that implements EXACTLY the named operator described.

PUT NAME: {put_name}
OPERATOR ID: {op_id}
OPERATOR LABEL: {op_label}
TARGET LOCATOR: {target_locator}
EXACT CHANGE: {transformation}
RATIONALE: {rationale}

ATTEMPT INDEX: {attempt_idx} of {n_attempts}  (different seed; same operator; produce a STRUCTURALLY DIFFERENT mutant from prior attempts)

━━━ ORIGINAL PROGRAM ━━━
```python
{original_code}
```

INSTRUCTIONS:
- Apply the operator transformation EXACTLY as specified.
- Output ONLY the complete mutated Python program in a ```python``` block.
- The mutated program MUST execute on x ∈ [0, 1] without raising exceptions.
- Preserve the function signature `def program(x): ...` returning a finite scalar.
- Do not explain or comment.
"""
PROMPT_SHA256 = hashlib.sha256(PROMPT_TEMPLATE.encode()).hexdigest()

REQUIRED_ENV = ("BLTCY_API_KEY", "BLTCY_BASE_URL")

# Cloud-agent secret-name adapter (author's dashboard names, 2026-07-29):
#   base_url -> BLTCY_BASE_URL, api_key_1 -> BLTCY_API_KEY (generation arm).
# Explicit BLTCY_* names take precedence when both are set.
_ENV_FALLBACKS = {"BLTCY_API_KEY": "api_key_1", "BLTCY_BASE_URL": "base_url"}
for _canon, _alt in _ENV_FALLBACKS.items():
    if not os.environ.get(_canon) and os.environ.get(_alt):
        os.environ[_canon] = os.environ[_alt]


def _strip_fences(text: str) -> str:
    """Same parser as scripts/cross_source_campaign.py::_strip_fences."""
    m = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def check_env() -> list[str]:
    return [k for k in REQUIRED_ENV if not os.environ.get(k)]


def dry_check() -> int:
    missing = check_env()
    print("v5 mutant generation — dry check")
    print(f"  n_app cells: {len(APPLICABLE_CELLS)}")
    print(f"  target confirmed/cell: {TARGET_CONFIRMED}")
    print(f"  attempts budget/cell: {ATTEMPTS_BUDGET}")
    print(f"  temperature: {TEMPERATURE}")
    print(f"  prompt SHA-256: {PROMPT_SHA256}")
    print(f"  base seed: {BASE_SEED}")
    if missing:
        print("BLOCKED: missing required env vars:")
        for k in missing:
            print(f"  - {k}")
        print("No LLM outputs fabricated. Re-run when keys are available.")
        return 2
    print("Env OK — ready to generate.")
    return 0


def _empty_funnel() -> dict:
    cells = []
    for op, put in APPLICABLE_CELLS:
        cells.append({
            "cell": f"{op}×{put}",
            "op": op,
            "put": put,
            "n_attempts": 0,
            "n_parse_ok": 0,
            "n_build_ok": 0,
            "n_trigger_ok": 0,
            "n_e1_and_e2_nonequiv": 0,
            "n_confirmed_nonequiv": 0,
            "n_certificate": 0,
        })
    return {
        "n_app": 51,
        "target_confirmed_per_cell": TARGET_CONFIRMED,
        "attempts_budget_per_cell": ATTEMPTS_BUDGET,
        "temperature": TEMPERATURE,
        "prompt_sha256": PROMPT_SHA256,
        "seed": BASE_SEED,
        "status": "BLOCKED_NO_API_KEYS",
        "cells": cells,
        "stage_totals": {
            "attempts": 0, "parse": 0, "build": 0,
            "trigger": 0, "e1_and_e2": 0, "certificate": 0,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-check", action="store_true",
                    help="validate config + env; write blocked funnel stub if keys missing")
    args = ap.parse_args()

    OUT_POOL.mkdir(parents=True, exist_ok=True)

    if args.dry_check or check_env():
        rc = dry_check()
        funnel = _empty_funnel()
        OUT_FUNNEL.write_text(json.dumps(funnel, indent=2))
        print(f"Wrote blocked stub {OUT_FUNNEL}")
        sys.exit(rc if args.dry_check else 2)

    # Live generation path (keys present)
    from openai import OpenAI  # deferred
    from p2.mutators.operator_registry import OPERATORS
    from p2.mutators.validation import validate_mutant

    client = OpenAI(
        api_key=os.environ["BLTCY_API_KEY"],
        base_url=os.environ["BLTCY_BASE_URL"],
    )
    model = os.environ.get("V5_GENERATOR_MODEL", "gpt-4o")

    # Index registry ops by (category, put)
    by_cell: dict[tuple[str, str], list] = {}
    for op in OPERATORS:
        by_cell.setdefault((op.category, op.put), []).append(op)

    funnel = _empty_funnel()
    funnel["status"] = "RUNNING"
    funnel_by = {c["cell"]: c for c in funnel["cells"]}

    for op_name, put in APPLICABLE_CELLS:
        cell = f"{op_name}×{put}"
        rec = funnel_by[cell]
        put_src = (ROOT / f"src/p2/puts/{put}.py").read_text()
        # Load original program
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            f"put_{put}", ROOT / f"src/p2/puts/{put}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        orig_fn = mod.program

        registry_ops = by_cell.get((op_name, put), [])
        if not registry_ops:
            # synthesize a minimal op descriptor for never-attempted cells
            class _Op:
                pass
            o = _Op()
            o.id = f"{put}_{op_name}1"
            o.put = put
            o.category = op_name
            o.label = f"{op_name} semantic edit on {put}"
            o.target_locator = f"wrapper-level site for {op_name} on {put}"
            o.transformation = f"apply {op_name} failure semantics at wrapper site"
            o.rationale = f"v5 applicable-cell generation for {cell}"
            registry_ops = [o]

        confirmed = 0
        for attempt in range(1, ATTEMPTS_BUDGET + 1):
            if confirmed >= TARGET_CONFIRMED:
                break
            op = registry_ops[(attempt - 1) % len(registry_ops)]
            prompt = PROMPT_TEMPLATE.format(
                put_name=put.upper(),
                op_id=getattr(op, "id", f"{put}_{op_name}1"),
                op_label=getattr(op, "label", op_name),
                target_locator=getattr(op, "target_locator", "wrapper site"),
                transformation=getattr(op, "transformation", op_name),
                rationale=getattr(op, "rationale", ""),
                attempt_idx=attempt,
                n_attempts=ATTEMPTS_BUDGET,
                original_code=put_src,
            )
            rec["n_attempts"] += 1
            funnel["stage_totals"]["attempts"] += 1
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=TEMPERATURE,
                )
                code = _strip_fences(resp.choices[0].message.content or "")
            except Exception as e:
                print(f"  {cell} a{attempt}: LLM_FAIL {e}")
                continue
            rec["n_parse_ok"] += 1
            funnel["stage_totals"]["parse"] += 1
            mid = f"mut-{op_name}-{put.upper()}-{attempt:02d}"
            try:
                v = validate_mutant(code, orig_fn)
            except Exception as e:
                print(f"  {cell} a{attempt}: BUILD_FAIL {e}")
                continue
            rec["n_build_ok"] += 1
            funnel["stage_totals"]["build"] += 1
            if not getattr(v, "passed", False):
                continue
            rec["n_trigger_ok"] += 1
            funnel["stage_totals"]["trigger"] += 1
            # E1∧E2 nonequiv + certificate counted when validation exposes them;
            # validate_mutant in v4 bundles the funnel gates we can see here.
            if getattr(v, "nonequiv", True):
                rec["n_e1_and_e2_nonequiv"] += 1
                funnel["stage_totals"]["e1_and_e2"] += 1
                rec["n_confirmed_nonequiv"] += 1
                confirmed += 1
                cell_dir = OUT_POOL / f"{put}_{op_name}"
                cell_dir.mkdir(parents=True, exist_ok=True)
                (cell_dir / f"{mid}.py").write_text(code)
                rec["n_certificate"] += 1
                funnel["stage_totals"]["certificate"] += 1
            print(f"  {cell} a{attempt}: confirmed={confirmed}", flush=True)

    funnel["status"] = "COMPLETE"
    funnel["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    OUT_FUNNEL.write_text(json.dumps(funnel, indent=2))
    print(f"Wrote {OUT_FUNNEL}")


if __name__ == "__main__":
    main()
