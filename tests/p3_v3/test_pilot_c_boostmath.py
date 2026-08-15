from __future__ import annotations

from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, read_canonical_json
from p3_v3.pilot_c_boostmath import (
    CERTIFICATION_TERMINAL_STATES,
    FROZEN_LINEAGE,
    apply_line_patch,
    build_claim_ledger,
    build_comparison,
    build_contract,
    build_independent_probe_source,
    evaluate_mono_oracle,
    normalize_probe_record,
    parse_probe_stdout,
    rebuild_comparison,
    require_fresh_close_before_historical,
    validate_atomic_row,
    validate_fixture_disclosure,
    write_frozen_contract,
)


def test_lineage_fields_are_exactly_the_frozen_pilot_identity():
    assert FROZEN_LINEAGE == {
        "study_role": "PILOT_ONLY",
        "execution_mode": "RETROSPECTIVE_PIPELINE_REPLAY",
        "confirmatory_eligible": False,
        "selection_outcome_independent": False,
        "excluded_from_35_subject_freeze": True,
        "claim_ceiling": "observed_single_case",
    }


def test_contract_freeze_contains_required_fields_and_is_immutable(tmp_path):
    contract = build_contract()
    assert contract["contract_id"] == "PILOT-C-BOOSTMATH-001-MONO-v1"
    assert contract["semantic_contract_family"] == "MONO"
    assert contract["subject"] == "boost::math::quantile(skew_normal_distribution, p)"
    assert contract["parameters"]["location"] == 573.39724735636185
    assert contract["parameters"]["scale"] == 77
    assert contract["parameters"]["shape"] == 4
    assert contract["oracle_kind"] == "dense_neighborhood_sweep"
    assert contract["retrospective_source_preexists"] is True
    assert contract["confirmatory_eligible"] is False
    assert contract["repetitions"] == 3
    assert "grid" in contract
    assert "tolerance" in contract
    assert "witness_order" in contract
    assert "terminal_states" in contract
    path = tmp_path / "contract.json"
    written = write_frozen_contract(path, contract)
    assert written["contract_sha256"] == canonical_sha256(
        {key: value for key, value in written.items() if key != "contract_sha256"}
    )
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_frozen_contract(path, contract)


def test_independent_probe_source_does_not_reuse_mr_verdict_code():
    source = build_independent_probe_source(build_contract())
    forbidden = (
        "MR SATISFIED",
        "MR VIOLATION",
        "### B1-1",
        "### B1-2",
        "### B1-3",
        "### B2-1",
        "### B2-4",
        "### B2-8",
        "### A1-a",
        "### A1-b",
        "verdict(",
    )
    for token in forbidden:
        assert token not in source


def test_mono_oracle_uses_frozen_tolerance_and_witness_order():
    contract = build_contract()
    increasing = [
        {"p": 0.1, "status": "VALUE", "value": 1.0},
        {"p": 0.2, "status": "VALUE", "value": 1.5},
        {"p": 0.3, "status": "VALUE", "value": 2.0},
    ]
    assert evaluate_mono_oracle(increasing, contract) == "SATISFIED"
    decreasing = [
        {"p": 0.1, "status": "VALUE", "value": 2.0},
        {"p": 0.2, "status": "VALUE", "value": 1.0},
    ]
    assert evaluate_mono_oracle(decreasing, contract) == "VIOLATED"
    nonfinite = [{"p": 0.1, "status": "NONFINITE", "value": None}]
    assert evaluate_mono_oracle(nonfinite, contract) == "VIOLATED"


def test_probe_parser_normalizes_values_or_stable_error_states():
    stdout = (
        "PROBE_V1\n"
        "p=0.10000000000000001 q=1.25\n"
        "p=0.20000000000000001 ERROR=EXCEPTION\n"
        "TERMINAL=OK\n"
    )
    records = parse_probe_stdout(stdout)
    assert [normalize_probe_record(item) for item in records] == [
        {"p": 0.1, "status": "VALUE", "value": 1.25},
        {"p": 0.2, "status": "EXCEPTION", "value": None},
    ]


def test_apply_line_patch_changes_only_the_declared_target(tmp_path):
    source = tmp_path / "roots.hpp"
    source.write_text("keep\n      if (0 == f0)\nkeep-tail\n", encoding="utf-8")
    dest = tmp_path / "mutated.hpp"
    result = apply_line_patch(
        source,
        dest,
        line=2,
        original="      if (0 == f0)\n",
        mutated="      if (0 != f0)\n",
    )
    assert dest.read_text(encoding="utf-8") == "keep\n      if (0 != f0)\nkeep-tail\n"
    assert result["changed_lines"] == [2]
    with pytest.raises(EvidenceError, match="E_PATCH_SCOPE"):
        apply_line_patch(
            source,
            tmp_path / "other.hpp",
            line=2,
            original="      if (0 != f0)\n",
            mutated="      if (0 == f0)\n",
        )


def test_fixture_disclosure_rejects_formal_denominator_language():
    disclosure = {
        "mutant_id": "roots_m037",
        "construction_mechanism": "LEGACY_SDL",
        "role": "PILOT_DIAGNOSTIC_CONTRACT_MUTANT",
        "source": "P12 historical manifest",
        "selection": "outcome-informed",
        "outcome_blind_generated": False,
        "contract_derived": False,
        "enters_formal_semantic_denominator": False,
        "enters_formal_syntactic_denominator": False,
        "substitute_on_failure": False,
    }
    validate_fixture_disclosure(disclosure)
    bad = dict(disclosure, outcome_blind_generated=True)
    with pytest.raises(EvidenceError, match="E_FIXTURE_DISCLOSURE"):
        validate_fixture_disclosure(bad)


def test_certification_terminal_states_are_the_closed_legal_set():
    assert CERTIFICATION_TERMINAL_STATES == {
        "CONFIRMED_NON_EQUIVALENT",
        "CERTIFIED_EQUIVALENT",
        "EQUIVALENCE_UNRESOLVED",
        "TRIGGER_UNEXERCISED",
        "INVALID_MUTANT",
        "DUPLICATE_MUTANT",
        "INFRASTRUCTURE_UNRESOLVED",
    }


def test_atomic_row_requires_the_frozen_bindings():
    row = {
        "run_id": "job-fixed-T1-r1",
        "object_id": "fixed-original",
        "object_role": "FIXED_ORIGINAL",
        "source_commit": "03ea9c8d7dff1083facd134c8f641e006b68fdae",
        "source_tree": "dc86f3259c84f68ac7c4e2be11a1ed8567011240",
        "patch_sha256": "a" * 64,
        "contract_sha256": "b" * 64,
        "mr_id": "T1",
        "mr_role": "REFERENCE_POSITIVE_CONTROL",
        "repetition": 1,
        "command": ["g++"],
        "environment_sha256": "c" * 64,
        "stdout_sha256": "d" * 64,
        "stderr_sha256": "e" * 64,
        "exit_code": 0,
        "runtime": 0.1,
        "terminal_state": "PASS",
    }
    validate_atomic_row(row)
    with pytest.raises(EvidenceError, match="E_ATOMIC_ROW"):
        validate_atomic_row({key: value for key, value in row.items() if key != "mr_id"})


def test_comparison_rebuilds_from_atomic_rows_only():
    rows = [
        {
            "run_id": "job-fixed-T1-r1",
            "object_id": "fixed-original",
            "object_role": "FIXED_ORIGINAL",
            "source_commit": "aa",
            "source_tree": "bb",
            "patch_sha256": "a" * 64,
            "contract_sha256": "b" * 64,
            "mr_id": "T1",
            "mr_role": "REFERENCE_POSITIVE_CONTROL",
            "repetition": 1,
            "command": ["t1"],
            "environment_sha256": "c" * 64,
            "stdout_sha256": "d" * 64,
            "stderr_sha256": "e" * 64,
            "exit_code": 0,
            "runtime": 0.2,
            "terminal_state": "PASS",
        },
        {
            "run_id": "job-m037-T1-r1",
            "object_id": "roots_m037",
            "object_role": "PILOT_DIAGNOSTIC_CONTRACT_MUTANT",
            "source_commit": "aa",
            "source_tree": "bb",
            "patch_sha256": "f" * 64,
            "contract_sha256": "b" * 64,
            "mr_id": "T1",
            "mr_role": "REFERENCE_POSITIVE_CONTROL",
            "repetition": 1,
            "command": ["t1"],
            "environment_sha256": "c" * 64,
            "stdout_sha256": "1" * 64,
            "stderr_sha256": "2" * 64,
            "exit_code": 1,
            "runtime": 0.2,
            "terminal_state": "VIOLATED",
        },
        {
            "run_id": "job-m003-T1-r1",
            "object_id": "roots_m003",
            "object_role": "PILOT_SYNTACTIC_COMPARATOR",
            "source_commit": "aa",
            "source_tree": "bb",
            "patch_sha256": "3" * 64,
            "contract_sha256": "b" * 64,
            "mr_id": "T1",
            "mr_role": "REFERENCE_POSITIVE_CONTROL",
            "repetition": 1,
            "command": ["t1"],
            "environment_sha256": "c" * 64,
            "stdout_sha256": "4" * 64,
            "stderr_sha256": "5" * 64,
            "exit_code": 0,
            "runtime": 0.2,
            "terminal_state": "PASS",
        },
    ]
    comparison = build_comparison(rows)
    rebuilt = rebuild_comparison(rows)
    assert rebuilt == comparison
    assert comparison["per_mr_difference"]["T1"]["roots_m037_vs_roots_m003"] is True
    forbidden = ("p-value", "significant", "superior", "generaliz", "mutation score")
    blob = str(comparison).lower()
    for token in forbidden:
        assert token not in blob


def test_historical_jsonl_is_blocked_until_fresh_artifacts_are_sealed(tmp_path):
    historical = tmp_path / "results-partial.jsonl"
    historical.write_text("{}\n", encoding="utf-8")
    with pytest.raises(EvidenceError, match="E_HISTORICAL_PREMATURE"):
        require_fresh_close_before_historical(
            historical,
            ledger_sha256=None,
            comparison_sha256=None,
        )
    digest = require_fresh_close_before_historical(
        historical,
        ledger_sha256="a" * 64,
        comparison_sha256="b" * 64,
    )
    assert len(digest) == 64


def test_claim_ledger_keeps_formal_claims_blocked_and_caps_pilot_claims():
    comparison = {
        "pipeline_complete": True,
        "observed_single_case_mr_difference": True,
        "artifact_sha256": "a" * 64,
    }
    ledger = build_claim_ledger(comparison)
    by_id = {claim["claim_id"]: claim for claim in ledger["claims"]}
    assert by_id["PILOT_C0_PIPELINE_EXECUTED"]["status"] in {"supported", "observed"}
    assert by_id["PILOT_C1_SINGLE_CASE_MR_DIFFERENCE"]["status"] == "observed"
    assert by_id["PILOT_C1_SINGLE_CASE_MR_DIFFERENCE"]["wording"].startswith(
        "In this retrospective pilot run"
    )
    for claim_id in (
        "C1_ARTIFACT_FIRST_SEMANTIC_MUTANT_PROTOCOL",
        "C2_CERTIFIED_MUTANTS_ACROSS_SCALES_TECHNIQUES",
        "C3_SEMANTIC_CONSTRUCT_DISTINCTNESS",
        "C4_FAMILY_AWARE_SMS_RESIDUAL_EXPLANATION",
        "C5_P12_CRITERION_INCREMENTAL_VALUE",
        "C6_UNIVERSAL_SUPERIORITY_CEILING",
        "C7_LANGUAGE_INDEPENDENT_AUTOMATION_CEILING",
        "C8_PROFILING_REPRESENTATIVENESS_CEILING",
        "SEMANTIC_MUTANT_SUPERIORITY",
        "CRITERION_VALIDITY",
        "THIRTY_FIVE_SUBJECT_EFFECT",
        "AUTOMATIC_GENERATION_VALIDITY",
        "OUTCOME_BLINDNESS",
    ):
        assert by_id[claim_id]["status"] == "blocked"
    empty = build_claim_ledger(
        {
            "pipeline_complete": False,
            "observed_single_case_mr_difference": False,
            "artifact_sha256": "b" * 64,
        }
    )
    empty_ids = {claim["claim_id"]: claim for claim in empty["claims"]}
    assert empty_ids["PILOT_C0_PIPELINE_EXECUTED"]["status"] == "blocked"
    assert empty_ids["PILOT_C1_SINGLE_CASE_MR_DIFFERENCE"]["status"] == "blocked"


def test_frozen_contract_file_is_canonical_json(tmp_path):
    path = tmp_path / "contract.json"
    write_frozen_contract(path, build_contract())
    loaded = read_canonical_json(path)
    assert loaded["contract_id"] == "PILOT-C-BOOSTMATH-001-MONO-v1"
