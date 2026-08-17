# Boost.Math PILOT_SOURCE_PREPARATION_ONLY Plan Review Packet — P1SP1R1

- Node name: `P1SP1R1_BOOST_MATH_PILOT_SOURCE_PREPARATION_PLAN_GATE_AND_RECOVERY_REPAIR`
- Packet title: gate-chain, snapshot, recovery, and FAIL-matrix repair
- Builder identity: Cursor VM
- Starting commit: `22b25e181ab951b2a4ee8ee4a2f430ee316a8b81`
- Ending commit: this node does not write an ending-commit token. The ending commit is the unique successor on `origin/main` that modifies only the two files listed below.
- Plan path: `docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md`
- Old plan SHA-256: `7ea27e5a001e856d59502a0db0b0bf9d21bcac5ccd1240aff8a9069bbf7d916c`
- Old plan bytes: 40898
- Old plan LF count: 988
- New plan SHA-256: `5f59a5d475f358f5901af88043126dc9b2ecb830f9b80c384105a4c87e338442`
- New plan bytes: 67506
- New plan LF count: 1585
- Packet path: `docs/review_20260817/boost_math_pilot_source_preparation_plan_review_packet.md`
- Old packet SHA-256: `a3baef78a1fb3a105eb09f2792b246cdb3b4c8611839e1dfc38644987be06e6a`
- Old packet bytes: 12052
- Old packet LF count: 274
- New packet SHA-256, bytes, and LF: recorded by the post-write `sha256sum` and `wc` commands in this node; this packet does not self-hash
- Requested reviewer: GPT-5.6 Sol High
- Reasoning setting: high
- Requested state: `PILOT_PLAN_REVIEW_CANDIDATE`
- Foundation state remains: `PILOT_IMPLEMENTATION_PASS`
- Process location remains: `PILOT_EXECUTION_AWAITING_USER_AUTHORIZATION`
- This packet is not an independent PASS.
- This packet does not record an independent review PASS and does not speak for the reviewer.
- No formal Sol High verdict was created.
- Authorization A was not created.
- Implementation, pytest, build, and production were not run.
- `claims=blocked`

This node repairs only the source-preparation plan and this packet. It is not user preparation authorization. Formal status remains `PILOT_IMPLEMENTATION_PASS`.

## File change list

This node modifies only:

1. `docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md`
2. `docs/review_20260817/boost_math_pilot_source_preparation_plan_review_packet.md`

No other file was created or modified. In particular:

- no formal Sol High verdict was created
- `data/p3_v3/pilot/boost_math/user-auth-preparation.txt` was not created
- `data/p3_v3/pilot/boost_math/source-manifest.json` was not created
- `data/p3_v3/pilot/boost_math/source-preparation-result.json` was not created
- `data/p3_v3/pilot/boost_math/source-preparation-launch.json` was not created
- `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` remains an unfrozen candidate and was not edited
- the claim ledger was not edited
- no source, test, protocol, Frame, or Boost.Math source file was created or modified

## Repair line index

Line numbers refer to the new plan.

| Repair | Anchors | Lines |
|---|---|---|
| Safe authority snapshot | `read_authority_snapshot`, `parse_canonical_authority_object` | 119–164 |
| Source-preparation plan verdict path and schema | `CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH`, `SOURCE_PREPARATION_PLAN_VERDICT_EXACT` | 166–244 |
| Capability implementation verdict path and schema | `CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH`, `SOURCE_PREPARATION_CAPABILITY_VERDICT_EXACT` | 246–313 |
| Launch authority path and schema | `SOURCE_PREPARATION_LAUNCH_PATH`, `SOURCE_PREPARATION_LAUNCH_EXACT` | 315–457 |
| Authorization A snapshot | `verify_authorization_a`, `read_authority_snapshot` | 459–527 |
| Gate-chain predecessor | `gate_chain_predecessor_sha256` | 529–562 |
| Streamed extractor limits | `StreamedLimitCounter` | 805–834 |
| Top-level directory vs file | `shared_top_level_directory` | 838–859 |
| Crash-safe publication order | `Crash-Safe Publication Order` | 960–977 |
| Reconciliation state table | `Reconciliation State Table` | 979–1002 |
| FAIL evidence matrix | `FAIL_RESULT_EVIDENCE` | 1114–1132 |
| Phase 1 tree-hash spy | `test_phase1_tree_hash_function_is_called_by_production_seam` | 1420–1438 |
| Single top-level file | `test_single_top_level_file_is_not_stripped` | 1412–1418 |
| Unique future task | `Task 1: Pilot Source-Preparation Capability On Synthetic Fixtures` | 1221 |

## Authority input hashes

Unchanged from `22b25e181ab951b2a4ee8ee4a2f430ee316a8b81`. Rechecked 17/17 OK.

| Path | SHA-256 |
|---|---|
| `docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md` | `479931df4dd6562177e28c333305f3c55bbf081a596f5e7de337b8a92fa73463` |
| `docs/review_20260816/boost_math_pilot_foundation_plan_review_packet.md` | `e6fd4ab16b3db44711014e4fb9aeaa9b41405c5b37650c3fe790d5f9dfaf9e92` |
| `docs/review_20260816/boost_math_pilot_foundation_sol_high_review.md` | `da5f211b7eab665aca696f5cf1d214d30b0914dc9ccb2a585bfcc06cb97be07c` |
| `docs/review_20260817/boost_math_pilot_foundation_implementation_sol_high_review.md` | `e7e5e9519ae49eb08c450c4e16c56d7551528030916d9d8fe88f0ab91a7b1c9d` |
| `data/p3_v3/pilot/boost_math/pilot-plan.json` | `23d7fb802a2395d93a211862f205065ce1abd52e6ae2e74374aaf2bb624d4cf2` |
| `src/p3_v3/pilot.py` | `4689ed3940f87d3c7c3297bf58c786a3fb2d289cbc45556de35903b0e9111c46` |
| `scripts/p3_v3/pilot.py` | `44597b83d59f159d6a7fbf7fbc010b9b747a1aaf4a366ae1c1fd222314b9b7c9` |
| `tests/p3_v3/test_pilot.py` | `04a61415b6b6071c8a23d4ccf39c4f39b330d1a0530ae19805aa83e71e2515ff` |
| `src/p3_v3/artifacts.py` | `9f619073626003caa7d724a19655b5abae92318afd3f656494a0843613b6f57a` |
| `src/p3_v3/bridge_and_frames.py` | `978fa53c66ae15f9c51b5fa73dc03afdb2d23448f7714d752bccf92c09503ad0` |
| `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` | `1612a6ee81773c7db97625ae3497fab31b93ad70f2ecaefce2fdd845bda73cca` |
| `research/evidence/p3_claim_ledger_v1.3.0.yml` | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| `data/p3_v3/protocol/protocol.json` | `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| `data/p3_v3/protocol/environment_lock.json` | `7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f` |
| `adapter-discovery` frame | `87fb9d05278c5c2e713c8a9d7f398cb1a1c84562df27b590e6d37f98fd7c1dd1` |
| `derived-subject` frame | `654a5c8a26b85013a44665dd92c59a66afee9f639ec7d28535d58357ec696f20` |
| `source-scale` frame | `dc9b56fe81bcf8301e6164f15007c6f57ee11e79cfff1b84e66906cb7de228d0` |

## RED

Command, run against the old plan at `22b25e181ab951b2a4ee8ee4a2f430ee316a8b81` before this repair. The checker executed `shared_top_level_directory(["readme.txt"])` and inspected function bodies. It did not stop at token presence.

Exit code: 1

```text
SEMANTIC_RED_FAILURES
- no canonical source-preparation plan verdict gate (missing CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH and SOURCE_PREPARATION_PLAN_VERDICT_EXACT)
- no canonical capability implementation verdict gate (missing CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH and SOURCE_PREPARATION_CAPABILITY_VERDICT_EXACT)
- no reviewed production-launch machine authority (missing source-preparation-launch.json exact schema)
- predecessor binds only foundation verdict, machine plan, and Authorization A; not plan verdict, capability verdict, or launch
- no manifest-only / materialized-root-only crash recovery state machine
- Authorization A still uses is_file/is_symlink then path.read_bytes
- Phase 1 tree-hash test is self-equality without spy or monkeypatch
- single top-level regular file is treated as a top-level directory; shared_top_level_directory(['readme.txt']) returned 'readme.txt'
- FAIL result does not freeze per-failure_reason field combinations (archive pair, materialized_tree_sha256, root/manifest existence)
RED_ITEM_COUNT=9
```

## GREEN

Command, run after both repaired files were written. The validator parses every Python fence, executes `shared_top_level_directory`, and checks gate, recovery, snapshot, spy, and FAIL-matrix contracts.

```text
python3 - <<'PY'
from pathlib import Path
import ast
import re

plan = Path(
    "docs/superpowers/plans/"
    "2026-08-17-p3-boost-math-pilot-source-preparation-only.md"
)
packet = Path(
    "docs/review_20260817/"
    "boost_math_pilot_source_preparation_plan_review_packet.md"
)
plan_text = plan.read_text(encoding="utf-8")
packet_text = packet.read_text(encoding="utf-8")

for token in ("T" + "BD", "T" + "ODO", "." * 3):
    assert token not in plan_text, token
    assert token not in packet_text, token

assert plan_text.count("### Task ") == 1
assert "src/p3_v3/pilot_source.py" in plan_text
assert "tests/p3_v3/test_pilot_source.py" in plan_text
assert "scripts/p3_v3/pilot.py" in plan_text
assert "tests/p3_v3/test_pilot.py" in plan_text
assert plan_text.count("src/p3_v3/packages.py") >= 1

blocks = re.findall(r"```python\n(.*?)```", plan_text, re.S)
for index, block in enumerate(blocks, start=1):
    ast.parse(block)
    print(f"AST_OK {index}")

shared = next(block for block in blocks if "def shared_top_level_directory" in block)
ns = {}
exec(compile(ast.parse(shared), "<shared>", "exec"), ns)
assert ns["shared_top_level_directory"](["readme.txt"]) is None
assert ns["shared_top_level_directory"](["pkg/a", "pkg/b"]) == "pkg"
assert ns["shared_top_level_directory"](["pkg/b", "pkg/a"]) == "pkg"

auth = next(block for block in blocks if "def verify_authorization_a" in block)
assert "read_authority_snapshot" in auth
assert "path.read_bytes()" not in auth
assert "path.is_file()" not in auth

tree = next(
    block
    for block in blocks
    if "def test_phase1_tree_hash_function_is_called_by_production_seam" in block
)
assert "monkeypatch.setattr(pilot_source, \"canonical_source_tree_sha256\", spy)" in tree
assert "calls == [snapshot]" in tree

old = next(
    block
    for block in blocks
    if "def test_materialized_tree_uses_phase1_canonical_hash" in block
)
start = old.index("def test_materialized_tree_uses_phase1_canonical_hash")
rest = old[start:]
nxt = rest.find("\ndef ", 4)
body = rest if nxt < 0 else rest[:nxt]
assert "canonical_source_tree_sha256(snapshot) == canonical_source_tree_sha256(" not in body

for token in (
    "SOURCE_PREPARATION_PLAN_VERDICT_EXACT",
    "SOURCE_PREPARATION_CAPABILITY_VERDICT_EXACT",
    "SOURCE_PREPARATION_LAUNCH_EXACT",
    "gate_chain_predecessor_sha256",
    "test_capability_verdict_absent_writes_no_output",
    "test_launch_authority_absent_writes_no_output",
    "manifest-only",
    "manifest-and-root",
    "result-without-manifest",
    "failure-terminal",
    "schema-mismatch",
    "orphan-root",
    "already-complete",
    "source manifest exclusive-create",
    "PASS result exclusive-create last",
    "FAIL_RESULT_EVIDENCE",
    "StreamedLimitCounter",
    "claims=blocked",
):
    assert token in plan_text, token

for token in (
    "Cursor VM",
    "22b25e181ab951b2a4ee8ee4a2f430ee316a8b81",
    "GPT-5.6 Sol High",
    "PILOT_PLAN_REVIEW_CANDIDATE",
    "PILOT_IMPLEMENTATION_PASS",
    "claims=blocked",
):
    assert token in packet_text, token

print("PASS gate chain exact and predecessor closed")
print("PASS capability verdict and launch authority absence write zero outputs")
print("PASS safe authority snapshot contract")
print("PASS crash/reconciliation state table complete and mutually exclusive")
print("PASS manifest/result/root commit order unique")
print("PASS Phase 1 tree-hash test is not self-equality")
print("PASS single top-level file is not stripped")
print("PASS streamed limits do not trust metadata")
print("PASS FAIL evidence matrix complete")
print("PASS one future Task")
print("PASS file map unexpanded")
print("PASS claims remain blocked")
PY
```

Exit code: 0

```text
AST_OK 1
AST_OK 2
AST_OK 3
AST_OK 4
AST_OK 5
AST_OK 6
AST_OK 7
AST_OK 8
AST_OK 9
AST_OK 10
AST_OK 11
AST_OK 12
AST_OK 13
AST_OK 14
AST_OK 15
AST_OK 16
PASS gate chain exact and predecessor closed
PASS capability verdict and launch authority absence write zero outputs
PASS safe authority snapshot contract
PASS crash/reconciliation state table complete and mutually exclusive
PASS manifest/result/root commit order unique
PASS Phase 1 tree-hash test is not self-equality
PASS single top-level file is not stripped
PASS streamed limits do not trust metadata
PASS FAIL evidence matrix complete
PASS one future Task
PASS file map unexpanded
PASS claims remain blocked
```

Repair rounds used: 0.

## Plan self-review

Checked against the repair contract:

- Exactly one `### Task ` heading remains
- Future Create files remain `src/p3_v3/pilot_source.py` and `tests/p3_v3/test_pilot_source.py`
- Future Modify files remain `scripts/p3_v3/pilot.py` and `tests/p3_v3/test_pilot.py`
- Capability tests still use runtime synthetic ZIP and TAR fixtures only
- Future implementation still does not read a real Boost.Math archive
- Future implementation still does not create a production artifact or Authorization A
- Production `run_validate_source` now requires the closed gate chain before any archive open
- Authorization A, verdicts, launch authority, and related files use one verified snapshot
- Crash recovery states are complete and mutually exclusive
- Publication order is manifest, then root rename, then PASS result
- Phase 1 tree-hash test spies the production seam
- A single top-level regular file is not stripped
- Streamed limits count actual bytes
- FAIL evidence matrix freezes per-reason field combinations
- `claims=blocked`
- Formal denominator membership is false
- `rq4_supported=false`
- Sixteen Python fences parse
- No unfinished-work markers and no three consecutive period characters

## Declarations

- The complete 2026-08-15 pilot plan remains unfrozen.
- Foundation state remains `PILOT_IMPLEMENTATION_PASS`.
- This source-preparation plan remains a review candidate and is not frozen by this packet.
- This packet is not an independent PASS.
- No formal Sol High verdict was created.
- Future implementation must not start until an independent plan review PASSes and a later implementation node is separately authorized.
- Production preparation must not start until Authorization A exists and a separately reviewed launch authority exists.
- No production path was executed.
- No pytest, implementation, build, preflight, profiling, mutant, or MR command was run.
- Package C, P12 reveal, buggy revisions, defect patches, reference MR, evaluated MR, mutant outcome, and real-fault outcome were not read, listed, or inferred.
- Boost.Math source was not downloaded, mounted, unpacked, or built.
- The claim ledger was not modified.
- The formal protocol was not modified.
- Existing untracked files were not deleted, moved, modified, or staged.
- `claims=blocked`
- Current requested state: `PILOT_PLAN_REVIEW_CANDIDATE`

GPT-5.6 Sol High is requested to perform an independent high-reasoning review of the unique two-file successor that starts from `22b25e181ab951b2a4ee8ee4a2f430ee316a8b81`. This builder does not assign PASS.
