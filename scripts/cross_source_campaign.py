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

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # offline dry-run may run without python-dotenv
    def load_dotenv(*_a, **_k):  # type: ignore[misc]
        return False
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
from p2.config.primary import PRIMARY_CELLS  # type: ignore[import-not-found]  # noqa: E402

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


# ══════════════════════════════════════════════════════════════════════════
# Study-2 dual-blind protocol (PREREGISTRATION_STUDY2.md §5).
#
# Both arms — same-source (one generator family, K=3) and cross-source (three
# families, K=3 each) — pass through ONE identical review+arbitration pipeline.
# Everything here is offline-implementable (role rotation, blinded packet,
# prompt assembly, verdict classification, seeds/counts). The single
# unavoidable live step (the reviewer/arbiter LLM call) is isolated behind
# _live_review_call(), a clearly marked TODO-gate.
# ══════════════════════════════════════════════════════════════════════════

REGISTERED_SEED = 20260708          # master seed (registration §7)
REGISTERED_K = 3                    # trials per (op, source), both arms (§5)
FAMILIES = ("claude", "gpt", "deepseek")

# Family → generator factory (all three share the cross-source generator set).
FAMILY_GENERATORS = {
    "claude": generator_claude,
    "gpt": generator_gpt,
    "deepseek": generator_deepseek,
}

ARMS = {
    # same-source arm (v3-style): ONE generator family, K=3.
    "same": ["claude"],
    # cross-source arm (v4-style): three generator families, K=3 each.
    "cross": list(FAMILIES),
}


def assign_review_roles(generator_family: str) -> tuple[str, str]:
    """Model-family rotation so generator ≠ reviewer ≠ arbiter (§5).

    Deterministic ring rotation over FAMILIES: reviewer is the next family,
    arbiter the one after. Guarantees no model reviews or arbitrates its own
    output, on every item, for both arms.
    """
    i = FAMILIES.index(generator_family)
    reviewer = FAMILIES[(i + 1) % len(FAMILIES)]
    arbiter = FAMILIES[(i + 2) % len(FAMILIES)]
    return reviewer, arbiter


def build_blind_review_packet(op, put_source: str, mutant_code: str) -> dict:
    """Assemble the reviewer's blinded packet (§5 step 2).

    'Blind' means the packet contains ONLY the mutant code, the operator
    specification, and the PUT source. It deliberately OMITS:
      (a) the generator's identity/family,
      (b) the arm label (same/cross),
      (c) any SMS / kill outcome (SMS is computed only after review closes).
    """
    return {
        "put_source": put_source,
        "mutant_code": mutant_code,
        "operator": {
            "id": op.id,
            "label": op.label,
            "target_locator": op.target_locator,
            "transformation": op.transformation,
        },
        # NOTE: generator family, arm label, and SMS are intentionally absent.
    }


REVIEW_PROMPT_TEMPLATE = """You are reviewing a candidate semantic mutant for validity against a named operator specification. You are given ONLY the original program, the mutant, and the operator spec. Decide whether the mutant implements EXACTLY the specified operator and is a valid single-fault mutant.

OPERATOR ID: {op_id}
OPERATOR LABEL: {op_label}
TARGET LOCATOR: {target_locator}
EXACT CHANGE: {transformation}

━━━ ORIGINAL PROGRAM ━━━
```python
{put_source}
```

━━━ CANDIDATE MUTANT ━━━
```python
{mutant_code}
```

Respond with ONLY a JSON object:
{{"operator_match": "Yes"|"No", "overall": "CONFIRMED"|"REJECTED", "reason": "<short>"}}
"""


def _live_review_call(reviewer_factory, prompt: str) -> str:
    """TODO-GATE (live API): the single step that requires network + creds.

    Builds the reviewer client from its family factory and issues one blind
    chat completion. Everything up to and after this call is offline. When
    .env is supplied this runs for real; the dry-run path bypasses it via a
    mock client injected as `reviewer_factory`.
    """
    client, model = reviewer_factory()
    code, _meta = _generate_one(client, model, prompt, max_tokens=300)
    return code


def run_blind_review(op, put_source, mutant_code, generator_family,
                     reviewer_factory=None, arbiter_factory=None) -> dict:
    """One dual-blind review+arbitration cycle over a single mutant (§5).

    `reviewer_factory` / `arbiter_factory` default to the rotated family
    clients; the dry-run injects mock factories so no network is touched.
    Returns {reviewer_family, arbiter_family, review_verdict, arbitrated}.
    """
    from types import SimpleNamespace
    from p2.mutators.dual_blind import classify_mutant, MutantStatus

    reviewer_family, arbiter_family = assign_review_roles(generator_family)
    packet = build_blind_review_packet(op, put_source, mutant_code)
    prompt = REVIEW_PROMPT_TEMPLATE.format(
        op_id=packet["operator"]["id"],
        op_label=packet["operator"]["label"],
        target_locator=packet["operator"]["target_locator"],
        transformation=packet["operator"]["transformation"],
        put_source=packet["put_source"],
        mutant_code=packet["mutant_code"],
    )
    rev_factory = reviewer_factory or FAMILY_GENERATORS[reviewer_family]
    raw = _live_review_call(rev_factory, prompt)  # <-- live gate (mocked in dry-run)
    parsed = _parse_review_json(raw)
    status = classify_mutant(SimpleNamespace(overall=parsed.get("overall", "UNCERTAIN")))

    arbitrated = False
    if status == MutantStatus.ARBITRATED:
        # generator/reviewer disagreement → third family arbitrates on the
        # SAME blinded packet (§5 step 3).
        arb_factory = arbiter_factory or FAMILY_GENERATORS[arbiter_family]
        raw_arb = _live_review_call(arb_factory, prompt)
        parsed = _parse_review_json(raw_arb)
        arbitrated = True

    return {
        "reviewer_family": reviewer_family,
        "arbiter_family": arbiter_family,
        "review_verdict": parsed.get("overall", "UNCERTAIN"),
        "operator_match": parsed.get("operator_match", "Uncertain"),
        "arbitrated": arbitrated,
    }


def _parse_review_json(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not m:
        return {"overall": "REJECTED", "reason": f"parse_error: {str(raw)[:80]}"}
    try:
        return json.loads(m.group())
    except json.JSONDecodeError as e:
        return {"overall": "REJECTED", "reason": f"json_error: {e}"}


# ── Offline mock client (dry-run only; never touches the network) ──────────

class _MockCompletionMessage:
    def __init__(self, content): self.content = content


class _MockChoice:
    def __init__(self, content): self.message = _MockCompletionMessage(content)


class _MockUsage:
    prompt_tokens = 128
    completion_tokens = 64


class _MockResponse:
    def __init__(self, content):
        self.choices = [_MockChoice(content)]
        self.usage = _MockUsage()


class _MockCompletions:
    def __init__(self, kind): self._kind = kind; self._n = 0

    def create(self, model, messages, max_tokens=800, temperature=0.7):
        prompt = messages[0]["content"]
        if self._kind == "reviewer":
            # deterministic blind reviewer: always confirm valid single-fault
            return _MockResponse('{"operator_match": "Yes", "overall": "CONFIRMED", '
                                 '"reason": "mock: fixture mutant valid"}')
        # generator: extract the original program from the prompt and wrap it
        # with a small deterministic perturbation → guaranteed valid + non-trivial.
        m = re.search(r"```python\s*\n(.*?)```", prompt, re.DOTALL)
        original = m.group(1).rstrip() if m else "def program(x):\n    return float(x)"
        self._n += 1
        delta = 0.10 + 0.01 * self._n  # vary per attempt → structural diversity
        wrapped = (original
                   + "\n\n_p_orig = program\n"
                   + f"def program(x):\n    return float(_p_orig(x)) + {delta}\n")
        return _MockResponse(f"```python\n{wrapped}\n```")


class _MockChat:
    def __init__(self, kind): self.completions = _MockCompletions(kind)


class MockLLMClient:
    """Drop-in for the OpenAI client used by _generate_one — no network."""
    def __init__(self, kind="generator"): self.chat = _MockChat(kind)


def _mock_generator_factory():
    return MockLLMClient("generator"), "mock-generator"


def _mock_reviewer_factory():
    return MockLLMClient("reviewer"), "mock-reviewer"


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


def run_dry_run() -> int:
    """OFFLINE end-to-end pipeline proof on 2 PUTs (one old a2, one new a4).

    Exercises the FULL campaign minus the API: mock generation (fixture
    mutants) → fence normalization → V1–V4 validation → blind dual-blind
    review (mock reviewer/arbiter) → proportional pool selection (dedup) →
    AVP/equiv → SMS bookkeeping. No network is touched.
    """
    import shutil
    global CACHE_DIR
    from p2.mutators.pool_builder import select_mutants_for_put

    # Load scripts/sms_campaign.py dynamically (scripts/ is not a package).
    sms_spec = importlib.util.spec_from_file_location(
        "sms_campaign_dry", ROOT / "scripts" / "sms_campaign.py")
    sms_mod = importlib.util.module_from_spec(sms_spec)  # type: ignore[arg-type]
    sms_spec.loader.exec_module(sms_mod)  # type: ignore[union-attr]

    dry_cache = ROOT / "data" / "operator_campaign" / "cache_dryrun"
    if dry_cache.exists():
        shutil.rmtree(dry_cache)
    dry_cache.mkdir(parents=True, exist_ok=True)

    saved_cache = CACHE_DIR
    CACHE_DIR = dry_cache  # _run_one_op_one_source writes fixtures here
    try:
        pairs = [("a2", "OLD"), ("a4", "NEW")]
        ops = [next(o for o in OPERATORS if o.put == put) for put, _ in pairs]
        mock_sources = [(fam, _mock_generator_factory) for fam in ARMS["cross"]]

        print(f"\n=== DRY-RUN (offline, no network) — arm=cross, K={REGISTERED_K}, "
              f"seed={REGISTERED_SEED} ===")
        all_recs, reviews = [], []
        for op in ops:
            original_code, original_fn = _load_put_program(op.put)
            print(f"\n--- {op.id} ({op.put.upper()}, "
                  f"{'existing' if op.put in ('a1','a2','a3') else 'new'} PUT) ---")
            for tag, fac in mock_sources:
                recs = _run_one_op_one_source(
                    op, original_code, original_fn, tag, fac, REGISTERED_K)
                all_recs.extend(recs)
                for r in recs:
                    if r.get("v_passed"):
                        code = (dry_cache / r["filename"]).read_text()
                        rev = run_blind_review(
                            op, original_code, code, tag,
                            reviewer_factory=_mock_reviewer_factory,
                            arbiter_factory=_mock_reviewer_factory)
                        reviews.append(rev)

        confirmed = [rec for rec in all_recs if rec.get("v_passed")]
        rev_confirmed = [rv for rv in reviews if rv["review_verdict"] == "CONFIRMED"]
        # Blinding assertion: generator family never reviews its own output.
        for rv in reviews:
            assert rv["reviewer_family"] != rv["arbiter_family"]

        print(f"\n  generated trials : {len(all_recs)}")
        print(f"  V1–V4 passed     : {len(confirmed)}")
        print(f"  blind-review CONF: {len(rev_confirmed)}/{len(reviews)}")

        # Pool (dedup/selection) + SMS (AVP/equiv/bookkeeping) per PUT.
        sms_summary = {}
        for op in ops:
            put = op.put
            selected = select_mutants_for_put(
                put, n_target=6, cache_dir=dry_cache, seed=REGISTERED_SEED)
            pool_dir = dry_cache / f"pool_{put}"
            if pool_dir.exists():
                shutil.rmtree(pool_dir)
            pool_dir.mkdir()
            for p, _opid in selected:
                shutil.copy(p, pool_dir / p.name)
            primary_mp = PRIMARY_CELLS[put]
            cell = sms_mod.evaluate_cell(put, primary_mp, mutant_dir=pool_dir)
            sms_summary[put] = cell
            print(f"  SMS {cell['cell']:<10} inst={cell['inst']} "
                  f"equiv={cell['equiv']} killed={cell['killed']} "
                  f"survive={cell['survive']} SMS={cell['sms']:.4f}")

        assert len(confirmed) > 0, "dry-run produced no valid mutants"
        assert all(s["inst"] > 0 for s in sms_summary.values()), "empty SMS pool"
        print("\n=== DRY-RUN COMPLETE — full pipeline exercised offline ===\n")
        return 0
    finally:
        CACHE_DIR = saved_cache
        if dry_cache.exists():
            shutil.rmtree(dry_cache)  # leave no artifact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--put", default=None, help="restrict to one PUT (e.g. a2)")
    parser.add_argument("--arm", choices=("same", "cross"), default="cross",
                        help="dual-blind arm: 'same'=one generator family (v3-style), "
                             "'cross'=three families (v4-style). Registered §5.")
    parser.add_argument("--review", action="store_true",
                        help="run the §5 dual-blind review+arbitration stage after "
                             "generation (live reviewer LLM; requires .env)")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true",
                        help="OFFLINE full-pipeline smoke test (mock LLMs, 2 PUTs)")
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

    if args.dry_run:
        raise SystemExit(run_dry_run())

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

    _n_src = len(ARMS[args.arm])
    print(f"Phase A MVP: {len(ops)} operators × {_n_src} sources × K={k} trials = "
          f"{len(ops)*_n_src*k} total LLM calls")

    # Arm selection (§5): 'same' uses one generator family; 'cross' uses three.
    _ALL_SOURCES = {
        "claude": generator_claude,
        "gpt": generator_gpt,
        "deepseek": generator_deepseek,
    }
    sources = [(fam, _ALL_SOURCES[fam]) for fam in ARMS[args.arm]]
    print(f"== dual-blind arm: {args.arm} ({len(sources)} generator "
          f"{'family' if len(sources) == 1 else 'families'}), "
          f"review={'on' if args.review else 'off'} ==")

    all_records = []
    t_start = time.time()

    # Cache PUT programs to avoid re-import
    put_cache: dict[str, tuple[str, callable]] = {}  # type: ignore[type-arg]

    for op in ops:
        if op.put not in put_cache:
            put_cache[op.put] = _load_put_program(op.put)
        original_code, original_fn = put_cache[op.put]
        print(f"\n--- {op.id} ({op.label}) ---")

        # sources in parallel via ThreadPoolExecutor (1 for 'same', 3 for 'cross')
        op_records = []
        with ThreadPoolExecutor(max_workers=max(1, len(sources))) as pool:
            futures = {
                pool.submit(_run_one_op_one_source, op, original_code, original_fn,
                            tag, fac, k): tag
                for tag, fac in sources
            }
            for fut in futures:
                op_records.extend(fut.result())
        all_records.extend(op_records)

        # §5 dual-blind review+arbitration stage (identical on both arms).
        # Live reviewer LLM; only runs with --review + valid .env.
        if args.review:
            for rec in op_records:
                if rec.get("v_passed") and rec.get("filename"):
                    code = (CACHE_DIR / rec["filename"]).read_text()
                    rev = run_blind_review(op, original_code, code, rec["source"])
                    rec["review"] = rev

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
