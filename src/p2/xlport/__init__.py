"""Family-XL adapter layer (Study 5, PREREGISTRATION_STUDY5_v1.md §2b/§2c).

Adapter/oracle-layer code ONLY (author-directed principle P1, §1.6): every
program under test is externally authored and vendored unmodified under
``third_party/``; this package contains the wrapper shims that call the
external entry points, the per-language build/run adapters (subprocess line
protocol, the registered ``src/p2/cport`` CPutProgram pattern), and the
Python-side reference shims used by the §2c certification gate.
"""
from .adapter import XlBuildError, XlPairProgram, load_pair, load_pyref  # noqa: F401
