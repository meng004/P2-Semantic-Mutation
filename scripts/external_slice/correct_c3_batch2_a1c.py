#!/usr/bin/env python3
"""Gate A1c Batch 2 correction — closes four blockers only.

A1C-FREIA-LOCK-001: fresh dual-arm FrEIA with --require-hashes exit 0
A1C-BUILD-EVIDENCE-001: real dual-arm build attempts (bounded timeout) for
    EXT-trilinos-01, EXT-dealii-01, EXT-castro-01
A1C-HANDOFF-HASH-001: recompute all hashes after redaction
A1C-HANDOFF-VERIFY-CMD-001: record exact verification commands + exits

Does not start Batch 3+. Keeps 29-row membership and sheet A2 PENDING.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get("C3_A1C_WORK", "/tmp/c3_a1c_fix"))
REPRO_ROOT = ROOT / "data" / "external_slice" / "reproduction"
TRIG_ROOT = ROOT / "data" / "external_slice" / "reproducers"
HARNESS_ROOT = TRIG_ROOT / "harnesses"
MEMBERSHIP = ROOT / "data" / "external_slice" / "BATCH2_MEMBERSHIP.json"
SEED = 0
HOST_PY = Path(sys.executable)
NJOBS = str(min(4, os.cpu_count() or 2))
# Declared bounded timeouts for heavy dual-arm build attempts (seconds per arm stage).
HEAVY_CONFIGURE_TIMEOUT = int(os.environ.get("C3_HEAVY_CONFIGURE_TIMEOUT", "600"))
HEAVY_BUILD_TIMEOUT = int(os.environ.get("C3_HEAVY_BUILD_TIMEOUT", "900"))
TOKEN = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN") or ""
REDACT = "<REDACTED_GITHUB_TOKEN>"


class CommandLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def run(
        self,
        command: list[str] | str,
        *,
        cwd: Path | None = None,
        env: dict | None = None,
        label: str = "",
        check: bool = True,
        allow_exit: set[int] | None = None,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess:
        if isinstance(command, str):
            cmd_display = command
            shell = True
            cmd_arg: list[str] | str = command
        else:
            cmd_display = subprocess.list2cmdline(command)
            shell = False
            cmd_arg = command
        # Never persist raw token in the command log.
        if TOKEN:
            cmd_display = cmd_display.replace(TOKEN, REDACT)
        merged = os.environ.copy()
        if env:
            merged.update(env)
        try:
            proc = subprocess.run(
                cmd_arg,
                cwd=str(cwd) if cwd else None,
                env=merged,
                text=True,
                capture_output=True,
                shell=shell,
                check=False,
                timeout=timeout,
            )
        except FileNotFoundError as exc:
            proc = subprocess.CompletedProcess(cmd_arg, 127, "", f"FileNotFoundError: {exc}")
        except subprocess.TimeoutExpired as exc:
            proc = subprocess.CompletedProcess(
                cmd_arg,
                124,
                (exc.stdout or "") if isinstance(exc.stdout, str) else "",
                ((exc.stderr or "") if isinstance(exc.stderr, str) else "")
                + f"\nTIMEOUT after {timeout}s",
            )
        entry = {
            "label": label,
            "command": cmd_display,
            "cwd": str(cwd) if cwd else str(Path.cwd()),
            "exit_code": proc.returncode,
            "stdout_tail": scrub((proc.stdout or "")[-4000:]),
            "stderr_tail": scrub((proc.stderr or "")[-4000:]),
            "timeout_s": timeout,
        }
        self.entries.append(entry)
        print(f"[{label}] exit={proc.returncode}: {cmd_display[:180]}", flush=True)
        allowed = allow_exit or ({0} if check else {proc.returncode})
        if check and proc.returncode not in allowed:
            raise RuntimeError(
                f"command failed ({proc.returncode}): {cmd_display}\n"
                f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
            )
        return proc


def scrub(text: str) -> str:
    if not text:
        return text
    out = text
    if TOKEN:
        out = out.replace(TOKEN, REDACT)
    out = re.sub(r"Bearer\s+ghp_[A-Za-z0-9]+", f"Bearer {REDACT}", out)
    out = re.sub(r"Bearer\s+github_pat_[A-Za-z0-9_]+", f"Bearer {REDACT}", out)
    out = re.sub(r"ghp_[A-Za-z0-9]{20,}", REDACT, out)
    out = re.sub(r"github_pat_[A-Za-z0-9_]{20,}", REDACT, out)
    return out


# Runbook §3 reserved-term pattern (hex escapes keep category tokens out of source).
RUNBOOK_RESERVED_PATTERN = (
    r"(?i)(^|[^[:alnum:]_])(C\x45|O\x53|H\x50|T\x46|S\x49|f\x69ber|strat\x75m)"
    r"([^[:alnum:]_]|$)"
)
# Broader token forms required by A1c re-review (ghp_ / github_pat_ / unredacted Bearer).
TOKEN_SCAN_PATTERN = (
    r"ghp_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"Bearer [A-Za-z0-9][A-Za-z0-9._-]{15,}"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_tree(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix().encode()
        h.update(rel)
        h.update(b"\0")
        h.update(sha256_file(path).encode())
        h.update(b"\0")
    return h.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tool_versions() -> dict:
    out = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    for name, cmd in (
        ("gcc", ["gcc", "--version"]),
        ("g++", ["g++", "--version"]),
        ("gfortran", ["gfortran", "--version"]),
        ("cmake", ["cmake", "--version"]),
        ("make", ["make", "--version"]),
    ):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            out[name] = ((proc.stdout or proc.stderr or "").splitlines() or [""])[0]
        except FileNotFoundError:
            out[name] = "missing"
    return out


def github_archive_url(repo: str, sha: str) -> str:
    return f"https://github.com/{repo}/archive/{sha}.tar.gz"


def download(url: str, dest: Path, log: CommandLog, label: str) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        digest = sha256_file(dest)
        log.entries.append(
            {
                "label": f"{label}:cache-hit",
                "command": f"# reuse {dest} sha256={digest}",
                "cwd": str(ROOT),
                "exit_code": 0,
                "stdout_tail": digest,
                "stderr_tail": "",
                "timeout_s": None,
            }
        )
        return digest
    headers: list[str] = []
    if TOKEN and "github.com" in url:
        headers = ["-H", f"Authorization: Bearer {TOKEN}"]
    log.run(["curl", "-fsSL", "-L", *headers, "-o", str(dest), url], label=label)
    return sha256_file(dest)


def extract_archive(archive: Path, dest: Path, log: CommandLog, label: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    log.run(
        ["tar", "-xzf", str(archive), "--strip-components=1", "-C", str(dest)],
        label=label,
    )


def member_by_id(nid: str) -> dict:
    membership = json.loads(MEMBERSHIP.read_text(encoding="utf-8"))
    for m in membership["members"]:
        if m["neutral_id"] == nid:
            return m
    raise KeyError(nid)


def finalize_case(
    *,
    member: dict,
    log_slice: list[dict],
    buggy_holds: bool | None,
    fixed_holds: bool | None,
    trigger_exits: dict,
    failure_stage: str | None,
    failure_detail: str | None,
    route: str,
    source_hashes: dict | None = None,
    extra_env: dict | None = None,
) -> dict:
    nid = member["neutral_id"]
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    locks = case_dir / "locks"
    locks.mkdir(parents=True, exist_ok=True)

    contrast = (
        buggy_holds is False
        and fixed_holds is True
        and trigger_exits.get("buggy") == 1
        and trigger_exits.get("fixed") == 0
    )
    if failure_stage:
        proposed = "REPRO_FAILED"
    elif contrast:
        proposed = "PASS"
    else:
        proposed = "REPRO_FAILED"
        failure_stage = failure_stage or "contrast"
        failure_detail = failure_detail or (
            f"buggy_holds={buggy_holds} fixed_holds={fixed_holds} exits={trigger_exits}"
        )

    # Redact before writing COMMANDS.json (hash contract: final bytes).
    scrubbed = []
    for e in log_slice:
        scrubbed.append(
            {
                **e,
                "command": scrub(e.get("command", "")),
                "stdout_tail": scrub(e.get("stdout_tail", "")),
                "stderr_tail": scrub(e.get("stderr_tail", "")),
            }
        )
    write_json(case_dir / "COMMANDS.json", {"commands": scrubbed})
    write_json(
        locks / "BUILD_TOOLS.json",
        {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "tools": tool_versions(),
            "heavy_configure_timeout_s": HEAVY_CONFIGURE_TIMEOUT,
            "heavy_build_timeout_s": HEAVY_BUILD_TIMEOUT,
        },
    )
    if source_hashes:
        write_json(locks / "SOURCE_HASHES.json", source_hashes)

    env = {
        "neutral_id": nid,
        "batch": 2,
        "correction": "Gate A1c",
        "route": route,
        "repo": member["repo"],
        "issue_url": member["issue_url"],
        "buggy_sha": member["buggy_sha"],
        "fixed_sha": member["fixed_sha"],
        "seed": SEED,
        "platform": tool_versions(),
        "proposed_crit_dual_arm_repro": proposed,
        "sheet_crit_dual_arm_repro_unchanged": "PENDING",
        "failure_stage": failure_stage,
        "failure_detail": failure_detail,
        "dual_arm_contrast": bool(contrast),
        "trigger_exit_codes": trigger_exits,
        "closed_findings": [],
    }
    if extra_env:
        env.update(extra_env)
    write_json(case_dir / "environment.json", env)

    for arm, holds in (("buggy", buggy_holds), ("fixed", fixed_holds)):
        path = case_dir / f"{arm}.json"
        if not path.is_file():
            write_json(
                path,
                {
                    "neutral_id": nid,
                    "seed": SEED,
                    "arm": arm,
                    "property_holds": holds,
                    "exit_status": None if holds is None else (0 if holds else 1),
                    "failure_stage": failure_stage,
                    "failure_detail": failure_detail,
                },
            )

    stdout_parts = []
    stderr_parts = []
    for arm in ("buggy", "fixed"):
        for kind, parts in (("stdout", stdout_parts), ("stderr", stderr_parts)):
            p = case_dir / f"{arm}.{kind}.txt"
            if p.is_file():
                parts.append(
                    f"=== {arm} {kind} ===\n"
                    + scrub(p.read_text(encoding="utf-8", errors="replace"))
                )
    (case_dir / "stdout.log").write_text("\n".join(stdout_parts) + "\n", encoding="utf-8")
    (case_dir / "stderr.log").write_text("\n".join(stderr_parts) + "\n", encoding="utf-8")

    return {
        "neutral_id": nid,
        "repo": member["repo"],
        "issue_url": member["issue_url"],
        "buggy_sha": member["buggy_sha"],
        "fixed_sha": member["fixed_sha"],
        "seed": SEED,
        "trigger": str((TRIG_ROOT / f"{nid}.py").relative_to(ROOT)),
        "artifact_dir": str(case_dir.relative_to(ROOT)),
        "locks_dir": str(locks.relative_to(ROOT)),
        "command_count": len(scrubbed),
        "buggy_property_holds": buggy_holds,
        "fixed_property_holds": fixed_holds,
        "dual_arm_contrast": bool(contrast),
        "trigger_exit_codes": trigger_exits,
        "proposed_crit_dual_arm_repro": proposed,
        "sheet_crit_dual_arm_repro_unchanged": "PENDING",
        "observation_status": "case-local observed pending Gate A1c re-review",
        "note": "Candidate sheet A2 left PENDING; Gate A1c may promote after zero-blocker re-review.",
        "failure_stage": failure_stage,
        "failure_detail": failure_detail,
        "route": route,
    }


def _parse_pip_artifact_name(filename: str) -> tuple[str, str] | None:
    lower = filename.lower()
    if lower.endswith(".whl"):
        parts = filename[:-4].split("-")
        return parts[0].replace("_", "-"), parts[1]
    if lower.endswith(".tar.gz"):
        stem = filename[: -len(".tar.gz")]
        name, ver = stem.rsplit("-", 1)
        return name.replace("_", "-"), ver
    if lower.endswith(".zip"):
        stem = filename[: -len(".zip")]
        name, ver = stem.rsplit("-", 1)
        return name.replace("_", "-"), ver
    return None


def _write_require_hashes_lock(
    *,
    dl: Path,
    out: Path,
    header_lines: list[str],
    preferred: list[str] | None = None,
) -> tuple[list[str], dict[str, str]]:
    artifact_hashes: dict[str, str] = {}
    req_to_hash: dict[str, str] = {}
    for path in sorted(p for p in dl.iterdir() if p.is_file()):
        parsed = _parse_pip_artifact_name(path.name)
        if parsed is None:
            continue
        name, ver = parsed
        digest = sha256_file(path)
        artifact_hashes[path.name] = digest
        req_to_hash[f"{name}=={ver}"] = digest
    if not req_to_hash:
        raise RuntimeError(f"no hashed artifacts under {dl}")
    ordered: list[str] = []
    for pref in preferred or []:
        # Allow preferred root without +cpu suffix match for torch.
        if pref in req_to_hash and pref not in ordered:
            ordered.append(pref)
            continue
        for r in req_to_hash:
            if r.startswith(pref.split("==", 1)[0] + "==") and r not in ordered:
                ordered.append(r)
                break
    for r in sorted(req_to_hash):
        if r not in ordered:
            ordered.append(r)
    lines = list(header_lines)
    for req in ordered:
        lines.append(f"{req} \\")
        lines.append(f"    --hash=sha256:{req_to_hash[req]}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ordered, artifact_hashes


def build_freia_build_lock(python: Path, locks: Path, log: CommandLog) -> Path:
    """Hash-lock pip/setuptools/wheel/packaging used for exact-source builds."""
    dl = locks / ".download-build"
    if dl.exists():
        shutil.rmtree(dl)
    dl.mkdir(parents=True)
    # Download the packaging/build closure only (no unpinned -U upgrade install).
    pkgs = ["pip", "setuptools", "wheel", "packaging"]
    log.run(
        [str(python), "-m", "pip", "download", "-d", str(dl), *pkgs],
        label="EXT-freia-01:build:pip-download",
    )
    out = locks / "requirements.build.txt"
    ordered, artifact_hashes = _write_require_hashes_lock(
        dl=dl,
        out=out,
        header_lines=[
            "# Hash-locked FrEIA packaging/build closure for Gate A1c re-review",
            f"# python={python}",
            f"# root_packages={pkgs}",
            "# install_with: pip install --require-hashes -r requirements.build.txt",
            "# then: pip install --no-deps --no-build-isolation <exact-source>",
        ],
        preferred=[],
    )
    write_json(
        locks / "BUILD_ARTIFACT_HASHES.json",
        {"artifacts": artifact_hashes, "resolved_requirements": ordered, "root_packages": pkgs},
    )
    shutil.rmtree(dl, ignore_errors=True)
    return out


def build_freia_lock(python: Path, locks: Path, log: CommandLog) -> Path:
    """Download runtime closure via PyTorch CPU + PyPI, write require-hashes lock."""
    dl = locks / ".download-deps"
    if dl.exists():
        shutil.rmtree(dl)
    dl.mkdir(parents=True)
    pkgs = ["numpy==2.2.6", "scipy==1.15.3", "torch==2.7.1"]
    log.run(
        [
            str(python),
            "-m",
            "pip",
            "download",
            "-d",
            str(dl),
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
            "--extra-index-url",
            "https://pypi.org/simple",
            *pkgs,
        ],
        label="EXT-freia-01:deps:pip-download",
    )
    out = locks / "requirements.deps.txt"
    ordered, artifact_hashes = _write_require_hashes_lock(
        dl=dl,
        out=out,
        header_lines=[
            "# Hash-locked FrEIA runtime deps for Gate A1c correction",
            f"# python={python}",
            f"# root_packages={pkgs}",
            "# install_with: pip install --require-hashes "
            "--index-url https://download.pytorch.org/whl/cpu "
            "--extra-index-url https://pypi.org/simple -r requirements.deps.txt",
        ],
        preferred=["numpy==2.2.6", "scipy==1.15.3", "torch==2.7.1"],
    )
    write_json(
        locks / "WHEEL_ARTIFACT_HASHES.json",
        {"artifacts": artifact_hashes, "resolved_requirements": ordered},
    )
    shutil.rmtree(dl, ignore_errors=True)
    return out


def correct_freia(log: CommandLog) -> dict:
    member = member_by_id("EXT-freia-01")
    nid = member["neutral_id"]
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    locks = case_dir / "locks"
    locks.mkdir(parents=True)
    work = WORK / nid
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}

    # Fresh separate envs. Do NOT run unpinned `pip install -U pip wheel setuptools`.
    for arm in ("buggy", "fixed"):
        log.run(
            [str(HOST_PY), "-m", "venv", str(work / f"venv-{arm}")],
            label=f"{nid}:{arm}:venv",
        )

    probe_py = work / "venv-buggy" / "bin" / "python"
    build_lock = build_freia_build_lock(probe_py, locks, log)
    deps_lock = build_freia_lock(probe_py, locks, log)

    for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
        py = work / f"venv-{arm}" / "bin" / "python"
        # 1) Hash-locked packaging/build closure (identical both arms).
        log.run(
            [
                str(py),
                "-m",
                "pip",
                "install",
                "--require-hashes",
                "-r",
                str(build_lock),
            ],
            label=f"{nid}:{arm}:pip-install-build-require-hashes",
            check=True,
            allow_exit={0},
        )
        # 2) Hash-locked runtime deps.
        log.run(
            [
                str(py),
                "-m",
                "pip",
                "install",
                "--require-hashes",
                "--index-url",
                "https://download.pytorch.org/whl/cpu",
                "--extra-index-url",
                "https://pypi.org/simple",
                "-r",
                str(deps_lock),
            ],
            label=f"{nid}:{arm}:pip-install-require-hashes",
            check=True,
            allow_exit={0},
        )
        arch = work / f"{arm}.tar.gz"
        src = work / f"{arm}-src"
        digest = download(
            github_archive_url(member["repo"], sha),
            arch,
            log,
            f"{nid}:{arm}:download-archive",
        )
        extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
        source_hashes[arm] = {
            "archive_sha256": digest,
            "source_tree_sha256": sha256_tree(src),
            "sha": sha,
        }
        # 3) Exact source with --no-build-isolation (no isolated build env resolution).
        src_proc = log.run(
            [
                str(py),
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--no-build-isolation",
                str(src),
            ],
            label=f"{nid}:{arm}:pip-install-freia-exact-source",
            check=True,
            allow_exit={0},
        )
        src_text = (src_proc.stdout or "") + "\n" + (src_proc.stderr or "")
        if "Installing build dependencies" in src_text:
            raise RuntimeError(
                f"{arm}: source install still resolved isolated build dependencies:\n{src_text[-2000:]}"
            )
        harness = HARNESS_ROOT / "freia_spline_roundtrip.py"
        proc = log.run(
            [str(py), str(harness), arm],
            label=f"{nid}:{arm}:trigger",
            check=False,
        )
        text = (proc.stdout or "") + "\n" + (proc.stderr or "")
        (case_dir / f"{arm}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
        (case_dir / f"{arm}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
        prop = ("### VERDICT: PASS" in text) or (
            "VERDICT: PASS" in text and "VIOLATED" not in text
        )
        if "VIOLATED" in text:
            prop = False
        write_json(
            case_dir / f"{arm}.json",
            {
                "neutral_id": nid,
                "seed": SEED,
                "arm": arm,
                "property_holds": prop,
                "exit_status": 0 if prop else 1,
                "observed_output": {
                    "stdout_tail": text[-4000:],
                    "returncode": proc.returncode,
                },
                "expected_property": "round-trip max error < 1e-2 with no crashes",
            },
        )
        exits[arm] = 0 if prop else 1
        holds[arm] = prop
        log.entries.append(
            {
                "label": f"{nid}:{arm}:trigger-normalized-exit",
                "command": f"# property_holds={prop} normalized_exit={exits[arm]}",
                "cwd": str(ROOT),
                "exit_code": exits[arm],
                "stdout_tail": text[-1000:],
                "stderr_tail": "",
                "timeout_s": None,
            }
        )

    result = finalize_case(
        member=member,
        log_slice=log.entries[start:],
        buggy_holds=holds.get("buggy"),
        fixed_holds=holds.get("fixed"),
        trigger_exits=exits,
        failure_stage=None,
        failure_detail=None,
        route="exact-source-python-hashlocked-no-build-isolation",
        source_hashes=source_hashes,
        extra_env={
            "deps_lock": str(deps_lock.relative_to(ROOT)),
            "build_lock": str(build_lock.relative_to(ROOT)),
            "closed_findings": ["A1C-FREIA-LOCK-001"],
            "hash_locked_install": True,
            "hash_locked_build_closure": True,
            "no_build_isolation": True,
            "unhashed_fallback_used": False,
        },
    )
    env_path = case_dir / "environment.json"
    env = json.loads(env_path.read_text(encoding="utf-8"))
    env["closed_findings"] = ["A1C-FREIA-LOCK-001"]
    env["unhashed_fallback_used"] = False
    env["hash_locked_build_closure"] = True
    env["no_build_isolation"] = True
    write_json(env_path, env)
    return result


def attempt_heavy_build(log: CommandLog, nid: str, kind: str) -> dict:
    member = member_by_id(nid)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    # Preserve prior source hashes if present; rebuild case artifacts.
    prior_hashes = {}
    prior_src = case_dir / "locks" / "SOURCE_HASHES.json"
    if prior_src.is_file():
        prior_hashes = json.loads(prior_src.read_text(encoding="utf-8"))
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    source_hashes: dict = dict(prior_hashes)
    exits: dict = {}
    holds: dict = {}
    build_outcomes: dict = {}

    try:
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            digest = download(
                github_archive_url(member["repo"], sha),
                arch,
                log,
                f"{nid}:{arm}:download-archive",
            )
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            source_hashes[arm] = {
                "archive_sha256": digest,
                "source_tree_sha256": sha256_tree(src),
                "sha": sha,
            }
            build = work / f"build-{arm}"
            if build.exists():
                shutil.rmtree(build)
            build.mkdir(parents=True)

            if kind == "trilinos":
                # Minimal Belos-focused attempt; still records real configure/build exits.
                # Force g++: /usr/bin/c++ may be clang selecting a GCC lib dir without libstdc++.
                cfg = log.run(
                    [
                        "cmake",
                        "-S",
                        str(src),
                        "-B",
                        str(build),
                        "-DCMAKE_C_COMPILER=gcc",
                        "-DCMAKE_CXX_COMPILER=g++",
                        "-DCMAKE_BUILD_TYPE=Release",
                        "-DTrilinos_ENABLE_ALL_PACKAGES=OFF",
                        "-DTrilinos_ENABLE_Belos=ON",
                        "-DTrilinos_ENABLE_Epetra=ON",
                        "-DTrilinos_ENABLE_Teuchos=ON",
                        "-DTrilinos_ENABLE_TESTS=OFF",
                        "-DTrilinos_ENABLE_EXAMPLES=OFF",
                        "-DBUILD_SHARED_LIBS=ON",
                        "-DTPL_ENABLE_MPI=OFF",
                        "-DTPL_ENABLE_BLAS=ON",
                        "-DTPL_ENABLE_LAPACK=ON",
                        "-DBLAS_LIBRARY_DIRS=/usr/lib/x86_64-linux-gnu",
                        "-DLAPACK_LIBRARY_DIRS=/usr/lib/x86_64-linux-gnu",
                    ],
                    label=f"{nid}:{arm}:cmake-configure",
                    check=False,
                    timeout=HEAVY_CONFIGURE_TIMEOUT,
                )
                build_outcomes[f"{arm}:configure"] = {
                    "exit_code": cfg.returncode,
                    "timeout_s": HEAVY_CONFIGURE_TIMEOUT,
                }
                if cfg.returncode != 0:
                    (case_dir / f"{arm}.stdout.txt").write_text(cfg.stdout or "", encoding="utf-8")
                    (case_dir / f"{arm}.stderr.txt").write_text(cfg.stderr or "", encoding="utf-8")
                    continue
                bld = log.run(
                    ["cmake", "--build", str(build), f"-j{NJOBS}"],
                    label=f"{nid}:{arm}:cmake-build",
                    check=False,
                    timeout=HEAVY_BUILD_TIMEOUT,
                )
                build_outcomes[f"{arm}:build"] = {
                    "exit_code": bld.returncode,
                    "timeout_s": HEAVY_BUILD_TIMEOUT,
                }
                (case_dir / f"{arm}.stdout.txt").write_text(bld.stdout or "", encoding="utf-8")
                (case_dir / f"{arm}.stderr.txt").write_text(bld.stderr or "", encoding="utf-8")
                if bld.returncode == 0:
                    # Optional harness compile if build succeeded
                    harness = HARNESS_ROOT / "trilinos_belos_singlered_cg.cpp"
                    bin_path = work / f"harness_{arm}"
                    comp = log.run(
                        [
                            "g++",
                            "-std=c++14",
                            "-O2",
                            "-include",
                            "cstdint",
                            str(harness),
                            f"-I{build}/packages/belos/src",
                            f"-I{src}/packages/belos/src",
                            f"-L{build}/packages/belos/src",
                            "-o",
                            str(bin_path),
                        ],
                        label=f"{nid}:{arm}:compile-harness",
                        check=False,
                    )
                    build_outcomes[f"{arm}:compile_harness"] = {"exit_code": comp.returncode}
                    if comp.returncode == 0:
                        trig = log.run(
                            [str(bin_path)],
                            label=f"{nid}:{arm}:trigger",
                            check=False,
                            timeout=300,
                        )
                        text = (trig.stdout or "") + "\n" + (trig.stderr or "")
                        prop = trig.returncode == 0 and "VIOLATED" not in text
                        if "VIOLATED" in text:
                            prop = False
                        write_json(
                            case_dir / f"{arm}.json",
                            {
                                "neutral_id": nid,
                                "seed": SEED,
                                "property_holds": prop,
                                "exit_status": 0 if prop else 1,
                            },
                        )
                        exits[arm] = 0 if prop else 1
                        holds[arm] = prop

            elif kind == "dealii":
                cfg = log.run(
                    [
                        "cmake",
                        "-S",
                        str(src),
                        "-B",
                        str(build),
                        "-DCMAKE_C_COMPILER=gcc",
                        "-DCMAKE_CXX_COMPILER=g++",
                        "-DCMAKE_BUILD_TYPE=Release",
                        "-DDEAL_II_WITH_MPI=OFF",
                        "-DDEAL_II_COMPONENT_EXAMPLES=OFF",
                    ],
                    label=f"{nid}:{arm}:cmake-configure",
                    check=False,
                    timeout=HEAVY_CONFIGURE_TIMEOUT,
                )
                build_outcomes[f"{arm}:configure"] = {
                    "exit_code": cfg.returncode,
                    "timeout_s": HEAVY_CONFIGURE_TIMEOUT,
                }
                (case_dir / f"{arm}.stdout.txt").write_text(cfg.stdout or "", encoding="utf-8")
                (case_dir / f"{arm}.stderr.txt").write_text(cfg.stderr or "", encoding="utf-8")
                if cfg.returncode == 0:
                    bld = log.run(
                        ["cmake", "--build", str(build), f"-j{NJOBS}"],
                        label=f"{nid}:{arm}:cmake-build",
                        check=False,
                        timeout=HEAVY_BUILD_TIMEOUT,
                    )
                    build_outcomes[f"{arm}:build"] = {
                        "exit_code": bld.returncode,
                        "timeout_s": HEAVY_BUILD_TIMEOUT,
                    }
                    (case_dir / f"{arm}.stdout.txt").write_text(
                        (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
                        + "\n"
                        + (bld.stdout or ""),
                        encoding="utf-8",
                    )
                    (case_dir / f"{arm}.stderr.txt").write_text(
                        (case_dir / f"{arm}.stderr.txt").read_text(encoding="utf-8", errors="replace")
                        + "\n"
                        + (bld.stderr or ""),
                        encoding="utf-8",
                    )

            elif kind == "castro":
                # Castro requires AMReX + Microphysics; attempt GNUMake of
                # reacting_convergence and record observed failure/timeout.
                amrex_hint = work / "amrex"
                micro_hint = work / "microphysics"
                if not amrex_hint.exists():
                    amrex_arch = work / "amrex-26.02.tar.gz"
                    download(
                        "https://github.com/AMReX-Codes/amrex/archive/refs/tags/26.02.tar.gz",
                        amrex_arch,
                        log,
                        f"{nid}:shared:download-amrex-26.02",
                    )
                    extract_archive(
                        amrex_arch,
                        amrex_hint,
                        log,
                        f"{nid}:shared:extract-amrex-26.02",
                    )
                if not micro_hint.exists():
                    micro_arch = work / "microphysics-26.02.tar.gz"
                    download(
                        "https://github.com/AMReX-Astro/Microphysics/archive/refs/tags/26.02.tar.gz",
                        micro_arch,
                        log,
                        f"{nid}:shared:download-microphysics-26.02",
                    )
                    extract_archive(
                        micro_arch,
                        micro_hint,
                        log,
                        f"{nid}:shared:extract-microphysics-26.02",
                    )
                ex_dir = src / "Exec" / "reacting_tests" / "reacting_convergence"
                if not ex_dir.is_dir():
                    cfg = log.run(
                        [
                            "cmake",
                            "-S",
                            str(src),
                            "-B",
                            str(build),
                            "-DCMAKE_C_COMPILER=gcc",
                            "-DCMAKE_CXX_COMPILER=g++",
                            f"-DAMReX_ROOT={amrex_hint}",
                            "-DCMAKE_BUILD_TYPE=Release",
                        ],
                        label=f"{nid}:{arm}:cmake-configure",
                        check=False,
                        timeout=HEAVY_CONFIGURE_TIMEOUT,
                    )
                    build_outcomes[f"{arm}:configure"] = {
                        "exit_code": cfg.returncode,
                        "timeout_s": HEAVY_CONFIGURE_TIMEOUT,
                    }
                    (case_dir / f"{arm}.stdout.txt").write_text(cfg.stdout or "", encoding="utf-8")
                    (case_dir / f"{arm}.stderr.txt").write_text(cfg.stderr or "", encoding="utf-8")
                    if cfg.returncode == 0:
                        bld = log.run(
                            ["cmake", "--build", str(build), f"-j{NJOBS}"],
                            label=f"{nid}:{arm}:cmake-build",
                            check=False,
                            timeout=HEAVY_BUILD_TIMEOUT,
                        )
                        build_outcomes[f"{arm}:build"] = {
                            "exit_code": bld.returncode,
                            "timeout_s": HEAVY_BUILD_TIMEOUT,
                        }
                else:
                    env = {
                        "AMREX_HOME": str(amrex_hint),
                        "MICROPHYSICS_HOME": str(micro_hint),
                        "CASTRO_HOME": str(src),
                        "CXX": "g++",
                        "CC": "gcc",
                        "F90": "gfortran",
                    }
                    # Configure-ish probe: realclean then bounded make.
                    cfg = log.run(
                        ["make", "realclean", "DIM=1", "USE_MPI=FALSE", "USE_OMP=FALSE"],
                        cwd=ex_dir,
                        env=env,
                        label=f"{nid}:{arm}:make-realclean",
                        check=False,
                        timeout=min(120, HEAVY_CONFIGURE_TIMEOUT),
                    )
                    build_outcomes[f"{arm}:configure"] = {
                        "exit_code": cfg.returncode,
                        "timeout_s": min(120, HEAVY_CONFIGURE_TIMEOUT),
                    }
                    bld = log.run(
                        [
                            "make",
                            f"-j{NJOBS}",
                            "DIM=1",
                            "USE_MPI=FALSE",
                            "USE_OMP=FALSE",
                            "USE_TRUE_SDC=TRUE",
                        ],
                        cwd=ex_dir,
                        env=env,
                        label=f"{nid}:{arm}:castro-make",
                        check=False,
                        timeout=HEAVY_BUILD_TIMEOUT,
                    )
                    build_outcomes[f"{arm}:build"] = {
                        "exit_code": bld.returncode,
                        "timeout_s": HEAVY_BUILD_TIMEOUT,
                    }
                    stdout_acc = (cfg.stdout or "") + "\n" + (bld.stdout or "")
                    stderr_acc = (cfg.stderr or "") + "\n" + (bld.stderr or "")
                    if bld.returncode == 0:
                        # Prefer TRUESDC binary; fall back to plain gnu.ex.
                        candidates = [
                            ex_dir / "Castro1d.gnu.TRUESDC.ex",
                            ex_dir / "Castro1d.gnu.ex",
                        ]
                        exe = next((p for p in candidates if p.is_file()), None)
                        inputs = ex_dir / "inputs.64"
                        if exe and inputs.is_file():
                            run_dir = work / f"run-{arm}"
                            if run_dir.exists():
                                shutil.rmtree(run_dir)
                            run_dir.mkdir(parents=True)
                            if (ex_dir / "helm_table.dat").is_file():
                                shutil.copy2(ex_dir / "helm_table.dat", run_dir / "helm_table.dat")
                            trig = log.run(
                                [
                                    str(exe),
                                    str(inputs),
                                    "castro.sdc_order=2",
                                    "castro.time_integration_method=2",
                                    "castro.ppm_type=0",
                                    "castro.sdc_solver=1",
                                    "castro.use_retry=0",
                                    "max_step=2",
                                    "amr.plot_int=-1",
                                ],
                                cwd=run_dir,
                                env=env,
                                label=f"{nid}:{arm}:trigger",
                                check=False,
                                timeout=300,
                            )
                            build_outcomes[f"{arm}:trigger"] = {
                                "exit_code": trig.returncode,
                                "timeout_s": 300,
                            }
                            stdout_acc += "\n" + (trig.stdout or "")
                            stderr_acc += "\n" + (trig.stderr or "")
                            text = (trig.stdout or "") + "\n" + (trig.stderr or "")
                            # Without fextrema discrimination, treat non-crash as holds;
                            # issue contrast requires dens-dependent floor and is not
                            # claimed here unless an explicit VIOLATED/PASS marker appears.
                            prop = trig.returncode == 0 and "VIOLATED" not in text
                            if "VIOLATED" in text:
                                prop = False
                            if "VERDICT: PASS" in text:
                                prop = True
                            write_json(
                                case_dir / f"{arm}.json",
                                {
                                    "neutral_id": nid,
                                    "seed": SEED,
                                    "arm": arm,
                                    "property_holds": prop,
                                    "exit_status": 0 if prop else 1,
                                    "note": "trigger executed after observed successful dual-arm build",
                                },
                            )
                            exits[arm] = 0 if prop else 1
                            holds[arm] = prop
                    (case_dir / f"{arm}.stdout.txt").write_text(stdout_acc, encoding="utf-8")
                    (case_dir / f"{arm}.stderr.txt").write_text(stderr_acc, encoding="utf-8")
            else:
                raise ValueError(kind)

        # Determine failure stage from observed outcomes only.
        failure_stage = None
        failure_detail = None
        if holds.get("buggy") is False and holds.get("fixed") is True:
            failure_stage = None
            failure_detail = None
        else:
            # Look for timeout or non-zero build/configure
            timed_out = any(
                v.get("exit_code") == 124 for v in build_outcomes.values() if isinstance(v, dict)
            )
            non_zero = any(
                v.get("exit_code", 0) not in (0,) for v in build_outcomes.values() if isinstance(v, dict)
            )
            if timed_out:
                failure_stage = "build"
                failure_detail = (
                    f"REPRO_FAILED:build - observed timeout during dual-arm attempt "
                    f"(configure_timeout_s={HEAVY_CONFIGURE_TIMEOUT}, "
                    f"build_timeout_s={HEAVY_BUILD_TIMEOUT}); outcomes={build_outcomes}"
                )
            elif non_zero or not build_outcomes:
                failure_stage = "build"
                failure_detail = (
                    f"REPRO_FAILED:build - observed configure/build failure on dual-arm attempt; "
                    f"outcomes={build_outcomes}"
                )
            else:
                failure_stage = "contrast"
                failure_detail = (
                    f"builds completed but issue-described contrast not demonstrated; "
                    f"outcomes={build_outcomes}"
                )

        result = finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=failure_stage,
            failure_detail=failure_detail,
            route="exact-source-cmake-timeout-bounded",
            source_hashes=source_hashes,
            extra_env={
                "closed_findings": ["A1C-BUILD-EVIDENCE-001"],
                "build_outcomes": build_outcomes,
                "configure_timeout_s": HEAVY_CONFIGURE_TIMEOUT,
                "build_timeout_s": HEAVY_BUILD_TIMEOUT,
            },
        )
        env_path = case_dir / "environment.json"
        env = json.loads(env_path.read_text(encoding="utf-8"))
        env["closed_findings"] = ["A1C-BUILD-EVIDENCE-001"]
        env["build_outcomes"] = build_outcomes
        write_json(env_path, env)
        return result
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build",
            failure_detail=f"REPRO_FAILED:build - exception during observed attempt: {exc}",
            route="exact-source-cmake-timeout-bounded",
            source_hashes=source_hashes,
            extra_env={"closed_findings": ["A1C-BUILD-EVIDENCE-001"], "build_outcomes": build_outcomes},
        )


def load_case_result_from_disk(member: dict) -> dict:
    nid = member["neutral_id"]
    case_dir = REPRO_ROOT / nid
    env = json.loads((case_dir / "environment.json").read_text(encoding="utf-8"))
    buggy_holds = fixed_holds = None
    for arm in ("buggy", "fixed"):
        jp = case_dir / f"{arm}.json"
        if jp.exists():
            d = json.loads(jp.read_text(encoding="utf-8"))
            if arm == "buggy":
                buggy_holds = d.get("property_holds")
            else:
                fixed_holds = d.get("property_holds")
    cmd_p = case_dir / "COMMANDS.json"
    ncmd = len(json.loads(cmd_p.read_text(encoding="utf-8")).get("commands", [])) if cmd_p.exists() else 0
    return {
        "neutral_id": nid,
        "repo": member["repo"],
        "issue_url": member["issue_url"],
        "buggy_sha": member["buggy_sha"],
        "fixed_sha": member["fixed_sha"],
        "seed": SEED,
        "trigger": str((TRIG_ROOT / f"{nid}.py").relative_to(ROOT)),
        "artifact_dir": str(case_dir.relative_to(ROOT)),
        "locks_dir": str((case_dir / "locks").relative_to(ROOT)),
        "command_count": ncmd,
        "buggy_property_holds": buggy_holds,
        "fixed_property_holds": fixed_holds,
        "dual_arm_contrast": env.get("dual_arm_contrast"),
        "trigger_exit_codes": env.get("trigger_exit_codes", {}),
        "proposed_crit_dual_arm_repro": env.get("proposed_crit_dual_arm_repro"),
        "sheet_crit_dual_arm_repro_unchanged": "PENDING",
        "observation_status": "case-local observed pending Gate A1c re-review",
        "note": "Candidate sheet A2 left PENDING; Gate A1c may promote after zero-blocker re-review.",
        "failure_stage": env.get("failure_stage"),
        "failure_detail": env.get("failure_detail"),
        "route": env.get("route"),
    }


def rebuild_global_command_log() -> list[dict]:
    membership = json.loads(MEMBERSHIP.read_text(encoding="utf-8"))
    all_cmds: list[dict] = []
    for m in membership["members"]:
        cp = REPRO_ROOT / m["neutral_id"] / "COMMANDS.json"
        if not cp.exists():
            continue
        cmds = json.loads(cp.read_text(encoding="utf-8")).get("commands", [])
        # Ensure redaction on every record before aggregation.
        for e in cmds:
            all_cmds.append(
                {
                    **e,
                    "command": scrub(e.get("command", "")),
                    "stdout_tail": scrub(e.get("stdout_tail", "")),
                    "stderr_tail": scrub(e.get("stderr_tail", "")),
                }
            )
    write_json(
        REPRO_ROOT / "BATCH2_COMMAND_LOG.json",
        {"commands": all_cmds, "command_count": len(all_cmds)},
    )
    return all_cmds


def redact_all_command_artifacts() -> None:
    for path in list(REPRO_ROOT.rglob("COMMANDS.json")) + [REPRO_ROOT / "BATCH2_COMMAND_LOG.json"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        text2 = scrub(text)
        if text2 != text:
            path.write_text(text2, encoding="utf-8")


def hash_tree_files(case_dir: Path) -> dict:
    files = {}
    for name in [
        "environment.json",
        "COMMANDS.json",
        "buggy.json",
        "fixed.json",
        "stdout.log",
        "stderr.log",
    ]:
        p = case_dir / name
        if p.exists():
            files[name] = sha256_file(p)
    locks = case_dir / "locks"
    if locks.exists():
        for p in sorted(locks.rglob("*")):
            if p.is_file():
                files[f"locks/{p.relative_to(locks).as_posix()}"] = sha256_file(p)
    return files


def run_verification(log: CommandLog) -> dict:
    """Record exact verification commands + exits (A1C-HANDOFF-VERIFY-CMD-001)."""
    start = len(log.entries)
    checks = {}

    # admission
    proc = log.run(
        [
            str(HOST_PY),
            "scripts/check_external_admission.py",
            "--sheet",
            "data/external_slice/admission_sheet.cursor_candidate.csv",
        ],
        cwd=ROOT,
        env={"PYTHONPATH": "src"},
        label="verify:admission_checker",
        check=False,
    )
    checks["admission_checker"] = {
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
    }

    # pytest
    proc = log.run(
        [str(HOST_PY), "-m", "pytest", "-q"],
        cwd=ROOT,
        env={"PYTHONPATH": "src"},
        label="verify:pytest",
        check=False,
    )
    checks["pytest"] = {
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
    }

    # compileall runner + reproducers
    proc = log.run(
        [
            str(HOST_PY),
            "-m",
            "compileall",
            "-q",
            "scripts/external_slice/run_c3_batch2_readiness.py",
            "scripts/external_slice/correct_c3_batch2_a1c.py",
            "data/external_slice/reproducers",
        ],
        cwd=ROOT,
        label="verify:compileall",
        check=False,
    )
    checks["compileall"] = {"exit_code": proc.returncode}

    # Runbook §3 reserved-term scan over decision-level Batch 2 artifacts.
    # Expected clean semantics: rg exit 1 (no match) => checker exit 0.
    # Use bash -lc + shlex.quote so the stored command keeps functional \xNN
    # escapes and is copy-pasteable; normalize rg exits inside the shell.
    decision_paths: list[str] = [
        "data/external_slice/readiness_batch2.json",
        "data/external_slice/BATCH2_MEMBERSHIP.json",
        "data/external_slice/HANDOFF_REPRO_BATCH2.json",
    ]
    for nid_path in sorted(REPRO_ROOT.glob("EXT-*")):
        for name in ("environment.json", "buggy.json", "fixed.json"):
            p = nid_path / name
            if p.is_file():
                decision_paths.append(str(p.relative_to(ROOT)))
    leak_shell = (
        "rg -n "
        + shlex.quote(RUNBOOK_RESERVED_PATTERN)
        + " "
        + " ".join(shlex.quote(p) for p in decision_paths)
        + "; ec=$?; if [ $ec -eq 1 ]; then exit 0; "
        "elif [ $ec -eq 0 ]; then echo 'RESERVED_TERM_LEAK'; exit 1; "
        "else exit $ec; fi"
    )
    proc = log.run(
        ["bash", "-lc", leak_shell],
        cwd=ROOT,
        label="verify:leak_scan_reserved_runbook",
        check=False,
    )
    checks["leak_scan_reserved_runbook"] = {
        "exit_code": proc.returncode,
        "expected_clean_rg_exit": 1,
        "expected_checker_exit": 0,
        "pattern": RUNBOOK_RESERVED_PATTERN,
        "scope": "decision-level Batch 2 artifacts",
        "stdout_tail": (proc.stdout or "")[-1000:],
    }
    # Keep legacy key for handoff consumers that still look for leak_scan_neutral.
    checks["leak_scan_neutral"] = checks["leak_scan_reserved_runbook"]

    # Token scan: ghp_ / github_pat_ / unredacted Bearer (not <REDACTED...>).
    token_paths = [
        "data/external_slice/reproduction",
        "data/external_slice/HANDOFF_REPRO_BATCH2.json",
        "data/external_slice/readiness_batch2.json",
        "data/external_slice/BATCH2_MEMBERSHIP.json",
    ]
    token_shell = (
        "rg -n "
        + shlex.quote(TOKEN_SCAN_PATTERN)
        + " "
        + " ".join(shlex.quote(p) for p in token_paths)
        + "; ec=$?; if [ $ec -eq 1 ]; then exit 0; "
        "elif [ $ec -eq 0 ]; then echo 'TOKEN_LEAK'; exit 1; "
        "else exit $ec; fi"
    )
    proc = log.run(
        ["bash", "-lc", token_shell],
        cwd=ROOT,
        label="verify:token_scan",
        check=False,
    )
    checks["token_scan"] = {
        "exit_code": proc.returncode,
        "expected_clean_rg_exit": 1,
        "expected_checker_exit": 0,
        "pattern": TOKEN_SCAN_PATTERN,
        "stdout_tail": (proc.stdout or "")[-1000:],
    }

    # membership consistency
    proc = log.run(
        [
            str(HOST_PY),
            "-c",
            "import csv,json; "
            "m=json.load(open('data/external_slice/BATCH2_MEMBERSHIP.json')); "
            "r=json.load(open('data/external_slice/readiness_batch2.json')); "
            "ids=[x['neutral_id'] for x in m['members']]; "
            "assert len(ids)==29==len(set(ids)); "
            "assert [c['neutral_id'] for c in r['cases']]==ids; "
            "rows=list(csv.DictReader(open('data/external_slice/admission_sheet.cursor_candidate.csv'))); "
            "assert all(row['crit_dual_arm_repro']=='PENDING' for row in rows if row['neutral_id'] in set(ids)); "
            "print('membership_ok', len(ids))",
        ],
        cwd=ROOT,
        label="verify:membership_and_sheet_pending",
        check=False,
    )
    checks["membership_and_sheet_pending"] = {
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-500:],
    }

    return {"checks": checks, "commands": log.entries[start:]}


def handoff_hash_checker(handoff_path: Path) -> int:
    """Exit 0 iff every declared hash matches committed bytes."""
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    bad = []
    for name, digest in handoff.get("outputs", {}).get("files", {}).items():
        # files may be bare names under data/external_slice or reproduction
        candidates = [
            ROOT / "data" / "external_slice" / name,
            ROOT / "data" / "external_slice" / "reproduction" / name,
            ROOT / name,
        ]
        path = next((p for p in candidates if p.is_file()), None)
        if path is None:
            bad.append((name, "missing", digest))
            continue
        actual = sha256_file(path)
        if actual != digest:
            bad.append((name, actual, digest))
    for nid, files in handoff.get("outputs", {}).get("per_case_artifact_sha256", {}).items():
        case_dir = REPRO_ROOT / nid
        for rel, digest in files.items():
            path = case_dir / rel
            if not path.is_file():
                bad.append((f"{nid}:{rel}", "missing", digest))
                continue
            actual = sha256_file(path)
            if actual != digest:
                bad.append((f"{nid}:{rel}", actual, digest))
    report = ROOT / "data" / "external_slice" / "reproduction" / "BATCH2_HANDOFF_HASH_CHECK.json"
    write_json(report, {"ok": not bad, "mismatches": bad, "checked_at": datetime.now(timezone.utc).isoformat()})
    if bad:
        print("HASH_MISMATCHES", len(bad))
        for row in bad[:20]:
            print(row)
        return 1
    print("HASH_CHECK_OK")
    return 0


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    log = CommandLog()
    membership = json.loads(MEMBERSHIP.read_text(encoding="utf-8"))
    skip_freia = os.environ.get("C3_A1C_SKIP_FREIA", "").strip() in {"1", "true", "yes"}

    if skip_freia:
        print("===== FrEIA correction SKIPPED (reuse disk artifacts) =====", flush=True)
        freia = load_case_result_from_disk(member_by_id("EXT-freia-01"))
    else:
        print("===== FrEIA correction =====", flush=True)
        freia = correct_freia(log)
    print("FrEIA proposed", freia["proposed_crit_dual_arm_repro"], freia.get("trigger_exit_codes"))

    print("===== Heavy build evidence =====", flush=True)
    heavy = {}
    heavy_all = (
        ("EXT-trilinos-01", "trilinos"),
        ("EXT-dealii-01", "dealii"),
        ("EXT-castro-01", "castro"),
    )
    skip_heavy = os.environ.get("C3_A1C_SKIP_HEAVY", "").strip() in {"1", "true", "yes"}
    only = {
        x.strip()
        for x in os.environ.get("C3_A1C_HEAVY_ONLY", "").split(",")
        if x.strip()
    }
    for nid, kind in heavy_all:
        if skip_heavy or (only and nid not in only):
            print(f"--- {nid} SKIPPED (reuse disk) ---", flush=True)
            heavy[nid] = load_case_result_from_disk(member_by_id(nid))
            continue
        print(f"--- {nid} ---", flush=True)
        t0 = time.time()
        heavy[nid] = attempt_heavy_build(log, nid, kind)
        print(
            nid,
            heavy[nid]["proposed_crit_dual_arm_repro"],
            heavy[nid].get("failure_stage"),
            f"elapsed={time.time()-t0:.1f}s",
            flush=True,
        )

    # Rebuild readiness from disk for all 29 (corrected cases overwritten above).
    results = []
    for m in membership["members"]:
        results.append(load_case_result_from_disk(m))

    readiness = {
        "batch": 2,
        "batch_name": "remaining-29-after-batch1",
        "correction_of": "01acdbbf6ffd220f9b768ffd386f02cc7fff591b",
        "closed_findings": [
            "A1C-HANDOFF-HASH-001",
            "A1C-FREIA-LOCK-001",
            "A1C-BUILD-EVIDENCE-001",
            "A1C-HANDOFF-VERIFY-CMD-001",
        ],
        "frozen_membership": "data/external_slice/BATCH2_MEMBERSHIP.json",
        "frozen_at_commit": membership.get("frozen_at_commit"),
        "gate_a1b_verdict": membership.get("gate_a1b_verdict"),
        "selection_rule": membership.get("selection_rule"),
        "cases": results,
        "counts": {
            "batch_size": len(results),
            "proposed_PASS": sum(1 for r in results if r.get("proposed_crit_dual_arm_repro") == "PASS"),
            "proposed_REPRO_FAILED": sum(
                1 for r in results if r.get("proposed_crit_dual_arm_repro") == "REPRO_FAILED"
            ),
        },
        "not_started": [
            "Batch 3+",
            "C4 annotation support",
            "human labelling",
            "category-map freeze",
            "predictive freeze",
            "detection-run execution",
            "canonical admission freeze",
        ],
        "sheet_mutation_policy": "candidate sheet A2 fields remain PENDING",
    }
    write_json(ROOT / "data" / "external_slice" / "readiness_batch2.json", readiness)

    # Redact ALL command artifacts, then rebuild global log from scrubbed per-case files.
    redact_all_command_artifacts()
    all_cmds = rebuild_global_command_log()
    redact_all_command_artifacts()

    # Verification commands (recorded after corrections).
    verify = run_verification(log)
    write_json(
        REPRO_ROOT / "BATCH2_VERIFICATION_LOG.json",
        {
            "checks": verify["checks"],
            "commands": [
                {
                    **e,
                    "command": scrub(e.get("command", "")),
                    "stdout_tail": scrub(e.get("stdout_tail", "")),
                    "stderr_tail": scrub(e.get("stderr_tail", "")),
                }
                for e in verify["commands"]
            ],
        },
    )

    # Final redaction sweep before hashing.
    redact_all_command_artifacts()
    for path in REPRO_ROOT.rglob("*.log"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            text2 = scrub(text)
            if text2 != text:
                path.write_text(text2, encoding="utf-8")

    # Compute hashes from final committed-byte candidates.
    outputs_files = {
        "readiness_batch2.json": sha256_file(ROOT / "data/external_slice/readiness_batch2.json"),
        "BATCH2_MEMBERSHIP.json": sha256_file(MEMBERSHIP),
        "BATCH2_COMMAND_LOG.json": sha256_file(REPRO_ROOT / "BATCH2_COMMAND_LOG.json"),
        "BATCH2_VERIFICATION_LOG.json": sha256_file(REPRO_ROOT / "BATCH2_VERIFICATION_LOG.json"),
        "admission_sheet.cursor_candidate.csv": sha256_file(
            ROOT / "data/external_slice/admission_sheet.cursor_candidate.csv"
        ),
    }
    per_case = {}
    for m in membership["members"]:
        per_case[m["neutral_id"]] = hash_tree_files(REPRO_ROOT / m["neutral_id"])

    case_results = []
    for r in results:
        case_results.append(
            {
                "neutral_id": r["neutral_id"],
                "proposed": r["proposed_crit_dual_arm_repro"],
                "trigger_exit_codes": r.get("trigger_exit_codes"),
                "failure_stage": r.get("failure_stage"),
            }
        )

    handoff = {
        "task": "C3 readiness Batch 2 Gate A1c correction (re-review round 2)",
        "gate": "A1c",
        "branch": "cursor/grok-phase3-c3-readiness",
        "cloud_agent": "bc-1d216e6e-25c0-46ef-9f68-b1d417f18f57",
        "baseline_commit": "01acdbbf6ffd220f9b768ffd386f02cc7fff591b",
        "blocked_audit_commit": "649d0c208496d64a19bacaa43660aab25d8e688c",
        "membership_commit": "c94684faadbb4b02f8685360255cc374c15183c8",
        "correction_of": "01acdbbf6ffd220f9b768ffd386f02cc7fff591b",
        "prior_correction_handoff": "01acdbbf6ffd220f9b768ffd386f02cc7fff591b",
        "closed_findings": [
            "A1C-HANDOFF-HASH-001",
            "A1C-FREIA-LOCK-001",
            "A1C-BUILD-EVIDENCE-001",
            "A1C-HANDOFF-VERIFY-CMD-001",
        ],
        "batch": {
            "number": 2,
            "member_count": 29,
            "selection": "unchanged frozen BATCH2_MEMBERSHIP.json",
            "replacement_policy": "forbidden",
            "sheet_a2_policy": "PENDING unchanged; proposed verdicts only in readiness_batch2.json",
            "stop_after_push": True,
            "batch3_started": False,
        },
        "counts": readiness["counts"],
        "case_results": case_results,
        "commands": {
            "case_execution_log": "data/external_slice/reproduction/BATCH2_COMMAND_LOG.json",
            "case_command_count": len(all_cmds),
            "verification_log": "data/external_slice/reproduction/BATCH2_VERIFICATION_LOG.json",
            "verification_command_count": len(verify["commands"]),
            "hash_check_script": "scripts/external_slice/check_batch2_handoff_hashes.py",
        },
        "exit_codes": {
            "per_case_trigger": {
                c["neutral_id"]: c.get("trigger_exit_codes") for c in results
            },
            "admission_checker": verify["checks"]["admission_checker"]["exit_code"],
            "pytest": verify["checks"]["pytest"]["exit_code"],
            "compileall": verify["checks"]["compileall"]["exit_code"],
            "leak_scan_reserved_runbook": verify["checks"]["leak_scan_reserved_runbook"][
                "exit_code"
            ],
            "leak_scan_neutral": verify["checks"]["leak_scan_neutral"]["exit_code"],
            "token_scan": verify["checks"]["token_scan"]["exit_code"],
            "membership_and_sheet_pending": verify["checks"]["membership_and_sheet_pending"][
                "exit_code"
            ],
        },
        "inputs": {
            "BATCH2_MEMBERSHIP.json": outputs_files["BATCH2_MEMBERSHIP.json"],
            "admission_sheet.cursor_candidate.csv": outputs_files[
                "admission_sheet.cursor_candidate.csv"
            ],
            "seed": 0,
            "heavy_configure_timeout_s": HEAVY_CONFIGURE_TIMEOUT,
            "heavy_build_timeout_s": HEAVY_BUILD_TIMEOUT,
        },
        "outputs": {
            "files": outputs_files,
            "per_case_artifact_sha256": per_case,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "tools": tool_versions(),
        },
        "failures": [c for c in case_results if c["proposed"] == "REPRO_FAILED"],
        "retries": [
            "A1c-r2 FrEIA packaging/build closure hash-locked; exact source via --no-build-isolation",
            "A1c-r2 verification uses runbook reserved pattern + ghp_/github_pat_/Bearer token scan",
            "A1c-r2 handoff hashes recomputed after redaction",
        ],
        "unresolved_findings": [],
        "not_started": readiness["not_started"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "admission_checker": scrub(
            verify["checks"]["admission_checker"].get("stdout_tail", "")[:300]
        ),
        "pytest": scrub(verify["checks"]["pytest"].get("stdout_tail", "")[-300:]),
    }
    handoff_path = ROOT / "data" / "external_slice" / "HANDOFF_REPRO_BATCH2.json"
    write_json(handoff_path, handoff)

    # Write hash checker helper and run it.
    checker = ROOT / "scripts" / "external_slice" / "check_batch2_handoff_hashes.py"
    checker.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import sys\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
        "from correct_c3_batch2_a1c import handoff_hash_checker, ROOT\n"
        "raise SystemExit(handoff_hash_checker(ROOT / 'data/external_slice/HANDOFF_REPRO_BATCH2.json'))\n",
        encoding="utf-8",
    )
    checker.chmod(0o755)
    hc = log.run(
        [str(HOST_PY), str(checker)],
        cwd=ROOT,
        label="verify:handoff_hash_checker",
        check=False,
    )
    # Update verification log + handoff exit for hash checker, then REHASH final files.
    vlog_path = REPRO_ROOT / "BATCH2_VERIFICATION_LOG.json"
    vlog = json.loads(vlog_path.read_text(encoding="utf-8"))
    vlog["checks"]["handoff_hash_checker"] = {
        "exit_code": hc.returncode,
        "stdout_tail": scrub((hc.stdout or "")[-1000:]),
    }
    vlog["commands"].append(
        {
            "label": "verify:handoff_hash_checker",
            "command": scrub(subprocess.list2cmdline([str(HOST_PY), str(checker)])),
            "cwd": str(ROOT),
            "exit_code": hc.returncode,
            "stdout_tail": scrub((hc.stdout or "")[-1000:]),
            "stderr_tail": scrub((hc.stderr or "")[-1000:]),
            "timeout_s": None,
        }
    )
    write_json(vlog_path, vlog)

    # Because verification log and handoff changed, recompute file hashes once more
    # and rewrite handoff, then re-run hash checker to confirm fixed point.
    outputs_files["BATCH2_VERIFICATION_LOG.json"] = sha256_file(vlog_path)
    outputs_files["readiness_batch2.json"] = sha256_file(
        ROOT / "data/external_slice/readiness_batch2.json"
    )
    outputs_files["BATCH2_COMMAND_LOG.json"] = sha256_file(REPRO_ROOT / "BATCH2_COMMAND_LOG.json")
    per_case = {m["neutral_id"]: hash_tree_files(REPRO_ROOT / m["neutral_id"]) for m in membership["members"]}
    handoff["outputs"]["files"] = outputs_files
    handoff["outputs"]["per_case_artifact_sha256"] = per_case
    handoff["exit_codes"]["handoff_hash_checker"] = None  # filled after final check
    handoff["commands"]["verification_command_count"] = len(vlog["commands"])
    write_json(handoff_path, handoff)

    final_hc = handoff_hash_checker(handoff_path)
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    handoff["exit_codes"]["handoff_hash_checker"] = final_hc
    # Updating handoff changes its own content but handoff is not in outputs.files self-hash.
    write_json(handoff_path, handoff)
    # Re-check once more after writing exit code (handoff file itself not in per-case hashes).
    final_hc2 = handoff_hash_checker(handoff_path)
    print("final_hash_checker", final_hc2)
    print(json.dumps(readiness["counts"], indent=2))
    print(
        "freia",
        freia["proposed_crit_dual_arm_repro"],
        freia.get("trigger_exit_codes"),
    )
    for nid in ("EXT-trilinos-01", "EXT-dealii-01", "EXT-castro-01"):
        print(nid, heavy[nid]["proposed_crit_dual_arm_repro"], heavy[nid].get("failure_stage"))
    return 0 if final_hc2 == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
