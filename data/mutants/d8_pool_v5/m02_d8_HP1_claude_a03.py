"""D8: Gaussian Process classifier - scalar x in [0,1] interface."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

def _build_model():
    rng = np.random.default_rng(42)
    Xtr = rng.uniform(-1.5, 1.5, (400, 2))
    ytr = (Xtr[:, 0] + Xtr[:, 1] > 0).astype(int)
    clf = GaussianProcessClassifier(
        kernel=RBF(length_scale=10.0, length_scale_bounds="fixed"), random_state=42)
    return clf.fit(Xtr, ytr)


_model = _build_model()


def program(x) -> float:
    x = float(x)
    z = 1.6 * x - 0.8
    return float(_model.predict_proba([[z, z]])[0, 1])