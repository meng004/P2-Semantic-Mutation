"""Aligned vs cross SMS box plot (Figure 2)."""
from pathlib import Path

import matplotlib.pyplot as plt

PRIMARY = {"a1": 1, "a2": 1, "a3": 1, "b1": 2, "b2": 2, "b3": 2,
           "c1": 5, "c2": 5, "c3": 5, "d1": 2, "d2": 2, "d3": 2}


def render_aligned_vs_cross(sms_data: dict, out_path: Path) -> None:
    """Box plot of aligned (j=k) vs cross (j!=k) SMS."""
    aligned, cross = [], []
    for cell, v in sms_data.items():
        put = cell.split("_")[0].lower()
        mp = int(cell.split("MP")[1])
        (aligned if PRIMARY[put] == mp else cross).append(v["sms"])
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.boxplot([aligned, cross], labels=["aligned (j=k)", "cross (j≠k)"])
    ax.set_ylabel("SMS")
    ax.set_title(f"Aligned vs cross SMS (n_a={len(aligned)}, n_c={len(cross)})")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf")
    plt.close(fig)
