"""Family-XL pair adapter: build an external program-language pair and expose
``program(x) -> float`` behind the registered subprocess line protocol.

This is the Study-5 generalisation of ``src/p2/cport.adapter.CPutProgram``
(PREREGISTRATION_STUDY5_v1.md §2c "Adapter layer"): persistent line REPL, one
``x`` per stdin line -> one float per stdout line, per-call timeout -> ``nan``,
crashed child auto-restart. Toolchains per the registration: ``gcc -std=c99
-O0 -Wall -lm`` (C), ``g++ -O0 -Wall`` (C++), ``javac/java`` (Java),
``go build`` (Go), ``rustc`` at opt-level 0 (Rust), ``julia`` (Julia).

P1 discipline (§1.6): every program under test lives UNMODIFIED under
``third_party/``; the shim sources in ``src/p2/xlport/shims/<pairid>/`` only
CALL the external entry points (wrapper shims are adapter code). The single
build-level accommodation is ``-Dmain=xl_ext_main`` (or an equivalent
``#define main`` in the shim before textually including an external
translation unit) to neutralise a demonstration ``main()`` shipped inside an
external source file; the external file's bytes are never edited.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import select
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[3]
SHIMS = Path(__file__).resolve().parent / "shims"
PYREF = Path(__file__).resolve().parent / "pyref"
DEFAULT_BUILD_ROOT = Path(tempfile.gettempdir()) / "p2_xlport_build"
DEFAULT_TIMEOUT = 20.0

CC = os.environ.get("CC", "gcc")
CXX = os.environ.get("CXX", "g++")
CFLAGS = ("-std=c99", "-O0", "-Wall")
CXXFLAGS = ("-O0", "-Wall")


class XlBuildError(RuntimeError):
    """Raised when a pair's toolchain build fails (registered V1 analogue)."""


def _spec(pair_id: str) -> tuple[Path, dict]:
    d = SHIMS / pair_id
    spec_path = d / "build.json"
    if not spec_path.exists():
        raise FileNotFoundError(f"no shim spec for pair '{pair_id}': {spec_path}")
    return d, json.loads(spec_path.read_text())


def _hash_key(pair_dir: Path, spec: dict) -> str:
    h = hashlib.sha256()
    h.update(json.dumps(spec, sort_keys=True).encode())
    for f in sorted(pair_dir.iterdir()):
        if f.is_file():
            h.update(f.name.encode())
            h.update(f.read_bytes())
    for rel in spec.get("external_sources", []) + list(spec.get("hash_extra", [])):
        p = ROOT / rel
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def _run(cmd, cwd=None, env=None) -> None:
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise XlBuildError(
            f"build failed ({proc.returncode}): {' '.join(map(str, cmd))}\n"
            f"{proc.stdout[-2000:]}\n{proc.stderr[-4000:]}"
        )


def build_pair(pair_id: str, build_root: Optional[Path] = None) -> list[str]:
    """Build (content-addressed, cached) and return the pair's run command."""
    pair_dir, spec = _spec(pair_id)
    lang = spec["language"]
    build_root = Path(build_root) if build_root else DEFAULT_BUILD_ROOT
    key = _hash_key(pair_dir, spec)
    bdir = build_root / f"{pair_id.replace('.', '_')}_{key}"
    stamp = bdir / ".ok"
    cmdfile = bdir / ".runcmd.json"
    if stamp.exists() and cmdfile.exists():
        return json.loads(cmdfile.read_text())
    if bdir.exists():
        shutil.rmtree(bdir)
    bdir.mkdir(parents=True)

    if lang == "c":
        out = bdir / "pair.bin"
        cmd = [CC, *CFLAGS, *spec.get("cflags", ())]
        for inc in spec.get("include_dirs", ()):
            cmd += ["-I", str(ROOT / inc)]
        for d in spec.get("defines", ()):
            cmd += [f"-D{d}"]
        cmd += ["-o", str(out), str(pair_dir / spec["shim"])]
        cmd += [str(ROOT / s) for s in spec.get("external_sources", ())]
        cmd += spec.get("libs", ["-lm"])
        _run(cmd)
        run_cmd = [str(out)]
    elif lang == "cpp":
        out = bdir / "pair.bin"
        cmd = [CXX, *CXXFLAGS, *spec.get("cxxflags", ())]
        for inc in spec.get("include_dirs", ()):
            cmd += ["-I", str(ROOT / inc)]
        for d in spec.get("defines", ()):
            cmd += [f"-D{d}"]
        # repo root on the include path so shims can textually include
        # external TUs by their stable third_party/ path.
        cmd += ["-I", str(ROOT)]
        cmd += ["-o", str(out), str(pair_dir / spec["shim"])]
        cmd += [str(ROOT / s) for s in spec.get("external_sources", ())]
        cmd += spec.get("libs", [])
        _run(cmd)
        run_cmd = [str(out)]
    elif lang == "java":
        classes = bdir / "classes"
        classes.mkdir()
        cp = [str(ROOT / j) for j in spec.get("classpath", ())]
        srcs = [str(pair_dir / spec["shim"])]
        srcs += [str(ROOT / s) for s in spec.get("external_sources", ())]
        cmd = ["javac", "-d", str(classes)]
        if cp:
            cmd += ["-cp", os.pathsep.join(cp)]
        cmd += srcs
        _run(cmd)
        run_cp = os.pathsep.join([str(classes), *cp])
        run_cmd = ["java", "-cp", run_cp, spec.get("main_class", "Main")]
    elif lang == "go":
        (bdir / "go.mod").write_text(
            f"module xlpair\n\ngo 1.21\n")
        shutil.copy(pair_dir / spec["shim"], bdir / "main.go")
        for pkg, files in spec.get("gopkg", {}).items():
            pdir = bdir / pkg
            pdir.mkdir()
            for rel in files:
                shutil.copy(ROOT / rel, pdir / Path(rel).name)
        env = dict(os.environ, GOPROXY="off", GOFLAGS="-mod=mod")
        env.setdefault("GOCACHE", str(build_root / "gocache"))
        out = bdir / "pair.bin"
        _run(["go", "build", "-o", str(out), "."], cwd=bdir, env=env)
        run_cmd = [str(out)]
    elif lang == "rust":
        # vendored external file copied VERBATIM into the build dir so the
        # shim's `#[path = "ext.rs"] mod ext;` resolves; bytes unmodified.
        shutil.copy(ROOT / spec["external_rs"], bdir / "ext.rs")
        shutil.copy(pair_dir / spec["shim"], bdir / "main.rs")
        out = bdir / "pair.bin"
        _run(["rustc", "-C", "opt-level=0", "--edition", "2021",
              "-o", str(out), str(bdir / "main.rs")])
        run_cmd = [str(out)]
    elif lang == "julia":
        julia = os.environ.get("XL_JULIA_BIN", "julia")
        run_cmd = [julia, "--startup-file=no", "-O0",
                   str(pair_dir / spec["shim"])]
    else:
        raise XlBuildError(f"unknown language {lang!r} for pair {pair_id!r}")

    cmdfile.write_text(json.dumps(run_cmd))
    stamp.write_text("ok")
    return run_cmd


class XlPairProgram:
    """Callable ``program(x)`` over a built external pair (REPL protocol)."""

    def __init__(self, pair_id: str, build_root: Optional[Path] = None,
                 timeout: float = DEFAULT_TIMEOUT):
        self.pair_id = pair_id
        self._build_root = build_root
        self.timeout = timeout
        self._cmd: Optional[list[str]] = None
        self._proc: Optional[subprocess.Popen] = None

    @property
    def cmd(self) -> list[str]:
        if self._cmd is None:
            self._cmd = build_pair(self.pair_id, self._build_root)
        return self._cmd

    def _ensure_proc(self) -> None:
        if self._proc is None or self._proc.poll() is not None:
            self._proc = subprocess.Popen(
                self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, bufsize=1,
            )

    def _kill(self) -> None:
        if self._proc is not None:
            try:
                self._proc.kill()
                self._proc.wait(timeout=2)
            except Exception:
                pass
            self._proc = None

    def close(self) -> None:
        self._kill()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def __call__(self, x) -> float:
        x = float(x)
        for _attempt in (0, 1):
            self._ensure_proc()
            assert self._proc is not None and self._proc.stdin and self._proc.stdout
            try:
                self._proc.stdin.write(f"{x!r}\n")
                self._proc.stdin.flush()
            except (BrokenPipeError, ValueError, OSError):
                self._kill()
                continue
            ready, _, _ = select.select([self._proc.stdout], [], [], self.timeout)
            if not ready:
                self._kill()
                return math.nan
            line = self._proc.stdout.readline()
            if line == "":
                self._kill()
                continue
            try:
                return float(line.strip())
            except ValueError:
                return math.nan
        return math.nan


def load_pair(pair_id: str, build_root: Optional[Path] = None) -> XlPairProgram:
    return XlPairProgram(pair_id, build_root=build_root)


def load_pyref(program: str):
    """Load the Python-side reference ``program(x)`` for a rostered program."""
    import importlib.util

    path = PYREF / f"{program}.py"
    if not path.exists():
        raise FileNotFoundError(f"no python reference for program '{program}'")
    spec = importlib.util.spec_from_file_location(f"xl_pyref_{program}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.program
