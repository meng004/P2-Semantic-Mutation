"""DVE two-level (PUT x fault-family) power simulation.

Plan reference: research/paper-draft-plan-mr-adequacy-tosem.md v1.1.1, section 3.6.

Purpose
-------
Determine the (number-of-PUTs, holdout-families-per-PUT) grid that reaches the
pre-registered 80% power target for the DVE-W primary endpoint, under the
pre-registered PUT-level sign-flip randomization test.

Generative model (matches the pre-registered analysis unit)
-----------------------------------------------------------
Dependence structure: mutant  in  family  in  PUT.  The endpoint is the
family detection score FDS(R) = family-equal mean of the per-family
instance-detection proportion det(R, g) in [0, 1].  The primary contrast is
the paired family-level difference between the treatment portfolio and a
comparator portfolio:

    diff(g) = det(R0 u S1, g) - det(R0 u S, g).

We simulate diff at the family level with a two-level random-effects
decomposition:

    diff(g) = mu + u_p + e_g,
        u_p ~ Normal(0, icc * v_tot)        (PUT-level effect, shared in PUT p)
        e_g ~ Normal(0, (1 - icc) * v_tot)  (family-level residual)

where mu is the TRUE mean paired difference (the effect being detected),
v_tot = sigma_diff**2 is the total variance of the family-level paired
difference, and icc = sigma_PUT**2 / v_tot is the intraclass correlation at
the PUT level.  This is exactly the dependence the round-3 EIC amendment
requires the test to respect: families within a PUT are correlated through
the shared u_p, so the exchangeable unit is the whole PUT.

Priors grounding (real pilot data, not invented)
------------------------------------------------
sigma_diff is grounded on the v4 pilot cell-level SMS spread
(std(SMS) = 0.211 across 60 cells; data/results/sms_track2_v4.json).  Because
two portfolios that both extend a shared R0 are positively correlated, the
paired-difference SD is smaller than the marginal SD; we sweep
sigma_diff in {0.15, 0.20, 0.25} to bracket plausible values and report the
sample size for each.

Primary test (pre-registered): PUT-level sign-flip
--------------------------------------------------
Per PUT p, aggregate the family diffs to d_p = mean_g diff(g).  The test
statistic is t = mean_p d_p (PUT-equal weight).  Under the sign-flip null,
each PUT's entire vector of observations may have its sign flipped; because
the statistic depends only on d_p, this reduces to flipping the sign of d_p.
For n_PUT <= EXACT_MAX we ENUMERATE all 2**n_PUT sign assignments exactly
(no Monte Carlo); otherwise we sample sign vectors.  One-sided p-value =
fraction of sign assignments whose statistic >= observed.

Reproducibility: fully seeded; no Date/random-without-seed usage.
"""
from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass, asdict

import numpy as np

EXACT_MAX = 20  # enumerate 2**n_PUT exactly up to this many PUTs
ALPHA = 0.05


def signflip_pvalue_exact(d_put: np.ndarray) -> float:
    """One-sided sign-flip p-value via exact enumeration of 2**P sign vectors.

    H0: mean paired difference <= 0.  Reject for large positive t.
    d_put: array of per-PUT aggregated differences d_p.
    """
    n = len(d_put)
    obs = d_put.mean()
    # enumerate sign vectors in {-1,+1}^n via bit patterns
    signs = np.array(list(itertools.product([1.0, -1.0], repeat=n)))
    stats = (signs * d_put).mean(axis=1)
    # >= obs (one-sided upper); +1 continuity via counting observed config
    ge = np.count_nonzero(stats >= obs - 1e-12)
    return ge / signs.shape[0]


def signflip_pvalue_sampled(d_put: np.ndarray, n_perm: int, rng: np.random.Generator) -> float:
    n = len(d_put)
    obs = d_put.mean()
    signs = rng.choice([1.0, -1.0], size=(n_perm, n))
    stats = (signs * d_put).mean(axis=1)
    ge = np.count_nonzero(stats >= obs - 1e-12)
    # include observed configuration for validity
    return (ge + 1) / (n_perm + 1)


def signflip_pvalue(d_put: np.ndarray, rng: np.random.Generator, n_perm: int = 20000) -> float:
    if len(d_put) <= EXACT_MAX:
        return signflip_pvalue_exact(d_put)
    return signflip_pvalue_sampled(d_put, n_perm, rng)


@dataclass
class Scenario:
    mu: float            # true mean paired family-diff (effect); 0 for type-I check
    sigma_diff: float    # total SD of family-level paired difference
    icc: float           # PUT-level intraclass correlation
    n_put: int           # number of PUTs
    n_fam: int           # holdout families per PUT


def simulate_once(sc: Scenario, rng: np.random.Generator) -> np.ndarray:
    """Return the per-PUT aggregated differences d_p for one simulated dataset."""
    v_tot = sc.sigma_diff ** 2
    sd_put = np.sqrt(sc.icc * v_tot)
    sd_fam = np.sqrt((1.0 - sc.icc) * v_tot)
    u = rng.normal(0.0, sd_put, size=sc.n_put)
    d_put = np.empty(sc.n_put)
    for p in range(sc.n_put):
        e = rng.normal(0.0, sd_fam, size=sc.n_fam)
        diff = sc.mu + u[p] + e
        d_put[p] = diff.mean()
    return d_put


def _sign_matrix(n_put: int, n_perm: int, rng: np.random.Generator) -> np.ndarray:
    """Sign vectors in {-1,+1}: exact enumeration if 2**n_put small, else sampled."""
    if 2 ** n_put <= max(n_perm, 4096):
        return np.array(list(itertools.product([1.0, -1.0], repeat=n_put)))
    return rng.choice([1.0, -1.0], size=(n_perm, n_put))


def power_of(sc: Scenario, n_sim: int, seed: int, n_perm: int = 2000) -> float:
    """Vectorized power: reuse one sign matrix across all simulated datasets.

    The primary test statistic t = mean_p d_p depends only on the sign vector
    applied to the per-PUT differences, so a single sign matrix serves every
    simulated dataset in the scenario (this is the standard, valid way to
    Monte-Carlo a randomization-test power curve).  Exact enumeration is used
    automatically whenever 2**n_put is small; the dedicated exact function
    (signflip_pvalue_exact) and its unit test cover the real single-dataset
    analysis path.
    """
    rng = np.random.default_rng(seed)
    signs = _sign_matrix(sc.n_put, n_perm, rng)          # (S, n_put)
    n_signs = signs.shape[0]
    # generate all datasets: per-PUT aggregated differences, shape (n_sim, n_put)
    v_tot = sc.sigma_diff ** 2
    sd_put = np.sqrt(sc.icc * v_tot)
    sd_fam = np.sqrt((1.0 - sc.icc) * v_tot)
    u = rng.normal(0.0, sd_put, size=(n_sim, sc.n_put))
    e_mean = rng.normal(0.0, sd_fam / np.sqrt(sc.n_fam), size=(n_sim, sc.n_put))
    d = sc.mu + u + e_mean                                # (n_sim, n_put)
    obs = d.mean(axis=1)                                 # (n_sim,)
    null_stats = (d @ signs.T) / sc.n_put                # (n_sim, S)
    ge = (null_stats >= obs[:, None] - 1e-12).sum(axis=1)
    pvals = ge / n_signs
    return float((pvals <= ALPHA).mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-sim", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260710)
    ap.add_argument("--out", default="data/dve/power_simulation_results.json")
    args = ap.parse_args()

    mu_grid = [0.0, 0.10, 0.15]          # 0.0 = type-I error check at nominal alpha
    sigma_grid = [0.15, 0.20, 0.25]
    icc_grid = [0.1, 0.2, 0.3]
    nput_grid = [12, 15, 17, 20]
    nfam_grid = [2, 3, 4]                 # holdout families per PUT

    results = []
    for mu in mu_grid:
        for sigma in sigma_grid:
            for icc in icc_grid:
                for n_put in nput_grid:
                    for n_fam in nfam_grid:
                        sc = Scenario(mu, sigma, icc, n_put, n_fam)
                        # deterministic per-scenario seed for reproducibility
                        sseed = (args.seed
                                 + int(mu * 1000) * 1_000_003
                                 + int(sigma * 100) * 10_007
                                 + int(icc * 100) * 101
                                 + n_put * 17 + n_fam)
                        pw = power_of(sc, args.n_sim, sseed)
                        row = asdict(sc)
                        row["total_holdout_families"] = n_put * n_fam
                        row["power" if mu > 0 else "type1"] = round(pw, 4)
                        results.append(row)

    payload = {
        "meta": {
            "plan_version": "v1.1.1",
            "plan_section": "3.6",
            "endpoint": "FDS (family-equal mean of per-family instance-detection proportion)",
            "test": "PUT-level sign-flip randomization, exact enumeration for n_PUT<=%d" % EXACT_MAX,
            "alpha": ALPHA,
            "n_sim": args.n_sim,
            "master_seed": args.seed,
            "prior_source": "data/results/sms_track2_v4.json (v4 pilot cell SMS std=0.211)",
            "grids": {
                "mu": mu_grid, "sigma_diff": sigma_grid, "icc": icc_grid,
                "n_put": nput_grid, "n_fam_per_put": nfam_grid,
            },
        },
        "results": results,
    }
    with open(args.out, "w") as f:
        json.dump(payload, f, indent=2)

    # console summary: type-I calibration + smallest design reaching 80% power
    t1 = [r["type1"] for r in results if "type1" in r]
    print("Type-I error (mu=0): mean=%.4f  min=%.4f  max=%.4f  (nominal %.2f)"
          % (np.mean(t1), np.min(t1), np.max(t1), ALPHA))
    for mu in [0.10, 0.15]:
        print(f"\n=== 80%% power frontier at true effect mu={mu} ===")
        for sigma in sigma_grid:
            for icc in icc_grid:
                ok = [r for r in results
                      if r.get("mu") == mu and r["sigma_diff"] == sigma
                      and r["icc"] == icc and r.get("power", 0) >= 0.80]
                if ok:
                    best = min(ok, key=lambda r: (r["n_put"], r["n_fam"]))
                    print("  sigma=%.2f icc=%.1f -> n_put=%d n_fam=%d (families=%d) power=%.3f"
                          % (sigma, icc, best["n_put"], best["n_fam"],
                             best["total_holdout_families"], best["power"]))
                else:
                    print("  sigma=%.2f icc=%.1f -> NOT reached within grid (max n_put=20,n_fam=4)"
                          % (sigma, icc))
    print("\nWrote", args.out)


if __name__ == "__main__":
    main()
