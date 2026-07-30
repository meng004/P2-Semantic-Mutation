# Cursor VM / Grok 4.5 High Fast：Phase 3–5 执行任务指令

## 1. 身份、分支与目标

你运行在 Cursor 云端 VM，模型固定为 **Grok 4.5 High Fast**。

- 工作分支：`cursor/grok-phase3-5-execution`
- 基线：`main@d91083af4b368457245adbcc4d55ac2b2f786822`
- 对端审计分支：`codex/gpt-desktop-phase3-5`
- 主责：机械导入、双臂复现、批量运行、预测候选、确定性分析、SSOT 机械注入、图表、编译与打包
- 非主责：批准冻结门禁、充当人类标注者、改变预注册口径、独立升级论文主张

本任务在 Cursor VM 中直接运行标准 shell 命令。若仓库其他说明要求命令包装器，以作者在本指令中的直接命令要求为准。

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

优先级：预注册冻结文件与 amendment > argumentation master > 双模型规格 > phase 拆分文件 > 本任务指令。遇到口径冲突时停止并形成 handoff finding，不自行选择更方便的解释。

## 3. VM 初始化与基线

```bash
git status --short --branch
git rev-parse HEAD
python3 --version
python3 -m pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest -q
```

预期基线：`233 passed`。如果依赖已经安装，可跳过重复安装，但必须记录 Python、编译器、系统和关键依赖版本。

不要把与任务无关的本地文件、缓存、凭据或投稿临时产物加入分支。

## 4. 通用执行纪律

1. 每个 gate 的规格、hash 与 schema 必须先于结果单独 commit。
2. 不把 specification 与 kill/result 放入同一个 commit。
3. 不修改预注册阈值、分析口径、stopping rule 或降级路径。
4. 不覆盖失败记录；使用 `REPRO_FAILED`、`PROTOCOL_AMBIGUOUS` 等冻结编码。
5. 不用方便样本替换失败样本。
6. 所有命令、环境、输入/输出 hash、退出码和重试写入 handoff manifest。
7. 每次 push 后停止，等待本地 GPT Desktop / GPT-5.6 Sol High 的 gate verdict。
8. verdict 为 `BLOCKED` 时只修复 finding，不启动后继任务。
9. 看过 kill 结果的会话不得回到 prediction 生成角色。
10. Cursor 分支不直接合并到 `main`。

## 5. Task C0：建立执行台账

创建：

```text
data/external_slice/CURSOR_EXECUTION_LEDGER.md
```

每个任务记录：

- task/gate
- VM/session 标识
- baseline commit
- exact command
- environment
- input hash
- output hash
- exit code
- failure/retry
- output commit
- auditor verdict

## 6. Task C1：一次性 Defect4MR sanitized import

此任务必须使用独立 Cursor VM/session。该 session 完成后永久退出，不得承担 admission、标注、预测或结果任务。

### 固定来源

```text
repo: meng004/P12-Defect4MR
commit: 2bf7c2401c846544e715d879eb639e8c3bf44067
path: data/ledgers/candidates.json
blob: 1469a2e2b15dcb2cdf59d185f3ec92f58fb77189
```

### 采用测试驱动实现

创建：

```text
scripts/external_slice/import_defect4mr_pool.py
tests/external_slice/test_import_defect4mr_pool.py
data/external_slice/defect4mr_import/candidates_sanitized.json
data/external_slice/defect4mr_import/PROVENANCE.json
data/external_slice/defect4mr_import/IMPORT_LOG.md
```

先写失败测试，至少覆盖：

1. 固定 repo/commit/path/blob。
2. 总数 64。
3. 状态分布 35 `verified_full`、16 `candidate_full`、12 `rejected`、1 `candidate_needs_oracle`。
4. ID 唯一。
5. 输出只允许：
   - `provisional_id`
   - `project`
   - `status`
   - `evidence_depth`
   - `source_urls`
   - `revisions`
   - `modified_files`
   - `exclusions_checked`
6. 禁止字段：
   - `mr_mapping`
   - `proposed_mr_oracle`
   - `reviewer_note`
   - `reproduction_risk`
7. 输出中不得出现 mutation、kill、fiber、operator 或 analysis alias。
8. 原始 ledger 不写入 P3 仓库。

运行：

```bash
PYTHONPATH=src python3 -m pytest tests/external_slice/test_import_defect4mr_pool.py -q
PYTHONPATH=src python3 scripts/external_slice/import_defect4mr_pool.py \
  --repo meng004/P12-Defect4MR \
  --commit 2bf7c2401c846544e715d879eb639e8c3bf44067 \
  --output data/external_slice/defect4mr_import/candidates_sanitized.json
PYTHONPATH=src python3 -m pytest tests/external_slice/test_import_defect4mr_pool.py -q
jq 'length' data/external_slice/defect4mr_import/candidates_sanitized.json
grep -RniE 'mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|kill|fiber|analysis_id' \
  data/external_slice/defect4mr_import
```

最后一个命令预期无匹配。

提交：

```bash
git add scripts/external_slice/import_defect4mr_pool.py \
  tests/external_slice/test_import_defect4mr_pool.py \
  data/external_slice/defect4mr_import \
  data/external_slice/CURSOR_EXECUTION_LEDGER.md
git commit -m "data(external): import sanitized Defect4MR pool"
git push -u origin cursor/grok-phase3-5-execution
```

生成 `HANDOFF_IMPORT.json`，记录所有输入/输出 hash 与命令。push 后停止，等待本地 Gate A0。

## 7. Task C2：64 池 admission 候选

只有 Gate A0 `PASS` 后启动。必须新建 Cursor VM/session；只读 sanitized manifest，不读取 P12 原始 ledger、MR/oracle、mutation 或 kill 数据。

对全部 64 例应用预注册三条标准：

1. public real defect + identifiable public fix
2. buggy/fixed dual-arm reproduction
3. numerical-kernel scope

原仓库 status 只是来源字段，不是 P3 admission verdict。

输出候选而非 canonical freeze：

```text
data/external_slice/admission_sheet.cursor_candidate.csv
data/external_slice/admission_evidence/<neutral-id>/
data/external_slice/HANDOFF_ADMISSION.json
```

要求：

- 64 条全部有裁决记录。
- `analysis_id` 全空。
- 中性 ID 不编码类别。
- issue、fix、buggy SHA、fixed SHA 使用不可变完整值。
- 不得引用 MR、kill、fiber、operator 或预测。
- `candidate_full` 无 fixed arm 时不得伪装为 dual-arm PASS。
- 9 行 supplemental pilot 保留但单独标识来源，不替代 64 条。
- 失败案保留，不能换样本。

运行泄漏与结构检查，执行完整测试：

```bash
PYTHONPATH=src python3 -m pytest -q
python3 scripts/check_external_admission.py \
  --sheet data/external_slice/admission_sheet.cursor_candidate.csv
grep -RniE 'mr_mapping|proposed_mr_oracle|kill|fiber|analysis_id[^,]*[^,[:space:]]' \
  data/external_slice/admission_sheet.cursor_candidate.csv \
  data/external_slice/admission_evidence
```

若 `scripts/check_external_admission.py` 尚不存在，先用测试驱动方式实现，验证 64 条覆盖、三标准枚举、中性 ID、空 analysis alias 和禁止字段。

提交并 push 后停止，等待本地 Gate A1。不得自行写 `FREEZE.sha256`。

## 8. Task C3：双臂 readiness 执行

只有本地 Gate A1 批准的案例可进入 readiness。

优先级：

1. registry 中 3 个 digest-pinned 案例：使用 `tools.d4mr verify`。
2. 其余 `verified_full`：根据 verification report 和 scripts 重建双臂。
3. GPU、m32、MPI、QEMU、era-Julia 等平台门禁必须记录，不得降格为普通 VM 失败。
4. supplemental 6 个 pending 案按 runbook 执行。

每案保存：

```text
data/external_slice/reproduction/<neutral-id>/environment.json
data/external_slice/reproduction/<neutral-id>/buggy.json
data/external_slice/reproduction/<neutral-id>/fixed.json
data/external_slice/reproduction/<neutral-id>/stdout.log
data/external_slice/reproduction/<neutral-id>/stderr.log
```

同一 trigger、input、seed 必须用于两个 arm。失败标记 `REPRO_FAILED` 并保留，不替换。

分批执行，每批单独 commit、push、handoff；本地 Sol 可分批审计。达到 ready n≥20、项目≥8 后仍须完成冻结范围内所有已启动案例的记录，不能因达到阈值而丢弃失败。

## 9. Task C4：标注支持

只有 admission freeze commit 存在后启动。

职责仅限：

- 生成盲化包
- 格式校验
- 发放清单
- 机械计算 κ
- 生成报告

禁止：

- 充当人类标注者
- 用模型标签补齐人类标签
- 向标注材料泄露 MR、kill、预测或 analysis alias

两名人类完成标注后运行冻结 κ 代码，将原始评分、计算命令和输出提交。push 后等待本地 Gate A2。不得自行完成 fiber freeze。

## 10. Task C5：prediction candidate

只有 admission freeze、fiber freeze、MR instance freeze 与 THM-WIN 全部存在后启动。必须使用新的干净 Cursor VM/session，且该 session 不得接触任何 Phase 3.4 结果。

输入固定为：

- frozen admission
- frozen fiber map
- frozen MR instances
- THM-WIN

输出：

```text
data/external_slice/predictions_frozen.cursor_candidate.json
data/external_slice/HANDOFF_PREDICTIONS.json
```

要求：

- 每个 `(defect, MR set)` 一条 detect/miss 预测。
- 每个缺陷有 MR 集排序预测。
- 输入 hash 完整。
- schema、记录数、唯一键和排序稳定。
- commit 不含 `runs/`、kill 或观测结果。

提交并 push 后停止，等待本地 Gate B。不得自行把 candidate 改名为 canonical，也不得启动 kill 执行。

## 11. Task C6：Phase 3.4 执行与揭盲

只有本地 prediction freeze commit 已 push 且 Gate B 报告 `PASS` 后启动。

按项目分片：

- 每个项目独立输出 `data/external_slice/runs/<project>/`
- 所有项目读取同一 prediction freeze commit 与 manifest
- 每个 ready defect 恰好归属一个分片
- 四条件：aligned、cross、v5、random floor
- 两个 arm：buggy、fixed
- MS 与 PC 基线读取同一冻结输入

如果需要并行 VM，不允许多个 VM 同时写同一分支。为每个项目创建临时执行分支，完成后由 Cursor 主执行分支按 manifest 汇合；临时分支名和 commit 必须写入执行台账。

所有分片完成后：

```bash
PYTHONPATH=src python3 scripts/prereg/analysis_hcal_hrank.py
PYTHONPATH=src python3 -m pytest -q
```

生成结果候选和 handoff，但不修改预注册脚本。push 后等待本地 CHECKPOINT 3 审计。

## 12. Task C7：Phase 4 机械工作

prediction freeze 后可与 Phase 3.4 并行：

- 建立 v2 工作副本
- SSOT 数字机械注入
- 区间宽度图
- block heatmap
- dose-response 图
- 逐节编译
- SSOT consistency

RQ4 数字和外部校准图等待 CHECKPOINT 3。不要预写结果方向。

本地 Sol 负责论证、负结果叙事和 Threats；Cursor 只接收明确的集成 commit 或 finding。每轮机械修改后运行完整测试和编译，提交并 push。

## 13. Task C8：Phase 5 流水线

只有作者完成 CHECKPOINT 4 后启动，严格串行：

1. final-integrity stage
2. 引文真实性审计
3. 标签、符号、数字和交叉引用检查
4. humanizer
5. humanizer diff 技术字段扫描
6. 双遍编译
7. arXiv tarball 构建

门槛：

- 引文 `✗=0`
- `△≤5`
- `Missing character=0`
- em-dash=0
- SSOT consistency exit 0
- tarball 含 `.bbl`
- tarball 可独立编译

push 后等待本地 Sol 最终审计。不得自行创建投稿 tag，不得自行投稿。

## 14. Handoff manifest 最小 schema

每次交接 JSON 至少包含：

```json
{
  "task": "C1",
  "gate_requested": "A0",
  "branch": "cursor/grok-phase3-5-execution",
  "baseline_commit": "full sha",
  "output_commit": "full sha",
  "commands": [],
  "environment": {},
  "inputs": [{"path": "path", "sha256": "sha256"}],
  "outputs": [{"path": "path", "sha256": "sha256"}],
  "exit_codes": [],
  "failures": [],
  "retries": [],
  "unresolved_findings": []
}
```

不得用聊天摘要替代 manifest 和文件证据。

## 15. 立即执行边界

开始时只执行 C0 与 C1。C1 push 后停止并请求本地 Gate A0。未经 Gate A0 `PASS`，不得启动 C2；不得在同一 VM/session 中继续 admission。
