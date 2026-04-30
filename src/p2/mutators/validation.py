"""Mechanical pre-validation before LLM review (L0 gate).

Checks applied to every generated mutant program string:
  V1  Syntax     — ast.parse succeeds
  V2  Executable — program(0.5) runs without exception, returns finite scalar or array
  V3  Non-trivial — |mutant(x) - original(x)| > 1e-6 for at least one x in probe set
                    (threshold matches AVP/E2 equivalence epsilon; see p2.equiv.judge)
  V4  Signature  — function named `program` with one positional argument exists
"""
import ast
import math
import types
import traceback
from typing import Callable

_PROBE_XS = [0.1, 0.3, 0.5, 0.7, 0.9]


def _load_program(code: str) -> tuple[bool, Callable | None, str]:
    """Exec code string, return (ok, program_fn, error_message)."""
    ns: dict = {}
    try:
        exec(compile(code, "<mutant>", "exec"), ns)  # noqa: S102
    except Exception:
        return False, None, traceback.format_exc(limit=3)
    fn = ns.get("program")
    if fn is None or not callable(fn):
        return False, None, "No callable `program` defined"
    return True, fn, ""


def _is_finite(val) -> bool:
    try:
        import numpy as np
        arr = np.asarray(val, dtype=float).flatten()
        return bool(np.all(np.isfinite(arr)))
    except Exception:
        return False


class ValidationResult:
    __slots__ = ("syntax_ok", "executable", "nontrivial", "error")

    def __init__(self, syntax_ok: bool, executable: bool, nontrivial: bool, error: str = ""):
        self.syntax_ok = syntax_ok
        self.executable = executable
        self.nontrivial = nontrivial
        self.error = error

    @property
    def passed(self) -> bool:
        return self.syntax_ok and self.executable and self.nontrivial

    def __repr__(self) -> str:
        return (f"ValidationResult(syntax={self.syntax_ok}, exec={self.executable}, "
                f"nontrivial={self.nontrivial}, err={self.error!r})")


def validate_mutant(code: str, original: Callable) -> ValidationResult:
    # V1 syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        return ValidationResult(False, False, False, str(e))

    # V4 signature check (simple: look for `def program`)
    if "def program" not in code:
        return ValidationResult(False, False, False, "No `def program` in code")

    # V2 executable
    ok, fn, err = _load_program(code)
    if not ok:
        return ValidationResult(True, False, False, err)

    outputs = []
    for x in _PROBE_XS:
        try:
            y = fn(x)
        except Exception as e:
            return ValidationResult(True, False, False, f"program({x}) raised: {e}")
        if not _is_finite(y):
            return ValidationResult(True, False, False, f"program({x}) → non-finite: {y}")
        outputs.append((x, y))

    # V3 non-trivial
    all_equiv = True
    for x, y_mut in outputs:
        try:
            import numpy as np
            y_orig = original(x)
            diff = float(np.linalg.norm(np.asarray(y_mut, float).flatten()
                                        - np.asarray(y_orig, float).flatten()))
            if diff > 1e-6:
                all_equiv = False
                break
        except Exception:
            all_equiv = False
            break

    if all_equiv:
        return ValidationResult(True, True, False, "Mutant output identical to original on probe set")

    return ValidationResult(True, True, True)
