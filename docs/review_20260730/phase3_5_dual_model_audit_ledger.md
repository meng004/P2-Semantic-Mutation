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
| Gate A1a — C2 admission candidate audit（pre-readiness） | handoff `f31a508ae6409c18dca8229fbabdf77598e0345d`；payload `90640368d21fe2087a266d8726ec81c2e9c2c124` | `BLOCKED` | `N/A（未集成 C2 payload/handoff）` | 否；C3 readiness、canonical admission freeze 与 A2/C4 均保持锁定 |

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
