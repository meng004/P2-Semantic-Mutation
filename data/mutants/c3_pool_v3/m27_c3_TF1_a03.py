import numpy as np
from sklearn.neural_network import MLPRegressor


SEED = 42
N_TRAIN = 100
T_LOW, T_HIGH = -3.0, 3.0


def _sigmoid_2t(arr):
    arr = np.asarray(arr, dtype=float)
    return 1.0 / (1.0 + np.exp(-(arr + arr)))


def _make_training_data():
    rng = np.random.default_rng(SEED)
    raw = rng.uniform(T_LOW, T_HIGH, N_TRAIN)
    ordered = np.sort(raw)
    return ordered.reshape((N_TRAIN, 1)), _sigmoid_2t(ordered)


_X_train, _y_train = _make_training_data()

_hidden_topology = (64, 32)
_model = MLPRegressor(
    hidden_layer_sizes=_hidden_topology,
    activation="relu",
    solver="adam",
    max_iter=5,
    random_state=SEED,
)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    xf = float(x)
    t_query = 6.0 * xf - 3.0
    feature_matrix = np.array([[t_query]], dtype=float)
    yhat = _model.predict(feature_matrix)
    return float(yhat[0])