"""Per-class forest plot of mean SMS (Figure 3)."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def render_class_forest(sms_data: dict, out_path: Path) -> None:
    """Per-class mean SMS +/- SEM forest plot (RQ3)."""
    classes = {"a": [], "b": [], "c": [], "d": []}
    for cell, v in sms_data.items():
        cls = cell[0].lower()
        if cls in classes:
            classes[cls].append(v["sms"])
    means = {c: float(np.mean(vs)) if vs else 0.0 for c, vs in classes.items()}
    sems = {c: (float(np.std(vs, ddof=1) / np.sqrt(len(vs))) if len(vs) > 1 else 0.0)
            for c, vs in classes.items()}
    fig, ax = plt.subplots(figsize=(5, 4))
    y = np.arange(len(means))
    ax.errorbar([means[c] for c in "abcd"], y,
                xerr=[sems[c] for c in "abcd"], fmt="o", capsize=4)
    ax.set_yticks(y)
    ax.set_yticklabels(["a numeric", "b probabilistic", "c surrogate", "d ML"])
    ax.set_xlabel("Mean SMS ± SEM")
    ax.axvline(0.0, color="gray", linestyle="--", linewidth=0.5)
    ax.set_title("Cross-class SMS (RQ3)")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf")
    plt.close(fig)
