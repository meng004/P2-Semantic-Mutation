# Independent TOSEM review (LOOP iteration 3) + response ledger

> Reviewer: independent EIC-role academic review of the executed DVE artifacts (HEAD d96b9f0).
> Verdict: **Reject as a paper (none exists); strong Conditional Pass as pre-registration + instrument-validation stage. NOT at TOSEM stable-acceptance.**
> This is the honest, expected verdict: only M0 + M-infra are executed; the confirmatory experiment (M1–M8) and manuscript do not exist.

## Reviewer's reproduction (independent)
- `pytest tests/dve/ -q` → 20 passed (confirmed).
- power sim `--n-sim 500` → type-I mean 0.0505, identical 80-family conservative frontier. **M0 numbers are real.**

## Response ledger

| Item | Reviewer point | Action taken this iteration | Status |
|---|---|---|---|
| P0-1 | Confirmatory experiment (M1–M8) unrun; no manuscript | None possible — requires real fault pool + holdout; honestly OPEN | OPEN (cannot fabricate) |
| P0-2 | Independent second reviewer does not exist | None possible — recruitment gate; disclosed threat | OPEN (cannot fabricate) |
| P0-3 | M0.5 formal audit unexecuted | None possible — external formal-methods reviewer | OPEN (cannot fabricate) |
| P1-1 | Power sim is Gaussian model of a bounded endpoint; priors overstated | Added `run_bounded_check` bounded-proportion model with ceiling compression; power 0.79–0.85 at 80 families corroborates Gaussian sizing; prereg §4 caveat made explicit that σ/ICC are assumed, not measured | **ADDRESSED** |
| P1-2 | Confounded S1-vs-S3 inside conjunctive "full confirmation" | Frozen reporting rule: lead with S1-vs-S2; S1-vs-S3 only "potency+transfer"; S1>S3-only = "no clean gain" (prereg amendments) | **ADDRESSED** |
| P1-3 | S2 can degenerate to a starved baseline | Pre-registered per-PUT syntactic-richness floor (≥20 survivors, ≥3 operator families); sub-floor PUTs reported separately, excluded from S1-vs-S2 confirmatory statistic | **ADDRESSED** |
| P1-4 | Recruitment feasibility unproven (≥160 families, new PUTs) | Acknowledged in risk register; genuine open risk, cannot be discharged without doing M1 | OPEN (honest) |
| P1-5 | Mechanism-class granularity is a researcher DoF | Declared integrity threat; taxonomy frozen at M1.5a + published verbatim; H3' re-runs under coarser/finer taxonomy (prereg amendment) | **ADDRESSED** |
| P2-1 | Sampled sign-flip path missing (ge+1)/(n_perm+1) | Fixed in `power_of`; sampled-path type-I recentered 0.0499 (was slightly anti-conservative, max 0.063→0.0615 MC noise) | **FIXED** |
| P2-2 | Redundant greedy tie-break | Simplified `_greedy_set_cover`; 20 tests still pass | **FIXED** |
| P2-3 | Dead code in dry_run (`if rng.random()<1.0: pass`) | Removed | **FIXED** |

## Net effect on the verdict
The reviewer's own conclusion already anticipates this: addressing the pre-freeze
items (P1-1/2/3/5 + P2) is exactly what is permissible before the freeze, and it
has been done. The stable-acceptance blockers that remain (P0-1..3, P1-4) are all
**execution/recruitment gates**, not design gaps — they cannot be closed in this
session without fabricating data, which the goal forbids. Stable acceptance stays
**NOT assessable until M5 produces a real holdout result and W4–W6 produce a
manuscript.**
