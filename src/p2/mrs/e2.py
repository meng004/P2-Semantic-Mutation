"""Metamorphic relations for OOD PUT e2: yan2024 Dirichlet five-point solver.

PUT contract (experiments/puts/ood_elliptic.py::program_e2):
  program(x) takes a grid parameter x (mapped to N = round(x) in [4, 48]) and
  returns the Cauchy self-convergence ratio U_N(probe)/U_2N(probe) at the fixed
  physical probe (0.5, 0.5), which -> 1.0 as N -> inf.

Why a self-convergence ratio (not error-vs-analytic): yan2024's published
Dirichlet program ships a degenerate analytic reference (a ``/2*0`` in its
source collapses the true solution to sin(pi*y), which the convection-laden
operator does not approach). The discrete scheme is nonetheless consistent and
self-converges, so the self-convergence ratio is a faithful, fault-sensitive
observable. A seeded discretisation fault breaks Cauchy convergence and drives
the ratio away from 1.0.

Each MR is a pair (r, R) mirroring the p2 study's five meta-patterns
(MP1..MP5), with the same ratio->1.0 semantics as PUT e1 (Neumann). This is an
OUT-OF-DISTRIBUTION domain (Yan & Zhu 2024, STVR), Dirichlet boundary variant.
"""
from __future__ import annotations


def r_mp1(x: float) -> float:
    """MP1 (conservation): identical re-run, output must match exactly."""
    return x


def R_mp1(y_src: float, y_fol: float) -> bool:
    return abs(y_src - y_fol) < 1e-9


def r_mp2(x: float) -> float:
    """MP2 (monotonicity): finer grid (larger N) should not worsen convergence."""
    return x * 2.0


def R_mp2(y_src: float, y_fol: float) -> bool:
    # finer grid: self-convergence ratio at least as close to 1.0
    return abs(y_fol - 1.0) <= abs(y_src - 1.0) + 1e-6


def r_mp3(x: float) -> float:
    """MP3 (convergence): refine the grid towards the continuum limit."""
    return x * 4.0


def R_mp3(y_src: float, y_fol: float) -> bool:
    # second-order convergence: a 4x finer grid brings the ratio closer to 1.0
    return abs(y_fol - 1.0) <= abs(y_src - 1.0) + 1e-6


def r_mp4(x: float) -> float:
    """MP4 (trajectory): a coarser grid for path-shape comparison."""
    return x / 2.0


def R_mp4(y_src: float, y_fol: float) -> bool:
    # trajectory: coarsening must not improve the self-convergence ratio
    return abs(y_fol - 1.0) >= abs(y_src - 1.0) - 1e-6


def r_mp5(x: float) -> float:
    """MP5 (partial order): finer grid for an accuracy ordering check."""
    return x * 2.0


def R_mp5(y_src: float, y_fol: float) -> bool:
    # partial order: finer-grid ratio bounded by coarser towards 1.0
    return abs(y_fol - 1.0) <= abs(y_src - 1.0) + 1e-6
