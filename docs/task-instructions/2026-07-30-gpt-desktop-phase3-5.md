# GPT Desktop / GPT-5.6 Sol High：Phase 3–5 审计与集成任务指令

## 1. 身份、分支与目标

你运行在本地 GPT Desktop，模型固定为 **GPT-5.6 Sol High**。

- 工作分支：`codex/gpt-desktop-phase3-5`
- 基线：`main@d91083af4b368457245adbcc4d55ac2b2f786822`
- 对端执行分支：`cursor/grok-phase3-5-execution`
- 主责：方法学审计、冻结门禁、结果复核、单一 lineage 集成、Phase 4 论证写作、Phase 5 最终审计
- 非主责：云端批量复现、kill 执行、原始运行结果生成、代替人类标注者

目标是让 Cursor VM / Grok 4.5 High Fast 生成的机器证据经过本地独立审计后，按预注册时序进入唯一研究 lineage。任何门禁未通过时停止集成，并把 finding 返回 Cursor 分支。

## 2. 开工前必读

按以下顺序完整阅读：

1. `docs/superpowers/specs/2026-07-29-p3-phase3-5-dual-model-execution-design.md`
2. `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`
3. `docs/superpowers/plans/论证提升-phase3-terra.md`
4. `docs/superpowers/plans/论证提升-phase4-fable.md`
5. `docs/superpowers/plans/论证提升-phase5-grok.md`
6. `docs/review_20260730/defect4mr_64_pool_audit.md`
7. `docs/review_20260728/external_admission_runbook.md`
8. `research/prereg_v2/external_slice_protocol.md`
9. `research/prereg_v2/hypotheses.md`
10. `scripts/prereg/analysis_hcal_hrank.py`

若文件之间冲突，优先级为：预注册冻结文件与 amendment > argumentation master > 双模型规格 > phase 拆分文件 >任务指令。发现冲突时记录 finding，不自行改口径。

## 3. 本地命令纪律

本仓库所有 shell 命令必须加 `rtk` 前缀。管道中的每个命令也必须分别加前缀。

首次进入分支：

```bash
rtk git status --short --branch
rtk git fetch origin
rtk git rev-parse HEAD
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
```

预期基线：`233 passed`。直接运行 pytest 会因 src-layout 未安装而导入不到 `p2`，因此验证命令必须显式设置 `PYTHONPATH=src`。

禁止把主工作区中未跟踪的 `artifacts/` 或投稿临时产物纳入本分支。

## 4. 双环境交接合同

Cursor 每次交接必须提供：

1. 执行分支和不可变 commit SHA。
2. 基线 commit。
3. 输入 manifest 与 SHA256。
4. 精确执行命令、环境与依赖版本。
5. 输出清单与 SHA256。
6. 退出码、失败、排除、重试记录。
7. 尚未解决的异常。

接收交接时先执行：

```bash
rtk git fetch origin
rtk git show --stat --oneline <CURSOR_COMMIT>
rtk git diff <CURSOR_BASE>..<CURSOR_COMMIT> --name-status
```

审计结论只允许：

- `PASS`：零 blocker，可进入下一门禁。
- `PASS_WITH_DISCLOSURE`：方法学不受损，但必须携带明确披露。
- `BLOCKED`：不得合并、不得启动后继结果生成。

模型意见不投票。分歧按预注册、固定哈希和原始证据裁决；仍无法裁决时停下请求作者。

## 5. Task S0：建立审计台账

创建：

```text
docs/review_20260730/phase3_5_dual_model_audit_ledger.md
```

每次交接记录：

- gate 名称
- Cursor commit
- 输入/输出 hash
- 审计命令
- findings
- verdict
- 本地集成 commit
- 后继任务是否解锁

仅提交审计台账和门禁报告，不改写 Cursor 原始日志。

## 6. Task S1：Gate A0 — Defect4MR sanitized import 审计

### 输入

Cursor 应提交：

```text
scripts/external_slice/import_defect4mr_pool.py
tests/external_slice/test_import_defect4mr_pool.py
data/external_slice/defect4mr_import/candidates_sanitized.json
data/external_slice/defect4mr_import/PROVENANCE.json
data/external_slice/defect4mr_import/IMPORT_LOG.md
```

### 必查项

1. provenance 固定为：
   - repo=`meng004/P12-Defect4MR`
   - commit=`2bf7c2401c846544e715d879eb639e8c3bf44067`
   - source path=`data/ledgers/candidates.json`
   - blob=`1469a2e2b15dcb2cdf59d185f3ec92f58fb77189`
2. sanitized manifest 恰好 64 条。
3. 状态分布为 35/16/12/1。
4. `provisional_id` 唯一。
5. 采用字段 allowlist；不得包含：
   - `mr_mapping`
   - `proposed_mr_oracle`
   - `reviewer_note`
   - `reproduction_risk`
   - mutation、kill、fiber、analysis alias
6. 导入脚本不把原始 ledger 写入 P3 工作区。
7. 导入 VM 的产出中不存在 admission 判断。

执行：

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/external_slice/test_import_defect4mr_pool.py -q
rtk jq 'length' data/external_slice/defect4mr_import/candidates_sanitized.json
rtk jq 'group_by(.status) | map({status: .[0].status, count: length})' data/external_slice/defect4mr_import/candidates_sanitized.json
rtk rg -n -i 'mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|kill|fiber|analysis_id' data/external_slice/defect4mr_import
```

最后一条预期无输出。将审计写入：

```text
docs/review_20260730/gate_a0_defect4mr_import.md
```

Gate A0 未 PASS 前，不审计 admission。

## 7. Task S2：Gate A1 — 64 池 admission 审计

### 输入

```text
data/external_slice/admission_sheet.cursor_candidate.csv
data/external_slice/admission_evidence/
data/external_slice/HANDOFF_ADMISSION.json
```

### 审计原则

1. 64 个 Defect4MR 候选全部有一行裁决，不因来源 status 预先跳过。
2. 原 `verified_full` 只是输入证据，不自动等于本研究 admission。
3. 只允许预注册三条准入标准：
   - public real defect + public fix
   - buggy/fixed dual-arm reproduction
   - numerical-kernel scope
4. `candidate_full` 若仍无公开 fixed arm，不能把历史单臂证据当双臂 PASS。
5. `REPRO_FAILED` 保留原位，不用方便样本替换。
6. admission 阶段 `analysis_id` 必须为空。
7. 9 行 supplemental pilot 单独标识来源；不能替代 64 池完整重裁。
8. 不得出现 MR、kill、fiber、operator 或预测信息泄漏。

逐案抽取 issue、fix、buggy/fixed SHA 和复现证据，形成：

```text
docs/review_20260730/gate_a1_admission_audit.md
docs/review_20260730/gate_a1_findings.csv
```

只有零 blocker 时，才由本地集成分支生成 canonical：

```text
data/external_slice/admission_sheet.csv
data/external_slice/FREEZE.sha256
```

admission freeze 必须是独立 commit，且 commit 中不得包含 kill、预测或运行结果。

## 8. Task S3：Gate A2 — 人类标注与 fiber freeze 审计

Sol 不能充当标注者，也不能用 LLM 标签补齐缺失的人类标签。

审计：

1. 标注包只有缺陷描述与 fix diff，无 MR/kill 信息。
2. DEF-CAL 训练 10 例未进入确认性池。
3. 两名人类独立标注；若启用降级，必须是一名人类且 test–retest 间隔不少于两周。
4. κ 计算使用冻结脚本。
5. κ<0.6 时仅允许预注册的一轮修订重标。
6. 仲裁记录完整。
7. `analysis_id` 仅在 mapping freeze 后回填。

输出：

```text
docs/review_20260730/gate_a2_fiber_audit.md
```

fiber freeze commit 必须早于任何 kill 执行。

## 9. Task S4：Gate B — prediction freeze 独立审计

此任务必须在专用、无结果的本地工作树执行。该工作树固定到 Gate A 完成后的 commit，不得 fetch、checkout 或读取 Phase 3.4 结果分支。

审计输入：

- frozen admission
- frozen fiber map
- frozen MR instances 与 hash
- THM-WIN
- `predictions_frozen.cursor_candidate.json`

逐项复算：

1. 每个 `(defect, MR set)` 的 detect/miss 预测可由冻结规则机械推出。
2. MR 集排序预测完整。
3. 输入 hash 与 freeze registry 一致。
4. prediction commit 不含 `runs/`、kill matrix 或分析结果。
5. 预测文件 schema、记录数、唯一键和排序稳定。

输出：

```text
docs/review_20260730/gate_b_prediction_audit.md
```

PASS 后，本地集成分支写入：

```text
data/external_slice/predictions_frozen.json
data/external_slice/FREEZE.sha256
```

形成独立 prediction freeze commit 并 push。只有该 commit 已存在且审计报告 PASS，才能通知 Cursor 启动 Phase 3.4。

## 10. Task S5：CHECKPOINT 3 结果审计

所有 Cursor 项目分片汇合后，审计：

1. frozen manifest 中每个 ready defect 恰好覆盖一次。
2. 每个分片均使用同一 prediction freeze commit。
3. buggy/fixed、aligned/cross/v5/random floor 四条件记录完整。
4. 原始输出未被人工修改。
5. `analysis_hcal_hrank.py` 与预注册冻结版本一致。
6. aligned 主口径 McNemar、fixed-arm FPR、项目等权 Kendall τ、合格项目数 J、paired bootstrap CI、MS/PC 对比均按冻结定义。
7. `PROTOCOL_AMBIGUOUS`、`REPRO_FAILED`、OUT_OF_SCOPE 和不合格项目按预注册处置。
8. 失败假设不改阈值、不换主口径、不隐藏。

输出：

```text
docs/review_20260730/checkpoint3_external_results_audit.md
```

将 claim 状态限定为 `supported`、`observed`、`qualified`、`insufficient` 或 `blocked`。CHECKPOINT 3 必须等待作者确认降级叙事。

## 11. Task S6：Phase 4 论证与本地集成

在 prediction freeze 后可先行：

- §1 旗舰主张、RQ 表和论文边界
- §3 方法、准入、盲化和 baseline
- RQ2、RQ3
- §5 缺口归因与有界比较
- §6 Threats

RQ4 数字、外部校准图与外部结果解释必须等待 CHECKPOINT 3。

规则：

1. 数字只来自 SSOT。
2. `qualified/observed` 不得升级为普适结论。
3. 失败假设按预注册降级。
4. 每节修改后执行：

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python scripts/check_ssot_consistency.py
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
```

Grok 生成的机械注入和图表只能按审计后的 commit 集成。全文完成后形成 CHECKPOINT 4 通读报告并等待作者拍板。

## 12. Task S7：Phase 5 最终审计

Cursor 完成流水线并 push 后，复核：

1. 引文真实性与正文支持关系。
2. 引文审计 `✗=0`、`△≤5`。
3. humanizer diff 无技术语义或数字漂移。
4. H-/EXP-/THM-/RQ 标签一致。
5. 数学符号先定义后使用。
6. `Missing character=0`。
7. em-dash=0。
8. tarball 含 `.bbl` 且可独立编译。
9. 投稿 PDF、supplementary、cover-letter 素材与 arXiv 包来自同一终稿 commit。

输出：

```text
docs/review_20260730/phase5_final_audit.md
```

最终审计 PASS 后才能建议作者创建投稿 tag；不得自行投稿。

## 13. Git 与提交规则

- 不直接提交到 `main`。
- 不重写 Cursor 原始结果。
- 每个 gate 单独 commit。
- finding 修复由 Cursor 分支完成，本地只复核修复 commit。
- 每次提交前执行完整 233-test 基线。
- 推送目标仅为 `origin/codex/gpt-desktop-phase3-5`。

建议提交信息：

```text
docs(audit): verify Defect4MR sanitized import
docs(audit): gate external admission freeze
docs(audit): gate external fiber mapping
docs(audit): verify prediction freeze
docs(audit): review external validation results
docs(manuscript): integrate audited phase 4 argumentation
docs(audit): complete phase 5 final integrity review
```

## 14. 立即执行边界

开始时只执行 Task S0，确认分支和基线；随后等待 Cursor 的 Gate A0 import commit。没有 Cursor commit 时，不提前编造审计结果，不重做 64 池导入，也不启动 admission。
