# P3 双角色初始化（2026-08-19）

**评审模型完整指令（整段粘贴）：**  
`docs/task-instructions/2026-08-19-review-model-init.md`

该文件是评审模型的唯一会话级权威。不要再使用旧的通用 Phase 2 / C++ qualification 剧本。

| 角色 | 主责 |
|---|---|
| **评审模型** | 独立核验、Standards + Spec 双轴、`PASS`/`BLOCKED`、纠偏签发、主线推进 |
| **Cursor VM** | 只执行评审模型签发的完整指令；不得自行签发 `SOL_*` token |
| **用户** | 科学运行、实现启动、重大范围变化、PR 的最终授权者 |

当前主线：B-POCKETFFT-001 adapter materialization correction。  
评审模型启动后必须立即双审固定远端 `CORRECTION_2_HEAD=dc9da765105e7fbc8229e407f71798f8338fa167`。  
`IMPLEMENTATION_AUTHORIZED=no`。旧 scientific authorization 已消费。未审 implementation/rotation/successor heads 不得当作已接受。

---

## 发给评审模型

把 `docs/task-instructions/2026-08-19-review-model-init.md` **全文**作为系统/首条指令。不要附加本文件的旧通用段落。

```text
按 docs/task-instructions/2026-08-19-review-model-init.md 全文初始化。
你是流程总控、独立评审者与 Gate 签发方。不要实现、不要 commit、不要 push。
第一动作：核验并双审 CORRECTION_2_HEAD=dc9da765105e7fbc8229e407f71798f8338fa167。
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

Cursor VM 环境没有 `rtk`。指令里的命令必须是普通 `git` / `python3` / `sha256sum` 等。

---

## Cursor VM 常驻禁区

- 不得把 `authorization.json` 的 `scientific_runs_authorized:true` 当作用户授权。
- 不得重用旧 scientific-run token 或旧 run attempt（`RUN_ATTEMPTS_REMAINING=0`）。
- 不得创建平行 implementation / successor / forensics 分支“再做一遍基础设施”。
- 不得 amend / reset / force-push 已审历史。
- 未经用户明确授权不得创建 PR。
- correction 若被签发：只改指令中的唯一允许文件，parent 必须是指令中的固定 HEAD。
