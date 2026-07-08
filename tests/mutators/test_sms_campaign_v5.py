"""Regression tests for scripts/sms_campaign.py pilot fixes.

Covers v5 (Study-2) pool resolution — STRICT, never falling back to a Study-1
pool — arbitrary new PUT ids (a4..d8), and the --puts cell restriction used by
the calibration pilot.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_sms():
    spec = importlib.util.spec_from_file_location(
        "_sms_campaign_test", ROOT / "scripts" / "sms_campaign.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sms = _load_sms()


# ── v5 pool resolution is strict (the pilot bug: v5 → scored v3) ───────────
def test_v5_resolves_to_v5_pool_not_v3():
    d = sms.resolve_pool_dir("a2", pool_version="v5")
    assert d.name == "a2_pool_v5"


def test_v4_resolves_to_v4_pool():
    assert sms.resolve_pool_dir("b4", pool_version="v4").name == "b4_pool_v4"


def test_v5_never_falls_back_to_study1_even_when_v3_exists(monkeypatch, tmp_path):
    # Simulate a PUT whose Study-1 v3 pool exists but v5 does not: strict v5
    # must still point at the (absent) v5 dir, never the frozen v3 one.
    monkeypatch.setattr(sms, "MUTANTS_DIR", tmp_path)
    (tmp_path / "a2_pool_v3").mkdir()
    (tmp_path / "a2_pool").mkdir()
    d = sms.resolve_pool_dir("a2", pool_version="v5")
    assert d.name == "a2_pool_v5"
    assert not d.exists()          # absent → inst=0 downstream, a VISIBLE failure


def test_unset_version_legacy_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(sms, "MUTANTS_DIR", tmp_path)
    (tmp_path / "c1_pool_v3").mkdir()
    assert sms.resolve_pool_dir("c1", pool_version="").name == "c1_pool_v3"


# ── arbitrary new PUT ids are first-class ──────────────────────────────────
def test_new_put_ids_present_in_primary_cells():
    from p2.config.primary import PRIMARY_CELLS
    for pid in ("a4", "a8", "b4", "b7", "c4", "c7", "d4", "d8"):
        assert pid in PRIMARY_CELLS


def test_new_put_v5_resolution():
    for pid in ("a4", "d8", "b4"):
        assert sms.resolve_pool_dir(pid, pool_version="v5").name == f"{pid}_pool_v5"


# ── --puts restriction: the 10-cell calibration pilot ─────────────────────
def test_puts_filter_track2_gives_10_pilot_cells():
    cells = sms._build_cell_list(track=2, cell=None, mp=None, puts=["a2", "b4"])
    assert len(cells) == 10                       # 2 PUTs × 5 MPs
    assert {p for p, _ in cells} == {"a2", "b4"}
    assert sorted({k for _, k in cells}) == [1, 2, 3, 4, 5]


def test_puts_filter_track1():
    cells = sms._build_cell_list(track=1, cell=None, mp=None, puts=["b4"])
    from p2.config.primary import PRIMARY_CELLS
    assert cells == [("b4", PRIMARY_CELLS["b4"])]


def test_no_puts_filter_track2_full_matrix():
    cells = sms._build_cell_list(track=2, cell=None, mp=None, puts=None)
    from p2.config.primary import PRIMARY_CELLS
    assert len(cells) == len(PRIMARY_CELLS) * 5
