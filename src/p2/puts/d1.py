"""D1: MLP Classifier.

Library: sklearn.neural_network.MLPClassifier (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html

Architecture: two hidden layers (32, 16), ReLU activation, Adam optimizer.
Training data (seed=42): 200 samples from 2D Gaussian mixture; label = (x1+x2 > 0).
program(x): 1D feature vector of length 2 → P(y=1) scalar.
"""
import numpy as np
from sklearn.neural_network import MLPClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.standard_normal((200, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = MLPClassifier(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=42,
)
_model.fit(_X_train, _y_train)


def program(x: np.ndarray) -> float:
    """Predict P(y=1) for 2D feature vector x."""
    x = np.asarray(x, dtype=float).ravel().reshape(1, -1)
    return float(_model.predict_proba(x)[0, 1])
