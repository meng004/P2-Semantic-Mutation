"""Smoke test: each viz module writes a non-empty PDF."""
import numpy as np

from p2.viz.heatmap import render_60cell_heatmap


def test_heatmap_writes_pdf(tmp_path):
    rng = np.random.default_rng(42)
    sms_data = {f"{p.upper()}_MP{k}": {"sms": float(rng.random())}
                for p in ("a1", "a2", "b1", "c1", "d1") for k in (1, 2, 3, 4, 5)}
    out = tmp_path / "fig1.pdf"
    render_60cell_heatmap(sms_data, out_path=out)
    assert out.exists() and out.stat().st_size > 1000
