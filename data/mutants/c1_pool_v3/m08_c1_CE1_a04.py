import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


class _SurrogateBuilder:
    def __init__(self, seed=42, n_train=60, t_lo=-3.0, t_hi=3.0,
                 length_scale=1.0, noise_level=1e-1):
        self.seed = seed
        self.n_train = n_train
        self.t_lo = t_lo
        self.t_hi = t_hi
        self.length_scale = length_scale
        self.noise_level = noise_level

    def _draw_samples(self):
        rng = np.random.default_rng(self.seed)
        unsorted = rng.uniform(self.t_lo, self.t_hi, self.n_train)
        return np.sort(unsorted)

    def _training_pair(self):
        t_sorted = self._draw_samples()
        X = t_sorted.reshape(-1, 1)
        y = erf(t_sorted)
        return X, y

    def _kernel(self):
        k_smooth = RBF(length_scale=self.length_scale)
        k_noise = WhiteKernel(noise_level=self.noise_level)
        return k_smooth + k_noise

    def build(self):
        X, y = self._training_pair()
        gpr = GaussianProcessRegressor(
            kernel=self._kernel(),
            random_state=self.seed,
            normalize_y=True,
        )
        gpr.fit(X, y)
        return gpr


_model = _SurrogateBuilder().build()


def program(x) -> float:
    xf = float(x)
    t = 6.0 * xf - 3.0
    pred = _model.predict(np.array([[t]]))
    return float(pred[0])