"""Build a per-PUT mutant pool by proportionally sampling the
v2.1 operator-campaign cache."""
import importlib.util
import random
import sys
from pathlib import Path
from typing import List, Tuple


# Module-level dedupe set: log only the first rejection of each exception type
# per process to avoid stderr spam during large pool builds while still
# surfacing the underlying cause for Round 7-8 LRCA debugging.
_SEEN_REJECT_TYPES: set = set()


def _record_reject(path: Path, exc: Exception) -> None:
    key = type(exc).__name__
    if key not in _SEEN_REJECT_TYPES:
        _SEEN_REJECT_TYPES.add(key)
        print(
            f"[pool_builder] first reject of type {key}: {path.name}: {exc!s:.120}",
            file=sys.stderr,
        )


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
    except Exception as e:
        _record_reject(path, e)
        return False


def select_mutants_for_put(
    put_id: str, n_target: int, cache_dir: Path, seed: int = 42,
) -> List[Tuple[Path, str]]:
    """Return up to n_target (path, op_id) pairs, proportional across operators
    that target this PUT. Filters out mutants that cannot be loaded or do not
    return a finite scalar.

    Distribution proceeds in two passes:

    1. Proportional pass: each operator gets ``n_target // n_ops`` slots, with
       the divmod remainder going to the operators with the most candidates.
    2. Redistribution pass: if any operator has fewer valid candidates than its
       quota, the unfilled slots are reallocated to operators that still have
       spare candidates (shuffled with the seeded RNG). This continues until
       either ``n_target`` is reached or no spare candidates remain — so a thin
       operator no longer silently shrinks the pool.

    When the total number of valid candidates is below ``n_target``, the
    function returns all of them (graceful degradation; the manifest's
    ``n_actual`` field captures the shortfall).
    """
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
    # First pass: shuffle each operator's candidate list once and take the
    # first `min(quota, available)` items. The shuffled order is preserved so
    # the redistribution pass can pick up where this pass left off.
    shuffled_by_op: dict = {}
    selected: List[Tuple[Path, str]] = []
    taken_count: dict = {}
    for op_id, q in quotas.items():
        candidates = list(valid_by_op[op_id])
        rng.shuffle(candidates)
        shuffled_by_op[op_id] = candidates
        take = min(q, len(candidates))
        taken_count[op_id] = take
        for p in candidates[:take]:
            selected.append((p, op_id))
    # Second pass: redistribute any unfilled slots to operators that still
    # have unselected candidates.
    needed = n_target - len(selected)
    if needed > 0:
        spare_pool: List[Tuple[Path, str]] = []
        for op_id, candidates in shuffled_by_op.items():
            for p in candidates[taken_count[op_id]:]:
                spare_pool.append((p, op_id))
        rng.shuffle(spare_pool)
        selected.extend(spare_pool[:needed])
    return selected
