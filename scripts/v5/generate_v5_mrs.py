#!/usr/bin/env python3
"""Held-out MR source generation for EXP-DIS (Task 2.2).

BLOCKED without a held-out provider API key. Writes the 7-item symmetry
checklist template to data/v5/MR_SOURCE_SYMMETRY.md (v4-side values prefilled;
provider column blank pending key availability).

Provider candidates ranked by symmetry-satisfiability (must be NONE of
Claude / GPT / DeepSeek used in v4):
  1. Gemini (Google) — OpenAI-compatible proxies common; prompt-verbatim +
     temperature + candidate-count easy to match; wide availability.
  2. Qwen (Alibaba / DashScope or OpenAI-compat proxy) — same chat API shape;
     good Chinese/English code; temperature control reliable.
  3. Mistral (La Plateforme / OpenAI-compat) — chat completions parity;
     slightly less ubiquitous proxy coverage.
  4. Llama-hosted (Together / Fireworks / Groq OpenAI-compat) — last resort;
     model-card temperature semantics can drift vs v4 proprietary models.

Required env (fail-fast):
  V5_MR_API_KEY, V5_MR_BASE_URL, V5_MR_MODEL
  (intentionally distinct from BLTCY_* generator keys so the held-out
   provider cannot silently collapse to a v4 source)

Usage:
  PYTHONPATH=src python scripts/v5/generate_v5_mrs.py --dry-check
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_MD = ROOT / "data" / "v5" / "MR_SOURCE_SYMMETRY.md"
BASE_SEED = 20260728

# v4 values (from scripts/cross_source_campaign.py)
V4_SOURCES = ("claude", "gpt", "deepseek")
V4_TEMPERATURE = 0.7
V4_K_TRIALS_DEFAULT = 3
V4_PROMPT_SHA256 = "06fa552d7431cecc00120bddeb4e8cdc4511ce03f695139809b5af83508a3e90"
V4_PARSER = "cross_source_campaign._strip_fences (```python fence extractor)"

REQUIRED_ENV = ("V5_MR_API_KEY", "V5_MR_BASE_URL", "V5_MR_MODEL")

PROVIDER_RANKING = [
    {
        "rank": 1,
        "name": "Gemini",
        "notes": (
            "OpenAI-compatible proxy widely available; matches prompt-verbatim, "
            "temperature=0.7, candidate-count, budget constraints; not used in v4."
        ),
    },
    {
        "rank": 2,
        "name": "Qwen",
        "notes": (
            "DashScope or OpenAI-compat; temperature + max_tokens parity; "
            "strong code generation; not used in v4."
        ),
    },
    {
        "rank": 3,
        "name": "Mistral",
        "notes": (
            "La Plateforme / OpenAI-compat; chat completions parity; "
            "slightly thinner proxy ecosystem than Gemini/Qwen."
        ),
    },
    {
        "rank": 4,
        "name": "Llama-hosted",
        "notes": (
            "Together/Fireworks/Groq OpenAI-compat; last resort — temperature "
            "semantics can drift vs proprietary v4 sources."
        ),
    },
]


def write_symmetry_md(provider: str | None = None) -> None:
    lines = [
        "# MR_SOURCE_SYMMETRY — EXP-DIS held-out provider checklist",
        "",
        f"Seed: `{BASE_SEED}`. v4 sources (FORBIDDEN for held-out): {', '.join(V4_SOURCES)}.",
        "",
        "## Provider candidate ranking (by symmetry-satisfiability)",
        "",
        "| Rank | Provider | Notes |",
        "|---|---|---|",
    ]
    for p in PROVIDER_RANKING:
        lines.append(f"| {p['rank']} | {p['name']} | {p['notes']} |")
    lines += [
        "",
        "## 7-item symmetry checklist",
        "",
        "| # | Item | v4 value | v5 held-out value | Status |",
        "|---|---|---|---|---|",
        f"| 1 | Prompt text | SHA-256 `{V4_PROMPT_SHA256}` (cross_source_campaign.PROMPT_TEMPLATE) | "
        f"{'SAME (pending run)' if not provider else 'SAME'} | ⬜ pending key |",
        f"| 2 | Parser version | `{V4_PARSER}` | same function | ⬜ pending key |",
        f"| 3 | Temperature | `{V4_TEMPERATURE}` | `{V4_TEMPERATURE}` | ⬜ pending key |",
        f"| 4 | Candidate count / K trials | default K=`{V4_K_TRIALS_DEFAULT}` per (op, source) | same K | ⬜ pending key |",
        f"| 5 | Repair / retry budget | v4: no auto-repair beyond K attempts | same | ⬜ pending key |",
        f"| 6 | Max tokens | `800` (cross_source_campaign._generate_one) | `800` | ⬜ pending key |",
        f"| 7 | Provider identity | Claude / GPT / DeepSeek | "
        f"{provider or '**(blank — select from ranking when key arrives)**'} | ⬜ pending key |",
        "",
        "## Required env vars",
        "",
        "```",
        "V5_MR_API_KEY=<held-out provider key>",
        "V5_MR_BASE_URL=<OpenAI-compatible base URL>",
        "V5_MR_MODEL=<model id>",
        "```",
        "",
        f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        "",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines))
    print(f"Wrote {OUT_MD}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-check", action="store_true")
    args = ap.parse_args()
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    write_symmetry_md(provider=None)
    if missing or args.dry_check:
        print("BLOCKED: held-out MR generation requires:")
        for k in REQUIRED_ENV:
            status = "OK" if os.environ.get(k) else "MISSING"
            print(f"  - {k}: {status}")
        print("Provider ranking: Gemini > Qwen > Mistral > Llama-hosted")
        print("No LLM outputs fabricated.")
        sys.exit(2 if missing else 0)
    print("Env OK — MR generation body not yet wired to a live provider in PASS-1;")
    print("symmetry checklist is the PASS-1 deliverable. Re-run after provider selection.")


if __name__ == "__main__":
    main()
