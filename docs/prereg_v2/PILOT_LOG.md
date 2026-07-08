# Calibration-Pilot Log — Study 2 `{a2, b4}` (amendment appendix)

**Referenced from** `PREREGISTRATION_STUDY2_v1.1.md` §2b (Calibration pilot) and
§10 (Amendments log). This is the append-only appendix the registration requires:
*"Any pilot-triggered change is logged in the §10 amendment appendix before the
confirmatory run begins."*

**Scope constraint (registration §2b firewall).** The pilot may fix **code
defects only** — harness bugs, tooling, determinism, blinding. It may **never**
change thresholds, estimands, DGP calibration, primary-MP assignment, or the
28-PUT confirmatory roster. Every entry below is verified code-level: it changes
*how the registered machinery is invoked or guarded*, never *what is measured or
how a hypothesis is decided*. None of these fixes read or depend on any Study-2
outcome.

Date: 2026-07-08. Branch: `claude/paper-journal-acceptance-kxpveo`.
Pilot PUTs: `a2` (LU determinant, original, deterministic; ops CE1/OS1/SI1),
`b4` (bootstrap resampling, new, stochastic; ops CE1/OS1/**TF1**).

---

## Incident #1 (NEAR-MISS) — Study-1 v3 pool deletion + recovery

**What happened.** The coordinator invoked
`scripts/build_pools.py --puts a2,b4 --pool-suffix _pool_v5`. The script parsed
**no** CLI arguments, so `--puts` and `--pool-suffix` were silently ignored. It
was driven only by the `POOL_VERSION` env var, which defaulted to `v3`. The v3
path resolves the cache to `data/operator_campaign/cache` — a directory that
does **not exist / is empty** in this checkout — and unconditionally
`shutil.rmtree`'d every existing `data/mutants/{put}_pool_v3/` before rebuilding.
It therefore wiped the **12 tracked, frozen Study-1 v3 pools** and rebuilt them
**empty** from the empty cache.

**Recovery.** `git restore data/mutants/` restored all pools from the tracked
tree. Verified intact after recovery: `a1_pool_v3` = 20 files (19 `.py` +
manifest), `d3_pool_v3` = 20 files. No Study-1 artefact was lost; the wipe never
reached a commit.

**Root cause.** Three compounding tooling defects (D1–D3 below): no argument
parsing, unconditional delete-before-select, and an empty-cache blind spot.

**Why code-level, not protocol-level.** Study-1 v3 pools are immutable frozen
artefacts. Restoring and never-again-touching them *preserves* the registration;
it does not alter any Study-2 threshold or estimand.

---

## Defect D1 — `build_pools.py` ignored all CLI arguments

- **Defect.** No `argparse`. `--puts`, `--pool-suffix`, `--pool-version`,
  `--cache-dir` were all silently discarded; behaviour was governed only by the
  `POOL_VERSION` env var, and the PUT set was **hardcoded to the 12 Study-1
  PUTs**. A caller asking for `{a2, b4}` at `v5` got "all 12 PUTs at `v3`".
- **Root cause.** Script written as a top-level loop with env-only configuration
  and a literal `PUTS = [...12...]` list; new-PUT / new-version invocation was
  never wired.
- **Fix.** Full `argparse` interface: `--pool-version` (env `POOL_VERSION` kept
  as backward-compatible default), `--puts` (comma list; auto-detected from the
  cache when omitted — no hardcoded list), explicit `--cache-dir`,
  `--mutants-dir`, `--pool-suffix` (validated against the version), `--seed`.
  Logic refactored into importable `build_pools(...)` / `version_spec(...)` /
  `puts_in_cache(...)` behind a `main()` guard.
- **Why code-level.** Argument plumbing and PUT auto-detection change *invocation
  ergonomics*, not the selection algorithm (`pool_builder.select_mutants_for_put`
  is unchanged) nor any registered quantity.

## Defect D2 — no `v5` in the version maps (wrong N + wrong cache)

- **Defect.** `_N_MAP` / `_SUFFIX_MAP` lacked a `v5` key, so a `v5` request fell
  back to `v2` semantics (`N=12`, suffix `_pool`, cache `cache`) — the wrong
  count, wrong directory, and wrong (Study-1) cache.
- **Root cause.** Maps enumerated only `v2/v3/v4`; the Study-2 confirmatory /
  pilot version was never registered in the tooling.
- **Fix.** Added a single `_VERSION_SPEC` table with `v5 → (suffix=_pool_v5,
  cache=cache_cross, N=30, frozen=False)`. **N=30 mirrors `v4` exactly** — the
  registration powers Study-2 at the same 30-mutant selection as the v4
  cross-source arm (v4 pool manifests carry `n_target=30`; the CAMPAIGN_RUNBOOK
  §2.3 parenthetical "v4 = 12" is a documentation typo contradicted by the built
  artefacts). Because both pilot PUTs supply only 27 candidates
  (3 ops × 3 sources × K=3), selection takes **min(N, available) = 27**; N=30 is
  never binding for the pilot.
- **Why code-level.** Restores the registered pool size and cache for v5; it does
  not change the registered N (30), it *encodes* it.

## Defect D3 — unconditional delete + empty-cache blind spot (the incident)

- **Defect.** `if pool_dir.exists(): shutil.rmtree(pool_dir)` ran **before**
  selection and with **no** guard on cache emptiness or on the version of the
  directory being deleted. An empty/absent cache silently produced empty pools
  that overwrote populated ones (Incident #1).
- **Root cause.** Delete-then-rebuild ordering with no safety preconditions.
- **Fix (four guards).**
  1. **Empty-cache refusal** — refuses to run when the cache has zero
     `*_attempt*.py` files, unless `--allow-empty`.
  2. **No empty-overwrite** — selection runs *before* any delete; a per-PUT empty
     selection is **skipped**, leaving the existing pool untouched (unless
     `--allow-empty`).
  3. **Wrong-version deletion guard** (`_assert_version_match`) — refuses to
     `rmtree` any directory whose suffix ≠ the requested version's suffix, and
     whose residual is not a bare PUT id. A `v5` build can only ever remove a
     `_pool_v5` dir, never a frozen `_pool_v3` one.
  4. **Frozen-version guard** — refuses to (re)build `v2`/`v3` (frozen Study-1
     versions) unless `--allow-frozen` is passed explicitly.
- **Why code-level.** Pure safety interlocks around immutable Study-1 artefacts;
  they cannot alter any Study-2 measurement.

## Defect D4 — `sms_campaign.py` had no `v5` pool resolution (silent Study-1 fallback)

- **Defect.** `evaluate_cell`'s auto-resolution knew only `v4`/`v3`/`v2`. With
  `POOL_VERSION=v5` it fell through to `elif pool_v3.exists()` and scored the
  **frozen Study-1 `_pool_v3`** mutants — a silent, wrong-pool SMS that would
  have looked plausible (a2/b4 both have Study-1 v3 pools).
- **Root cause.** Same missing-`v5` omission as D2, on the scoring side.
- **Fix.** Extracted `resolve_pool_dir(put_id, pool_version=None)`. For the
  Study-2 versions `v4`/`v5` it is **strict**: it returns `{put}_pool_{version}`
  and **never** falls back to a Study-1 pool. If the version dir is absent,
  `_load_mutants` yields empty and the cell reports `inst=0` — a **visible**
  failure rather than a silently-wrong score. Added `--pool-version` (overrides
  the env for the run) and a `--puts` filter so a track run can be restricted to
  the pilot subset (→ 10 cells for `{a2,b4}` × 5 MP).
- **Why code-level.** Points scoring at the correct pool and fails loudly when it
  cannot; the SMS/AVP/equiv machinery and the primary-MP rule are untouched.

---

## Pilot pipeline run record (post-fix)

| Step | Command (abridged) | Result |
|---|---|---|
| Build v5 pilot pools | `build_pools.py --puts a2,b4 --pool-version v5` (filter ON, seed 20260708) | `a2_pool_v5` = **27**, `b4_pool_v5` = **27** (min(30, 27 available)) |
| CF/TF single-stratum screen (b4 TF1) | screen exercised on the leakage-relevant family, 20-repeat AVP | **9 pass / 0 fail** of 9 (all flip=0, single-stratum) |
| SMS, 10 pilot cells | `sms_campaign.py --track 2 --puts a2,b4 --pool-version v5 --out …_v5_pilot.json` | all 10 cells populated (inst=27 each; no empty pools, no errors) |
| Review-packet export | `cross_source_campaign.py --export-review-packets … --cache-dir cache_cross` | **54** blinded packets (a2:27 + b4:27); generator identity / arm / SMS omitted |

**Output isolation.** Pilot SMS lands in `data/results/sms_track2_v5_pilot.json`.
The confirmatory SSOT `data/results/sms_track2_v5.json` (the path the pre-frozen
analysis scripts consume) is **not created** by the pilot — verified absent. The
pilot pool dirs `{a2,b4}_pool_v5` are pilot-only; the confirmatory roster (§2c)
excludes `{a2,b4}`.

**Firewall attestation.** No threshold, estimand, DGP, primary-MP assignment, or
roster was changed. Pilot outcomes were used only to exercise and debug the
tooling above. Confirmatory generation has **not** begun.

## Regression tests added

- `tests/mutators/test_build_pools.py` (12) — empty-cache refusal, no
  empty-overwrite, wrong-version deletion guard, frozen-version guard, v5 mapping
  (= v4 N=30 / cache_cross), PUT auto-detect, versioned manifest.
- `tests/mutators/test_sms_campaign_v5.py` (9) — strict v4/v5 resolution (no
  Study-1 fallback), new PUT ids `a4..d8`, `--puts` 10-cell pilot restriction.
- Full suite: **443 passed** (422 baseline + 21 new).
