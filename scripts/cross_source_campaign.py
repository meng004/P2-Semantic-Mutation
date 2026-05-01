"""Phase A MVP: cross-source mutant campaign.

Round-robin three LLMs (Claude Opus 4.6, GPT-5.4, DeepSeek chat) over the
37-operator registry. Each operator: K=3 trials per source, V1-V4 mechanical
validation only (no reviewer LLM, MVP simplification).

Output:
  data/operator_campaign/cache_cross/{op_id}_{source}_attempt{NN}.py
  data/operator_campaign/cache_cross/_log.json   (per-trial metadata)

Usage:
    PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py
    PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py --put a2  # one PUT
    PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py --dryrun  # 1 PUT, K=2
"""
import argparse
import asyncio
import importlib.util
import json
import re
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from p2.mutators.llm_client import (  # type: ignore[import-not-found]  # noqa: E402
    generator_claude, generator_gpt, generator_deepseek,
)
from p2.mutators.operator_registry import OPERATORS  # type: ignore[import-not-found]  # noqa: E402
from p2.mutators.validation import validate_mutant  # type: ignore[import-not-found]  # noqa: E402

CACHE_DIR = ROOT / "data/operator_campaign/cache_cross"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

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


def _load_put_program(put_id: str) -> tuple[str, callable]:  # type: ignore[type-arg]
    src_path = ROOT / f"src/p2/puts/{put_id}.py"
    code = src_path.read_text()
    spec = importlib.util.spec_from_file_location(f"_put_{put_id}", src_path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return code, mod.program


def _strip_fences(text: str) -> str:
    m = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _generate_one(client: OpenAI, model: str, prompt: str, max_tokens: int = 800) -> tuple[str, dict]:
    """Single chat completion with timing + token usage."""
    t0 = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    dt = time.time() - t0
    msg = resp.choices[0].message
    content = msg.content or ""
    usage = resp.usage
    return _strip_fences(content), {
        "latency_s": round(dt, 2),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
    }


def _run_one_op_one_source(op, original_code, original_fn, source_tag, factory, k_trials):
    """Synchronous helper: run K trials for one (operator, source)."""
    client, model = factory()
    results = []
    for attempt in range(1, k_trials + 1):
        prompt = PROMPT_TEMPLATE.format(
            put_name=op.put.upper(),
            op_id=op.id,
            op_label=op.label,
            target_locator=op.target_locator,
            transformation=op.transformation,
            rationale=op.rationale,
            attempt_idx=attempt,
            n_attempts=k_trials,
            original_code=original_code,
        )
        try:
            code, meta = _generate_one(client, model, prompt)
        except Exception as e:
            results.append({
                "op": op.id, "source": source_tag, "attempt": attempt,
                "v_passed": False, "error": f"LLM_FAIL: {type(e).__name__}: {e}",
            })
            continue

        v = validate_mutant(code, original_fn)
        record = {
            "op": op.id,
            "put": op.put,
            "source": source_tag,
            "model": model,
            "attempt": attempt,
            "v_syntax": v.syntax_ok,
            "v_executable": v.executable,
            "v_nontrivial": v.nontrivial,
            "v_passed": v.passed,
            "v_error": v.error,
            "latency_s": meta["latency_s"],
            "prompt_tokens": meta["prompt_tokens"],
            "completion_tokens": meta["completion_tokens"],
        }
        if v.passed:
            fname = f"{op.id}_{source_tag}_attempt{attempt:02d}.py"
            (CACHE_DIR / fname).write_text(code)
            record["filename"] = fname
        results.append(record)
        print(f"  [{op.id} {source_tag} a{attempt:02d}] "
              f"{'PASS' if v.passed else 'FAIL'} {meta['latency_s']}s "
              f"{meta['completion_tokens']}t",
              flush=True)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--put", default=None, help="restrict to one PUT (e.g. a2)")
    parser.add_argument("--ops", default=None,
                        help="comma-separated op_id list (e.g. a3_SI1,c1_HP1)")
    parser.add_argument("--resume", action="store_true",
                        help="skip ops with full 3-source coverage")
    parser.add_argument("--dryrun", action="store_true",
                        help="1 PUT, K=2 trials/source")
    parser.add_argument("--k", type=int, default=3, help="trials per (op, source)")
    parser.add_argument("--workers", type=int, default=3,
                        help="parallel sources (Claude+GPT+DeepSeek = 3)")
    args = parser.parse_args()

    if args.dryrun:
        ops = [op for op in OPERATORS if op.put == "a2"][:1]
        k = 2
    elif args.ops:
        wanted = set(args.ops.split(","))
        ops = [op for op in OPERATORS if op.id in wanted]
        k = args.k
    elif args.put:
        ops = [op for op in OPERATORS if op.put == args.put]
        k = args.k
    else:
        ops = list(OPERATORS)
        k = args.k

    if args.resume:
        from collections import defaultdict
        import re as _re
        op_sources: dict[str, set] = defaultdict(set)
        for f in CACHE_DIR.glob("*.py"):
            m = _re.match(r"([a-d]\d_[A-Z]+\d)_(claude|gpt|deepseek)_", f.name)
            if m:
                op_sources[m.group(1)].add(m.group(2))
        ops = [op for op in ops if len(op_sources.get(op.id, set())) < 3]
        print(f"--resume: {len(ops)} ops with < 3 sources")

    print(f"Phase A MVP: {len(ops)} operators × 3 sources × K={k} trials = "
          f"{len(ops)*3*k} total LLM calls")

    sources = [
        ("claude", generator_claude),
        ("gpt", generator_gpt),
        ("deepseek", generator_deepseek),
    ]

    all_records = []
    t_start = time.time()

    # Cache PUT programs to avoid re-import
    put_cache: dict[str, tuple[str, callable]] = {}  # type: ignore[type-arg]

    for op in ops:
        if op.put not in put_cache:
            put_cache[op.put] = _load_put_program(op.put)
        original_code, original_fn = put_cache[op.put]
        print(f"\n--- {op.id} ({op.label}) ---")

        # 3 sources in parallel via ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [
                pool.submit(_run_one_op_one_source, op, original_code, original_fn,
                            tag, fac, k)
                for tag, fac in sources
            ]
            for fut in futures:
                all_records.extend(fut.result())

    dt_total = time.time() - t_start
    log_path = CACHE_DIR / "_log.json"
    log_path.write_text(json.dumps({
        "trials": all_records,
        "wall_time_s": round(dt_total, 1),
        "n_operators": len(ops),
        "k_per_source": k,
        "sources": [s[0] for s in sources],
    }, indent=2, ensure_ascii=False))

    confirmed = [r for r in all_records if r.get("v_passed")]
    by_source: dict[str, int] = {}
    for r in confirmed:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
    print(f"\n=== SUMMARY ===")
    print(f"  total trials:    {len(all_records)}")
    print(f"  confirmed (V1-V4 pass): {len(confirmed)} ({100*len(confirmed)/len(all_records):.0f}%)")
    print(f"  per-source confirmed: {by_source}")
    print(f"  wall time:       {dt_total:.0f}s")
    print(f"  log:             {log_path}")


if __name__ == "__main__":
    main()
