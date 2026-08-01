#!/usr/bin/env python3
"""Fresh reconstruction of C3 Batch 1 with exact commands + hash locks.

Closes Gate A1b blockers A1B-HANDOFF-CMD-001 and A1B-LOCK-PROVENANCE-001.
Does not start Batch 2. Writes artifacts under data/external_slice/reproduction/
and a machine-readable command log for the correction handoff.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get("C3_FIX_WORK", "/tmp/c3_batch1_fix"))
REPRO_ROOT = ROOT / "data" / "external_slice" / "reproduction"
TRIG_ROOT = ROOT / "data" / "external_slice" / "reproducers"
SEED = 0
PY39 = Path("/tmp/c3_batch1/work/python39/install/bin/python3.9")
HOST_PY = Path(sys.executable)

CASES = {
    "EXT-scipy-04": {
        "route": "pinned-release",
        "buggy_sha": "5621f933e8434ebc6123dcb485e9836bf43e7be1",
        "fixed_sha": "1caf2339491aa8a1f9d018d1b202228ea85b022c",
        "registry_case": "c-scipy-002",
        "digest": "sha256:78a2247a5c46bdef645f80471a774ceb8c46ac94f26d2a5366e8792630d52fed",
    },
    "EXT-numpy-03": {
        "route": "exact-source",
        "repo": "numpy/numpy",
        "buggy_sha": "57684c06258ad61891df4aee1b617ee1764307ab",
        "fixed_sha": "5112fa07aab50daa2a615ac4c8f055f626a66d17",
        "registry_case": "b-pocketfft-004",
        "digest": "sha256:dd9463df9c14944a8071ef760d89cef8ff39171061eb77454f8b4f915e794b31",
    },
    "EXT-sundials-07": {
        "route": "exact-source",
        "repo": "LLNL/sundials",
        "buggy_sha": "b577f273a5704a8e32fa053061166689349fdfbe",
        "fixed_sha": "5f5a8c3facdd413e54e02361afc47a2032091175",
        "registry_case": "e-sundials-007",
        "digest": "sha256:c28ba71804fd7faef1bc6bf2c446cc0cbdbc431d4d9f915841fe4c21b0373c20",
    },
}


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
        input_text: str | None = None,
        label: str = "",
        allow_exit: set[int] | None = None,
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
        proc = subprocess.run(
            cmd_arg,
            cwd=str(cwd) if cwd else None,
            env=merged,
            input=input_text,
            text=True,
            capture_output=True,
            shell=shell,
            check=False,
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
        print(f"[{label}] exit={proc.returncode}: {cmd_display[:160]}")
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


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_wheel_or_sdist_name(filename: str) -> tuple[str, str] | None:
    """Return (name, version) from a wheel/sdist filename."""
    lower = filename.lower()
    if lower.endswith(".whl"):
        # {distribution}-{version}(-...)-{py}-{abi}-{plat}.whl
        parts = filename[:-4].split("-")
        if len(parts) >= 2:
            return parts[0], parts[1]
    for ext in (".tar.gz", ".zip"):
        if lower.endswith(ext):
            stem = filename[: -len(ext)]
            # {name}-{version}
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
) -> dict:
    """Download wheels/sdists and write a --require-hashes lock covering the closure."""
    dl = out.parent / f".download-{out.stem}"
    if dl.exists():
        shutil.rmtree(dl)
    dl.mkdir(parents=True)
    cmd = [str(python), "-m", "pip", "download", "-d", str(dl), *packages]
    if not with_deps:
        cmd.insert(4, "--no-deps")
    log.run(cmd, label=f"{label}:pip-download")
    lines = [
        "# Hash-locked requirements generated for C3 Batch 1 Gate A1b correction",
        f"# python={python}",
        f"# root_packages={packages}",
        f"# with_deps={with_deps}",
    ]
    artifact_hashes = {}
    req_to_hash: dict[str, str] = {}
    for path in sorted(p for p in dl.iterdir() if p.is_file()):
        parsed = _parse_wheel_or_sdist_name(path.name)
        if parsed is None:
            continue
        name, ver = parsed
        digest = sha256_file(path)
        artifact_hashes[path.name] = digest
        # PEP 503 normalize for requirement name
        req_name = name.replace("_", "-")
        req_to_hash[f"{req_name}=={ver}"] = digest
    if not req_to_hash:
        raise RuntimeError(f"no hashed artifacts produced for {packages}")
    # Put explicitly requested packages first, then the remainder stably.
    ordered = list(packages) + sorted(r for r in req_to_hash if r not in packages)
    seen = set()
    for req in ordered:
        if req in seen or req not in req_to_hash:
            continue
        seen.add(req)
        lines.append(f"{req} \\")
        lines.append(f"    --hash=sha256:{req_to_hash[req]}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Keep only the lock file in-tree; downloaded wheels stay outside git.
    shutil.rmtree(dl, ignore_errors=True)
    return {
        "lock_file": str(out.relative_to(ROOT)),
        "artifacts": artifact_hashes,
        "packages": packages,
        "resolved_requirements": sorted(req_to_hash),
    }


def ensure_py39(log: CommandLog) -> Path:
    if PY39.is_file():
        proc = log.run(
            [str(PY39), "-c", "import ssl; print(ssl.OPENSSL_VERSION)"],
            label="py39:ssl-check",
            check=False,
        )
        if proc.returncode == 0:
            return PY39
    # Rebuild if missing/broken
    src_root = WORK / "python39"
    src_root.mkdir(parents=True, exist_ok=True)
    tarball = src_root / "Python-3.9.18.tgz"
    if not tarball.is_file():
        log.run(
            [
                "curl",
                "-fsSL",
                "-o",
                str(tarball),
                "https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz",
            ],
            label="py39:download",
        )
    digest = sha256_file(tarball)
    expected = "504ce8cfd59addc04c22f590377c6be454ae7406cb1ebf6f5a350149225a9354"
    if digest != expected:
        raise RuntimeError(f"Python tarball hash mismatch: {digest}")
    build_dir = src_root / "Python-3.9.18"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    log.run(["tar", "-xzf", str(tarball), "-C", str(src_root)], label="py39:extract")
    prefix = src_root / "install"
    log.run(
        ["./configure", f"--prefix={prefix}"],
        cwd=build_dir,
        label="py39:configure",
    )
    log.run(["make", f"-j{os.cpu_count() or 2}"], cwd=build_dir, label="py39:make")
    log.run(["make", "install"], cwd=build_dir, label="py39:install")
    log.run(
        [str(prefix / "bin" / "python3.9"), "-c", "import ssl; print(ssl.OPENSSL_VERSION)"],
        label="py39:ssl-check-after-build",
    )
    return prefix / "bin" / "python3.9"


def rebuild_scipy(log: CommandLog, py39: Path) -> None:
    meta = CASES["EXT-scipy-04"]
    case_dir = REPRO_ROOT / "EXT-scipy-04"
    work = WORK / "scipy"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    locks = case_dir / "locks"
    locks.mkdir(parents=True, exist_ok=True)

    # Create venvs
    for arm in ("buggy", "fixed"):
        log.run([str(py39), "-m", "venv", str(work / f"venv-{arm}")], label=f"scipy:{arm}:venv")
        log.run(
            [str(work / f"venv-{arm}" / "bin" / "python"), "-m", "pip", "install", "-U", "pip", "wheel", "setuptools"],
            label=f"scipy:{arm}:bootstrap-pip",
        )

    buggy_pkgs = ["numpy==1.19.5", "scipy==1.5.4"]
    fixed_pkgs = ["numpy==1.19.5", "scipy==1.6.0"]
    buggy_lock = pip_hash_lock(
        work / "venv-buggy" / "bin" / "python",
        buggy_pkgs,
        locks / "requirements.buggy.txt",
        log,
        "scipy:buggy",
    )
    fixed_lock = pip_hash_lock(
        work / "venv-fixed" / "bin" / "python",
        fixed_pkgs,
        locks / "requirements.fixed.txt",
        log,
        "scipy:fixed",
    )

    for arm, lock in (("buggy", locks / "requirements.buggy.txt"), ("fixed", locks / "requirements.fixed.txt")):
        log.run(
            [
                str(work / f"venv-{arm}" / "bin" / "python"),
                "-m",
                "pip",
                "install",
                "--require-hashes",
                "-r",
                str(lock),
            ],
            label=f"scipy:{arm}:pip-install-require-hashes",
        )

    # Execute triggers
    trigger = TRIG_ROOT / "EXT-scipy-04.py"
    exits = {}
    for arm in ("buggy", "fixed"):
        out_json = case_dir / f"{arm}.json"
        stdout_path = case_dir / f"{arm}.stdout.txt"
        stderr_path = case_dir / f"{arm}.stderr.txt"
        expected = {1} if arm == "buggy" else {0}
        proc = log.run(
            [
                str(work / f"venv-{arm}" / "bin" / "python"),
                str(trigger),
                "--seed",
                str(SEED),
                "--json-out",
                str(out_json),
            ],
            cwd=ROOT,
            label=f"scipy:{arm}:trigger",
            allow_exit=expected,
            check=True,
        )
        stdout_path.write_text(proc.stdout or "", encoding="utf-8")
        stderr_path.write_text(proc.stderr or "", encoding="utf-8")
        exits[arm] = proc.returncode

    (case_dir / "stdout.log").write_text(
        "=== buggy stdout ===\n"
        + (case_dir / "buggy.stdout.txt").read_text(encoding="utf-8")
        + "\n=== fixed stdout ===\n"
        + (case_dir / "fixed.stdout.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (case_dir / "stderr.log").write_text(
        "=== buggy stderr ===\n"
        + (case_dir / "buggy.stderr.txt").read_text(encoding="utf-8")
        + "\n=== fixed stderr ===\n"
        + (case_dir / "fixed.stderr.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    buggy = json.loads((case_dir / "buggy.json").read_text(encoding="utf-8"))
    fixed = json.loads((case_dir / "fixed.json").read_text(encoding="utf-8"))
    contrast = (not buggy["property_holds"]) and fixed["property_holds"]
    env = {
        "neutral_id": "EXT-scipy-04",
        "route": "pinned-release",
        "buggy_sha": meta["buggy_sha"],
        "fixed_sha": meta["fixed_sha"],
        "seed": SEED,
        "trigger": "data/external_slice/reproducers/EXT-scipy-04.py",
        "same_trigger_input_seed": True,
        "dual_arm_contrast": contrast,
        "trigger_exit_codes": exits,
        "platform": {
            "python": "3.9.18",
            "python_executable": str(py39),
            "python_tarball_sha256": "504ce8cfd59addc04c22f590377c6be454ae7406cb1ebf6f5a350149225a9354",
            "host_platform": platform.platform(),
        },
        "locks": {
            "buggy": buggy_lock,
            "fixed": fixed_lock,
        },
        "release_mapping": {
            "note": "fixed_sha is PR #12640 merge (first in scipy 1.6.0); buggy_sha is its first parent.",
            "buggy_packages": {"python": "3.9.18", "numpy": "1.19.5", "scipy": "1.5.4"},
            "fixed_packages": {"python": "3.9.18", "numpy": "1.19.5", "scipy": "1.6.0"},
        },
        "docker_digest_route": {
            "attempted": True,
            "registry_case": meta["registry_case"],
            "digest": meta["digest"],
            "result": "GHCR pull 403 Forbidden after docker login; host pinned-release rebuild used",
        },
        "recorded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    write_json(case_dir / "environment.json", env)
    write_json(
        case_dir / "COMMANDS.json",
        {"neutral_id": "EXT-scipy-04", "commands": [e for e in log.entries if e["label"].startswith("scipy:")]},
    )


def download_github_archive(repo: str, sha: str, dest: Path, log: CommandLog, label: str) -> str:
    url = f"https://github.com/{repo}/archive/{sha}.tar.gz"
    dest.parent.mkdir(parents=True, exist_ok=True)
    log.run(["curl", "-fsSL", "-L", "-o", str(dest), url], label=label)
    return sha256_file(dest)


def rebuild_numpy(log: CommandLog) -> None:
    meta = CASES["EXT-numpy-03"]
    case_dir = REPRO_ROOT / "EXT-numpy-03"
    work = WORK / "numpy"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    locks = case_dir / "locks"
    locks.mkdir(parents=True, exist_ok=True)

    # Exact-source materialisation via GitHub archives + git submodule completion
    source_hashes = {}
    for arm, sha in (("buggy", meta["buggy_sha"]), ("fixed", meta["fixed_sha"])):
        tarball = work / f"{arm}.tar.gz"
        digest = download_github_archive(meta["repo"], sha, tarball, log, f"numpy:{arm}:download-archive")
        source_hashes[f"{arm}_archive"] = {
            "url": f"https://github.com/{meta['repo']}/archive/{sha}.tar.gz",
            "sha": sha,
            "sha256": digest,
            "bytes": tarball.stat().st_size,
        }
        src = work / f"{arm}-src"
        src.mkdir()
        log.run(
            ["tar", "-xzf", str(tarball), "--strip-components=1", "-C", str(src)],
            label=f"numpy:{arm}:extract-archive",
        )

    # Submodules are not in GitHub archive; complete from a git clone at the same SHAs.
    clone = work / "src.git"
    log.run(
        ["git", "clone", "--filter=blob:none", f"https://github.com/{meta['repo']}.git", str(clone)],
        label="numpy:git-clone",
    )
    submodule_pins = {}
    for arm, sha in (("buggy", meta["buggy_sha"]), ("fixed", meta["fixed_sha"])):
        log.run(["git", "fetch", "origin", sha], cwd=clone, label=f"numpy:{arm}:git-fetch")
        log.run(["git", "checkout", "--detach", sha], cwd=clone, label=f"numpy:{arm}:git-checkout")
        head = log.run(["git", "rev-parse", "HEAD"], cwd=clone, label=f"numpy:{arm}:git-rev-parse")
        got = head.stdout.strip()
        if got != sha:
            raise RuntimeError(f"numpy {arm} checkout mismatch: {got} != {sha}")
        log.run(
            ["git", "submodule", "update", "--init"],
            cwd=clone,
            label=f"numpy:{arm}:git-submodule-update",
        )
        status = log.run(
            ["git", "submodule", "status"],
            cwd=clone,
            label=f"numpy:{arm}:git-submodule-status",
        )
        submodule_pins[arm] = {
            "head": got,
            "submodule_status": status.stdout.strip().splitlines(),
        }
        # Overlay submodule contents into archive-extracted tree
        src = work / f"{arm}-src"
        for rel in status.stdout.strip().splitlines():
            # format: "<sha> <path> (...)" or " <sha> <path> ..."
            parts = rel.strip().lstrip("+-U ").split()
            if len(parts) < 2:
                continue
            sub_path = parts[1]
            src_sub = clone / sub_path
            dst_sub = src / sub_path
            if src_sub.exists():
                if dst_sub.exists():
                    shutil.rmtree(dst_sub)
                shutil.copytree(src_sub, dst_sub, symlinks=True)
        # Hash the completed source tree via tar
        tree_tar = work / f"{arm}-src-complete.tar.gz"
        log.run(
            ["tar", "-czf", str(tree_tar), "-C", str(src), "."],
            label=f"numpy:{arm}:hash-tree-tar",
        )
        source_hashes[f"{arm}_source_tree"] = {
            "sha": sha,
            "sha256": sha256_file(tree_tar),
            "bytes": tree_tar.stat().st_size,
            "includes_submodules": True,
        }

    write_json(locks / "SOURCE_HASHES.json", {"case": "EXT-numpy-03", "hashes": source_hashes, "submodules": submodule_pins})

    # Build-requirement lock (identical for both arms)
    for arm in ("buggy", "fixed"):
        log.run([str(HOST_PY), "-m", "venv", str(work / f"venv-{arm}")], label=f"numpy:{arm}:venv")
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
            label=f"numpy:{arm}:bootstrap-pip",
        )

    # Resolve current build-tool versions first, then hash-lock the exact closure.
    log.run(
        [
            str(work / "venv-buggy" / "bin" / "python"),
            "-m",
            "pip",
            "install",
            "cython<3.1",
            "meson-python",
            "ninja",
            "pkgconfig",
            "patchelf",
        ],
        label="numpy:build:probe-install",
    )
    freeze = log.run(
        [str(work / "venv-buggy" / "bin" / "python"), "-m", "pip", "freeze"],
        label="numpy:build:probe-freeze",
    )
    wanted = ("Cython", "meson-python", "ninja", "pkgconfig", "patchelf", "meson", "pyproject-metadata", "packaging")
    build_pkgs = []
    for line in freeze.stdout.splitlines():
        if "==" not in line:
            continue
        name = line.split("==", 1)[0]
        if name.lower().replace("_", "-") in {w.lower().replace("_", "-") for w in wanted}:
            build_pkgs.append(line.strip())
    if not build_pkgs:
        raise RuntimeError(f"failed to resolve numpy build packages from freeze:\n{freeze.stdout}")
    build_lock = pip_hash_lock(
        work / "venv-buggy" / "bin" / "python",
        build_pkgs,
        locks / "requirements.build.txt",
        log,
        "numpy:build",
    )

    for arm in ("buggy", "fixed"):
        log.run(
            [
                str(work / f"venv-{arm}" / "bin" / "python"),
                "-m",
                "pip",
                "install",
                "--require-hashes",
                "-r",
                str(locks / "requirements.build.txt"),
            ],
            label=f"numpy:{arm}:pip-install-build-reqs",
        )
        env = {"CC": "gcc", "CXX": "g++", "PATH": f"{work / f'venv-{arm}' / 'bin'}:{os.environ.get('PATH','')}"}
        log.run(
            [
                str(work / f"venv-{arm}" / "bin" / "python"),
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--no-build-isolation",
                str(work / f"{arm}-src"),
            ],
            label=f"numpy:{arm}:pip-install-source",
            env=env,
        )

    trigger = TRIG_ROOT / "EXT-numpy-03.py"
    exits = {}
    for arm in ("buggy", "fixed"):
        out_json = case_dir / f"{arm}.json"
        expected = {1} if arm == "buggy" else {0}
        proc = log.run(
            [
                str(work / f"venv-{arm}" / "bin" / "python"),
                str(trigger),
                "--seed",
                str(SEED),
                "--json-out",
                str(out_json),
            ],
            cwd=Path("/tmp"),
            label=f"numpy:{arm}:trigger",
            allow_exit=expected,
            check=True,
            env={"CC": "gcc", "CXX": "g++"},
        )
        (case_dir / f"{arm}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
        (case_dir / f"{arm}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
        exits[arm] = proc.returncode

    (case_dir / "stdout.log").write_text(
        "=== buggy stdout ===\n"
        + (case_dir / "buggy.stdout.txt").read_text(encoding="utf-8")
        + "\n=== fixed stdout ===\n"
        + (case_dir / "fixed.stdout.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (case_dir / "stderr.log").write_text(
        "=== buggy stderr ===\n"
        + (case_dir / "buggy.stderr.txt").read_text(encoding="utf-8")
        + "\n=== fixed stderr ===\n"
        + (case_dir / "fixed.stderr.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    buggy = json.loads((case_dir / "buggy.json").read_text(encoding="utf-8"))
    fixed = json.loads((case_dir / "fixed.json").read_text(encoding="utf-8"))
    contrast = (not buggy["property_holds"]) and fixed["property_holds"]
    env = {
        "neutral_id": "EXT-numpy-03",
        "route": "exact-source",
        "buggy_sha": meta["buggy_sha"],
        "fixed_sha": meta["fixed_sha"],
        "seed": SEED,
        "trigger": "data/external_slice/reproducers/EXT-numpy-03.py",
        "same_trigger_input_seed": True,
        "dual_arm_contrast": contrast,
        "trigger_exit_codes": exits,
        "platform": {
            "python": platform.python_version(),
            "python_executable": str(HOST_PY),
            "host_platform": platform.platform(),
            "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
            "gxx": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
        },
        "locks": {
            "build": build_lock,
            "source_hashes": "data/external_slice/reproduction/EXT-numpy-03/locks/SOURCE_HASHES.json",
        },
        "docker_digest_route": {
            "attempted": True,
            "registry_case": meta["registry_case"],
            "digest": meta["digest"],
            "result": "GHCR pull 403 Forbidden after docker login; host exact-source rebuild used",
        },
        "recorded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    write_json(case_dir / "environment.json", env)
    write_json(
        case_dir / "COMMANDS.json",
        {"neutral_id": "EXT-numpy-03", "commands": [e for e in log.entries if e["label"].startswith("numpy:")]},
    )


def rebuild_sundials(log: CommandLog) -> None:
    meta = CASES["EXT-sundials-07"]
    case_dir = REPRO_ROOT / "EXT-sundials-07"
    work = WORK / "sundials"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    locks = case_dir / "locks"
    locks.mkdir(parents=True, exist_ok=True)

    source_hashes = {}
    for arm, sha in (("buggy", meta["buggy_sha"]), ("fixed", meta["fixed_sha"])):
        tarball = work / f"{arm}.tar.gz"
        digest = download_github_archive(meta["repo"], sha, tarball, log, f"sundials:{arm}:download-archive")
        source_hashes[f"{arm}_archive"] = {
            "url": f"https://github.com/{meta['repo']}/archive/{sha}.tar.gz",
            "sha": sha,
            "sha256": digest,
            "bytes": tarball.stat().st_size,
        }
        src = work / f"{arm}-src"
        src.mkdir()
        log.run(
            ["tar", "-xzf", str(tarball), "--strip-components=1", "-C", str(src)],
            label=f"sundials:{arm}:extract-archive",
        )

    write_json(locks / "SOURCE_HASHES.json", {"case": "EXT-sundials-07", "hashes": source_hashes})

    tool_versions = {
        "cmake": subprocess.check_output(["cmake", "--version"], text=True).splitlines()[0],
        "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
        "gxx": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
        "make": subprocess.check_output(["make", "--version"], text=True).splitlines()[0],
    }
    write_json(locks / "BUILD_TOOLS.json", tool_versions)

    cmake_flags = [
        "-DCMAKE_BUILD_TYPE=Release",
        "-DBUILD_SHARED_LIBS=ON",
        "-DENABLE_MPI=OFF",
        "-DEXAMPLES_ENABLE_C=OFF",
        "-DEXAMPLES_ENABLE_CXX=OFF",
        "-DBUILD_ARKODE=ON",
        "-DBUILD_CVODE=OFF",
        "-DBUILD_CVODES=OFF",
        "-DBUILD_IDA=OFF",
        "-DBUILD_IDAS=OFF",
        "-DBUILD_KINSOL=OFF",
    ]
    for arm in ("buggy", "fixed"):
        build = work / f"build-{arm}"
        install = work / f"install-{arm}"
        build.mkdir()
        install.mkdir()
        log.run(
            [
                "cmake",
                "-S",
                str(work / f"{arm}-src"),
                "-B",
                str(build),
                f"-DCMAKE_INSTALL_PREFIX={install}",
                *cmake_flags,
            ],
            label=f"sundials:{arm}:cmake-configure",
        )
        log.run(
            ["cmake", "--build", str(build), f"-j{os.cpu_count() or 2}"],
            label=f"sundials:{arm}:cmake-build",
        )
        log.run(["cmake", "--install", str(build)], label=f"sundials:{arm}:cmake-install")

    # Identical harness source from buggy tree, compiled against each install
    harness_rel = "test/unit_tests/arkode/CXX_serial/ark_test_kpr_mriadapt.cpp"
    util_rel = "test/unit_tests/utilities/test_utilities.hpp"
    kpr = work / "kprsrc"
    utilities = work / "utilities"
    kpr.mkdir()
    utilities.mkdir()
    shutil.copy2(work / "buggy-src" / harness_rel, kpr / "ark_test_kpr_mriadapt.cpp")
    shutil.copy2(work / "buggy-src" / util_rel, utilities / "test_utilities.hpp")
    log.run(
        [
            "sed",
            "-i",
            "s#../../utilities/#../utilities/#g",
            str(kpr / "ark_test_kpr_mriadapt.cpp"),
        ],
        label="sundials:harness:fix-include-path",
    )
    for arm in ("buggy", "fixed"):
        install = work / f"install-{arm}"
        lib = install / "lib"
        if not lib.is_dir():
            lib = install / "lib64"
        log.run(
            [
                "g++",
                "-O2",
                "-o",
                str(work / f"kprmri-{arm}"),
                str(kpr / "ark_test_kpr_mriadapt.cpp"),
                f"-I{install / 'include'}",
                f"-I{work}",
                f"-L{lib}",
                f"-Wl,-rpath,{lib}",
                "-lsundials_arkode",
                "-lsundials_nvecserial",
                "-lsundials_core",
                "-lm",
            ],
            label=f"sundials:{arm}:compile-harness",
        )

    trigger = TRIG_ROOT / "EXT-sundials-07.py"
    exits = {}
    for arm in ("buggy", "fixed"):
        out_json = case_dir / f"{arm}.json"
        expected = {1} if arm == "buggy" else {0}
        proc = log.run(
            [
                str(HOST_PY),
                str(trigger),
                "--seed",
                str(SEED),
                "--json-out",
                str(out_json),
                "--harness",
                str(work / f"kprmri-{arm}"),
            ],
            cwd=ROOT,
            label=f"sundials:{arm}:trigger",
            allow_exit=expected,
            check=True,
        )
        (case_dir / f"{arm}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
        (case_dir / f"{arm}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
        exits[arm] = proc.returncode
        # also capture raw harness for logs
        hproc = log.run(
            [
                str(work / f"kprmri-{arm}"),
                "--scontrol",
                "5",
                "--faccum",
                "1",
                "--w",
                "100000",
                "--rtol",
                "1e-5",
            ],
            label=f"sundials:{arm}:harness-raw",
            check=False,
        )
        (case_dir / f"{arm}.harness.stdout.txt").write_text(hproc.stdout or "", encoding="utf-8")
        (case_dir / f"{arm}.harness.stderr.txt").write_text(hproc.stderr or "", encoding="utf-8")

    (case_dir / "stdout.log").write_text(
        "=== buggy trigger stdout ===\n"
        + (case_dir / "buggy.stdout.txt").read_text(encoding="utf-8")
        + "\n=== fixed trigger stdout ===\n"
        + (case_dir / "fixed.stdout.txt").read_text(encoding="utf-8")
        + "\n=== buggy harness stdout ===\n"
        + (case_dir / "buggy.harness.stdout.txt").read_text(encoding="utf-8")
        + "\n=== fixed harness stdout ===\n"
        + (case_dir / "fixed.harness.stdout.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (case_dir / "stderr.log").write_text(
        "=== buggy trigger stderr ===\n"
        + (case_dir / "buggy.stderr.txt").read_text(encoding="utf-8")
        + "\n=== fixed trigger stderr ===\n"
        + (case_dir / "fixed.stderr.txt").read_text(encoding="utf-8")
        + "\n=== buggy harness stderr ===\n"
        + (case_dir / "buggy.harness.stderr.txt").read_text(encoding="utf-8")
        + "\n=== fixed harness stderr ===\n"
        + (case_dir / "fixed.harness.stderr.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    buggy = json.loads((case_dir / "buggy.json").read_text(encoding="utf-8"))
    fixed = json.loads((case_dir / "fixed.json").read_text(encoding="utf-8"))
    contrast = (not buggy["property_holds"]) and fixed["property_holds"]
    env = {
        "neutral_id": "EXT-sundials-07",
        "route": "exact-source",
        "buggy_sha": meta["buggy_sha"],
        "fixed_sha": meta["fixed_sha"],
        "seed": SEED,
        "trigger": "data/external_slice/reproducers/EXT-sundials-07.py",
        "same_trigger_input_seed": True,
        "dual_arm_contrast": contrast,
        "trigger_exit_codes": exits,
        "platform": tool_versions | {"host_platform": platform.platform(), "python": platform.python_version()},
        "cmake_flags": cmake_flags,
        "decisive_config": {"scontrol": 5, "faccum": 1, "w": 100000, "rtol": "1e-5"},
        "harness": {
            "source": harness_rel,
            "note": "Identical buggy-tree harness source compiled against each arm install",
        },
        "locks": {
            "source_hashes": "data/external_slice/reproduction/EXT-sundials-07/locks/SOURCE_HASHES.json",
            "build_tools": "data/external_slice/reproduction/EXT-sundials-07/locks/BUILD_TOOLS.json",
        },
        "docker_digest_route": {
            "attempted": True,
            "registry_case": meta["registry_case"],
            "digest": meta["digest"],
            "result": "GHCR pull 403 Forbidden after docker login; host exact-source rebuild used",
        },
        "recorded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    write_json(case_dir / "environment.json", env)
    write_json(
        case_dir / "COMMANDS.json",
        {"neutral_id": "EXT-sundials-07", "commands": [e for e in log.entries if e["label"].startswith("sundials:")]},
    )


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    log = CommandLog()
    # Record GHCR 403 disclosure attempt once
    for image, digest in [
        (
            "ghcr.io/meng004/d4mr-c-scipy-002",
            "sha256:78a2247a5c46bdef645f80471a774ceb8c46ac94f26d2a5366e8792630d52fed",
        ),
        (
            "ghcr.io/meng004/d4mr-b-pocketfft-004",
            "sha256:dd9463df9c14944a8071ef760d89cef8ff39171061eb77454f8b4f915e794b31",
        ),
        (
            "ghcr.io/meng004/d4mr-e-sundials-007",
            "sha256:c28ba71804fd7faef1bc6bf2c446cc0cbdbc431d4d9f915841fe4c21b0373c20",
        ),
    ]:
        log.run(
            ["docker", "pull", f"{image}@{digest}"],
            label=f"ghcr:pull:{image.split('/')[-1]}",
            check=False,
        )

    py39 = ensure_py39(log)
    rebuild_scipy(log, py39)
    rebuild_numpy(log)
    rebuild_sundials(log)

    # Global command log for handoff
    write_json(
        REPRO_ROOT / "BATCH1_COMMAND_LOG.json",
        {
            "task": "C3_BATCH1_CORRECTION",
            "recorded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "work_root": str(WORK),
            "commands": log.entries,
        },
    )
    print("DONE: reconstructed batch1 with provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
