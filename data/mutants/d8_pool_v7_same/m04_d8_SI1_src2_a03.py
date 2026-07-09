"""D8 mutant: second feature zeroed (keyword args, ndarray query row)."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_gen = np.random.default_rng(seed=42)
_X = _gen.uniform(-1.5, 1.5, size=(400, 2))
_y = np.where(_X[:, 0] + _X[:, 1] > 0, 1, 0)

_gpc = GaussianProcessClassifier(kernel=RBF(length_scale=1.0), random_state=42)
_gpc.fit(_X, _y)


def program(x) -> float:
    x = float(x)
    f1 = 1.6 * x - 0.8
    f2 = 0.0
    return float(_gpc.predict_proba(np.array([[f1, f2]]))[0, 1])