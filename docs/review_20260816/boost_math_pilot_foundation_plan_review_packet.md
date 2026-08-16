# Boost.Math PILOT_FOUNDATION_ONLY Plan Review Packet — P1SD1

- Packet title: P1SD1 Boost.Math pilot foundation scope downgrade
- Round: P1SD1_BOOST_MATH_PILOT_FOUNDATION_ONLY_PLAN
- Builder identity: Cursor VM
- Amendment type: controller-required scope downgrade after independent P1A2 `SCOPE_DOWNGRADE`
- Starting commit: `4746283ca2d89da435596ea60ef0e707c2abee79`
- Ending commit: the unique successor commit on `origin/main` that adds only the two files listed below
- Foundation plan path: `docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md`
- Packet path: `docs/review_20260816/boost_math_pilot_foundation_plan_review_packet.md`
- Foundation plan SHA-256: `26994305219c42a39b9683ff31b0bc4ed490118ea691bf3932201414dce2418a`
- Foundation plan bytes: 25711
- Foundation plan LF count: 541
- Packet SHA-256, bytes, and LF: the SHA-256, byte length, and LF count of this file after the authorized two-file commit; this packet does not self-hash
- Requested reviewer: GPT-5.6 Sol High
- Reasoning setting: high
- Requested state: `PILOT_PLAN_REVIEW_CANDIDATE`
- This packet is not an independent PASS.
- This packet does not record an independent review PASS and does not speak for the reviewer.
- Task 1 was not started.
- `claims=blocked`

Independent P1A2 review confirmed surface-contract hygiene on the complete 2026-08-15 plan and then returned `SCOPE_DOWNGRADE`. Certification exact-schema binding and orphan closure now need a new evidence model. This node therefore does not amend or freeze that complete plan. It proposes a separate `PILOT_FOUNDATION_ONLY` candidate that covers only G1 isolation.

## File change list

This round creates only:

1. `docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md`
2. `docs/review_20260816/boost_math_pilot_foundation_plan_review_packet.md`

No existing file was modified. In particular, `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` and `docs/review_20260815/boost_math_pilot_plan_review_packet.md` were not edited, not executed, and not frozen. The complete 2026-08-15 pilot plan remains an unfrozen candidate.

No source, test, protocol, ledger, claim, data, or Boost.Math source file was created or modified.

## Authority input hashes

Unchanged from `4746283ca2d89da435596ea60ef0e707c2abee79`.

| Path | SHA-256 |
|---|---|
| `docs/review_20260815/phase1_sol_high_final_review.md` | `95345c4229e8e3dedd21e3f7da022fc5daeceb1018392dc1d0e3e35b00fa5a7d` |
| `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md` | `bd9234e3a26557e0036e42415528f983f2c18313295352ddffb4ccc076c1d5e4` |
| `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md` | `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830` |
| `data/p3_v3/protocol/protocol.json` | `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| `data/p3_v3/protocol/environment_lock.json` | `7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f` |
| `data/p3_v3/protocol/claim_ceiling_authority.json` | `1f46b7cd97e6ddf6d65f6c52a552f4e4b6680a987a088d4f5a65ebc19bf017ed` |
| `research/evidence/p3_claim_ledger_v1.3.0.yml` | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| `data/p3_v3/phase1_frames/receipts.json` | `8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440` |
| `data/p3_v3/phase1_frames/pass1_baseline_manifest.json` | `b0be90ded75a4242bf883698d2b8c3f0c55d70b1b0928d7068bc1a3797e4eb11` |

Boost.Math Phase 1 frames, suffix `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`, unchanged from P1A2 packet L69-78:

| File | SHA-256 |
|---|---|
| `adapter-discovery` | `87fb9d05278c5c2e713c8a9d7f398cb1a1c84562df27b590e6d37f98fd7c1dd1` |
| `derived-subject` | `654a5c8a26b85013a44665dd92c59a66afee9f639ec7d28535d58357ec696f20` |
| `evaluation-inputs-common` | `92d35c3cf98a1287703f8d00dd2343cfa792b2a0e035bce63d9850324f95b239` |
| `profiling-results` | `5a1de4c1a9e52efcc100a448e018229abc984bc350a805c530133f7e689cc133` |
| `profiling-workload` | `e6cd3b5054bdac30dea8e6fbc613c29758be6a97ead4d6d134d33dfdfc8c8380` |
| `public-behavior-frame` | `a740d5019a19ee354f07e73e7c542dd1d79fb8969a2af48d5ef7975e534da4d3` |
| `source-scale` | `dc9b56fe81bcf8301e6164f15007c6f57ee11e79cfff1b84e66906cb7de228d0` |
| `technique-profile` | `da09281afcfb30d41f6f52823afbca9a994a543ae1ef8b82198b5aea58a5c91f` |

## RED

Command, run before either target file existed:

```text
python3 - <<'PY'
from pathlib import Path

plan = Path("docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md")
packet = Path("docs/review_20260816/boost_math_pilot_foundation_plan_review_packet.md")

assert plan.is_file()
assert packet.is_file()
PY
```

Exit code: 1

```text
Traceback (most recent call last):
  File "<stdin>", line 6, in <module>
AssertionError
```

Failure location: `docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md` did not exist.

## GREEN

Command, run after the foundation plan was written:

```text
python3 - <<'PY'
from pathlib import Path

plan = Path("docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md")
text = plan.read_text(encoding="utf-8")

required = [
    "PILOT_FOUNDATION_ONLY",
    "PILOT_PLAN_REVIEW_CANDIDATE",
    "p3-pilot-plan-v1",
    'schema.startswith("p3-pilot-")',
    "execution_class",
    "PILOT_ONLY",
    "denominator",
    "artifact_sha256",
    "markdown_plan_sha256",
    "sol_high_plan_verdict_sha256",
    "formal_denominator_membership",
    "rq4_supported",
    "claims=blocked",
    "PILOT_IMPLEMENTATION_REVIEW_CANDIDATE",
    "python3 -m pytest tests/p3_v3 -q",
]
for token in required:
    assert token in text, token

for token in ("TODO", "TBD", "..."):
    assert token not in text, token

assert text.count("### Task ") == 1
assert "def certify_mutant" not in text
assert "def build_execution_plan" not in text
assert "reconcile_orphaned_intent" not in text
assert "cmake -S" not in text
assert "git clone" not in text
assert "PILOT_PLAN_FROZEN" not in text

print("PASS foundation-only scope")
print("PASS exact pilot isolation contract")
print("PASS one implementation task")
print("PASS no source/build/certification/execution procedures")
print("PASS claims remain blocked")
PY
```

First GREEN attempt exit code: 1

```text
Traceback (most recent call last):
  File "<stdin>", line 27, in <module>
AssertionError: ...
```

Cause: one `write_canonical_json(..., exclusive=True)` placeholder in Step 3. One mechanical correction replaced it with `write_canonical_json(output_path, value, exclusive=True)`.

Second GREEN attempt exit code: 0

```text
PASS foundation-only scope
PASS exact pilot isolation contract
PASS one implementation task
PASS no source/build/certification/execution procedures
PASS claims remain blocked
```

Repair rounds used: 1.

## Foundation contract captured by the new plan

- `execution_class = PILOT_ONLY`
- `denominator = PILOT_ONLY`
- every `schema.startswith("p3-pilot-")` object is rejected by confirmatory package, run-record, and evidence seams
- unknown future `p3-pilot-*` schemas are rejected the same way
- `p3-pilot-plan-v1` uses exact keys, exact types, and `artifact_sha256` self-hash
- machine plan binds foundation Markdown SHA-256, a future archived Sol High plan verdict SHA-256, `claims=blocked`, `formal_denominator_membership=false`, and `rq4_supported=false`
- plan artifact cannot be accepted as a source manifest, freeze, execution plan, or result
- exactly one implementation task
- Task 1 PASS does not authorize source preparation or production execution
- later implementation must stop at `PILOT_IMPLEMENTATION_REVIEW_CANDIDATE`

Approved later Create paths:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`
- `tests/p3_v3/test_pilot_leakage.py`
- `tests/p3_v3/fixtures/pilot/valid_plan_min.json`
- `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json`
- `data/p3_v3/pilot/boost_math/pilot-plan.json`

Approved later Modify paths:

- `src/p3_v3/packages.py`
- `src/p3_v3/run_records.py`
- `scripts/p3_v3/evidence.py`
- `tests/p3_v3/test_packages.py`
- `tests/p3_v3/test_run_records.py`
- `tests/p3_v3/test_cli.py`

No other later file is approved by this foundation plan.

## Declarations

- The complete 2026-08-15 pilot plan remains unfrozen.
- This packet is not an independent PASS.
- No production path was executed.
- No Phase 2 formal execution authorization is granted by this packet.
- No pytest, build, preflight, profiling, mutant, or MR command was run.
- Task 1 was not started.
- Package C, P12 reveal, buggy revisions, defect patches, reference MR, evaluated MR, mutant outcome, and real-fault outcome were not read, listed, or inferred.
- Boost.Math source was not downloaded and was not cloned.
- The claim ledger was not modified.
- The formal protocol was not modified.
- Existing untracked files were not deleted, moved, modified, or staged.
- `claims=blocked`
- Current requested state: `PILOT_PLAN_REVIEW_CANDIDATE`

GPT-5.6 Sol High is requested to perform an independent high-reasoning review of the two new files on the successor of `4746283ca2d89da435596ea60ef0e707c2abee79`. This builder does not assign PASS.
