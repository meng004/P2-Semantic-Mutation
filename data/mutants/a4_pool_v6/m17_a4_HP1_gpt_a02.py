import numpy as np
import numpy.polynomial.legendre as _leg

_NODES, _WEIGHTS = _leg.leggauss(1)


def program(x) -> float:
    x = float(x)
    integrand = x + 0.5 * _NODES**2
    return float(np.sum(_WEIGHTS * integrand))