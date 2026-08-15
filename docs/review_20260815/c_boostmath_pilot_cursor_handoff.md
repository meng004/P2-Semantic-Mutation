# C-BOOSTMATH-001 Cursor handoff

Status: **PENDING_SOL_REVIEW**
Authorization: **NOT AUTHORIZED FOR 35-SUBJECT EXPANSION**

Executor role only. Claim adjudication and any 35-subject decision remain
with Sol High.

## Base / head

| Item | SHA |
|---|---|
| Required P3 base commit | `8cd3e2da8ab31cc313a17fed01dc63ea84d59690` |
| Required P3 base tree | `be48398268f8096b6872d9e918f3064fa13cea98` |
| Branch | `cursor/p3-c-boostmath-pilot-001` |
| Head after evidence commit | `422420ebaf169a34106eb2e0f78527c9b3856c1c` |

Start-gate check at session open:

```text
git rev-parse HEAD
8cd3e2da8ab31cc313a17fed01dc63ea84d59690
git rev-parse HEAD^{tree}
be48398268f8096b6872d9e918f3064fa13cea98
git status --porcelain
(empty)
```

## New commits

1. `39cd3f4b078e3b8037898df38858de7bf2a82f85`
   `feat(p3-v3): add isolated boostmath pilot runner`
2. `422420ebaf169a34106eb2e0f78527c9b3856c1c`
   `exp(p3-v3): record C-BOOSTMATH-001 pilot evidence`

## Exact execution commands

```bash
git switch -c cursor/p3-c-boostmath-pilot-001
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  libboost-dev python3-pytest python3-yaml python3-pip
# P12 GitHub clone returned 404; Zenodo 1.0.1 used for the five required files.
curl -fsSL -o .pilot-work/P12-Defect4MR-1.0.1.zip \
  https://zenodo.org/api/records/21203937/files/P12-Defect4MR-1.0.1.zip/content
git clone --filter=blob:none --no-checkout https://github.com/boostorg/math.git \
  .pilot-work/boost-math
git -C .pilot-work/boost-math rev-parse --verify 03ea9c8^{commit}
git -C .pilot-work/boost-math rev-parse --verify 75dcb3e^{commit}
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_c_boostmath.py -q
PYTHONPATH=src python3 scripts/p3_v3/run_c_boostmath_pilot.py
```

No `rtk`. Compiler and `-O2 -std=c++14` were not changed after seeing outcomes.

## Identities

### P3

- Base: `8cd3e2da8ab31cc313a17fed01dc63ea84d59690` /
  `be48398268f8096b6872d9e918f3064fa13cea98`

### P12

- Required commit: `a324498e22b8bd6126de89cf3613680cfad94b3b`
- GitHub clone: **INACCESSIBLE** with the Cursor installation token
  (`Repository not found`)
- Fallback: Zenodo `10.5281/zenodo.21203937` `P12-Defect4MR-1.0.1.zip`
  - md5 `c8fe0b296441f3ceb94e5696c5fcd608`
  - sha256 `39c53ef016accf7d0108827a41f4284e0437aad7300eb01970adf4ce3433eb7f`
  - zip git comment `3639356ff11c5907d8ca45b0fe64ffe6d7543017`
- Five required file SHA-256 values: **MATCH** the task brief
- Historical JSONL SHA-256: **MATCH**
  `b3af810dd383368d1fcd07374912fef10720d333dd33a400e32e01498b10429c`

### Boost.Math

| Arm | Full SHA | Tree SHA |
|---|---|---|
| fixed `03ea9c8` | `03ea9c8d7dff1083facd134c8f641e006b68fdae` | `dc86f3259c84f68ac7c4e2be11a1ed8567011240` |
| buggy `75dcb3e` | `75dcb3e3d560663be7e4e04dc4556d12fe54e348` | `e0b72128532db7dbac0fb2c1bfb740ba0851f576` |

Each short SHA resolved uniquely. Metadata is in
`data/p3_v3/pilots/c-boostmath-001/identities.json`.

## Tests

```text
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_c_boostmath.py -q
13 passed in 0.03s

PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_pilot_c_boostmath.py \
  tests/p3_v3/test_artifacts.py \
  tests/p3_v3/test_run_records.py \
  tests/p3_v3/test_cli.py -q
512 passed in 595.49s
```

The remaining `tests/p3_v3` adapter/preflight/frame files were not part of
the added module. They were left unrun to avoid treating an unrelated suite
as this pilot’s receipt. This VM is not syscall-sandboxed for pytest
(the 512-test run completed). Label: `FULL_SUITE_NOT_RUN_UNRELATED`.

## Artifact hashes

File SHA-256 of the durable bytes. Self-hashes inside JSON, where present,
are listed in parentheses.

| Artifact | File SHA-256 |
|---|---|
| contract.json | `2b01213e8f1577e87ccaa2e3e98548dea333688abb94be7e751b1e7a6751ba24` (`contract_sha256=2b79fd46cc188d53f8438ee3c6edec182fbe56c77dc34c7221be2419f4b1dd17`) |
| fixture-import.json | `1b97624c13e5876d23c79c016805a7392dae0b987394e66d965b3d6bfdbfbb88` |
| certification.json | `c66619d4800d631f279d01546e2bfd3a6fc087a0f5c605d036a4ba9ec43ef2c9` |
| mr-inventory.json | `64cde56347edab98801c4be2bf4c4f22fef1f2aa0a6e7626cadf31cac7c06f18` |
| atomic-ledger.jsonl | `41253ecc312606f3c327fba466733291de340014c1bf051f7beef1cef9892543` |
| comparison.json | `85512fcfa54271006f778c5ba79d2fc52c9fed18ce8d3bc631ff6b3425ddf390` (`artifact_sha256=0dd3e96de7fd594484ae89a762585c9185dc9509016c1393639ef9755a21cd33`) |
| historical-replay.json | `6f8ac65f0972790f6a1471a99b803ee9df96e0c90ee1b76f33d70bbecb968e28` |
| historical-replay-detail.json | `23a786ceccb51a615d843e74c5a0a049a3508a10aff18cb0d61b51303af58129` |
| identities.json | `e2f2e86070cc7a9831e311d52a15547bc90f89e55fbcaef8ecc5ed60842d3216` |
| environment.json | `0d31795fc0a50c36d291817969a2fc7d149f7fa2c2386fb70f14a250d956ac64` |

## Certification terminal states

- roots_m037: `CONFIRMED_NON_EQUIVALENT`
- roots_m003: `CONFIRMED_NON_EQUIVALENT`

## MR matrix / comparison

- `data/p3_v3/pilots/c-boostmath-001/comparison.json`
- `data/p3_v3/pilots/c-boostmath-001/atomic-ledger.jsonl`
- Raw stdout/stderr: `data/p3_v3/pilots/c-boostmath-001/logs/`

## Fresh versus historical

Historical file hash matched. After close, the two imported fixtures mapped
onto the same per-MR states as the historical JSONL (`PASS` / `VIOLATED` /
`CRASH`). Other historical mutants were not replayed. No rerun was performed
to force agreement.

## Deviations and failures

1. Requested model was Grok 4.5 High. This run used Cursor Grok 4.6 High Fast
   (`originalModelName=cursor-grok-4.6-high-fast`).
2. `git clone https://github.com/meng004/P12-Defect4MR.git` failed (private
   repo, token 404). Byte-identical required files were taken from Zenodo
   1.0.1. Required P12 commit was not checked out as a git object.
3. Boost include trees were materialized from GitHub archives after unique
   commit resolution on a blobless clone.
4. Formal `p3_v3.run_records` claim/intent schemas were not used; they cannot
   express pilot claim statuses or certification terminal states.
5. roots_m037 T1 terminated as `CRASH` (`evaluation_error`), matching
   historical `kill/crash_rc-6`. Not retried.
6. No PR and no merge, per task instruction.
7. Phase 1 was not marked `PHASE1_CLOSED`.
8. Ordinary apt packages were installed (`libboost-dev`, `python3-pytest`).
   Compiler and optimization were not swapped to chase an outcome.

## Claim ledger summary

- `PILOT_C0_PIPELINE_EXECUTED`: supported
- `PILOT_C1_SINGLE_CASE_MR_DIFFERENCE`: observed
  wording starts with “In this retrospective pilot run...”
- P3 C1–C8: blocked
- Semantic superiority, criterion validity, 35-subject effect, automatic
  generation validity, and outcome blindness: blocked

## Explicit status

- `PENDING_SOL_REVIEW`
- `NOT AUTHORIZED FOR 35-SUBJECT EXPANSION`
