"""Build a per-PUT mutant pool by proportionally sampling the
v2.1 operator-campaign cache."""
import importlib.util
import random
from pathlib import Path
from typing import List, Tuple


def _is_valid_program(path: Path) -> bool:
    spec = importlib.util.spec_from_file_location(f"_v_{path.stem}", path)
    if spec is None or spec.loader is None:
        return False
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        prog = getattr(mod, "program", None)
        if prog is None:
            return False
        y = prog(0.5)
        return isinstance(y, (int, float))
    except Exception:
        return False


def select_mutants_for_put(
    put_id: str, n_target: int, cache_dir: Path, seed: int = 42,
) -> List[Tuple[Path, str]]:
    """Return up to n_target (path, op_id) pairs, proportional across operators
    that target this PUT. Filters out mutants that cannot be loaded or do not
    return a finite scalar."""
    rng = random.Random(seed)
    by_op: dict = {}
    for fp in sorted(cache_dir.glob(f"{put_id}_*_attempt*.py")):
        op_id = fp.name.split("_attempt")[0]
        by_op.setdefault(op_id, []).append(fp)
    valid_by_op: dict = {}
    for op_id, paths in by_op.items():
        valid_by_op[op_id] = [p for p in paths if _is_valid_program(p)]
    valid_by_op = {k: v for k, v in valid_by_op.items() if v}
    if not valid_by_op:
        return []
    n_ops = len(valid_by_op)
    base, rem = divmod(n_target, n_ops)
    quotas = {op: base for op in valid_by_op}
    extras = sorted(valid_by_op, key=lambda o: -len(valid_by_op[o]))[:rem]
    for op in extras:
        quotas[op] += 1
    selected: List[Tuple[Path, str]] = []
    for op_id, q in quotas.items():
        candidates = list(valid_by_op[op_id])
        rng.shuffle(candidates)
        for p in candidates[: min(q, len(candidates))]:
            selected.append((p, op_id))
    return selected
