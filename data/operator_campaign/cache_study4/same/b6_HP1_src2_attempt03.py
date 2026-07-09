import numpy as np

_SAMPLE_COUNT = 30


def _uniforms():
    return np.random.default_rng(42).uniform(1e-12, 1.0, _SAMPLE_COUNT)


_U = _uniforms()


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    return float(np.mean(-np.log(_U) / lam))