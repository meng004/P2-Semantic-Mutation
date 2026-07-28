# 论证提升-phase1-fable：预注册包（适用矩阵 / 功效模拟 / 假设冻结 / 外部协议）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——预注册是方法学文本+统计设计的复合体；功效模拟代码由同一模型完成以保证与假设文本一致）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（符号与标识——假设一律用 H-ZERO/H-DISC/H-CONS/H-DOSE/H-CAL/H-RANK）、§1.1（对象集合定义，语义命名 KER-*/POOL-*/MRSET-*/DEF-*）、§1.2（RQ→假设→对象→方法→指标 链路总表，判据公式所在）、§1.3（预处理规范与统一标识——Task 1.4 须内嵌其 §1.3.1 挖掘规范）、§1.4（对象构建原则 P1–P7，预注册文本须引用）。内容冲突以 master 为准。

**前置门禁:** Phase 0 完成（REVIEW CHECKPOINT 0 已过）。**分段门禁**：Task 1.1/1.2/1.4 可在理论线 CHECKPOINT T2 之前先行；**Task 1.3（假设与分析代码冻结）与冻结 tag 必须等理论线 CHECKPOINT T2（THM-GAP 内部评审）通过**。

**并行性:** 与理论线 T1–T5 并行；Task 1.4 协议单独冻结（hash 入库）后，Phase 3 的 Task 3.1/3.2 即可启动，不必等本阶段全部完成。

**交接物:** `research/prereg_v2/` 全件（适用矩阵、功效报告、六假设、外部协议、AMENDMENTS.md 模板（F-7）、FREEZE_MANIFEST）+ `prereg-v2-freeze` tag → Phase 2/3 的执行依据。

---

## Task 1.1：适用矩阵冻结

**Files:** Create: `research/prereg_v2/applicability_matrix.md`

- [ ] **Step 1:** 从算子设计文档与 v4 development 数据，对 5 算子 × 4 PUT 类逐格声明 applicable / inapplicable + 一句机理理由（例：SI 需要可注入结构位点，B 类采样核无 → inapplicable）
- [ ] **Step 2:** 声明规则：inapplicable 格不进 H-CONS 分母、不进 H-DISC 对比；预测零（COR-ZERO）与不适用零分别编码 `PRED_ZERO_ALIGN` / `NOT_APPLICABLE`
- [ ] **Step 2b（F-5）:** PUT 级位点核查：类级裁定按"类内继承"广播后，逐 PUT 核验证算子所需代码位点存在性（60 格，每格一句判断；沿用两人独立+仲裁协议）；类内例外格改 `NOT_APPLICABLE` 并标注"类内例外"。**运行期重编码规则（F-5a）**：仅人工确认的位点结构性缺失可在揭盲前重编码 `NOT_APPLICABLE` 并记录；生成器工程性失败（位点在、工具败）一律留在漏斗计损耗，不得重编码（防 H-CONS 分母操纵）；揭盲后不得改
- [ ] **Step 3:** 两人独立填写后合并分歧（记录分歧格与仲裁理由）；`shasum -a 256` 值写入文件头
- [ ] **Step 4:** Commit

## Task 1.2：功效模拟与 MID 锁定

**Files:** Create: `scripts/prereg/power_simulation.py`；Output: `research/prereg_v2/power_report.md`

- [ ] **Step 1:** 从 v4 数据估计两部分分布参数：P(SMS>0|aligned)、P(SMS>0|cross)、非零部分的 Beta 拟合参数
- [ ] **Step 2:** 模拟设计变量网格（cell=算子×PUT，master §0.3）：applicable cell 数 × 每 cell 变异体密度 {8,12,16,20} × MR 集数（v5 held-out 份数 {1,2}）；每格 2000 次模拟，输出 H-ZERO（McNemar）与 H-DISC（配对口径：Wilcoxon 符号秩 + \(r_{\mathrm{mp}}\)，MID 候选由 δ=0.33 换算）的功效；**强制产出预算算术表**：applicable cell 数 × 密度 = 变异体总量（预算区间约 300–840）× 单变异体生成/执行成本
- [ ] **Step 2b:** 外部线可行性模拟（R-3）：以 DEF-CAL 检出率为先验、以扣除 10 训练例后的计数为基线（F-1a），模拟就绪缺陷数 n∈{12,16,20,24} × 项目数 J∈{6,8,10} × 每项目缺陷分布下 H-CAL（主口径=aligned 条件每缺陷一对，精确二项 McNemar，F-3a）与 H-RANK（\(\bar\tau\ge0.3\)；显式模拟每项目 4 条件排序的 τ_b 与并列密度，F-4a）的功效；输出"阈值检验 or 区间估计"裁定建议
- [ ] **Step 2c（F-4）:** H-DOSE 功效模拟：生成模型=由 THM-WIN 窗宽 \(O(\Delta_r+2\bar\eta)\) 与噪声假设推导的 logistic 转变曲线（参数来源诚实标注为理论推导而非 v4 数据，斜率敏感性扫描）；配置空间受总执行数 ≤960 约束（6 档×20 重复×8 曲线=960 恰为上限，8 档配置须削重复数）；同时模拟转变中心估计精度（供 H-DOSE-CTR 判据锁定，B-2）；H-CONS 为操纵检验不入模拟，另报固定 \(n_{\mathrm{app}}\) 下的 Wilson CI 宽度预算（解析）
- [ ] **Step 3:** 选定最小达 0.8 功效的配置写入 power_report；若 KER 全集（12 核）配置全部 <0.8，触发"追加 4–8 个紧凑核"决策（追加=PUT 级增加 cell 数；列出候选核清单与选择标准，交作者拍板）；若外部线模拟显示 \(\bar\tau\) 阈值检验功效 <0.8，H-RANK 冻结前降为区间估计报告（Task 1.3 落实）
- [ ] **Step 4:** Commit

## Task 1.3：假设与分析代码冻结（门禁：理论线 CHECKPOINT T2 已过）

**Files:** Create: `research/prereg_v2/hypotheses.md`、`scripts/prereg/analysis_hzero.py`、`analysis_hdisc.py`、`analysis_hcons.py`、`analysis_hdose.py`、`analysis_hcal_hrank.py`

- [ ] **Step 1:** hypotheses.md 定稿 **5 headline + 1 操纵检验**（R-11）：headline——H-ZERO balanced accuracy ≥0.75 + McNemar；H-DISC 配对主口径：within-cell（aligned−cross）Wilcoxon 符号秩 + \(r_{\mathrm{mp}}\) ≥ 模拟锁定 MID 且 CI 下界 >0，非配对条件 Cliff's δ 降敏感性（v4 可比）；H-DOSE isotonic vs 常数置换检验；H-CAL 主口径=aligned 条件每缺陷一对（n=就绪缺陷数），accuracy 优于多数类（精确二项 McNemar；不采 cluster bootstrap 作主口径，理由明文：n≈20–25 簇不稳，F-3）；fixed 臂 FPR 单列规则；Brier 删除（二值预测下冗余，F-3a）；H-RANK 项目等权 Kendall τ ≥ MID——项目准入：就绪缺陷 ≥3、并列处理与合格项目数 J 报告规则明文、若 Task 1.2 Step 2b 可行性模拟功效 <0.8 则本条冻结前降为区间估计报告——\(\tau_{\mathrm{SMS}}-\tau_{\mathrm{MS}}\) 描述性。操纵检验——H-CONS Wilson 下界 >0.5（EXP-CON 可行性门槛，不入 headline 主张）。每条注明推导来源定理（THM-GAP/THM-WIN/COR-ZERO）与降级路径；**检验族政策（F-11）**：五条 headline 为异质构念的 co-primary，各自 α=0.05 不作族校正（理由明文：无合取主张+强制全报告防选择性；H-CONS 操纵检验不入族）
- [ ] **Step 1b:** A-PROV 桥接假设显式化（R-6）：hypotheses.md 开篇声明 provenance-as-coverage 操作化（\(\mathrm{Cov}(R)\) = 适用矩阵 × MR 出处；权威表述=理论计划 §0.3 A-PROV 条目）；**证据双通道（F-2）**：A-PROV 断言由 ex-ante 出处审计（对称清单、生成期 eff 标签、适用矩阵哈希）决定，与 kill 结果无关；ξ 为 ex-post 诊断随判别结果并报；**裁决规则**：H-ZERO/H-DISC verdict 无条件按冻结判据判定，ξ 不改变任何 verdict，只进讨论段归因
- [ ] **Step 2:** 分析脚本按假设一比一实现，输入统一为 SSOT JSON 新键，输出统一 schema `{hypothesis, estimate, ci, p, verdict}`；对空输入跑通冒烟测试（合成数据）
- [ ] **Step 3:** 冻结机制：先创建 `research/prereg_v2/AMENDMENTS.md`（仅表头模板，字段：编号/日期/触发事件/影响范围/改动摘要+diff 哈希/§6 披露句/作者签署；**显式排除出 FREEZE_MANIFEST 哈希集**——该文件生来冻结后追加，完整性由逐条 amendment 单独 commit 的 git 历史保证，F-7a）；再 `git tag prereg-v2-freeze && shasum -a 256 $(ls research/prereg_v2/* | grep -v AMENDMENTS) scripts/prereg/*.py > research/prereg_v2/FREEZE_MANIFEST.sha256`（F-7）
- [ ] **Step 4:** Commit

## Task 1.4：外部切片准入与映射协议

**Files:** Create: `research/prereg_v2/external_slice_protocol.md`

- [ ] **Step 1:** 准入三条（且仅三条）：真实缺陷（公开 issue+fix commit）；双臂可复现（buggy/fixed 构建+触发）；in-scope（单/少输出数值核，签名可适配）。**明文排除** "MR 可判别"条件并注明这是对 D0 循环的修正
- [ ] **Step 1b:** 内嵌 master §1.3.1 挖掘规范：仓库白名单定稿（Defect4MR 覆盖项目 + numpy/scipy/scikit-learn/statsmodels/PyMC/GPy/GPyTorch/chaospy/SALib/PyTorch/JAX 数值组件候选池取舍；GPy 低活跃预期管理见 master §1.3.1，R-12）、issue 检索信号词与排除类清单、语义符合性判定模板（issue URL + buggy SHA + fixed SHA + 一句机理）、两段式统一标识规则（准入期 `EXT-<repo>-<序号>`，映射冻结后 `bug-<算子代号>-<序号>`；准入期禁止出现算子归类）
- [ ] **Step 2:** fiber 映射协议：**两名人类标注者**（身份类别写入协议；均不接触 MR 生成与 kill 执行；LLM 仅可作标注辅助工具，须声明且不计入 κ）、训练集=DEF-CAL 训练子集 10 例（抽取规则预注册：seeded 简单随机或按 repo 分层、禁以 fiber 标签为分层变量、抽取者不得担任标注者，F-1a；10 例以 `MAPPING_TRAIN` 从确认性 DEF-REAL 扣除）、标签集 {DIRECT, ADJACENT, OUT_OF_SCOPE, UNCERTAIN}、盲化规定（不见 kill 结果、不见对方标注）、κ≥0.6 门禁、分歧仲裁程序；**降级方案并列预注册（R-4）**：第二人类标注者不可得 → 单人类标注者 + 时间分隔（≥2 周）test–retest 自一致性 + 全部标注材料公开 + §6 披露
- [ ] **Step 2c（F-15）:** 外部模块 MR 实例化条款：对每个就绪缺陷模块，aligned/cross MR 由各 fiber 的模式按 provenance 实例化为该模块签名可执行版本；执笔者不接触任何 kill 结果；完成时点在 Task 3.3 冻结预测之前；实例化产物（MR 文本+适配代码）`shasum -a 256` 随 predictions_frozen 一并冻结；random floor 按冻结 seed 从预注册 MR 池抽样适配
- [ ] **Step 3:** 冻结预测协议：执行前对每 (defect, MR set) 产出 detect/miss 预测 + 每 MR 集 SMS 排序预测，`shasum -a 256` 存证；揭盲规则
- [ ] **Step 4:** Commit（协议单独冻结后即可通知 `论证提升-phase3-terra.md` 启动 Task 3.1/3.2）

**REVIEW CHECKPOINT 1：作者审预注册包全件（矩阵、功效配置、六假设、协议），冻结后进入执行。**

---

## 本阶段风险

| 风险 | 触发点 | 处置 |
|---|---|---|
| 功效模拟判 KER 全集（12 核）不足 | Task 1.2 | 追加核清单交作者拍板；若拒绝追加 → H-DISC MID 上调并在 §6 披露欠功效 |
| 理论线 CHECKPOINT T2 延迟 | Task 1.3 | 1.1/1.2/1.4 先行完成待命；1.3 严禁提前冻结（假设推导来源未定稿即冻结=预注册失效） |
