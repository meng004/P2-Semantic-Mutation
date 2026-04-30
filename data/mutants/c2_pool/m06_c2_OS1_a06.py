import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer

class _Surrogate:
    def __init__(self, seed=42, n_samples=80):
        rng = np.random.default_rng(seed)
        ts = np.sort(rng.uniform(-2.0, 2.0, n_samples))
        self._X = ts.reshape(-1, 1)
        self._y = np.tanh(ts)
        self._basis = SplineTransformer(n_knots=6, degree=3)
        Phi = self._basis.fit_transform(self._X)
        self._reg = LinearRegression().fit(Phi, self._y)

    def __call__(self, t_value):
        feats = self._basis.transform(np.array([[t_value]], dtype=float))
        return float(self._reg.predict(feats)[0])

_surrogate = _Surrogate()


def program(x) -> float:
    xv = float(x)
    t = 4.0 * xv - 2.0
    return _surrogate(t)