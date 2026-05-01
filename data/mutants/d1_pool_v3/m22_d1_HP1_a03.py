import numpy as np
from sklearn.neural_network import MLPClassifier

ALPHA_VALUE = 1.0
HIDDEN = (32, 16)
TRAIN_SIZE = 400
BOUNDS = (-1.5, 1.5)
SEED = 42

rng = np.random.default_rng(SEED)
samples = rng.uniform(BOUNDS[0], BOUNDS[1], (TRAIN_SIZE, 2))
sums = np.add(samples[:, 0], samples[:, 1])
y_labels = (sums > 0).astype(np.int64)

classifier = MLPClassifier(
    hidden_layer_sizes=HIDDEN,
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=SEED,
    alpha=ALPHA_VALUE,
)
classifier = classifier.fit(samples, y_labels)


def program(x) -> float:
    scalar = float(x)
    feature_row = [[scalar, scalar]]
    probability_matrix = classifier.predict_proba(feature_row)
    return float(probability_matrix[0, 1])