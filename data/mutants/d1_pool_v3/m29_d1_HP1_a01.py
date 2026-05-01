import numpy as np
from sklearn.neural_network import MLPClassifier

SEED = 42
N_SAMPLES = 400
LOW, HIGH = -1.5, 1.5

def _make_training_data(seed: int):
    rng = np.random.default_rng(seed)
    features = rng.uniform(LOW, HIGH, (N_SAMPLES, 2))
    labels = np.where(features.sum(axis=1) > 0, 1, 0)
    return features, labels

_features, _labels = _make_training_data(SEED)

_mlp_kwargs = dict(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=SEED,
    alpha=1.0,
)
_model = MLPClassifier(**_mlp_kwargs).fit(_features, _labels)


def program(x) -> float:
    val = float(x)
    sample = np.array([[val, val]])
    proba = _model.predict_proba(sample)
    return float(proba[0, 1])