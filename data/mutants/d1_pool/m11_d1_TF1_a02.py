import numpy as np
from sklearn.neural_network import MLPClassifier

def _build_labels(features):
    flipped = np.empty(features.shape[0], dtype=int)
    for idx in range(features.shape[0]):
        original = 1 if (features[idx, 0] + features[idx, 1]) > 0 else 0
        flipped[idx] = 1 - original
    return flipped

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = _build_labels(_X_train)

_model = MLPClassifier(
    hidden_layer_sizes=(32, 16), activation="relu",
    solver="adam", max_iter=500, random_state=42,
)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x, x]])[0, 1])