# 论证提升-phase2-grok：构念线（EXP-CON / EXP-DIS / EXP-DOSE / EXP-STR）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `cursor-grok-4.5-high-fast`（分派类别：**执行**——生成/跑批/分析脚本执行量大，速度优先；全部判据与分析代码已在 Phase 1 冻结，本阶段不做统计设计决策）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（标识系统）、§1.1（对象集合定义与说明——KER-*/POOL-* 语义命名）、§1.2（链路总表=判据公式）、§1.3（预处理规范——变异体统一标识 `mut-<算子>-<PUT>-<序号>` 与剂量档位标定）、§1.5（方法卡片）。内容冲突以 master 为准。**纪律：预注册冻结后分析代码不得改动，改动即降级 exploratory 并披露。**

**前置门禁:** Phase 1 完成（`prereg-v2-freeze` tag 存在，REVIEW CHECKPOINT 1 已过）。

**并行性:** 与 Phase 3（terra）并行；工期 4–6 周。Task 2.3 的对象清单受理论线 Phase T3 输出（\(L_r\) 不可估 PUT 清单）联动约束。

**交接物:** SSOT 新键 `funnel_v5`、`dose_response_v5`、`fix_intervention_v5`（B-4）、`syntactic_overlap_v2` + headline verdict（H-CONS/H-ZERO/H-DISC/H-DOSE）与 secondary verdict（H-XI/H-DOSE-CTR/H-FIX，B 组）→ 供 Phase 4 写作模板注入。

---

## Task 2.1：新变异体生成（v5 lineage，EXP-CON）

- [ ] **Step 1:** 按 Task 1.2 锁定配置在 applicable cell 生成新变异体（生成器版本、seed、prompt 哈希入台账 `data/v5/GENERATION_LEDGER.md`）；逐个赋统一标识 `mut-<算子>-<PUT>-<序号>`（master §1.3.2）
- [ ] **Step 2:** 全漏斗插桩：parse/build/trigger/E1∧E2/证书 各级损耗计数落 SSOT 新键 `funnel_v5`
- [ ] **Step 3:** 跑 `analysis_hcons.py`，verdict 入 SSOT；Commit

## Task 2.2：held-out MR source（v5-MR，EXP-DIS）

- [ ] **Step 1:** 选定未用过的 provider（候选按对称协议可满足性排序），逐项核对对称清单：prompt=v4 同文、parser 同版、候选数/修复次数/预算/温度同值；清单存 `data/v5/MR_SOURCE_SYMMETRY.md`
- [ ] **Step 2:** 生成 aligned/cross MR 集 → prescreen → kill 矩阵
- [ ] **Step 3:** 跑 `analysis_hzero.py`（零预测：THM-GAP/COR-ZERO 预测标签 vs 观测零/非零）、`analysis_hdisc.py`（条件判别，配对主口径：within-cell Wilcoxon + \(r_{\mathrm{mp}}\)，非配对 δ 作敏感性）与 `analysis_hxi.py`（pooled ξ vs 0.10 地标 + 2×2 裁决表格位，B-1）；verdict 入 SSOT；Commit

## Task 2.3：剂量反应实验（EXP-DOSE，H-DOSE）

- [ ] **Step 1:** 参数化算子实现：HP（超参幅度）与 CE（守恒侵蚀强度）各设 ≥6 档幅度网格，每档名义+实测实现 \(\varepsilon_m\) 两轴标定入台账（master §1.3.3，F-10：实现轴用直接不变量违反泛函，不经 MR 检查器）；对象=每类一核（Lorenz、MC 积分、GPR、LogReg，数据键 A1/B3/C1/D3；若理论线 Phase T3 判某核的 Lipschitz 常数 \(L_r\) 不可估则按其清单替换）
- [ ] **Step 2:** 每档 × 按 power_report 锁定的重复数（≤960 总执行上限，F-4）执行 kill 判定（个体标识 `mut-<算子>-<PUT>-e<档位>-r<重复>`），曲线数据落 SSOT `dose_response_v5`
- [ ] **Step 3:** 跑 `analysis_hdose.py`（isotonic vs 常数，置换 p；Page's L）；同时判定 **H-DOSE-CTR（B-2）**：转变中心是否落于 \(\varepsilon_{\mathrm{tol}}\pm(\Delta_r+2\bar\eta)\)（逐曲线，横轴=实测实现 \(\varepsilon_m\)；判据=冻结锁定值，候选 ≥6/8）；Commit

## Task 2.4：语法基线扩充（EXP-STR）

- [ ] **Step 1:** cosmic-ray 既有 1,250 一阶变异体与 v4+v5 语义变异体（POOL-SEM）做 AST 归一化精确重叠审计（复用现有审计脚本，`rg -l "ast" scripts/ | head` 定位；引擎版本钉扎入台账，R-10）
- [ ] **Step 2:** 构造性论证文档（R-10，替代第二引擎运行）：整理 cosmic-ray 与 mutmut 公开算子清单，逐族映射到"一阶 AST 局部编辑"类，论证语法引擎可达集边界；材料入 `docs/review_20260728/syntactic_reach.md`
- [ ] **Step 3:** 重叠表 + 论证文档索引入 SSOT `syntactic_overlap_v2`；Commit

## Task 2.5：add-one 修复干预（EXP-FIX，H-FIX，B-4）

- [ ] **Step 1:** 按预注册抽样规则（冻结 seed）从预测非零对比集中抽 10–15 个 Gap_aln>0 的 cell；对每 cell 构造增广集 \(R^+\) = cross ∪ {一条目标层 aligned MR（取自已生成 MRSET-ALN，不新生成）}
- [ ] **Step 2:** 复用 POOL-SEM 既有变异体补跑 \(R^+\) kill 判定（仅增量执行）；结果落 SSOT 新键 `fix_intervention_v5`
- [ ] **Step 3:** 跑 `analysis_hfix.py`（SMS_j 0→正比例 + Wilson 95% CI；\(\mathrm{Gap}_{\mathrm{aln}}\) 转移账目表）；verdict 入 SSOT；Commit

**REVIEW CHECKPOINT 2：构念线结果 verdict 汇报——headline（H-CONS/H-ZERO/H-DISC/H-DOSE）+ secondary（H-XI/H-DOSE-CTR/H-FIX），含任何降级触发。**

---

## 本阶段风险

| 风险 | 触发点 | 处置 |
|---|---|---|
| v5 provider 不满足对称清单 | Task 2.2 | 换第二候选；全部不满足 → 判别线降 development 复现，H-DISC 降 exploratory |
| 任一确认性假设失败 | 各 Task Step 3 | 按 hypotheses.md 预注册降级路径执行，不改阈值、不删数据 |
| 分析脚本运行报缺陷需改代码 | 任意 | 修 bug 须同步在 `research/prereg_v2/AMENDMENTS.md` 记 amendment（哈希+理由，F-7），对应假设标注 exploratory 风险并在 CHECKPOINT 2 汇报 |
