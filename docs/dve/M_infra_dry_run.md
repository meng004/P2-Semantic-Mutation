# M-infra execution record — frozen machinery + end-to-end dry-run (I4)

> LOOP iteration 2. Goal: build the pre-registered analysis machinery whose
> correctness is checkable now, and rehearse the whole pipeline on synthetic
> worlds to certify its operating characteristics BEFORE any real holdout.
> Date: 2026-07-10.

## What was actually built and verified (real, reproducible)

| Module | Purpose | Tests |
|---|---|---|
| `src/p2/dve/endpoint.py` | FDS endpoint, PUT-level sign-flip, two-level bootstrap CI | 5 |
| `src/p2/dve/strategies.py` | S1–S4 greedy portfolio selectors | 4 |
| `src/p2/dve/family_registry.py` | nested `(PUT, mechanism)` families, freeze+hash | 3 |
| `src/p2/dve/split.py` | SHA-256 commitment + one-shot holdout guard | 2 |
| `tests/dve/` total | | **20 passing** |

Command: `PYTHONPATH=src .venv/bin/python -m pytest tests/dve/ -q` → 20 passed.

## The dry-run and the four design findings it surfaced (the real value)

The end-to-end dry-run (`scripts/dve/dry_run_pipeline.py`) ran the whole
pipeline on synthetic worlds with a tunable `transfer` parameter (how much the
dev signal carries holdout information). Getting a *coherent* validation
required four iterations; each failure was a genuine design finding, not a
coding slip, and each is fed back into the pre-registration.

1. **Potency confound (v0, preserved as `*_v0_confounded.py.bak`).**
   Comparing S1 to S2/S3 baselines built from holdout-independent signals gave
   apparent S1 superiority ≈ 0.44 that was *insensitive to transfer*
   (NULL 0.445 vs SIGNAL 0.484). Cause: S1 intrinsically selects broadly-potent
   MRs; a baseline that ignores kills loses for a reason unrelated to signal
   transfer. → **Design consequence:** S1-vs-S3 (coverage) is confounded by
   potency; the clean confirmatory comparison is **S1-vs-S2** (kill-signal vs
   kill-signal). S1-vs-S3 is reported but interpreted as potency+transfer.

2. **Label-permutation is not a valid null for a degree-driven selector (v1).**
   Permuting dev family labels left greedy set-cover picks unchanged (it is
   degree-invariant), so Δ≡0. This exposed that "transfer" decomposes into
   (i) stable MR-level potency (a *legitimate* value source for S1) and
   (ii) mechanism-specific alignment.

3. **R0-redundancy / coverage-diversification confound (v2).**
   Even with equipotent MRs, S1 beat naive random at transfer=0 (Δ≈+0.13)
   because "residual" is defined relative to R0, so S1 always covers non-R0
   classes while random wastes picks on R0-covered ones. → **Design
   consequence:** the confirmatory comparator must be **coverage-matched**
   (pick k distinct non-R0 classes), not naive random, so the only remaining
   difference is *which* non-R0 classes — the thing transfer governs.

4. **PUT independence is a validity precondition for the sign-flip test (v3).**
   A single *global* portfolio shared across PUTs correlated the per-PUT
   differences (all same-sign per world), inflating type-I to ≈ 0.17. → This is
   exactly why plan §3.5 selects **per-PUT** from `R_valid(P) \ R_0(P)`. With
   per-PUT selection restored, PUTs are independent replicates and the test is
   valid.

## Final validated operating characteristics (per-PUT selection, coverage-matched comparator)

`scripts/dve/dry_run_pipeline.py --n-worlds 1500`, base config
n_put=12, n_fam=16, n_mech=24, k0=4, k=5:

| transfer | mean Δ(S1 − matched-random) FDS | reject @0.05 |
|---|---|---|
| 0.00 (null) | +0.0015 | **0.044** (type-I ≈ nominal) |
| 0.30 | +0.0057 | 0.045 |
| 0.85 | +0.0140 | 0.053 |

**Reading.** (a) Type-I is controlled at 0.044 — the pipeline does NOT
manufacture false positives when the dev signal carries no holdout information.
(b) Δ rises monotonically with transfer — the pipeline detects real signal in
the correct direction. (c) Power is low here *by design and consistently*: the
toy transfer effect (~0.014 FDS) is an order of magnitude below the MID (0.10),
so the M0 power curve correctly predicts near-nil power at this effect size.
The two analyses agree.

## Plan-conformance check (LOOP discipline)

| Plan requirement | Conformance |
|---|---|
| §3.4 SHA-256 commitment + one-shot holdout | ✅ `split.py`, tested |
| §3.3 nested `(PUT, mechanism)` families, freeze | ✅ `family_registry.py`, tested |
| §3.6 FDS size-insensitive endpoint | ✅ `endpoint.fds`, tested |
| §3.6 PUT-level exact sign-flip | ✅ `endpoint.signflip_test`, validated |
| §3.5 per-PUT selection | ✅ **confirmed necessary** by finding 4 |
| §3.6 S1 vs joint baselines S2,S3 | ⚠️ refined: S1-vs-S2 clean; S1-vs-S3 potency-confounded (finding 1) |

## Design amendments fed back (pre-registration deltas)

- Elevate **S1-vs-S2** to the decisive confirmatory comparison; keep S1-vs-S3
  but pre-register its potency-confound interpretation.
- The confirmatory decision-value estimand must be measured against a
  **coverage-matched** comparator, not naive random (random stays as the S4
  sanity floor).
- State explicitly that **per-PUT selection** is a validity precondition of the
  PUT-level sign-flip test (already in §3.5; now justified empirically).

## Honest status of M-infra

- **Done and verified:** all four modules, 20 unit tests, end-to-end dry-run
  with calibrated type-I and correct-direction response.
- **Not done (cannot be fabricated):** the real certified fault pool, real MR
  catalogue, real kill matrices. The dry-run uses synthetic worlds solely to
  certify the instrument; it makes NO claim about whether the real SMS signal
  has decision value — that is the open empirical question the frozen
  experiment exists to answer.
