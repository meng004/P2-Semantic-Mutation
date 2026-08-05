# Gate A1b — C3 Readiness Batch 1 Audit

- **Initial audit time:** `2026-08-01T20:46:14+08:00`
- **Finding-closure re-review:** `2026-08-01T21:15:43+08:00`
- **Scope:** first C3 dual-arm readiness batch; three digest-pinned cases in the Gate A1a-approved 32-row queue
- **Current verdict:** `PASS_WITH_DISCLOSURE`
- **Open blockers:** 0; both initial provenance blockers are closed
- **Observed contrast status:** three case-local contrasts are accepted as readiness A2 `PASS` evidence; the candidate sheet remains `PENDING` until later canonical admission integration
- **Successor state:** C3 Batch 2 is unlocked in a new Cursor session; canonical admission freeze, A2/C4, fiber mapping, predictions, and result execution remain locked

## 1. Audited lineage

| Role | Commit / value |
|---|---|
| Cursor branch | `origin/cursor/grok-phase3-c3-readiness` |
| Approved baseline | `533f8e26cd7d87e48afaceaa9424a3f7ed38a997` |
| Batch 1 payload | `4ac5dab0f1692a2c2c46486c763abcce9d27984d` |
| Batch 1 handoff | `607acb044856101d8744f62cd2f7173a396c99b5` |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH1.json` |
| Pull request | `#4`, head `607acb044856101d8744f62cd2f7173a396c99b5`, base `main` |

The payload is a direct child of the approved Gate A1a baseline, and the handoff
is the direct child of the payload. The remote branch and PR head resolve to the
handoff commit.

## 2. Independently verified facts

### 2.1 Selection and frozen inputs

- The pinned Defect4MR registry at commit
  `2bf7c2401c846544e715d879eb639e8c3bf44067` contains exactly three non-null
  image digests: `b-pocketfft-004`, `e-sundials-007`, and `c-scipy-002`.
- Their digests equal the three values recorded in the Batch 1 environment
  files, and their public issue/SHA content maps to `EXT-numpy-03`,
  `EXT-sundials-07`, and `EXT-scipy-04`.
- All three neutral rows are members of the approved A1-and-A3 queue: A1 `PASS`,
  A2 `PENDING`, A3 `PASS`, decision `ADMIT_PENDING_REPRO`, blank analysis alias.
- Candidate sheet, sanitized manifest, Gate A1a report, and runbook input hashes
  reproduce the handoff values.

### 2.2 Artifact integrity and observations

- Every declared individual output SHA256 matches.
- The three five-file directory aggregates independently reproduce:
  - `EXT-numpy-03`: `63f9928f4a69822ae552ee38a1f0e619761dd55a0ecc9cda4910d546d24885b7`
  - `EXT-sundials-07`: `9b623dd7efb9fe5111cba5ad4478241bc5b16b1629b31e9d4fea55085a200a9b`
  - `EXT-scipy-04`: `77f23a54daa1cee92535a14e27df4a38c69bef0dea28b91a7b1b3e0f75b636d8`
- Each case records seed `0`, matching semantic inputs and the same trigger
  implementation on both arms. The SUNDIALS harness path is necessarily
  arm-specific; its arguments and decision bound match.
- Stored canonical JSON records buggy `property_holds=false`, exit status `1`,
  and fixed `property_holds=true`, exit status `0` for all three cases.
- The observed values agree with the pinned Defect4MR verification reports:
  NumPy explicit-length real transforms, SUNDIALS relative accuracy
  `7228.26` versus `91.2214`, and SciPy negative-skew Pearson-III CDF
  monotonicity.
- GHCR `403` is an acceptable disclosed trigger for the runbook-authorized
  host-rebuild fallback; it does not by itself invalidate the observations.
- The diff contains no canonical sheet, freeze, annotation, prediction, kill,
  or later-phase run artifact.

### 2.3 Executable checks

- admission checker: exit `0`, pre-readiness-only PASS;
- all three reproducers compile;
- NumPy and SciPy triggers execute successfully in the auditor's current fixed
  environment; SUNDIALS relative-accuracy parsing independently accepts both
  recorded output forms;
- structured selection/schema/arm comparison: PASS for all three cases;
- full suite from an archive of the immutable handoff commit:
  `260 passed, 10 warnings`.

These checks validate structure and the committed observations. They do not
recreate the historical source builds, because the handoff omits the materials
needed for that independent replay.

## 3. Blockers

### `A1B-HANDOFF-CMD-001` — exact execution record is missing

The handoff contract requires exact commands and exit codes. The manifest gives
only the summaries `docker pull digest-pinned ghcr images` and
`exact-source/pinned-release dual-arm triggers for batch-1 cases`. It does not
record the per-arm source materialisation, interpreter build, dependency
installation, compile, trigger, or output-capture commands. Its `exit_codes`
array also omits the three expected buggy-trigger exit statuses of `1`, although
those statuses appear inside the arm JSON files.

Without exact commands, an auditor cannot replay the claimed environments or
distinguish a faithful build from an equivalent-looking reconstruction. This is
a blocker under the dual-environment handoff contract.

### `A1B-LOCK-PROVENANCE-001` — runbook-required locks and package/source hashes are absent

Runbook section 6.2 requires each pinned-release or exact-source route to save
lock files with exact versions and hashes, record the package/source hash, and
pin the build requirements. No lock or requirements file exists under the
Batch 1 reproducer/reproduction paths.

The environment JSON files record useful `pip freeze` summaries and revision
labels, but they do not provide:

- hash-locked transitive requirements for the NumPy and SciPy environments;
- immutable wheel/sdist hashes for the SciPy 1.5.4/1.6.0 arms;
- downloaded source-archive hashes or checkout verification for the two
  exact-source builds;
- the exact SUNDIALS configure/build/install commands and dependency pins.

Consequently, the claimed build provenance cannot be independently reconstructed
from the committed evidence package. This is a blocker even though the stored
behavioural contrasts agree with the prior verification reports.

## 4. Initial verdict and required correction (historical)

At audit commit `6419fbe3ffb6fd57116ad2586a40365e370321e4`, Gate A1b
Batch 1 was `BLOCKED`. The three contrasts remained valid as narrowly
scoped observations, but A2 remains `PENDING`; the payload/handoff are not
integrated into the local lineage, and Batch 2 remains locked.

A correction handoff must:

1. rerun or deterministically reconstruct all three cases in a fresh workspace;
2. commit the exact per-arm source/download, environment, build, trigger, and
   capture commands with their exit codes, including expected buggy exit `1`;
3. commit per-case lock files containing exact versions and hashes, plus source
   archive or checkout verification hashes;
4. record complete SUNDIALS configure/build/install commands and dependency
   versions;
5. retain the GHCR `403`, Python rebuild, and NumPy submodule retry histories;
6. regenerate output hashes and a direct-child correction handoff;
7. rerun the admission checker, reproducer checks, leakage/forbidden-action
   scan, and full test suite.

Only a zero-blocker re-review may integrate the Batch 1 artifacts and promote
the three case-local A2 values to `PASS` in the later canonical admission
integration.

## 5. Finding-closure re-review

### 5.1 Correction lineage and local integration

| Role | Commit |
|---|---|
| Correction baseline | `607acb044856101d8744f62cd2f7173a396c99b5` |
| Correction payload | `764840f3ad61e8f12ec2ead59422498082a462be` |
| Correction handoff | `09da03a4585130dfb57428983f05ef7a4fb914bc` |
| Local original payload integration | `061e1891` |
| Local original handoff integration | `66b8ca9d` |
| Local correction payload integration | `a7bdaa05` |
| Local correction handoff integration | `1a6d6f35` |

The correction payload is the direct child of the blocked handoff, and the
correction handoff is the direct child of the correction payload. PR #4 and
the remote Cursor branch resolve to the correction handoff. The four Batch 1
commits were integrated into the local lineage in immutable order only after
this re-review found zero blockers.

### 5.2 Closure of `A1B-HANDOFF-CMD-001`

- `BATCH1_COMMAND_LOG.json` contains 61 executed reconstruction commands.
- The correction handoff contains those same 61 commands after removal of the
  retained stdout/stderr tails, plus four explicit verification commands, for
  65 total.
- Per-case `COMMANDS.json` files exactly equal their filtered global-log
  subsets: NumPy 30, SUNDIALS 17, and SciPy 10 commands.
- All commands carry command text, working directory, label, and exit code;
  the global log additionally retains stdout/stderr tails.
- Trigger exits are explicitly and consistently recorded as buggy `1` and
  fixed `0` for all three cases.
- Source materialisation, interpreter/environment preparation, dependency
  installation, compilation, trigger execution, raw harness capture, retries,
  and the three failed GHCR attempts are represented in the command history.

Finding `A1B-HANDOFF-CMD-001` is **CLOSED**.

### 5.3 Closure of `A1B-LOCK-PROVENANCE-001`

- SciPy uses two committed `--require-hashes` locks. The NumPy 1.19.5,
  SciPy 1.5.4, and SciPy 1.6.0 wheel hashes independently match current
  authoritative PyPI metadata.
- NumPy uses a shared eight-package hash-locked build closure for both arms.
  Both `pip install --require-hashes` commands exit `0`.
- NumPy records archive hashes, exact checkout heads, submodule SHAs, and
  completed-tree hashes. Fresh downloads of both pinned GitHub archives
  independently reproduce the committed archive hashes.
- SUNDIALS records both pinned archive hashes, compiler/CMake/make versions,
  complete CMake flags, configure/build/install commands, and identical
  buggy-tree harness-source compilation against each arm. Fresh downloads of
  both archives independently reproduce the committed hashes.
- All corrected individual outputs and the three eight-file directory
  aggregates reproduce the handoff SHA256 values.

Finding `A1B-LOCK-PROVENANCE-001` is **CLOSED**.

### 5.4 Behavioural and repository re-verification

- The approved three-case selection, neutral IDs, issue URLs, and buggy/fixed
  SHAs are unchanged.
- Seed, semantic input, expected property, arm status, and contrast remain
  consistent for all three cases: buggy fails, fixed holds.
- Candidate-sheet A2 remains `PENDING`, aliases remain blank, and no canonical
  sheet or freeze was written.
- Admission checker exits `0`; all reproducers and the reconstruction script
  compile; the intended leakage scan is clean.
- Full test suite from an immutable correction-handoff archive:
  `260 passed, 10 warnings`.
- Batch 2 and all later locked tasks were not started.

### 5.5 Disclosures and verdict

Two non-blocking environment disclosures remain:

1. the original Batch 1 session recorded authenticated GHCR blob `403`; the
   correction session's fresh pull attempts instead failed earlier on Docker
   socket permission. Both failures are preserved, and the audited evidence
   comes from the permitted host-rebuild routes;
2. the correction created fresh SciPy arm venvs but reused the previously
   verified SSL-enabled CPython 3.9.18 toolchain. Both arms share it, its
   version/path and upstream tarball hash are recorded, and the hash-locked
   wheels independently match PyPI.

Gate A1b Batch 1 is `PASS_WITH_DISCLOSURE`. The three case-local dual-arm
readiness results are accepted as A2 `PASS` evidence for later canonical
integration. C3 Batch 2 is unlocked; canonical admission freeze, A2/C4,
fiber mapping, predictions, kill execution, and all later phases remain locked.
