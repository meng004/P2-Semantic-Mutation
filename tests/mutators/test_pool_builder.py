from pathlib import Path
from unittest.mock import patch
from p2.mutators.pool_builder import select_mutants_for_put


def test_select_returns_n_mutants_distributed_across_operators(tmp_path):
    cache = tmp_path / "cache"; cache.mkdir()
    for op in ("a2_CE1", "a2_OS1", "a2_SI1"):
        for k in range(4):
            (cache / f"{op}_attempt{k:02d}.py").write_text(
                f"def program(x):\n    return float(x) + {k}.0  # {op}\n"
            )
    selected = select_mutants_for_put(
        put_id="a2", n_target=9, cache_dir=cache, seed=42,
    )
    assert len(selected) == 9
    op_counts = {}
    for path, op_id in selected:
        op_counts[op_id] = op_counts.get(op_id, 0) + 1
    assert all(c == 3 for c in op_counts.values()), op_counts


def test_select_skips_invalid_mutants(tmp_path):
    cache = tmp_path / "cache"; cache.mkdir()
    (cache / "a2_CE1_attempt00.py").write_text("not python code")
    (cache / "a2_CE1_attempt01.py").write_text(
        "def program(x):\n    return float(x)\n"
    )
    selected = select_mutants_for_put(
        put_id="a2", n_target=1, cache_dir=cache, seed=42,
    )
    assert len(selected) == 1
    assert "attempt01" in selected[0][0].name
