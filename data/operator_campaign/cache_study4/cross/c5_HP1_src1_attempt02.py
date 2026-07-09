import numpy as np
from sklearn.ensemble import RandomForestRegressor


def _make_training_data():
    rng = np.random.default_rng(42)
    t = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    y = np.tanh(2.0 * t.ravel())
    return t, y


_t_train, _y_train = _make_training_data()
_model = RandomForestRegressor(random_state=42, n_estimators=1)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    prediction = _model.predict([[t]])[0]
    return float(prediction)