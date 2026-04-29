import numpy as np
from p2.equiv.sampler import sample_inputs, UniformSampler


def test_uniform_sampler_returns_k_eq_samples():
    sampler = UniformSampler(low=0.0, high=1.0, dim=3, seed=42)
    samples = sample_inputs(sampler, k_eq=1000)
    assert samples.shape == (1000, 3)
    assert np.all(samples >= 0) and np.all(samples <= 1)


def test_seed_reproducibility():
    s1 = sample_inputs(UniformSampler(0, 1, 2, seed=42), k_eq=100)
    s2 = sample_inputs(UniformSampler(0, 1, 2, seed=42), k_eq=100)
    np.testing.assert_array_equal(s1, s2)
