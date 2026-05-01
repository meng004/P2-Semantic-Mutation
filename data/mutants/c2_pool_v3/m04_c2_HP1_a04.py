import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline


class _PCESurrogate:
    def __init__(self, degree, n_train, t_lo, t_hi, seed):
        self.degree = degree
        rng = np.random.default_rng(seed)
        pts = rng.uniform(t_lo, t_hi, n_train)
        idx = np.argsort(pts)
        self._X = pts[idx].reshape(-1, 1)
        self._y = np.tanh(self._X.ravel())
        self._pipe = make_pipeline(
            PolynomialFeatures(self.degree, include_bias=True),
            LinearRegression(),
        )
        self._pipe.fit(self._X, self._y)

    def evaluate(self, t_value):
        arr = np.array([[t_value]])
        return float(self._pipe.predict(arr)[0])


_PCE = _PCESurrogate(degree=1, n_train=80, t_lo=-2.0, t_hi=2.0, seed=42)


def program(x) -> float:
    xv = float(x)
    t = 4.0 * xv - 2.0
    return _PCE.evaluate(t)