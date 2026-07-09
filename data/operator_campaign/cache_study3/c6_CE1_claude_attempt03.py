"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

rng = np.random.default_rng(42)
xs = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
ys = erf(xs.ravel())
model = RBFInterpolator(xs, ys, kernel="thin_plate_spline")


def program(x) -> float:
    x = float(x)
    t = x * 6.0 - 2.0
    query = [[t]]
    return float(model(query).item())