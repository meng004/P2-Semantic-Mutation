"""Real version-switching executor for boundary cases (方案 a).

Runs a standalone scalar observable script inside an isolated uv venv pinned to
a specific (package, version), so the genuine historical buggy/fixed library
releases run unmodified. Envs are cached under code/boundary/.version_envs/.

This is experiment-PROCESS-CONTROL (PC) infrastructure — cross-meta-pattern,
not meta-pattern-named.
"""
import json
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
ENVROOT = _ROOT / ".version_envs"


def _installed_ok(py: Path, pkg: str, ver: str) -> bool:
    if not py.exists():
        return False
    chk = subprocess.run([str(py), "-c", f"import {pkg}; print({pkg}.__version__)"],
                         capture_output=True, text=True)
    return chk.returncode == 0 and chk.stdout.strip() == ver


def ensure_env(pkg: str, ver: str, extra=("numpy",), python: str = "3.12") -> Path:
    """Create (and cache) a uv venv on the given Python with pkg==ver installed.

    Verifies the package is actually importable at the requested version, and
    (re)installs if a stale/empty venv is found — the venv existing is not enough.
    """
    env = ENVROOT / f"{pkg}-{ver}"
    py = env / "bin" / "python"
    if not _installed_ok(py, pkg, ver):
        ENVROOT.mkdir(exist_ok=True)
        subprocess.run(["uv", "venv", "--python", python, str(env)],
                       check=True, capture_output=True, text=True)
        subprocess.run(
            ["uv", "pip", "install", "--python", str(py), f"{pkg}=={ver}", *extra],
            check=True, capture_output=True, text=True,
        )
        if not _installed_ok(py, pkg, ver):
            raise RuntimeError(f"failed to provision {pkg}=={ver} on python {python}")
    return py


def run_observable(pkg: str, ver: str, script: str, x, extra=("numpy",),
                   python: str = "3.12") -> float:
    """Run `script x` under pkg==ver; the script prints a JSON line {"value": ...}."""
    py = ensure_env(pkg, ver, extra, python=python)
    out = subprocess.run([str(py), str(script), str(x)],
                         check=True, capture_output=True, text=True)
    last = out.stdout.strip().splitlines()[-1]
    return float(json.loads(last)["value"])
