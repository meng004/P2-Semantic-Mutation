#!/usr/bin/env python3
"""Study-5 Family-XL REGISTERED CALIBRATION PILOT (PREREGISTRATION_STUDY5_v1.md §2e).

Pilot pairs (deterministic §2e pick, frozen in Amendment A1 §9): the first two
certified pairs in frozen roster (walk) order on two different programs AND
two different languages = **invsqrt.cpp** (C++, primary MP5) and **brent.c**
(C, primary MP3). Budget: **1 attempt / operator / slot** (confirmatory budget
is registered separately). Pool tag: **v8xl_pilot**.

Serving (registration §5a, Study-4 v1.2 economics unchanged):
  * XL non-claude generation slots  -> gateway  (src1=gpt-5.5,
    src2=gemini-3.5-flash, src3=grok-4.1->grok-4.3; the pinned
    configs/study4_models.json mapping)
  * XL claude generation slot       -> session harness (packet export/ingest;
    vendor-neutral tag src4)
  * XL blinded review               -> session harness (blinded packets,
    identical blinding machinery to Study-4)
  * arbitration on reviewer-UNCERTAIN -> gateway gpt-5.5

FIREWALL (§2e, verbatim discipline). All artifacts are *_pilot-tagged:
cache  data/operator_campaign/cache_xl_pilot/{pair}/
pools  data/mutants/{pair}_pool_v8xl_pilot/
packets data/study5_packets/{gen,review}_xl_pilot/
results data/results/study5/xl_pilot_*.json
The confirmatory SSOTs (sms_track2_v8xl.json, hlang2_delta_v8xl.json) and the
confirmatory pools ({pair}_pool_v8xl) are NEVER created here (asserted).
Pilot outcomes may fix CODE defects only, logged P15+ in PILOT_LOG.md and §10
BEFORE the confirmatory run. The two pilot pairs REMAIN in the 21-pair
confirmatory roster (§2e registers no exclusion for the XL pilot, unlike the
OS/MR pilots' {a2, b4}; Study-4 C-arm precedent: pilot {a3, b2} stayed
confirmatory, confirmatory cells drawn fresh).

One-shot discipline (§5c): every (operator, slot) is drawn ONCE; the JSONL
campaign log is the draw ledger (a validity-FAIL attempt is a consumed draw;
a transport error is not); re-runs skip drawn slots.

Usage (phases, in order):
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py certify
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py gen-gateway
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py export-harness
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py ingest-harness
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py export-review
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py ingest-review
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py pool-sms
    PYTHONPATH=src python3 scripts/xl_pilot_campaign.py report
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import math
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _load_env() -> None:
    if os.environ.get("BLTCY_BASE_URL") and os.environ.get("BLTCY_API_KEY"):
        return
    envf = ROOT / ".env"
    if not envf.exists():
        return
    for line in envf.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()


def _load_by_path(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load_by_path("cross_source_campaign_xlpilot",
                     "scripts/cross_source_campaign.py")

from p2.avp.dispatcher import call_avp                      # noqa: E402
from p2.avp.interface import MR, AVPResult                  # noqa: E402
from p2.equiv.sampler import UniformSampler                 # noqa: E402
from p2.pipeline.run_cell import run_one_cell               # noqa: E402
from p2.xlport.adapter import XlPairProgram                 # noqa: E402
from p2.xlport.operators_pilot import (                     # noqa: E402
    XL_PILOT_OPERATORS_BY_PROGRAM, XL_PILOT_TARGET_MP)
from p2.xlport.registry import CANDIDATES                   # noqa: E402
from p2.xlport.validation import (                          # noqa: E402
    load_xl_mutant, mutable_source, pair_ext, validate_xl_mutant)

# ── registered pilot constants (§2e / A1 §9) ────────────────────────────────
PILOT_PAIRS = ("invsqrt.cpp", "brent.c")
ATTEMPTS = 1                          # 1 attempt / operator / slot (§2e)
POOL_VERSION = "v8xl_pilot"           # never the confirmatory v8xl
SEED = 20260708                       # registration master seed
GATEWAY_SLOTS = ("src1", "src2", "src3")        # gpt / gemini / grok (§5a)
HARNESS_SLOT = "src4"                           # claude-family (harness)
XL_GEN_MAX_TOKENS = 2048              # P14 precedent: self-contained C/C++ TU

CACHE_ROOT = ROOT / "data" / "operator_campaign" / "cache_xl_pilot"
PACKETS_GEN = ROOT / "data" / "study5_packets" / "gen_xl_pilot"
PACKETS_REVIEW = ROOT / "data" / "study5_packets" / "review_xl_pilot"
RESULTS = ROOT / "data" / "results" / "study5"
LOG_PATH = CACHE_ROOT / "campaign_log.jsonl"

PAIR_PROGRAM = {"invsqrt.cpp": "invsqrt", "brent.c": "brent"}
PAIR_LANG = {"invsqrt.cpp": "cpp", "brent.c": "c"}
_REG = {c["program"]: c for c in CANDIDATES if isinstance(c, dict)}
INSTANTIABLE = {p: sorted(_REG[prog]["instantiable"].keys())
                for p, prog in PAIR_PROGRAM.items()}

TOOLCHAIN_LINE = {
    "cpp": "compile with `g++ -O0 -Wall` (zero errors) and link nothing "
           "beyond the C++ standard library",
    "c": "compile with `gcc -std=c99 -O0 -Wall` and link against GSL "
         "(`-lgsl -lgslcblas -lm`); GSL headers are available",
}
FENCE_TAG = {"cpp": "cpp", "c": "c"}

PROMPT_TEMPLATE_XL = """You are an expert in scientific computing software testing. Generate a SEMANTIC MUTANT of the {lang_name} program below that implements EXACTLY the named operator described.

PAIR NAME: {pair_name}
OPERATOR ID: {op_id}
OPERATOR LABEL: {op_label}
TARGET LOCATOR: {target_locator}
EXACT CHANGE: {transformation}
RATIONALE: {rationale}

ATTEMPT INDEX: {attempt_idx} of {n_attempts}  (different seed; same operator; produce a STRUCTURALLY DIFFERENT mutant from prior attempts)

The operator semantics are language-agnostic; apply the SAME change to the {lang_name} source at the analogous site named by the target locator.

━━━ ORIGINAL PROGRAM ({lang_name}) ━━━
```{fence}
{original_code}
```

INSTRUCTIONS:
- Apply the operator transformation EXACTLY as specified.
- Output ONLY the complete mutated {lang_name} program in a ```{fence}``` block.
- The program MUST {toolchain_line}, and run on x in [0, 1] returning a finite scalar.
- Preserve `double program(double x)` (static linkage allowed, as in the original) and the harness `main` (one x per stdin line -> one float per stdout line).
- Do not explain or comment.
"""

LANG_NAME = {"cpp": "C++", "c": "C99"}


# ── shared helpers ───────────────────────────────────────────────────────────
def _log_append(record: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as fh:
        fh.write(json.dumps({"ts": CAMP._now_iso(), **record},
                            ensure_ascii=False) + "\n")


def _read_log() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    out = []
    for line in LOG_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _drawn_counts() -> dict:
    """{(pair, op_id, slot): n draws} from the JSONL ledger (one-shot rule)."""
    counts: dict = {}
    for r in _read_log():
        if r.get("kind") == "generate":
            k = (r.get("pair"), r.get("op_id"), r.get("slot"))
            counts[k] = counts.get(k, 0) + 1
    return counts


def _pair_ops(pair: str):
    return sorted(XL_PILOT_OPERATORS_BY_PROGRAM[PAIR_PROGRAM[pair]],
                  key=lambda o: o.id)


def _render_prompt(pair: str, op, attempt: int) -> str:
    lang = PAIR_LANG[pair]
    return PROMPT_TEMPLATE_XL.format(
        lang_name=LANG_NAME[lang], pair_name=pair.upper(), op_id=op.id,
        op_label=op.label, target_locator=op.target_locator,
        transformation=op.transformation, rationale=op.rationale,
        attempt_idx=attempt, n_attempts=ATTEMPTS, fence=FENCE_TAG[lang],
        original_code=mutable_source(pair), toolchain_line=TOOLCHAIN_LINE[lang])


def admit_xl_mutant(pair: str, op, raw_code: str, original_fn, slot: str,
                    attempt: int) -> dict:
    """Fence-strip -> §2c V1–V3 -> cache write. XL analogue of admit_c_mutant."""
    cache_dir = CACHE_ROOT / pair
    cache_dir.mkdir(parents=True, exist_ok=True)
    code = CAMP._strip_code_fences(raw_code)
    v = validate_xl_mutant(code, pair, original_fn,
                           build_dir=cache_dir / "_build")
    record = {
        "pair": pair, "op": op.id, "put": op.put, "source": slot,
        "attempt": attempt, "lang": PAIR_LANG[pair],
        "v_syntax": v.syntax_ok, "v_executable": v.executable,
        "v_nontrivial": v.nontrivial, "v_passed": v.passed, "v_error": v.error,
    }
    if v.passed:
        fname = f"{op.id}_{slot}_attempt{attempt:02d}{pair_ext(pair)}"
        (cache_dir / fname).write_text(code)
        record["filename"] = fname
    return record


def _build_mr(program: str, mp: int) -> MR:
    mod = importlib.import_module(f"p2.xlport.mrs_pilot.{program}")
    return MR(r=getattr(mod, f"r_mp{mp}"), R=getattr(mod, f"R_mp{mp}"),
              mp_index=mp, name=f"{program.upper()}_mp{mp}_xlpilot")


# ── phase: certify (MR battery V1/V2 on the UNMUTATED pairs, pre-mutant) ────
def phase_certify() -> int:
    """Battery V1 (executes) / V2 (AVP on the unmutated pair) certification.

    Registered basis §2b (batteries authored pre-mutant, certified V1/V2)
    executed through the FROZEN dispatcher; per-MR verdicts are recorded
    honestly, including the structural MP3/MP4 dispatcher findings.
    """
    out = {}
    for pair in PILOT_PAIRS:
        prog = XlPairProgram(pair)
        program = PAIR_PROGRAM[pair]
        per_mr = {}
        try:
            for mp in INSTANTIABLE[pair]:
                mr = _build_mr(program, mp)
                # V1: r/R execute on real outputs
                try:
                    x0 = 0.37
                    y0 = prog(x0)
                    y1 = prog(mr.r(x0))
                    _ = mr.R(y0, y1)
                    v1 = True
                    v1_err = ""
                except Exception as e:      # noqa: BLE001 (recorded verbatim)
                    v1, v1_err = False, f"{type(e).__name__}: {e}"
                # V2: the frozen AVP verdict on the unmutated pair
                try:
                    v2 = (call_avp(prog, mr, 1e-6) == AVPResult.PASS)
                    v2_err = ""
                except Exception as e:      # noqa: BLE001
                    v2, v2_err = False, f"{type(e).__name__}: {e}"
                per_mr[f"MP{mp}"] = {"V1_executes": v1, "V1_error": v1_err,
                                     "V2_unmutated_avp_pass": v2,
                                     "V2_error": v2_err}
        finally:
            prog.close()
        out[pair] = per_mr
        print(f"[certify] {pair}: " + ", ".join(
            f"MP{mp}={'PASS' if per_mr[f'MP{mp}']['V2_unmutated_avp_pass'] else 'FAIL(V2)'}"
            for mp in INSTANTIABLE[pair]))
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "xl_pilot_mr_certification.json").write_text(json.dumps({
        "artefact": "xl_pilot_mr_certification",
        "registration": "PREREGISTRATION_STUDY5_v1.md §2b/§2e (pilot batteries "
                        "authored pre-mutant, blind to all mutants; certified "
                        "through the FROZEN Track-2 dispatcher)",
        "note": "V2 = AVP(unmutated pair) PASS under the frozen dispatcher. "
                "Structural findings (MP3 h-grid verifier ignores r/R; MP4 "
                "DTW requires exact invariance) are pilot calibration "
                "lessons, NOT grounds to alter the frozen scorer.",
        "batteries": out}, indent=2, ensure_ascii=False))
    _log_append({"kind": "certify-batteries", "result": {
        p: {k: v["V2_unmutated_avp_pass"] for k, v in d.items()}
        for p, d in out.items()}})
    print(f"[certify] wrote {RESULTS / 'xl_pilot_mr_certification.json'}")
    return 0


# ── phase: gateway generation (src1..src3) ───────────────────────────────────
def phase_gen_gateway() -> int:
    from p2.mutators.llm_client import study4_slot_factories
    if not (os.environ.get("BLTCY_BASE_URL") and os.environ.get("BLTCY_API_KEY")):
        print("FATAL: gateway env missing")
        return 2
    slot_factories = dict(study4_slot_factories("cross"))   # src1/2/3 pinned map
    drawn = _drawn_counts()
    records = []
    for pair in PILOT_PAIRS:
        original = XlPairProgram(pair)
        try:
            for op in _pair_ops(pair):
                for slot in GATEWAY_SLOTS:
                    if drawn.get((pair, op.id, slot), 0) >= ATTEMPTS:
                        print(f"  [{pair} {op.id} {slot}] already drawn — skip "
                              "(one-shot)")
                        continue
                    for attempt in range(1, ATTEMPTS + 1):
                        prompt = _render_prompt(pair, op, attempt)
                        try:
                            code, meta = CAMP._study4_call(
                                slot_factories[slot], prompt, kind="generate",
                                slot_tag=slot, op_id=op.id, log_path=None,
                                max_tokens=XL_GEN_MAX_TOKENS)
                        except Exception as e:  # transport error: NOT a draw
                            _log_append({"kind": "generate-error", "pair": pair,
                                         "op_id": op.id, "slot": slot,
                                         "error": f"{type(e).__name__}: {e}"})
                            print(f"  [{pair} {op.id} {slot}] TRANSPORT-ERR {e}")
                            continue
                        _log_append({"kind": "generate", "pair": pair,
                                     "op_id": op.id, "slot": slot,
                                     "attempt": attempt,
                                     "requested_model": meta.get("requested_model"),
                                     "served_model": meta.get("served_model"),
                                     "latency_s": meta.get("latency_s"),
                                     "prompt_tokens": meta.get("prompt_tokens"),
                                     "completion_tokens": meta.get("completion_tokens"),
                                     "cost_usd": meta.get("cost_usd")})
                        rec = admit_xl_mutant(pair, op, code, original, slot,
                                              attempt)
                        rec["model"] = meta.get("requested_model")
                        rec["served_model"] = meta.get("served_model")
                        rec["cost_usd"] = meta.get("cost_usd")
                        records.append(rec)
                        _log_append({"kind": "admit", **{k: rec.get(k) for k in (
                            "pair", "op", "source", "attempt", "v_syntax",
                            "v_executable", "v_nontrivial", "v_passed",
                            "filename")},
                            "v_error": (rec.get("v_error") or "")[:300]})
                        print(f"  [{pair} {op.id} {slot}] "
                              f"{'ADMIT' if rec['v_passed'] else 'FAIL'} "
                              f"served={meta.get('served_model')} "
                              f"ct={meta.get('completion_tokens')}"
                              + ("" if rec["v_passed"]
                                 else f" err={(rec.get('v_error') or '')[:80]}"))
        finally:
            original.close()
    n_admit = sum(1 for r in records if r.get("v_passed"))
    print(f"[gen-gateway] {len(records)} draws, {n_admit} admitted")
    return 0


# ── phase: harness packet export / ingest (claude slot src4) ────────────────
def phase_export_harness() -> int:
    PACKETS_GEN.mkdir(parents=True, exist_ok=True)
    tpl_pin = CAMP._pin_template("xl_pilot_campaign.PROMPT_TEMPLATE_XL",
                                 PROMPT_TEMPLATE_XL)
    drawn = _drawn_counts()
    written = 0
    for pair in PILOT_PAIRS:
        slots, op_blocks = [], []
        for op in _pair_ops(pair):
            if drawn.get((pair, op.id, HARNESS_SLOT), 0) >= ATTEMPTS:
                continue
            prompts = {str(a): _render_prompt(pair, op, a)
                       for a in range(1, ATTEMPTS + 1)}
            op_blocks.append({"spec": CAMP._operator_spec(op),
                              "target_mp_design_intent": XL_PILOT_TARGET_MP.get(op.id),
                              "prompts_by_attempt": prompts})
            for a in range(1, ATTEMPTS + 1):
                slots.append({"op_id": op.id, "source": HARNESS_SLOT,
                              "attempt": a})
        if not slots:
            continue
        pid = f"gen_xl_{pair.replace('.', '_')}"
        packet = {
            "packet_type": "generation",
            "packet_id": pid,
            "put_id": pair,
            "lang": PAIR_LANG[pair],
            "arm": "xl",
            "stratum": "xl_pilot",
            "seed": SEED,
            "k_per_source": ATTEMPTS,
            "sources": [HARNESS_SLOT],
            "registered_prompt_template": tpl_pin,
            "put_source": mutable_source(pair),
            "operators": op_blocks,
            "required_slots": slots,
            "response_schema": {
                **CAMP.GENERATION_RESPONSE_SCHEMA_C,
                "mutants_item_fields": {
                    **CAMP.GENERATION_RESPONSE_SCHEMA_C["mutants_item_fields"],
                    "code": f"complete {LANG_NAME[PAIR_LANG[pair]]} mutant "
                            f"program (```{FENCE_TAG[PAIR_LANG[pair]]} fences "
                            "tolerated, stripped on ingest); must keep "
                            "double program(double x) + the REPL main; must "
                            + TOOLCHAIN_LINE[PAIR_LANG[pair]],
                }},
            "response_filename": f"{pid}_response.json",
            "instructions": (
                "Act as the mutant generator (claude-family harness slot, "
                "registration §5a). For EACH required slot, follow the "
                "operator's rendered prompt and return the complete mutant "
                "program in the 'code' field. ONE-SHOT: exactly one entry per "
                "required slot; no regeneration after admission is visible. "
                "Do NOT include any SMS/kill/survive/outcome field."),
        }
        CAMP._assert_no_outcome_fields(packet)
        text = json.dumps(packet, indent=2, ensure_ascii=False)
        (PACKETS_GEN / f"{pid}.json").write_text(text)
        written += 1
        print(f"[export-harness] {pid}.json ({len(slots)} slot(s))")
    _log_append({"kind": "export-harness", "n_packets": written})
    return 0


def phase_ingest_harness() -> int:
    n_admit, n_draws = 0, 0
    for pair in PILOT_PAIRS:
        pid = f"gen_xl_{pair.replace('.', '_')}"
        ppath = PACKETS_GEN / f"{pid}.json"
        rpath = PACKETS_GEN / f"{pid}_response.json"
        if not (ppath.exists() and rpath.exists()):
            print(f"[ingest-harness] missing packet/response for {pair} — skip")
            continue
        packet = json.loads(ppath.read_text())
        obj = json.loads(rpath.read_text())
        valid, errs = CAMP._validate_generation_response(obj, packet)
        for e in errs:
            print(f"[ingest-harness] SCHEMA-ERR {e}")
        op_by_id = {o.id: o for o in _pair_ops(pair)}
        drawn = _drawn_counts()
        original = XlPairProgram(pair)
        try:
            for m in valid:
                if drawn.get((pair, m["op_id"], m["source"]), 0) >= ATTEMPTS:
                    print(f"  [{pair} {m['op_id']} {m['source']}] already drawn "
                          "— skip (one-shot)")
                    continue
                _log_append({"kind": "generate", "pair": pair,
                             "op_id": m["op_id"], "slot": m["source"],
                             "attempt": m["attempt"],
                             "requested_model": "claude-family(harness)",
                             "served_model": "claude-family(harness)"})
                n_draws += 1
                rec = admit_xl_mutant(pair, op_by_id[m["op_id"]], m["code"],
                                      original, m["source"], m["attempt"])
                _log_append({"kind": "admit", **{k: rec.get(k) for k in (
                    "pair", "op", "source", "attempt", "v_syntax",
                    "v_executable", "v_nontrivial", "v_passed", "filename")},
                    "v_error": (rec.get("v_error") or "")[:300]})
                if rec["v_passed"]:
                    n_admit += 1
                print(f"  [{pair} {m['op_id']} {m['source']}] "
                      f"{'ADMIT' if rec['v_passed'] else 'FAIL'}"
                      + ("" if rec["v_passed"]
                         else f" err={(rec.get('v_error') or '')[:80]}"))
        finally:
            original.close()
    print(f"[ingest-harness] {n_draws} draws, {n_admit} admitted")
    return 0


# ── phase: blinded review packets (export / ingest+arbitrate) ───────────────
def phase_export_review() -> int:
    PACKETS_REVIEW.mkdir(parents=True, exist_ok=True)
    blind_map, n = {}, 0
    for pair in PILOT_PAIRS:
        cache_dir = CACHE_ROOT / pair
        if not cache_dir.exists():
            continue
        op_by_id = {o.id: o for o in _pair_ops(pair)}
        put_source = mutable_source(pair)
        lang = PAIR_LANG[pair]
        for mut in sorted(cache_dir.glob(f"*_attempt*{pair_ext(pair)}")):
            stem = mut.name[:-len(pair_ext(pair))]
            op_id, slot, att = stem.rsplit("_", 2)
            attempt = int(att.replace("attempt", ""))
            op = op_by_id.get(op_id)
            if op is None:
                continue
            code = mut.read_text()
            for tok in CAMP._REVIEW_REDACT_TOKENS:     # P7 blinding redaction
                import re as _re
                code = _re.sub(tok, "src", code, flags=_re.IGNORECASE)
            blind = CAMP._blind_id(f"{pair}|{op_id}", slot, attempt)
            review_prompt = CAMP.REVIEW_PROMPT_TEMPLATE.format(
                op_id=op.id, op_label=op.label,
                target_locator=op.target_locator,
                transformation=op.transformation,
                put_source=put_source, mutant_code=code)
            review_prompt = review_prompt.replace("```python",
                                                  f"```{FENCE_TAG[lang]}")
            packet = CAMP.build_blind_review_packet(op, put_source, code)
            packet.update({
                "packet_type": "review",
                "blind_id": blind,
                "lang": lang,
                "review_prompt": review_prompt,
                "response_schema": CAMP.REVIEW_RESPONSE_SCHEMA,
                "response_filename": f"{blind}_response.json",
                "instructions": (
                    "Act as a BLIND reviewer. You are given only the original "
                    "pair program, the candidate mutant, and the operator "
                    "spec. Judge the V-checks and give an equivalence opinion "
                    "under the E1∧E2 protocol (E1 = output-equivalence on the "
                    "declared domain within tolerance; E2 = a behavioural "
                    "classifier over sampled executions cannot distinguish; "
                    "equivalent=true only if BOTH hold). Write the JSON "
                    "verdict to the file named in response_filename, in the "
                    "same directory as this packet; do not guess who "
                    "generated the mutant."),
            })
            CAMP._assert_no_outcome_fields(packet)
            flat = json.dumps(packet).lower()
            for tok in CAMP._REVIEW_REDACT_TOKENS:
                assert tok not in json.dumps(packet["mutant_code"]).lower(), \
                    f"review packet leaks vendor token {tok!r}"
            for fam in CAMP.FAMILIES:
                assert fam not in flat, f"review packet leaks family {fam}"
            assert slot not in blind
            text = json.dumps(packet, indent=2, ensure_ascii=False)
            (PACKETS_REVIEW / f"{blind}.json").write_text(text)
            blind_map[blind] = {"pair": pair, "op_id": op_id, "source": slot,
                                "attempt": attempt, "mutant_file": mut.name,
                                "packet_sha256": CAMP._sha256_text(text)}
            n += 1
    (PACKETS_REVIEW / "_blind_map.json").write_text(
        json.dumps(blind_map, indent=2, ensure_ascii=False))
    _log_append({"kind": "export-review", "n_packets": n})
    print(f"[export-review] wrote {n} blinded review packet(s) -> "
          f"{PACKETS_REVIEW}")
    return 0


def phase_ingest_review() -> int:
    """Ingest harness verdicts; reviewer-UNCERTAIN -> live gateway gpt-5.5
    arbitration on the SAME blinded packet (§5a role table)."""
    from p2.mutators.llm_client import study4_role_factory
    verdicts, errors, arbitrated = [], [], []
    for f in sorted(PACKETS_REVIEW.glob("rev_*_response.json")):
        obj = json.loads(f.read_text())
        parsed, errs = CAMP._validate_review_response(obj)
        if errs:
            errors.append({"file": f.name, "errors": errs})
            print(f"[ingest-review] {f.name}: SCHEMA-ERR {errs}")
            continue
        rec = {"blind_id": parsed["blind_id"], "overall": parsed["overall"],
               "operator_match": parsed.get("operator_match"),
               "equivalence": parsed.get("equivalence"),
               "reason": parsed.get("reason"), "arbitrated": False}
        if parsed["overall"] == "UNCERTAIN":
            packet = json.loads(
                (PACKETS_REVIEW / f"{parsed['blind_id']}.json").read_text())
            raw, _meta = CAMP._study4_call(
                study4_role_factory("arbiter"), packet["review_prompt"],
                kind="arbitrate", slot_tag="arbiter", op_id=None,
                log_path=None, max_tokens=400)
            arb = CAMP._parse_review_json(raw)
            rec["arbitrated"] = True
            rec["arbiter_overall"] = arb.get("overall", "UNCERTAIN")
            rec["overall_final"] = rec["arbiter_overall"]
            arbitrated.append(parsed["blind_id"])
            _log_append({"kind": "arbitrate", "blind_id": parsed["blind_id"],
                         "verdict": rec["arbiter_overall"]})
        else:
            rec["overall_final"] = parsed["overall"]
        verdicts.append(rec)
        _log_append({"kind": "review", "blind_id": rec["blind_id"],
                     "overall": rec["overall"],
                     "overall_final": rec["overall_final"]})
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "xl_pilot_review_verdicts.json").write_text(json.dumps({
        "artefact": "xl_pilot_review_verdicts",
        "reviewer": "claude-family (session harness, §5a)",
        "arbiter": "gpt-5.5 (gateway, on reviewer-UNCERTAIN only)",
        "n_verdicts": len(verdicts), "n_arbitrated": len(arbitrated),
        "verdicts": verdicts, "errors": errors},
        indent=2, ensure_ascii=False))
    print(f"[ingest-review] {len(verdicts)} verdict(s), "
          f"{len(arbitrated)} arbitrated, {len(errors)} schema-rejected")
    return 0


# ── phase: pool build + SMS through the frozen Track-2 machinery ────────────
def evaluate_xl_cell(pair: str, mp: int, pool_dir: Path) -> dict:
    cell_label = f"{pair.upper()}_MP{mp}"
    if mp not in INSTANTIABLE[pair]:
        return {"cell": cell_label, "vacant": True, "adjudicated": False,
                "sms": None,
                "note": "registered-vacant: stratum not instantiable on this "
                        "program (frozen A1 registry; standard _is_excluded)"}
    original = XlPairProgram(pair)
    mutant_progs, names = [], []
    try:
        for src in sorted(pool_dir.glob(f"*{pair_ext(pair)}")):
            names.append(src.name)
            mutant_progs.append(load_xl_mutant(src, pair,
                                               build_dir=pool_dir / "_build"))
        mr = _build_mr(PAIR_PROGRAM[pair], mp)
        if not names:
            return {"cell": cell_label, "mutant_dir": str(pool_dir),
                    "inst": 0, "equiv": 0, "killed": 0, "survive": 0,
                    "sms": 0.0, "outcomes": []}
        sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=42)
        result = run_one_cell(
            put=original, mutants=mutant_progs, mr_set=[mr],
            cell_id=cell_label, sampler=sampler, k_eq=1000,
            epsilon_eq=1e-6, epsilon_avp=1e-6, repeats=1)
        outcomes = []
        for idx, name in enumerate(names):
            label = ("EQUIV" if idx in result.equiv_indices else
                     "KILLED" if idx in result.killed_indices else "SURVIVE")
            outcomes.append({"file": name, "label": label})
        return {"cell": cell_label,
                "mutant_dir": str(pool_dir.relative_to(ROOT)),
                "repeats": 1, "inst": result.inst_count,
                "equiv": result.equiv_count, "killed": result.killed_count,
                "survive": result.survive_count,
                "sms": round(result.sms, 4), "outcomes": outcomes}
    finally:
        original.close()
        for p in mutant_progs:
            p.close()


def phase_pool_sms() -> int:
    sms_matrix = {}
    for pair in PILOT_PAIRS:
        cache_dir = CACHE_ROOT / pair
        pool_dir = ROOT / "data" / "mutants" / f"{pair}_pool_{POOL_VERSION}"
        if pool_dir.exists():
            shutil.rmtree(pool_dir)
        pool_dir.mkdir(parents=True)
        n_pool = 0
        for mut in sorted(cache_dir.glob(f"*_attempt*{pair_ext(pair)}")):
            shutil.copy(mut, pool_dir / mut.name)
            n_pool += 1
        print(f"[pool] {pair}: {n_pool} admitted mutant(s) -> {pool_dir.name}")
        for mp in (1, 2, 3, 4, 5):
            cell = evaluate_xl_cell(pair, mp, pool_dir)
            sms_matrix[cell["cell"]] = cell
            if cell.get("vacant"):
                print(f"  {cell['cell']}: registered-vacant")
            else:
                print(f"  {cell['cell']}: inst={cell['inst']} "
                      f"equiv={cell['equiv']} killed={cell['killed']} "
                      f"survive={cell['survive']} SMS={cell['sms']:.4f}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "xl_pilot_sms.json"
    out.write_text(json.dumps(sms_matrix, indent=2, ensure_ascii=False))
    _log_append({"kind": "sms", "pool_version": POOL_VERSION,
                 "cells": {c: v.get("sms") for c, v in sms_matrix.items()}})
    print(f"[pool-sms] wrote {out}")

    # Machinery smoke of the FROZEN Study-5 analyzer on the PILOT pool
    # (exercises load_xl_roster + the UNDER_CERTIFIED gate; pilot-tagged
    # output, never the confirmatory hlang2_delta_v8xl.json).
    hl = _load_by_path("compute_hlang_delta_xlpilot",
                       "scripts/compute_hlang_delta.py")
    report = hl.run(matrix_path=out,
                    out_path=RESULTS / "xl_pilot_hlang_smoke.json",
                    preset=hl.STUDY5_PRESETS["xl"])
    h = report["H_LANG_cross_language_invariance"]
    print(f"[analyzer-smoke] delta_XL={h['cliffs_delta_C']:+.4f} "
          f"verdict={h['verdict']} (expected UNDER_CERTIFIED: n_pairs="
          f"{h['n_puts']} < {h['registered_min_n_pairs']})")
    assert h["verdict"] == "UNDER_CERTIFIED", \
        "pilot smoke must trip the registered UNDER_CERTIFIED gate"
    return 0


# ── phase: report + firewall attestation ────────────────────────────────────
def phase_report() -> int:
    logs = _read_log()
    gen = [r for r in logs if r.get("kind") == "generate"]
    admit = [r for r in logs if r.get("kind") == "admit"]
    declared = len(PILOT_PAIRS) * 3 * (len(GATEWAY_SLOTS) + 1) * ATTEMPTS
    by_slot: dict = {}
    for r in admit:
        s = by_slot.setdefault(r["source"], {"draws": 0, "admitted": 0})
        s["draws"] += 1
        s["admitted"] += 1 if r.get("v_passed") else 0
    cost = sum(r.get("cost_usd") or 0.0 for r in gen)
    reviews = json.loads((RESULTS / "xl_pilot_review_verdicts.json").read_text()) \
        if (RESULTS / "xl_pilot_review_verdicts.json").exists() else {}
    sms = json.loads((RESULTS / "xl_pilot_sms.json").read_text()) \
        if (RESULTS / "xl_pilot_sms.json").exists() else {}
    report = {
        "pilot": "study5_family_xl_calibration_{invsqrt.cpp,brent.c}",
        "registration": "PREREGISTRATION_STUDY5_v1.md §2e (XL pilot), §5a "
                        "(serving), §2c (admission); Amendment A1 §9 "
                        "(deterministic pilot-pair pick)",
        "pool_version": POOL_VERSION,
        "attempts_per_op_slot": ATTEMPTS,
        "slots": {"gateway": list(GATEWAY_SLOTS),
                  "harness_claude": HARNESS_SLOT},
        "firewall": "pilot-tagged only; confirmatory sms_track2_v8xl.json / "
                    "hlang2_delta_v8xl.json / {pair}_pool_v8xl NEVER created; "
                    "pilot pairs REMAIN confirmatory (§2e registers no XL "
                    "exclusion; C-arm {a3,b2} precedent) — their confirmatory "
                    "cells are drawn fresh",
        "declared_slots": declared,
        "draws": len(gen),
        "per_slot": by_slot,
        "gateway_cost_usd": round(cost, 4),
        "n_review_verdicts": reviews.get("n_verdicts"),
        "n_arbitrated": reviews.get("n_arbitrated"),
        "sms_cells": {c: (v.get("sms") if not v.get("vacant") else "VACANT")
                      for c, v in sorted(sms.items())},
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "xl_pilot_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False))

    # firewall attestation (§2e)
    assert not (ROOT / "data/results/sms_track2_v8xl.json").exists()
    assert not (ROOT / "data/results/hlang2_delta_v8xl.json").exists()
    roster = json.loads((ROOT / "configs/xl_roster.json").read_text())
    for p in roster["pairs"]:
        assert not (ROOT / "data" / "mutants" / f"{p.lower()}_pool_v8xl").exists(), \
            f"pilot must NOT create the confirmatory {p} v8xl pool"
    print("[firewall] attested: no confirmatory v8xl artifact exists")
    print(f"[report] wrote {RESULTS / 'xl_pilot_report.json'}")
    print(json.dumps(report, indent=2)[:2000])
    return 0


PHASES = {
    "certify": phase_certify,
    "gen-gateway": phase_gen_gateway,
    "export-harness": phase_export_harness,
    "ingest-harness": phase_ingest_harness,
    "export-review": phase_export_review,
    "ingest-review": phase_ingest_review,
    "pool-sms": phase_pool_sms,
    "report": phase_report,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("phase", choices=sorted(PHASES))
    args = ap.parse_args()
    return PHASES[args.phase]()


if __name__ == "__main__":
    raise SystemExit(main())
