"""60-cell SMS heatmap (rows=PUT, cols=MP)."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

PUTS = ["a1", "a2", "a3", "b1", "b2", "b3",
        "c1", "c2", "c3", "d1", "d2", "d3"]
MPS = [1, 2, 3, 4, 5]
PRIMARY = {"a1": 1, "a2": 1, "a3": 1, "b1": 2, "b2": 2, "b3": 2,
           "c1": 5, "c2": 5, "c3": 5, "d1": 2, "d2": 2, "d3": 2}


def render_60cell_heatmap(sms_data: dict, out_path: Path) -> None:
    """Render 60-cell SMS heatmap. sms_data: {f'{PUT}_MP{k}': {'sms': float}, ...}."""
    matrix = np.zeros((len(PUTS), len(MPS)))
    annot = np.empty((len(PUTS), len(MPS)), dtype=object)
    for i, put in enumerate(PUTS):
        for j, mp in enumerate(MPS):
            cell = f"{put.upper()}_MP{mp}"
            sms = sms_data.get(cell, {}).get("sms", 0.0)
            matrix[i, j] = sms
            mark = "★" if PRIMARY[put] == mp else ""
            annot[i, j] = f"{sms:.2f}{mark}"
    fig, ax = plt.subplots(figsize=(7, 9))
    sns.heatmap(matrix, annot=annot, fmt="", cmap="YlOrRd",
                xticklabels=[f"MP{k}" for k in MPS],
                yticklabels=[p.upper() for p in PUTS],
                vmin=0.0, vmax=1.0, ax=ax,
                cbar_kws={"label": "SMS"})
    ax.set_title("60-cell SMS heatmap (★ = j=k aligned)")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf")
    plt.close(fig)
