"""C3: Neural Network surrogate regressor — scalar x∈[0,1] interface.

Library: sklearn.neural_network.MLPRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x − 3 ∈ [−3, 3]. Training: sigmoid(2t) (monotone increasing).
MLP (64, 2), ReLU, Adam. Returns scalar prediction. Monotone in x.
"""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_rng = np.random.default_rng(42)
_t_train = _rng.uniform(-3.0, 3.0, size=(100, 1))
_t_train.sort(axis=0)
_y_train = _sigmoid(np.squeeze(_t_train, axis=1))

_hidden_width = 2
_model = MLPRegressor(
    hidden_layer_sizes=(64, _hidden_width),
    activation="relu",
    solver="adam",
    max_iter=1000,
    random_state=42,
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    pred = _model.predict(np.array([[t]], dtype=float))
    return float(pred.item())