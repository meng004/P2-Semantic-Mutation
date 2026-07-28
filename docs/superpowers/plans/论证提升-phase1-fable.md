# 论证提升-phase1-fable：预注册包（适用矩阵 / 功效模拟 / 假设冻结 / 外部协议）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——预注册是方法学文本+统计设计的复合体；功效模拟代码由同一模型完成以保证与假设文本一致）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（符号与标识——假设一律用 H-ZERO/H-DISC/H-CONS/H-DOSE/H-CAL/H-RANK）、§1.1（对象集合定义，语义命名 KER-*/POOL-*/MRSET-*/DEF-*）、§1.2（RQ→假设→对象→方法→指标 链路总表，判据公式所在）、§1.3（预处理规范与统一标识——Task 1.4 须内嵌其 §1.3.1 挖掘规范）、§1.4（对象构建原则 P1–P7，预注册文本须引用）。内容冲突以 master 为准。

**前置门禁:** Phase 0 完成（REVIEW CHECKPOINT 0 已过）。**分段门禁**：Task 1.1/1.2/1.4 可在理论线 CHECKPOINT T2 之前先行；**Task 1.3（假设与分析代码冻结）与冻结 tag 必须等理论线 CHECKPOINT T2（THM-GAP 内部评审）通过**。

**并行性:** 与理论线 T1–T5 并行；Task 1.4 协议单独冻结（hash 入库）后，Phase 3 的 Task 3.1/3.2 即可启动，不必等本阶段全部完成。

**交接物:** `research/prereg_v2/` 全件（适用矩阵、功效报告、六假设、外部协议、FREEZE_MANIFEST）+ `prereg-v2-freeze` tag → Phase 2/3 的执行依据。

---

## Task 1.1：适用矩阵冻结

**Files:** Create: `research/prereg_v2/applicability_matrix.md`

- [ ] **Step 1:** 从算子设计文档与 v4 development 数据，对 5 算子 × 4 PUT 类逐格声明 applicable / inapplicable + 一句机理理由（例：SI 需要可注入结构位点，B 类采样核无 → inapplicable）
- [ ] **Step 2:** 声明规则：inapplicable 格不进 H-CONS 分母、不进 H-DISC 对比；预测零（COR-ZERO）与不适用零分别编码 `PRED_ZERO_ALIGN` / `NOT_APPLICABLE`
- [ ] **Step 3:** 两人独立填写后合并分歧（记录分歧格与仲裁理由）；`shasum -a 256` 值写入文件头
- [ ] **Step 4:** Commit

## Task 1.2：功效模拟与 MID 锁定

**Files:** Create: `scripts/prereg/power_simulation.py`；Output: `research/prereg_v2/power_report.md`

- [ ] **Step 1:** 从 v4 数据估计两部分分布参数：P(SMS>0|aligned)、P(SMS>0|cross)、非零部分的 Beta 拟合参数
- [ ] **Step 2:** 模拟设计变量网格：applicable cell 数 × 每 cell 变异体数 {20,30} × MR 集数（v5 held-out 份数 {1,2}）；每格 2000 次模拟，输出 H-ZERO（McNemar）与 H-DISC（条件 Cliff's δ=0.33）的功效
- [ ] **Step 3:** 选定最小达 0.8 功效的配置写入 power_report；若 KER 全集（12 核）配置全部 <0.8，触发"追加 4–8 个紧凑核"决策（列出候选核清单与选择标准，交作者拍板）
- [ ] **Step 4:** Commit

## Task 1.3：假设与分析代码冻结（门禁：理论线 CHECKPOINT T2 已过）

**Files:** Create: `research/prereg_v2/hypotheses.md`、`scripts/prereg/analysis_hzero.py`、`analysis_hdisc.py`、`analysis_hcons.py`、`analysis_hdose.py`、`analysis_hcal_hrank.py`

- [ ] **Step 1:** hypotheses.md 定稿六条（H-ZERO balanced accuracy ≥0.75 + McNemar；H-DISC 条件 δ ≥ 模拟锁定 MID + BCa CI；H-CONS Wilson 下界 >0.5；H-DOSE isotonic vs 常数置换检验；H-CAL accuracy/Brier 优于多数类；H-RANK 项目等权 Kendall τ ≥ MID，\(\tau_{\mathrm{SMS}}-\tau_{\mathrm{MS}}\) 描述性）；每条注明推导来源定理（THM-GAP/THM-WIN/COR-ZERO）与降级路径
- [ ] **Step 2:** 分析脚本按假设一比一实现，输入统一为 SSOT JSON 新键，输出统一 schema `{hypothesis, estimate, ci, p, verdict}`；对空输入跑通冒烟测试（合成数据）
- [ ] **Step 3:** 冻结机制：`git tag prereg-v2-freeze && shasum -a 256 research/prereg_v2/* scripts/prereg/*.py > research/prereg_v2/FREEZE_MANIFEST.sha256`
- [ ] **Step 4:** Commit

## Task 1.4：外部切片准入与映射协议

**Files:** Create: `research/prereg_v2/external_slice_protocol.md`

- [ ] **Step 1:** 准入三条（且仅三条）：真实缺陷（公开 issue+fix commit）；双臂可复现（buggy/fixed 构建+触发）；in-scope（单/少输出数值核，签名可适配）。**明文排除** "MR 可判别"条件并注明这是对 D0 循环的修正
- [ ] **Step 1b:** 内嵌 master §1.3.1 挖掘规范：仓库白名单定稿（Defect4MR 覆盖项目 + numpy/scipy/scikit-learn/statsmodels/PyMC/GPy/GPyTorch/chaospy/SALib 候选池取舍）、issue 检索信号词与排除类清单、语义符合性判定模板（issue URL + buggy SHA + fixed SHA + 一句机理）、两段式统一标识规则（准入期 `EXT-<repo>-<序号>`，映射冻结后 `bug-<算子代号>-<序号>`；准入期禁止出现算子归类）
- [ ] **Step 2:** fiber 映射协议：两名标注者、训练集=DEF-CAL（verified_full）中 10 例（development）、标签集 {DIRECT, ADJACENT, OUT_OF_SCOPE, UNCERTAIN}、盲化规定（不见 kill 结果、不见对方标注）、κ≥0.6 门禁、分歧仲裁程序
- [ ] **Step 3:** 冻结预测协议：执行前对每 (defect, MR set) 产出 detect/miss 预测 + 每 MR 集 SMS 排序预测，`shasum -a 256` 存证；揭盲规则
- [ ] **Step 4:** Commit（协议单独冻结后即可通知 `论证提升-phase3-terra.md` 启动 Task 3.1/3.2）

**REVIEW CHECKPOINT 1：作者审预注册包全件（矩阵、功效配置、六假设、协议），冻结后进入执行。**

---

## 本阶段风险

| 风险 | 触发点 | 处置 |
|---|---|---|
| 功效模拟判 KER 全集（12 核）不足 | Task 1.2 | 追加核清单交作者拍板；若拒绝追加 → H-DISC MID 上调并在 §6 披露欠功效 |
| 理论线 CHECKPOINT T2 延迟 | Task 1.3 | 1.1/1.2/1.4 先行完成待命；1.3 严禁提前冻结（假设推导来源未定稿即冻结=预注册失效） |
