"""Verify mutant_dir auto-resolution: prefer _pool/ over legacy _MP{k}_llm/.

Locks the precedence rule introduced in Round 4 so future refactors can't
silently revert to the legacy 3-5 mutant pool when the enriched 8-12 mutant
pool exists.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _load_sms_campaign():
    """Load scripts/sms_campaign.py as a module (scripts/ is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "_sms_campaign", ROOT / "scripts" / "sms_campaign.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# A trivial mutant body — actual SMS values don't matter for this test;
# we only inspect which directory's files appear in `outcomes`.
_MUTANT_BODY = "def program(x):\n    return float(x) * 2.0\n"
_MUTANT_BODY_LEGACY = "def program(x):\n    return float(x) + 1.0\n"


def test_pool_preferred_over_legacy(tmp_path, monkeypatch):
    """Both _pool/ and legacy dirs exist -> _pool/ wins."""
    sms = _load_sms_campaign()

    pool = tmp_path / "a2_pool"
    legacy = tmp_path / "a2_MP1_llm"
    pool.mkdir()
    legacy.mkdir()
    (pool / "m01_pool.py").write_text(_MUTANT_BODY)
    (legacy / "m01_legacy.py").write_text(_MUTANT_BODY_LEGACY)

    monkeypatch.setattr(sms, "MUTANTS_DIR", tmp_path)

    res = sms.evaluate_cell(put_id="a2", mp_k=1)
    assert any("pool" in o["file"] for o in res["outcomes"]), res["outcomes"]
    assert not any("legacy" in o["file"] for o in res["outcomes"]), res["outcomes"]
    # Reproducibility metadata should also reflect _pool/.
    assert res["mutant_dir"].endswith("a2_pool"), res["mutant_dir"]


def test_legacy_fallback_when_pool_absent(tmp_path, monkeypatch):
    """Only legacy dir exists -> legacy is used."""
    sms = _load_sms_campaign()

    legacy = tmp_path / "a2_MP1_llm"
    legacy.mkdir()
    (legacy / "m01_legacy.py").write_text(_MUTANT_BODY_LEGACY)

    monkeypatch.setattr(sms, "MUTANTS_DIR", tmp_path)

    res = sms.evaluate_cell(put_id="a2", mp_k=1)
    assert any("legacy" in o["file"] for o in res["outcomes"]), res["outcomes"]
    assert res["mutant_dir"].endswith("a2_MP1_llm"), res["mutant_dir"]
