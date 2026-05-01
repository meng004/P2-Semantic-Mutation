import numpy as np
from sklearn.linear_model import LogisticRegression


def _generate_corpus(rng_seed: int, count: int):
    gen = np.random.default_rng(rng_seed)
    coords = gen.uniform(-1.5, 1.5, size=(count, 2))
    x1_col = coords[:, 0]
    x2_col = coords[:, 1]
    margin = np.subtract(np.multiply(0.8, x1_col), np.multiply(0.6, x2_col))
    classes = (margin > 0).astype(int)
    return coords, classes


_TRAIN_X, _TRAIN_Y = _generate_corpus(42, 400)

_C_VALUE = 1e-4
_SOLVER = "lbfgs"
_MAX_ITER = 1000
_SEED = 42

_classifier = LogisticRegression(
    C=_C_VALUE,
    solver=_SOLVER,
    max_iter=_MAX_ITER,
    random_state=_SEED,
)
_classifier.fit(_TRAIN_X, _TRAIN_Y)


def program(x) -> float:
    scalar = float(x)
    sample = np.asarray([[scalar, 0.0]], dtype=float)
    posterior = _classifier.predict_proba(sample)
    return float(posterior[0, 1])