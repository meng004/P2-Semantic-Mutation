# Boost.Math PILOT_FOUNDATION_ONLY Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This document authorizes only the single foundation task below. After that task, stop for independent review. Do not start source preparation or production execution.

**Goal:** Isolate Boost.Math `PILOT_ONLY` work behind a fail-closed `p3-pilot-*` discriminator, one exact `p3-pilot-plan-v1` machine artifact, and confirmatory leakage guards. This plan covers foundation isolation only.

**Architecture:** Keep every confirmatory `p3-v3-*` schema unchanged. Add one new exact artifact family whose every `schema_version` starts with `p3-pilot-`. Teach confirmatory package, run-record, and evidence seams to reject that prefix and the `PILOT_ONLY` class before any confirmatory object is accepted. Bind the machine plan to this Markdown file, a future archived independent Sol High plan verdict, and a blocked claim ceiling. After the single implementation task, stop at `PILOT_IMPLEMENTATION_REVIEW_CANDIDATE`.

**Tech Stack:** Python 3.11 or newer, existing `src/p3_v3/artifacts.py` exact-object helpers, existing confirmatory package, run-record, and evidence modules, pytest with `PYTHONPATH=src`.

## Global Constraints

- Plan class is `PILOT_FOUNDATION_ONLY`.
- After this document is written, the requested review state is `PILOT_PLAN_REVIEW_CANDIDATE`. This document is not an independent PASS.
- After the single implementation task, the required stop state is `PILOT_IMPLEMENTATION_REVIEW_CANDIDATE`.
- `execution_class = PILOT_ONLY` and `denominator = PILOT_ONLY` on every durable pilot object.
- Every object whose `schema.startswith("p3-pilot-")` is a pilot object, including unknown future values such as `p3-pilot-future-v9`.
- Confirmatory package, run-record, and evidence seams reject those objects fail-closed.
- `p3-pilot-plan-v1` uses exact keys, exact types, and `artifact_sha256` self-hash.
- Machine plan binds `markdown_plan_sha256`, `sol_high_plan_verdict_sha256`, `claims=blocked`, `formal_denominator_membership=false`, and `rq4_supported=false`.
- The plan artifact must not be accepted as a source manifest, freeze, execution plan, or result.
- Task 1 PASS does not authorize source preparation or production execution.
- `claims` remain `blocked` for C1 through C8 and RQ1 through RQ4.
- This node does not modify `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md`. That complete plan remains an unfrozen candidate and is not executed here.
- This node and the later foundation task do not prepare source, download Boost.Math, unpack archives, configure or build the subject, construct mutants, certify mutants, evaluate metamorphic relations, write an execution plan, reconcile orphans, or close evidence.
- Reuse without changing scientific meaning: `EvidenceError`, `canonical_sha256`, `validate_exact_object(value, schema, context)`, `validate_sha256`, `write_canonical_json`, and `read_canonical_json`.
- `validate_exact_object` takes exactly three positional arguments: `value`, `schema`, and `context`. Two-argument calls are forbidden.
- `p3_v3.packages.ALLOWED_CLASSES` remains the confirmatory class set and must stay free of `PILOT_ONLY`.
- `p3_v3.run_records` confirmatory execution classes remain `SYNTHETIC_INFRASTRUCTURE`, `NON_SCIENTIFIC_CONTROL`, and `REAL_SCIENTIFIC`.
- Cursor VM has no `rtk`. Later implementation uses bare `python3`, `pytest`, and `git`.
- This planning node does not run pytest, does not run a production command, and does not start Task 1.

---

## Scope Downgrade Context

Independent P1A2 review returned `SCOPE_DOWNGRADE` on the complete plan `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md`. Surface contracts in that document are not enough to freeze a full source-to-closure path, because certification binding and orphan closure now need a new evidence model. Those problems stay out of scope.

This foundation plan covers only G1 isolation:

- `p3-pilot-*` discriminator;
- `PILOT_ONLY` execution class and denominator;
- exact `p3-pilot-plan-v1` artifact;
- confirmatory package, run-record, and evidence fail-closed leakage guards;
- the listed unit tests and the full `tests/p3_v3` regression command written for a later implementation session.

This plan has exactly one implementation task.

Starting commit for this planning node: `4746283ca2d89da435596ea60ef0e707c2abee79`.

---

## Frozen Authority Identities

These files are identity-checked only. This plan does not modify them.

| File | SHA-256 |
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

Boost.Math Phase 1 frames remain the P1A2 packet L69-78 identities. They identify the intended later subject. This foundation plan does not download, unpack, or compile that subject.

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

Identity labels copied into the machine plan, and only as labels:

- `p12_item_id`: `C-BOOSTMATH-001`
- `neutral_snapshot_id`: `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`
- `normalized_source_tree_sha256`: `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- `controlled_subject_id`: `89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914`
- `controlled_subject_source_id`: `e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7`

Presence of those labels does not prove that source was mounted and does not open a source gate.

---

## Approved Future File Map

The later implementation task may create only:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`
- `tests/p3_v3/test_pilot_leakage.py`
- `tests/p3_v3/fixtures/pilot/valid_plan_min.json`
- `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json`
- `data/p3_v3/pilot/boost_math/pilot-plan.json`

The later implementation task may modify only:

- `src/p3_v3/packages.py`
- `src/p3_v3/run_records.py`
- `scripts/p3_v3/evidence.py`
- `tests/p3_v3/test_packages.py`
- `tests/p3_v3/test_run_records.py`
- `tests/p3_v3/test_cli.py`

No other file is approved. In particular, do not create `tests/p3_v3/test_pilot_extract.py`, `tests/p3_v3/fixtures/pilot/valid_source_manifest_min.json`, or `data/p3_v3/pilot/boost_math/source-manifest.json`.

---

## Discriminator and Leakage Guards

Named schema implemented by this foundation: `p3-pilot-plan-v1`.

Any other `schema_version` that starts with `p3-pilot-` is still a pilot object. Confirmatory seams must reject it even when the concrete name is unknown to `src/p3_v3/pilot.py`.

```python
from collections.abc import Mapping
from typing import Any

from p3_v3.artifacts import EvidenceError

PILOT_EXECUTION_CLASS = "PILOT_ONLY"
PILOT_DENOMINATOR = "PILOT_ONLY"
PILOT_SCHEMA_PREFIX = "p3-pilot-"


def is_pilot_artifact(value: Mapping[str, Any]) -> bool:
    schema = value.get("schema_version")
    execution = value.get("execution_class")
    denominator = value.get("denominator")
    return (
        isinstance(schema, str)
        and schema.startswith("p3-pilot-")
    ) or execution == PILOT_EXECUTION_CLASS or denominator == PILOT_DENOMINATOR


def reject_confirmatory_pilot(value: Mapping[str, Any], context: str) -> None:
    if is_pilot_artifact(value):
        raise EvidenceError(
            "E_PILOT_DENOMINATOR_LEAK",
            f"{context} rejected PILOT_ONLY or p3-pilot schema",
        )
```

A confirmatory seam must call `is_pilot_artifact` before filename checks and before ordinary schema-version mismatch errors. An unknown `schema_version` such as `p3-pilot-future-v9` must be rejected.

`src/p3_v3/packages.py`:

- `ALLOWED_CLASSES` must not gain `PILOT_ONLY`.
- `build_package` must reject a file spec whose `class` equals `PILOT_ONLY` with `E_PILOT_PACKAGE_CLASS` before the generic `E_PACKAGE_CONTENT_CLASS` path.
- `_validate_manifest` must call `reject_confirmatory_pilot(value, "package.manifest")` before hash or version checks, so a forged `schema_version` of `p3-pilot-future-v9` raises `E_PILOT_DENOMINATOR_LEAK`.

`src/p3_v3/run_records.py`:

- `_EXECUTION_CLASSES` must stay `{SYNTHETIC_INFRASTRUCTURE, NON_SCIENTIFIC_CONTROL, REAL_SCIENTIFIC}`.
- `_validate_locked_jobs` must treat `execution_class=PILOT_ONLY` as `E_PILOT_DENOMINATOR_LEAK` before the generic `E_AUTHORITY_EXECUTION_CLASS` path.
- `validate_claim_ledger` must reject any evidence reference whose path starts with `data/p3_v3/pilot/` using `E_PILOT_DENOMINATOR_LEAK`.

`scripts/p3_v3/evidence.py`:

- Import `reject_confirmatory_pilot`.
- `verify-package`, `verify-run-records`, and `verify-evidence` must reject an object whose `schema.startswith("p3-pilot-")` or whose `execution_class` or `denominator` equals `PILOT_ONLY`.
- Add `reject_confirmatory_artifact(value, context)` as a thin wrapper that calls `reject_confirmatory_pilot`. Tests may call that wrapper directly.

---

## Schema `p3-pilot-plan-v1`

Machine plan path: `data/p3_v3/pilot/boost_math/pilot-plan.json`.

Exact keys and exact types. No extra key is legal. `validate_exact_object` must be called as `validate_exact_object(value, PILOT_PLAN_EXACT, "p3-pilot-plan-v1")`.

```python
PILOT_PLAN_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "plan_class": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "markdown_plan_sha256": str,
    "sol_high_plan_verdict_sha256": str,
    "claims": str,
    "formal_denominator_membership": bool,
    "rq4_supported": bool,
    "artifact_sha256": str,
}
```

Literal constraints after the exact-object check:

| Field | Required value |
|---|---|
| `schema_version` | `p3-pilot-plan-v1` |
| `execution_class` | `PILOT_ONLY` |
| `denominator` | `PILOT_ONLY` |
| `plan_class` | `PILOT_FOUNDATION_ONLY` |
| `p12_item_id` | `C-BOOSTMATH-001` |
| `neutral_snapshot_id` | `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886` |
| `normalized_source_tree_sha256` | `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8` |
| `controlled_subject_id` | `89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914` |
| `controlled_subject_source_id` | `e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7` |
| `claims` | `blocked` |
| `formal_denominator_membership` | `false` |
| `rq4_supported` | `false` |

`predecessor_sha256` is a sorted unique list of lowercase SHA-256 strings. `markdown_plan_sha256` and `sol_high_plan_verdict_sha256` must pass `validate_sha256`. `artifact_sha256` is `canonical_sha256` of the object with that field removed.

The producer `write_pilot_plan(markdown_path, verdict_path, output_path)` may run only when the verdict file already exists. It binds:

- `markdown_plan_sha256` = SHA-256 of `docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md` for the production output, or of the caller-supplied markdown path in tests;
- `sol_high_plan_verdict_sha256` = SHA-256 of the archived independent Sol High plan verdict file.

A missing verdict file is `E_PILOT_PLAN_VERDICT_ABSENT`. The producer must not invent a placeholder hash.

This schema is not a source-identity document, not a freeze, not an execution plan, and not a result. Extra keys such as `archive_sha256`, `freeze_id`, `execution_plan_id`, `job_id`, or `terminal_status` are `E_SCHEMA_KEYS`.

Foundation CLI `scripts/p3_v3/pilot.py` may expose only:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py write-plan \
  --markdown docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md \
  --verdict <archived-sol-high-plan-verdict> \
  --output data/p3_v3/pilot/boost_math/pilot-plan.json

env PYTHONPATH=src python3 scripts/p3_v3/pilot.py validate-plan \
  --plan data/p3_v3/pilot/boost_math/pilot-plan.json
```

Forbidden CLI verbs include `validate-source`, `extract`, `freeze`, `execute`, and `certify`. Forbidden module names include `write_source_manifest`, `validate_pilot_source_manifest`, `prepare_source`, `enter_source_gate`, `enter_execution_gate`, and `write_execution_plan`.

---

### Task 1: Pilot Foundation Isolation and Leakage Guards

**Files:**
- Create: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`, `tests/p3_v3/test_pilot_leakage.py`, `tests/p3_v3/fixtures/pilot/valid_plan_min.json`, `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json`, `data/p3_v3/pilot/boost_math/pilot-plan.json`
- Modify: `src/p3_v3/packages.py`, `src/p3_v3/run_records.py`, `scripts/p3_v3/evidence.py`, `tests/p3_v3/test_packages.py`, `tests/p3_v3/test_run_records.py`, `tests/p3_v3/test_cli.py`

**Interfaces:**
- Consumes: `validate_exact_object(value, schema, context)`, `canonical_sha256`, `validate_sha256`, `write_canonical_json`, `read_canonical_json`, `EvidenceError`, existing confirmatory package, run-record, and evidence entry points
- Produces: `is_pilot_artifact`, `reject_confirmatory_pilot`, `validate_pilot_plan`, `write_pilot_plan`, confirmatory rejection at package, run-record, and evidence seams, and one `p3-pilot-plan-v1` file
- Does not produce: source manifest, freeze, execution plan, result, or claim-ledger write

User authorization required: no. Gate: `G1_IMPLEMENTATION` only after an archived independent Sol High plan-review verdict exists. This planning node does not start the gate.

- [ ] **Step 1: Write the failing tests**

Create `tests/p3_v3/test_pilot.py` with at least:

```python
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, write_canonical_json


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_pilot_plan_requires_exact_keys(tmp_path):
    from p3_v3.pilot import validate_pilot_plan

    value = {
        "schema_version": "p3-pilot-plan-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
    }
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_pilot_plan(value)


def test_pilot_plan_requires_self_hash(tmp_path):
    from p3_v3.pilot import write_pilot_plan, validate_pilot_plan

    markdown = tmp_path / "plan.md"
    verdict = tmp_path / "verdict.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict.write_text("archived verdict\n", encoding="utf-8")
    written = write_pilot_plan(markdown, verdict, output)
    broken = dict(written)
    broken["artifact_sha256"] = "0" * 64
    with pytest.raises(EvidenceError, match="E_PILOT_PLAN_HASH"):
        validate_pilot_plan(broken)


def test_pilot_plan_binds_markdown_and_verdict(tmp_path):
    from p3_v3.pilot import write_pilot_plan, validate_pilot_plan

    markdown = tmp_path / "plan.md"
    verdict = tmp_path / "verdict.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict.write_text("archived verdict\n", encoding="utf-8")
    written = write_pilot_plan(markdown, verdict, output)
    validated = validate_pilot_plan(written)
    assert validated["markdown_plan_sha256"] == _sha256_bytes(
        markdown.read_bytes()
    )
    assert validated["sol_high_plan_verdict_sha256"] == _sha256_bytes(
        verdict.read_bytes()
    )
    assert validated["claims"] == "blocked"
    assert validated["formal_denominator_membership"] is False
    assert validated["rq4_supported"] is False
    assert validated["execution_class"] == "PILOT_ONLY"
    assert validated["denominator"] == "PILOT_ONLY"


def test_pilot_plan_rejected_as_source_manifest():
    from p3_v3.pilot import validate_pilot_plan

    forged = {
        "schema_version": "p3-pilot-source-manifest-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "archive_sha256": "0" * 64,
        "archive_bytes": 1,
    }
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_pilot_plan(forged)


def test_foundation_cannot_create_source_manifest():
    import p3_v3.pilot as pilot

    assert not hasattr(pilot, "write_source_manifest")
    assert not hasattr(pilot, "validate_pilot_source_manifest")


def test_foundation_cannot_enter_source_or_execution_gate():
    import p3_v3.pilot as pilot

    forbidden = (
        "prepare_source",
        "enter_source_gate",
        "enter_execution_gate",
        "write_execution_plan",
        "write_freeze",
        "write_result",
    )
    for name in forbidden:
        assert not hasattr(pilot, name)
```

Create `tests/p3_v3/test_pilot_leakage.py` with at least:

```python
from __future__ import annotations

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.packages import build_package, verify_package
from p3_v3.run_records import validate_claim_ledger
import p3_v3.run_records as run_records_module
import scripts.p3_v3.evidence as evidence_module


def test_unknown_pilot_schema_rejected_from_confirmatory_package(tmp_path):
    manifest = {
        "schema_version": "p3-pilot-future-v9",
        "role": "CONSTRUCTION_A",
        "parents": [],
        "files": [],
        "package_tree_sha256": canonical_sha256([]),
        "artifact_sha256": "0" * 64,
    }
    with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
        verify_package(tmp_path, manifest)


def test_pilot_execution_class_rejected_from_confirmatory_run_records(tmp_path):
    from tests.p3_v3.test_run_records import _locked_job

    locked = [_locked_job(execution_class="PILOT_ONLY")]
    with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
        run_records_module.verify_locked_execution(
            locked, tmp_path / "jobs", tmp_path / "ledger.jsonl"
        )


def test_pilot_denominator_rejected_from_confirmatory_evidence():
    value = {
        "schema_version": "p3-package-manifest-v1",
        "execution_class": "SYNTHETIC_INFRASTRUCTURE",
        "denominator": "PILOT_ONLY",
    }
    with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
        evidence_module.reject_confirmatory_artifact(value, "verify-evidence")
```

Add the same three leakage assertions to `tests/p3_v3/test_packages.py`, `tests/p3_v3/test_run_records.py`, and `tests/p3_v3/test_cli.py` respectively so those existing modules also fail closed:

- `test_packages.py`: `build_package` with `class=PILOT_ONLY` raises `E_PILOT_PACKAGE_CLASS`; `ALLOWED_CLASSES` values do not contain `PILOT_ONLY`.
- `test_run_records.py`: `validate_claim_ledger` rejects a reference starting with `data/p3_v3/pilot/`.
- `test_cli.py`: `evidence_module.dispatch` for `verify-package` rejects a `p3-pilot-future-v9` manifest; `scripts/p3_v3/pilot.py` parser has no `validate-source`, `extract`, `freeze`, `execute`, or `certify` command.

Create fixture `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json` as a complete object whose `schema_version` is `p3-pilot-future-v9` and whose `execution_class` and `denominator` are `PILOT_ONLY`. Create `tests/p3_v3/fixtures/pilot/valid_plan_min.json` only by calling `write_pilot_plan` on a committed markdown and verdict pair, then copying the produced object. Do not hand-edit `artifact_sha256`.

- [ ] **Step 2: Run RED**

Run:

```text
env PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_pilot.py \
  tests/p3_v3/test_pilot_leakage.py \
  tests/p3_v3/test_packages.py \
  tests/p3_v3/test_run_records.py \
  tests/p3_v3/test_cli.py -q
```

Expected: exit 1 because `p3_v3.pilot` is absent and the new leakage assertions fail.

- [ ] **Step 3: Write the minimal implementation**

`src/p3_v3/pilot.py` must define the discriminator, `PILOT_PLAN_EXACT`, `validate_pilot_plan`, and `write_pilot_plan` exactly as specified above. `write_pilot_plan` writes only `p3-pilot-plan-v1` through `write_canonical_json(output_path, value, exclusive=True)` and then re-reads the file with `validate_pilot_plan`.

`scripts/p3_v3/pilot.py` must parse only `write-plan` and `validate-plan`.

In `src/p3_v3/packages.py`, insert the `PILOT_ONLY` class rejection and the `_validate_manifest` discriminator call shown below.

```python
from p3_v3.pilot import reject_confirmatory_pilot


def _reject_pilot_package_class(class_name: str, context: str) -> None:
    if class_name == "PILOT_ONLY":
        raise EvidenceError("E_PILOT_PACKAGE_CLASS", f"{context} rejected PILOT_ONLY")
```

Call `_reject_pilot_package_class(spec["class"], f"file_specs[{index}]")` inside `build_package` before the `effective_classes` membership test. Call `reject_confirmatory_pilot(value, "package.manifest")` as the first statement after `value = validate_exact_object(dict(manifest), _MANIFEST_SCHEMA, "manifest")` in `_validate_manifest`.

In `src/p3_v3/run_records.py`:

```python
from p3_v3.pilot import reject_confirmatory_pilot

if job["execution_class"] == "PILOT_ONLY":
    raise EvidenceError(
        "E_PILOT_DENOMINATOR_LEAK",
        f"locked_jobs[{index}] rejected PILOT_ONLY execution_class",
    )
```

Place that check immediately after the successful `validate_exact_object` call in `_validate_locked_jobs`, before the generic `_EXECUTION_CLASSES` test. In `validate_claim_ledger`, after `safe_relative_path(reference)`:

```python
if reference.startswith("data/p3_v3/pilot/"):
    raise EvidenceError(
        "E_PILOT_DENOMINATOR_LEAK",
        "claim ledger cannot cite pilot evidence",
    )
```

In `scripts/p3_v3/evidence.py`:

```python
from p3_v3.pilot import reject_confirmatory_pilot


def reject_confirmatory_artifact(value, context: str) -> None:
    reject_confirmatory_pilot(value, context)
```

Call `reject_confirmatory_artifact` on every JSON object read by `verify-package`, `verify-run-records`, and `verify-evidence` before ordinary confirmatory validation.

Production `write-plan` output path is `data/p3_v3/pilot/boost_math/pilot-plan.json`. That write is allowed only after the archived Sol High verdict file exists. This planning node does not perform that write.

- [ ] **Step 4: Run minimum GREEN**

Run:

```text
env PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_pilot.py \
  tests/p3_v3/test_pilot_leakage.py \
  tests/p3_v3/test_packages.py \
  tests/p3_v3/test_run_records.py \
  tests/p3_v3/test_cli.py -q
```

Expected: exit 0.

- [ ] **Step 5: Run the complete confirmatory suite**

Run:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Expected: exit 0. Existing confirmatory tests must keep passing. `ALLOWED_CLASSES` must still omit `PILOT_ONLY`.

- [ ] **Step 6: Stop for independent implementation review**

Stage only the approved Create and Modify paths. Do not enter a source gate. Do not enter an execution gate. Requested state after this task is `PILOT_IMPLEMENTATION_REVIEW_CANDIDATE`. Task 1 PASS does not authorize source preparation or production execution.

---

## Commands This Planning Node Must Not Run

The pytest commands above are future implementation commands. This planning node must not run them. This planning node must not run a build, preflight, profiling, mutant, or production command.

---

## Stop Conditions

Stop immediately if implementation would require:

- modifying a file outside the approved map;
- designing source, build, certification, execution, orphan, or evidence-closure procedures;
- changing an authority or Frame file;
- writing a claim-ledger update;
- treating a Task 1 PASS as production authorization.

---

## Claim Ceiling

`claims=blocked`. Formal denominator membership is false. RQ4 is not supported. The claim ledger must remain byte-identical to `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`.
