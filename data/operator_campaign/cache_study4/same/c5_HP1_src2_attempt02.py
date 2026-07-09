"""C5: Random-Forest regressor surrogate, scalar x in [0,1] interface.

Library: sklearn.ensemble.RandomForestRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html

program(x) where x in [0,1] scalar.
x -> test point t = 6x-3 in [-3,3]. Training: tanh(2t) (monotone increasing).
100-tree ensemble surrogate (seed 42). Returns scalar prediction, monotone in x.
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.tanh(2.0 * _t_train.ravel())

_model = RandomForestRegressor(random_state=42)
_model.set_params(n_estimators=1)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])