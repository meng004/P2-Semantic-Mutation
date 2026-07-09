import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer

_N_KNOTS = 6
_DEGREE = 3
_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_steps = [("basis", SplineTransformer(n_knots=_N_KNOTS, degree=_DEGREE)),
          ("reg", LinearRegression())]
_model = Pipeline(_steps)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    return float(_model.predict([[t]])[0])