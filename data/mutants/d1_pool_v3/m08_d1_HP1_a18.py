import numpy as np
from sklearn.neural_network import MLPClassifier


_SEED_VALUE = 42
_SAMPLE_COUNT = 400
_RANGE_LIMIT = 1.5

_random_source = np.random.default_rng(_SEED_VALUE)
_coordinate_matrix = _random_source.uniform(-_RANGE_LIMIT, _RANGE_LIMIT, size=(_SAMPLE_COUNT, 2))

_sum_per_row = np.add(_coordinate_matrix[:, 0], _coordinate_matrix[:, 1])
_class_labels = np.where(_sum_per_row > 0, 1, 0).astype(int)


def _construct_classifier():
    params = {
        "hidden_layer_sizes": (32, 16),
        "activation": "relu",
        "solver": "adam",
        "max_iter": 500,
        "random_state": _SEED_VALUE,
    }
    params["alpha"] = 1.0
    return MLPClassifier(**params)


_classifier_instance = _construct_classifier()
_classifier_instance.fit(_coordinate_matrix, _class_labels)


def program(x) -> float:
    scalar_value = float(x)
    feature_vector = np.array([[scalar_value, scalar_value]])
    probability_output = _classifier_instance.predict_proba(feature_vector)
    return float(probability_output[0, 1])