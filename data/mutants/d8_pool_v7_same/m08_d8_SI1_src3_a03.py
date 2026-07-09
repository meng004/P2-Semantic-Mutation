"""Mutated D8 Gaussian Process classifier: second feature zeroed (lazy-style builder)."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF


def _build_classifier():
    rng = np.random.default_rng(42)
    X = rng.uniform(-1.5, 1.5, (400, 2))
    y = np.where(X[:, 0] + X[:, 1] > 0, 1, 0)
    return GaussianProcessClassifier(kernel=RBF(1.0), random_state=42).fit(X, y)


_CLF = _build_classifier()


def program(x) -> float:
    x = float(x)
    z = 1.6 * x - 0.8
    return float(_CLF.predict_proba([[z, 0.0]])[:, 1][0])