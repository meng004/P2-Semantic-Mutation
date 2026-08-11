from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

import p3_v3.bridge_and_frames as frames_module
import scripts.p3_v3.evidence as evidence_module
from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import (
    build_public_behavior_frame,
    derive_subject_material,
    run_adapter_discovery,
    select_profiling_workload,
    validate_adapter_registry,
    validate_common_inputs_on_fixed_source,
    validate_input_generator_registry,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
ADAPTER_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "adapters"
COMMANDS = {
    "validate-protocol",
    "verify-bridge",
    "build-frames",
    "verify-mr-inventory",
    "build-package",
    "verify-package",
    "run-preflight",
    "verify-run-records",
    "close-phase",
    "verify-evidence",
}
SCIENTIFIC_PLAN_SHA256 = (
    "fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830"
)
EVIDENCE_DESIGN_SHA256 = (
    "7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9"
)
TECHNIQUE_ORDER = [
    "HYBRID_NATIVE",
    "TENSOR_AUTODIFF",
    "PROBABILISTIC_SURROGATE",
    "ITERATIVE_STOCHASTIC",
    "ARRAY_NUMERICAL",
    "SCALAR_CONTROL",
    "TECH_UNCERTAIN",
]
P12_OUTCOME_STATES = [
    "MR_VIOLATION",
    "MR_SATISFIED",
    "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
    "SCIENTIFIC_INCONCLUSIVE",
    "INFRASTRUCTURE_UNRESOLVED",
]
BEHAVIOR_CATEGORY_ORDER = [
    "PUBLIC_API",
    "CLI",
    "EXAMPLE",
    "BENCHMARK",
    "PROJECT_TEST",
]
_ADAPTER_SPECS = (
    ("PYTHON_PEP517_V1", "python", "adapters/python_pep517_v1.py"),
    ("CMAKE_CTEST_V1", "cmake", "adapters/cmake_ctest_v1.py"),
    ("MESON_TEST_V1", "meson", "adapters/meson_test_v1.py"),
    ("AUTOTOOLS_MAKECHECK_V1", "autotools", "adapters/autotools_makecheck_v1.py"),
)
SECRET_ORIGIN = (
    "https://audit-user:TOP_SECRET_TOKEN@github.com/" "meng004/P3-Semantic-Mutation.git"
)
SECRET_IDENTITY = "github.com/meng004/P3-Semantic-Mutation"
SECRET_ORIGIN_SHA256 = (
    "8b90a20c89d81eff7287a414ad53840b1d030a1e1d42a409a69396efbe2ec3d2"
)


def _env():
    return {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _digest(label: str) -> str:
    return canonical_sha256({"fixture": label})


AUTHORITY_LOCK_KEYS = {
    "schema_version",
    "task_id",
    "controller_repository",
    "subjects",
    "governing_materials",
    "protocol",
    "registries",
    "preflight",
    "jobs",
    "claim_policy",
}
_CONTROLLER_AUTHORITY_KEYS = {
    "normalized_repository_identity",
    "base_commit",
    "base_tree",
    "tracked_source_manifest_sha256",
}
_SUBJECT_AUTHORITY_KEYS = {
    "subject_id",
    "repository_role",
    "normalized_repository_identity",
    "base_commit",
    "base_tree",
    "tracked_source_manifest_sha256",
    "build_descriptor_sha256",
    "adapter_id",
}
_GOVERNING_AUTHORITY_KEYS = {
    "scientific_plan_sha256",
    "evidence_design_sha256",
    "authority_lock_design_sha256",
    "implementation_plan_sha256",
    "controller_implementation_manifest_sha256",
}
_PROTOCOL_AUTHORITY_KEYS = {
    "protocol_sha256",
    "rq_spec_sha256",
    "claim_ceiling_sha256",
    "p12_contract_sha256",
    "operator_catalogue_sha256",
    "mr_policy_sha256",
    "site_policy_sha256",
    "analysis_spec_sha256",
    "package_policy_sha256",
    "environment_lock_sha256",
    "job_derivation_policy_sha256",
}
_REGISTRY_AUTHORITY_KEYS = {
    "adapter_registry_sha256",
    "input_generator_registry_sha256",
}
_PREFLIGHT_AUTHORITY_KEYS = {
    "normalized_repository_identity",
    "base_commit",
    "base_tree",
    "dependency_lock_sha256",
    "environment_policy_sha256",
    "required_capabilities",
    "forbidden_credential_fields",
}
_JOB_AUTHORITY_KEYS = {
    "job_id",
    "phase",
    "job_role",
    "object_identity",
    "input_identity_sha256",
    "intent_template_sha256",
    "maximum_attempts",
    "retry_trigger",
    "execution_class",
    "p12_access_class",
}
_CLAIM_POLICY_AUTHORITY_KEYS = {"claim_ceiling_sha256", "required_status"}
_AUTHORITY_OBJECT_SCHEMAS = (
    ((), AUTHORITY_LOCK_KEYS),
    (("controller_repository",), _CONTROLLER_AUTHORITY_KEYS),
    (("subjects", 0), _SUBJECT_AUTHORITY_KEYS),
    (("governing_materials",), _GOVERNING_AUTHORITY_KEYS),
    (("protocol",), _PROTOCOL_AUTHORITY_KEYS),
    (("registries",), _REGISTRY_AUTHORITY_KEYS),
    (("preflight",), _PREFLIGHT_AUTHORITY_KEYS),
    (("jobs", 0), _JOB_AUTHORITY_KEYS),
    (("claim_policy",), _CLAIM_POLICY_AUTHORITY_KEYS),
)


def _authority_lock() -> dict:
    protocol = {
        "protocol_sha256": "6" * 64,
        "rq_spec_sha256": "7" * 64,
        "claim_ceiling_sha256": "8" * 64,
        "p12_contract_sha256": "9" * 64,
        "operator_catalogue_sha256": "a" * 64,
        "mr_policy_sha256": "b" * 64,
        "site_policy_sha256": "c" * 64,
        "analysis_spec_sha256": "d" * 64,
        "package_policy_sha256": "e" * 64,
        "environment_lock_sha256": "f" * 64,
        "job_derivation_policy_sha256": "0" * 64,
    }
    return {
        "schema_version": "P3_V3_AUTHORITY_LOCK_V1",
        "task_id": "p3-v3-foundation",
        "controller_repository": {
            "normalized_repository_identity": "github.com/example/controller",
            "base_commit": "1" * 40,
            "base_tree": "2" * 40,
            "tracked_source_manifest_sha256": "1" * 64,
        },
        "subjects": [
            {
                "subject_id": "subject-a",
                "repository_role": "CONTROLLED_A",
                "normalized_repository_identity": "github.com/example/subject-a",
                "base_commit": "3" * 40,
                "base_tree": "4" * 40,
                "tracked_source_manifest_sha256": "2" * 64,
                "build_descriptor_sha256": "4" * 64,
                "adapter_id": "PYTHON_PEP517_V1",
            },
            {
                "subject_id": "subject-b",
                "repository_role": "CONTROLLED_B",
                "normalized_repository_identity": "github.com/example/subject-b",
                "base_commit": "5" * 40,
                "base_tree": "6" * 40,
                "tracked_source_manifest_sha256": "3" * 64,
                "build_descriptor_sha256": "5" * 64,
                "adapter_id": "CMAKE_CTEST_V1",
            },
        ],
        "governing_materials": {
            "scientific_plan_sha256": "1" * 64,
            "evidence_design_sha256": "2" * 64,
            "authority_lock_design_sha256": "3" * 64,
            "implementation_plan_sha256": "4" * 64,
            "controller_implementation_manifest_sha256": "1" * 64,
        },
        "protocol": protocol,
        "registries": {
            "adapter_registry_sha256": "a" * 64,
            "input_generator_registry_sha256": "b" * 64,
        },
        "preflight": {
            "normalized_repository_identity": "github.com/example/controller",
            "base_commit": "1" * 40,
            "base_tree": "2" * 40,
            "dependency_lock_sha256": "c" * 64,
            "environment_policy_sha256": protocol["environment_lock_sha256"],
            "required_capabilities": ["cpu", "disk", "memory"],
            "forbidden_credential_fields": [
                "authorization",
                "credential",
                "password",
                "token",
            ],
        },
        "jobs": [
            {
                "job_id": "1" * 64,
                "phase": "PHASE_0",
                "job_role": "PREFLIGHT_CONTROL",
                "object_identity": "CONTROL:preflight",
                "input_identity_sha256": "2" * 64,
                "intent_template_sha256": "3" * 64,
                "maximum_attempts": 3,
                "retry_trigger": "FAIL_INFRASTRUCTURE",
                "execution_class": "NON_SCIENTIFIC_CONTROL",
                "p12_access_class": "FORBIDDEN",
            },
            {
                "job_id": "2" * 64,
                "phase": "PHASE_1",
                "job_role": "SYNTHETIC_CHECK",
                "object_identity": "SYNTHETIC:case-1",
                "input_identity_sha256": "4" * 64,
                "intent_template_sha256": "5" * 64,
                "maximum_attempts": 3,
                "retry_trigger": "FAIL_INFRASTRUCTURE",
                "execution_class": "SYNTHETIC_INFRASTRUCTURE",
                "p12_access_class": "PERMITTED",
            },
        ],
        "claim_policy": {
            "claim_ceiling_sha256": protocol["claim_ceiling_sha256"],
            "required_status": "blocked",
        },
    }


def _nested_value(value, path):
    for component in path:
        value = value[component]
    return value


def test_controller_manifest_covers_exact_controller_role_roots(tmp_path):
    source = tmp_path / "src/p3_v3/controller.py"
    script = tmp_path / "scripts/p3_v3/evidence.py"
    dependency_lock = tmp_path / "requirements-frozen.txt"
    source.parent.mkdir(parents=True)
    script.parent.mkdir(parents=True)
    source.write_text("controller = True\n", encoding="utf-8")
    script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    dependency_lock.write_text("pytest==8.4.2\n", encoding="utf-8")

    manifest = evidence_module.build_tracked_source_manifest(
        tmp_path,
        ["src/p3_v3", "scripts/p3_v3", "requirements-frozen.txt"],
        "controller-source",
    )

    assert set(manifest) == {"schema_version", "role", "files"}
    assert manifest["schema_version"] == "P3_V3_TRACKED_SOURCE_MANIFEST_V1"
    assert manifest["role"] == "controller-source"
    assert manifest["files"] == [
        {
            "relative_path": "requirements-frozen.txt",
            "mode": "100644",
            "sha256": hashlib.sha256(dependency_lock.read_bytes()).hexdigest(),
        },
        {
            "relative_path": "scripts/p3_v3/evidence.py",
            "mode": "100755",
            "sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        },
        {
            "relative_path": "src/p3_v3/controller.py",
            "mode": "100644",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
    ]


def test_controller_manifest_rejects_omitted_role_root(tmp_path):
    (tmp_path / "src/p3_v3").mkdir(parents=True)
    (tmp_path / "scripts/p3_v3").mkdir(parents=True)
    (tmp_path / "requirements-frozen.txt").write_text("locked\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path,
            ["src/p3_v3", "scripts/p3_v3"],
            "controller-source",
        )


def test_subject_manifest_includes_complete_root_and_excludes_git(tmp_path):
    source = tmp_path / "subject.py"
    vendor = tmp_path / "vendor/dependency.py"
    fixture = tmp_path / "fixtures/input.txt"
    generated = tmp_path / "generated/parser.py"
    git_config = tmp_path / ".git/config"
    for path in (source, vendor, fixture, generated, git_config):
        path.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("password = token\n", encoding="utf-8")
    vendor.write_text("vendor = True\n", encoding="utf-8")
    fixture.write_text("fixture\n", encoding="utf-8")
    generated.write_text("generated = True\n", encoding="utf-8")
    git_config.write_text("authorization = credential\n", encoding="utf-8")

    manifest = evidence_module.build_tracked_source_manifest(
        tmp_path, ["."], "subject-source"
    )

    assert [row["relative_path"] for row in manifest["files"]] == [
        "fixtures/input.txt",
        "generated/parser.py",
        "subject.py",
        "vendor/dependency.py",
    ]
    assert all(set(row) == {"relative_path", "mode", "sha256"} for row in manifest["files"])


def test_subject_manifest_rejects_selective_file_roots(tmp_path):
    (tmp_path / "subject.py").write_text("subject = True\n", encoding="utf-8")
    (tmp_path / "omitted.py").write_text("omitted = True\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["subject.py"], "subject-source"
        )


@pytest.mark.parametrize(
    "transient",
    [".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist"],
)
def test_subject_manifest_rejects_transient_environment_or_build_paths(
    tmp_path, transient
):
    path = tmp_path / transient / "generated.bin"
    path.parent.mkdir()
    path.write_bytes(b"transient")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["."], "subject-source"
        )


@pytest.mark.parametrize("node_kind", ["symlink", "fifo", "git-symlink"])
def test_subject_manifest_rejects_symlink_and_special_nodes(tmp_path, node_kind):
    source = tmp_path / "subject.py"
    source.write_text("subject = True\n", encoding="utf-8")
    if node_kind == "symlink":
        (tmp_path / "linked.py").symlink_to(source)
    elif node_kind == "fifo":
        os.mkfifo(tmp_path / "source.fifo")
    else:
        outside = tmp_path / "worktree-admin"
        outside.mkdir()
        (tmp_path / ".git").symlink_to(outside, target_is_directory=True)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["."], "subject-source"
        )


def test_source_manifest_rejects_missing_and_overlapping_role_roots(tmp_path):
    tree = tmp_path / "tree"
    nested = tree / "nested"
    nested.mkdir(parents=True)
    (nested / "source.py").write_text("source = True\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["missing"], "fixture-source"
        )
    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["tree", "tree/nested"], "fixture-source"
        )


def test_source_manifest_rejects_symlinked_role_root_parent(tmp_path):
    actual = tmp_path / "actual/nested"
    actual.mkdir(parents=True)
    (actual / "source.py").write_text("source = True\n", encoding="utf-8")
    (tmp_path / "linked").symlink_to(tmp_path / "actual", target_is_directory=True)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["linked/nested"], "fixture-source"
        )


def test_controller_and_subject_manifests_are_independent(tmp_path):
    controller = tmp_path / "controller"
    subject_a = tmp_path / "subject-a"
    subject_b = tmp_path / "subject-b"
    for root, content in ((subject_a, "a\n"), (subject_b, "b\n")):
        root.mkdir()
        (root / "source.py").write_text(content, encoding="utf-8")
    (controller / "src/p3_v3").mkdir(parents=True)
    (controller / "scripts/p3_v3").mkdir(parents=True)
    (controller / "src/p3_v3/controller.py").write_text("c\n", encoding="utf-8")
    (controller / "scripts/p3_v3/evidence.py").write_text("e\n", encoding="utf-8")
    (controller / "requirements-frozen.txt").write_text("r\n", encoding="utf-8")

    manifests = [
        evidence_module.build_tracked_source_manifest(
            controller,
            ["src/p3_v3", "scripts/p3_v3", "requirements-frozen.txt"],
            "controller-source",
        ),
        evidence_module.build_tracked_source_manifest(
            subject_a, ["."], "subject-source"
        ),
        evidence_module.build_tracked_source_manifest(
            subject_b, ["."], "subject-source"
        ),
    ]

    assert len({hashlib.sha256(canonical_json_bytes(item)).hexdigest() for item in manifests}) == 3


def test_validate_authority_lock_accepts_exact_schema():
    lock = _authority_lock()

    assert evidence_module.validate_authority_lock(lock) == lock


@pytest.mark.parametrize(
    ("path", "missing_key"),
    [
        (path, key)
        for path, keys in _AUTHORITY_OBJECT_SCHEMAS
        for key in sorted(keys)
    ],
)
def test_authority_lock_rejects_every_missing_top_level_or_nested_key(
    path, missing_key
):
    lock = _authority_lock()
    del _nested_value(lock, path)[missing_key]

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize("path", [path for path, _keys in _AUTHORITY_OBJECT_SCHEMAS])
def test_authority_lock_rejects_extra_top_level_or_nested_key(path):
    lock = _authority_lock()
    _nested_value(lock, path)["unexpected"] = "not-authority"

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize(
    ("collection", "mutation"),
    [
        ("subjects", "swapped"),
        ("subjects", "duplicated"),
        ("jobs", "swapped"),
        ("jobs", "duplicated"),
    ],
)
def test_authority_lock_rejects_swapped_or_duplicated_rows(collection, mutation):
    lock = _authority_lock()
    if mutation == "swapped":
        lock[collection].reverse()
    else:
        lock[collection][1] = copy.deepcopy(lock[collection][0])

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


def test_authority_lock_rejects_duplicate_intent_templates_under_distinct_job_ids():
    lock = _authority_lock()
    lock["jobs"][1]["intent_template_sha256"] = lock["jobs"][0][
        "intent_template_sha256"
    ]

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("execution_class", "RELABELED"),
        ("p12_access_class", "UNKNOWN"),
        ("retry_trigger", "ALWAYS"),
        ("maximum_attempts", 4),
    ],
)
def test_authority_lock_rejects_invalid_job_enums_and_retry_policy(field, value):
    lock = _authority_lock()
    lock["jobs"][0][field] = value

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize(
    ("path", "field", "value", "error"),
    [
        (("controller_repository",), "base_commit", "A" * 40, "E_AUTHORITY_LOCK_SCHEMA"),
        (
            ("controller_repository",),
            "tracked_source_manifest_sha256",
            "A" * 64,
            "E_SHA256",
        ),
        (("jobs", 0), "maximum_attempts", True, "E_SCHEMA_TYPE"),
        ((), "schema_version", "P3_V3_AUTHORITY_LOCK_V2", "E_AUTHORITY_LOCK_SCHEMA"),
    ],
)
def test_authority_lock_rejects_invalid_hash_type_and_version(path, field, value, error):
    lock = _authority_lock()
    _nested_value(lock, path)[field] = value

    with pytest.raises(EvidenceError, match=error):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize("field", ["required_capabilities", "forbidden_credential_fields"])
def test_authority_lock_rejects_unsorted_or_duplicated_preflight_lists(field):
    lock = _authority_lock()
    lock["preflight"][field] = list(reversed(lock["preflight"][field]))

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize("field", ["token", "password", "authorization", "credential"])
def test_authority_lock_rejects_credential_metadata_without_echoing_value(field):
    lock = _authority_lock()
    secret = "TOP_SECRET_DO_NOT_ECHO"
    lock["preflight"][field] = secret

    with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
        evidence_module.validate_authority_lock(lock)

    assert secret not in str(caught.value)


def test_authority_lock_rejects_raw_origin_userinfo_without_echoing_value():
    lock = _authority_lock()
    secret = "TOP_SECRET_DO_NOT_ECHO"
    lock["controller_repository"]["normalized_repository_identity"] = (
        f"https://audit-user:{secret}@github.com/example/controller"
    )

    with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
        evidence_module.validate_authority_lock(lock)

    assert secret not in str(caught.value)


@pytest.mark.parametrize(
    "mutation",
    [
        "preflight-identity",
        "preflight-commit",
        "preflight-tree",
        "environment-policy",
        "claim-ceiling",
        "subject-role-duplicate",
        "subject-manifest-duplicate",
    ],
)
def test_authority_lock_rejects_cross_field_divergence(mutation):
    lock = _authority_lock()
    if mutation == "preflight-identity":
        lock["preflight"]["normalized_repository_identity"] = "github.com/example/other"
    elif mutation == "preflight-commit":
        lock["preflight"]["base_commit"] = "9" * 40
    elif mutation == "preflight-tree":
        lock["preflight"]["base_tree"] = "9" * 40
    elif mutation == "environment-policy":
        lock["preflight"]["environment_policy_sha256"] = "9" * 64
    elif mutation == "claim-ceiling":
        lock["claim_policy"]["claim_ceiling_sha256"] = "9" * 64
    elif mutation == "subject-role-duplicate":
        lock["subjects"][1]["repository_role"] = lock["subjects"][0]["repository_role"]
    else:
        lock["subjects"][1]["tracked_source_manifest_sha256"] = lock["subjects"][0][
            "tracked_source_manifest_sha256"
        ]

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


def test_load_authority_lock_rejects_changed_bytes_before_parsing_fields(tmp_path):
    path = tmp_path / "authority-lock.json"
    original_raw = canonical_json_bytes(_authority_lock())
    expected_sha256 = hashlib.sha256(original_raw).hexdigest()
    path.write_bytes(b"not-json\n")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_DIGEST"):
        evidence_module.load_authority_lock(path, expected_sha256)


def test_load_authority_lock_rejects_matching_noncanonical_bytes(tmp_path):
    path = tmp_path / "authority-lock.json"
    raw = json.dumps(_authority_lock(), sort_keys=True, indent=2).encode("utf-8") + b"\n"
    path.write_bytes(raw)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.load_authority_lock(path, hashlib.sha256(raw).hexdigest())


def test_load_authority_lock_accepts_matching_canonical_bytes(tmp_path):
    path = tmp_path / "authority-lock.json"
    raw = canonical_json_bytes(_authority_lock())
    path.write_bytes(raw)

    assert evidence_module.load_authority_lock(
        path, hashlib.sha256(raw).hexdigest()
    ) == _authority_lock()


def _source_tree_sha256(root: Path) -> str:
    files = [
        {
            "path": path.relative_to(root).as_posix(),
            "byte_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    return canonical_sha256({"domain": "P3-NORMALIZED-SOURCE-TREE-v1", "files": files})


def _profiling_receipt(
    workload: dict,
    source_record: dict,
    neutral: str,
    adapter_source_sha256: str | None,
) -> dict:
    rows = []
    for selected in workload["selected_rows"]:
        call_trace = [
            {
                "sequence": 1,
                "module": "fixture.subject",
                "symbol": f"scalar_{selected['behavior_id'][:12]}",
                "call_kind": "PYTHON_CALL",
                "argument_types": ["float"],
                "keyword_names": [],
            }
        ]
        rows.append({
            "behavior_id": selected["behavior_id"],
            "status": "SUCCESS",
            "argv": ["fixture-runner", selected["behavior_id"]],
            "input_sha256": ["51" * 32],
            "environment_sha256": "52" * 32,
            "runner_version": "fixture-runner-v1",
            "exit_code": 0,
            "stdout_sha256": "53" * 32,
            "stderr_sha256": "54" * 32,
            "call_trace": call_trace,
            "call_trace_sha256": canonical_sha256(call_trace),
            "timed_out": False,
            "failure_code": "",
            "observed_site_ids": [],
        })
    body = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": neutral,
        "controlled_subject_source_id": workload["controlled_subject_source_id"],
        **source_record,
        "profiling_workload_sha256": workload["artifact_sha256"],
        "adapter_implementation_source_sha256": adapter_source_sha256,
        "runner_implementation_source_sha256": hashlib.sha256(
            Path(frames_module.__file__).read_bytes()
        ).hexdigest(),
        "results": sorted(rows, key=lambda row: row["behavior_id"]),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _run_git(root: Path, *argv: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *argv],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def _secret_preflight_fixture(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "repo"
    root.mkdir()
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "Fixture")
    _run_git(root, "config", "user.email", "fixture@example.invalid")
    _run_git(root, "remote", "add", "origin", SECRET_ORIGIN)
    lock = root / "requirements.lock"
    lock.write_text("dependency==1\n", encoding="utf-8")
    input_path = root / "input.json"
    input_path.write_text("{}\n", encoding="utf-8")
    _run_git(root, "add", "requirements.lock", "input.json")
    _run_git(root, "commit", "-m", "fixture")
    spec = {
        "schema_version": "p3-preflight-v1",
        "repository_identity": SECRET_IDENTITY,
        "expected_commit": _run_git(root, "rev-parse", "HEAD"),
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "phase_inputs": [
            {
                "path": "input.json",
                "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
            }
        ],
        "smoke_commands": [["python3", "-c", "print(1)"]],
        "timeout_seconds": 10,
        "phase_role": "CONTROLLED_B",
        "minimum_cpu_count": 1,
        "minimum_memory_bytes": 1,
        "minimum_disk_free_bytes": 1,
        "worker_limit": 1,
    }
    return root, spec


def _protocol_body(**overrides):
    body = {
        "schema_version": "p3-protocol-v1",
        "scientific_plan_sha256": SCIENTIFIC_PLAN_SHA256,
        "evidence_design_sha256": EVIDENCE_DESIGN_SHA256,
        "claims_initial_status": "blocked",
        "rq_spec_sha256": _digest("rq"),
        "claim_ceiling_sha256": _digest("ceiling"),
        "p12_contract_sha256": _digest("p12"),
        "operator_catalogue_sha256": _digest("operators"),
        "adapter_registry_sha256": _digest("adapters"),
        "input_generator_registry_sha256": _digest("generators"),
        "mr_policy_sha256": _digest("mr"),
        "site_policy_sha256": _digest("site"),
        "analysis_spec_sha256": _digest("analysis"),
        "package_policy_sha256": _digest("package"),
        "environment_lock_sha256": _digest("env"),
        "profiling_budgets": {"S": 10, "M": 15, "L": 20},
        "behavior_category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "technique_order": list(TECHNIQUE_ORDER),
        "e_common_count": 30,
        "e_contract_count": 5,
        "p12_outcome_states": list(P12_OUTCOME_STATES),
        "p12_primary_estimand": "INTENTION_TO_EVALUATE_LOWER_BOUND",
        "infrastructure_retry_limit": 3,
    }
    body.update(overrides)
    return body


def _write_protocol(path: Path, body: dict) -> bytes:
    payload = {**body}
    if "artifact_sha256" not in payload:
        payload["artifact_sha256"] = canonical_sha256(payload)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    path.write_bytes(raw)
    return raw


def _adapter_registry(tmp_path: Path) -> dict:
    adapters = []
    for adapter_id, ecosystem, rel in _ADAPTER_SPECS:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        fixture = ADAPTER_FIXTURE_ROOT / Path(rel).name
        if fixture.is_file():
            path.write_bytes(fixture.read_bytes())
        else:
            path.write_text(f"# adapter {adapter_id}\n", encoding="utf-8")
        adapters.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": rel,
                "source_sha256": __import__("hashlib")
                .sha256(path.read_bytes())
                .hexdigest(),
            }
        )
    body = {"schema_version": "p3-adapter-registry-v1", "adapters": adapters}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _tagged_declarations(name: str) -> list[dict]:
    fixture = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    rows = []
    for item in fixture["declarations"]:
        row = dict(item)
        row["ecosystem"] = fixture["ecosystem"]
        if fixture.get("adapter_id") is not None:
            row["adapter_id"] = fixture["adapter_id"]
        rows.append(row)
    return rows


def test_cli_help_lists_only_frozen_commands():
    result = subprocess.run(
        ["python3", str(CLI), "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    line = next(
        item for item in result.stdout.splitlines() if "{" in item and "}" in item
    )
    observed = set(line[line.index("{") + 1 : line.index("}")].split(","))
    assert observed == COMMANDS


def test_build_frames_subject_specs_are_the_only_subject_authority_options(tmp_path):
    help_result = subprocess.run(
        ["python3", str(CLI), "build-frames", "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert help_result.returncode == 0
    assert "--subject-specs" in help_result.stdout
    for removed in ("--declarations", "--features", "--scale-class"):
        assert removed not in help_result.stdout
        output_root = tmp_path / removed.removeprefix("--")
        result = subprocess.run(
            [
                "python3",
                str(CLI),
                "build-frames",
                "--bridge",
                str(tmp_path / "bridge.json"),
                "--subject-specs",
                str(tmp_path / "subject-specs.json"),
                "--adapter-root",
                str(tmp_path),
                "--generator-root",
                str(tmp_path),
                "--slots",
                str(tmp_path / "slots.json"),
                "--contracts",
                str(tmp_path / "contracts.json"),
                "--applicability-map",
                str(tmp_path / "applicability.json"),
                "--output-root",
                str(output_root),
                removed,
                "legacy-authority.json",
            ],
            capture_output=True,
            check=False,
            text=True,
            env=_env(),
        )
        assert result.returncode == 2
        assert f"unrecognized arguments: {removed}" in result.stderr
        assert not output_root.exists()


@pytest.mark.parametrize("case", ["missing", "duplicate", "extra"])
def test_build_frames_subject_spec_coverage_fails_before_adapter_execution(
    tmp_path, case
):
    neutral = _digest("subject-neutral")
    record = {
        "neutral_snapshot_id": neutral,
        "fixed_tree_commitment": "4" * 64,
        "normalized_source_tree_sha256": "21" * 32,
        "source_archive_sha256": "5" * 64,
        "build_descriptor_sha256": "22" * 32,
        "eligibility_reason": "fixture",
        "eligible_for_construct": True,
        "eligible_for_criterion": True,
    }
    bridge = {"records": [record]}
    base_spec = {
        "neutral_snapshot_id": neutral,
        "source_root": str(tmp_path / "must-not-execute"),
        "source_record": {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
        },
        "build_descriptor": {"ecosystem": "python"},
        "adapter_registry": {},
        "input_generator_registry": {},
        "profiling_results": {},
    }
    if case == "missing":
        specs = []
    elif case == "duplicate":
        specs = [base_spec, dict(base_spec)]
    else:
        specs = [{**base_spec, "neutral_snapshot_id": _digest("extra-neutral")}]
    paths = {
        "bridge": tmp_path / "bridge.json",
        "specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    for path, value in (
        (paths["bridge"], bridge),
        (paths["specs"], specs),
        (paths["slots"], []),
        (paths["contracts"], {}),
        (paths["applicability"], {}),
    ):
        write_canonical_json(path, value, exclusive=True)
    output_root = tmp_path / "frames-out"
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "build-frames",
            "--bridge",
            str(paths["bridge"]),
            "--subject-specs",
            str(paths["specs"]),
            "--adapter-root",
            str(tmp_path),
            "--generator-root",
            str(tmp_path),
            "--slots",
            str(paths["slots"]),
            "--contracts",
            str(paths["contracts"]),
            "--applicability-map",
            str(paths["applicability"]),
            "--output-root",
            str(output_root),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SUBJECT_SPEC_COVERAGE"
    assert not output_root.exists()


def test_run_preflight_stdout_and_receipt_do_not_reveal_secret_origin(tmp_path):
    root, spec = _secret_preflight_fixture(tmp_path)
    spec_path = tmp_path / "preflight.json"
    receipt_path = tmp_path / "receipt.json"
    write_canonical_json(spec_path, spec, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "run-preflight",
            "--root",
            str(root),
            "--spec",
            str(spec_path),
            "--output",
            str(receipt_path),
        ],
        capture_output=True,
        check=False,
        env=_env(),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["repository_identity"] == SECRET_IDENTITY
    assert payload["origin_transport"] == "HTTPS"
    assert payload["origin_sha256"] == SECRET_ORIGIN_SHA256
    assert "raw_origin" not in payload
    for stream in (result.stdout, result.stderr, receipt_path.read_bytes()):
        assert b"audit-user" not in stream
        assert b"TOP_SECRET_TOKEN" not in stream


def test_run_preflight_error_does_not_reveal_secret_origin(tmp_path):
    root, spec = _secret_preflight_fixture(tmp_path)
    spec["repository_identity"] = "github.com/Other/Repo"
    spec_path = tmp_path / "preflight.json"
    write_canonical_json(spec_path, spec, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "run-preflight",
            "--root",
            str(root),
            "--spec",
            str(spec_path),
        ],
        capture_output=True,
        check=False,
        env=_env(),
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PREFLIGHT_REPOSITORY"
    for stream in (result.stdout, result.stderr):
        assert b"audit-user" not in stream
        assert b"TOP_SECRET_TOKEN" not in stream


def test_validate_protocol_prints_one_canonical_json_result(tmp_path):
    protocol = tmp_path / "protocol.json"
    raw = _write_protocol(protocol, _protocol_body())
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["protocol_sha256"] == __import__("hashlib").sha256(raw).hexdigest()
    assert (
        result.stdout
        == json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    )


def test_validate_protocol_rejects_a_different_well_formed_plan_hash(tmp_path):
    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body(scientific_plan_sha256="a" * 64))
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_AUTHORITY"


def test_validate_protocol_rejects_extra_key_before_writing_output(tmp_path):
    protocol = tmp_path / "protocol.json"
    body = _protocol_body()
    body["extra_field"] = "nope"
    body["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in body.items() if key != "artifact_sha256"}
    )
    protocol.write_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "validate-protocol",
            "--protocol",
            str(protocol),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


def test_validate_protocol_rejects_missing_key(tmp_path):
    protocol = tmp_path / "protocol.json"
    body = _protocol_body()
    del body["e_common_count"]
    body["artifact_sha256"] = canonical_sha256(body)
    protocol.write_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


def test_validate_protocol_rejects_old_authority_digest(tmp_path):
    protocol = tmp_path / "protocol.json"
    _write_protocol(
        protocol,
        _protocol_body(
            scientific_plan_sha256="911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772",
            evidence_design_sha256="e2a943b30f8096aa65a72c43aa514df67b8d58e16fcf7209930799ee4444c346",
        ),
    )
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_AUTHORITY"


def test_validate_protocol_rejects_wrong_counts_retry_or_outcome_order(tmp_path):
    cases = [
        {"e_common_count": 29},
        {"e_contract_count": 4},
        {"infrastructure_retry_limit": 4},
        {
            "p12_outcome_states": [
                "MR_SATISFIED",
                "MR_VIOLATION",
                "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
                "SCIENTIFIC_INCONCLUSIVE",
                "INFRASTRUCTURE_UNRESOLVED",
            ]
        },
    ]
    for overrides in cases:
        protocol = tmp_path / f"protocol-{next(iter(overrides))}.json"
        _write_protocol(protocol, _protocol_body(**overrides))
        result = subprocess.run(
            ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
            capture_output=True,
            check=False,
            text=True,
            env=_env(),
        )
        assert result.returncode == 2
        assert json.loads(result.stderr)["code"] in {
            "E_PROTOCOL",
            "E_PROTOCOL_COUNTS",
            "E_PROTOCOL_RETRY",
            "E_PROTOCOL_OUTCOMES",
        }


def test_verify_mr_inventory_accepts_exact_chronology(tmp_path):
    candidate_body = {
        "schema_version": "p3-mr-candidate-frame-v1",
        "artifact_type": "MR_CANDIDATE_FRAME",
        "candidate_mr_ids": ["mr-1"],
    }
    candidate = {**candidate_body, "artifact_sha256": canonical_sha256(candidate_body)}
    receipt_body = {
        "schema_version": "p3-mr-custodian-receipt-v1",
        "artifact_type": "MR_CUSTODIAN_RECEIPT",
        "candidate_frame_sha256": candidate["artifact_sha256"],
        "receipt_state": "CLOSED",
        "admitted_mr_ids": ["mr-1"],
        "excluded_mr_ids": [],
    }
    receipt = {**receipt_body, "artifact_sha256": canonical_sha256(receipt_body)}
    inventory_body = {
        "schema_version": "p3-mr-final-inventory-v1",
        "artifact_type": "MR_FINAL_INVENTORY",
        "custodian_receipt_sha256": receipt["artifact_sha256"],
        "mr_ids": ["mr-1"],
    }
    inventory = {
        **inventory_body,
        "artifact_sha256": canonical_sha256(inventory_body),
    }
    portfolios_body = {
        "schema_version": "p3-mr-portfolios-v1",
        "artifact_type": "MR_PORTFOLIOS",
        "final_inventory_sha256": inventory["artifact_sha256"],
        "portfolios": [{"portfolio_id": "primary", "mr_ids": ["mr-1"]}],
    }
    portfolios = {
        **portfolios_body,
        "artifact_sha256": canonical_sha256(portfolios_body),
    }
    paths = {}
    for name, artifact in (
        ("candidate", candidate),
        ("receipt", receipt),
        ("inventory", inventory),
        ("portfolios", portfolios),
    ):
        paths[name] = tmp_path / f"{name}.json"
        write_canonical_json(paths[name], artifact, exclusive=True)
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-mr-inventory",
            "--candidate-frame",
            str(paths["candidate"]),
            "--custodian-receipt",
            str(paths["receipt"]),
            "--final-inventory",
            str(paths["inventory"]),
            "--portfolios",
            str(paths["portfolios"]),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "PASS"

    legacy = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-mr-inventory",
            "--inventory",
            str(paths["inventory"]),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert legacy.returncode == 2
    help_result = subprocess.run(
        ["python3", str(CLI), "verify-mr-inventory", "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert "--inventory" not in help_result.stdout


def test_build_frames_writes_declared_artifacts_under_output_root_only(tmp_path):
    adapter_root = tmp_path / "adapters-root"
    adapter_root.mkdir()
    raw_registry = _adapter_registry(adapter_root)
    registry = validate_adapter_registry(raw_registry, adapter_root)
    source_root = tmp_path / "source-root"
    source_root.mkdir()
    fixture = json.loads((FIXTURE_ROOT / "python.json").read_text(encoding="utf-8"))
    for relative in fixture["source_files"]:
        path = source_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def solve(value):\n    return value\n", encoding="utf-8")
    manifest = source_root / "adapter-python.json"
    write_canonical_json(manifest, fixture, exclusive=True)
    descriptor = {
        "ecosystem": "python",
        "manifest_path": manifest.name,
        "reverse": False,
    }
    source_record = {
        "normalized_source_tree_sha256": _source_tree_sha256(source_root),
        "build_descriptor_sha256": canonical_sha256(descriptor),
    }
    neutral = canonical_sha256({"fixture": "neutral"})
    discovery = run_adapter_discovery(
        source_root, descriptor, registry, "PYTHON_PEP517_V1"
    )
    frame = build_public_behavior_frame(source_record, discovery)
    workload = select_profiling_workload(frame, "S")
    profiling_results = _profiling_receipt(
        workload,
        source_record,
        neutral,
        discovery["implementation_source_sha256"],
    )
    bridge = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "fixture",
        "p12_repository_identity": "Example/P12-Defect4MR",
        "p12_contract_path": "release/contract.json",
        "p12_contract_blob_sha": "0" * 40,
        "p12_package_root_sha256": "1" * 64,
        "p12_contract_sha256": "2" * 64,
        "eligible_inventory_root_sha256": "3" * 64,
        "eligible_item_count": 1,
        "trust_mode": "PINNED_GIT_RELEASE",
        "records": [
            {
                "neutral_snapshot_id": neutral,
                "fixed_tree_commitment": "4" * 64,
                "normalized_source_tree_sha256": source_record[
                    "normalized_source_tree_sha256"
                ],
                "source_archive_sha256": "5" * 64,
                "build_descriptor_sha256": source_record["build_descriptor_sha256"],
                "eligibility_reason": "fixture",
                "eligible_for_construct": True,
                "eligible_for_criterion": True,
            }
        ],
    }
    bridge = {**bridge, "artifact_sha256": canonical_sha256(bridge)}
    generator_registry = json.loads(
        (
            Path(__file__).resolve().parent / "fixtures/input_generators/registry.json"
        ).read_text(encoding="utf-8")
    )
    generator_root = Path(__file__).resolve().parent / "fixtures/input_generators"
    subject_specs = [
        {
            "neutral_snapshot_id": bridge["records"][0]["neutral_snapshot_id"],
            "source_root": str(source_root),
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": raw_registry,
            "input_generator_registry": generator_registry,
            "profiling_results": profiling_results,
        }
    ]
    outside = tmp_path / "outside"
    outside.mkdir()
    output_root = tmp_path / "frames-out"
    paths = {
        "bridge": tmp_path / "bridge.json",
        "subject_specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    write_canonical_json(paths["bridge"], bridge, exclusive=True)
    write_canonical_json(paths["subject_specs"], subject_specs, exclusive=True)
    write_canonical_json(paths["slots"], [], exclusive=True)
    write_canonical_json(paths["contracts"], {}, exclusive=True)
    write_canonical_json(paths["applicability"], {}, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "build-frames",
            "--bridge",
            str(paths["bridge"]),
            "--subject-specs",
            str(paths["subject_specs"]),
            "--adapter-root",
            str(adapter_root),
            "--generator-root",
            str(generator_root),
            "--slots",
            str(paths["slots"]),
            "--contracts",
            str(paths["contracts"]),
            "--applicability-map",
            str(paths["applicability"]),
            "--output-root",
            str(output_root),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    neutral = bridge["records"][0]["neutral_snapshot_id"]
    expected = {
        f"adapter-discovery-{neutral}.json",
        f"source-scale-{neutral}.json",
        f"public-behavior-frame-{neutral}.json",
        f"profiling-workload-{neutral}.json",
        f"evaluation-inputs-common-{neutral}.json",
        f"profiling-results-{neutral}.json",
        f"technique-profile-{neutral}.json",
        f"derived-subject-{neutral}.json",
        "subject-frames.json",
    }
    written = {path.name for path in output_root.iterdir() if path.is_file()}
    assert expected <= written
    assert list(outside.iterdir()) == []
    common = json.loads(
        (output_root / f"evaluation-inputs-common-{neutral}.json").read_text()
    )
    assert len(common["rows"]) == 30
    assert any(row["status"] == "COMMON_INPUT_EXECUTABLE" for row in common["rows"])


def _indexed_reference(index_root: Path, path: Path) -> dict:
    return {
        "path": path.relative_to(index_root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _write_evidence_index(path: Path, body: dict) -> None:
    write_canonical_json(
        path,
        {**body, "artifact_sha256": canonical_sha256(body)},
        exclusive=True,
    )


def _claim_authority() -> dict:
    associations = {
        "C1_SEMANTIC_MUTATION_SYSTEM_PROTOCOL": ["RQ1", "RQ2", "RQ3"],
        "C2_CROSS_PROJECT_OPERATOR_EFFECTIVENESS": ["RQ1"],
        "C3_EQUIVALENCE_PROTOCOL_VALUE": ["RQ2"],
        "C4_SMS_DISCRIMINANT_VALIDITY": ["RQ2"],
        "C5_CONTROLLED_REAL_CONSISTENCY": ["RQ3"],
        "C6_STRUCTURED_VS_NATIVE_SUPERIORITY": ["RQ2"],
        "C7_REPRODUCIBLE_EVIDENCE_INFRASTRUCTURE": ["RQ1", "RQ2", "RQ3"],
    }
    claims = [
        {"claim_id": claim_id, "rqs": rqs, "initial_status": "blocked"}
        for claim_id, rqs in associations.items()
    ]
    body = {"schema_version": "p3-claim-ceiling-authority-v1", "claims": claims}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _blocked_claim_ledger(*references: str) -> dict:
    evidence = sorted(set(references))
    authority = _claim_authority()
    claims = []
    for authority_claim in authority["claims"]:
        claim_body = {
            "claim_id": authority_claim["claim_id"],
            "rqs": authority_claim["rqs"],
            "evidence_references": evidence,
            "status": "blocked",
        }
        claims.append(
            {**claim_body, "artifact_sha256": canonical_sha256(claim_body)}
        )
    body = {
        "schema_version": "p3-claim-evidence-v1",
        "claim_authority_sha256": hashlib.sha256(
            canonical_json_bytes(authority)
        ).hexdigest(),
        "rq_authority_sha256": hashlib.sha256(
            (
                ROOT
                / "research/p3-semantic-mutation-core-claims-rqs-v1.2.0.md"
            ).read_bytes()
        ).hexdigest(),
        "claims": claims,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


_PROTOCOL_ARTIFACT_FIELDS = (
    "rq_spec_sha256",
    "claim_ceiling_sha256",
    "p12_contract_sha256",
    "operator_catalogue_sha256",
    "mr_policy_sha256",
    "site_policy_sha256",
    "analysis_spec_sha256",
    "package_policy_sha256",
    "environment_lock_sha256",
)


def _install_protocol_authorities(tmp_path: Path) -> dict:
    artifact_paths = {}
    for field in _PROTOCOL_ARTIFACT_FIELDS:
        path = tmp_path / f"authority-{field}.bin"
        if field == "rq_spec_sha256":
            path.write_bytes(
                (
                    ROOT
                    / "research/p3-semantic-mutation-core-claims-rqs-v1.2.0.md"
                ).read_bytes()
            )
        elif field == "claim_ceiling_sha256":
            path.write_bytes(canonical_json_bytes(_claim_authority()))
        else:
            path.write_bytes(f"{field}\n".encode())
        artifact_paths[field] = path

    adapter_root = tmp_path / "authority-adapters"
    adapter_root.mkdir()
    adapter_registry = _adapter_registry(adapter_root)
    adapter_registry_path = adapter_root / "registry.json"
    write_canonical_json(adapter_registry_path, adapter_registry, exclusive=True)

    generator_fixture_root = Path(__file__).resolve().parent / "fixtures/input_generators"
    generator_root = tmp_path / "authority-generators"
    shutil.copytree(
        generator_fixture_root,
        generator_root,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    generator_registry_path = generator_root / "registry.json"
    generator_registry = json.loads(generator_registry_path.read_text())

    hashes = {
        field: hashlib.sha256(path.read_bytes()).hexdigest()
        for field, path in artifact_paths.items()
    }
    hashes.update(
        {
            "adapter_registry_sha256": hashlib.sha256(
                adapter_registry_path.read_bytes()
            ).hexdigest(),
            "input_generator_registry_sha256": hashlib.sha256(
                generator_registry_path.read_bytes()
            ).hexdigest(),
        }
    )
    return {
        "hashes": hashes,
        "artifacts": artifact_paths,
        "adapter_registry": adapter_registry,
        "adapter_registry_path": adapter_registry_path,
        "generator_registry": generator_registry,
        "generator_registry_path": generator_registry_path,
    }


def _empty_evidence_index_body(tmp_path: Path) -> dict:
    authorities = _install_protocol_authorities(tmp_path)
    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body(**authorities["hashes"]))
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")
    (tmp_path / "jobs").mkdir()
    claims = _blocked_claim_ledger(
        "authority-rq_spec_sha256.bin",
        "authority-claim_ceiling_sha256.bin",
        "protocol.json",
    )
    claims_path = tmp_path / "claims.json"
    write_canonical_json(claims_path, claims, exclusive=True)
    return {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V1",
        "phase_coverage": [],
        "protocol": _indexed_reference(tmp_path, protocol),
        "protocol_artifacts": {
            field: _indexed_reference(tmp_path, authorities["artifacts"][field])
            for field in _PROTOCOL_ARTIFACT_FIELDS
        },
        "adapter_registries": [
            _indexed_reference(tmp_path, authorities["adapter_registry_path"])
        ],
        "input_generator_registries": [
            _indexed_reference(tmp_path, authorities["generator_registry_path"])
        ],
        "subjects": [],
        "packages": [],
        "mr_chain": {},
        "job_root": "jobs",
        "ledger": _indexed_reference(tmp_path, ledger),
        "phase_receipts": [],
        "p12": {},
        "claims": _indexed_reference(tmp_path, claims_path),
    }


def _run_evidence_index(index_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(CLI), "verify-evidence", "--index", str(index_path)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("extra_key", "E_SCHEMA_KEYS"),
        ("missing_key", "E_SCHEMA_KEYS"),
        ("unsafe_path", "E_PATH"),
        ("duplicate_path", "E_INDEX_DUPLICATE"),
        ("hash_mismatch", "E_INDEX_FILE_HASH"),
        ("unknown_phase", "E_INDEX_PHASE"),
        ("empty_phase_collections", "E_INDEX_COVERAGE"),
    ],
)
def test_evidence_index_rejects_structural_forgery(tmp_path, mutation, expected_code):
    body = _empty_evidence_index_body(tmp_path)
    if mutation == "extra_key":
        body["unbound"] = []
    elif mutation == "missing_key":
        del body["claims"]
    elif mutation == "unsafe_path":
        body["protocol"] = {**body["protocol"], "path": "../protocol.json"}
    elif mutation == "duplicate_path":
        body["claims"] = dict(body["protocol"])
    elif mutation == "hash_mismatch":
        body["protocol"] = {**body["protocol"], "sha256": "0" * 64}
    elif mutation == "unknown_phase":
        body["phase_coverage"] = ["PHASE_8"]
    elif mutation == "empty_phase_collections":
        body["phase_coverage"] = ["PHASE_0"]
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == expected_code
    assert not result.stdout


def test_evidence_index_rejects_noncanonical_bytes(tmp_path):
    body = _empty_evidence_index_body(tmp_path)
    index = {**body, "artifact_sha256": canonical_sha256(body)}
    index_path = tmp_path / "evidence-index.json"
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_NONCANONICAL_JSON"
    assert not result.stdout


def _complete_phase_zero_evidence_index(tmp_path: Path) -> Path:
    from p3_v3.packages import build_package
    from p3_v3.run_records import (
        close_phase,
        create_intent,
        reconstruct_attempt_events,
        write_result,
    )

    authorities = _install_protocol_authorities(tmp_path)
    protocol = tmp_path / "protocol.json"
    protocol_raw = _write_protocol(protocol, _protocol_body(**authorities["hashes"]))
    package_root = tmp_path / "package-a"
    package_root.mkdir()
    (package_root / "source.py").write_bytes(b"print(1)\n")
    manifest = build_package(
        "CONSTRUCTION_A",
        package_root,
        [{"path": "source.py", "class": "SOURCE"}],
        [],
    )
    manifest_path = tmp_path / "package-a-manifest.json"
    output_manifest_path = tmp_path / "phase-0-output-manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    write_canonical_json(output_manifest_path, manifest, exclusive=True)

    job_id = "phase-0-job"
    attempt = tmp_path / f"jobs/PHASE_0/{job_id}/1"
    intent = {
        "job_id": job_id,
        "protocol_sha256": hashlib.sha256(protocol_raw).hexdigest(),
        "phase": "PHASE_0",
        "argv": ["python3", "-c", "print(1)"],
        "cwd_identity": "fixture-root",
        "environment_sha256": "b" * 64,
        "input_sha256": ["c" * 64],
        "seed": None,
        "timeout_seconds": 30,
        "attempt": 1,
        "object_type": "PREFLIGHT",
        "object_id": "phase-0",
        "mr_id": "not-applicable",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": "phase-0-input",
        "repetition_id": 1,
        "environment_id": "env-1",
        "job_role": "PRIMARY_CONTROLLED",
    }
    create_intent(attempt, intent)
    write_result(
        attempt,
        {
            "job_id": job_id,
            "attempt": 1,
            "status": "PASS",
            "exit_code": 0,
            "stdout_sha256": "d" * 64,
            "stderr_sha256": "e" * 64,
            "duration_seconds": 0.25,
            "failure_code": "",
            "scientific_outcome": None,
            "call_trace_sha256": None,
            "call_trace_identity": None,
        },
    )
    events = reconstruct_attempt_events(tmp_path / "jobs")
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(
        b"".join(
            json.dumps(event, sort_keys=True, separators=(",", ":")).encode() + b"\n"
            for event in events
        )
    )
    expected_jobs_path = tmp_path / "phase-0-expected-jobs.json"
    write_canonical_json(expected_jobs_path, [job_id], exclusive=True)
    receipt = close_phase(
        "PHASE_0",
        hashlib.sha256(protocol_raw).hexdigest(),
        [job_id],
        ledger,
        manifest["artifact_sha256"],
    )
    receipt_path = tmp_path / "phase-0-receipt.json"
    write_canonical_json(receipt_path, receipt, exclusive=True)
    claims_path = tmp_path / "claims.json"
    write_canonical_json(
        claims_path,
        _blocked_claim_ledger(
            "authority-rq_spec_sha256.bin",
            "authority-claim_ceiling_sha256.bin",
            "protocol.json",
        ),
        exclusive=True,
    )
    body = {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V1",
        "phase_coverage": ["PHASE_0"],
        "protocol": _indexed_reference(tmp_path, protocol),
        "protocol_artifacts": {
            field: _indexed_reference(tmp_path, authorities["artifacts"][field])
            for field in _PROTOCOL_ARTIFACT_FIELDS
        },
        "adapter_registries": [
            _indexed_reference(tmp_path, authorities["adapter_registry_path"])
        ],
        "input_generator_registries": [
            _indexed_reference(tmp_path, authorities["generator_registry_path"])
        ],
        "subjects": [],
        "packages": [
            {
                "phase": "PHASE_0",
                "input_role": "A",
                "root": package_root.relative_to(tmp_path).as_posix(),
                "manifest": _indexed_reference(tmp_path, manifest_path),
            }
        ],
        "mr_chain": {},
        "job_root": "jobs",
        "ledger": _indexed_reference(tmp_path, ledger),
        "phase_receipts": [
            {
                "phase": "PHASE_0",
                "receipt": _indexed_reference(tmp_path, receipt_path),
                "expected_jobs": _indexed_reference(tmp_path, expected_jobs_path),
                "output_manifest": _indexed_reference(tmp_path, output_manifest_path),
            }
        ],
        "p12": {},
        "claims": _indexed_reference(tmp_path, claims_path),
    }
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)
    return index_path


def _refresh_attempt_evidence(tmp_path: Path, index: dict) -> None:
    from p3_v3.run_records import close_phase, reconstruct_attempt_events

    events = reconstruct_attempt_events(tmp_path / index["job_root"])
    ledger_path = tmp_path / index["ledger"]["path"]
    ledger_path.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
    index["ledger"]["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    protocol_sha256 = index["protocol"]["sha256"]
    for entry in index["phase_receipts"]:
        expected_path = tmp_path / entry["expected_jobs"]["path"]
        output_path = tmp_path / entry["output_manifest"]["path"]
        expected = json.loads(expected_path.read_text())
        output = json.loads(output_path.read_text())
        receipt = close_phase(
            entry["phase"],
            protocol_sha256,
            expected,
            ledger_path,
            output["artifact_sha256"],
        )
        receipt_path = tmp_path / entry["receipt"]["path"]
        receipt_path.write_bytes(canonical_json_bytes(receipt))
        entry["receipt"]["sha256"] = hashlib.sha256(
            receipt_path.read_bytes()
        ).hexdigest()


def _complete_reconstructable_subject_index(tmp_path: Path) -> Path:
    from p3_v3.run_records import create_intent, write_result

    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    adapter_registry_path = tmp_path / index["adapter_registries"][0]["path"]
    generator_registry_path = tmp_path / index["input_generator_registries"][0]["path"]
    adapter_registry = validate_adapter_registry(
        json.loads(adapter_registry_path.read_text()), adapter_registry_path.parent
    )
    generator_registry = validate_input_generator_registry(
        json.loads(generator_registry_path.read_text()), generator_registry_path.parent
    )
    for cache in generator_registry_path.parent.rglob("__pycache__"):
        shutil.rmtree(cache)
    source_root = tmp_path / "indexed-subject-source"
    source_root.mkdir()
    fixture = json.loads((FIXTURE_ROOT / "python.json").read_text())
    for relative in fixture["source_files"]:
        source = source_root / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("def solve(value):\n    return value\n", encoding="utf-8")
    manifest_path = source_root / "adapter-python.json"
    write_canonical_json(manifest_path, fixture, exclusive=True)
    descriptor = {
        "ecosystem": "python",
        "manifest_path": manifest_path.name,
        "reverse": False,
    }
    source_record = {
        "normalized_source_tree_sha256": _source_tree_sha256(source_root),
        "build_descriptor_sha256": canonical_sha256(descriptor),
    }
    neutral = canonical_sha256({"fixture": "final-subject"})
    bridge_record = {
        "neutral_snapshot_id": neutral,
        "fixed_tree_commitment": "4" * 64,
        "normalized_source_tree_sha256": source_record[
            "normalized_source_tree_sha256"
        ],
        "source_archive_sha256": "5" * 64,
        "build_descriptor_sha256": source_record["build_descriptor_sha256"],
        "eligibility_reason": "fixture",
        "eligible_for_construct": True,
        "eligible_for_criterion": True,
    }
    discovery = run_adapter_discovery(
        source_root, descriptor, adapter_registry, "PYTHON_PEP517_V1"
    )
    frame = build_public_behavior_frame(source_record, discovery)
    workload = select_profiling_workload(frame, "S")
    profiling_results = _profiling_receipt(
        workload,
        source_record,
        neutral,
        discovery["implementation_source_sha256"],
    )
    material = derive_subject_material(
        {
            "neutral_snapshot_id": neutral,
            "source_root": str(source_root),
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": adapter_registry,
            "input_generator_registry": generator_registry,
            "profiling_results": profiling_results,
        },
        bridge_record,
    )
    validity = validate_common_inputs_on_fixed_source(
        material["common_inputs"],
        lambda row: row["status"],
        sites=[],
        contracts=[],
        profile={},
        frame_artifact_sha256=material["public_behavior_frame"]["artifact_sha256"],
    )

    trace_entries = []
    protocol_sha256 = index["protocol"]["sha256"]
    for ordinal, row in enumerate(profiling_results["results"], start=1):
        job_id = f"profile-{ordinal:02d}"
        trace_path = tmp_path / f"profile-trace-{ordinal:02d}.json"
        write_canonical_json(trace_path, row["call_trace"], exclusive=True)
        trace_sha256 = hashlib.sha256(trace_path.read_bytes()).hexdigest()
        trace_identity = canonical_sha256(
            {
                "job_id": job_id,
                "attempt": 1,
                "behavior_id": row["behavior_id"],
                "call_trace_sha256": trace_sha256,
                "domain": "P3-PROFILING-TRACE-v1",
            }
        )
        attempt = tmp_path / f"jobs/PHASE_1/{job_id}/1"
        create_intent(
            attempt,
            {
                "job_id": job_id,
                "protocol_sha256": protocol_sha256,
                "phase": "PHASE_1",
                "argv": row["argv"],
                "cwd_identity": material["controlled_subject_source_id"],
                "environment_sha256": row["environment_sha256"],
                "input_sha256": row["input_sha256"],
                "seed": None,
                "timeout_seconds": 30,
                "attempt": 1,
                "object_type": "PROFILING_BEHAVIOR",
                "object_id": row["behavior_id"],
                "mr_id": "not-applicable",
                "evaluation_input_class": "E_COMMON",
                "evaluation_input_id": material["common_inputs"]["rows"][0]["input_id"],
                "repetition_id": 1,
                "environment_id": "profile-env",
                "job_role": "PROFILING",
            },
        )
        write_result(
            attempt,
            {
                "job_id": job_id,
                "attempt": 1,
                "status": "PASS",
                "exit_code": row["exit_code"],
                "stdout_sha256": row["stdout_sha256"],
                "stderr_sha256": row["stderr_sha256"],
                "duration_seconds": 0.25,
                "failure_code": row["failure_code"],
                "scientific_outcome": None,
                "call_trace_sha256": trace_sha256,
                "call_trace_identity": trace_identity,
            },
        )
        trace_entries.append(
            {
                "job_id": job_id,
                "attempt": 1,
                "behavior_id": row["behavior_id"],
                "artifact": _indexed_reference(tmp_path, trace_path),
            }
        )

    artifacts = {
        "bridge_record": bridge_record,
        "source_record": source_record,
        "build_descriptor": descriptor,
        "adapter_discovery": material["adapter_discovery"],
        "source_scale": material["source_scale"],
        "public_frame": material["public_behavior_frame"],
        "profiling_workload": material["profiling_workload"],
        "profiling_results": profiling_results,
        "common_inputs": material["common_inputs"],
        "common_input_validity": validity,
        "technique_profile": material["technique_profile"],
        "sites": material["subject"]["sites"],
        "subject": material["subject"],
    }
    references = {}
    for name, artifact in artifacts.items():
        path = tmp_path / f"indexed-{name}.json"
        write_canonical_json(path, artifact, exclusive=True)
        references[name] = _indexed_reference(tmp_path, path)
    index["subjects"] = [
        {
            "phase": "PHASE_1",
            "controlled_subject_source_id": material["controlled_subject_source_id"],
            "controlled_subject_id": material["subject"]["controlled_subject_id"],
            "bridge_record": references["bridge_record"],
            "source_root": source_root.relative_to(tmp_path).as_posix(),
            "source_record": references["source_record"],
            "build_descriptor": references["build_descriptor"],
            "adapter_registry_sha256": adapter_registry["artifact_sha256"],
            "input_generator_registry_sha256": generator_registry["artifact_sha256"],
            "adapter_discovery": references["adapter_discovery"],
            "source_scale": references["source_scale"],
            "public_frame": references["public_frame"],
            "profiling_workload": references["profiling_workload"],
            "profiling_results": references["profiling_results"],
            "profiling_traces": trace_entries,
            "common_inputs": references["common_inputs"],
            "common_input_validity": references["common_input_validity"],
            "technique_profile": references["technique_profile"],
            "sites": references["sites"],
            "subject": references["subject"],
            "slot_artifacts": [],
        }
    ]
    expected_jobs = [entry["job_id"] for entry in trace_entries]
    expected_path = tmp_path / "phase-1-expected-jobs.json"
    write_canonical_json(expected_path, expected_jobs, exclusive=True)
    output_path = tmp_path / "phase-1-output.json"
    output_body = {
        "schema_version": "p3-phase-output-fixture-v1",
        "subject_sha256": canonical_sha256(material["subject"]),
    }
    write_canonical_json(
        output_path,
        {**output_body, "artifact_sha256": canonical_sha256(output_body)},
        exclusive=True,
    )
    receipt_path = tmp_path / "phase-1-receipt.json"
    write_canonical_json(receipt_path, {"pending": True}, exclusive=True)
    index["phase_coverage"] = ["PHASE_0", "PHASE_1"]
    index["phase_receipts"].append(
        {
            "phase": "PHASE_1",
            "receipt": _indexed_reference(tmp_path, receipt_path),
            "expected_jobs": _indexed_reference(tmp_path, expected_path),
            "output_manifest": _indexed_reference(tmp_path, output_path),
        }
    )
    for cache in [
        *adapter_registry_path.parent.rglob("__pycache__"),
        *generator_registry_path.parent.rglob("__pycache__"),
    ]:
        shutil.rmtree(cache)
    _refresh_attempt_evidence(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))
    return index_path


def test_evidence_index_reconstructs_a_complete_phase_zero_set(tmp_path):
    result = _run_evidence_index(_complete_phase_zero_evidence_index(tmp_path))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "status": "PASS",
        "index_sha256": hashlib.sha256(
            (tmp_path / "evidence-index.json").read_bytes()
        ).hexdigest(),
        "phase_coverage": ["PHASE_0"],
        "manifest_count": 1,
        "phase_receipt_count": 1,
        "slot_artifact_count": 0,
        "ledger_event_count": 2,
        "verified_subject_count": 0,
        "verified_p12_result_count": 0,
        "verified_claim_count": 7,
    }


def test_verify_evidence_reconstructs_every_indexed_subject(tmp_path):
    result = _run_evidence_index(_complete_reconstructable_subject_index(tmp_path))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["verified_subject_count"] == 1


def test_verify_evidence_rejects_legacy_subject_mixed_with_reconstructable(tmp_path):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text())
    legacy = {
        key: value
        for key, value in index["subjects"][0].items()
        if key
        in {
            "phase",
            "controlled_subject_source_id",
            "controlled_subject_id",
            "public_frame",
            "profiling_workload",
            "profiling_results",
            "common_inputs",
            "common_input_validity",
            "slot_artifacts",
        }
    }
    index["subjects"].append(legacy)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_role",
        "missing_trace_digest",
        "altered_trace_bytes",
        "cross_subject_swap",
        "stdout_only_forgery",
    ],
)
def test_verify_evidence_authenticates_profile_trace_to_terminal_attempt(
    tmp_path, mutation
):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text())
    trace_entry = index["subjects"][0]["profiling_traces"][0]
    attempt_root = tmp_path / f"jobs/PHASE_1/{trace_entry['job_id']}/1"
    intent_path = attempt_root / "intent.json"
    result_path = attempt_root / "result.json"
    intent = json.loads(intent_path.read_text())
    result_record = json.loads(result_path.read_text())
    if mutation == "wrong_role":
        intent["job_role"] = "PRIMARY_CONTROLLED"
    elif mutation == "missing_trace_digest":
        result_record["call_trace_sha256"] = None
    elif mutation == "altered_trace_bytes":
        trace_path = tmp_path / trace_entry["artifact"]["path"]
        trace = json.loads(trace_path.read_text())
        trace.append({"module": "forged.subject", "symbol": "forged"})
        trace_path.write_bytes(canonical_json_bytes(trace))
        trace_entry["artifact"]["sha256"] = hashlib.sha256(
            trace_path.read_bytes()
        ).hexdigest()
    elif mutation == "cross_subject_swap":
        intent["cwd_identity"] = "0" * 64
    else:
        result_record["stdout_sha256"] = result_record["call_trace_sha256"]
        result_record["call_trace_sha256"] = None
        result_record["call_trace_identity"] = None
    if mutation in {"wrong_role", "cross_subject_swap"}:
        intent_path.write_bytes(canonical_json_bytes(intent))
    if mutation in {"missing_trace_digest", "stdout_only_forgery"}:
        result_path.write_bytes(canonical_json_bytes(result_record))
    if mutation == "cross_subject_swap":
        _refresh_attempt_evidence(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] in {
        "E_PROFILE_TRACE_BINDING",
        "E_PROFILE_ATTEMPT_BINDING",
    }
    assert not result.stdout


def _complete_p12_evidence_index(tmp_path: Path) -> Path:
    from p3_v3.run_records import (
        create_intent,
        freeze_p12_denominator,
        recompute_p12_summary,
        write_result,
    )

    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    job = {
        "job_id": "p12-job-01",
        "object_type": "P12_FAULT",
        "object_id": "fault-01",
        "mr_id": "mr-01",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": "p12-common-01",
        "repetition_id": 1,
        "environment_id": "p12-env-01",
        "job_role": "P12",
        "weight": 1,
    }
    denominator = freeze_p12_denominator(["fault-01"], [job])
    intent = {
        key: value for key, value in job.items() if key != "weight"
    } | {
        "protocol_sha256": index["protocol"]["sha256"],
        "phase": "PHASE_7",
        "argv": ["p12-runner", "fault-01"],
        "cwd_identity": "p12-fixture-root",
        "environment_sha256": "8" * 64,
        "input_sha256": ["9" * 64],
        "seed": None,
        "timeout_seconds": 30,
        "attempt": 1,
    }
    attempt = tmp_path / "jobs/PHASE_7/p12-job-01/1"
    create_intent(attempt, intent)
    result_record = {
        "job_id": job["job_id"],
        "attempt": 1,
        "status": "PASS",
        "exit_code": 0,
        "stdout_sha256": "a" * 64,
        "stderr_sha256": "b" * 64,
        "duration_seconds": 0.25,
        "failure_code": "",
        "scientific_outcome": "MR_SATISFIED",
        "call_trace_sha256": None,
        "call_trace_identity": None,
    }
    write_result(attempt, result_record)
    terminal = [{"intent": intent, "result": result_record}]
    result_rows = [
        {
            "job_id": job["job_id"],
            "scientific_outcome": result_record["scientific_outcome"],
        }
    ]
    summary = recompute_p12_summary(denominator, terminal)
    p12_paths = {}
    for name, artifact in {
        "denominator": denominator,
        "result_rows": result_rows,
        "summary": summary,
    }.items():
        path = tmp_path / f"p12-{name}.json"
        write_canonical_json(path, artifact, exclusive=True)
        p12_paths[name] = path
    expected_path = tmp_path / "phase-7-expected-jobs.json"
    write_canonical_json(expected_path, [job["job_id"]], exclusive=True)
    output_path = tmp_path / "phase-7-output.json"
    output_body = {
        "schema_version": "p3-phase-output-fixture-v1",
        "denominator_sha256": denominator["artifact_sha256"],
    }
    write_canonical_json(
        output_path,
        {**output_body, "artifact_sha256": canonical_sha256(output_body)},
        exclusive=True,
    )
    receipt_path = tmp_path / "phase-7-receipt.json"
    write_canonical_json(receipt_path, {"pending": True}, exclusive=True)
    index["phase_coverage"] = ["PHASE_0", "PHASE_7"]
    index["phase_receipts"].append(
        {
            "phase": "PHASE_7",
            "receipt": _indexed_reference(tmp_path, receipt_path),
            "expected_jobs": _indexed_reference(tmp_path, expected_path),
            "output_manifest": _indexed_reference(tmp_path, output_path),
        }
    )
    index["p12"] = {
        name: _indexed_reference(tmp_path, path) for name, path in p12_paths.items()
    }
    _refresh_attempt_evidence(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))
    return index_path


def test_verify_evidence_rebuilds_p12_rows_and_summary_from_terminal_attempts(tmp_path):
    result = _run_evidence_index(_complete_p12_evidence_index(tmp_path))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["verified_p12_result_count"] == 1


@pytest.mark.parametrize(
    ("field", "expected_code"),
    [("result_rows", "E_P12_RESULT_ROWS"), ("summary", "E_P12_SUMMARY")],
)
def test_verify_evidence_rejects_rehashed_p12_declarations(
    tmp_path, field, expected_code
):
    index_path = _complete_p12_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    reference = index["p12"][field]
    path = tmp_path / reference["path"]
    artifact = json.loads(path.read_text())
    if field == "result_rows":
        artifact[0]["scientific_outcome"] = "MR_VIOLATION"
    else:
        artifact["lower_numerator"] = 1
        body = {
            key: value for key, value in artifact.items() if key != "artifact_sha256"
        }
        artifact["artifact_sha256"] = canonical_sha256(body)
    path.write_bytes(canonical_json_bytes(artifact))
    reference["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == expected_code
    assert not result.stdout


@pytest.mark.parametrize(
    "field",
    [
        *_PROTOCOL_ARTIFACT_FIELDS,
        "adapter_registry_sha256",
        "input_generator_registry_sha256",
    ],
)
def test_protocol_binding_rejects_every_rehashed_authority_byte(tmp_path, field):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    if field == "adapter_registry_sha256":
        reference = index["adapter_registries"][0]
    elif field == "input_generator_registry_sha256":
        reference = index["input_generator_registries"][0]
    else:
        reference = index["protocol_artifacts"][field]
    artifact_path = tmp_path / reference["path"]
    artifact_path.write_bytes(artifact_path.read_bytes() + b"forged\n")
    reference["sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] in {
        "E_PROTOCOL_BINDING",
        "E_ADAPTER_REGISTRY_HASH",
        "E_GENERATOR_REGISTRY_HASH",
        "E_NONCANONICAL_JSON",
    }


@pytest.mark.parametrize("collection", ["adapter_registries", "input_generator_registries"])
def test_protocol_binding_rejects_omitted_mandatory_registry(tmp_path, collection):
    body = _empty_evidence_index_body(tmp_path)
    body[collection] = []
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_BINDING"


@pytest.mark.parametrize("collection", ["adapter_registries", "input_generator_registries"])
def test_protocol_binding_requires_exactly_one_registry_authority(tmp_path, collection):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    source = tmp_path / index[collection][0]["path"]
    duplicate = tmp_path / f"duplicate-{collection}.json"
    duplicate.write_bytes(source.read_bytes())
    index[collection].append(_indexed_reference(tmp_path, duplicate))
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_BINDING"


def test_mapping_free_yaml_claim_ceiling_fails_closed(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    authority_ref = index["protocol_artifacts"]["claim_ceiling_sha256"]
    authority_path = tmp_path / authority_ref["path"]
    authority_path.write_text("claims_initial_status: blocked\n", encoding="utf-8")
    authority_ref["sha256"] = hashlib.sha256(authority_path.read_bytes()).hexdigest()
    protocol_path = tmp_path / index["protocol"]["path"]
    protocol = json.loads(protocol_path.read_text())
    protocol["claim_ceiling_sha256"] = authority_ref["sha256"]
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    protocol_path.write_bytes(canonical_json_bytes(protocol))
    index["protocol"]["sha256"] = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    index_body = {
        key: value for key, value in index.items() if key != "artifact_sha256"
    }
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_JSON"
    assert not result.stdout


@pytest.mark.parametrize("field", _PROTOCOL_ARTIFACT_FIELDS)
def test_protocol_binding_rejects_omitted_mandatory_policy(tmp_path, field):
    body = _empty_evidence_index_body(tmp_path)
    del body["protocol_artifacts"][field]
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


@pytest.mark.parametrize(
    "mutation",
    ["unindexed", "supported", "result_prose", "missing", "extra", "renamed", "rq_swap"],
)
def test_claim_ledger_is_fail_closed_in_final_verification(tmp_path, mutation):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    claims_path = tmp_path / index["claims"]["path"]
    claims = json.loads(claims_path.read_text())
    claim = claims["claims"][0]
    if mutation == "unindexed":
        claim["evidence_references"] = ["not-indexed.json"]
    elif mutation == "supported":
        claim["status"] = "supported"
    else:
        if mutation == "result_prose":
            claim["result_prose"] = "The results support the claim."
        elif mutation == "missing":
            claims["claims"].pop()
        elif mutation == "extra":
            extra = json.loads(json.dumps(claims["claims"][-1]))
            extra["claim_id"] = "C8_FORGED"
            extra_body = {
                key: value for key, value in extra.items() if key != "artifact_sha256"
            }
            extra["artifact_sha256"] = canonical_sha256(extra_body)
            claims["claims"].append(extra)
        elif mutation == "renamed":
            claim["claim_id"] = "C1_RENAMED"
        else:
            claim["rqs"] = ["RQ3"]
    if mutation not in {"missing", "extra"}:
        claim_body = {
            key: value for key, value in claim.items() if key != "artifact_sha256"
        }
        claim["artifact_sha256"] = canonical_sha256(claim_body)
    claims_body = {
        key: value for key, value in claims.items() if key != "artifact_sha256"
    }
    claims["artifact_sha256"] = canonical_sha256(claims_body)
    claims_path.write_bytes(
        json.dumps(claims, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    index["claims"]["sha256"] = hashlib.sha256(claims_path.read_bytes()).hexdigest()
    index_body = {
        key: value for key, value in index.items() if key != "artifact_sha256"
    }
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] in {
        "E_CLAIM_EVIDENCE",
        "E_CLAIM_STATUS",
        "E_CLAIM_SET",
        "E_SCHEMA_KEYS",
    }
    assert not result.stdout


def test_evidence_index_rejects_unindexed_attempt_file(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    (tmp_path / "jobs/PHASE_0/phase-0-job/1/unindexed.txt").write_text("x")

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_ATTEMPT_TREE"


def test_evidence_index_rejects_unindexed_file_outside_declared_roots(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    (tmp_path / "unindexed-root.txt").write_text("forged", encoding="utf-8")

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_INDEX_UNINDEXED"


def test_evidence_index_rejects_symlink_in_indexed_path_ancestor(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    claims_path = tmp_path / index["claims"]["path"]
    outside = tmp_path / "outside"
    outside.mkdir()
    os.rename(claims_path, outside / "claims.json")
    (tmp_path / "linked").symlink_to(outside, target_is_directory=True)
    index["claims"] = {
        "path": "linked/claims.json",
        "sha256": hashlib.sha256((outside / "claims.json").read_bytes()).hexdigest(),
    }
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_INDEX_PATH"


def test_evidence_index_rejects_duplicate_phase_receipt(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    duplicate = {"phase": "PHASE_0"}
    for field in ("receipt", "expected_jobs", "output_manifest"):
        source = tmp_path / index["phase_receipts"][0][field]["path"]
        target = tmp_path / f"duplicate-{field}.json"
        target.write_bytes(source.read_bytes())
        duplicate[field] = _indexed_reference(tmp_path, target)
    index["phase_receipts"].append(duplicate)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_INDEX_COVERAGE"


def test_evidence_index_rejects_rebuilt_attempts_bound_to_another_protocol(tmp_path):
    from p3_v3.run_records import close_phase, reconstruct_attempt_events

    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    intent_path = tmp_path / "jobs/PHASE_0/phase-0-job/1/intent.json"
    intent = json.loads(intent_path.read_text())
    intent["protocol_sha256"] = "0" * 64
    intent_path.write_bytes(
        json.dumps(intent, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    events = reconstruct_attempt_events(tmp_path / "jobs")
    ledger_path = tmp_path / index["ledger"]["path"]
    ledger_path.write_bytes(
        b"".join(
            json.dumps(event, sort_keys=True, separators=(",", ":")).encode() + b"\n"
            for event in events
        )
    )
    index["ledger"]["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    receipt_entry = index["phase_receipts"][0]
    output_manifest = json.loads(
        (tmp_path / receipt_entry["output_manifest"]["path"]).read_text()
    )
    receipt = close_phase(
        "PHASE_0",
        "0" * 64,
        ["phase-0-job"],
        ledger_path,
        output_manifest["artifact_sha256"],
    )
    receipt_path = tmp_path / receipt_entry["receipt"]["path"]
    receipt_path.write_bytes(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    receipt_entry["receipt"]["sha256"] = hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_BINDING"


def _phase_zero_index_with_slots(tmp_path: Path, slots: list[dict]) -> Path:
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    source_id = "21" * 32
    rows = []
    for ordinal in range(1, 31):
        seed_digest = canonical_sha256(
            {
                "domain": "P3-E-COMMON-SEED-v1",
                "controlled_subject_source_id": source_id,
                "ordinal": ordinal,
            }
        )
        seed = int.from_bytes(bytes.fromhex(seed_digest)[:8], "big")
        identity = {
            "controlled_subject_source_id": source_id,
            "ordinal": ordinal,
            "generator_id": None,
            "schema_selection_key": None,
            "raw_schema_sha256": None,
            "schema_provenance_path": None,
            "schema_provenance_span_or_key": None,
            "generator_source_sha256": None,
            "raw_payload_sha256": None,
            "status": "COMMON_INPUT_UNAVAILABLE",
            "failure_code": "COMMON_INPUT_UNAVAILABLE",
            "domain": "P3-E-COMMON-INPUT-v1",
        }
        rows.append(
            {
                "ordinal": ordinal,
                "seed": seed,
                "generator_id": None,
                "schema_kind": None,
                "schema_selection_key": None,
                "raw_schema_sha256": None,
                "schema_provenance_path": None,
                "schema_provenance_span_or_key": None,
                "generator_source_sha256": None,
                "status": "COMMON_INPUT_UNAVAILABLE",
                "failure_code": "COMMON_INPUT_UNAVAILABLE",
                "envelope": None,
                "raw_payload_sha256": None,
                "input_id": canonical_sha256(identity),
            }
        )
    frame_body = {
        "schema_version": "p3-public-behavior-frame-v1",
        "controlled_subject_source_id": source_id,
        "rows": [],
        "public_schemas": [],
    }
    frame = {**frame_body, "artifact_sha256": canonical_sha256(frame_body)}
    workload = select_profiling_workload(frame, "S")
    common_body = {
        "schema_version": "p3-evaluation-inputs-common-v1",
        "controlled_subject_source_id": source_id,
        "eligible_schema_count": 0,
        "rows": rows,
    }
    common = {**common_body, "artifact_sha256": canonical_sha256(common_body)}
    validity_body = {
        "schema_version": "p3-common-input-validity-v1",
        "controlled_subject_source_id": source_id,
        "inventory_artifact_sha256": common["artifact_sha256"],
        "rows": [
            {
                key: row[key]
                for key in (
                    "ordinal",
                    "input_id",
                    "raw_payload_sha256",
                    "envelope",
                    "generator_id",
                    "schema_kind",
                    "schema_selection_key",
                    "raw_schema_sha256",
                    "seed",
                    "status",
                    "failure_code",
                )
            }
            for row in rows
        ],
        "sites": [],
        "contracts": [],
        "profile": {},
        "frame_artifact_sha256": frame["artifact_sha256"],
    }
    validity = {**validity_body, "artifact_sha256": canonical_sha256(validity_body)}
    artifacts = {
        "public-frame.json": frame,
        "workload.json": workload,
        "profiling-results.json": {"status": "NOT_RUN"},
        "common.json": common,
        "validity.json": validity,
    }
    for name, artifact in artifacts.items():
        write_canonical_json(tmp_path / name, artifact, exclusive=True)
    slot_refs = []
    for index, slot in enumerate(slots):
        path = tmp_path / f"slot-{index}.json"
        write_canonical_json(path, slot, exclusive=True)
        slot_refs.append(
            {
                "slot_id": slot["slot_id"],
                "controlled_subject_id": "22" * 32,
                "artifact": _indexed_reference(tmp_path, path),
            }
        )
    index = json.loads(index_path.read_text())
    index["subjects"] = [
        {
            "phase": "PHASE_0",
            "controlled_subject_source_id": source_id,
            "controlled_subject_id": "22" * 32,
            "public_frame": _indexed_reference(
                tmp_path, tmp_path / "public-frame.json"
            ),
            "profiling_workload": _indexed_reference(
                tmp_path, tmp_path / "workload.json"
            ),
            "profiling_results": _indexed_reference(
                tmp_path, tmp_path / "profiling-results.json"
            ),
            "common_inputs": _indexed_reference(tmp_path, tmp_path / "common.json"),
            "common_input_validity": _indexed_reference(
                tmp_path, tmp_path / "validity.json"
            ),
            "slot_artifacts": slot_refs,
        }
    ]
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    return index_path


def _reconstructable_index_with_slots(tmp_path: Path, slots: list[dict]) -> Path:
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text())
    controlled_subject_id = index["subjects"][0]["controlled_subject_id"]
    slot_refs = []
    for ordinal, slot in enumerate(slots):
        path = tmp_path / f"slot-{ordinal}.json"
        write_canonical_json(path, slot, exclusive=True)
        slot_refs.append(
            {
                "slot_id": slot["slot_id"],
                "controlled_subject_id": controlled_subject_id,
                "artifact": _indexed_reference(tmp_path, path),
            }
        )
    index["subjects"][0]["slot_artifacts"] = slot_refs
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))
    return index_path


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("coordinate", "E_SLOT_COORDINATE"),
        ("input_role", "E_SLOT_INPUT_ROLE"),
        ("unknown_common", "E_SLOT_INPUT_ROLE"),
    ],
)
def test_evidence_index_rejects_slot_coordinate_or_input_role_drift(
    tmp_path, mutation, expected_code
):
    slot_id = "61" * 32
    not_applicable = {
        "slot_id": slot_id,
        "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
        "contract": None,
        "e_contract": None,
        "patch": None,
        "certification_witness": None,
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    if mutation == "coordinate":
        slots = [not_applicable, dict(not_applicable)]
    else:
        common_id = "71" * 32
        contract_id = common_id if mutation == "input_role" else "75" * 32
        slots = [
            {
                "slot_id": slot_id,
                "chronology": [
                    "SITE_FROZEN",
                    "CONTRACT_FROZEN",
                    "E_CONTRACT_FROZEN",
                    "PATCH_FROZEN",
                    "CERTIFICATION_WITNESS_SELECTED",
                    "TERMINAL_STATE",
                ],
                "contract": {"contract_id": "72" * 32},
                "e_contract": {"rows": []},
                "patch": {"patch_id": "73" * 32},
                "certification_witness": {"witness_id": "74" * 32},
                "e_common_input_ids": [common_id],
                "e_contract_input_ids": [contract_id],
            }
        ]
    result = _run_evidence_index(_reconstructable_index_with_slots(tmp_path, slots))

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == expected_code


@pytest.mark.parametrize("mutation", ["contract_rows", "hidden_overlap"])
def test_evidence_index_binds_slot_role_lists_to_real_inventories(tmp_path, mutation):
    slot_id = "61" * 32
    slot = {
        "slot_id": slot_id,
        "chronology": [
            "SITE_FROZEN",
            "CONTRACT_FROZEN",
            "E_CONTRACT_FROZEN",
            "PATCH_FROZEN",
            "CERTIFICATION_WITNESS_SELECTED",
            "TERMINAL_STATE",
        ],
        "contract": {"contract_id": "72" * 32},
        "e_contract": {"rows": [{"input_id": "75" * 32}]},
        "patch": {"patch_id": "73" * 32},
        "certification_witness": {"witness_id": "74" * 32},
        "e_common_input_ids": [],
        "e_contract_input_ids": ["76" * 32],
    }
    index_path = _reconstructable_index_with_slots(tmp_path, [slot])
    index = json.loads(index_path.read_text())
    common = json.loads(
        (tmp_path / index["subjects"][0]["common_inputs"]["path"]).read_text()
    )
    common_id = common["rows"][0]["input_id"]
    slot_path = tmp_path / index["subjects"][0]["slot_artifacts"][0]["artifact"]["path"]
    material = json.loads(slot_path.read_text())
    if mutation == "contract_rows":
        material["e_contract_input_ids"] = ["76" * 32]
    else:
        material["e_common_input_ids"] = [common_id]
        material["e_contract"]["rows"] = [{"input_id": common_id}]
        material["e_contract_input_ids"] = ["76" * 32]
    slot_path.write_bytes(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    index["subjects"][0]["slot_artifacts"][0]["artifact"]["sha256"] = hashlib.sha256(
        slot_path.read_bytes()
    ).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SLOT_INPUT_ROLE"


def test_forged_evidence_index_is_rejected_without_pass_receipt(tmp_path):
    """Removing reconstruction cannot turn self-consistent declarations into PASS."""

    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body())
    claims = _blocked_claim_ledger("protocol.json")
    claims_path = tmp_path / "claims.json"
    write_canonical_json(claims_path, claims, exclusive=True)

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")

    common_body = {
        "schema_version": "p3-evaluation-inputs-common-v1",
        "controlled_subject_source_id": "21" * 32,
        "eligible_schema_count": 0,
        "rows": [{"status": "FABRICATED"} for _ in range(30)],
    }
    common = {**common_body, "artifact_sha256": canonical_sha256(common_body)}
    common_path = tmp_path / "common.json"
    write_canonical_json(common_path, common, exclusive=True)

    denominator_body = {
        "schema_version": "p3-p12-denominator-v1",
        "p12_paired_ids": [],
        "jobs": [],
        "planned_count": 0,
        "job_inventory_sha256": canonical_sha256([]),
        "paired_ids_sha256": canonical_sha256([]),
    }
    denominator = {
        **denominator_body,
        "artifact_sha256": canonical_sha256(denominator_body),
    }
    denom_path = tmp_path / "denominator.json"
    write_canonical_json(denom_path, denominator, exclusive=True)
    summary_body = {
        "planned_count": 0,
        "denominator_sha256": denominator["artifact_sha256"],
        "status": "FABRICATED",
    }
    summary = {**summary_body, "artifact_sha256": canonical_sha256(summary_body)}
    summary_path = tmp_path / "summary.json"
    write_canonical_json(summary_path, summary, exclusive=True)

    result_rows_path = tmp_path / "p12-results.json"
    write_canonical_json(result_rows_path, [], exclusive=True)
    validity_path = tmp_path / "common-validity.json"
    write_canonical_json(validity_path, {"status": "FABRICATED"}, exclusive=True)
    public_frame_path = tmp_path / "public-frame.json"
    write_canonical_json(public_frame_path, {"status": "FABRICATED"}, exclusive=True)
    workload_path = tmp_path / "profiling-workload.json"
    write_canonical_json(workload_path, {"status": "FABRICATED"}, exclusive=True)
    profiling_path = tmp_path / "profiling-results.json"
    write_canonical_json(profiling_path, {"status": "FABRICATED"}, exclusive=True)

    index_body = {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V1",
        "phase_coverage": ["PHASE_1"],
        "protocol": _indexed_reference(tmp_path, protocol),
        "adapter_registries": [],
        "input_generator_registries": [],
        "subjects": [
            {
                "phase": "PHASE_1",
                "controlled_subject_source_id": "21" * 32,
                "controlled_subject_id": "22" * 32,
                "public_frame": _indexed_reference(tmp_path, public_frame_path),
                "profiling_workload": _indexed_reference(tmp_path, workload_path),
                "profiling_results": _indexed_reference(tmp_path, profiling_path),
                "common_inputs": _indexed_reference(tmp_path, common_path),
                "common_input_validity": _indexed_reference(tmp_path, validity_path),
                "slot_artifacts": [],
            }
        ],
        "packages": [],
        "mr_chain": {},
        "job_root": "jobs",
        "ledger": _indexed_reference(tmp_path, ledger),
        "phase_receipts": [],
        "p12": {
            "denominator": _indexed_reference(tmp_path, denom_path),
            "result_rows": _indexed_reference(tmp_path, result_rows_path),
            "summary": _indexed_reference(tmp_path, summary_path),
        },
        "claims": _indexed_reference(tmp_path, claims_path),
    }
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, index_body)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(index_path),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode != 0
    assert not result.stdout
    assert b'"status":"PASS"' not in result.stdout.encode()


def test_verify_evidence_accepts_only_one_index_argument():
    result = subprocess.run(
        ["python3", str(CLI), "verify-evidence", "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    assert "--index" in result.stdout
    for legacy in (
        "--protocol",
        "--manifest",
        "--ledger",
        "--phase-receipt",
        "--slot-artifacts",
        "--common-inputs",
        "--denominator",
        "--p12-summary",
        "--claims",
    ):
        assert legacy not in result.stdout
