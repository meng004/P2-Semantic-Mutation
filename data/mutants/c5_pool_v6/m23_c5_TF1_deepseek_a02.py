"""C5: Random-Forest regressor surrogate mutant."""
import numpy as np
from sklearn.ensemble import RandomForestRegressor

_rng = np.random.default_rng(42)
_bound = 1.0
_samples = _rng.uniform(-_bound, _bound, 300)
_t_train = np.sort(_samples).reshape(-1, 1)
_y_train = np.tanh(2.0 * _t_train.ravel())

_model = RandomForestRegressor(n_estimators=100, random_state=42)
_model.fit(_t_train, _y_train)

def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])