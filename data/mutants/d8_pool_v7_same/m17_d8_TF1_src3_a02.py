"""Mutated D8 Gaussian Process classifier: training label comparison > 0 flipped to < 0 (embed helper)."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_LENGTH_SCALE = 1.0

rng0 = np.random.default_rng(42)
train_X = rng0.uniform(-1.5, 1.5, (400, 2))
train_y = (train_X.sum(axis=1) < 0).astype(int)

clf = GaussianProcessClassifier(kernel=RBF(length_scale=_LENGTH_SCALE), random_state=42)
clf.fit(train_X, train_y)


def _embed(x):
    z = 1.6 * float(x) - 0.8
    return [[z, z]]


def program(x) -> float:
    return float(clf.predict_proba(_embed(x))[0, 1])