import pytest
import numpy as np
from p2.avp.interface import AVPResult, MR

fastdtw = pytest.importorskip("fastdtw", reason="fastdtw not installed")
from p2.avp.mp4_dtw import verify_trajectory_dtw


def test_close_trajectory_passes():
    def smooth_traj(x):
        t = np.linspace(0, 1, 100)
        return np.sin(2 * np.pi * t)  # x-independent trajectory

    mr = MR(r=lambda x: x * 1.1, R=lambda a, b: True, mp_index=4, name="sine")
    result = verify_trajectory_dtw(smooth_traj, mr, epsilon_dtw=0.1, n_samples=10)
    assert result == AVPResult.PASS


def test_distorted_trajectory_fails():
    def chaotic(x):
        t = np.linspace(0, 1, 100)
        rng = np.random.default_rng(int(x * 10000))
        return rng.normal(0, 5, size=100)  # completely different per x

    mr = MR(r=lambda x: x * 1.1, R=lambda a, b: True, mp_index=4, name="chaotic")
    result = verify_trajectory_dtw(chaotic, mr, epsilon_dtw=0.1, n_samples=10)
    assert result == AVPResult.FAIL
