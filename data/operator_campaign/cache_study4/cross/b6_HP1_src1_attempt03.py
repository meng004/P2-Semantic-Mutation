"""B6: Inverse-transform sampling — inverse-CDF (quantile) draws (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar.
Exponential draws t = -ln(U)/λ(x), λ(x)=2.5-2x. Returns sample mean ≈ 1/λ(x),
monotone increasing in x. seed=42, n=6000.
"""
import numpy as np

_SEED = 42
_N = 30
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    samples = -np.log(_U) / lam
    return float(np.mean(samples))