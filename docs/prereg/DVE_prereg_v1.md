# Pre-registration: Decision-Value Experiment (DVE) v1

> Plan of record: `research/paper-draft-plan-mr-adequacy-tosem.md` v1.1.1 (frozen after EIC round-3 conditional pass).
> Status: **DRAFT — awaiting EIC confirmation to freeze.** On freeze this file is tagged and its SHA-256 recorded; thereafter only power-simulation-driven sample sizing may change (round-3 freeze clause).
> Milestone: M0 (design freeze). This document is the single source of truth for every frozen decision; the paper's Method section is a tense-rewrite of it.

This pre-registration is written *before* any cross-execution between the semantic-fault branch and the MR branch. It fixes the hypotheses, endpoint, analysis, sample size, certification rules, and stopping rules so that the confirmatory DVE-W result cannot be reshaped after the holdout is opened.

---

## 1. Objects and roles (plan §3.2)

- **PUTs**: 12 existing scientific-computing PUTs (`src/p2/puts/`) re-frozen with new blinded roles, plus 8–12 newly recruited PUTs from open-source scientific kernels with locatable historical bug-fix commits. 2–3 new PUTs are held out whole for the leave-PUT-out transfer arm (DVE-T).
- **Roles** (programmatic isolation under a single-author reality via time-locks + independent git branches + hash commitments): mutation generator, semantic certifier, MR designer, executor, holdout custodian, unblinding analyst. Independent audit (§5) and D-level adjudication are performed by a second reviewer. The "one person acting several roles across time" limitation is disclosed as a threat.

## 2. Frozen hypotheses (plan §3.6)

Primary endpoint: **FDS** (family detection score) = family-equal mean over holdout families of the per-family instance-detection proportion
`det(R, g) = mean_{m in I_g} det_R(m)`.

Primary contrast: `Δ_{S1,S} = FDS(R0 ∪ S1(k*)) − FDS(R0 ∪ S(k*))`, for comparator strategies S ∈ {S2, S3}.

- **H-DV (primary, confirmatory, joint-baseline family)**: `Δ_{S1,S2} > 0` AND `Δ_{S1,S3} > 0`, Holm-corrected. Both hold = full confirmation; exactly one = partial confirmation (pre-registered graded wording); neither = no decision-value gain (framework demoted to diagnostic per §3.9).
- **MID two-tier rule**: (a) statistical superiority = reject `H0: Δ ≤ 0`; (b) practical importance = reject `H0: Δ ≤ MID` (one-sided lower confidence bound > MID). **MID = 0.10 FDS**, frozen after the power simulation below. Point estimate exceeding MID without (b) may NOT be reported as exceeding the MID.
- **H-DV-T (secondary, confirmatory)**: on DVE-T, `S1-T+` vs `S2-T`/`S3-T` same-form difference > 0.
- **Sanity**: S1 exceeds the pre-registered 90th percentile of the S4 random-selection distribution; failure triggers the §3.9 signal-chain failure analysis.
- **H1' (distinctiveness)**, **H3' (robustness)**: per plan §3.6.

Original strict-sufficiency claim (SMS=1) is NOT a headline hypothesis; it is reported as an RQ4 diagnostic.

## 3. Frozen primary analysis (plan §3.6; round-3 amendment 1)

**PUT-level sign-flip randomization test.** Per PUT p aggregate family paired
differences to `d_{p,S} = mean_{g∈G_p}[det(R0∪S1(k*),g) − det(R0∪S(k*),g)]`.
Test statistic `t = mean_p d_{p,S}` (PUT-equal weight). The exchangeable unit
is the whole PUT (families within a PUT are correlated). For n_PUT ≤ 20 the
test **exactly enumerates** all `2^{n_PUT}` sign assignments (e.g. `2^17 =
131,072`); no Monte-Carlo or asymptotic-normal approximation. Holm correction
over {S1 vs S2, S1 vs S3}. The MID-tier test applies the same sign-flip frame
to the shifted statistic `t − MID`.

Effect size / CI: family-level risk difference via two-level bootstrap
(resample PUTs, then families within PUT; BCa). GLMM
`det ~ strategy + (1|PUT) + (1|family)` is secondary with a **pre-registered
singular-fit fallback = the sign-flip / bootstrap above** (the v4 singular-fit
problem is not decided ad hoc).

Analysis implementation is frozen as code (`scripts/dve/`, `src/p2/dve/`) with
commit hashes recorded before unblinding. The exact sign-flip primitive is
unit-tested (`tests/dve/test_power_simulation.py`).

## 4. Sample size — grounded in the executed power simulation

The power simulation (`scripts/dve/power_simulation.py`, results
`data/dve/power_simulation_results.json`, seed 20260710, 3000 sims/scenario)
uses a two-level random-effects generative model
`diff(g) = μ + u_p + e_g` with PUT ICC ∈ {0.1,0.2,0.3} and family-diff SD
σ ∈ {0.15,0.20,0.25} (σ grounded on the v4 pilot cell-SMS spread
std=0.211, `data/results/sms_track2_v4.json`), evaluated under the exact
PUT-level sign-flip test.

**Type-I calibration (real):** at μ=0 the empirical rejection rate is
mean **0.0508** (min 0.0403, max 0.0630) against nominal 0.05 — the test is
correctly calibrated.

**80% power frontier at true effect μ = MID = 0.10 FDS (holdout families):**

| σ (family-diff SD) | ICC 0.1 | ICC 0.2 | ICC 0.3 |
|---|---|---|---|
| 0.15 | 24 | 24 | 24 |
| 0.20 | 36 | 48 | 60 |
| 0.25 | 60 | 68 | **80** |

**Frozen sizing decision.** The confirmatory target is the **conservative
regime (σ=0.25, ICC=0.3): 80 holdout families**, i.e. **20 PUTs × 4 holdout
families each**. With the 50:50 dev:holdout family split (plan §3.4) this
implies **≥ 160 A–C certified families in total** and correspondingly
≥ 500–800 certified mutants.

> **Amendment to plan §3.3 (permitted by the freeze clause).** Plan v1.1.1
> §3.3 stated "A–C certified family ≥ 80" as a *total*. The executed power
> simulation shows 80 must be the *holdout-side* count under conservative
> assumptions; the total certified-family target is therefore raised to
> **≥ 160** (dev + holdout). If, after M1, the achieved σ (estimated from the
> dev-side family-diff spread) lands in the moderate regime (σ ≤ 0.20), the
> holdout target may drop to 40–48 families (total ≥ 80–96), re-frozen once
> and disclosed. Under-recruitment triggers the pre-registered scope-narrowing
> rule (fewer mechanism classes, never lower certification standards).

## 5. Certification rules and stratified independent audit (plan §4.1)

- Evidence grades A/B/C → primary denominator; D → sensitivity-only; "inadmissible" row (LLM/author intent only, or killed only by some MR) never enters any denominator.
- Operational-equivalence estimator sample size, reference oracle, tolerance frozen here; sensitivity into RQ5.
- **Audit timing (round-3 amendment 2), two segments:**
  1. *Before split (boundary-changing):* registry build → second-reviewer family-boundary + fidelity audit → resolve all merges/splits → **freeze registry** → only then dev/holdout random split + cryptographic commitment. No family merge/split after the split.
  2. *After split, before unblinding (non-boundary):* certificate-correctness re-checks (A/B/C rerun, REJECTED, UNCERTAIN, LLM, multi-effect) blinded to dev/holdout assignment; may only move objects between primary↔sensitivity pools, never alter family structure.
- Per-layer κ / agreement thresholds (κ ≥ 0.6 or agreement ≥ 0.9, frozen on freeze day); failure → whole-layer re-review → still failing → objects demoted out of primary + disclosed.

## 6. Family registry (round-3 amendment 2)

Family ID is nested in PUT: `(PUT, mechanism/template cluster)`, matching
`mutant ⊂ family ⊂ PUT`. Cross-PUT similar mechanisms share a **mechanism
class** (used for quota and DVE-T transfer mapping), NOT a family ID. Registry
frozen (hash recorded) before any split.

## 7. Strategies (frozen as code, plan §3.5–§3.6)

Selection space `R_valid(P) \ R_0(P)` where
`R_valid(P) = {r ∈ R_cand(P): AVP(P,r)=pass}` (original-program false-positive
MRs removed from the space). Budget k* = 4 (swept {2,4,6,8} in RQ5), to be
confirmed on the pilot rehearsal before freeze.

- **S1 residual-guided** (treatment): greedy set-cover of dev residual families `U(R0, M_dev)`, family-counted increments, ties by execution cost.
- **S2 classical-MS-guided** (joint primary baseline): same greedy over surviving syntactic (Cosmic Ray default first-order, config frozen) mutants of R0.
- **S3 MR-coverage-guided** (joint primary baseline): greedy over the pre-registered MR-coverage metric; no mutant information.
- **S4 random / generic** (sanity-check): 1000 random draws + a fixed generic reference.

**Dry-run design amendments (M-infra, `docs/dve/M_infra_dry_run.md`).** The
end-to-end I4 rehearsal certified the instrument (type-I 0.044 at zero transfer;
monotone response to real signal) and surfaced three confounds, now frozen into
the confirmatory reading:

1. **S1-vs-S2 is the decisive confirmatory comparison** (kill-signal vs
   kill-signal, a fair fight). S1-vs-S3 is reported but pre-registered as
   potency+transfer, because S1 intrinsically prefers potent MRs and S3 does not
   target kills.
2. The confirmatory decision-value estimand is measured against a
   **coverage-matched comparator** (k distinct non-R0-covered classes), because
   "residual" is defined relative to R0 and a naive-random comparator would
   miscredit coverage diversification as transfer (dry-run showed Δ≈+0.13 at
   zero transfer against naive random). Naive random remains only as the S4
   sanity floor.
3. **Per-PUT selection is a validity precondition** of the PUT-level sign-flip
   test: a global shared portfolio correlates the per-PUT differences and
   inflated type-I to ≈0.17; per-PUT selection (§7 selection space) restores
   nominal type-I.
- **DVE-T**: S1-T+ (target-informed: reads dev kill matrix + target-PUT Fault-Card mechanism-class distribution), S1-T0 (distribution-blind, exploratory), S2-T/S3-T/S4-T comparators.

## 8. Stopping / one-shot rules (plan §3.1, §3.9)

- Holdout opened **once**, after all strategy outputs are hash-sealed. Full pipeline rehearsed on pilot (v4) data first (I4 dry-run).
- Null / partial / DVE-T-fail / sanity-fail / ceiling-too-low / under-recruitment interpretations are all pre-registered (§3.9); endpoint, budget, denominator may NOT be swapped after seeing results.
- Any post-freeze change is a protocol deviation disclosed in the paper's Deviations section.

## 9. Artifacts committed at freeze

`docs/prereg/DVE_prereg_v1.md` (this file), `scripts/dve/power_simulation.py`,
`data/dve/power_simulation_results.json`, `tests/dve/`, family-registry schema,
split-committer, strategy selectors — all hash-recorded. Reference:
`docs/dve/M0_power_and_signflip_validation.md`.
