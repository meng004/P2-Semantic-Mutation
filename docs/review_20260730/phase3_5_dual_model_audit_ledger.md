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
| 交接/复核时间 | `<ISO 8601 时间及时区>` |
| Cursor 分支 | `<远端跟踪分支>` |
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

§5 的详细审计记录严格 append-only：新交接或复核只能追加新条目，不得删除或改写既有历史。下表仅是从 §5 派生的当前状态索引；新增详细审计条目后允许更新对应 gate 的当前 commit、verdict、集成 commit 和解锁状态，但这种索引更新不得替代、删除或改写 §5 的任何详细记录。

| Gate | Cursor commit | Verdict | 本地集成 commit | 后继任务是否解锁 |
|---|---|---|---|---|
| Gate A0 — Defect4MR sanitized import | handoff `e72faa2d7b7469eba75b8a4e240083dc76de90dd`；payload `a789bcecbd9d0544c223d4401fa101909694fbbb` | `PASS_WITH_DISCLOSURE` | payload `e3d9cdc673f92072ffefdcd1baafa295f1ee2cbb`；handoff `2b35fd30fd96091ad835d194fc63a72b24794b02` | 是；C2 / Gate A1 admission execution 可在新 session 启动 |
| Gate A1a — C2 admission candidate audit（pre-readiness） | correction handoff `d4967e1c8221318ab624957f29955dd323cc49d9`；correction payload `964fcafcbd977004536979fab950aec88cec7b32` | `PASS_WITH_DISCLOSURE` | initial payload `c5425d51fbe4bc878634c44ec2386fe7fb78dc6e`；initial handoff `2ad1d40dd103fb1469dc8c9f5c05fa1a308ff258`；correction payload `7da7599b1db873bb9058126c907ced93f033157b`；correction handoff `25ae6f5d364823722ac7e29999412972153f8518` | 是；仅 corrected 32-row queue 解锁 C3 readiness；canonical freeze 与 A2/C4 仍锁定 |
| Gate A1b — C3 readiness Batch 1 | correction handoff `09da03a4585130dfb57428983f05ef7a4fb914bc`；correction payload `764840f3ad61e8f12ec2ead59422498082a462be` | `PASS_WITH_DISCLOSURE` | original payload/handoff `061e1891`/`66b8ca9d`；correction payload/handoff `a7bdaa05`/`1a6d6f35` | 是；仅 C3 Batch 2 解锁；canonical freeze 与 A2/C4 仍锁定 |
| Gate A1c — C3 readiness Batch 2 | second-correction handoff `929e93f8a50cd8aedea618ad7016aada72e0cc16`；payload `70c4ae0546d98267edfd80ee7023d94ad8111b98`；membership `c94684faadbb4b02f8685360255cc374c15183c8` | `PASS_WITH_DISCLOSURE` | membership `543dd90f`；original payload/handoff `ddaac13c`/`f0256427`；first correction `406f507d`/`b1f24356`；second correction `29df0ac9`/`a3c07e34` | 是；仅六行 supplemental-pilot C3 Batch 3 解锁；canonical freeze 与 A2/C4 仍锁定 |
| Gate SUPPLEMENTAL_ADMISSION_R1 — supplemental mining | R4 handoff `8b52441fbbcfee36ce0945f53e0f532f59657583`；payload `f78288df3c4676d5e66fc508dcba7912eda65d23` | `PASS_WITH_DISCLOSURE`（安全 hard-fail/withdrawal；零 admitted row） | N/A（等待显式 integration 决策） | supplemental 后继不解锁；下一门禁为已完成 PR #6 的本地 Gate A1d 审计 |
| Gate A1d — C3 readiness Batch 3 | A1d-r3 handoff `f6f1888f361a524a481cc9505e567a8bc414b9ea`；payload `82863d5804d3a7e7eae1c1266092b3a467bddb8a` | `PASS_WITH_DISCLOSURE` | N/A（等待显式 integration 决策） | 是；accepted ready=18，但 canonical freeze 仍锁定；仅 Local Desktop Supplemental Mining R2 协议修订/设计解锁 |
| Gate SUPPLEMENTAL_MINING_R2_DESIGN-r1 | correction audit `d95d6277ee09479d638bb83d75562e9dc4348031`；payload `1ed9fb2dc2714cb452bba4016d6093cefb36204d` | `PASS_WITH_DISCLOSURE` | N/A（设计分支，不含实验 payload） | 设计修订通过；但已发生的 Cursor Task 4 需独立执行审计，不能追溯通过 |
| Gate SUPPLEMENTAL_ADMISSION_R2 — Task 4 transport | admission handoff `30c30a73f1544a2129505bb4ee26f87f7cf710bb`；payload `ca1c55c05d5f90d2140ad99d479e0c12f483b558` | `BLOCKED`（crash-only A3 错判；stop/handoff/provenance fail-open） | N/A（PR #7 未集成） | 否；仅同分支 `SUPPLEMENTAL_ADMISSION_R2-r1` correction；不解锁 readiness/downstream |

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
| `STARTUP-CONFLICT-001` | 未验证的口径兼容性风险；若未解决则为 Gate A2 blocker | 冻结的 `research/prereg_v2/external_slice_protocol.md` §2.1 仍以 Defect4MR v1.0.0 / DOI release manifest 为项目池来源，§3 规定 DEF-CAL 10 例从按 v1.0.0 release manifest 字典序排序的 35 个 `verified_full` ID 中抽样；2026-07-30 双模型执行规格与任务则将 A0 sanitized import 来源钉扎到私有仓库 commit `2bf7c2401c846544e715d879eb639e8c3bf44067` 的 ledger blob `1469a2e2b15dcb2cdf59d185f3ec92f58fb77189`。两个 manifest 的 35-ID 集合及排序是否等价尚未验证；本 finding 不声称二者已经不等价。 | 不改写 A0 provenance，也不新增或改变 A0 verdict。在 Gate A2 的 DEF-CAL 抽样或训练排除前，必须用不可变 crosswalk 及其 hash 证明两个 manifest 的 35-ID 集合与排序等价；若不等价，必须依照高优先级冻结协议通过 `AMENDMENTS.md` 和作者裁决处理，禁止默默改用 commit ledger 顺序。若 Gate A2 前仍未解决，本 finding 升为 A2 blocker。 |

#### 判定

当前不存在可审计的 Gate A0 Cursor handoff，不能验证 provenance、64 条计数、35/16/12/1 状态分布、字段 allowlist、泄漏隔离或导入测试。Gate A0 判定为 `BLOCKED`。不创建 `gate_a0_defect4mr_import.md`；Gate A1 及以后保持锁定，直至新的 Cursor commit 提供完整交接并通过独立审计。

### 5.2 Gate A0 首次审计：C1 sanitized import handoff

| 字段 | 记录 |
|---|---|
| Gate | Gate A0 — Defect4MR sanitized import |
| 记录类型 | 首次审计；关闭 §5.1 的三项 intake blocker |
| 交接/复核时间 | `2026-07-31T22:38:33+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-5-execution` |
| Cursor commit | handoff `e72faa2d7b7469eba75b8a4e240083dc76de90dd`；payload `a789bcecbd9d0544c223d4401fa101909694fbbb` |
| Cursor baseline | `785a95a4ba9f0b98403b6c65445f7f2eef602391` |
| Handoff manifest | `data/external_slice/HANDOFF_IMPORT.json` at `e72faa2d7b7469eba75b8a4e240083dc76de90dd`; final SHA256 `e96cf128d2642a139b10503163129e827ad0d38de9346cfd0bd518a8b3c2e3ef` |
| 输入 hash | `meng004/P12-Defect4MR@2bf7c2401c846544e715d879eb639e8c3bf44067:data/ledgers/candidates.json`; blob `1469a2e2b15dcb2cdf59d185f3ec92f58fb77189`; SHA256 `0f797c10da5e7b3e12656f0062aa55b0dc3e31c701249ee5f05f4e744171786e` |
| 输出 hash | `scripts/external_slice/import_defect4mr_pool.py` = `292a8da4840060a26dac8cc844ee52dff4d3d179828f93d3f5a88fa74658f16f`; `tests/external_slice/test_import_defect4mr_pool.py` = `7ba189e6039abe63de3368349bd565daed4a6f7e7b2d6c18decc1aa156d5de5c`; `data/external_slice/defect4mr_import/candidates_sanitized.json` = `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac`; `data/external_slice/defect4mr_import/PROVENANCE.json` = `af7e9c522967bcccaba02db2361a1aadaf11fb64219b4a5bafcaab4cc89de152`; `data/external_slice/defect4mr_import/IMPORT_LOG.md` = `384134afddba35ca8e5e08d5965474ac9996a38e0d344165ce60dfe6af0834fe`; `data/external_slice/CURSOR_EXECUTION_LEDGER.md` = `ca034af0cfeda092efce50524fc4165a453722bc70c6583fce402087e1acb74e`; `data/external_slice/HANDOFF_IMPORT.json` = `e96cf128d2642a139b10503163129e827ad0d38de9346cfd0bd518a8b3c2e3ef` |
| 审计命令 | 下方“精确审计命令与退出码”完整记录 |
| Findings | `A0-INTAKE-001`–`003` 已由新 handoff 关闭；`A0-HANDOFF-SPLIT-001` 为非阻塞披露；`STARTUP-CONFLICT-001` 仍仅约束 Gate A2 |
| Verdict | `PASS_WITH_DISCLOSURE` |
| 本地集成 commit | payload `e3d9cdc673f92072ffefdcd1baafa295f1ee2cbb`；handoff `2b35fd30fd96091ad835d194fc63a72b24794b02` |
| 后继任务是否解锁 | 是。C2 / Gate A1 admission execution 可在新 session 启动；C1 VM/session 退役。 |

#### 精确审计命令与退出码

```text
rtk git show --stat --oneline e72faa2d
# exit 0
rtk git show --stat --oneline a789bcec
# exit 0
rtk git diff 785a95a4ba9f0b98403b6c65445f7f2eef602391..e72faa2d --name-status
# exit 0; seven added A0 handoff/payload paths
rtk gh api 'repos/meng004/P12-Defect4MR/contents/data/ledgers/candidates.json?ref=2bf7c2401c846544e715d879eb639e8c3bf44067' --jq '.sha + " " + .path'
# exit 0; path resolves to blob 1469a2e2b15dcb2cdf59d185f3ec92f58fb77189
rtk gh api repos/meng004/P12-Defect4MR/git/blobs/1469a2e2b15dcb2cdf59d185f3ec92f58fb77189 --jq .content | rtk base64 --decode | rtk shasum -a 256
# exit 0; input SHA256 0f797c10da5e7b3e12656f0062aa55b0dc3e31c701249ee5f05f4e744171786e
rtk shasum -a 256 scripts/external_slice/import_defect4mr_pool.py tests/external_slice/test_import_defect4mr_pool.py data/external_slice/defect4mr_import/candidates_sanitized.json data/external_slice/defect4mr_import/PROVENANCE.json data/external_slice/defect4mr_import/IMPORT_LOG.md data/external_slice/CURSOR_EXECUTION_LEDGER.md data/external_slice/HANDOFF_IMPORT.json
# exit 0; values recorded above
rtk jq 'length' data/external_slice/defect4mr_import/candidates_sanitized.json
# exit 0; 64
rtk jq 'group_by(.status) | map({status: .[0].status, count: length})' data/external_slice/defect4mr_import/candidates_sanitized.json
# exit 0; 35/16/12/1
rtk jq '{rows:length, unique_ids:([.[].provisional_id]|unique|length), all_key_sets:([.[]|keys]|unique)}' data/external_slice/defect4mr_import/candidates_sanitized.json
# exit 0; 64 rows, 64 unique IDs, exact eight-key allowlist
rtk rg -n -i 'mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|kill|fiber|analysis_id' data/external_slice/defect4mr_import
# exit 1; no output (required clean result)
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python scripts/external_slice/import_defect4mr_pool.py --repo meng004/P12-Defect4MR --commit 2bf7c2401c846544e715d879eb639e8c3bf44067 --output /private/tmp/p3-a0-audit.6PXs1N/regen/candidates_sanitized.json --source-file /private/tmp/p3-a0-audit.6PXs1N/candidates.raw.json
# exit 0; sanitized SHA256 34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac
rtk cmp data/external_slice/defect4mr_import/candidates_sanitized.json /private/tmp/p3-a0-audit.6PXs1N/regen/candidates_sanitized.json
# exit 0; byte-identical
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/external_slice/test_import_defect4mr_pool.py -q
# exit 0; 8 passed
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
# exit 0; 241 passed, 10 warnings
```

#### 独立复算结果

- 固定私有路径解析到 blob `1469a2e2...`，原始 bytes SHA256 为 `0f797c10...`。
- sanitized manifest 为 64 行、64 个唯一 `provisional_id`，状态分布 35/16/12/1。
- 每行顶层 key 严格等于八项 allowlist；规定泄漏扫描 exit 1、无输出。
- 固定原始 blob 的离线重放得到 SHA256 `34e819cc...`，与提交产物逐字节一致。
- import 专项测试 `8 passed`；完整测试 `241 passed, 10 warnings`。

#### 判定

Gate A0 零 blocker，按 `PASS_WITH_DISCLOSURE` 解锁后继。唯一披露为 payload commit `a789bcec...` 与最终 handoff commit `e72faa2d` 的双提交表达；五个规定 A0 工件在两提交间未变化。详细证据见 `docs/review_20260730/gate_a0_defect4mr_import.md`。

### 5.3 Gate A1a 首次审计：C2 admission candidate handoff（pre-readiness）

| 字段 | 记录 |
|---|---|
| Gate | Gate A1a — C2 admission candidate audit（pre-readiness） |
| 记录类型 | 首次审计 |
| 交接/复核时间 | `2026-08-01T10:08:35+08:00` |
| C2 分支 | `origin/codex/gpt-desktop-phase3-5-c2-admission` |
| C2 commit | handoff `f31a508ae6409c18dca8229fbabdf77598e0345d`；payload `90640368d21fe2087a266d8726ec81c2e9c2c124` |
| C2 baseline | `e5737f3c1c88641bc783bf8449fd7c53a6178df9` |
| Handoff manifest | `data/external_slice/HANDOFF_ADMISSION.json` at `f31a508ae6409c18dca8229fbabdf77598e0345d`；SHA256 `c244ef61d0fa11eb39b8e797a308d35cb0e5becca4b5cc44459a41d4a2baa847` |
| 输入 hash | sanitized 64-row manifest = `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac`；separate 9-row pilot = `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a`；protocol = `186b9734077035f63a1819569ecf45e645545862d045cb5ee899a7dd8f2841ca`；runbook = `a3ced473d0d4ab91c39480bb59e7032c05bd15f68e57ee277da71582b3256f05` |
| 输出 hash | candidate sheet = `79eb9de7f9d53d4b4b574aeace93f4b474849d13c686e94c3c005ed3e8aae802`；64-file evidence aggregate = `84823edab5dfb72e35c8f2c21af35e97f415937cba28fdab20f4c24c8f85d122`；checker = `cd84515e5247cb4a18640839a6048611b799353a8a5cb23aef742034f6c7d92e`；checker tests = `21ef6abb7a9130fc5ef94df6e152a33cb40ecc49d35d0f3640f2989423d421b4` |
| 审计命令 | 见 `docs/review_20260730/gate_a1_admission_audit.md` §6；全部结构、hash、公开证据与测试结果逐项记录 |
| Findings | blockers: `A1-SCOPE-001`、`A1-SCOPE-002`、`A1-SCOPE-003`、`A1-SOURCE-BINDING-001`；非阻塞：`A1-A2-PENDING-001`、`A1-EXECUTOR-SEPARATION-001`、`A1-VALIDATOR-SCOPE-001`、`A1-REAL-DEFECT-CHECK-001`、`A1-NEUTRAL-ID-CHECK-001`；`STARTUP-CONFLICT-001` 仍仅约束 Gate A2 |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（BLOCKED；未集成 C2 payload/handoff）` |
| 后继任务是否解锁 | 否。C3 readiness、canonical admission freeze 与 A2/C4 均保持锁定。 |

#### 独立复算结果

- payload/handoff 父子关系及 A0 baseline ancestry 精确匹配；远端 tracking ref 指向 handoff commit。
- handoff 声明的候选、证据树、checker、tests 及输入 hash 全部复算一致。
- 64 行、64 evidence、9-row supplemental 隔离、0 nonblank `analysis_id`；A1=35/29、A2=64 PENDING、submitted A3=59/5、decision=35/29。
- 35/35 public fixed commit 可解析，且 35/35 的第一父提交等于记录的 buggy SHA；35/35 public tracker entry 可访问。
- targeted tests `14 passed`；完整测试 `255 passed, 10 warnings`；规定泄漏扫描 exit 1、无输出。
- 三个 submitted A3 PASS 案例的实际输出分别为整数 transform size、整数 maximum index、communicator/permutation index sets，违反冻结的 float-vector → float/few-float A3 定义。
- checker 仅用 source row position 与 aggregate manifest hash，不能把每个 neutral row 绑定到对应 sanitized member；swap/rename 可逃逸。

#### 判定

Gate A1a 判定为 `BLOCKED`。A2 全部 `PENDING` 是 C2 的预期状态而非 blocker，但它意味着本阶段只能审核 pre-readiness queue，不能生成 canonical admission freeze。因存在三项 A3 错判和源成员绑定 blocker，本地不集成 C2 payload/handoff、不写 `FREEZE.sha256`、不启动 C3。修复要求与完整逐案记录见 `docs/review_20260730/gate_a1_admission_audit.md` 和 `docs/review_20260730/gate_a1_findings.csv`。

### 5.4 Gate A1a finding 修复复核：C2 correction handoff

| 字段 | 记录 |
|---|---|
| Gate | Gate A1a — C2 admission candidate audit（pre-readiness） |
| 记录类型 | finding 修复复核；关闭 §5.3 的四项 blocker |
| 交接/复核时间 | `2026-08-01T11:17:18+08:00` |
| C2 分支 | `origin/codex/gpt-desktop-phase3-5-c2-admission` |
| C2 commit | correction handoff `d4967e1c8221318ab624957f29955dd323cc49d9`；correction payload `964fcafcbd977004536979fab950aec88cec7b32` |
| C2 ancestry | `90640368...` → `f31a508a...` → `964fcafc...` → `d4967e1c...`，每个 handoff 均为对应 payload 的 direct child |
| Handoff manifest | `data/external_slice/HANDOFF_ADMISSION.json` at `d4967e1c8221318ab624957f29955dd323cc49d9`；SHA256 `d366e8271b2dab4f2f8aa0927df02212ef7decf807f699f85240a876ddb5ce13` |
| 输入 hash | sanitized manifest = `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac`；9-row pilot = `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a`；blocked report = `2aa9efd7353e33a8405af538533f3a4715fee5ef4973cec141a9f4c3ba960c75`；blocked findings = `13d24a6ff1212c8b5635697900d35395fdf79e31edcf2016ef474c734eef926f` |
| 输出 hash | corrected sheet = `4b0296c3656219e77a03acf1e9a727f574651bbaf1650ae07f31f2c47294adb8`；corrected evidence aggregate = `854a2e06f97a2cf2928504be4a4d55afd327be2da31ad3cc7975924b45bc43ae`；checker = `4fed32a87ac22c4e17ea13c735cfd65430e1abcf41e139484172320d59df1428`；tests = `ddcef0dd58c0e11b82aa4666ce38c6419661787b00fb97da59808e372d76b50e` |
| Findings | `A1-SCOPE-001`、`A1-SCOPE-002`、`A1-SCOPE-003`、`A1-SOURCE-BINDING-001` 全部 CLOSED；`A1-SCOPE-004` 记录 `EXT-fftw-05` 的新增保守排除；fixed-parent 在线关系仍由独立审计验证，为非阻塞披露；`STARTUP-CONFLICT-001` 仍仅约束 Gate A2 |
| Verdict | `PASS_WITH_DISCLOSURE` |
| 本地集成 commit | initial payload `c5425d51fbe4bc878634c44ec2386fe7fb78dc6e`；initial handoff `2ad1d40dd103fb1469dc8c9f5c05fa1a308ff258`；correction payload `7da7599b1db873bb9058126c907ced93f033157b`；correction handoff `25ae6f5d364823722ac7e29999412972153f8518` |
| 后继任务是否解锁 | 是，但仅 corrected 32-row A1∧A3 queue 可进入 C3 readiness。canonical admission freeze、A2/C4、预测与结果执行仍锁定。 |

#### 独立复算结果

- correction handoff SHA 与所有输入/输出 hash 匹配；correction diff 未触及 canonical sheet、freeze、C3 reproduction、runs 或审计文档。
- checker exit 0；targeted tests `19 passed`；完整测试 `260 passed, 10 warnings`；泄漏扫描 exit 1、无输出。
- 64 个 evidence 的 `source_record_sha256` 全部对对应 sanitized record 独立重算匹配且互异；swap-negative test 覆盖原 source-binding blocker。
- 64 个 case-specific A3 rationale 全部不同；三项原 A3 错判改为 FAIL/EXCLUDED，额外保守排除 `EXT-fftw-05` 合理且未替换样本。
- 修正后 A1=35/29、A2=64 PENDING、A3=55/9、decision=32/32、analysis aliases=0。
- initial/corrected sheet 的 64 个 ID、顺序、repo、issue、buggy/fixed SHA、mechanism、A1、A2 与 blank alias 均不变；只有四行 A3 及派生字段变化。

#### 判定

四项 blocker 全部关闭，Gate A1a 以 `PASS_WITH_DISCLOSURE` 解锁 corrected 32-row queue 的 C3 readiness。该判定不是 final admission：64 行 A2 仍为 PENDING，不创建 canonical `admission_sheet.csv` 或 `FREEZE.sha256`，不解锁 A2/C4 或更晚任务。详细复核证据见更新后的 `docs/review_20260730/gate_a1_admission_audit.md` 与 `docs/review_20260730/gate_a1_findings.csv`。

### 5.5 Gate A1b 首次审计：C3 readiness Batch 1

| 字段 | 记录 |
|---|---|
| Gate | Gate A1b — C3 readiness Batch 1 |
| 记录类型 | 首次审计 |
| 交接/复核时间 | `2026-08-01T20:46:14+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness` |
| Cursor commit | handoff `607acb044856101d8744f62cd2f7173a396c99b5`；payload `4ac5dab0f1692a2c2c46486c763abcce9d27984d` |
| Cursor baseline | `533f8e26cd7d87e48afaceaa9424a3f7ed38a997` |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH1.json` at `607acb044856101d8744f62cd2f7173a396c99b5` |
| 输入 hash | candidate sheet `4b0296c3656219e77a03acf1e9a727f574651bbaf1650ae07f31f2c47294adb8`；sanitized manifest `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac`；Gate A1a report `77f0515bf24985e5df12369bd52389751cf8757b6a82109aee9f35ddc66a58b3`；runbook `a3ced473d0d4ab91c39480bb59e7032c05bd15f68e57ee277da71582b3256f05` |
| 输出 hash | readiness JSON `7400824048a3b3ea614a97d2cb275f0d479fc2fefcb9d839a41db6b5c55d3613`；NumPy aggregate `63f9928f4a69822ae552ee38a1f0e619761dd55a0ecc9cda4910d546d24885b7`；SUNDIALS aggregate `9b623dd7efb9fe5111cba5ad4478241bc5b16b1629b31e9d4fea55085a200a9b`；SciPy aggregate `77f23a54daa1cee92535a14e27df4a38c69bef0dea28b91a7b1b3e0f75b636d8`；全部 individual hash 匹配 handoff |
| Findings | blockers: `A1B-HANDOFF-CMD-001`、`A1B-LOCK-PROVENANCE-001`；non-blocking disclosure: `C3-GHCR-403` |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（BLOCKED；未集成 Batch 1 payload/handoff）` |
| 后继任务是否解锁 | 否。Batch 2、canonical admission freeze、A2/C4、fiber、prediction 与结果执行均保持锁定。 |

#### 独立复算结果

- payload/handoff 父子关系、远端分支与 PR head 均匹配；diff 仅包含 Batch 1 readiness 工件、reproducer、日志、ledger 与 `.gitignore` 日志例外。
- 固定 Defect4MR registry 的三个非空 digest 与 Batch 1 三个案例及 digest 精确对应；三例均属于 Gate A1a 批准的 32-row queue。
- 全部输入、individual 输出和三目录 aggregate SHA256 匹配。
- 三例的 seed、语义输入、expected property 与 arm 状态一致；stored observations 均为 buggy fail / fixed hold，并与固定验证报告吻合。
- admission checker exit 0；三个 reproducer 均可编译；结构化 selection/schema/arm 检查 PASS；完整测试 `260 passed, 10 warnings`。
- Handoff 未记录逐臂精确构建/运行命令与实际 exit code；三个案例均无 runbook §6.2 要求的带 hash lock 文件及足够的 source/package/build provenance，因而不能独立重放历史环境。

#### 判定

行为对比仅记为 case-local `observed`，不足以晋升 A2 `PASS`。Gate A1b Batch 1 判定为 `BLOCKED`；本地不 cherry-pick payload/handoff，不改 candidate/canonical sheet，不解锁 Batch 2。完整 findings 与修复合同见 `docs/review_20260730/gate_a1b_readiness_batch1_audit.md`。

### 5.6 Gate A1b finding 修复复核：C3 readiness Batch 1 correction

| 字段 | 记录 |
|---|---|
| Gate | Gate A1b — C3 readiness Batch 1 |
| 记录类型 | finding 修复复核；关闭 §5.5 的两个 blocker |
| 交接/复核时间 | `2026-08-01T21:15:43+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness` |
| Cursor commit | correction handoff `09da03a4585130dfb57428983f05ef7a4fb914bc`；correction payload `764840f3ad61e8f12ec2ead59422498082a462be` |
| Cursor ancestry | `4ac5dab0...` → `607acb04...` → `764840f3...` → `09da03a4...`；每个 handoff 均为对应 payload 的 direct child |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH1.json` at `09da03a4585130dfb57428983f05ef7a4fb914bc` |
| Findings | `A1B-HANDOFF-CMD-001` CLOSED；`A1B-LOCK-PROVENANCE-001` CLOSED；non-blocking disclosures：original GHCR 403 / correction Docker socket denial、复用已验证 CPython 3.9.18 toolchain |
| Verdict | `PASS_WITH_DISCLOSURE` |
| 本地集成 commit | original payload `061e1891`；original handoff `66b8ca9d`；correction payload `a7bdaa05`；correction handoff `1a6d6f35` |
| 后继任务是否解锁 | 是，但仅 C3 Batch 2。Candidate sheet A2 保持 PENDING；canonical admission freeze、A2/C4、fiber、prediction、kill/result execution 继续锁定。 |

#### 独立复算结果

- Global command log 61 条；handoff 精确包含相同 61 条（去 retained tails）+ 4 条验证命令，共 65 条。Per-case 子集精确为 NumPy 30、SUNDIALS 17、SciPy 10。
- 三例 trigger exit 均为 buggy `1` / fixed `0`；same seed/input/property 与 3/3 contrast 不变。
- 全部 handoff individual 与 directory aggregate hash 匹配；两个 NumPy、两个 SUNDIALS GitHub archive hash 由新下载独立复算一致。
- SciPy/NumPy 三个 pinned-release wheel hash 与 PyPI 权威 metadata 一致；NumPy build lock 的双臂 `--require-hashes` 安装、SciPy 双 lock 安装均 exit 0。
- SUNDIALS exact-source、build tools、CMake flags、compile/run 命令完整；NumPy exact SHA、submodule pins 与 build closure 完整。
- admission checker exit 0；py_compile exit 0；leak scan clean；完整测试 `260 passed, 10 warnings`。
- Candidate sheet/canonical freeze 未变，Batch 2 与后继任务未启动。

#### 判定

两个 blocker 全部关闭。Gate A1b Batch 1 以 `PASS_WITH_DISCLOSURE` 接受三例 case-local A2 `PASS` readiness 证据，并按顺序集成 original/correction 四个 commit。仅 C3 Batch 2 解锁；A2 字段的 canonical 回填与切片 freeze 继续等待全部 readiness 批次及后续门禁。完整复核见更新后的 `docs/review_20260730/gate_a1b_readiness_batch1_audit.md`。

### 5.7 Gate A1c 首次审计：C3 readiness Batch 2

| 字段 | 记录 |
|---|---|
| Gate | Gate A1c — C3 readiness Batch 2 |
| 记录类型 | 首次审计 |
| 交接/复核时间 | `2026-08-01T23:54:40+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness` |
| Cursor commit | handoff `1f1586e66712ff220386e7c29e98593cda7e48ba`；payload `20c445d7aa50f377e1aeb87f73774142f9d75cff`；membership `c94684faadbb4b02f8685360255cc374c15183c8` |
| Cursor baseline | Gate A1b correction handoff `09da03a4585130dfb57428983f05ef7a4fb914bc` |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH2.json` at `1f1586e66712ff220386e7c29e98593cda7e48ba` |
| Findings | blockers: `A1C-HANDOFF-HASH-001`、`A1C-FREIA-LOCK-001`、`A1C-BUILD-EVIDENCE-001`、`A1C-HANDOFF-VERIFY-CMD-001`；non-blocking disclosure: PR #4 title still names Batch 1 |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（BLOCKED；未集成 membership/payload/handoff）` |
| 后继任务是否解锁 | 否。仅原 Cursor 分支上的 finding correction 解锁；Batch 3+、candidate A2 promotion、canonical freeze、A2/C4、fiber、prediction 与 detection runs 均保持锁定。 |

#### 独立复算结果

- ancestry 连续，远端分支与 OPEN PR #4 head 均为 `1f1586e6...`。
- approved 32-row queue 减去 Batch 1 三行，精确等于按 sheet 顺序冻结的 29 行；membership、readiness 与 handoff case 列表一致，无重复、重叠或换例。
- 268 条 global commands 精确等于29个 per-case command 数组的顺序拼接；结果计数为 PASS 9 / REPRO_FAILED 20，失败阶段分布与 handoff 一致。
- 9 个 proposed PASS 的18个 buggy/fixed 公共源码归档 hash 全部经 fresh download 匹配；Boost 1.84.0 基础归档也匹配。
- 19 个 per-case `COMMANDS.json` 的 handoff 声明 hash 与最终已脱敏文件不符；其余声明 hash 匹配。
- FrEIA 两臂的 `--require-hashes` 安装均 exit 1，实际使用未带 hash 的网络 fallback，故其 proposed PASS 暂不接受。
- Trilinos、deal.II、Castro 仅下载/解压，未执行 build，却被记录为 `REPRO_FAILED:build`，缺少失败证据。
- Handoff 未保存 admission/pytest/compile/leak/token/hash 验证的 exact commands 与 exits。
- 独立 admission checker exit 0；compileall exit 0；leak/token scans exit 1 且无输出；完整测试 `260 passed, 10 warnings`；candidate sheet hash 不变且 A2 仍全为 PENDING。

#### 判定

Gate A1c 判定为 `BLOCKED`。本地不 cherry-pick Batch 2 三个 commit，不回填 candidate A2，不解锁 Batch 3+ 或任何后继门禁。仅允许 Cursor 从 `1f1586e6...` 新开 correction session，按四项 finding 合同修复后重新提交 Gate A1c。完整审计与修复合同见 `docs/review_20260730/gate_a1c_readiness_batch2_audit.md`。

### 5.8 Gate A1c finding 修复复核：C3 readiness Batch 2 correction

| 字段 | 记录 |
|---|---|
| Gate | Gate A1c — C3 readiness Batch 2 |
| 记录类型 | finding 修复复核 |
| 交接/复核时间 | `2026-08-02T08:22:24+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness` |
| Cursor commit | correction handoff `01acdbbf6ffd220f9b768ffd386f02cc7fff591b`；correction payload `9f6f65afae8d9849b485dde94865a613d9d14269` |
| Cursor ancestry | `1f1586e6...` → `9f6f65af...` → `01acdbbf...`；远端分支与 OPEN PR #4 head 均为 correction handoff |
| Findings | `A1C-HANDOFF-HASH-001` CLOSED；`A1C-BUILD-EVIDENCE-001` CLOSED；`A1C-FREIA-LOCK-001` PARTIAL/OPEN；`A1C-HANDOFF-VERIFY-CMD-001` PARTIAL/OPEN |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（未集成 Batch 2 或 correction commits）` |
| 后继任务是否解锁 | 否。仅从 `01acdbbf...` 启动第二次 finding correction；Batch 3+、candidate A2 promotion、canonical freeze、A2/C4、fiber、prediction 与 detection runs 均锁定。 |

#### 独立复算结果

- membership 与 candidate sheet 相对 blocked handoff 无变化；29行顺序、无换例规则和 A2 PENDING 均保持。
- 280条 global commands 精确等于29个 per-case command 数组的顺序拼接；全部 handoff individual hash 独立复算为零 mismatch；hash checker exit 0。
- Trilinos/deal.II 双臂 configure 均 exit 0、build 均 exit 2；Castro 双臂 build/trigger 均 exit 0且无 contrast，因此 heavy-build finding 关闭，统计仍为9/20。
- FrEIA 双臂 runtime `--require-hashes` 均 exit 0且无 fallback；但 source install 未使用 `--no-build-isolation`，日志确认另行安装未纳入 hash lock 的 build dependencies，故 lock finding 尚未关闭。
- Verification log 已记录7条命令，但 neutral regex 的双反斜线使词边界失效，token scan 也只覆盖 `ghp_`；独立正确表达式证明扫描器缺陷，实际 runbook reserved-term scan 与 broader token scan均无真实泄漏。
- 独立 admission checker exit 0；compileall exit 0；handoff hash checker exit 0；完整测试 `260 passed, 10 warnings`。

#### 判定

四项原 blocker 中两项关闭、两项仍开。Gate A1c 继续 `BLOCKED`，不 cherry-pick correction，不回填 candidate A2，不解锁 Batch 3+。修复要求见 `docs/review_20260730/gate_a1c_readiness_batch2_audit.md` §5.3。

### 5.9 Gate A1c 第二次 finding 修复复核：C3 readiness Batch 2 A1c-r2

| 字段 | 记录 |
|---|---|
| Gate | Gate A1c — C3 readiness Batch 2 |
| 记录类型 | 第二次 finding 修复复核；关闭 §5.8 剩余两项 blocker |
| 交接/复核时间 | `2026-08-02T08:43:52+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness` |
| Cursor commit | handoff `929e93f8a50cd8aedea618ad7016aada72e0cc16`；payload `70c4ae0546d98267edfd80ee7023d94ad8111b98` |
| Cursor ancestry | `01acdbbf...` → `70c4ae05...` → `929e93f8...`；远端分支与 OPEN draft PR #4 head 均为 handoff |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH2.json`；SHA256 `2fab1703566db004a6a121e382c039e39cf21bb0ecdc9b3f2312b373573ed4e9` |
| 输入 hash | membership `b6bb4a45219b1e65c13d78f93c46bae4c972b9873942cc75bfc831f38a0c0153`；candidate sheet 与 first-correction baseline byte-identical |
| 输出 hash | readiness `7d922fca1cf87b6070c29173ad98003db5c70db182cad16755b77d35a06b1150`；command log `71b02141ca47094663d2ad2023e69201afdadbf2ac965e5e9ba3f4f895c78a4c`；verification log `a38666aef17838138074d7ce7025bacae1bd207bad656676079f4499d575e80b`；FrEIA build lock `f4554c8497a56b5af72ffaf4072318a8620534dc90d4248f5553eb66a35ddaa5`；build-artifact manifest `2d215761c5a2b50f15b28b325b6c1c31b4ac765006c50ddfb2e28fe6a66c615a` |
| Findings | `A1C-FREIA-LOCK-001` CLOSED；`A1C-HANDOFF-VERIFY-CMD-001` CLOSED；四项原 blocker 全部关闭 |
| Verdict | `PASS_WITH_DISCLOSURE` |
| 本地集成 commit | membership `543dd90f`；original payload/handoff `ddaac13c`/`f0256427`；first correction payload/handoff `406f507d`/`b1f24356`；second correction payload/handoff `29df0ac9`/`a3c07e34` |
| 后继任务是否解锁 | 是，但仅新 Cursor VM/session 中对 supplemental pilot 六行 A1/A3 PASS、A2 PENDING 队列执行 C3 Batch 3。Candidate/canonical A2 回填、admission freeze、C4、标注、fiber、prediction 与 detection runs 继续锁定。 |

#### 独立复算结果

- FrEIA 双臂 fresh venv 的 build/runtime hash-lock 安装与 exact-source `--no-deps --no-build-isolation` 安装均 exit 0；build lock 与四项 artifact hash 对齐，无 isolated build dependency 日志；contrast 仍为 buggy 1 / fixed 0。
- Runbook §3 reserved pattern 的正控 exit 0 并命中；decision-level 正式扫描 raw `rg` exit 1、无输出。`ghp_` / `github_pat_` / unredacted `Bearer` 扫描 raw exit 1、无输出；committed checker 均规范化为 exit 0。
- 281 条 global commands 精确等于 29 个 per-case 数组顺序拼接；membership 仍为 approved 32 减 Batch 1 三行，无换例。
- 结果为 9 PASS / 20 REPRO_FAILED；failure stage 为 build_or_trigger 8、contrast 4、build 2、era-Julia 3、GPU 2、arch 1。
- Handoff 顶层与逐案所有 SHA256 零 mismatch；checker exit 0、`HASH_CHECK_OK`。Admission checker exit 0；compileall exit 0；完整测试 `260 passed, 10 warnings`。
- Candidate sheet A2 仍全 PENDING；Batch 3、canonical freeze、标注、alias、prediction 与 detection/result 路径相对 correction baseline 均未变。

#### 判定

四项原 blocker 全部关闭，Gate A1c 以 `PASS_WITH_DISCLOSURE` 接受并按不可变顺序集成全部 Batch 2 lineage。披露项仅为 PR #4 标题仍写 Batch 1，以及保留两轮 correction lineage。Batch 1+2 合计 12 ready / 20 retained failures，尚未达到协议 `n >= 20` 目标；因此下一任务不是 canonical freeze，而是新 Cursor VM 的 C3 Batch 3，范围严格限定为独立 supplemental pilot 中六行 A1/A3 PASS、A2 PENDING 案例。

### 5.10 Gate SUPPLEMENTAL_ADMISSION_R1 首次审计：supplemental mining R1

| 字段 | 记录 |
|---|---|
| Gate | Gate SUPPLEMENTAL_ADMISSION_R1 — supplemental mining R1 |
| 记录类型 | 首次审计 |
| 交接/复核时间 | `2026-08-02T09:55:39+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r1`；draft PR #5 |
| Cursor commit | handoff `ac887e8a4a980dafca31c9ee803ec971a57698bc`；payload `a1cc795f340c38b340550c6789ece72a00c4c316`；scope `e108b82d38e53d89991960266385edf62da9eefc` |
| Cursor baseline | `0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a` |
| Handoff manifest | `data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json`；SHA256 `4a57cb082203de0e79105e248e00e07b89d6762aa305dbc95871d5a91f8b3aab` |
| 输入 hash | plan `1c2df1d7f2516d58385e1cee6688c6633bf4307cf2328059a5e86e35923e7af5`；scope `e90b084bf74152ea4836d04773a8b117e4b24577cf03e2d8d4269c22f3fa51e7`；其余六项 immutable input 与 frozen scope 声明一致 |
| 输出 hash | search `df9fa7158ce65eda35b2f984257a54e650682a91c2431d2acb8a68403cf7451c`；queue `e110811b6b8fceb24242597a8b4d5cd969ea877aef4c9728cd0ae9e7c7e09c7a`；evidence snapshot `50a1c86149f8043130d0f012418abdac7670d2438b0231ff6dedf1b033e4b914`；decisions `e8c60c34a4806f80f044ec855a4c73397330d379c240b1bf41a0743ffb6513c7`；sheet `ae347f4868731425f78b94d2532d0234bc5b089dae040f9b08ee7e9db334a6f0` |
| Findings | blockers `SUPP-R1-SEARCH-SEMANTICS-001`、`SUPP-R1-QUEUE-BINDING-001`；high `SUPP-R1-HANDOFF-DISCLOSURE-001`；non-blocking `SUPP-R1-CODE-QUALITY-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（BLOCKED；未集成 scope/payload/handoff）` |
| 后继任务是否解锁 | 否。仅从 blocked handoff 新开 correction session；supplemental readiness、A2 promotion、canonical freeze、C4、标注、预测和 detection runs 均锁定。 |

#### 独立复算结果

- 三段 ancestry 与 draft PR #5 head 正确；handoff hash checker `HASH_CHECK_OK`；structural checker exit 0。
- targeted tests `18 passed`；完整测试 `278 passed, 10 warnings`；reserved/token/prohibited scans raw exit 1、无输出；既有 admission/readiness/downstream 路径未变。
- 搜索快照的 262 hits 全部为 PR、issue 为零；实现通过未冻结的 PR→issue 回溯构造 128-row queue，其中 21 条为 open。
- exact first frozen query 独立重放返回 20 issue / 0 PR，因此现有 queue、neutral-ID 顺序、56 个决策与 12 个 proposed pending 均不属于冻结搜索总体。
- checker 不接收 queue；decision validator 只比较 ID 存在性，对错误 review order 执行 no-op，不能证明严格选择顺序。
- handoff 的 unresolved findings 未记录上述搜索语义偏离和 open-item 污染。

#### 判定

Gate `SUPPLEMENTAL_ADMISSION_R1` 为 `BLOCKED`。不 cherry-pick PR #5 的三项 commit，不认可其 12 条 proposed rows，不启动其 readiness。仅允许在新 Cursor VM/session 中从 blocked handoff 执行 correction，移除 PR fallback、重跑 direct issue-only 搜索、重新分配 ID/评审并补齐 queue binding 与 handoff disclosure。完整修复合同见 `docs/review_20260730/gate_supplemental_admission_r1_audit.md`。

### 5.11 Gate SUPPLEMENTAL_ADMISSION_R1-r2 finding 修复复核

| 字段 | 记录 |
|---|---|
| Gate | Gate SUPPLEMENTAL_ADMISSION_R1-r2 |
| 记录类型 | finding 修复复核 |
| 交接/复核时间 | `2026-08-02T11:00:10+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r1`；draft PR #5 |
| Cursor commit | handoff `e007042074956e6c57a089cfed1ecc404b5723a4`；payload `bc3a4e30f57f38f728b4f3971c05c07e6285f643` |
| Cursor ancestry | `ac887e8a...` → `bc3a4e30...` → `e0070420...`；PR 与远端 branch head 均为 handoff |
| Handoff manifest | `data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json`；SHA256 `792c02d116727344a8c4ef11666b99b241194f7e673167ebb18e36d6fc6b8eae` |
| 输出 hash | diagnostic `04241a898c15ee81dec0b1da785b29313735fa1a6f372bd2e1b0a8d09e3b6f9b`；hard fail `56c73ed2bf80a34f2f3017f933d6823dcf319f609fbf4db674be58b2b95a29e9`；withdrawal `42ad107522d910b53ef816561eb400857428bf4aa0d98ec7279e594dd973544a`；command log `c15cd9ce5f11735ee5a02febbc6067948675747f41a23f62f137b2c1681f9486`；verification log `0b290325961870035f996ee109b5861d6225d7f4c86ef8d72abbbcc32c0f8135` |
| Findings | blocker `SUPP-R1-R2-FULL-BINDING-001`；high `SUPP-R1-R2-DIAGNOSTIC-PROVENANCE-001`；low/non-blocking `SUPP-R1-R2-STYLE-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（BLOCKED；未集成 R2 payload/handoff）` |
| 后继任务是否解锁 | 否。仅从 `e0070420...` 开始 R3 correction；readiness、A2 promotion、canonical freeze 及下游任务全部锁定。 |

#### 独立复算结果

- R2 ancestry、远端 branch 与 draft PR #5 head 一致；handoff hash checker `HASH_CHECK_OK`。
- 旧 56 个 `(neutral_id, decision)` 与 withdrawal 清单 canonical hash 完全相同；旧 snapshot、queue、decisions、sheet、evidence snapshot/tree 均已删除，无替代行。
- targeted tests `22 passed`；完整测试 `282 passed, 10 warnings`；compileall、token scan、immutable-path 与 diff check 通过。
- official miner 在首个 PR-typed item 上 hard-fail，PR→issue fallback 已删除；无 readiness 或其他 downstream 工件。
- 两个独立负向探针均错误 exit 0：queue/decision/sheet/evidence 可整体换成 snapshot 中不存在的 issue；sheet SHA 可与 decision/evidence 不一致。
- 66-query diagnostic 只有汇总行，无 66 条命令/响应 hash；command log 仅有首个 `gh api` 调用，关键 wrapper exit 2 也无完整命令记录。本地重放首查询为 20 issue / 0 PR，因此诊断结论只能视为未证实的 Cursor VM 局部现象。

#### 判定

`SUPP-R1-SEARCH-SEMANTICS-001` 与原 handoff disclosure finding 关闭；`SUPP-R1-QUEUE-BINDING-001` 仍为 OPEN/PARTIAL。Gate R2 保持 `BLOCKED`，不集成 payload/handoff，不认可或恢复任何 supplemental row。仅允许按 `gate_supplemental_admission_r1_audit.md` §7.4 在新 Cursor VM/session 执行 R3 correction。

### 5.12 Gate SUPPLEMENTAL_ADMISSION_R1-r3 finding 修复复核

| 字段 | 记录 |
|---|---|
| Gate | Gate SUPPLEMENTAL_ADMISSION_R1-r3 |
| 记录类型 | finding 修复复核 |
| 交接/复核时间 | `2026-08-02T11:30:27+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r1`；draft PR #5 |
| Cursor commit | handoff `e6110b104e3271dc31c74c6346eff808e0239048`；payload `72a11bc0bf39c9d667bbaab9aa198b85c48c13af` |
| Cursor ancestry | `e0070420...` → `72a11bc0...` → `e6110b10...`；PR 与远端 branch head 均为 handoff |
| Handoff manifest | `data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json`；SHA256 `66f6e7823b756437fc19ac039e3b710e5ecb988f1525a540b4be8a5a471a5a44` |
| 输出 hash | diagnostic withdrawal `0086087502b7365fdbf32925d2eab800fe0b15a370f32bae1ebfb494e137e7d2`；hard fail `2652f4923b31fd6438c9371b675edcf235e9d30d4a81ad22c66d570615af7184`；withdrawal `42ad107522d910b53ef816561eb400857428bf4aa0d98ec7279e594dd973544a`；command log `4770c0c2dff70b60288a6381f7a88eb7bd034434dc05310933b19af1076d3e76`；verification log `2d72e9e8dd1d096f4b871538a6e480235e4a2c0098b11686d7812f4011837a22` |
| Findings | blocker `SUPP-R1-R3-PHRASE-PROVENANCE-001`；medium/non-blocking `SUPP-R1-R3-NEGATIVE-COVERAGE-001`；low/non-blocking `SUPP-R1-R3-STYLE-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（BLOCKED；未集成 R3 payload/handoff）` |
| 后继任务是否解锁 | 否。仅从 `e6110b10...` 开始 R4 correction；readiness、A2 promotion、canonical freeze 及下游任务全部锁定。 |

#### 独立复算结果

- R3 ancestry、远端 branch 与 draft PR #5 head 一致；handoff hash checker `HASH_CHECK_OK`。
- 两个 R2 exit-0 负向探针现均 exit 1；旧 56 项 withdrawal hash 仍精确一致；无候选或 readiness 工件恢复。
- targeted tests `33 passed`；完整测试 `293 passed, 10 warnings`；compileall、token scan、immutable-path 与 diff check 通过。
- R2 diagnostic 文件和 66-query claim 已撤回；首个 Cursor VM query 与 official wrapper exit 2 的命令、时间、hash/tail 已记录并限定环境范围。
- 新 phrase-provenance 探针将 snapshot item phrase 改为未冻结字符串后，checker 仍错误 exit 0/PASS；`setdefault` 保留了被篡改的 item phrase。
- “every cross-artifact field mismatch” negative coverage 仍不完整，但现有比较代码覆盖多数未单测字段。

#### 判定

R3 关闭两个旧 concrete escape 与 diagnostic provenance finding，但 phrase provenance 仍未绑定冻结查询。Gate 保持 `BLOCKED`，不集成 R3 payload/handoff，不认可或恢复任何 supplemental row。仅允许按 `gate_supplemental_admission_r1_audit.md` §8.4 在新 Cursor VM/session 执行 R4 correction。

### 5.13 Gate SUPPLEMENTAL_ADMISSION_R1-r4 finding 修复复核

| 字段 | 记录 |
|---|---|
| Gate | Gate SUPPLEMENTAL_ADMISSION_R1-r4 |
| 记录类型 | finding 修复复核；关闭 R3 phrase provenance 与 negative-coverage findings |
| 交接/复核时间 | `2026-08-02T13:29:19+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r1`；draft PR #5 |
| Cursor commit | handoff `8b52441fbbcfee36ce0945f53e0f532f59657583`；payload `f78288df3c4676d5e66fc508dcba7912eda65d23` |
| Cursor ancestry | `e6110b10...` → `f78288df...` → `8b52441f...`；远端 branch 与 PR #5 head 均为 handoff |
| Handoff manifest | `data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json`；SHA256 `ef6cef595220e01402542472df7288d72d4729dda714183fb1e27cb5d21e8085` |
| 输出 hash | verification log `2b00039806e5d314035e4fa760afabaf5505fbc176693dfa52a9ef9e787ff3dc`；withdrawal `42ad107522d910b53ef816561eb400857428bf4aa0d98ec7279e594dd973544a`；checker `d18b0b684109b99fed257f7dfa695b00b1017adc5e1c04f95715d5d4fd9001ce`；checker tests `5eaff7aacfe3336351bbc9ba5a44f837fbf969716872be51c41036a2060fb3b4` |
| Findings | `SUPP-R1-R3-PHRASE-PROVENANCE-001` CLOSED；`SUPP-R1-R3-NEGATIVE-COVERAGE-001` CLOSED；`SUPP-R1-R2-FULL-BINDING-001` CLOSED；style observations low/non-blocking |
| Verdict | `PASS_WITH_DISCLOSURE`：接受安全 hard-fail、withdrawal 与审计工具修复；不产生 admitted candidate |
| 本地集成 commit | `N/A（PR #5 correction lineage 等待显式 integration 决策）` |
| 后继任务是否解锁 | supplemental readiness 不解锁；旧 12 rows 不得复用。下一门禁是已独立完成并 push 的 PR #6 / C3 Batch 3 本地 Gate A1d 审计。 |

#### 独立复算结果

- R4 ancestry 连续，远端分支和 PR #5 head 为 `8b52441f...`；handoff hash checker `HASH_CHECK_OK`（6 files，0 tree/evidence）。
- exact tampered-phrase 探针和两个既有 full-binding 探针均 exit 1；item repository/phrase 现与 enclosing frozen query 强绑定。
- targeted tests `47 passed`；完整测试 `307 passed, 10 warnings`；compileall、immutable-path 与 diff check exit 0；token scan raw exit 1、无输出。
- 原 R1 的 12 pending IDs 与 44 excluded IDs 分别与 withdrawal 清单逐项一致；snapshot、R2 diagnostic、queue、decisions、sheet、evidence、readiness 均不存在。
- 没有新搜索、候选、A2、dual-arm 或 downstream 产物；Cursor VM Search API 异常仍仅作环境限定披露。

#### 判定

所有 R4 blocker 关闭。Gate 以 `PASS_WITH_DISCLOSURE` 接受“正确停止且完整撤回”的状态，但该结论不等于 supplemental admission 成功：admitted row 数仍为 0，旧 12 rows 不可复用，supplemental readiness 不解锁。PR #5 是否集成由作者显式决定。仓库远端已存在此前独立授权的 C3 Batch 3 handoff `da70fa67...`（PR #6，6/6 proposed PASS），因此下一任务应在 Local Desktop 对其执行 Gate A1d 审计，而不是重新运行 Batch 3 或进入 canonical freeze。

### 5.14 Gate A1d 首次审计：C3 readiness Batch 3

| 字段 | 记录 |
|---|---|
| Gate | Gate A1d — C3 readiness Batch 3 |
| 记录类型 | 首次审计 |
| 交接/复核时间 | `2026-08-02T13:44:43+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness-batch3`；draft PR #6 |
| Cursor commit | handoff `da70fa676ebcab8ef1e98f532aa711c2d01f0c84`；payload `00d1ca3fdfaa582f831f89589aabcfb51667c3c0`；membership `cc3321da3a9e6f1f7d67e5b90cdf21d6fb9001c1` |
| Cursor baseline | `0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a` |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH3.json`；SHA256 `cc488df412eb0a709552f7e2559f230df702397f0f8818b793fd00a45665b421` |
| 输入 hash | membership `02d47656f6fc5a528c9f1cf747bba8025440914e12873fcc8975a8f54e6da853`；source sheet `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a` |
| 输出 hash | readiness `194e255aca7dc82c30dc00061c2e16233ed26cf9a6502669e37c80eb974238a2`；command log `28991dbb6236b6a4ca4d50144fad4faef154a7a85b3acc49807cdf3a950c58f2`；verification log `fbaed8e5f154ab13a89465211be2a9a39f9c957fa60629921d1472ab0f2904f8`；runner `10c2416415665a7d0748049adbfac04fa2d38368db859f0747708617bdc27c4a` |
| Findings | blockers `A1D-REPETITION-001`、`A1D-SM03-CONTRACT-001`、`A1D-LINALG-PROVENANCE-001`；Standards axis FAIL |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（未集成 PR #6 membership/payload/handoff）` |
| 后继任务是否解锁 | 否。仅从 `da70fa67...` 启动 A1d-r1 correction；supplementary mining、canonical freeze、C4、标注、category map、prediction、detection 均锁定。 |

#### 独立复算结果

- lineage 连续，PR #6 和远端分支 head 均为 handoff；membership 精确等于 Gate A1c 授权六例，无换例。
- handoff checker `HASH_CHECK_OK`；篡改一个 fixed JSON 后 checker exit 1；121 条 global commands 精确等于六个 per-case logs 的顺序拼接。
- admission checker exit 0；独立绑定探针 `A1D_INDEPENDENT_PROBE_OK cases=6 commands=121`；完整测试 `260 passed, 10 warnings`；compileall exit 0；reserved/token scans raw exit 1、无输出。
- 每案现有一个 seed=0 buggy/fixed 对比均为 1/0，source/build/dependency hashes 与 sheet SHAs 一致；A2 仍全 PENDING，downstream 路径未变。
- 但 runbook 要求 smoke 加足够 seeded repetitions，当前每臂仅一次；statsmodels-03 的 PASS predicate 忽略单样本约束，独立探针证实该约束失败仍 exit 0；两个线性代数相关环境未记录 BLAS/LAPACK provider。

#### 判定

Gate A1d 为 `BLOCKED`。六个单次对比只能记为 case-local observed，不能接受为 A2 PASS；accepted ready 数保持 Batch 1+2 的 12。不得集成 PR #6 或进入新的 mining/freeze。唯一解锁任务是在原 Cursor 分支按 `gate_a1d_readiness_batch3_audit.md` §6 完成 correction，固定 smoke+seeds 0–4 的重复矩阵、修复 statsmodels-03 完整 predicate、补 per-arm BLAS/LAPACK provenance 和 targeted negative tests，然后停在 Gate A1d-r1。

### 5.15 Gate A1d-r1 复审：C3 readiness Batch 3

| 字段 | 记录 |
|---|---|
| Gate | Gate A1d-r1 — C3 readiness Batch 3 correction |
| 记录类型 | finding-closure 复审 |
| 交接/复核时间 | `2026-08-02T19:21:36+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness-batch3`；draft PR #6 |
| Cursor commit | handoff `4287ea4a1c782030d34af2162355fd459d50a563`；payload `dfc94736fa9722cd1ab5ab6a61f8ad6f677138e2`；matrix `64568960ec5ccfeb12571ab01a1b9aeacbf48da2` |
| Cursor baseline | blocked handoff `da70fa676ebcab8ef1e98f532aa711c2d01f0c84` |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH3.json`；SHA256 `58b7d370a5e299c3920a1cee253fa6327a8e0ceaa9413c517c39516471828041` |
| 输入 hash | membership `02d47656f6fc5a528c9f1cf747bba8025440914e12873fcc8975a8f54e6da853`；matrix `addab92a9ab0643c4ecf89d056c910088180cf5c4651ba1beee543d8bfa776d6`；source sheet `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a` |
| 输出 hash | readiness `c9d3d57bd4d5c6d5120c1d92e64b094b47bbd3635e26af817ab24fd80dffc016`；command log `a2bbaa97d3038bf8982a0c425300e5b289f80be70f945b4f4643921e0814fb8c`；verification log `de7343c65a4b1090eb12ada6f18894e13a5872067dd5f4eeb1a8c94e8ab824de` |
| Findings | 原三项 empirical blocker 已关闭；新增 blocker `A1D-R1-MATRIX-AGGREGATION-FAILOPEN-001`；Standards axis FAIL |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（未集成 PR #6）` |
| 后继任务是否解锁 | 否。仅从 `4287ea4a...` 启动 A1d-r2 correction；accepted ready 仍为 12，supplementary mining、canonical freeze、C4、标注、category map、prediction、detection 均锁定。 |

#### 独立复算结果

- lineage 是连续的 matrix → payload → handoff，PR #6 与远端 branch head 均固定到 handoff；membership 与 sheets 未变。
- handoff checker 为 `HASH_CHECK_OK`；篡改一个 formal raw RC 后 checker exit 1 并指出精确文件；独立重构验证 6 cases、30 formal pairs、6 smoke pairs 和 72 arm executions。
- retained evidence 全部符合预期：每个 formal pair 输入相同，buggy false/RC1，fixed true/RC0；12 个 provider 记录均 exit 0、识别 OpenBLAS 并被 per-case hash tree 绑定。
- statsmodels-03 旧逃逸已关闭；admission checker exit 0；targeted `7 passed`；full suite `267 passed, 10 warnings`；compileall exit 0；reserved/token raw scans exit 1。
- 但独立负测证明 formal aggregator 对缺失 parity 和反转 RC 均返回 `PASS`；standalone verifier 只信 summary，未从 raw files fail-closed 重构。
- Standards 独立复审发现 runner 的 E402、I001 和两处 E501；新提交 subject 与 `git diff --check` 合格。

#### 判定

Gate A1d-r1 仍为 `BLOCKED`。当前 6/6 是证据层面的 observed contrast，但 decision code 存在可复现 fail-open，不能晋升为 accepted A2，ready 数仍为 12。唯一解锁任务是在同一 Cursor 分支完成 A1d-r2：显式要求每 seed parity 为 true 且 raw RC 为 1/0，由 verifier 从 hash-bound raw artifacts 重构五个 seed，加入缺失 parity/反转 RC 负测，修复四个 Ruff violations，重算 derived files/handoff 后停止复审。无需重跑未变的 dual-arm evidence。

### 5.16 Gate A1d-r2 复审：C3 readiness Batch 3

| 字段 | 记录 |
|---|---|
| Gate | Gate A1d-r2 — C3 readiness Batch 3 correction |
| 记录类型 | finding-closure 复审 |
| 交接/复核时间 | `2026-08-02T20:27:44+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness-batch3`；draft PR #6 |
| Cursor commit | handoff `8ef20d26ea0a785bd0209b922a94e7f3bc1e8064`；payload `eab67f3ab08329d1d38feb6ed445d138d14d2f2f` |
| Cursor baseline | blocked A1d-r1 handoff `4287ea4a1c782030d34af2162355fd459d50a563` |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH3.json`；SHA256 `c8c47cee21e2d0bcdfcc306a019028dc50ff6ab12a8f9da46117835660afb108` |
| 输入 hash | membership `02d47656f6fc5a528c9f1cf747bba8025440914e12873fcc8975a8f54e6da853`；matrix `addab92a9ab0643c4ecf89d056c910088180cf5c4651ba1beee543d8bfa776d6` |
| 输出 hash | readiness `7446ea002d131797ac9f9ac77397fcf1b59389c668dd854a3241831f2b8fcb02`；verification log `e0613d4ae5bda8d622f233d06491715cb6c893c516d7221b8ed6ba89d1f2a911`；verifier `cca164b6bd2dcade90ed8a5de0a82b28366d6e6d6b87b4c1b1105a28cee90602` |
| Findings | `A1D-R1-MATRIX-AGGREGATION-FAILOPEN-001` 已关闭；新增 blocker `A1D-R2-HANDOFF-VERDICT-BINDING-001`；Standards axis PASS |
| Verdict | `BLOCKED` |
| 本地集成 commit | `N/A（未集成 PR #6）` |
| 后继任务是否解锁 | 否。仅从 `8ef20d26...` 启动 A1d-r3 correction；accepted ready 仍为 12，supplementary mining、canonical freeze、C4、标注、category map、prediction、detection 均锁定。 |

#### 独立复算结果

- r1 的两条 aggregation escape 已关闭：缺失 parity 和反转 RC 均得到 `REPRO_FAILED`；verifier 从五个 raw JSON/RC 重构并核对 repetition matrix 与 readiness。
- membership、matrix、sheets、smoke/formal raw executions 和 provider evidence 相对 `4287ea4a` 无变化；无 dual-arm rerun；独立证据重构仍为 6 cases、30 formal pairs、6 smoke pairs、72 arms。
- handoff checker `HASH_CHECK_OK`；admission/membership/compileall/Ruff 均 exit 0；targeted `10 passed`；full suite `270 passed, 10 warnings`；reserved/token raw scans exit 1。
- 但 verifier 完全未读取 handoff；只将一个 handoff case verdict 从 PASS 改为 REPRO_FAILED 后，verifier 与 hash checker 均 exit 0。这违反 A1d-r2 明确的 handoff cross-check 合同。

#### 判定

Gate A1d-r2 仍为 `BLOCKED`。当前提交的六个 handoff verdict 虽与 raw evidence 一致，但不存在 fail-closed 的 handoff semantic binding，因此不能晋升为 accepted A2。唯一解锁任务是在同一 Cursor 分支完成 A1d-r3：verifier 读取 handoff，逐案绑定 reconstructed/readiness/repetition/handoff verdict 与 seeds/RC/failure metadata，重算 counts/failures，并增加 handoff-only verdict/count tamper 负测。无需重跑 dual-arm evidence。

### 5.17 Gate A1d-r3 复审与最终判定：C3 readiness Batch 3

| 字段 | 记录 |
|---|---|
| Gate | Gate A1d-r3 — C3 readiness Batch 3 correction |
| 记录类型 | finding-closure 最终复审 |
| 交接/复核时间 | `2026-08-02T20:41:22+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-c3-readiness-batch3`；draft PR #6 |
| Cursor commit | handoff `f6f1888f361a524a481cc9505e567a8bc414b9ea`；payload `82863d5804d3a7e7eae1c1266092b3a467bddb8a` |
| Cursor baseline | blocked A1d-r2 handoff `8ef20d26ea0a785bd0209b922a94e7f3bc1e8064` |
| Handoff manifest | `data/external_slice/HANDOFF_REPRO_BATCH3.json`；SHA256 `e192ee839a08bd71d8e682b44fad4e7defec68f8998d08e07e3292d3ec0ec64b` |
| 输入 hash | membership `02d47656f6fc5a528c9f1cf747bba8025440914e12873fcc8975a8f54e6da853`；matrix `addab92a9ab0643c4ecf89d056c910088180cf5c4651ba1beee543d8bfa776d6` |
| 输出 hash | readiness `628cde0104906a8a0a92578ce989fe487f20eee4ac184e6f5fa2850410df9fba`；verification log `6862812d89a296b96a0c325c521ad84c406bc49dea96061aead0b1d738298224`；verifier `b21eea2724b3f5782167c9f6d78dfe5e0a5bd58e9b51f4c374a98185447e0da3` |
| Findings | `A1D-R2-HANDOFF-VERDICT-BINDING-001` 已关闭；Standards PASS；Spec PASS |
| Verdict | `PASS_WITH_DISCLOSURE` |
| 本地集成 commit | `N/A（PR #6 integration 等待显式授权）` |
| 后继任务是否解锁 | accepted ready=18；canonical freeze/C4/标注/prediction/detection 仍锁定。仅 Local Desktop Supplemental Mining R2 协议修订与设计解锁。 |

#### 独立复算结果

- verifier 现读取 handoff，严格绑定六案 ID/order、五个 formal seeds、verdict、smoke/formal seeds、seed-0 RC、failure stage、counts 和 failures。
- handoff-only verdict、counts、failures 三个独立篡改分别触发对应 AssertionError 并 exit 1；正向 verifier 为 `membership_matrix_ok 6`，hash checker 为 `HASH_CHECK_OK`。
- previous aggregation escapes 继续得到 `REPRO_FAILED`；独立证据重构为 6 cases、30 formal pairs、6 smoke pairs、72 arms。
- membership、matrix、sheets、raw executions 与 provider artifacts 相对 r2 无变化；无 dual-arm rerun或 downstream artifact。
- targeted `12 passed`；full suite `272 passed, 10 warnings`；Ruff、admission、compileall、`git diff --check` 均 exit 0；reserved/token raw scans exit 1。

#### 判定与扩样状态

Gate A1d-r3 以 `PASS_WITH_DISCLOSURE` 关闭。Batch 3 六案可计入 accepted ready，使累计从 12 增至 18，覆盖 11 个 projects。两张 sheet 的 A2 仍按 pre-freeze 合同保持 `PENDING`，PR #6 是否集成等待作者显式决定。

样本仍不满足冻结协议：n=18<20，且只有 SUNDIALS(4) 与 statsmodels(3) 两个 projects 达到“每项目至少 3 ready”的 H-RANK qualification floor，要求为 6 个。最低分布感知补样是新增 6 个 ready：NumPy +1、SciPy +1，并在两个当前单例项目各 +2，达到 n=24。Supplemental R1/R4 的旧候选已全部撤回且不可复用，因此下一任务必须先在 Local Desktop 冻结 Supplemental Mining R2 的 issue-typed retrieval 协议修订；不得直接在 Cursor 重启 mining，也不得进入 canonical freeze/C4。

### 5.18 SUPPLEMENTAL_MINING_R2_DESIGN-r1 独立复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_MINING_R2_DESIGN-r1` |
| 记录类型 | correction handoff 独立复审 |
| Local commit | `d95d6277ee09479d638bb83d75562e9dc4348031`；parent `1ed9fb2dc2714cb452bba4016d6093cefb36204d` |
| Plan SHA-256 | `04b6b08c344b550c9ce11b8bb0fca57a0cb00fcb5f7bffceb4d49ab71155e8d5` |
| Findings | Standards 0；Spec 0；Cursor 命令无 `rtk` 前缀 |
| Verdict | `PASS_WITH_DISCLOSURE` |
| 后继任务是否解锁 | 设计本身通过；已提前发生的 Cursor 执行不追溯通过，须独立审计。 |

独立复核确认 direct-child、plan hash、clean diff 和 `260 passed, 10 warnings`。
披露项是 Cursor branch 在该复核落盘前已创建并执行，违反设计 handoff 的停点；这不改变设计文本正确性，但其执行证据必须另行判定。

### 5.19 SUPPLEMENTAL_ADMISSION_R2 Task 4 transport 审计

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2` — Task 4 transport |
| 记录类型 | 首次 live retrieval hard-fail 审计 |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | diagnostic `548702be000249bbb4262ffe3bf282f4e93b962c`；code `d989f713938d46b8a25519fafd5c465554d3da45`；contract `7ede024f2605bd3497e16648e44beb589b984020` |
| Cursor baseline | `d95d6277ee09479d638bb83d75562e9dc4348031` |
| Findings | `SUPP-R2-RUN-ONCE-001`、`SUPP-R2-CODE-BEFORE-LIVE-001`、`SUPP-R2-UNEXPECTED-FAIL-CLEANUP-001`；Ruff F401 |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同一 Cursor 分支的 transport correction；fresh retrieval、admission、readiness 和全部 downstream 均锁定。 |

最终树未铸造 snapshot、queue、decision、sheet、evidence 或 handoff，这一原子结果属实。但 `COMMAND_LOG.json` 有 992 条记录、六仓各两条 page 0、460 组重复 page/cursor；hard-fail 时间后仍有 26 个请求。首个请求早于 runner commit `519ab9ad...`，且 generic exception 未完整清理或写 terminal failure log。Targeted `109 passed`、full `369 passed, 10 warnings`、compileall 通过；精确 Ruff 因未使用 `hashlib` 失败。现有日志仅保留为失败证据，不得用于 mint payload。

### 5.20 SUPPLEMENTAL_ADMISSION_R2 transport-r1 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-r1` |
| 记录类型 | transport correction 独立复审 |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `62fe052d017d66c9ac054442ee31cd9e3303705b` |
| Cursor baseline | `548702be000249bbb4262ffe3bf282f4e93b962c` |
| Findings | Standards PASS；`SUPP-R2-LOCK-LOSER-MUTATION-001`、`SUPP-R2-RUN-BINDING-FAILOPEN-001`；endCursor、atomic publish、failed-run preservation 未闭环 |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同一 Cursor 分支 transport-r2 correction；fresh retrieval 及所有 downstream 均锁定。 |

Correction 是 blocked baseline 的 direct child；旧 992-entry log 和 diagnostic 未变；diff 仅 miner/tests。独立验证为 targeted `113 passed`、full `373 passed, 10 warnings`，Ruff、compileall、diff-check 均通过。

但锁失败者会在零网络调用后删除 owner snapshot/queue；checker 对 snapshot `run_id` 和 queue `code_commit` 的独立篡改仍 exit 0；queue rebuild 丢失绑定；page command log 缺少 `endCursor`；最终 pages/snapshot/queue 发布并非 atomic rename；下一次 retrieval 还会覆盖应保留的失败日志。因此不得运行 fresh retrieval。

### 5.21 SUPPLEMENTAL_ADMISSION_R2 transport-r2 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-r2` |
| 记录类型 | transport correction 独立复审 |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `ebbafad20859c6f6fbb6990ca63e3af8703a3773` |
| Cursor baseline | `62fe052d017d66c9ac054442ee31cd9e3303705b` |
| Findings | Standards PASS；`SUPP-R2-ENDCURSOR-BINDING-001`、`SUPP-R2-FAILED-PAGE-PROVENANCE-001`、`SUPP-R2-PUBLISH-CRASH-ATOMICITY-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同一 Cursor 分支 transport-r3 correction；fresh retrieval 及所有 downstream 均锁定。 |

r2 关闭了 lock-loser mutation、run/code fail-open、queue rebuild binding 和失败日志归档问题；archive 两个 SHA 与 live originals 一致，旧 992-entry log/diagnostic 未变。独立验证 targeted `128 passed`、full `388 passed, 10 warnings`，Ruff、compileall、diff-check 全部通过。

但单独篡改 page log `endCursor` 后 admission checker 仍 exit 0；`validate_page` 失败的已执行请求没有 page command record；fork+`os._exit(77)` 在 pages promotion 后模拟真实进程死亡，留下 pages/staging 而 snapshot/queue 缺失。因此 transport evidence 尚不能支持一次正式网络执行。

### 5.22 SUPPLEMENTAL_ADMISSION_R2 transport-r3 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-r3` |
| 记录类型 | transport correction 独立复审 |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `e3973bf7e0cf5af47598cd79c04a8a6b689f59d6` |
| Cursor baseline | `ebbafad20859c6f6fbb6990ca63e3af8703a3773` |
| Findings | Standards PASS；`SUPP-R2-FULL-TRAVERSAL-COVERAGE-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同一 Cursor 分支 transport-r4 correction；fresh retrieval 及所有 downstream 均锁定。 |

r3 关闭了 page-record completeness、endCursor 单字段 binding 和 publish crash-seal 问题；真实 `os._exit(70)` boundary tests、r2 regression 与 archive 均通过。独立验证 targeted `145 passed`、full `405 passed, 10 warnings`，Ruff、compileall、diff-check 全部通过。

但 checker 只验证 supplied set。完整删除 PyMC 的 log/manifest/page 并重算 snapshot seal 与 `PUBLISH_COMMIT` 后，剩余 5/6 repositories 仍获 `ADMISSION_CHECK_OK`；修改 raw terminality 后 reseal 也可通过。seal 尚未绑定冻结 scope 的六仓全遍历要求，因此不得运行 fresh retrieval。

### 5.23 SUPPLEMENTAL_ADMISSION_R2 transport-r4 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-r4` |
| 记录类型 | transport correction 独立复审 |
| 交接/复核时间 | `2026-08-03T11:28:20+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `be88a04ae55058f49ac52ec1a9aa28eb17aa6e70` |
| Cursor baseline | `e3973bf7e0cf5af47598cd79c04a8a6b689f59d6` |
| Findings | Standards PASS；`SUPP-R2-FULL-TRAVERSAL-COVERAGE-001` 已关闭；`SUPP-R2-CROSS-REPOSITORY-IDENTITY-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同一 Cursor 分支 transport-r5 correction；fresh retrieval 及所有 downstream 均锁定。 |

r4 关闭了六仓覆盖与顺序、连续非空 page block、raw pageInfo 绑定、终止性、稳定 totalCount 和每仓节点计数问题。删除整段 PyMC 数据并完整 reseal 后，checker 已按预期 exit 1。独立验证 targeted `155 passed`、full `415 passed, 10 warnings`，Ruff、compileall、diff-check 和 no-data-change check 全部通过。

但节点 ID/URL 的唯一性集合在每个 repository block 内重置。将 PyMC 节点复制到 GPyTorch retained page 并重算 page/manifest/`PUBLISH_COMMIT` 后，完整 checker 仍返回 `ADMISSION_CHECK_OK`。全局身份重复与 URL 所属仓库错误仍可进入语料，因此 fresh retrieval 不得启动；r5 只需补齐跨六仓 ID/URL 唯一性、URL-to-scope 绑定及两项 resealed 负测。

### 5.24 SUPPLEMENTAL_ADMISSION_R2 transport-r5 最终复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-r5` |
| 记录类型 | transport correction 最终独立复审 |
| 交接/复核时间 | `2026-08-03T12:02:34+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `5a76aa6a9032283f5dc086f94c0c2c098d80b4c7` |
| Cursor baseline | `be88a04ae55058f49ac52ec1a9aa28eb17aa6e70` |
| Findings | `SUPP-R2-CROSS-REPOSITORY-IDENTITY-001` 已关闭；Standards PASS；Spec PASS |
| Verdict | `PASS_WITH_DISCLOSURE`（仅 transport preflight） |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 仅同一 Cursor 分支一次 fresh Task 4 retrieval；A1/A3、admission、readiness 与所有 downstream 仍锁定。 |

r5 在 miner 和独立 checker 中均实现六仓共享 node-ID/canonical-URL 唯一性，同时保持 issue number 仅仓库内唯一；URL 必须精确绑定 enclosing SCOPE owner/name。三项 fully resealed identity attacks 被拒绝，跨仓相同 issue number 的正向控制继续通过。

独立验证 targeted `159 passed`、full `419 passed, 10 warnings`、四项 identity controls `4 passed`；Ruff、compileall、diff-check、no-data-change check 均通过。该 PASS 只授权一次正式 transport retrieval；它不代表 snapshot/admission 已通过，也不改变 accepted-ready=18。

### 5.25 SUPPLEMENTAL_ADMISSION_R2 Task 4 live transport-result 审计

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-result` |
| 记录类型 | 唯一一次 live Task 4 retrieval 结果独立审计 |
| 交接/复核时间 | `2026-08-03T12:51:33+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | result `bc6cab5c6dbc83ab2d1185a3dd9f822f81de96fc`；producer `5a76aa6a9032283f5dc086f94c0c2c098d80b4c7` |
| Cursor baseline | `5a76aa6a9032283f5dc086f94c0c2c098d80b4c7` |
| Run ID | `0d76e415-0831-4417-b2fa-81b6ac046b2b`；retrieve exit 0 |
| Findings | Standards PASS；live payload observed-valid；`SUPP-R2-RAW-SNAPSHOT-SEMANTIC-BINDING-001`；distribution structural shortfall |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同分支 transport-result-r1 checker correction；不得重跑 retrieval，不解锁 A1/A3、readiness 或 downstream。 |

独立算法从 552 页、54,902 个 raw closed issues 精确重建出相同的 156 条 snapshot 与 156 条 queue。六仓 page 数为 `33/11/3/3/447/55`，selected rows 为 `24/5/2/0/91/34`；run/code/log/page/seal、全局身份、terminality 和 992-entry 历史失败归档均一致。Targeted `159 passed`、full `419 passed, 10 warnings`，562 个 JSON 全部可解析，credential scan raw exit 1。

但 fully resealed 的 frozen-but-false phrase 攻击在重建全部 downstream binding 后仍得到 `ADMISSION_CHECK_OK`。checker 没有从 source page/node 重建 snapshot 的 identity、timestamps、title/body hashes、labels、真实 phrase/surfaces、top-20、dedupe 与排序，违反冻结 raw-page replay 合同。live 数据无需重跑且保持 observed-valid；唯一修正是补齐独立 raw→snapshot reconstruction 及 resealed 负测后再次本地复审。

此外 chaospy 只有 2 条候选、SALib 为 0，均低于各自 3-ready quota。no-replacement 下 J=6 路径已结构性不可达；任何后继 handoff 必须披露 `DISTRIBUTION_TARGET_AT_RISK`，不得用 PyTorch/JAX 补位。

### 5.26 SUPPLEMENTAL_ADMISSION_R2 transport-result-r1 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-result-r1` |
| 记录类型 | raw-to-snapshot checker correction 独立复审 |
| 交接/复核时间 | `2026-08-03T15:19:38+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `1e5aee2329c9549ef665cc5cb6d487ebbab74b63` |
| Cursor baseline | live result `bc6cab5c6dbc83ab2d1185a3dd9f822f81de96fc` |
| Findings | Standards PASS；旧 frozen-but-false symptom 已关闭；`SUPP-R2-CHECKER-INDEPENDENCE-001`；`SUPP-R2-RAW-NODE-VALIDATION-001`；negative-test isolation gap |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同分支 transport-result-r2 checker correction；不得重跑 retrieval，不解锁 A1/A3、readiness 或 downstream。 |

旧攻击在完整重建 downstream 后现以 `match_surfaces` mismatch 返回 1，且 live 156-row snapshot 正向重建通过。Targeted `168 passed`、full `428 passed, 10 warnings`，Ruff、compileall、diff-check、live-data byte check 均通过。

但 checker 直接调用 producer `miner.select_phrase_union`，不构成独立 selection replay；它也未验证 raw `__typename`、closed state/closedAt 和 labels pagination。将 raw node 改为 `PullRequest`、更新全部 hashes/bindings 并完整 reseal 后，checker 仍返回 `ADMISSION_CHECK_OK`。新增 phrase test 使用非冻结字符串，且 reseal helper 不重建 downstream，因此不能隔离证明新 binding。唯一 r2 修正是 checker-owned replay、raw node completeness validation 与真实 fully resealed negatives；live data 和 distribution shortfall 均不得改变。

### 5.27 SUPPLEMENTAL_ADMISSION_R2 transport-result-r2 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-result-r2` |
| 记录类型 | independent raw-to-snapshot checker correction 复审 |
| 交接/复核时间 | `2026-08-03T15:41:41+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `8076d82f8c02209ad33416594ee30e7183e8b7c6` |
| Cursor baseline | `1e5aee2329c9549ef665cc5cb6d487ebbab74b63` |
| Findings | `SUPP-R2-CHECKER-INDEPENDENCE-001` 与 raw PullRequest symptom 已关闭；`SUPP-R2-LABEL-PAGINATION-FAILOPEN-001`；`SUPP-R2-RAW-NEGATIVE-ISOLATION-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同分支 transport-result-r3 checker correction；不得重跑 retrieval，不解锁 A1/A3、readiness 或 downstream。 |

r2 已实现 checker-owned cutoff、normalization、phrase matching、top-20、dedupe、ordering 与 record construction；producer selection/builders 被 monkeypatch 为异常时正向 checker 仍通过。完整同步 raw-page/manifest/snapshot/downstream hashes 后，`PullRequest` 与 labels `hasNextPage=true` 攻击均被拒绝。

但 checker 只拒绝 `hasNextPage is True`。删除该字段或设为 JSON `null` 后，完整重封并重建 queue、decisions、sheet、evidence 的独立攻击仍获得 `ADMISSION_CHECK_OK`/0，违反冻结的 exact-false label-pagination 合同。现有两条 raw 负测只刷新 manifest/PUBLISH，未同步 snapshot source hashes/record hashes 或 downstream，因此在禁用目标 semantic guard 后仍会因 stale binding 通过负测，不能证明目标检查。

独立验证 targeted `172 passed`、full `432 passed, 10 warnings`；Ruff、compileall、`git diff --check`、live-data byte check 均通过。Standards 与 Spec 均为 FAIL。唯一 r3 修正是 exact `hasNextPage is False`、完整重建且 guard-isolated 的 PullRequest/label pagination negatives；live data、accepted-ready=18 与 `DISTRIBUTION_TARGET_AT_RISK` shortfall 不变。

### 5.28 SUPPLEMENTAL_ADMISSION_R2 transport-result-r3 最终复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-transport-result-r3` |
| 记录类型 | transport-result checker 最终独立复审 |
| 交接/复核时间 | `2026-08-03T22:07:47+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | `020b60fb83f7eb1d34f143458fca62beab5aa398` |
| Cursor baseline | `8076d82f8c02209ad33416594ee30e7183e8b7c6` |
| Findings | `SUPP-R2-LABEL-PAGINATION-FAILOPEN-001` 已关闭；`SUPP-R2-RAW-NEGATIVE-ISOLATION-001` 已关闭；Standards 0；Spec 0 |
| Verdict | `PASS_WITH_DISCLOSURE` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 是；仅同分支 Task 5/6 A1+A3 admission review；不得重跑 retrieval，不解锁 readiness 或 downstream。 |

checker 现要求 labels/pageInfo 为对象且 `hasNextPage is False`。完整同步 raw-page、manifest、snapshot source/record hashes、command log、publish seal 并重建 queue/decisions/sheet/evidence 后，PullRequest 与八种 labels/pageInfo/hasNextPage 非法状态均被拒绝，literal false 正控通过。移除 typename 或 label 目标 guard 后，对应 fully synchronized negative 由拒绝转为接受，证明负测不再依赖 stale hash。

独立验证 targeted `182 passed`、full `442 passed, 10 warnings`、focused matrix `12 passed`；Ruff、compileall、`git diff --check` 与 live-data byte check 全部通过。live pages/snapshot/queue 未变，未执行 retrieval、A1/A3 或 readiness。

Gate 以 `PASS_WITH_DISCLOSURE` 关闭。披露仍为 immutable snapshot 的结构性配额不足：chaospy 最多 2、SALib 为 0，因此 frozen J=6 路径不可达，后继 handoff 必须保留 `DISTRIBUTION_TARGET_AT_RISK` 且不得以 PyTorch/JAX 补位。accepted-ready 仍为 18。唯一解锁动作是在同一 Cursor VM 分支按 queue/stop-rule 完成 public A1/A3 review，生成 bound admission payload 与 direct-child handoff 后停止本地审计；所有 readiness/downstream 继续锁定。

### 5.29 SUPPLEMENTAL_ADMISSION_R2 payload/handoff 审计

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2` |
| 记录类型 | A1/A3 admission payload 与 handoff 独立审计 |
| 交接/复核时间 | `2026-08-03T23:31:56+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | payload `ca1c55c05d5f90d2140ad99d479e0c12f483b558`；handoff `30c30a73f1544a2129505bb4ee26f87f7cf710bb` |
| Cursor baseline | `020b60fb83f7eb1d34f143458fca62beab5aa398` |
| Findings | `SUPP-R2-A3-CRASH-ONLY-001`；`SUPP-R2-STOP-RULE-FAILOPEN-001`；`SUPP-R2-HANDOFF-SEMANTIC-COUNTS-001`；`SUPP-R2-VERIFICATION-PROVENANCE-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同分支 `SUPPLEMENTAL_ADMISSION_R2-r1` correction；不得重跑 retrieval，不解锁 readiness 或 downstream。 |

结构复算得到 63 decisions/sheet/evidence、10 pending、53 excluded，逐仓 reviewed 为 `16/5/2/0/20/20`，A2/aliases/blind scan、transport immutability、direct-child lineage 与 `DISTRIBUTION_TARGET_AT_RISK` 均一致。十个 submitted fix commits 均公开存在，且 buggy SHA 是 fixed commit first parent。Targeted `182 passed`、full `442 passed, 10 warnings`、admission 与 handoff checker 均 exit 0。

但 public evidence 证明 `EXT-pymc-04`、`EXT-pymc-16` 与 `EXT-gpytorch-05` 只有 TypeError/RuntimeError 症状，违反冻结 crash-only exclusion；三行须 A3 FAIL/EXCLUDED。PyMC 因此仅 3 个有效 admit，row16 停止无效，必须继续 row17–20。GPyTorch 耗尽后仅 1 个有效 pending。

Checker 还接受未到 5 admits/20 reviews/queue exhaustion 的 fully rebuilt early-stop payload；把 handoff decision total 从 63 改为 999 后 admission/hash checker 仍双双 exit 0。Verification log 未记录 handoff 阶段命令，且其 diff-check zero claim 在未披露 `cr-at-eol` 配置时不可复现：native Local Git 对 64 行 CRLF CSV 返回 2。

Standards PASS，Spec FAIL。唯一 correction 是修正三行和 PyMC 后续 queue review，补严 stop-rule 与 handoff semantic reconstruction/负测，规范 LF/provenance，重发 payload+direct-child handoff；accepted-ready 保持 18，readiness/downstream 全部锁定。

### 5.30 SUPPLEMENTAL_ADMISSION_R2-r1 correction 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-r1` |
| 记录类型 | admission correction 独立复审 |
| 交接/复核时间 | `2026-08-04T08:59:11+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | payload `48728c423be28de20951be24a22f905e42c8a1d7`；handoff `dc4060da182b60fa5175710000379659babcd4ea` |
| Cursor baseline | `30c30a73f1544a2129505bb4ee26f87f7cf710bb` |
| Findings | crash-only、LF、handoff-checker count tamper 已关闭；`SUPP-R2-A1-FIX-PARENT-001`；`SUPP-R2-STOP-FIRST-HIT-001`；`SUPP-R2-EXTRA-DECISION-SCOPE-001`；`SUPP-R2-ADMISSION-HANDOFF-SEMANTICS-001`；`SUPP-R2-VERIFICATION-PROVENANCE-002` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同分支 `SUPPLEMENTAL_ADMISSION_R2-r2` correction；不得重跑 retrieval，不解锁 readiness 或 downstream。 |

三条 crash-only 行已正确降级，PyMC 已顺序审到 row20；提交工件复算为 67 decisions/sheet/evidence、9 submitted、58 excluded，A2/aliases/transport/no-downstream 均保持。CSV 已为 LF，native diff-check 通过；handoff checker 已能重算 counts/stop/shortfall。独立验证 targeted `191 passed`、full `451 passed, 10 warnings`，Ruff、compileall、admission/handoff/transport checks 均通过。Standards PASS。

Spec 仍 FAIL。`EXT-pymc-20` 的 recorded buggy SHA 不是 fixed commit `09afc8e...` 的 first parent，违反 runbook A1；正确 parent 为 `5d2fe4f...`。Stop-rule 只验证最终 totals，会接受第五个 admit 后的额外 decision。更强的 fully rebuilt probe 还证明 out-of-scope `evil/repo` decision 可通过 producer、payload、admission 和 handoff 全链。Admission checker 未按要求重算完整 handoff semantics：把 total/reviewed 改为 999 并将 `analysis_id_all_blank` 设 false 仍返回 0。Verification log 仍未记录 write-handoff/hash commands，且 gate identity 仍为未带 `-r1` 的旧值。

唯一 r2 correction 是修正 first-parent binding、实现 ordered earliest-stop、拒绝 out-of-scope/empty-queue decisions、让两个 checker 分别验证完整 handoff semantics、补 fully rebuilt isolated negatives 和 correction-gate provenance。accepted-ready 仍为 18；`DISTRIBUTION_TARGET_AT_RISK` 与 no-substitution 继续有效，readiness/downstream 全部锁定。

### 5.31 SUPPLEMENTAL_ADMISSION_R2-r2 correction 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-r2` |
| 记录类型 | admission correction 独立复审 |
| 交接/复核时间 | `2026-08-04T10:44:56+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | payload `6da4af6726cb14d29e89597a472fccbeae8bdb1a`；handoff `1e4004268016f9f4b0167fb392a6a4ff7ec116cf` |
| Cursor baseline | `dc4060da182b60fa5175710000379659babcd4ea` |
| Findings | first-parent、ordered stop、scope/empty/global prefix、summary tamper 已关闭；`SUPP-R2-GATE-IDENTITY-003`；`SUPP-R2-CONFIRMATION-EVIDENCE-001`；`SUPP-R2-NEGATIVE-E2E-001` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同分支 `SUPPLEMENTAL_ADMISSION_R2-r3` correction；不得重跑 retrieval，不解锁 readiness 或 downstream。 |

`EXT-pymc-20` 已绑定 verified first parent；producer/checker 现正确执行 ordered earliest stop、row20 tie、scope/empty/global exact-prefix guards。旧 `evil/repo` fully rebuilt attack 与 totals/per-repo/shortfall/confirmation tamper 均返回非零。提交计数保持 67/9/58，transport/no-downstream 不变。独立验证 targeted `200 passed`、full `460 passed, 10 warnings`，Ruff、compileall、admission/handoff/parent/transport checks 全通过。Standards PASS。

Spec 仍 FAIL。Verification log 请求 `SUPPLEMENTAL_ADMISSION_R2-r2`，但 handoff 和 producer 仍硬编码旧 Gate，且两个 checker 接受该不一致。更深的 confirmation attack 给 frozen `SCOPE.json` 增加字段并同步当前 handoff hash 后，`existing_files_unchanged=true` 仍被两个 checker 接受；readiness sentinel 也不可见，因为三个非 decision confirmation 仍是共享硬编码常量。最后，after-fifth、out-of-scope、empty-queue 新测试只是内存函数测试，未按 r2 scope 完成 fully rebuilt/guard-isolated end-to-end regression。

唯一 r3 correction 是绑定 exact gate identity、从 frozen hashes/command log/forbidden paths 真实证明 confirmation，并补六类 fully rebuilt isolated negatives。accepted-ready 仍为 18；`DISTRIBUTION_TARGET_AT_RISK` 和 no-substitution 保持，readiness/downstream 继续锁定。

### 5.32 SUPPLEMENTAL_ADMISSION_R2-r3 correction 复审

| 字段 | 记录 |
|---|---|
| Gate | `SUPPLEMENTAL_ADMISSION_R2-r3` |
| 记录类型 | admission correction 独立复审 |
| 交接/复核时间 | `2026-08-04T11:10:11+08:00` |
| Cursor 分支 | `origin/cursor/grok-phase3-supplemental-mining-r2`；draft PR #7 |
| Cursor commit | payload `8be5ac1dac12febe05afbb38d3afbc16d0d2732f`；handoff `2e3520969035a2cc4078eeaea9a9fac4083819ae` |
| Cursor baseline | `1e4004268016f9f4b0167fb392a6a4ff7ec116cf` |
| Findings | exact r3 label 已关闭；`SUPP-R2-GATE-BINDING-004`；`SUPP-R2-CONFIRMATION-EVIDENCE-002`；`SUPP-R2-NEGATIVE-E2E-002` |
| Verdict | `BLOCKED` |
| 本地集成 commit | N/A（PR #7 未集成） |
| 后继任务是否解锁 | 否；仅同分支 `SUPPLEMENTAL_ADMISSION_R2-r4` correction；不得重跑 retrieval，不解锁 readiness 或 downstream。 |

正向工件保持 67/9/58、A2 全 PENDING、transport freeze 和 `DISTRIBUTION_TARGET_AT_RISK`；独立验证 targeted `206 passed`、full `466 passed, 10 warnings`，Ruff、compileall、admission/handoff/parent/transport checks 均通过。Standards PASS、0 findings。

Spec 仍 FAIL。Admission checker 删除 hash-bound verification log 后仍返回 0。SCOPE 自身加字段并同步 handoff hash、在 `data/external_slice/` 同级加入 readiness sentinel、或将 verification-log command 重封为 `run_readiness.py`，两套 checker 都仍返回 0。原因是 immutable hashes 来自可变 SCOPE、path scan 只覆盖 supplemental 子目录、command scan 只读旧 COMMAND_LOG。新增 full-chain tests 也未同步重建全部 downstream，且没有证明移除单一目标 guard 后攻击才逃逸。

唯一 r4 correction 是强制两 checker 存在性与 hash-binding、用固定 transport baseline 锚定所有 immutable inputs、扫描两份 command log 与仓库级 downstream path boundary，并为全部攻击补 fully synchronized/both-checker/guard-isolated negatives。accepted-ready 仍为 18；shortfall/no-substitution 保持，readiness/downstream 全部锁定。
