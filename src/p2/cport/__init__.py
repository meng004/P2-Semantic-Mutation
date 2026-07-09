"""C-PUT port adapter (Study-4 / H-LANG language-invariance grid).

Public surface:
  CPutProgram        -- Callable[[float], float] over a compiled C PUT/mutant
  compile_c_source   -- gcc -O0 -lm build into a sandboxed build dir
  load_c_put         -- load src/p2/cput/{put_id}.c as a program
  validate_c_mutant  -- V1-V3 admission gate for C mutants
  CValidationResult, CCompileError
"""
from p2.cport.adapter import (
    CPutProgram,
    CCompileError,
    compile_c_source,
    load_c_put,
)
from p2.cport.validation import CValidationResult, validate_c_mutant

__all__ = [
    "CPutProgram",
    "CCompileError",
    "compile_c_source",
    "load_c_put",
    "CValidationResult",
    "validate_c_mutant",
]
