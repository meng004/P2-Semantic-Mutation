import numpy as np
from scipy.stats import jarque_bera


def is_assumption_violated(
    samples: np.ndarray, alpha: float = 0.05, autocorr_threshold: float = 0.3,
) -> bool:
    """L3: violation if lag-1 autocorrelation exceeds threshold, or Jarque-Bera rejects normality."""
    samples = np.asarray(samples)
    if len(samples) < 8:
        return False
    lag1 = np.corrcoef(samples[:-1], samples[1:])[0, 1]
    if abs(float(lag1)) > autocorr_threshold:
        return True
    _, p = jarque_bera(samples)
    return bool(p < alpha)
