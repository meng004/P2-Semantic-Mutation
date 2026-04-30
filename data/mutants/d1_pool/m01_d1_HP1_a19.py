import numpy as np
from sklearn.neural_network import MLPClassifier


def _spawn_corpus():
    src = np.random.default_rng(42)
    raw = src.uniform(-1.5, 1.5, 800).reshape(400, 2)
    flags = []
    for row_idx in range(raw.shape[0]):
        a = raw[row_idx, 0]
        b = raw[row_idx, 1]
        flags.append(int(a + b > 0))
    return raw, np.array(flags, dtype=int)


_inputs, _outputs = _spawn_corpus()


def _assemble_net():
    base_config = dict(
        hidden_layer_sizes=(32, 16),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
    )
    overrides = {"alpha": 1.0}
    merged = {**base_config, **overrides}
    return MLPClassifier(**merged)


_net = _assemble_net()
_net.fit(_inputs, _outputs)


def program(x) -> float:
    coord = float(x)
    point = [[coord] * 2]
    distribution = _net.predict_proba(np.asarray(point))
    return float(distribution[0, 1])