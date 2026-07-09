"""Mechanical pre-validation for C mutants (C-grid analogue of
``p2.mutators.validation``).

The Python gate checks V1 syntax (ast.parse), V2 executable (finite on a
probe set), V3 non-trivial (differs from the original on the probe set).
The C gate is the language-faithful mirror:

  V1  Syntax     -> the source COMPILES with ``gcc -O0 -Wall`` (a C
                    program has no separate parse step; a clean compile is
                    the syntactic + signature gate).
  V2  Executable -> ``program(x)`` runs (via the adapter) and returns a
                    finite float for every probe x.
  V3  Non-trivial -> |mutant(x) - original(x)| > 1e-6 for at least one
                    probe x (same epsilon as the Python V3 / AVP-E2).

Signature (V4) is folded into V1: the C source must define
``double program(double x)`` or it will not compile against the harness
``main`` (both live in the same self-contained .c file, exactly as the
Python PUT defines ``program`` in one module).
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Callable, Optional, Union

from p2.cport.adapter import CPutProgram, CCompileError, compile_c_source

_PROBE_XS = [0.1, 0.3, 0.5, 0.7, 0.9]


class CValidationResult:
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
        return (f"CValidationResult(syntax={self.syntax_ok}, "
                f"exec={self.executable}, nontrivial={self.nontrivial}, "
                f"err={self.error!r})")


def validate_c_mutant(
    code: Union[str, Path],
    original: Callable,
    build_dir: Optional[Union[str, Path]] = None,
) -> CValidationResult:
    """Run the V1-V3 admission gate on a candidate C mutant.

    ``original`` is any callable ``program(x) -> float`` (typically a
    :class:`CPutProgram` for the C original PUT). Mirrors
    :func:`p2.mutators.validation.validate_mutant`.
    """
    # V1: compile (syntax + signature)
    try:
        compile_c_source(code, build_dir)
    except CCompileError as e:
        return CValidationResult(False, False, False, str(e))

    prog = CPutProgram(code, build_dir=build_dir)

    # V2: executable + finite on the probe set
    outputs = []
    for x in _PROBE_XS:
        y = prog(x)
        if not math.isfinite(y):
            prog.close()
            return CValidationResult(True, False, False,
                                     f"program({x}) -> non-finite: {y}")
        outputs.append((x, y))

    # V3: non-trivial vs original
    all_equiv = True
    for x, y_mut in outputs:
        try:
            y_orig = float(original(x))
        except Exception:
            all_equiv = False
            break
        if math.isfinite(y_orig) and abs(y_mut - y_orig) > 1e-6:
            all_equiv = False
            break
    prog.close()
    if all_equiv:
        return CValidationResult(True, True, False,
                                 "Mutant output identical to original on probe set")
    return CValidationResult(True, True, True)
