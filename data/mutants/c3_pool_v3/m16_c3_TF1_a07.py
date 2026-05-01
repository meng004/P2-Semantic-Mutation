import numpy as np
from sklearn.neural_network import MLPRegressor


class _TrainingBundle:
    def __init__(self, seed, n):
        self.seed = seed
        self.n = n
        self._build()

    @staticmethod
    def _phi(values):
        values = np.asarray(values, dtype=float)
        exponent = -2.0 * values
        return 1.0 / (1.0 + np.exp(exponent))

    def _build(self):
        rng = np.random.default_rng(self.seed)
        samples = rng.uniform(-3.0, 3.0, self.n)
        samples.sort()
        self.X = samples.reshape(self.n, 1)
        self.y = self._phi(samples)


_BUNDLE = _TrainingBundle(seed=42, n=100)


def _build_regressor(seed):
    kwargs = {}
    kwargs["hidden_layer_sizes"] = (64, 32)
    kwargs["activation"] = "relu"
    kwargs["solver"] = "adam"
    kwargs["max_iter"] = 5
    kwargs["random_state"] = seed
    return MLPRegressor(**kwargs)


_model = _build_regressor(42)
_model.fit(_BUNDLE.X, _BUNDLE.y)


def program(x) -> float:
    xv = float(x)
    t_val = -3.0 + 6.0 * xv
    query = np.array([[t_val]], dtype=float)
    yhat = _model.predict(query)[0]
    return float(yhat)