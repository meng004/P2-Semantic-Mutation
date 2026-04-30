"""MR functions for A1 Lorenz ODE.

Primary MP: MP4 (Trajectory DTW).
  r_mp4: tiny perturbation to x → nearby initial conditions → similar trajectory.
  R_mp4: not used by DTW verifier (DTW verifier ignores mr.R).
Trivial: r_trivial (identity), R_trivial (always True) for MP1/2/3/5.
"""
import numpy as np


def r_mp4(x) -> float:
    return float(np.clip(float(x) + 0.001, 0.0, 1.0))


def R_mp4(y_orig, y_new) -> bool:
    return True  # DTW verifier ignores R; distance checked by verifier itself


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
