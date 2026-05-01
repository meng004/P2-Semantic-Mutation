"""Render Figures 1-5 for §5 of the P2 paper from canonical JSON datasets."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.viz.boxplot import render_aligned_vs_cross  # noqa: E402
from p2.viz.forest import render_class_forest  # noqa: E402
from p2.viz.heatmap import render_60cell_heatmap  # noqa: E402
from p2.viz.scatter import render_scatter  # noqa: E402


def main() -> None:
    fig_dir = ROOT / "figures"
    fig_dir.mkdir(exist_ok=True)
    sms = json.loads((ROOT / "data/results/sms_track2_v2.json").read_text())
    lrca = json.loads((ROOT / "data/results/lrca_60cell.json").read_text())
    rq4 = json.loads((ROOT / "data/results/rq4_pattern_coverage.json").read_text())

    render_60cell_heatmap(sms, fig_dir / "fig1_60cell_heatmap.pdf")
    render_aligned_vs_cross(sms, fig_dir / "fig2_aligned_vs_cross_box.pdf")
    render_class_forest(sms, fig_dir / "fig3_class_forest.pdf")

    xs, ys = [], []
    for cell, sm in sms.items():
        if cell in lrca:
            xs.append(lrca[cell]["c1_share"])
            ys.append(sm["sms"])
    render_scatter(xs, ys, "C1_share (LRCA)", "SMS",
                   "SMS vs C1_share per cell (Figure 4)",
                   fig_dir / "fig4_sms_vs_c1share.pdf")

    xs = [v["pattern_coverage"] for v in rq4["per_put"].values()]
    ys = [v["mean_sms_over_5_cells"] for v in rq4["per_put"].values()]
    render_scatter(xs, ys, "Pattern coverage", "Mean SMS over 5 cells",
                   "SMS vs pattern coverage per PUT (Figure 5, RQ4)",
                   fig_dir / "fig5_sms_vs_pc.pdf")
    print("All 5 figures rendered to figures/")


if __name__ == "__main__":
    main()
