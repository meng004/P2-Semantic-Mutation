import numpy as np
from sklearn.neural_network import MLPRegressor as _MLP


_TRAIN_SEED = 42
_TRAIN_SIZE = 100


def _sig2(z):
    z = np.asarray(z, dtype=float)
    neg_two_z = np.negative(2.0 * z)
    denom = np.add(1.0, np.exp(neg_two_z))
    return np.divide(1.0, denom)


def _draw_grid():
    gen = np.random.default_rng(_TRAIN_SEED)
    pts = gen.uniform(low=-3.0, high=3.0, size=_TRAIN_SIZE)
    pts = np.sort(pts, kind="quicksort")
    return pts


_t_vec = _draw_grid()
_X = _t_vec[:, None]
_Y = _sig2(_t_vec)

_params = {
    "hidden_layer_sizes": (64, 32),
    "activation": "relu",
    "solver": "adam",
    "max_iter": 5,
    "random_state": _TRAIN_SEED,
}

_net = _MLP(**_params)
_net.fit(_X, _Y)


def program(x) -> float:
    xv = float(x)
    tv = 6.0 * xv - 3.0
    feats = [[tv]]
    out = _net.predict(feats)
    return float(out[0])