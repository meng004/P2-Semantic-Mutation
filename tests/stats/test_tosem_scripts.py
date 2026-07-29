from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_power_scripts_use_frozen_primary_symbol():
    for name in ("compute_rq2_power.py", "compute_rq2_power_stipulated.py"):
        text = (ROOT / "scripts" / name).read_text()
        assert "PRIMARY_CELLS_V3 as PRIMARY" in text
        assert "PRIMARY_CELLS as PRIMARY" not in text


def test_cluster_script_declares_put_resampling():
    text = (ROOT / "scripts/compute_rq2_cluster_bootstrap.py").read_text()
    assert "n_boot=100_000" in text
    assert '"PUT"' in text
