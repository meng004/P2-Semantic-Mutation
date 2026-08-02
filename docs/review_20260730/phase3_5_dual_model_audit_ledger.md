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
| Gate SUPPLEMENTAL_ADMISSION_R1 — supplemental mining | handoff `ac887e8a4a980dafca31c9ee803ec971a57698bc`；payload `a1cc795f340c38b340550c6789ece72a00c4c316`；scope `e108b82d38e53d89991960266385edf62da9eefc` | `BLOCKED` | N/A（未集成） | 否；仅 R1 correction 解锁，12 条 proposed rows 不得进入 readiness |

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
