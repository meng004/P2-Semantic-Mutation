import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_rng = np.random.default_rng(42)
_Xtr = _rng.uniform(-1.5, 1.5, (400, 2))
_ytr = (_Xtr[:, 0] + _Xtr[:, 1] > 0).astype(int)

_smooth_kernel = RBF(length_scale=10.0, length_scale_bounds="fixed")
_model = GaussianProcessClassifier(random_state=42, kernel=_smooth_kernel)
_model.fit(_Xtr, _ytr)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[1.6 * x - 0.8, 1.6 * x - 0.8]])[0, 1])