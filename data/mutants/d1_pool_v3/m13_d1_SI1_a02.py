import numpy as np
from sklearn.neural_network import MLPClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = MLPClassifier(
    hidden_layer_sizes=(32, 16), activation="relu",
    solver="adam", max_iter=500, random_state=42,
)
_model.fit(_X_train, _y_train)


def _build_features(val):
    out = []
    for i in range(2):
        if i == 1:
            out.append(0.0)
        else:
            out.append(val)
    return [out]


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba(_build_features(x))[0, 1])