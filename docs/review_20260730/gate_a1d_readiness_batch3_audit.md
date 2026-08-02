# Gate A1d — C3 Readiness Batch 3 Audit

- **Audit time:** `2026-08-02T13:44:43+08:00`
- **Cursor branch:** `origin/cursor/grok-phase3-c3-readiness-batch3`
- **Draft PR:** #6; OPEN; head `da70fa676ebcab8ef1e98f532aa711c2d01f0c84`
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
