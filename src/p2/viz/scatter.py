"""SMS vs (C1_share or PC) scatter plots (Figures 4, 5)."""
from pathlib import Path

import matplotlib.pyplot as plt
from scipy.stats import spearmanr


def render_scatter(x_data: list, y_data: list,
                   x_label: str, y_label: str,
                   title: str, out_path: Path) -> None:
    """Generic scatter with Spearman rho overlay."""
    rho, p = spearmanr(x_data, y_data)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(x_data, y_data, s=40, alpha=0.7)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(f"{title}\nSpearman ρ = {rho:.3f}, p = {p:.3g}")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf")
    plt.close(fig)
