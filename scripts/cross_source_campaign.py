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
import hashlib
import importlib.util
import json
import re
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
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
    study4_slot_factories, study4_role_factory,
)
from p2.config import study4 as study4_cfg  # type: ignore[import-not-found]  # noqa: E402
from p2.mutators.operator_registry import OPERATORS  # type: ignore[import-not-found]  # noqa: E402
from p2.mutators.validation import validate_mutant  # type: ignore[import-not-found]  # noqa: E402
from p2.config.primary import PRIMARY_CELLS  # type: ignore[import-not-found]  # noqa: E402
from p2.config.campaign import single_stratum_filter_enabled  # type: ignore[import-not-found]  # noqa: E402
from p2.mutators.stratum_filter import single_stratum_prompt_clause  # type: ignore[import-not-found]  # noqa: E402

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
# Study-4 (H-LANG) C-language grid. The operator registry semantics are
# LANGUAGE-AGNOSTIC and reused verbatim; only the rendered prompt, the PUT
# source language, and the admission gate (gcc compile + adapter, vs
# ast/exec) change. C admissions land in a separate cache so Python pools
# are never touched. Grid = the 7 ORIGINAL Study-1 PUTs with a faithful
# pure-C99 port (see docs/prereg_v2/C_PORT_SPEC.md; c1/c3/d1/d2/d3 excluded
# as ML-library kernels).
# ══════════════════════════════════════════════════════════════════════════
C_GRID_PUTS = ("a1", "a2", "a3", "b1", "b2", "b3", "c2")
# P14 (C-arm pilot): a self-contained C mutant (includes + program + REPL main)
# is 2-4x the token length of a Python mutant body; 800 (the Python default)
# truncated the longer kernels. 2048 fits every C_GRID kernel with headroom.
C_GEN_MAX_TOKENS = 2048
CACHE_DIR_CLANG = ROOT / "data/operator_campaign/cache_clang"
CACHE_DIR_CLANG.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE_C = """You are an expert in scientific computing software testing. Generate a SEMANTIC MUTANT of the C program below that implements EXACTLY the named operator described.

PUT NAME: {put_name}
OPERATOR ID: {op_id}
OPERATOR LABEL: {op_label}
TARGET LOCATOR: {target_locator}
EXACT CHANGE: {transformation}
RATIONALE: {rationale}

ATTEMPT INDEX: {attempt_idx} of {n_attempts}  (different seed; same operator; produce a STRUCTURALLY DIFFERENT mutant from prior attempts)

The operator semantics are language-agnostic; apply the SAME change to the C source at the analogous site named by the target locator.

━━━ ORIGINAL PROGRAM (C99) ━━━
```c
{original_code}
```

INSTRUCTIONS:
- Apply the operator transformation EXACTLY as specified.
- Output ONLY the complete mutated C program in a ```c``` block.
- The program MUST compile with `gcc -std=c99 -O0 -Wall` (zero warnings) and run on x in [0, 1] returning a finite scalar.
- Preserve `double program(double x)` and the harness `main` (one x per stdin line -> one float per stdout line).
- Do not explain or comment.
"""


def _strip_code_fences(text: str) -> str:
    """Strip a fenced code block for ANY language tag (```python, ```c, bare
    ```). Superset of ``_strip_fences``; used by the C admission path."""
    m = re.search(r"```[a-zA-Z0-9_+.-]*\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _load_c_put_program(put_id: str):
    """C analogue of ``_load_put_program``: returns (source_text, CPutProgram)."""
    from p2.cport.adapter import load_c_put
    src_path = ROOT / f"src/p2/cput/{put_id}.c"
    return src_path.read_text(), load_c_put(put_id, ROOT)


def admit_c_mutant(op, raw_code, original_fn, source_tag, attempt, cache_dir=None):
    """C analogue of ``admit_mutant``: fence-strip -> V1-V3 (gcc + adapter)
    -> cache ``{op}_{source}_attemptNN.c``. Byte-parallel to the Python path
    so ingest bookkeeping (v_passed, filename) is identical downstream."""
    from p2.cport.validation import validate_c_mutant
    cache_dir = Path(cache_dir) if cache_dir is not None else CACHE_DIR_CLANG
    cache_dir.mkdir(parents=True, exist_ok=True)
    code = _strip_code_fences(raw_code)
    v = validate_c_mutant(code, original_fn, build_dir=cache_dir / "_build")
    record = {
        "op": op.id, "put": op.put, "source": source_tag, "attempt": attempt,
        "lang": "c",
        "v_syntax": v.syntax_ok, "v_executable": v.executable,
        "v_nontrivial": v.nontrivial, "v_passed": v.passed, "v_error": v.error,
    }
    if v.passed:
        fname = f"{op.id}_{source_tag}_attempt{attempt:02d}.c"
        (cache_dir / fname).write_text(code)
        record["filename"] = fname
    return record


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


# Retryable gateway failures (Study-4): rate limits, 5xx, timeouts, dropped
# connections. Imported lazily-safe so an offline dry-run without the SDK error
# classes still loads (they exist in openai>=1, but guard anyway).
try:  # pragma: no cover - trivial import guard
    from openai import (RateLimitError, APITimeoutError, APIConnectionError,
                        InternalServerError, APIStatusError)
    _RETRYABLE = (RateLimitError, APITimeoutError, APIConnectionError,
                  InternalServerError)
except Exception:  # pragma: no cover
    APIStatusError = ()  # type: ignore[assignment,misc]
    _RETRYABLE = ()  # type: ignore[assignment]


def _chat_with_retry(client, *, model, messages, max_tokens, temperature,
                     tries: int = 3, base_delay: float = 1.5):
    """chat.completions.create with exponential backoff on 429/5xx/timeouts.

    Study-4 gateway calls retry ``tries`` times (default 3) with delays
    base_delay * 2**attempt. A 4xx that is not 429 is a hard error (bad request /
    auth) and is NOT retried. The MockLLMClient path never raises, so this is a
    transparent pass-through offline.
    """
    last = None
    for attempt in range(tries):
        try:
            return client.chat.completions.create(
                model=model, messages=messages,
                max_tokens=max_tokens, temperature=temperature)
        except _RETRYABLE as e:  # transient — back off and retry
            last = e
        except APIStatusError as e:  # retry only 5xx / 429
            code = getattr(e, "status_code", None)
            if code is not None and (code >= 500 or code == 429):
                last = e
            else:
                raise
        if attempt < tries - 1:
            time.sleep(base_delay * (2 ** attempt))
    raise last  # type: ignore[misc]


def _generate_one(client: OpenAI, model: str, prompt: str, max_tokens: int = 800,
                  min_max_tokens: int = 0) -> tuple[str, dict]:
    """Single chat completion with timing, token usage, and served-model echo.

    ``min_max_tokens`` raises the effective ``max_tokens`` floor for models whose
    reasoning consumes the budget (gemini-3.5-flash needs >= 2000). The returned
    meta records ``served_model`` (response.model) so the grok-4.1 -> grok-4.3
    mapping is captured at runtime in the campaign log.
    """
    eff_max = max(max_tokens, min_max_tokens) if min_max_tokens else max_tokens
    t0 = time.time()
    resp = _chat_with_retry(
        client, model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=eff_max, temperature=0.7)
    dt = time.time() - t0
    msg = resp.choices[0].message
    content = msg.content or ""
    usage = resp.usage
    return _strip_fences(content), {
        "latency_s": round(dt, 2),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "requested_model": model,
        "served_model": getattr(resp, "model", None),
    }


def admit_mutant(op, raw_code, original_fn, source_tag, attempt,
                 cache_dir=None, meta=None):
    """THE shared normalization → V1–V4 → admission path.

    Every source of a raw mutant string — the live LLM client, the offline
    MockLLMClient, and the packet-workflow agent responses — funnels through
    this ONE function. There is deliberately NO packet-specific leniency: the
    fence stripping, `validate_mutant` gate, and cache-write naming convention
    (`{op}_{source}_attemptNN.py`) are identical regardless of caller, so a
    packet-ingested mutant is byte-indistinguishable from a live-generated one
    downstream (pool_builder → AVP/equiv → SMS).

    Returns the per-trial record dict; on V-pass it also writes the admitted
    mutant into `cache_dir` and stamps `record["filename"]`.
    """
    cache_dir = cache_dir if cache_dir is not None else CACHE_DIR
    code = _strip_fences(raw_code)
    v = validate_mutant(code, original_fn)
    record = {
        "op": op.id,
        "put": op.put,
        "source": source_tag,
        "attempt": attempt,
        "v_syntax": v.syntax_ok,
        "v_executable": v.executable,
        "v_nontrivial": v.nontrivial,
        "v_passed": v.passed,
        "v_error": v.error,
    }
    if meta is not None:
        record["latency_s"] = meta.get("latency_s")
        record["prompt_tokens"] = meta.get("prompt_tokens")
        record["completion_tokens"] = meta.get("completion_tokens")
    if v.passed:
        fname = f"{op.id}_{source_tag}_attempt{attempt:02d}.py"
        (cache_dir / fname).write_text(code)
        record["filename"] = fname
    return record


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
        # Study-2 weak spec-level guardrail for CF/TF (layer 1; the load-bearing
        # enforcement is the post-generation single-stratum admission screen in
        # scripts/build_pools.py). Returns "" for the four local-edit families,
        # so non-CF/TF prompts stay byte-identical to before.
        if single_stratum_filter_enabled():
            prompt += single_stratum_prompt_clause(op.category)
        try:
            code, meta = _generate_one(client, model, prompt)
        except Exception as e:
            results.append({
                "op": op.id, "source": source_tag, "attempt": attempt,
                "v_passed": False, "error": f"LLM_FAIL: {type(e).__name__}: {e}",
            })
            continue

        record = admit_mutant(op, code, original_fn, source_tag, attempt,
                              cache_dir=CACHE_DIR, meta=meta)
        record["model"] = model
        results.append(record)
        print(f"  [{op.id} {source_tag} a{attempt:02d}] "
              f"{'PASS' if record['v_passed'] else 'FAIL'} {meta['latency_s']}s "
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


# ══════════════════════════════════════════════════════════════════════════
# PACKET WORKFLOW (harness mode) — Study-2 generation/review WITHOUT network.
#
# When no external LLM credentials exist, generator/reviewer roles are served
# by Claude-agent instances orchestrated by the main session (disclosed in the
# v1.1 amendment). The campaign becomes two offline phases per cell batch:
#   export  → agent fills responses → ingest.
# The ingest side re-uses `admit_mutant` (the SAME normalization → V1–V4 →
# admission path as the live/mock client) so the offline pipeline (dedup,
# AVP/equiv, SMS bookkeeping) stays byte-for-byte the registered machinery.
# Packets carry NO SMS/outcome fields; review packets are additionally blinded
# (no generator identity, no arm label, no cell aggregates).
# ══════════════════════════════════════════════════════════════════════════

PACKET_ROOT = ROOT / "data" / "study2_packets"

# Field-name tokens that must NEVER appear as keys in any packet (outcome leak).
_FORBIDDEN_PACKET_KEY_TOKENS = ("sms", "killed", "survive", "outcome", "verdict",
                                "kill_count")

GENERATION_RESPONSE_SCHEMA = {
    "description": "Return ONE JSON object per generation packet. No prose.",
    "required_top_level": ["packet_id", "put_id", "mutants"],
    "mutants_item_fields": {
        "op_id": "one of the packet's operator ids",
        "source": "one of the packet's 'sources' role tags",
        "attempt": "integer in 1..k_per_source",
        "code": "complete Python mutant program (```python fences tolerated, "
                "stripped on ingest); must define def program(x)",
    },
    "one_entry_per": "required_slots (op_id x source x attempt)",
    "forbidden_fields_anywhere": list(_FORBIDDEN_PACKET_KEY_TOKENS) + ["equiv"],
    "strictness": "Malformed entries are rejected and logged; well-formed "
                  "entries run the identical V1–V4 admission gate as live runs.",
}

GENERATION_RESPONSE_SCHEMA_C = {
    **GENERATION_RESPONSE_SCHEMA,
    "mutants_item_fields": {
        "op_id": "one of the packet's operator ids",
        "source": "one of the packet's 'sources' role tags",
        "attempt": "integer in 1..k_per_source",
        "code": "complete C99 mutant program (```c fences tolerated, stripped "
                "on ingest); must define double program(double x) plus the "
                "harness main; MUST compile with gcc -std=c99 -O0 -Wall",
    },
    "strictness": "Malformed entries are rejected and logged; well-formed "
                  "entries run the identical V1–V3 gate (gcc compile + adapter) "
                  "as the Python path, into data/operator_campaign/cache_clang/.",
}

REVIEW_RESPONSE_SCHEMA = {
    "description": "Return ONE JSON verdict object per review packet. No prose.",
    "required_top_level": ["blind_id", "V1_syntax_ok", "V2_executable",
                           "V3_nontrivial", "operator_match", "equivalence",
                           "overall", "reason"],
    "field_domains": {
        "V1_syntax_ok": "true|false",
        "V2_executable": "Yes|No|Uncertain",
        "V3_nontrivial": "Yes|No|Uncertain",
        "operator_match": "Yes|No|Uncertain",
        "equivalence": "object {E1: Yes|No, E2: Yes|No, equivalent: true|false} "
                       "per the registered E1∧E2 equivalence protocol",
        "overall": "CONFIRMED|REJECTED|UNCERTAIN",
    },
    "note": "The mechanical AVP/equiv pipeline remains authoritative for SMS; "
            "the equivalence opinion is recorded, not used to alter the pool.",
}


def _sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pin_template(source_name: str, text: str) -> dict:
    """Pin the registered prompt template by content hash (auditability §5)."""
    return {"source": source_name, "sha256": _sha256_text(text),
            "char_len": len(text)}


def _load_mrs_source(put: str) -> dict:
    p = ROOT / "src" / "p2" / "mrs" / f"{put}.py"
    text = p.read_text()
    mps = sorted({int(m) for m in re.findall(r"def r_mp(\d)\(", text)})
    return {"path": f"src/p2/mrs/{put}.py", "sha256": _sha256_text(text),
            "available_mps": mps, "source": text}


def _operator_spec(op) -> dict:
    spec = {
        "id": op.id, "put": op.put, "category": op.category, "label": op.label,
        "target_locator": op.target_locator, "transformation": op.transformation,
        "rationale": op.rationale, "is_key": bool(getattr(op, "is_key", False)),
    }
    # CF/TF constraint flag: forward-compatible with F2's registry change. When
    # MutationOperator gains `constraint_flag`, it is consumed here with no
    # packet-code change; until then we surface the documented integration
    # point so CF/TF packets are audit-complete either way. (F2's landed layer
    # is the single_stratum admission screen in build_pools.py; a per-operator
    # flag field, if added, is picked up here automatically.)
    cf = getattr(op, "constraint_flag", None)
    if cf is None:
        cf = getattr(op, "cf_tf_constraint", None)
    spec["constraint_flag"] = cf
    if cf is None and op.category in ("CF", "TF"):
        spec["constraint_flag_integration_point"] = (
            "MutationOperator exposes no constraint_flag yet; when F2's registry "
            "change merges a per-operator flag, it is read via "
            "getattr(op,'constraint_flag') with no packet-code change. The "
            "load-bearing CF/TF enforcement is the single-stratum admission "
            "screen in build_pools.py.")
    return spec


def _assert_no_outcome_fields(obj, path="root") -> None:
    """Recursively assert no packet KEY leaks an SMS/outcome field (§ blinding)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            for tok in _FORBIDDEN_PACKET_KEY_TOKENS:
                if tok in kl:
                    raise AssertionError(
                        f"packet leaks outcome field '{k}' at {path}")
            _assert_no_outcome_fields(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_no_outcome_fields(v, f"{path}[{i}]")


def _manifest_path(d) -> Path:
    return Path(d) / "manifest.json"


def _load_manifest(d) -> dict:
    p = _manifest_path(d)
    if p.exists():
        return json.loads(p.read_text())
    return {"generation_packets": [], "generation_responses": [],
            "review_packets": [], "review_verdicts": []}


def _save_manifest(d, m) -> None:
    _manifest_path(d).write_text(json.dumps(m, indent=2, ensure_ascii=False))


def _campaign_log_append(work_dir, event: str, payload: dict) -> None:
    log = Path(work_dir) / "campaign_log.json"
    entries = json.loads(log.read_text()) if log.exists() else []
    entries.append({"event": event, "ts": _now_iso(), **payload})
    log.write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    # Best-effort global audit trail under data/study2_packets/.
    try:
        PACKET_ROOT.mkdir(parents=True, exist_ok=True)
        with (PACKET_ROOT / "campaign_log.jsonl").open("a") as fh:
            fh.write(json.dumps({"event": event, "ts": _now_iso(),
                                 "work_dir": str(work_dir), **payload}) + "\n")
    except OSError:
        pass


# ── Phase 1: export GENERATION packets ─────────────────────────────────────

def export_generation_packets(out_dir, puts=None, arm="cross",
                              k=REGISTERED_K, seed=REGISTERED_SEED,
                              lang="py") -> dict:
    """One GENERATION packet per selected PUT (its operators feed one per-PUT
    pool, reused across all 5 MPs). NO SMS/outcome fields anywhere.

    ``lang`` selects the grid: 'py' (default, all registry PUTs) or 'c'
    (Study-4 H-LANG; restricted to C_GRID_PUTS, C prompt + C schema, C PUT
    source). The operator specs and shared MR definitions are identical
    across languages."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    is_c = (lang == "c")
    if is_c:
        template = PROMPT_TEMPLATE_C
        load_prog = _load_c_put_program
        schema = GENERATION_RESPONSE_SCHEMA_C
        tpl = _pin_template("cross_source_campaign.PROMPT_TEMPLATE_C", template)
        universe = list(C_GRID_PUTS)
        puts = [p for p in (sorted(puts) if puts else universe) if p in C_GRID_PUTS]
    else:
        template = PROMPT_TEMPLATE
        load_prog = _load_put_program
        schema = GENERATION_RESPONSE_SCHEMA
        tpl = _pin_template("cross_source_campaign.PROMPT_TEMPLATE", template)
        puts = sorted(puts) if puts else sorted({o.put for o in OPERATORS})
    sources = list(ARMS[arm])
    manifest = _load_manifest(out_dir)
    written = []
    for put in puts:
        ops = sorted((o for o in OPERATORS if o.put == put), key=lambda o: o.id)
        if not ops:
            continue
        original_code, _ = load_prog(put)
        # Mirror the live generator prompt EXACTLY: append F2's single-stratum
        # CF/TF guardrail clause when enabled (empty for the 4 local-edit
        # families), so packet prompts are byte-identical to a live campaign.
        stratum_on = single_stratum_filter_enabled()
        op_blocks, slots = [], []
        for op in ops:
            clause = single_stratum_prompt_clause(op.category) if stratum_on else ""
            prompts = {
                str(a): template.format(
                    put_name=op.put.upper(), op_id=op.id, op_label=op.label,
                    target_locator=op.target_locator,
                    transformation=op.transformation, rationale=op.rationale,
                    attempt_idx=a, n_attempts=k, original_code=original_code) + clause
                for a in range(1, k + 1)
            }
            op_blocks.append({"spec": _operator_spec(op),
                              "prompts_by_attempt": prompts})
            for source in sources:
                for a in range(1, k + 1):
                    slots.append({"op_id": op.id, "source": source, "attempt": a})
        pid = f"gen_c_{put}" if is_c else f"gen_{put}"
        packet = {
            "packet_type": "generation",
            "packet_id": pid,
            "put_id": put,
            "lang": lang,
            "arm": arm,
            "seed": seed,
            "k_per_source": k,
            "sources": sources,
            "registered_prompt_template": tpl,
            "single_stratum_guardrail": stratum_on,
            "put_source": original_code,
            "mr_definitions": _load_mrs_source(put),
            "operators": op_blocks,
            "mutant_count_target": {
                "per_operator_total": len(sources) * k,
                "n_operators": len(ops),
                "packet_total": len(slots),
            },
            "required_slots": slots,
            "response_schema": schema,
            "response_filename": f"{pid}_response.json",
            "instructions": (
                "Act as the mutant generator. For EACH required slot, follow the "
                "operator's rendered prompt (operators[].prompts_by_attempt[attempt]) "
                "and return the complete mutant program in the 'code' field. Return "
                "exactly one mutants[] entry per required_slots item. Do NOT include "
                "any SMS/kill/survive/outcome field. Write the JSON response to the "
                "file named in response_filename, in the same directory as this "
                "packet."),
        }
        _assert_no_outcome_fields(packet)
        text = json.dumps(packet, indent=2, ensure_ascii=False)
        path = out_dir / f"{packet['packet_id']}.json"
        path.write_text(text)
        entry = {"packet_id": packet["packet_id"], "put": put,
                 "file": path.name, "sha256": _sha256_text(text),
                 "n_operators": len(ops), "n_slots": len(slots),
                 "created": _now_iso()}
        manifest["generation_packets"] = [
            e for e in manifest["generation_packets"]
            if e["packet_id"] != entry["packet_id"]] + [entry]
        written.append(entry)
    _save_manifest(out_dir, manifest)
    _campaign_log_append(out_dir, "export-generation",
                         {"arm": arm, "k": k, "seed": seed,
                          "n_packets": len(written),
                          "puts": [e["put"] for e in written]})
    print(f"[export-packets] wrote {len(written)} generation packet(s) → {out_dir}")
    return manifest


# ── Phase 2: ingest GENERATION responses ───────────────────────────────────

def _validate_generation_response(obj, packet) -> tuple[list, list]:
    """Strict schema validation. Returns (valid_entries, errors)."""
    errors, valid = [], []
    if not isinstance(obj, dict):
        return [], ["response is not a JSON object"]
    for key in ("packet_id", "put_id", "mutants"):
        if key not in obj:
            errors.append(f"missing top-level key '{key}'")
    if errors:
        return [], errors
    if obj["packet_id"] != packet["packet_id"]:
        errors.append(f"packet_id mismatch: {obj['packet_id']} != {packet['packet_id']}")
    if obj["put_id"] != packet["put_id"]:
        errors.append(f"put_id mismatch: {obj['put_id']} != {packet['put_id']}")
    if not isinstance(obj["mutants"], list):
        errors.append("'mutants' is not a list")
        return [], errors
    allowed = {(s["op_id"], s["source"], s["attempt"])
               for s in packet["required_slots"]}
    op_ids = {s["op_id"] for s in packet["required_slots"]}
    sources = set(packet["sources"])
    k = packet["k_per_source"]
    for i, m in enumerate(obj["mutants"]):
        tag = f"mutants[{i}]"
        if not isinstance(m, dict):
            errors.append(f"{tag}: not an object")
            continue
        leak = [key for key in m
                if any(t in str(key).lower() for t in _FORBIDDEN_PACKET_KEY_TOKENS)]
        if leak:
            errors.append(f"{tag}: forbidden outcome field(s) {leak}")
            continue
        missing = [f for f in ("op_id", "source", "attempt", "code") if f not in m]
        if missing:
            errors.append(f"{tag}: missing field(s) {missing}")
            continue
        if m["op_id"] not in op_ids:
            errors.append(f"{tag}: op_id '{m['op_id']}' not in packet")
            continue
        if m["source"] not in sources:
            errors.append(f"{tag}: source '{m['source']}' not a packet source")
            continue
        if not isinstance(m["attempt"], int) or not (1 <= m["attempt"] <= k):
            errors.append(f"{tag}: attempt '{m['attempt']}' out of 1..{k}")
            continue
        if (m["op_id"], m["source"], m["attempt"]) not in allowed:
            errors.append(f"{tag}: slot ({m['op_id']},{m['source']},{m['attempt']}) "
                          "not a declared slot")
            continue
        if not isinstance(m["code"], str) or not m["code"].strip():
            errors.append(f"{tag}: empty/non-string code")
            continue
        valid.append(m)
    return valid, errors


def _iter_response_files(in_dir):
    for f in sorted(Path(in_dir).glob("*.json")):
        if f.name in ("manifest.json", "campaign_log.json",
                      "_blind_map.json", "ingest_generation_log.json",
                      "ingest_review_log.json"):
            continue
        try:
            obj = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            yield f, None, f"invalid JSON: {e}"
            continue
        if isinstance(obj, dict) and obj.get("packet_type") in (
                "generation", "review"):
            continue  # a packet, not a response
        yield f, obj, None


def ingest_generation(in_dir, cache_dir=None, packets_dir=None, lang=None) -> dict:
    """Validate agent GENERATION responses (strict) and run each admitted
    mutant through the SAME admission path as the live/mock client.

    The language is taken per-packet from the packet's ``lang`` field
    (falling back to the ``lang`` arg, then 'py'); C packets validate via
    gcc+adapter and default to the ``cache_clang`` cache, so Python and C
    responses can even be ingested from the same directory without cross
    contamination."""
    in_dir = Path(in_dir)
    packets_dir = Path(packets_dir) if packets_dir else in_dir
    cache_override = Path(cache_dir) if cache_dir else None
    cache_dir = cache_override or CACHE_DIR    # last-touched cache, for the return
    manifest = _load_manifest(in_dir)
    all_records, all_errors, per_put = [], [], {}
    put_fn_cache: dict = {}
    for f, obj, ferr in _iter_response_files(in_dir):
        if ferr:
            all_errors.append({"file": f.name, "errors": [ferr]})
            print(f"[ingest-generation] REJECT {f.name}: {ferr}")
            continue
        if not isinstance(obj, dict) or "mutants" not in obj:
            continue  # not a generation response
        pid = obj.get("packet_id")
        ppath = packets_dir / f"{pid}.json"
        if not ppath.exists():
            msg = f"no matching packet '{pid}.json' in {packets_dir}"
            all_errors.append({"file": f.name, "errors": [msg]})
            print(f"[ingest-generation] REJECT {f.name}: {msg}")
            continue
        packet = json.loads(ppath.read_text())
        valid, errs = _validate_generation_response(obj, packet)
        for e in errs:
            print(f"[ingest-generation] {f.name}: SCHEMA-ERR {e}")
        if errs:
            all_errors.append({"file": f.name, "errors": errs})
        put = packet["put_id"]
        pkt_lang = packet.get("lang", lang or "py")
        is_c = (pkt_lang == "c")
        cache_dir = cache_override or (CACHE_DIR_CLANG if is_c else CACHE_DIR)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_key = (put, pkt_lang)
        if cache_key not in put_fn_cache:
            put_fn_cache[cache_key] = (
                _load_c_put_program(put) if is_c else _load_put_program(put))
        _, original_fn = put_fn_cache[cache_key]
        op_by_id = {o.id: o for o in OPERATORS if o.put == put}
        admit = admit_c_mutant if is_c else admit_mutant
        covered = set()
        for m in valid:
            op = op_by_id[m["op_id"]]
            rec = admit(op, m["code"], original_fn, m["source"],
                        m["attempt"], cache_dir=cache_dir)
            rec["ingested_from"] = f.name
            all_records.append(rec)
            covered.add((m["op_id"], m["source"], m["attempt"]))
        declared = {(s["op_id"], s["source"], s["attempt"])
                    for s in packet["required_slots"]}
        gaps = sorted(declared - covered)
        n_pass = sum(1 for r in all_records
                     if r.get("ingested_from") == f.name and r.get("v_passed"))
        per_put[put] = {"file": f.name, "n_valid": len(valid),
                        "n_admitted": n_pass, "n_gaps": len(gaps),
                        "n_schema_errors": len(errs)}
        manifest["generation_responses"] = [
            e for e in manifest["generation_responses"]
            if e.get("file") != f.name] + [{
                "file": f.name, "packet_id": pid, "put": put,
                "sha256": _sha256_text(f.read_text()),
                "n_valid": len(valid), "n_admitted": n_pass,
                "n_gaps": len(gaps), "n_schema_errors": len(errs),
                "ingested": _now_iso()}]
        print(f"[ingest-generation] {f.name}: {len(valid)} valid, {n_pass} "
              f"admitted (V1–V4), {len(errs)} schema-err, {len(gaps)} gaps")
    _save_manifest(in_dir, manifest)
    _campaign_log_append(in_dir, "ingest-generation", {
        "n_records": len(all_records),
        "n_admitted": sum(1 for r in all_records if r.get("v_passed")),
        "n_files_with_errors": len(all_errors),
        "per_put": per_put})
    (in_dir / "ingest_generation_log.json").write_text(
        json.dumps({"records": all_records, "errors": all_errors,
                    "per_put": per_put}, indent=2, ensure_ascii=False))
    return {"records": all_records, "errors": all_errors, "per_put": per_put,
            "cache_dir": str(cache_dir)}


# ── Phase 3: export/ingest blinded REVIEW packets ──────────────────────────

def _blind_id(op_id: str, source: str, attempt: int) -> str:
    return "rev_" + _sha256_text(f"{op_id}|{source}|{attempt}")[:12]


def export_review_packets(cache_dir=None, out_dir=None) -> dict:
    """One BLINDED review packet per admitted mutant. Omits generator identity,
    arm label, and cell aggregates; carries mutant code + PUT + operator only."""
    cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    op_by_id = {o.id: o for o in OPERATORS}
    manifest = _load_manifest(out_dir)
    blind_map = {}
    n = 0
    for mut in sorted(cache_dir.glob("*_attempt*.py")):
        m = re.match(r"([a-d]\d+_[A-Z]+\d+)_([a-z]+)_attempt(\d+)\.py$", mut.name)
        if not m:
            continue
        op_id, source, attempt = m.group(1), m.group(2), int(m.group(3))
        op = op_by_id.get(op_id)
        if op is None:
            continue
        put_source, _ = _load_put_program(op.put)
        code = mut.read_text()
        # Blinding redaction (incident P7): some generators echo the slot's
        # source label into the mutant docstring. Redact source-family tokens
        # from the DISPLAYED code only (deterministic, case-insensitive,
        # presentation-layer; the admitted artifact on disk is untouched and
        # the docstring carries no program semantics). The leak assertion
        # below remains the final guard post-redaction.
        for fam in FAMILIES:
            code = re.sub(fam, "src", code, flags=re.IGNORECASE)
        blind = _blind_id(op_id, source, attempt)
        packet = build_blind_review_packet(op, put_source, code)
        packet.update({
            "packet_type": "review",
            "blind_id": blind,
            "review_prompt": REVIEW_PROMPT_TEMPLATE.format(
                op_id=op.id, op_label=op.label,
                target_locator=op.target_locator,
                transformation=op.transformation,
                put_source=put_source, mutant_code=code),
            "response_schema": REVIEW_RESPONSE_SCHEMA,
            "response_filename": f"{blind}_response.json",
            "instructions": (
                "Act as a BLIND reviewer. You are given only the original PUT, "
                "the candidate mutant, and the operator spec. Judge the V-checks "
                "and give an equivalence opinion under the E1∧E2 protocol: "
                "E1 = the mutant is output-equivalent to the original PUT on the "
                "declared input domain (same output within numerical tolerance "
                "for every admissible input); E2 = a behavioural classifier over "
                "sampled executions cannot distinguish mutant from original. "
                "Report equivalent=true only if BOTH E1 and E2 hold in your "
                "judgment. Write the JSON verdict to the file named in "
                "response_filename, in the same directory as this packet; do not "
                "guess who generated the mutant."),
        })
        # Blinding guarantees (§5): no source/arm/cell-aggregate leak.
        _assert_no_outcome_fields(packet)
        flat = json.dumps(packet).lower()
        for fam in FAMILIES:
            assert fam not in flat, f"review packet leaks generator family {fam}"
        assert "arm" not in packet and source not in packet.get("blind_id", "")
        text = json.dumps(packet, indent=2, ensure_ascii=False)
        (out_dir / f"{blind}.json").write_text(text)
        blind_map[blind] = {"op_id": op_id, "put": op.put, "source": source,
                            "attempt": attempt, "mutant_file": mut.name,
                            "packet_sha256": _sha256_text(text)}
        n += 1
    # Private map (audit only — never shown to the reviewer agent).
    (out_dir / "_blind_map.json").write_text(
        json.dumps(blind_map, indent=2, ensure_ascii=False))
    manifest["review_packets"] = [{"blind_id": b, **v}
                                  for b, v in sorted(blind_map.items())]
    _save_manifest(out_dir, manifest)
    _campaign_log_append(out_dir, "export-review", {"n_packets": n})
    print(f"[export-review-packets] wrote {n} blinded review packet(s) → {out_dir}")
    return {"n_packets": n, "blind_map": blind_map}


def _validate_review_response(obj) -> tuple[dict, list]:
    errors = []
    if not isinstance(obj, dict):
        return None, ["verdict is not a JSON object"]
    for key in REVIEW_RESPONSE_SCHEMA["required_top_level"]:
        if key not in obj:
            errors.append(f"missing key '{key}'")
    if errors:
        return None, errors
    if obj["overall"] not in ("CONFIRMED", "REJECTED", "UNCERTAIN"):
        errors.append(f"overall '{obj['overall']}' not in domain")
    if not isinstance(obj.get("equivalence"), dict):
        errors.append("equivalence must be an object {E1,E2,equivalent}")
    if errors:
        return None, errors
    return obj, []


def ingest_review(in_dir, packets_dir=None) -> dict:
    """Ingest agent REVIEW verdicts (strict); classify and, for disagreements
    (UNCERTAIN → arbitration), emit blinded arbitration packets."""
    from types import SimpleNamespace
    from p2.mutators.dual_blind import classify_mutant, MutantStatus
    in_dir = Path(in_dir)
    packets_dir = Path(packets_dir) if packets_dir else in_dir
    manifest = _load_manifest(in_dir)
    verdicts, errors, arbitration_ids = [], [], []
    arb_dir = in_dir / "arbitration"
    for f, obj, ferr in _iter_response_files(in_dir):
        if ferr:
            errors.append({"file": f.name, "errors": [ferr]})
            print(f"[ingest-review] REJECT {f.name}: {ferr}")
            continue
        if not isinstance(obj, dict) or "overall" not in obj or "blind_id" not in obj:
            continue  # not a verdict file
        parsed, errs = _validate_review_response(obj)
        if errs:
            for e in errs:
                print(f"[ingest-review] {f.name}: SCHEMA-ERR {e}")
            errors.append({"file": f.name, "errors": errs})
            continue
        blind = parsed["blind_id"]
        status = classify_mutant(SimpleNamespace(overall=parsed["overall"]))
        rec = {"blind_id": blind, "overall": parsed["overall"],
               "operator_match": parsed.get("operator_match"),
               "equivalence": parsed.get("equivalence"),
               "status": status.value, "file": f.name}
        verdicts.append(rec)
        if status == MutantStatus.ARBITRATED:
            arbitration_ids.append(blind)
            src_packet = packets_dir / f"{blind}.json"
            if src_packet.exists():
                arb_dir.mkdir(parents=True, exist_ok=True)
                pk = json.loads(src_packet.read_text())
                pk["packet_type"] = "review"
                pk["arbitration"] = True
                pk["response_filename"] = f"{blind}_response.json"
                pk["instructions"] = (
                    "ARBITRATION: generator/reviewer disagreed. Re-judge this "
                    "blinded mutant independently under the same E1∧E2 protocol "
                    "(E1 = output-equivalence on the declared domain within "
                    "tolerance; E2 = behavioural classifier cannot distinguish; "
                    "equivalent=true only if BOTH hold). Write the JSON verdict "
                    "to the file named in response_filename, in the same "
                    "directory as this packet.")
                (arb_dir / f"{blind}.json").write_text(
                    json.dumps(pk, indent=2, ensure_ascii=False))
    manifest["review_verdicts"] = verdicts
    _save_manifest(in_dir, manifest)
    (in_dir / "ingest_review_log.json").write_text(
        json.dumps({"verdicts": verdicts, "errors": errors,
                    "arbitration": arbitration_ids}, indent=2, ensure_ascii=False))
    _campaign_log_append(in_dir, "ingest-review", {
        "n_verdicts": len(verdicts), "n_errors": len(errors),
        "n_arbitration": len(arbitration_ids)})
    print(f"[ingest-review] {len(verdicts)} verdict(s), {len(errors)} rejected, "
          f"{len(arbitration_ids)} → arbitration")
    return {"verdicts": verdicts, "errors": errors,
            "arbitration": arbitration_ids}


# ══════════════════════════════════════════════════════════════════════════
# STUDY-4 (H2-2 cross-vendor) — LIVE four-vendor campaign wiring.
#
# Four vendors on ONE OpenAI-compatible gateway, model-role mapping read from
# the pinned config (p2.config.study4), never hardcoded here:
#   arm=same  -> all 3 generator slots = claude-fable-5
#   arm=cross -> src1=gpt-5.5, src2=gemini-3.5-flash, src3=grok-4.1
#   reviewer  = claude-fable-5 (blinded, packets identical to harness mode)
#   arbiter   = gpt-5.5 (only on reviewer UNCERTAIN)
# Every generation and review is funnelled through the SAME admit_mutant path
# (fence-strip -> V1-V4 -> cache-write), with per-call token/cost accounting
# appended to a JSONL campaign log. Slot tags (src1/2/3) are vendor-neutral and
# identical across arms, so neither the filename nor the blinded packet reveals
# the vendor or the arm.
# ══════════════════════════════════════════════════════════════════════════

STUDY4_CACHE = ROOT / "data" / "operator_campaign" / "cache_study4_pilot"

# Vendor tokens redacted from the DISPLAYED mutant code in review packets, so a
# model that echoes its own family into a docstring cannot de-blind itself
# (presentation-layer only; the admitted artifact on disk is untouched).
STUDY4_VENDOR_TOKENS = ("claude", "fable", "anthropic", "gpt", "openai",
                        "gemini", "google", "grok", "xai", "deepseek")


def _study4_log_append(log_path, record: dict) -> None:
    """Append one JSON line (per-call token/cost accounting) to the campaign log."""
    if log_path is None:
        return
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": _now_iso(), **record}
    with log_path.open("a") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _study4_call(factory, prompt: str, *, kind: str, slot_tag: str,
                 op_id: str | None, log_path, max_tokens: int = 800) -> tuple[str, dict]:
    """One gateway call with the model's quirks, cost accounting, and served-id echo.

    Applies the config ``min_max_tokens`` floor (gemini), records the served
    model (grok-4.1 -> grok-4.3), and appends a per-call cost row to the JSONL
    campaign log. Returns (stripped_code, meta) with meta['cost_usd'] set.
    """
    client, model, quirks = factory()
    floor = int(quirks.get("min_max_tokens", 0) or 0)
    code, meta = _generate_one(client, model, prompt, max_tokens=max_tokens,
                               min_max_tokens=floor)
    cost = study4_cfg.estimate_cost_usd(
        model, meta.get("prompt_tokens"), meta.get("completion_tokens"))
    meta["cost_usd"] = round(cost, 6)
    meta["vendor"] = quirks.get("vendor")
    _study4_log_append(log_path, {
        "event": f"study4-{kind}", "kind": kind, "slot": slot_tag,
        "op_id": op_id, "requested_model": model,
        "served_model": meta.get("served_model"),
        "served_mismatch": (meta.get("served_model") not in (None, model)),
        "latency_s": meta.get("latency_s"),
        "prompt_tokens": meta.get("prompt_tokens"),
        "completion_tokens": meta.get("completion_tokens"),
        "cost_usd": meta["cost_usd"], "empty_body": not bool(code)})
    return code, meta


def study4_generate_slot(op, original_code, original_fn, slot_tag, factory,
                         attempts, cache_dir, log_path, lang="py"):
    """Generate + admit ``attempts`` mutants for one (operator, slot) on the gateway.

    ``lang`` selects the grid: 'py' (default, Study-4 Python arms — byte-unchanged)
    or 'c' (Study-4 H-LANG C-arm pilot: PROMPT_TEMPLATE_C prompt, gcc-compile
    admission via ``admit_c_mutant``, tag-agnostic fence stripping). The gateway
    call, cost accounting, served-id echo, and per-call log are IDENTICAL across
    languages."""
    is_c = (lang == "c")
    tmpl = PROMPT_TEMPLATE_C if is_c else PROMPT_TEMPLATE
    strip = _strip_code_fences if is_c else _strip_fences
    # P14 (C-arm pilot): a C mutant carries the FULL self-contained program
    # (includes + program(x) + the REPL main), which is 2-4x the token length of
    # a Python mutant body. The Python-inherited 800-token budget truncated the
    # longer C kernels (esp. a3 heat-FDM) mid-program -> gcc V1 fails / empty
    # bodies. Raise the C-generation budget so the completion is not truncated by
    # the harness config (the per-model min_max_tokens floor still applies on top).
    gen_max_tokens = C_GEN_MAX_TOKENS if is_c else 800
    results = []
    for attempt in range(1, attempts + 1):
        prompt = tmpl.format(
            put_name=op.put.upper(), op_id=op.id, op_label=op.label,
            target_locator=op.target_locator, transformation=op.transformation,
            rationale=op.rationale, attempt_idx=attempt, n_attempts=attempts,
            original_code=original_code)
        if not is_c and single_stratum_filter_enabled():
            prompt += single_stratum_prompt_clause(op.category)
        try:
            code, meta = _study4_call(factory, prompt, kind="generate",
                                      slot_tag=slot_tag, op_id=op.id,
                                      log_path=log_path, max_tokens=gen_max_tokens)
        except Exception as e:
            rec = {"op": op.id, "put": op.put, "source": slot_tag,
                   "attempt": attempt, "v_passed": False,
                   "error": f"LLM_FAIL: {type(e).__name__}: {e}"}
            results.append(rec)
            _study4_log_append(log_path, {"event": "study4-generate-error",
                                          "op_id": op.id, "slot": slot_tag,
                                          "error": rec["error"]})
            continue
        if is_c:
            rec = admit_c_mutant(op, code, original_fn, slot_tag, attempt,
                                 cache_dir=cache_dir)
            rec["latency_s"] = meta.get("latency_s")
            rec["prompt_tokens"] = meta.get("prompt_tokens")
            rec["completion_tokens"] = meta.get("completion_tokens")
        else:
            rec = admit_mutant(op, code, original_fn, slot_tag, attempt,
                               cache_dir=cache_dir, meta=meta)
        rec["model"] = meta.get("requested_model")
        rec["served_model"] = meta.get("served_model")
        rec["cost_usd"] = meta.get("cost_usd")
        rec["malformed"] = not bool(strip(code))
        results.append(rec)
        print(f"  [{op.id} {slot_tag} a{attempt:02d}] lang={lang} "
              f"{'PASS' if rec['v_passed'] else 'FAIL'} "
              f"{meta['latency_s']}s ct={meta.get('completion_tokens')} "
              f"served={meta.get('served_model')}"
              + ("" if rec["v_passed"] else f" v_err={rec.get('v_error','')[:60]}"),
              flush=True)
    return results


def _study4_blind_code(code: str) -> str:
    """Redact vendor-family tokens from the displayed mutant code (blinding)."""
    for tok in STUDY4_VENDOR_TOKENS:
        code = re.sub(tok, "src", code, flags=re.IGNORECASE)
    return code


def run_study4_blind_review(op, put_source, mutant_code, log_path,
                            reviewer_factory=None, arbiter_factory=None,
                            lang="py") -> dict:
    """Blinded review (claude-fable-5) + arbitration (gpt-5.5) over one mutant.

    Blinding is IDENTICAL to harness mode: the packet is built by
    ``build_blind_review_packet`` (no generator identity, no arm, no SMS) and
    the displayed code is vendor-token-redacted. Arbitration fires only when the
    reviewer returns UNCERTAIN (classify_mutant -> ARBITRATED). ``lang`` only
    swaps the displayed code-fence language (```python -> ```c) so the C reviewer
    sees a correctly-tagged C block; the blinding + verdict semantics are unchanged.
    """
    from types import SimpleNamespace
    from p2.mutators.dual_blind import classify_mutant, MutantStatus

    reviewer_factory = reviewer_factory or study4_role_factory("reviewer")
    arbiter_factory = arbiter_factory or study4_role_factory("arbiter")
    display_code = _study4_blind_code(mutant_code)
    packet = build_blind_review_packet(op, put_source, display_code)
    # Blinding guard: no vendor family may survive into the packet.
    flat = json.dumps(packet).lower()
    for tok in STUDY4_VENDOR_TOKENS:
        assert tok not in flat, f"review packet leaks vendor token {tok!r}"
    prompt = REVIEW_PROMPT_TEMPLATE.format(
        op_id=packet["operator"]["id"], op_label=packet["operator"]["label"],
        target_locator=packet["operator"]["target_locator"],
        transformation=packet["operator"]["transformation"],
        put_source=packet["put_source"], mutant_code=packet["mutant_code"])
    if lang == "c":
        prompt = prompt.replace("```python", "```c")

    raw, _m = _study4_call(reviewer_factory, prompt, kind="review",
                           slot_tag="reviewer", op_id=op.id, log_path=log_path,
                           max_tokens=400)
    parsed = _parse_review_json(raw)
    status = classify_mutant(SimpleNamespace(overall=parsed.get("overall", "UNCERTAIN")))
    arbitrated = False
    if status == MutantStatus.ARBITRATED:
        raw_arb, _ma = _study4_call(arbiter_factory, prompt, kind="arbitrate",
                                    slot_tag="arbiter", op_id=op.id,
                                    log_path=log_path, max_tokens=400)
        parsed = _parse_review_json(raw_arb)
        arbitrated = True
    return {"review_verdict": parsed.get("overall", "UNCERTAIN"),
            "operator_match": parsed.get("operator_match", "Uncertain"),
            "arbitrated": arbitrated}


def study4_campaign(puts, arm, attempts, cache_dir=None, log_path=None,
                    review=False, lang="py"):
    """Live Study-4 generation (+ optional blinded review) over the given PUTs.

    Returns {records, reviews, cache_dir}. All four vendors run on the gateway;
    the slot->model mapping is read from the pinned config via
    ``study4_slot_factories(arm)``. ``lang`` selects the grid: 'py' (default, the
    Python H2-2 arms) or 'c' (the Study-4 H-LANG C-arm pilot: the PUT is loaded
    as its C99 source + compiled ``CPutProgram`` original, admission is gcc-based).
    """
    cache_dir = Path(cache_dir) if cache_dir else STUDY4_CACHE
    cache_dir.mkdir(parents=True, exist_ok=True)
    is_c = (lang == "c")
    # C arm is registered on the 7 ported PUTs only (§2c); guard against loading
    # a non-ported PUT's (absent) .c source when the caller passes a wider roster.
    put_set = set(puts)
    if is_c:
        put_set &= set(C_GRID_PUTS)
    cfg = study4_cfg.load_study4_config()
    # Registered rich-class x4 slot multiplier (§2a/§4b): C/D PUTs generate at
    # base*mult per (operator, slot) in the Python arms; A/B at baseline; the C
    # arm gets NO multiplier (§2c). Config-driven, default 1 (off) when absent.
    mult = study4_cfg.rich_multiplier(cfg) if not is_c else 1
    slots = study4_slot_factories(arm)
    ops = sorted((o for o in OPERATORS if o.put in put_set), key=lambda o: o.id)
    if mult > 1:
        rich = sorted({o.put for o in ops if study4_cfg.is_rich_put(o.put, cfg)})
        print(f"  [rich-x{mult}] {len(rich)} rich (C/D) PUTs at {attempts}x{mult}"
              f"={attempts * mult} attempts/slot; A/B at {attempts}: rich={rich}",
              flush=True)
    records, reviews = [], []
    put_cache: dict = {}
    for op in ops:
        if op.put not in put_cache:
            put_cache[op.put] = (_load_c_put_program(op.put) if is_c
                                 else _load_put_program(op.put))
        original_code, original_fn = put_cache[op.put]
        eff_attempts = study4_cfg.attempts_for_put(attempts, op.put, lang=lang, cfg=cfg)
        for slot_tag, factory in slots:
            recs = study4_generate_slot(op, original_code, original_fn, slot_tag,
                                        factory, eff_attempts, cache_dir, log_path,
                                        lang=lang)
            records.extend(recs)
            if review:
                for r in recs:
                    if r.get("v_passed") and r.get("filename"):
                        code = (cache_dir / r["filename"]).read_text()
                        rev = run_study4_blind_review(op, original_code, code,
                                                      log_path, lang=lang)
                        r["review"] = rev
                        reviews.append(rev)
    return {"records": records, "reviews": reviews, "cache_dir": str(cache_dir)}


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
    # ── Harness (packet) mode — offline generation/review, no network ──────
    parser.add_argument("--export-packets", dest="export_packets", default=None,
                        metavar="DIR",
                        help="HARNESS: write one GENERATION packet per PUT to DIR")
    parser.add_argument("--ingest-generation", dest="ingest_generation", default=None,
                        metavar="DIR",
                        help="HARNESS: ingest agent generation responses from DIR")
    parser.add_argument("--export-review-packets", dest="export_review", default=None,
                        metavar="DIR",
                        help="HARNESS: write blinded review packets to DIR")
    parser.add_argument("--ingest-review", dest="ingest_review", default=None,
                        metavar="DIR",
                        help="HARNESS: ingest agent review verdicts from DIR")
    parser.add_argument("--puts", default=None,
                        help="comma-separated PUT ids for --export-packets (default all)")
    parser.add_argument("--packets-dir", dest="packets_dir", default=None,
                        metavar="DIR",
                        help="where matching packets live for an ingest step "
                             "(default = the ingest DIR)")
    parser.add_argument("--cache-dir", dest="cache_dir", default=None,
                        metavar="DIR",
                        help="mutant cache dir for packet ingest / review export "
                             "(default data/operator_campaign/cache_cross)")
    parser.add_argument("--lang", choices=("py", "c"), default="py",
                        help="grid language for --export-packets / "
                             "--ingest-generation: 'py' (default) or 'c' "
                             "(Study-4 H-LANG; 7-PUT C grid, gcc admission, "
                             "cache_clang). Ingest also auto-detects per packet.")
    # ── Study-4 (H2-2 cross-vendor) LIVE four-vendor gateway mode ──────────
    parser.add_argument("--study4", action="store_true",
                        help="LIVE Study-4 four-vendor gateway campaign "
                             "(model-role mapping from configs/study4_models.json)")
    parser.add_argument("--attempts", type=int, default=None,
                        help="Study-4: attempts per (operator, slot). Default = "
                             "study4 registered_k; the pilot uses 1.")
    parser.add_argument("--study4-log", dest="study4_log", default=None,
                        metavar="FILE",
                        help="Study-4: JSONL per-call token/cost log path")
    args = parser.parse_args()

    if args.study4:
        puts = args.puts.split(",") if args.puts else sorted({o.put for o in OPERATORS})
        cfg = study4_cfg.load_study4_config()
        attempts = args.attempts if args.attempts is not None else int(cfg["registered_k"])
        cache = Path(args.cache_dir) if args.cache_dir else STUDY4_CACHE
        log_path = Path(args.study4_log) if args.study4_log else (cache / "campaign_log.jsonl")
        print(f"== Study-4 LIVE (arm={args.arm}, attempts={attempts}, "
              f"lang={args.lang}, review={'on' if args.review else 'off'}) — slots "
              f"{study4_cfg.arm_slots(args.arm)} ==")
        out = study4_campaign(puts, args.arm, attempts, cache_dir=cache,
                              log_path=log_path, review=args.review, lang=args.lang)
        n_pass = sum(1 for r in out["records"] if r.get("v_passed"))
        print(f"== Study-4 done: {len(out['records'])} gen, {n_pass} admitted, "
              f"{len(out['reviews'])} reviewed; log={log_path} ==")
        raise SystemExit(0)

    # ── Harness (packet) dispatch — each is a terminal offline action ──────
    if args.export_packets:
        puts = args.puts.split(",") if args.puts else None
        export_generation_packets(args.export_packets, puts=puts, arm=args.arm,
                                  k=args.k, seed=REGISTERED_SEED, lang=args.lang)
        raise SystemExit(0)
    if args.ingest_generation:
        ingest_generation(args.ingest_generation, cache_dir=args.cache_dir,
                          packets_dir=args.packets_dir, lang=args.lang)
        raise SystemExit(0)
    if args.export_review:
        export_review_packets(cache_dir=args.cache_dir, out_dir=args.export_review)
        raise SystemExit(0)
    if args.ingest_review:
        ingest_review(args.ingest_review, packets_dir=args.packets_dir)
        raise SystemExit(0)

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
