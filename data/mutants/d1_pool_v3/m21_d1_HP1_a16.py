import numpy as np
from sklearn.neural_network import MLPClassifier


def _generate_dataset(seed=42, count=400, span=1.5):
    gen = np.random.default_rng(seed)
    xs = gen.uniform(-span, span, count)
    ys = gen.uniform(-span, span, count)
    coords = np.column_stack((xs, ys))
    decision = np.greater(xs + ys, 0)
    return coords, decision.astype(int)


class _BoundaryLearner:
    def __init__(self):
        self.model = MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            solver="adam",
            max_iter=500,
            random_state=42,
            alpha=1.0,
        )

    def train(self, X, y):
        self.model.fit(X, y)
        return self

    def positive_prob(self, vec):
        return float(self.model.predict_proba(vec)[0, 1])


_features, _labels = _generate_dataset()
_learner = _BoundaryLearner().train(_features, _labels)


def program(x) -> float:
    value = float(x)
    query = np.stack([[value, value]])
    return _learner.positive_prob(query)