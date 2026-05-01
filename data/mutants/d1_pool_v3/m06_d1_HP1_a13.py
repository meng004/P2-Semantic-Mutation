import numpy as np
from sklearn.neural_network import MLPClassifier

SEED = 42
N_TRAIN = 400
LOW, HIGH = -1.5, 1.5

_random_state = np.random.default_rng(SEED)
_train_features = _random_state.uniform(LOW, HIGH, size=(N_TRAIN, 2))
_train_labels = np.asarray(
    [1 if (row[0] + row[1]) > 0 else 0 for row in _train_features],
    dtype=int,
)

_mlp_params = {
    "hidden_layer_sizes": (32, 16),
    "activation": "relu",
    "solver": "adam",
    "max_iter": 500,
    "random_state": SEED,
    "alpha": 1.0,
}

_classifier = MLPClassifier(**_mlp_params)
_classifier.fit(_train_features, _train_labels)


def program(x) -> float:
    scalar = float(x)
    query = np.array([[scalar, scalar]], dtype=float)
    prob_matrix = _classifier.predict_proba(query)
    return float(prob_matrix[0, 1])