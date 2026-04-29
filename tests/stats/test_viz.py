import numpy as np
import matplotlib
matplotlib.use("Agg")
from pathlib import Path
import tempfile
from p2.stats.viz import plot_sms_heatmap


def test_heatmap_saves_file():
    sms_grid = np.random.RandomState(0).rand(12, 5, 5)
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "heat.png"
        plot_sms_heatmap(sms_grid, out_path=out)
        assert out.exists() and out.stat().st_size > 0
