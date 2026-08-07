#!/usr/bin/env python3
"""Bundle and bootstrap closure validation for Supplemental R3 Addendum 03."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


def _load_common():
    path = Path(__file__).with_name("supplemental_r3_common.py")
    spec = importlib.util.spec_from_file_location("_supplemental_r3_common_bootstrap", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load supplemental_r3_common")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_common = _load_common()
GateError = _common.GateError
canonical_json_bytes = _common.canonical_json_bytes
atomic_write_bytes = _common.atomic_write_bytes
sha256_file = _common.sha256_file
utc_now = _common.utc_now

RUNTIME_PREFIX = "supplemental-r3-a01-bootstrap-addendum-03-"
SUMMARY_REL = "bootstrap-spool/task1-command-summary.json"
VM_SEAL_REL = Path("data/external_slice/supplemental_r3/PRE_NETWORK_AUTHORITY.json")
BUNDLE_MANIFEST_REL = Path("data/external_slice/supplemental_r3/EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json")
LOCAL_RED_REL = Path("data/external_slice/supplemental_r3/LOCAL_RED_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json")
LOCAL_GREEN_REL = Path("data/external_slice/supplemental_r3/LOCAL_GREEN_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json")
BUNDLE_PATHS = (
    "scripts/external_slice/supplemental_r3_common.py",
    "scripts/external_slice/supplemental_r3_bootstrap.py",
    "scripts/external_slice/mine_supplemental_r3.py",
    "scripts/external_slice/check_supplemental_r3_admission.py",
    "scripts/external_slice/check_supplemental_r3_handoff_hashes.py",
    "tests/external_slice/test_supplemental_r3_ref_isolation.py",
    "tests/external_slice/test_mine_supplemental_r3.py",
    "tests/external_slice/test_check_supplemental_r3_admission.py",
    "tests/external_slice/test_check_supplemental_r3_handoff_hashes.py",
    "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json",
    "tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py",
)
RED_PATHS = tuple(path for path in BUNDLE_PATHS if path.startswith("tests/"))
GREEN_PATHS = tuple(path for path in BUNDLE_PATHS if path.startswith("scripts/"))
SEAL_PATHS = (
    LOCAL_RED_REL.as_posix(),
    LOCAL_GREEN_REL.as_posix(),
    BUNDLE_MANIFEST_REL.as_posix(),
)
FAILED_SESSIONS = {
    "743f5552",
    "bc-9bcdda05-3350-49aa-b4c6-c60fbb236f30",
    "bc-1368031b-b5fa-43c2-9074-c49b862ca08e",
}
BOOTSTRAP_TRACE_KINDS = [
    "platform_head", "clean_status", "origin", "fetch_refspec", "authorization_fetch",
    "fetched_commit", "fetched_tree", "bundle_manifest", "red_parent", "green_parent",
    "seal_parent", "branch_switch", "branch_head", "branch_clean", "authority_tree",
    "r2_tree", "admission_blob", "runtime_allocate",
]
BUNDLE_BRANCH = "codex/supplemental-r3-amendment-01-execution-bundle-a03"
EVIDENCE_BRANCH = "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence"
VM_GREEN_REPORT_NAME = "vm-green-report.json"
ENVIRONMENT_VERIFIED_OPERATION = "verify_environment_seal"


def allocate_runtime() -> Path:
    root = Path(tempfile.mkdtemp(prefix=RUNTIME_PREFIX, dir="/tmp"))
    os.chmod(root, 0o700)
    if root.is_symlink() or stat.S_IMODE(root.stat().st_mode) != 0o700 or any(root.iterdir()):
        raise GateError("runtime_allocation")
    return root


def run_vm_green(
    *, root: Path, runtime_root: Path, journal: Path, output: Path
) -> dict[str, Any]:
    root = Path(root)
    runtime_root = Path(runtime_root)
    output = Path(output)
    if output != runtime_root / VM_GREEN_REPORT_NAME:
        raise GateError("vm_green_output")
    if output.exists() or output.is_symlink():
        raise GateError("vm_green_output_exists")
    summary = runtime_root / SUMMARY_REL
    validate_prejournal_layout_after_journal(runtime_root, summary, Path(journal))

    full_suite_spy_root: Path | None = None
    full_suite_spy_log: Path | None = None

    def executor(argv: Sequence[str]) -> tuple[int, bytes, bytes]:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(root / "src")
        if list(argv) == [sys.executable, "-m", "pytest", "-q"]:
            if full_suite_spy_root is None or full_suite_spy_log is None:
                raise GateError("vm_green_full_suite_spy")
            environment["PATH"] = (
                str(full_suite_spy_root) + os.pathsep + environment.get("PATH", "")
            )
            environment["PYTHONPATH"] = (
                str(full_suite_spy_root) + os.pathsep + str(root / "src")
            )
            environment["SUPPLEMENTAL_R3_NETWORK_SPY_LOG"] = str(full_suite_spy_log)
        proc = subprocess.run(
            list(argv),
            cwd=root,
            env=environment,
            capture_output=True,
            check=False,
            shell=False,
        )
        return proc.returncode, proc.stdout, proc.stderr

    runner = _common.TerminalCommandRunner(
        Path(journal), executor=executor, python_executable=sys.executable
    )
    operation_key = runner.begin_operation(
        "run_vm_green", {"root": str(root), "output": str(output)}
    )
    full_suite_spy_root = runtime_root / "vm-green-full-suite-network-spy"
    if full_suite_spy_root.exists() or full_suite_spy_root.is_symlink():
        raise GateError("vm_green_full_suite_spy_exists")
    full_suite_spy_root.mkdir(mode=0o700)
    full_suite_spy_log = full_suite_spy_root / "requests.jsonl"
    shim = full_suite_spy_root / "network_shim.py"
    shim.write_text(
        "#!" + sys.executable + "\nimport json,os,sys\n"
        "with open(os.environ['SUPPLEMENTAL_R3_NETWORK_SPY_LOG'],'a',encoding='utf-8') as h: "
        "h.write(json.dumps({'argv':sys.argv})+'\\n')\nraise SystemExit(97)\n",
        encoding="utf-8",
    )
    shim.chmod(0o700)
    for name in ("gh", "curl", "wget", "http", "https", "ssh", "scp", "nc", "ncat"):
        (full_suite_spy_root / name).symlink_to(shim)
    (full_suite_spy_root / "sitecustomize.py").write_text(
        "import json,os,socket\n"
        "def blocked(*args,**kwargs):\n"
        " with open(os.environ['SUPPLEMENTAL_R3_NETWORK_SPY_LOG'],'a',encoding='utf-8') as h: "
        "h.write(json.dumps({'argv':['python-socket']})+'\\n')\n"
        " raise OSError('SUPPLEMENTAL_R3_NETWORK_BLOCKED')\n"
        "socket.socket.connect=blocked\n"
        "socket.socket.connect_ex=blocked\n"
        "socket.create_connection=blocked\n",
        encoding="utf-8",
    )
    matrix_argv = [
        sys.executable,
        "tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py",
        "--phase",
        "green",
        "--manifest",
        "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json",
        "--report",
        str(output),
        "--vm-run",
    ]
    runner.run(matrix_argv)
    full_stdout, full_stderr = runner.run([sys.executable, "-m", "pytest", "-q"])
    full_text = (full_stdout + full_stderr).decode("utf-8", errors="replace")
    match = re.search(
        r"(?:=+\s+)?(?P<passed>\d+) passed(?:, (?P<warnings>\d+) warnings)? in "
        r"(?P<duration>[0-9]+(?:\.[0-9]+)?)s",
        full_text,
    )
    if match is None:
        raise GateError("vm_green_full_suite_summary")
    full_suite_network_count = (
        len(full_suite_spy_log.read_text(encoding="utf-8").splitlines())
        if full_suite_spy_log.exists()
        else 0
    )
    if full_suite_network_count != 0:
        raise GateError("vm_green_full_suite_network")
    report_raw = output.read_bytes()
    try:
        report = json.loads(report_raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"vm_green_report_json: {exc}") from exc
    matrix_manifest_path = (
        root / "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json"
    )
    try:
        matrix_manifest = json.loads(matrix_manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"vm_green_manifest_json: {exc}") from exc
    expected_nodes = [row.get("node_id") for row in matrix_manifest.get("nodes", [])]
    report_nodes = [row.get("node_id") for row in report.get("records", [])]
    if (
        report_raw != canonical_json_bytes(report) + b"\n"
        or report.get("schema_version") != 1
        or report.get("phase") != "green"
        or report.get("vm_run") is not True
        or report.get("manifest_sha256") != sha256_file(matrix_manifest_path)
        or report.get("evidence_request_count") != 0
        or not isinstance(report.get("records"), list)
        or not report["records"]
        or report_nodes != expected_nodes
        or any(record.get("outcome") != "PASS" for record in report["records"])
    ):
        raise GateError("vm_green_report")
    report["full_suite"] = {
        "passed": int(match.group("passed")),
        "warnings": int(match.group("warnings") or 0),
        "duration_seconds": float(match.group("duration")),
    }
    report["full_suite_network_spy_count"] = full_suite_network_count
    atomic_write_bytes(output, canonical_json_bytes(report) + b"\n")
    runner.complete_operation(
        operation_key,
        {
            "report_sha256": sha256_file(output),
            "node_count": len(report["records"]),
            "full_suite": report["full_suite"],
            "full_suite_network_spy_count": 0,
        },
    )
    return report


def _load_journal_records(journal: Path) -> tuple[list[bytes], list[dict[str, Any]]]:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for line in lines:
        try:
            record = json.loads(line.decode("utf-8"))
        except Exception as exc:
            raise GateError(f"journal_json: {exc}") from exc
        if line != canonical_json_bytes(record) + b"\n":
            raise GateError("journal_not_canonical")
        records.append(record)
    if [row.get("sequence") for row in records] != list(range(1, len(records) + 1)):
        raise GateError("journal_sequence")
    return lines, records


def _verify_vm_green_journal_lineage(
    *,
    journal: Path,
    root: Path,
    runtime_root: Path,
    report: dict[str, Any],
    require_tail: bool = True,
) -> None:
    _, records = _load_journal_records(journal)
    intents = [
        (index, row)
        for index, row in enumerate(records)
        if row.get("stage") == "operation_intent"
        and row.get("operation_name") == "run_vm_green"
    ]
    if len(intents) != 1:
        raise GateError("vm_green_journal_intent")
    index, intent = intents[0]
    report_python = report.get("records", [{}])[0].get("argv", [None])[0]
    if not isinstance(report_python, str) or not Path(report_python).is_absolute():
        raise GateError("vm_green_python_executable")
    expected_matrix = [
        report_python,
        "tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py",
        "--phase", "green",
        "--manifest", "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json",
        "--report", str(Path(runtime_root) / VM_GREEN_REPORT_NAME),
        "--vm-run",
    ]
    if index + 3 >= len(records):
        raise GateError("vm_green_journal_sequence")
    matrix_record, full_record, completion = records[index + 1:index + 4]
    if (
        intent.get("metadata")
        != {"root": str(Path(root)), "output": str(Path(runtime_root) / VM_GREEN_REPORT_NAME)}
        or matrix_record.get("stage") != "command"
        or matrix_record.get("argv") != expected_matrix
        or matrix_record.get("exit_code") != 0
        or matrix_record.get("evidence_request") is not False
        or full_record.get("stage") != "command"
        or full_record.get("argv") != [report_python, "-m", "pytest", "-q"]
        or full_record.get("exit_code") != 0
        or full_record.get("evidence_request") is not False
        or completion.get("stage") != "operation"
        or completion.get("operation_key") != intent.get("operation_key")
        or completion.get("metadata")
        != {
            "report_sha256": sha256_file(Path(runtime_root) / VM_GREEN_REPORT_NAME),
            "node_count": len(report["records"]),
            "full_suite": report["full_suite"],
            "full_suite_network_spy_count": 0,
        }
        or require_tail and index + 4 != len(records)
    ):
        raise GateError("vm_green_journal_sequence")
    expected_nodes = [
        row["node_id"]
        for row in json.loads(
            (
                Path(root)
                / "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json"
            ).read_text(encoding="utf-8")
        )["nodes"]
    ]
    if [row.get("node_id") for row in report["records"]] != expected_nodes:
        raise GateError("vm_green_node_order")
    for node, row in zip(expected_nodes, report["records"], strict=True):
        if (
            row.get("argv")
            != [report_python, "-m", "pytest", "-q", "--maxfail=1", node]
            or row.get("exit_code") != 0
            or row.get("network_spy_count") != 0
            or row.get("outcome") != "PASS"
            or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("stdout_sha256", "")))
            or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("stderr_sha256", "")))
        ):
            raise GateError("vm_green_node_record")


def _verify_environment_commit_journal_lineage(
    *, journal: Path, seal: dict[str, Any], seal_sha256: str
) -> None:
    lines, records = _load_journal_records(journal)
    count = seal.get("journal_record_count")
    if not isinstance(count, int) or count <= 0 or len(records) != count + 3:
        raise GateError("environment_commit_journal_sequence")
    intent = records[count - 1]
    completion, add_record, commit_record = records[count:count + 3]
    if (
        hashlib.sha256(b"".join(lines[:count])).hexdigest()
        != seal.get("journal_prefix_sha256")
        or intent.get("stage") != "operation_intent"
        or intent.get("operation_name") != "materialize_pre_network_seal"
        or completion.get("stage") != "operation"
        or completion.get("operation_key") != intent.get("operation_key")
        or completion.get("metadata") != {"sha256": seal_sha256}
        or add_record.get("stage") != "command"
        or add_record.get("argv") != ["git", "add", VM_SEAL_REL.as_posix()]
        or add_record.get("exit_code") != 0
        or add_record.get("evidence_request") is not False
        or commit_record.get("stage") != "command"
        or commit_record.get("argv")
        != ["git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"]
        or commit_record.get("exit_code") != 0
        or commit_record.get("evidence_request") is not False
    ):
        raise GateError("environment_commit_journal_sequence")


def validate_bootstrap_summary(payload: dict[str, Any]) -> None:
    if payload.get("protocol") != "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03":
        raise GateError("summary_protocol")
    session = str(payload.get("session", ""))
    if payload.get("model") != "cursor-grok-4.5-high-fast" or not session or any(session.startswith(item) for item in FAILED_SESSIONS):
        raise GateError("summary_session")
    locked = payload.get("locked_hashes", {})
    sha40_keys = (
        "authority", "platform_head", "red_commit", "green_commit",
        "bundle_commit", "bundle_tree",
    )
    sha64_keys = ("design_sha256", "bundle_manifest_sha256", "execution_plan_sha256")
    if any(not re.fullmatch(r"[0-9a-f]{40}", str(locked.get(key, ""))) for key in sha40_keys):
        raise GateError("summary_locked_hashes")
    if any(not re.fullmatch(r"[0-9a-f]{64}", str(locked.get(key, ""))) for key in sha64_keys):
        raise GateError("summary_locked_hashes")
    parents = locked.get("parent_plan_sha256")
    audits = locked.get("bundle_audit_sha256")
    if not isinstance(parents, list) or len(parents) != 3 or not all(re.fullmatch(r"[0-9a-f]{64}", str(item)) for item in parents):
        raise GateError("summary_parent_plans")
    if not isinstance(audits, list) or len(audits) != 2 or not all(re.fullmatch(r"[0-9a-f]{64}", str(item)) for item in audits):
        raise GateError("summary_bundle_audits")
    if locked["authority"] != "31a4a8249f4ba6de12ba92291ab0cd55a65043b4":
        raise GateError("summary_authority")
    if locked["platform_head"] != "3c518b8467f74c9a6efd11f2db267f9f30e1c822":
        raise GateError("summary_platform_head")
    commands = payload.get("commands")
    if not isinstance(commands, list) or [row.get("trace_kind") for row in commands] != BOOTSTRAP_TRACE_KINDS:
        raise GateError("summary_trace_kinds")
    if [row.get("sequence") for row in commands] != list(range(1, len(commands) + 1)):
        raise GateError("summary_sequence")
    if any(row.get("assertion") != "PASS" or row.get("exit_code") != 0 for row in commands):
        raise GateError("summary_assertions")
    if any(not isinstance(row.get("argv"), list) or not row["argv"] or row["argv"][0] == "rtk" for row in commands):
        raise GateError("summary_argv")
    fetches = [row for row in commands if row["argv"][:2] == ["git", "fetch"]]
    exact_fetch = [
        "git", "fetch", "--no-tags", "origin",
        f"+refs/heads/{BUNDLE_BRANCH}:refs/remotes/origin/{BUNDLE_BRANCH}",
    ]
    if len(fetches) != 1 or fetches[0]["argv"] != exact_fetch:
        raise GateError("summary_authorization_fetch")
    remote_ref = f"refs/remotes/origin/{BUNDLE_BRANCH}"
    expected_argv = {
        "platform_head": ["git", "rev-parse", "HEAD"],
        "clean_status": ["git", "status", "--porcelain=v1"],
        "origin": ["git", "remote", "get-url", "origin"],
        "fetch_refspec": ["git", "config", "--get-all", "remote.origin.fetch"],
        "authorization_fetch": exact_fetch,
        "fetched_commit": ["git", "rev-parse", remote_ref],
        "fetched_tree": ["git", "rev-parse", f"{remote_ref}^{{tree}}"],
        "bundle_manifest": ["shasum", "-a", "256", BUNDLE_MANIFEST_REL.as_posix()],
        "red_parent": ["git", "rev-list", "--parents", "-n", "1", locked["red_commit"]],
        "green_parent": ["git", "rev-list", "--parents", "-n", "1", locked["green_commit"]],
        "seal_parent": ["git", "rev-list", "--parents", "-n", "1", locked["bundle_commit"]],
        "branch_switch": ["git", "switch", "-c", EVIDENCE_BRANCH, locked["bundle_commit"]],
        "branch_head": ["git", "rev-parse", "HEAD"],
        "branch_clean": ["git", "status", "--porcelain=v1"],
        "authority_tree": ["git", "rev-parse", f'{locked["authority"]}^{{tree}}'],
        "r2_tree": [
            "git", "rev-parse", f'{locked["authority"]}:data/external_slice/supplemental_r2'
        ],
        "admission_blob": [
            "git", "rev-parse", f'{locked["authority"]}:data/external_slice/admission_sheet.csv'
        ],
        "runtime_allocate": [
            "python3", "scripts/external_slice/supplemental_r3_bootstrap.py", "allocate-runtime"
        ],
    }
    if any(row.get("argv") != expected_argv[row["trace_kind"]] for row in commands):
        raise GateError("summary_trace_argv")
    expected_stdout = {
        "platform_head": locked["platform_head"] + "\n",
        "clean_status": "",
        "origin": "https://github.com/meng004/P3-Semantic-Mutation\n",
        "fetched_commit": locked["bundle_commit"] + "\n",
        "fetched_tree": locked["bundle_tree"] + "\n",
        "red_parent": f'{locked["red_commit"]} {locked["authority"]}\n',
        "green_parent": f'{locked["green_commit"]} {locked["red_commit"]}\n',
        "seal_parent": f'{locked["bundle_commit"]} {locked["green_commit"]}\n',
        "branch_head": locked["bundle_commit"] + "\n",
        "branch_clean": "",
        "authority_tree": "a993c5537680358870e1dfaf9614a3c31b9f42d6\n",
        "r2_tree": "2e8fe75233bed73c9facb1c66b5d72b6a172487d\n",
        "admission_blob": "5ef073d4d6297639695491c46d20733236bede52\n",
    }
    for row in commands:
        expected = expected_stdout.get(row["trace_kind"])
        if expected is not None and row.get("stdout_sha256") != _common.sha256_bytes(
            expected.encode("utf-8")
        ):
            raise GateError(f'summary_stdout: {row["trace_kind"]}')


def _relative_tree(root: Path) -> list[str]:
    entries: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root).as_posix()
        if path.is_dir() and not path.is_symlink():
            continue
        entries.append(rel)
    return sorted(entries)


def validate_prejournal_layout(
    runtime_root: Path,
    summary_path: Path,
    *,
    require_tmp_parent: bool = True,
) -> dict[str, Any]:
    root = Path(runtime_root)
    summary = Path(summary_path)
    try:
        root_stat = os.lstat(root)
    except OSError as exc:
        raise GateError(f"runtime_root_missing: {exc}") from exc
    if not stat.S_ISDIR(root_stat.st_mode) or stat.S_ISLNK(root_stat.st_mode):
        raise GateError("runtime_root_type")
    if stat.S_IMODE(root_stat.st_mode) != 0o700:
        raise GateError("runtime_root_mode")
    if not root.name.startswith(RUNTIME_PREFIX):
        raise GateError("runtime_root_prefix")
    if require_tmp_parent and root.parent != Path("/tmp"):
        raise GateError("runtime_root_parent")
    expected_summary = root / SUMMARY_REL
    if summary != expected_summary:
        raise GateError("summary_path")
    spool = root / "bootstrap-spool"
    if not spool.is_dir() or spool.is_symlink():
        raise GateError("spool_type")
    if not summary.is_file() or summary.is_symlink() or summary.stat().st_nlink != 1:
        raise GateError("summary_type")
    entries = _relative_tree(root)
    if entries != [SUMMARY_REL]:
        raise GateError(f"prejournal_path_set: {entries!r}")
    for absent in (
        root / "command-journal.jsonl",
        root / "candidate",
        root / "red-report.json",
        root / "green-report.json",
    ):
        if absent.exists() or absent.is_symlink():
            raise GateError(f"prejournal_target_exists: {absent.name}")
    raw = summary.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"summary_json: {exc}") from exc
    if raw != canonical_json_bytes(payload) + b"\n":
        raise GateError("summary_not_canonical")
    if payload.get("runtime_root") != str(root):
        raise GateError("summary_runtime_root")
    if payload.get("evidence_request_count") != 0:
        raise GateError("summary_request_count")
    commands = payload.get("commands")
    if not isinstance(commands, list) or not commands:
        raise GateError("summary_commands")
    if [entry.get("sequence") for entry in commands] != list(range(1, len(commands) + 1)):
        raise GateError("summary_sequence")
    if any(entry.get("assertion") != "PASS" or entry.get("exit_code") != 0 for entry in commands):
        raise GateError("summary_assertions")
    validate_bootstrap_summary(payload)
    return {"summary_sha256": sha256_file(summary), "entries": entries, "payload": payload}


def initialize_journal(
    runtime_root: Path,
    summary_path: Path,
    *,
    require_tmp_parent: bool = True,
) -> Path:
    journal = Path(runtime_root) / "command-journal.jsonl"
    if journal.exists() or journal.is_symlink():
        raise GateError("journal_exists")
    validated = validate_prejournal_layout(
        runtime_root, summary_path, require_tmp_parent=require_tmp_parent
    )
    try:
        fd = os.open(journal, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise GateError("journal_exists") from exc
    try:
        commands = validated["payload"]["commands"]
        for entry in commands:
            record = dict(entry)
            record["stage"] = "bootstrap_import"
            record["evidence_request"] = False
            record["runner_state"] = "active"
            os.write(fd, canonical_json_bytes(record) + b"\n")
        final = {
            "sequence": len(commands) + 1,
            "stage": "journal_initialized",
            "argv": ["supplemental_r3_bootstrap.py", "initialize-journal"],
            "started_at_utc": utc_now(),
            "ended_at_utc": utc_now(),
            "exit_code": 0,
            "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "evidence_request": False,
            "runner_state": "active",
            "summary_sha256": validated["summary_sha256"],
        }
        os.write(fd, canonical_json_bytes(final) + b"\n")
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(journal, 0o600)
    return journal


_FORBIDDEN_GIT = {
    ("git", "for-each-ref"),
    ("git", "show-ref"),
    ("git", "fsck"),
}


def evaluate_execution_closure(
    *,
    commands: Sequence[Sequence[str]],
    ancestry_ids: Sequence[str],
    configured_refspecs: Sequence[str],
    deny: str,
    stale_refs: dict[str, str],
) -> dict[str, Any]:
    del stale_refs
    trace = [list(command) for command in commands]
    for command in trace:
        if tuple(command[:2]) in _FORBIDDEN_GIT or command[:3] == ["git", "rev-list", "--all"]:
            raise GateError("forbidden_git_inventory")
    if deny in ancestry_ids or any(deny in refspec for refspec in configured_refspecs):
        raise GateError("deny_in_execution_closure")
    return {"verdict": "PASS", "trace": trace}


def verify_bundle_lineage(
    *,
    authority: str,
    red_commit: str,
    green_commit: str,
    seal_commit: str,
    parents: dict[str, Sequence[str]],
) -> None:
    expected = {
        red_commit: [authority],
        green_commit: [red_commit],
        seal_commit: [green_commit],
    }
    if parents != expected:
        raise GateError(f"bundle_lineage: {parents!r}")


def verify_bundle(
    *,
    runner: Any,
    root: Path,
    authority: str,
    red_commit: str,
    green_commit: str,
    seal_commit: str,
    bundle_tree: str,
    manifest: Path,
    manifest_sha256: str,
    expected_design_sha256: str,
    expected_parent_plan_sha256: Sequence[str],
    checkout_head: str | None = None,
) -> dict[str, Any]:
    root_text = str(Path(root))
    head_raw, _ = runner.run(["git", "-C", root_text, "rev-parse", "HEAD"])
    tree_raw, _ = runner.run([
        "git", "-C", root_text, "rev-parse", f"{seal_commit}^{{tree}}"
    ])
    if head_raw.decode("ascii").strip() != (checkout_head or seal_commit):
        raise GateError("bundle_head")
    if tree_raw.decode("ascii").strip() != bundle_tree:
        raise GateError("bundle_tree")
    parents: dict[str, list[str]] = {}
    for commit in (red_commit, green_commit, seal_commit):
        raw, _ = runner.run([
            "git", "-C", root_text, "rev-list", "--parents", "-n", "1", commit
        ])
        fields = raw.decode("ascii").strip().split()
        if not fields or fields[0] != commit:
            raise GateError("bundle_history")
        parents[commit] = fields[1:]
    verify_bundle_lineage(
        authority=authority,
        red_commit=red_commit,
        green_commit=green_commit,
        seal_commit=seal_commit,
        parents=parents,
    )
    authority_tree_raw, _ = runner.run([
        "git", "-C", root_text, "rev-parse", f"{authority}^{{tree}}"
    ])
    expected_changed = {
        red_commit: set(RED_PATHS),
        green_commit: set(GREEN_PATHS),
        seal_commit: set(SEAL_PATHS),
    }
    for commit, expected_paths in expected_changed.items():
        changed_raw, _ = runner.run([
            "git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r", commit
        ])
        changed = [line for line in changed_raw.decode("utf-8").splitlines() if line]
        if set(changed) != expected_paths or len(changed) != len(expected_paths):
            raise GateError(f"bundle_commit_paths: {commit}")
    manifest = Path(manifest)
    if manifest != Path(root) / BUNDLE_MANIFEST_REL:
        raise GateError("bundle_manifest_path")
    if sha256_file(manifest) != manifest_sha256:
        raise GateError("bundle_manifest_sha256")
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"bundle_manifest_json: {exc}") from exc
    if (
        payload.get("authority") != authority
        or payload.get("authority_tree") != authority_tree_raw.decode("ascii").strip()
        or payload.get("design_sha256") != expected_design_sha256
        or payload.get("commits", {}).get("red") != {"commit": red_commit, "parent": authority}
        or payload.get("commits", {}).get("green") != {"commit": green_commit, "parent": red_commit}
        or payload.get("parent_plan_sha256") != list(expected_parent_plan_sha256)
        or "plan_sha256" in payload
    ):
        raise GateError("bundle_manifest_bindings")
    file_hashes = payload.get("file_sha256")
    if not isinstance(file_hashes, dict) or set(file_hashes) != set(BUNDLE_PATHS):
        raise GateError("bundle_file_set")
    for relative, expected in file_hashes.items():
        path = Path(root) / relative
        if not path.is_file() or path.is_symlink() or sha256_file(path) != expected:
            raise GateError(f"bundle_file_sha256: {relative}")
    logs = payload.get("logs")
    expected_logs = {"red": LOCAL_RED_REL, "green": LOCAL_GREEN_REL}
    if not isinstance(logs, dict) or set(logs) != set(expected_logs):
        raise GateError("bundle_logs")
    for phase, relative in expected_logs.items():
        binding = logs.get(phase)
        path = Path(root) / relative
        if (
            not isinstance(binding, dict)
            or binding.get("path") != relative.as_posix()
            or not path.is_file()
            or path.is_symlink()
            or binding.get("sha256") != sha256_file(path)
        ):
            raise GateError(f"bundle_log_sha256: {phase}")
    if payload.get("allowed_bundle_paths") != list(BUNDLE_PATHS) + list(SEAL_PATHS):
        raise GateError("allowed_bundle_paths")
    status_raw, _ = runner.run([
        "git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"
    ])
    if status_raw:
        raise GateError("bundle_worktree_dirty")
    return {"head": seal_commit, "tree": bundle_tree, "manifest_sha256": manifest_sha256}


def _load_canonical_report(path: Path, expected_phase: str) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    try:
        report = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"{expected_phase}_report_json: {exc}") from exc
    if raw != canonical_json_bytes(report) + b"\n":
        raise GateError(f"{expected_phase}_report_not_canonical")
    if report.get("phase") != expected_phase:
        raise GateError(f"{expected_phase}_report_phase")
    if report.get("evidence_request_count") != 0:
        raise GateError(f"{expected_phase}_report_network")
    if not isinstance(report.get("records"), list):
        raise GateError(f"{expected_phase}_report_records")
    if expected_phase == "green":
        full_suite = report.get("full_suite")
        if (
            not isinstance(full_suite, dict)
            or not isinstance(full_suite.get("passed"), int)
            or full_suite.get("passed", 0) <= 0
            or not isinstance(full_suite.get("warnings"), int)
            or not isinstance(full_suite.get("duration_seconds"), (int, float))
        ):
            raise GateError("green_report_full_suite")
    return report


def _git_bytes(root: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(Path(root)), *args], capture_output=True, check=False, shell=False
    )
    if proc.returncode != 0:
        raise GateError(f"bundle_git: {list(args)!r}: {proc.stderr.decode('utf-8', errors='replace')}")
    return proc.stdout


def _tree_entries(root: Path, authority: str, prefix: str) -> list[dict[str, str]]:
    raw = _git_bytes(root, "ls-tree", "-r", "-z", authority, "--", prefix)
    entries: list[dict[str, str]] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, raw_path = item.split(b"\t", 1)
        mode, object_type, oid = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8")
        blob = _git_bytes(root, "show", f"{authority}:{path}")
        entries.append({
            "path": path,
            "mode": mode,
            "type": object_type,
            "oid": oid,
            "sha256": _common.sha256_bytes(blob),
        })
    return entries


def _bundle_git_identity(root: Path, authority: str) -> dict[str, Any]:
    green = _git_bytes(root, "rev-parse", "HEAD").decode("ascii").strip()
    green_line = _git_bytes(root, "rev-list", "--parents", "-n", "1", green).decode("ascii").strip().split()
    if len(green_line) != 2:
        raise GateError("green_parent")
    red = green_line[1]
    red_line = _git_bytes(root, "rev-list", "--parents", "-n", "1", red).decode("ascii").strip().split()
    if red_line != [red, authority]:
        raise GateError("red_parent")
    authority_tree = _git_bytes(root, "rev-parse", f"{authority}^{{tree}}").decode("ascii").strip()
    r2_tree = _git_bytes(root, "rev-parse", f"{authority}:data/external_slice/supplemental_r2").decode("ascii").strip()
    r2_entries = _tree_entries(root, authority, "data/external_slice/supplemental_r2")
    if r2_tree != "2e8fe75233bed73c9facb1c66b5d72b6a172487d" or len(r2_entries) != 634:
        raise GateError("r2_identity")
    r3_entries = _tree_entries(root, authority, "data/external_slice/supplemental_r3")
    admission_blob = _git_bytes(
        root, "rev-parse", f"{authority}:data/external_slice/admission_sheet.csv"
    ).decode("ascii").strip()
    admission_bytes = _git_bytes(root, "show", f"{authority}:data/external_slice/admission_sheet.csv")
    return {
        "authority_tree": authority_tree,
        "red_commit": red,
        "red_parent": authority,
        "green_commit": green,
        "green_parent": red,
        "r2_tree": r2_tree,
        "r2_entries": r2_entries,
        "frozen_r3_entries": r3_entries,
        "admission_sheet": {"blob": admission_blob, "sha256": _common.sha256_bytes(admission_bytes)},
    }


def _environment_identity(root: Path) -> dict[str, Any]:
    import pytest

    dependency_files = {}
    for relative in ("pyproject.toml", "uv.lock", "requirements.txt", "requirements-dev.txt"):
        path = Path(root) / relative
        if path.is_file():
            dependency_files[relative] = sha256_file(path)
    return {
        "python": sys.version,
        "pytest": pytest.__version__,
        "git": _git_bytes(root, "--version").decode("utf-8").strip(),
        "os": platform.platform(),
        "dependency_files": dependency_files,
    }


def build_bundle_seal(
    *,
    root: Path,
    red_report: Path,
    green_report: Path,
    output: Path,
    authority: str,
    design_sha256: str,
    parent_plan_sha256: Sequence[str],
    enforce_output_paths: bool = True,
) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", authority):
        raise GateError("authority_sha")
    if not re.fullmatch(r"[0-9a-f]{64}", design_sha256):
        raise GateError("design_sha256")
    plans = list(parent_plan_sha256)
    if len(plans) != 3 or not all(re.fullmatch(r"[0-9a-f]{64}", item) for item in plans):
        raise GateError("parent_plan_sha256")
    root = Path(root)
    if enforce_output_paths and (
        Path(red_report) != root / LOCAL_RED_REL
        or Path(green_report) != root / LOCAL_GREEN_REL
        or Path(output) != root / BUNDLE_MANIFEST_REL
    ):
        raise GateError("bundle_output_paths")
    red = _load_canonical_report(red_report, "red")
    green = _load_canonical_report(green_report, "green")
    file_sha256: dict[str, str] = {}
    for relative in BUNDLE_PATHS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise GateError(f"bundle_path: {relative}")
        file_sha256[relative] = sha256_file(path)
    git_identity = _bundle_git_identity(root, authority)
    environment = _environment_identity(root)
    payload = {
        "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03",
        "amendment_id": "AMENDMENT_01_REF_ISOLATION",
        "bootstrap_addendum_id": "BOOTSTRAP_EXECUTION_ADDENDUM_03",
        "authority": authority,
        "design_sha256": design_sha256,
        "parent_plan_sha256": plans,
        "authority_tree": git_identity["authority_tree"],
        "commits": {
            "red": {"commit": git_identity["red_commit"], "parent": git_identity["red_parent"]},
            "green": {"commit": git_identity["green_commit"], "parent": git_identity["green_parent"]},
        },
        "file_sha256": file_sha256,
        "logs": {
            "red": {"path": LOCAL_RED_REL.as_posix(), "sha256": sha256_file(Path(red_report))},
            "green": {"path": LOCAL_GREEN_REL.as_posix(), "sha256": sha256_file(Path(green_report)), "full_suite": green["full_suite"]},
        },
        "test_counts": {"red": len(red["records"]), "green": len(green["records"])},
        "environment": environment,
        "frozen_inputs": {
            "r2_tree": git_identity["r2_tree"],
            "r2_entries": git_identity["r2_entries"],
            "original_r3_entries": git_identity["frozen_r3_entries"],
            "admission_sheet": git_identity["admission_sheet"],
            "batch3_deny_consistency": "PASS_NO_VALUE_EMITTED",
        },
        "allowed_bundle_paths": list(BUNDLE_PATHS) + [
            LOCAL_RED_REL.as_posix(), LOCAL_GREEN_REL.as_posix(), BUNDLE_MANIFEST_REL.as_posix()
        ],
        "future_cli_schemas": {
            "common": {
                "run-command": ["--journal", "command_argv..."],
                "run-shutdown-diagnostic": ["--journal"],
            },
            "bootstrap": {
                "allocate-runtime": [],
                "initialize-journal": ["--runtime-root", "--summary"],
                "verify-bundle": [
                    "--authority", "--red-commit", "--green-commit", "--seal-commit",
                    "--bundle-tree", "--manifest", "--manifest-sha256", "--design-sha256",
                    "--parent-plan-sha256", "--root", "--journal",
                ],
                "run-vm-green": [
                    "--root", "--runtime-root", "--journal", "--output",
                ],
                "verify-environment-seal": [
                    "--root", "--runtime-root", "--journal",
                ],
                "materialize-seal": [
                    "--bundle-seal", "--root", "--runtime-root", "--journal", "--session",
                    "--model", "--bundle-commit", "--bundle-tree",
                    "--bundle-manifest-sha256", "--execution-plan-sha256",
                    "--vm-green-report",
                ],
            },
            "miner": {
                "execute": ["--root", "--candidate-root", "--authority", "--journal"]
            },
            "admission": {
                operation: [
                    "--root", "--candidate-root", "--authority", "--journal", "--branch"
                ]
                for operation in ("build-payload", "verify-payload", "publish-payload")
            },
            "handoff": {
                "verify-staged-payload": ["--root", "--authority", "--journal"],
                "build-handoff": ["--root", "--authority", "--journal", "--output"],
                "verify-handoff": ["--root", "--authority", "--journal", "--handoff"],
                "push-once": [
                    "--root", "--journal", "--handoff", "--handoff-commit",
                ],
                "verify-push-journal": ["--root", "--journal"],
            },
        },
        "limitations": [
            "candidate evidence only", "requires later Local Desktop evidence audit",
            "no readiness/r8/freeze/PR/merge/downstream execution",
        ],
        "zero_network": {"evidence_request_count": 0},
        "network_entrypoint_closure": _common.audit_network_source_closure(
            root, BUNDLE_PATHS[:5]
        ),
    }
    atomic_write_bytes(Path(output), canonical_json_bytes(payload) + b"\n")
    return payload


def materialize_pre_network_seal(
    *,
    bundle_seal: Path,
    bundle_manifest_sha256: str,
    execution_plan_sha256: str,
    vm_green_report: Path,
    root: Path,
    runtime_root: Path,
    journal: Path,
    session: str,
    model: str,
    bundle_commit: str,
    bundle_tree: str,
) -> dict[str, Any]:
    if not session or any(session == item or session.startswith(item) for item in FAILED_SESSIONS):
        raise GateError("session_identity")
    if model != "cursor-grok-4.5-high-fast":
        raise GateError("model_identity")
    if not re.fullmatch(r"[0-9a-f]{40}", bundle_commit) or not re.fullmatch(r"[0-9a-f]{40}", bundle_tree):
        raise GateError("bundle_identity")
    runtime_root = Path(runtime_root)
    summary = runtime_root / SUMMARY_REL
    validate_prejournal_layout_after_journal(runtime_root, summary, Path(journal))
    summary_raw = summary.read_bytes()
    try:
        summary_payload = json.loads(summary_raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"summary_json: {exc}") from exc
    if summary_raw != canonical_json_bytes(summary_payload) + b"\n":
        raise GateError("summary_not_canonical")
    validate_bootstrap_summary(summary_payload)
    vm_green_path = Path(vm_green_report)
    if vm_green_path != runtime_root / VM_GREEN_REPORT_NAME:
        raise GateError("vm_green_output")
    vm_green_raw = vm_green_path.read_bytes()
    try:
        vm_green = json.loads(vm_green_raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"vm_green_report_json: {exc}") from exc
    if (
        vm_green_raw != canonical_json_bytes(vm_green) + b"\n"
        or vm_green.get("phase") != "green"
        or vm_green.get("vm_run") is not True
        or vm_green.get("evidence_request_count") != 0
        or not isinstance(vm_green.get("records"), list)
        or not vm_green["records"]
        or not isinstance(vm_green.get("full_suite"), dict)
        or vm_green["full_suite"].get("passed", 0) <= 0
        or vm_green.get("full_suite_network_spy_count") != 0
    ):
        raise GateError("vm_green_report")
    _verify_vm_green_journal_lineage(
        journal=Path(journal),
        root=Path(root),
        runtime_root=runtime_root,
        report=vm_green,
    )
    bundle_raw = Path(bundle_seal).read_bytes()
    try:
        bundle = json.loads(bundle_raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"bundle_seal_json: {exc}") from exc
    if bundle_raw != canonical_json_bytes(bundle) + b"\n":
        raise GateError("bundle_seal_not_canonical")
    if bundle.get("protocol") != "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03":
        raise GateError("bundle_protocol")
    if bundle.get("zero_network", {}).get("evidence_request_count") != 0:
        raise GateError("bundle_network")
    matrix_manifest_path = (
        Path(root)
        / "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json"
    )
    if (
        vm_green.get("manifest_sha256") != sha256_file(matrix_manifest_path)
        or len(vm_green["records"]) != bundle.get("test_counts", {}).get("green")
    ):
        raise GateError("vm_green_bundle_binding")
    if bundle.get("authority") is None or not re.fullmatch(r"[0-9a-f]{64}", str(bundle.get("design_sha256", ""))):
        raise GateError("bundle_bindings")
    parent_plans = bundle.get("parent_plan_sha256")
    if not isinstance(parent_plans, list) or len(parent_plans) != 3 or not all(re.fullmatch(r"[0-9a-f]{64}", str(item)) for item in parent_plans):
        raise GateError("bundle_plan_lineage")
    if not re.fullmatch(r"[0-9a-f]{64}", execution_plan_sha256):
        raise GateError("execution_plan_sha256")
    locked = summary_payload["locked_hashes"]
    actual_manifest_sha256 = sha256_file(Path(bundle_seal))
    if (
        locked.get("authority") != bundle.get("authority")
        or locked.get("design_sha256") != bundle.get("design_sha256")
        or locked.get("parent_plan_sha256") != parent_plans
        or locked.get("execution_plan_sha256") != execution_plan_sha256
        or locked.get("bundle_commit") != bundle_commit
        or locked.get("bundle_tree") != bundle_tree
        or locked.get("bundle_manifest_sha256") != bundle_manifest_sha256
        or bundle_manifest_sha256 != actual_manifest_sha256
    ):
        raise GateError("summary_bundle_binding")
    commits = bundle.get("commits", {})
    red_binding = commits.get("red", {}) if isinstance(commits, dict) else {}
    green_binding = commits.get("green", {}) if isinstance(commits, dict) else {}
    runner = _common.TerminalCommandRunner(Path(journal))
    verify_bundle(
        runner=runner,
        root=Path(root),
        authority=bundle["authority"],
        red_commit=red_binding.get("commit", ""),
        green_commit=green_binding.get("commit", ""),
        seal_commit=bundle_commit,
        bundle_tree=bundle_tree,
        manifest=Path(bundle_seal),
        manifest_sha256=bundle_manifest_sha256,
        expected_design_sha256=locked["design_sha256"],
        expected_parent_plan_sha256=locked["parent_plan_sha256"],
    )
    frozen_inputs = _common.verify_frozen_inputs(
        root=Path(root),
        authority=bundle["authority"],
        runner=runner,
        expected_r2_entries=bundle.get("frozen_inputs", {}).get("r2_entries"),
        expected_original_r3_entries=bundle.get("frozen_inputs", {}).get("original_r3_entries"),
        expected_admission_sheet=bundle.get("frozen_inputs", {}).get("admission_sheet"),
    )
    operation_key = runner.begin_operation(
        "materialize_pre_network_seal",
        {"output": str(Path(root) / VM_SEAL_REL), "bundle_commit": bundle_commit},
    )
    payload = {
        "protocol": bundle["protocol"],
        "authority": bundle.get("authority"),
        "design_sha256": bundle.get("design_sha256"),
        "plan_sha256": list(parent_plans) + [execution_plan_sha256],
        "session": session,
        "model": model,
        "runtime_root": str(runtime_root),
        "bundle_commit": bundle_commit,
        "bundle_tree": bundle_tree,
        "bundle_manifest_sha256": actual_manifest_sha256,
        "spool_sha256": sha256_file(summary),
        "vm_green_report_sha256": sha256_file(vm_green_path),
        "vm_green_report": vm_green,
        "vm_green": {
            "node_count": len(vm_green["records"]),
            "full_suite": vm_green["full_suite"],
            "evidence_request_count": 0,
        },
        "environment_seal_commit_command": [
            "git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"
        ],
        "journal_prefix_sha256": sha256_file(Path(journal)),
        "journal_record_count": runner.sequence,
        "frozen_inputs": frozen_inputs,
        "evidence_request_count": 0,
    }
    output = Path(root) / VM_SEAL_REL
    if output.exists() or output.is_symlink():
        raise GateError("pre_network_seal_exists")
    atomic_write_bytes(Path(output), canonical_json_bytes(payload) + b"\n")
    runner.complete_operation(
        operation_key, {"sha256": sha256_file(output)}
    )
    return payload


def verify_environment_seal(
    *, root: Path, runtime_root: Path, journal: Path
) -> dict[str, Any]:
    root = Path(root)
    runtime_root = Path(runtime_root)
    journal = Path(journal)
    validate_prejournal_layout_after_journal(
        runtime_root, runtime_root / SUMMARY_REL, journal
    )
    seal_path = root / VM_SEAL_REL
    seal_raw = seal_path.read_bytes()
    try:
        seal = json.loads(seal_raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"environment_seal_json: {exc}") from exc
    if seal_raw != canonical_json_bytes(seal) + b"\n":
        raise GateError("environment_seal_not_canonical")
    _verify_environment_commit_journal_lineage(
        journal=journal,
        seal=seal,
        seal_sha256=sha256_file(seal_path),
    )
    embedded = seal.get("vm_green_report")
    vm_report_path = runtime_root / VM_GREEN_REPORT_NAME
    if (
        seal.get("protocol")
        != "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03"
        or not isinstance(embedded, dict)
        or sha256_file(vm_report_path) != seal.get("vm_green_report_sha256")
        or vm_report_path.read_bytes() != canonical_json_bytes(embedded) + b"\n"
        or embedded.get("phase") != "green"
        or embedded.get("vm_run") is not True
        or embedded.get("evidence_request_count") != 0
        or not isinstance(embedded.get("records"), list)
        or not embedded["records"]
        or any(row.get("outcome") != "PASS" for row in embedded["records"])
        or embedded.get("full_suite_network_spy_count") != 0
        or seal.get("vm_green")
        != {
            "node_count": len(embedded["records"]),
            "full_suite": embedded.get("full_suite"),
            "evidence_request_count": 0,
        }
    ):
        raise GateError("environment_vm_green_binding")
    _verify_vm_green_journal_lineage(
        journal=journal,
        root=root,
        runtime_root=runtime_root,
        report=embedded,
        require_tail=False,
    )
    bundle_path = root / BUNDLE_MANIFEST_REL
    if sha256_file(bundle_path) != seal.get("bundle_manifest_sha256"):
        raise GateError("environment_bundle_binding")
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    runner = _common.TerminalCommandRunner(journal)
    root_text = str(root)
    head_raw, _ = runner.run(["git", "-C", root_text, "rev-parse", "HEAD"])
    seal_commit = head_raw.decode("ascii").strip()
    history_raw, _ = runner.run([
        "git", "-C", root_text, "rev-list", "--parents", "-n", "1", seal_commit
    ])
    changed_raw, _ = runner.run([
        "git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r",
        seal_commit,
    ])
    committed_raw, _ = runner.run([
        "git", "-C", root_text, "show", f"{seal_commit}:{VM_SEAL_REL.as_posix()}"
    ])
    subject_raw, _ = runner.run([
        "git", "-C", root_text, "show", "-s", "--format=%s", seal_commit
    ])
    status_raw, _ = runner.run([
        "git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"
    ])
    if (
        history_raw.decode("ascii").strip().split()
        != [seal_commit, str(seal.get("bundle_commit"))]
        or changed_raw.decode("utf-8").splitlines() != [VM_SEAL_REL.as_posix()]
        or committed_raw != seal_raw
        or subject_raw.decode("utf-8").strip()
        != "evidence(external): seal Supplemental R3 environment"
        or status_raw
        or runner.evidence_request_count != 0
    ):
        raise GateError("environment_seal_history")
    commits = bundle.get("commits", {})
    verify_bundle(
        runner=runner,
        root=root,
        authority=str(seal.get("authority")),
        red_commit=str(commits.get("red", {}).get("commit", "")),
        green_commit=str(commits.get("green", {}).get("commit", "")),
        seal_commit=str(seal.get("bundle_commit")),
        bundle_tree=str(seal.get("bundle_tree")),
        manifest=bundle_path,
        manifest_sha256=str(seal.get("bundle_manifest_sha256")),
        expected_design_sha256=str(seal.get("design_sha256")),
        expected_parent_plan_sha256=list(seal.get("plan_sha256", []))[:3],
        checkout_head=seal_commit,
    )
    frozen = _common.verify_frozen_inputs(
        root=root,
        authority=str(seal.get("authority")),
        runner=runner,
        expected_r2_entries=bundle.get("frozen_inputs", {}).get("r2_entries"),
        expected_original_r3_entries=bundle.get("frozen_inputs", {}).get(
            "original_r3_entries"
        ),
        expected_admission_sheet=bundle.get("frozen_inputs", {}).get("admission_sheet"),
    )
    operation_key = runner.begin_operation(
        ENVIRONMENT_VERIFIED_OPERATION,
        {"seal_commit": seal_commit, "seal_sha256": sha256_file(seal_path)},
    )
    result = {
        "seal_commit": seal_commit,
        "seal_sha256": sha256_file(seal_path),
        "vm_green_report_sha256": seal["vm_green_report_sha256"],
        "frozen_inputs": frozen,
        "evidence_request_count": 0,
    }
    runner.complete_operation(operation_key, result)
    return result


def validate_prejournal_layout_after_journal(
    runtime_root: Path, summary_path: Path, journal: Path
) -> dict[str, Any]:
    root = Path(runtime_root)
    if Path(summary_path) != root / SUMMARY_REL or Path(journal) != root / "command-journal.jsonl":
        raise GateError("runtime_continuity")
    if not summary_path.is_file() or summary_path.is_symlink():
        raise GateError("summary_type")
    if not journal.is_file() or journal.is_symlink() or journal.stat().st_nlink != 1:
        raise GateError("journal_type")
    records: list[dict[str, Any]] = []
    for raw_line in journal.read_bytes().splitlines(keepends=True):
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except Exception as exc:
            raise GateError(f"journal_json: {exc}") from exc
        if raw_line != canonical_json_bytes(record) + b"\n":
            raise GateError("journal_not_canonical")
        records.append(record)
    if not records or [row.get("sequence") for row in records] != list(range(1, len(records) + 1)):
        raise GateError("journal_sequence")
    if any(row.get("evidence_request") is not False for row in records):
        raise GateError("journal_pre_network")
    command_stages = {"bootstrap_import", "journal_initialized", "command", "shutdown_command"}
    if any(
        row.get("stage") in command_stages and row.get("exit_code") != 0
        for row in records
    ):
        raise GateError("journal_pre_network")
    if any(row.get("runner_state") == "terminal" for row in records):
        raise GateError("journal_terminal")
    intents = {
        str(row.get("operation_key"))
        for row in records
        if row.get("stage") == "operation_intent" and row.get("operation_key")
    }
    completions = {
        str(row.get("operation_key"))
        for row in records
        if row.get("stage") == "operation" and row.get("operation_key")
    }
    if intents != completions:
        raise GateError("journal_pending_operation")
    return {"journal_record_count": len(records)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("allocate-runtime")
    initialize = commands.add_parser("initialize-journal")
    initialize.add_argument("--runtime-root", type=Path, required=True)
    initialize.add_argument("--summary", type=Path, required=True)
    verify = commands.add_parser("verify-bundle")
    verify.add_argument("--authority", required=True)
    verify.add_argument("--red-commit", required=True)
    verify.add_argument("--green-commit", required=True)
    verify.add_argument("--seal-commit", required=True)
    verify.add_argument("--bundle-tree", required=True)
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--manifest-sha256", required=True)
    verify.add_argument("--design-sha256", required=True)
    verify.add_argument("--parent-plan-sha256", action="append", required=True)
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("--journal", type=Path, required=True)
    vm_green = commands.add_parser("run-vm-green")
    vm_green.add_argument("--root", type=Path, required=True)
    vm_green.add_argument("--runtime-root", type=Path, required=True)
    vm_green.add_argument("--journal", type=Path, required=True)
    vm_green.add_argument("--output", type=Path, required=True)
    verify_environment = commands.add_parser("verify-environment-seal")
    verify_environment.add_argument("--root", type=Path, required=True)
    verify_environment.add_argument("--runtime-root", type=Path, required=True)
    verify_environment.add_argument("--journal", type=Path, required=True)
    materialize = commands.add_parser("materialize-seal")
    materialize.add_argument("--bundle-seal", type=Path, required=True)
    materialize.add_argument("--root", type=Path, required=True)
    materialize.add_argument("--runtime-root", type=Path, required=True)
    materialize.add_argument("--journal", type=Path, required=True)
    materialize.add_argument("--session", required=True)
    materialize.add_argument("--model", required=True)
    materialize.add_argument("--bundle-commit", required=True)
    materialize.add_argument("--bundle-tree", required=True)
    materialize.add_argument("--bundle-manifest-sha256", required=True)
    materialize.add_argument("--execution-plan-sha256", required=True)
    materialize.add_argument("--vm-green-report", type=Path, required=True)
    bundle = commands.add_parser("build-bundle-seal")
    bundle.add_argument("--root", type=Path, required=True)
    bundle.add_argument("--red-report", type=Path, required=True)
    bundle.add_argument("--green-report", type=Path, required=True)
    bundle.add_argument("--output", type=Path, required=True)
    bundle.add_argument("--authority", required=True)
    bundle.add_argument("--design-sha256", required=True)
    bundle.add_argument("--parent-plan-sha256", action="append", required=True)
    return parser


def _dispatch(args: argparse.Namespace, *, require_tmp_parent: bool) -> int:
    if args.command == "allocate-runtime":
        runtime = allocate_runtime()
        print((canonical_json_bytes({"runtime_root": str(runtime)}) + b"\n").decode("utf-8"), end="")
        return 0
    if args.command == "initialize-journal":
        initialize_journal(
            args.runtime_root, args.summary, require_tmp_parent=require_tmp_parent
        )
        return 0
    if args.command == "verify-bundle":
        runner = _common.TerminalCommandRunner(args.journal)
        verify_bundle(
            runner=runner,
            root=args.root,
            authority=args.authority,
            red_commit=args.red_commit,
            green_commit=args.green_commit,
            seal_commit=args.seal_commit,
            bundle_tree=args.bundle_tree,
            manifest=args.manifest,
            manifest_sha256=args.manifest_sha256,
            expected_design_sha256=args.design_sha256,
            expected_parent_plan_sha256=args.parent_plan_sha256,
        )
        return 0
    if args.command == "run-vm-green":
        run_vm_green(
            root=args.root,
            runtime_root=args.runtime_root,
            journal=args.journal,
            output=args.output,
        )
        return 0
    if args.command == "verify-environment-seal":
        verify_environment_seal(
            root=args.root,
            runtime_root=args.runtime_root,
            journal=args.journal,
        )
        return 0
    if args.command == "materialize-seal":
        materialize_pre_network_seal(
            bundle_seal=args.bundle_seal,
            bundle_manifest_sha256=args.bundle_manifest_sha256,
            execution_plan_sha256=args.execution_plan_sha256,
            vm_green_report=args.vm_green_report,
            root=args.root,
            runtime_root=args.runtime_root,
            journal=args.journal,
            session=args.session,
            model=args.model,
            bundle_commit=args.bundle_commit,
            bundle_tree=args.bundle_tree,
        )
        return 0
    if args.command == "build-bundle-seal":
        build_bundle_seal(
            root=args.root,
            red_report=args.red_report,
            green_report=args.green_report,
            output=args.output,
            authority=args.authority,
            design_sha256=args.design_sha256,
            parent_plan_sha256=args.parent_plan_sha256,
        )
        return 0
    raise GateError(f"unknown_command: {args.command}")


def main(argv: Sequence[str] | None = None, *, require_tmp_parent: bool = True) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _dispatch(args, require_tmp_parent=require_tmp_parent)
    except Exception as exc:
        journal = getattr(args, "journal", None)
        if args.command != "initialize-journal" and isinstance(journal, Path) and journal.is_file():
            _common.persist_cli_failure(journal, f"bootstrap_{args.command}", exc)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
