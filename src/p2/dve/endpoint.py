"""DVE primary endpoint (FDS) and the pre-registered PUT-level sign-flip test.

Plan v1.1.1 §3.6; pre-registration §3. The kill matrix K is a boolean map
mutant -> detected-by-portfolio; families group mutants; PUTs group families.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class FamilyDetection:
    """Per-family detection score in a single portfolio evaluation."""
    put: str
    family: str
    score: float          # mean over instances of det_R(m) in [0,1]
    n_instances: int


def family_detection_score(detected: Sequence[bool]) -> float:
    """det(R, g) = mean over family instances of the boolean detection flag."""
    if len(detected) == 0:
        raise ValueError("family has no instances")
    return float(np.mean([1.0 if d else 0.0 for d in detected]))


def fds(fam_scores: Iterable[FamilyDetection]) -> float:
    """FDS(R) = family-equal mean of per-family detection scores."""
    scores = [f.score for f in fam_scores]
    if not scores:
        raise ValueError("no families")
    return float(np.mean(scores))


def paired_family_diffs(
    treat: Mapping[tuple, float],
    comp: Mapping[tuple, float],
) -> Dict[str, List[float]]:
    """Group paired (treat-comp) family differences by PUT.

    treat/comp map (put, family) -> per-family detection score for the two
    portfolios being compared. Returns {put: [diff, ...]}.
    """
    if set(treat) != set(comp):
        raise ValueError("treat and comp must cover the same (put, family) keys")
    by_put: Dict[str, List[float]] = {}
    for key in treat:
        put, _fam = key
        by_put.setdefault(put, []).append(treat[key] - comp[key])
    return by_put


def put_level_diffs(by_put: Mapping[str, Sequence[float]]) -> np.ndarray:
    """d_p = mean over families in PUT p of the paired difference (§3.6)."""
    puts = sorted(by_put)
    return np.array([float(np.mean(by_put[p])) for p in puts])


def signflip_test(d_put: np.ndarray, shift: float = 0.0,
                  exact_max: int = 20, n_perm: int = 20000,
                  seed: int = 0) -> dict:
    """One-sided PUT-level sign-flip randomization test.

    H0: mean paired difference <= shift (shift=0 for statistical superiority;
    shift=MID for practical importance). Statistic t = mean_p d_p. The
    exchangeable unit is the whole PUT, so signs are flipped per PUT. For
    n_PUT <= exact_max all 2**n_PUT sign vectors are ENUMERATED exactly.
    """
    d = np.asarray(d_put, dtype=float) - shift
    n = len(d)
    if n == 0:
        raise ValueError("no PUTs")
    obs = d.mean()
    if 2 ** n <= max(exact_max_signs(exact_max), n_perm):
        signs = np.array(list(itertools.product([1.0, -1.0], repeat=n)))
        exact = True
    else:
        rng = np.random.default_rng(seed)
        signs = rng.choice([1.0, -1.0], size=(n_perm, n))
        # include the observed all-plus configuration for validity
        signs = np.vstack([np.ones(n), signs])
        exact = False
    stats = (signs * d).mean(axis=1)
    ge = int(np.count_nonzero(stats >= obs - 1e-12))
    pval = ge / signs.shape[0]
    return {
        "statistic": float(d_put.mean() if shift == 0 else obs + shift),
        "shifted_statistic": float(obs),
        "shift": shift,
        "p_value": float(pval),
        "n_put": n,
        "exact": exact,
        "n_configurations": int(signs.shape[0]),
    }


def exact_max_signs(exact_max: int) -> int:
    return 2 ** exact_max


def two_level_bootstrap_ci(by_put: Mapping[str, Sequence[float]],
                           n_boot: int = 10000, alpha: float = 0.05,
                           seed: int = 0) -> dict:
    """Percentile CI for the mean family-diff via two-level bootstrap.

    Resample PUTs with replacement, then families within each resampled PUT.
    (BCa is specified in the prereg; the percentile interval here is the
    validated core; BCa correction is a thin wrapper added at analysis time.)
    """
    rng = np.random.default_rng(seed)
    puts = sorted(by_put)
    arrs = {p: np.asarray(by_put[p], dtype=float) for p in puts}
    point = float(np.mean([arrs[p].mean() for p in puts]))
    boots = np.empty(n_boot)
    npu = len(puts)
    for b in range(n_boot):
        chosen = rng.integers(0, npu, size=npu)
        put_means = []
        for idx in chosen:
            fam = arrs[puts[idx]]
            rs = rng.integers(0, len(fam), size=len(fam))
            put_means.append(fam[rs].mean())
        boots[b] = np.mean(put_means)
    lo = float(np.quantile(boots, alpha / 2))
    hi = float(np.quantile(boots, 1 - alpha / 2))
    lo1 = float(np.quantile(boots, alpha))  # one-sided lower for MID test
    return {"point": point, "ci_lo": lo, "ci_hi": hi, "one_sided_lo": lo1}
