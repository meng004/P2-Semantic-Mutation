from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import stat
from pathlib import Path

import pytest


ROOT = Path(os.environ.get("SUPPLEMENTAL_R3_MODULE_ROOT", Path(__file__).resolve().parents[2]))


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_summary() -> dict:
    authority = "31a4a8249f4ba6de12ba92291ab0cd55a65043b4"
    platform_head = "3c518b8467f74c9a6efd11f2db267f9f30e1c822"
    red_commit = "1" * 40
    green_commit = "2" * 40
    bundle_commit = "3" * 40
    bundle_tree = "4" * 40
    trace = [
        ("platform_head", ["git", "rev-parse", "HEAD"]),
        ("clean_status", ["git", "status", "--porcelain=v1"]),
        ("origin", ["git", "remote", "get-url", "origin"]),
        ("fetch_refspec", ["git", "config", "--get-all", "remote.origin.fetch"]),
        ("authorization_fetch", ["git", "fetch", "--no-tags", "origin", "+refs/heads/codex/supplemental-r3-amendment-01-execution-bundle-a03:refs/remotes/origin/codex/supplemental-r3-amendment-01-execution-bundle-a03"]),
        ("fetched_commit", ["git", "rev-parse", "refs/remotes/origin/codex/supplemental-r3-amendment-01-execution-bundle-a03"]),
        ("fetched_tree", ["git", "rev-parse", "refs/remotes/origin/codex/supplemental-r3-amendment-01-execution-bundle-a03^{tree}"]),
        ("bundle_manifest", ["shasum", "-a", "256", "data/external_slice/supplemental_r3/EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json"]),
        ("red_parent", ["git", "rev-list", "--parents", "-n", "1", red_commit]),
        ("green_parent", ["git", "rev-list", "--parents", "-n", "1", green_commit]),
        ("seal_parent", ["git", "rev-list", "--parents", "-n", "1", bundle_commit]),
        ("branch_switch", ["git", "switch", "-c", "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence", bundle_commit]),
        ("branch_head", ["git", "rev-parse", "HEAD"]),
        ("branch_clean", ["git", "status", "--porcelain=v1"]),
        ("authority_tree", ["git", "rev-parse", f"{authority}^{{tree}}"]),
        ("r2_tree", ["git", "rev-parse", f"{authority}:data/external_slice/supplemental_r2"]),
        ("admission_blob", ["git", "rev-parse", f"{authority}:data/external_slice/admission_sheet.csv"]),
        ("runtime_allocate", ["python3", "scripts/external_slice/supplemental_r3_bootstrap.py", "allocate-runtime"]),
    ]
    locked = {
        "authority": authority,
        "platform_head": platform_head,
        "red_commit": red_commit,
        "green_commit": green_commit,
        "design_sha256": "c6f950f01f3def9d6aad32e29bb8af9ae1bf7a8dd1bc4ef68c1b0ffe5a780820",
        "bundle_commit": bundle_commit,
        "bundle_tree": bundle_tree,
        "bundle_manifest_sha256": "5" * 64,
        "parent_plan_sha256": ["6" * 64, "7" * 64, "8" * 64],
        "execution_plan_sha256": "9" * 64,
        "bundle_audit_sha256": ["a" * 64, "b" * 64],
    }
    expected_stdout = {
        "platform_head": platform_head + "\n",
        "clean_status": "",
        "origin": "https://github.com/meng004/P3-Semantic-Mutation\n",
        "fetched_commit": bundle_commit + "\n",
        "fetched_tree": bundle_tree + "\n",
        "red_parent": f"{red_commit} {authority}\n",
        "green_parent": f"{green_commit} {red_commit}\n",
        "seal_parent": f"{bundle_commit} {green_commit}\n",
        "branch_head": bundle_commit + "\n",
        "branch_clean": "",
        "authority_tree": "a993c5537680358870e1dfaf9614a3c31b9f42d6\n",
        "r2_tree": "2e8fe75233bed73c9facb1c66b5d72b6a172487d\n",
        "admission_blob": "5ef073d4d6297639695491c46d20733236bede52\n",
    }
    return {
        "schema_version": 1,
        "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03",
        "runtime_root": "RUNTIME_ROOT_BOUND_AFTER_ALLOCATION",
        "session": "fresh-session",
        "model": "cursor-grok-4.5-high-fast",
        "evidence_request_count": 0,
        "locked_hashes": locked,
        "commands": [
            {
                "sequence": index,
                "trace_kind": kind,
                "argv": argv,
                "exit_code": 0,
                "stdout_sha256": hashlib.sha256(
                    expected_stdout.get(kind, "synthetic-output\n").encode("utf-8")
                ).hexdigest(),
                "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "assertion": "PASS",
            }
            for index, (kind, argv) in enumerate(trace, start=1)
        ],
    }


def make_runtime_root(tmp_path: Path) -> tuple[Path, Path]:
    runtime = tmp_path / "supplemental-r3-a01-bootstrap-addendum-03-abcdef12"
    runtime.mkdir(mode=0o700)
    os.chmod(runtime, 0o700)
    spool = runtime / "bootstrap-spool"
    spool.mkdir(mode=0o700)
    summary_path = spool / "task1-command-summary.json"
    payload = canonical_summary()
    payload["runtime_root"] = str(runtime)
    summary_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return runtime, summary_path


def test_canonical_json_is_compact_sorted_utf8() -> None:
    common = load_module("supplemental_r3_common", "scripts/external_slice/supplemental_r3_common.py")
    assert common.canonical_json_bytes({"β": 2, "a": 1}) == b'{"a":1,"\xce\xb2":2}'


def test_runtime_layout_accepts_only_typed_spool_before_journal(tmp_path: Path) -> None:
    bootstrap = load_module("supplemental_r3_bootstrap", "scripts/external_slice/supplemental_r3_bootstrap.py")
    runtime, summary = make_runtime_root(tmp_path)
    result = bootstrap.validate_prejournal_layout(runtime, summary, require_tmp_parent=False)
    assert result["summary_sha256"]
    assert result["entries"] == ["bootstrap-spool/task1-command-summary.json"]


def test_runtime_layout_rejects_addendum02_style_helper_at_root(tmp_path: Path) -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_extra", "scripts/external_slice/supplemental_r3_bootstrap.py")
    runtime, summary = make_runtime_root(tmp_path)
    (runtime / "rev-list-head-stdout.txt").write_text("unexpected", encoding="utf-8")
    with pytest.raises(bootstrap.GateError, match="prejournal_path_set"):
        bootstrap.validate_prejournal_layout(runtime, summary, require_tmp_parent=False)


def test_bootstrap_summary_binds_fixed_values_and_every_trace_argv() -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_summary", "scripts/external_slice/supplemental_r3_bootstrap.py")
    payload = canonical_summary()
    bootstrap.validate_bootstrap_summary(payload)
    payload["commands"][0]["argv"] = ["git", "rev-parse", "3c518b8467f74c9a6efd11f2db267f9f30e1c822"]
    with pytest.raises(bootstrap.GateError, match="summary_trace_argv"):
        bootstrap.validate_bootstrap_summary(payload)

    payload = canonical_summary()
    payload["locked_hashes"]["authority"] = "0" * 40
    with pytest.raises(bootstrap.GateError, match="summary_authority"):
        bootstrap.validate_bootstrap_summary(payload)


def test_initialize_journal_imports_summary_once_and_exclusive_creates(tmp_path: Path) -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_init", "scripts/external_slice/supplemental_r3_bootstrap.py")
    runtime, summary = make_runtime_root(tmp_path)
    journal = bootstrap.initialize_journal(runtime, summary, require_tmp_parent=False)
    assert stat.S_IMODE(journal.stat().st_mode) == 0o600
    records = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    assert [record["sequence"] for record in records] == list(range(1, 20))
    assert records[-1]["stage"] == "journal_initialized"
    with pytest.raises(bootstrap.GateError, match="journal_exists"):
        bootstrap.initialize_journal(runtime, summary, require_tmp_parent=False)


def test_command_runner_becomes_terminal_and_rejects_retry(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_runner", "scripts/external_slice/supplemental_r3_common.py")
    journal = tmp_path / "commands.jsonl"
    calls: list[tuple[str, ...]] = []

    def executor(argv):
        calls.append(tuple(argv))
        return (1, b"", b"first failure")

    runner = common.TerminalCommandRunner(journal, executor=executor)
    with pytest.raises(common.GateError, match="command_failed"):
        runner.run(["git", "status", "--short"])
    with pytest.raises(common.GateError, match="runner_terminal"):
        runner.run(["git", "status", "--short"])
    assert calls == [("git", "status", "--short")]


def test_command_runner_rejects_global_git_inventory_before_execution(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_inventory", "scripts/external_slice/supplemental_r3_common.py")
    calls = []
    runner = common.TerminalCommandRunner(
        tmp_path / "journal.jsonl",
        executor=lambda argv: calls.append(tuple(argv)) or (0, b"", b""),
    )
    with pytest.raises(common.GateError, match="forbidden_git_inventory"):
        runner.run(["git", "for-each-ref"])
    with pytest.raises(common.GateError, match="runner_terminal"):
        runner.run(["git", "rev-parse", "HEAD"])
    assert calls == []


def test_command_runner_rejects_non_graphql_network_entrypoints(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_network", "scripts/external_slice/supplemental_r3_common.py")
    forbidden = [
        ["curl", "https://example.invalid"],
        ["gh", "api", "repos/example/repo"],
        ["git", "fetch", "origin"],
    ]
    for index, argv in enumerate(forbidden):
        calls = []
        runner = common.TerminalCommandRunner(
            tmp_path / f"network-{index}.jsonl",
            executor=lambda command: calls.append(tuple(command)) or (0, b"", b""),
        )
        with pytest.raises(common.GateError, match="forbidden_network_command"):
            runner.run(argv)
        assert calls == []

    alternate_entrypoints = [
        ["/usr/bin/curl", "https://example.invalid"],
        ["python3", "-c", "import socket"],
        ["node", "-e", "fetch('https://example.invalid')"],
        ["open", "https://example.invalid"],
    ]
    for index, argv in enumerate(alternate_entrypoints, start=20):
        calls = []
        runner = common.TerminalCommandRunner(
            tmp_path / f"network-{index}.jsonl",
            executor=lambda command: calls.append(tuple(command)) or (0, b"", b""),
        )
        expected = "forbidden_python_command" if argv[0] == "python3" else "forbidden_executable"
        with pytest.raises(common.GateError, match=expected):
            runner.run(argv)
        assert calls == []

    calls = []
    runner = common.TerminalCommandRunner(
        tmp_path / "network-git-config.jsonl",
        executor=lambda command: calls.append(tuple(command)) or (0, b"", b""),
    )
    with pytest.raises(common.GateError, match="forbidden_git_operation"):
        runner.run(["git", "-c", "credential.helper=!network-helper", "fetch", "origin"])
    assert calls == []

    runner = common.TerminalCommandRunner(
        tmp_path / "unmarked-graphql.jsonl", executor=lambda command: (0, b"", b"")
    )
    with pytest.raises(common.GateError, match="unmarked_evidence_request"):
        runner.run(["gh", "api", "graphql", "-f", "query=query { viewer { login } }"])

    root = Path(__file__).resolve().parents[2]
    closure = common.audit_network_source_closure(root, [
        "scripts/external_slice/supplemental_r3_common.py",
        "scripts/external_slice/supplemental_r3_bootstrap.py",
        "scripts/external_slice/mine_supplemental_r3.py",
        "scripts/external_slice/check_supplemental_r3_admission.py",
        "scripts/external_slice/check_supplemental_r3_handoff_hashes.py",
    ])
    assert closure["python_network_imports"] == []
    assert closure["live_endpoint"] == ["gh", "api", "graphql"]


def test_command_runner_allows_only_exact_vm_green_python_surface(tmp_path: Path) -> None:
    common = load_module(
        "supplemental_r3_common_vm_python",
        "scripts/external_slice/supplemental_r3_common.py",
    )
    calls = []
    python_executable = "/opt/frozen/bin/python3"
    runner = common.TerminalCommandRunner(
        tmp_path / "vm-python.jsonl",
        executor=lambda argv: calls.append(tuple(argv)) or (0, b"ok", b""),
        python_executable=python_executable,
    )
    report = "/tmp/supplemental-r3-a01-bootstrap-addendum-03-fresh/vm-green-report.json"
    matrix = [
        python_executable,
        "tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py",
        "--phase", "green",
        "--manifest", "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json",
        "--report", report,
        "--vm-run",
    ]
    runner.run(matrix)
    runner.run([python_executable, "-m", "pytest", "-q"])
    assert calls == [tuple(matrix), (python_executable, "-m", "pytest", "-q")]


def test_run_vm_green_binds_matrix_and_full_suite_before_seal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bootstrap = load_module(
        "supplemental_r3_bootstrap_vm_green",
        "scripts/external_slice/supplemental_r3_bootstrap.py",
    )
    runtime, summary = make_runtime_root(tmp_path)
    journal = bootstrap.initialize_journal(runtime, summary, require_tmp_parent=False)
    output = runtime / bootstrap.VM_GREEN_REPORT_NAME
    matrix_manifest = tmp_path / "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json"
    matrix_manifest.parent.mkdir(parents=True)
    matrix_manifest.write_text(json.dumps({"nodes": [{"node_id": "f.py::test_node"}]}) + "\n")
    calls = []

    class FakeRunner:
        def __init__(self, journal_path, *, executor, python_executable):
            assert journal_path == journal
            assert python_executable == bootstrap.sys.executable
            self.executor = executor

        def begin_operation(self, name, metadata):
            assert name == "run_vm_green"
            assert metadata == {"root": str(tmp_path), "output": str(output)}
            return "vm-green-operation"

        def run(self, argv):
            calls.append(list(argv))
            exit_code, stdout, stderr = self.executor(argv)
            assert exit_code == 0
            return stdout, stderr

        def complete_operation(self, operation_key, metadata):
            assert operation_key == "vm-green-operation"
            assert metadata["node_count"] == 1
            assert metadata["full_suite"]["passed"] == 549
            assert metadata["report_sha256"] == bootstrap.sha256_file(output)
            assert metadata["full_suite_network_spy_count"] == 0

    class Result:
        returncode = 0
        stderr = b""

        def __init__(self, stdout):
            self.stdout = stdout

    def fake_subprocess_run(argv, *, cwd, env, capture_output, check, shell):
        assert cwd == tmp_path
        assert capture_output is True and check is False and shell is False
        if "--vm-run" in argv:
            output.write_bytes(bootstrap.canonical_json_bytes({
                "schema_version": 1,
                "phase": "green",
                "vm_run": True,
                "manifest_sha256": bootstrap.sha256_file(matrix_manifest),
                "evidence_request_count": 0,
                "records": [{"node_id": "f.py::test_node", "outcome": "PASS"}],
            }) + b"\n")
            assert env["PYTHONPATH"] == str(tmp_path / "src")
            return Result(b"")
        spy_root = runtime / "vm-green-full-suite-network-spy"
        assert env["PATH"].split(os.pathsep)[0] == str(spy_root)
        assert env["PYTHONPATH"].split(os.pathsep) == [str(spy_root), str(tmp_path / "src")]
        assert env["SUPPLEMENTAL_R3_NETWORK_SPY_LOG"] == str(spy_root / "requests.jsonl")
        return Result(b"549 passed, 10 warnings in 420.00s\n")

    monkeypatch.setattr(bootstrap._common, "TerminalCommandRunner", FakeRunner)
    monkeypatch.setattr(bootstrap.subprocess, "run", fake_subprocess_run)
    report = bootstrap.run_vm_green(
        root=tmp_path,
        runtime_root=runtime,
        journal=journal,
        output=output,
    )
    assert calls[0][-1] == "--vm-run"
    assert calls[1] == [bootstrap.sys.executable, "-m", "pytest", "-q"]
    assert report["full_suite"] == {
        "passed": 549, "warnings": 10, "duration_seconds": 420.0
    }
    assert report["full_suite_network_spy_count"] == 0


def test_vm_green_and_environment_commit_journal_lineage_are_exact(tmp_path: Path) -> None:
    bootstrap = load_module(
        "supplemental_r3_bootstrap_journal_lineage",
        "scripts/external_slice/supplemental_r3_bootstrap.py",
    )
    runtime, summary = make_runtime_root(tmp_path)
    journal = bootstrap.initialize_journal(runtime, summary, require_tmp_parent=False)
    root = tmp_path / "repository"
    node = "f.py::test_node"
    python_executable = "/usr/bin/python3"
    node_manifest = root / "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json"
    node_manifest.parent.mkdir(parents=True)
    node_manifest.write_text(json.dumps({"nodes": [{"node_id": node}]}) + "\n")
    report_path = runtime / bootstrap.VM_GREEN_REPORT_NAME
    report = {
        "schema_version": 1,
        "phase": "green",
        "vm_run": True,
        "manifest_sha256": bootstrap.sha256_file(node_manifest),
        "evidence_request_count": 0,
        "records": [{
            "node_id": node,
            "argv": [python_executable, "-m", "pytest", "-q", "--maxfail=1", node],
            "exit_code": 0,
            "stdout_sha256": "a" * 64,
            "stderr_sha256": "b" * 64,
            "network_spy_count": 0,
            "outcome": "PASS",
        }],
        "full_suite": {"passed": 551, "warnings": 10, "duration_seconds": 408.89},
        "full_suite_network_spy_count": 0,
    }
    report_path.write_bytes(bootstrap.canonical_json_bytes(report) + b"\n")
    existing = journal.read_bytes()
    start = len(existing.splitlines()) + 1
    matrix = [
        python_executable,
        "tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py",
        "--phase", "green",
        "--manifest", "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json",
        "--report", str(report_path),
        "--vm-run",
    ]
    operation_key = f"{start}:run_vm_green"
    records = [
        {"sequence": start, "stage": "operation_intent", "operation_name": "run_vm_green",
         "operation_key": operation_key, "metadata": {"root": str(root), "output": str(report_path)},
         "evidence_request": False, "runner_state": "pending"},
        {"sequence": start + 1, "stage": "command", "argv": matrix, "exit_code": 0,
         "evidence_request": False, "runner_state": "active"},
        {"sequence": start + 2, "stage": "command", "argv": [python_executable, "-m", "pytest", "-q"],
         "exit_code": 0, "evidence_request": False, "runner_state": "active"},
        {"sequence": start + 3, "stage": "operation", "operation_key": operation_key,
         "metadata": {"report_sha256": bootstrap.sha256_file(report_path), "node_count": 1,
                      "full_suite": report["full_suite"],
                      "full_suite_network_spy_count": 0},
         "evidence_request": False, "runner_state": "active"},
    ]
    journal.write_bytes(existing + b"".join(
        bootstrap.canonical_json_bytes(row) + b"\n" for row in records
    ))
    bootstrap._verify_vm_green_journal_lineage(
        journal=journal, root=root, runtime_root=runtime, report=report
    )

    materialize_sequence = start + 4
    materialize_key = f"{materialize_sequence}:materialize_pre_network_seal"
    materialize_intent = {
        "sequence": materialize_sequence, "stage": "operation_intent",
        "operation_name": "materialize_pre_network_seal", "operation_key": materialize_key,
        "evidence_request": False, "runner_state": "pending",
    }
    journal.write_bytes(
        journal.read_bytes() + bootstrap.canonical_json_bytes(materialize_intent) + b"\n"
    )
    seal = {
        "journal_record_count": materialize_sequence,
        "journal_prefix_sha256": hashlib.sha256(journal.read_bytes()).hexdigest(),
    }
    tail = [
        {"sequence": materialize_sequence + 1, "stage": "operation",
         "operation_key": materialize_key, "metadata": {"sha256": "f" * 64},
         "evidence_request": False, "runner_state": "active"},
        {"sequence": materialize_sequence + 2, "stage": "command",
         "argv": ["git", "add", bootstrap.VM_SEAL_REL.as_posix()], "exit_code": 0,
         "evidence_request": False, "runner_state": "active"},
        {"sequence": materialize_sequence + 3, "stage": "command",
         "argv": ["git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"],
         "exit_code": 0, "evidence_request": False, "runner_state": "active"},
    ]
    journal.write_bytes(journal.read_bytes() + b"".join(
        bootstrap.canonical_json_bytes(row) + b"\n" for row in tail
    ))
    bootstrap._verify_environment_commit_journal_lineage(
        journal=journal, seal=seal, seal_sha256="f" * 64
    )
    bootstrap._verify_vm_green_journal_lineage(
        journal=journal,
        root=root,
        runtime_root=runtime,
        report=report,
        require_tail=False,
    )
    tail[-1]["argv"][-1] = "different subject"
    prefix = b"".join(journal.read_bytes().splitlines(keepends=True)[:-3])
    journal.write_bytes(prefix + b"".join(
        bootstrap.canonical_json_bytes(row) + b"\n" for row in tail
    ))
    with pytest.raises(bootstrap.GateError, match="environment_commit_journal_sequence"):
        bootstrap._verify_environment_commit_journal_lineage(
            journal=journal, seal=seal, seal_sha256="f" * 64
        )

def test_command_runner_resumes_sequence_and_request_keys_across_processes(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_resume", "scripts/external_slice/supplemental_r3_common.py")
    journal = tmp_path / "journal.jsonl"
    first = common.TerminalCommandRunner(journal, executor=lambda argv: (0, b"one", b""))
    first.run(["gh", "api", "graphql"], evidence_request=True, request_key="page-1")
    calls = []
    resumed = common.TerminalCommandRunner(
        journal, executor=lambda argv: calls.append(tuple(argv)) or (0, b"two", b""),
    )
    assert resumed.sequence == 2
    assert resumed.evidence_request_count == 1
    with pytest.raises(common.GateError, match="duplicate_request"):
        resumed.run(["gh", "api", "graphql"], evidence_request=True, request_key="page-1")
    assert calls == []


def test_request_intent_is_fsynced_before_executor_and_unresolved_intent_is_terminal(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_intent", "scripts/external_slice/supplemental_r3_common.py")
    journal = tmp_path / "journal.jsonl"

    def executor(argv):
        records = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
        assert records[-1]["stage"] == "request_intent"
        assert records[-1]["request_key"] == "page-1"
        return 0, b"ok", b""

    runner = common.TerminalCommandRunner(journal, executor=executor)
    runner.run(["gh", "api", "graphql"], evidence_request=True, request_key="page-1")
    records = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    assert [row["stage"] for row in records] == ["request_intent", "command"]

    unresolved = tmp_path / "unresolved.jsonl"
    unresolved.write_bytes(common.canonical_json_bytes({
        "sequence": 1, "stage": "request_intent", "argv": ["gh", "api", "graphql"],
        "started_at_utc": "2026-08-08T00:00:00Z", "ended_at_utc": None,
        "exit_code": None, "stdout_sha256": None, "stderr_sha256": None,
        "evidence_request": True, "evidence_request_count": 1,
        "request_key": "lost-page", "runner_state": "pending",
    }) + b"\n")
    blocked = common.TerminalCommandRunner(unresolved, executor=lambda argv: (0, b"", b""))
    with pytest.raises(common.GateError, match="runner_terminal"):
        blocked.run(["gh", "api", "graphql"], evidence_request=True, request_key="lost-page")


def test_persist_cli_failure_makes_upper_layer_invariant_terminal(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_cli_failure", "scripts/external_slice/supplemental_r3_common.py")
    journal = tmp_path / "journal.jsonl"
    common.persist_cli_failure(journal, "admission", common.GateError("quota_vector"))
    resumed = common.TerminalCommandRunner(journal, executor=lambda argv: (0, b"", b""))
    with pytest.raises(common.GateError, match="runner_terminal"):
        resumed.run(["git", "status", "--porcelain=v1"])


def test_terminal_runner_allows_only_one_exact_predeclared_shutdown_command(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_shutdown", "scripts/external_slice/supplemental_r3_common.py")
    journal = tmp_path / "journal.jsonl"
    failing = common.TerminalCommandRunner(journal, executor=lambda argv: (1, b"", b"failed"))
    with pytest.raises(common.GateError, match="command_failed"):
        failing.run(["git", "status", "--short"])
    shutdown = ["git", "status", "--porcelain=v1"]
    calls = []
    resumed = common.TerminalCommandRunner(
        journal,
        executor=lambda argv: calls.append(tuple(argv)) or (0, b"", b""),
        shutdown_allowlist=[shutdown],
    )
    resumed.run(shutdown)
    with pytest.raises(common.GateError, match="runner_terminal"):
        resumed.run(shutdown)
    assert calls == [tuple(shutdown)]
    cli_journal = tmp_path / "cli-terminal.jsonl"
    cli_failing = common.TerminalCommandRunner(
        cli_journal, executor=lambda argv: (1, b"", b"failed")
    )
    with pytest.raises(common.GateError, match="command_failed"):
        cli_failing.run(["git", "status", "--short"])
    cli_calls = []
    assert common.main(
        ["run-shutdown-diagnostic", "--journal", str(cli_journal)],
        executor=lambda argv: cli_calls.append(tuple(argv)) or (0, b"", b""),
    ) == 0
    assert cli_calls == [tuple(shutdown)]
    for index, forbidden in enumerate((
        ["git", "push", "--force", "origin", "bad"],
        ["git", "merge", "bad"],
        ["git", "fetch", "origin"],
    )):
        with pytest.raises(common.GateError, match="shutdown_allowlist"):
            common.TerminalCommandRunner(
                tmp_path / f"shutdown-forbidden-{index}.jsonl",
                shutdown_allowlist=[forbidden],
            )

    push_journal = tmp_path / "one-shot-push.jsonl"
    push = [
        "git", "push", "-u", "origin",
        "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
    ]
    push_calls = []
    push_runner = common.TerminalCommandRunner(
        push_journal,
        executor=lambda argv: push_calls.append(tuple(argv)) or (0, b"pushed", b""),
    )
    handoff_commit = "a" * 40
    push_runner.run(
        push, push_handoff_commit=handoff_commit, push_preflight_sha256="1" * 64
    )
    with pytest.raises(common.GateError, match="runner_success_closed"):
        push_runner.run(push)
    reloaded = common.TerminalCommandRunner(
        push_journal,
        executor=lambda argv: push_calls.append(tuple(argv)) or (0, b"pushed", b""),
    )
    with pytest.raises(common.GateError, match="runner_success_closed"):
        reloaded.run(["git", "status", "--porcelain=v1"])
    assert push_calls == [tuple(push)]
    push_records = [json.loads(line) for line in push_journal.read_text().splitlines()]
    assert [row["stage"] for row in push_records] == ["push_intent", "push_completion"]
    assert push_records[0]["handoff_commit"] == handoff_commit
    assert push_records[1]["runner_state"] == "success_closed"


def test_terminal_runner_persists_push_intent_before_side_effect_and_never_retries(
    tmp_path: Path,
) -> None:
    common = load_module(
        "supplemental_r3_common_push_crash",
        "scripts/external_slice/supplemental_r3_common.py",
    )
    journal = tmp_path / "push-crash.jsonl"
    push = [
        "git", "push", "-u", "origin",
        "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
    ]
    side_effects: list[tuple[str, ...]] = []

    def side_effect_then_crash(argv):
        side_effects.append(tuple(argv))
        intent = json.loads(journal.read_text(encoding="utf-8").splitlines()[-1])
        assert intent["stage"] == "push_intent"
        assert intent["runner_state"] == "pending"
        raise RuntimeError("process interrupted after remote update")

    runner = common.TerminalCommandRunner(journal, executor=side_effect_then_crash)
    with pytest.raises(common.GateError, match="executor_error"):
        runner.run(
            push, push_handoff_commit="b" * 40, push_preflight_sha256="2" * 64
        )

    reloaded = common.TerminalCommandRunner(
        journal,
        executor=lambda argv: side_effects.append(tuple(argv)) or (0, b"", b""),
    )
    with pytest.raises(common.GateError, match="runner_terminal"):
        reloaded.run(
            push, push_handoff_commit="b" * 40, push_preflight_sha256="2" * 64
        )
    assert side_effects == [tuple(push)]


def test_operation_intent_is_durable_and_incomplete_operation_is_terminal(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_operation", "scripts/external_slice/supplemental_r3_common.py")
    complete_journal = tmp_path / "complete.jsonl"
    complete = common.TerminalCommandRunner(complete_journal)
    operation_key = complete.begin_operation("publish_candidate", {"target": "candidate"})
    complete.complete_operation(operation_key, {"sha256": "a" * 64})
    resumed = common.TerminalCommandRunner(complete_journal)
    assert resumed.terminal is False

    incomplete_journal = tmp_path / "incomplete.jsonl"
    incomplete = common.TerminalCommandRunner(incomplete_journal)
    incomplete.begin_operation("publish_candidate", {"target": "candidate"})
    blocked = common.TerminalCommandRunner(incomplete_journal)
    with pytest.raises(common.GateError, match="runner_terminal"):
        blocked.run(["git", "status", "--porcelain=v1"])


def test_common_run_command_cli_journals_exact_argv_and_relays_output(tmp_path: Path, capsys) -> None:
    common = load_module("supplemental_r3_common_cli", "scripts/external_slice/supplemental_r3_common.py")
    journal = tmp_path / "commands.jsonl"
    calls = []

    def executor(argv):
        calls.append(tuple(argv))
        return 0, b"stdout\n", b"stderr\n"

    assert common.main(
        ["run-command", "--journal", str(journal), "git", "status", "--short"],
        executor=executor,
    ) == 0
    assert calls == [("git", "status", "--short")]
    captured = capsys.readouterr()
    assert captured.out == "stdout\n"
    assert captured.err == "stderr\n"
    record = json.loads(journal.read_text(encoding="utf-8").splitlines()[-1])
    assert record["stage"] == "command"
    assert record["argv"] == ["git", "status", "--short"]


def test_frozen_inputs_bind_r2_tree_paths_bytes_and_batch3_scope(tmp_path: Path) -> None:
    common = load_module("supplemental_r3_common_frozen", "scripts/external_slice/supplemental_r3_common.py")
    root = Path(__file__).resolve().parents[2]
    runner = common.TerminalCommandRunner(tmp_path / "journal.jsonl")
    result = common.verify_frozen_inputs(
        root=root,
        authority="31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        runner=runner,
    )
    assert result["r2_tree"] == "2e8fe75233bed73c9facb1c66b5d72b6a172487d"
    assert result["r2_path_count"] == 634
    assert result["admission_blob"] == "5ef073d4d6297639695491c46d20733236bede52"
    assert result["batch3_deny_consistent"] is True
    assert "batch3_deny_sha" not in result


def test_stale_ref_rename_does_not_change_trace_or_verdict() -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_ref", "scripts/external_slice/supplemental_r3_bootstrap.py")
    commands = [["git", "rev-parse", "HEAD"], ["git", "rev-list", "HEAD"]]
    first = bootstrap.evaluate_execution_closure(
        commands=commands,
        ancestry_ids=["31a4a8249f4ba6de12ba92291ab0cd55a65043b4"],
        configured_refspecs=["+refs/heads/main:refs/remotes/origin/main"],
        deny="f" * 40,
        stale_refs={"refs/remotes/origin/stale-a": "f" * 40},
    )
    renamed = bootstrap.evaluate_execution_closure(
        commands=commands,
        ancestry_ids=["31a4a8249f4ba6de12ba92291ab0cd55a65043b4"],
        configured_refspecs=["+refs/heads/main:refs/remotes/origin/main"],
        deny="f" * 40,
        stale_refs={"refs/remotes/origin/stale-renamed": "f" * 40},
    )
    assert first == renamed
    assert first["verdict"] == "PASS"


def test_path_guard_rejects_downstream_tokens_without_false_prefix_hits() -> None:
    common = load_module("supplemental_r3_common_guard", "scripts/external_slice/supplemental_r3_common.py")
    for forbidden in ("readiness", "r8", "canonical_freeze", "canonical-freeze", "merge", "pr"):
        with pytest.raises(common.GateError, match="forbidden_token"):
            common.guard_tokens([forbidden])
    common.guard_tokens(["r80", "prefreeze", "prereadiness"])


def test_bundle_lineage_is_exact_linear_chain_from_authority() -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_lineage", "scripts/external_slice/supplemental_r3_bootstrap.py")
    authority = "1" * 40
    red = "2" * 40
    green = "3" * 40
    seal = "4" * 40
    bootstrap.verify_bundle_lineage(
        authority=authority,
        red_commit=red,
        green_commit=green,
        seal_commit=seal,
        parents={red: [authority], green: [red], seal: [green]},
    )
    with pytest.raises(bootstrap.GateError, match="bundle_lineage"):
        bootstrap.verify_bundle_lineage(
            authority=authority,
            red_commit=red,
            green_commit=green,
            seal_commit=seal,
            parents={red: [authority], green: [red, authority], seal: [green]},
        )


def test_verify_bundle_reads_actual_git_identity_through_runner(tmp_path: Path) -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_actual_bundle", "scripts/external_slice/supplemental_r3_bootstrap.py")
    authority, red, green, seal = (character * 40 for character in "1234")
    tree = "5" * 40
    authority_tree = "6" * 40
    design = "7" * 64
    plans = ["8" * 64, "9" * 64, "a" * 64]
    for relative in bootstrap.BUNDLE_PATHS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(relative + "\n", encoding="utf-8")
    red_log = tmp_path / bootstrap.LOCAL_RED_REL
    green_log = tmp_path / bootstrap.LOCAL_GREEN_REL
    red_log.parent.mkdir(parents=True, exist_ok=True)
    red_log.write_text("red\n", encoding="utf-8")
    green_log.write_text("green\n", encoding="utf-8")

    red_paths = sorted(path for path in bootstrap.BUNDLE_PATHS if path.startswith("tests/"))
    green_paths = sorted(path for path in bootstrap.BUNDLE_PATHS if path.startswith("scripts/"))
    seal_paths = sorted([
        bootstrap.LOCAL_RED_REL.as_posix(), bootstrap.LOCAL_GREEN_REL.as_posix(),
        bootstrap.BUNDLE_MANIFEST_REL.as_posix(),
    ])

    def response_stream():
        return iter([
            (seal + "\n").encode(), (tree + "\n").encode(),
            f"{red} {authority}\n".encode(), f"{green} {red}\n".encode(),
            f"{seal} {green}\n".encode(), (authority_tree + "\n").encode(),
            ("\n".join(red_paths) + "\n").encode(),
            ("\n".join(green_paths) + "\n").encode(),
            ("\n".join(seal_paths) + "\n").encode(), b"",
        ])

    class Runner:
        def __init__(self):
            self.argv = []
            self.responses = response_stream()

        def run(self, argv, **kwargs):
            self.argv.append(list(argv))
            return next(self.responses), b""

    manifest = tmp_path / bootstrap.BUNDLE_MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({
        "authority": authority,
        "authority_tree": authority_tree,
        "design_sha256": design,
        "commits": {"red": {"commit": red, "parent": authority}, "green": {"commit": green, "parent": red}},
        "parent_plan_sha256": plans,
        "file_sha256": {
            relative: bootstrap.sha256_file(tmp_path / relative)
            for relative in bootstrap.BUNDLE_PATHS
        },
        "logs": {
            "red": {"path": bootstrap.LOCAL_RED_REL.as_posix(), "sha256": bootstrap.sha256_file(red_log)},
            "green": {"path": bootstrap.LOCAL_GREEN_REL.as_posix(), "sha256": bootstrap.sha256_file(green_log)},
        },
        "allowed_bundle_paths": list(bootstrap.BUNDLE_PATHS) + [
            bootstrap.LOCAL_RED_REL.as_posix(), bootstrap.LOCAL_GREEN_REL.as_posix(),
            bootstrap.BUNDLE_MANIFEST_REL.as_posix(),
        ],
    }, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    runner = Runner()
    bootstrap.verify_bundle(
        runner=runner, root=tmp_path, authority=authority, red_commit=red,
        green_commit=green, seal_commit=seal, bundle_tree=tree,
        manifest=manifest, manifest_sha256=bootstrap.sha256_file(manifest),
        expected_design_sha256=design, expected_parent_plan_sha256=plans,
    )
    mutated = tmp_path / bootstrap.BUNDLE_PATHS[0]
    mutated.write_bytes(mutated.read_bytes() + b"x")
    with pytest.raises(bootstrap.GateError, match="bundle_file_sha256"):
        bootstrap.verify_bundle(
            runner=Runner(), root=tmp_path, authority=authority, red_commit=red,
            green_commit=green, seal_commit=seal, bundle_tree=tree,
            manifest=manifest, manifest_sha256=bootstrap.sha256_file(manifest),
            expected_design_sha256=design, expected_parent_plan_sha256=plans,
        )


def test_bootstrap_cli_exposes_only_frozen_vm_operations() -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_cli", "scripts/external_slice/supplemental_r3_bootstrap.py")
    parser = bootstrap.build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices) == {
        "allocate-runtime", "initialize-journal", "verify-bundle", "run-vm-green",
        "verify-environment-seal", "materialize-seal", "build-bundle-seal",
    }


def test_bootstrap_main_dispatches_initialize_journal(tmp_path: Path) -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_main", "scripts/external_slice/supplemental_r3_bootstrap.py")
    runtime, summary = make_runtime_root(tmp_path)
    assert bootstrap.main(
        ["initialize-journal", "--runtime-root", str(runtime), "--summary", str(summary)],
        require_tmp_parent=False,
    ) == 0
    assert (runtime / "command-journal.jsonl").is_file()


def test_build_bundle_seal_binds_zero_request_red_green_logs(tmp_path: Path) -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_bundle_seal", "scripts/external_slice/supplemental_r3_bootstrap.py")
    red = tmp_path / "red.json"
    green = tmp_path / "green.json"
    for phase, path in (("red", red), ("green", green)):
        report = {"phase": phase, "evidence_request_count": 0, "records": []}
        if phase == "green":
            report["full_suite"] = {"passed": 527, "warnings": 10, "duration_seconds": 460.64}
        path.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    output = tmp_path / bootstrap.BUNDLE_MANIFEST_REL.name
    bootstrap._bundle_git_identity = lambda root, authority: {
        "authority_tree": "a" * 40,
        "red_commit": "b" * 40,
        "red_parent": authority,
        "green_commit": "c" * 40,
        "green_parent": "b" * 40,
        "r2_tree": "2e8fe75233bed73c9facb1c66b5d72b6a172487d",
        "r2_entries": [{"path": f"p{i}", "mode": "100644", "oid": "d" * 40, "sha256": "e" * 64} for i in range(634)],
        "frozen_r3_entries": [],
        "admission_sheet": {"blob": "5ef073d4d6297639695491c46d20733236bede52", "sha256": "77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a"},
    }
    bootstrap._environment_identity = lambda root: {"python": "test", "pytest": "test", "git": "test", "os": "test", "dependency_files": {}}
    result = bootstrap.build_bundle_seal(
        root=Path(__file__).resolve().parents[2],
        red_report=red,
        green_report=green,
        output=output,
        authority="31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        design_sha256="c6f950f01f3def9d6aad32e29bb8af9ae1bf7a8dd1bc4ef68c1b0ffe5a780820",
        parent_plan_sha256=["1" * 64, "2" * 64, "3" * 64],
        enforce_output_paths=False,
    )
    assert result["zero_network"]["evidence_request_count"] == 0
    assert result["parent_plan_sha256"] == ["1" * 64, "2" * 64, "3" * 64]
    assert "plan_sha256" not in result
    assert len(result["frozen_inputs"]["r2_entries"]) == 634
    assert result["commits"]["red"]["parent"] == "31a4a8249f4ba6de12ba92291ab0cd55a65043b4"
    assert output.is_file()


def test_materialize_pre_network_seal_binds_spool_journal_and_vm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bootstrap = load_module("supplemental_r3_bootstrap_vm_seal", "scripts/external_slice/supplemental_r3_bootstrap.py")
    runtime, summary = make_runtime_root(tmp_path)
    bundle = tmp_path / "bundle.json"
    bundle.write_text(json.dumps({
        "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03",
        "authority": "31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        "commits": {
            "red": {"commit": "1" * 40, "parent": "31a4a8249f4ba6de12ba92291ab0cd55a65043b4"},
            "green": {"commit": "2" * 40, "parent": "1" * 40},
        },
        "design_sha256": "c" * 64,
        "parent_plan_sha256": ["1" * 64, "2" * 64, "3" * 64],
        "zero_network": {"evidence_request_count": 0},
        "test_counts": {"red": 1, "green": 1},
    }, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    summary_payload = json.loads(summary.read_text(encoding="utf-8"))
    summary_payload["locked_hashes"].update({
        "design_sha256": "c" * 64,
        "parent_plan_sha256": ["1" * 64, "2" * 64, "3" * 64],
        "execution_plan_sha256": "4" * 64,
        "bundle_commit": "a" * 40,
        "bundle_tree": "b" * 40,
        "bundle_manifest_sha256": bootstrap.sha256_file(bundle),
    })
    rebound_stdout = {
        "fetched_commit": "a" * 40 + "\n",
        "fetched_tree": "b" * 40 + "\n",
        "seal_parent": f'{"a" * 40} {"2" * 40}\n',
        "branch_head": "a" * 40 + "\n",
    }
    for command in summary_payload["commands"]:
        kind = command["trace_kind"]
        if kind == "seal_parent":
            command["argv"][-1] = "a" * 40
        elif kind == "branch_switch":
            command["argv"][-1] = "a" * 40
        if kind in rebound_stdout:
            command["stdout_sha256"] = hashlib.sha256(
                rebound_stdout[kind].encode("utf-8")
            ).hexdigest()
    summary.write_bytes(bootstrap.canonical_json_bytes(summary_payload) + b"\n")
    journal = bootstrap.initialize_journal(runtime, summary, require_tmp_parent=False)
    matrix_manifest = (
        (tmp_path / "repository")
        / "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json"
    )
    matrix_manifest.parent.mkdir(parents=True)
    matrix_manifest.write_text(json.dumps({"nodes": [{"node_id": "f.py::test_node"}]}) + "\n")
    vm_green_report = runtime / bootstrap.VM_GREEN_REPORT_NAME
    vm_green_report.write_bytes(bootstrap.canonical_json_bytes({
        "schema_version": 1,
        "phase": "green",
        "vm_run": True,
        "manifest_sha256": bootstrap.sha256_file(matrix_manifest),
        "evidence_request_count": 0,
        "records": [{"node_id": "f.py::test_node", "outcome": "PASS"}],
        "full_suite": {"passed": 549, "warnings": 10, "duration_seconds": 420.0},
        "full_suite_network_spy_count": 0,
    }) + b"\n")
    repository = tmp_path / "repository"
    repository.mkdir(exist_ok=True)
    bootstrap.verify_bundle = lambda **kwargs: {"head": "a" * 40}
    monkeypatch.setattr(bootstrap, "_verify_vm_green_journal_lineage", lambda **kwargs: None)
    bootstrap._common.verify_frozen_inputs = lambda **kwargs: {
        "r2_tree": "2e8fe75233bed73c9facb1c66b5d72b6a172487d",
        "r2_path_count": 634,
        "admission_blob": "5ef073d4d6297639695491c46d20733236bede52",
        "batch3_deny_consistent": True,
    }
    seal = bootstrap.materialize_pre_network_seal(
        bundle_seal=bundle,
        bundle_manifest_sha256=bootstrap.sha256_file(bundle),
        execution_plan_sha256="4" * 64,
        vm_green_report=vm_green_report,
        root=repository,
        runtime_root=runtime,
        journal=journal,
        session="fresh-session",
        model="cursor-grok-4.5-high-fast",
        bundle_commit="a" * 40,
        bundle_tree="b" * 40,
    )
    output = repository / bootstrap.VM_SEAL_REL
    assert seal["spool_sha256"] == bootstrap.sha256_file(summary)
    assert seal["evidence_request_count"] == 0
    assert seal["frozen_inputs"]["r2_path_count"] == 634
    assert seal["vm_green_report_sha256"] == bootstrap.sha256_file(vm_green_report)
    assert seal["vm_green_report"]["records"][0]["outcome"] == "PASS"
    assert seal["vm_green"]["full_suite"]["passed"] == 549
    assert seal["environment_seal_commit_command"] == [
        "git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"
    ]
    assert output.read_bytes() == bootstrap.canonical_json_bytes(seal) + b"\n"
