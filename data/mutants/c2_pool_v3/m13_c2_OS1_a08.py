import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer
from sklearn.pipeline import make_pipeline

def _build_model():
    rng = np.random.default_rng(42)
    grid = rng.uniform(-2.0, 2.0, 80)
    grid = np.sort(grid)
    Xtr = grid.reshape((-1, 1))
    ytr = np.tanh(grid)
    pipe = make_pipeline(
        SplineTransformer(n_knots=6, degree=3),
        LinearRegression(),
    )
    return pipe.fit(Xtr, ytr)

_FITTED = _build_model()


def program(x) -> float:
    xv = float(x)
    t_query = 4.0 * xv - 2.0
    feature_row = [[t_query]]
    yhat = _FITTED.predict(feature_row)
    return float(np.asarray(yhat).ravel()[0])