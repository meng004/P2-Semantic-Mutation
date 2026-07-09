"""D8: Gaussian Process classifier — scalar x∈[0,1] interface.

Library: sklearn.gaussian_process.GaussianProcessClassifier (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html

program(x) where x ∈ [0,1] scalar.
Feature: [1.6x-0.8, 1.6x-0.8]. Boundary: x1+x2=0 → positive when x>0.5.
RBF-kernel Bayesian classifier; predict_proba monotone increasing over the
scaled feature band. Training: 400 pts from [-1.5,1.5]², label = (x1+x2 > 0).
"""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_train_score = _X_train[:, 0] + _X_train[:, 1]
_y_train = (_train_score < 0).astype(int)

_model = GaussianProcessClassifier(kernel=RBF(length_scale=1.0), random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[1.6 * x - 0.8, 1.6 * x - 0.8]])[0, 1])