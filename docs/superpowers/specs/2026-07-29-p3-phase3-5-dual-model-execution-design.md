# P3 Phase 3–5 双模型交叉门禁执行设计

**日期：** 2026-07-29；2026-07-30 按执行环境与 Defect4MR 来源修订  
**范围：** 从当前 `main` 的 Phase 3 未完成项继续，完成 Phase 3、Phase 4、Phase 5；不重跑已完成的 Phase 0–2 与理论增强 Phase。  
**环境 A：** Cursor 云端 VM，模型固定为 Grok 4.5 High Fast（以下简称 Grok）；每个执行单元独立 VM、独立分支、独立输出目录。  
**环境 B：** 本地 GPT Desktop，模型固定为 GPT-5.6 Sol High（以下简称 Sol）；负责审计、集成、门禁报告和论文论证，不在 Cursor VM 中运行。

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
- Phase 3.1 已形成 9 行补充挖掘试点，其中 6 例为 `ADMIT_PENDING_REPRO`。
- Defect4MR 64 池已定位到私有 GitHub 仓库 `meng004/P12-Defect4MR`（用户给出的 `github.com/meng004/defect4mr` 会解析到该仓库）。本计划钉扎 `main` 提交 `2bf7c2401c846544e715d879eb639e8c3bf44067`，不跟随分支漂移。
- Phase 3.2 的标注包与 κ 计算路径已就绪，但仍需两名人类标注者；预注册降级仍至少需要一名人类和不少于两周的 test–retest。
- 理论 T3 与 T6.1 已完成，因此它们不再阻塞 Phase 3.3 和 Phase 4。
- Phase 4、Phase 5 尚未开始。

## 3. Defect4MR 64 池工件判定

### 3.1 权威清单

- 仓库：`https://github.com/meng004/P12-Defect4MR`
- 固定提交：`2bf7c2401c846544e715d879eb639e8c3bf44067`
- 64 池 SSOT：`data/ledgers/candidates.json`
- SSOT blob SHA：`1469a2e2b15dcb2cdf59d185f3ec92f58fb77189`
- entry schema：`schemas/candidate.schema.json`

固定提交上的 64 条记录分布为：

| status | 数量 |
|---|---:|
| `verified_full` | 35 |
| `candidate_full` | 16 |
| `rejected` | 12 |
| `candidate_needs_oracle` | 1 |

台账覆盖 31 个项目标签。`README.md` 明确把 `data/ledgers/candidates.json` 定义为 authoritative defect ledger。仓库自带 71 项单元测试在固定提交上全部通过。

### 3.2 关联工件

- `reports/cloud/<case>-verification.md`：逐案验证报告；35 个 `verified_full` 中 34 个有同名 verification report，`A-MAGMA-002` 使用独立 GPU round judgment 报告。
- `scripts/cloud/<case>-verification/`：34 个 `verified_full` 的复现脚本目录；`A-MAGMA-002` 为 GPU 特殊路径。
- `data/registry/cases.yaml` 与 `data/registry/cases.json`：35 个 `verified_full` 的一一对应双臂运行注册表。
- `tools/d4mr/` 与 `docs/d4mr-CONTRACT.md`：`list/info/checkout/run/verify` CLI 与双臂判决契约。
- `data/mutation/`：下游变异实验资料，不是 64 池 admission SSOT。
- `data/kappa/`：既有 14 例标注材料，不是 64 池清单，也不能直接替代本研究预注册抽取。

### 3.3 可执行性边界

`data/registry/cases.json` 的 35 个 ID 与 `verified_full` 完全一致，其中 34 个为 tier A、`A-MAGMA-002` 为需 GPU 的 tier B。然而只有 3/35 个容器镜像已填 digest，32/35 仍为 `digest: null`。因此：

1. 64 池导入与逐案重裁已经解除 blocker。
2. 不能把 `verified_full` 等同于“当前 Cursor VM 可直接拉取镜像复跑”。
3. 有 digest 的案例可优先走 `tools.d4mr verify`；无 digest 案例必须依据 verification report 重建双臂，或先完成镜像发布与 digest 钉扎。
4. `v1.0.1` tag 仅有 34 `verified_full` + 17 `candidate_full`，与 master plan 使用的 35/16 口径不一致；本阶段必须使用上述固定 `main` commit，不能改用 `v1.0.1`。

### 3.4 防泄漏导入

原始 `candidates.json` 含 `mr_mapping` 与 `proposed_mr_oracle`，不能直接交给 admission 裁决会话。导入分两步：

1. 独立的一次性机械导入任务验证 commit、blob SHA、64 条计数和 schema，生成只含来源、修订、modified files、排除检查和风险说明的 sanitized manifest；该任务结束后不得参与 admission 裁决。
2. admission 执行与审计只读取 sanitized manifest、公共 issue/fix 证据和双臂复现结果；不得读取原始 MR 映射、oracle、mutation 结果或既有 kill 数据。

原始文件不复制进 P3 admission 工作目录，只记录仓库、固定 commit、blob SHA 和导入日志。9 行补充挖掘试点保留为 supplemental source，不替代 64 池。

## 4. 方案比较与选择

### 4.1 方案 A：按 Phase 独占模型

一个 Phase 从头到尾只由一个模型负责。优点是交接少；缺点是准入判断、预测生成、结果解释可能形成同源偏差，且 Phase 3 同时包含高判断密度任务和高执行密度任务。

### 4.2 方案 B：所有关键任务双跑择优

Sol 与 Grok 对同一任务各自产出，再由作者选择。优点是覆盖面高；缺点是成本接近翻倍，容易产生两个不兼容的冻结物，不适合预注册研究的单一 lineage。

### 4.3 方案 C：双模型交叉门禁

Grok 主执行，Sol 主审计；关键冻结物只保留一个候选版本，由另一模型根据冻结协议和证据清单签核。若两模型意见不一致，不进行投票，由 master plan、预注册和可复算证据裁决；需要改变冻结规则时只能走 amendment 或作者门禁。

**选择：方案 C。** 它兼顾速度、独立审计和单一证据 lineage，且已获作者批准。

## 5. 模型与环境职责

### 5.1 Cursor VM / Grok 4.5 High Fast

主责：

- 一次性 Defect4MR sanitized manifest 机械导入；该导入 VM 不再承担 admission。
- GitHub 缺陷挖掘、双臂构建、触发复现和批量日志整理。
- 基于已冻结规则生成结构化候选表、预测文件和 manifest。
- Phase 3.4 四条件实验、MS/PC 基线、确定性分析脚本运行。
- 图表生成、SSOT 数字注入、LaTeX 编译、引用与标签扫描、投稿包构建。

约束：

- 不充当 Phase 3.2 的人类标注者。
- 不独立批准 admission freeze、fiber freeze 或 prediction freeze；这些门禁由本地 Sol 审计。
- 看过 kill 结果的 Grok 会话不得回到预测生成角色。
- 对论文主张只能使用 claim ledger 已允许的强度，不得将 `observed`、`qualified` 或失败假设升级为普适结论。

### 5.2 本地 GPT Desktop / GPT-5.6 Sol High

主责：

- 逐案复核准入理由、复现证据、排除码和中性 ID 纪律。
- 审核盲化包、κ 门禁、仲裁记录和分析别名回填。
- 在不读取 kill 结果的会话中复核预测生成规则、MR 实例化哈希和 `predictions_frozen.json`。
- 复核 Phase 3.4 聚合、统计口径、失败路径和 H-CAL/H-RANK verdict。
- 主导 Phase 4 的论证结构、负结果叙事、威胁披露和 claim–evidence 对齐。
- 对 Phase 5 最终稿进行语义漂移、引用充分性和主张强度终审。

约束：

- 本地审计工作树不直接重写 Cursor VM 的原始运行结果。
- 发现错误时生成结构化 finding；修复由原执行分支或独立修复分支完成。
- 不能以更好的写作措辞替代缺失实验或证据。
- prediction audit 必须在固定到 Gate A/B 前置 commit 的独立本地工作树中完成；该工作树不得 fetch、checkout 或读取 Phase 3.4 结果分支。

### 5.3 人类门禁

作者保留以下不可委托决策：

- 若需要偏离固定 Defect4MR commit，批准新的来源版本与口径迁移。
- 安排 Phase 3.2 两名人类标注者，或明确启用预注册降级。
- 审批任何 amendment。
- 在 CHECKPOINT 3 确认负结果降级叙事。
- 在 CHECKPOINT 4 拍板全文和投稿包。

## 6. 双环境拓扑与交接

| 环境/分支 | 模型 | 写入范围 | 可并行关系 |
|---|---|---|---|
| Cursor `phase3-d4mr-import` | Grok 4.5 High Fast | sanitized manifest、来源/hash/计数日志 | 一次性任务；结束后不参与 admission |
| Cursor `phase3-admission-exec` | Grok 4.5 High Fast | admission 候选、reproducer、逐案日志 | 与人类标注准备并行 |
| 本地 `phase3-admission-audit` | GPT-5.6 Sol High | 只写审计报告和 finding | admission 执行形成批次并 push 后启动 |
| Cursor `phase3-annotation-support` | Grok 4.5 High Fast | 盲化包生成、格式校验、κ 脚本输出 | 与 admission 后半并行；不生成标注结论 |
| 本地 `phase3-fiber-audit` | GPT-5.6 Sol High | 盲化与 κ 审计报告 | 人类标注完成后启动 |
| Cursor `phase3-prediction-exec` | Grok 4.5 High Fast | 唯一预测候选与哈希清单 | admission/fiber/MR 三冻结后启动 |
| 本地 `phase3-prediction-audit` | GPT-5.6 Sol High | 预测签核报告 | 必须使用无 kill 结果的独立本地工作树 |
| Cursor `phase3-run-<project>` | Grok 4.5 High Fast | 对应项目的独立 `runs/<project>/` | prediction freeze 后按项目并行 |
| 本地 `phase3-results-audit` | GPT-5.6 Sol High | 聚合与统计审计报告 | 所有运行分片 push 并汇合后启动 |
| Cursor `phase4-mechanical` | Grok 4.5 High Fast | SSOT 注入、图表、编译与一致性修复 | prediction freeze 后可与 Phase 3.4 并行 |
| 本地 `phase4-argumentation` | GPT-5.6 Sol High | 章节论证、边界段、Threats、结果解释 | prediction freeze 后启动；RQ4 等待 Phase 3.4 |
| Cursor `phase5-pipeline` | Grok 4.5 High Fast | 引文审计表、构建产物、tarball | CHECKPOINT 4 后串行 |
| 本地 `phase5-final-audit` | GPT-5.6 Sol High | 最终审计报告 | Grok 流水线完成并 push 后 |

所有 Cursor VM 必须从同一个经确认的基线 commit 创建。Cursor 分支不得互相直接合并；每个执行单元 push commit 与 handoff manifest 后，由本地 Sol 工作树 fetch、审计并生成门禁报告。只有本地集成分支可以按门禁顺序 cherry-pick 或合并进入主 lineage。

## 7. 执行波次与门禁

### Wave A：外部切片与标注

1. 独立 Cursor import VM 从固定 Defect4MR commit 生成 sanitized 64-pool manifest，验证 64/35/16/12/1 计数并提交导入日志；任务结束。
2. 新 Cursor admission VM 只读取 sanitized manifest，按预注册三条准入逐案重裁全部 64 例。
3. Grok 优先对 35 个 `verified_full` 核查公开 fix 与双臂证据；3 个 digest-pinned 案可走 `tools.d4mr verify`，其余按报告重建。所有状态均需重新裁定，仓库原 status 不自动等于本研究 admission 结果。
4. Grok 并行执行 6 个 supplemental `ADMIT_PENDING_REPRO` 的双臂复现；只有 64 池不足时才按预注册预算继续补充挖掘。
5. 本地 Sol 分批复核 admission 证据；只有零 blocker 的记录可以进入 ready slice。
6. Grok 生成不含 MR/kill 信息的标注包。
7. 人类标注者独立标注；Grok 仅计算 κ 和生成机械报告。
8. 本地 Sol 复核盲化、κ、仲裁和降级路径。

**Gate A：** ready slice、admission hash、fiber map、analysis alias 分别满足计划要求并形成结果前提交。

### Wave B：预测冻结

1. Grok 在干净 VM 中读取 frozen admission、frozen fiber map、frozen MR instances 和 THM-WIN，生成唯一预测候选。
2. Sol 在无 kill 数据的独立本地工作树中逐项复算/审计预测。
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

## 8. 文件所有权与交接合同

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

Cursor → 本地的交接只通过已 push 的不可变 commit、manifest 与日志；不得用聊天文字代替运行证据。本地 → Cursor 的修复反馈使用 finding 文件与精确基线 commit，避免两个环境基线漂移。

## 9. 分歧与失败处理

- **模型分歧：** 不投票。先对照 master、预注册、冻结哈希和原始证据；仍无法裁决时升级作者。
- **Defect4MR 固定 commit 暂时不可访问：** 记录访问失败，不切换到口径不同的 `v1.0.1`；恢复访问后从固定 commit 导入。只有作者批准版本迁移后才能换源。
- **容器 digest 为空：** 不把 registry entry 当作可直接运行镜像；按 verification report 重建，或先完成镜像发布和 digest 钉扎。
- **ready n<20 或项目数不足：** 执行已冻结的补充挖掘预算；仍不足则按实际 n 报告并保留限制，不事后降低门槛。
- **κ<0.6：** 仅允许预注册的一轮协议修订重标；仍失败则按既定敏感性分析降级。
- **复现失败：** 保留 `REPRO_FAILED`，不以方便样本替换。
- **揭盲后发现协议歧义：** 标记 `PROTOCOL_AMBIGUOUS`，主分析排除并提供含入敏感性分析。
- **运行分片环境漂移：** 该分片无效，修复环境后从冻结输入重跑；禁止人工修改原始结果使其通过。
- **humanizer 语义漂移：** 技术语句和数字逐 diff 复核；数字变化一律回滚至 SSOT。

## 10. 验证策略

每一门禁采用“执行证据 + 异源审计”：

- Grok 产出机器可复算证据、测试输出和 hash。
- 本地 Sol 产出逐条 finding 与 PASS/BLOCKED 结论。
- 作者只在 CHECKPOINT 或 amendment 处做判断，不介入正常批处理。

最终验收至少包括：

- 冻结时序检查：所有规格 commit 早于结果 commit。
- Defect4MR provenance 检查：仓库、固定 commit、ledger blob SHA、64 条计数和状态分布全部匹配。
- sanitized import 检查：不含 `mr_mapping`、`proposed_mr_oracle`、mutation/kill 字段。
- 工作区中性纪律检查：admission 阶段不存在 MR/kill 泄漏和 analysis alias。
- 分片完整性检查：manifest 每个 ready defect 恰好由一个项目分片覆盖。
- SSOT consistency exit 0。
- 引文审计 `✗=0`、`△≤5`。
- `Missing character=0`、em-dash=0。
- arXiv tarball 包含 `.bbl` 并可独立编译。

## 11. 非目标

- 不重跑 Phase 0–2。
- 不改变已冻结假设、阈值、统计口径或 stopping rule。
- 不让模型替代人类标注者或作者 CHECKPOINT。
- 不在 Phase 3 结果出现后重新生成预测。
- 不以多模型多数票替代证据裁决。
