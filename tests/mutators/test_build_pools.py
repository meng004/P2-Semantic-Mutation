"""Regression tests for scripts/build_pools.py — the pilot defect fixes.

Covers the SAFETY gates that prevent the Study-1 v3-pool wipe incident
(docs/prereg_v2/PILOT_LOG.md #1): empty-cache refusal, no empty-overwrite of a
populated pool, wrong-version deletion guard, frozen-version guard, and correct
v5 version mapping.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_build_pools():
    spec = importlib.util.spec_from_file_location(
        "_build_pools_test", ROOT / "scripts" / "build_pools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bp = _load_build_pools()


def _write_valid_mutants(cache: Path, put="a2", ops=("CE1", "OS1", "SI1"),
                         source="claude", k=3):
    cache.mkdir(parents=True, exist_ok=True)
    for op in ops:
        for a in range(1, k + 1):
            (cache / f"{put}_{op}_{source}_attempt{a:02d}.py").write_text(
                f"def program(x):\n    return float(x) + 0.{a}  # {op}\n")


# ── version mapping ────────────────────────────────────────────────────────
def test_v5_version_spec_matches_v4_selection_and_cache_cross():
    v5 = bp.version_spec("v5")
    v4 = bp.version_spec("v4")
    assert v5["suffix"] == "_pool_v5"
    assert v5["cache"] == "cache_cross"
    assert v5["n"] == 30 == v4["n"]          # same 30-mutant selection as v4
    assert v5["frozen"] is False
    assert "v5" in bp._STUDY2_VERSIONS       # CF/TF filter applies to v5


def test_frozen_versions_flagged():
    assert bp.version_spec("v2")["frozen"] is True
    assert bp.version_spec("v3")["frozen"] is True
    assert bp.version_spec("v4")["frozen"] is False


def test_unknown_version_rejected():
    with pytest.raises(ValueError):
        bp.version_spec("v9")


def test_puts_autodetect_from_cache(tmp_path):
    cache = tmp_path / "cache_cross"
    _write_valid_mutants(cache, put="a2")
    _write_valid_mutants(cache, put="b4", ops=("TF1",))
    assert bp.puts_in_cache(cache) == ["a2", "b4"]


# ── SAFETY: empty cache ────────────────────────────────────────────────────
def test_empty_cache_refused(tmp_path):
    cache = tmp_path / "cache_cross"
    cache.mkdir()
    with pytest.raises(RuntimeError, match="empty"):
        bp.build_pools(["a2"], "v5", cache, mutants_dir=tmp_path / "mut",
                       allow_empty=False, screen_fn=lambda *_: True, verbose=False)


def test_empty_cache_allowed_with_flag(tmp_path):
    cache = tmp_path / "cache_cross"
    cache.mkdir()
    res = bp.build_pools(["a2"], "v5", cache, mutants_dir=tmp_path / "mut",
                         allow_empty=True, screen_fn=lambda *_: True, verbose=False)
    assert res[0]["n_actual"] == 0


# ── SAFETY: never overwrite a populated pool with an empty rebuild ─────────
def test_empty_selection_does_not_wipe_existing_pool(tmp_path):
    mut = tmp_path / "mut"
    existing = mut / "a2_pool_v5"
    existing.mkdir(parents=True)
    (existing / "m01_a2_CE1_a01.py").write_text("def program(x):\n    return x\n")
    cache = tmp_path / "cache_cross"          # non-empty cache, but no a2 mutants
    _write_valid_mutants(cache, put="b4", ops=("TF1",))
    # a2 selection is empty → the existing populated a2 pool must be untouched.
    res = bp.build_pools(["a2"], "v5", cache, mutants_dir=mut,
                         allow_empty=False, screen_fn=lambda *_: True, verbose=False)
    assert res[0]["skipped"] is True
    assert (existing / "m01_a2_CE1_a01.py").exists()


# ── SAFETY: wrong-version deletion guard ───────────────────────────────────
def test_wrong_version_deletion_guard_direct():
    # a v3 pool dir must never be deleted while building v5 (suffix mismatch).
    with pytest.raises(RuntimeError, match="wrong-version deletion guard"):
        bp._assert_version_match(Path("data/mutants/a2_pool_v3"), "_pool_v5")
    # residual not a bare PUT id
    with pytest.raises(RuntimeError, match="wrong-version deletion guard"):
        bp._assert_version_match(Path("data/mutants/garbage_pool_v5"), "_pool_v5")
    # correct match passes
    bp._assert_version_match(Path("data/mutants/a2_pool_v5"), "_pool_v5")


def test_v5_build_never_touches_v3_pool(tmp_path):
    mut = tmp_path / "mut"
    v3_pool = mut / "a2_pool_v3"            # frozen Study-1 pool sitting alongside
    v3_pool.mkdir(parents=True)
    (v3_pool / "keep.py").write_text("def program(x):\n    return x\n")
    cache = tmp_path / "cache_cross"
    _write_valid_mutants(cache, put="a2")
    bp.build_pools(["a2"], "v5", cache, mutants_dir=mut,
                   allow_empty=False, screen_fn=lambda *_: True, verbose=False)
    # v3 pool untouched; v5 pool created separately.
    assert (v3_pool / "keep.py").exists()
    assert (mut / "a2_pool_v5" / "manifest.json").exists()


# ── SAFETY: frozen Study-1 version guard ───────────────────────────────────
def test_frozen_version_refused_without_flag(tmp_path):
    cache = tmp_path / "cache"
    _write_valid_mutants(cache, put="a2")
    with pytest.raises(RuntimeError, match="FROZEN"):
        bp.build_pools(["a2"], "v3", cache, mutants_dir=tmp_path / "mut",
                       allow_frozen=False, verbose=False)


def test_frozen_version_allowed_with_flag(tmp_path):
    cache = tmp_path / "cache"
    _write_valid_mutants(cache, put="a2")
    res = bp.build_pools(["a2"], "v3", cache, mutants_dir=tmp_path / "mut",
                         allow_frozen=True, verbose=False)
    assert res[0]["n_actual"] > 0


# ── happy path: v5 build writes a manifest tagged with the version ─────────
def test_v5_build_writes_versioned_manifest(tmp_path):
    import json
    cache = tmp_path / "cache_cross"
    _write_valid_mutants(cache, put="a2")     # 9 valid, no CF/TF
    res = bp.build_pools(["a2"], "v5", cache, mutants_dir=tmp_path / "mut",
                         screen_fn=lambda *_: True, verbose=False)
    assert res[0]["n_actual"] == 9            # min(30, 9 available)
    man = json.loads((tmp_path / "mut" / "a2_pool_v5" / "manifest.json").read_text())
    assert man["version"] == "v5"
    assert man["n_target"] == 30
