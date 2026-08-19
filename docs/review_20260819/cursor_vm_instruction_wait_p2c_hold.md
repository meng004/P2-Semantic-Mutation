# Cursor VM instruction — WAIT (SUPERSEDED)

**Superseded** by `docs/review_20260819/cursor_vm_instruction_2026-08-19-005.md`
(author one-archive + cmake exception). Do not paste this WAIT block into
a new VM. The authorized next input is packet 005.

Historical WAIT text below is **void**. Do not execute it.

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
STATUS=AUTHOR_STRING_REFUSED_NO_TREE
TOKEN=none
PARENT=none
HEAD=none
REF=origin/cursor/phase2-c0-p2a-packet-a558
AUTHORITY=docs/review_20260819/author_string_2026-08-19-tree-present-refused.md
AUTHORITY_COMMIT=987f6bc1
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
WAITING_FOR_EXACT_STRING=none
WAITING_FOR=disk evidence on reviewer VM or named executor: extracted/1f67b3f3... directory OR archives/1f67b3f3....tar sha256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c
WAITING_STRING_MEANING=the token P2C_EXTRACTED_TREE_PRESENT_ON_EXECUTOR_VM=yes was received and refused on 2026-08-19. Repeating it is not new evidence. This WAIT VM must not start work, download P12, or cmake.
UNTIL_THEN_FORBIDDEN=P2-C remainder; P2-D L_t/U_t; booking remaining frozen rows as missing-only terminals (rejected option B); cmake; P12 download; claim upgrade; packet 005; re-issue 004 without a tree; treat verbal yes as a tree
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
