from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.preflight import normalize_repository_identity, run_preflight


def _run(root: Path, *argv: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *argv],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def git_repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "Fixture")
    _run(root, "config", "user.email", "fixture@example.invalid")
    _run(root, "remote", "add", "origin", "git@github.com:Example/Repo.git")
    lock = root / "requirements.lock"
    lock.write_text("dependency==1\n", encoding="utf-8")
    input_path = root / "input.json"
    input_path.write_text("{}\n", encoding="utf-8")
    _run(root, "add", "requirements.lock", "input.json")
    _run(root, "commit", "-m", "fixture")
    return root


def _spec(root: Path, smoke=None, phase_role="CONTROLLED_B"):
    return {
        "schema_version": "p3-preflight-v1",
        "repository_identity": "Example/Repo",
        "expected_commit": _run(root, "rev-parse", "HEAD"),
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": hashlib.sha256(
            (root / "requirements.lock").read_bytes()
        ).hexdigest(),
        "phase_inputs": [
            {
                "path": "input.json",
                "sha256": hashlib.sha256((root / "input.json").read_bytes()).hexdigest(),
            }
        ],
        "smoke_commands": smoke or [["python3", "-c", "print(1)"]],
        "timeout_seconds": 10,
        "phase_role": phase_role,
        "minimum_cpu_count": 1,
        "minimum_memory_bytes": 1,
        "minimum_disk_free_bytes": 1,
        "worker_limit": 1,
    }


def _boom_executor(*_args, **_kwargs):
    raise AssertionError("smoke commands must not run")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://github.com/Example/Repo.git", "Example/Repo"),
        ("https://github.com/Example/RepoXgit", "Example/RepoXgit"),
        ("git@github.com:Example/Repo.git", "Example/Repo"),
        ("ssh://git@github.com/Example/Repo.git", "Example/Repo"),
        (
            "https://x-access-token:TOKEN@github.com/Owner/Repo.git",
            "Owner/Repo",
        ),
    ],
)
def test_repository_identity_normalizes_transport_spelling(raw, expected):
    assert normalize_repository_identity(raw) == expected


def test_preflight_passes_without_creating_scientific_intent(git_repo):
    result = run_preflight(git_repo, _spec(git_repo))
    assert result["status"] == "PASS"
    assert result["repository_identity"] == "Example/Repo"
    assert result["smoke"][0]["exit_code"] == 0
    assert result["atomic_replace_status"] == "PASS"
    assert result["file_lock_status"] == "PASS"
    assert result["phase_role"] == "CONTROLLED_B"
    assert result["worker_limit"] == 1
    assert "job_id" not in result
    assert not list(git_repo.glob("**/intent.json"))


def test_preflight_failure_is_repeatable_and_not_scientific(git_repo):
    spec = _spec(git_repo, smoke=[["python3", "-c", "raise SystemExit(7)"]])
    first = run_preflight(git_repo, spec)
    second = run_preflight(git_repo, spec)
    assert first["status"] == second["status"] == "FAIL"
    assert first["failure_code"] == second["failure_code"] == "E_PREFLIGHT_SMOKE"
    assert not list(git_repo.glob("**/intent.json"))


def test_preflight_rejects_wrong_commit_before_smoke(git_repo):
    spec = {**_spec(git_repo), "expected_commit": "0" * 40}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_COMMIT"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_wrong_repository_before_smoke(git_repo):
    spec = {**_spec(git_repo), "repository_identity": "Other/Repo"}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_REPOSITORY"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_wrong_dependency_lock_before_smoke(git_repo):
    spec = {**_spec(git_repo), "dependency_lock_sha256": "a" * 64}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_DEPENDENCY_LOCK"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_wrong_phase_input_before_smoke(git_repo):
    spec = _spec(git_repo)
    spec["phase_inputs"] = [{"path": "input.json", "sha256": "b" * 64}]
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_INPUT"):
        run_preflight(git_repo, spec, executor=_boom_executor)


@pytest.mark.parametrize("phase_role", ["CONSTRUCTION_A", "CONTROLLED_B"])
@pytest.mark.parametrize(
    "relative",
    [
        "data/package-c/holdout.json",
        "REAL_HOLDOUT/secret.json",
        "artifacts/holdout/x.json",
    ],
)
def test_preflight_rejects_package_c_path_in_ab_before_smoke(
    git_repo, phase_role, relative
):
    target = git_repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}\n", encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    spec = _spec(git_repo, phase_role=phase_role)
    spec["phase_inputs"] = [{"path": relative, "sha256": digest}]
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_PACKAGE_C"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_insufficient_cpu_before_smoke(git_repo):
    import os

    cpu = os.cpu_count() or 1
    spec = {**_spec(git_repo), "minimum_cpu_count": cpu + 1}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_CPU"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_insufficient_memory_before_smoke(git_repo):
    spec = {**_spec(git_repo), "minimum_memory_bytes": 2**62}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_MEMORY"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_unavailable_memory_when_minimum_positive(
    git_repo, monkeypatch
):
    def _unavailable(_name):
        raise ValueError("missing")

    monkeypatch.setattr("p3_v3.preflight.os.sysconf", _unavailable)
    spec = {**_spec(git_repo), "minimum_memory_bytes": 1}
    with pytest.raises(EvidenceError, match="UNAVAILABLE"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_insufficient_disk_before_smoke(git_repo):
    spec = {**_spec(git_repo), "minimum_disk_free_bytes": 2**62}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_DISK"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_rejects_invalid_worker_limit_before_smoke(git_repo):
    spec = {**_spec(git_repo), "worker_limit": 0}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_WORKER"):
        run_preflight(git_repo, spec, executor=_boom_executor)


def test_preflight_failed_atomic_replace_before_smoke(git_repo, monkeypatch):
    monkeypatch.setattr(
        "p3_v3.preflight._probe_atomic_replace", lambda _root: "FAIL"
    )
    result = run_preflight(git_repo, _spec(git_repo), executor=_boom_executor)
    assert result["status"] == "FAIL"
    assert result["failure_code"] == "E_PREFLIGHT_ATOMIC_REPLACE"
    assert result["atomic_replace_status"] == "FAIL"
    assert result["smoke"] == []
    assert "job_id" not in result


def test_preflight_failed_file_lock_before_smoke(git_repo, monkeypatch):
    monkeypatch.setattr("p3_v3.preflight._probe_file_lock", lambda _root: "FAIL")
    result = run_preflight(git_repo, _spec(git_repo), executor=_boom_executor)
    assert result["status"] == "FAIL"
    assert result["failure_code"] == "E_PREFLIGHT_FILE_LOCK"
    assert result["file_lock_status"] == "FAIL"
    assert result["smoke"] == []
    assert "job_id" not in result


def test_corrected_preflight_passes_without_intent_or_ledger_mutation(git_repo):
    ledger = git_repo / "scientific_ledger.jsonl"
    ledger.write_text('{"event":"baseline"}\n', encoding="utf-8")
    before = ledger.read_bytes()
    broken = {**_spec(git_repo), "dependency_lock_sha256": "c" * 64}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_DEPENDENCY_LOCK"):
        run_preflight(git_repo, broken, executor=_boom_executor)
    result = run_preflight(git_repo, _spec(git_repo, phase_role="CONSTRUCTION_A"))
    assert result["status"] == "PASS"
    assert result["phase_role"] == "CONSTRUCTION_A"
    assert result["atomic_replace_status"] == "PASS"
    assert result["file_lock_status"] == "PASS"
    assert ledger.read_bytes() == before
    assert not list(git_repo.glob("**/intent.json"))


def test_preflight_caps_worker_limit_at_cpu_count(git_repo):
    import os

    cpu = os.cpu_count() or 1
    spec = {**_spec(git_repo), "worker_limit": cpu + 5}
    result = run_preflight(git_repo, spec)
    assert result["status"] == "PASS"
    assert result["worker_limit"] == cpu
    assert result["declared_worker_limit"] == cpu + 5


def test_preflight_accepts_tokenized_https_origin(git_repo):
    _run(
        git_repo,
        "remote",
        "set-url",
        "origin",
        "https://x-access-token:TOKEN@github.com/Example/Repo.git",
    )
    result = run_preflight(git_repo, _spec(git_repo))
    assert result["status"] == "PASS"
    assert result["repository_identity"] == "Example/Repo"


def test_preflight_module_does_not_import_create_intent():
    source = Path(__file__).resolve().parents[2] / "src/p3_v3/preflight.py"
    text = source.read_text(encoding="utf-8")
    assert "create_intent" not in text
