"""RED/GREEN Amendment 01 Bootstrap Addendum 01 ref-isolation gate tests.

Production modules are intentionally absent during RED. Each test lazily loads
exactly one production symbol so RED signatures are distinct and stable.
The Batch-3 deny identity is loaded only from SCOPE.json and is never embedded
as a second literal in this file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMMON = ROOT / "scripts/external_slice/supplemental_r3_common.py"
SCOPE_PATH = ROOT / "data/external_slice/supplemental_r3/SCOPE.json"
BOOTSTRAP_COMMANDS_PATH = (
    ROOT
    / "data/external_slice/supplemental_r3"
    / "BOOTSTRAP_COMMANDS_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json"
)
PLATFORM_HEAD = "3c518b8467f74c9a6efd11f2db267f9f30e1c822"
AUTHORITY = "31a4a8249f4ba6de12ba92291ab0cd55a65043b4"
PARENT_PLAN = "7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5"
ADDENDUM_PLAN = "7363445ea67618e9f5bb378a0b45eaad07ed4c57f9fcce87323d99a1a6d59c5b"
AUTH_FETCH = [
    "git",
    "fetch",
    "--no-tags",
    "origin",
    (
        "refs/heads/codex/phase3-supplemental-r3-ref-isolation-amendment:"
        "refs/remotes/origin/codex/phase3-supplemental-r3-ref-isolation-amendment"
    ),
]
BRANCH = (
    "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-01-evidence"
)
CANONICAL_ORIGIN = "https://github.com/meng004/P3-Semantic-Mutation"
CONFIGURED_WILDCARD_REFSPEC = "+refs/heads/*:refs/remotes/origin/*"
DIAGNOSTIC_PATHS = (
    "data/external_slice/supplemental_r3/"
    "FIRST_FAILURE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json",
    "data/external_slice/supplemental_r3/"
    "COMMAND_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json",
)


def _load_common_symbol(name: str):
    import importlib.util

    if not COMMON.is_file():
        raise AssertionError(f"missing production symbol: {name}")
    spec = importlib.util.spec_from_file_location("supplemental_r3_common", COMMON)
    mod = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(mod)
    if not hasattr(mod, name):
        raise AssertionError(f"missing production symbol: {name}")
    return getattr(mod, name)


def _deny_sha() -> str:
    return json.loads(SCOPE_PATH.read_text(encoding="utf-8"))["batch3_denylist"][
        "head_sha"
    ]


def _fixed_bootstrap_argvs() -> list[list[str]]:
    records = json.loads(BOOTSTRAP_COMMANDS_PATH.read_text(encoding="utf-8"))
    return [list(rec["argv"]) for rec in records]


def _assert_negative_terminal(result: Any, runner: Any) -> None:
    assert result.ok is False
    assert result.failed_invariant
    assert result.evidence_request_count == 0
    assert result.terminal is True
    assert getattr(result, "partial_payload", False) is False
    assert getattr(result, "retry_performed", False) is False
    assert runner.terminal is True
    assert runner.evidence_request_count == 0
    with pytest.raises(Exception):
        runner.run(["git", "status", "--porcelain=v1"])


def _make_spy_runner(CommandRunner: Any, *, deny: str, stale_ref: str | None = None):
    """Build a CommandRunner wired to an in-memory ref map and deny identity.

    Expected production constructor (or factory kwargs) shape:
      CommandRunner(
          deny_sha=...,
          ref_map={ref: sha, ...},   # optional in-memory synthetic refs
          on_stale_ref_access=callable that raises if enum/resolve/delete/object-read
      )
    """

    stale = stale_ref or "refs/remotes/origin/synthetic-unrelated-stale"
    accessed: list[str] = []

    def _on_stale_ref_access(action: str, ref: str) -> None:
        accessed.append(f"{action}:{ref}")
        raise AssertionError(
            f"stale-ref spy forbidden action={action!r} ref={ref!r}"
        )

    runner = CommandRunner(
        deny_sha=deny,
        ref_map={stale: deny},
        on_stale_ref_access=_on_stale_ref_access,
        stale_refs={stale},
    )
    runner._spy_accessed = accessed  # type: ignore[attr-defined]
    runner._spy_stale_ref = stale  # type: ignore[attr-defined]
    return runner


def _gate_kwargs() -> dict[str, Any]:
    return {
        "platform_head": PLATFORM_HEAD,
        "authority": AUTHORITY,
        "branch": BRANCH,
        "auth_fetch": list(AUTH_FETCH),
        "canonical_origin": CANONICAL_ORIGIN,
        "parent_plan_sha256": PARENT_PLAN,
        "addendum_plan_sha256": ADDENDUM_PLAN,
        "deny_sha": _deny_sha(),
        "fixed_main": PLATFORM_HEAD,
    }


def _run_gate(BootstrapGate: Any, runner: Any, **overrides: Any):
    """Call BootstrapGate(...).run_from(...) with synthetic fixture values.

    Production must accept these keyword arguments on ``run_from`` and return an
    object with attributes:
      ok, failed_invariant, evidence_request_count, commands, terminal,
      repository_writes
    plus optional: partial_payload, retry_performed, reached_stage.
    ``commands`` is the ordered list of argv lists actually executed.
    """

    params = {
        "initial_head": PLATFORM_HEAD,
        "status": "",
        "origin": CANONICAL_ORIGIN,
        "refspec": CONFIGURED_WILDCARD_REFSPEC,
        "fetched_authority": AUTHORITY,
        "branch_exists": False,
        "switch_ok": True,
        "post_switch_head": AUTHORITY,
        "post_switch_status": "",
        "ancestry_stream": [AUTHORITY],
        "main_is_ancestor": True,
        "authority_chain_ok": True,
        "active_inputs": [],
        "payload_lineage": [],
    }
    params.update(overrides)
    gate = BootstrapGate(runner, **_gate_kwargs())
    return gate.run_from(**params)


# ---------------------------------------------------------------------------
# 1–13, 18–20, 22, 30: BootstrapGate
# ---------------------------------------------------------------------------


def test_platform_head_mismatch_stops_before_status():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        initial_head="0" * 40,
    )
    assert result.ok is False
    assert result.failed_invariant == "platform_head"
    assert result.evidence_request_count == 0
    assert result.terminal is True
    assert result.repository_writes == []
    assert all(cmd[:2] != ["git", "status"] for cmd in result.commands)
    assert all(cmd[:2] != ["git", "fetch"] for cmd in result.commands)
    assert runner.evidence_request_count == 0


def test_platform_head_permits_status():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(BootstrapGate, runner, stop_after="status")
    assert result.ok is True or result.reached_stage in {"status", "origin", "done"}
    assert result.evidence_request_count == 0
    assert any(cmd[:2] == ["git", "status"] for cmd in result.commands) or (
        # production may treat injected status= as already observed
        result.reached_stage in {"status", "origin", "refspec", "done"}
    )
    assert all(cmd[:2] != ["git", "fetch"] for cmd in result.commands) or (
        result.reached_stage == "done"
    )


def test_dirty_status_stops_before_origin():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(BootstrapGate, runner, status=" M README.md\n")
    assert result.ok is False
    assert result.failed_invariant == "clean_status"
    assert result.evidence_request_count == 0
    assert result.repository_writes == []
    assert all("remote.origin.url" not in cmd for cmd in result.commands)
    assert all(cmd[:2] != ["git", "fetch"] for cmd in result.commands)


def test_clean_status_permits_origin():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(BootstrapGate, runner, status="", stop_after="origin")
    assert result.ok is True or result.reached_stage in {"origin", "refspec", "done"}
    assert result.evidence_request_count == 0
    assert result.failed_invariant != "clean_status"


def test_wrong_origin_stops_before_refspec():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        origin="https://example.invalid/not-the-canonical-origin",
    )
    assert result.ok is False
    assert result.failed_invariant == "canonical_origin"
    assert result.evidence_request_count == 0
    assert result.repository_writes == []
    assert all("remote.origin.fetch" not in cmd for cmd in result.commands)
    assert all(cmd[:2] != ["git", "fetch"] for cmd in result.commands)


def test_canonical_origin_permits_refspec():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        origin=CANONICAL_ORIGIN,
        stop_after="refspec",
    )
    assert result.ok is True or result.reached_stage in {"refspec", "fetch", "done"}
    assert result.evidence_request_count == 0
    assert result.failed_invariant != "canonical_origin"


def test_empty_refspec_stops_before_fetch():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(BootstrapGate, runner, refspec="")
    assert result.ok is False
    assert result.failed_invariant == "refspec_nonempty"
    assert result.evidence_request_count == 0
    assert result.repository_writes == []
    assert all(cmd[:2] != ["git", "fetch"] for cmd in result.commands)


def test_nonempty_refspec_permits_exact_fetch_only():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        refspec=CONFIGURED_WILDCARD_REFSPEC,
        stop_after="fetch",
    )
    fetch_cmds = [cmd for cmd in result.commands if cmd[:2] == ["git", "fetch"]]
    assert len(fetch_cmds) == 1
    assert fetch_cmds[0] == AUTH_FETCH
    assert result.evidence_request_count == 0


def test_wildcard_refspec_text_never_executed_as_fetch():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        refspec=CONFIGURED_WILDCARD_REFSPEC,
        stop_after="fetch",
    )
    for cmd in result.commands:
        if cmd[:2] == ["git", "fetch"]:
            assert "*" not in "".join(cmd)
            assert cmd == AUTH_FETCH
    assert result.evidence_request_count == 0


def test_second_or_different_fetch_is_terminal():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    # Inject an already-recorded foreign fetch; gate must go terminal and refuse
    # any additional fetch before evidence retrieval.
    result = _run_gate(
        BootstrapGate,
        runner,
        prior_fetches=[["git", "fetch", "origin", "refs/heads/other:refs/remotes/origin/other"]],
        attempt_second_fetch=True,
    )
    assert result.ok is False
    assert result.failed_invariant in {
        "fetch_once",
        "fetch_exact",
        "second_fetch",
    }
    assert result.terminal is True
    assert result.evidence_request_count == 0
    fetch_cmds = [cmd for cmd in result.commands if cmd[:2] == ["git", "fetch"]]
    assert len(fetch_cmds) <= 1
    _assert_negative_terminal(result, runner)


def test_fetched_authority_mismatch_stops_before_switch():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        fetched_authority="a" * 40,
    )
    assert result.ok is False
    assert result.failed_invariant == "fetched_authority"
    assert result.evidence_request_count == 0
    assert result.repository_writes == []
    assert all(cmd[:2] != ["git", "switch"] for cmd in result.commands)


def test_exact_authority_permits_addendum_branch_creation():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        fetched_authority=AUTHORITY,
        stop_after="switch",
    )
    switch_cmds = [cmd for cmd in result.commands if cmd[:2] == ["git", "switch"]]
    assert switch_cmds == [["git", "switch", "-c", BRANCH, AUTHORITY]]
    assert result.evidence_request_count == 0
    assert result.failed_invariant != "fetched_authority"


def test_preexisting_branch_or_switch_failure_terminal():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        branch_exists=True,
        switch_ok=False,
    )
    assert result.ok is False
    assert result.failed_invariant in {
        "branch_absent",
        "switch",
        "preexisting_branch",
    }
    assert result.terminal is True
    assert result.evidence_request_count == 0
    assert result.repository_writes == []
    # No delete/reset/repair/retry commands.
    joined = [" ".join(cmd) for cmd in result.commands]
    assert not any(" branch -D " in f" {c} " or c.endswith("branch -D") for c in joined)
    assert not any("reset" in c.split() for c in joined)
    assert not any("repair" in c for c in joined)
    _assert_negative_terminal(result, runner)


# ---------------------------------------------------------------------------
# 14–17, 21, 26–27, 32: CommandRunner
# ---------------------------------------------------------------------------


def test_successful_bootstrap_command_spy_trace():
    CommandRunner = _load_common_symbol("CommandRunner")
    BootstrapGate = _load_common_symbol("BootstrapGate")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(BootstrapGate, runner)
    expected = _fixed_bootstrap_argvs()
    # Byte-equivalent fixed sequential argv for the bootstrap gate stages.
    assert result.commands == expected
    assert result.ok is True
    assert result.evidence_request_count == 0
    assert result.repository_writes == []
    assert runner.evidence_request_count == 0
    # Platform HEAD bound to authority transition.
    assert result.commands[0] == ["git", "rev-parse", "HEAD"]
    assert ["git", "switch", "-c", BRANCH, AUTHORITY] in result.commands


def test_stale_ref_map_with_scope_deny_passes():
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    stale = "refs/remotes/origin/synthetic-unrelated-stale"
    runner = _make_spy_runner(CommandRunner, deny=deny, stale_ref=stale)
    # evaluate_stale_ref_map is the expected production API: pass/fail on an
    # in-memory map whose value equals the SCOPE-loaded deny identity without
    # enumerating, resolving, deleting, or reading the synthetic object.
    evaluate = getattr(runner, "evaluate_stale_ref_map", None)
    if evaluate is None:
        # Alternate expected shape: CommandRunner.gate_ref_map(ref_map) -> verdict
        evaluate = getattr(runner, "gate_ref_map", None)
    assert callable(evaluate), (
        "CommandRunner must expose evaluate_stale_ref_map(ref_map) "
        "or gate_ref_map(ref_map)"
    )
    ref_map = {stale: deny, "refs/heads/main": PLATFORM_HEAD}
    verdict = evaluate(ref_map)
    ok = verdict is True or getattr(verdict, "ok", None) is True
    assert ok is True
    assert runner._spy_accessed == []  # type: ignore[attr-defined]
    assert runner.evidence_request_count == 0


def test_stale_ref_rename_preserves_verdict_and_trace():
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    stale_a = "refs/remotes/origin/synthetic-unrelated-stale"
    stale_b = "refs/remotes/origin/synthetic-unrelated-stale-renamed"
    runner_a = _make_spy_runner(CommandRunner, deny=deny, stale_ref=stale_a)
    runner_b = _make_spy_runner(CommandRunner, deny=deny, stale_ref=stale_b)
    evaluate_a = getattr(runner_a, "evaluate_stale_ref_map", None) or getattr(
        runner_a, "gate_ref_map"
    )
    evaluate_b = getattr(runner_b, "evaluate_stale_ref_map", None) or getattr(
        runner_b, "gate_ref_map"
    )
    map_a = {stale_a: deny, "refs/heads/main": PLATFORM_HEAD}
    map_b = {stale_b: deny, "refs/heads/main": PLATFORM_HEAD}
    verdict_a = evaluate_a(map_a)
    verdict_b = evaluate_b(map_b)
    ok_a = verdict_a is True or getattr(verdict_a, "ok", None) is True
    ok_b = verdict_b is True or getattr(verdict_b, "ok", None) is True
    assert ok_a is True and ok_b is True
    # Renaming only the synthetic stale ref preserves verdict and spy trace.
    assert runner_a.commands == runner_b.commands
    assert runner_a._spy_accessed == runner_b._spy_accessed  # type: ignore[attr-defined]


def test_unrelated_ref_map_differences_preserve_verdict_trace():
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    stale = "refs/remotes/origin/synthetic-unrelated-stale"
    runner_a = _make_spy_runner(CommandRunner, deny=deny, stale_ref=stale)
    runner_b = _make_spy_runner(CommandRunner, deny=deny, stale_ref=stale)
    evaluate_a = getattr(runner_a, "evaluate_stale_ref_map", None) or getattr(
        runner_a, "gate_ref_map"
    )
    evaluate_b = getattr(runner_b, "evaluate_stale_ref_map", None) or getattr(
        runner_b, "gate_ref_map"
    )
    map_a = {
        stale: deny,
        "refs/heads/main": PLATFORM_HEAD,
        "refs/remotes/origin/noise-a": "b" * 40,
    }
    map_b = {
        stale: deny,
        "refs/heads/main": PLATFORM_HEAD,
        "refs/remotes/origin/noise-b": "c" * 40,
        "refs/tags/noise": "d" * 40,
    }
    verdict_a = evaluate_a(map_a)
    verdict_b = evaluate_b(map_b)
    ok_a = verdict_a is True or getattr(verdict_a, "ok", None) is True
    ok_b = verdict_b is True or getattr(verdict_b, "ok", None) is True
    assert ok_a is True and ok_b is True
    assert runner_a.commands == runner_b.commands


def test_deny_in_ancestry_stream_fails_before_retrieval():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        ancestry_stream=[AUTHORITY, deny, PLATFORM_HEAD],
    )
    assert result.ok is False
    assert result.failed_invariant == "deny_absent_from_ancestry"
    assert result.evidence_request_count == 0
    _assert_negative_terminal(result, runner)


def test_deny_in_configured_refspec_text_fails_before_retrieval():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        refspec=f"refs/heads/evil/{deny}:refs/remotes/origin/evil",
    )
    assert result.ok is False
    assert result.failed_invariant == "deny_absent_from_refspec"
    assert result.evidence_request_count == 0
    assert all(cmd[:2] != ["git", "fetch"] for cmd in result.commands)
    _assert_negative_terminal(result, runner)


def test_wrong_main_or_authority_chain_fails_before_retrieval():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        main_is_ancestor=False,
        authority_chain_ok=False,
    )
    assert result.ok is False
    assert result.failed_invariant in {
        "fixed_main_ancestor",
        "authority_chain",
        "main_or_authority_chain",
    }
    assert result.evidence_request_count == 0
    _assert_negative_terminal(result, runner)


def test_command_targeting_deny_identity_fails():
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    forbidden_argvs = [
        ["git", "fetch", "origin", deny],
        ["git", "show", deny],
        ["git", "cat-file", "-t", deny],
        ["git", "checkout", deny],
        ["git", "switch", deny],
        ["git", "merge", deny],
        ["git", "rebase", deny],
        ["git", "cherry-pick", deny],
        ["git", "diff", deny],
        ["git", "log", deny],
        ["git", "branch", "--contains", deny],
        ["git", "merge-base", deny, AUTHORITY],
    ]
    for argv in forbidden_argvs:
        local = CommandRunner(deny_sha=deny)
        with pytest.raises(Exception):
            local.run(argv)
        assert local.terminal is True
        assert local.evidence_request_count == 0
        with pytest.raises(Exception):
            local.run(["git", "status", "--porcelain=v1"])


def test_batch3_active_input_or_payload_lineage_fails():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(
        BootstrapGate,
        runner,
        active_inputs=[
            {
                "kind": "payload_lineage",
                "source": "PR#6 Batch 3 payload",
                "head_sha": deny,
            }
        ],
        payload_lineage=["batch3", deny],
    )
    assert result.ok is False
    assert result.failed_invariant in {
        "batch3_lineage",
        "active_input_lineage",
        "payload_lineage",
    }
    assert result.evidence_request_count == 0
    _assert_negative_terminal(result, runner)


def test_second_literal_deny_in_fixture_fails():
    load_deny_from_scope = _load_common_symbol("load_deny_from_scope")
    deny = _deny_sha()
    # Fixture text that injects a second literal copy of the SCOPE deny value.
    fixture_text = f"seed\n{deny}\ntrailer\n"
    with pytest.raises(Exception) as excinfo:
        load_deny_from_scope(
            scope_path=SCOPE_PATH,
            scan_texts=[fixture_text],
            allow_scope_field=True,
        )
    msg = str(excinfo.value).lower()
    assert "literal" in msg or "second" in msg or "deny" in msg


def test_plan_hash_or_failure_provenance_drift_fails():
    assert_failure_provenance_intact = _load_common_symbol(
        "assert_failure_provenance_intact"
    )
    # One-byte drift in a locked plan hash must fail closed before retrieval.
    with pytest.raises(Exception):
        assert_failure_provenance_intact(
            root=ROOT,
            parent_plan_sha256="0" + PARENT_PLAN[1:],
            addendum_plan_sha256=ADDENDUM_PLAN,
        )
    with pytest.raises(Exception):
        assert_failure_provenance_intact(
            root=ROOT,
            parent_plan_sha256=PARENT_PLAN,
            addendum_plan_sha256="1" + ADDENDUM_PLAN[1:],
        )
    # Intact hashes must pass.
    assert_failure_provenance_intact(
        root=ROOT,
        parent_plan_sha256=PARENT_PLAN,
        addendum_plan_sha256=ADDENDUM_PLAN,
    )


def test_r2_byte_path_tree_drift_fails(tmp_path: Path):
    assert_r2_tree_frozen = _load_common_symbol("assert_r2_tree_frozen")
    # Mutating a frozen R2 collision input by one byte must fail.
    review_queue = ROOT / "data/external_slice/supplemental_r2/REVIEW_QUEUE.json"
    drifted = tmp_path / "REVIEW_QUEUE.json"
    drifted.write_bytes(review_queue.read_bytes() + b"\n")
    with pytest.raises(Exception):
        assert_r2_tree_frozen(
            root=ROOT,
            overrides={
                "data/external_slice/supplemental_r2/REVIEW_QUEUE.json": drifted,
            },
        )
    # Canonical tree must pass.
    assert_r2_tree_frozen(root=ROOT)


def test_negative_asserts_terminal_runner_and_zero_requests():
    CommandRunner = _load_common_symbol("CommandRunner")
    BootstrapGate = _load_common_symbol("BootstrapGate")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    result = _run_gate(BootstrapGate, runner, initial_head="f" * 40)
    _assert_negative_terminal(result, runner)
    assert result.repository_writes == []
    assert getattr(result, "partial_payload", False) is False


def test_pre_arm_failure_is_transcript_journal_only():
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny, shutdown_runner_armed=False)
    # Simulate a post-Task-1 / pre-arm failure path.
    fail = getattr(runner, "record_pre_arm_failure", None)
    assert callable(fail), (
        "CommandRunner must expose record_pre_arm_failure(reason) that journals "
        "only to transcript/external journal with zero diagnostic argv/commit/push"
    )
    outcome = fail("synthetic_pre_arm_failure")
    assert runner.evidence_request_count == 0
    assert runner.terminal is True
    commands = list(getattr(runner, "commands", []))
    assert not any("commit" in cmd for cmd in commands)
    assert not any("push" in cmd for cmd in commands)
    assert not any(
        "FIRST_FAILURE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json" in " ".join(cmd)
        for cmd in commands
    )
    assert not any(
        "COMMAND_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json" in " ".join(cmd)
        for cmd in commands
    )
    assert getattr(outcome, "repository_writes", []) == [] or outcome is None or (
        getattr(outcome, "repository_writes", None) in ([], None)
    )


def test_armed_shutdown_commit_only_two_diagnostic_paths(tmp_path: Path):
    run_shutdown_and_record = _load_common_symbol("run_shutdown_and_record")
    journal = tmp_path / "journal.jsonl"
    journal.write_text("", encoding="utf-8")
    state = tmp_path / "journal.jsonl.state.json"
    state.write_text(
        json.dumps(
            {
                "shutdown_runner_armed": True,
                "payload_tree_published": False,
                "terminal": False,
                "evidence_request_count": 0,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_shutdown_and_record(
        journal_path=journal,
        repo_root=repo,
        payload_commit_exists=False,
        reason="synthetic_armed_shutdown",
    )
    assert result.ok is True or getattr(result, "committed", False) is True
    written = list(getattr(result, "repository_writes", []) or getattr(result, "paths", []))
    assert set(written) == set(DIAGNOSTIC_PATHS)
    commands = list(getattr(result, "commands", []))
    assert any("commit" in cmd for cmd in commands)
    assert any(cmd[:2] == ["git", "push"] or "push" in cmd for cmd in commands)


def test_armed_shutdown_rejects_when_payload_commit_exists(tmp_path: Path):
    run_shutdown_and_record = _load_common_symbol("run_shutdown_and_record")
    journal = tmp_path / "journal.jsonl"
    journal.write_text("", encoding="utf-8")
    result = run_shutdown_and_record(
        journal_path=journal,
        repo_root=tmp_path / "repo",
        payload_commit_exists=True,
        reason="synthetic_payload_present",
    )
    assert result.ok is False or getattr(result, "rejected", False) is True
    commands = list(getattr(result, "commands", []))
    assert not any("commit" in cmd for cmd in commands)
    assert not any("push" in cmd for cmd in commands)


def test_task1_failure_zero_repo_writes_even_after_branch():
    BootstrapGate = _load_common_symbol("BootstrapGate")
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(deny_sha=deny)
    # Branch creation succeeds, then a later Task-1 assertion fails.
    result = _run_gate(
        BootstrapGate,
        runner,
        post_switch_head="e" * 40,  # SHA mismatch after switch
    )
    assert result.ok is False
    assert result.failed_invariant in {
        "post_switch_head",
        "post_switch_status",
        "task1_post_switch",
    }
    assert result.repository_writes == []
    assert result.evidence_request_count == 0
    commands = list(result.commands)
    assert not any("push" in cmd for cmd in commands)
    assert not any(
        cmd[:2] == ["git", "commit"] or (len(cmd) >= 2 and cmd[1] == "commit")
        for cmd in commands
    )


def test_publication_rollback_on_move_failure(tmp_path: Path):
    publish_payload_transaction = _load_common_symbol("publish_payload_transaction")
    repo = tmp_path / "repo"
    repo.mkdir()
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "payload.json").write_text('{"ok": true}\n', encoding="utf-8")
    pre_tree = {
        p.relative_to(repo).as_posix(): p.read_bytes()
        for p in repo.rglob("*")
        if p.is_file()
    }
    # Force a transactional move failure via a callback or flag.
    with pytest.raises(Exception):
        publish_payload_transaction(
            repo_root=repo,
            staging_root=staging,
            moves=[
                {
                    "src": staging / "payload.json",
                    "dst": repo / "data/external_slice/supplemental_r3/payload.json",
                },
                {
                    "src": staging / "missing-handoff.json",
                    "dst": repo / "data/external_slice/supplemental_r3/handoff.json",
                },
            ],
            fail_on_move_index=1,
        )
    post_tree = {
        p.relative_to(repo).as_posix(): p.read_bytes()
        for p in repo.rglob("*")
        if p.is_file()
    }
    assert post_tree == pre_tree


def test_post_publication_failures_skip_diagnostic_commit_push():
    CommandRunner = _load_common_symbol("CommandRunner")
    deny = _deny_sha()
    runner = CommandRunner(
        deny_sha=deny,
        shutdown_runner_armed=True,
        payload_tree_published=True,
    )
    handler = getattr(runner, "record_post_publication_failure", None)
    assert callable(handler), (
        "CommandRunner must expose record_post_publication_failure(reason) that "
        "skips diagnostic commit and push after successful publication"
    )
    outcome = handler("staged_check_failed")
    commands = list(getattr(runner, "commands", []))
    assert not any("commit" in cmd for cmd in commands)
    assert not any("push" in cmd for cmd in commands)
    assert runner.evidence_request_count == 0
    assert outcome is None or getattr(outcome, "diagnostic_commit", False) is False
