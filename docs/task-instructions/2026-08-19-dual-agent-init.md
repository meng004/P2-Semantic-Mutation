# P3 双角色初始化（2026-08-19）

**评审模型完整指令（整段粘贴）：**  
`docs/task-instructions/2026-08-19-review-model-init.md`

该文件是评审模型的唯一会话级权威。它按 P12 评审提示词的 Gate 体例写成，但战役是 **P3 论文 / Phase 2 证据**，不是 B-POCKETFFT-001。

| 角色 | 主责 |
|---|---|
| **评审模型** | 独立核验、Standards + Spec 双轴、`PASS`/`BLOCKED`、纠偏签发、主线推进 |
| **Cursor VM** | 只执行评审模型签发的完整指令；不得自行签发 `SOL_*` token |
| **用户** | 科学运行、实现启动、重大范围变化、PR 的最终授权者 |

当前主线：独立双审未接受的 P2-A 单受试 preflight 头  
`UNREVIEWED_P2A_HEAD=f270c31733ed575f59a80abb719c05a2326ac1c7`。  
`PHASE2_P2A_RECEIPT_ACCEPTED=no`。C++ qualification 已合入 `main`，但执行与 attempt-2 未授权。Boost.Math evidence 头与 #16–#19 不得当新主线。Claim 保持 `blocked`。不得写 TOSEM Results。

---

## 发给评审模型

把 `docs/task-instructions/2026-08-19-review-model-init.md` **全文**作为系统/首条指令。

```text
按 docs/task-instructions/2026-08-19-review-model-init.md 全文初始化。
你是 P3 论文的流程总控、独立评审者与 Gate 签发方。不要实现、不要 commit、不要 push。
第一动作：核验并双审 UNREVIEWED_P2A_HEAD=f270c31733ed575f59a80abb719c05a2326ac1c7。
C0 包 aa580894 只是未审计划，不是已接受 Gate。
然后按该文件第九节输出 Gate 和下一份 Cursor VM 完整指令。
在你发出 Gate 之前，Cursor VM 保持 WAIT。
```

---

## 发给 Cursor VM

只粘贴评审模型刚签发的那一份完整指令。没有该指令时，唯一合法动作是保持 WAIT。

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
<在此粘贴评审模型签发的 CURSOR_VM_INSTRUCTION>
```

Cursor VM 环境没有 `rtk`。指令里的命令必须是普通 `git` / `python3` / `sha256sum` / `pytest` 等。

---

## Cursor VM 常驻禁区

- 不得把未审 `preflight-result.json` 的 `status=PASS` 当成 Phase 2 关闭或 RQ 支持。
- 不得重跑 preflight，除非用户给出 `PHASE2_P2A_RERUN_AUTHORIZED=yes`。
- 不得执行 C++ qualification / attempt-2 / Boost.Math successor。
- 不得创建平行 qualification / forensics / 授权链分支。
- 不得 amend / reset / force-push 已审历史。
- 未经用户明确授权不得创建 PR。
- 不得改 `submission/TOSEM_*` Results，不得升级 claim，不得揭盲 P12。
