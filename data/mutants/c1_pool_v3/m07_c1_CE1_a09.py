import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


class _SurrogateBuilder:
    def __init__(self, seed=42, n=60, lo=-3.0, hi=3.0, length=1.0, noise=1e-1):
        self.seed = seed
        self.n = n
        self.lo = lo
        self.hi = hi
        self.length = length
        self.noise = noise

    def _draw_inputs(self):
        rng = np.random.default_rng(self.seed)
        pts = rng.uniform(self.lo, self.hi, self.n)
        return np.sort(pts)

    def _kernel(self):
        parts = (RBF(length_scale=self.length), WhiteKernel(noise_level=self.noise))
        acc = parts[0]
        for p in parts[1:]:
            acc = acc + p
        return acc

    def build(self):
        t_sorted = self._draw_inputs()
        X = t_sorted.reshape((-1, 1))
        y = erf(t_sorted)
        gpr = GaussianProcessRegressor(
            kernel=self._kernel(),
            random_state=self.seed,
            normalize_y=True,
        )
        gpr.fit(X, y)
        return gpr


_model = _SurrogateBuilder().build()


def program(x) -> float:
    val = float(x)
    t = 6.0 * val - 3.0
    pred = _model.predict(np.array([[t]], dtype=float))
    return float(np.ravel(pred)[0])