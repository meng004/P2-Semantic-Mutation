import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer

def _prepare():
    gen = np.random.default_rng(42)
    samples = gen.uniform(-2.0, 2.0, 80)
    samples = np.sort(samples)
    X = samples.reshape(-1, 1)
    y = np.tanh(samples)
    return X, y

_X_TRAIN, _Y_TRAIN = _prepare()

_BASIS = SplineTransformer(n_knots=6, degree=3).fit(_X_TRAIN)
_DESIGN_MATRIX = _BASIS.transform(_X_TRAIN)
_REG = LinearRegression()
_REG.fit(_DESIGN_MATRIX, _Y_TRAIN)


def program(x) -> float:
    val = float(x)
    t = 4.0 * val - 2.0
    pt = np.array([[t]], dtype=float)
    phi = _BASIS.transform(pt)
    out = _REG.predict(phi)
    return float(out.item())