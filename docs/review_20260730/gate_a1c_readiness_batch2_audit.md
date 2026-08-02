# Gate A1c — C3 Readiness Batch 2 Audit

- **Audit time:** `2026-08-01T23:54:40+08:00`
- **First correction re-review:** `2026-08-02T08:22:24+08:00`
- **Second correction re-review:** `2026-08-02T08:43:52+08:00`
- **Scope:** the 29 Gate A1a-approved queue rows remaining after Batch 1
- **Verdict:** `PASS_WITH_DISCLOSURE`
- **Open blockers:** 0; all four original findings are closed after two correction rounds
- **Successor state:** only C3 Batch 3 for the six A1/A3-passing supplemental-pilot rows is unlocked; canonical admission freeze, A2/C4, fibre mapping, prediction, and detection runs remain locked

## 1. Audited lineage

| Role | Commit / value |
|---|---|
| Cursor branch | `origin/cursor/grok-phase3-c3-readiness` |
| Gate A1b baseline | `09da03a4585130dfb57428983f05ef7a4fb914bc` |
| Batch 2 membership freeze | `c94684faadbb4b02f8685360255cc374c15183c8` |
| Batch 2 payload | `20c445d7aa50f377e1aeb87f73774142f9d75cff` |
| Batch 2 handoff | `1f1586e66712ff220386e7c29e98593cda7e48ba` |
| Pull request | `#4`, OPEN, head `1f1586e66712ff220386e7c29e98593cda7e48ba` |

The three Batch 2 commits are consecutive descendants of the approved Gate A1b
baseline. The remote branch and PR head both resolve to the handoff commit. The
PR title still names Batch 1; this is a non-blocking metadata disclosure.

## 2. Independently verified facts

### 2.1 Membership and no substitution

- The pre-readiness candidate contains exactly 32 rows with A1 `PASS`, A2
  `PENDING`, A3 `PASS`, and decision `ADMIT_PENDING_REPRO`.
- Removing the three Batch 1 IDs leaves exactly the 29 frozen Batch 2 members,
  in candidate-sheet order. IDs are unique, there is no Batch 1 overlap, and
  membership fields match the sheet.
- `readiness_batch2.json`, the handoff case list, and the membership freeze use
  the same 29 IDs and order. No replacement occurred.
- The candidate sheet remains byte-identical at SHA256
  `4b0296c3656219e77a03acf1e9a727f574651bbaf1650ae07f31f2c47294adb8`;
  every A2 field remains `PENDING`.

### 2.2 Results and command structure

- Proposed results reproduce as 9 `PASS` and 20 `REPRO_FAILED`.
- Failure stages reproduce exactly: `build_or_trigger` 8, `contrast` 3,
  `build` 3, `PLATFORM_GATE:era-julia` 3, `PLATFORM_GATE:gpu` 2, and
  `PLATFORM_GATE:arch` 1.
- The global command log has 268 records. Concatenating the 29 per-case
  `COMMANDS.json` arrays in frozen order produces the same 268 records exactly.
- All 9 proposed-PASS records store seed 0, buggy `property_holds=false` and
  exit 1, fixed `property_holds=true` and exit 0.
- Fresh downloads independently reproduce all 18 buggy/fixed public source
  archive hashes for the 9 proposed-PASS cases. The shared Boost 1.84.0 release
  archive also reproduces its recorded SHA256.

### 2.3 Fresh executable checks

- admission checker: exit 0, explicitly pre-readiness-only PASS;
- Batch 2 runner and all reproducers: `compileall` exit 0;
- complete suite from an archive of the immutable handoff:
  `260 passed, 10 warnings`;
- neutral-ID leakage scan: exit 1 with no output;
- GitHub-token scan: exit 1 with no output; retained bearer values are exactly
  `<REDACTED_GITHUB_TOKEN>`.

These checks validate the committed structure. They do not override the four
handoff and provenance blockers below.

## 3. Blocking findings and correction contracts

### `A1C-HANDOFF-HASH-001` — 19 declared artifact hashes do not identify the committed files

The handoff SHA256 values for 19 per-case `COMMANDS.json` files do not match the
files at `1f1586e6...`. Every mismatch is in a case that downloaded an archive;
the committed command files contain redacted bearer tokens. Other declared
file hashes match. This is consistent with per-case hashes being captured
before final token redaction, but the handoff does not identify the committed
artifacts and therefore fails the immutable handoff contract.

Correction contract:

1. Complete all redaction and normalization before hashing.
2. Recompute every handoff file and per-case artifact SHA256 from the final
   committed-byte candidates, not from in-memory pre-redaction content.
3. Commit the corrected handoff and provide a checker that exits 0 only when
   every declared hash matches.

### `A1C-FREIA-LOCK-001` — FrEIA PASS used an un-hashed dependency fallback

For both FrEIA arms, `pip install --require-hashes -r requirements.deps.txt`
exited 1. The runner then installed NumPy, SciPy, Torch, and transitive
dependencies from network indexes without `--require-hashes`, and nevertheless
promoted `EXT-freia-01` to proposed PASS. Exact version arguments do not satisfy
the runbook's hash-lock requirement, particularly because transitive packages
were resolved during the fallback.

Correction contract:

1. Recreate both FrEIA arms from clean, separate environments.
2. Install the recorded dependency closure with `--require-hashes` and the
   required PyTorch index arguments, or from a hash-verified local wheelhouse.
3. Require both locked installation commands to exit 0; remove the un-hashed
   fallback route.
4. Rerun both triggers and regenerate FrEIA environment, commands, outputs,
   readiness entry, global command log, and handoff hashes.

### `A1C-BUILD-EVIDENCE-001` — three `REPRO_FAILED:build` outcomes have no build attempt

`EXT-trilinos-01`, `EXT-dealii-01`, and `EXT-castro-01` each record only four
successful commands: download and extraction for the two arms. No configure,
build, trigger, timeout, or non-zero build exit exists. The runner assigns
`REPRO_FAILED:build` from a hard-coded assertion that a full build exceeds the
VM budget. Under runbook §§4, 6.3, and 7, a predicted resource burden is not an
observed failed build.

Correction contract:

1. Attempt both-arm builds with exact commands and a declared bounded timeout,
   preserving stdout, stderr, and actual exits, then run the trigger if builds
   succeed.
2. Code `REPRO_FAILED:build` only from an observed build error or timeout.
3. If the study needs a resource-based platform gate without attempting the
   build, stop and obtain an explicit protocol amendment instead of silently
   treating the estimate as build evidence.

### `A1C-HANDOFF-VERIFY-CMD-001` — verification claims lack exact commands and exits

The handoff stores summary strings for admission and pytest, but its 268-command
log contains only case execution. It does not retain the exact admission,
pytest, compile, leakage, or token-scan commands and their exits. This repeats
the command-provenance class closed at Gate A1b.

Correction contract:

1. Rerun admission, full pytest, compile, neutral-leak, token-leak, membership,
   and handoff-hash checks after the corrections above.
2. Record every exact command, working directory, exit code, and sufficient
   output in the corrected handoff or a referenced verification log.

## 4. Initial gate decision

Gate A1c is `BLOCKED`. The 29-row membership freeze and no-substitution rule are
accepted, and eight non-FrEIA proposed-PASS contrasts are provisionally
consistent with their recorded evidence. The FrEIA PASS, three unsupported
build failures, and handoff integrity cannot be accepted until the four
findings close.

No Batch 2 commit is cherry-picked into the local lineage. Batch 3+, candidate
A2 promotion, canonical admission freeze, C4, fibre/category work, prediction,
and detection runs remain locked. The only unlocked work is a new Cursor
correction session based on `1f1586e66712ff220386e7c29e98593cda7e48ba`.

## 5. Correction re-review

### 5.1 Correction lineage and unchanged boundaries

| Role | Commit / value |
|---|---|
| Blocked handoff | `1f1586e66712ff220386e7c29e98593cda7e48ba` |
| Correction payload | `9f6f65afae8d9849b485dde94865a613d9d14269` |
| Correction handoff | `01acdbbf6ffd220f9b768ffd386f02cc7fff591b` |
| PR state | `#4`, OPEN, head `01acdbbf6ffd220f9b768ffd386f02cc7fff591b` |

The correction payload is the direct child of the blocked handoff and the
correction handoff is the direct child of the payload. The 29-row membership
and candidate sheet are unchanged; A2 remains `PENDING`, and the diff contains
no Batch 3+, annotation, freeze, prediction, or result artifacts.

### 5.2 Findings closed by the correction

#### `A1C-HANDOFF-HASH-001` — CLOSED

- Final-byte hashing now occurs after command/log redaction.
- The independent auditor recomputed every top-level and per-case declared hash:
  zero mismatches.
- `check_batch2_handoff_hashes.py` independently exits 0 with
  `HASH_CHECK_OK` on the immutable correction handoff.

#### `A1C-BUILD-EVIDENCE-001` — CLOSED

- Trilinos buggy/fixed configure commands each exit 0; both bounded build
  commands exit 2 with 900-second limits and retained compiler output.
- deal.II buggy/fixed configure commands each exit 0; both bounded build
  commands exit 2 with 900-second limits and retained compiler output.
- Castro buggy/fixed clean/build commands and triggers all exit 0. Both arms
  satisfy the same property, so the case is conservatively recoded from
  `REPRO_FAILED:build` to `REPRO_FAILED:contrast`.
- The total remains 9 PASS / 20 REPRO_FAILED; the failure-stage distribution is
  now build 2 and contrast 4, with all other categories unchanged.

### 5.3 Findings not yet closed

#### `A1C-FREIA-LOCK-001` — PARTIALLY FIXED, STILL OPEN

Both fresh FrEIA arms now run the runtime dependency command with
`--require-hashes` and the required PyTorch/PyPI index arguments; both commands
exit 0, no dependency fallback is present, and the behavioural contrast remains
buggy 1 / fixed 0. Source and wheel hashes are retained.

However, the build path is still outside the exact-source contract:

- each fresh venv first runs unpinned, un-hashed
  `pip install -U pip wheel setuptools`;
- `pip install --no-deps <source>` omits `--no-build-isolation`;
- its retained stdout explicitly says `Installing build dependencies`, meaning
  pip created an isolated build environment and resolved build requirements not
  covered by `requirements.deps.txt` or `WHEEL_ARTIFACT_HASHES.json`.

The fixed runtime dependency closure therefore does not yet establish a fully
hash-locked exact-source build. To close the finding, place the packaging/build
closure (including the actually used pip/setuptools/wheel/packaging versions as
applicable) under hashes, install it identically in both arms, run the source
installation with `--no-build-isolation`, and rerun both triggers from new
venvs. The source-install commands must exit 0 without any isolated dependency
resolution.

#### `A1C-HANDOFF-VERIFY-CMD-001` — PARTIALLY FIXED, STILL OPEN

`BATCH2_VERIFICATION_LOG.json` now records seven commands with cwd, exit,
stdout, and stderr, and admission/pytest/compile/membership/hash checks are
auditable. The neutral-leak command is nevertheless non-functional:

- the stored regex contains double backslashes such as
  `\\boperator\\b`, so ripgrep searches for literal backslash sequences instead
  of word boundaries;
- on a retained compiler log known to contain `operator`, the stored expression
  exits 1 with no match, while the correctly escaped `\boperator\b` expression
  returns 45 matches;
- scanning raw compiler/source logs for the generic C++ word `operator` would
  be a false-positive-prone scope in any case. The actual runbook reserved-term
  scan over the decision-level Batch 2 artifacts independently exits 1 with no
  output.

The token scan also checks only `ghp_`; it omits `github_pat_` and an
unredacted `Bearer` pattern. The independent broader scan currently finds no
leak, but the committed verification command does not prove that claim.

To close the finding, replace the neutral scan with the exact runbook reserved
pattern and an appropriate decision-artifact scope, and broaden the token scan
to all supported token forms. Record the expected clean exit semantics, rerun
both scans, update the verification log, rehash the handoff, and rerun the hash
checker.

### 5.4 Correction re-review decision

Gate A1c remains `BLOCKED` with two open blockers. The correction commits are
not cherry-picked locally. Only a second correction session based on
`01acdbbf6ffd220f9b768ffd386f02cc7fff591b` is unlocked; Batch 3+, candidate A2
promotion, canonical admission freeze, C4, fibre/category work, prediction, and
detection runs remain locked.

## 6. Second correction re-review and final decision

### 6.1 Lineage, boundary preservation, and local integration

| Role | Commit / value |
|---|---|
| Second-correction baseline | `01acdbbf6ffd220f9b768ffd386f02cc7fff591b` |
| Second-correction payload | `70c4ae0546d98267edfd80ee7023d94ad8111b98` |
| Second-correction handoff | `929e93f8a50cd8aedea618ad7016aada72e0cc16` |
| PR state at audit | `#4`, OPEN draft, head `929e93f8a50cd8aedea618ad7016aada72e0cc16` |
| Local membership integration | `543dd90f` |
| Local original payload / handoff | `ddaac13c` / `f0256427` |
| Local first-correction payload / handoff | `406f507d` / `b1f24356` |
| Local second-correction payload / handoff | `29df0ac9` / `a3c07e34` |

The two new commits are consecutive descendants of the first correction. The
29-row membership file, the 64-row candidate sheet, the nine-row supplemental
pilot sheet, and all later-stage freeze/result paths are unchanged by the
second correction. Every candidate-sheet A2 value remains `PENDING`; no Batch
3, annotation, alias, prediction, or detection artifact was created.

### 6.2 `A1C-FREIA-LOCK-001` — CLOSED

- Both arms were recreated as distinct venvs.
- Both arms installed the packaging/build closure from
  `requirements.build.txt` with `--require-hashes`; the lock covers exact
  `pip`, `setuptools`, `wheel`, and `packaging` versions and four artifact
  hashes. The artifact manifest and lock agree.
- Both arms installed the runtime closure with `--require-hashes` and no
  fallback, then installed their exact source tree with both `--no-deps` and
  `--no-build-isolation`. All six install commands exited 0.
- Neither retained source-install output contains `Installing build
  dependencies`; no isolated resolver route remains.
- The deterministic contrast is unchanged: buggy normalized exit 1 and fixed
  normalized exit 0 at seed 0.

### 6.3 `A1C-HANDOFF-VERIFY-CMD-001` — CLOSED

- The committed reserved-term expression equals runbook §3's hexadecimal
  expression and is scoped to decision-level Batch 2 artifacts. An independent
  positive control matched retained `fiber` text, proving the expression is
  functional; the decision-artifact scan then returned raw `rg` exit 1 with no
  output.
- The committed token scan covers `ghp_`, `github_pat_`, and unredacted
  `Bearer` values. The independent raw scan returned exit 1 with no output.
- The verification log records the clean raw-exit contract (`rg=1`) and the
  normalized checker exit (`0`) for both scans. Admission, pytest, compileall,
  membership, and handoff-hash commands and exits remain present.

### 6.4 Independent final verification

- Frozen membership equals the approved 32-row queue minus the three Batch 1
  IDs, in sheet order: 29 unique members, no substitution or overlap.
- The global command log contains 281 entries and exactly equals the ordered
  concatenation of all 29 per-case command arrays.
- Results remain 9 proposed `PASS` and 20 `REPRO_FAILED`. Failure stages are
  `build_or_trigger` 8, `contrast` 4, `build` 2,
  `PLATFORM_GATE:era-julia` 3, `PLATFORM_GATE:gpu` 2, and
  `PLATFORM_GATE:arch` 1.
- Every top-level and per-case handoff SHA256 matches; the committed checker
  exits 0 with `HASH_CHECK_OK`.
- The admission checker exits 0 with its explicit pre-readiness-only notice;
  compileall exits 0; the complete immutable-snapshot suite reports
  `260 passed, 10 warnings`.

### 6.5 Verdict and next boundary

All four original Gate A1c blockers are closed. Gate A1c is therefore
`PASS_WITH_DISCLOSURE`. The disclosures are procedural only: PR #4's title
still names Batch 1 although its head contains Batch 2, and the accepted
lineage preserves two auditable correction rounds rather than squashing them.

The 29-case Batch 2 evidence is accepted as case-local readiness evidence; it
is integrated without modifying the candidate sheet. Together with Batch 1,
the frozen 32-row queue has 12 proposed ready cases and 20 retained failures.
This is below the protocol's ready `n >= 20` target, and the separate
nine-row supplemental pilot still has six A1/A3-passing rows with A2
`PENDING`. Consequently, the only unlocked successor is a fresh Cursor VM
session for C3 Batch 3 over exactly those six rows. Canonical admission freeze,
human annotation/C4, category mapping, prediction, and detection execution stay
locked pending that handoff and its next local gate.
