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

---

# Study-4 calibration-pilot log — `{a2, b4}` four-vendor LIVE gateway (2026-07-09)

REDUCED pilot (1 attempt per operator × slot instead of K=3 → 18 generations per
arm; both arms) over the OpenAI-compatible cross-vendor gateway. Driver:
`scripts/pilot_smoke_study4.py`. Wiring: `scripts/cross_source_campaign.py`
(`--study4`), `src/p2/mutators/llm_client.py` (four-vendor gateway layer),
`src/p2/config/study4.py` + `configs/study4_models.json` (config-driven
model-role map). Code-level firewall: PILOT-marked `v8_pilot` outputs only; the
frozen v5/v6 pools and confirmatory SSOTs are untouched. Confirmatory run NOT
started (awaits the sibling's PREREGISTRATION_STUDY4 pin).

## Pilot run record

| Check | Expectation | Result |
|---|---|---|
| generation (both arms) | 18 + 18 = 36 live calls | 36 (same 18, cross 18) |
| admission (shared `admit_mutant`) | high V1–V4 pass | 35/36 admitted (97.2%) |
| pool → SMS | 10 pilot cells per arm, inst>0 | 10/10 per arm, inst=6, 3 nonzero-kill cells each |
| blinded API review (reviewer claude-fable-5) | one verdict per admitted mutant | 35 verdicts (18 same, 17 cross) |
| arbitration (gpt-5.5) | fires only on reviewer UNCERTAIN | 0 live (no UNCERTAIN; path is mock-tested) |

Per-model (generation): claude-fable-5 success 1.00, malformed 0.00, lat 12.0 s,
ct 368; gpt-5.5 1.00 / 0.00 / 7.9 s / ct 300; gemini-3.5-flash 1.00 / 0.00 /
2.8 s / ct 271; grok-4.1 0.833 / 0.00 / 8.4 s / ct 260 (served **grok-4.3**).

## Model-specific pathologies + the code they forced (code-level only)

| # | Pathology | Category | Code fix forced |
|---|---|---|---|
| P10 | The gateway serves id `grok-4.1` as **grok-4.3** (`response.model` self-reports grok-4.3), and grok emits **bare ` ``` ` fences** (no `python` language tag). A naive `python`-only fence parser would drop every grok body. | vendor id-remap + fence format | `_generate_one` now echoes `response.model` into `meta['served_model']`; `_study4_call` logs it per call with a `served_mismatch` flag, and `configs/study4_models.json` pins `served_as: grok-4.3`. `_strip_fences`' bare-` ``` ` fallback (pre-existing) is confirmed load-bearing for grok — retained deliberately. |
| P11 | `claude-fable-5` gateway **over-reports and destabilises `usage.prompt_tokens`**: 12,123 mean (range ~8k–37k) for a rendered prompt whose real size is ~600 tokens. It inflates same-arm generation **and** the claude reviewer, dominating the projected cost ($0.042/gen and $0.031/review vs ~$0.001–0.006 for the other vendors). | gateway usage accounting | Cost accounting reads `usage` **verbatim** per call (never a nominal estimate) so the inflation is captured, not hidden; the config flags `claude-fable-5` prompt tokens as gateway-reported/unstable. The projection therefore reflects the true (inflated) claude cost rather than an optimistic nominal one. |
| P12 | `gemini-3.5-flash` spends its token budget on hidden reasoning; at the default `max_tokens=800` the visible completion truncates/empties. | reasoning-token budget | `min_max_tokens` quirk (config-driven, 2000 for gemini) applied in `_generate_one`/`_study4_call` — the effective `max_tokens` floor is raised per model. With the floor, gemini returned non-empty valid bodies on 6/6 calls (malformed 0.00). |

Non-pathology note: the single cross-arm miss (grok `a2_SI1`) was a V1–V4
validation FAIL (`malformed_rate=0`, i.e. well-formed body that failed the
non-triviality/executable gate), not a response pathology — a normal generation
miss, no code change.

## Cost projection — full confirmatory run

Assumptions (from the pilot means): 28 PUTs × 3.03 mean ops ≈ **85 operators**,
K=3, 3 slots/arm, 2 arms → **1,530 generation calls**; admission 0.972 →
**1,488 reviewer (claude-fable-5) calls**; reviewer-UNCERTAIN rate 0.0 → **0
arbitration calls** (a nonzero rate in the confirmatory run adds gpt-5.5 arbiter
cost linearly). Projected: **generation $34.6 + review $46.0 + arbitration $0.0
≈ $80.6 USD**. The review leg exceeds generation because the claude reviewer
carries the P11 prompt-token inflation on every admitted mutant; a cheaper
reviewer (or a gateway prompt-token fix) is the largest available cost lever.

SSOT: `data/results/study4/pilot_report.json`,
`data/results/study4/sms_v8_pilot_{same,cross}.json`.

## Regression tests added

- `tests/mutators/test_study4_client.py` (**16**) — config-driven arm/role
  mapping + env-override roster, gemini `max_tokens` floor, grok served-id echo,
  bare-fence stripping, retry/backoff (transient-then-success, exhaustion,
  non-retryable-not-retried), per-call cost accounting + log, blind-code vendor
  redaction, review CONFIRMED-no-arbitration vs UNCERTAIN-triggers-arbitration,
  and a full offline `study4_campaign` wiring test. No live calls in pytest.

---

# Study-4 C-arm (H-LANG) calibration pilot — `{a3, b2}` LIVE gateway, `--lang c` (2026-07-09)

REDUCED pilot (1 attempt per operator x slot, BOTH arms -> 18 + 18 = 36 live
generations) over the four-vendor gateway through the NEW C-language path
(`--lang c`). Driver: `scripts/pilot_smoke_study4_cport.py`. Wiring:
`scripts/cross_source_campaign.py` (`study4_campaign(..., lang="c")` ->
`PROMPT_TEMPLATE_C`, `admit_c_mutant` gcc admission), `src/p2/cport/{adapter,
validation}.py`, `scripts/sms_campaign.py` (`evaluate_cell(..., lang="c")`).

**Firewall (registration §0.3 A2, §2b′).** a2 is CONFIRMATORY in the C grid, so
the C-arm pilot uses **`{a3, b2}`** (a3 deterministic heat-FDM; b2 stochastic
Metropolis–Hastings) — NOT a2. All outputs are `v7c_pilot`-tagged
(`{a3,b2}_pool_v7c_pilot_{same,cross}`, `data/results/study4/sms_v7c_pilot_*.json`);
the confirmatory `data/results/sms_track2_v7c.json` and `{put}_pool_v7c` pools are
**verified absent** (asserted by the driver). Confirmatory C run NOT started. Only
CODE-level fixes below; no threshold, estimand, DGP, primary-MP, or roster changed.

## Defect P13 — `p2.cport.adapter._resolve_source` crash on an empty LLM body

- **Defect.** `_resolve_source("")` executed `Path("")`, which resolves to the
  **cwd directory** (`.`). `Path("").exists()` is True (a directory exists), so
  the adapter called `.read_text()` on `.` and raised
  `IsADirectoryError: [Errno 21] Is a directory: '.'`, crashing the whole
  campaign the first time any model returned an empty/whitespace body (a
  truncated or fence-only response). Surfaced live at `b2_HP1` in the same arm.
- **Root cause.** The path-vs-raw-code heuristic used `p.exists()` (true for a
  directory) and did not special-case the empty string; `Path("") == Path(".")`.
- **Fix (code-level).** Treat a `str` as a file path ONLY when it is non-empty,
  single-line, and `Path(s).is_file()` (false for `.`); otherwise return it as
  raw code (so an empty body falls through to gcc and fails as a normal V1 miss).
  A `Path` argument is still always read. Guarded `OSError/ValueError` for
  over-long strings.
- **Why code-level.** Adapter robustness against malformed LLM output; it changes
  how a body is routed to gcc, never any measured quantity. Regression:
  `tests/cport/test_adapter.py::test_empty_or_blank_body_is_raw_not_path`
  (parametrised over `"", "   ", ".", "  \n  "`).

## Defect P14 — C generation truncated at the Python-inherited `max_tokens=800`

- **Defect.** `study4_generate_slot` issued the C generation call with the
  Python default `max_tokens=800`. A self-contained C mutant carries the FULL
  program (includes + `double program(double)` + the REPL `main`), 2–4x the
  token length of a Python mutant body, so the longer kernels (especially `a3`
  heat-FDM) were **truncated mid-program** -> incomplete source -> `gcc` V1 fail
  (and the empty-tail bodies that tripped P13). Baseline (pre-fix) same-arm
  claude C: **7 PASS / 8 FAIL**, and **7 of the 8 FAILs were at the `ct=800`
  cap** (5 gcc-compile fails, 3 V3-triviality); the PASSes needed ct 1179–1543.
- **Root cause.** The 800-token budget is correct for a Python mutant body but
  too small for a whole C program; the C path inherited it unchanged.
- **Fix (code-level).** `C_GEN_MAX_TOKENS = 2048` passed to `_study4_call` when
  `lang == "c"` (the per-model `min_max_tokens` floor still applies on top).
  Post-fix, the same a3 slots that truncated at ct=800 completed at ct
  1561/1901/1891 and compiled.
- **Why code-level.** A token budget sized to the output language; no threshold,
  estimand, DGP, primary-MP, or roster is touched.

## Pilot run record (post-fix, LIVE) — per-vendor C-code quality (NEW territory)

36 live generations (same 18 + cross 18), 1 attempt/op/slot. Ops: a3
(CE1/OS1/SI1), b2 (HP1/CF1/CE1). Admission = gcc `-std=c99 -O0 -Wall` compile
(V1) + adapter finite-probe (V2) + non-triviality vs the C original (V3).

| Vendor (role) | n | compile-fail (V1) | V3-trivial | admitted | admit rate | served | mean lat |
|---|---|---|---|---|---|---|---|
| `gpt-5.5` (cross src1) | 6 | **0/6 (0.00)** | 1 | 5 | 0.83 | gpt-5.5 | 21.5 s |
| `gemini-3.5-flash` (cross src2) | 6 | 1/6 (0.17) | 0 | 5 | 0.83 | gemini-3.5-flash | 7.1 s |
| `claude-fable-5` (same, all 3 slots) | 18 | 1/18 (0.06) | 3 | 14 | 0.78 | claude-fable-5 | 16.3 s |
| `grok-4.1` (cross src3) | 6 | **5/6 (0.83)** | 1 | **0/6 (0.00)** | 0.00 | **grok-4.3** | 15.1 s |

**Headline (honest, NEW territory — LLMs writing C).** After the P14 budget fix,
`gpt-5.5` (0/6 compile-fail), `gemini-3.5-flash` (1/6), and `claude-fable-5`
(1/18) write compilable C99 reliably. **`grok-4.1` (served `grok-4.3`) does NOT**:
5/6 of its C bodies failed `gcc -std=c99 -O0 -Wall` and **0/6 were admitted** —
a genuine cross-vendor capability gap in generating compilable C, recorded
without spin. Pilot totals: **36 generated, 24 admitted (0.667)** (same 14/18,
cross 10/18); **24 blinded reviews** (claude-fable-5), **0 arbitrations** (no
reviewer-UNCERTAIN); SMS ran on all 10 pilot cells per arm (2 nonzero-kill cells
each). The grok C-compile gap is a live cost/feasibility signal for the
confirmatory C run (the cross arm's src3 slot will admit far fewer C mutants than
its Python counterpart); it is recorded here as a pilot observation, NOT a
protocol change.

SSOT: `data/results/study4/cport_pilot_report.json`,
`data/results/study4/sms_v7c_pilot_{same,cross}.json`.

## Regression tests added

- `tests/cport/test_adapter.py::test_empty_or_blank_body_is_raw_not_path` (P13
  empty/blank/`.` body -> raw code -> clean `CCompileError`, never
  `IsADirectoryError`).
- The `--lang c` Study-4 wiring (`study4_campaign`/`study4_generate_slot`/
  `run_study4_blind_review` `lang` params) is additive; the Python arms are
  byte-unchanged (existing `tests/mutators/test_study4_client.py` stays green).

## Defect P15 — Study-4 relaunch silently REDREW already-drawn gateway slots

**What happened.** After the quota top-up, the cross-arm gateway relaunch
(2026-07-09 11:23 UTC, `--resume`) started regenerating from the FIRST slot
(`a1_CE1 src1 a01`) instead of resuming: the legacy `--resume` filter matches
the Study-2 filename scheme `(claude|gpt|deepseek)` and never matches Study-4's
`src1/src2/src3` cache names, and `study4_campaign()` itself had NO resume
logic at all. An earlier runaway process (the pkill survivor noted under the
v1.2 amendment) had likewise overwritten same-arm and C-arm files. Damage at
detection (12:28 UTC, process killed): 55 cross + 24 same + 6 C cached mutant
files overwritten and 10 new files written for previously FAILED attempts.

**Why this is a one-shot violation if left in place.** The registration's
one-shot rule (a resume fills only undrawn slots; drawn slots — including
validity-FAILED attempts — are never redrawn) makes the FIRST draw canonical.
Keeping any second draw would be a redraw with post-hoc choice between two
realisations of the same slot.

**Remediation (first-draw-canonical, applied before ANY outcome was computed).**
1. All redraw content archived unread to
   `archive/study4_redraw_quarantine_2026-07-09/{cross,same,clang}/`
   (59 + 27 + 7 files) — none of it enters any pool. (Diagnosis involved one
   structural diff of `cross/a1_HP1_src1_attempt01.py`; no execution, no SMS.)
2. Overwritten cache files restored byte-identical to the committed run-1
   checkpoint (`git restore`); redraws of run-1 FAILED attempts deleted from
   the cache (those attempts remain consumed-and-failed).
3. Campaign logs kept append-only: the redundant run-2 rows remain in
   `campaign_log.jsonl` as cost/provenance records (~143 cross + 88 same +
   31 C rows), explicitly flagged here as discarded redraws.
4. Fix: `study4_campaign()` now counts `kind=="generate"` rows per
   (op_id, slot) in the campaign log and starts each slot at attempt
   drawn+1; a transport/quota `study4-generate-error` row is NOT a draw
   (the model returned nothing), a validity-FAIL row IS. Verified offline:
   77/77 drawn (op,slot) pairs skipped, 0 partial pairs, undrawn set =
   {b2: 4 pairs} + {b3,b5,b6,b7,c1..c7,d1..d8}.
5. Relaunched 12:5x UTC with the fixed resume; log header now prints the
   skip count (`[resume] 359 attempts already drawn across 77 pairs`).

**Blast radius on inference: none.** No SMS, review, or verdict had been
computed on any Study-4 arm at any point in this window; the selection risk
of "choosing between draws" never materialised because the redraws were
quarantined unread and the first draws restored from the committed
checkpoint. Cost of the defect: ~143 redundant gateway generation calls
(logged), plus 534 zero-cost transport-error rows from one relaunch attempt
that ran without `.env` loaded (also logged, not draws).
