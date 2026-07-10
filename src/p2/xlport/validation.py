"""Mechanical V1–V3 admission gate for Family-XL mutants (registration §2c).

XL analogue of ``p2.cport.validation`` (the registered C-arm precedent),
driven by the pair's own toolchain from ``src/p2/xlport/shims/<pair>/build.json``:

  V1  Syntax      -> the mutant source COMPILES/PARSES in the pair's
                     registered toolchain (V4 signature folded in: the
                     source must keep the ``program`` entry + REPL main or
                     the build/probe fails).
  V2  Executable  -> the built mutant answers every certification-grid probe
                     x in {0.1, 0.3, 0.5, 0.7, 0.9} with a finite float via
                     the registered line-REPL adapter (§2c probe set).
  V3  Non-trivial -> |mutant(x) - original(x)| > 1e-6 for at least one
                     probe x (same epsilon as the Python/C V3).

A MUTANT here is one complete, self-contained source file for the pair's
mutable composition (see ``mutable_source``): for source-vendored pairs the
external translation unit textually inlined into the REPL shim; for
library-backed pairs (e.g. GSL) the shim/driver translation unit compiled
against the UNMODIFIED external library. The vendored ``third_party/`` bytes
and the frozen shim on disk are never touched by admission; every mutant
builds in its own scratch directory.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional, Union

from p2.xlport.adapter import (
    CC, CXX, CFLAGS, CXXFLAGS, ROOT, SHIMS, XlBuildError, XlPairProgram,
)

_PROBE_XS = [0.1, 0.3, 0.5, 0.7, 0.9]           # §2c certification-grid probes
_V3_EPS = 1e-6

_EXT = {"c": ".c", "cpp": ".cpp", "java": ".java", "go": ".go",
        "rust": ".rs", "julia": ".jl"}

_INCLUDE_RE = re.compile(r'^[ \t]*#[ \t]*include[ \t]*"(third_party/[^"]+)"',
                         re.MULTILINE)


def pair_spec(pair_id: str) -> dict:
    return json.loads((SHIMS / pair_id / "build.json").read_text())


def pair_ext(pair_id: str) -> str:
    return _EXT[pair_spec(pair_id)["language"]]


def mutable_source(pair_id: str) -> str:
    """The pair's complete single-file mutable composition (the text shown to
    generators and the text a mutant replaces).

    Source-vendored pairs: the shim with each ``#include "third_party/..."``
    replaced by that file's verbatim contents (the surrounding
    ``#define main xl_ext_main`` guard in the shim keeps neutralising the
    external demo ``main``). Library-backed pairs (no vendored source files,
    e.g. GSL): the shim/driver translation unit itself — the external
    implementation stays behind its linked, unmodified library.
    """
    d = SHIMS / pair_id
    spec = pair_spec(pair_id)
    shim = (d / spec["shim"]).read_text()

    def _inline(m: re.Match) -> str:
        p = ROOT / m.group(1)
        return p.read_text()

    return _INCLUDE_RE.sub(_inline, shim)


def compile_xl_mutant(code: Union[str, Path], pair_id: str,
                      build_dir: Optional[Union[str, Path]] = None) -> Path:
    """Compile one mutant source with the pair's registered toolchain (V1).

    Returns the built binary path; raises :class:`XlBuildError` on failure.
    Pilot scope: C and C++ (the two registered pilot pairs). Other
    toolchains are added at their first confirmatory use.
    """
    spec = pair_spec(pair_id)
    lang = spec["language"]
    if lang not in ("c", "cpp"):
        raise XlBuildError(
            f"mutant toolchain for language {lang!r} not wired yet "
            f"(pilot covers c/cpp)")
    bdir = Path(build_dir) if build_dir else Path(tempfile.mkdtemp(
        prefix="xlmut_", dir=tempfile.gettempdir()))
    bdir.mkdir(parents=True, exist_ok=True)
    src = code if isinstance(code, Path) else None
    if src is None:
        src = bdir / f"mutant{_EXT[lang]}"
        src.write_text(code)                     # type: ignore[arg-type]
    out = bdir / (Path(src).stem + ".bin")
    if lang == "c":
        cmd = [CC, *CFLAGS, *spec.get("cflags", ())]
    else:
        cmd = [CXX, *CXXFLAGS, *spec.get("cxxflags", ())]
    for inc in spec.get("include_dirs", ()):
        cmd += ["-I", str(ROOT / inc)]
    cmd += ["-I", str(ROOT)]                     # third_party/ include root
    cmd += ["-o", str(out), str(src)]
    cmd += spec.get("libs", ["-lm"] if lang == "c" else [])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise XlBuildError(
            f"V1 compile failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"{proc.stdout[-1500:]}\n{proc.stderr[-3000:]}")
    return out


class XlMutantProgram(XlPairProgram):
    """Callable ``program(x)`` over one compiled mutant binary (line REPL)."""

    def __init__(self, binary: Path, timeout: float = 20.0):
        super().__init__(pair_id=f"mutant:{binary.name}", timeout=timeout)
        self._cmd = [str(binary)]


def load_xl_mutant(source: Union[str, Path], pair_id: str,
                   build_dir: Optional[Union[str, Path]] = None) -> XlMutantProgram:
    return XlMutantProgram(compile_xl_mutant(source, pair_id, build_dir))


class XlValidationResult:
    __slots__ = ("syntax_ok", "executable", "nontrivial", "error")

    def __init__(self, syntax_ok: bool, executable: bool, nontrivial: bool,
                 error: str = ""):
        self.syntax_ok = syntax_ok
        self.executable = executable
        self.nontrivial = nontrivial
        self.error = error

    @property
    def passed(self) -> bool:
        return self.syntax_ok and self.executable and self.nontrivial

    def __repr__(self) -> str:
        return (f"XlValidationResult(syntax={self.syntax_ok}, "
                f"exec={self.executable}, nontrivial={self.nontrivial}, "
                f"err={self.error!r})")


def validate_xl_mutant(
    code: str, pair_id: str, original: Callable,
    build_dir: Optional[Union[str, Path]] = None,
) -> XlValidationResult:
    """Run the registered §2c V1–V3 gate on one candidate XL mutant."""
    try:
        binary = compile_xl_mutant(code, pair_id, build_dir)
    except XlBuildError as e:
        return XlValidationResult(False, False, False, str(e))

    prog = XlMutantProgram(binary)
    try:
        outputs = []
        for x in _PROBE_XS:                      # V2: finite on the probe grid
            y = prog(x)
            if not math.isfinite(y):
                return XlValidationResult(True, False, False,
                                          f"program({x}) -> non-finite: {y}")
            outputs.append((x, y))

        all_equiv = True                         # V3: non-trivial vs original
        for x, y_mut in outputs:
            try:
                y_orig = float(original(x))
            except Exception:
                all_equiv = False
                break
            if math.isfinite(y_orig) and abs(y_mut - y_orig) > _V3_EPS:
                all_equiv = False
                break
        if all_equiv:
            return XlValidationResult(
                True, True, False,
                "Mutant output identical to original on probe set")
        return XlValidationResult(True, True, True)
    finally:
        prog.close()
