#!/usr/bin/env python3
"""Held-out MR source generation for EXP-DIS (Task 2.2, Step 1-2a) — live.

Design (frozen constants from prereg v2 + master plan §1.3.4):
  - s = 2 held-out MR-set replicates; two DISTINCT non-v4 provider families
    (ranking Gemini > Qwen > Mistral > Llama; none of Claude/GPT/DeepSeek),
    which also strengthens the provider-singularity threat answer
    (power_report.md §3).
  - Slots: 12 PUTs × 5 MPs per set (60 slots/set). One MR per slot.
  - Generation-protocol symmetry with v4 (MR_SOURCE_SYMMETRY.md, 7 items):
    one fixed prompt template for every slot and both sets (SHA-256 recorded;
    v4 had no MR-generation arm, so "prompt-verbatim" is instantiated as
    v4-matched protocol parameters + a single fixed template shared by both
    sets), parser = v4 _strip_fences, temperature 0.7, K = 3 candidates per
    slot, no auto-repair beyond the K attempts, max_tokens 800.
  - Prescreen (ex-ante, kill-blind — uses ONLY the original program):
    (a) compiles; defines callables r and R; allowed imports math/numpy;
    (b) domain safety: r maps probe grid {0.1,0.3,0.5,0.7,0.9} to finite
        values in [0,1] (a3: (0,1]); R returns bool on a probe output pair;
    (c) instrument validity: AVP(original, mr) == PASS under the frozen v4
        dispatcher (p2.avp.dispatcher.call_avp, epsilon 1e-6).
    First candidate passing wins the slot; 3 failures leave the slot EMPTY
    (recorded; the affected (cell, condition) becomes unmeasurable and is
    excluded + logged downstream, never imputed).
  - No LLM output is ever fabricated. Raw responses archived.

Outputs:
  data/v5/mrs/set{1,2}/{put}_mp{k}.py     (winning MR code)
  data/v5/mrs/set{1,2}/manifest.json
  data/v5/mrs/raw/                         (all raw responses)
  data/v5/mr_funnel_v5.json                (per-slot funnel)
  data/v5/MR_SOURCE_SYMMETRY.md            (finalised 7-item checklist)

Usage:
  PYTHONPATH=src .venv/bin/python scripts/v5/generate_v5_mrs.py            # live
  PYTHONPATH=src .venv/bin/python scripts/v5/generate_v5_mrs.py --dry-check
  ... --slots a1:1,b3:2 --sets 1                                           # smoke
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

OUT_DIR = ROOT / "data" / "v5" / "mrs"
OUT_FUNNEL = ROOT / "data" / "v5" / "mr_funnel_v5.json"
OUT_MD = ROOT / "data" / "v5" / "MR_SOURCE_SYMMETRY.md"
BASE_SEED = 20260728
TEMPERATURE = 0.7
# v4 budget item (checklist #6): 800 OUTPUT tokens on non-thinking models.
# The author-directed 2026-generation held-out models (2026-07-29 instruction:
# prefer gpt-5.5 / gemini-3.5-flash / grok-4.5 / deepseek-v4-flash / glm-5.2 /
# qwen3.7-plus / minimax-m2.7) route reasoning tokens through max_tokens on
# this proxy, so the mechanical 800 cap yields finish=length with NO artifact
# (probe evidence in MR_SOURCE_SYMMETRY.md). MAX_TOKENS therefore covers the
# reasoning channel; the DELIVERABLE budget is enforced separately in
# prescreen: winning artifact <= ARTIFACT_ENVELOPE_CHARS (~v4's 800 tokens).
MAX_TOKENS = 16000
ARTIFACT_ENVELOPE_CHARS = 3200   # ≈ 800 tokens × 4 chars/token (v4 envelope)
K_CANDIDATES = 3           # v4 convention: K=3 trials per item
EPSILON_AVP = 1e-6
PRESCREEN_TIMEOUT_S = 240
PUTS = ["a1", "a2", "a3", "b1", "b2", "b3",
        "c1", "c2", "c3", "d1", "d2", "d3"]
MPS = [1, 2, 3, 4, 5]

# v4 values (from scripts/cross_source_campaign.py)
V4_SOURCES = ("claude", "gpt", "deepseek")
V4_PROMPT_SHA256 = "06fa552d7431cecc00120bddeb4e8cdc4511ce03f695139809b5af83508a3e90"
V4_PARSER = "cross_source_campaign._strip_fences (```python fence extractor)"

# Held-out set configuration (author-directed preference, 2026-07-29):
#   The author's priority list (gpt-5.5, gemini-3.5-flash, grok-4.5;
#   deepseek-v4-flash, glm-5.2, qwen3.7-plus, minimax-m2.7) is filtered by
#   (a) the frozen held-out family constraint — NOT Claude/GPT/DeepSeek, so
#   gpt-5.5 and deepseek-v4-flash are ineligible for the MR arm — and
#   (b) deliverability probes at MAX_TOKENS=16000 (temperature 0.7):
#       gemini-3.5-flash  finish=stop  ✓ (32s)
#       grok-4.5          finish=stop  ✓ (290s)
#       glm-5.2           finish=length, content empty  ✗
#       qwen3.7-plus      finish=length, 30K visible reasoning ✗
#       minimax-m2.7      finish=length, 57K no fenced block  ✗
#   => set 1: Gemini family (gemini-3.5-flash); set 2: xAI family (grok-4.5).
#   Both non-v4 families, reachable via api_key_1 (credential shared with the
#   generation arm; family-level held-out-ness is the operative criterion,
#   noted for transparency).
SET_DEFAULTS = {
    1: {"model_env": "V5_MR_MODEL_SET1", "model": "gemini-3.5-flash",
        "key_envs": ("V5_MR_API_KEY_SET1", "api_key_1", "BLTCY_API_KEY"),
        "family": "gemini"},
    2: {"model_env": "V5_MR_MODEL_SET2", "model": "grok-4.5",
        "key_envs": ("V5_MR_API_KEY_SET2", "api_key_1", "BLTCY_API_KEY"),
        "family": "grok"},
}

MP_NAMES = {1: "Conservation", 2: "Monotonicity", 3: "Convergence order",
            4: "Trajectory similarity", 5: "Asymptotic ordering"}

# Exact harness semantics per MP (from src/p2/avp/dispatcher.py and the
# mp-specific verifiers) — stated explicitly in the generation prompt per the
# prereg discipline "generation prompts must state implicit invariants
# explicitly" (hypotheses.md §4).
MP_CONTRACTS = {
    1: ("The harness draws 30 samples x ~ Uniform(0,1) (seed 42) and requires "
        "R(program(x), program(r(x))) to be True for EVERY sample. The MR "
        "passes iff all 30 checks hold. Design r as an input transform tied "
        "to a conservation-type invariant of THIS program, and R as the "
        "(tolerance) relation between the two outputs that the invariant "
        "implies for the ORIGINAL program. A conservation-eroding defect "
        "should make R fail."),
    2: ("The harness draws 50 samples x ~ Uniform(0,1) (seed 42) and computes "
        "diff = program(r(x)) - program(x); the sample contributes diff when "
        "R(y_orig, y_new) is True, else -|diff|. The MR passes iff a "
        "one-sided Wilcoxon signed-rank test (alternative='greater') on these "
        "values is significant at alpha=0.05 (all-zero diffs also pass, "
        "degenerately). So r must move inputs so that the ORIGINAL program's "
        "output systematically INCREASES; R gates per-sample validity "
        "(return False for invalid/non-finite pairs)."),
    3: ("At run time the harness ignores r and R: it computes "
        "err(h) = |program(h) - 1.0| on the grid h in {0.1, 0.05, 0.025, "
        "0.0125} and passes iff the log-log regression slope is within "
        "2.0 +/- 0.2 (second-order convergence toward reference value 1.0). "
        "Still provide (r, R) documenting the refinement relation (e.g. "
        "r(h) = h/2) and the expected error-contraction bound; they are "
        "consumed by the equivalence-coherence channel."),
    4: ("The harness uses r only: it draws 10 samples x ~ Uniform(0,1) "
        "(seed 42) and passes iff mean |program(r(x)) - program(x)| <= 1e-6, "
        "i.e. r must be an EXACTLY output-preserving input transform for the "
        "ORIGINAL program (to 1e-6). Prefer a non-identity transform that "
        "exploits a genuine invariance of the computation if one exists; "
        "identity is admissible only as a last resort. R documents the "
        "intended trajectory-similarity relation."),
    5: ("Same harness as MP2 (one-sided Wilcoxon 'greater' over 50 seeded "
        "samples of diff = program(r(x)) - program(x), R gating validity): "
        "design r to move inputs toward the asymptotic regime in which the "
        "ORIGINAL program's output systematically INCREASES (an asymptotic "
        "ordering the program should respect)."),
}

MR_PROMPT_TEMPLATE = """You are an expert in metamorphic testing of scientific computing software. Design ONE metamorphic relation (MR) for the program below, targeting EXACTLY the named meta-pattern.

PUT NAME: {put_name}
META-PATTERN: MP{mp_index} ({mp_name})
VERIFIER CONTRACT (the exact harness that will evaluate this MR): {contract}

ATTEMPT INDEX: {attempt_idx} of {n_attempts}  (different seed; same meta-pattern; produce a STRUCTURALLY DIFFERENT relation from prior attempts)

━━━ ORIGINAL PROGRAM ━━━
```python
{original_code}
```

INSTRUCTIONS:
- Output ONLY one ```python``` block defining exactly two top-level functions:
    def r(x): ...              # input transform; maps the valid input domain into itself
    def R(y_orig, y_new): ...  # output relation verifier; returns a bool
- The relation MUST HOLD for the ORIGINAL program under the stated harness (it is discarded otherwise).
- The relation SHOULD be violated by plausible semantic defects of the targeted meta-pattern kind (that is what makes it a useful checker).
- Allowed imports: math, numpy as np. No other imports, no I/O, no randomness, no side effects.
- Do not explain or comment.
"""
MR_PROMPT_SHA256 = hashlib.sha256(MR_PROMPT_TEMPLATE.encode()).hexdigest()


def _strip_fences(text: str) -> str:
    """Same parser as scripts/cross_source_campaign.py::_strip_fences."""
    m = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _env_any(*names: str) -> str | None:
    for n in names:
        for cand in (n, n.upper(), n.lower()):
            v = os.environ.get(cand)
            if v:
                return v
    return None


def _norm_base(url: str) -> str:
    """OpenAI client appends /chat/completions; ensure the /v1 suffix."""
    url = url.rstrip("/")
    return url if url.endswith("/v1") else url + "/v1"


def _resolve_set(set_id: int) -> dict:
    cfg = SET_DEFAULTS[set_id]
    model = os.environ.get(cfg["model_env"]) or cfg["model"]
    for fam in V4_SOURCES:
        assert fam not in model.lower(), (
            f"held-out model {model!r} collapses to v4 family {fam!r} — forbidden")
    key = _env_any(*cfg["key_envs"])
    base = _env_any("V5_MR_BASE_URL", "base_url", "BLTCY_BASE_URL")
    return {"set": set_id, "model": model, "key": key,
            "base_url": _norm_base(base) if base else None,
            "family": cfg["family"]}


class _Timeout(Exception):
    pass


def _alarm(signum, frame):  # noqa: ARG001
    raise _Timeout()


def _load_put(put: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        f"put_{put}", ROOT / f"src/p2/puts/{put}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.program


def _compile_mr(code: str):
    """Compile candidate MR code in a namespace offering math/numpy only."""
    import numpy as np
    banned = re.findall(r"^\s*(?:import|from)\s+(?!math|numpy)(\w+)",
                        code, re.MULTILINE)
    if banned:
        raise ValueError(f"disallowed import(s): {banned}")
    ns: dict = {"math": math, "np": __import__("numpy"), "numpy": np}
    exec(compile(code, "<v5-mr>", "exec"), ns)  # noqa: S102
    r, R = ns.get("r"), ns.get("R")
    if not (callable(r) and callable(R)):
        raise ValueError("must define callables r and R")
    return r, R


def prescreen(put: str, mp_k: int, code: str, orig_fn) -> tuple[bool, str]:
    """Ex-ante instrument check; sees only the ORIGINAL program."""
    from p2.avp.dispatcher import call_avp
    from p2.avp.interface import MR, AVPResult

    if len(code) > ARTIFACT_ENVELOPE_CHARS:
        # deliverable-budget guard: keeps the winning artifact within the
        # v4 800-token envelope even though MAX_TOKENS covers reasoning
        return False, f"ARTIFACT_OVER_ENVELOPE {len(code)}>{ARTIFACT_ENVELOPE_CHARS}"
    try:
        r, R = _compile_mr(code)
    except Exception as e:  # noqa: BLE001
        return False, f"COMPILE_FAIL {str(e)[:120]}"

    lo = 1e-9 if put == "a3" else 0.0
    try:
        for x in (0.1, 0.3, 0.5, 0.7, 0.9):
            rx = float(r(x))
            if not (math.isfinite(rx) and lo <= rx <= 1.0):
                return False, f"DOMAIN_FAIL r({x})={rx!r}"
        y0 = float(orig_fn(0.5))
        y1 = float(orig_fn(float(r(0.5))))
        out = R(y0, y1)
        if not isinstance(out, (bool,)) and not hasattr(out, "__bool__"):
            return False, "R_NOT_BOOL"
        bool(out)
    except Exception as e:  # noqa: BLE001
        return False, f"PROBE_FAIL {str(e)[:120]}"

    mr = MR(r=r, R=R, mp_index=mp_k, name=f"{put.upper()}_mp{mp_k}_v5")
    try:
        verdict = call_avp(orig_fn, mr, EPSILON_AVP)
    except Exception as e:  # noqa: BLE001
        return False, f"AVP_ERROR {str(e)[:120]}"
    if verdict != AVPResult.PASS:
        return False, "AVP_ORIG_FAIL"
    return True, "OK"


def generate_all(sets: list[int], slots: list[tuple[str, int]], workers: int) -> None:
    """Dispatch all LLM calls (K candidates per slot per set), archive raw."""
    from openai import OpenAI

    raw_dir = OUT_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    put_src = {p: (ROOT / f"src/p2/puts/{p}.py").read_text() for p in PUTS}

    clients = {}
    for s in sets:
        cfg = _resolve_set(s)
        assert cfg["key"] and cfg["base_url"], f"set {s}: missing key/base_url"
        clients[s] = (OpenAI(api_key=cfg["key"], base_url=cfg["base_url"],
                             timeout=360.0, max_retries=2), cfg["model"])

    tasks = []
    for s in sets:
        for put, mp_k in slots:
            for a in range(1, K_CANDIDATES + 1):
                tasks.append((s, put, mp_k, a))

    def _one(task):
        s, put, mp_k, a = task
        raw_path = raw_dir / f"set{s}_{put}_mp{mp_k}_a{a}.json"
        if raw_path.exists():
            return "cached"
        client, model = clients[s]
        prompt = MR_PROMPT_TEMPLATE.format(
            put_name=put.upper(), mp_index=mp_k, mp_name=MP_NAMES[mp_k],
            contract=MP_CONTRACTS[mp_k], attempt_idx=a,
            n_attempts=K_CANDIDATES, original_code=put_src[put])
        last_err = None
        for retry in range(3):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
                content = resp.choices[0].message.content or ""
                raw_path.write_text(json.dumps({
                    "set": s, "put": put, "mp": mp_k, "attempt": a,
                    "model": model, "content": content,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }))
                return "ok"
            except Exception as e:  # noqa: BLE001
                last_err = e
                time.sleep(4 * (2 ** retry))
        raw_path.write_text(json.dumps({
            "set": s, "put": put, "mp": mp_k, "attempt": a,
            "model": clients[s][1], "content": None, "api_error": str(last_err),
        }))
        return "api_fail"

    counts = {"ok": 0, "cached": 0, "api_fail": 0}
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_one, t) for t in tasks]
        for fut in as_completed(futs):
            counts[fut.result()] += 1
            done += 1
            if done % 30 == 0:
                print(f"  MR generation {done}/{len(tasks)} {counts}", flush=True)
    print(f"  MR generation complete: {counts}", flush=True)


def screen_all(sets: list[int], slots: list[tuple[str, int]]) -> dict:
    raw_dir = OUT_DIR / "raw"
    funnel = {
        "seed": BASE_SEED,
        "k_candidates": K_CANDIDATES,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "prompt_sha256": MR_PROMPT_SHA256,
        "parser": V4_PARSER,
        "prescreen": "compile+imports(math,numpy) -> domain probes -> AVP(original)==PASS (kill-blind)",
        "sets": {},
        "slots": [],
    }
    for s in sets:
        cfg = _resolve_set(s)
        funnel["sets"][str(s)] = {"model": cfg["model"], "family": cfg["family"]}

    orig_cache = {}
    for s in sets:
        set_dir = OUT_DIR / f"set{s}"
        set_dir.mkdir(parents=True, exist_ok=True)
        manifest = []
        for put, mp_k in slots:
            if put not in orig_cache:
                orig_cache[put] = _load_put(put)
            orig_fn = orig_cache[put]
            slot_rec = {"set": s, "put": put, "mp": mp_k, "attempts": [],
                        "winner": None}
            for a in range(1, K_CANDIDATES + 1):
                raw_path = raw_dir / f"set{s}_{put}_mp{mp_k}_a{a}.json"
                if not raw_path.exists():
                    slot_rec["attempts"].append({"a": a, "status": "RAW_MISSING"})
                    continue
                raw = json.loads(raw_path.read_text())
                if raw.get("content") is None:
                    slot_rec["attempts"].append(
                        {"a": a, "status": f"API_FAIL {str(raw.get('api_error'))[:80]}"})
                    continue
                code = _strip_fences(raw["content"])
                if not code:
                    slot_rec["attempts"].append({"a": a, "status": "PARSE_EMPTY"})
                    continue
                signal.signal(signal.SIGALRM, _alarm)
                signal.alarm(PRESCREEN_TIMEOUT_S)
                try:
                    ok, why = prescreen(put, mp_k, code, orig_fn)
                except _Timeout:
                    ok, why = False, f"TIMEOUT>{PRESCREEN_TIMEOUT_S}s"
                finally:
                    signal.alarm(0)
                slot_rec["attempts"].append({"a": a, "status": why})
                if ok:
                    mr_path = set_dir / f"{put}_mp{mp_k}.py"
                    header = (f'"""v5 held-out MR — set {s} '
                              f'({funnel["sets"][str(s)]["model"]}), '
                              f'{put} MP{mp_k}, candidate {a}/{K_CANDIDATES}."""\n')
                    mr_path.write_text(header + code + "\n")
                    slot_rec["winner"] = {
                        "attempt": a,
                        "sha256": hashlib.sha256(code.encode()).hexdigest(),
                        "path": str(mr_path.relative_to(ROOT)),
                    }
                    manifest.append({"put": put, "mp": mp_k, **slot_rec["winner"]})
                    break
            funnel["slots"].append(slot_rec)
            status = "OK" if slot_rec["winner"] else "EMPTY"
            print(f"  set{s} {put} MP{mp_k}: {status} "
                  f"({[x['status'][:28] for x in slot_rec['attempts']]})", flush=True)
        (set_dir / "manifest.json").write_text(json.dumps({
            "set": s, **funnel["sets"][str(s)], "n_slots_won": len(manifest),
            "mrs": manifest}, indent=2))
    return funnel


def write_symmetry_md(funnel: dict | None, sets: list[int]) -> None:
    filled = funnel is not None and funnel.get("slots")
    set_cfgs = {s: _resolve_set(s) for s in sets}
    won = {s: 0 for s in sets}
    tot = {s: 0 for s in sets}
    if filled:
        for rec in funnel["slots"]:
            tot[rec["set"]] += 1
            if rec["winner"]:
                won[rec["set"]] += 1
    st = "✅" if filled else "⬜ pending"
    lines = [
        "# MR_SOURCE_SYMMETRY — EXP-DIS held-out provider checklist",
        "",
        f"Seed: `{BASE_SEED}`. v4 sources (FORBIDDEN for held-out): {', '.join(V4_SOURCES)}.",
        f"Design: s = 2 held-out MR-set replicates from two distinct non-v4 families "
        f"(strengthens the provider-singularity answer, power_report.md §3).",
        "",
        "## Selected providers (author-directed preference + deliverability probes, 2026-07-29)",
        "",
        "Author instruction (2026-07-29): prioritise gpt-5.5 / gemini-3.5-flash / "
        "grok-4.5 / deepseek-v4-flash / glm-5.2 / qwen3.7-plus / minimax-m2.7. "
        "Filtered by (a) the frozen held-out family constraint (NOT Claude/GPT/"
        "DeepSeek → gpt-5.5, deepseek-v4-flash ineligible for the MR arm) and "
        "(b) deliverability probes (MAX_TOKENS=16000, temperature 0.7): "
        "gemini-3.5-flash finish=stop ✓; grok-4.5 finish=stop ✓; glm-5.2 "
        "finish=length/empty ✗; qwen3.7-plus finish=length ✗; minimax-m2.7 "
        "finish=length/no fenced block ✗. Earlier 800-token probes (gemini-2.5 "
        "family, glm-4.7, qwen3-235b, kimi, minimax-m2.5) are archived in git "
        "history; the prior partial run (qwen3-235b + glm-4.7) is preserved "
        "under `data/v5/mrs/raw_prior_run_qwen_glm/`.",
        "",
        "| Set | Family | Model | Credential | Slots won |",
        "|---|---|---|---|---|",
    ]
    for s in sets:
        cfg = set_cfgs[s]
        cred = ("api_key_1 (shared with generation arm; family-level held-out-ness "
                "is the operative criterion, noted for transparency)")
        lines.append(f"| {s} | {cfg['family']} | `{cfg['model']}` | {cred} | "
                     f"{won[s]}/{tot[s] if filled else 60} |")
    lines += [
        "",
        "## 7-item symmetry checklist",
        "",
        "| # | Item | v4 value | v5 held-out value | Status |",
        "|---|---|---|---|---|",
        f"| 1 | Prompt text | SHA-256 `{V4_PROMPT_SHA256}` (cross_source_campaign.PROMPT_TEMPLATE; v4 had no MR-generation arm) | ONE fixed template shared verbatim by both sets and all slots, v4-matched structure/parameters; SHA-256 `{MR_PROMPT_SHA256}` | {st} |",
        f"| 2 | Parser version | `{V4_PARSER}` | same function (replicated verbatim) | {st} |",
        f"| 3 | Temperature | `0.7` | `{TEMPERATURE}` | {st} |",
        f"| 4 | Candidate count / K trials | K=`3` per (op, source) | K=`{K_CANDIDATES}` per (PUT, MP, set) slot | {st} |",
        f"| 5 | Repair / retry budget | no auto-repair beyond K attempts | none beyond K candidates (first prescreen pass wins) | {st} |",
        f"| 6 | Max tokens | `800` (cross_source_campaign._generate_one; non-thinking output budget) | `{MAX_TOKENS}` total to cover the reasoning channel of 2026-generation models (author-directed preference; mechanical 800 yields finish=length with NO artifact — probe evidence above); **deliverable budget enforced in prescreen: artifact ≤ {ARTIFACT_ENVELOPE_CHARS} chars ≈ v4's 800-token envelope** | {st} deviation-documented |",
        f"| 7 | Provider identity | Claude / GPT / DeepSeek | set1 `{set_cfgs[1]['model'] if 1 in set_cfgs else '-'}`, set2 `{set_cfgs[2]['model'] if 2 in set_cfgs else '-'}` — both non-v4 families | {st} |",
        "",
        "## Prescreen (ex-ante, kill-blind)",
        "",
        "1. Compiles; defines callables `r`, `R`; imports restricted to math/numpy.",
        "2. Domain safety: `r` maps probes {0.1,0.3,0.5,0.7,0.9} to finite values in [0,1] ((0,1] for a3); `R` returns bool on a probe output pair.",
        "3. Instrument validity: `AVP(original, mr) == PASS` under the frozen v4 dispatcher (epsilon 1e-6). An MR that fails on the original can never kill (kill requires original PASS), so it is a broken instrument, not evidence.",
        "4. First passing candidate wins; K=3 exhausted -> slot EMPTY, recorded; the affected (cell, condition) is excluded + logged downstream (never imputed, never treated as observed zero).",
        "",
        f"MR prompt template SHA-256: `{MR_PROMPT_SHA256}` (fixed before any kill execution; kill matrices run only after this file + funnel are committed).",
        "",
        f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"Wrote {OUT_MD}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-check", action="store_true")
    ap.add_argument("--sets", type=str, default="1,2")
    ap.add_argument("--slots", type=str, default=None,
                    help="comma-separated put:mp subset, e.g. a1:1,b3:2 (smoke)")
    ap.add_argument("--skip-generation", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    sets = [int(x) for x in args.sets.split(",")]
    slots = [(p, k) for p in PUTS for k in MPS]
    if args.slots:
        want = {(x.split(":")[0], int(x.split(":")[1]))
                for x in args.slots.split(",")}
        slots = [sl for sl in slots if sl in want]
        assert slots

    missing = []
    for s in sets:
        cfg = _resolve_set(s)
        if not cfg["key"]:
            missing.append(f"set{s} key ({SET_DEFAULTS[s]['key_envs']})")
        if not cfg["base_url"]:
            missing.append("base_url")
    if args.dry_check or missing:
        print("v5 held-out MR generation — dry check")
        for s in sets:
            cfg = _resolve_set(s)
            print(f"  set {s}: family={cfg['family']} model={cfg['model']} "
                  f"key={'OK' if cfg['key'] else 'MISSING'}")
        print(f"  slots: {len(slots)} × {K_CANDIDATES} candidates × {len(sets)} sets")
        print(f"  MR prompt SHA-256: {MR_PROMPT_SHA256}")
        if missing:
            print(f"BLOCKED: missing {missing}")
            write_symmetry_md(None, sets)
            sys.exit(2)
        sys.exit(0)

    print(f"v5 MR generation: {len(slots)} slots × {len(sets)} sets, "
          f"K={K_CANDIDATES}", flush=True)
    if not args.skip_generation:
        generate_all(sets, slots, args.workers)
    funnel = screen_all(sets, slots)
    funnel["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    OUT_FUNNEL.write_text(json.dumps(funnel, indent=2))
    print(f"Wrote {OUT_FUNNEL}")
    if len(slots) == 60 and sets == [1, 2]:
        write_symmetry_md(funnel, sets)


if __name__ == "__main__":
    main()
