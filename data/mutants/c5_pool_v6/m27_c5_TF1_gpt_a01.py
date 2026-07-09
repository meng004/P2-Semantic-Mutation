"""C5: Random-Forest regressor surrogate mutant."""
import numpy as np
from sklearn.ensemble import RandomForestRegressor

_rng = np.random.default_rng(42)
_raw = _rng.uniform(-1.0, 1.0, 300)
_t_train = np.sort(_raw).reshape(-1, 1)
_y_train = np.tanh(2.0 * _t_train.ravel())

_model = RandomForestRegressor(n_estimators=100, random_state=42)
_model.fit(_t_train, _y_train)

def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])