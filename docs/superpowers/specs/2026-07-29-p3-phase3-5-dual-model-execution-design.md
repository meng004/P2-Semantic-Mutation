# P3 Phase 3–5 双模型交叉门禁执行设计

**日期：** 2026-07-29  
**范围：** 从当前 `main` 的 Phase 3 未完成项继续，完成 Phase 3、Phase 4、Phase 5；不重跑已完成的 Phase 0–2 与理论增强 Phase。  
**模型：** GPT-5.6 Sol（以下简称 Sol）与 Grok 4.5 High/Fast（以下简称 Grok）。  
**运行环境：** Cursor 云端 VM，每个执行单元独立 VM、独立分支、独立输出目录。

## 1. 目标与成功条件

目标是在不破坏预注册、盲法、预测冻结和证据 lineage 的前提下，利用 Grok 的长时工具执行能力与 Sol 的高密度推理/审计能力，缩短 Phase 3–5 的关键路径。

成功条件：

1. Phase 3 的 admission、fiber 映射、MR 实例化、预测和执行结果具有可审计的分离提交。
2. 任何预测冻结 commit 均早于首个 kill 结果 commit。
3. Grok 不替代 Phase 3.2 要求的人类标注者。
4. Phase 3.4 可按项目分片并行，但所有分片读取同一冻结 manifest，且不直接修改共享 SSOT。
5. Phase 4 的数字、裁决和主张强度均可追溯到 SSOT、预注册和 Phase 3 结果。
6. Phase 5 的引文、编译、标签、字符和投稿包验收满足 master plan §1.7。

## 2. 当前基线

- Phase 0–2、CHECKPOINT 2 与理论增强线已经完成。
- Phase 3.1 已形成 9 行补充挖掘试点，其中 6 例为 `ADMIT_PENDING_REPRO`；Defect4MR 64 池工件当前不在工作区。
- Phase 3.2 的标注包与 κ 计算路径已就绪，但仍需两名人类标注者；预注册降级仍至少需要一名人类和不少于两周的 test–retest。
- 理论 T3 与 T6.1 已完成，因此它们不再阻塞 Phase 3.3 和 Phase 4。
- Phase 4、Phase 5 尚未开始。

## 3. 方案比较与选择

### 方案 A：按 Phase 独占模型

一个 Phase 从头到尾只由一个模型负责。优点是交接少；缺点是准入判断、预测生成、结果解释可能形成同源偏差，且 Phase 3 同时包含高判断密度任务和高执行密度任务。

### 方案 B：所有关键任务双跑择优

Sol 与 Grok 对同一任务各自产出，再由作者选择。优点是覆盖面高；缺点是成本接近翻倍，容易产生两个不兼容的冻结物，不适合预注册研究的单一 lineage。

### 方案 C：双模型交叉门禁

Grok 主执行，Sol 主审计；关键冻结物只保留一个候选版本，由另一模型根据冻结协议和证据清单签核。若两模型意见不一致，不进行投票，由 master plan、预注册和可复算证据裁决；需要改变冻结规则时只能走 amendment 或作者门禁。

**选择：方案 C。** 它兼顾速度、独立审计和单一证据 lineage，且已获作者批准。

## 4. 模型职责

### 4.1 Grok 4.5

主责：

- GitHub 缺陷挖掘、双臂构建、触发复现和批量日志整理。
- 基于已冻结规则生成结构化候选表、预测文件和 manifest。
- Phase 3.4 四条件实验、MS/PC 基线、确定性分析脚本运行。
- 图表生成、SSOT 数字注入、LaTeX 编译、引用与标签扫描、投稿包构建。

约束：

- 不充当 Phase 3.2 的人类标注者。
- 不独立批准 admission freeze、fiber freeze 或 prediction freeze。
- 看过 kill 结果的 Grok 会话不得回到预测生成角色。
- 对论文主张只能使用 claim ledger 已允许的强度，不得将 `observed`、`qualified` 或失败假设升级为普适结论。

### 4.2 GPT-5.6 Sol

主责：

- 逐案复核准入理由、复现证据、排除码和中性 ID 纪律。
- 审核盲化包、κ 门禁、仲裁记录和分析别名回填。
- 在不读取 kill 结果的会话中复核预测生成规则、MR 实例化哈希和 `predictions_frozen.json`。
- 复核 Phase 3.4 聚合、统计口径、失败路径和 H-CAL/H-RANK verdict。
- 主导 Phase 4 的论证结构、负结果叙事、威胁披露和 claim–evidence 对齐。
- 对 Phase 5 最终稿进行语义漂移、引用充分性和主张强度终审。

约束：

- 审计分支不直接重写原始运行结果。
- 发现错误时生成结构化 finding；修复由原执行分支或独立修复分支完成。
- 不能以更好的写作措辞替代缺失实验或证据。

### 4.3 人类门禁

作者保留以下不可委托决策：

- 提供或确认 Defect4MR 64 池工件来源。
- 安排 Phase 3.2 两名人类标注者，或明确启用预注册降级。
- 审批任何 amendment。
- 在 CHECKPOINT 3 确认负结果降级叙事。
- 在 CHECKPOINT 4 拍板全文和投稿包。

## 5. Cursor 云端 VM 拓扑

| VM/分支 | 模型 | 写入范围 | 可并行关系 |
|---|---|---|---|
| `phase3-admission-exec` | Grok High/Fast | admission 候选、reproducer、逐案日志 | 与人类标注准备并行 |
| `phase3-admission-audit` | Sol xhigh | 只写审计报告和 finding | admission 执行形成批次后启动 |
| `phase3-annotation-support` | Grok Fast | 盲化包生成、格式校验、κ 脚本输出 | 与 admission 后半并行；不生成标注结论 |
| `phase3-fiber-audit` | Sol xhigh | 盲化与 κ 审计报告 | 人类标注完成后启动 |
| `phase3-prediction-exec` | Grok High | 唯一预测候选与哈希清单 | admission/fiber/MR 三冻结后启动 |
| `phase3-prediction-audit` | Sol xhigh | 预测签核报告 | 必须使用无 kill 结果的干净 VM |
| `phase3-run-<project>` | Grok Fast/High | 对应项目的独立 `runs/<project>/` | prediction freeze 后按项目并行 |
| `phase3-results-audit` | Sol xhigh | 聚合与统计审计报告 | 所有运行分片汇合后启动 |
| `phase4-mechanical` | Grok High | SSOT 注入、图表、编译与一致性修复 | prediction freeze 后可与 Phase 3.4 并行 |
| `phase4-argumentation` | Sol xhigh | 章节论证、边界段、Threats、结果解释 | prediction freeze 后启动；RQ4 等待 Phase 3.4 |
| `phase5-pipeline` | Grok Fast/High | 引文审计表、构建产物、tarball | CHECKPOINT 4 后串行 |
| `phase5-final-audit` | Sol xhigh | 最终审计报告 | Grok 流水线完成后 |

每个 VM 必须从同一个经确认的基线 commit 创建。云端分支不得直接合并；由单一集成者按门禁顺序 cherry-pick 或合并。

## 6. 执行波次与门禁

### Wave A：外部切片与标注

1. Grok 执行 6 个 `ADMIT_PENDING_REPRO` 的双臂复现并继续补充挖掘。
2. Sol 分批复核 admission 证据；只有零 blocker 的记录可以进入 ready slice。
3. Grok 生成不含 MR/kill 信息的标注包。
4. 人类标注者独立标注；Grok 仅计算 κ 和生成机械报告。
5. Sol 复核盲化、κ、仲裁和降级路径。

**Gate A：** ready slice、admission hash、fiber map、analysis alias 分别满足计划要求并形成结果前提交。

### Wave B：预测冻结

1. Grok 在干净 VM 中读取 frozen admission、frozen fiber map、frozen MR instances 和 THM-WIN，生成唯一预测候选。
2. Sol 在另一台无 kill 数据的干净 VM 中逐项复算/审计预测。
3. finding 清零后写入 `predictions_frozen.json` 和 `FREEZE.sha256`，单独 commit。

**Gate B：** prediction freeze commit 已推送并由 Sol 签核。未通过 Gate B 不得启动任何 kill 执行。

### Wave C：运行分片与 Phase 4 前半

1. Grok 按项目分片执行 Phase 3.4；每个分片只写自己的目录。
2. Grok 可并行运行 MS 与 PC 基线，但必须读取相同 frozen manifest。
3. 同时，Grok 建立 Phase 4 工作副本、完成 SSOT 机械注入与前三幅非外部结果图。
4. Sol 编写或重构 §1、§3、RQ2、RQ3、§5、§6；RQ4 仅保留可编译结构，不预写结果方向。

### Wave D：结果汇合与 CHECKPOINT 3

1. 单一集成者聚合所有 Phase 3.4 分片。
2. Grok 运行冻结的 `analysis_hcal_hrank.py` 并生成 SSOT 候选。
3. Sol 复核样本纳入、项目等权、McNemar、Kendall τ、bootstrap、基线比较和失败披露。
4. 作者在 CHECKPOINT 3 确认 H-CAL/H-RANK 的预注册 verdict 与降级叙事。

### Wave E：Phase 4 汇稿

1. Grok 将经批准的外部结果注入 SSOT、RQ4 和外部校准图。
2. Sol 完成结果解释、论文边界、Threats 和 claim–evidence map。
3. Grok 执行逐节编译和 SSOT consistency。
4. Sol 终审全文；作者完成 CHECKPOINT 4。

### Wave F：Phase 5

1. Grok 串行执行完整性检测、参考文献核查、proofread、humanizer 后检查、双遍编译和 arXiv 打包。
2. Sol 对 humanizer diff、引用充分性、符号和主张强度做最终审计。
3. 所有门槛通过后才能创建提交与投稿 tag。

## 7. 文件所有权与交接合同

共享文件实行单写者：

- `data/external_slice/FREEZE.sha256`：只由 Gate A/B 集成分支写。
- `data/external_slice/predictions_frozen.json`：只由 prediction integration 写。
- `research/paper_numbers.yaml` 及其他 SSOT：只由 results/manuscript integration 写。
- `submission/TOSEM_regular_v2_workdir/main.tex`：只由 Phase 4 集成分支写。

执行 VM 交接时必须提供：

1. 基线 commit 与当前 commit。
2. 精确命令、环境/依赖版本和退出码。
3. 输入 manifest 与 SHA256。
4. 输出文件清单与 SHA256。
5. 失败、排除和重试记录。
6. 未解决 finding 列表。

## 8. 分歧与失败处理

- **模型分歧：** 不投票。先对照 master、预注册、冻结哈希和原始证据；仍无法裁决时升级作者。
- **Defect4MR 工件仍不可用：** 继续预注册白名单补充挖掘；不得虚构 64 池重裁已完成。
- **ready n<20 或项目数不足：** 执行已冻结的补充挖掘预算；仍不足则按实际 n 报告并保留限制，不事后降低门槛。
- **κ<0.6：** 仅允许预注册的一轮协议修订重标；仍失败则按既定敏感性分析降级。
- **复现失败：** 保留 `REPRO_FAILED`，不以方便样本替换。
- **揭盲后发现协议歧义：** 标记 `PROTOCOL_AMBIGUOUS`，主分析排除并提供含入敏感性分析。
- **运行分片环境漂移：** 该分片无效，修复环境后从冻结输入重跑；禁止人工修改原始结果使其通过。
- **humanizer 语义漂移：** 技术语句和数字逐 diff 复核；数字变化一律回滚至 SSOT。

## 9. 验证策略

每一门禁采用“执行证据 + 异源审计”：

- Grok 产出机器可复算证据、测试输出和 hash。
- Sol 产出逐条 finding 与 PASS/BLOCKED 结论。
- 作者只在 CHECKPOINT 或 amendment 处做判断，不介入正常批处理。

最终验收至少包括：

- 冻结时序检查：所有规格 commit 早于结果 commit。
- 工作区中性纪律检查：admission 阶段不存在 MR/kill 泄漏和 analysis alias。
- 分片完整性检查：manifest 每个 ready defect 恰好由一个项目分片覆盖。
- SSOT consistency exit 0。
- 引文审计 `✗=0`、`△≤5`。
- `Missing character=0`、em-dash=0。
- arXiv tarball 包含 `.bbl` 并可独立编译。

## 10. 非目标

- 不重跑 Phase 0–2。
- 不改变已冻结假设、阈值、统计口径或 stopping rule。
- 不让模型替代人类标注者或作者 CHECKPOINT。
- 不在 Phase 3 结果出现后重新生成预测。
- 不以多模型多数票替代证据裁决。
