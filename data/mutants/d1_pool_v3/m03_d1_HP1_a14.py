import numpy as np
from sklearn.neural_network import MLPClassifier

_SEED = 42
_NUM_POINTS = 400
_BOUND = 1.5

_rng = np.random.default_rng(_SEED)
_raw_points = _rng.uniform(-_BOUND, _BOUND, (_NUM_POINTS, 2))

_labels_list = []
for _i in range(_raw_points.shape[0]):
    _a, _b = _raw_points[_i, 0], _raw_points[_i, 1]
    _labels_list.append(int((_a + _b) > 0))
_targets = np.array(_labels_list, dtype=int)

_config = {}
_config["hidden_layer_sizes"] = (32, 16)
_config["activation"] = "relu"
_config["solver"] = "adam"
_config["max_iter"] = 500
_config["random_state"] = _SEED
_config["alpha"] = 1.0

_net = MLPClassifier(**_config)
_net = _net.fit(_raw_points, _targets)


def program(x) -> float:
    v = float(x)
    feat = [[v, v]]
    probs = _net.predict_proba(feat)
    return float(probs[0, 1])