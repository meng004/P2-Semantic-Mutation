# 论证提升-phase3-terra：外部线（EXP-EXT，准入重裁 → 盲化映射 → 冻结预测 → 执行揭盲）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `gpt-5.6-terra-max`（分派类别：**逻辑评审或审计**——64 例缺陷准入重裁逐案判断 + 盲化映射仲裁 + 冻结预测纪律核验，判断密度全计划最高；附带的跑臂/揭盲执行步骤一并完成）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（标识系统——结果编码 `REPRO_FAILED`/`PROTOCOL_AMBIGUOUS` 等）、§1.1（DEF-REAL/DEF-CAL 集合定义）、§1.2（链路总表——H-CAL/H-RANK 判据与 κ 门禁公式）、**§1.3.1（挖掘白名单 + 两段式统一标识 `EXT-<repo>-<序号>` → `bug-<算子代号>-<序号>`，本阶段核心纪律）**、§1.4（构建原则 P3/P5）。内容冲突以 master 为准。

**前置门禁（分段）:** Task 3.1/3.2 在 Phase 1 的 Task 1.4 协议单独冻结（hash 入库）后即可启动，不必等 Phase 1 全部完成；**Task 3.3（冻结预测）额外要求理论线 Phase T3（THM-WIN 草稿）完成**；Task 3.4 在 3.3 的冻结 commit 之后。

**并行性:** 与 Phase 2（grok）并行；工期 6–10 周（外部线是全计划关键路径）。

**交接物:** `data/external_slice/`（admission_sheet、FREEZE.sha256、predictions_frozen.json、runs/）+ SSOT 键 `external_fiber_map`、`external_validation` + H-CAL/H-RANK verdict → 供 Phase 4 写作。

---

## Task 3.1：重裁与就绪检查

- [ ] **Step 1:** 对 Defect4MR 64 候选按 Task 1.4 三条准入重裁，产出 `data/external_slice/admission_sheet.csv`（列：neutral_id=`EXT-<repo>-<序号>`、issue_url、buggy_sha、fixed_sha、三条判定、纳入/排除理由；analysis_id 列此阶段留空，Task 3.2 映射冻结后回填）；预期可纳入池 ≥25（verified_full 35 − 10 映射训练例=25 去掉 oracle 条件后基本全过 + candidate_full 16 部分过；训练例以 `MAPPING_TRAIN` 单列，F-1）
- [ ] **Step 2:** 就绪检查：逐案跑双臂构建+触发冒烟（复用 `reproducers/`），失败案标 `REPRO_FAILED` 保留不替换；目标就绪 n≥20、≥8 项目（其中入 \(\bar\tau\) 分析的项目需就绪缺陷 ≥3，计入补充挖掘目标），不足则按 master §1.3.1 白名单+检索信号词启动补充挖掘（准入判定同 Task 1.4 三条）
- [ ] **Step 3:** **切片冻结**：名单 SHA256 入 `data/external_slice/FREEZE.sha256`；Commit

## Task 3.2：盲化 fiber 映射

- [ ] **Step 1:** 发放标注包（缺陷描述+fix diff，无任何 MR/kill 信息；不含 DEF-CAL 训练 10 例，F-1）；两名人类标注者独立标注（或按 Task 1.4 预注册降级方案执行单人 test–retest）
- [ ] **Step 2:** 计算 κ（`analysis_hcal_hrank.py` 内置函数）；κ<0.6 → 协议修订一轮重标（预注册允许一次）；仍不达 → DIRECT 主分析降敏感性分析（降级路径生效）
- [ ] **Step 3:** 仲裁后映射表冻结入 SSOT `external_fiber_map`；按 master §1.3.1 赋分析别名 `bug-<算子代号>-<序号>`（ADJACENT → `bug-ADJ-`、OUT_OF_SCOPE → `bug-OOS-`）回填 admission_sheet 的 analysis_id 列——**此 commit 必须早于任何 kill 执行**；Commit

## Task 3.3：冻结预测（门禁：理论线 Phase T3 完成）

- [ ] **Step 1:** 确认外部 MR 实例化产物已按 Task 1.4 Step 2c 冻结（哈希在案，F-15）；按 fiber 对齐 + THM-WIN 窗口（可估处）生成每 (defect, MR set) detect/miss 预测与 MR 集排序预测；写 `data/external_slice/predictions_frozen.json`
- [ ] **Step 2:** `shasum -a 256 data/external_slice/predictions_frozen.json >> data/external_slice/FREEZE.sha256 && git commit`——此 commit 必须早于任何执行产物

## Task 3.4：执行与揭盲

- [ ] **Step 1:** 对就绪案逐一执行四组 MR（aligned/cross/v5/random floor）于 buggy/fixed 双臂；原始判定落 `data/external_slice/runs/`
- [ ] **Step 2:** 经典 MS 基线：cosmic-ray 跑对应模块得 kill-rate 排序（版本与 normaliser 与 EXP-STR 同钉扎，R-10）；Pattern Coverage 排序同步计算（描述性次级基线）
- [ ] **Step 3:** 跑 `analysis_hcal_hrank.py`：预测校准（主口径：aligned 条件每缺陷一对 accuracy vs 多数类，精确 McNemar；fixed 臂 FPR 单列，F-3）、项目等权 Kendall τ（SMS 排序 vs 真实检出排序；仅就绪缺陷 ≥3 的合格项目入 \(\bar\tau\)，报告合格项目数 J，不合格项目描述性单列）、\(\tau_{\mathrm{SMS}}-\tau_{\mathrm{MS}}\) 与 \(\tau_{\mathrm{SMS}}-\tau_{\mathrm{PC}}\) 描述性对比、OUT_OF_SCOPE 份额；全部入 SSOT `external_validation`
- [ ] **Step 4:** Commit

**REVIEW CHECKPOINT 3：外部线揭盲结果汇报；若 H-CAL/H-RANK 无信号，确认按预注册降级叙事（有界不一致 + THM-GAP 归因）执行写作。**

---

## 本阶段风险

| 风险 | 触发点 | 处置 |
|---|---|---|
| 就绪 n<20 | Task 3.1 | 启动补充挖掘（预算 2 周）；仍不足 → 按实际 n 报告并在 §6 披露；H-RANK 按冻结时裁定口径执行（阈值检验或区间估计），MID 不事后调整 |
| 揭盲后发现预测协议歧义 | Task 3.4 | 歧义案单列 `PROTOCOL_AMBIGUOUS` 不计入主分析，附敏感性分析含入版本 |
| 理论线 Phase T3 延迟阻塞 3.3 | Task 3.3 | 3.1/3.2 先行完成待命；严禁在 THM-WIN 草稿缺位时用临时规则出预测（预测协议完整性破坏） |
