import numpy as np
from sklearn.neural_network import MLPClassifier


class _DataBuilder:
    def __init__(self, seed, count, low, high):
        self.seed = seed
        self.count = count
        self.low = low
        self.high = high

    def build(self):
        engine = np.random.default_rng(self.seed)
        matrix = engine.uniform(self.low, self.high, size=(self.count, 2))
        targets = np.zeros(self.count, dtype=int)
        idx = 0
        while idx < self.count:
            if (matrix[idx, 0] + matrix[idx, 1]) > 0:
                targets[idx] = 1
            idx += 1
        return matrix, targets


_builder = _DataBuilder(seed=42, count=400, low=-1.5, high=1.5)
_X_set, _y_set = _builder.build()

_config = {}
_config.update({"hidden_layer_sizes": (32, 16)})
_config.update({"activation": "relu"})
_config.update({"solver": "adam"})
_config.update({"max_iter": 500})
_config.update({"random_state": 42})
_config.update({"alpha": 1.0})

_network = MLPClassifier(**_config)
_network.fit(_X_set, _y_set)


def program(x) -> float:
    scalar_input = float(x)
    feature_vector = np.array([[scalar_input, scalar_input]])
    probabilities = _network.predict_proba(feature_vector)
    return float(probabilities[0][1])