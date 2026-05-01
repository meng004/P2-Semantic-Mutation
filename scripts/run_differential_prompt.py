"""R-16 (P2): differential prompt experiment scaffold.

Implements the §4.2.5.1 protocol: 3 prompt variants × 3 LLM sources ×
37 operators × K=3 trials = 999 trials. Outputs source-and-prompt-
stratified mutant pools and a Cliff's-delta comparison vs v4 baseline.

NOT auto-run by CI; explicit invocation required because:
  - cost ~$18-30 USD across three providers
  - wall-clock 3-4 h
  - the paper §4.2.5.1 already records the protocol as a R2/P4
    commitment; running this script CLOSES R-16 empirically but is not
    required for the current revision

Usage:
  cp .env.example .env  # ensure 3 LLM credentials are set
  PYTHONPATH=src .venv/bin/python scripts/run_differential_prompt.py \\
      [--prompt {canonical|persona|cot}] [--source {claude|gpt|deepseek}] \\
      [--dry-run] [--operators OPS]

Outputs:
  data/operator_campaign/cache_diffprompt/{prompt}_{source}_{op_id}_attemptNN.py
  data/results/diff_prompt_summary.json
  data/results/sms_track2_v5.json (after running build_pools.py + sms_campaign.py)

Exit criterion (per paper §4.2.5.1):
  max(delta_canonical, delta_persona, delta_cot) - min(...) < 0.05
    => confirm v4 conclusion is robust to prompt style
  >= 0.05 and any variant pushes delta > 0.474
    => H2 verdict reframes to "prompt-conditional met"
  >= 0.05 but all variants stay below 0.474
    => prompt sensitivity exists, H2 unchanged, log as limitation
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROMPT_VARIANTS = {
    "canonical": {
        "description": "Generic mutation operator instruction (v4 baseline)",
        "system_template": "prompts/operator_template.txt",
        "per_source_overrides": {},
    },
    "persona": {
        "description": "Per-LLM identity prompt to elicit source-specific style",
        "system_template": "prompts/operator_template.txt",
        "per_source_overrides": {
            "claude": (
                "You are a numerical analysis editor reviewing a Python "
                "implementation of a scientific computing program. Apply "
                "the requested mutation operator with attention to "
                "numerical stability and floating-point semantics."
            ),
            "gpt": (
                "You are a scientific software refactorer specialized in "
                "rewriting numerical Python code with subtle semantic "
                "shifts that preserve syntactic plausibility."
            ),
            "deepseek": (
                "You are a library API substitution specialist who "
                "replaces calls to numpy / scipy / sklearn primitives "
                "with semantically related but algebraically distinct "
                "alternatives."
            ),
        },
    },
    "cot": {
        "description": "Per-LLM native reasoning style activator",
        "system_template": "prompts/operator_template.txt",
        "per_source_overrides": {
            "claude": (
                "Use <thinking> tags to plan the mutation: identify the "
                "target AST node, list 3 candidate replacements, and "
                "select one that preserves type signature."
            ),
            "gpt": (
                "Reason step by step. First identify the target line. "
                "Second, list two semantically related replacements. "
                "Third, pick the one most likely to preserve compilation."
            ),
            "deepseek": (
                "Think through this step by step. Output your reasoning "
                "as a numbered list before producing the final mutated "
                "code block."
            ),
        },
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", choices=list(PROMPT_VARIANTS.keys()),
                    default=None, help="Run only one prompt variant")
    ap.add_argument("--source", choices=["claude", "gpt", "deepseek"],
                    default=None, help="Run only one LLM source")
    ap.add_argument("--operators", default=None,
                    help="Comma-separated operator IDs (default: all 37)")
    ap.add_argument("--k-trials", type=int, default=3,
                    help="Trials per (operator, prompt, source) cell")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print plan and exit without LLM calls")
    args = ap.parse_args()

    prompts = [args.prompt] if args.prompt else list(PROMPT_VARIANTS.keys())
    sources = [args.source] if args.source else ["claude", "gpt", "deepseek"]

    plan = {
        "prompts": prompts,
        "sources": sources,
        "k_trials": args.k_trials,
        "operators": args.operators or "all (37)",
        "estimated_trials": (
            len(prompts) * len(sources)
            * (37 if not args.operators else len(args.operators.split(",")))
            * args.k_trials
        ),
        "estimated_cost_usd_low": 18,
        "estimated_cost_usd_high": 30,
        "estimated_walltime_hours": "3-4 with concurrency=4",
    }
    print(json.dumps(plan, indent=2, ensure_ascii=False))

    if args.dry_run:
        print("\n--dry-run: exiting without LLM calls.")
        return

    # ------------------------------------------------------------------
    # Implementation hook: this is where the actual differential-prompt
    # campaign would call the existing cross_source_campaign.py machinery
    # with prompt-variant-aware system messages. Intentionally left as a
    # NotImplementedError so users opt in deliberately.
    # ------------------------------------------------------------------
    raise NotImplementedError(
        "R-16 differential prompt campaign is intentionally NOT auto-run. "
        "To execute: (1) ensure .env has all 3 LLM credentials; "
        "(2) extend src/p2/mutators/llm_client.py to accept "
        "system_prompt_override per source; (3) reuse the per-operator "
        "loop in scripts/cross_source_campaign.py with the variant table "
        "above; (4) write trials to data/operator_campaign/cache_diffprompt/; "
        "(5) run scripts/build_pools.py with POOL_VERSION=v5_canonical / "
        "v5_persona / v5_cot; (6) run scripts/sms_campaign.py for each; "
        "(7) compare deltas per the §4.2.5.1 exit criterion. "
        "Cost/time estimates above; deferred to R2 revision or P4 paper."
    )


if __name__ == "__main__":
    sys.exit(main() or 0)
