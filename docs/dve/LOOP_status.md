# DVE execution LOOP — status tracker

> Honest, evidence-based status of executing plan v1.1.1. Updated each LOOP iteration.
> Rule: only tasks with real executed artifacts are marked done; recruitment/administrative
> and substantive-data gates that cannot be fabricated are marked OPEN, not faked.

## Milestone ledger

| Milestone | Content | Status | Evidence |
|---|---|---|---|
| M0 | Pre-registration + two-level power simulation | **DONE (computational parts)** | `scripts/dve/power_simulation.py`, `data/dve/power_simulation_results.json`, `docs/dve/M0_power_and_signflip_validation.md`; type-I 0.0508 @ nominal 0.05 |
| M0 (freeze) | EIC confirmation to freeze pre-registration | OPEN | requires EIC sign-off (external) |
| M0.5 | Independent formal audit of the framework | OPEN | requires external formal-methods reviewer |
| M-infra | Frozen analysis machinery + I4 dry-run | **DONE (verified)** | `src/p2/dve/*.py`, `tests/dve/*` (20 passing), `docs/dve/M_infra_dry_run.md`; type-I 0.044, monotone response |
| M1 | Build + certify the A–C fault pool (≥160 families) | OPEN | requires domain-expert fault-card construction + certification |
| M1.5a | Family-boundary + fidelity audit → registry freeze | OPEN | requires second reviewer |
| M2 | family-level split commitment + DVE-T PUT freeze | OPEN | depends on M1 |
| M2.5 | Post-split certificate audit (8 strata) | OPEN | requires second reviewer |
| M3 | R_cand freeze + FP screen + R0 | OPEN | requires MR designer (blinded) |
| M4 | dev cross-execution + syntactic pool + strategy code freeze | OPEN | depends on M1–M3 |
| M5 | unblinding + one-shot holdout evaluation | OPEN | depends on M4 |
| M6 | analysis + draft | OPEN | depends on M5 |
| M7 | closure-ledger final verification | OPEN | depends on all |
| M8 | submission package | OPEN | depends on all |

## What is genuinely established (real execution)

1. The pre-registered **PUT-level sign-flip test is calibrated** (type-I 0.0508
   in the power sim across 108 null scenarios; 0.044 end-to-end in the dry-run).
2. **Sample size is grounded**: 80% power at MID=0.10 FDS needs 24–80 holdout
   families depending on σ/ICC; conservative target 80 holdout → ≥160 total
   certified families.
3. The **analysis machinery works and is unit-tested** (20 tests): FDS endpoint,
   sign-flip, bootstrap, nested family registry with freeze/hash, SHA-256 split
   commitment with one-shot guard, S1–S4 selectors.
4. The **I4 dry-run certified the instrument** and self-caught four design
   confounds (potency; degree-invariant permutation; R0-redundancy; PUT
   independence), all fed back into the plan and pre-registration.

## What is NOT established (must not be claimed)

- Whether the real SMS/residual signal has ANY decision value — this is the open
  empirical question the confirmatory experiment (M1–M5) exists to answer, and
  it has not been run. No Results section exists.
- Whether ≥160 A–C certified families can actually be constructed at the frozen
  standard.
- All second-reviewer / domain-expert / EIC-sign-off gates.

## LOOP iteration 3 — independent TOSEM review + response

Independent academic review (`docs/review_2026-07-10/r2_independent_tosem_review_and_response.md`)
verdict: **Reject as a paper / strong Conditional Pass as pre-registration stage /
NOT at TOSEM stable-acceptance.** Reviewer independently reproduced the 20 tests
and the power-sim frontier (M0 numbers real). All pre-freeze-permissible items
addressed this iteration: P1-1 (bounded-endpoint power corroboration), P1-2
(S1-vs-S2 as decisive reporting rule), P1-3 (S2 richness floor), P1-5 (taxonomy
integrity threat), P2-1/2/3 (code fixes). Remaining blockers P0-1..3 and P1-4 are
execution/recruitment gates that cannot be closed without fabricating data.

## Honest bottom line

The project is at **"pre-registration frozen-candidate + instrument validated,
awaiting data collection."** This is a legitimate, well-founded pre-registration
stage — but it is NOT a TOSEM stable-accept paper, because a confirmatory
empirical paper requires the confirmatory data, which do not yet exist and
cannot be fabricated. The academic-reviewer assessment (LOOP iteration 3)
records the formal verdict.
