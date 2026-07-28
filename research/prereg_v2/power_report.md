# Power / Feasibility Report — Task 1.2 (argumentation-uplift Phase 1)

**Date:** 2026-07-28 · **Script:** `scripts/prereg/power_simulation.py` (seed 20260728) · **Raw output:** `data/results/prereg_power_v2.json`  
**Run parameters:** N_SIM=2000 per config (Monte-Carlo se ≤1.1%); dose section 800 sims × 300 conditional-permutation draws (real EXP-DOSE analysis will use 10⁴ permutations; the reduction here affects only the power-estimate error).  
**Inputs:** applicability matrix (n_app=51; sensitivity {39, 45, 51}); v4 development data `sms_track2_v4.json`; Defect4MR v1.0.0 (35 `verified_full` / 20 projects; T1 DETECT 34/34, selection-conditioned).  
**Status:** design recommendations for author at CHECKPOINT 1; final judg­ment lock happens in Task 1.3 (blocked on theory CHECKPOINT T2).

---

## 1. Development-data parameters (Step 1, two anchors)

| Anchor | Split | P(SMS>0 \| aligned) | P(SMS>0 \| cross) | nonzero Beta (aligned) | nonzero Beta (cross) |
|---|---|---|---|---|---|
| **A** (plan-instructed) | PUT × class-primary-MP (12/48 cells) | **0.500** | **0.1875** | MoM Beta(0.844, 1.134), mean 0.427 | Beta(2.140, 3.093), mean 0.409 |
| **B** (pessimistic) | operator × alignment-map (34 op-cells) | **0.118** (nonzero all = 1.0) | 0.324 | degenerate at 1.0 | Beta(2.873, 7.859), mean 0.268 |

**Load-bearing finding:** at the operator level, v4 shows *no* aligned>cross discrimination (anchor B reverses the sign of the zero-part gap). Anchor B is biased against the redesign — v4 MR sets were class-primary-instantiated, never operator-targeted, and per-MP denominators are tiny (~9) — but it defines the honest falsification scenario: if operator-targeted MR generation does not outperform v4's untargeted MRs, H-ZERO and H-DISC *should and will* fail. Simulation scenarios: `S_A` (anchor A), `S_U65`/`S_U80` (theory-success uplift of the aligned zero-part to 0.65/0.80), `S_ADV` (anchor B).

## 2. H-DISC — paired Wilcoxon + r_mp (headline)

Power of the compound criterion (one-sided p<0.05 **and** r_mp ≥ MID), n_app=51:

| Scenario | m=8 | m=12 | m=16 | m=20 | (MID=0.33, s=1) |
|---|---|---|---|---|---|
| S_A anchor | 0.835 | 0.849 | 0.858 | 0.874 | powered at all densities |
| S_U65 | 0.979 | 0.977 | 0.987 | 0.988 | saturating |
| S_U80 | 0.997 | 1.000 | 1.000 | 1.000 | saturated |
| S_ADV | 0.087 | 0.057 | 0.052 | 0.042 | correct failure mode |

MID sensitivity at anchor A (m=16, s=2): power 0.867 (MID 0.30/0.33 nearly identical), 0.810 (MID 0.40); 10th-percentile realized r_mp ≈ 0.32.  
**Recommendation: MID(r_mp) = 0.33** (converted from Cliff's δ medium 0.33; both quantities are P(favorable)−P(unfavorable) contrasts, conversion documented as heuristic anchor, not identity). n_app sensitivity: at n_app=39 the anchor-A power at m=16, MID 0.33 remains ≥0.80.

## 3. H-ZERO — balanced accuracy + McNemar (headline)

Power of (observed BA ≥ 0.75 **and** one-sided exact McNemar vs majority-class p<0.05); n_app=51:

| Scenario | s=1, m=16 | s=1, m=20 | **s=2, m=16** | s=2, m=20 | true-BA at config |
|---|---|---|---|---|---|
| S_A anchor | 0.003 | 0.002 | 0.004 | 0.006 | ≈0.635 — prediction fails, correctly |
| S_U65 | 0.123 | 0.145 | ~0.15 | ~0.17 | ≈0.70 < threshold |
| S_U80 | 0.712 | 0.723 | **0.806** | 0.824 | ≈0.785 |

Reading discipline (anti-over-defence, CLAUDE.md §10): under anchor-A behaviour the H-ZERO prediction is *false* (BA_true≈0.64), and no sample size rescues a false prediction — low "power" there is falsifiability working as intended, not under-powering. Power is therefore assessed at the **design alternative S_U80** (theory-targeted generation lifts the aligned nonzero rate to 0.8, the level THM-GAP/COR-ZERO coverage accounting implies when aligned MR sets actually cover the injected effect layer).

**Recommendation: density m=16, v5 held-out MR sets s=2** → H-ZERO power 0.806 at the design alternative; H-DISC 0.867 at anchor A. The second held-out MR-set replicate is what pushes H-ZERO over 0.8 (it suppresses measurement zeros in the TPR arm); it also strengthens the provider-singularity threat answer.

**Kernel augmentation (Step 3 trigger): NOT triggered** — a KER-12 configuration reaching ≥0.8 for both headline tests exists (m=16, s=2). Conditional sketch if the author judges S_U80 too optimistic as the design alternative: adding 6 compact kernels (+~25 applicable cells → n_app≈76) raises S_U80 H-ZERO power to ≈0.9 but does nothing for the S_A/S_U65 worlds (there the prediction itself is false; BA_true < 0.75). Candidate pool (same float→float, <2KB, class-balanced): A: damped-pendulum ODE (energy decay), tridiagonal Thomas solver, RK4 two-body orbit; B: Gibbs sampler (bivariate normal), bootstrap CI kernel; C: RBF interpolation surrogate; D: Gaussian naive Bayes, decision-stump ensemble. Selection criteria: signature homogeneity (P2), ≥3 applicable operators per kernel by the §3 site rules, no library-internal-only invariants.

## 4. H-CONS — manipulation check, analytic Wilson budget

Criterion: Wilson 95% lower bound of p̂ (share of applicable cells with ≥5 non-equivalent mutants) > 0.5.

| n_app | minimal passing p̂ | Wilson LB at p̂ | CI width at p̂=0.7 |
|---|---|---|---|
| 39 | 0.70 (28/39) | 0.543 | 0.277 |
| 45 | 0.667 (30/45) | 0.520 | 0.259 |
| 51 | 0.65 (34/51) | 0.513 | 0.244 |

Dev anchor: 24/36 attempted-applicable v4 combos reached ≥5 confirmed (p̂_dev≈0.667, at a comparable generation budget: v4 K=20 attempts/cell vs v5 ≈18 attempts at m=16) → gate passes marginally. **Risk concentration: SI (1/6 dev combos ≥5).** The 15 applicable-never-attempted combos (matrix §5) carry the residual generation risk.

## 5. Budget arithmetic table (mandatory)

Density m = confirmed non-equivalent mutants per applicable cell (kill-matrix denominator); attempts ≈ ×1.117 (v4: 333 attempts → 298 confirmed).

| n_app | m | total mutants | in envelope 300–840 | est. LLM generation calls | kill-matrix evaluations (× s=2 MR sets) |
|---|---|---|---|---|---|
| 51 | 8 | 408 | ✓ | ≈457 | 816 mutant-set units |
| 51 | 12 | 612 | ✓ | ≈685 | 1,224 |
| **51** | **16** | **816** | **✓ (≤840)** | **≈914** | **1,632** |
| 51 | 20 | 1,020 | ✗ over envelope | ≈1,142 | 2,040 |

Each mutant-set unit = one mutant × one MR set × K_avp trials (v4 convention: 20 repeats). EXP-DOSE adds ≤960 executions (§7); EXP-FIX adds ≤15 cells × 16 mutants × 1 added MR ≈ 240 incremental kill evaluations.

## 6. External line feasibility (Step 2b)

### 6.1 H-CAL — threshold test infeasible at any realistic configuration

Power of one-sided exact McNemar (our frozen predictions vs majority-class predictor):

| n defects | prevalence 0.6 | 0.7 | 0.8 | 0.9 | (predictor accuracy 0.8) |
|---|---|---|---|---|---|
| 16 | 0.180 | 0.068 | 0.015 | 0.001 | |
| 20 | 0.246 | 0.087 | 0.012 | 0.001 | |
| 24 | 0.308 | 0.126 | 0.016 | 0.001 | |

Even at predictor accuracy 0.9: max 0.658 (n=24, prevalence 0.6); ≤0.37 for prevalence ≥0.7. Root cause: at the DEF-CAL-informed prevalence range (historical selection-conditioned detect rate 34/34; decoupled admission will lower it but plausibly stays ≥0.6), the majority-class baseline is already strong and discordant pairs are few at n≤24.

**Ruling recommendation (R-3 / F-3a path): pre-register H-CAL as interval estimation** — report accuracy with Wilson 95% CI (widths at n=20: 0.27–0.37 across acc 0.7–0.9) plus descriptive per-arm FPR (fixed arm) — instead of the majority-class McNemar threshold test. The McNemar comparison may be retained as a labelled descriptive. Formal lock in Task 1.3 (post-T2).

### 6.2 H-RANK — retain threshold criterion, with project-qualification floor

P(τ̄ ≥ 0.3) by scenario (4 conditions ALN/v5/CRS/RND per project; τ_b vs frozen predicted ranking; fully-tied projects excluded, tie fraction ≤4%):

| n | J | J qualifying | strong | moderate | weak | null (false-pass) |
|---|---|---|---|---|---|---|
| 20 | 6 | 6 | 1.000 | 0.929 | 0.532 | 0.084 |
| 20 | 8 | 4 | 0.996 | 0.865 | 0.529 | 0.140 |
| 24 | 8 | 8 | 1.000 | 0.932 | 0.501 | 0.057 |
| 24 | 10 | 4 | 0.994 | 0.872 | 0.512 | 0.143 |

**Ruling recommendation: retain τ̄ ≥ 0.3 as the pass-line** (moderate-scenario power 0.87–0.93 ≥ 0.8), with an added qualification floor: **≥6 qualifying projects** (each ≥3 ready defects) — at 4 qualifying projects the null false-pass rate reaches 14%, at ≥6 it stays ≤9%. Weak-separation power ~0.5 is boundary behaviour (τ̄_true≈0.3), not under-powering. Mining target: n≥20 ready defects spread so that ≥6 projects hold ≥3 each (n=24 with J=8 is the comfortable configuration).

## 7. EXP-DOSE (Step 2c)

Generative model: logistic kill curve centred at ε_tol (normalised 1.0), slope = window/4 where window = Δ_r+2η̄ — **parameters are theory-derived (THM-WIN family), not fitted to v4 data**; slope scan s/c ∈ {0.05, 0.1, 0.2, 0.4}; dose grid log-spaced ε ∈ [0.25, 4.0]·ε_tol.

| Config (levels × reps × 8 curves) | total execs | per-curve power (worst slope) | ≥6/8 curves | centre-estimate sd (slope 0.2 / 0.4) |
|---|---|---|---|---|
| **6 × 20 × 8** | **960 (= cap)** | 1.000 | 1.000 | 0.067 / 0.159 |
| 8 × 15 × 8 | 960 | 1.000 | 1.000 | 0.094 / 0.158 |
| 6 × 15 × 8 | 720 | 1.000 | 1.000 | 0.079 / 0.183 |
| 6 × 10 × 8 | 480 | 1.000 | 1.000 | 0.108 / 0.220 |

H-DOSE headline power is saturated at every configuration if the theory-derived monotone transition exists in [0.25, 4]·ε_tol; the honest failure modes are a flat/non-monotone realized curve (theory wrong → correct failure) or grid misplacement (centre outside the grid) — mitigated by the F-10 two-axis calibration (nominal + realized ε_m measured by the direct invariant-violation functional).  
**H-DOSE-CTR (B-2) calibration note:** centre-estimation noise (sd ≤ 0.22 at the cheapest config) is small against any plausible window (±4·slope); per-curve containment is ≈1.0 under a correctly-located centre, so the pre-registered "≥6/8 curves contained" criterion bites on *centre mislocation* (theory error), not estimation noise — the desired property.  
**Recommendation: 2 operators (HP, CE) × 4 kernels (A1, B3, C1, D3) × 6 levels × 20 repeats = 960 executions** (cap-compliant, tightest centre estimates for H-DOSE-CTR).

## 8. Secondary-family feasibility notes (B-group)

- **H-XI (B-1) estimability guard:** expected total kills under the recommended config ≈ 816 × 2 × mean-kill ≈ ≥250 even at anchor-A rates ≫ 50 (UNDERPOWERED guard unlikely to trigger; guard retained).
- **H-FIX (B-4) Wilson budget:** criterion LB>0.5 requires 9/10, 10/12, or 12/15 cells transitioning 0→positive. **Recommend sampling 15 cells** (upper end of the pre-registered 10–15): the implied pass bar 12/15 (p̂=0.80) is demanding but achievable if THM-GAP attribution is actionable; at 10 cells the bar (9/10) is near-ceiling and fragile.
- **H-CAL clustered secondary (B-3):** unaffected by §6.1 (it is a separate pooled-conditions bootstrap); no feasibility blocker identified at n≥20.

## 9. Step-3 decision summary (for author at CHECKPOINT 1)

1. **Primary config: n_app=51 · density 16 · two v5 held-out MR sets** (816 mutants, envelope-compliant; H-DISC 0.867 @ anchor A, H-ZERO 0.806 @ design alternative).
2. **MID(r_mp) = 0.33** (lock in Task 1.3).
3. **Kernel augmentation not triggered**; conditional candidate sketch in §3.
4. **H-CAL → interval estimation** (threshold test infeasible: max power 0.31 at acc 0.8, 0.66 at acc 0.9); **H-RANK → retain τ̄≥0.3** with ≥6-qualifying-projects floor (null false-pass ≤9%).
5. **EXP-DOSE: 6×20×8 = 960 executions**; H-DOSE-CTR criterion (≥6/8) confirmed to test location, not noise.
6. **EXP-FIX: sample 15 cells** (pass bar 12/15).
7. All locks above are recommendations until Task 1.3 freezes them (blocked on theory CHECKPOINT T2); any post-freeze change goes through `AMENDMENTS.md` (F-7).
