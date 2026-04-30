import numpy as np
from sklearn.neural_network import MLPRegressor


class _SigmoidTarget:
    def __init__(self, scale=2.0):
        self.scale = scale

    def __call__(self, t):
        t_arr = np.asarray(t, dtype=float)
        return np.reciprocal(1.0 + np.exp(-self.scale * t_arr))


def _make_training_data(seed=42, n=100, lo=-3.0, hi=3.0):
    rng = np.random.default_rng(seed)
    samples = rng.uniform(lo, hi, n)
    samples = np.sort(samples)
    target_fn = _SigmoidTarget(scale=2.0)
    return samples.reshape(-1, 1), target_fn(samples)


_X_tr, _y_tr = _make_training_data()


def _spec_pairs():
    yield "hidden_layer_sizes", (64, 32)
    yield "solver", "adam"
    yield "max_iter", 1000
    yield "random_state", 42
    yield "activation", "tanh"


_regressor = MLPRegressor(**dict(_spec_pairs()))
_regressor.fit(_X_tr, _y_tr)


def program(x) -> float:
    xf = float(x)
    t = 6.0 * xf - 3.0
    query = np.array([[t]], dtype=float)
    return float(_regressor.predict(query)[0])