"""Python-side reference for XL program 'fft' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

import numpy as np

_K = np.arange(64, dtype=float)


def program(x) -> float:
    w = 3.0 + 9.0 * float(x)
    s = np.exp(-(((_K - 32.0) / w) ** 2))
    S = np.fft.fft(s)
    return float(abs(S[4]) ** 2)
