# Gate A1b — C3 Readiness Batch 1 Audit

- **Audit time:** `2026-08-01T20:46:14+08:00`
- **Scope:** first C3 dual-arm readiness batch; three digest-pinned cases in the Gate A1a-approved 32-row queue
- **Current verdict:** `BLOCKED`
- **Observed contrast status:** three case-local contrasts are `observed`; none is promoted to A2 `PASS` until the reproduction contract is closed
- **Successor state:** Batch 2, canonical admission freeze, A2/C4, fiber mapping, predictions, and result execution remain locked

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

## 4. Verdict and required correction

Gate A1b Batch 1 is `BLOCKED`. The three contrasts remain valid as narrowly
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
