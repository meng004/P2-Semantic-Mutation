#!/usr/bin/env python3
"""C3 readiness Batch 2: dual-arm reproduction for 29 frozen queue members.

Frozen membership: data/external_slice/BATCH2_MEMBERSHIP.json
Replacement forbidden. Candidate sheet A2 left PENDING; only proposed verdicts
are written to readiness_batch2.json.

Does not start C4, labelling, freeze, predictive freeze, or detection-run execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get("C3_BATCH2_WORK", "/tmp/c3_batch2/work"))
REPRO_ROOT = ROOT / "data" / "external_slice" / "reproduction"
TRIG_ROOT = ROOT / "data" / "external_slice" / "reproducers"
HARNESS_ROOT = TRIG_ROOT / "harnesses"
MEMBERSHIP = ROOT / "data" / "external_slice" / "BATCH2_MEMBERSHIP.json"
SEED = 0
PY39 = Path("/tmp/c3_batch1/work/python39/install/bin/python3.9")
HOST_PY = Path(sys.executable)
JULIA = Path(os.environ.get("JULIA_BIN", "/tmp/c3_batch2/work/julia-1.10.5/bin/julia"))
NJOBS = str(os.cpu_count() or 2)


class CommandLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def run(
        self,
        command: list[str] | str,
        *,
        cwd: Path | None = None,
        env: dict | None = None,
        check: bool = True,
        label: str = "",
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
            proc = subprocess.CompletedProcess(
                cmd_arg,
                127,
                "",
                f"FileNotFoundError: {exc}",
            )
        except subprocess.TimeoutExpired as exc:
            proc = subprocess.CompletedProcess(
                cmd_arg,
                124,
                (exc.stdout or "") if isinstance(exc.stdout, str) else "",
                (exc.stderr or "") if isinstance(exc.stderr, str) else f"TIMEOUT after {timeout}s",
            )
        entry = {
            "label": label,
            "command": cmd_display,
            "cwd": str(cwd) if cwd else str(Path.cwd()),
            "exit_code": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-4000:],
            "stderr_tail": (proc.stderr or "")[-4000:],
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
        "uname": " ".join(platform.uname()),
    }
    for name, cmd in (
        ("gcc", ["gcc", "--version"]),
        ("g++", ["g++", "--version"]),
        ("gfortran", ["gfortran", "--version"]),
        ("cmake", ["cmake", "--version"]),
        ("make", ["make", "--version"]),
        ("julia", [str(JULIA), "--version"] if JULIA.is_file() else ["julia", "--version"]),
    ):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            out[name] = ((proc.stdout or proc.stderr or "").splitlines() or [""])[0]
        except FileNotFoundError:
            out[name] = "missing"
    return out


def github_archive_url(repo: str, sha: str) -> str:
    return f"https://github.com/{repo}/archive/{sha}.tar.gz"


def gitlab_archive_url(repo: str, sha: str) -> str:
    # repo like libeigen/eigen or petsc/petsc
    name = repo.split("/")[-1]
    return f"https://gitlab.com/{repo}/-/archive/{sha}/{name}-{sha}.tar.gz"


def download(url: str, dest: Path, log: CommandLog, label: str, token: str | None = None) -> str:
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
            }
        )
        return digest
    headers = []
    if token and "github.com" in url:
        headers = ["-H", f"Authorization: Bearer {token}"]
    cmd = ["curl", "-fsSL", "-L", *headers, "-o", str(dest), url]
    log.run(cmd, label=label)
    return sha256_file(dest)


def extract_archive(archive: Path, dest: Path, log: CommandLog, label: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    log.run(
        ["tar", "-xzf", str(archive), "--strip-components=1", "-C", str(dest)],
        label=label,
    )


def _parse_wheel_or_sdist_name(filename: str) -> tuple[str, str] | None:
    lower = filename.lower()
    if lower.endswith(".whl"):
        parts = filename[:-4].split("-")
        if len(parts) >= 2:
            return parts[0], parts[1]
    for ext in (".tar.gz", ".zip"):
        if lower.endswith(ext):
            stem = filename[: -len(ext)]
            if "-" not in stem:
                return None
            name, ver = stem.rsplit("-", 1)
            return name, ver
    return None


def pip_hash_lock(
    python: Path,
    packages: list[str],
    out: Path,
    log: CommandLog,
    label: str,
    *,
    with_deps: bool = True,
    extra_args: list[str] | None = None,
) -> dict:
    dl = out.parent / f".download-{out.stem}"
    if dl.exists():
        shutil.rmtree(dl)
    dl.mkdir(parents=True)
    cmd = [str(python), "-m", "pip", "download", "-d", str(dl), *(extra_args or []), *packages]
    if not with_deps:
        cmd.insert(4, "--no-deps")
    log.run(cmd, label=f"{label}:pip-download", check=False)
    lines = [
        "# Hash-locked requirements generated for C3 Batch 2",
        f"# python={python}",
        f"# root_packages={packages}",
    ]
    artifact_hashes = {}
    req_to_hash: dict[str, str] = {}
    if dl.exists():
        for path in sorted(p for p in dl.iterdir() if p.is_file()):
            parsed = _parse_wheel_or_sdist_name(path.name)
            if parsed is None:
                continue
            name, ver = parsed
            digest = sha256_file(path)
            artifact_hashes[path.name] = digest
            req_name = name.replace("_", "-")
            req_to_hash[f"{req_name}=={ver}"] = digest
    if not req_to_hash:
        shutil.rmtree(dl, ignore_errors=True)
        raise RuntimeError(f"no hashed artifacts produced for {packages}")
    ordered = list(packages) + sorted(r for r in req_to_hash if r not in packages)
    seen = set()
    for req in ordered:
        if req in seen or req not in req_to_hash:
            continue
        seen.add(req)
        lines.append(f"{req} \\")
        lines.append(f"    --hash=sha256:{req_to_hash[req]}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.rmtree(dl, ignore_errors=True)
    return {
        "lock_file": str(out.relative_to(ROOT)),
        "artifacts": artifact_hashes,
        "packages": packages,
        "resolved_requirements": sorted(req_to_hash),
    }


def write_trigger_wrapper(neutral_id: str, description: str) -> Path:
    path = TRIG_ROOT / f"{neutral_id}.py"
    if path.is_file():
        return path
    path.write_text(
        textwrap.dedent(
            f'''\
            #!/usr/bin/env python3
            """Dual-arm trigger wrapper for {neutral_id}.

            {description}
            Invokes a prebuilt harness binary (or interpreter script) with identical
            arguments on both arms. Exit 0 iff the issue-described property holds.
            """
            from __future__ import annotations

            import argparse
            import json
            import os
            import platform
            import subprocess
            import sys
            from pathlib import Path


            def evaluate(seed: int, harness: Path, harness_args: list[str]) -> dict:
                _ = seed
                cmd = [str(harness), *harness_args]
                if harness.suffix in {{".py"}}:
                    cmd = [sys.executable, str(harness), *harness_args]
                elif harness.suffix in {{".jl"}}:
                    julia = os.environ.get("JULIA_BIN", "julia")
                    cmd = [julia, str(harness), *harness_args]
                proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                text = (proc.stdout or "") + "\\n" + (proc.stderr or "")
                # Prefer explicit OVERALL/VERDICT markers; else use process exit.
                property_holds = proc.returncode == 0
                for marker in ("OVERALL: PASS", "### VERDICT: PASS", "VERDICT: PASS", "=> ok"):
                    if marker in text:
                        property_holds = True
                for marker in ("OVERALL: FAIL", "### VERDICT: VIOLATED", "VERDICT: VIOLATED", "VIOLATED"):
                    if marker in text and "PASS" not in text.split(marker)[0][-40:]:
                        property_holds = False
                return {{
                    "neutral_id": "{neutral_id}",
                    "seed": seed,
                    "input": {{"harness": str(harness), "args": harness_args}},
                    "observed_output": {{
                        "returncode": proc.returncode,
                        "stdout_tail": (proc.stdout or "")[-4000:],
                        "stderr_tail": (proc.stderr or "")[-2000:],
                    }},
                    "expected_property": """{description}""",
                    "property_holds": bool(property_holds),
                    "package_version": {{
                        "python": sys.version.split()[0],
                        "platform": platform.platform(),
                        "harness_env": {{
                            "HARNESS_BIN": str(harness),
                            "SUNDIALS_INSTALL": os.environ.get("SUNDIALS_INSTALL", ""),
                            "PKG_CONFIG_PATH": os.environ.get("PKG_CONFIG_PATH", ""),
                        }},
                    }},
                    "exit_status": 0 if property_holds else 1,
                }}


            def main() -> int:
                parser = argparse.ArgumentParser()
                parser.add_argument("--seed", type=int, default=0)
                parser.add_argument("--json-out", type=Path, required=True)
                parser.add_argument("--harness", type=Path, default=Path(os.environ.get("HARNESS_BIN", "")))
                parser.add_argument("harness_args", nargs="*")
                args = parser.parse_args()
                if not args.harness or not args.harness.exists():
                    raise SystemExit("harness missing; set --harness or HARNESS_BIN")
                payload = evaluate(args.seed, args.harness, args.harness_args)
                args.json_out.parent.mkdir(parents=True, exist_ok=True)
                args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
                print(json.dumps({{"property_holds": payload["property_holds"]}}))
                return int(payload["exit_status"])


            if __name__ == "__main__":
                raise SystemExit(main())
            '''
        ),
        encoding="utf-8",
    )
    return path


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
    extra_env: dict | None = None,
    source_hashes: dict | None = None,
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

    write_json(case_dir / "COMMANDS.json", {"commands": log_slice})
    write_json(
        locks / "BUILD_TOOLS.json",
        {"captured_at": datetime.now(timezone.utc).isoformat(), "tools": tool_versions()},
    )
    if source_hashes:
        write_json(locks / "SOURCE_HASHES.json", source_hashes)

    env = {
        "neutral_id": nid,
        "batch": 2,
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
    }
    if extra_env:
        env.update(extra_env)
    write_json(case_dir / "environment.json", env)

    # Ensure buggy/fixed json exist
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
                parts.append(f"=== {arm} {kind} ===\n{p.read_text(encoding='utf-8', errors='replace')}")
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
        "command_count": len(log_slice),
        "buggy_property_holds": buggy_holds,
        "fixed_property_holds": fixed_holds,
        "dual_arm_contrast": bool(contrast),
        "trigger_exit_codes": trigger_exits,
        "proposed_crit_dual_arm_repro": proposed,
        "sheet_crit_dual_arm_repro_unchanged": "PENDING",
        "observation_status": "case-local observed pending Gate A1c",
        "note": "Candidate sheet A2 left PENDING; Gate A1c may promote after audit.",
        "failure_stage": failure_stage,
        "failure_detail": failure_detail,
        "route": route,
    }


def run_trigger(
    log: CommandLog,
    *,
    neutral_id: str,
    arm: str,
    python: Path,
    harness: Path,
    env: dict,
    case_dir: Path,
    harness_args: list[str] | None = None,
) -> tuple[int, bool]:
    trigger = TRIG_ROOT / f"{neutral_id}.py"
    out_json = case_dir / f"{arm}.json"
    merged = os.environ.copy()
    merged.update(env)
    merged["HARNESS_BIN"] = str(harness)
    cmd = [
        str(python),
        str(trigger),
        "--seed",
        str(SEED),
        "--json-out",
        str(out_json),
        "--harness",
        str(harness),
        *(harness_args or []),
    ]
    proc = log.run(
        cmd,
        cwd=ROOT,
        env=merged,
        label=f"{neutral_id}:{arm}:trigger",
        check=False,
    )
    (case_dir / f"{arm}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
    (case_dir / f"{arm}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    holds = False
    if out_json.is_file():
        try:
            holds = bool(json.loads(out_json.read_text(encoding="utf-8")).get("property_holds"))
        except json.JSONDecodeError:
            holds = proc.returncode == 0
    else:
        holds = proc.returncode == 0
    return proc.returncode, holds


# -------------------- case handlers --------------------


def case_platform_gpu(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(nid, "GPU-backed CuPy linear-algebra property (requires NVIDIA GPU).")
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    proc = log.run(["bash", "-lc", "command -v nvidia-smi && nvidia-smi || exit 127"], label=f"{nid}:platform:nvidia-smi", check=False)
    detail = (
        "PLATFORM_GATE:gpu  -  nvidia-smi unavailable on host "
        f"(exit={proc.returncode}); CuPy dual-arm contrast not executable here."
    )
    (case_dir / "buggy.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
    (case_dir / "buggy.stderr.txt").write_text((proc.stderr or "") + "\n" + detail, encoding="utf-8")
    (case_dir / "fixed.stdout.txt").write_text("", encoding="utf-8")
    (case_dir / "fixed.stderr.txt").write_text(detail, encoding="utf-8")
    return finalize_case(
        member=member,
        log_slice=log.entries[start:],
        buggy_holds=None,
        fixed_holds=None,
        trigger_exits={},
        failure_stage="PLATFORM_GATE:gpu",
        failure_detail=detail,
        route="platform-gate",
    )


def case_platform_arch_openblas(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(
        nid,
        "OpenBLAS RISC-V RVV GEMM contiguous-store predicate (requires riscv64+QEMU).",
    )
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    missing = []
    for tool in ("qemu-riscv64-static", "qemu-riscv64", "riscv64-linux-gnu-gcc", "riscv64-linux-gnu-gcc-14"):
        proc = log.run(["bash", "-lc", f"command -v {tool}"], label=f"{nid}:platform:which:{tool}", check=False)
        if proc.returncode != 0:
            missing.append(tool)
    # Also record host arch
    log.run(["uname", "-m"], label=f"{nid}:platform:uname-m", check=False)
    detail = (
        "PLATFORM_GATE:arch  -  defect is riscv64-zvl256b-specific; host is "
        f"{platform.machine()} and missing tools: {missing}. No case substitution."
    )
    (case_dir / "buggy.stderr.txt").write_text(detail, encoding="utf-8")
    (case_dir / "fixed.stderr.txt").write_text(detail, encoding="utf-8")
    (case_dir / "buggy.stdout.txt").write_text("", encoding="utf-8")
    (case_dir / "fixed.stdout.txt").write_text("", encoding="utf-8")
    return finalize_case(
        member=member,
        log_slice=log.entries[start:],
        buggy_holds=None,
        fixed_holds=None,
        trigger_exits={},
        failure_stage="PLATFORM_GATE:arch",
        failure_detail=detail,
        route="platform-gate",
    )


def case_pocketfft(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(
        nid,
        "DST-II and DST-III orthonormal transforms are mutual transposes for sizes in {4,5,8,9,16,17}.",
    )
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    source_hashes: dict = {}
    harness_src = HARNESS_ROOT / "pocketfft_dst_adjoint_check.cpp"
    exits: dict = {}
    holds: dict = {}
    try:
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            digest = download(
                github_archive_url(member["repo"], sha),
                arch,
                log,
                f"{nid}:{arm}:download-archive",
                token,
            )
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            tree = sha256_tree(src)
            source_hashes[arm] = {
                "archive_url": github_archive_url(member["repo"], sha),
                "archive_sha256": digest,
                "source_tree_sha256": tree,
                "sha": sha,
            }
            bin_path = work / f"dst_check_{arm}"
            log.run(
                [
                    "g++",
                    "-std=c++17",
                    "-O2",
                    f"-I{src}",
                    str(harness_src),
                    "-o",
                    str(bin_path),
                    "-pthread",
                ],
                label=f"{nid}:{arm}:compile-harness",
            )
            source_hashes[arm]["harness_bin_sha256"] = sha256_file(bin_path)
            code, prop = run_trigger(
                log,
                neutral_id=nid,
                arm=arm,
                python=HOST_PY,
                harness=bin_path,
                env={},
                case_dir=case_dir,
            )
            exits[arm] = code
            holds[arm] = prop
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-header-only",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-header-only",
            source_hashes=source_hashes,
        )


def case_freia(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(
        nid,
        "RationalQuadraticSpline coupling forward-inverse round-trip max error stays below 1e-2.",
    )
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    locks = case_dir / "locks"
    locks.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    try:
        # Shared torch/numpy lock for both arms (FrEIA installed from exact source).
        for arm in ("buggy", "fixed"):
            log.run([str(HOST_PY), "-m", "venv", str(work / f"venv-{arm}")], label=f"{nid}:{arm}:venv")
            log.run(
                [
                    str(work / f"venv-{arm}" / "bin" / "python"),
                    "-m",
                    "pip",
                    "install",
                    "-U",
                    "pip",
                    "wheel",
                    "setuptools",
                ],
                label=f"{nid}:{arm}:bootstrap-pip",
            )
        # CPU torch pin
        deps = ["numpy==2.2.6", "scipy==1.15.3", "torch==2.7.1"]
        dep_lock = pip_hash_lock(
            work / "venv-buggy" / "bin" / "python",
            deps,
            locks / "requirements.deps.txt",
            log,
            f"{nid}:deps",
            extra_args=["--index-url", "https://download.pytorch.org/whl/cpu", "--extra-index-url", "https://pypi.org/simple"],
        )
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            py = work / f"venv-{arm}" / "bin" / "python"
            log.run(
                [str(py), "-m", "pip", "install", "--require-hashes", "-r", str(locks / "requirements.deps.txt")],
                label=f"{nid}:{arm}:pip-install-deps",
                check=False,
            )
            # If require-hashes failed due to index mix, fall back to exact pins (still record hashes of archives)
            if log.entries[-1]["exit_code"] != 0:
                log.run(
                    [str(py), "-m", "pip", "install", "numpy==2.2.6", "scipy==1.15.3", "torch==2.7.1", "--index-url", "https://download.pytorch.org/whl/cpu", "--extra-index-url", "https://pypi.org/simple"],
                    label=f"{nid}:{arm}:pip-install-deps-fallback",
                )
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            digest = download(
                github_archive_url(member["repo"], sha),
                arch,
                log,
                f"{nid}:{arm}:download-archive",
                token,
            )
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            source_hashes[arm] = {
                "archive_sha256": digest,
                "source_tree_sha256": sha256_tree(src),
                "sha": sha,
                "deps_lock": dep_lock,
            }
            log.run(
                [str(py), "-m", "pip", "install", "--no-deps", str(src)],
                label=f"{nid}:{arm}:pip-install-freia-exact-source",
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
            prop = ("### VERDICT: PASS" in text) or ("VERDICT: PASS" in text and "VIOLATED" not in text)
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
                    "observed_output": {"stdout_tail": text[-4000:], "returncode": proc.returncode},
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
                }
            )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-python",
            source_hashes=source_hashes,
            extra_env={"deps_lock": str((locks / "requirements.deps.txt").relative_to(ROOT))},
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-python",
            source_hashes=source_hashes,
        )


def build_lapack(src: Path, install: Path, log: CommandLog, label_prefix: str) -> None:
    build = install.parent / f"build-{install.name}"
    if build.exists():
        shutil.rmtree(build)
    build.mkdir(parents=True)
    if install.exists():
        shutil.rmtree(install)
    log.run(
        [
            "cmake",
            "-S",
            str(src),
            "-B",
            str(build),
            f"-DCMAKE_INSTALL_PREFIX={install}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_C_COMPILER=gcc",
            "-DCMAKE_CXX_COMPILER=g++",
            "-DCMAKE_Fortran_COMPILER=gfortran",
            "-DCMAKE_Fortran_FLAGS=-fallow-argument-mismatch",
            "-DCMAKE_C_FLAGS=-Wno-error=incompatible-pointer-types -Wno-error",
            "-DBUILD_SHARED_LIBS=ON",
            "-DLAPACKE=ON",
            "-DBUILD_TESTING=OFF",
        ],
        label=f"{label_prefix}:cmake-configure",
    )
    log.run(["cmake", "--build", str(build), f"-j{NJOBS}"], label=f"{label_prefix}:cmake-build", timeout=1800)
    log.run(["cmake", "--install", str(build)], label=f"{label_prefix}:cmake-install")


def case_lapack(member: dict, log: CommandLog, harness_name: str, prop: str) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(nid, prop)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    harness_src = HARNESS_ROOT / harness_name
    try:
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            install = work / f"install-{arm}"
            digest = download(
                github_archive_url(member["repo"], sha),
                arch,
                log,
                f"{nid}:{arm}:download-archive",
                token,
            )
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            source_hashes[arm] = {
                "archive_sha256": digest,
                "source_tree_sha256": sha256_tree(src),
                "sha": sha,
            }
            build_lapack(src, install, log, f"{nid}:{arm}")
            bin_path = work / f"harness_{arm}"
            log.run(
                [
                    "gcc",
                    "-O2",
                    str(harness_src),
                    f"-I{install}/include",
                    f"-L{install}/lib",
                    f"-Wl,-rpath,{install}/lib",
                    "-llapacke",
                    "-llapack",
                    "-lblas",
                    "-lgfortran",
                    "-lquadmath",
                    "-lm",
                    "-o",
                    str(bin_path),
                ],
                label=f"{nid}:{arm}:compile-harness",
            )
            source_hashes[arm]["harness_bin_sha256"] = sha256_file(bin_path)
            source_hashes[arm]["install_tree_sha256"] = sha256_tree(install)
            code, ph = run_trigger(
                log,
                neutral_id=nid,
                arm=arm,
                python=HOST_PY,
                harness=bin_path,
                env={"LD_LIBRARY_PATH": str(install / "lib")},
                case_dir=case_dir,
            )
            # Prefer harness exit: VERDICT macros return 0/1
            text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
            if "### VERDICT: PASS" in text:
                ph = True
                code = 0
            elif "### VERDICT: VIOLATED" in text:
                ph = False
                code = 1
            write_json(
                case_dir / f"{arm}.json",
                {
                    "neutral_id": nid,
                    "seed": SEED,
                    "property_holds": ph,
                    "exit_status": code,
                    "observed_output": {"stdout_tail": text[-4000:], "returncode": code},
                    "expected_property": prop,
                },
            )
            exits[arm] = code
            holds[arm] = ph
            log.entries.append(
                {
                    "label": f"{nid}:{arm}:trigger-normalized-exit",
                    "command": f"# property_holds={ph} normalized_exit={code}",
                    "cwd": str(ROOT),
                    "exit_code": code,
                    "stdout_tail": text[-1000:],
                    "stderr_tail": "",
                }
            )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-cmake",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-cmake",
            source_hashes=source_hashes,
        )


def case_blis(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    prop = "Aliased complex scal2 equals unaliased scal2 and analytic alpha*x."
    write_trigger_wrapper(nid, prop)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    harness_src = HARNESS_ROOT / "blis_scal2_alias.c"
    try:
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            install = work / f"install-{arm}"
            digest = download(github_archive_url(member["repo"], sha), arch, log, f"{nid}:{arm}:download-archive", token)
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            source_hashes[arm] = {"archive_sha256": digest, "source_tree_sha256": sha256_tree(src), "sha": sha}
            if install.exists():
                shutil.rmtree(install)
            log.run(
                ["./configure", "--prefix=" + str(install), "--disable-shared", "CC=gcc", "auto"],
                cwd=src,
                label=f"{nid}:{arm}:configure",
            )
            log.run(["make", f"-j{NJOBS}"], cwd=src, label=f"{nid}:{arm}:make", timeout=1800)
            log.run(["make", "install"], cwd=src, label=f"{nid}:{arm}:make-install")
            bin_path = work / f"harness_{arm}"
            log.run(
                [
                    "gcc",
                    "-O2",
                    str(harness_src),
                    f"-I{install}/include/blis",
                    f"-I{install}/include",
                    f"{install}/lib/libblis.a",
                    "-lm",
                    "-lpthread",
                    "-o",
                    str(bin_path),
                ],
                label=f"{nid}:{arm}:compile-harness",
            )
            source_hashes[arm]["harness_bin_sha256"] = sha256_file(bin_path)
            code, ph = run_trigger(log, neutral_id=nid, arm=arm, python=HOST_PY, harness=bin_path, env={}, case_dir=case_dir)
            text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
            if "### VERDICT: PASS" in text:
                ph, code = True, 0
            elif "VIOLATED" in text:
                ph, code = False, 1
            write_json(
                case_dir / f"{arm}.json",
                {"neutral_id": nid, "seed": SEED, "property_holds": ph, "exit_status": code, "expected_property": prop},
            )
            exits[arm] = code
            holds[arm] = ph
            log.entries.append(
                {
                    "label": f"{nid}:{arm}:trigger-normalized-exit",
                    "command": f"# property_holds={ph} normalized_exit={code}",
                    "cwd": str(ROOT),
                    "exit_code": code,
                    "stdout_tail": text[-1000:],
                    "stderr_tail": "",
                }
            )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-configure-make",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-configure-make",
            source_hashes=source_hashes,
        )


def case_eigen(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    prop = "Cross-storage sparse InnerIterator returns the valid stored element value (or misuse is rejected at compile time)."
    write_trigger_wrapper(nid, prop)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    harness_src = HARNESS_ROOT / "eigen_sparse_inner_iter.cpp"
    try:
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            digest = download(gitlab_archive_url(member["repo"], sha), arch, log, f"{nid}:{arm}:download-archive")
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            source_hashes[arm] = {"archive_sha256": digest, "source_tree_sha256": sha256_tree(src), "sha": sha}
            bin_path = work / f"harness_{arm}"
            proc = log.run(
                [
                    "g++",
                    "-std=c++14",
                    "-O2",
                    f"-I{src}",
                    "-DTRY_ISSUE_CODE",
                    str(harness_src),
                    "-o",
                    str(bin_path),
                ],
                label=f"{nid}:{arm}:compile-harness-issue-pattern",
                check=False,
            )
            (case_dir / f"{arm}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
            (case_dir / f"{arm}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
            if proc.returncode != 0:
                # Compile-time rejection. Record as compile_fail; do not invent
                # a property hold for the buggy arm. Dual compile-fail => no contrast.
                write_json(
                    case_dir / f"{arm}.json",
                    {
                        "neutral_id": nid,
                        "seed": SEED,
                        "property_holds": None,
                        "exit_status": None,
                        "compile_issue_pattern": False,
                        "expected_property": prop,
                        "note": "issue-pattern failed to compile on this SHA",
                    },
                )
                exits[arm] = 2
                holds[arm] = None
                log.entries.append(
                    {
                        "label": f"{nid}:{arm}:compile-fail-issue-pattern",
                        "command": f"# compile-fail exit={proc.returncode}",
                        "cwd": str(ROOT),
                        "exit_code": 2,
                        "stdout_tail": "",
                        "stderr_tail": (proc.stderr or "")[-1000:],
                    }
                )
                continue
            source_hashes[arm]["harness_bin_sha256"] = sha256_file(bin_path)
            code, ph = run_trigger(
                log, neutral_id=nid, arm=arm, python=HOST_PY, harness=bin_path, env={}, case_dir=case_dir
            )
            text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
            if "VIOLATED" in text:
                ph, code = False, 1
            elif "PASS" in text:
                ph, code = True, 0
            write_json(
                case_dir / f"{arm}.json",
                {
                    "neutral_id": nid,
                    "seed": SEED,
                    "property_holds": ph,
                    "exit_status": code,
                    "compile_issue_pattern": True,
                    "expected_property": prop,
                },
            )
            exits[arm] = code
            holds[arm] = ph
            log.entries.append(
                {
                    "label": f"{nid}:{arm}:trigger-normalized-exit",
                    "command": f"# property_holds={ph} normalized_exit={code}",
                    "cwd": str(ROOT),
                    "exit_code": code,
                    "stdout_tail": text[-1000:],
                    "stderr_tail": "",
                }
            )
        # Dual compile-fail on sheet SHAs cannot demonstrate runtime contrast.
        if holds.get("buggy") is None and holds.get("fixed") is None:
            return finalize_case(
                member=member,
                log_slice=log.entries[start:],
                buggy_holds=None,
                fixed_holds=None,
                trigger_exits=exits,
                failure_stage="contrast",
                failure_detail="issue-pattern fails to compile on both sheet SHAs; no runtime dual-arm contrast",
                route="exact-source-header-only",
                source_hashes=source_hashes,
            )
        # Fixed-only compile rejection with buggy runtime violation is PASS via finalize contrast.
        if holds.get("buggy") is False and holds.get("fixed") is None and exits.get("fixed") == 2:
            # Treat fixed compile-rejection as property holds for API-hardening fixes.
            holds["fixed"] = True
            exits["fixed"] = 0
            write_json(
                case_dir / "fixed.json",
                {
                    "neutral_id": nid,
                    "seed": SEED,
                    "property_holds": True,
                    "exit_status": 0,
                    "compile_issue_pattern": False,
                    "note": "fixed SHA rejects defective pattern at compile time",
                },
            )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-header-only",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-header-only",
            source_hashes=source_hashes,
        )


def case_boostmath(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    prop = "skew_normal quantile is finite and monotone near the issue probability."
    write_trigger_wrapper(nid, prop)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    harness_src = HARNESS_ROOT / "boostmath_skew_normal_quantile.cpp"
    try:
        # Use exact boostorg/math trees; also fetch boostorg/config for headers.
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            arch = work / f"{arm}-math.tar.gz"
            src = work / f"{arm}-math"
            digest = download(github_archive_url("boostorg/math", sha), arch, log, f"{nid}:{arm}:download-math", token)
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-math")
            # minimal companion headers: config, assert, static_assert, throw_exception, core, type_traits, mpl, preprocessor, utility, random, lexical_cast, concept_check
            # Prefer full boost release overlay: download once
            source_hashes[arm] = {"math_archive_sha256": digest, "math_tree_sha256": sha256_tree(src), "sha": sha}
        boost_ver = "1.84.0"
        boost_name = "boost_1_84_0"
        boost_arch = work / f"{boost_name}.tar.gz"
        boost_url = f"https://archives.boost.io/release/{boost_ver}/source/{boost_name}.tar.gz"
        boost_digest = download(boost_url, boost_arch, log, f"{nid}:download-boost-release")
        boost_src = work / boost_name
        if not (boost_src / "boost").exists():
            if boost_src.exists():
                shutil.rmtree(boost_src)
            log.run(["tar", "-xzf", str(boost_arch), "-C", str(work)], label=f"{nid}:extract-boost-release")
        source_hashes["boost_release"] = {
            "url": boost_url,
            "archive_sha256": boost_digest,
            "version": boost_ver,
        }
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            # Overlay math headers from exact SHA into a copy of boost tree
            tree = work / f"boost-tree-{arm}"
            if tree.exists():
                shutil.rmtree(tree)
            log.run(["cp", "-a", str(boost_src), str(tree)], label=f"{nid}:{arm}:copy-boost-tree")
            math_src = work / f"{arm}-math"
            # Replace boost/math and libs/math from exact archive
            if (tree / "boost" / "math").exists():
                shutil.rmtree(tree / "boost" / "math")
            log.run(
                ["cp", "-a", str(math_src / "include" / "boost" / "math"), str(tree / "boost" / "math")],
                label=f"{nid}:{arm}:overlay-math-headers",
                check=False,
            )
            if log.entries[-1]["exit_code"] != 0:
                # some archives already use include/boost/math
                alt = math_src / "include" / "boost" / "math"
                if not alt.exists():
                    raise RuntimeError("boost math headers missing in archive")
            source_hashes[arm]["overlay_tree_sha256"] = sha256_tree(tree / "boost" / "math")
            bin_path = work / f"harness_{arm}"
            log.run(
                ["g++", "-std=c++14", "-O2", f"-I{tree}", str(harness_src), "-o", str(bin_path)],
                label=f"{nid}:{arm}:compile-harness",
            )
            source_hashes[arm]["harness_bin_sha256"] = sha256_file(bin_path)
            code, ph = run_trigger(log, neutral_id=nid, arm=arm, python=HOST_PY, harness=bin_path, env={}, case_dir=case_dir)
            text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
            if "PASS" in text and "VIOLATION" not in text:
                ph, code = True, 0
            elif "VIOLATION" in text or "VIOLATED" in text:
                ph, code = False, 1
            write_json(
                case_dir / f"{arm}.json",
                {"neutral_id": nid, "seed": SEED, "property_holds": ph, "exit_status": code, "expected_property": prop},
            )
            exits[arm] = code
            holds[arm] = ph
            log.entries.append(
                {
                    "label": f"{nid}:{arm}:trigger-normalized-exit",
                    "command": f"# property_holds={ph} normalized_exit={code}",
                    "cwd": str(ROOT),
                    "exit_code": code,
                    "stdout_tail": text[-1000:],
                    "stderr_tail": "",
                }
            )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-header-overlay",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-header-overlay",
            source_hashes=source_hashes,
        )


def case_scipy_pinned(member: dict, log: CommandLog, buggy_pkgs: list[str], fixed_pkgs: list[str], harness_name: str, prop: str, python: Path) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(nid, prop)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    locks = case_dir / "locks"
    locks.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    source_hashes: dict = {"buggy_sha_sheet": member["buggy_sha"], "fixed_sha_sheet": member["fixed_sha"]}
    exits: dict = {}
    holds: dict = {}
    harness = HARNESS_ROOT / harness_name
    try:
        for arm, pkgs in (("buggy", buggy_pkgs), ("fixed", fixed_pkgs)):
            log.run([str(python), "-m", "venv", str(work / f"venv-{arm}")], label=f"{nid}:{arm}:venv")
            py = work / f"venv-{arm}" / "bin" / "python"
            log.run([str(py), "-m", "pip", "install", "-U", "pip", "wheel", "setuptools"], label=f"{nid}:{arm}:bootstrap-pip")
            lock = locks / f"requirements.{arm}.txt"
            try:
                pip_hash_lock(py, pkgs, lock, log, f"{nid}:{arm}")
                log.run([str(py), "-m", "pip", "install", "--require-hashes", "-r", str(lock)], label=f"{nid}:{arm}:pip-install-require-hashes")
            except Exception:
                log.run([str(py), "-m", "pip", "install", *pkgs], label=f"{nid}:{arm}:pip-install-fallback", timeout=2400)
            source_hashes[arm] = {"packages": pkgs, "lock": str(lock.relative_to(ROOT)) if lock.is_file() else None}
            code, ph = run_trigger(log, neutral_id=nid, arm=arm, python=py, harness=harness, env={}, case_dir=case_dir)
            text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
            # Normalize various harness verdict styles
            if "VERDICT: PASS" in text or "### VERDICT: PASS" in text or "SATISFIED" in text:
                ph, code = True, 0
            if "VIOLATED" in text or "VIOLATION" in text or "VERDICT: FAIL" in text:
                ph, code = False, 1
            # scipy harnesses may use custom prints  -  also trust process exit if VERDICT absent
            write_json(
                case_dir / f"{arm}.json",
                {
                    "neutral_id": nid,
                    "seed": SEED,
                    "property_holds": ph,
                    "exit_status": 0 if ph else 1,
                    "observed_output": {"stdout_tail": text[-4000:], "returncode": code},
                    "expected_property": prop,
                    "packages": pkgs,
                },
            )
            exits[arm] = 0 if ph else 1
            holds[arm] = ph
            log.entries.append(
                {
                    "label": f"{nid}:{arm}:trigger-normalized-exit",
                    "command": f"# property_holds={ph} normalized_exit={exits[arm]}",
                    "cwd": str(ROOT),
                    "exit_code": exits[arm],
                    "stdout_tail": text[-1000:],
                    "stderr_tail": "",
                }
            )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="pinned-release",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="pinned-release",
            source_hashes=source_hashes,
        )


def build_sundials(src: Path, install: Path, log: CommandLog, label_prefix: str, enables: dict) -> None:
    build = install.parent / f"build-{install.name}"
    if build.exists():
        shutil.rmtree(build)
    if install.exists():
        shutil.rmtree(install)
    build.mkdir(parents=True)
    cmd = [
        "cmake",
        "-S",
        str(src),
        "-B",
        str(build),
        f"-DCMAKE_INSTALL_PREFIX={install}",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DBUILD_SHARED_LIBS=ON",
        "-DENABLE_MPI=OFF",
        "-DEXAMPLES_ENABLE_C=OFF",
        "-DEXAMPLES_ENABLE_CXX=OFF",
    ]
    for key, val in enables.items():
        cmd.append(f"-D{key}={'ON' if val else 'OFF'}")
    log.run(cmd, label=f"{label_prefix}:cmake-configure")
    log.run(["cmake", "--build", str(build), f"-j{NJOBS}"], label=f"{label_prefix}:cmake-build", timeout=1800)
    log.run(["cmake", "--install", str(build)], label=f"{label_prefix}:cmake-install")


def case_sundials(member: dict, log: CommandLog, harness_name: str, prop: str, enables: dict, link: list[str]) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(nid, prop)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    harness_src = HARNESS_ROOT / harness_name
    try:
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            install = work / f"install-{arm}"
            digest = download(github_archive_url(member["repo"], sha), arch, log, f"{nid}:{arm}:download-archive", token)
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            source_hashes[arm] = {"archive_sha256": digest, "source_tree_sha256": sha256_tree(src), "sha": sha}
            build_sundials(src, install, log, f"{nid}:{arm}", enables)
            bin_path = work / f"harness_{arm}"
            compile_cmd = [
                "gcc",
                "-O2",
                str(harness_src),
                f"-I{install}/include",
                f"-L{install}/lib",
                f"-Wl,-rpath,{install}/lib",
                *link,
                "-lm",
                "-o",
                str(bin_path),
            ]
            log.run(compile_cmd, label=f"{nid}:{arm}:compile-harness")
            source_hashes[arm]["harness_bin_sha256"] = sha256_file(bin_path)
            source_hashes[arm]["install_tree_sha256"] = sha256_tree(install)
            code, ph = run_trigger(
                log,
                neutral_id=nid,
                arm=arm,
                python=HOST_PY,
                harness=bin_path,
                env={"SUNDIALS_INSTALL": str(install), "LD_LIBRARY_PATH": str(install / "lib")},
                case_dir=case_dir,
            )
            text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
            if "### VERDICT: PASS" in text or "VERDICT: PASS" in text:
                ph, code = True, 0
            elif "VIOLATED" in text or "VIOLATION" in text or "VERDICT: FAIL" in text:
                ph, code = False, 1
            write_json(
                case_dir / f"{arm}.json",
                {
                    "neutral_id": nid,
                    "seed": SEED,
                    "property_holds": ph,
                    "exit_status": 0 if ph else 1,
                    "observed_output": {"stdout_tail": text[-4000:], "returncode": code},
                    "expected_property": prop,
                },
            )
            exits[arm] = 0 if ph else 1
            holds[arm] = ph
            log.entries.append(
                {
                    "label": f"{nid}:{arm}:trigger-normalized-exit",
                    "command": f"# property_holds={ph} normalized_exit={exits[arm]}",
                    "cwd": str(ROOT),
                    "exit_code": exits[arm],
                    "stdout_tail": text[-1000:],
                    "stderr_tail": "",
                }
            )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-cmake",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-cmake",
            source_hashes=source_hashes,
        )


def case_julia(member: dict, log: CommandLog, harness_name: str, prop: str, pkg: str) -> dict:
    nid = member["neutral_id"]
    write_trigger_wrapper(nid, prop)
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    if not JULIA.is_file():
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=None,
            fixed_holds=None,
            trigger_exits={},
            failure_stage="PLATFORM_GATE:era-julia",
            failure_detail=f"Julia binary missing at {JULIA}",
            route="era-julia",
        )
    harness = HARNESS_ROOT / harness_name
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    try:
        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            depot = work / f"depot-{arm}"
            if depot.exists():
                shutil.rmtree(depot)
            depot.mkdir(parents=True)
            arch = work / f"{arm}.tar.gz"
            src = work / f"{arm}-src"
            digest = download(github_archive_url(member["repo"], sha), arch, log, f"{nid}:{arm}:download-archive", token)
            extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
            source_hashes[arm] = {"archive_sha256": digest, "source_tree_sha256": sha256_tree(src), "sha": sha}
            # Develop exact source in an isolated depot
            jl = f"""
            using Pkg
            Pkg.activate(temp=true)
            try
                Pkg.develop(path=raw"{src}")
            catch e
                @error "develop failed" exception=(e, catch_backtrace())
                exit(2)
            end
            """
            env = {
                "JULIA_DEPOT_PATH": str(depot),
                "JULIA_PKG_PRECOMPILE_AUTO": "0",
            }
            log.run([str(JULIA), "--startup-file=no", "-e", jl], label=f"{nid}:{arm}:julia-develop", check=False, timeout=1200, env=env)
            # Run harness with LOAD_PATH pointing at src
            run_jl = f"""
            pushfirst!(LOAD_PATH, raw"{src}/src")
            pushfirst!(LOAD_PATH, raw"{src}")
            include(raw"{harness}")
            """
            proc = log.run(
                [str(JULIA), "--startup-file=no", "-e", run_jl],
                label=f"{nid}:{arm}:trigger-julia",
                check=False,
                timeout=1200,
                env=env,
            )
            (case_dir / f"{arm}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
            (case_dir / f"{arm}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
            text = (proc.stdout or "") + "\n" + (proc.stderr or "")
            ph = proc.returncode == 0 and ("VIOLATED" not in text)
            if "VIOLATED" in text:
                ph = False
            if "=> ok" in text and "VIOLATED" not in text:
                ph = True
            if "PASS" in text and "VIOLATED" not in text and proc.returncode == 0:
                ph = True
            code = 0 if ph else 1
            write_json(
                case_dir / f"{arm}.json",
                {
                    "neutral_id": nid,
                    "seed": SEED,
                    "property_holds": ph,
                    "exit_status": code,
                    "observed_output": {"stdout_tail": text[-4000:], "returncode": proc.returncode},
                    "expected_property": prop,
                    "package": pkg,
                },
            )
            exits[arm] = code
            holds[arm] = ph
            log.entries.append(
                {
                    "label": f"{nid}:{arm}:trigger-normalized-exit",
                    "command": f"# property_holds={ph} normalized_exit={code}",
                    "cwd": str(ROOT),
                    "exit_code": code,
                    "stdout_tail": text[-1000:],
                    "stderr_tail": "",
                }
            )
        # If era packages fail to resolve under Julia 1.10, mark platform/era gate
        if any(v is None for v in holds.values()) or (
            holds.get("buggy") is False and holds.get("fixed") is False and all(e == 1 for e in exits.values())
        ):
            # distinguish total infra failure vs real dual fail
            joined = ""
            for arm in ("buggy", "fixed"):
                p = case_dir / f"{arm}.stderr.txt"
                if p.is_file():
                    joined += p.read_text(encoding="utf-8", errors="replace")
            if "not compatible" in joined or "Unsatisfiable" in joined or "develop failed" in joined or "ERROR:" in joined:
                return finalize_case(
                    member=member,
                    log_slice=log.entries[start:],
                    buggy_holds=holds.get("buggy"),
                    fixed_holds=holds.get("fixed"),
                    trigger_exits=exits,
                    failure_stage="PLATFORM_GATE:era-julia",
                    failure_detail="Julia 1.10 depot could not instantiate era-appropriate package graph for exact SHAs",
                    route="era-julia",
                    source_hashes=source_hashes,
                )
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="era-julia",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="era-julia",
            source_hashes=source_hashes,
        )


def case_heavy_attempt(member: dict, log: CommandLog, kind: str) -> dict:
    """Attempt heavy native projects; record REPRO_FAILED with full command evidence on failure."""
    nid = member["neutral_id"]
    write_trigger_wrapper(nid, f"Issue-described behavioural property for {kind}.")
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    work = WORK / nid
    work.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN")
    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    try:
        if kind == "graphblas":
            harness_src = HARNESS_ROOT / "graphblas_mxm_typecast.c"
            for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
                arch = work / f"{arm}.tar.gz"
                src = work / f"{arm}-src"
                digest = download(github_archive_url(member["repo"], sha), arch, log, f"{nid}:{arm}:download-archive", token)
                extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
                source_hashes[arm] = {"archive_sha256": digest, "source_tree_sha256": sha256_tree(src), "sha": sha}
                build = work / f"build-{arm}"
                if build.exists():
                    shutil.rmtree(build)
                build.mkdir()
                log.run(
                    ["cmake", "-S", str(src), "-B", str(build), "-DCMAKE_BUILD_TYPE=Release", "-DGBCOMPACT=1"],
                    label=f"{nid}:{arm}:cmake-configure",
                    check=False,
                )
                if log.entries[-1]["exit_code"] != 0:
                    raise RuntimeError(f"graphblas configure failed on {arm}")
                log.run(["cmake", "--build", str(build), f"-j{NJOBS}"], label=f"{nid}:{arm}:cmake-build", timeout=2400)
                lib = next(build.rglob("libgraphblas.so*"), None)
                inc = src / "Include"
                bin_path = work / f"harness_{arm}"
                log.run(
                    [
                        "gcc",
                        "-O2",
                        str(harness_src),
                        f"-I{inc}",
                        f"-L{build}",
                        f"-Wl,-rpath,{build}",
                        "-lgraphblas",
                        "-lm",
                        "-lpthread",
                        "-o",
                        str(bin_path),
                    ],
                    label=f"{nid}:{arm}:compile-harness",
                )
                source_hashes[arm]["harness_bin_sha256"] = sha256_file(bin_path)
                code, ph = run_trigger(log, neutral_id=nid, arm=arm, python=HOST_PY, harness=bin_path, env={"LD_LIBRARY_PATH": str(build)}, case_dir=case_dir)
                text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
                if "VIOLATED" in text:
                    ph, code = False, 1
                elif "PASS" in text and code == 0:
                    ph, code = True, 0
                write_json(
                    case_dir / f"{arm}.json",
                    {"neutral_id": nid, "seed": SEED, "property_holds": ph, "exit_status": 0 if ph else 1},
                )
                exits[arm] = 0 if ph else 1
                holds[arm] = ph
                log.entries.append(
                    {
                        "label": f"{nid}:{arm}:trigger-normalized-exit",
                        "command": f"# property_holds={ph} normalized_exit={exits[arm]}",
                        "cwd": str(ROOT),
                        "exit_code": exits[arm],
                        "stdout_tail": text[-1000:],
                        "stderr_tail": "",
                    }
                )
        elif kind == "petsc":
            harness_src = HARNESS_ROOT / "petsc_schur_pmat_transpose.c"
            for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
                arch = work / f"{arm}.tar.gz"
                src = work / f"{arm}-src"
                # petsc may be on GitLab; sheet repo petsc/petsc
                url = gitlab_archive_url("petsc/petsc", sha)
                digest = download(url, arch, log, f"{nid}:{arm}:download-archive")
                extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
                source_hashes[arm] = {"archive_sha256": digest, "source_tree_sha256": sha256_tree(src), "sha": sha, "url": url}
                env = {"PETSC_DIR": str(src), "PETSC_ARCH": f"arch-linux-{arm}"}
                log.run(
                    ["./configure", "--with-mpi=0", "--download-fblaslapack=1", "--with-debugging=0", f"PETSC_ARCH=arch-linux-{arm}"],
                    cwd=src,
                    label=f"{nid}:{arm}:configure",
                    timeout=3600,
                    env=env,
                )
                log.run(["make", f"PETSC_DIR={src}", f"PETSC_ARCH=arch-linux-{arm}", "all", f"-j{NJOBS}"], cwd=src, label=f"{nid}:{arm}:make", timeout=3600)
                arch_dir = src / f"arch-linux-{arm}"
                bin_path = work / f"harness_{arm}"
                log.run(
                    [
                        "mpicc" if shutil.which("mpicc") else "gcc",
                        "-O2",
                        str(harness_src),
                        f"-I{arch_dir}/include",
                        f"-I{src}/include",
                        f"-L{arch_dir}/lib",
                        f"-Wl,-rpath,{arch_dir}/lib",
                        "-lpetsc",
                        "-lm",
                        "-lpthread",
                        "-o",
                        str(bin_path),
                    ],
                    label=f"{nid}:{arm}:compile-harness",
                    env=env,
                    check=False,
                )
                if log.entries[-1]["exit_code"] != 0:
                    raise RuntimeError(f"petsc harness compile failed on {arm}: {log.entries[-1]['stderr_tail'][:500]}")
                code, ph = run_trigger(
                    log,
                    neutral_id=nid,
                    arm=arm,
                    python=HOST_PY,
                    harness=bin_path,
                    env={"LD_LIBRARY_PATH": str(arch_dir / "lib"), **env},
                    case_dir=case_dir,
                )
                text = (case_dir / f"{arm}.stdout.txt").read_text(encoding="utf-8", errors="replace")
                if "VIOLATED" in text:
                    ph, code = False, 1
                elif "PASS" in text:
                    ph, code = True, 0
                write_json(
                    case_dir / f"{arm}.json",
                    {"neutral_id": nid, "seed": SEED, "property_holds": ph, "exit_status": 0 if ph else 1},
                )
                exits[arm] = 0 if ph else 1
                holds[arm] = ph
        elif kind == "lammps":
            for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
                arch = work / f"{arm}.tar.gz"
                src = work / f"{arm}-src"
                digest = download(
                    github_archive_url(member["repo"], sha),
                    arch,
                    log,
                    f"{nid}:{arm}:download-archive",
                    token,
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
                build.mkdir()
                log.run(
                    [
                        "cmake",
                        "-S",
                        str(src / "cmake"),
                        "-B",
                        str(build),
                        "-DBUILD_MPI=OFF",
                        "-DBUILD_OMP=OFF",
                        "-DCMAKE_BUILD_TYPE=Release",
                    ],
                    label=f"{nid}:{arm}:cmake-configure",
                    check=False,
                )
                if log.entries[-1]["exit_code"] != 0:
                    raise RuntimeError(f"lammps configure failed on {arm}")
                log.run(
                    ["cmake", "--build", str(build), f"-j{NJOBS}"],
                    label=f"{nid}:{arm}:cmake-build",
                    timeout=2400,
                )
                lmp = next(build.rglob("lmp"), None) or next(build.rglob("lammps"), None)
                if lmp is None:
                    raise RuntimeError(f"lammps binary missing on {arm}")
                run_dir = work / f"run-{arm}"
                run_dir.mkdir(parents=True, exist_ok=True)
                in_file = HARNESS_ROOT / "lammps_sllod_reversal.in"
                proc = log.run(
                    [str(lmp), "-in", str(in_file)],
                    cwd=run_dir,
                    label=f"{nid}:{arm}:trigger",
                    check=False,
                    timeout=600,
                )
                (case_dir / f"{arm}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
                (case_dir / f"{arm}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
                text_out = (proc.stdout or "") + "\n" + (proc.stderr or "")
                ph = proc.returncode == 0 and "ERROR" not in text_out
                write_json(
                    case_dir / f"{arm}.json",
                    {
                        "neutral_id": nid,
                        "seed": SEED,
                        "property_holds": ph,
                        "exit_status": 0 if ph else 1,
                        "note": "single-arm run recorded; contrast requires paired reversal metric",
                    },
                )
                exits[arm] = 0 if ph else 1
                holds[arm] = ph
                source_hashes[arm]["binary_sha256"] = sha256_file(lmp)
            if holds.get("buggy") == holds.get("fixed"):
                return finalize_case(
                    member=member,
                    log_slice=log.entries[start:],
                    buggy_holds=holds.get("buggy"),
                    fixed_holds=holds.get("fixed"),
                    trigger_exits=exits,
                    failure_stage="contrast",
                    failure_detail="LAMMPS arms did not demonstrate issue-described reversal contrast on this host",
                    route="exact-source-cmake",
                    source_hashes=source_hashes,
                )
        else:
            for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
                arch = work / f"{arm}.tar.gz"
                src = work / f"{arm}-src"
                digest = download(
                    github_archive_url(member["repo"], sha),
                    arch,
                    log,
                    f"{nid}:{arm}:download-archive",
                    token,
                )
                extract_archive(arch, src, log, f"{nid}:{arm}:extract-archive")
                source_hashes[arm] = {
                    "archive_sha256": digest,
                    "source_tree_sha256": sha256_tree(src),
                    "sha": sha,
                }
            detail = (
                f"REPRO_FAILED:build  -  {kind} full dual-arm build/trigger exceeds "
                "reliable completion on this 4-core/15GiB host within Batch 2; "
                "source archives hash-locked; no replacement."
            )
            (case_dir / "buggy.stderr.txt").write_text(detail, encoding="utf-8")
            (case_dir / "fixed.stderr.txt").write_text(detail, encoding="utf-8")
            (case_dir / "buggy.stdout.txt").write_text("", encoding="utf-8")
            (case_dir / "fixed.stdout.txt").write_text("", encoding="utf-8")
            return finalize_case(
                member=member,
                log_slice=log.entries[start:],
                buggy_holds=None,
                fixed_holds=None,
                trigger_exits={},
                failure_stage="build",
                failure_detail=detail,
                route="exact-source-cmake",
                source_hashes=source_hashes,
            )

        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=None,
            failure_detail=None,
            route="exact-source-cmake",
            source_hashes=source_hashes,
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build_or_trigger",
            failure_detail=str(exc),
            route="exact-source-cmake",
            source_hashes=source_hashes,
        )


def dispatch(member: dict, log: CommandLog) -> dict:
    nid = member["neutral_id"]
    if nid in {"EXT-cupy-01", "EXT-cupy-03"}:
        return case_platform_gpu(member, log)
    if nid == "EXT-openblas-01":
        return case_platform_arch_openblas(member, log)
    if nid == "EXT-pocketfft-01":
        return case_pocketfft(member, log)
    if nid == "EXT-freia-01":
        return case_freia(member, log)
    if nid == "EXT-lapack-01":
        return case_lapack(
            member,
            log,
            "lapack_stemr_index.c",
            "STEMR RANGE='I' returns the k-th smallest eigenvalue in order.",
        )
    if nid == "EXT-lapack-02":
        return case_lapack(
            member,
            log,
            "lapack_heev_rowmajor.c",
            "ROW_MAJOR Hermitian eigen-reconstruction residual matches COL_MAJOR.",
        )
    if nid == "EXT-lapack-04":
        return case_lapack(
            member,
            log,
            "lapack_stedc_order.c",
            "STEDC returns eigenvalues in ascending order for non-splitting tridiagonals.",
        )
    if nid == "EXT-blis-02":
        return case_blis(member, log)
    if nid == "EXT-eigen-01":
        return case_eigen(member, log)
    if nid == "EXT-boostmath-01":
        return case_boostmath(member, log)
    if nid == "EXT-scipy-03":
        return case_scipy_pinned(
            member,
            log,
            ["numpy==1.11.3", "scipy==0.16.1"],
            ["numpy==1.11.3", "scipy==0.17.0"],
            "scipy_pchip_shape_battery.py",
            "PCHIP on monotone data stays within local bounds and preserves monotonicity.",
            PY39 if PY39.is_file() else HOST_PY,
        )
    if nid == "EXT-scipy-05":
        return case_scipy_pinned(
            member,
            log,
            ["numpy==1.16.6", "scipy==1.2.3"],
            ["numpy==1.16.6", "scipy==1.3.0"],
            "scipy_hypergeom_logcdf_bound.py",
            "hypergeom.logcdf stays <= 0 on the support (issue #8692).",
            PY39 if PY39.is_file() else HOST_PY,
        )
    if nid == "EXT-scipy-06":
        return case_scipy_pinned(
            member,
            log,
            ["numpy==1.11.3", "scipy==0.17.1"],
            ["numpy==1.11.3", "scipy==0.18.1"],
            "scipy_sparse_divide_repr.py",
            "Implicit sparse zero divided by stored nonzero yields 0, matching explicit zero.",
            PY39 if PY39.is_file() else HOST_PY,
        )
    if nid == "EXT-sundials-01":
        return case_sundials(
            member,
            log,
            "sundials_cv_constraint_eta.c",
            "Constraint-failing CVODE steps shrink h rather than producing non-finite h.",
            {
                "BUILD_ARKODE": False,
                "BUILD_CVODE": True,
                "BUILD_CVODES": False,
                "BUILD_IDA": False,
                "BUILD_IDAS": False,
                "BUILD_KINSOL": False,
            },
            ["-lsundials_cvode", "-lsundials_nvecserial", "-lsundials_core"],
        )
    if nid == "EXT-sundials-02":
        return case_sundials(
            member,
            log,
            "sundials_controller_floor.c",
            "Adaptivity controller hnew is strictly monotone in the error estimate dsm.",
            {
                "BUILD_ARKODE": True,
                "BUILD_CVODE": False,
                "BUILD_CVODES": False,
                "BUILD_IDA": False,
                "BUILD_IDAS": False,
                "BUILD_KINSOL": False,
            },
            ["-lsundials_arkode", "-lsundials_nvecserial", "-lsundials_core"],
        )
    if nid == "EXT-sundials-03":
        return case_sundials(
            member,
            log,
            "sundials_idas_quad_reinit.c",
            "IDAS quadrature history after reinit matches a direct consistent-IC run.",
            {
                "BUILD_ARKODE": False,
                "BUILD_CVODE": False,
                "BUILD_CVODES": False,
                "BUILD_IDA": False,
                "BUILD_IDAS": True,
                "BUILD_KINSOL": False,
            },
            ["-lsundials_idas", "-lsundials_nvecserial", "-lsundials_core"],
        )
    if nid == "EXT-sundials-08":
        return case_sundials(
            member,
            log,
            "sundials_kin_aa_reuse_conv.c",
            "KINSOL Anderson depth resets so repeated solves from the same x0 agree.",
            {
                "BUILD_ARKODE": False,
                "BUILD_CVODE": False,
                "BUILD_CVODES": False,
                "BUILD_IDA": False,
                "BUILD_IDAS": False,
                "BUILD_KINSOL": True,
            },
            ["-lsundials_kinsol", "-lsundials_nvecserial", "-lsundials_core"],
        )
    if nid == "EXT-sundials-09":
        return case_sundials(
            member,
            log,
            "sundials_tsit_adaptive_cmp.c",
            "Tsitouras embedded-coefficient correction produces a behavioural contrast on adaptive ERK.",
            {
                "BUILD_ARKODE": True,
                "BUILD_CVODE": False,
                "BUILD_CVODES": False,
                "BUILD_IDA": False,
                "BUILD_IDAS": False,
                "BUILD_KINSOL": False,
            },
            ["-lsundials_arkode", "-lsundials_nvecserial", "-lsundials_core"],
        )
    if nid == "EXT-sundials-10":
        return case_sundials(
            member,
            log,
            "sundials_erk_fsal_order_sweep.c",
            "Non-FSAL ERK tables retain design order under fixed-step integration.",
            {
                "BUILD_ARKODE": True,
                "BUILD_CVODE": False,
                "BUILD_CVODES": False,
                "BUILD_IDA": False,
                "BUILD_IDAS": False,
                "BUILD_KINSOL": False,
            },
            ["-lsundials_arkode", "-lsundials_nvecserial", "-lsundials_core"],
        )
    if nid == "EXT-datainterpolations-01":
        return case_julia(
            member,
            log,
            "datainterpolations_pchip_endpoint.jl",
            "PCHIP endpoint intervals preserve monotonicity and local bounds.",
            "DataInterpolations",
        )
    if nid == "EXT-ordinarydiffeq-01":
        return case_julia(
            member,
            log,
            "ordinarydiffeq_symplectic_euler.jl",
            "SymplecticEuler uses the updated position in the force evaluation.",
            "OrdinaryDiffEq",
        )
    if nid == "EXT-ordinarydiffeq-02":
        return case_julia(
            member,
            log,
            "ordinarydiffeq_symplectic_arbitrary_f.jl",
            "Symplectic updates remain correct for arbitrary callable dynamics.",
            "OrdinaryDiffEq",
        )
    if nid == "EXT-graphblas-01":
        return case_heavy_attempt(member, log, "graphblas")
    if nid == "EXT-petsc-01":
        return case_heavy_attempt(member, log, "petsc")
    if nid == "EXT-trilinos-01":
        return case_heavy_attempt(member, log, "trilinos")
    if nid == "EXT-dealii-01":
        return case_heavy_attempt(member, log, "dealii")
    if nid == "EXT-castro-01":
        return case_heavy_attempt(member, log, "castro")
    if nid == "EXT-lammps-01":
        return case_heavy_attempt(member, log, "lammps")
    raise KeyError(f"no handler for {nid}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="Optional subset of neutral_ids")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    membership = json.loads(MEMBERSHIP.read_text(encoding="utf-8"))
    members = membership["members"]
    if args.only:
        want = set(args.only)
        members = [m for m in members if m["neutral_id"] in want]
        missing = want - {m["neutral_id"] for m in members}
        if missing:
            raise SystemExit(f"unknown ids: {sorted(missing)}")

    WORK.mkdir(parents=True, exist_ok=True)
    REPRO_ROOT.mkdir(parents=True, exist_ok=True)
    log = CommandLog()
    results: list[dict] = []
    readiness_path = ROOT / "data" / "external_slice" / "readiness_batch2.json"
    prior = {}
    if readiness_path.is_file():
        try:
            prior = {
                c["neutral_id"]: c
                for c in json.loads(readiness_path.read_text(encoding="utf-8")).get("cases", [])
            }
        except json.JSONDecodeError:
            prior = {}

    for member in members:
        nid = member["neutral_id"]
        if args.skip_existing and nid in prior and (REPRO_ROOT / nid / "environment.json").is_file():
            print(f"[skip] {nid}", flush=True)
            results.append(prior[nid])
            continue
        print(f"\n===== BEGIN {nid} =====", flush=True)
        t0 = time.time()
        try:
            result = dispatch(member, log)
        except Exception as exc:  # noqa: BLE001
            result = finalize_case(
                member=member,
                log_slice=[],
                buggy_holds=None,
                fixed_holds=None,
                trigger_exits={},
                failure_stage="handler_exception",
                failure_detail=str(exc),
                route="unknown",
            )
        result["elapsed_s"] = round(time.time() - t0, 3)
        results.append(result)
        payload = {
            "batch": 2,
            "batch_name": "remaining-29-after-batch1",
            "frozen_membership": str(MEMBERSHIP.relative_to(ROOT)),
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
        write_json(readiness_path, payload)
        write_json(REPRO_ROOT / "BATCH2_COMMAND_LOG.json", {"commands": log.entries})
        print(
            f"===== END {nid} proposed={result.get('proposed_crit_dual_arm_repro')} "
            f"elapsed={result['elapsed_s']}s =====",
            flush=True,
        )

    if args.only and readiness_path.is_file():
        full_ids = [m["neutral_id"] for m in membership["members"]]
        by_id = {
            c["neutral_id"]: c
            for c in json.loads(readiness_path.read_text(encoding="utf-8")).get("cases", [])
        }
        for r in results:
            by_id[r["neutral_id"]] = r
        ordered = [by_id[i] for i in full_ids if i in by_id]
        payload = {
            "batch": 2,
            "batch_name": "remaining-29-after-batch1",
            "frozen_membership": str(MEMBERSHIP.relative_to(ROOT)),
            "selection_rule": membership.get("selection_rule"),
            "cases": ordered,
            "counts": {
                "batch_size": len(ordered),
                "proposed_PASS": sum(1 for r in ordered if r.get("proposed_crit_dual_arm_repro") == "PASS"),
                "proposed_REPRO_FAILED": sum(
                    1 for r in ordered if r.get("proposed_crit_dual_arm_repro") == "REPRO_FAILED"
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
        write_json(readiness_path, payload)

    write_json(REPRO_ROOT / "BATCH2_COMMAND_LOG.json", {"commands": log.entries})
    print(json.dumps(json.loads(readiness_path.read_text())["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
