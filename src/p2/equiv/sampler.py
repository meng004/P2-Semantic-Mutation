import numpy as np
from dataclasses import dataclass
from typing import Protocol


class InputSampler(Protocol):
    def sample(self, k_eq: int) -> np.ndarray: ...


@dataclass
class UniformSampler:
    low: float
    high: float
    dim: int
    seed: int = 42

    def sample(self, k_eq: int) -> np.ndarray:
        rng = np.random.default_rng(self.seed)
        return rng.uniform(self.low, self.high, size=(k_eq, self.dim))


def sample_inputs(sampler: InputSampler, k_eq: int) -> np.ndarray:
    return sampler.sample(k_eq)
