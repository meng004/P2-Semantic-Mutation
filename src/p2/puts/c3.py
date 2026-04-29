"""C3: Neural Network (MLP) surrogate regressor.

Library: sklearn.neural_network.MLPRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html

Architecture: two hidden layers (64, 32), ReLU activation, Adam optimizer.
Training data (seed=42): 80 points from f(t) = sin(t)·exp(−0.1t²), t ∈ [−4,4].
program(x): scalar or 1D array of test points → predicted values.
"""
import numpy as np
from sklearn.neural_network import MLPRegressor

_rng = np.random.default_rng(42)
_X_train = np.sort(_rng.uniform(-4.0, 4.0, 80)).reshape(-1, 1)
_t = _X_train.ravel()
_y_train = np.sin(_t) * np.exp(-0.1 * _t**2)

_model = MLPRegressor(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=42,
)
_model.fit(_X_train, _y_train)


def program(x: np.ndarray) -> np.ndarray:
    """Predict MLP surrogate at test points x; returns array."""
    x = np.asarray(x, dtype=float).ravel().reshape(-1, 1)
    return _model.predict(x)
