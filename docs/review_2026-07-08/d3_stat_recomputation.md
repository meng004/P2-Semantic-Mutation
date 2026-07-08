# Wave-D3 — Statistical Recomputation Audit (2026-07-08)

Auditor role: independently re-run every new analysis script added today, confirm SSOT JSONs and
manuscript numbers are reproducible, deterministic, and honestly labeled.

**Environment note.** No `.venv` exists in the repo; system `python` (3.11) carries the required
stack (numpy 2.4.6, scipy 1.17.1, statsmodels 0.14.6). `pytest` + `matplotlib`/`pandas`/`seaborn`/
`fastdtw`/`scikit-learn` were pip-installed into the system interpreter to run the suite. All runs
used `PYTHONPATH=src`. All commands below were executed from the repo root.

---

## 1. compute_s5_purity.py

**Command:** `PYTHONPATH=src python scripts/compute_s5_purity.py` — exit 0.
**Output SSOT:** `data/results/s5_purity_v4.json` — **BYTE-IDENTICAL** to committed (diff empty).
**Rerun (determinism):** second run byte-identical. Deterministic (no RNG; pure count over frozen matrix).

Key outputs: 292 mutants; flip histogram {0:170, 1:93, 2:27, 3:2}; silent=170, pure=93, multi(>=2)=29;
sigma well-defined 263/292 = **90.1%**; multi-stratum 9.9%; purity-among-detected 76.2% (93/122);
off-diagonal kill mass 88 = pure 57 + multi 31 (35.2% multi).

**Logic spot-check (does the flip derivation follow from sms_track2_v4.json?)** — YES.
- Every mutant appears in **exactly 5 MP cells** (verified: 292 mutants × 5 = 1460 outcome rows;
  label vocabulary is binary {KILLED:153, SURVIVE:1307}). So `flip_count = #MPs that KILL` is
  well-defined over all five invariants for every admitted mutant; no mutant is missing an MP cell
  that could silently undercount flips.
- Internal consistency: Σ flip_count = 0·170 + 1·93 + 2·27 + 3·2 = 153 = total KILLED. Arithmetic sound.
- `sigma_well_defined_fraction = (silent + pure)/N` = (170+93)/292 = 0.9006 → 90.1%. Correct.

**Hidden-assumption flag (F1, non-fatal, disclosed):** the 90.1% denominator folds the **170 silent
mutants** (flip=0, perturb no invariant; mapped to "active-off-taxonomy") into "sigma single-valued".
Purity **among detected** mutants is materially lower at 76.2% (93/122). The headline 90.1% therefore
leans on the large silent fraction (58% of the corpus). This is not an error — sigma is genuinely
single-valued on silent mutants, the SSOT carries both numbers, and main.tex:1004-1009 / 2461-2469
disclose the residual 9.9% multi-stratum explicitly. The 90.1% claim is valid and honestly labeled.

---

## 2. compute_h2_incidence.py

**Command:** `PYTHONPATH=src python scripts/compute_h2_incidence.py` — exit 0.
**Output SSOT:** `data/results/h2_incidence_v4.json` — **BYTE-IDENTICAL** to committed.
**Rerun:** byte-identical. Deterministic (scipy fisher_exact + conditional-MLE odds_ratio; no RNG).

**PRIMARY_V3 vs src/p2/config/primary.py PRIMARY_CELLS_V3:** identical
(a*→MP1, b*→MP2, c*→MP5, d*→MP2). Confirmed.

**Independent re-derivation** of the 2×2 from sms_track2_v4.json (re-implemented outside the script):
aligned nonzero/zero = **6/6**, cross nonzero/zero = **9/39** → aligned 6/12, cross 9/48. Matches SSOT.
sample OR 4.3333, conditional-MLE OR 4.2038, one-sided Fisher p 0.035488, CI-low 1.1165. All match SSOT.

Robustness grid makes sense — same estimand across pool variants, sample OR 4.13–7.00, one-sided
p 0.0064–0.0486; directionally stable. Manuscript quotes "OR 4.1–7.0, p 0.006–0.049" — matches.

**Note:** the script's `manuscript_claim_9_12_vs_6_48` block (OR 21, p 5.3e-5) is a *diagnostic*
reproduction of a historical mislabel, NOT a live claim. The current manuscript (main.tex:2000-2007)
uses the SSOT-correct 6/12 vs 9/48 and OR 4.2/4.33 — the mislabel has already been corrected in prose.

---

## 3. build_industrial_ssot.py (both modes)

**Derive mode:** `PYTHONPATH=src python scripts/build_industrial_ssot.py` — exit 0, **all 24 checks PASS**.
Outputs `industrial_arm_v1.json` + `industrial_stats_v1.json` — both **BYTE-IDENTICAL** to committed.
Reads only the committed `data/results/industrial_percase_v1.json` — **self-sufficient** (no scratchpad
needed). **No reproducibility gap:** a fresh clone reproduces every paper number via derive mode.

**Extract mode:** `PYTHONPATH=src python scripts/build_industrial_ssot.py --extract <scratchpad>/defect4mr/P12-Defect4MR-1.0.1`
— exit 0; regenerated `industrial_percase_v1.json` is **BYTE-IDENTICAL** to committed (34 cases,
1124 applied mutants). Extract mode requires the Zenodo deposit (DOI 10.5281/zenodo.21203424), which
is public and documented in PROVENANCE — appropriate; the committed per-case SSOT decouples paper
reproduction from the deposit download.

**Rerun (determinism):** derive-mode second run byte-identical for both outputs. Seeds honored
(BOOT_SEED=20260704). Battery reproduces **exactly**:

| Battery statistic | Reproduced | Target |
|---|---|---|
| Exact sign-flip permutation p (2^27 DP) | 0.01423 | 0.014 ✓ |
| Monte Carlo sign-flip mean-diff p (seeded) | 0.0047 | 0.005 ✓ |
| BCa CI Cliff's delta | [0.068, 0.461] | [+0.068, +0.461] ✓ |
| Wilcoxon V / z / unadj p | 279.5 / 2.1623 / 0.0153 | 279.5 / 2.162 / 0.015 ✓ |

---

## 4. rq3_friedman_v4.json (16.76 / 0.0022)

**Command:** `PYTHONPATH=src SMS_VERSION=v4 python scripts/compute_rq3_friedman.py` — exit 0.
**Headline chi2 = 16.7586, p = 0.0021532 — reproduce EXACTLY** (manuscript 16.76 / 0.0022, main.tex:2653).
Per-class p (a 0.406, b 0.0350, c 0.231, d 0.287) × Bonferroni 4 → 1.000 / 0.140 / 0.924 / 1.000,
matches main.tex:2659.

**Flag (F2, secondary field):** the file does **NOT** regenerate byte-identically. `rank_means`
regenerate as [3.25, 2.417, 2.25, 2.75, 4.333] vs committed [3.083, 2.583, 2.0, 3.0, 4.333]
(plus one last-digit float in per_class b). Cause: the script derives rank means via
`np.argsort(np.argsort(M,axis=1))` — **ordinal (not average) ranks with an unstable default sort**;
tie-breaking is numpy-version dependent. Reruns in THIS environment are mutually identical
(run2==run3, i.e. deterministic here), so the committed values came from a different numpy build.
The manuscript's rank means (3.08/2.58/2.00/3.00/4.33, main.tex:2657) match the **committed** JSON,
not a fresh regen here. The headline chi2/p (the load-bearing numbers) are unaffected. File was
restored to committed via `git checkout` after the audit.

---

## 5. Test suite

`PYTHONPATH=src python -m pytest tests/ -q` → **192 passed, 0 failed** (19 warnings, 13 s).
Matches the documented "192 passed" baseline; today's changes do not break the suite.
(15 initial collection errors were missing optional deps — matplotlib etc. — resolved by install,
not caused by today's changes.)

---

## 6. Number-by-number manuscript ↔ SSOT match table

| Value | SSOT path | tex location | Match |
|---|---|---|---|
| 263/292 (90.1%) sigma single-valued | s5_purity_v4 overall.n_silent+n_pure / n_mutants | main.tex:1006, 2461 | ✓ |
| residual 9.9% multi-stratum | s5_purity_v4 overall.multistratum_fraction | main.tex:1007, 2462 | ✓ |
| flip hist {0:170,1:93,≥2:29} | s5_purity_v4 overall.flip_histogram | main.tex:2460 | ✓ |
| 29 multi-stratum mutants | s5_purity_v4 n_multistratum_flip_ge2 | main.tex:2462 | ✓ |
| 57:31 pure/multi off-diagonal | s5_purity_v4 rq2_off_diagonal_reattribution | main.tex:2473 | ✓ |
| aligned 6/12, cross 9/48 | h2_incidence_v4 headline table_aligned/cross | main.tex:2000 | ✓ |
| incidence 50% vs 18.75% | h2_incidence_v4 aligned/cross_incidence | main.tex:2001 | ✓ |
| Fisher one-sided p | h2_incidence_v4 fisher_p_onesided_greater = 0.035488 | main.tex:2002 "p=0.036" | △ rounding (0.0355→0.035, tex says 0.036) |
| cond-MLE OR 4.2 / sample OR 4.33 | h2_incidence_v4 conditional_mle/sample_odds_ratio | main.tex:2003 | ✓ |
| CI [1.12, +∞) | h2_incidence_v4 or_ci95_onesided_lower = 1.1165 | main.tex:2004 | ✓ |
| grid OR 4.1–7.0, p 0.006–0.049 | h2_incidence_v4 robustness_grid | main.tex:2005 | ✓ |
| T1 377/1124=0.335, Wilson [0.308,0.364] | industrial_arm_v1 group_kill_totals/rates_wilson95 | main.tex:2545 | ✓ |
| A1 348, B1 274, B2 228 (0.310/0.244/0.203) | industrial_arm_v1 group_kill_totals/rates | main.tex:2546-2547 | ✓ |
| mean paired diff +0.101, CI [0.029,0.179] | industrial_stats_v1 primary_comparison_T1_gt_B1 | main.tex:2548-2549 | ✓ |
| Holm p 0.046, Cliff delta 0.247 | industrial_stats_v1 primary...holm/cliffs_delta | main.tex:2549-2550 | ✓ |
| Wilcoxon V=279.5, z=2.16, p=0.015 | industrial_stats_v1 R3_...wilcoxon_summary | main.tex:2550-2551 | ✓ |
| exact perm p=0.014 (2^27) | industrial_stats_v1 exact_sign_flip... | main.tex:2557-2558 | ✓ |
| MC sign-flip p=0.005 | industrial_stats_v1 monte_carlo_sign_flip... | main.tex:2559 | ✓ |
| BCa CI [+0.07,+0.46] | industrial_stats_v1 bca_bootstrap_ci_cliffs_delta | main.tex:2560-2561 | ✓ |
| face 34/34 T1 | industrial_arm_v1 real_defect_face_totals.T1_detect | main.tex:2571 | ✓ |
| B1 miss 27/34, B2 miss 26/34 | industrial_arm_v1 ...B1/B2_zero_detect_cases | main.tex:2576-2577 | ✓ |
| A1-a lose 19, A1-b lose 17, shared 11 | industrial_arm_v1 ...A1a/A1b_lose, shared_losses | main.tex:2577-2579 | ✓ |
| chi2 16.76, p 0.0022 | rq3_friedman_v4 chi2/p_value | main.tex:2653 | ✓ |
| per-class Bonferroni 1.000/0.140/0.924/1.000 | rq3_friedman_v4 per_class (×4) | main.tex:2659 | ✓ |
| MP rank means 3.08/2.58/2.00/3.00/4.33 | rq3_friedman_v4 rank_means_mp1_to_mp5 | main.tex:2657 | △ matches committed JSON but not fresh regen (F2) |

No number in the new passages lacks an SSOT. No substantive mismatch.

---

## Flags summary

- **F1 (non-fatal, disclosed):** S5 90.1% denominator includes 170 silent mutants; purity-among-detected
  is 76.2%. Both in SSOT; manuscript discloses residual. Honest labeling — no action required.
- **F2 (minor reproducibility gap):** rq3_friedman_v4.json `rank_means` are computed with unstable
  ordinal argsort ranks → not byte-reproducible across numpy builds. Headline chi2/p unaffected and
  fully reproducible. Suggested fix: use average ranks (e.g. `scipy.stats.rankdata`) for `rank_means`
  so the secondary field is environment-stable. Low priority (does not touch any load-bearing claim).
- **△ (rounding nit):** Fisher one-sided p SSOT 0.035488 → main.tex:2002 states 0.036 (rounds to 0.035).
  Cosmetic; recommend 0.035 for exactness.

## Reproducibility verdicts

| Artifact | Byte-identical regen | Deterministic | Headline reproduces |
|---|---|---|---|
| s5_purity_v4.json | YES | YES | YES (90.1%) |
| h2_incidence_v4.json | YES | YES | YES (OR 4.33/4.2, p 0.036) |
| industrial_arm_v1.json | YES | YES | YES |
| industrial_stats_v1.json | YES | YES | YES (battery exact) |
| industrial_percase_v1.json (extract) | YES | YES | YES |
| rq3_friedman_v4.json | NO (rank_means only) | YES (same env) | YES (16.76/0.0022) |

Test suite: **192 passed, 0 failed.**
