"""D8 mutant: training label comparison > 0 flipped to < 0."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_gen = np.random.default_rng(42)
_X = _gen.uniform(-1.5, 1.5, (400, 2))
_y = (_X[:, 0] + _X[:, 1] < 0).astype(int)

_gpc = GaussianProcessClassifier(kernel=RBF(1.0), random_state=42)
_gpc.fit(_X, _y)


def program(x) -> float:
    x = float(x)
    return float(_gpc.predict_proba([[1.6 * x - 0.8, 1.6 * x - 0.8]])[0][1])