import numpy as np
from sklearn.neural_network import MLPClassifier
import operator

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_sum_features = np.add(_X_train[:, 0], _X_train[:, 1])
_original_labels = np.greater(_sum_features, 0).astype(int)
_y_train = np.fromiter((operator.sub(1, v) for v in _original_labels), dtype=int, count=_original_labels.shape[0])

_classifier_kwargs = dict(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=42,
)
_model = MLPClassifier(**_classifier_kwargs)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x, x]])[0, 1])