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

## Defects P4-P5: review-packet content gaps (found by pilot review round)

Both blinded reviewer instances completed all 54 verdicts (54 CONFIRMED /
0 REJECTED / 0 UNCERTAIN; ingest-review: 54 accepted, 0 schema-err,
0 arbitration). Two packet-content defects surfaced from their reports:

| # | Defect | Root cause | Fix (code-level) |
|---|---|---|---|
| P4 | Response filename convention not stated in any packet; both reviewers had to infer `<blind_id>_response.json` from the generation-side pattern (they converged, so ingestion succeeded) | `--export-packets` / `--export-review-packets` omitted an explicit `response_filename` field | Added `response_filename` to generation, review, and arbitration packets; instructions now point to it explicitly |
| P5 | E1∧E2 protocol referenced but not defined in-packet; reviewers had to guess the conjunct semantics (their reading — equivalent=true iff both E1 and E2 hold — matches the registered protocol, so no verdict is invalidated) | Review-packet instructions assumed protocol knowledge the blinded role cannot have | E1/E2 operational definitions embedded verbatim in review + arbitration packet instructions |

Both fixes change packet *presentation* only: schemas, admission gates,
blinding guarantees, and verdict semantics are untouched. Classified
code-level under §2b. The 54 pilot verdicts remain valid (reviewer
inference matched the registered semantics; filenames converged).

## Confirmatory-phase incidents and disclosed deviations (post-freeze)

| # | Item | Class | Detail |
|---|---|---|---|
| P6 | `sms_campaign.py` defaulted to `--track 1` and wrote the 28 primary-cell scores over the tracked Study-1 `data/results/sms_track1.json` | tooling incident, no protocol impact | File restored via `git restore` before any use; rerun with explicit `--track 2 --out data/results/sms_track2_v5.json`. SMS scoring is a deterministic mechanical measurement of the frozen pools — the rerun is re-execution, not regeneration. Runbook command updated. |
| P7 | Review-packet export tripped the blinding assertion: b5's 27 mutants carried the slot's source label in their docstrings | blinding guard worked as designed | Presentation-layer redaction added at export (source-family tokens → "src" in the DISPLAYED code only; artifacts on disk untouched; assertion retained as final guard). 315 partially-exported packets discarded and re-exported. |
| D-A1 | `compute_dualblind_delta.py` gained a `--gated-h2-2` CLI mode POST-DATA | **disclosed deviation** (script-interface, non-statistical) | The frozen CLI required both arm files even though H2-2 is gated not-run by registration v1.1 (same-vendor freeze). The added mode skips only the H2-2 computation and emits the registered NOT-RUN verdict; H2-1 statistical logic is byte-unchanged. Recorded in the output SSOT (`post_freeze_deviation`) and here. |
| P8 | The CF/TF single-stratum admission screen was a **silent no-op** for the entire v5 campaign | **disclosed design-intent defect** (post-hoc; no re-verdict) | `pool_builder` set `op_id` to the filename-before-`_attempt` **including** the model-source suffix (e.g. `c7_TF1_claude`). `stratum_filter._OPID_CAT_RE = ^[a-d][1-8]_([A-Z]{2})\d+$` anchors at end-of-string after the operator digit, so the `_claude`/`_deepseek`/`_gpt` suffix makes `category_from_op_id(...) -> None`; `screen_mutant` treats `None` as unconstrained and admits without evaluating flip count. Verified: 81/81 CF/TF multi-stratum mutants have `category_from_op_id(build_op_id) == null`. The Incident #1 pilot "b4 TF1 passed 9/9 at admission" was the **same** false negative (`category_from_op_id("b4_TF1_claude") -> None`), not a verified single-stratum pass. Consequence: H4' evaluated the **unscreened** pool. The registered decision rule scores `suspect_share` on the admitted pool and does not condition on the screen, so the frozen `NOT_CONFIRMED` verdict (mean 0.1714, `s5_purity_v5.json`) is unaffected in validity; only the design intent (CF/TF entering single-stratum) was not realised. Diagnosis SSOT: `data/results/h4_leakage_diagnosis_v5.json`. **The filter code is deliberately NOT fixed here** — correcting `_OPID_CAT_RE` (or keying off `category_from_filename`) and extending `CONSTRAINED_CATEGORIES` to OS/SI belongs to the Study-3 registration wave. |

## Confirmatory verdicts (registered decision rules, pre-frozen scripts)

| Hypothesis | Verdict | SSOT |
|---|---|---|
| H2-1' aligned>cross (Family A) | **CONFIRM** (δ=+0.4295, one-sided 95% lower +0.2653; descriptive Romano band medium, two-sided CI [0.2328, 0.6193]) | dualblind_delta_delta_v5.json |
| H1' instantiability | **CONFIRM** (5/5 families ≥8/28; CE 23, OS 14, HP 21, TF 15, SI 8) | h1_instantiability_v5.json |
| H3' class consistency | **CONFIRM** (3/4 classes positive; class C negative, reported) | h3_class_consistency_v5.json |
| H4' attribution purity | **NOT_CONFIRMED** (mean suspect_share 0.1714 > 0.05; multi-stratum by family CF 9 / OS 27 / SI 9 / TF 72 — leakage generalises beyond the Study-1 CF/TF diagnosis) | s5_purity_v5.json |
| H2-2 cross-vendor dual-blind (Family B) | **NOT-RUN** (gated; same-vendor freeze, no substitution) | dualblind_delta_delta_v5.json |

Review pipeline: 747 blinded verdicts (18 independent reviewer instances), 4 REJECTED at round 1, 6 UNCERTAIN → third-instance arbitration (all 6 CONFIRMED under a uniform GP-hyperparameter-pinning rationale). Admission: 774 valid → 756 admitted (V1–V4); pools 756 mutants / 28 PUTs; 140 confirmatory cells (36 nonzero).

---

# Study-3 calibration-pilot log — `{a2, b4}` under the P8-fixed all-family screen

**Referenced from** `PREREGISTRATION_STUDY3_v2.md` §2b (pilot reused verbatim),
§5c (screen-smoke gate), §10. Same append-only firewall: **code-level defects
only**; no threshold, estimand, DGP, primary-MP assignment, or 28-PUT roster is
touched. Date: 2026-07-09. Branch: `claude/paper-journal-acceptance-kxpveo`.
Env pinned: `P2_SCREEN_ALL_FAMILIES=1`, `P2_PRIMARY_VERSION=v3`,
`P2_SINGLE_STRATUM_FILTER=1`. Pilot driver: `scripts/pilot_smoke_study3.py`.

## Defect P9 — no `v6` pool version in the build/score tooling (Study-3 wiring)

- **Defect.** `build_pools._VERSION_SPEC` / `_STUDY2_VERSIONS` and
  `sms_campaign.resolve_pool_dir` knew only `v2..v5`. A Study-3 `v6` request had
  no suffix/cache/N mapping and no strict pool resolution — the exact class of
  omission as v5's D2/D4, on the Study-3 side.
- **Fix (code-level, mirrors D2/D4).** Added `v6 → (suffix=_pool_v6,
  cache=cache_cross, N=30, frozen=False)` to `_VERSION_SPEC`; extended
  `_STUDY2_VERSIONS` and the strict `resolve_pool_dir` branch to `{v4,v5,v6}`. v6
  is built **under the all-family screen** (`P2_SCREEN_ALL_FAMILIES=1`); the
  frozen v5 pools are never touched (wrong-version deletion guard enforces a v6
  build can only ever remove a `_pool_v6` dir).
- **Why code-level.** Encodes the registered N (30) and cache for a new pool
  version and points scoring at the correct strict dir; it changes no registered
  quantity. No Study-3 outcome is read.

## Pilot pipeline run record (Study 3, all-family screen wired)

| Step | Check (registration) | Result |
|---|---|---|
| (b) op_id category resolution (P8) | every pilot op_id resolves a known family, else loud fail | **18/18** resolve — CE 6, OS 6, SI 3, TF 3; zero `None` |
| (a) screen-smoke loud-fail gate (§5c) | wired all-family screen matches **> 0** screened evaluations | **PASS: 54 screened**, 45 admitted, 9 rejected multi-stratum (b4 `OS1` 9/9 flip≥2; b4 `TF1` admitted single-stratum) |
| v6 pilot pools | build under screen; never touch frozen v5 | `a2_pool_v6` = **27** (all single-stratum), `b4_pool_v6` = **18** (CE 9 + TF 9; OS 9 screened out) |
| (c) determinism | identical selection across two rebuilds | **PASS** (a2 27, b4 18 byte-identical source selection) |
| (d) SMS, 10 pilot cells | populate `sms_track2_v6_pilot.json` (PILOT path) | **10/10 cells** populated (a2 inst=27, b4 inst=18); confirmatory `sms_track2_v6.json` **not created** |
| (e) graded-script end-to-end smoke | `compute_h4_graded.py --pilot-smoke` consumes the pilot SMS output | artefact `h4_graded_v6_PILOT_SMOKE`; strict n_clean=9 purity 1.0 screened=45; graded n_rich=0 (a2/b4 not rich) — **NOT confirmatory**, firewalled |

**Contrast with the incident-P8 v5 no-op.** In v5 the CF/TF screen silently
admitted every candidate (`category_from_op_id("b4_TF1_claude") → None`). Under
the P8-fixed parser + all-family scope the screen now performs real work — it
**rejects** b4's 9 multi-stratum `OS1` mutants at admission — and the registered
smoke assertion (screened > 0) passes loudly rather than masquerading as an
unconstrained pass.

**Firewall attestation.** No threshold, estimand, DGP, primary-MP assignment, or
roster changed. The only code change is the P9 `v6` tooling wiring. Pilot outputs
(`sms_track2_v6_pilot.json`, `h4_graded_v6_pilot.json`, `{a2,b4}_pool_v6`) are
PILOT-marked; the confirmatory SSOTs (`sms_track2_v6.json`, `h4_graded_v6.json`,
`s5_purity_v6.json`) are **verified absent**. Confirmatory generation has **not**
begun.

## Pre-frozen analysis script + regression tests

- `scripts/compute_h4_graded.py` (**NEW, pre-frozen** before any Study-3 data;
  §7b contract) — H4''-graded (per-mutant primary-stratum share `s_m`, PUT mean,
  rich C+D aggregate, B=10,000 percentile-bootstrap lower bound, seed 20260708,
  confirm iff `boot_lower_95 > 0.15`) + H4''-strict (single-stratum purity on
  {CE,HP,CF-with-screen}, one-sided 95% lower Clopper-Pearson, confirm iff
  `cp_lower_95 ≥ 0.90` **and** the all-family screen matched > 0 candidates; a
  zero-match forces a loud `FAIL_SCREEN_NOOP`). Writes `data/results/h4_graded_v6.json`;
  prints the registered licensed verdict strings; exits 2 with no input.
- `tests/analysis/test_compute_h4_graded.py` (**17**) — graded pass/fail/boundary
  (mean exactly 0.15 fails the strict inequality), strict pass/fail,
  screen-smoke-gate FAIL (zero match), pilot exclusion, missing-input exit-2,
  malformed-input, deterministic bootstrap, pilot-smoke SSOT guard.
- Full suite: **465 passed** (448 baseline + 17 new).
