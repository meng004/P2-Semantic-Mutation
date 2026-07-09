import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_basis = SplineTransformer(n_knots=6, degree=3)
_Phi = _basis.fit_transform(_t_train)
_reg = LinearRegression().fit(_Phi, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    return float(_reg.predict(_basis.transform([[t]]))[0])