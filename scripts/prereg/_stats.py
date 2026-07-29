"""Shared frozen statistics utilities for the prereg-v2 analysis scripts.

Part of the FREEZE_MANIFEST hash set (F-7). Any post-freeze edit demotes the
consuming analysis to exploratory and must be logged in AMENDMENTS.md.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

Z95 = 1.959963984540054


def wilson_ci(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return float(centre - half), float(centre + half)


def mcnemar_onesided(b: int, c: int) -> float:
    """Exact one-sided McNemar: P(X >= b), X ~ Bin(b+c, 1/2)."""
    n = b + c
    if n == 0:
        return 1.0
    return float(stats.binom.sf(b - 1, n, 0.5))


def wilcoxon_greater(d: np.ndarray) -> tuple[float, float]:
    """One-sided (greater) Wilcoxon signed-rank p + matched-pairs
    rank-biserial r_mp (Kerby). Zero differences dropped (zero_method
    'wilcox'); scipy method='auto' (exact when tie-free and n<=25)."""
    d = np.asarray(d, float)
    d = d[d != 0]
    if len(d) < 5:
        return 1.0, 0.0
    ranks = stats.rankdata(np.abs(d))
    t_pos = float(ranks[d > 0].sum())
    t_neg = float(ranks[d < 0].sum())
    r_mp = (t_pos - t_neg) / (t_pos + t_neg)
    try:
        p = float(stats.wilcoxon(d, alternative="greater", method="auto").pvalue)
    except ValueError:
        p = 1.0
    return p, float(r_mp)


def hodges_lehmann(d: np.ndarray) -> float:
    """One-sample HL estimator: median of Walsh averages."""
    d = np.asarray(d, float)
    if len(d) == 0:
        return float("nan")
    i, j = np.triu_indices(len(d))
    return float(np.median((d[i] + d[j]) / 2.0))


def cliffs_delta(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    gt = sum((xi > y).sum() for xi in x)
    lt = sum((xi < y).sum() for xi in x)
    return float((gt - lt) / (len(x) * len(y)))


def cohen_kappa(a: list, b: list) -> float:
    assert len(a) == len(b) and len(a) > 0
    labels = sorted(set(a) | set(b))
    idx = {l: i for i, l in enumerate(labels)}
    m = np.zeros((len(labels), len(labels)))
    for x, y in zip(a, b):
        m[idx[x], idx[y]] += 1
    n = m.sum()
    po = np.trace(m) / n
    pe = float((m.sum(0) * m.sum(1)).sum()) / n**2
    if pe == 1.0:
        return 1.0
    return float((po - pe) / (1 - pe))


def bootstrap_ci(values: np.ndarray, stat_fn, n_boot: int = 10_000,
                 seed: int = 20260728, method: str = "bca") -> tuple[float, float]:
    """BCa (default) or percentile bootstrap CI for stat_fn(values)."""
    values = np.asarray(values, float)
    n = len(values)
    rng = np.random.default_rng(seed)
    theta = stat_fn(values)
    boots = np.array([
        stat_fn(values[rng.integers(0, n, n)]) for _ in range(n_boot)
    ])
    boots = boots[np.isfinite(boots)]
    if len(boots) == 0:
        return float("nan"), float("nan")
    if method == "percentile":
        return float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))
    prop = np.clip((boots < theta).mean(), 1e-9, 1 - 1e-9)
    z0 = stats.norm.ppf(prop)
    jack = np.array([
        stat_fn(np.delete(values, i)) for i in range(n)
    ])
    jm = jack.mean()
    num = ((jm - jack) ** 3).sum()
    den = 6.0 * (((jm - jack) ** 2).sum()) ** 1.5
    a = num / den if den > 0 else 0.0
    lo_p = stats.norm.cdf(z0 + (z0 + stats.norm.ppf(0.025)) / (1 - a * (z0 + stats.norm.ppf(0.025))))
    hi_p = stats.norm.cdf(z0 + (z0 + stats.norm.ppf(0.975)) / (1 - a * (z0 + stats.norm.ppf(0.975))))
    lo_p, hi_p = float(np.clip(lo_p, 0, 1)), float(np.clip(hi_p, 0, 1))
    return float(np.quantile(boots, lo_p)), float(np.quantile(boots, hi_p))


def pava_means(y_sum: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Weighted non-decreasing isotonic fit of level means (PAVA)."""
    means = y_sum / w
    out: list[list[float]] = []
    for i in range(len(means)):
        out.append([i, means[i], w[i]])
        while len(out) > 1 and out[-2][1] >= out[-1][1]:
            i0, m1, w1 = out[-2]
            _, m2, w2 = out.pop()
            out[-1] = [i0, (m1 * w1 + m2 * w2) / (w1 + w2), w1 + w2]
    fit = np.empty(len(means))
    for k, (i0, mval, _) in enumerate(out):
        i1 = out[k + 1][0] if k + 1 < len(out) else len(means)
        fit[int(i0):int(i1)] = mval
    return fit


def dose_T(kills: np.ndarray, reps: int) -> float:
    """T = RSS_const - RSS_iso on level kill-rates (weights = reps)."""
    kills = np.asarray(kills, float)
    L = len(kills)
    means = kills / reps
    pooled = kills.sum() / (reps * L)
    rss_const = float((reps * (means - pooled) ** 2).sum())
    fit = pava_means(kills, np.full(L, float(reps)))
    rss_iso = float((reps * (means - fit) ** 2).sum())
    return rss_const - rss_iso


def page_L(rate_matrix: np.ndarray) -> tuple[float, float]:
    """Descriptive Page trend statistic: rows = curves (subjects),
    cols = ordered dose levels (treatments). Returns (L, approx one-sided p)."""
    ranks = np.apply_along_axis(stats.rankdata, 1, rate_matrix)
    n, k = rate_matrix.shape
    L = float((ranks.sum(axis=0) * np.arange(1, k + 1)).sum())
    mu = n * k * (k + 1) ** 2 / 4.0
    var = n * k**2 * (k + 1) * (k**2 - 1) / 144.0
    z = (L - mu) / np.sqrt(var) if var > 0 else 0.0
    return L, float(stats.norm.sf(z))


def record(hypothesis: str, estimate, ci, p, verdict: str, **extras) -> dict:
    """Unified output schema {hypothesis, estimate, ci, p, verdict} (+extras)."""
    return {
        "hypothesis": hypothesis,
        "estimate": None if estimate is None else float(estimate),
        "ci": None if ci is None else [float(ci[0]), float(ci[1])],
        "p": None if p is None else float(p),
        "verdict": verdict,
        "extras": extras,
    }
