# Gate A1c — C3 Readiness Batch 2 Audit

- **Audit time:** `2026-08-01T23:54:40+08:00`
- **Scope:** the 29 Gate A1a-approved queue rows remaining after Batch 1
- **Verdict:** `BLOCKED`
- **Open blockers:** 4
- **Successor state:** correction work only; Batch 3+, canonical admission freeze, A2/C4, fibre mapping, prediction, and detection runs remain locked

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

## 4. Gate decision

Gate A1c is `BLOCKED`. The 29-row membership freeze and no-substitution rule are
accepted, and eight non-FrEIA proposed-PASS contrasts are provisionally
consistent with their recorded evidence. The FrEIA PASS, three unsupported
build failures, and handoff integrity cannot be accepted until the four
findings close.

No Batch 2 commit is cherry-picked into the local lineage. Batch 3+, candidate
A2 promotion, canonical admission freeze, C4, fibre/category work, prediction,
and detection runs remain locked. The only unlocked work is a new Cursor
correction session based on `1f1586e66712ff220386e7c29e98593cda7e48ba`.
