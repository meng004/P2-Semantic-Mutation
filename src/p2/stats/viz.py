import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PUT_LABELS = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3"]
MP_LABELS = ["MP1", "MP2", "MP3", "MP4", "MP5"]


def plot_sms_heatmap(sms_grid: np.ndarray, out_path: Path) -> None:
    """sms_grid shape (12 PUT, 5 MP, 5 mut) → flattened to 12×25 heatmap."""
    flat = sms_grid.reshape(sms_grid.shape[0], -1)
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(flat, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_yticks(range(len(PUT_LABELS)))
    ax.set_yticklabels(PUT_LABELS)
    ax.set_xticks(range(flat.shape[1]))
    col_labels = [f"{mp}/mut{j}" for mp in MP_LABELS for j in range(1, 6)]
    ax.set_xticklabels(col_labels, rotation=90, fontsize=7)
    fig.colorbar(im, label="SMS")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
