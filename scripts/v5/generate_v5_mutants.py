#!/usr/bin/env python3
"""POOL-SEM v5 mutant generation (EXP-CON / Task 2.1) — live pipeline.

Frozen design constants (prereg v2, hypotheses.md §2 / power_report.md §9):
  - 51 applicable cells (applicability_matrix.md §3, hardcoded with provenance)
  - density target 16 confirmed non-equivalent / cell
  - attempts budget ceil(16*1.117) = 18 LLM calls / cell (all dispatched;
    the pool keeps the first 16 confirmed in attempt order)
  - prompt = v4 cross_source_campaign.PROMPT_TEMPLATE verbatim
    (SHA-256 asserted at startup against GENERATION_LEDGER value)
  - temperature 0.7; parser = v4 _strip_fences; max_tokens 800
  - confirmation = E1∧E2 non-equivalence (E2: K_eq=1000 uniform[0,1] seed-42
    samples, eps 1e-6; E1: AVP coherence over the PUT's five hand-coded MRs)
    — the same judgement procedure as the v4 SMS campaign (scripts/
    sms_campaign.py constants), applied per mutant with the full 5-MP MR set.

Funnel stages recorded per cell (SSOT key `funnel_v5`):
  attempts -> parse (fenced code extracted) -> build (V1 syntax + V2
  executable + V4 signature) -> trigger (V3 non-trivial on probe grid)
  -> E1∧E2 non-equivalent -> confirmed (non-equivalent, deduplicated,
  first 16 by attempt order) -> certificate (archived to pool + manifest).

Generator engineering failures (API errors, timeouts) stay in the funnel as
attrition and are NEVER recoded (F-5a). No LLM output is ever fabricated.

Required env (fail-fast if missing):
  BLTCY_API_KEY / BLTCY_BASE_URL — or cloud-agent secret aliases
  api_key_1 / base_url (any case; cloud injection uppercases names).
  V5_GENERATOR_MODEL optional (default gpt-4o).

Usage:
  PYTHONPATH=src .venv/bin/python scripts/v5/generate_v5_mutants.py
  PYTHONPATH=src .venv/bin/python scripts/v5/generate_v5_mutants.py --dry-check
  ... --cells CE:a1,OS:b2      # restricted smoke subset
  ... --skip-generation        # revalidate existing raw candidates only
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
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

OUT_POOL = ROOT / "data" / "v5" / "pools"
OUT_RAW = ROOT / "data" / "v5" / "raw_candidates"
OUT_FUNNEL = ROOT / "data" / "v5" / "funnel_v5.json"
LEDGER = ROOT / "data" / "v5" / "GENERATION_LEDGER.md"
BASE_SEED = 20260728
TARGET_CONFIRMED = 16
ATTEMPTS_BUDGET = math.ceil(TARGET_CONFIRMED * 1.117)  # 18
TEMPERATURE = 0.7
MAX_TOKENS = 800
K_EQ = 1000          # E2 sample count (v4 sms_campaign convention)
EPSILON_EQ = 1e-6
EPSILON_AVP = 1e-6
STAGE_TIMEOUT_S = 300  # per-candidate validation/confirmation wall clock

# Provenance: applicability_matrix.md §3 PUT-level table (✓ cells only).
# n_app = CE9+OS12+HP11+TF9+SI10 = 51. Frozen at prereg-v2-freeze.
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

# Alignment map (applicability_matrix.md §7): generation-time eff stratum.
ALIGNED_MP = {"CE": 1, "OS": 2, "HP": 3, "TF": 4, "SI": 5}

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
LEDGER_PROMPT_SHA = "06fa552d7431cecc00120bddeb4e8cdc4511ce03f695139809b5af83508a3e90"
assert PROMPT_SHA256 == LEDGER_PROMPT_SHA, "prompt drifted from ledger SHA"

REQUIRED_ENV = ("BLTCY_API_KEY", "BLTCY_BASE_URL")

# Cloud-agent secret-name adapter (author's dashboard names, 2026-07-29):
#   base_url -> BLTCY_BASE_URL, api_key_1 -> BLTCY_API_KEY (generation arm).
# Cloud injection uppercases secret names, so case variants are accepted.
# Explicit BLTCY_* names take precedence when both are set.
_ENV_FALLBACKS = {"BLTCY_API_KEY": "api_key_1", "BLTCY_BASE_URL": "base_url"}
for _canon, _alt in _ENV_FALLBACKS.items():
    if not os.environ.get(_canon):
        for _cand in (_alt, _alt.upper(), _alt.lower()):
            if os.environ.get(_cand):
                os.environ[_canon] = os.environ[_cand]
                break


def _norm_base(url: str) -> str:
    """OpenAI client appends /chat/completions; ensure the /v1 suffix."""
    url = url.rstrip("/")
    return url if url.endswith("/v1") else url + "/v1"

# ---------------------------------------------------------------------------
# Operator descriptors for the 15 applicable-but-never-attempted combos
# (applicability_matrix.md §5). Site wording follows matrix §3 (arbitrated),
# with implicit invariants stated explicitly per hypotheses.md §4 discipline
# (e.g. c2 odd-symmetry). Descriptors are ex-ante design text, written before
# any v5 kill data exists.
# ---------------------------------------------------------------------------
_NEVER_ATTEMPTED: dict[tuple[str, str], dict] = {
    ("CE", "c2"): dict(
        label="target odd-symmetry erosion",
        target_locator="training-target construction `_y_train = np.tanh(_t_train.ravel())`",
        transformation="apply a type-preserving edit that erodes the odd symmetry of the "
                       "training targets (e.g. add a small constant offset to _y_train, or "
                       "replace tanh with a non-odd variant such as tanh(t)+c)",
        rationale="implicit invariant stated explicitly: tanh oddness plus the symmetric "
                  "input map t=4x-2 induce the conservation relation f(x)+f(1-x)=0, which "
                  "the symmetric degree-5 fit approximately maintains; eroding target "
                  "symmetry breaks this conserved quantity (CE failure semantics)",
    ),
    ("OS", "b2"): dict(
        label="acceptance rule swap",
        target_locator="Metropolis-Hastings acceptance step comparing the log-uniform "
                       "draw with the acceptance log-ratio",
        transformation="substitute the acceptance rule so it no longer implements "
                       "detailed balance, e.g. flip the comparison direction (accept when "
                       "the log-uniform draw EXCEEDS the log-ratio), or negate the "
                       "log-ratio in the comparison, or swap the roles of current and "
                       "proposed log-densities in the ratio",
        rationale="acceptance-rule substitution is a classic MCMC implementation slip "
                  "(OS failure semantics on the acceptance site); note '<' vs '<=' is a "
                  "measure-zero non-change and does not qualify",
    ),
    ("OS", "c1"): dict(
        label="input-map arithmetic swap",
        target_locator="input map `6*x - 3` (or kernel additive composition) in the GPR wrapper",
        transformation="substitute one arithmetic operator in the input map, e.g. "
                       "`6*x - 3` -> `6*x + 3`, or swap `+` for `*` in the kernel composition",
        rationale="sign/operator substitution in coordinate mapping is a plausible "
                  "scientist mistake (OS failure semantics)",
    ),
    ("OS", "c3"): dict(
        label="sigmoid input-map swap",
        target_locator="sigmoid target / input map arithmetic in the NN-surrogate wrapper",
        transformation="substitute one arithmetic operator in the input or target map "
                       "(e.g. flip a sign inside the sigmoid argument)",
        rationale="operator substitution in feature/target construction (OS semantics)",
    ),
    ("OS", "d1"): dict(
        label="label-rule comparison swap",
        target_locator="training label rule `> 0` in the MLP-classifier wrapper",
        transformation="substitute the comparison operator in the label rule "
                       "(e.g. `> 0` -> `>= 0.1` or `< 0`)",
        rationale="decision-boundary comparison substitution (OS failure semantics)",
    ),
    ("OS", "d3"): dict(
        label="label-rule coefficient-sign swap",
        target_locator="training label rule `0.8*x1 - 0.6*x2 > 0` in the logistic-regression wrapper",
        transformation="substitute one operator in the label rule, e.g. `-` -> `+` "
                       "(0.8*x1 + 0.6*x2 > 0) or flip the inequality direction",
        rationale="sign substitution in a linear decision rule (OS failure semantics)",
    ),
    ("HP", "a3"): dict(
        label="stability-ratio loosening",
        target_locator="stability ratio constant `_R_STAB` (or the grid-spacing floor) in the FDM wrapper",
        transformation="change the stability ratio to a nearby but wrong value "
                       "(e.g. 0.5 -> 0.55) or loosen the h-floor",
        rationale="explicit-FDM stability requires r = alpha*dt/dx^2 <= 0.5 (implicit "
                  "invariant stated explicitly); a slightly-too-large ratio degrades "
                  "convergence order without immediate blow-up (HP failure semantics)",
    ),
    ("HP", "b3"): dict(
        label="MC sample-count reduction",
        target_locator="module-level `_N_SAMPLES` constant of the Monte-Carlo integrator",
        transformation="reduce _N_SAMPLES from 5000 to a much smaller value (e.g. 50)",
        rationale="sample-budget hyperparameter typo inflates MC error while remaining "
                  "runnable (HP failure semantics)",
    ),
    ("TF", "a1"): dict(
        label="state-vector ordering flip",
        target_locator="Lorenz RHS state unpacking / initial-condition vector ordering (y and z components)",
        transformation="swap the ordering of the y and z state components in the RHS "
                       "(trajectory-structure corruption, NOT a parameter change)",
        rationale="state-ordering confusion corrupts the trajectory structure while "
                  "preserving types and signature (TF failure semantics)",
    ),
    ("TF", "a3"): dict(
        label="time-step loop reorder",
        target_locator="ordered time-stepping loop of the explicit FDM solver",
        transformation="corrupt the ordered update sequence, e.g. update from the "
                       "previous-previous step or skip every other time step "
                       "(sequence corruption, not a coefficient change)",
        rationale="trajectory/sequence-order corruption of the time march (TF semantics)",
    ),
    ("TF", "b2"): dict(
        label="chain segment reorder",
        target_locator="MH chain accumulation and warm-up boundary in the MCMC wrapper",
        transformation="corrupt the chain's temporal structure, e.g. include warm-up "
                       "samples in the averaged segment or reverse a chain segment "
                       "before averaging",
        rationale="warm-up/segment boundary confusion corrupts the trajectory the "
                  "estimator averages over (TF failure semantics)",
    ),
    ("SI", "c1"): dict(
        label="kernel length-scale fidelity tier",
        target_locator="GPR kernel construction (RBF length_scale / WhiteKernel prior scale)",
        transformation="replace the kernel prior with a systematically lower-fidelity "
                       "tier (e.g. fix length_scale to a large constant, or drop the "
                       "tuned prior scale), an ordered structural downgrade",
        rationale="structural fidelity-tier degradation of the surrogate prior "
                  "(SI failure semantics: ordered domination, not a random tweak)",
    ),
    ("SI", "c2"): dict(
        label="polynomial degree tier",
        target_locator="PolynomialFeatures(5, ...) degree in the PCE wrapper",
        transformation="replace degree 5 with a structurally lower tier (e.g. 2), an "
                       "ordered fidelity downgrade of the expansion",
        rationale="expansion-order fidelity tier (SI failure semantics: the lower tier "
                  "is systematically dominated on the smooth tanh target)",
    ),
    ("SI", "c3"): dict(
        label="architecture fidelity tier",
        target_locator="MLPRegressor hidden_layer_sizes in the NN-surrogate wrapper",
        transformation="replace the hidden architecture with a strictly lower-capacity "
                       "tier (e.g. a single tiny hidden layer)",
        rationale="capacity fidelity tier (SI failure semantics: ordered structural downgrade)",
    ),
    ("SI", "d2"): dict(
        label="kernel family tier",
        target_locator="SVC kernel specification (kernel='rbf') in the SVM wrapper",
        transformation="replace the RBF kernel with the structurally lower tier "
                       "kernel='linear' (fidelity-ladder downgrade for the circular "
                       "decision boundary)",
        rationale="kernel-family fidelity tier: a linear kernel cannot represent the "
                  "circular boundary, giving ordered domination (SI failure semantics)",
    ),
}


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


class _Timeout(Exception):
    pass


def _alarm_handler(signum, frame):  # noqa: ARG001
    raise _Timeout()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_mutant_program(code: str):
    ns: dict = {}
    exec(compile(code, "<v5-mutant>", "exec"), ns)  # noqa: S102
    fn = ns.get("program")
    if fn is None or not callable(fn):
        raise ValueError("no callable `program`")
    return fn


def _hand_mr_set(put: str):
    """The PUT's five hand-coded MRs (E1 coherence set; v4 infrastructure)."""
    from p2.avp.interface import MR
    mod = _load_module(f"mrs_{put}", ROOT / "src" / "p2" / "mrs" / f"{put}.py")
    mrs = []
    for k in (1, 2, 3, 4, 5):
        mrs.append(MR(r=getattr(mod, f"r_mp{k}"), R=getattr(mod, f"R_mp{k}"),
                      mp_index=k, name=f"{put.upper()}_mp{k}"))
    return mrs


def _cell_descriptors(op_name: str, put: str) -> list:
    """Registry operators for (category, put); curated descriptor otherwise."""
    from p2.mutators.operator_registry import OPERATORS

    class _Op:
        pass

    ops = [o for o in OPERATORS if o.category == op_name and o.put == put]
    if ops:
        return ops
    spec = _NEVER_ATTEMPTED.get((op_name, put))
    assert spec is not None, f"no descriptor for never-attempted cell {op_name}x{put}"
    o = _Op()
    o.id = f"{put}_{op_name}1v5"
    o.put = put
    o.category = op_name
    o.label = spec["label"]
    o.target_locator = spec["target_locator"]
    o.transformation = spec["transformation"]
    o.rationale = spec["rationale"]
    return [o]


def _empty_funnel(cells: list[tuple[str, str]]) -> dict:
    rows = []
    for op, put in cells:
        rows.append({
            "cell": f"{op}×{put}",
            "op": op,
            "put": put,
            "n_attempts": 0,
            "n_parse_ok": 0,
            "n_build_ok": 0,
            "n_trigger_ok": 0,
            "n_e1_and_e2_nonequiv": 0,
            "n_duplicate": 0,
            "n_confirmed_nonequiv": 0,
            "n_certificate": 0,
            "attrition_log": [],
        })
    return {
        "n_app": 51,
        "cells_in_run": len(cells),
        "target_confirmed_per_cell": TARGET_CONFIRMED,
        "attempts_budget_per_cell": ATTEMPTS_BUDGET,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "prompt_sha256": PROMPT_SHA256,
        "seed": BASE_SEED,
        "equiv_judgement": {
            "procedure": "E1(AVP coherence, 5 hand-coded MRs) AND E2(K_eq=1000 uniform[0,1] seed 42, eps 1e-6)",
            "nonequiv": "NOT equivalent (fails E2 output equality on any sample OR fails E1 AVP coherence on any MR)",
            "source": "p2.equiv.judge.is_equivalent semantics; constants = scripts/sms_campaign.py",
        },
        "status": "PENDING",
        "cells": rows,
        "stage_totals": {
            "attempts": 0, "parse": 0, "build": 0,
            "trigger": 0, "e1_and_e2": 0, "certificate": 0,
        },
    }


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


# ---------------------------------------------------------------------------
# Stage 1: LLM generation (parallel over all (cell, attempt) tasks)
# ---------------------------------------------------------------------------
def generate_candidates(cells: list[tuple[str, str]], model: str, workers: int) -> None:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["BLTCY_API_KEY"],
                    base_url=_norm_base(os.environ["BLTCY_BASE_URL"]),
                    timeout=180.0, max_retries=2)

    put_sources = {put: (ROOT / f"src/p2/puts/{put}.py").read_text()
                   for put in sorted({p for _, p in cells})}

    tasks = []
    for op_name, put in cells:
        ops = _cell_descriptors(op_name, put)
        for attempt in range(1, ATTEMPTS_BUDGET + 1):
            op = ops[(attempt - 1) % len(ops)]
            base_tf = getattr(op, "transformation", op_name)
            cycle = (attempt - 1) // len(ops)
            # The frozen template demands a STRUCTURALLY DIFFERENT mutant per
            # attempt while instructing "apply the transformation EXACTLY as
            # specified"; the field input (not the template) therefore carries
            # the attempt-specific instantiation. Guards the duplicated-edit
            # failure mode (power_report.md §4, b3 precedent); exact-SHA dedup
            # still enforces distinctness downstream.
            nontrivial_note = ("the edit must change program output by more than "
                               "1e-6 for at least one x in [0,1]; no-op or "
                               "measure-zero edits (such as '<' vs '<=') do not count")
            if cycle == 0:
                transformation = f"{base_tf} ({nontrivial_note})"
            else:
                transformation = (
                    f"operator class: {base_tf}\n"
                    f"EXACT CHANGE FOR THIS ATTEMPT (reuse #{cycle} of this spec): "
                    f"realize the SAME operator class as a concrete edit that DIFFERS "
                    f"from every earlier attempt — for numeric-constant edits pick a "
                    f"clearly different wrong value (e.g. scale the perturbation by "
                    f"~{1.0 + 0.5 * cycle:.1f}x or flip its sign); for structural or "
                    f"comparison edits act on a different eligible code site or use a "
                    f"different substitution of the same class; never reproduce the "
                    f"exemplar or any prior attempt's exact change ({nontrivial_note})")
            prompt = PROMPT_TEMPLATE.format(
                put_name=put.upper(),
                op_id=getattr(op, "id", f"{put}_{op_name}1"),
                op_label=getattr(op, "label", op_name),
                target_locator=getattr(op, "target_locator", "wrapper site"),
                transformation=transformation,
                rationale=getattr(op, "rationale", ""),
                attempt_idx=attempt,
                n_attempts=ATTEMPTS_BUDGET,
                original_code=put_sources[put],
            )
            tasks.append((op_name, put, attempt, getattr(op, "id", ""), prompt))

    OUT_RAW.mkdir(parents=True, exist_ok=True)
    done = 0

    def _one(task):
        op_name, put, attempt, op_id, prompt = task
        raw_path = OUT_RAW / f"{put}_{op_name}_a{attempt:02d}.json"
        if raw_path.exists():
            return "cached"
        last_err = None
        for retry in range(3):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                )
                if isinstance(resp, str):
                    # proxy returned 200 with a bare JSON string (e.g. an
                    # upstream-saturation message) — treat as retryable
                    raise RuntimeError(f"proxy_string_response: {resp[:200]}")
                content = resp.choices[0].message.content or ""
                raw_path.write_text(json.dumps({
                    "cell": f"{op_name}×{put}", "attempt": attempt,
                    "op_id": op_id, "model": model,
                    "content": content,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }))
                return "ok"
            except Exception as e:  # noqa: BLE001
                last_err = e
                time.sleep(4 * (2 ** retry))
        raw_path.write_text(json.dumps({
            "cell": f"{op_name}×{put}", "attempt": attempt, "op_id": op_id,
            "model": model, "content": None, "api_error": str(last_err),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }))
        return "api_fail"

    counts = {"ok": 0, "cached": 0, "api_fail": 0}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_one, t) for t in tasks]
        for fut in as_completed(futs):
            counts[fut.result()] += 1
            done += 1
            if done % 50 == 0:
                print(f"  generation {done}/{len(tasks)} {counts}", flush=True)
    print(f"  generation complete: {counts}", flush=True)


# ---------------------------------------------------------------------------
# Stage 2: validation + E1∧E2 confirmation (sequential, attempt order)
# ---------------------------------------------------------------------------
def confirm_cell(op_name: str, put: str, rec: dict, funnel: dict, model: str) -> None:
    from p2.equiv.avp_coherent import judge_e1
    from p2.equiv.sampler import UniformSampler, sample_inputs
    from p2.mutators.validation import validate_mutant

    put_mod = _load_module(f"put_{put}", ROOT / f"src/p2/puts/{put}.py")
    orig_fn = put_mod.program
    mr_set = _hand_mr_set(put)
    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=42)
    samples = sample_inputs(sampler, K_EQ)
    orig_outputs = []
    for x in samples:
        x_in = x[0] if x.shape == (1,) else x
        orig_outputs.append(float(orig_fn(x_in)))

    def nonequiv(mut_fn) -> bool:
        """NOT is_equivalent: E2 output difference OR E1 AVP incoherence.

        Mirrors p2.equiv.output_equiv.judge_e2 numerics exactly (norm over
        flattened outputs; NaN comparisons follow the same v4 semantics),
        with cached original outputs for speed.
        """
        import numpy as np
        for i, x in enumerate(samples):
            x_in = x[0] if x.shape == (1,) else x
            y_mut = np.asarray(mut_fn(x_in)).flatten()
            if y_mut.shape != (1,):
                return True  # signature-breaking output shape -> differs
            if np.linalg.norm(np.array([orig_outputs[i]]) - y_mut) > EPSILON_EQ:
                return True  # fails E2 equality -> non-equivalent
        # outputs equal everywhere; equivalence additionally needs E1 coherence
        return not judge_e1(orig_fn, mut_fn, mr_set, EPSILON_AVP)

    cell = f"{op_name}×{put}"
    cell_dir = OUT_POOL / f"{put}_{op_name}"
    seen_hashes: set[str] = set()
    manifest: list[dict] = []
    confirmed = 0

    for attempt in range(1, ATTEMPTS_BUDGET + 1):
        raw_path = OUT_RAW / f"{put}_{op_name}_a{attempt:02d}.json"
        if not raw_path.exists():
            rec["attrition_log"].append(f"a{attempt:02d}: RAW_MISSING")
            continue
        raw = json.loads(raw_path.read_text())
        rec["n_attempts"] += 1
        funnel["stage_totals"]["attempts"] += 1
        if raw.get("content") is None:
            rec["attrition_log"].append(f"a{attempt:02d}: API_FAIL {raw.get('api_error','')[:100]}")
            continue
        code = _strip_fences(raw["content"])
        if not code:
            rec["attrition_log"].append(f"a{attempt:02d}: PARSE_EMPTY")
            continue
        rec["n_parse_ok"] += 1
        funnel["stage_totals"]["parse"] += 1

        signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(STAGE_TIMEOUT_S)
        try:
            v = validate_mutant(code, orig_fn)
            if not (v.syntax_ok and v.executable):
                rec["attrition_log"].append(f"a{attempt:02d}: BUILD_FAIL {v.error[:120]}")
                continue
            rec["n_build_ok"] += 1
            funnel["stage_totals"]["build"] += 1
            if not v.nontrivial:
                rec["attrition_log"].append(f"a{attempt:02d}: TRIVIAL (V3)")
                continue
            rec["n_trigger_ok"] += 1
            funnel["stage_totals"]["trigger"] += 1

            code_hash = hashlib.sha256(code.encode()).hexdigest()
            if code_hash in seen_hashes:
                rec["n_duplicate"] += 1
                rec["attrition_log"].append(f"a{attempt:02d}: DUPLICATE")
                continue
            seen_hashes.add(code_hash)

            mut_fn = _load_mutant_program(code)
            if not nonequiv(mut_fn):
                rec["attrition_log"].append(f"a{attempt:02d}: EQUIVALENT (E1∧E2)")
                continue
        except _Timeout:
            rec["attrition_log"].append(f"a{attempt:02d}: TIMEOUT>{STAGE_TIMEOUT_S}s")
            continue
        except Exception as e:  # noqa: BLE001
            rec["attrition_log"].append(f"a{attempt:02d}: EXEC_FAIL {str(e)[:120]}")
            continue
        finally:
            signal.alarm(0)

        rec["n_e1_and_e2_nonequiv"] += 1
        funnel["stage_totals"]["e1_and_e2"] += 1

        if confirmed >= TARGET_CONFIRMED:
            rec["attrition_log"].append(f"a{attempt:02d}: SURPLUS (pool full at {TARGET_CONFIRMED})")
            continue

        confirmed += 1
        mid = f"mut-{op_name}-{put.upper()}-{confirmed:02d}"
        cell_dir.mkdir(parents=True, exist_ok=True)
        (cell_dir / f"{mid}.py").write_text(code)
        manifest.append({
            "mutant_id": mid,
            "attempt_idx": attempt,
            "op_id": raw.get("op_id", ""),
            "model": model,
            "sha256": code_hash,
            "eff_stratum": ALIGNED_MP[op_name],
            "raw_relpath": str(raw_path.relative_to(ROOT)),
        })
        rec["n_confirmed_nonequiv"] += 1
        rec["n_certificate"] += 1
        funnel["stage_totals"]["certificate"] += 1

    if manifest:
        (cell_dir / "manifest.json").write_text(json.dumps({
            "cell": cell, "op": op_name, "put": put,
            "eff_stratum": ALIGNED_MP[op_name],
            "n_confirmed": confirmed,
            "mutants": manifest,
        }, indent=2))
    print(f"  {cell}: attempts={rec['n_attempts']} parse={rec['n_parse_ok']} "
          f"build={rec['n_build_ok']} trigger={rec['n_trigger_ok']} "
          f"nonequiv={rec['n_e1_and_e2_nonequiv']} confirmed={confirmed}", flush=True)


def update_ledger(funnel: dict, model: str) -> None:
    lines = [
        "# GENERATION_LEDGER — POOL-SEM v5 (Task 2.1)",
        "",
        f"Status: **{funnel['status']}** (live run; keys injected 2026-07-29).",
        "",
        "## Run configuration",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Generator script | `scripts/v5/generate_v5_mutants.py` |",
        "| Generator version | `v5.1.0-live` |",
        f"| Generator model | `{model}` |",
        f"| Base seed | `{BASE_SEED}` (nominal; provider sampling is not seed-reproducible, raw outputs archived under `data/v5/raw_candidates/`) |",
        "| Prompt source | `scripts/cross_source_campaign.py` `PROMPT_TEMPLATE` (verbatim) |",
        f"| Prompt SHA-256 | `{PROMPT_SHA256}` |",
        f"| Temperature | `{TEMPERATURE}` |",
        f"| Max tokens | `{MAX_TOKENS}` |",
        "| Parser | `cross_source_campaign._strip_fences` (replicated) |",
        "| n_app | `51` (applicability_matrix.md §3) |",
        f"| Target confirmed / cell | `{TARGET_CONFIRMED}` |",
        f"| Attempts budget / cell | `{ATTEMPTS_BUDGET}` (= ceil(16 × 1.117)) |",
        "| Confirmation | E1∧E2 non-equivalence: E2 K_eq=1000 uniform[0,1] seed 42 eps 1e-6; E1 AVP coherence over the PUT's 5 hand-coded MRs (v4 sms_campaign constants) |",
        "| Dedup | exact SHA-256 of parsed code within cell |",
        "| Mutant ID scheme | `mut-<OP>-<PUT>-<NN>` (NN = confirmed order) |",
        "| eff stratum labels | generation-time: CE→1 OS→2 HP→3 TF→4 SI→5 (ex-ante, applicability_matrix.md §7) |",
        "| Output pools | `data/v5/pools/` (+ per-cell `manifest.json`) |",
        "| Funnel SSOT | `data/v5/funnel_v5.json` (schema for `analysis_hcons.py`) |",
        "",
        "## Per-cell funnel (attempts → parse → build → trigger → E1∧E2 → confirmed)",
        "",
        "| cell | attempts | parse | build | trigger | E1∧E2 nonequiv | dup | confirmed | certificate |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in funnel["cells"]:
        lines.append(
            f"| {c['cell']} | {c['n_attempts']} | {c['n_parse_ok']} | {c['n_build_ok']} "
            f"| {c['n_trigger_ok']} | {c['n_e1_and_e2_nonequiv']} | {c['n_duplicate']} "
            f"| {c['n_confirmed_nonequiv']} | {c['n_certificate']} |")
    lines += [
        "",
        "## Held-out MR source (Task 2.2)",
        "",
        "See `data/v5/MR_SOURCE_SYMMETRY.md`.",
        "",
        "## Timestamps",
        "",
        "| Event | Time (UTC) |",
        "|---|---|",
        "| PASS-1 ledger template written | 2026-07-29 (phase-2 executor) |",
        f"| Live generation run | {funnel.get('completed_at', 'in progress')} |",
        "",
    ]
    LEDGER.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-check", action="store_true")
    ap.add_argument("--cells", type=str, default=None,
                    help="comma-separated OP:put subset, e.g. CE:a1,OS:b2 (smoke)")
    ap.add_argument("--skip-generation", action="store_true",
                    help="reuse existing raw candidates; run validation only")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--model", type=str,
                    default=os.environ.get("V5_GENERATOR_MODEL", "gpt-4o"))
    args = ap.parse_args()

    if args.dry_check:
        rc = dry_check()
        if not OUT_FUNNEL.exists():
            OUT_POOL.mkdir(parents=True, exist_ok=True)
            f = _empty_funnel(APPLICABLE_CELLS)
            f["status"] = "BLOCKED_NO_API_KEYS" if check_env() else "READY"
            OUT_FUNNEL.write_text(json.dumps(f, indent=2))
        sys.exit(rc)

    if check_env():
        dry_check()
        sys.exit(2)

    cells = APPLICABLE_CELLS
    if args.cells:
        want = {tuple(x.split(":")) for x in args.cells.split(",")}
        cells = [c for c in APPLICABLE_CELLS if c in want]
        assert cells, f"no valid cells in {args.cells}"

    print(f"v5 mutant generation: {len(cells)} cells × {ATTEMPTS_BUDGET} attempts, "
          f"model={args.model}", flush=True)

    if not args.skip_generation:
        generate_candidates(cells, args.model, args.workers)

    funnel = _empty_funnel(cells)
    funnel["status"] = "RUNNING"
    funnel["generator_model"] = args.model
    by_cell = {c["cell"]: c for c in funnel["cells"]}
    t0 = time.time()
    for op_name, put in cells:
        confirm_cell(op_name, put, by_cell[f"{op_name}×{put}"], funnel, args.model)

    funnel["status"] = "COMPLETE" if cells == APPLICABLE_CELLS else "SUBSET_RUN"
    funnel["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    funnel["confirm_wall_s"] = round(time.time() - t0, 1)
    OUT_FUNNEL.write_text(json.dumps(funnel, indent=2))
    print(f"Wrote {OUT_FUNNEL}")
    if cells == APPLICABLE_CELLS:
        update_ledger(funnel, args.model)
        print(f"Updated {LEDGER}")


if __name__ == "__main__":
    main()
