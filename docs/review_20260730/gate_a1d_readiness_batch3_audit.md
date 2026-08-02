# Gate A1d — C3 Readiness Batch 3 Audit

- **Audit time:** `2026-08-02T13:44:43+08:00`
- **Cursor branch:** `origin/cursor/grok-phase3-c3-readiness-batch3`
- **Draft PR:** #6; OPEN; head `8ef20d26ea0a785bd0209b922a94e7f3bc1e8064`
- **Baseline:** `0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a`
- **Verdict:** `BLOCKED`
- **Integration:** none
- **Accepted ready count:** remains 12 from audited Batches 1–2; the six Batch 3 rows remain proposed only
- **Successor state:** only an in-place Batch 3 correction is unlocked; canonical freeze, C4, annotation, category-map freeze, prediction, detection, and further mining remain locked

## 1. Audited lineage and scope

The submitted lineage is consecutive and remotely pinned:

```text
0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a
  -> cc3321da3a9e6f1f7d67e5b90cdf21d6fb9001c1  membership
  -> 00d1ca3fdfaa582f831f89589aabcfb51667c3c0  payload
  -> da70fa676ebcab8ef1e98f532aa711c2d01f0c84  handoff
```

The membership is exactly the six supplemental-pilot rows authorized by Gate
A1c, in sheet order, with no replacement:

```text
EXT-numpy-01
EXT-scipy-01
EXT-scikit-learn-01
EXT-statsmodels-01
EXT-statsmodels-02
EXT-statsmodels-03
```

Membership, readiness, handoff, and the pilot sheet agree on IDs, repositories,
issue URLs, buggy/fixed SHAs, and order. Both submitted sheets keep A2
`PENDING`; no canonical freeze or downstream artifact changed.

## 2. Independent verification

| Check | Result |
|---|---|
| Handoff hash checker | `HASH_CHECK_OK` |
| Tampered-artifact negative probe | changed `EXT-numpy-01/fixed.json`; checker exited 1 with the exact hash mismatch |
| Admission checker | exit 0; pre-readiness structure only |
| Independent binding probe | `A1D_INDEPENDENT_PROBE_OK cases=6 commands=121` |
| Command binding | global 121 commands exactly equal the ordered concatenation of six per-case logs |
| Full tests in immutable archive | `260 passed, 10 warnings` |
| Compileall | exit 0 |
| Reserved/token scans | raw `rg` exit 1, no output |
| Immutable downstream paths | exit 0; unchanged |
| Sheet hash | `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a` |

Key submitted hashes:

| Artifact | SHA256 |
|---|---|
| `HANDOFF_REPRO_BATCH3.json` | `cc488df412eb0a709552f7e2559f230df702397f0f8818b793fd00a45665b421` |
| `BATCH3_MEMBERSHIP.json` | `02d47656f6fc5a528c9f1cf747bba8025440914e12873fcc8975a8f54e6da853` |
| `readiness_batch3.json` | `194e255aca7dc82c30dc00061c2e16233ed26cf9a6502669e37c80eb974238a2` |
| `BATCH3_COMMAND_LOG.json` | `28991dbb6236b6a4ca4d50144fad4faef154a7a85b3acc49807cdf3a950c58f2` |
| `BATCH3_VERIFICATION_LOG.json` | `fbaed8e5f154ab13a89465211be2a9a39f9c957fa60629921d1472ab0f2904f8` |
| runner | `10c2416415665a7d0748049adbfac04fa2d38368db859f0747708617bdc27c4a` |

These checks establish integrity and one observed buggy/fixed contrast per
case. They do not satisfy all execution requirements below.

## 3. Spec findings

### `A1D-REPETITION-001` — BLOCKER

The admission runbook §6.3 requires one environment smoke execution and enough
seeded repetitions to establish deterministic issue behaviour, with matching
seeds and inputs across arms. The runner at
`scripts/external_slice/run_c3_batch3_readiness.py:688-721` invokes each arm
exactly once. The global command log contains 12 actual trigger commands:
buggy/fixed once for each of six cases, all at seed 0. There is neither a
separate smoke execution nor a repetition series.

This is especially material for the randomized scikit-learn and
`EXT-statsmodels-02` triggers. The six one-shot contrasts are `observed`,
but the proposed claim that all six satisfy A2 is `blocked` until the frozen
execution rule is met.

### `A1D-SM03-CONTRACT-001` — BLOCKER

The frozen mechanism for `EXT-statsmodels-03` is two-part: restore the zero
default for the two-sample null difference **and** require an explicit
one-sample null value. The trigger calculates
`one_sample_requires_value`, and its own comment says silent one-sample
acceptance is a contract failure, but line 45 sets:

```python
ok = two_sample_ok
```

An independent fake-module probe made both one- and two-sample calls accept
`value=None`. The trigger still returned:

```text
SM03_ESCAPE property_holds=True one_sample_requires_value=False exit_status=0
```

Thus half of the issue-described contract can fail while the case is proposed
`PASS`, contrary to runbook §6.3(3–6). The current recorded fixed output does
show the desired one-sample exception, but the decision predicate does not bind
that evidence.

### `A1D-LINALG-PROVENANCE-001` — BLOCKER

Runbook §6.2 requires the BLAS/LAPACK provider to be recorded where relevant.
The scikit-learn calibration/CV workload and the statsmodels VIF auxiliary
regressions are linear-algebra-dependent, yet their `environment.json` files
record only Python, platform, machine, GCC, and G++. No per-arm BLAS/LAPACK
provider or provider-discovery command/output is retained. Source, dependency,
build-tool, and wheel hashes are otherwise present.

## 4. Standards axis

Standards review is `FAIL`, independently of the Spec result:

- the runner has nine lines over the documented 100-character limit;
- all six reproducers have overlong shared boilerplate lines, with two
  additional overlong lines in the SciPy trigger;
- `check_batch3_handoff_hashes.py` does not follow PEP 8 import grouping and
  top-level separation;
- the payload commit subject is descriptive rather than imperative.

The prior commit subject should be disclosed rather than rewritten. The code
style violations should be corrected in the correction payload. Non-blocking
smells are the 1,384-line runner's divergent responsibilities/raw dictionaries
and duplicated reproducer CLI/JSON boilerplate.

## 5. Finding disposition and decision

| Finding | Disposition |
|---|---|
| Exact six-row membership/no replacement | verified |
| Same trigger/input/seed within each recorded arm pair | verified for the one retained run |
| Exact source/build/dependency locks | verified |
| Handoff and per-case hash integrity | verified |
| Sheet A2 remains `PENDING`; downstream lock | verified |
| `A1D-REPETITION-001` | OPEN / BLOCKER |
| `A1D-SM03-CONTRACT-001` | OPEN / BLOCKER |
| `A1D-LINALG-PROVENANCE-001` | OPEN / BLOCKER |
| Standards axis | FAIL; correction required |

Gate A1d is `BLOCKED`. Do not cherry-pick PR #6, promote any of its proposed
A2 values, count the six rows as accepted ready cases, or start another mining
loop. The accepted ready count remains 12, not 18. Canonical freeze and all
later empirical stages remain locked.

## 6. A1d-r1 correction contract

Use a fresh Cursor VM/session without `rtk`, on the existing branch starting
from `da70fa676ebcab8ef1e98f532aa711c2d01f0c84`.

1. Keep the six-row membership byte-identical; no substitution or new case.
2. Define and commit the execution matrix before running: one separate smoke
   run per arm at seed 0, followed by repetitions at seeds 0, 1, 2, 3, and 4.
   Every seed/input must match across buggy/fixed arms. Save distinct stdout,
   stderr, return code, and canonical JSON for every arm/run.
3. Derive each case verdict from the complete repetition matrix. `PASS`
   requires every retained repetition to show buggy issue behaviour and fixed
   removal; otherwise retain the row as `REPRO_FAILED`. Do not hide or replace
   failures.
4. Change the statsmodels-03 predicate to require both
   `two_sample_ok and one_sample_requires_value`. Align the expected-property
   text with the frozen mechanism and add a negative regression reproducing
   `SM03_ESCAPE`.
5. Record BLAS/LAPACK provider discovery commands and raw results separately
   for both arms of every relevant NumPy/SciPy/scikit-learn/statsmodels
   workload. Bind these artifacts into the handoff hashes.
6. Add targeted tests for the smoke/repetition matrix, per-seed arm parity,
   complete verdict aggregation, statsmodels-03 escape, exact membership, and
   handoff tamper rejection.
7. Fix the documented PEP 8/100-character violations and use imperative
   subjects for new commits. Do not rewrite the historical payload commit.
8. Recompute readiness, command/verification logs, environments, all hashes,
   and the handoff. Keep both sheets A2 `PENDING` and preserve all downstream
   absences.
9. Commit a correction payload and direct-child correction handoff separately,
   push, and stop for `Gate A1d-r1`. Do not start supplementary mining,
   canonical freeze, C4, annotation, prediction, or detection.

## 7. Gate A1d-r1 re-review

- **Re-review time:** `2026-08-02T19:21:36+08:00`
- **Correction lineage:** `da70fa67` → matrix `64568960` → payload
  `dfc94736` → handoff `4287ea4a`
- **Verdict:** `BLOCKED`
- **Integration:** none
- **Accepted ready count:** remains 12; the six Batch 3 rows remain proposed only

### 7.1 Closed original findings and retained evidence

The correction closes the three original empirical-evidence findings:

- membership remains byte-identical at
  `02d47656f6fc5a528c9f1cf747bba8025440914e12873fcc8975a8f54e6da853`;
- the frozen matrix specifies smoke seed 0 and formal seeds 0–4, and all 72
  retained arm executions are present (12 smoke plus 60 formal);
- an independent reconstruction found every formal pair input-identical with
  buggy `property_holds=false`/raw RC 1 and fixed
  `property_holds=true`/raw RC 0;
- `EXT-statsmodels-03` now requires both two-sample success and one-sample
  explicit-value rejection; the prior escape probe now returns property false
  and exit 1;
- all 12 per-arm BLAS/LAPACK records exit 0, identify OpenBLAS, retain raw
  command/stdout/stderr/return-code artifacts, and are included in the
  handoff per-case hash trees.

Independent checks produced:

| Check | Result |
|---|---|
| Lineage and remote head | exact direct ancestry; PR #6 head equals `4287ea4a...` |
| Handoff checker | `HASH_CHECK_OK` |
| Tampered formal RC artifact | checker exit 1 with exact file hash mismatch |
| Independent evidence probe | `A1D_R1_INDEPENDENT_PROBE_OK cases=6 formal_runs=30 smoke_runs=6 arms=72` |
| Admission checker | exit 0; pre-readiness structure only |
| Targeted A1d-r1 tests | `7 passed` |
| Full test suite | `267 passed, 10 warnings` |
| Compileall | exit 0 |
| Reserved/token scans | raw `rg` exit 1, no output |
| Membership and both sheets | membership unchanged; A2 remains `PENDING` |

Correction hashes:

| Artifact | SHA256 |
|---|---|
| handoff | `58b7d370a5e299c3920a1cee253fa6327a8e0ceaa9413c517c39516471828041` |
| execution matrix | `addab92a9ab0643c4ecf89d056c910088180cf5c4651ba1beee543d8bfa776d6` |
| readiness | `c9d3d57bd4d5c6d5120c1d92e64b094b47bbd3635e26af817ab24fd80dffc016` |
| command log | `a2bbaa97d3038bf8982a0c425300e5b289f80be70f945b4f4643921e0814fb8c` |
| verification log | `de7343c65a4b1090eb12ada6f18894e13a5872067dd5f4eeb1a8c94e8ab824de` |
| runner | `8cb40a1446b9a556a6a5b2ce3838298a10ca646639ea93abd97f42f786cd91ee` |
| aggregation helper | `45ede051685b5d837b103d4bac5724e0160f42c8a26702d66ce087531336aa59` |

### 7.2 `A1D-R1-MATRIX-AGGREGATION-FAILOPEN-001` — BLOCKER

The retained observations are correct, but the code that turns them into a
decision remains fail-open. In `batch3_a1d_r1.py`, absent
`input_parity_ok` defaults to true, and buggy/fixed raw return codes are copied
into output rows without participating in the contrast predicate. Two
independent negative probes supplied all five formal rows and obtained `PASS`
when:

1. every `input_parity_ok` field was absent; and
2. raw return codes were reversed to buggy 0 / fixed 1.

The standalone membership/matrix verifier also trusts the summarized
`all_seeds_contrasted` flag instead of reconstructing the five seed rows and
binding properties, explicit parity, and raw RCs. The targeted tests do not
cover either escape. This violates correction-contract items 2, 3, and 6, so
the six proposed verdicts cannot yet be accepted even though the retained
evidence happens to meet the intended rule.

### 7.3 Standards axis — FAIL

`ruff check --select E,F,I,E501 --ignore-noqa` reports four violations in
`run_c3_batch3_readiness.py`: E402 and I001 for the post-path-mutation import,
plus 114- and 107-character lines at current lines 1224 and 1631. The three
new commit subjects are imperative and `git diff --check` is clean.

### 7.4 Decision and A1d-r2 correction contract

Gate A1d-r1 remains `BLOCKED`. Do not integrate PR #6, count the six rows as
accepted ready cases, or begin supplementary mining/canonical freeze/C4. The
only unlocked task is an in-place A1d-r2 correction on the same Cursor branch:

1. Make formal aggregation fail closed: every seed 0–4 must be present,
   `input_parity_ok is True`, buggy property false with raw RC 1, and fixed
   property true with raw RC 0. Any absent or mismatched value must produce
   `REPRO_FAILED` and remain visible in `failing_seeds`.
2. Make the standalone verifier reconstruct all five formal rows from the
   hash-bound per-execution JSON and return-code files; do not trust a summary
   flag alone. Cross-check reconstructed rows against the repetition matrix,
   readiness, and handoff verdict.
3. Add negative regressions for absent parity and reversed raw return codes,
   alongside the existing missing-seed and statsmodels-03 escape tests.
4. Fix all four reported PEP 8/import/100-character violations and require the
   exact Ruff command above to pass without relying on `noqa` for the import.
5. Preserve the matrix, membership, sheets, and retained execution/provider
   evidence. Re-running dual-arm experiments is unnecessary unless those raw
   artifacts are changed. Recompute derived decision files, verification log,
   hashes, and handoff.
6. Commit a correction payload and direct-child handoff, push, and stop at
   `Gate A1d-r2`; do not start any later empirical stage.

## 8. Gate A1d-r2 re-review

- **Re-review time:** `2026-08-02T20:27:44+08:00`
- **Correction lineage:** `4287ea4a` → payload `eab67f3a` → handoff
  `8ef20d26`
- **Verdict:** `BLOCKED`
- **Integration:** none
- **Accepted ready count:** remains 12; the six Batch 3 rows remain proposed

### 8.1 Closed A1d-r1 finding and retained evidence

The A1d-r2 implementation closes the prior aggregation escapes. Independent
probes now obtain `REPRO_FAILED` for both an absent `input_parity_ok` field and
reversed buggy/fixed raw return codes. Each seed now requires explicit parity
true, buggy property false/RC1, and fixed property true/RC0. The verifier
reconstructs five formal rows from per-execution JSON and return-code files and
cross-checks the repetition matrix and readiness verdict.

The immutable-evidence diff from `4287ea4a` is empty for membership, execution
matrix, both sheets, all smoke/formal execution files, and all per-arm provider
artifacts. No dual-arm rerun occurred. Independent reconstruction again found
6 cases, 30 formal pairs, 6 smoke pairs, and 72 total arm executions with the
intended contrasts.

| Check | Result |
|---|---|
| Handoff hash checker | `HASH_CHECK_OK` |
| Previous fail-open probes | both return `REPRO_FAILED` |
| Independent evidence reconstruction | `A1D_R1_INDEPENDENT_PROBE_OK cases=6 formal_runs=30 smoke_runs=6 arms=72` |
| Admission / membership checker | exit 0 |
| Targeted A1d tests | `10 passed` |
| Full test suite | `270 passed, 10 warnings` |
| Ruff exact correction command | `All checks passed!` |
| Compileall / `git diff --check` | exit 0 |
| Reserved/token scans | raw `rg` exit 1, no output |

Correction hashes:

| Artifact | SHA256 |
|---|---|
| handoff | `c8c47cee21e2d0bcdfcc306a019028dc50ff6ab12a8f9da46117835660afb108` |
| membership | `02d47656f6fc5a528c9f1cf747bba8025440914e12873fcc8975a8f54e6da853` |
| execution matrix | `addab92a9ab0643c4ecf89d056c910088180cf5c4651ba1beee543d8bfa776d6` |
| readiness | `7446ea002d131797ac9f9ac77397fcf1b59389c668dd854a3241831f2b8fcb02` |
| command log | `a2bbaa97d3038bf8982a0c425300e5b289f80be70f945b4f4643921e0814fb8c` |
| verification log | `e0613d4ae5bda8d622f233d06491715cb6c893c516d7221b8ed6ba89d1f2a911` |
| aggregation helper | `bf24c6b339bccc6d3ed8ef8ee687db805fa319d59e0162546634613ec03df97e` |
| standalone verifier | `cca164b6bd2dcade90ed8a5de0a82b28366d6e6d6b87b4c1b1105a28cee90602` |

### 8.2 `A1D-R2-HANDOFF-VERDICT-BINDING-001` — BLOCKER

The A1d-r2 contract required the reconstructed formal verdict to be
cross-checked against the repetition matrix, readiness, **and handoff**. The
standalone verifier never reads `HANDOFF_REPRO_BATCH3.json`; the handoff hash
checker validates only files named by the handoff and cannot validate the
handoff's own semantic fields.

An independent negative probe changed only the first handoff
`case_results[].proposed` value from `PASS` to `REPRO_FAILED`. Both commands
still returned exit 0:

```text
verify_batch3_membership_matrix.py  -> membership_matrix_ok 6
check_batch3_handoff_hashes.py      -> HASH_CHECK_OK
```

Thus a handoff verdict can disagree with the hash-bound raw evidence,
repetition matrix, and readiness without rejection. This is a direct,
reproducible miss of correction-contract item 2. The submitted handoff happens
to contain six matching PASS values, but the gate requires the decision path to
fail closed under this inconsistency.

### 8.3 Standards axis — PASS

The exact required Ruff command and `git diff --check` pass. All four previous
violations are closed, and both new commit subjects are imperative. The
reviewer noted only non-gating design smells: duplicated dynamic helper loading,
raw-dictionary data clumps, and scattered `rederive_from_artifacts` mode
branches.

### 8.4 Decision and A1d-r3 correction contract

Gate A1d-r2 remains `BLOCKED`. Do not integrate PR #6 or promote the six
proposed cases. The only unlocked task is an in-place A1d-r3 correction:

1. Load the handoff in the standalone verifier and require exact case ID/order.
2. For each case, cross-check the reconstructed verdict, failure stage,
   formal/smoke seeds, and seed-0 trigger exit codes against both readiness and
   the corresponding handoff `case_results` entry.
3. Recompute and cross-check handoff counts and failures from reconstructed
   case results; reject missing, duplicate, extra, or inconsistent entries.
4. Add a regression that mutates only a handoff case verdict and requires the
   verifier or semantic handoff checker to exit nonzero. Also cover handoff
   count/failure mismatch.
5. Preserve membership, matrix, sheets, raw execution/provider evidence, and
   current fail-closed aggregation. No dual-arm rerun is required.
6. Recompute derived verification/handoff artifacts, commit a payload and its
   direct-child handoff, push, and stop at `Gate A1d-r3` without starting later
   stages.
