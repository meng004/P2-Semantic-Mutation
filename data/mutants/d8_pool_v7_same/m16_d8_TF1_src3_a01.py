"""Mutated D8 Gaussian Process classifier: training label comparison > 0 flipped to < 0."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

rng0 = np.random.default_rng(42)
train_X = rng0.uniform(-1.5, 1.5, (400, 2))
train_y = (train_X[:, 0] + train_X[:, 1] < 0).astype(int)

clf = GaussianProcessClassifier(kernel=RBF(length_scale=1.0), random_state=42)
clf.fit(train_X, train_y)


def program(x) -> float:
    x = float(x)
    proba = clf.predict_proba([[1.6 * x - 0.8, 1.6 * x - 0.8]])
    return float(proba[0, 1])