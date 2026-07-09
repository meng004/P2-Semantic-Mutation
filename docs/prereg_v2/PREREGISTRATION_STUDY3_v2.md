# Pre-Registration — Study 3 (Confirmatory) — v2.0

**Paper**: *When Same-Prompt LLM Source Diversity Doesn't Help — Semantic
Mutation Operator Ablation in Metamorphic Testing for Single-Output Scientific
Computing Kernels* (P2/P3, IST/TOSEM two-study architecture).

**This document is a NEW confirmatory registration** in the lineage
`PREREGISTRATION_STUDY2.md` (v1.0, commit `072a015`) →
`PREREGISTRATION_STUDY2_v1.1.md` (v1.1, 2026-07-08) → **this v2.0 (Study 3)**. It
does **not** amend or re-open the frozen Study-2 registration; Study 2 is closed
and its confirmatory verdicts (including the `H4' = NOT_CONFIRMED`, mean
`suspect_share` 0.1714) stand FROZEN and UNCHANGED. Study 3 re-registers **only**
the attribution construct, in response to the post-hoc H4' leakage diagnosis
(`docs/prereg_v2/H4_DIAGNOSIS.md`; `data/results/h4_leakage_diagnosis_v5.json`,
commit `e319ab8`), on **fresh data that does not yet exist**.

**Status**: FROZEN before any **Study-3** data generation. Frozen apparatus:
this file + `scripts/power_analysis_study3.py` (power/feasibility SSOT
`data/results/power_study3.json`) + the P8-remediated screen
(`src/p2/mutators/stratum_filter.py`, all-family scope) + the pre-freeze
contract for `scripts/compute_h4_graded.py` (§7b). Master seed `20260708`
(freeze-date seed convention retained). Any change after this freeze is a logged,
dated entry in §10, not an edit to the frozen body.

---

## 0. Amendment record (lineage v1.0 → v1.1 → v2.0)

### 0.1 Pre-data attestation (Study-3 data specifically)

> **This registration was drafted and frozen before any STUDY-3 data
> generation. No Study-3 mutant, SMS cell, LRCA classification, dual-blind
> label, or graded-attribution outcome exists or was visible to the authors of
> this registration.** Study 3 is a **full 28-PUT regeneration** (§2c): fresh
> mutants, fresh seeds, a fresh validated pool. Verification performed at
> drafting (2026-07-09): no `data/mutants/*_study3_*` or `*_v6` pool exists; no
> Study-3 SSOT (`sms_track2_v6.json`, `h4_graded_v6.json`, `s5_purity_v6.json`)
> exists.
>
> **Study-2 (v5) data IS seen, and is used for ONE purpose only — design
> calibration — stated openly.** The v5 leakage distribution
> (`sms_track2_v5.json`, `h4_leakage_diagnosis_v5.json`) is the prior study from
> which the graded-attribution DGP and thresholds are derived
> (`power_study3.json`), exactly as Study-2 calibrated its thresholds from the
> Study-1 v4 pool. This is **design-from-prior-study**, the standard registered-
> science practice; it is not selection on the Study-3 response, because no
> Study-3 response exists. The confirmatory verdict is computed on the fresh
> Study-3 pool through the pre-frozen scorer (§7b), never on v5.

### 0.2 Diff table (Study-3 additions over the frozen Study-2 v1.1)

| # | Clause | Study-2 v1.1 | Study-3 v2.0 | Justification |
|---|---|---|---|---|
| S1 | Attribution hypothesis | **H4'** single-valued purity: mean `suspect_share` ≤ 0.05 over 140 cells | **superseded** by H4''-graded + H4''-strict (§3) | v5 diagnosis: leakage is REAL construct-level coupling (B=117/117), not measurement noise; a single-valued σ is the wrong model for rich PUTs (`H4_DIAGNOSIS.md` §6) |
| S2 | Screen wiring | CF/TF screen (`_OPID_CAT_RE`), silently no-op on v5 (incident P8) | **P8-remediated**: op_id parser fixed, all-family scope, loud-fail on null category (§4b) | the v5 screen never ran (regex rejected the source suffix) and never targeted OS/SI; forward-looking fix, alters NO committed v5 artefact |
| S3 | Graded DGP + power | — | `power_study3.json` (seed 20260708) calibrated from the v5 rich-class share distribution | the graded threshold must trace to a committed power SSOT |
| S4 | Analysis contract | `compute_h4_attribution.py` (purity) | adds `compute_h4_graded.py` (graded) + reuses fixed `stratum_filter.audit_matrix` for strict (§7b) | pre-frozen scorer for the new estimand |
| S5 | Scope | 28-PUT confirmatory reuse of v5 pool | **full 28-PUT regeneration** (fresh mutants/seeds) — §2c | a hypothesis about attribution formed after seeing v5 cannot be confirmed on v5 |
| S6 | H1'/H3' | registered (feasibility/direction) | **NOT re-registered** (§3.3) — Study-2 already confirmed them; avoid needless multiplicity | H1'/H3' verdicts are settled; re-testing on fresh data adds multiplicity without a new question |
| S7 | H2-1' magnitude | registered, confirmed | **NOT re-registered** as confirmatory; re-run descriptively only | the aligned>cross magnitude claim is closed by Study 2 |
| S8 | Registered smoke assertion | — | the wired all-family screen MUST match >0 candidates or the campaign fails loudly (§3 H4''-strict, §5c) | never again a silent no-op (incident P8) |

Attestation applies to **every** row: *frozen before any Study-3 data
generation; no Study-3 outcome was visible; Study-2 data used for calibration
only.*

---

## 1. Confirmatory research question (single, focused)

- **RQ-S3 (attribution structure).** On structurally rich PUT classes
  (surrogate-regression C and ML-classifier D), where a single semantic fault
  *inherently* perturbs multiple invariant strata, is the detected mutant's kill
  signal still **substantially attributed to the declared MetaPattern** (a
  *graded* attribution), and — separately — on the families where coupling is
  **absent** (CE, HP) or **stable and screenable** (CF), does the **single-
  stratum purity** premise hold once the P8-fixed all-family screen is wired?

Study 3 registers exactly two confirmatory verdicts (H4''-graded, H4''-strict)
plus a registered screen-effectiveness smoke assertion. H1'/H2-1'/H3' are **not**
re-registered (§3.3): Study 2 already confirmed them; re-testing invites
multiplicity without a new question.

---

## 2. Registered sample size, pilot, roster

### 2a. Sample size (traceable to `power_study3.json`)

| Estimand | Registered n | Powered target | Achieved power | JSON trace |
|---|---|---|---|---|
| **H4''-graded** (rich C+D cells) | **28-PUT grid → n_rich = 15** (C7 + D8) | mean share ≥ 0.15 | **0.82** | `power_study3.json::a…power_by_threshold.tau_0.15[15]` |
| H4''-graded (conservative floor) | n_rich = 15 | mean share ≥ 0.10 | **0.92** | `a…tau_0.1[15]` |
| **H4''-strict** (clean CE/HP/CF-screened) | **n_detected = 99** (v5-calibrated) | purity ≥ 0.90 (95% lower CP) | **≥ 0.82** for true purity ≥ 0.97 | `power_study3.json::b…power.threshold_0.9` |

**n_rich note.** The standard 28-PUT class balance (A7/B6/C7/D8) yields
**n_rich = 15** rich-class PUTs (C7 + D8). At n_rich = 15 the graded mean-share
lower bound clears **τ = 0.15 with power 0.82** and **τ = 0.10 with power 0.92**
(`power_study3.json`). τ = 0.20 is **not** powered even at n_rich = 24 and is
therefore **not** registered as a pass/fail bar (the Study-1 under-powering error
is not repeated). If Study 3 re-weights toward more rich PUTs (e.g. C9/D9 within
28), n_rich rises and τ = 0.15 gains headroom; the registered analysis uses
whatever rich subset the frozen roster (§2c) produces, and reports the achieved
n_rich alongside the verdict.

### 2b. Calibration pilot — reuse the `{a2, b4}` protocol verbatim

The Study-2 v1.1 **2-PUT calibration pilot `{a2, b4}`** protocol is reused
verbatim for Study 3.

- **Pick rationale (machinery-representative).** `a2` (LU determinant) is the
  canonical dry-run anchor (`CAMPAIGN_RUNBOOK.md §5`); `b4` (bootstrap
  resampling) stresses the new-PUT loader, a stochastic estimator, and a **TF**
  operator so the single-stratum screen can be debugged on a leakage-relevant
  family. Together they span original-vs-new, deterministic-vs-stochastic, two
  design classes (A, B), and include TF.
- **Firewall.** The pilot is **excluded from every confirmatory analysis**
  (H4''-graded, H4''-strict). Pilot outcomes may fix **code defects only**
  (harness bugs, fence-stripping, review-packet blinding, determinism, **and the
  screen wiring**) — **never** thresholds, estimands, DGP calibration, primary-MP
  assignment, or the roster. Any pilot-triggered change is logged in the §10
  amendment appendix **before** the confirmatory run begins. Pilot amendment
  appendix: `docs/prereg_v2/PILOT_LOG.md` (append-only).
- **Study-3-specific pilot duty.** The pilot MUST exercise the P8-fixed
  all-family screen end-to-end and confirm the registered smoke assertion (the
  screen matches > 0 candidates on `b4`'s TF operator); a zero-match is the
  incident-P8 no-op and blocks the confirmatory run.

### 2c. Confirmatory roster — full 28-PUT regeneration

The 28 confirmatory PUTs = 30 − pilot `{a2, b4}`, class balance **7/6/7/8**
(A: a1,a3,a4,a5,a6,a7,a8; B: b1,b2,b3,b5,b6,b7; C: c1,c2,c3,c4,c5,c6,c7; D:
d1,d2,d3,d4,d5,d6,d7,d8), identical IDs to Study-2 v1.1 §2c. **Rich-class
subset for H4''-graded = C7 + D8 = 15 PUTs.** Each PUT keeps
`program(x: float) -> float`, x∈[0,1], deterministic (seeds fixed at load).

**Fresh generation is required (S5).** Study 3 regenerates **all** mutants with
**fresh seeds** and a **fresh validated pool** (SSOT `sms_track2_v6.json`). The
v5 pool is **not** reused for any confirmatory verdict: a hypothesis about
attribution structure that was *formed after seeing v5* cannot be confirmed on
v5 without circularity. The v5 pool serves calibration (§0.1) only.

---

## 3. Confirmatory hypotheses

Format: statistic · threshold (power justification) · test · α · decision rule ·
licensed verdict.

### 3.1 H4''-graded — Graded attribution to the declared MetaPattern (RQ-S3, primary)

- **Construct (NOETHER-aligned).** On rich PUT classes, a single semantic fault
  perturbs several invariant strata at once (the [2,5] = `{m_mono, m_cmp}`
  co-flip on C/D; `H4_DIAGNOSIS.md` §4). Rather than demand single-valued purity
  (which fails by construction), Study 3 asks whether the detected kill signal is
  still substantially **attributed to the declared MetaPattern** `m_xxx` (the
  registered class-primary: A→MP1 `m_inv`, B→MP2 `m_mono`, C→MP5 `m_cmp`,
  D→MP2 `m_mono`; §4).
- **Graded measure (chosen; alternatives in §7b).** For each **detected** mutant
  `m` (flip count ≥ 1) declared to primary stratum `m*`:
  `s_m = 𝟙[m* ∈ flipset(m)] / |flipset(m)|`.
  The cell statistic is the mean of `s_m` over the detected mutants declared to a
  PUT; the aggregate is the **mean over the rich-class (C, D) PUTs**. It is a
  per-mutant ratio in [0,1]: 1 for a purely attributed mutant, 1/f for an f-way
  co-flip, 0 for a mis-declared kill. It reuses the frozen S5/audit flip
  definition byte-for-byte and needs no threshold on the LRCA magnitude.
  *Justification for this measure over alternatives:* it is bounded, monotone in
  attribution concentration, and interpretable as "expected posterior mass on the
  declared stratum under a uniform prior over the flipped set"; the two rejected
  alternatives (a) raw declared-stratum kill rate (ignores co-flip dilution) and
  (b) off-diagonal `suspect_share` (the failed H4' estimand, not graded) are
  recorded in §7b.
- **Threshold**: **mean primary-stratum kill share ≥ 0.15** over the rich-class
  cells. **Power 0.82 at n_rich = 15** (`power_study3.json::a…tau_0.15[15]`);
  τ = 0.10 floor reaches 0.92 (`a…tau_0.1[15]`). The v5-calibrated DGP central
  value is 0.3077 with observed bootstrap lower bound 0.1923
  (`a…true_rich_mean_dgp`, `a…boot_lower_observed`) — the registered 0.15 bar
  sits below the calibrated point estimate with a genuine, powered margin, and
  well above the ≈0 mis-attribution floor of the worst (mis-declared) cells.
- **Test**: one-sided 95% lower confidence bound on the rich-class mean share
  (analysis-time: B = 10,000 percentile bootstrap, seed 20260708; the power
  simulation uses the matching normal-approx lower bound). **α**: 0.05,
  one-sided. **Family**: G (single test).
- **Decision**: lower bound > 0.15 → **confirm graded attribution** (the declared
  MetaPattern carries substantial attribution mass on rich PUTs); else report the
  achieved rich-class mean share and per-class breakdown factually.
- **Licensed verdict**: a *graded* attribution claim — the declared MetaPattern
  is the dominant single stratum but co-fires with structurally-coupled
  neighbours; **not** a single-stratum purity claim. NOETHER naming: attribution
  to `m_xxx` (the class-declared MetaPattern), not to an ordinal cell.

### 3.2 H4''-strict — Single-stratum purity where coupling is absent (RQ-S3, sub-hypothesis)

- **Statistic**: fraction of **detected** clean-family mutants that are
  single-stratum (flip ≤ 1), over the registered clean families **{CE, HP,
  CF-with-screen}**. CE and HP are 0-leakage in both studies
  (`H4_DIAGNOSIS.md` §5); CF leakage is **stable** (9/9, class-b, `[1,2]` =
  `{m_inv, m_mono}`, identical across v4/v5) and therefore cheaply and
  deterministically screenable — so CF is admitted **through the fixed
  all-family screen**, which rejects its double-flips at admission, leaving a
  single-stratum-pure admitted CF pool. OS/SI/TF are **excluded** from the strict
  family (their coupling is intrinsic on rich PUTs — the graded regime).
- **Screen wiring (registered, verified).** The P8-remediated all-family screen
  (§4b) is wired at admission with `P2_SCREEN_ALL_FAMILIES=1`. Its effectiveness
  is verified by a **registered smoke assertion**: on the confirmatory campaign
  the screen MUST **match > 0 candidates** and, on a re-audit of any
  leakage-bearing family, **flag > 0 double-flips**. A screen that matches zero
  candidates is the incident-P8 silent no-op and **fails the campaign loudly**
  (never again a no-op). Basis: on the v5 corpus the all-family audit matches
  **741** candidates and flags **117** double-flips
  (`power_study3.json::c_screen_smoke_assertion`).
- **Threshold**: **single-stratum purity ≥ 0.90** (one-sided 95% lower
  Clopper-Pearson bound). Post-screen the construct guarantees purity ≈ 1.0 (CF
  double-flips rejected; CE/HP 0-leakage): the v5-calibrated post-screen purity
  is **1.000** (pre-screen 0.909; the screen removes all 9 CF double-flips),
  over **n = 99** detected clean-family mutants. **Power ≥ 0.82** for any true
  purity ≥ 0.97 (`power_study3.json::b…power.threshold_0.9`); the ≥ 0.95 bar is
  reported as sensitivity (powered only for true purity ≥ 0.99) to avoid a
  fragile bar.
- **Test**: one-sided 95% lower CP bound on the clean-family purity ≥ 0.90.
  **α**: 0.05, one-sided. **Family**: G.
- **Decision**: lower bound ≥ 0.90 → **confirm single-stratum purity holds where
  coupling is absent/screenable**; else report the observed purity and the
  escaping family factually.
- **Licensed verdict**: the single-stratum σ model is valid for {CE, HP,
  CF-with-screen}; it is **not** claimed for OS/SI/TF on rich PUTs (those are the
  graded regime, H4''-graded).

### 3.3 NOT re-registered (multiplicity control)

- **H2-1' (aligned>cross magnitude)**, **H1' (operator instantiability)**,
  **H3' (cross-class direction)** are **not** re-registered as Study-3
  confirmatory hypotheses. Study 2 confirmed them; re-testing on fresh data adds
  family multiplicity without posing a new question. They may be **re-run
  descriptively** on the Study-3 pool for continuity, labelled exploratory (Family
  X), never as confirmatory verdicts.
- **H2-2 (cross-vendor source diversity)** remains **gated not-run** under the
  same-vendor harness (§5b), unchanged from v1.1.

---

## 4. Primary meta-pattern rule + P8-remediated screen

### 4a. Primary MP rule — UNCHANGED from Study-2 v1.1 / v1.0

The deterministic, taxonomy-indexed, data-independent rule (A→MP1, B→MP2,
C→MP5-held, D→MP2) is retained exactly (`PRIMARY_CELLS_V3`, run with
`P2_PRIMARY_VERSION=v3`; the `v3b` selection-on-response path is prohibited). The
graded measure declares each rich-class mutant to its class-primary MP under this
frozen rule; the C→MP5 declaration is retained even though v5 shows C kills
concentrate off MP5 — the graded measure *reports* that mismatch (low C share)
rather than re-deriving the primary from the response.

### 4b. Screen remediation (incident P8) — forward-looking, alters no v5 artefact

The single-stratum screen (`src/p2/mutators/stratum_filter.py`) is remediated for
the Study-3 generation path only; the committed v5 SSOTs and the frozen H4'
verdict are **untouched** (the diagnosis reproduces its no-op evidence via a
pinned historical parser):

1. **op_id parser fixed** — `_OPID_CAT_RE` tolerates the cross-source suffix
   (`c7_TF1_claude` → `TF`), so categories resolve for every v5-style id (was
   `None` for all 117 leakage mutants).
2. **all-family scope** — `ALL_FAMILIES` + `active_constrained_categories()`,
   selected per-registration via `screen_all_families_enabled()`
   (`P2_SCREEN_ALL_FAMILIES=1` for Study 3); Study-2 default stays {CF,TF}.
3. **loud-fail on null category** — `decide(None)` raises instead of admitting
   silently, so a parse failure can never again masquerade as an unconstrained
   pass.

Validation (regression tests, `tests/mutators/test_stratum_filter.py`): the fixed
all-family audit flags exactly the 117 committed v5 double-flips (byte-identical
to `h4_leakage_diagnosis_v5.json`, family split OS 27 / CF 9 / TF 72 / SI 9); the
Study-1 29/29 audit still reproduces byte-for-byte; the null category raises
loudly. Full suite green (448 passed).

---

## 5. Dual-blind protocol + harness disclosure + one-shot rule

### 5a. Dual-blind core — UNCHANGED from v1.1

Generation → **blind review** (reviewer sees only mutant code + operator spec +
PUT source; generator identity, arm label, SMS withheld) → **arbitration** on
disagreement → **freeze then score** (SMS computed only after review labels are
frozen). Generator ≠ reviewer ≠ arbiter on every item. Analyst blindness
preserved. The single-stratum screen runs at admission, **before** any SMS or
graded share is computed, identically for every cell.

### 5b. Harness instantiation disclosure — VERBATIM from v1.1

Study generation and review run through the **Claude Code Agent harness**:

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
  it is gated not-run unless cross-vendor credentials are supplied. The
  same-vendor arm tests the Study-3 attribution hypotheses only.
- **SSOT record**: the **exact agent-tier model name at generation time** is
  recorded in the campaign SSOT (`data/operator_campaign/…_log.json`) at run
  time; it is not fixed in this registration because the harness resolves it at
  generation.

### 5c. One-shot confirmatory rule — VERBATIM from v1.1 (screen-smoke clause added)

**Confirmatory generation runs ONCE per the registered budget** — the mutant-count
targets per cell, seeds (20260708), and prompt-template version pinned by file
hash. **Regeneration, cherry-picking cells, or moving any threshold after ANY
confirmatory outcome is visible is a protocol violation that must be reported as
such** in §10 and in the paper. Confirmatory analysis runs **only** through the
pre-frozen scripts (§7). The calibration pilot (§2b) is the *only* place live
outcomes are seen before the confirmatory freeze, and it may fix code defects
only. **Screen-smoke gate (Study-3):** the wired all-family screen MUST match > 0
candidates at admission; a zero-match halts the confirmatory run as an incident-P8
regression (loud failure, logged in §10), it is never silently ignored.

---

## 6. Industrial corpus — OUT OF SCOPE for Study 3

Study 3 does not touch the industrial legs (H2-3, H2-4), the two-tier census, or
the Tier-A/B firewall — all closed under Study 2 v1.1 §6 and unchanged.

---

## 7. Analysis plan — SSOT paths + pre-frozen scripts + §7b contracts

**SSOT paths (Study 3)**: `sms_track2_v6.json` (fresh validated pool),
`h4_graded_v6.json` (graded verdict), `s5_purity_v6.json` (strict-purity
verdict); power reference `power_study3.json`.

**Pre-frozen scripts** (frozen before any Study-3 data; each carries the
"pre-frozen / post-data change = disclosed deviation" header):

### 7b. Analysis-script contracts (sibling MUST pre-freeze before generation)

- **`scripts/compute_h4_graded.py`** (NEW — pre-freeze required).
  - **Input**: the frozen Study-3 validated pool `sms_track2_v6.json` (per-cell
    `outcomes` = {file, label}); `PRIMARY_CELLS_V3` under `P2_PRIMARY_VERSION=v3`;
    the fixed `p2.mutators.stratum_filter.audit_matrix(...,
    constrained=ALL_FAMILIES)` for the flip sets (identical audit definition to
    S5). Pilots `a2`, `b4` excluded.
  - **Computation**: per detected mutant, `s_m = 𝟙[primary∈flipset]/|flipset|`;
    per rich-class PUT (C, D), the mean of `s_m`; the rich aggregate mean; the
    one-sided 95% percentile-bootstrap lower bound (B=10,000, seed 20260708).
  - **Output**: `data/results/h4_graded_v6.json` with `rich_mean_share`,
    `boot_lower_95`, per-class (C, D) share means, per-PUT shares, `n_rich`, and
    `verdict = (boot_lower_95 > 0.15)`. Prints the licensed verdict string, not
    just numbers.
  - **Decision rule (frozen)**: confirm iff `boot_lower_95 > 0.15`.
- **`scripts/compute_h4_strict.py`** (or the existing
  `compute_h4_attribution.py` re-pointed to v6).
  - **Input**: the fixed `audit_matrix(..., constrained=ALL_FAMILIES)` over
    `sms_track2_v6.json`; the wired all-family screen (`P2_SCREEN_ALL_FAMILIES=1`).
  - **Computation**: over detected clean-family {CE, HP, CF-with-screen} mutants,
    the single-stratum fraction and its one-sided 95% lower Clopper-Pearson bound;
    the screen-smoke counters (`n_screened_candidates`, `n_multistratum_flagged`).
  - **Output**: `data/results/s5_purity_v6.json` with `purity`, `cp_lower_95`,
    `n_clean_detected`, `cf_screened_out`, the smoke counters, and
    `verdict = (cp_lower_95 ≥ 0.90 AND n_screened_candidates > 0)`. A
    zero-candidate screen forces a loud FAIL verdict, not a silent pass.
  - **Decision rule (frozen)**: confirm iff `cp_lower_95 ≥ 0.90` **and** the
    screen matched > 0 candidates.

Both scripts are covered by offline synthetic-fixture tests in `tests/analysis/`
before generation, and each prints the registered licensed verdict.

**Seeds**: all bootstrap at 20260708. **Exclusion rules** (analysis-time):
silent (flip = 0) mutants are undetected and excluded from the graded share (no
0/0); vacant cells excluded; pilots `{a2,b4}` excluded from every confirmatory
statistic.

**Multiplicity — Study-3 family map**

| Family | Members | Correction | Confirmatory? |
|---|---|---|---|
| G — Attribution | H4''-graded (share ≥ 0.15), H4''-strict (purity ≥ 0.90) | Holm (2) within family G | yes |
| X — Exploratory | descriptive re-runs of H2-1'/H1'/H3', per-class graded breakdown, C→MP5 mismatch, ≥0.95 purity sensitivity | per-test as labeled | no |

Holm(2) within family G controls the two-test attribution family; no study-wide
cross-family correction (Study 2's families are closed). Confirmatory ↔
exploratory bright line unchanged.

---

## 8. Decision matrix

| Hypothesis | Confirm licenses | Non-confirm licenses |
|---|---|---|
| H4''-graded | "on rich (C/D) PUTs, the declared MetaPattern carries graded attribution (mean share ≥ 0.15)" | achieved rich-class mean share + per-class breakdown stated factually |
| H4''-strict | "single-stratum purity holds where coupling is absent/screenable (CE/HP/CF-with-screen, purity ≥ 0.90)" | observed purity + escaping family stated factually; if the screen matched 0 candidates → loud FAIL, incident-P8 regression |

**What would count against the construct (registered a priori)**: (i) rich-class
graded share lower bound ≤ 0.15 despite 0.82 power (attribution not graded —
kills are near-random over strata); (ii) clean-family purity lower bound < 0.90
despite the wired screen (coupling is NOT absent even in CE/HP/CF); (iii) the
all-family screen matching zero candidates (P8 regression).

---

## 9. Deviations-from-prior lessons table

| # | Prior lesson | Study-3 v2.0 closure | Trace |
|---|---|---|---|
| L12 | Study-2 H4 leakage dominated by CF/TF; the single-stratum bar assumed away real coupling | split the estimand: graded attribution on rich (C/D), strict purity only where coupling is absent/screenable | `H4_DIAGNOSIS.md` §6-7 |
| L14 | Incident P8: the CF/TF screen was a silent no-op (op_id regex rejected the source suffix) and never targeted OS/SI | P8-remediated all-family screen (fixed parser, all-family scope, loud-fail null), verified by regression tests + a registered smoke assertion | §4b; `test_stratum_filter.py` |
| L15 | A hypothesis formed after seeing v5 cannot be confirmed on v5 | full 28-PUT regeneration (fresh mutants/seeds); v5 used for calibration only, stated openly | §0.1, §2c |
| L16 | Registering settled hypotheses inflates multiplicity | H2-1'/H1'/H3' NOT re-registered; only the two attribution verdicts are confirmatory (Holm within family G) | §3.3, §7 |

---

## 10. Amendments log (append-only, dated)

**Registration #1 — 2026-07-09 (this document, Study-3 v2.0).** Superseded the
frozen Study-2 H4' with two attribution verdicts — H4''-graded (rich-class mean
primary-stratum kill share ≥ 0.15, power 0.82 at n_rich = 15) and H4''-strict
(single-stratum purity ≥ 0.90 on {CE, HP, CF-with-screen} with the P8-fixed
all-family screen wired, power ≥ 0.82 for true purity ≥ 0.97); remediated the
incident-P8 screen (fixed op_id parser, all-family scope, loud-fail null),
altering no committed v5 artefact; reused the `{a2, b4}` calibration-pilot
protocol; declared a full 28-PUT regeneration; did NOT re-register the settled
H2-1'/H1'/H3'; registered a screen-effectiveness smoke assertion (fail loudly on
zero-match). All changes pre-Study-3-data; Study-2 (v5) data used for design
calibration only (§0.1). Power/feasibility SSOT: `data/results/power_study3.json`
(seed 20260708).

*(No further amendments. Any post-freeze change — a pilot-triggered code fix, a
seed correction — is appended here with date and rationale before the
confirmatory run.)*
