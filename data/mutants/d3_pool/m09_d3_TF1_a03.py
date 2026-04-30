import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_scores = 0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1]
_y_train = np.where(_scores > 0, 0, 1).astype(int)

_classifier = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_classifier.fit(_X_train, _y_train)


def program(x) -> float:
    x_val = float(x)
    probabilities = _classifier.predict_proba([[x_val, 0.0]])
    return float(probabilities[0, 1])