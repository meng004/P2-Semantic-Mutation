import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures


def _build_pce_model(degree):
    rng = np.random.default_rng(42)
    raw = rng.uniform(-2.0, 2.0, 80)
    t_grid = np.sort(raw).reshape(-1, 1)
    targets = np.tanh(t_grid.ravel())
    pipe = make_pipeline(
        PolynomialFeatures(degree, include_bias=True),
        LinearRegression(),
    )
    pipe.fit(t_grid, targets)
    return pipe


_DEGREE = 1
_model = _build_pce_model(_DEGREE)


def program(x) -> float:
    xv = float(x)
    t_point = 4.0 * xv - 2.0
    pred = _model.predict(np.asarray([[t_point]]))
    return float(pred[0])