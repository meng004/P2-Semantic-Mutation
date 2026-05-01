import numpy as np
from sklearn.neural_network import MLPClassifier


def _build_dataset():
    generator = np.random.default_rng(42)
    points = generator.uniform(-1.5, 1.5, size=(400, 2))
    targets = (points[:, 0] + points[:, 1] > 0).astype(int)
    return points, targets


def _train_classifier(X, y):
    clf = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
        alpha=1.0,
    )
    clf.fit(X, y)
    return clf


_X_train, _y_train = _build_dataset()
_model = _train_classifier(_X_train, _y_train)


def program(x) -> float:
    xv = float(x)
    feat = [[xv, xv]]
    probs = _model.predict_proba(feat)
    return float(probs[0][1])