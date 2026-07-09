"""D8 mutant: second feature zeroed (feature helper, chained fit)."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF


def _phi(x):
    z = 1.6 * float(x) - 0.8
    return [z, 0.0]


_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train.sum(axis=1) > 0).astype(int)

_model = GaussianProcessClassifier(
    kernel=RBF(length_scale=1.0), random_state=42
).fit(_X_train, _y_train)


def program(x) -> float:
    return float(_model.predict_proba([_phi(x)])[0, 1])