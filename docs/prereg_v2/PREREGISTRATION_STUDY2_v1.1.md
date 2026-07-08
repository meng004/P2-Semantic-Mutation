# Pre-Registration — Study 2 (Confirmatory) — AMENDMENT v1.1

**Paper**: *When Same-Prompt LLM Source Diversity Doesn't Help — Semantic
Mutation Operator Ablation in Metamorphic Testing for Single-Output Scientific
Computing Kernels* (P2/P3, IST/TOSEM two-study architecture).

**This document supersedes** `PREREGISTRATION_STUDY2.md` (v1.0, registration
commit `072a015`). v1.0 was frozen but **not yet Zenodo-minted**, and **no
Study-2 mutant, dual-blind review, or industrial candidate verification has been
run** (verified: no `data/mutants/{a4..d8}_pool_*` dirs, no `*_v5` SSOT,
`cache_cross/` holds only the Study-1 pilot `_log.json`). Amending a versioned,
un-minted, pre-data registration is standard registered-science practice. This
amendment **strengthens** v1.0's integrity machinery and weakens none of it: the
deterministic primary-MP rule (§4), the dual-blind blinding + role rotation (§5),
the Tier-A/Tier-B industrial firewall (§6), the LRCA measurement (§H4'), and the
one-shot confirmatory rule (§5c) are all retained verbatim or tightened.

**Status**: FROZEN before any Study-2 data generation. The frozen artefacts are
this file + `scripts/power_analysis_study2.py` (v1.0 power SSOT
`data/results/power_study2.json`) + `scripts/power_analysis_v11.py` (v1.1
feasibility SSOT `data/results/power_study2_v11.json`). Master seed `20260708`
(v1.1 keeps the v1.0 freeze-date seed convention). Any change after this freeze
is a logged, dated entry in §10, not an edit to the frozen body.

---

## 0. Amendment record (v1.0 → v1.1)

### 0.1 Pre-data attestation

> **This amendment was drafted and frozen before any Study-2 data generation.
> No Study-2 outcome — no mutant, no SMS cell, no dual-blind review label, no
> industrial per-case kill — was visible to the authors of this amendment.**
> Verification performed at drafting (2026-07-08): (i) no `data/mutants/`
> directory exists for any new PUT `a4..d8`; (ii) no Study-2 SSOT
> (`sms_track2_v5.json`, `rq2_cliffs_delta_v5.json`,
> `dualblind_delta_delta_v5.json`, `industrial_percase_v2.json`) exists; (iii)
> `data/operator_campaign/cache_cross/` contains only the Study-1 six-operator
> pilot log. Every threshold registered below traces to a Study-1 SSOT
> (`sms_track2_v4.json`, `s5_purity_v4.json`, `industrial_percase_v1.json`) or to
> the blind-authored operator registry (`operator_registry.py`), never to a
> Study-2 outcome. Operator→PUT coverage is a property of the spec, authored
> blind to mutation results (`PUT_EXPANSION_ROSTER.md` integrity constraint), so
> using it to set the H1' bar introduces no selection on the response.

### 0.2 Diff table (every changed / added clause, one row each)

| # | Clause | v1.0 | v1.1 | Justification |
|---|---|---|---|---|
| D1 | §0 amendment record | — (absent) | this §0: diff table + pre-data attestation | registered-science requires a disclosed, versioned amendment trail |
| D2 | Freeze provenance | power SSOT = `power_study2.json` | adds `power_study2_v11.json` (seed 20260708, `n_sim=20000`) | successor-hypothesis feasibility numbers need their own committed SSOT |
| D3 | Confirmatory grid n (§2) | **30 PUTs** | **28 PUTs** (30 − 2 calibration-pilot) | pilot subset carved out for pipeline debugging (D4); confirmatory analyses exclude it |
| D4 | Calibration pilot (new §2b) | — | 2-PUT pilot `{a2, b4}`; outcomes visible for debugging; excluded from all confirmatory analyses; may fix code defects only | pipeline needs a live-outcome debug loop that cannot touch thresholds/estimands |
| D5 | Confirmatory roster (new §2c) | "30 PUTs, 7–8/class" | **28 PUTs** listed by ID; class balance A7/B6/C7/D8 | finalize the exact confirmatory set after pilot removal |
| D6 | H2-1 → **H2-1'** (§3) | δ>0 at n=30, power 0.9445 | δ>0 at **n=28**, power **0.9285** (`v11::sms…delta_ref_0.0[28]`) | pilot removal lowers n; leg stays powered ≥0.8, disclosed honestly |
| D7 | **H1'** instantiability (new; supersedes H2-5 †) (§3) | H2-5: ≥4/5 ops, ≥5 mutants, ≥23/30 PUTs (0.75·30, uniform-applicability bar) | ≥4 of 5 families produce ≥5 non-equiv mutants on **≥8 of 28** PUTs; feasibility **0.843** (`v11::h1_instantiability`) | Study-1 refuted the uniform-applicability bar (H1 not met: only HP cleared); re-derive from actual outcome-independent coverage |
| D8 | **H3'** class-consistency (new; supersedes H2-6) (§3) | H2-6: within-class sign 4/4 + Friedman (exploratory) | ≥3 of 4 classes show positive aligned>cross direction; power **0.949** (`v11::h3_class_consistency`) | 4/4 significant per-class sign tests are unpowered at 6–8 PUTs/class; register the powered ≥3/4 direction criterion |
| D9 | **H4'** attribution (new; supersedes H2-7) (§3) | H2-7: mean suspect_share ≤ **0.20** over 150 cells | mean suspect_share ≤ **0.05** over **140** cells (28×5), margin 0.037 (`v11::h4_attribution`) | single-stratum spec constraint pushes CF/TF leakage to the CE/OS/HP/SI regime (0/229 → rule-of-three 0.013); tighten the bar |
| D10 | H2-2 gating (§3, §5b) | confirmatory single test (Family B) | **registered but gated**: executable only with cross-vendor credentials; if unavailable at freeze → **reported not-run (no substitution)** | the harness is same-vendor (single LLM family); a cross-vendor dual-blind cannot be instantiated by it |
| D11 | Harness instantiation (new §5b) | "generator model family / reviewer of a different family" (vendor-agnostic) | discloses Claude-Code Agent harness: Opus-tier generator, role-isolated Claude reviewers on blinded packets, third-instance arbiter; **same-vendor**; model tier recorded in campaign SSOT | honest disclosure of the actual instantiation and its single-vendor limit |
| D12 | One-shot rule (new §5c, promoted) | dispersed in §4b/§5/§7 | consolidated prominent clause: one confirmatory generation per registered budget; regeneration / cell cherry-pick / post-outcome threshold move = protocol violation reported as such | make the anti-p-hacking guarantee unmissable |
| D13 | Analysis-script contracts (§7) | `compute_dualblind_delta.py`, `compute_industrial_stats.py` pre-frozen | adds required contracts for `compute_h1_instantiability.py`, `compute_h3_class_consistency.py`, `compute_h4_attribution.py` (sibling pre-freezes before generation) | H1'/H3'/H4' need pre-frozen scorers, same gold-standard ordering |
| D14 | Family map (§7) | E = H2-5 (†), H2-7 (descriptive) | E = **H1' (feasibility-bounded), H3' (powered), H4' (projection-bounded)**; H2-6 Friedman stays exploratory (X) | reflect the superseded successors; correction structure unchanged |
| D15 | §10 amendments log | empty | records this amendment as entry #1, dated 2026-07-08 | append-only provenance |

Fifteen rows (D1–D15). Attestation applies to **every** row: *amended before any
Study-2 data generation; no Study-2 outcome was visible to the authors of this
amendment.*

---

## 1. Confirmatory research questions

Unchanged from v1.0:

- **RQ-S2a (aligned/cross magnitude).** On the confirmatory PUT grid, does the
  operator-MP aligned slice (j=k) stochastically dominate the cross slice (j≠k)?
- **RQ-S2b (source diversity, dual-blind).** Under one identical dual-blind
  protocol on a same-source and a cross-source arm, does cross-source pooling
  move Δδ? *(v1.1: testable only if cross-**vendor** credentials exist — §5b.)*
- **RQ-S2c (industrial construct separation).** On a pre-frozen census of
  reproduced library defects, does the pattern-derived relation dominate
  generic baselines in mutation-phase kills and real-defect incidence?

Elevated in v1.1 from naive carry-forward to powered/feasibility-bounded
successors: **H1'** operator instantiability, **H3'** cross-class direction
consistency, **H4'** attribution purity (§3).

---

## 2. Registered sample sizes (traceable to power SSOTs)

| Arm | Registered n | Powered target | Achieved power | JSON trace |
|---|---|---|---|---|
| PUT grid (SMS), **confirmatory** | **28 PUTs** (30 − 2 pilot); n_aligned=28, n_cross=112 | δ>0 one-sided | **0.9285** | `power_study2_v11.json::sms…delta_ref_0.0[28]` |
| Dual-blind Δδ *(gated, §5b)* | 28 PUTs paired | Δδ=0.20 two-sided | **0.793** @28 | `power_study2_v11.json::sms…dd_0.2[28]` |
| Industrial (Tier A) | **≥35 verified_full** (+`N_rescued`); 45 only if reachable | T1>B1 one-sided Wilcoxon | 0.74 @35 · 0.83 @45 | `power_study2.json::c.wilcoxon_power` |

**n note (amended).** Removing the two calibration-pilot PUTs (§2b) drops the
confirmatory grid 30→28. The magnitude leg **H2-1'** (δ>0) is robust to this:
power 0.9285 at n=28 vs 0.9445 at n=30. The dual-blind Δδ=0.20 leg falls to
**0.793** at n=28 (from 0.824 at n=30) — marginally below the 0.80 target. This
is disclosed honestly, but is **moot under the same-vendor freeze**: H2-2 is
gated not-run unless cross-vendor credentials are supplied (§5b); if they are, the
paired grid can be restored toward n=30 by promoting pilot PUTs only *before* any
confirmatory generation (never after). The industrial arm is unchanged from v1.0.

### 2b. Calibration pilot (new; amendment item 2)

A **2-PUT calibration pilot** `{a2, b4}` is declared for pipeline debugging with
**outcomes visible**.

- **Pick rationale (machinery-representative).** `a2` (LU determinant) is the
  canonical original PUT and the established dry-run anchor
  (`CAMPAIGN_RUNBOOK.md §5`); it exercises the original-12 path, the OS
  prod→sum key operator, and a deterministic kernel. `b4` (bootstrap resampling)
  is a *new* PUT: it stresses the new-PUT module loader, a freshly authored MR
  set, a new operator triple (OS/CE/**TF**), and — being a seeded stochastic
  estimator — the harness's seed-determinism. Together they span
  original-vs-new, deterministic-vs-stochastic, two design classes (A, B), and
  include a **TF** operator so the single-stratum-spec constraint (H4') can be
  debugged on a leakage-relevant family.
- **Firewall.** The pilot is **excluded from every confirmatory analysis**
  (H2-1', H2-2, H1', H3', H4', and all industrial legs). Pilot outcomes may fix
  **code defects only** (harness bugs, fence-stripping, review-packet blinding,
  determinism) — **never** thresholds, estimands, DGP calibration, primary-MP
  assignment, or the roster. Any pilot-triggered change is logged in the §10
  amendment appendix **before** the confirmatory run begins.

### 2c. Confirmatory roster finalized — 28 PUTs (new; amendment item 3)

The 28 confirmatory PUTs = 30 − pilot `{a2, b4}`, class balance **7/6/7/8**:

| Class | Confirmatory PUTs | n |
|---|---|---|
| A — numeric | a1, a3, a4, a5, a6, a7, a8 | 7 |
| B — probabilistic | b1, b2, b3, b5, b6, b7 | 6 |
| C — surrogate | c1, c2, c3, c4, c5, c6, c7 | 7 |
| D — ML | d1, d2, d3, d4, d5, d6, d7, d8 | 8 |
| **Total** | | **28** |

Diversity rationale imported from `PUT_EXPANSION_ROSTER.md §5`: A spans
quadrature / spline / root-finding / linear-solve / RK4; B spans bootstrap /
rejection / inverse-transform / importance sampling; C spans kNN / RF / RBF /
SVR surrogates; D spans generative (GaussianNB) / discriminant (LDA, QDA) /
SGD-linear / kernel-Bayesian (GPC) classifiers. Each PUT keeps
`program(x: float) -> float`, x∈[0,1], deterministic (seeds fixed at load).

---

## 3. Confirmatory hypotheses

Format unchanged: statistic · threshold (power/feasibility justification) · test ·
α · family · decision rule · licensed verdict.

### H2-1' — Aligned slice dominates cross slice (RQ-S2a), pilot-adjusted
- **Statistic**: Cliff's δ between aligned (j=k, n=28) and cross (j≠k, n=112)
  SMS cells under the §4 primary-MP rule.
- **Threshold**: δ > 0 (one-sided stochastic dominance). **Power**: the
  Study-1-calibrated DGP has true δ≈0.32 (`power_study2.json::a.true_delta_dgp`);
  δ>0 reaches **0.9285** at n=28
  (`power_study2_v11.json::sms…power_by_threshold.delta_ref_0.0[28]`). δ≥0.147
  (0.49) and δ≥0.33 (~0.04) remain unpowered and are **not** registered as
  pass/fail (Study-1 error not repeated).
- **Test**: two-sample Cliff's δ, one-sided 95% percentile-bootstrap lower bound
  (multinomial two-sample bootstrap, B=10,000, seed 20260708) must exceed 0.
- **α**: 0.05, one-sided. **Family**: A (single test). Same-vendor testable.
- **Decision**: lower bound > 0 → confirm aligned dominates cross.
- **Licensed verdict**: directional construct claim, not a large-effect claim.
  Romano (2006) bands reported descriptively only (§7).

### H2-2 — Source-diversity effect (RQ-S2b) — REGISTERED BUT GATED
- **Statistic**: Δδ = δ(cross-source) − δ(same-source), paired on the 28 PUTs
  under the identical dual-blind protocol of §5.
- **Threshold**: |Δδ| ≥ 0.20 detectable; paired SE at n=28 = 0.072
  (`power_study2_v11.json::sms…paired_se_by_n[28]`), power **0.793** — marginal.
- **GATE (amendment item 4).** H2-2 is a **cross-vendor dual-blind** contrast.
  The Study-2 harness is **same-vendor** (single LLM family; §5b), so this arm
  **cannot instantiate** the cross-vendor comparison. H2-2 therefore stays
  **registered but gated**: *"executable only when cross-vendor credentials are
  available at generation freeze; if unavailable, reported as **not-run** — no
  substitution of a same-vendor proxy for a cross-vendor arm."* The same-vendor
  arm reports H2-1', H1', H3', H4' only.
- **Test / decision (if ungated)**: paired-role bootstrap 95% two-sided CI
  (B=10,000, seed 20260708); CI excludes 0 → confirm; CI includes 0 with
  half-width ≤ 0.14 → bounded null; else under-recruited. α 0.05, two-sided.
  Family B (single test).
- **Licensed verdict**: unchanged from v1.0 when executable; when not-run, the
  paper reports the same-vendor δ (H2-1') and states the cross-vendor question
  as open, not as a null.

### H1' — Operator instantiability (RQ3 successor; supersedes H2-5)
- **Statistic**: per operator family, the count of confirmatory PUTs (of 28) on
  which the family produces ≥5 non-equivalent (confirmed) mutants.
- **Coverage ceiling (outcome-independent, from `operator_registry.py`)**: over
  the 28 confirmatory PUTs, family→#applicable-PUTs is
  **CE 23, OS 14, HP 21, TF 15, SI 10**
  (`power_study2_v11.json::h1_instantiability.coverage_ceiling_confirmatory28`).
  A family cannot instantiate on a PUT with no spec for it, so these are hard
  ceilings; the original-12 sub-counts (CE 8, OS 7, HP 9, TF 6, SI 6) reproduce
  `main.tex` Table `tab:p2-32` exactly, validating the parse.
- **Threshold (same shape as Study-1 H1)**: **≥4 of 5 operator families produce
  ≥5 non-equivalent mutants on ≥8 of the 28 confirmatory PUTs.** **Feasibility
  0.843** (`h1_instantiability.registered_feasibility`) under a Monte-Carlo DGP
  in which each applicable PUT clears the ≥5-mutant bar with the
  Study-1-calibrated per-applicable success rate (main.tex L2063: CE 4/8, OS 5/7,
  HP 9/9, TF 5/6, SI 1/6; Jeffreys-shrunk to avoid a degenerate HP=1). Expected
  PUTs cleared per family: **HP 19.95, TF 11.79, CE 11.5, OS 9.63, SI 2.14**.
  M=8 is the **largest** bar with feasibility ≥0.80 (M=9 → 0.654), so it is
  registered with the headroom the data support (OS, the tightest of the four
  clearing families, expects 9.63 vs the 8 bar).
- **Justification for relaxing the Study-1 0.75 bar**: Study-1 H1 was **not met**
  precisely because the ≥9/12 (0.75) bar assumed uniform operator applicability,
  which class-targeted operators refute (`main.tex` L2052–2057). H1' re-derives
  the bar from actual, blind-authored coverage; SI (narrow, high-risk; Study-1
  1/6) is **expected to stay below** the bar, so the criterion is a genuine test
  (feasibility 0.84, not ~1.0), not a rubber stamp. This calibrates to reality;
  it does not weaken integrity (coverage is outcome-independent).
- **Test**: deterministic count on the frozen pool; feasibility-bounded, not a
  sampling test. **α**: n/a (exact count). **Family**: E. **Decision**: ≥4 of 5
  families clear ≥8/28 → confirm operator adequacy on the confirmatory grid;
  else report the achieved per-family counts factually (Study-1 honesty norm).

### H3' — Cross-class direction consistency (RQ5 successor; supersedes H2-6)
- **Statistic**: per design class, the sign of (class-mean aligned SMS −
  class-mean cross SMS) over the class's confirmatory PUTs (A7/B6/C7/D8).
- **Threshold / power**: **positive direction (aligned > cross) in ≥3 of the 4
  classes.** Simulated power **0.949**
  (`power_study2_v11.json::h3_class_consistency.power_P_ge3of4_positive`) under
  the Study-1-calibrated hurdle DGP (per PUT: aligned cell ~ hurdle(0.5,
  aligned-mags); cross representative = mean of 4 hurdle(0.1875, cross-mags)
  cells). P(4/4)=0.661.
- **Why not per-class significance**: per-class one-sided binomial sign tests are
  **underpowered** at 6–8 PUTs/class with heavy SMS ties — simulated per-class
  power ≈ 0.05–0.06 (`h3_class_consistency.per_class_signtest_power`). Registering
  4/4 significant sign tests (v1.0-implied) would repeat the Study-1
  under-powering. The ≥3/4 *direction* criterion is the achievable, powered test.
- **Test**: class-mean sign over the frozen SMS pool; per-class binomial sign-test
  p-values reported **descriptively**; Friedman χ² across MPs stays **exploratory**
  (Family X), exactly as Study-1. **α**: 0.05 (descriptive companions).
  **Family**: E (the ≥3/4 direction criterion). **Decision**: ≥3/4 classes
  positive → confirm cross-class consistency; else report factually.

### H4' — Attribution purity under the single-stratum spec constraint (RQ4 successor; supersedes H2-7)
- **Statistic**: mean `suspect_share` (LRCA multi-stratum leakage fraction) over
  the **140** confirmatory cells (28 PUTs × 5 MP). **LRCA machinery is identical
  to Study 1** — no measurement change is introduced post-data or pre-data.
- **Expected post-constraint leakage**: in Study 1
  (`s5_purity_v4.json`), **29/292** mutants were multi-stratum (0.0993), and
  **all 29 came from CF (9) + TF (20)**
  (`power_study2_v11.json::h4_attribution.study1_multistratum_by_family`). The
  already-single-stratum families **CE/OS/HP/SI show 0/229** incidental
  multi-stratum leakage. Under the **single-stratum spec constraint** (a sibling
  agent re-specs CF/TF so each flips exactly one stratum — referenced here as an
  amendment item, implemented before generation), CF/TF residual incidental
  leakage is projected to the single-stratum-family regime, whose one-sided 95%
  upper bound is the **rule-of-three 3/229 = 0.0131**.
- **Threshold**: **mean suspect_share ≤ 0.05** across the 140 cells — a **margin
  of 0.037** above the projected 0.0131 upper bound
  (`h4_attribution.margin_above_projected_upper`), and **tighter** than
  Study-1's 0.20 because the constraint removes the by-construction CF/TF
  contamination.
- **Test**: descriptive mean on the frozen pool; no independence assumed.
  **α**: n/a. **Family**: E. **Decision**: mean ≤ 0.05 → confirm attribution
  purity; else report the observed leakage and the offending families factually.

### H2-3, H2-4 (industrial) — unchanged from v1.0
Carried forward verbatim (§6, Families C and D). This amendment does not touch
the industrial legs, the two-tier census, the Tier-A/B firewall, or the
`N_rescued` protocol variable. H2-3a magnitude keeps its under-recruitment
fallback; H2-4 Fisher incidence keeps power 1.00.

---

## 4. Primary meta-pattern selection rule — UNCHANGED from v1.0

The deterministic, taxonomy-indexed, data-independent rule (A→MP1, B→MP2,
C→MP5-held, D→MP2) is retained exactly. The Study-1 v3b MP5→MP1
selection-on-response is prohibited. New PUTs inherit their class primary MP at
authoring. Run with `P2_PRIMARY_VERSION=v3`; the `v3b` path is not invoked. PUT
class-assignment is frozen at authoring, blind to mutation results
(`PUT_EXPANSION_ROSTER.md`, `PUT_EXPANSION_IMPLEMENTATION.md`).

---

## 5. Dual-blind protocol (both arms, identical) — UNCHANGED core + §5b, §5c added

The v1.0 §5 pipeline is retained: generation → **blind review** (reviewer sees
only mutant code + operator spec + PUT source; generator identity, arm label, and
SMS withheld) → **arbitration** on disagreement → **freeze then score** (SMS
computed only after review labels are frozen and committed). Model-family/instance
rotation guarantees generator ≠ reviewer ≠ arbiter on every item. Analyst
blindness preserved.

### 5b. Harness instantiation disclosure (new; amendment item 4)

Study-2 generation and review run through the **Claude Code Agent harness**:

- **Generator role**: Claude **Opus-tier** agents.
- **Reviewer roles**: **separately-spawned, role-isolated** Claude agent
  instances that receive **BLINDED packets** — no generator identity, no arm
  label, no SMS / kill outcome.
- **Arbitration**: a **third** separately-spawned Claude instance on the same
  blinded packet.
- **Honest limitation**: this is a **same-vendor (single-LLM-family)**
  instantiation. Role isolation and packet blinding are enforced across
  *instances*, but all instances share one model family. Therefore the
  **cross-vendor** dual-blind hypothesis **H2-2 cannot be tested by this arm** —
  it is gated not-run unless cross-vendor credentials are supplied (§3, H2-2).
  The same-vendor arm tests **H2-1', H1', H3', H4'** only.
- **SSOT record**: the **exact agent-tier model name at generation time** (e.g.
  the resolved Opus model id) is recorded in the campaign SSOT
  (`data/operator_campaign/…_log.json`) at run time; it is not fixed in this
  registration because the harness resolves it at generation.

### 5c. One-shot confirmatory rule (new, promoted; amendment item 5)

**Confirmatory generation runs ONCE per the registered budget** — the mutant-count
targets per cell, seeds (20260708), and prompt-template version pinned by file
hash. **Regeneration, cherry-picking cells, or moving any threshold after ANY
confirmatory outcome is visible is a protocol violation that must be reported as
such** in §10 and in the paper. Confirmatory analysis runs **only** through the
pre-frozen scripts (§7). The calibration pilot (§2b) is the *only* place
live outcomes are seen before the confirmatory freeze, and it may fix code
defects only.

---

## 6. Industrial corpus census protocol — UNCHANGED from v1.0

Two-tier census with firewall retained verbatim: Tier A (`verified_full`, public
upstream fix) is the only tier in the primary estimand (H2-3, H2-4); Tier B
(reproduced-but-unfixed, local-patch fixed arm) is sensitivity-only, never
relabeled verified. Verification blindness, inclusion criteria (1)–(6),
`N_rescued` as a freeze-time protocol variable, E-PETSC-004 completion, the
honest under-recruitment fallback, and the frozen SSOT
`industrial_percase_v2.json` are all unchanged.

---

## 7. Analysis plan — SSOT paths + one-shot scripts + §7b contracts

**SSOT paths (Study 2)**: `sms_track2_v5.json`, `rq2_cliffs_delta_v5.json`,
`dualblind_delta_delta_v5.json`, `industrial_percase_v2.json`,
`industrial_stats_v2.json`; power references `power_study2.json` (v1.0) **and
`power_study2_v11.json` (v1.1)**.

**Pre-frozen scripts** (frozen before any Study-2 data; each carries the
"pre-frozen / post-data change = disclosed deviation" header):
`scripts/compute_dualblind_delta.py`, `scripts/compute_industrial_stats.py`,
`scripts/compute_h2_incidence.py`.

### 7b. New analysis-script contracts for H1'/H3'/H4' (amendment item 5)

These MUST be pre-frozen by a sibling **before generation**, covered by
offline synthetic-fixture tests in `tests/analysis/`, and each prints the
registered licensed verdict (not just numbers):

- **`compute_h1_instantiability.py`** — input: the frozen validated pool
  (`sms_track2_v5.json` + the per-cell equivalence/dedup ledger). Output: per
  family (CE, OS, HP, TF, SI) the count of the 28 confirmatory PUTs with ≥5
  non-equivalent mutants; verdict = (≥4 of 5 families clear ≥8/28). Pilots `a2`,
  `b4` excluded. Emits `data/results/h1_instantiability_v5.json`.
- **`compute_h3_class_consistency.py`** — input: `rq2_cliffs_delta_v5.json` /
  the per-cell SMS pool. Output: per-class (A,B,C,D) sign of class-mean
  (aligned − cross); verdict = (≥3 of 4 classes positive); plus per-class binomial
  sign-test p (descriptive) and Friedman χ² (exploratory). Emits
  `data/results/h3_class_consistency_v5.json`.
- **`compute_h4_attribution.py`** — input: the Study-2 LRCA per-mutant
  classification (identical LRCA machinery to `s5_purity_v4` scoring). Output:
  mean suspect_share over the 140 confirmatory cells + per-family multi-stratum
  breakdown; verdict = (mean ≤ 0.05). Emits `data/results/s5_purity_v5.json`.

**Seeds**: all bootstrap/permutation at 20260708. **Exclusion rules**
(analysis-time): unchanged from v1.0 (vacant cells excluded from δ; all-dead PUTs
retained as zeros; live-only pools exploratory only).

**Multiplicity — one family map for the whole of Study 2 (amended row E)**

| Family | Members | Correction | Confirmatory? |
|---|---|---|---|
| A — SMS magnitude | H2-1' (δ>0, n=28) | single test | yes |
| B — Source diversity | H2-2 (Δδ) | single test | **yes, but gated (not-run if same-vendor freeze)** |
| C — Industrial mutation-phase | H2-3a/b/c Wilcoxon | Holm (3) | yes |
| D — Industrial incidence | H2-4 Fisher | single, outside C | yes |
| E — Successor pool verdicts | **H1' (feasibility 0.843), H3' (power 0.949), H4' (≤0.05 projection)** | none (count / direction / descriptive) | verdict-factual |
| X — Exploratory | H2-6-style Friedman, Romano bands, coverage ρ/τ, LRCA detail, live-only/vacant sensitivities | per-test as labeled | no |

No study-wide cross-family correction (per-family control under
pre-registration), stated not "corrected." Confirmatory ↔ exploratory bright line
unchanged: anything discovered after freeze is exploratory by definition.

---

## 8. Decision matrix — v1.0 rows retained; successor rows added

| Hypothesis | Confirm licenses | Non-confirm licenses |
|---|---|---|
| H2-1' | "aligned slice dominates cross" (directional) | no directional claim on this pool |
| H2-2 | "cross-source pooling moves δ ≥0.20" | bounded null / **or not-run** (same-vendor freeze) → cross-vendor question stated open, not null |
| H1' | "operators adequately instantiate (≥4/5 families ≥8/28)" | achieved per-family counts stated factually |
| H3' | "aligned>cross direction consistent (≥3/4 classes)" | direction not consistent, stated factually |
| H4' | "attribution pure (mean suspect_share ≤0.05) under single-stratum spec" | observed leakage + offending families stated factually |
| H2-3/H2-4 | unchanged from v1.0 | unchanged from v1.0 |

**What would count against the construct (registered a priori)**: (i) aligned δ
CI crossing 0 at n=28 despite 0.93 power; (ii) H3' direction reversing in ≥2
classes; (iii) H4' leakage exceeding 0.05 despite the single-stratum spec; (iv)
H1' fewer than 4 families clearing 8/28; (v) reviewer arbitration failing audit.

---

## 9. Deviations-from-Study-1 lessons table — v1.0 rows retained

The v1.0 L1–L9 closure table is retained. v1.1 adds:

| # | Study-1 lesson | Study-2 v1.1 closure | Trace |
|---|---|---|---|
| L10 | H1 uniform-applicability bar (0.75) unmet because operators are class-targeted | H1' bar re-derived from outcome-independent operator coverage; feasibility 0.843; SI still expected to fail | `v11::h1_instantiability` |
| L11 | H3 per-class sign test underpowered at small class n | H3' registers the powered ≥3/4 *direction* criterion (0.949); per-class tests demoted to descriptive | `v11::h3_class_consistency` |
| L12 | H4 leakage dominated by CF/TF (29/29 multi-stratum) | single-stratum spec constraint + tighter 0.05 bar with 0.037 margin | `v11::h4_attribution` |
| L13 | Cross-source vs cross-vendor conflation risk | H2-2 gated: same-vendor harness cannot test cross-vendor; not-run, no substitution | §5b |

---

## 10. Amendments log (append-only, dated)

**Amendment #1 — 2026-07-08 (this document, v1.0 → v1.1).** Added three powered/
feasibility-bounded successor hypotheses (H1', H3', H4') superseding the naive
carry-forwards H2-5/6/7; declared a 2-PUT calibration pilot `{a2, b4}` (code
fixes only, excluded from confirmatory); finalized the 28-PUT confirmatory roster
(A7/B6/C7/D8); disclosed the same-vendor Claude-Code Agent harness and gated H2-2
as cross-vendor not-run; promoted a prominent one-shot rule; specified pre-freeze
contracts for the three new analysis scripts. All changes pre-data; no Study-2
outcome was visible (see §0.1). Power/feasibility SSOT:
`data/results/power_study2_v11.json` (seed 20260708). Frozen body of v1.0 is not
edited; this file is the amended registration of record.

*(No further amendments. Any post-freeze change — a pilot-triggered code fix, a
candidate that failed reproduction, a seed correction — is appended here with
date and rationale before the confirmatory run.)*
