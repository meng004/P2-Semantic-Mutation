import numpy as np
from sklearn.neural_network import MLPClassifier


def _build_training_data(seed: int = 42, n: int = 400):
    generator = np.random.default_rng(seed)
    samples = generator.uniform(-1.5, 1.5, (n, 2))
    labels = (np.add(samples[:, 0], samples[:, 1]) > 0).astype(int)
    return samples, labels


def _train_classifier(features, targets):
    clf = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
        alpha=1.0,
    )
    clf.fit(features, targets)
    return clf


_X_train, _y_train = _build_training_data()
_model = _train_classifier(_X_train, _y_train)


def program(x) -> float:
    val = float(x)
    point = np.array([[val, val]])
    probabilities = _model.predict_proba(point)
    return float(probabilities[0][1])