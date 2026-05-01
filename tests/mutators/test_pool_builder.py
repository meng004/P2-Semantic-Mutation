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


def test_remainder_distributed_to_largest_pool(tmp_path):
    """divmod remainder goes to the operator with most candidates."""
    cache = tmp_path / "cache"; cache.mkdir()
    # op A has 5 candidates, op B has 5, op C has 5 — n_target=10 → 10/3=3 r=1
    for op, n in [("a2_CE1", 5), ("a2_OS1", 5), ("a2_SI1", 5)]:
        for k in range(n):
            (cache / f"{op}_attempt{k:02d}.py").write_text(
                f"def program(x):\n    return float(x) + {k}.0\n"
            )
    selected = select_mutants_for_put("a2", n_target=10, cache_dir=cache, seed=42)
    assert len(selected) == 10
    # All operators got at least 3; one got 4 (the remainder); none exceeded 5
    op_counts = {}
    for _, op in selected:
        op_counts[op] = op_counts.get(op, 0) + 1
    assert min(op_counts.values()) == 3
    assert max(op_counts.values()) == 4
    assert sum(op_counts.values()) == 10


def test_short_operator_redistributes_to_others(tmp_path):
    """When op A has only 1 candidate but quota would be 4, the 3 leftover
    slots should be filled from operators with spare capacity."""
    cache = tmp_path / "cache"; cache.mkdir()
    # op A: 1 candidate, ops B and C: 8 each — n_target=12, quotas {4,4,4} naively
    (cache / "a2_CE1_attempt00.py").write_text(
        "def program(x):\n    return float(x)\n"
    )
    for op in ("a2_OS1", "a2_SI1"):
        for k in range(8):
            (cache / f"{op}_attempt{k:02d}.py").write_text(
                f"def program(x):\n    return float(x) + {k}.0\n"
            )
    selected = select_mutants_for_put("a2", n_target=12, cache_dir=cache, seed=42)
    # With redistribution we should hit 12 (1 + 8 + 3 spare from B/C)
    assert len(selected) == 12


def test_returns_fewer_when_total_available_below_target(tmp_path):
    """Graceful return: n_actual <= n_available regardless of n_target."""
    cache = tmp_path / "cache"; cache.mkdir()
    for k in range(3):
        (cache / f"a2_CE1_attempt{k:02d}.py").write_text(
            f"def program(x):\n    return float(x) + {k}.0\n"
        )
    selected = select_mutants_for_put("a2", n_target=10, cache_dir=cache, seed=42)
    assert len(selected) == 3
