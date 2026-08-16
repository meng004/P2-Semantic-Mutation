from __future__ import annotations

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.packages import verify_package
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
