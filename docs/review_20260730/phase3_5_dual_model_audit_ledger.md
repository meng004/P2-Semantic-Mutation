# Phase 3–5 双模型审计台账

## 1. 台账身份与固定元数据

本文件是 Phase 3–5 Cursor VM / Grok 执行产出进入本地 GPT Desktop / Sol 单一研究 lineage 的审计台账（SSOT）。记录按交接发生顺序追加；既有条目不得静默改写。finding 被修复时，应新增复核条目并引用原 finding，不得删除原始记录。

| 字段 | 固定值 |
|---|---|
| 台账建立日期 | 2026-07-30 |
| 本地审计分支 | `codex/gpt-desktop-phase3-5` |
| 台账建立前本地 HEAD | `6309c279ed5183cfc059f6a6f2b2dbafd3a3aae4` |
| 审计基线 | `main@d91083af4b368457245adbcc4d55ac2b2f786822` |
| Cursor 执行分支 | `origin/cursor/grok-phase3-5-execution` |
| Defect4MR 固定来源 commit | `2bf7c2401c846544e715d879eb639e8c3bf44067` |
| Defect4MR ledger blob | `1469a2e2b15dcb2cdf59d185f3ec92f58fb77189` |
| 审计报告目录 | `docs/review_20260730/` |

本地审计只提交本台账和各 gate 的门禁报告，不改写 Cursor 原始日志或原始运行结果。每个 gate 使用独立 commit；提交前必须运行：

```text
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
```

完整基线的预期结果为 `233 passed`。

S0 台账建立提交前实测：

| 日期 | 命令 | 退出码 | 结果 |
|---|---|---:|---|
| 2026-07-30 | `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q` | 0 | `233 passed, 10 warnings` |

## 2. Verdict 语义

审计 verdict 只能取以下三个值：

| Verdict | 语义 | 后继任务 |
|---|---|---|
| `PASS` | 零 blocker；交接证据完整且满足冻结协议。 | 可按依赖图解锁。 |
| `PASS_WITH_DISCLOSURE` | 方法学完整性未受损，但必须携带明确披露。 | 可按依赖图解锁，披露继续进入后继工件。 |
| `BLOCKED` | 存在 blocker、交接不完整或不可审计。 | 不得集成 Cursor 产出，不得启动依赖该 gate 的后继任务。 |

模型意见不以投票裁决。出现分歧时依次依据预注册冻结文件与 amendment、固定 hash、原始证据和已批准执行规格；仍无法裁决则保持 `BLOCKED` 并升级作者。

## 3. 追加记录合同

每次 Cursor 交接或 finding 修复复核必须新增一个独立条目，并完整记录：

1. gate 名称与交接/复核时间；
2. Cursor 分支、不可变 Cursor commit 和基线 commit；
3. handoff manifest 路径；
4. 全部输入路径及 SHA256；
5. 全部输出路径及 SHA256；
6. 实际执行的审计命令及退出码；
7. findings（含稳定 ID、严重性、证据与处置）；
8. verdict；
9. 本地集成 commit；若未集成则明确写 `N/A` 及原因；
10. 后继任务是否解锁，以及被解锁或继续锁定的精确任务。

不得用聊天摘要替代已 push 的不可变 commit、handoff manifest、命令记录和文件 hash。缺失值统一写为 `N/A（未交接）`，不得推测或补造。

### 3.1 条目模板

| 字段 | 记录 |
|---|---|
| Gate | `<gate 名称>` |
| 记录类型 | `<首次审计 / finding 修复复核>` |
| Cursor commit | `<完整 SHA>` |
| Cursor baseline | `<完整 SHA>` |
| Handoff manifest | `<路径与 SHA256>` |
| 输入 hash | `<路径 = SHA256；逐项列出>` |
| 输出 hash | `<路径 = SHA256；逐项列出>` |
| 审计命令 | `<精确命令、退出码与关键结果>` |
| Findings | `<finding ID、证据、处置>` |
| Verdict | `<PASS / PASS_WITH_DISCLOSURE / BLOCKED>` |
| 本地集成 commit | `<完整 SHA；未集成则 N/A 与原因>` |
| 后继任务是否解锁 | `<是/否；精确任务>` |

## 4. Gate 状态总览

| Gate | Cursor commit | Verdict | 本地集成 commit | 后继任务是否解锁 |
|---|---|---|---|---|
| Gate A0 — Defect4MR sanitized import | `785a95a4ba9f0b98403b6c65445f7f2eef602391`（仅盘点到任务指令；不是有效 handoff） | `BLOCKED` | `N/A`（未集成 Cursor 产出） | 否；Gate A1 及以后均未解锁 |

## 5. 交接审计记录

### 5.1 启动盘点：Gate A0 — Defect4MR sanitized import

| 字段 | 记录 |
|---|---|
| Gate | Gate A0 — Defect4MR sanitized import |
| 记录类型 | 启动盘点；尚无可审计的 Cursor handoff |
| 盘点日期 | 2026-07-30 |
| Cursor 分支 | `origin/cursor/grok-phase3-5-execution` |
| Cursor commit | `785a95a4ba9f0b98403b6c65445f7f2eef602391` |
| Cursor baseline | `d91083af4b368457245adbcc4d55ac2b2f786822` |
| Handoff manifest | `N/A（未交接）` |
| 输入 hash | `N/A（未交接）` |
| 输出 hash | `N/A（未交接）` |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（BLOCKED；未集成 Cursor 产出）` |
| 后继任务是否解锁 | 否。Gate A1 以及依赖 A0 的全部后继任务均未解锁。 |

#### 审计命令与结果

```text
rtk git rev-parse HEAD
# 6309c279ed5183cfc059f6a6f2b2dbafd3a3aae4

rtk git rev-parse main
# d91083af4b368457245adbcc4d55ac2b2f786822

rtk git rev-parse origin/cursor/grok-phase3-5-execution
# 785a95a4ba9f0b98403b6c65445f7f2eef602391

rtk git diff --name-status d91083af4b368457245adbcc4d55ac2b2f786822..785a95a4ba9f0b98403b6c65445f7f2eef602391
# A  docs/task-instructions/2026-07-30-cursor-vm-phase3-5.md
```

上述命令均退出码 0。差异盘点表明 Cursor commit 相对基线仅新增执行任务指令，不构成 Gate A0 交接。

#### Findings

| Finding ID | 严重性 | 证据 | 处置 |
|---|---|---|---|
| `A0-INTAKE-001` | blocker | Cursor commit 中没有 `HANDOFF_IMPORT.json` 或其他 handoff manifest，因而没有可复核的命令、环境、退出码、失败/重试、输入 hash 或输出 hash。 | Cursor 必须从固定基线提交并 push 完整 handoff manifest；收到不可变 commit 后新增 A0 首次审计条目。 |
| `A0-INTAKE-002` | blocker | 相对基线的唯一新增文件是 `docs/task-instructions/2026-07-30-cursor-vm-phase3-5.md`。 | 任务指令不能代替运行证据；不得据此签核 A0。 |
| `A0-INTAKE-003` | blocker | 缺少 `scripts/external_slice/import_defect4mr_pool.py`、`tests/external_slice/test_import_defect4mr_pool.py`、`data/external_slice/defect4mr_import/candidates_sanitized.json`、`data/external_slice/defect4mr_import/PROVENANCE.json`、`data/external_slice/defect4mr_import/IMPORT_LOG.md`。 | Cursor 完成一次性 sanitized import，并将全部规定工件与 handoff manifest 置于同一可审计交接中。 |

#### 判定

当前不存在可审计的 Gate A0 Cursor handoff，不能验证 provenance、64 条计数、35/16/12/1 状态分布、字段 allowlist、泄漏隔离或导入测试。Gate A0 判定为 `BLOCKED`。不创建 `gate_a0_defect4mr_import.md`；Gate A1 及以后保持锁定，直至新的 Cursor commit 提供完整交接并通过独立审计。
