import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer

def _build_model():
    rng = np.random.default_rng(42)
    t_samples = np.sort(rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
    y_samples = np.tanh(t_samples.ravel())
    transformer = SplineTransformer(n_knots=6, degree=3)
    design = transformer.fit_transform(t_samples)
    estimator = LinearRegression().fit(design, y_samples)
    return transformer, estimator

_transformer, _estimator = _build_model()


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    point = np.asarray([[t]], dtype=float)
    basis = _transformer.transform(point)
    return float(_estimator.predict(basis)[0])