import numpy as np
from fastdtw import fastdtw
from typing import Callable
from p2.avp.interface import AVPResult, MR


def verify_trajectory_dtw(
    program: Callable, mr: MR, epsilon_dtw: float, n_samples: int = 10,
) -> AVPResult:
    """MP_4 verification: DTW distance between original and transformed trajectories."""
    rng = np.random.default_rng(seed=42)
    distances = []
    for _ in range(n_samples):
        x = rng.uniform(0, 1)
        y_orig = np.asarray(program(x)).reshape(-1, 1)
        y_new = np.asarray(program(mr.r(x))).reshape(-1, 1)
        dist, _ = fastdtw(y_orig, y_new)
        distances.append(dist / max(len(y_orig), len(y_new)))
    avg = float(np.mean(distances))
    return AVPResult.PASS if avg <= epsilon_dtw else AVPResult.FAIL
