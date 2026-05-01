import numpy as np
from sklearn.neural_network import MLPRegressor


def _sig2(arr):
    arr = np.asarray(arr, dtype=float)
    denom = 1.0 + np.exp(-(arr + arr))
    return 1.0 / denom


def _prepare():
    gen = np.random.default_rng(42)
    pts = gen.uniform(-3.0, 3.0, 100)
    pts = np.sort(pts)
    feature_matrix = np.reshape(pts, (-1, 1))
    label_vector = _sig2(pts)
    return feature_matrix, label_vector


_features, _labels = _prepare()

_settings = {"random_state": 42}
_settings["hidden_layer_sizes"] = (64, 32)
_settings["activation"] = "relu"
_settings["solver"] = "adam"
_settings["max_iter"] = 5

_estimator = MLPRegressor(**_settings)
_estimator.fit(_features, _labels)


def program(x) -> float:
    val = float(x)
    mapped_t = 6.0 * val - 3.0
    sample = np.array([[mapped_t]], dtype=float)
    yhat = _estimator.predict(sample)
    return float(yhat[0])