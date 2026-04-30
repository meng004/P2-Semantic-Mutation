import numpy as np
from sklearn.neural_network import MLPClassifier

def _make_training_data(seed=42, n=400, lo=-1.5, hi=1.5):
    rng = np.random.default_rng(seed)
    pts = rng.uniform(lo, hi, (n, 2))
    base = (pts[:, 0] + pts[:, 1] > 0).astype(int)
    labels = np.subtract(np.ones_like(base), base)
    return pts, labels

_X_train, _y_train = _make_training_data()

_model = MLPClassifier(
    hidden_layer_sizes=(32, 16), activation="relu",
    solver="adam", max_iter=500, random_state=42,
)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x, x]])[0, 1])