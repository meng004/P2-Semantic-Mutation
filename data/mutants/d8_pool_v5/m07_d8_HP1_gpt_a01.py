"""D8: Gaussian Process classifier - scalar x in [0,1] interface."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

np_rng = np.random.default_rng(42)
X = np_rng.uniform(-1.5, 1.5, (400, 2))
y = (X[:, 0] + X[:, 1] > 0).astype(int)

gpc = GaussianProcessClassifier(kernel=RBF(10.0, length_scale_bounds="fixed"), random_state=42)
gpc.fit(X, y)


def program(x) -> float:
    v = 1.6 * float(x) - 0.8
    return float(gpc.predict_proba([[v, v]])[0, 1])