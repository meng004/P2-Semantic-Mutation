#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


PYTEST_SELECTION_ENV = (
    "PYTEST_ADDOPTS",
    "PYTEST_PLUGINS",
    "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
    "PYTHONSTARTUP",
    "PYTHONINSPECT",
    "PYTHONWARNINGS",
    "PYTHONOPTIMIZE",
    "COVERAGE_PROCESS_START",
)


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    nodes = payload.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise SystemExit("manifest nodes must be a nonempty list")
    ids = [entry.get("node_id") for entry in nodes]
    if len(ids) != len(set(ids)) or not all(isinstance(node, str) and node for node in ids):
        raise SystemExit("manifest node ids must be unique nonempty strings")
    return payload


def controlled_test_environment(root: Path, spy_root: Path, spy_log: Path) -> dict[str, str]:
    environment = dict(os.environ)
    for name in PYTEST_SELECTION_ENV:
        environment.pop(name, None)
    environment["PATH"] = str(spy_root) + os.pathsep + environment.get("PATH", "")
    environment["PYTHONPATH"] = str(spy_root) + os.pathsep + str(root / "src")
    environment["SUPPLEMENTAL_R3_NETWORK_SPY_LOG"] = str(spy_log)
    return environment


def checkout_identity(root: Path, executor) -> dict[str, str]:
    values = {}
    for key, revision in (("head", "HEAD"), ("tree", "HEAD^{tree}")):
        proc = executor(
            ["git", "-C", str(root), "rev-parse", revision],
            cwd=root,
            capture_output=True,
            check=False,
            shell=False,
        )
        value = proc.stdout.decode("ascii", errors="strict").strip()
        if proc.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", value) or proc.stderr:
            raise SystemExit(f"checkout {key} identity failed")
        values[key] = value
    return {"cwd": str(root), **values}


def run_phase(
    phase: str,
    manifest_path: Path,
    report_path: Path,
    *,
    run_full_suite: bool = False,
    vm_run: bool = False,
    executor=subprocess.run,
) -> int:
    manifest_path = manifest_path.resolve()
    root = manifest_path.parents[2]
    expected_manifest = (
        root
        / "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json"
    )
    if manifest_path != expected_manifest:
        raise SystemExit("manifest path does not identify one repository root")
    manifest = load_manifest(manifest_path)
    records = []
    full_suite = None
    full_suite_network_spy_count = None
    checkout = None if vm_run else checkout_identity(root, executor)
    with tempfile.TemporaryDirectory(prefix="supplemental-r3-a03-network-spy-") as spy_dir:
        spy_root = Path(spy_dir)
        spy_log = spy_root / "requests.jsonl"
        shim = spy_root / "network_shim.py"
        shim.write_text(
            "#!" + sys.executable + "\nimport json,os,sys\n"
            "with open(os.environ['SUPPLEMENTAL_R3_NETWORK_SPY_LOG'],'a',encoding='utf-8') as h: "
            "h.write(json.dumps({'argv':sys.argv})+'\\n')\nraise SystemExit(97)\n",
            encoding="utf-8",
        )
        shim.chmod(0o700)
        for name in ("gh", "curl", "wget", "http", "https", "ssh", "scp", "nc", "ncat"):
            (spy_root / name).symlink_to(shim)
        (spy_root / "sitecustomize.py").write_text(
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
        for entry in manifest["nodes"]:
            node = entry["node_id"]
            argv = [sys.executable, "-m", "pytest", "-q", "--maxfail=1", node]
            env = controlled_test_environment(root, spy_root, spy_log)
            before = len(spy_log.read_text(encoding="utf-8").splitlines()) if spy_log.exists() else 0
            red_root = None
            if phase == "red":
                red_root = tempfile.TemporaryDirectory(prefix="supplemental-r3-a03-red-root-")
                source_test = node.split("::", 1)[0]
                target_by_test = {
                    "tests/external_slice/test_supplemental_r3_ref_isolation.py": (
                        "scripts/external_slice/supplemental_r3_common.py"
                        if entry["red_signature"].endswith(":supplemental_r3_common")
                        else "scripts/external_slice/supplemental_r3_bootstrap.py"
                    ),
                    "tests/external_slice/test_mine_supplemental_r3.py": "scripts/external_slice/mine_supplemental_r3.py",
                    "tests/external_slice/test_check_supplemental_r3_admission.py": "scripts/external_slice/check_supplemental_r3_admission.py",
                    "tests/external_slice/test_check_supplemental_r3_handoff_hashes.py": "scripts/external_slice/check_supplemental_r3_handoff_hashes.py",
                }
                target = Path(red_root.name) / target_by_test[source_test]
                target.parent.mkdir(parents=True, exist_ok=True)
                signature = entry["red_signature"]
                target.write_text(
                    "def __getattr__(name):\n"
                    f"    raise AttributeError({(signature + ':symbol=')!r} + name)\n",
                    encoding="utf-8",
                )
                env["SUPPLEMENTAL_R3_MODULE_ROOT"] = red_root.name
            proc = executor(
                argv, cwd=root, capture_output=True, check=False, env=env, shell=False
            )
            after = len(spy_log.read_text(encoding="utf-8").splitlines()) if spy_log.exists() else 0
            network_count = after - before
            combined = proc.stdout + proc.stderr
            text = combined.decode("utf-8", errors="replace")
            if phase == "red":
                ok = proc.returncode != 0 and entry["red_signature"] in text and "1 failed" in text
            else:
                ok = proc.returncode == 0 and "1 passed" in text
            ok = ok and network_count == 0
            records.append({
                "node_id": node,
                "argv": argv,
                "exit_code": proc.returncode,
                "stdout_sha256": digest(proc.stdout),
                "stderr_sha256": digest(proc.stderr),
                "network_spy_count": network_count,
                "outcome": "PASS" if ok else "FAIL",
            })
            if not ok:
                sys.stderr.write(f"MATRIX_NODE_FAILED: {node}\n")
                sys.stderr.write(text)
                if red_root is not None:
                    red_root.cleanup()
                return 1
            if red_root is not None:
                red_root.cleanup()
        if run_full_suite:
            if phase != "green" or vm_run:
                raise SystemExit("local full suite is green Stage-A only")
            argv = [sys.executable, "-m", "pytest", "-q", "--maxfail=1"]
            env = controlled_test_environment(root, spy_root, spy_log)
            before = len(spy_log.read_text(encoding="utf-8").splitlines()) if spy_log.exists() else 0
            proc = executor(
                argv, cwd=root, capture_output=True, check=False, env=env, shell=False
            )
            after = len(spy_log.read_text(encoding="utf-8").splitlines()) if spy_log.exists() else 0
            full_suite_network_spy_count = after - before
            combined = proc.stdout + proc.stderr
            text = combined.decode("utf-8", errors="replace")
            match = re.search(
                r"(?P<passed>\d+) passed(?:, (?P<warnings>\d+) warnings?)? in "
                r"(?P<duration>\d+(?:\.\d+)?)s",
                text,
            )
            if proc.returncode != 0 or full_suite_network_spy_count != 0 or match is None:
                sys.stderr.write("LOCAL_FULL_SUITE_FAILED\n")
                sys.stderr.write(text)
                return 1
            full_suite = {
                "argv": argv,
                "exit_code": proc.returncode,
                "stdout_sha256": digest(proc.stdout),
                "stderr_sha256": digest(proc.stderr),
                "passed": int(match.group("passed")),
                "warnings": int(match.group("warnings") or 0),
                "duration_seconds": float(match.group("duration")),
            }
    payload = {
        "schema_version": 1,
        "phase": phase,
        "manifest_sha256": digest(manifest_path.read_bytes()),
        "evidence_request_count": sum(record["network_spy_count"] for record in records),
        "records": records,
        "vm_run": vm_run,
    }
    if checkout is not None:
        payload["checkout"] = checkout
    if full_suite is not None:
        payload["full_suite"] = full_suite
        payload["full_suite_network_spy_count"] = full_suite_network_spy_count
    report_path.write_bytes(canonical_bytes(payload) + b"\n")
    return 0


def verify_pair(red_path: Path, green_path: Path) -> int:
    red = json.loads(red_path.read_text(encoding="utf-8"))
    green = json.loads(green_path.read_text(encoding="utf-8"))
    red_nodes = [record["node_id"] for record in red["records"]]
    green_nodes = [record["node_id"] for record in green["records"]]
    if red_nodes != green_nodes:
        raise SystemExit("RED/GREEN node order differs")
    if red["manifest_sha256"] != green["manifest_sha256"]:
        raise SystemExit("RED/GREEN manifest hash differs")
    if red["evidence_request_count"] != 0 or green["evidence_request_count"] != 0:
        raise SystemExit("evidence request count is nonzero")
    if any(record["outcome"] != "PASS" for record in red["records"] + green["records"]):
        raise SystemExit("RED/GREEN contains failed matrix record")
    for phase, report in (("RED", red), ("GREEN", green)):
        checkout = report.get("checkout")
        if (
            not isinstance(checkout, dict)
            or set(checkout) != {"cwd", "head", "tree"}
            or not os.path.isabs(str(checkout.get("cwd", "")))
            or not re.fullmatch(r"[0-9a-f]{40}", str(checkout.get("head", "")))
            or not re.fullmatch(r"[0-9a-f]{40}", str(checkout.get("tree", "")))
        ):
            raise SystemExit(f"{phase} checkout identity is missing or invalid")
    if green.get("full_suite_network_spy_count") != 0:
        raise SystemExit("GREEN full-suite network spy count is nonzero or missing")
    full_suite = green.get("full_suite")
    if not isinstance(full_suite, dict) or full_suite.get("exit_code") != 0:
        raise SystemExit("GREEN full-suite proof is missing or failed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("red", "green"))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--verify-log-pair", action="store_true")
    parser.add_argument("--red-report", type=Path)
    parser.add_argument("--green-report", type=Path)
    parser.add_argument("--run-full-suite", action="store_true")
    parser.add_argument("--vm-run", action="store_true")
    args = parser.parse_args()
    if args.verify_log_pair:
        if args.red_report is None or args.green_report is None:
            parser.error("--verify-log-pair requires --red-report and --green-report")
        return verify_pair(args.red_report, args.green_report)
    if args.phase is None or args.manifest is None or args.report is None:
        parser.error("phase mode requires --phase, --manifest and --report")
    return run_phase(
        args.phase,
        args.manifest,
        args.report,
        run_full_suite=args.run_full_suite,
        vm_run=args.vm_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
