"""D8 mutant: training label comparison > 0 flipped to < 0 (training encapsulated in a builder)."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF


def _fit_model():
    gen = np.random.default_rng(42)
    X = gen.uniform(-1.5, 1.5, (400, 2))
    y = (X[:, 0] + X[:, 1] < 0).astype(int)
    clf = GaussianProcessClassifier(kernel=RBF(length_scale=1.0), random_state=42)
    clf.fit(X, y)
    return clf


_gpc = _fit_model()


def program(x) -> float:
    z = 1.6 * float(x) - 0.8
    row = np.array([[z, z]])
    return float(_gpc.predict_proba(row)[0, 1])