#!/usr/bin/env python3
"""Study-5 Family-MR — Arm-L battery elicitation + V1/V2 certification wave.

Registered under docs/prereg_v2/PREREGISTRATION_STUDY5_v1.md §2d/§5/§7 and
the frozen prompt template docs/prereg_v2/STUDY5_MR_ELICITATION_PROMPT.md
(Amendment A2, sha256-pinned below). This tool covers the ELICITATION +
CERTIFICATION wave only; it performs NO SMS scoring (the scoring wave builds
sms_track2_v8_mrL{,_same}.json later, from the batteries assembled here).

Design (mirrors the Study-4 campaign discipline):

  draw          one-shot gateway elicitation for the 3 non-Anthropic vendor
                slots (gpt-5.5 / gemini-3.5-flash / grok-4.1->grok-4.3), one
                call per (PUT, MP, vendor); raw completion saved verbatim; a
                saved raw file IS the draw (drawn is drawn — resume skips it;
                transport failures leave no raw file and are retryable).
  ingest-claude ingest the session-harness claude-fable-5 responses (authored
                in-session, one file per cell) through the IDENTICAL parse
                path — byte-symmetric with the gateway vendors downstream.
  certify       V1/V2 executability certification of every parsed MR against
                the unmutated PUT through the frozen p2.avp harness
                (registration §2d: V1 = parses + executes as a runnable check
                within the harness MR-interface; V2 = not violated by the
                unmutated PUT, i.e. call_avp == PASS). NO mutant is ever
                consulted; NO quality filtering; certification is
                deterministic/mechanical and re-runnable (it is not a draw).
  assemble      per-cell union battery (all four vendors' certified MRs) ->
                data/mr_batteries/study5_L/batteries/{PUT}_MP{k}.json
  summary       honest accounting: per-vendor counts, certification pass
                rates, per-family coverage, cost totals.

One-shot rule (§5c/§7): each (PUT, stratum, vendor) is elicited exactly once.
There is deliberately NO re-roll path in this tool; deleting a raw draw to
re-elicit would be a protocol violation and must be reported as such.

Usage:
  set -a; source .env; set +a
  PYTHONPATH=src python3 scripts/study5_mr_elicit.py draw --puts a2,b4 --tag v8mr_pilot
  PYTHONPATH=src python3 scripts/study5_mr_elicit.py ingest-claude --puts a2,b4 --tag v8mr_pilot
  PYTHONPATH=src python3 scripts/study5_mr_elicit.py certify --puts a2,b4 --tag v8mr_pilot
  PYTHONPATH=src python3 scripts/study5_mr_elicit.py assemble --puts a2,b4 --tag v8mr_pilot
  PYTHONPATH=src python3 scripts/study5_mr_elicit.py summary --tag v8mr_pilot
  ... same subcommands with --confirmatory (28-PUT roster, tag v8mr)
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
import re
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR, AVPResult          # noqa: E402
from p2.avp.dispatcher import call_avp              # noqa: E402
from p2.config import study4 as s4cfg               # noqa: E402

# ---- registered constants ---------------------------------------------------
TEMPLATE_PATH = ROOT / "docs" / "prereg_v2" / "STUDY5_MR_ELICITATION_PROMPT.md"
TEMPLATE_SHA256 = "67c879d29e42f1f8b6c2cfb45e8a59a6efa70517cd252828488b1fe20192a02c"
BATTERY_ROOT = ROOT / "data" / "mr_batteries" / "study5_L"

CONFIRMATORY_PUTS = (
    "a1", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b5", "b6", "b7",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
)
PILOT_PUTS = ("a2", "b4")
MPS = (1, 2, 3, 4, 5)

GATEWAY_MODELS = ("gpt-5.5", "gemini-3.5-flash", "grok-4.1")
CLAUDE_MODEL = "claude-fable-5"          # session harness, not gateway
ALL_VENDOR_SLOTS = GATEWAY_MODELS + (CLAUDE_MODEL,)

TEMPERATURE = 0.7                        # frozen serving parameter (A2)
REQUESTED_MAX_TOKENS = 2500              # frozen serving parameter (A2)
EPSILON_AVP = 1e-6                       # identical to scripts/sms_campaign.py
V1_PROBES = (0.1, 0.3, 0.5, 0.7, 0.9)    # C_PORT_SPEC §5 / registration §2c precedent
CERT_TIMEOUT_S = 120                     # per-MR wall-clock executability guard
MAX_MRS_PER_RESPONSE = 3                 # frozen output-format contract (A2)

PUTS_DIR = ROOT / "src" / "p2" / "puts"


# --------------------------------------------------------------------------- #
# Template rendering (single source: the frozen, hash-pinned markdown file)
# --------------------------------------------------------------------------- #
def _template_text() -> str:
    raw = TEMPLATE_PATH.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != TEMPLATE_SHA256:
        print(f"ERROR: frozen prompt template hash mismatch\n"
              f"  pinned : {TEMPLATE_SHA256}\n  found  : {got}\n"
              "The template is frozen by Amendment A2; it must not change "
              "after the first elicitation call.", file=sys.stderr)
        raise SystemExit(4)
    return raw.decode("utf-8")


def _extract_body(md: str) -> str:
    m = re.search(r"````text\n(.*?)````", md, re.DOTALL)
    if not m:
        raise RuntimeError("template body fence not found")
    return m.group(1).strip("\n")


def _extract_table_blocks(md: str, heading_marker: str) -> dict[int, str]:
    """Parse the '| MPk | text |' rows of the table under a given heading."""
    sec = md.split(heading_marker, 1)[1]
    out: dict[int, str] = {}
    for line in sec.splitlines():
        m = re.match(r"\|\s*MP(\d)\s*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            out[int(m.group(1))] = m.group(2)
        if len(out) == 5:
            break
    if len(out) != 5:
        raise RuntimeError(f"expected 5 MP rows under {heading_marker!r}, got {len(out)}")
    return out


def put_source(put_id: str) -> str:
    return (PUTS_DIR / f"{put_id}.py").read_text()


def render_prompt(put_id: str, mp_k: int) -> str:
    md = _template_text()
    body = _extract_body(md)
    strata = _extract_table_blocks(md, "## `{stratum_block}`")
    evals = _extract_table_blocks(md, "## `{eval_block}`")
    return body.format(put_id=put_id,
                       put_source=put_source(put_id).rstrip(),
                       stratum_block=strata[mp_k],
                       eval_block=evals[mp_k])


# --------------------------------------------------------------------------- #
# Gateway call (mirrors cross_source_campaign._chat_with_retry/_generate_one:
# temperature, retry classes, served-model echo, cost accounting)
# --------------------------------------------------------------------------- #
try:
    from openai import (RateLimitError, APITimeoutError, APIConnectionError,
                        InternalServerError, APIStatusError)
    _RETRYABLE = (RateLimitError, APITimeoutError, APIConnectionError,
                  InternalServerError)
except Exception:                                    # pragma: no cover
    APIStatusError = ()                              # type: ignore[assignment,misc]
    _RETRYABLE = ()                                  # type: ignore[assignment]

_LOG_LOCK = threading.Lock()


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _chat_with_retry(client, *, model, messages, max_tokens, temperature,
                     tries: int = 3, base_delay: float = 1.5):
    last = None
    for attempt in range(tries):
        try:
            return client.chat.completions.create(
                model=model, messages=messages,
                max_tokens=max_tokens, temperature=temperature)
        except _RETRYABLE as e:
            last = e
        except APIStatusError as e:
            code = getattr(e, "status_code", None)
            if code is not None and (code >= 500 or code == 429):
                last = e
            else:
                raise
        if attempt < tries - 1:
            time.sleep(base_delay * (2 ** attempt))
    raise last                                        # type: ignore[misc]


def _log_append(log_path: Path, record: dict) -> None:
    record = {"ts": _now_iso(), **record}
    with _LOG_LOCK:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _gateway_elicit_one(model_id: str, put_id: str, mp_k: int, *,
                        raw_dir: Path, log_path: Path, tag: str) -> dict:
    """One one-shot elicitation call; saving the raw completion IS the draw."""
    from p2.mutators.llm_client import study4_client
    client, model, quirks = study4_client(model_id)
    floor = int(quirks.get("min_max_tokens", 0) or 0)
    eff_max = max(REQUESTED_MAX_TOKENS, floor)
    prompt = render_prompt(put_id, mp_k)
    cell = f"{put_id.upper()}_MP{mp_k}"
    raw_file = raw_dir / f"{put_id}_MP{mp_k}_{model_id}.txt"
    t0 = time.time()
    try:
        resp = _chat_with_retry(
            client, model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=eff_max, temperature=TEMPERATURE)
    except Exception as e:
        _log_append(log_path, {
            "event": "mrL-elicit-error", "tag": tag, "cell": cell,
            "requested_model": model, "error": f"{type(e).__name__}: {e}"[:400],
            "note": "transport/quota failure after retries — NOT a draw "
                    "(P14 precedent); re-invoking draw resumes here"})
        return {"cell": cell, "model": model_id, "ok": False}
    dt = time.time() - t0
    content = resp.choices[0].message.content or ""
    usage = resp.usage
    pt = usage.prompt_tokens if usage else None
    ct = usage.completion_tokens if usage else None
    cost = s4cfg.estimate_cost_usd(model, pt, ct)
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(content)
    _log_append(log_path, {
        "event": "mrL-elicit", "tag": tag, "cell": cell, "put": put_id,
        "mp": mp_k, "requested_model": model,
        "served_model": getattr(resp, "model", None),
        "served_mismatch": getattr(resp, "model", None) not in (None, model),
        "latency_s": round(dt, 2), "prompt_tokens": pt,
        "completion_tokens": ct, "cost_usd": round(cost, 6),
        "empty_body": not bool(content.strip()),
        "template_sha256": TEMPLATE_SHA256, "raw_file": str(raw_file.relative_to(ROOT)),
        "temperature": TEMPERATURE, "max_tokens": eff_max})
    return {"cell": cell, "model": model_id, "ok": True,
            "cost": cost, "pt": pt, "ct": ct}


# --------------------------------------------------------------------------- #
# Response parsing (identical for all four vendors)
# --------------------------------------------------------------------------- #
def _strip_fences(text: str) -> str:
    """Byte-mirror of cross_source_campaign._strip_fences (python tag, bare tag,
    else whole text)."""
    m = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


_ALLOWED_IMPORTS = {"math", "numpy"}
_BANNED_CALLS = {"exec", "eval", "compile", "open", "__import__", "input",
                 "breakpoint", "globals", "locals", "vars", "setattr",
                 "delattr"}


def _format_screen(tree: ast.AST) -> str | None:
    """Frozen output-format contract screen (A2): import allowlist + banned
    call names. A violation is a V1 format/executability failure."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in _ALLOWED_IMPORTS:
                    return f"format: disallowed import {a.name!r}"
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in _ALLOWED_IMPORTS:
                return f"format: disallowed import from {node.module!r}"
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id in _BANNED_CALLS:
                return f"format: banned call {fn.id!r}"
    return None


def parse_response(raw_text: str) -> dict:
    """-> {module_src, mr_ks: [k...], parse_error, format_error, n_extra}."""
    code = _strip_fences(raw_text)
    out = {"module_src": code, "mr_ks": [], "parse_error": None,
           "format_error": None, "n_extra_pairs": 0}
    if not code.strip():
        out["parse_error"] = "empty completion body"
        return out
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        out["parse_error"] = f"SyntaxError: {e}"
        return out
    fmt = _format_screen(tree)
    if fmt:
        out["format_error"] = fmt
        return out
    # P15 pilot fix: the frozen contract fixes the NAMES r_k/R_k, not the
    # binding syntax — grok binds MRs as ``r_1 = lambda x: ...`` assignments.
    # Accept module-level FunctionDef AND Name-target assignments; whether the
    # bound object is actually callable is checked at V1 (certify).
    names = {n.name for n in tree.body
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            names.update(t.id for t in n.targets if isinstance(t, ast.Name))
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            names.add(n.target.id)
    ks = [k for k in (1, 2, 3) if f"r_{k}" in names and f"R_{k}" in names]
    extra = [k for k in range(4, 10) if f"r_{k}" in names and f"R_{k}" in names]
    out["mr_ks"] = ks
    out["n_extra_pairs"] = len(extra)     # beyond-contract pairs: logged, unused
    if not ks:
        out["parse_error"] = ("no contract-conforming MR pair (r_k/R_k, "
                              "k in 1..3) found")
    return out


# --------------------------------------------------------------------------- #
# V1/V2 certification (frozen harness; executability ONLY — registration §2d)
# --------------------------------------------------------------------------- #
class _CertTimeout(Exception):
    pass


def _alarm(_sig, _frm):
    raise _CertTimeout()


def _load_put(put_id: str):
    spec = importlib.util.spec_from_file_location(
        f"_put_{put_id}", PUTS_DIR / f"{put_id}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                      # type: ignore[union-attr]
    return mod.program


def _exec_module(module_src: str, tag: str) -> dict | None:
    ns: dict = {"__name__": f"_mrL_{tag}"}
    exec(compile(module_src, f"<mrL:{tag}>", "exec"), ns)   # noqa: S102
    return ns


def certify_mr(put_fn, r_fn, R_fn, mp_k: int, name: str) -> dict:
    """V1 = executes as a runnable check within the harness MR-interface;
    V2 = not violated by the unmutated PUT (call_avp == PASS). Nothing else."""
    rec = {"v1": False, "v1_reason": None, "v2": False, "certified": False}
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(CERT_TIMEOUT_S)
    try:
        # V1a: r on the registered probe set — finite float inside [0,1]
        for x in V1_PROBES:
            rx = r_fn(x)
            rxf = float(rx)
            if not math.isfinite(rxf):
                rec["v1_reason"] = f"r({x}) non-finite"
                return rec
            if not (0.0 <= rxf <= 1.0):
                rec["v1_reason"] = f"r({x})={rxf!r} outside [0,1] (format contract)"
                return rec
        # V1b: R on real PUT output pairs — must return a bool
        for x in V1_PROBES:
            y0 = put_fn(x)
            y1 = put_fn(float(r_fn(x)))
            res = R_fn(y0, y1)
            if not isinstance(res, (bool,)) and type(res).__name__ != "bool_":
                rec["v1_reason"] = f"R returned {type(res).__name__}, not bool"
                return rec
        # V1c: the full frozen harness check executes without exception
        mr = MR(r=r_fn, R=R_fn, mp_index=mp_k, name=name)
        verdict = call_avp(put_fn, mr, EPSILON_AVP)
        rec["v1"] = True
        # V2: the unmutated PUT does not violate the MR
        rec["v2"] = (verdict == AVPResult.PASS)
        rec["certified"] = rec["v1"] and rec["v2"]
        return rec
    except _CertTimeout:
        rec["v1_reason"] = f"cert-timeout >{CERT_TIMEOUT_S}s"
        return rec
    except Exception as e:                            # executability failure
        rec["v1_reason"] = f"{type(e).__name__}: {e}"[:300]
        return rec
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


# --------------------------------------------------------------------------- #
# Wave drivers
# --------------------------------------------------------------------------- #
def _dirs(tag: str) -> dict:
    base = BATTERY_ROOT if tag == "v8mr" else BATTERY_ROOT / tag
    return {"base": base, "raw": base / "raw", "records": base / "records",
            "batteries": base / "batteries",
            "log": base / "elicitation_log.jsonl",
            "claude_inbox": base / "claude_inbox"}


def cmd_draw(puts, tag, workers: int) -> None:
    d = _dirs(tag)
    jobs = []
    for put in puts:
        for mp in MPS:
            for model in GATEWAY_MODELS:
                raw_file = d["raw"] / f"{put}_MP{mp}_{model}.txt"
                if raw_file.exists():
                    continue                          # drawn is drawn
                jobs.append((put, mp, model))
    total = len(puts) * len(MPS) * len(GATEWAY_MODELS)
    print(f"[draw] tag={tag} cells={len(puts)}x5 gateway calls due="
          f"{len(jobs)}/{total} (rest already drawn)")
    if not jobs:
        return
    spent = 0.0
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_gateway_elicit_one, m, p, k, raw_dir=d["raw"],
                          log_path=d["log"], tag=tag): (p, k, m)
                for (p, k, m) in jobs}
        for fut in as_completed(futs):
            p, k, m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:                    # defensive; logged inside
                print(f"  [{p}_MP{k} {m}] UNCAUGHT {type(e).__name__}: {e}")
                continue
            done += 1
            if r.get("ok"):
                spent += r.get("cost") or 0.0
                print(f"  [{r['cell']} {m}] drawn ct={r.get('ct')} "
                      f"(${spent:.2f} cum, {done}/{len(jobs)})", flush=True)
            else:
                print(f"  [{r['cell']} {m}] TRANSPORT-FAIL (resumable)", flush=True)
    print(f"[draw] gateway spend this invocation: ${spent:.4f}")


def cmd_ingest_claude(puts, tag) -> None:
    """Ingest session-harness claude responses (one file per cell) through the
    same raw-file convention as the gateway vendors."""
    d = _dirs(tag)
    n = 0
    for put in puts:
        for mp in MPS:
            src = d["claude_inbox"] / f"{put}_MP{mp}.md"
            dst = d["raw"] / f"{put}_MP{mp}_{CLAUDE_MODEL}.txt"
            if dst.exists():
                continue                              # drawn is drawn
            if not src.exists():
                print(f"  MISSING claude response: {src.relative_to(ROOT)}")
                continue
            text = src.read_text()
            d["raw"].mkdir(parents=True, exist_ok=True)
            dst.write_text(text)
            _log_append(d["log"], {
                "event": "mrL-elicit", "tag": tag,
                "cell": f"{put.upper()}_MP{mp}", "put": put, "mp": mp,
                "requested_model": CLAUDE_MODEL,
                "served_model": "session-harness",
                "served_mismatch": False, "latency_s": None,
                "prompt_tokens": None, "completion_tokens": None,
                "cost_usd": 0.0, "empty_body": not bool(text.strip()),
                "template_sha256": TEMPLATE_SHA256,
                "raw_file": str(dst.relative_to(ROOT)),
                "note": "claude-family slot served in-session by the harness "
                        "(registration §5a); no gateway tokens"})
            n += 1
    print(f"[ingest-claude] ingested {n} cell responses")


def cmd_certify(puts, tag) -> None:
    d = _dirs(tag)
    d["records"].mkdir(parents=True, exist_ok=True)
    for put in puts:
        put_fn = _load_put(put)
        for mp in MPS:
            for model in ALL_VENDOR_SLOTS:
                raw_file = d["raw"] / f"{put}_MP{mp}_{model}.txt"
                rec_file = d["records"] / f"{put}_MP{mp}_{model}.json"
                if not raw_file.exists():
                    continue
                parsed = parse_response(raw_file.read_text())
                mrs = []
                if not parsed["parse_error"] and not parsed["format_error"]:
                    try:
                        ns = _exec_module(parsed["module_src"],
                                          f"{put}_MP{mp}_{model}")
                        exec_err = None
                    except Exception as e:
                        ns, exec_err = None, f"{type(e).__name__}: {e}"[:300]
                    for k in parsed["mr_ks"]:
                        name = f"{put}_MP{mp}_L_{model}_{k}"
                        if ns is None:
                            mrs.append({"k": k, "v1": False,
                                        "v1_reason": f"module exec: {exec_err}",
                                        "v2": False, "certified": False})
                            continue
                        r_obj, R_obj = ns.get(f"r_{k}"), ns.get(f"R_{k}")
                        if not (callable(r_obj) and callable(R_obj)):
                            mrs.append({"k": k, "v1": False,
                                        "v1_reason": "r_k/R_k bound but not "
                                                     "callable",
                                        "v2": False, "certified": False})
                            continue
                        cert = certify_mr(put_fn, r_obj, R_obj, mp, name)
                        mrs.append({"k": k, **cert})
                rec = {
                    "cell": f"{put.upper()}_MP{mp}", "put": put, "mp": mp,
                    "vendor_slot": model, "tag": tag,
                    "template_sha256": TEMPLATE_SHA256,
                    "raw_file": str(raw_file.relative_to(ROOT)),
                    "module_src": parsed["module_src"],
                    "parse_error": parsed["parse_error"],
                    "format_error": parsed["format_error"],
                    "n_extra_pairs": parsed["n_extra_pairs"],
                    "n_parsed": len(parsed["mr_ks"]),
                    "n_certified": sum(m["certified"] for m in mrs),
                    "mrs": mrs,
                }
                rec_file.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        print(f"  certified {put} (5 cells x vendors present)", flush=True)
    print("[certify] done")


def cmd_assemble(puts, tag) -> None:
    d = _dirs(tag)
    d["batteries"].mkdir(parents=True, exist_ok=True)
    n_cells = 0
    for put in puts:
        for mp in MPS:
            cell = f"{put.upper()}_MP{mp}"
            vendors = {}
            union = []
            for model in ALL_VENDOR_SLOTS:
                rec_file = d["records"] / f"{put}_MP{mp}_{model}.json"
                if not rec_file.exists():
                    continue
                rec = json.loads(rec_file.read_text())
                vendors[model] = {
                    "n_parsed": rec["n_parsed"],
                    "n_certified": rec["n_certified"],
                    "parse_error": rec["parse_error"],
                    "format_error": rec["format_error"],
                    "mrs": rec["mrs"],
                }
                for m in rec["mrs"]:
                    if m["certified"]:
                        union.append({"vendor_slot": model, "k": m["k"],
                                      "name": f"{put}_MP{mp}_L_{model}_{m['k']}",
                                      "record": str(rec_file.relative_to(ROOT))})
            battery = {
                "cell": cell, "put": put, "mp": mp, "tag": tag,
                "registration": "PREREGISTRATION_STUDY5_v1.md §2d (union of "
                                "the four vendors' certified MRs)",
                "template_sha256": TEMPLATE_SHA256,
                "vendors": vendors,
                "union_battery": union,
                "union_size": len(union),
            }
            (d["batteries"] / f"{cell}.json").write_text(
                json.dumps(battery, indent=2, ensure_ascii=False))
            n_cells += 1
    print(f"[assemble] wrote {n_cells} cell batteries -> "
          f"{d['batteries'].relative_to(ROOT)}")


def cmd_summary(puts, tag) -> dict:
    d = _dirs(tag)
    per_vendor = {m: {"responses": 0, "empty": 0, "parse_fail": 0,
                      "format_fail": 0, "mrs_parsed": 0, "v1_pass": 0,
                      "v2_pass": 0, "certified": 0,
                      "cost_usd": 0.0, "prompt_tokens": 0,
                      "completion_tokens": 0, "calls_logged": 0,
                      "transport_errors": 0, "served_models": {}}
                  for m in ALL_VENDOR_SLOTS}
    # log-side accounting
    if d["log"].exists():
        for line in d["log"].read_text().splitlines():
            row = json.loads(line)
            model = row.get("requested_model")
            if model not in per_vendor:
                continue
            if row["event"] == "mrL-elicit-error":
                per_vendor[model]["transport_errors"] += 1
                continue
            if row["event"] != "mrL-elicit":
                continue
            pv = per_vendor[model]
            pv["calls_logged"] += 1
            pv["cost_usd"] += row.get("cost_usd") or 0.0
            pv["prompt_tokens"] += row.get("prompt_tokens") or 0
            pv["completion_tokens"] += row.get("completion_tokens") or 0
            sm = row.get("served_model")
            pv["served_models"][str(sm)] = pv["served_models"].get(str(sm), 0) + 1
    # record-side accounting
    per_family = {f"MP{k}": {"cells": 0, "cells_with_nonempty_union": 0,
                             "union_mrs": 0} for k in MPS}
    per_put = {}
    for put in puts:
        per_put[put] = {"cells_with_nonempty_union": 0, "union_mrs": 0}
        for mp in MPS:
            fam = per_family[f"MP{mp}"]
            fam["cells"] += 1
            bfile = d["batteries"] / f"{put.upper()}_MP{mp}.json"
            if bfile.exists():
                b = json.loads(bfile.read_text())
                if b["union_size"] > 0:
                    fam["cells_with_nonempty_union"] += 1
                    per_put[put]["cells_with_nonempty_union"] += 1
                fam["union_mrs"] += b["union_size"]
                per_put[put]["union_mrs"] += b["union_size"]
            for model in ALL_VENDOR_SLOTS:
                rec_file = d["records"] / f"{put}_MP{mp}_{model}.json"
                if not rec_file.exists():
                    continue
                rec = json.loads(rec_file.read_text())
                pv = per_vendor[model]
                pv["responses"] += 1
                if not rec["module_src"].strip():
                    pv["empty"] += 1
                if rec["parse_error"]:
                    pv["parse_fail"] += 1
                if rec["format_error"]:
                    pv["format_fail"] += 1
                pv["mrs_parsed"] += rec["n_parsed"]
                for m in rec["mrs"]:
                    pv["v1_pass"] += bool(m["v1"])
                    pv["v2_pass"] += bool(m["v2"])
                    pv["certified"] += bool(m["certified"])
    for pv in per_vendor.values():
        pv["cost_usd"] = round(pv["cost_usd"], 4)
        pv["cert_rate_of_parsed"] = (round(pv["certified"] / pv["mrs_parsed"], 4)
                                     if pv["mrs_parsed"] else None)
    summary = {
        "artefact": f"study5_L_battery_summary ({tag})",
        "generated_by": "scripts/study5_mr_elicit.py summary",
        "template_sha256": TEMPLATE_SHA256,
        "puts": list(puts),
        "n_cells": len(puts) * len(MPS),
        "per_vendor": per_vendor,
        "per_family_coverage": per_family,
        "per_put": per_put,
        "total_gateway_cost_usd": round(sum(
            per_vendor[m]["cost_usd"] for m in GATEWAY_MODELS), 4),
    }
    out = d["base"] / "battery_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps({k: summary[k] for k in
                      ("n_cells", "total_gateway_cost_usd")}, indent=2))
    print(f"[summary] wrote {out.relative_to(ROOT)}")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=("draw", "ingest-claude", "certify",
                                    "assemble", "summary", "render"))
    ap.add_argument("--puts", default=None,
                    help="comma-separated PUT ids (e.g. a2,b4 for the pilot)")
    ap.add_argument("--confirmatory", action="store_true",
                    help="use the frozen 28-PUT confirmatory roster")
    ap.add_argument("--tag", default=None,
                    help="v8mr_pilot (pilot) or v8mr (confirmatory; default "
                         "with --confirmatory)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--cell", default=None, help="render: PUT_MPk, e.g. a1_MP2")
    args = ap.parse_args()

    if args.cmd == "render":                          # debugging / audit aid
        put, mp = args.cell.split("_MP")
        print(render_prompt(put, int(mp)))
        return 0

    if args.confirmatory:
        puts = CONFIRMATORY_PUTS
        tag = args.tag or "v8mr"
    else:
        puts = tuple(s.strip() for s in (args.puts or "").split(",") if s.strip())
        tag = args.tag
        if not puts or not tag:
            ap.error("non-confirmatory runs need --puts and --tag "
                     "(e.g. --puts a2,b4 --tag v8mr_pilot)")
    if args.confirmatory and set(puts) & set(PILOT_PUTS):
        ap.error("pilot PUTs may not enter the confirmatory roster")

    fn = {"draw": lambda: cmd_draw(puts, tag, args.workers),
          "ingest-claude": lambda: cmd_ingest_claude(puts, tag),
          "certify": lambda: cmd_certify(puts, tag),
          "assemble": lambda: cmd_assemble(puts, tag),
          "summary": lambda: cmd_summary(puts, tag)}[args.cmd]
    fn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
