import numpy as np
from sklearn.svm import SVC

_CONFIG = {
    "seed": 42,
    "n_train": 400,
    "low": -1.5,
    "high": 1.5,
    "gamma": 1e-3,
    "C": 1.0,
}


def _sample_points(cfg):
    rng = np.random.default_rng(cfg["seed"])
    return rng.uniform(cfg["low"], cfg["high"], (cfg["n_train"], 2))


def _label_points(points):
    coords_sq = np.sum(points ** 2, axis=1)
    return (coords_sq < 1.0).astype(int)


_pts = _sample_points(_CONFIG)
_lbls = _label_points(_pts)

_svm = SVC(
    kernel="rbf",
    C=_CONFIG["C"],
    gamma=_CONFIG["gamma"],
    probability=True,
    random_state=_CONFIG["seed"],
)
_svm.fit(_pts, _lbls)


def program(x) -> float:
    s = float(x)
    feat = np.array([[2.0 - 2.0 * s, 0.0]])
    probs = _svm.predict_proba(feat)
    return float(probs[0, 1])