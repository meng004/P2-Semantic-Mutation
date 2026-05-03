"""Layer 3 operator campaign — K=10 default, +10 for key operators.

Per operator:
  1. Run K=10 trials concurrently via operator_runner.run_operator_K_times
  2. If op.is_key, run +10 more trials with start_idx=10 (total 20)
  3. Save raw trial JSON to data/operator_campaign/raw/{op_id}.json
  4. Save accepted code per attempt to data/operator_campaign/cache/

Operators run in parallel too (also gated by the same client Semaphore).
"""
import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from p2.mutators.operator_registry import OPERATORS, MutationOperator
from p2.mutators.async_llm import AsyncSemaphoreClient
from p2.mutators.claude_cli import ClaudeCLIClient
from p2.mutators.operator_runner import run_operator_K_times

PUTS_DIR = ROOT / "src" / "p2" / "puts"
RAW_DIR = ROOT / "data" / "operator_campaign" / "raw"
CACHE_DIR = ROOT / "data" / "operator_campaign" / "cache"
LOG_PATH = ROOT / "data" / "operator_campaign" / "campaign_log.json"

DOMAINS: dict[str, str] = {
    "a1": "Lorenz ODE system solved with RK45",
    "a2": "LU decomposition of a 2×2 parameterised matrix",
    "a3": "Explicit Euler finite-difference heat equation (1D)",
    "b1": "Beta-Binomial conjugate Bayesian update",
    "b2": "Metropolis-Hastings MCMC targeting a Gaussian",
    "b3": "Monte Carlo integration of ∫₀¹(x+t²)dt",
    "c1": "Gaussian Process Regression surrogate for erf(t)",
    "c2": "Polynomial Chaos Expansion surrogate for tanh(t)",
    "c3": "MLP neural network surrogate for sigmoid(2t)",
    "d1": "Linear SVM binary classifier",
    "d2": "RBF SVM binary classifier",
    "d3": "Decision Tree binary classifier",
}


def read_semaphore_recommendation() -> int:
    path = ROOT / "data" / "results" / "concurrency_probe.txt"
    if not path.exists():
        return 20
    text = path.read_text()
    m = re.search(r"RECOMMENDED_SEMAPHORE_LIMIT=(\d+)", text)
    return int(m.group(1)) if m else 20


def load_put_source(put_id: str) -> str:
    return (PUTS_DIR / f"{put_id}.py").read_text()


async def run_one_operator(
    op: MutationOperator, K: int, gen_client,
    rev_client: AsyncSemaphoreClient, temperature: float,
    generator_model: str,
) -> dict:
    put_source = load_put_source(op.put)
    domain = DOMAINS[op.put]

    results = await run_operator_K_times(
        op=op, K=K, put_source=put_source, put_name=op.put.upper(),
        scientific_domain=domain,
        generator_client=gen_client, reviewer_client=rev_client,
        temperature=temperature, start_idx=0,
        generator_model=generator_model,
    )

    if op.is_key:
        extra = await run_operator_K_times(
            op=op, K=K, put_source=put_source, put_name=op.put.upper(),
            scientific_domain=domain,
            generator_client=gen_client, reviewer_client=rev_client,
            temperature=temperature, start_idx=K,
            generator_model=generator_model,
        )
        results = results + extra

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{op.id}.json").write_text(
        json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)
    )
    accepted = 0
    for r in results:
        if r.is_confirmed:
            (CACHE_DIR / f"{op.id}_attempt{r.attempt_idx:02d}.py").write_text(r.code)
            accepted += 1

    return {
        "op_id": op.id, "put": op.put, "category": op.category,
        "K": len(results), "confirmed": accepted,
        "is_key": op.is_key,
    }


async def main_async(args):
    sem_n = args.concurrency or read_semaphore_recommendation()
    print(f"== reviewer concurrency limit: {sem_n} ==")
    print(f"== generator backend: {args.generator} ==")

    if args.generator == "claude-cli":
        gen_client = ClaudeCLIClient(concurrency=args.cli_concurrency)
        print(f"== generator (Opus subscription via claude CLI): "
              f"concurrency={args.cli_concurrency}, model={args.generator_model} ==")
    else:
        gen_client = AsyncSemaphoreClient(
            api_key=os.environ["BLTCY_API_KEY"],
            base_url=os.environ["BLTCY_BASE_URL"],
            concurrency=sem_n,
        )
        print(f"== generator (OpenAI-compatible proxy): {args.generator_model} ==")

    rev_client = AsyncSemaphoreClient(
        api_key=os.environ["BLTCY_API_KEY"],
        base_url=os.environ["BLTCY_BASE_URL"],
        concurrency=sem_n,
    )

    if args.op_id:
        ops = [op for op in OPERATORS if op.id == args.op_id]
    elif args.put:
        ops = [op for op in OPERATORS if op.put == args.put]
    else:
        ops = list(OPERATORS)

    print(f"== operators in campaign: {len(ops)} ==")
    t0 = time.time()
    coros = [
        run_one_operator(op, K=args.k, gen_client=gen_client,
                         rev_client=rev_client, temperature=args.temperature,
                         generator_model=args.generator_model)
        for op in ops
    ]
    summaries = await asyncio.gather(*coros)
    dt = time.time() - t0

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps({
        "elapsed_s": round(dt, 1),
        "concurrency": sem_n,
        "K_default": args.k,
        "temperature": args.temperature,
        "summaries": list(summaries),
    }, indent=2, ensure_ascii=False))

    print(f"\n== campaign log → {LOG_PATH} ==")
    print(f"{'op_id':<10} {'put':<4} {'cat':<3} {'K':>3} {'conf':>5}  key")
    print("-" * 40)
    for s in summaries:
        print(f"{s['op_id']:<10} {s['put']:<4} {s['category']:<3} "
              f"{s['K']:>3} {s['confirmed']:>5}  {'★' if s['is_key'] else ''}")
    print(f"\ntotal elapsed: {dt:.1f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=10, help="K trials per operator")
    parser.add_argument("--concurrency", type=int, default=0,
                        help="override Semaphore limit for reviewer (default: read probe)")
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--op-id", help="run a single operator (debug)")
    parser.add_argument("--put", help="run all operators for one PUT")
    parser.add_argument("--generator", choices=["claude-cli", "proxy"],
                        default="claude-cli",
                        help="generator backend: claude-cli (subscription) or proxy (OpenAI-compatible endpoint set via BLTCY_BASE_URL)")
    parser.add_argument("--cli-concurrency", type=int, default=12,
                        help="max concurrent claude CLI subprocesses (default 12)")
    parser.add_argument("--generator-model", default="opus",
                        help="generator model alias (default 'opus' for claude-cli)")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
