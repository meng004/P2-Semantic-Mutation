# Pre-Registration — Study 4 (Confirmatory) — v1.0

**Paper**: *When Same-Prompt LLM Source Diversity Doesn't Help — Semantic
Mutation Operator Ablation in Metamorphic Testing for Single-Output Scientific
Computing Kernels* (P2/P3, IST/TOSEM multi-study architecture).

**This document is a NEW confirmatory registration** in the lineage
`PREREGISTRATION_STUDY2.md` (v1.0, commit `072a015`) →
`PREREGISTRATION_STUDY2_v1.1.md` (v1.1, 2026-07-08) →
`PREREGISTRATION_STUDY3_v2.md` (v2.0, 2026-07-09) → **this v1.0 (Study 4)**. It
does **not** amend or re-open any frozen registration; Studies 2 and 3 are
closed and their confirmatory verdicts stand FROZEN and UNCHANGED (including
Study-2 `H4' = NOT_CONFIRMED` and the Study-3 `H4''-graded = NOT_CONFIRMED`
(rich-class mean share 0.0833, n_rich = 6), `H4''-strict = CONFIRM`). Study 4
registers **three** confirmatory families on **fresh data that does not yet
exist**, made possible by a live cross-vendor gateway (four vendor lineages
confirmed working 2026-07-09: `claude-fable-5` / `gpt-5.5` / `gemini-3.5-flash`
/ `grok-4.1`→`grok-4.3`; credentials in the gitignored `.env`, never committed).

**Editorial stance (encoded).** This registration is written to ARGUE, not
merely report: each family poses a sharp, well-motivated hypothesis and commits
to an honest verdict either way. H2-2 finally executes the cross-vendor contrast
that was gated not-run for two studies; H4''' pre-commits to the sharp
interpretation that a low graded-attribution share at *adequate* n confirms
misattribution as a construct property (not a small-sample artifact); H-LANG
stakes the bold NOETHER-derived claim that the construct is language-invariant
and puts it to a one-shot falsification test on a C port. No defensive hedging;
under-recruitment gates are registered so that a weak result is reported as weak,
never disguised.

**Status**: FROZEN before any **Study-4** data generation. Frozen apparatus:
this file + `scripts/power_analysis_study4.py` (power/feasibility SSOT
`data/results/power_study4.json`) + the pre-freeze analysis-script contracts of
§7b (`compute_dualblind_delta.py` unchanged, `compute_hlang_delta.py` new,
`compute_h4_graded.py --pooled` flag). Master seed `20260708` (freeze-date seed
convention retained). Any change after this freeze is a logged, dated entry in
§10, not an edit to the frozen body.

---

## 0. Lineage record (v1.0 → v1.1 → v2.0 → Study-4 v1.0)

### 0.1 Pre-data attestation (Study-4 data specifically)

> **This registration was drafted and frozen before any STUDY-4 data
> generation. No Study-4 mutant, SMS cell, LRCA classification, dual-blind
> label, graded-attribution outcome, cross-vendor arm, or C-port kill exists or
> was visible to the authors of this registration.** Verification performed at
> drafting (2026-07-09): no `data/mutants/*_v7*` pool exists; no Study-4 SSOT
> (`sms_track2_v7.json`, `sms_track2_v7_same.json`, `dualblind_delta_delta_v7.json`,
> `h4_graded_v7.json`, `hlang_delta_vC.json`) exists (all verified absent).
>
> **Prior-study data (v4/v5/v6) IS seen, and is used for ONE purpose only —
> design calibration — stated openly.** The v4 hurdle pool calibrates the H2-2
> Delta-delta power (as in v1.1); the v5 pool (observed aligned>cross
> `delta = 0.4295`, `dualblind_delta_delta_v5.json`) calibrates the H-LANG DGP;
> the v6 graded outcome (detected `n_rich = 6` of 15 rich PUTs, `h4_graded_v6.json`)
> calibrates the H4''' recruitment multiplier. This is **design-from-prior-study**,
> the standard registered-science practice, exactly as Study 2 calibrated from
> Study-1 v4 and Study 3 from Study-2 v5. It is **not** selection on the Study-4
> response, because no Study-4 response exists. Every confirmatory verdict is
> computed on fresh Study-4 pools through the pre-frozen scorers (§7b), never on
> v4/v5/v6.

### 0.2 Diff table (Study-4 additions over the frozen Study-3 v2.0)

| # | Clause | Prior state | Study-4 v1.0 | Justification |
|---|---|---|---|---|
| T1 | H2-2 cross-vendor source diversity | **gated not-run** (same-vendor harness; v1.1 §3, v2.0 §3.3) | **EXECUTABLE**: two API-served arms via the cross-vendor gateway (§3.1, §5b) | the four-vendor gateway removes the same-vendor limitation that gated H2-2 for two studies; the estimand + decision rule are v1.1's VERBATIM |
| T2 | H2-2 review/arbitration wiring | Claude-only instances (same vendor) | reviewer = `claude-fable-5` (blinded, BOTH arms); arbiter = `gpt-5.5` (different vendor from reviewer) (§5) | genuine cross-vendor arbitration; the DIVERSITY under test is generation-side (§5c honesty note) |
| T3 | Rich-class recruitment | Study-3 v6 detected only n_rich = 6 of 15 (too thin for the graded bootstrap) | **H4'''-graded** re-test: DOUBLE-swept per-operator slots on C/D PUTs in BOTH arms + **pre-declared pooling** of the two arms; registered multiplier **x4** (§2a, §3.2, §4b) | binomial projection from the v6 detection rate p0 = 6/15 fixes the thinness root cause; x2 shown insufficient |
| T4 | H4''' decision + recruitment gate | v2.0 single-arm graded, n_rich = 6 observed | same graded measure + 0.15 bar on the **POOLED** arms; registered gate: detected pooled n_rich < 24 -> **UNDER-RECRUITED** (no threshold move); sharp interpretation pre-declared either way (§3.2) | evaluate the adequate-n graded share; if it stays low at adequate n the misattribution finding is CONFIRMED as a construct property |
| T5 | **H-LANG** cross-language invariance | — (absent) | NEW bold hypothesis: on a C port of the 12 original Study-1 PUTs, delta_C > 0 replicates (§3.3); C_PORT_SPEC forthcoming | NOETHER derives MetaPatterns from operator-algebra invariants, not surface syntax -> the construct should be language-invariant; frozen NOW, blind to the port outcome |
| T6 | H-LANG power | — | n = 12 from the v5 DGP (delta ~ 0.43); achieved power **0.8735** (§2a) | n=12 gives less power than n=28; disclosed honestly; the delta~0.43 DGP keeps the direction claim well-powered |
| T7 | Analysis-script contracts | `compute_h4_graded.py` (v6), `compute_dualblind_delta.py` (v5) | `compute_dualblind_delta.py` serves H2-2 **as-is** (verified §7b); NEW `compute_hlang_delta.py` (C grid); `compute_h4_graded.py --pooled` flag contract (§7b) | pre-freeze the scorers before generation, same gold-standard ordering |
| T8 | Not re-registered | — | H2-1', H1', H3' (settled by Study 2); H4''-strict (settled by Study 3) are **not** re-registered as Study-4 confirmatory; re-runnable descriptively (Family X) | avoid needless multiplicity on settled verdicts |
| T9 | Incident ledger | ends at P9 (Study-3 v6 tooling) | continues at **P10+** (§10); Incident #1 (v3-pool wipe) retained | append-only provenance |

Attestation applies to **every** row: *frozen before any Study-4 data
generation; no Study-4 outcome was visible; v4/v5/v6 used for calibration only.*

---

## 1. Confirmatory research questions (three families)

- **RQ-S4a (cross-vendor source diversity, dual-blind).** Under one identical,
  fully API-served dual-blind protocol on a same-source arm and a genuinely
  cross-vendor arm, does cross-source pooling move Delta-delta? *(Now executable:
  the same-vendor limitation that gated this for Studies 2–3 is removed by the
  four-vendor gateway.)*
- **RQ-S4b (attribution structure at adequate rich-class n).** With the rich
  (C, D) classes recruited to an adequate sample (pooled n_rich >= 24), is the
  detected kill signal substantially attributed to the declared MetaPattern
  (graded share >= 0.15), or does the attribution share stay low — confirming
  the Study-3 misattribution as a **construct property**, not a small-sample
  artifact?
- **RQ-S4c (cross-language invariance).** On a C-language port of the 12 original
  Study-1 PUTs, does the aligned-dominates-cross direction replicate
  (delta_C > 0)? MetaPatterns are operator-algebra invariants of the governing
  equations, not surface syntax (NOETHER `\citep{noether2026}`); the construct
  should therefore be **language-invariant**.

Study 4 registers exactly three confirmatory verdicts: **H2-2** (Family B),
**H4'''-graded** (Family H), **H-LANG** (Family L). H2-1'/H1'/H3'/H4''-strict are
**not** re-registered (§3.4).

---

## 2. Registered sample sizes, pilot, roster

### 2a. Sample sizes (traceable to `power_study4.json`)

| Estimand | Registered n | Powered target | Achieved power | JSON trace |
|---|---|---|---|---|
| **H2-2** cross-vendor Delta-delta | **28 PUTs** paired (per arm n_aligned=28, n_cross=112) | \|Delta-delta\| >= 0.20 two-sided | **0.793** @28 | `power_study4.json::a…power_by_delta_delta.dd_0.2[28]` |
| **H4'''-graded** (pooled rich C+D) | **pooled n_rich >= 24** target (2 arms x 15 rich PUTs, x4 slots) | mean share >= 0.15 | recruitment: **P(n_rich>=24) = 0.92** @ x4 | `power_study4.json::b…multiplier_curve.4` |
| **H-LANG** delta_C > 0 | **12 PUTs** (C port of the original 12) | delta_C > 0 one-sided | **0.8735** @ n=12 | `power_study4.json::c…power_delta_gt0_at_n12` |

**H2-2 n note.** The paired Delta-delta = 0.20 leg reaches **0.793** at n = 28
(paired SE 0.072, calibrated rho 0.759) — marginally below the 0.80 target,
**exactly as disclosed in v1.1** and reproduced here (the power is effect-size
driven and the DGP is unchanged; only executability changed). This is reported
honestly; the registered three-way rule (§3.1) already licenses an
UNDER-RECRUITED verdict when the CI is wide, so no threshold is moved to
manufacture power. The magnitude leg H2-1' was confirmed by Study 2 and is not
re-tested.

**H4''' recruitment note.** Study-3 v6 detected only n_rich = 6 of the 15
rich-class (C7+D8) PUTs; the graded bootstrap over 6 PUT-means is thin, which is
the root cause of the Study-3 `NOT_CONFIRMED` fragility. Per-PUT-per-arm
detection probability p0 = 6/15 = 0.40. Doubling the per-operator slots
multiplies the independent detection opportunities (p_m = 1 - (1-p0)^m), and
**pooling the two Study-4 arms** gives up to N = 2 x 15 = 30 rich PUT-arm units;
detected pooled n_rich ~ Binomial(30, p_m). The multiplier sweep
(`power_study4.json::b…multiplier_curve`):

| Multiplier | per-PUT detect p_m | expected pooled n_rich | P(n_rich >= 24) | meets gate |
|---|---|---|---|---|
| x2 | 0.640 | 19.2 | 0.047 | **no** |
| x3 | 0.784 | 23.5 | 0.521 | no |
| **x4** | **0.870** | **26.1** | **0.915** | **YES** |
| x5 | 0.922 | 27.7 | 0.993 | yes |

**x2 is INSUFFICIENT** (expected 19.2, P(>=24) = 0.047). The **registered
multiplier is x4** (expected pooled n_rich 26.1, P(>=24) = 0.92). Cost: x4
roughly quadruples the C/D mutant-generation + blinded-review budget on the 15
rich PUTs across both arms; A/B slots are unchanged, so whole-campaign cost rises
well below 4x. **H-LANG power note.** The C-port grid is the 12 original PUTs
(n = 12), which gives less power than the n = 28 grid; the v5-calibrated DGP
(true delta = 0.4385, matching the observed v5 delta = 0.4295) keeps the
one-sided direction claim **well-powered at 0.8735**, so H-LANG is registered as
confirmatory with power > 0.80 disclosed; had it fallen below 0.80 it would
still be registered confirmatory with the achieved value disclosed.

### 2b. Calibration pilot — reuse the `{a2, b4}` protocol verbatim

The Study-2/3 **2-PUT calibration pilot `{a2, b4}`** protocol is reused verbatim.

- **Pick rationale (machinery-representative).** `a2` (LU determinant) is the
  canonical dry-run anchor (`CAMPAIGN_RUNBOOK.md §5`); `b4` (bootstrap
  resampling) stresses the new-PUT loader, a stochastic estimator, and a **TF**
  operator. Together they span original-vs-new, deterministic-vs-stochastic, two
  design classes (A, B), and include TF.
- **Study-4-specific pilot duties.** The pilot MUST additionally exercise
  end-to-end, on `{a2, b4}` only: (i) **each of the four vendor lineages**
  through the gateway (`claude-fable-5` / `gpt-5.5` / `gemini-3.5-flash` /
  `grok-4.1`) returns a parseable mutant under the symmetric API protocol (no
  harness/API asymmetry between arms); (ii) `gemini-3.5-flash` runs with
  `max_tokens >= 2000` (reasoning-token consumption, per the gateway smoke note);
  (iii) the blinded review packet strips generator/vendor identity and arm label
  for BOTH arms; (iv) the `x4` C/D slot multiplier and the `--pooled` graded path
  run without error on the pilot pool.
- **Firewall.** The pilot is **excluded from every confirmatory analysis** (H2-2,
  H4'''-graded, H-LANG). Pilot outcomes may fix **code defects only** (harness
  bugs, gateway wiring, fence-stripping, review-packet blinding, determinism,
  slot-multiplier wiring, pooling) — **never** thresholds, estimands, DGP
  calibration, primary-MP assignment, the roster, or vendor role assignments.
  Any pilot-triggered change is logged in `docs/prereg_v2/PILOT_LOG.md`
  (append-only) and in §10 **before** the confirmatory run begins.

### 2c. Confirmatory rosters

- **H2-2 and H4''' rosters** = the frozen 28-PUT confirmatory set (30 − pilot
  `{a2, b4}`, class balance 7/6/7/8: A a1,a3,a4,a5,a6,a7,a8; B b1,b2,b3,b5,b6,b7;
  C c1,c2,c3,c4,c5,c6,c7; D d1,d2,d3,d4,d5,d6,d7,d8), identical IDs to Studies
  2–3. **Rich-class subset for H4'''-graded = C7 + D8 = 15 PUTs**, each generated
  in BOTH arms at the **x4** per-operator slot multiplier.
- **H-LANG roster** = the **12 original Study-1 PUTs** (a1,a2,a3,b1,b2,b3,c1,c2,
  c3,d1,d2,d3) **ported to C**. A sibling agent is building the port **blind to
  outcomes**; the C-port specification is referenced as forthcoming
  `docs/prereg_v2/C_PORT_SPEC.md` (frozen hypothesis NOW, before any port kill is
  visible). The C mutants are produced through the same four-vendor cross-vendor
  slots (§5); review blinded as below. Note the H-LANG grid deliberately includes
  the pilot PUTs `a2`/`b4`-analogues at the *language* level — the `{a2,b4}`
  code-firewall applies to the Python confirmatory pools, whereas H-LANG is a
  distinct C-port estimand on the original 12; no Python pilot outcome enters the
  C-port delta.

**Fresh generation is required.** Study 4 generates **all** mutants fresh (fresh
seeds, fresh validated pools: `sms_track2_v7.json` cross-source arm,
`sms_track2_v7_same.json` same-source arm, C-port pool `sms_track2_vC.json`). No
v4/v5/v6 pool is reused for any confirmatory verdict.

---

## 3. Confirmatory hypotheses

Format: statistic · threshold (power justification) · test · α · decision rule ·
licensed verdict.

### 3.1 H2-2 — Cross-vendor dual-blind source diversity (RQ-S4a, Family B) — EXECUTABLE

- **Design (two arms, both API-served — symmetric, no harness/API asymmetry).**
  - **Same-source arm**: `claude-fable-5` generates ALL three slots on every
    confirmatory PUT.
  - **Cross-source arm**: the identical 3-slot structure is mapped to three
    **non-Anthropic** lineages — `gpt-5.5` (OpenAI), `gemini-3.5-flash` (Google),
    `grok-4.1`→`grok-4.3` (xAI) — one lineage per slot.
  - Both arms run the **identical** dual-blind protocol (§5); the only difference
    is the generator-vendor mapping of the three slots. Every generation call is
    an API call through the same gateway, so there is **no harness-vs-API
    asymmetry** between arms.
- **Blinded review (identical protocol, both arms).** Reviewer = `claude-fable-5`
  on **blinded packets** (mutant code + operator spec + PUT source only; no
  generator identity, no vendor tag, no arm label, no SMS). Arbitration on
  disagreement = `gpt-5.5` (a **different vendor** from the reviewer). SMS is
  computed only after review labels are frozen and committed (freeze-then-score).
- **Statistic**: Delta-delta = delta(cross-source) − delta(same-source), paired
  on the 28 confirmatory PUTs under the identical dual-blind protocol.
- **Threshold / power**: \|Delta-delta\| >= 0.20 detectable; paired SE at n = 28
  = 0.072 (calibrated rho 0.759), power **0.793**
  (`power_study4.json::a…dd_0.2[28]`) — marginal, reproduced verbatim from v1.1
  (effect-size-driven DGP unchanged; only executability changed).
- **Test**: paired-role bootstrap (block-resample the 28 PUTs, the SAME resample
  applied to both arms so the two per-arm deltas stay paired), 95% two-sided CI
  (B = 10,000, seed 20260708). α 0.05, two-sided. Family B (single test).
- **Decision rule (v1.1 VERBATIM)**:
  - CI **excludes 0** → **CONFIRM** a source-diversity effect of magnitude >= 0.20;
  - CI **includes 0 AND half-width <= 0.14** → **BOUNDED NULL** (no >= 0.20 effect
    detectable under the matched protocol — supports the MR-design-is-the-lever
    thesis as CONFIRMED, not confounded);
  - CI **includes 0 AND half-width > 0.14** → **UNDER-RECRUITED** (inconclusive).
- **Licensed verdict**: a directional/bounded source-diversity claim as above. A
  CONFIRM whose sign reverses the Study-1 Delta-delta anchor (−0.009) is flagged
  as counting against the construct (§8). This is the **generation-side**
  diversity contrast; the single-vendor reviewer is by design (§5c).

### 3.2 H4'''-graded — Graded attribution at adequate rich-class n (RQ-S4b, Family H)

- **Construct (NOETHER-aligned).** On rich PUT classes a single semantic fault
  perturbs several invariant strata at once; the graded measure asks whether the
  detected kill signal is still substantially attributed to the declared
  MetaPattern (registered class-primary: A→MP1 `m_inv`, B→MP2 `m_mono`, C→MP5
  `m_cmp`, D→MP2 `m_mono`; §4a).
- **Graded measure (identical to v2.0).** For each detected mutant m (flip count
  >= 1) declared to primary stratum m*:
  `s_m = 𝟙[m* ∈ flipset(m)] / |flipset(m)|`. Cell/PUT statistic = mean of s_m
  over the detected mutants declared to a PUT; aggregate = **mean over the rich
  (C, D) PUT-means of the POOLED Study-4 arms** (pre-declared pooling, §4b). It
  reuses the frozen S5/audit flip definition byte-for-byte (imported
  `audit_matrix(..., constrained=ALL_FAMILIES)`).
- **Recruitment fix (§2a).** BOTH arms generate the rich (C, D) PUTs at the **x4**
  per-operator slot multiplier; the two arms are **pooled** (pre-declared),
  giving a projected pooled n_rich of 26.1 (P(n_rich >= 24) = 0.92).
- **Threshold**: **mean primary-stratum kill share >= 0.15** over the pooled
  rich-class PUT-means, same measure and bar as v2.0 (τ = 0.20 remains unpowered
  and is NOT a registered bar).
- **Test**: one-sided 95% percentile-bootstrap lower bound on the pooled
  rich-class mean share (B = 10,000, seed 20260708). α 0.05, one-sided. Family H
  (single test).
- **Registered recruitment gate (no threshold moving).** If **detected pooled
  n_rich < 24 at analysis time**, the verdict is **UNDER-RECRUITED** — the
  achieved n_rich and share are reported factually and **no threshold is moved**.
- **Decision rule**:
  - detected pooled n_rich >= 24 **AND** boot_lower_95 > 0.15 → **CONFIRM graded
    attribution** (the declared MetaPattern carries substantial attribution mass
    on rich PUTs at adequate n);
  - detected pooled n_rich >= 24 **AND** boot_lower_95 <= 0.15 → **MISATTRIBUTION
    CONFIRMED as a construct property**: at an adequate rich-class sample the
    attribution share is genuinely low, so the Study-3 finding is **not** a
    small-sample artifact (the sharp, pre-declared interpretation — reported as a
    substantive confirmatory result about the construct, not a null to be
    explained away);
  - detected pooled n_rich < 24 → **UNDER-RECRUITED** (factual report only).
- **Licensed verdict**: either a graded-attribution claim (declared MetaPattern
  dominant-but-co-firing) OR the construct-property misattribution claim, at
  adequate n; never a single-stratum purity claim.

### 3.3 H-LANG — Cross-language invariance (RQ-S4c, Family L) — the bold hypothesis

- **Rationale (NOETHER, `\citep{noether2026}`).** MetaPatterns are derived as
  closure-guaranteed equivalence classes over the **operator algebra of the
  governing equations** (NOETHER Thm 1–2), NOT from surface syntax. The
  semantic-mutation construct therefore probes an invariant of the *program's
  mathematics*, which a language port preserves. **Prediction: the construct is
  LANGUAGE-INVARIANT** — the aligned-dominates-cross direction that held in
  Python must replicate in C.
- **Registered prediction / statistic**: on a C port of the 12 original Study-1
  PUTs, Cliff's delta between the aligned (j = k, primary MP per PRIMARY_CELLS_V3
  mapped to the C cells) and cross (j != k) SMS slices, delta_C.
- **Threshold / power**: **delta_C > 0** (one-sided stochastic dominance). Power
  simulated at **n = 12** from the Study-2 v5 DGP (true delta = 0.4385, matching
  the observed v5 delta = 0.4295): **0.8735**
  (`power_study4.json::c…power_delta_gt0_at_n12`). n = 12 gives less power than
  the n = 28 grid — reported honestly — but the delta~0.43-calibrated DGP keeps
  the one-sided direction claim **well-powered (> 0.80)**. Had it fallen below
  0.80, H-LANG would remain registered as confirmatory with the achieved power
  disclosed (the direction claim, not a magnitude claim, is the estimand).
- **Test**: one-sided 95% percentile-bootstrap lower bound on delta_C > 0
  (multinomial two-sample bootstrap, B = 10,000, seed 20260708) — the SAME
  estimand and bootstrap as H2-1'. α 0.05, one-sided. Family L (single test).
- **Generation**: the C mutants are produced through the same four-vendor
  cross-vendor slot structure as the Study-4 arms; review blinded as in §5.
- **Decision rule**: lower bound > 0 → **CONFIRM cross-language invariance** (the
  construct's aligned>cross direction replicates in C); else report delta_C and
  its bound factually — a direction that fails to replicate is a genuine,
  reportable falsification of the language-invariance claim, not hedged away.
- **Licensed verdict**: a language-invariance *direction* claim, not a
  magnitude-equality claim between Python and C.

### 3.4 NOT re-registered (multiplicity control)

- **H2-1' (aligned>cross magnitude)**, **H1' (operator instantiability)**,
  **H3' (cross-class direction)** — confirmed by Study 2 — and **H4''-strict
  (single-stratum purity)** — confirmed by Study 3 — are **not** re-registered as
  Study-4 confirmatory hypotheses. They may be **re-run descriptively** on the
  Study-4 pools for continuity, labelled exploratory (Family X), never as
  confirmatory verdicts.

---

## 4. Primary meta-pattern rule + rich-class slot multiplier

### 4a. Primary MP rule — UNCHANGED from Studies 2–3

The deterministic, taxonomy-indexed, data-independent rule (A→MP1, B→MP2,
C→MP5-held, D→MP2) is retained exactly (`PRIMARY_CELLS_V3`, run with
`P2_PRIMARY_VERSION=v3`; the `v3b` selection-on-response path is prohibited). For
H-LANG the same rule is mapped cell-for-cell onto the C-ported PUTs (class
membership of the original 12 is frozen; the port preserves class, not code). The
graded measure declares each rich-class mutant to its class-primary MP under this
frozen rule and *reports* any mismatch rather than re-deriving the primary from
the response.

### 4b. Rich-class slot multiplier + pre-declared pooling (registered)

- **Multiplier x4** on every per-operator slot for the C/D (rich) confirmatory
  PUTs, in **both** arms. A/B PUTs keep the baseline slot count. Derivation:
  §2a binomial projection from the v6 detection rate p0 = 6/15 (x2 insufficient,
  P(n_rich >= 24) = 0.047; x4 meets the gate, P = 0.92).
- **Pre-declared pooling.** The two Study-4 arms (same-source, cross-source) are
  **pooled** for the H4'''-graded aggregate — declared HERE, before any Study-4
  outcome. Pooling doubles the rich PUT-arm units (up to 2 x 15 = 30) and is the
  mechanism by which the x4 multiplier reaches the n_rich >= 24 recruitment
  target. Pooling is registered for H4''' ONLY; H2-2 keeps the arms separate (it
  IS the between-arm contrast).

---

## 5. Dual-blind protocol + cross-vendor harness disclosure + one-shot rule

### 5a. Dual-blind core — UNCHANGED from v1.1/v2.0

Generation → **blind review** (reviewer sees only mutant code + operator spec +
PUT source; generator/vendor identity, arm label, SMS withheld) → **arbitration**
on disagreement → **freeze then score** (SMS computed only after review labels are
frozen and committed). Analyst blindness preserved. The rich-class slot
multiplier and any admission screen run at generation/admission, **before** any
SMS or graded share is computed, identically for every cell.

### 5b. Cross-vendor harness instantiation disclosure (NEW — supersedes the v1.1/v2.0 same-vendor disclosure)

Study-4 generation and review run through the cross-vendor gateway
(OpenAI-compatible; `BLTCY_BASE_URL` / `BLTCY_API_KEY` in the gitignored `.env`,
never committed). Confirmed working 2026-07-09 (200 + valid completion on all
four):

| Role | Gateway model id | Vendor lineage | Note |
|---|---|---|---|
| Same-source arm generator | `claude-fable-5` | Anthropic | all three slots in the same-source arm |
| Cross-source arm generators | `gpt-5.5` / `gemini-3.5-flash` / `grok-4.1` | OpenAI / Google / xAI | one lineage per slot; `grok-4.1` maps to `grok-4.3` (self-reported) |
| Blinded reviewer (both arms) | `claude-fable-5` | Anthropic | identical review protocol; never sees generator identity |
| Arbiter | `gpt-5.5` | OpenAI | different vendor from the reviewer |

- **Symmetric protocol.** Both arms are API-served through the one gateway, so
  there is **no harness-vs-API asymmetry** between arms — the only manipulated
  variable is the generator-vendor mapping of the three slots.
- **SSOT record.** The exact resolved model ids at generation time (including the
  `grok-4.1`→`grok-4.3` remap the gateway self-reports) are recorded in the
  campaign SSOT (`data/operator_campaign/…_log.json`) at run time.

### 5c. Same-vendor-review limitation — honestly noted (registered estimand)

The reviewer is `claude-fable-5` for BOTH arms, i.e. **single-vendor by design**.
This is deliberate and is the registered estimand's point: **the diversity under
test in H2-2 is GENERATION-side** (does mapping the three slots across three
non-Anthropic lineages move Delta-delta relative to a single-vendor generator?).
Holding the reviewer fixed across both arms **removes reviewer-vendor as a
confound** — a moving reviewer would confound generation-diversity with
review-diversity. Arbitration is cross-vendor (`gpt-5.5`) to avoid a single
instance adjudicating its own family's disagreements. We do **not** claim to have
tested reviewer-side vendor diversity; that is out of scope and stated as open,
not as a null.

### 5d. One-shot confirmatory rule — VERBATIM from v1.1/v2.0

**Confirmatory generation runs ONCE per the registered budget per arm** — the
per-cell mutant-count targets (including the x4 rich-class multiplier), seeds
(20260708), vendor role assignments, and prompt-template version pinned by file
hash. **Regeneration, cherry-picking cells or vendors, re-rolling an arm, or
moving any threshold after ANY confirmatory outcome is visible is a protocol
violation that must be reported as such** in §10 and in the paper. Confirmatory
analysis runs **only** through the pre-frozen scripts (§7). The calibration pilot
(§2b) is the *only* place live outcomes are seen before the confirmatory freeze,
and it may fix code defects only.

---

## 6. Industrial corpus — OUT OF SCOPE for Study 4

Study 4 does not touch the industrial legs (H2-3, H2-4), the two-tier census, or
the Tier-A/B firewall — all closed under Study 2 v1.1 §6 and unchanged.

---

## 7. Analysis plan — SSOT paths + pre-frozen scripts + §7b contracts

**SSOT paths (Study 4)**: `sms_track2_v7.json` (cross-source arm),
`sms_track2_v7_same.json` (same-source arm), `dualblind_delta_delta_v7.json`
(H2-2 verdict), `h4_graded_v7.json` (pooled H4'''-graded verdict),
`sms_track2_vC.json` (C-port pool) + `hlang_delta_vC.json` (H-LANG verdict);
power reference `power_study4.json`.

### 7b. Analysis-script contracts (sibling MUST pre-freeze before generation)

- **`scripts/compute_dualblind_delta.py`** — **serves H2-2 AS-IS; verified.** The
  frozen script already implements exactly the registered H2-2 estimand and the
  v1.1 three-way decision rule (`verdict_h2_2`: CI excludes 0 → CONFIRM; includes
  0 ∧ half-width <= 0.14 → BOUNDED_NULL; else UNDER_RECRUITED), the paired-role
  bootstrap (`paired_bootstrap_dd`, B = 10,000, seed 20260708), and the
  PRIMARY_CELLS_V3 aligned/cross split. **No code change is required**: Study 4
  invokes it **without** `--gated-h2-2` (cross-vendor credentials now exist),
  pointing `--cross` at `sms_track2_v7.json` and `--same` at
  `sms_track2_v7_same.json`, `--out data/results/dualblind_delta_delta_v7.json`.
  Its `STUDY1_DD = -0.009` sign-reversal flag is retained for the §8 construct
  check. (The `--gated-h2-2` path is simply not used.)
- **`scripts/compute_hlang_delta.py`** (NEW — pre-freeze required).
  - **Input**: the frozen C-port validated pool `sms_track2_vC.json` (per-cell
    `outcomes` = {file, label}); `PRIMARY_CELLS_V3` mapped to the C cells of the
    12 original PUTs.
  - **Computation**: split aligned (j = k) / cross (j != k) SMS over the 12 C
    PUTs by the primary-MP rule; two-sample Cliff's delta_C; one-sided 95%
    percentile-bootstrap lower bound (multinomial two-sample bootstrap,
    B = 10,000, seed 20260708) — byte-identical bootstrap to
    `compute_dualblind_delta.analyze_h2_1`.
  - **Output**: `data/results/hlang_delta_vC.json` with `cliffs_delta_C`,
    `one_sided_95_lower_bound`, `n_aligned`, `n_cross`, `n_puts = 12`, and
    `verdict = (one_sided_95_lower_bound > 0)`. Prints the licensed verdict string.
  - **Decision rule (frozen)**: confirm iff `one_sided_95_lower_bound > 0`.
- **`scripts/compute_h4_graded.py --pooled`** (flag contract — pre-freeze
  required).
  - **New flag**: `--pooled A.json B.json` (or repeated `--matrix`) admits the
    two Study-4 arm SMS pools and forms the graded aggregate over the **union**
    of rich PUT-arm units (each arm's rich PUT contributes its own PUT-mean; a
    rich PUT detected in both arms contributes two units). All other logic
    (per-mutant `s_m`, detected-only inclusion, pilot exclusion, B = 10,000
    bootstrap, seed 20260708, confirm iff `boot_lower_95 > 0.15`) is UNCHANGED
    from the v6 scorer.
  - **New output field**: `pooled_n_rich` = detected rich PUT-arm units; the
    verdict layer applies the §3.2 recruitment gate — if `pooled_n_rich < 24` the
    verdict is `UNDER_RECRUITED` (no bootstrap-threshold pass), else the frozen
    `boot_lower_95 > 0.15` rule with the two-way CONFIRM /
    MISATTRIBUTION-CONFIRMED reading of §3.2.
  - **Output**: `data/results/h4_graded_v7.json`.
  - **Decision rule (frozen)**: `pooled_n_rich >= 24` gate, then
    `boot_lower_95 > 0.15`.

All new/changed contracts are covered by offline synthetic-fixture tests in
`tests/analysis/` **before** generation, and each prints the registered licensed
verdict. **Seeds**: all bootstrap at 20260708. **Exclusion rules**
(analysis-time): pilots `{a2, b4}` excluded from every Python confirmatory
statistic; silent (flip = 0) mutants excluded from the graded share (no 0/0);
vacant cells excluded.

**Multiplicity — Study-4 family map**

| Family | Members | Correction | Confirmatory? |
|---|---|---|---|
| B — Source diversity | H2-2 (cross-vendor Delta-delta) | single test | yes |
| H — Attribution at adequate n | H4'''-graded (pooled share >= 0.15, gate n_rich >= 24) | single test | yes |
| L — Language invariance | H-LANG (delta_C > 0) | single test | yes |
| X — Exploratory | descriptive re-runs of H2-1'/H1'/H3'/H4''-strict on Study-4 pools, per-class graded breakdown, Python-vs-C magnitude comparison, Romano bands | per-test as labeled | no |

Each confirmatory family holds a single test; no within-family Holm needed and no
study-wide cross-family correction (per-family control under pre-registration;
Studies 2–3 families are closed). Confirmatory ↔ exploratory bright line
unchanged: anything discovered after freeze is exploratory by definition.

---

## 8. Decision matrix

| Hypothesis | Confirm licenses | Non-confirm licenses |
|---|---|---|
| H2-2 | "cross-source pooling moves delta by >= 0.20" (CI excludes 0) | BOUNDED NULL (no >= 0.20 effect under matched protocol — MR-design-is-the-lever CONFIRMED) / or UNDER-RECRUITED (CI wide) |
| H4'''-graded | at pooled n_rich >= 24: "declared MetaPattern carries graded attribution (share >= 0.15)" | at pooled n_rich >= 24 with share <= 0.15: "**misattribution CONFIRMED as a construct property**, not a small-sample artifact"; at n_rich < 24: UNDER-RECRUITED, factual |
| H-LANG | "the aligned>cross construct is language-invariant (delta_C > 0 in C)" | delta_C bound crossing 0: language-invariance does NOT replicate, reported as a genuine falsification |

**What would count against the construct (registered a priori)**: (i) an H2-2
CONFIRM whose Delta-delta sign reverses the Study-1 anchor (−0.009); (ii)
H4'''-graded share low at pooled n_rich >= 24 (this is the misattribution
construct-property confirmation, argued as such, not hidden); (iii) H-LANG
delta_C lower bound <= 0 despite 0.87 power (the construct is Python-specific, a
falsification of language-invariance).

---

## 9. Deviations-from-prior lessons table

| # | Prior lesson | Study-4 v1.0 closure | Trace |
|---|---|---|---|
| L13 | Cross-source vs cross-vendor conflation; H2-2 gated same-vendor not-run | H2-2 EXECUTED cross-vendor (4-lineage gateway); estimand + rule verbatim; reviewer held single-vendor to remove reviewer-vendor confound (generation-side diversity is the estimand) | §3.1, §5b, §5c |
| L15 | A hypothesis formed after seeing prior data cannot be confirmed on that data | fresh v7/vC generation; v4/v5/v6 used for calibration only, stated openly | §0.1, §2c |
| L17 | Study-3 H4''-graded thin (n_rich = 6) → fragile NOT_CONFIRMED | x4 rich-class slot multiplier + pre-declared two-arm pooling → projected pooled n_rich 26.1 (P(>=24) = 0.92); recruitment gate blocks threshold-moving | §2a, §3.2, §4b |
| L18 | Bold construct claims must be pre-committed and falsifiable | H-LANG frozen NOW (blind to the C-port outcome), one-shot, delta_C > 0 at 0.87 power; a non-replication is reported as a falsification, not hedged | §3.3 |

---

## 10. Amendments log + incident ledger (append-only, dated)

**Registration #1 — 2026-07-09 (this document, Study-4 v1.0).** Registered three
confirmatory families on fresh data that does not yet exist: **H2-2** cross-vendor
dual-blind source diversity (finally executable via the four-vendor gateway;
same-source `claude-fable-5` vs cross-source `gpt-5.5`/`gemini-3.5-flash`/
`grok-4.1`; blinded reviewer `claude-fable-5`, arbiter `gpt-5.5`; estimand +
three-way decision rule VERBATIM from v1.1; power 0.793 @ n=28, marginal, honestly
reproduced); **H4'''-graded** rich-class re-test (x4 per-operator slot multiplier
on C/D PUTs in both arms + pre-declared pooling → projected pooled n_rich 26.1,
P(>=24) = 0.92; same graded measure + 0.15 bar on the pooled arms; recruitment
gate → UNDER-RECRUITED if detected pooled n_rich < 24; sharp interpretation
pre-declared: low share at adequate n = misattribution CONFIRMED as a construct
property); **H-LANG** cross-language invariance (bold NOETHER-derived claim:
delta_C > 0 on a C port of the 12 original PUTs; power 0.8735 @ n=12 from the v5
delta~0.43 DGP; C_PORT_SPEC forthcoming, hypothesis frozen now). Pre-froze the
analysis-script contracts (`compute_dualblind_delta.py` serves H2-2 as-is;
`compute_hlang_delta.py` new; `compute_h4_graded.py --pooled` flag). Did NOT
re-register the settled H2-1'/H1'/H3'/H4''-strict. One-shot rule per arm; reused
the `{a2, b4}` calibration-pilot protocol with four-vendor gateway pilot duties.
All changes pre-Study-4-data; v4/v5/v6 used for design calibration only (§0.1).
Power/feasibility SSOT: `data/results/power_study4.json` (seed 20260708).

**Incident ledger (continued from P9).** Prior ledger: Incident #1 (Study-1
v3-pool wipe + git restore), P4–P7 (Study-2/3 code fixes), P8 (v5 CF/TF screen
silent no-op), P9 (v6 all-family screen tooling wiring). Study 4 opens the ledger
at **P10+** for any pilot-triggered code defect (gateway wiring, per-vendor
`max_tokens` handling — notably `gemini-3.5-flash` requiring `max_tokens >= 2000`
for reasoning-token consumption — fence-stripping across four vendor response
formats, `grok-4.1`→`grok-4.3` id remap logging, slot-multiplier / `--pooled`
wiring, review-packet vendor-tag stripping). Each P10+ entry is appended here and
in `docs/prereg_v2/PILOT_LOG.md` **before** the confirmatory run, verified
code-level (never protocol-level).

*(No further amendments. Any post-freeze change — a pilot-triggered code fix, a
vendor id remap, a seed correction — is appended here with date and rationale
before the confirmatory run.)*
