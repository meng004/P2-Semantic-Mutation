"""C3: Neural Network surrogate regressor — scalar x∈[0,1] interface.

Library: sklearn.neural_network.MLPRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x − 3 ∈ [−3, 3]. Training: sigmoid(2t) (monotone increasing).
MLP (64, 32), ReLU, Adam. Returns scalar prediction. Monotone in x.
"""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


def _make_training_data():
    rng = np.random.default_rng(42)
    t_train = rng.uniform(-3.0, 3.0, size=100)
    t_train.sort()
    y_train = _sigmoid(t_train)
    return t_train.reshape(-1, 1), y_train


def _build_model():
    params = {
        "hidden_layer_sizes": (64, 32),
        "activation": "relu",
        "solver": "adam",
        "random_state": 42,
        "max_iter": 5,
    }
    return MLPRegressor(**params)


_t_train, _y_train = _make_training_data()
_model = _build_model()
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    pred = _model.predict(np.array([[t]], dtype=float))
    return float(pred.item())