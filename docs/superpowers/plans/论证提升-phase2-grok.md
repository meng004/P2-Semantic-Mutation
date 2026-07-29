# 论证提升-phase2-grok：构念线（EXP-CON / EXP-DIS / EXP-DOSE / EXP-STR）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `cursor-grok-4.5-high-fast`（分派类别：**执行**——生成/跑批/分析脚本执行量大，速度优先；全部判据与分析代码已在 Phase 1 冻结，本阶段不做统计设计决策）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（标识系统）、§1.1（对象集合定义与说明——KER-*/POOL-* 语义命名）、§1.2（链路总表=判据公式）、§1.3（预处理规范——变异体统一标识 `mut-<算子>-<PUT>-<序号>` 与剂量档位标定）、§1.5（方法卡片）。内容冲突以 master 为准。**纪律：预注册冻结后分析代码不得改动，改动即降级 exploratory 并披露。**

**前置门禁:** Phase 1 完成（`prereg-v2-freeze` tag 存在，REVIEW CHECKPOINT 1 已过）。

**并行性:** 与 Phase 3（terra）并行；工期 4–6 周。Task 2.3 的对象清单受理论线 Phase T3 输出（\(L_r\) 不可估 PUT 清单）联动约束。

**交接物:** SSOT 新键 `funnel_v5`、`dose_response_v5`、`fix_intervention_v5`（B-4）、`syntactic_overlap_v2` + headline verdict（H-CONS/H-ZERO/H-DISC/H-DOSE）与 secondary verdict（H-XI/H-DOSE-CTR/H-FIX，B 组）→ 供 Phase 4 写作模板注入。

---

## Task 2.1：新变异体生成（v5 lineage，EXP-CON）

> **状态：BLOCKED（环境无 LLM API 密钥）。** 管线已备好一键可跑：`scripts/v5/generate_v5_mutants.py`（fail-fast 列出所需 env：`BLTCY_API_KEY`/`BLTCY_BASE_URL`）；台账/漏斗模板已预填（prompt SHA-256=`06fa552d…`）。密钥注入后按 Step 1–3 执行。**严禁伪造 LLM 输出。**

- [ ] **Step 1:** 按 Task 1.2 锁定配置在 applicable cell 生成新变异体（生成器版本、seed、prompt 哈希入台账 `data/v5/GENERATION_LEDGER.md`）；逐个赋统一标识 `mut-<算子>-<PUT>-<序号>`（master §1.3.2）
- [ ] **Step 2:** 全漏斗插桩：parse/build/trigger/E1∧E2/证书 各级损耗计数落 SSOT 新键 `funnel_v5`
- [ ] **Step 3:** 跑 `analysis_hcons.py`，verdict 入 SSOT；Commit

## Task 2.2：held-out MR source（v5-MR，EXP-DIS）

> **状态：BLOCKED（同 2.1）。** 候选 provider 排序（排除 v4 的 Claude/GPT/DeepSeek）：Gemini > Qwen > Mistral > Llama-hosted；对称清单模板已预填 v4 侧参数（`data/v5/MR_SOURCE_SYMMETRY.md`）。

- [ ] **Step 1:** 选定未用过的 provider（候选按对称协议可满足性排序），逐项核对对称清单：prompt=v4 同文、parser 同版、候选数/修复次数/预算/温度同值；清单存 `data/v5/MR_SOURCE_SYMMETRY.md`
- [ ] **Step 2:** 生成 aligned/cross MR 集 → prescreen → kill 矩阵
- [ ] **Step 3:** 跑 `analysis_hzero.py`（零预测：THM-GAP/COR-ZERO 预测标签 vs 观测零/非零）、`analysis_hdisc.py`（条件判别，配对主口径：within-cell Wilcoxon + \(r_{\mathrm{mp}}\)，非配对 δ 作敏感性）与 `analysis_hxi.py`（pooled ξ vs 0.10 地标 + 2×2 裁决表格位，B-1）；verdict 入 SSOT；Commit

## Task 2.3：剂量反应实验（EXP-DOSE，H-DOSE）

- [x] **Step 1:** 参数化算子实现 + F-10 双轴标定 + **窗口冻结**（`data/dose/WINDOWS_FROZEN.json`，commit `f7ca7cc`，先于任何剂量产物；随后 Amendment #2（`9b9939b`）以仪器分辨率下限修复 6/8 确定性核的退化窗，均在执行前）
- [x] **Step 2:** 960/960 执行（0 错误，56s），曲线数据落 `data/dose/dose_response_v5.json`（commit `2378065`）
- [x] **Step 3:** 冻结脚本裁决：**H-DOSE PASS**（全局置换 p=9.999e-5，由 CE-B3/CE-C1 干净转变驱动）；**H-DOSE-CTR FAIL（2/8，判据 ≥6/8）**——诚实落账；归因：CE-D3 硬界提前触发（转变在网格左侧）、CE-A1 与全部 HP 曲线的 aligned 检查器弱/近空（kill 通道不动而实现轴单调上升）→ A-PROV 操作化失配 + REM-FPOS 叙事素材，留 CHECKPOINT 2 汇报

## Task 2.4：语法基线扩充（EXP-STR）

- [x] **Step 1:** v4 池 AST 归一化重叠审计：15/292=5.14%，HP/SI/TF 零重叠（lineage=已提交审计 JSON；会话 sqlite 不在仓库，未咨询）；**v5 增补审计待 POOL-SEM v5 落地后重跑**（完整性注记，非阻塞）
- [x] **Step 2:** 构造性论证文档 `docs/review_20260728/syntactic_reach.md`（cosmic-ray + mutmut 算子族 → 一阶 AST 局部编辑类；HOM 不作反驳声明）
- [x] **Step 3:** `data/results/syntactic_overlap_v2.json` 入库（commit `f7ca7cc`）

## Task 2.5：add-one 修复干预（EXP-FIX，H-FIX，B-4）

> **状态：BLOCKED（依赖 Task 2.1/2.2 的 POOL-SEM v5 与 MRSET-ALN）。**

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
