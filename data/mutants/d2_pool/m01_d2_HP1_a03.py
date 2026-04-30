import numpy as np
from sklearn.svm import SVC

_GAMMA = 1e-3
_SEED = 42

def _make_dataset():
    generator = np.random.default_rng(_SEED)
    samples = generator.uniform(-1.5, 1.5, size=(400, 2))
    sq_x = samples[:, 0] * samples[:, 0]
    sq_y = samples[:, 1] * samples[:, 1]
    inside = (sq_x + sq_y) < 1.0
    return samples, inside.astype(np.int64)


_data, _labels = _make_dataset()

_classifier = SVC(kernel="rbf", C=1.0, gamma=_GAMMA,
                  probability=True, random_state=_SEED)
_classifier = _classifier.fit(_data, _labels)


def _to_feature(scalar_value):
    coord = 2.0 - 2.0 * scalar_value
    return [[coord, 0.0]]


def program(x) -> float:
    scalar = float(x)
    point = _to_feature(scalar)
    prob_matrix = _classifier.predict_proba(point)
    positive_prob = prob_matrix[0, 1]
    return float(positive_prob)