"""C-PUT adapter: compile a C PUT/mutant and expose ``program(x) -> float``.

This is the language-invariance bridge for Study-4 (H-LANG). A C source
file that defines ``double program(double x)`` plus the standard REPL
``main`` (see src/p2/cput/*.c) is compiled with ``gcc -O0 -lm`` into a
sandboxed build directory and driven through a persistent line protocol:
the harness writes one ``x`` per line to the child's stdin and reads one
float per line from its stdout.

The resulting :class:`CPutProgram` is a plain ``Callable[[float], float]``,
so the EXISTING metamorphic-relation machinery (src/p2/mrs/*.py, AVP,
equivalence judge, run_one_cell, sms_campaign) evaluates C cells with NO
modification: to those callers a CPutProgram is indistinguishable from a
Python PUT's ``program``.

Determinism / RNG: stochastic C kernels (b2, b3, c2) embed a fixed-seed
LCG. The contract vs the Python reference is distributional, not
bit-equality (see docs/prereg_v2/C_PORT_SPEC.md).
"""
from __future__ import annotations

import hashlib
import math
import os
import select
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Optional, Union

DEFAULT_BUILD_DIR = Path(tempfile.gettempdir()) / "p2_cport_build"
DEFAULT_CC = os.environ.get("CC", "gcc")
# -O0 (task requirement), C99, warnings surfaced, libm for the numeric kernels.
DEFAULT_CFLAGS = ("-std=c99", "-O0", "-Wall")
DEFAULT_TIMEOUT = 10.0


class CCompileError(RuntimeError):
    """Raised when gcc fails to build a C PUT/mutant."""


def _resolve_source(source: Union[str, Path]) -> tuple[str, str]:
    """Return (code_text, stem) for a path or a raw code string.

    A ``Path`` is always read as a file. A ``str`` is treated as a file path
    ONLY when it is non-empty, single-line, and points at an existing regular
    FILE; otherwise it is raw code. This guards the P13 pilot defect where an
    empty/whitespace LLM body ``""`` made ``Path("")`` resolve to the cwd
    directory (``.``) and ``read_text()`` raised ``IsADirectoryError`` — an empty
    body must fall through as raw code so gcc fails it as a normal V1 miss."""
    if isinstance(source, Path):
        return source.read_text(), source.stem
    s = str(source)
    if s and "\n" not in s:
        try:
            p = Path(s)
            if p.is_file():                     # is_file() is False for "." (a dir)
                return p.read_text(), p.stem
        except (OSError, ValueError):           # path too long / invalid -> raw code
            pass
    return s, "inline"


def compile_c_source(
    source: Union[str, Path],
    build_dir: Optional[Union[str, Path]] = None,
    cc: str = DEFAULT_CC,
    cflags: Iterable[str] = DEFAULT_CFLAGS,
    extra_flags: Iterable[str] = (),
) -> Path:
    """Compile a C PUT/mutant to an executable; return the binary path.

    The binary is content-addressed (hash of source + flags) inside
    ``build_dir`` so repeated compiles of identical source are cached.
    Raises :class:`CCompileError` on a non-zero gcc exit.
    """
    code, stem = _resolve_source(source)
    build_dir = Path(build_dir) if build_dir else DEFAULT_BUILD_DIR
    build_dir.mkdir(parents=True, exist_ok=True)
    flags = list(cflags) + list(extra_flags)
    key = hashlib.sha256((code + "\0" + "\0".join(flags)).encode()).hexdigest()[:16]
    src_path = build_dir / f"{stem}_{key}.c"
    bin_path = build_dir / f"{stem}_{key}.bin"
    if bin_path.exists():
        return bin_path
    src_path.write_text(code)
    cmd = [cc, *flags, "-o", str(bin_path), str(src_path), "-lm"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not bin_path.exists():
        raise CCompileError(
            f"gcc failed ({proc.returncode}) for {stem}:\n{proc.stderr.strip()}"
        )
    return bin_path


class CPutProgram:
    """Callable wrapper over a compiled C PUT/mutant.

    ``CPutProgram(source)(x)`` compiles once (lazily on first call) and
    then serves each evaluation through a persistent child process. A
    hung evaluation (mutant infinite loop) is bounded by ``timeout`` and
    yields ``nan``; a crashed child is transparently restarted.
    """

    def __init__(
        self,
        source: Union[str, Path],
        build_dir: Optional[Union[str, Path]] = None,
        timeout: float = DEFAULT_TIMEOUT,
        cflags: Iterable[str] = DEFAULT_CFLAGS,
        extra_flags: Iterable[str] = (),
    ):
        self._source = source
        self._build_dir = build_dir
        self._cflags = tuple(cflags)
        self._extra = tuple(extra_flags)
        self.timeout = timeout
        self._binary: Optional[Path] = None
        self._proc: Optional[subprocess.Popen] = None

    # -- lifecycle -------------------------------------------------------
    @property
    def binary(self) -> Path:
        if self._binary is None:
            self._binary = compile_c_source(
                self._source, self._build_dir, cflags=self._cflags,
                extra_flags=self._extra,
            )
        return self._binary

    def _ensure_proc(self) -> None:
        if self._proc is None or self._proc.poll() is not None:
            self._proc = subprocess.Popen(
                [str(self.binary)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, bufsize=1,
            )

    def _kill(self) -> None:
        if self._proc is not None:
            try:
                self._proc.kill()
                self._proc.wait(timeout=1)
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

    # -- evaluation ------------------------------------------------------
    def __call__(self, x) -> float:
        x = float(x)
        for attempt in (0, 1):
            self._ensure_proc()
            assert self._proc is not None and self._proc.stdin and self._proc.stdout
            try:
                self._proc.stdin.write(f"{x!r}\n")
                self._proc.stdin.flush()
            except (BrokenPipeError, ValueError, OSError):
                self._kill()
                continue  # restart once
            ready, _, _ = select.select([self._proc.stdout], [], [], self.timeout)
            if not ready:
                self._kill()          # hung on this input
                return math.nan
            line = self._proc.stdout.readline()
            if line == "":            # child died producing output
                self._kill()
                continue              # restart once
            try:
                return float(line.strip())
            except ValueError:
                return math.nan
        return math.nan


def load_c_put(put_id: str, root: Union[str, Path],
               build_dir: Optional[Union[str, Path]] = None) -> CPutProgram:
    """Load the C PUT ``src/p2/cput/{put_id}.c`` as a callable program.

    Mirror of :func:`p2.pipeline.loaders.load_put` for the C grid.
    """
    root = Path(root)
    src = root / "src" / "p2" / "cput" / f"{put_id.lower()}.c"
    if not src.exists():
        raise FileNotFoundError(f"no C PUT for '{put_id}': {src}")
    return CPutProgram(src, build_dir=build_dir)
