import numpy as np
from scipy.stats import spearmanr, kendalltau


def spearman_kendall(sms: np.ndarray, coverage: np.ndarray) -> tuple[float, float]:
    rho, _ = spearmanr(sms, coverage)
    tau, _ = kendalltau(sms, coverage)
    return float(rho), float(tau)
