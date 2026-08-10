from __future__ import annotations

import copy
from fractions import Fraction

import pytest

import p3_v3.run_records as run_records_module
from p3_v3.artifacts import EvidenceError, canonical_json_bytes, canonical_sha256
from p3_v3.run_records import (
    INFRASTRUCTURE_RETRY_LIMIT,
    P12_OUTCOME_STATES,
    close_phase,
    create_intent,
    freeze_p12_denominator,
    reduce_attempts,
    summarize_p12_outcomes,
    verify_ledger,
    write_result,
)


def _intent(
    job_id="job-1",
    attempt=1,
    *,
    phase="PHASE-2",
    job_role="PRIMARY_CONTROLLED",
    evaluation_input_class="E_COMMON",
    object_type="SEMANTIC_MUTANT",
    object_id="mut-1",
    mr_id="mr-1",
    evaluation_input_id="e-common-0",
    repetition_id=1,
    environment_id="env-1",
):
    return {
        "job_id": job_id,
        "protocol_sha256": "a" * 64,
        "phase": phase,
        "argv": ["python3", "-c", "print(1)"],
        "cwd_identity": "fixture-root",
        "environment_sha256": "b" * 64,
        "input_sha256": ["c" * 64],
        "seed": None,
        "timeout_seconds": 30,
        "attempt": attempt,
        "object_type": object_type,
        "object_id": object_id,
        "mr_id": mr_id,
        "evaluation_input_class": evaluation_input_class,
        "evaluation_input_id": evaluation_input_id,
        "repetition_id": repetition_id,
        "environment_id": environment_id,
        "job_role": job_role,
    }


def _result(job_id="job-1", attempt=1, status="PASS", scientific_outcome=None):
    return {
        "job_id": job_id,
        "attempt": attempt,
        "status": status,
        "exit_code": 0 if status == "PASS" else 1,
        "stdout_sha256": "d" * 64,
        "stderr_sha256": "e" * 64,
        "duration_seconds": 0.25,
        "failure_code": "" if status == "PASS" else "E_SYNTHETIC",
        "scientific_outcome": scientific_outcome,
    }


def test_result_requires_existing_intent(tmp_path):
    with pytest.raises(EvidenceError, match="E_RESULT_WITHOUT_INTENT"):
        write_result(tmp_path / "jobs/job-1/1", _result())


def test_intent_and_result_are_exclusive(tmp_path):
    attempt = tmp_path / "jobs/job-1/1"
    create_intent(attempt, _intent())
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        create_intent(attempt, _intent())
    write_result(attempt, _result())
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_result(attempt, _result())


def test_result_identity_must_match_intent(tmp_path):
    attempt = tmp_path / "jobs/job-1/1"
    create_intent(attempt, _intent())
    with pytest.raises(EvidenceError, match="E_RESULT_IDENTITY"):
        write_result(attempt, _result(job_id="job-2"))


def test_reducer_retains_failed_attempt_before_success(tmp_path):
    jobs = tmp_path / "jobs"
    first = jobs / "job-1/1"
    second = jobs / "job-1/2"
    create_intent(first, _intent(attempt=1))
    write_result(first, _result(attempt=1, status="FAIL_INFRASTRUCTURE"))
    create_intent(second, _intent(attempt=2))
    write_result(second, _result(attempt=2))
    ledger = tmp_path / "ledger.jsonl"
    events = reduce_attempts(jobs, ledger)
    assert [(event["kind"], event["attempt"]) for event in events] == [
        ("INTENT", 1),
        ("RESULT", 1),
        ("INTENT", 2),
        ("RESULT", 2),
    ]
    verify_ledger(ledger)


def test_reducer_rejects_noncontiguous_or_scientific_retry(tmp_path):
    jobs = tmp_path / "jobs"
    gap = jobs / "job-1/2"
    create_intent(gap, _intent(attempt=2))
    write_result(gap, _result(attempt=2))
    with pytest.raises(EvidenceError, match="E_ATTEMPT_SEQUENCE"):
        reduce_attempts(jobs, tmp_path / "gap.jsonl")

    other_jobs = tmp_path / "other-jobs"
    first = other_jobs / "job-2/1"
    second = other_jobs / "job-2/2"
    create_intent(first, _intent(job_id="job-2", attempt=1))
    write_result(first, _result(job_id="job-2", attempt=1, status="FAIL_SCIENTIFIC"))
    create_intent(second, _intent(job_id="job-2", attempt=2))
    write_result(second, _result(job_id="job-2", attempt=2))
    with pytest.raises(EvidenceError, match="E_RETRY_POLICY"):
        reduce_attempts(other_jobs, tmp_path / "scientific-retry.jsonl")


_RETRY_IDENTITY_MUTATIONS = {
    "job_id": "job-other",
    "protocol_sha256": "9" * 64,
    "phase": "PHASE-3",
    "argv": ["python3", "-c", "print(2)"],
    "cwd_identity": "other-fixture-root",
    "environment_sha256": "8" * 64,
    "input_sha256": ["7" * 64],
    "seed": 17,
    "timeout_seconds": 31,
    "object_type": "P12_FAULT",
    "object_id": "mut-2",
    "mr_id": "mr-2",
    "evaluation_input_id": "e-common-1",
    "repetition_id": 2,
    "environment_id": "env-2",
    "job_role": "P12",
}


@pytest.mark.parametrize(
    ("field", "mutated_value"),
    _RETRY_IDENTITY_MUTATIONS.items(),
    ids=_RETRY_IDENTITY_MUTATIONS,
)
def test_retry_rejects_every_mutated_identity_field(
    tmp_path, field, mutated_value
):
    jobs = tmp_path / "jobs"
    first = jobs / "job-1/1"
    second = jobs / "job-1/2"
    create_intent(first, _intent(attempt=1))
    write_result(first, _result(attempt=1, status="FAIL_INFRASTRUCTURE"))

    retried = {**_intent(attempt=2), field: mutated_value}
    if field == "job_id":
        second.mkdir(parents=True)
        (second / "intent.json").write_bytes(canonical_json_bytes(retried))
    else:
        create_intent(second, retried)

    with pytest.raises(EvidenceError, match="E_RETRY_IDENTITY"):
        reduce_attempts(jobs, tmp_path / f"retry-{field}.jsonl")


def test_retry_invariant_validates_intent_and_removes_only_attempt():
    intent = _intent(attempt=2)
    invariant = run_records_module.retry_invariant(intent)
    assert invariant == {key: value for key, value in intent.items() if key != "attempt"}

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        run_records_module.retry_invariant(
            {**intent, "unbound_retry_field": "ignored-by-bug"}
        )


def test_retry_allows_three_total_attempts_but_rejects_fourth(tmp_path):
    jobs = tmp_path / "jobs"
    for attempt in range(1, 4):
        directory = jobs / f"job-1/{attempt}"
        create_intent(directory, _intent(attempt=attempt))
        write_result(
            directory,
            _result(attempt=attempt, status="FAIL_INFRASTRUCTURE"),
        )

    reduce_attempts(jobs, tmp_path / "three-attempts.jsonl")

    create_intent(jobs / "job-1/4", _intent(attempt=4))
    with pytest.raises(EvidenceError, match="E_RETRY_POLICY"):
        reduce_attempts(jobs, tmp_path / "four-attempts.jsonl")


def test_ledger_tampering_breaks_event_hash(tmp_path):
    jobs = tmp_path / "jobs"
    attempt = jobs / "job-1/1"
    create_intent(attempt, _intent())
    write_result(attempt, _result())
    ledger = tmp_path / "ledger.jsonl"
    events = reduce_attempts(jobs, ledger)
    changed = copy.deepcopy(events)
    changed[0]["job_id"] = "other"
    ledger.write_text("\n".join(__import__("json").dumps(x, sort_keys=True, separators=(",", ":")) for x in changed) + "\n")
    with pytest.raises(EvidenceError, match="E_LEDGER_EVENT_HASH"):
        verify_ledger(ledger)


def test_ledger_rejects_rehashed_non_digest_artifact_identity(tmp_path):
    jobs = tmp_path / "jobs"
    attempt = jobs / "job-1/1"
    create_intent(attempt, _intent())
    write_result(attempt, _result())
    ledger = tmp_path / "ledger.jsonl"
    events = reduce_attempts(jobs, ledger)
    changed = copy.deepcopy(events)
    changed[0]["artifact_sha256"] = "not-a-digest"
    body = {key: value for key, value in changed[0].items() if key != "event_sha256"}
    changed[0]["event_sha256"] = canonical_sha256(body)
    ledger.write_text(
        "\n".join(
            __import__("json").dumps(x, sort_keys=True, separators=(",", ":"))
            for x in changed
        )
        + "\n"
    )
    with pytest.raises(EvidenceError, match="E_SHA256"):
        verify_ledger(ledger)


def test_phase_close_rejects_pending_and_then_binds_complete_ledger(tmp_path):
    jobs = tmp_path / "jobs"
    attempt = jobs / "job-1/1"
    create_intent(attempt, _intent())
    pending_ledger = tmp_path / "pending.jsonl"
    reduce_attempts(jobs, pending_ledger)
    with pytest.raises(EvidenceError, match="E_PHASE_PENDING"):
        close_phase("PHASE-2", "a" * 64, ["job-1"], pending_ledger, "f" * 64)

    write_result(attempt, _result())
    ledger = tmp_path / "ledger.jsonl"
    reduce_attempts(jobs, ledger)
    receipt = close_phase("PHASE-2", "a" * 64, ["job-1"], ledger, "f" * 64)
    assert receipt["terminal_result_count"] == 1
    assert receipt["expected_job_count"] == 1
    assert len(receipt["ledger_raw_sha256"]) == 64


def test_phase_close_rejects_empty_phase_identity(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")
    with pytest.raises(EvidenceError, match="E_PHASE_ID"):
        close_phase("", "a" * 64, [], ledger, "f" * 64)


def test_primary_controlled_and_p12_jobs_require_e_common(tmp_path):
    controlled = tmp_path / "jobs/controlled/1"
    with pytest.raises(EvidenceError, match="E_JOB_ROLE_INPUT"):
        create_intent(
            controlled,
            _intent(
                job_id="controlled",
                job_role="PRIMARY_CONTROLLED",
                evaluation_input_class="E_CONTRACT",
            ),
        )

    p12 = tmp_path / "jobs/p12-job/1"
    with pytest.raises(EvidenceError, match="E_JOB_ROLE_INPUT"):
        create_intent(
            p12,
            _intent(
                job_id="p12-job",
                phase="PHASE-7",
                job_role="P12",
                object_type="P12_FAULT",
                object_id="fault-1",
                evaluation_input_class="E_CONTRACT",
            ),
        )

    create_intent(
        tmp_path / "jobs/ok-controlled/1",
        _intent(job_id="ok-controlled", job_role="PRIMARY_CONTROLLED"),
    )
    create_intent(
        tmp_path / "jobs/ok-p12/1",
        _intent(
            job_id="ok-p12",
            phase="PHASE-7",
            job_role="P12",
            object_type="P12_FAULT",
            object_id="fault-1",
            evaluation_input_class="E_COMMON",
        ),
    )


def test_contract_sensitivity_requires_e_contract(tmp_path):
    bad = tmp_path / "jobs/sens-bad/1"
    with pytest.raises(EvidenceError, match="E_JOB_ROLE_INPUT"):
        create_intent(
            bad,
            _intent(
                job_id="sens-bad",
                job_role="CONTRACT_SENSITIVITY",
                evaluation_input_class="E_COMMON",
            ),
        )
    create_intent(
        tmp_path / "jobs/sens-ok/1",
        _intent(
            job_id="sens-ok",
            job_role="CONTRACT_SENSITIVITY",
            evaluation_input_class="E_CONTRACT",
            evaluation_input_id="e-contract-0",
        ),
    )


def test_rejects_profiling_or_certification_witness_input_classes(tmp_path):
    for forbidden in ("PROFILING", "CERTIFICATION_WITNESS"):
        with pytest.raises(EvidenceError, match="E_EVALUATION_INPUT_CLASS"):
            create_intent(
                tmp_path / f"jobs/bad-{forbidden}/1",
                _intent(
                    job_id=f"bad-{forbidden}",
                    evaluation_input_class=forbidden,
                ),
            )


def test_rejects_attempt_four_after_three_infrastructure_failures(tmp_path):
    assert INFRASTRUCTURE_RETRY_LIMIT == 3
    jobs = tmp_path / "jobs"
    for attempt in (1, 2, 3):
        path = jobs / f"job-1/{attempt}"
        create_intent(path, _intent(attempt=attempt))
        write_result(path, _result(attempt=attempt, status="FAIL_INFRASTRUCTURE"))
    fourth = jobs / "job-1/4"
    create_intent(fourth, _intent(attempt=4))
    write_result(fourth, _result(attempt=4, status="FAIL_INFRASTRUCTURE"))
    with pytest.raises(EvidenceError, match="E_RETRY_POLICY"):
        reduce_attempts(jobs, tmp_path / "four.jsonl")


def test_rejects_retry_after_any_scientific_terminal_result(tmp_path):
    for status in ("PASS", "FAIL_SCIENTIFIC", "INCONCLUSIVE", "MISSING_WITH_REASON"):
        root = tmp_path / f"jobs-{status}"
        first = root / "job-1/1"
        second = root / "job-1/2"
        create_intent(first, _intent(attempt=1))
        write_result(first, _result(attempt=1, status=status))
        create_intent(second, _intent(attempt=2))
        write_result(second, _result(attempt=2))
        with pytest.raises(EvidenceError, match="E_RETRY_POLICY"):
            reduce_attempts(root, tmp_path / f"{status}.jsonl")


def _p12_job(
    job_id,
    object_id,
    *,
    mr_id="mr-1",
    evaluation_input_id="e-common-0",
    weight=1,
):
    return {
        "job_id": job_id,
        "object_type": "P12_FAULT",
        "object_id": object_id,
        "mr_id": mr_id,
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": evaluation_input_id,
        "repetition_id": 1,
        "environment_id": "env-1",
        "job_role": "P12",
        "weight": weight,
    }


def test_freeze_p12_denominator_before_results_and_summary_covers_five_outcomes():
    paired_ids = ["fault-a", "fault-b", "fault-c", "fault-d", "fault-e"]
    jobs = [
        _p12_job("j-violation", "fault-a"),
        _p12_job("j-declared", "fault-b", evaluation_input_id="e-common-1"),
        _p12_job("j-satisfied", "fault-c", evaluation_input_id="e-common-2"),
        _p12_job("j-inconclusive", "fault-d", evaluation_input_id="e-common-3"),
        _p12_job("j-infra", "fault-e", evaluation_input_id="e-common-4"),
    ]
    denominator = freeze_p12_denominator(paired_ids, jobs)
    assert denominator["planned_count"] == 5
    assert denominator["p12_paired_ids"] == paired_ids
    assert "artifact_sha256" in denominator

    results = [
        {"job_id": "j-violation", "scientific_outcome": "MR_VIOLATION"},
        {
            "job_id": "j-declared",
            "scientific_outcome": "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
        },
        {"job_id": "j-satisfied", "scientific_outcome": "MR_SATISFIED"},
        {"job_id": "j-inconclusive", "scientific_outcome": "SCIENTIFIC_INCONCLUSIVE"},
        {"job_id": "j-infra", "scientific_outcome": "INFRASTRUCTURE_UNRESOLVED"},
    ]
    summary = summarize_p12_outcomes(denominator, results)
    assert summary["planned_count"] == 5
    assert summary["state_counts"] == {
        "MR_VIOLATION": 1,
        "MR_SATISFIED": 1,
        "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION": 1,
        "SCIENTIFIC_INCONCLUSIVE": 1,
        "INFRASTRUCTURE_UNRESOLVED": 1,
    }
    assert list(summary["state_counts"]) == list(P12_OUTCOME_STATES)
    assert summary["lower_numerator"] == 2
    assert summary["upper_numerator"] == 4
    assert summary["lower_rate"] == str(Fraction(2, 5))
    assert summary["upper_rate"] == str(Fraction(4, 5))
    assert summary["complete_case_numerator"] == 2
    assert summary["complete_case_denominator"] == 3
    assert summary["complete_case_rate"] == str(Fraction(2, 3))
    assert summary["scientific_inconclusive_count"] == 1
    assert summary["infrastructure_unresolved_count"] == 1


def test_p12_denominator_rejects_role_membership_and_reweight_mutations():
    paired_ids = ["fault-a", "fault-b"]
    jobs = [
        _p12_job("j1", "fault-a"),
        _p12_job("j2", "fault-b", evaluation_input_id="e-common-1"),
    ]
    denominator = freeze_p12_denominator(paired_ids, jobs)

    with pytest.raises(EvidenceError, match="E_P12_INPUT_CLASS"):
        freeze_p12_denominator(
            paired_ids,
            [
                {
                    **_p12_job("j1", "fault-a"),
                    "evaluation_input_class": "E_CONTRACT",
                }
            ],
        )

    with pytest.raises(EvidenceError, match="E_P12_PAIRED"):
        freeze_p12_denominator(["fault-a"], jobs)

    results = [
        {"job_id": "j1", "scientific_outcome": "MR_VIOLATION"},
        {"job_id": "j2", "scientific_outcome": "MR_SATISFIED"},
    ]
    summarize_p12_outcomes(denominator, results)

    with pytest.raises(EvidenceError, match="E_P12_JOB_SET"):
        summarize_p12_outcomes(
            denominator,
            results
            + [{"job_id": "j3", "scientific_outcome": "MR_VIOLATION"}],
        )

    with pytest.raises(EvidenceError, match="E_P12_JOB_SET"):
        summarize_p12_outcomes(denominator, results[:1])

    mutated_paired = copy.deepcopy(denominator)
    mutated_paired["p12_paired_ids"] = ["fault-a", "fault-x"]
    body = {
        key: value for key, value in mutated_paired.items() if key != "artifact_sha256"
    }
    mutated_paired["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_P12_PAIRED|E_P12_DENOMINATOR"):
        summarize_p12_outcomes(mutated_paired, results)

    reweighted = copy.deepcopy(denominator)
    reweighted["jobs"] = [
        {**job, "weight": 2 if job["job_id"] == "j1" else job["weight"]}
        for job in reweighted["jobs"]
    ]
    body = {key: value for key, value in reweighted.items() if key != "artifact_sha256"}
    reweighted["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_P12_WEIGHT|E_P12_DENOMINATOR"):
        summarize_p12_outcomes(reweighted, results)


def test_phase7_p12_result_requires_scientific_outcome_and_others_forbid_it(tmp_path):
    controlled = tmp_path / "jobs/controlled/1"
    create_intent(controlled, _intent(job_id="controlled"))
    with pytest.raises(EvidenceError, match="E_SCIENTIFIC_OUTCOME"):
        write_result(
            controlled,
            _result(job_id="controlled", scientific_outcome="MR_VIOLATION"),
        )
    write_result(controlled, _result(job_id="controlled", scientific_outcome=None))

    p12 = tmp_path / "jobs/p12-job/1"
    create_intent(
        p12,
        _intent(
            job_id="p12-job",
            phase="PHASE-7",
            job_role="P12",
            object_type="P12_FAULT",
            object_id="fault-1",
        ),
    )
    with pytest.raises(EvidenceError, match="E_SCIENTIFIC_OUTCOME"):
        write_result(p12, _result(job_id="p12-job", scientific_outcome=None))
    with pytest.raises(EvidenceError, match="E_SCIENTIFIC_OUTCOME"):
        write_result(
            p12,
            _result(job_id="p12-job", scientific_outcome="NOT_A_STATE"),
        )
    write_result(
        p12,
        _result(job_id="p12-job", scientific_outcome="MR_SATISFIED"),
    )


def _complete_attempt(job_root, phase, job_id, attempt=1, status="PASS"):
    directory = job_root / phase / job_id / str(attempt)
    create_intent(
        directory,
        _intent(job_id=job_id, attempt=attempt, phase=phase),
    )
    write_result(
        directory,
        _result(job_id=job_id, attempt=attempt, status=status),
    )
    return directory


def test_reconstruct_attempt_events_orders_phase_job_attempt_and_ordinal(tmp_path):
    jobs = tmp_path / "jobs"
    _complete_attempt(jobs, "PHASE_3", "job-b")
    _complete_attempt(jobs, "PHASE_1", "job-z")
    first = _complete_attempt(
        jobs, "PHASE_1", "job-a", status="FAIL_INFRASTRUCTURE"
    )
    assert first.is_dir()
    _complete_attempt(jobs, "PHASE_1", "job-a", attempt=2)

    events = run_records_module.reconstruct_attempt_events(jobs)

    assert [
        (event["job_id"], event["attempt"], event["kind"])
        for event in events
    ] == [
        ("job-a", 1, "INTENT"),
        ("job-a", 1, "RESULT"),
        ("job-a", 2, "INTENT"),
        ("job-a", 2, "RESULT"),
        ("job-z", 1, "INTENT"),
        ("job-z", 1, "RESULT"),
        ("job-b", 1, "INTENT"),
        ("job-b", 1, "RESULT"),
    ]
    assert [event["sequence"] for event in events] == list(range(1, 9))


@pytest.mark.parametrize("mutation", ["unknown_file", "gap", "drifted_intent"])
def test_reconstruct_attempt_events_rejects_nonfrozen_tree(tmp_path, mutation):
    jobs = tmp_path / "jobs"
    _complete_attempt(jobs, "PHASE_2", "job-1", status="FAIL_INFRASTRUCTURE")
    if mutation == "unknown_file":
        (jobs / "PHASE_2/job-1/1/undeclared.txt").write_text("x")
    elif mutation == "gap":
        _complete_attempt(jobs, "PHASE_2", "job-1", attempt=3)
    else:
        second = jobs / "PHASE_2/job-1/2"
        create_intent(
            second,
            {**_intent(job_id="job-1", attempt=2, phase="PHASE_2"), "seed": 7},
        )
        write_result(second, _result(job_id="job-1", attempt=2))

    with pytest.raises(EvidenceError, match="E_ATTEMPT_(TREE|SEQUENCE)|E_RETRY_IDENTITY"):
        run_records_module.reconstruct_attempt_events(jobs)


def test_verify_attempt_tree_requires_exact_ledger_bytes(tmp_path):
    jobs = tmp_path / "jobs"
    _complete_attempt(jobs, "PHASE_1", "job-a")
    _complete_attempt(jobs, "PHASE_2", "job-b")
    events = run_records_module.reconstruct_attempt_events(jobs)
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
    assert run_records_module.verify_attempt_tree(jobs, ledger) == events

    reordered = tmp_path / "reordered.jsonl"
    reordered.write_bytes(
        canonical_json_bytes(events[2])
        + canonical_json_bytes(events[3])
        + canonical_json_bytes(events[0])
        + canonical_json_bytes(events[1])
    )
    with pytest.raises(EvidenceError, match="E_LEDGER_RECONSTRUCTION"):
        run_records_module.verify_attempt_tree(jobs, reordered)

    altered = copy.deepcopy(events)
    altered[-1]["status"] = "FAIL_SCIENTIFIC"
    altered_path = tmp_path / "altered.jsonl"
    altered_path.write_bytes(
        b"".join(canonical_json_bytes(event) for event in altered)
    )
    with pytest.raises(EvidenceError, match="E_LEDGER_RECONSTRUCTION"):
        run_records_module.verify_attempt_tree(jobs, altered_path)


def test_verify_phase_receipt_recomputes_every_closed_phase_binding(tmp_path):
    jobs = tmp_path / "jobs"
    _complete_attempt(jobs, "PHASE_2", "job-1")
    events = run_records_module.reconstruct_attempt_events(jobs)
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
    output_body = {
        "schema_version": "p3-package-manifest-v1",
        "role": "CONSTRUCTION_A",
        "parents": [],
        "files": [],
        "package_tree_sha256": canonical_sha256([]),
    }
    output_manifest = {
        **output_body,
        "artifact_sha256": canonical_sha256(output_body),
    }
    receipt = close_phase(
        "PHASE_2",
        "a" * 64,
        ["job-1"],
        ledger,
        output_manifest["artifact_sha256"],
    )
    assert receipt["phase_status"] == "CLOSED"
    run_records_module.verify_phase_receipt(
        receipt, events, ["job-1"], output_manifest
    )

    mutations = {
        "ledger_event_count": 1,
        "expected_job_count": 2,
        "expected_job_inventory_sha256": "0" * 64,
        "output_manifest_sha256": "1" * 64,
        "terminal_result_count": 0,
        "phase_status": "OPEN",
    }
    for field, value in mutations.items():
        changed = {**receipt, field: value}
        changed["artifact_sha256"] = canonical_sha256(
            {key: item for key, item in changed.items() if key != "artifact_sha256"}
        )
        with pytest.raises(EvidenceError, match="E_PHASE_RECEIPT"):
            run_records_module.verify_phase_receipt(
                changed, events, ["job-1"], output_manifest
            )
