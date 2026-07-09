"""D8 mutant: training label comparison > 0 flipped to < 0 (kernel hoisted to module constant)."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_KERNEL = RBF(length_scale=1.0)

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = np.where(_X_train[:, 0] + _X_train[:, 1] < 0, 1, 0)

_model = GaussianProcessClassifier(kernel=_KERNEL, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    z = 1.6 * float(x) - 0.8
    return float(_model.predict_proba([[z, z]])[0, 1])