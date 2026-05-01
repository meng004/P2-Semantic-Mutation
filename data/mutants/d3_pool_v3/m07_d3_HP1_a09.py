import numpy as np
from sklearn.linear_model import LogisticRegression


def _generate_training_data(seed=42, count=400, low=-1.5, high=1.5):
    gen = np.random.default_rng(seed)
    samples = gen.uniform(low, high, (count, 2))
    return samples


_data = _generate_training_data()

_x1 = _data[:, 0]
_x2 = _data[:, 1]
_decision_values = np.add(np.multiply(0.8, _x1), np.multiply(-0.6, _x2))
_y = (_decision_values > 0).astype(int)

_C_VALUE = 10 ** (-4)

_logreg = LogisticRegression(
    C=_C_VALUE,
    solver="lbfgs",
    max_iter=1000,
    random_state=42,
)
_logreg.fit(_data, _y)


def program(x) -> float:
    scalar = float(x)
    sample = np.asarray([[scalar, 0.0]])
    probabilities = _logreg.predict_proba(sample)
    return float(probabilities[0][1])