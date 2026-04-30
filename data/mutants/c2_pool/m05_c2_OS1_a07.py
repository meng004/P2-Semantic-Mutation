import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer
from sklearn.pipeline import Pipeline

_SEED = 42
_N = 80

def _draw_training_grid():
    g = np.random.default_rng(_SEED)
    points = g.uniform(-2.0, 2.0, _N)
    return np.sort(points)

_t_vals = _draw_training_grid()
_t_train = _t_vals[:, np.newaxis]
_y_train = np.tanh(_t_vals)

_steps = [
    ("basis", SplineTransformer(n_knots=6, degree=3)),
    ("linreg", LinearRegression()),
]
_pipe = Pipeline(_steps).fit(_t_train, _y_train)


def program(x) -> float:
    xf = float(x)
    t = 4.0 * xf - 2.0
    prediction = _pipe.predict(np.array([[t]], dtype=float))
    return float(prediction[0])