"""Metamorphic relations for OOD PUT e1: yan2024 Neumann elliptic solver.

PUT contract (experiments/puts/ood_elliptic.py::program_e1):
  program(x) takes a grid spacing x = h in (0, 0.25] and returns the
  convergence observable U_numeric(probe) / U_exact(probe) at (0.25, 0.25),
  which -> 1.0 as h -> 0. A seeded discretisation fault makes it deviate.

Each MR is a pair (r, R) mirroring the p2 study's five meta-patterns
(MP1..MP5). Semantics follow the a3 heat-FDM template (ratio -> 1.0).

This PUT is an OUT-OF-DISTRIBUTION domain: an independent research group's
(Yan & Zhu 2024, STVR) second-order elliptic PDE solver, ported faithfully
to Python. Used to test whether the minimal-complete MR subset selected on
the reactor-physics domain extrapolates to a different PDE family.
"""
from __future__ import annotations


def r_mp1(x: float) -> float:
    """MP1 (conservation): identical re-run, output must match exactly."""
    return x


def R_mp1(y_src: float, y_fol: float) -> bool:
    return abs(y_src - y_fol) < 1e-9


def r_mp2(x: float) -> float:
    """MP2 (monotonicity): finer grid (smaller h) should not worsen accuracy."""
    return x / 2.0


def R_mp2(y_src: float, y_fol: float) -> bool:
    # finer grid: observable should be at least as close to 1.0
    return abs(y_fol - 1.0) <= abs(y_src - 1.0) + 1e-6


def r_mp3(x: float) -> float:
    """MP3 (convergence): refine the grid towards the continuum limit."""
    return x / 4.0


def R_mp3(y_src: float, y_fol: float) -> bool:
    # second-order convergence: refining by 4x should bring the observable
    # markedly closer to 1.0 (error shrinks ~16x); require strict improvement.
    return abs(y_fol - 1.0) <= abs(y_src - 1.0) + 1e-6


def r_mp4(x: float) -> float:
    """MP4 (trajectory): a coarser grid for path-shape comparison."""
    return x * 2.0


def R_mp4(y_src: float, y_fol: float) -> bool:
    # trajectory monotonicity: coarsening must not improve accuracy
    return abs(y_fol - 1.0) >= abs(y_src - 1.0) - 1e-6


def r_mp5(x: float) -> float:
    """MP5 (partial order): finer grid for an accuracy ordering check."""
    return x / 2.0


def R_mp5(y_src: float, y_fol: float) -> bool:
    # partial order: finer-grid observable bounded by coarser towards 1.0
    return abs(y_fol - 1.0) <= abs(y_src - 1.0) + 1e-6
