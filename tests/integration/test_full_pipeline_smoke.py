"""End-to-end smoke: registry → mech-validation → diversity metric (no LLM)."""
import importlib
import importlib.util
from pathlib import Path

from p2.mutators.operator_registry import OPERATORS, get_operators_for_put
from p2.mutators.diversity import diversity_score
from p2.mutators.validation import validate_mutant

ROOT = Path(__file__).parent.parent.parent


def test_every_put_has_loadable_program():
    for op in OPERATORS:
        spec = importlib.util.spec_from_file_location(
            op.put, ROOT / "src" / "p2" / "puts" / f"{op.put}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        y = mod.program(0.4)
        assert isinstance(y, (int, float)), (
            f"PUT {op.put} must return scalar; got {type(y).__name__}"
        )


def test_diversity_metric_nonzero_on_real_codes():
    codes = [
        "def program(x):\n    return float(x) ** 2\n",
        "def program(x):\n    return float(x) * float(x)\n",
        "def program(x):\n    y = float(x); return y * y\n",
    ]
    assert diversity_score(codes) > 0.0


def test_validation_module_loads_each_put():
    for op in OPERATORS:
        spec = importlib.util.spec_from_file_location(
            op.put, ROOT / "src" / "p2" / "puts" / f"{op.put}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # original passes V1-V2-V4 by definition; V3 is "non-trivial vs itself" → False
        res = validate_mutant(open(ROOT / "src" / "p2" / "puts" / f"{op.put}.py").read(),
                              mod.program)
        assert res.syntax_ok and res.executable
        assert not res.nontrivial  # PUT is never non-trivial vs itself
