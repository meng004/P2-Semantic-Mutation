# Cursor VM instruction — WAIT (author A; post-004)

Issued after C1 `docs/review_20260819/2026-08-19-004_review.md`.
This is the only authorized Cursor VM input until the reviewer issues a
new `EXECUTION_PACKET`.

Paste the wrapper plus the `CURSOR_VM_INSTRUCTION` block into a new
Cursor VM. The VM must HARD STOP after confirming WAIT. It must not
invent P2-C remainder, P2-D, cmake, a P12 download, or packet 005.

The exact unblocking string is sent to the **评审模型**, not acted on
by this VM. Packet 004 already booked the process-argv row as
`E_SOURCE_TREE_ABSENT`. Repeating the old READY string is not a new
science packet.

---

## Wrapper (paste first)

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=WAIT_P2C_REMAINDER_AND_P2D
STATUS=AUTHOR_A_HOLD
TOKEN=none
PARENT=none
HEAD=none
REF=origin/cursor/phase2-c0-p2a-packet-a558
AUTHORITY=docs/review_20260819/author_decision_2026-08-19-A.md
AUTHORITY_COMMIT=a7af34f8
BRANCH=none
WORKTREE=none
ALLOWED_FILES=none
FORBIDDEN=create qualification/successor/forensics/boostmath branches; accept unreviewed heads as paper-citable; start P2-C remainder; start P2-D; profile another row; download P12; extract-by-fetch; cmake; meson; autotools; c++; qualify_cxx_link; Boost.Math; claim upgrade; P12 reveal; edit submission/TOSEM_*; open PR; rtk; merge #22/#23/#24/#25; issue next Gate; write execution_packet_2026-08-19-005; re-run packet 004 as missing-only copies
READINESS=wait
COMMANDS_EXECUTED=none
FILES_CHANGED=none
TESTS=do not run tests
COMMIT=none
PUSH=none
LS_REMOTE=none
EDITS=none
COMMIT_SUBJECT=none
TOPOLOGY=none
REPORT_FIELDS=phase,status,commands_executed,files_changed,waiting_for,hard_stop
WAITING_FOR_EXACT_STRING=P2C_EXTRACTED_TREE_PRESENT_ON_EXECUTOR_VM=yes
WAITING_STRING_MEANING=author asserts to the 评审模型 that an extracted tree or hash-matching local archive for subject 1f67b3f3 is actually present on a future executor VM. The 评审模型 must still confirm that tree on executor evidence before issuing a spawn-retry of the existing ltest process-argv seam. This WAIT VM must not interpret that string as a license to start work, download P12, or cmake.
UNTIL_THEN_FORBIDDEN=P2-C remainder; P2-D L_t/U_t; booking remaining frozen rows as missing-only terminals (rejected option B); cmake; P12 download; claim upgrade; packet 005; re-issue 004 without a tree
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```

## Closed vs blocked (do not reopen)

Closed minimum slices only: P2-A 1/35 preflight; P2-B synthetic
PILOT_ONLY PASS+FAIL; P2-C header row `E_SOURCE_TREE_ABSENT` (003);
P2-C process-argv row `E_SOURCE_TREE_ABSENT` (004). Process-argv
script exists on PR #25. Blocked: real `ltest` spawn, P2-C remainder,
P2-D, P2-E, P2-F, Phase 2 as a whole. Claims stay `blocked`.

## HARD STOP checklist

1. Do not `git checkout` a feature branch for this instruction.
2. Do not create or modify files.
3. Do not run pytest, preflight, profiling, or qualification.
4. Reply with `PHASE=WAIT_P2C_REMAINDER_AND_P2D`, `COMMANDS_EXECUTED=none`,
   `FILES_CHANGED=none`, then stop.
