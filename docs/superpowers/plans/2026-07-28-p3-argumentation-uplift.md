# P3 论证提升执行计划（SSOT → 预注册 → 构念线 → 外部线 → 重构写作）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans。任务用 checkbox 跟踪；每个 REVIEW CHECKPOINT 必须停下等作者拍板。

**Goal:** 解决构念效度证据为负与外部效度断链两大问题：以理论派生假设 + 两部分口径重建判别效度，以准入解耦切片重建真实缺陷外部锚，并完成合并稿重构与投稿前流水线。

**Architecture:** 五阶段串行门禁（Phase 0 SSOT → 1 预注册 → 2 构念线 ∥ 3 外部线 → 4 写作 → 5 流水线）；Phase 1 以理论增强计划的 REVIEW CHECKPOINT T2（THM-GAP 内部评审通过）为前置。

**上游输入:** `research/p3-tosem-v2.0-writing-plan.md`（指标/对象/baseline 定义）、`docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`（符号系统 §0 与定理群）、`research/fable-p3-p12-new-argumentation-plan.md` §3.4（SSOT 冲突记录）。

**证据纪律:** 旧 60-cell 数据 development-only；确认性结论仅出自新 lineage 数据；预注册冻结后分析代码不得改动（改动即降级为 exploratory 并披露）。

**执行分派（按模型拆分）:** 本计划为规格权威（§0 符号与标识、§1 实验规格总表、任务定义源）；逐阶段执行在下列拆分文件中进行（checkbox 在拆分文件中打勾），内容冲突以本计划为准，修订先改本计划再同步拆分文件。

**分派原则（三类，两计划共用）:** ① **最强推理**（证明起草、方法学/统计设计、手稿写作）→ `claude-fable-5-thinking-max`；② **逻辑评审或审计**（符号审计、独立交叉检验、整合核对、准入重裁）→ `gpt-5.6-terra-max`（跨家族独立视角，审计者与被审产出不同源）；③ **执行**（跑批、脚本、管线、构建打包）→ `cursor-grok-4.5-high-fast`。同类阶段可由同一模型的多个实例并行执行。

| Phase | 拆分文件 | 模型（类别） | 前置 | 可并行于 |
|---|---|---|---|---|
| 0 SSOT | `论证提升-phase0-grok.md` | cursor-grok-4.5-high-fast（执行） | — | 理论 T0 |
| 1 预注册 | `论证提升-phase1-fable.md` | claude-fable-5-thinking-max（推理） | Phase 0；Task 1.3 另需理论 CHECKPOINT T2 | 理论 T1–T5（Task 1.1/1.2/1.4 先行） |
| 2 构念线 | `论证提升-phase2-grok.md` | cursor-grok-4.5-high-fast（执行） | Phase 1（prereg tag） | Phase 3；理论 T6 审计窗口 |
| 3 外部线 | `论证提升-phase3-terra.md` | gpt-5.6-terra-max（审计） | Task 1.4 冻结（3.1/3.2）；理论 Phase T3（3.3） | Phase 2 |
| 4 写作 | `论证提升-phase4-fable.md` | claude-fable-5-thinking-max（推理） | CHECKPOINT 2 + Task 3.3；理论 T6.1 整合 | Phase 3 尾部 |
| 5 流水线 | `论证提升-phase5-grok.md` | cursor-grok-4.5-high-fast（执行） | Phase 4（CHECKPOINT 4） | —（终末串行） |

---

## 0. 符号与标识系统（第 0 节为符号说明；数学符号唯一权威=理论计划 §0.2 总表）

### 0.1 数学符号（引用 SSOT，不另立）

本计划不新造数学符号；使用的全部数学符号以**理论增强计划 §0.2 符号总表**（35 项闭集）与 §0.3 定义清单（DEF-01–14）为唯一权威。本计划高频使用其中：\(\mathrm{SMS}_{\mathrm{strict}}/\mathrm{SMS}_{\mathrm{cons}}\)（#19）、\(n,k,u,u_{\mathrm{neq}}\)（#18）、\(\mathrm{Cov}(R)\)（#21）、\(\mathrm{Gap}_{\mathrm{aln}}(R)/\mathrm{Gap}_{\mathrm{str}}(R)\)（#22）、\(\xi(R)\)（#23）、\(\varepsilon_{\mathrm{tol}}\)（#13）、\(\varepsilon_m\)（#25）、\(\Delta_r\)（#26）、\(\mathrm{eff}\)（#16）、\(\Psi\)（#15）、\(M_j,w_j\)（#17/#20）。确需新增符号 → 先入理论计划 §0.2 总表（补序号与冲突检查）再使用。

### 0.2 统计符号补充表（仅实证章节使用）

| # | 符号 | 含义 | 备注 |
|---|---|---|---|
| S1 | Cliff's δ | 有序效应量 | 与四柱 \(\mathrm{StatValid}_{\alpha,\delta}\) 的漏检率 δ 无关；正文首现加 "(ordinal effect size)" |
| S2 | Cohen's κ | 标注者一致性 | 与四柱 T4 最小完备基数 \(\kappa(\Gamma,\mathcal R)\) 无关；正文首现加 "(inter-rater agreement)" |
| S3 | Kendall τ（变体 \(\tau_{\mathrm{SMS}},\tau_{\mathrm{MS}},\tau_{\mathrm{PC}}\)） | 秩相关（下标=排序来源） | 与 v3.1 误差预算 τ 无关；正文首现加 "(rank correlation)" |
| S4 | p、CI、TPR、TNR | 常规统计量 | — |
| S5 | Brier | 概率预测校准分数 | \(\mathrm{Brier}=\mathrm{mean}(\mathrm{pred}-\mathrm{outcome})^2\) |
| S6 | MID | 最小重要差异 | 预注册冻结值 |

**语境隔离规则**：理论章节禁用 δ、κ、τ 三个字母命名任何新对象（对应理论计划 §0.4 消解表）；统计符号仅出现在实证章节且首现带限定词。

### 0.3 标识（ID）系统（非数学符号的编号规约）

- **RQ**：RQ1 形式保证 / RQ2 双向对应 / RQ3 可构造性 / RQ4 判别效度 / RQ5 外部锚（v2.0 设计稿 §3 冻结口径）；RQ-S 结构定位审计（描述性，不设判据）。
- **假设**（`H-<语义缩写>`）：H-ZERO 零预测、H-DISC 条件判别、H-CONS 可构造性、H-DOSE 剂量反应、H-CAL 外部校准、H-RANK 排序一致。旧标签映射：H-B1→H-ZERO、H-B2→H-DISC、H-C1→H-CONS、H-C2→H-DOSE、H-X1→H-CAL、H-X2→H-RANK。现稿旧 H1–H4 仅在 Prior Audit 小节以历史标签出现。
- **实验**（`EXP-<语义缩写>`）：EXP-CON 构造审计（旧 E2）、EXP-DIS 两部分判别（旧 E3）、EXP-DOSE 剂量反应（旧 E3c）、EXP-EXT 外部盲测（旧 E4）、EXP-STR 结构定位审计（旧 RQ-S 审计）。**判等程序 E1∧E2（现稿 §2.3）保留原名**；实验全部改用 `EXP-` 前缀后，两个标签空间不再撞名。RQ1 的载体是理论计划 Task T6.2（独立形式审计），不占本计划实验编号。
- **结果编码**（字符串枚举，全大写下划线）：`PRED_ZERO_ALIGN` / `NOT_APPLICABLE` / `REPRO_FAILED` / `PROTOCOL_AMBIGUOUS`。
- **对象集合代号**（语义命名，禁数字前缀）：KER-NUM / KER-STAT / KER-SCIML / KER-MLC（四类程序核集）、POOL-SEM / POOL-DOSE / POOL-SYN（变异体池）、MRSET-ALN / MRSET-CRS / MRSET-RND（MR 条件集）、DEF-REAL / DEF-CAL（缺陷集）；定义与说明见 §1.1。
- **对象统一标识**（个体级，定义见 §1.3）：缺陷两段式 `EXT-<repo>-<序号>`（准入期中性 ID）→ `bug-<算子代号>-<序号>`（盲化映射冻结后的分析别名，ADJACENT/OUT_OF_SCOPE 记 `bug-ADJ-`/`bug-OOS-`）；语义变异体 `mut-<算子>-<PUT>-<序号>`；剂量变异体 `mut-<算子>-<PUT>-e<档位>-r<重复>`。
- **PUT 类标签**：A（动力学/数值）、B（统计随机）、C（代理建模）、D（ML 分类）及编号（A1 Lorenz…）为既有数据资产命名（台账与数据键沿用，改名会断 lineage），不作数学符号使用；对外叙述一律用 §1.1 的语义集合名（KER-*），类字母仅存于数据键与个体 ID。
- **定理引用**：一律用理论计划 §0.5 的语义标签（THM-INT/THM-GAP/THM-WIN/PROP-IDF/COR-ZERO 等）。

---

## 1. 实验规格总表（自包含，执行者不需回读上游文档）

### 1.1 实验对象集合定义与说明（语义命名；集合以程序特征命名，不用数字前缀）

| 集合（代号） | 成员 | 代码规模 | 来源 / 仓库 / 参考 | 预处理 | 服务实验 |
|---|---|---|---|---|---|
| 数值动力学核集（KER-NUM） | Lorenz-63 显式积分器；LU 分解；一维热传导显式 FDM | 每核 `float→float`、<2KB（约 40–120 LOC） | 本仓库 12-PUT 基础设施（与 P2 共用；执行时 `rg --files` 定位路径并在台账固化 SHA256） | 无内容预处理（§1.3.6 资产盘点） | EXP-CON/DIS/DOSE/STR |
| 统计随机核集（KER-STAT） | Beta-Binomial 共轭后验；Metropolis–Hastings 采样器；蒙特卡洛积分 | 同上 | 同上 | 同上 | 同上 |
| SciML 代理核集（KER-SCIML） | 高斯过程回归（GPR）；多项式混沌展开（PCE）；浅层 NN 代理 | 同上 | 同上 | 同上 | 同上 |
| 分类学习核集（KER-MLC） | MLP；SVM；逻辑回归 | 同上 | 同上 | 同上 | 同上 |
| 追加紧凑核（条件触发） | 与上四类同签名同体量的候选核 | 同上约束 | Task 1.2 功效模拟触发的候选清单，作者拍板 | 同 KER 各集 | 功效补充 |
| 语义变异体池（POOL-SEM，v5 lineage） | 5 语义算子在 applicable cell 内对 KER 全集生成的变异体 | 密度 ≥20/cell，预计 200–400 个 | 本计划 Task 2.1 生成（generator 版本/seed/prompt 哈希入台账） | 生成漏斗+三态归档+统一标识（§1.3.2） | EXP-CON/DIS 确认性分母 |
| 剂量梯度池（POOL-DOSE） | HP（超参幅度）、CE（守恒侵蚀）两参数化算子 × 每类一核（Lorenz、MC 积分、GPR、LogReg）× ≥6 档 × 20 重复 | ≥960 次执行 | 本计划 Task 2.3 实现 | 档位 \(\varepsilon_m\) 标定+统一标识（§1.3.3） | EXP-DOSE |
| MR 条件集（MRSET-ALN / MRSET-CRS / MRSET-RND） | aligned / cross / seeded-random 三组 | 每 cell 3 条件 | v4=development；v5 held-out provider=确认性 | 对称清单核对+prescreen（§1.3.4） | EXP-DIS/EXT 处理与对照 |
| 真实缺陷对集（DEF-REAL） | 数值语义缺陷的 buggy/fixed 程序对 | 就绪 n≥20、项目 ≥8 | Defect4MR 64 池（P12 仓库 `/Users/limeng/Papers/P12-Defect4MR`）重裁 + 主流权威仓库补充挖掘（白名单见 §1.3.1） | **issue 挖掘+双臂复现+两段式统一标识（§1.3.1，核心预处理）** | EXP-EXT validation |
| 校准缺陷集（DEF-CAL） | verified_full 35 例（选择条件披露） | 35 | P12 Defect4MR `verified_full` | 无新预处理；仅 fiber 映射训练 | EXP-EXT development/校准 only |
| 语法变异体参照池（POOL-SYN） | cosmic-ray 一阶变异体（1,250，既有）+ mutmut 默认算子集（新跑） | 双引擎全量 | cosmic-ray / mutmut 官方默认配置（版本号入台账） | AST 归一化（§1.3.5） | EXP-STR 参照 + MS 排序基线 |

### 1.2 RQ → 假设 → 对象集合 → 实验方法 → 评价指标 链路总表（判据冻结于 prereg）

| RQ | 假设 | 对象集合 | 实验方法 | 评价指标（计算公式） | 判据 | 支撑论点 |
|---|---|---|---|---|---|---|
| RQ1 形式保证 | —（无实证假设） | 不占实证对象；区间演示用 KER 全集 v4 数据（development） | 理论计划 Task T6.2 独立形式审计 + THM-INT 区间演示 | 审计清单 8 项通过数；区间宽度 \(\mathrm{SMS}_{\mathrm{strict}}\cdot u/(n+u)\)（描述性，随证书预算收窄曲线） | 审计 8/8 ✓ | SMS 给出健全区间、单调收窄与可归因缺口 |
| RQ2 双向对应 | H-DOSE | POOL-DOSE ×（KER-NUM/STAT/SCIML/MLC 每类一核） | EXP-DOSE 单因子剂量梯度（≥6 档 × 20 重复，档内独立 seed） | isotonic 回归 vs 常数模型：\(T=\mathrm{RSS}_{\mathrm{const}}-\mathrm{RSS}_{\mathrm{iso}}\)，置换检验 p（10⁴ 次）；辅 Page's L；转变中心与 \(\varepsilon_{\mathrm{tol}}\) 偏差 | p<0.05；偏差仅报告（模型检验，无通过线） | kill 行为受 THM-WIN 检测窗支配：沿 \(\varepsilon_m\) 单调、中心 ≈ \(\varepsilon_{\mathrm{tol}}\) |
| RQ2 双向对应（辨识侧） | —（模型检验） | POOL-SEM × MRSET | 块结构检验（PROP-IDF 伴随） | \(\xi(R)=\) 块外 kill 质量 / 总 kill 质量（理论计划 DEF-09） | ξ ≤ 预注册上界（草案 0.10），超界触发 THM-GAP 前提讨论 | kill 签名可辨识缺陷层 |
| RQ3 可构造性 | H-CONS | KER 全集（12 核）× POOL-SEM | EXP-CON 单臂生成漏斗（applicability-aware，5 级计数） | 实例化率 \(\hat p = n^{+}_{\mathrm{cell}}/n_{\mathrm{app}}\)（\(n^{+}_{\mathrm{cell}}\)=非等价变异体≥5 的 applicable cell 数，\(n_{\mathrm{app}}\)=applicable cell 总数），Wilson 95% CI | CI 下界 >0.5 | 证书准入的语义变异体可按预冻结适用矩阵批量构造 |
| RQ4 判别效度（零部分） | H-ZERO | KER 全集 × POOL-SEM × MRSET-ALN/CRS | EXP-DIS 处理-对照；预测标签=COR-ZERO 的 PRED_ZERO/NONZERO | balanced accuracy \(=(\mathrm{TPR}+\mathrm{TNR})/2\)，观测=cell SMS 是否为 0 | ≥0.75 且 McNemar p<0.05（vs 多数类） | SMS 的零来自理论预测的结构对齐缺失，非度量失效 |
| RQ4 判别效度（非零部分） | H-DISC | 同上（仅预测非零 cell；MR 源=v5 held-out） | EXP-DIS 两部分（hurdle）之条件比较 | 条件 Cliff's δ \(=\frac{\#\{(a,c):x_a>x_c\}-\#\{(a,c):x_a<x_c\}}{n_a n_c}\)（aligned vs cross），BCa 95% CI（10⁴ 次 bootstrap） | δ ≥ MID（模拟锁定，草案 0.33）且 CI 下界 >0 | 判别效度在非同源 MR 上成立，排除生成器同源伪迹 |
| RQ5 外部锚（前置门禁） | —（质量门禁） | DEF-REAL 标注 | 盲化 fiber 映射（双标注） | Cohen's κ \(=(p_o-p_e)/(1-p_e)\) | κ ≥0.6，否则走降级路径 | 映射可靠性达标，别名 `bug-算子-序号` 方可赋予 |
| RQ5 外部锚（校准） | H-CAL | DEF-REAL × MRSET 全部（DEF-CAL 仅训练） | EXP-EXT 前瞻盲测（映射盲+预测冻结哈希，buggy/fixed 双臂） | accuracy；Brier \(=\frac1n\sum_i(\mathrm{pred}_i-\mathrm{outcome}_i)^2\) | accuracy 显著优于多数类（McNemar p<0.05） | SMS 盲测预测在准入解耦的真实缺陷上可校准 |
| RQ5 外部锚（排序） | H-RANK | DEF-REAL × MRSET + POOL-SYN（MS 排序基线） | EXP-EXT 排序一致性 | 项目内 Kendall \(\tau_b\)（并列校正）后项目等权平均 \(\bar\tau=\frac1J\sum_j\tau_b^{(j)}\)；对比 \(\tau_{\mathrm{MS}},\tau_{\mathrm{PC}}\) | \(\bar\tau\) ≥ MID（草案 0.3）；\(\tau_{\mathrm{SMS}}-\tau_{\mathrm{MS}}\) 描述性报告 | SMS 排序对真实检出排序有外推力 |
| RQ-S 结构定位 | —（描述性） | POOL-SEM（v4+v5）vs POOL-SYN | EXP-STR AST 归一化精确重叠审计（逐引擎、逐算子族） | 重叠率 \(=\lvert M_{\mathrm{sem}}\cap M_{\mathrm{syn}}\rvert_{\mathrm{AST}}/\lvert M_{\mathrm{sem}}\rvert\) | 描述性，无判据 | 语义变异体大部不在语法引擎可达集内（定位主张，非优越性主张） |

统计符号的语境隔离与首现限定词规则见 §0.2。verified_full（DEF-CAL）不产确认性论点，防泄漏声明入 §6 Threats；seeded random（MRSET-RND）作 H-DISC/H-CAL 的 sanity floor。

### 1.3 预处理规范与统一标识

- **1.3.1 DEF-REAL 真实缺陷挖掘（核心预处理，两段式标识防循环）**
  1. **仓库白名单**（冻结进 Task 1.4 协议，不得因结果增删）：Defect4MR 已覆盖项目 + 主流权威科学计算仓库——numpy、scipy、scikit-learn、statsmodels、PyMC、GPy/GPyTorch、chaospy、SALib（候选池，Task 1.4 定稿）。
  2. **issue 扫描**：检索信号词（wrong result / incorrect value / numerical regression / precision loss / convergence failure / conservation violation / biased estimate 等），**排除** crash-only、构建/打包、API 误用、文档类；要求 issue 可定位到 fix commit。
  3. **语义符合性判定**：fix diff 的语义效应可映射到不变量族 \(\Psi\) 某层（符合本文语义变异体定义：类型/签名保持、在可采输入上违反某 \(\psi_j\)）；判定证据=（issue URL, buggy SHA, fixed SHA）三元组 + 一句机理说明。
  4. **双臂复现**：buggy/fixed 两版本构建+触发脚本（`reproducers/`）；失败标 `REPRO_FAILED` 保留不替换。
  5. **两段式统一标识**：准入期赋中性 ID **`EXT-<repo>-<序号>`**（如 `EXT-scipy-07`），准入期**禁止**出现任何算子/层归类；盲化 fiber 映射（Task 3.2）仲裁冻结后赋分析别名 **`bug-<算子代号>-<序号>`**（算子代号 ∈ Task 1.1 适用矩阵冻结的 5 算子；ADJACENT 记 `bug-ADJ-<序号>`，OUT_OF_SCOPE 记 `bug-OOS-<序号>`）；对照表入 SSOT `external_fiber_map`，**别名赋予 commit 必须晚于映射冻结、早于任何 kill 执行**（`git log` 时间戳可验证）。两段式的理由：算子归类是盲化映射的输出，若准入 ID 先带算子名，等于把待检验的对应关系写进选样，重蹈 D0 循环。
- **1.3.2 POOL-SEM**：applicability 过滤 → 生成（generator 版本/seed/prompt 哈希入 `GENERATION_LEDGER.md`）→ parse/build/trigger → E1∧E2 → 证书三态归档；统一标识 **`mut-<算子>-<PUT>-<序号>`**；全漏斗计数入 SSOT `funnel_v5`。
- **1.3.3 POOL-DOSE**：参数化算子实现；每档名义违反幅度 \(\varepsilon_m\) 标定入台账（THM-WIN 预测的横轴）；统一标识 **`mut-<算子>-<PUT>-e<档位>-r<重复>`**。
- **1.3.4 MRSET**：held-out provider 对称清单核对（prompt 同文/parser 同版/候选数/预算/温度同值）→ 生成 → prescreen；MRSET-RND 按冻结 seed 抽样，规模与 aligned 等大。
- **1.3.5 POOL-SYN**：mutmut 默认配置跑批 → AST 归一化（与 cosmic-ray 审计同一 normaliser）→ 精确匹配指纹表。
- **1.3.6 KER 各集**：无内容预处理；执行前路径盘点 + 文件 SHA256 固化入台账（保证与 P2 共用版本一致）。

### 1.4 对象集合构建与选取原则

四类对象集合（KER 核集、变异体池、MR 条件集、缺陷对集）共守四条元原则：**覆盖由理论决定、规模由功效决定、准入由协议决定、身份由 lineage 决定**。展开为七条可核验原则：

- **P1 分层覆盖（理论决定覆盖）**：核集按科学计算程序特征取 4 类 × 3 核（KER-NUM/STAT/SCIML/MLC），保证不变量族 \(\Psi\) 的五个语义层在每类上均有 applicable 格；否则 THM-GAP 的块结构在观测上不可检验。→ 服务 H-ZERO、H-DISC（RQ4）。
- **P2 签名同质（工程混淆控制）**：全部核限 `float→float` 紧凑实现（<2KB），使构建/触发的工程失败率≈0，把 P12 D1 教训（工程损耗淹没科学信号）挡在设计外。→ 服务全部假设的内部效度。
- **P3 预注册封闭（反 selection-on-response）**：各集合成员名单在 prereg tag 前冻结；追加只能由功效模拟（Task 1.2）触发且在冻结前完成；执行后不增删不替换（失败案以 `REPRO_FAILED` 等编码保留）。→ 服务全部确认性判据的可信度。
- **P4 development/confirmatory 隔离**：v4 资产（旧 60-cell、DEF-CAL）只用于参数估计、功效模拟、映射训练；确认性分母全部来自新 lineage（POOL-SEM、MRSET v5 held-out、DEF-REAL 冻结切片）。这是对"构念效度证据为负"论证中同源循环的直接修复。→ 服务 RQ4/RQ5 的确认性资格。
- **P5 真值锚独立（反循环）**：合成侧的层标签真值来自注入构造本身（生成期 \(\mathrm{eff}\) 标签）；外部侧的准入真值来自 issue+fix 双臂（明文排除"MR 可判别"条件，两段式标识见 §1.3.1）。两锚互不依赖 MR 侧结论。→ 服务 RQ5 外部锚的非循环性，回应 D0 选择偏倚。
- **P6 功效定规模**：每 cell 变异体密度（≥20）、cell 数、MR 集份数由功效模拟 ≥0.8 锁定；不足触发追加紧凑核决策（交作者拍板），拒绝追加则上调 MID 并披露欠功效。规模是推导量，不是方便样本。→ 服务 H-ZERO/H-DISC 判据的可解释性。
- **P7 对照完备**：每个确认性对比配 floor（MRSET-RND）+ 参照（MRSET-ALN）+ 跨引擎语法参照（POOL-SYN 双引擎），阻断"效应是单一工具伪迹"的替代解释。→ 服务 EXP-DIS/EXP-EXT/EXP-STR 结论的排他性。

### 1.5 实验方法卡片

| 卡片 | EXP-CON 构造审计 | EXP-DIS 判别（两部分） | EXP-DOSE 剂量反应 | EXP-EXT 外部盲测 | EXP-STR 结构审计 |
|---|---|---|---|---|---|
| 设计类型 | 单臂生成漏斗 | 处理-对照 | 单因子剂量梯度 | 前瞻盲测校准 | 结构比对 |
| 分析单位 | 候选变异体 | cell × MR 集 | 单次执行 | defect × MR 集 | 变异体 |
| 处理/对照 | —（分层=applicable） | aligned vs cross vs random floor | 幅度档 | 四组 MR 条件 × buggy/fixed 双臂 | 语义 vs 双引擎语法 |
| 随机化 | 生成 seed 台账 | MR 分配对称协议 | 档内 20 重复独立 seed | 执行顺序随机 | — |
| 盲化 | — | 生成者不见 kill 结果 | — | 双层：映射盲 + 预测冻结哈希 | — |
| 样本量 | 由 Task 1.2 锁定 | 同左（功效 ≥0.8） | ≥960 执行 | n≥20 缺陷 | 292+v5 vs 全部语法体 |
| 主检验 | Wilson CI | McNemar + hurdle（logistic + 条件 δ） | isotonic 置换 | McNemar + Kendall τ | 描述性 |

### 1.6 Baseline/对比基准配置总表

| 基准 | 精确配置 | 服务对象 | 角色 |
|---|---|---|---|
| cosmic-ray 默认 | 既有 1,250 一阶变异体，版本与配置沿用 §3.5 台账 | EXP-STR | 语法可达性参照（已有） |
| mutmut 默认 | 最新 stable 版，默认算子集，KER 全集（12 核）全跑，版本号入台账 | EXP-STR + EXP-EXT 的 MS 排序 | 第二语法引擎（新增，产 POOL-SYN） |
| seeded random MR 集（MRSET-RND） | 从预注册 MR 池按固定 seed 抽样，规模与 aligned 集等大 | EXP-DIS/EXP-EXT | sanity floor |
| 多数类预测器 | 训练集=development 数据的零/非零多数类 | H-ZERO/H-CAL | 预测下限 |
| 经典 MS 排序 | mutmut kill-rate 对各 MR 集排序（同模块、同预算） | H-RANK | "SMS 是否带来增量"对照 |
| Pattern Coverage 排序 | 既有 PC 指标对 MR 集排序 | H-RANK | 覆盖类代理对照 |
| E1-alone / E2-alone | 既有 App A.3 消融配置（判等程序消融，非实验标签） | 等价判定敏感性 | 消融（保留） |

### 1.7 计划级可度量目标

| 阶段 | 验收度量 |
|---|---|
| Phase 0 | SSOT 重生 diff=0；`check_ssot_consistency` exit 0；根因文档含两冲突值的复算命令 |
| Phase 1 | 适用矩阵 20 格全裁定 + 两人分歧记录；功效报告选定配置 H-ZERO/H-DISC 均 ≥0.8；6 假设全部含 MID+降级路径；FREEZE_MANIFEST 覆盖全部 prereg 文件；tag 存在 |
| Phase 2 | EXP-CON 漏斗 5 级计数完整入 SSOT；v5 对称清单 7/7 ✓；EXP-DOSE ≥960 条执行记录；EXP-STR 双引擎 KER 全集（12 核）全覆盖；四个 verdict 入 SSOT |
| Phase 3 | admission sheet 64 行全裁定；就绪 n≥20、项目 ≥8；κ≥0.6；预测冻结 commit 时间戳早于首个 run 产物（`git log` 可验证）；执行完整率 ≥95%（缺失单列原因） |
| Phase 4 | 处置表 12 行全闭合；每节编译过门禁；claim-evidence map 新增 ≥6 行 |
| Phase 5 | 引文审计 ✗=0、△≤5；`Missing character`=0；em-dash=0；arXiv tarball 含 .bbl |

---

## Phase 0：SSOT 冲突修复与数字管线（门禁：diff=0）

### Task 0.1：定位并复现冲突

- [ ] **Step 1:** 定位结果生成脚本与两个冲突数源：

```bash
rg -ln "0\.4392|0\.314" data/results/ submission/ scripts/ --glob "!*.pdf"
rg -ln "cliff|delta" scripts/ --glob "*.py" | head
```

- [ ] **Step 2:** 重跑结果脚本重生 `data/results/paper_numbers_v4.json`，`git diff data/results/paper_numbers_v4.json` 记录是否漂移
- [ ] **Step 3:** 追溯 0.314 的来源（脚本版本 / 数据切片 / 聚合口径），在 `docs/review_20260728/ssot_reconciliation.md` 写明根因与裁定值，两个数字各附计算命令

### Task 0.2：CI 式数字比对

**Files:** Create: `scripts/check_ssot_consistency.py`

- [ ] **Step 1:** 实现：从 main.tex 提取全部统计数字（正则匹配 `\d+\.\d{2,4}` 邻接关键词 delta/CI/p/mean），与 SSOT JSON 键值比对，不一致则非零退出并列出差异表
- [ ] **Step 2:** 验证：`python scripts/check_ssot_consistency.py submission/TOSEM_regular_20260706/main.tex data/results/paper_numbers_v4.json`，当前应报出 δ 冲突（若 20260706 稿沿用旧值）；修正 main.tex 后重跑，期望 exit 0
- [ ] **Step 3:** Commit：`fix(ssot): reconcile v4 cliff delta + add manuscript-SSOT consistency gate`

**REVIEW CHECKPOINT 0：作者确认裁定值与根因说明。此后任何稿件数字改动必须过 check_ssot_consistency。**

---

## Phase 1：预注册包（并行细则：Task 1.1/1.2/1.4 可在理论计划 CHECKPOINT T2 之前先行；Task 1.3 与冻结 tag 必须等 CHECKPOINT T2 通过）

### Task 1.1：适用矩阵冻结

**Files:** Create: `research/prereg_v2/applicability_matrix.md`

- [ ] **Step 1:** 从算子设计文档与 v4 development 数据，对 5 算子 × 4 PUT 类逐格声明 applicable / inapplicable + 一句机理理由（例：SI 需要可注入结构位点，B 类采样核无 → inapplicable）
- [ ] **Step 2:** 声明规则：inapplicable 格不进 H-CONS 分母、不进 H-DISC 对比；预测零（COR-ZERO）与不适用零分别编码 `PRED_ZERO_ALIGN` / `NOT_APPLICABLE`
- [ ] **Step 3:** 两人独立填写后合并分歧（记录分歧格与仲裁理由）；`shasum -a 256` 值写入文件头
- [ ] **Step 4:** Commit

### Task 1.2：功效模拟与 MID 锁定

**Files:** Create: `scripts/prereg/power_simulation.py`；Output: `research/prereg_v2/power_report.md`

- [ ] **Step 1:** 从 v4 数据估计两部分分布参数：P(SMS>0|aligned)、P(SMS>0|cross)、非零部分的 Beta 拟合参数
- [ ] **Step 2:** 模拟设计变量网格：applicable cell 数 × 每 cell 变异体数 {20,30} × MR 集数（v5 held-out 份数 {1,2}）；每格 2000 次模拟，输出 H-ZERO（McNemar）与 H-DISC（条件 Cliff's δ=0.33）的功效
- [ ] **Step 3:** 选定最小达 0.8 功效的配置写入 power_report；若 KER 全集（12 核）配置全部 <0.8，触发"追加 4–8 个紧凑核"决策（列出候选核清单与选择标准，交作者拍板）
- [ ] **Step 4:** Commit

### Task 1.3：假设与分析代码冻结

**Files:** Create: `research/prereg_v2/hypotheses.md`、`scripts/prereg/analysis_hzero.py`、`analysis_hdisc.py`、`analysis_hcons.py`、`analysis_hdose.py`、`analysis_hcal_hrank.py`

- [ ] **Step 1:** hypotheses.md 定稿六条（H-ZERO balanced accuracy ≥0.75 + McNemar；H-DISC 条件 δ ≥ 模拟锁定 MID + BCa CI；H-CONS Wilson 下界 >0.5；H-DOSE isotonic vs 常数置换检验；H-CAL accuracy/Brier 优于多数类；H-RANK 项目等权 Kendall τ ≥ MID，\(\tau_{\mathrm{SMS}}-\tau_{\mathrm{MS}}\) 描述性）；每条注明推导来源定理（THM-GAP/THM-WIN/COR-ZERO）与降级路径
- [ ] **Step 2:** 分析脚本按假设一比一实现，输入统一为 SSOT JSON 新键，输出统一 schema `{hypothesis, estimate, ci, p, verdict}`；对空输入跑通冒烟测试（合成数据）
- [ ] **Step 3:** 冻结机制：`git tag prereg-v2-freeze && shasum -a 256 research/prereg_v2/* scripts/prereg/*.py > research/prereg_v2/FREEZE_MANIFEST.sha256`
- [ ] **Step 4:** Commit

### Task 1.4：外部切片准入与映射协议

**Files:** Create: `research/prereg_v2/external_slice_protocol.md`

- [ ] **Step 1:** 准入三条（且仅三条）：真实缺陷（公开 issue+fix commit）；双臂可复现（buggy/fixed 构建+触发）；in-scope（单/少输出数值核，签名可适配）。**明文排除** "MR 可判别"条件并注明这是对 D0 循环的修正
- [ ] **Step 1b:** 内嵌 §1.3.1 挖掘规范：仓库白名单定稿（Defect4MR 覆盖项目 + numpy/scipy/scikit-learn/statsmodels/PyMC/GPy/GPyTorch/chaospy/SALib 候选池取舍）、issue 检索信号词与排除类清单、语义符合性判定模板（issue URL + buggy SHA + fixed SHA + 一句机理）、两段式统一标识规则（准入期 `EXT-<repo>-<序号>`，映射冻结后 `bug-<算子代号>-<序号>`；准入期禁止出现算子归类）
- [ ] **Step 2:** fiber 映射协议：两名标注者、训练集=DEF-CAL（verified_full）中 10 例（development）、标签集 {DIRECT, ADJACENT, OUT_OF_SCOPE, UNCERTAIN}、盲化规定（不见 kill 结果、不见对方标注）、κ≥0.6 门禁、分歧仲裁程序
- [ ] **Step 3:** 冻结预测协议：执行前对每 (defect, MR set) 产出 detect/miss 预测 + 每 MR 集 SMS 排序预测，`shasum -a 256` 存证；揭盲规则
- [ ] **Step 4:** Commit

**REVIEW CHECKPOINT 1：作者审预注册包全件（矩阵、功效配置、六假设、协议），冻结后进入执行。**

---

## Phase 2：构念线（EXP-CON / EXP-DIS / EXP-DOSE / EXP-STR，4–6 周，与 Phase 3 并行）

### Task 2.1：新变异体生成（v5 lineage，EXP-CON）

- [ ] **Step 1:** 按 Task 1.2 锁定配置在 applicable cell 生成新变异体（生成器版本、seed、prompt 哈希入台账 `data/v5/GENERATION_LEDGER.md`）；逐个赋统一标识 `mut-<算子>-<PUT>-<序号>`（§1.3.2）
- [ ] **Step 2:** 全漏斗插桩：parse/build/trigger/E1∧E2/证书 各级损耗计数落 SSOT 新键 `funnel_v5`
- [ ] **Step 3:** 跑 `analysis_hcons.py`，verdict 入 SSOT；Commit

### Task 2.2：held-out MR source（v5-MR，EXP-DIS）

- [ ] **Step 1:** 选定未用过的 provider（候选按对称协议可满足性排序），逐项核对对称清单：prompt=v4 同文、parser 同版、候选数/修复次数/预算/温度同值；清单存 `data/v5/MR_SOURCE_SYMMETRY.md`
- [ ] **Step 2:** 生成 aligned/cross MR 集 → prescreen → kill 矩阵
- [ ] **Step 3:** 跑 `analysis_hzero.py`（零预测：THM-GAP/COR-ZERO 预测标签 vs 观测零/非零）与 `analysis_hdisc.py`（条件判别）；verdict 入 SSOT；Commit

### Task 2.3：剂量反应实验（EXP-DOSE，H-DOSE）

- [ ] **Step 1:** 参数化算子实现：HP（超参幅度）与 CE（守恒侵蚀强度）各设 ≥6 档幅度网格，每档名义违反幅度 \(\varepsilon_m\) 标定入台账（§1.3.3）；对象=每类一核（Lorenz、MC 积分、GPR、LogReg，数据键 A1/B3/C1/D3；若理论计划 Phase T3 判某核的 Lipschitz 常数 \(L_r\) 不可估则按其清单替换）
- [ ] **Step 2:** 每档 × 20 重复执行 kill 判定（个体标识 `mut-<算子>-<PUT>-e<档位>-r<重复>`），曲线数据落 SSOT `dose_response_v5`
- [ ] **Step 3:** 跑 `analysis_hdose.py`（isotonic vs 常数，置换 p；Page's L）；同时报告转变位置与 THM-WIN 预测中心 \(\varepsilon_{\mathrm{tol}}\) 的偏差（模型检验，不设通过线）；Commit

### Task 2.4：语法基线扩充（EXP-STR）

- [ ] **Step 1:** mutmut 默认配置跑 KER 全集（12 核），产物 AST 归一化后与 v4+v5 语义变异体（POOL-SEM）做精确重叠审计（复用现有 cosmic-ray 审计脚本，`rg -l "ast" scripts/ | head` 定位）
- [ ] **Step 2:** 双引擎重叠表入 SSOT `syntactic_overlap_v2`；Commit

**REVIEW CHECKPOINT 2：构念线四组结果（H-CONS/H-ZERO/H-DISC/H-DOSE）verdict 汇报，含任何降级触发。**

---

## Phase 3：外部线（EXP-EXT，6–10 周。并行细则：Task 3.1/3.2 在 Task 1.4 协议单独冻结（hash 入库）后即可启动，不必等 Phase 1 全部完成；Task 3.3 冻结预测额外要求理论计划 Phase T3（THM-WIN 草稿）完成）

### Task 3.1：重裁与就绪检查

- [ ] **Step 1:** 对 Defect4MR 64 候选按 Task 1.4 三条准入重裁，产出 `data/external_slice/admission_sheet.csv`（列：neutral_id=`EXT-<repo>-<序号>`、issue_url、buggy_sha、fixed_sha、三条判定、纳入/排除理由；analysis_id 列此阶段留空，Task 3.2 映射冻结后回填）；预期可纳入池 ≥30（verified_full 35 去掉 oracle 条件后基本全过 + candidate_full 16 部分过）
- [ ] **Step 2:** 就绪检查：逐案跑双臂构建+触发冒烟（复用 `reproducers/`），失败案标 `REPRO_FAILED` 保留不替换；目标就绪 n≥20、≥8 项目，不足则按 §1.3.1 白名单+检索信号词启动补充挖掘（准入判定同 Task 1.4 三条）
- [ ] **Step 3:** **切片冻结**：名单 SHA256 入 `data/external_slice/FREEZE.sha256`；Commit

### Task 3.2：盲化 fiber 映射

- [ ] **Step 1:** 发放标注包（缺陷描述+fix diff，无任何 MR/kill 信息）；两人独立标注
- [ ] **Step 2:** 计算 κ（`analysis_hcal_hrank.py` 内置函数）；κ<0.6 → 协议修订一轮重标（预注册允许一次）；仍不达 → DIRECT 主分析降敏感性分析（降级路径生效）
- [ ] **Step 3:** 仲裁后映射表冻结入 SSOT `external_fiber_map`；按 §1.3.1 赋分析别名 `bug-<算子代号>-<序号>`（ADJACENT → `bug-ADJ-`、OUT_OF_SCOPE → `bug-OOS-`）回填 admission_sheet 的 analysis_id 列——**此 commit 必须早于任何 kill 执行**；Commit

### Task 3.3：冻结预测

- [ ] **Step 1:** 按 fiber 对齐 + THM-WIN 窗口（可估处）生成每 (defect, MR set) detect/miss 预测与 MR 集排序预测；写 `data/external_slice/predictions_frozen.json`
- [ ] **Step 2:** `shasum -a 256 data/external_slice/predictions_frozen.json >> data/external_slice/FREEZE.sha256 && git commit`——此 commit 必须早于任何执行产物

### Task 3.4：执行与揭盲

- [ ] **Step 1:** 对就绪案逐一执行四组 MR（aligned/cross/v5/random floor）于 buggy/fixed 双臂；原始判定落 `data/external_slice/runs/`
- [ ] **Step 2:** 经典 MS 基线：mutmut 跑对应模块得 kill-rate 排序；Pattern Coverage 排序同步计算
- [ ] **Step 3:** 跑 `analysis_hcal_hrank.py`：预测校准（accuracy/Brier vs 多数类）、项目等权 Kendall τ（SMS 排序 vs 真实检出排序）、\(\tau_{\mathrm{SMS}}-\tau_{\mathrm{MS}}\) 与 \(\tau_{\mathrm{SMS}}-\tau_{\mathrm{PC}}\) 描述性对比、OUT_OF_SCOPE 份额；全部入 SSOT `external_validation`
- [ ] **Step 4:** Commit

**REVIEW CHECKPOINT 3：外部线揭盲结果汇报；若 H-CAL/H-RANK 无信号，确认按预注册降级叙事（有界不一致 + THM-GAP 归因）执行写作。**

---

## Phase 4：手稿重构写作（3–4 周，可与 Phase 2/3 尾部重叠）

### Task 4.1：建立 v2 工作副本

- [ ] **Step 1:** `cp -r submission/TOSEM_regular_20260706 submission/TOSEM_regular_v2_workdir && git add -A && git commit -m "docs(v2): open manuscript workdir"`（理论计划的 §2 改动若已落在 20260706 目录则以其为源）

### Task 4.2：章节改写（按 writing-plan §0 处置表执行）

- [ ] **Step 1:** §1：旗舰主张一句话替换摘要与贡献段；新 RQ1–RQ5 表（口径=本计划 §0.3）；**论文 2 边界段**（concurrent TOSEM submission 声明 + "元模式作为给定词汇消费"）；claim-evidence map 增补 THM-INT/THM-GAP/THM-WIN/PROP-IDF 行与外部锚行（骨架=§1.2 链路总表）
- [ ] **Step 2:** §3 新增四小节：适用矩阵（引 prereg 哈希）、剂量反应设计、held-out source 对称协议、外部切片准入与盲化协议（含 §1.3.1 两段式标识）；baseline 小节并入 mutmut/random-floor/MS 排序三基线；对象选取原则段=§1.4 的 P1–P7 压缩版（≤1 段）；对象命名一律用 §1.1 语义集合名（KER-*/POOL-*/MRSET-*/DEF-*）
- [ ] **Step 3:** §4 重排：**先 H-ZERO 零预测准确率 → H-DISC 条件判别 → H-CONS/H-DOSE → 外部线 H-CAL/H-RANK → Prior Audit 小节（旧 H1–H4 原样 + 一段"为什么旧阈值与理论错配"）**；全部数字模板注入自 SSOT
- [ ] **Step 4:** §5：缺口归因解读段（零膨胀的 \(\mathrm{Gap}_{\mathrm{aln}}(R)\) 部分=理论确认）、SMS vs MS 有界比较段（明示不做普适优越主张）、T1/T2/T4 接口段（各一句+引用）
- [ ] **Step 5:** §6 Threats 新增：双重使用防火墙（旧数据用途清单）、外部切片选择披露（准入解耦声明+就绪失败案保留）、v5 provider 单一性
- [ ] **Step 6:** 每节改完即编译 + `python scripts/check_ssot_consistency.py` 过门禁；分节 commit

### Task 4.3：图表重生

- [ ] **Step 1:** 新图清单：区间宽度 vs 证书预算（THM-INT 演示）、块结构热图（fiber × MR 层 kill matrix + ξ 标注）、剂量反应曲线（4 PUT × 2 算子）、外部校准图（预测 vs 观测 + Kendall τ 对比条）；沿用 `figs/` 现有生成脚本风格，300dpi PNG + PDF 双格式
- [ ] **Step 2:** Commit

**REVIEW CHECKPOINT 4：全稿通读稿交作者；确认叙事顺序与降级措辞。**

---

## Phase 5：投稿前流水线（CLAUDE.md §3 五步，1–2 周）

- [ ] **Step 1:** academic-pipeline stage 检测（终稿 → stage 4.5 FINAL INTEGRITY）
- [ ] **Step 2:** 参考文献真实性校验（paper-search MCP 逐条，审计表落 `docs/review_<DATE>/reference_verification.md`；门槛 ✗=0、△≤5）
- [ ] **Step 3:** proofread：数字/交叉引用/符号先用后定义（对照理论计划 §0.2 总表逐项）/图表 caption 一致性
- [ ] **Step 4:** humanizer 去 AI 化（em-dash 零容忍、AI 高频词清单、连接词保留规则）
- [ ] **Step 5:** 构建验证：两遍编译 + `grep -c "Missing character" main.log`=0 + check_ssot_consistency=0；arXiv 预印本 tarball 同步构建（.bbl 内联、图平铺）；Commit + tag `tosem-v2-submitted`

---

## 风险与回退

| 风险 | 触发点 | 处置 |
|---|---|---|
| 功效模拟判 KER 全集（12 核）不足 | Task 1.2 | 追加核清单交作者拍板；若拒绝追加 → H-DISC MID 上调并在 §6 披露欠功效 |
| v5 provider 不满足对称清单 | Task 2.2 | 换第二候选；全部不满足 → 判别线降 development 复现，H-DISC 降 exploratory |
| 就绪 n<20 | Task 3.1 | 启动补充挖掘（预算 2 周）；仍不足 → 按实际 n 报告并在 §6 披露，H-RANK 的 τ MID 不变 |
| 揭盲后发现预测协议歧义 | Task 3.4 | 歧义案单列 `PROTOCOL_AMBIGUOUS` 不计入主分析，附敏感性分析含入版本 |
| 任一确认性假设失败 | 各 checkpoint | 按 hypotheses.md 预注册降级路径执行，不改阈值、不删数据 |
