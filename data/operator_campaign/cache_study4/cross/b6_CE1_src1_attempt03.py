"""B6: Inverse-transform sampling — inverse-CDF (quantile) draws (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar.
Exponential draws t = -ln(U)/λ(x), λ(x)=2.5-x. Returns sample mean ≈ 1/λ(x),
monotone increasing in x. seed=42, n=6000.
"""
import numpy as np

_SEED = 42
_N = 6000
_RNG = np.random.default_rng(_SEED)
_U = _RNG.uniform(1e-12, 1.0, _N)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 1.0 * x
    log_u = np.log(_U)
    samples = -log_u / lam
    mean_value = np.mean(samples)
    return float(mean_value)