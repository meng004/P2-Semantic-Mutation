import numpy as np
from sklearn.neural_network import MLPClassifier


def _prepare():
    generator = np.random.default_rng(42)
    samples = generator.uniform(-1.5, 1.5, (400, 2))
    sums = np.add(samples[:, 0], samples[:, 1])
    tags = (sums > 0) * 1
    return samples, tags.astype(int)


_X_data, _y_data = _prepare()


def _build_classifier():
    settings = {}
    for key, value in [
        ("hidden_layer_sizes", (32, 16)),
        ("activation", "relu"),
        ("solver", "adam"),
        ("max_iter", 500),
        ("random_state", 42),
        ("alpha", 1.0),
    ]:
        settings[key] = value
    return MLPClassifier(**settings)


_net = _build_classifier()
_net.fit(_X_data, _y_data)


def program(x) -> float:
    z = float(x)
    pair = [[z, z]]
    result = _net.predict_proba(pair)
    return float(result[0, 1])