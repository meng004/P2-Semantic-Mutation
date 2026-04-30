"""One-shot benchmark of bltcy.ai concurrency / RPM cap.

Runs N parallel chat completions with trivial prompt, increasing concurrency
each round, and reports first round where errors appear (rate-limit / 429).
"""
import asyncio
import os
import time
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from openai import AsyncOpenAI

CONCURRENCY_LEVELS = [5, 10, 20, 30, 50]
REQUESTS_PER_LEVEL = 30


async def one_call(client: AsyncOpenAI, model: str, idx: int) -> tuple[int, bool, str]:
    try:
        await client.chat.completions.create(
            model=model, max_tokens=4, temperature=0,
            messages=[{"role": "user", "content": f"reply with the single word OK ({idx})"}],
        )
        return idx, True, ""
    except Exception as e:
        return idx, False, type(e).__name__ + ": " + str(e)[:80]


async def run_level(concurrency: int, n: int):
    client = AsyncOpenAI(
        base_url=os.environ["BLTCY_BASE_URL"],
        api_key=os.environ["BLTCY_API_KEY"],
    )
    sem = asyncio.Semaphore(concurrency)

    async def gated(i):
        async with sem:
            return await one_call(client, "gpt-5.4", i)

    t0 = time.time()
    results = await asyncio.gather(*[gated(i) for i in range(n)])
    dt = time.time() - t0
    ok = sum(1 for _, s, _ in results if s)
    fails = [(i, e) for i, s, e in results if not s]
    return {"concurrency": concurrency, "n": n, "ok": ok, "fail": len(fails),
            "elapsed_s": round(dt, 1), "rps": round(n / dt, 2),
            "first_failure": fails[0] if fails else None}


async def main():
    print(f"{'conc':>5} {'n':>4} {'ok':>4} {'fail':>5} {'time':>7} {'rps':>5}  first-fail")
    recommended = 10  # safe default if all levels pass
    for c in CONCURRENCY_LEVELS:
        r = await run_level(c, REQUESTS_PER_LEVEL)
        print(f"{r['concurrency']:>5} {r['n']:>4} {r['ok']:>4} {r['fail']:>5} "
              f"{r['elapsed_s']:>6}s {r['rps']:>5}  {r['first_failure']}")
        if r["fail"] > 0:
            # recommend the last level that had 0 failures
            idx = CONCURRENCY_LEVELS.index(c)
            recommended = CONCURRENCY_LEVELS[idx - 1] if idx > 0 else 5
            print(f"  >>> stopping: first failure at concurrency={c}")
            return recommended
    print("  >>> all levels OK, recommend concurrency = 30")
    return 30


if __name__ == "__main__":
    rec = asyncio.run(main())
    print(f"\nRecommended Semaphore limit: {rec}")
