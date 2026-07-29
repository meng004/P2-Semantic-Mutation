# 论证提升-phase1-fable：预注册包（适用矩阵 / 功效模拟 / 假设冻结 / 外部协议）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——预注册是方法学文本+统计设计的复合体；功效模拟代码由同一模型完成以保证与假设文本一致）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（符号与标识——假设一律用 H-ZERO/H-DISC/H-CONS/H-DOSE/H-CAL/H-RANK；secondary 族：H-XI/H-DOSE-CTR/H-FIX + H-CAL 聚簇，B 组）、§1.1（对象集合定义，语义命名 KER-*/POOL-*/MRSET-*/DEF-*）、§1.2（RQ→假设→对象→方法→指标 链路总表，判据公式所在）、§1.3（预处理规范与统一标识——Task 1.4 须内嵌其 §1.3.1 挖掘规范）、§1.4（对象构建原则 P1–P7，预注册文本须引用）。内容冲突以 master 为准。

**前置门禁:** Phase 0 完成（REVIEW CHECKPOINT 0 已过）。**分段门禁**：Task 1.1/1.2/1.4 可在理论线 CHECKPOINT T2 之前先行；**Task 1.3（假设与分析代码冻结）与冻结 tag 必须等理论线 CHECKPOINT T2（THM-GAP 内部评审）通过**。

**并行性:** 与理论线 T1–T5 并行；Task 1.4 协议单独冻结（hash 入库）后，Phase 3 的 Task 3.1/3.2 即可启动，不必等本阶段全部完成。

**交接物:** `research/prereg_v2/` 全件（适用矩阵、功效报告、假设全件=5 headline + 1 操纵检验 + secondary 族（B 组）、外部协议、AMENDMENTS.md 模板（F-7）、FREEZE_MANIFEST）+ `prereg-v2-freeze` tag → Phase 2/3 的执行依据。

---

## Task 1.1：适用矩阵冻结

**Files:** Create: `research/prereg_v2/applicability_matrix.md`

- [x] **Step 1:** 从算子设计文档与 v4 development 数据，对 5 算子 × 4 PUT 类逐格声明 applicable / inapplicable + 一句机理理由（例：SI 需要可注入结构位点，B 类采样核无 → inapplicable）
  - 注：SI×B 的计划示例被 v4 代码证据推翻——b3 的 2 个 SI 变异体（算术→几何均值，AM–GM 有序退化）证明位点存在；裁定=类 applicable、b1/b2 类内例外（见矩阵 §4 D2）。
- [x] **Step 2:** 声明规则：inapplicable 格不进 H-CONS 分母、不进 H-DISC 对比；预测零（COR-ZERO）与不适用零分别编码 `PRED_ZERO_ALIGN` / `NOT_APPLICABLE`
- [x] **Step 2b（F-5）:** PUT 级位点核查：类级裁定按"类内继承"广播后，逐 PUT 核验证算子所需代码位点存在性（60 格，每格一句判断；沿用两人独立+仲裁协议）；类内例外格改 `NOT_APPLICABLE` 并标注"类内例外"。**运行期重编码规则（F-5a）**：仅人工确认的位点结构性缺失可在揭盲前重编码 `NOT_APPLICABLE` 并记录；生成器工程性失败（位点在、工具败）一律留在漏斗计损耗，不得重编码（防 H-CONS 分母操纵）；揭盲后不得改
- [x] **Step 3:** 两人独立填写后合并分歧（记录分歧格与仲裁理由）；`shasum -a 256` 值写入文件头
  - Rater A=claude-fable-5（本会话）；Rater B=gpt-5.6-sol-xhigh 独立子代理（跨家族；terra-max 本环境不可用）；分歧 2 格 + 仲裁记录=矩阵 §4；n_app=51（敏感性 {39,45,51}）；作者在 CHECKPOINT 1 复核可翻转。
- [x] **Step 4:** Commit

## Task 1.2：功效模拟与 MID 锁定

**Files:** Create: `scripts/prereg/power_simulation.py`；Output: `research/prereg_v2/power_report.md`

- [x] **Step 1:** 从 v4 数据估计两部分分布参数：P(SMS>0|aligned)、P(SMS>0|cross)、非零部分的 Beta 拟合参数
  - 双锚点：A=PUT×class-primary-MP（0.500/0.1875 + Beta 拟合）；B=算子级 alignment-map（0.118/0.324，信号反转）——B 作为诚实证伪情景入模拟（报告 §1）。
- [x] **Step 2:** 模拟设计变量网格（cell=算子×PUT，master §0.3）：applicable cell 数 × 每 cell 变异体密度 {8,12,16,20} × MR 集数（v5 held-out 份数 {1,2}）；每格 2000 次模拟，输出 H-ZERO（McNemar）与 H-DISC（配对口径：Wilcoxon 符号秩 + \(r_{\mathrm{mp}}\)，MID 候选由 δ=0.33 换算）的功效；**强制产出预算算术表**：applicable cell 数 × 密度 = 变异体总量（预算区间约 300–840）× 单变异体生成/执行成本
  - H-DISC 锚点 A 全密度 ≥0.835（MID 0.33）；H-ZERO 需 m=16+s=2 在设计备择 S_U80 达 0.806；预算表=报告 §5（m=16 → 816 恰在 ≤840 内）。
- [x] **Step 2b:** 外部线可行性模拟（R-3）：……输出"阈值检验 or 区间估计"裁定建议
  - H-CAL 阈值检验全网格不可行（acc 0.8 最高 0.31；acc 0.9 最高 0.66）→ **建议降区间估计**（Wilson CI 宽度表在案）；H-RANK 保留 τ̄≥0.3 pass-line，新增 **合格项目 ≥6 门槛**（null 伪通过 4 项目 14% → ≥6 项目 ≤9%）。
- [x] **Step 2c（F-4）:** H-DOSE 功效模拟 + 中心估计精度 + H-CONS Wilson 解析预算
  - 全配置 per-curve 功效饱和（理论转变存在时）；中心估计 sd ≤0.22 ≪ 窗宽 → H-DOSE-CTR ≥6/8 判据检验"位置"而非"噪声"✓；H-CONS n=51 需 p̂≥0.65（dev 锚 0.667 边际通过，SI 为风险集中点）。
- [x] **Step 3:** 选定最小达 0.8 功效的配置写入 power_report
  - **主配置：n_app=51 × 密度 16 × 2 份 v5 held-out MR 集**；MID(r_mp)=0.33；**增核决策未触发**（含条件性候选清单交作者）；EXP-DOSE=6档×20重复×8曲线=960；EXP-FIX 抽 15 cells（bar=12/15）。
- [x] **Step 4:** Commit

## Task 1.3：假设与分析代码冻结（门禁：理论线 CHECKPOINT T2 已过）

**Files:** Create: `research/prereg_v2/hypotheses.md`、`scripts/prereg/analysis_hzero.py`、`analysis_hdisc.py`、`analysis_hcons.py`、`analysis_hdose.py`（含 H-DOSE-CTR，B-2）、`analysis_hcal_hrank.py`（含 B-3 聚簇 secondary 与 \(\bar\tau\) 配对差 CI）、`analysis_hxi.py`（B-1）、`analysis_hfix.py`（B-4）

> **门禁记录：** 理论 CHECKPOINT T2 于 2026-07-28 经作者确认通过（THM-GAP 草稿=理论分支 `7c48d06`+`7bb1519`）；本任务随即执行。

- [x] **Step 1:** hypotheses.md 定稿 **5 headline + 1 操纵检验**（R-11）：headline——H-ZERO balanced accuracy ≥0.75 + McNemar；H-DISC 配对主口径：within-cell（aligned−cross）Wilcoxon 符号秩 + \(r_{\mathrm{mp}}\) ≥ 模拟锁定 MID 且 CI 下界 >0，非配对条件 Cliff's δ 降敏感性（v4 可比）；H-DOSE isotonic vs 常数置换检验；H-CAL 主口径=aligned 条件每缺陷一对（n=就绪缺陷数），accuracy 优于多数类（精确二项 McNemar；不采 cluster bootstrap 作主口径，理由明文：n≈20–25 簇不稳，F-3）；fixed 臂 FPR 单列规则；Brier 删除（二值预测下冗余，F-3a）；H-RANK 项目等权 Kendall τ ≥ MID——项目准入：就绪缺陷 ≥3、并列处理与合格项目数 J 报告规则明文、若 Task 1.2 Step 2b 可行性模拟功效 <0.8 则本条冻结前降为区间估计报告——\(\bar\tau_{\mathrm{SMS}}-\bar\tau_{\mathrm{MS}}\) 配对差+bootstrap 95% CI 估计优先报告（不做优越性检验：J≈8 无功效，B-3）。操纵检验——H-CONS Wilson 下界 >0.5（EXP-CON 可行性门槛，不入 headline 主张）。每条注明推导来源定理（THM-GAP/THM-WIN/COR-ZERO）与降级路径；**检验族政策（F-11，两族版）**：五条 headline 为异质构念的 co-primary，各自 α=0.05 不作族校正（理由明文：无合取主张+强制全报告防选择性；H-CONS 操纵检验不入族）；**secondary confirmatory 族（B 组）**——H-XI（Step 1b）、H-DOSE-CTR（中心包含，候选 ≥6/8，Step 2c 校准后冻结前锁定；\(\Delta_r/\bar\eta\) 逐曲线估计协议引 THM-WIN 审计项 (5)，B-2）、H-CAL 四条件合并聚簇 bootstrap（缺陷为簇，B-3）、H-FIX（master Task 2.5，B-4）：各自 α=0.05、显式标注 secondary、失败如实报告、不 gate headline
- [x] **Step 1b:** A-PROV 桥接假设显式化（R-6）：hypotheses.md 开篇声明 provenance-as-coverage 操作化（\(\mathrm{Cov}(R)\) = 适用矩阵 × MR 出处；权威表述=理论计划 §0.3 A-PROV 条目）；**证据双通道（F-2）**：A-PROV 断言由 ex-ante 出处审计（对称清单、生成期 eff 标签、适用矩阵哈希）决定，与 kill 结果无关；ξ 为 ex-post 诊断随判别结果并报；**裁决规则**：H-ZERO/H-DISC verdict 无条件按冻结判据判定，ξ 不改变任何 verdict，只进讨论段归因；**H-XI（B-1，secondary confirmatory）**：pooled ξ ≤ 0.10（先验固定地标）+ bootstrap 95% CI + 可估性守卫（总 kill <50 → UNDERPOWERED 报区间）；**H-ZERO × H-XI 2×2 裁决表**四格结论句式预注册入 hypotheses.md（四格=双过同证 / ZERO 过 XI 败主张有界 / ZERO 败 XI 过诚实否证 / 双败操作化失败）
- [x] **Step 2:** 分析脚本按假设一比一实现，输入统一为 SSOT JSON 新键，输出统一 schema `{hypothesis, estimate, ci, p, verdict}`；对空输入跑通冒烟测试（合成数据）
  - 7 脚本 + `_stats.py` 共享冻结工具 + `smoke_all.py`；冒烟 **7/7 PASS**。
- [x] **Step 3:** 冻结机制：先创建 `research/prereg_v2/AMENDMENTS.md`（仅表头模板，字段：编号/日期/触发事件/影响范围/改动摘要+diff 哈希/§6 披露句/作者签署；**显式排除出 FREEZE_MANIFEST 哈希集**——该文件生来冻结后追加，完整性由逐条 amendment 单独 commit 的 git 历史保证，F-7a）；再 `git tag prereg-v2-freeze && shasum -a 256 $(ls research/prereg_v2/* | grep -v AMENDMENTS) scripts/prereg/*.py > research/prereg_v2/FREEZE_MANIFEST.sha256`（F-7）
  - 顺序按可审计性调整为：manifest 入 commit（`eaa400d`）→ tag 指向该 commit（tag 内含 manifest）。
- [x] **Step 4:** Commit（`6ad5388` 包内容 + `eaa400d` manifest/tag）

## Task 1.4：外部切片准入与映射协议

**Files:** Create: `research/prereg_v2/external_slice_protocol.md`

- [x] **Step 1:** 准入三条（且仅三条）：真实缺陷（公开 issue+fix commit）；双臂可复现（buggy/fixed 构建+触发）；in-scope（单/少输出数值核，签名可适配）。**明文排除** "MR 可判别"条件并注明这是对 D0 循环的修正（协议 §1）
- [x] **Step 1b:** 内嵌 master §1.3.1 挖掘规范：白名单定稿（GPy 排除、理由=低活跃 R-12，surrogate 覆盖交 GPyTorch）、信号词/排除类清单、判定模板、两段式标识 + git 时序不变量（协议 §2）
- [x] **Step 2:** fiber 映射协议：两名人类标注者 + 训练集抽取规则（seeded 简单随机，seed=20260728，抽取者≠标注者，F-1a）+ 8 类联合标签 κ≥0.6 门禁 + 一次重标 + 仲裁 + R-4 降级方案并列预注册（协议 §3）
- [x] **Step 2c（F-15）:** 外部模块 MR 实例化条款（执笔者隔离、时点先于预测冻结、哈希随 predictions_frozen 冻结、RND 冻结 seed 抽样；协议 §4）
- [x] **Step 3:** 冻结预测协议：detect/miss + SMS 排序预测、逐条 rationale 字段、`shasum -a 256` 存证、git 时序链、揭盲与 `PROTOCOL_AMBIGUOUS` 规则（协议 §5）
- [x] **Step 4:** Commit（协议单独冻结后即可通知 `论证提升-phase3-terra.md` 启动 Task 3.1/3.2）
  - 独立哈希已入库 `research/prereg_v2/external_slice_protocol.sha256`；Phase 3 Task 3.1/3.2 依计划解锁（执行模型=gpt-5.6-terra-max 类，另行调度）。

**REVIEW CHECKPOINT 1：作者审预注册包全件（矩阵、功效/可行性配置、假设全件=5 headline + 1 操纵检验 + secondary 族（B 组）、协议），冻结后进入执行。**

> **状态（2026-07-28，final）：** Task 1.1/1.2/1.3/1.4 全部完成。预审（作者委托）经干预式探针 UPHELD 两处仲裁并定位 H-ZERO 功效悬崖（`docs/review_20260728/prereg_prereview.md`）；理论 CHECKPOINT T2 经作者确认通过后，Task 1.3 假设全件冻结（冒烟 7/7），`FREEZE_MANIFEST.sha256` 入 commit `eaa400d`，tag **`prereg-v2-freeze`** 已打。**REVIEW CHECKPOINT 1 已就绪待作者裁决**——全件=矩阵（仲裁已探针背书）+ 功效报告 + 假设全件 + 外部协议 + 冻结清单。裁决通过后：Phase 2（grok 类）与 Phase 3（terra 类）依计划调度并行执行。

---

## 本阶段风险

| 风险 | 触发点 | 处置 |
|---|---|---|
| 功效模拟判 KER 全集（12 核）不足 | Task 1.2 | 追加核清单交作者拍板；若拒绝追加 → H-DISC MID 上调并在 §6 披露欠功效 |
| 理论线 CHECKPOINT T2 延迟 | Task 1.3 | 1.1/1.2/1.4 先行完成待命；1.3 严禁提前冻结（假设推导来源未定稿即冻结=预注册失效） |
