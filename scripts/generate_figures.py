"""Generate publication-quality figures for the IST submission.

Three figures, all PNG @ 300 DPI, written to ``figs/`` under project root:

  1. ``fig1_three_layer_methodology.png`` -- conceptual diagram of the
     three-layer methodology backbone (Definitional / Operational /
     Applied) with the five meta-mutation operator classes and the
     refutation evidence linkage.

  2. ``fig2_60cell_heatmap.png`` -- 12-PUT x 5-MP SMS heatmap from
     ``data/results/sms_track2_v4.json``; aligned (j == k) cells get a
     thick border.

  3. ``fig3_ast_overlap_per_class.png`` -- per-operator-class AST
     overlap rate from
     ``data/results/cosmic_ray_12put_ast_diff.json``
     (``aggregated.per_class_aggregated``).

Run from project root:

    PYTHONPATH=src .venv/bin/python scripts/generate_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "figs"
DATA_DIR = ROOT / "data" / "results"

# Pre-registered v3 primary MP per PUT (see src/p2/config/primary.py).
PRIMARY_MP = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}
PUTS = ["a1", "a2", "a3", "b1", "b2", "b3",
        "c1", "c2", "c3", "d1", "d2", "d3"]
MPS = [1, 2, 3, 4, 5]
MP_LABELS = ["MP1\ncons.", "MP2\nmono.", "MP3\nconv.", "MP4\ntraj.", "MP5\np-ord."]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


# ---------------------------------------------------------------------------
# Figure 1: three-layer methodology backbone
# ---------------------------------------------------------------------------
def figure1(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Color palette (muted, journal-friendly).
    layer_colors = {
        "L1": "#E8F1FA",  # pale blue
        "L2": "#FFF4E6",  # pale orange
        "L3": "#EAF7EA",  # pale green
    }
    edge_colors = {
        "L1": "#3B6FA0",
        "L2": "#C97A2C",
        "L3": "#3F8A4F",
    }

    def add_box(x, y, w, h, key, title, body):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.18",
            linewidth=1.6,
            edgecolor=edge_colors[key],
            facecolor=layer_colors[key],
            zorder=2,
        )
        ax.add_patch(box)
        ax.text(
            x + 0.20, y + h - 0.32, title,
            fontsize=11.5, fontweight="bold",
            color=edge_colors[key], zorder=3,
        )
        ax.text(
            x + 0.20, y + h - 0.78, body,
            fontsize=9.2, color="#222222", zorder=3,
            verticalalignment="top",
        )
        return box

    # Layer 1: Definitional (top)
    add_box(
        0.4, 5.7, 9.2, 1.95,
        "L1",
        "Layer 1 -- Definitional ($\\S$3.2.0)",
        ("Necessary conditions for a domain-semantic mutation:\n"
         "  (a) cross-function-boundary substitution    "
         "(b) domain knowledge required    "
         "(c) algorithmic-class change\n"
         r"$\Rightarrow$ five meta-mutation operator classes:  "
         "CE  /  OS  /  HP  /  TF  /  SI"),
    )

    # Layer 2: Operational (middle)
    add_box(
        0.4, 3.2, 9.2, 1.95,
        "L2",
        "Layer 2 -- Operational ($\\S$2.3, $\\S$4.4)",
        ("Equivalence judgement under E1 $\\wedge$ E2 (semantic E1 + output E2)\n"
         "Two-stage screening + dual-blind review + AVP meta-pattern oracle\n"
         r"$\Rightarrow$ conservative, complete instantiation of L1 conditions"),
    )

    # Layer 3: Applied (bottom)
    add_box(
        0.4, 0.7, 9.2, 1.95,
        "L3",
        "Layer 3 -- Applied ($\\S$3.5)",
        ("12-PUT cosmic-ray AST traceability  (292 P2 vs 1,250 syntactic mutants)\n"
         "Overall AST overlap = 5.14%   (15 / 292)\n"
         "HP / SI / TF categorically unreachable for syntactic mutants:  0 / 0 / 0"),
    )

    # Arrow Layer 1 -> Layer 2 (operationalisation)
    arr12 = FancyArrowPatch(
        (3.0, 5.65), (3.0, 5.20),
        arrowstyle="-|>", mutation_scale=18,
        linewidth=1.8, color="#444444", zorder=4,
    )
    ax.add_patch(arr12)
    ax.text(
        3.15, 5.42, "operationalisation",
        fontsize=9, color="#444444", zorder=5,
    )

    # Arrow Layer 1 -> Layer 3 (refutation evidence, vertical, OUTSIDE box right edge)
    arr13 = FancyArrowPatch(
        (9.85, 6.675), (9.85, 1.675),
        arrowstyle="-|>", mutation_scale=18,
        linewidth=1.8, color="#A04040", zorder=4,
        linestyle=(0, (4, 2)),
    )
    ax.add_patch(arr13)
    ax.text(
        10.05, 4.175, "refutation\nevidence",
        fontsize=9, color="#A04040", zorder=5,
        ha="left", va="center",
    )

    ax.set_title(
        "Three-layer methodology backbone: from definitional necessary\n"
        "conditions to operational judgement to applied refutation",
        fontsize=12, pad=10,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2: 60-cell SMS heatmap
# ---------------------------------------------------------------------------
def figure2(out_path: Path) -> None:
    sms = json.loads((DATA_DIR / "sms_track2_v4.json").read_text())

    matrix = np.zeros((len(PUTS), len(MPS)))
    for i, put in enumerate(PUTS):
        for j, mp in enumerate(MPS):
            cell = f"{put.upper()}_MP{mp}"
            matrix[i, j] = sms.get(cell, {}).get("sms", 0.0)

    # RdYlGn reversed so 0=red, 1=green
    cmap = plt.get_cmap("RdYlGn")

    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    im = ax.imshow(
        matrix, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto",
    )

    # Cell annotations
    for i in range(len(PUTS)):
        for j in range(len(MPS)):
            v = matrix[i, j]
            # text colour: dark for mid-band, white for very low (red end)
            text_color = "white" if v < 0.25 else "#0a0a0a"
            ax.text(
                j, i, f"{v:.2f}",
                ha="center", va="center",
                fontsize=9, color=text_color,
            )

    # Thick borders on aligned cells (j == primary_mp - 1).
    for i, put in enumerate(PUTS):
        prim = PRIMARY_MP[put]
        j = prim - 1
        ax.add_patch(
            mpatches.Rectangle(
                (j - 0.5, i - 0.5), 1, 1,
                fill=False, edgecolor="#1a1a1a",
                linewidth=2.6, zorder=4,
            )
        )

    ax.set_xticks(range(len(MPS)))
    ax.set_xticklabels(MP_LABELS, fontsize=9.5)
    ax.set_yticks(range(len(PUTS)))
    ax.set_yticklabels([p.upper() for p in PUTS], fontsize=9.5)
    ax.set_xlabel("Metamorphic relation (MP)")
    ax.set_ylabel("Program-under-test (PUT)")
    ax.set_title(
        "60-cell SMS heatmap (12 PUTs $\\times$ 5 MPs, v4 cross-source pool)\n"
        "thick border = aligned cell ($j = k$, primary MP per PUT)",
        fontsize=12, pad=8,
    )

    # Class boundaries (between a/b, b/c, c/d) for readability
    for sep in (2.5, 5.5, 8.5):
        ax.axhline(sep, color="#777777", linewidth=0.8, alpha=0.55)

    cbar = fig.colorbar(im, ax=ax, fraction=0.038, pad=0.025)
    cbar.set_label("SMS = killed / (instantiated $-$ equivalent)")
    cbar.ax.tick_params(labelsize=9)

    # Make sure top/right spines are off (already in rcParams) but
    # the imshow rebuilds spines; force them off.
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3: per-operator-class AST overlap rate
# ---------------------------------------------------------------------------
def figure3(out_path: Path) -> None:
    blob = json.loads((DATA_DIR / "cosmic_ray_12put_ast_diff.json").read_text())
    per_class = blob["aggregated"]["per_class_aggregated"]

    # Sort ascending by overlap rate; ties broken by class name.
    items = sorted(per_class.items(), key=lambda kv: (kv[1]["rate"], kv[0]))
    classes = [k for k, _ in items]
    rates = [v["rate"] for _, v in items]
    n_overlap = [v["n_overlap"] for _, v in items]
    n_p2 = [v["n_p2"] for _, v in items]

    # Color scheme: HP / SI / TF (categorically unreachable) -> green;
    # CE / OS / CF -> orange.
    green = "#3F8A4F"
    orange = "#D08A2C"
    unreachable = {"HP", "SI", "TF"}
    colors = [green if c in unreachable else orange for c in classes]

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    x = np.arange(len(classes))
    bars = ax.bar(
        x, rates,
        color=colors, edgecolor="#222222", linewidth=1.0, width=0.62,
    )

    # Annotate above each bar with n_overlap/n_p2 = rate
    for i, bar in enumerate(bars):
        y = bar.get_height()
        label = f"{n_overlap[i]}/{n_p2[i]} = {rates[i]:.3f}"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y + 0.04,
            label, ha="center", va="bottom",
            fontsize=9.5, color="#1a1a1a",
        )

    # Reference line at 1.0 (rejected hypothesis)
    ax.axhline(
        1.0, color="#A04040", linestyle="--", linewidth=1.4,
    )
    ax.text(
        len(classes) - 0.55, 1.02,
        "syntactic-mutant subset hypothesis (rejected)",
        color="#A04040", fontsize=9.5,
        ha="right", va="bottom",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=11)
    ax.set_xlabel("Meta-mutation operator class")
    ax.set_ylabel("AST overlap rate  (P2 mutants intersect cosmic-ray)")
    ax.set_ylim(0.0, 1.20)
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

    ax.set_title(
        "Per-class AST overlap with cosmic-ray (syntactic) mutants  "
        "($n_{P2}=292$, $n_{CR}=1{,}250$)\n"
        "HP / SI / TF categorically unreachable by syntactic mutants  (0 / 0 / 0)",
        fontsize=11.5, pad=8,
    )

    # Legend
    legend_handles = [
        mpatches.Patch(facecolor=green, edgecolor="#222222",
                       label="categorically unreachable (rate = 0)"),
        mpatches.Patch(facecolor=orange, edgecolor="#222222",
                       label="partially overlapping with syntactic"),
    ]
    ax.legend(
        handles=legend_handles, loc="upper left",
        frameon=False, fontsize=9.5,
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def _kb(path: Path) -> float:
    return path.stat().st_size / 1024.0


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    targets = [
        ("fig1_three_layer_methodology.png", figure1,
         "Conceptual three-layer methodology backbone "
         "(Definitional / Operational / Applied)."),
        ("fig2_60cell_heatmap.png", figure2,
         "12-PUT x 5-MP SMS heatmap (v4 cross-source); aligned cells boxed."),
        ("fig3_ast_overlap_per_class.png", figure3,
         "Per-class AST overlap rate vs cosmic-ray syntactic mutants."),
    ]
    print("[generate_figures] writing into", FIG_DIR)
    for name, fn, descr in targets:
        path = FIG_DIR / name
        fn(path)
        print(f"  + {name}  ({_kb(path):.1f} KB)  -- {descr}")
    print("[generate_figures] done; 3/3 figures generated.")


if __name__ == "__main__":
    main()
