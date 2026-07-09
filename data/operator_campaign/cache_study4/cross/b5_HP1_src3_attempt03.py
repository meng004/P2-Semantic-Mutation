"""B5: Rejection sampling — acceptance-rejection Monte-Carlo (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar (target mean).
Samples a truncated Gaussian on [-3,3] with mean μ=4x-2 by rejection
(uniform proposals, accept ∝ exp(-½(t-μ)²)). Returns accepted-sample mean.
Monotone increasing in x. seed=42, 50 proposals.
"""
import numpy as np

_SEED = 42
_N_PROP = 50
_LO, _HI = -3.0, 3.0


def program(x):
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    accept = us < np.exp(-0.5 * (props - mu) ** 2)
    return float(np.mean(props[accept]))