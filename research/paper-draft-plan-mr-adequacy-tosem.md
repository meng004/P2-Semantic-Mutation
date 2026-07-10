# 论文初稿计划：MR 集合充分性 × held-out 决策价值主实验（TOSEM 重写）

> 状态：初稿计划 v1.0（2026-07-10）
> 上游文档：`research/paper-outline-semantic-mutation-mr-adequacy.md`（论证骨架 v0.1，branch `claude/paper-journal-acceptance-kxpveo` @ 0274196）
> 触发输入：EIC quick assessment（verdict：Reject—Premature, Resubmission Encouraged；核心缺口 = 尚无一项能证明 SMS 改变软件测试决策的主实验）
> 前提约束：**忘记已有正文、附录和四项旧实验的叙事结构**；旧数据只按提纲 §10 的迁移决策充当 pilot / 探索性证据；新论文的确认性结论必须全部来自本计划定义的新双盲实验。

---

## 0. 计划的一句话

在提纲 v0.1 的形式框架之上，把 EIC 的 P0 要求落成一项**预注册、双盲、held-out 的 MR 决策价值实验（Decision-Value Experiment, DVE）**：证明（或证伪）"用 SMS/residual faults 指导 MR 选择，在同等预算下，对**从未见过的**认证语义缺陷取得比经典 mutation score、MR coverage 和随机选择更高的检测收益"。该实验成为论文的确认性核心；提纲原有的 RQ1–RQ4 降为构造性与诊断性支撑。

---

## 1. EIC 意见 → 计划映射

| EIC 优先级 | 意见要点 | 本计划的落点 |
|---|---|---|
| **P0** | 执行 held-out decision-value 实验 | §3（主实验 DVE 完整技术方案与论证） |
| **P1** | 冻结独立认证规则：A–C 级进 primary denominator，纯专家裁决 D 级只进敏感性分析 | §4.1（认证规则冻结条款，写入预注册） |
| **P1** | 证明 Fault Card 外部来源：需求 / 算法规范 / 历史缺陷 + 时间戳 + 访问隔离记录 | §4.2（provenance ledger + hash 承诺机制） |
| **P2** | 补充最邻近工作差异：domain-specific mutation / specification mutation / PBT / MR adequacy | §5（四族最邻近工作差异表，进 Related Work §2.3–2.4） |
| **P3** | 最后再扩写正文、摘要与投稿信 | §7（写作顺序：Results-first，Intro/Abstract/cover letter 最后） |

EIC 指出的三个相互关联的问题，本计划的针对性回答：

1. **"\(M_\Sigma(P)\) 只存在于方法定义中"** → §3.3 Phase 1–2 真实构建它，且设验收门槛 G1（认证变异体数量与证据等级达标才允许进入后续阶段）。292 个旧变异体按提纲 §10 只作 pilot，用于功效分析的先验参数，不进任何新 denominator。
2. **"独立认证可能重新引入 oracle problem"** → §3.8 给出三段论辩护（证书是一次性、离线、面向实验仪器有效性的构造物，不是面向任意生产输入的通用输出 oracle），并规定论文正文必须以独立小节（§3.3 末或 §6 Discussion）承载该辩护。
3. **"SMS=1 ⟺ U=∅ 是定义性结论"** → 论文的经验主张从充分性等价式**整体迁移**到可证伪的比较性假设 H-DV（§3.6）：residual-guided 选择是否在 held-out 缺陷上产生更高检测收益。定义性等价式只保留为框架性质（提纲命题 1），不作为经验贡献宣称。

---

## 2. 新论文的贡献与 RQ 重组

### 2.1 贡献收敛（在提纲 §9 三条之上增加第四条并调序）

1. **C1 概念与兼容性**（提纲 §9-1，保持）：语义规范、Fault Card、认证语义变异体、SMS，作为经典 mutation-score 结构的保守扩展。
2. **C2 MT 充分性准则**（提纲 §9-2，保持）：组级 MR verdict、kill、残余缺陷集、相对充分性。
3. **C3 双盲构建协议**（提纲 §9-3，保持）：MR-free 缺陷构造、independent certification、freeze-before-crossing。
4. **C4 决策价值证据（新，成为 headline）**：预注册 held-out 实验证明 residual-guided MR 选择相对三类 baseline 的检测收益（或如实报告无收益，将框架限定为诊断工具——提纲 §5.5 的诚实条款保留）。

### 2.2 RQ 重组（提纲 §2.1 的四问 → 五问，决策价值升为确认性核心）

| 新编号 | 内容 | 性质 | 对应提纲 |
|---|---|---|---|
| RQ1 | 构造性：能否 MR-free 地构造并独立认证语义变异体集合？ | 构造性 | 原 RQ1 |
| RQ2 | 区别性：语义缺陷域与句法缺陷域的机理/覆盖差异 | 描述性 | 原 RQ2 |
| RQ3 | **决策价值：residual-guided MR 选择是否在 held-out 缺陷上优于 MS-guided / coverage-guided / random？** | **确认性（预注册主检验）** | 新增（EIC P0） |
| RQ4 | 充分性诊断：冻结 MR 集合对声明缺陷域的 SMS、残余缺陷结构 | 诊断性 | 原 RQ3 |
| RQ5 | 判定与结论稳健性：样本、容差、证据等级、预算的敏感性 | 稳健性 | 原 RQ4 + 扩展 |

原 H2（严格充分性 SMS=1）不再作为 headline 假设：它对 \(R_0\) 大概率被证伪（这正是 residual faults 存在、S1 策略有事可做的前提），在论文中作为 RQ4 的诊断结果如实报告，避免"把失败阈值藏进平均数"的旧问题。

---

## 3. 主实验 DVE：技术方案与论证（P0，本计划的核心）

### 3.1 设计总览

两阶段、双盲、held-out、四策略、同预算：

```
Phase 0  角色冻结 + 预注册            （§3.2）
Phase 1  双盲语义缺陷池构建 + 独立认证  （§3.3，分支 A，MR-free）
Phase 2  dev/holdout 划分 + 密码学承诺 （§3.4）
Phase 3  MR 候选目录 R_cand 独立构建   （§3.5，分支 B，mutant-free）
Phase 4  开发期交叉执行（R_cand × M_dev + 句法池）
Phase 5  四策略同预算选择（算法化，代码冻结）
Phase 6  解盲：R_k^S × M_holdout 一次性评估 + 历史缺陷外部臂
```

关键不变量（写入预注册，违反即实验作废）：

- **I1 独立性**：M 池构建全程不可见任何 MR 定义、实现、结果（提纲定义 6 的角色访问矩阵照搬执行）。
- **I2 非循环性**：SMS/residual 信号只允许来自 \(M_{\mathrm{dev}}\)；四个策略以**冻结代码**形式在解盲前定稿（commit hash 封存）；\(M_{\mathrm{holdout}}\) 在全部策略输出选定 MR 集合之后才解密。
- **I3 同预算**：所有策略在完全相同的决策空间（同一 \(R_{\mathrm{cand}}\)）与完全相同的预算 \(k\) 下比较。
- **I4 一次性**：holdout 只打开一次；不允许任何"看了结果再补一轮"的操作。全流程先在 pilot 数据上彩排（dry-run），再对真 holdout 执行。

### 3.2 Phase 0：对象、角色与预注册

**PUT 集合**：现有 12 个科学计算 PUT（`src/p2/puts/`）作为主载体（程序本身未被污染，污染在旧 mutant/MR 的共同设计史；对策是全部材料重新冻结 + 新盲化团队/角色），另招募 **6–8 个新 PUT**，选自带有可考历史缺陷（bug-fix commit 可定位）的开源科学计算内核（SciPy/NumPy/statsmodels 类），承担外部验证臂（§3.7）。PUT 选择标准沿用提纲 §4.2：单输出/低输出维、确定性或可控随机、存在可信参考实现或解析解。

**角色隔离**：变异生成者、语义认证者、MR 设计者、执行器、holdout 托管者（custodian）、解盲分析者。单作者现实下的可操作化：角色按时间锁 + 独立 git 分支 + hash 承诺实现程序性隔离，D 级认证与 LRCA 类编码引入第二评者（κ 报告）；"同一人分时扮演多角色"作为 threat 显式披露（提纲 §6.5 已列共同规范偏差，此处加一条角色隔离强度的 threat）。

**预注册内容**（`docs/prereg/DVE_prereg_v1.md`，冻结时打 tag + 记录 SHA-256；可选同步 OSF）：假设 H-DV/H1/H3'、primary endpoint、预算 \(k^\*\)、统计检验与 α、效应量与 MID（最小重要差异）、样本量与功效模拟、认证规则（§4.1）、策略算法伪代码、停止规则、null 结果的解释规则（§3.9）。

### 3.3 Phase 1：双盲语义缺陷池（构建真实的 \(M_\Sigma(P)\)）

流程沿提纲 §7.2（Fault Card 库 → 候选生成 → 机械检查 → 独立认证 → 冻结），本计划的增量约束：

- **来源约束（EIC P1）**：Fault Card 只允许四类外部来源——需求/领域约束文档、算法规范（教材与数值分析文献的算法性质）、历史缺陷（issue/commit URL）、FMEA 分析。每张卡带 `prov` 字段：来源类型、引用、获取时间戳、录入者角色。**禁止**来源字段为"作者直觉"或"LLM 建议"单独成立（LLM 可辅助起草，但必须回溯锚定到四类来源之一）。
- **认证等级门槛（EIC P1）**：A–C 级证书进 primary denominator；D 级（双专家独立裁决）单独成池，只进 RQ5 敏感性分析。规则在 Phase 0 冻结，禁止事后按结果调整（详见 §4.1）。
- **规模目标**：认证（A–C）变异体总量 ≥ **300**（跨 12+ PUT、各缺陷机理类最低配额 ≥ 15），由 §3.6 功效模拟反推。旧 v4 数据提供先验：kill 率量级 0.1–0.4 区间，据此模拟不同 baseline 检测率下的 holdout 需求量。
- **验收门槛 G1**：A–C 认证量、类配额、认证率达标才进入 Phase 2；不达标触发预注册的范围收缩规则（缩减缺陷类而非放松认证标准）。

### 3.4 Phase 2：dev/holdout 划分与密码学承诺（非循环性的机制保证）

- 划分时点：**任何 MR 交叉执行发生之前**（严格早于 Phase 4）。
- 划分方式：按 (PUT × 缺陷机理类 × 证书等级) 分层随机，比例 50:50（dev 用于产生指导信号，holdout 用于确认，均衡分配统计功效）。随机种子预注册。
- 承诺机制：holdout 变异体 ID 列表 + salt 的 SHA-256 写入 git（timestamped commit + tag）；holdout 变异体 diff 加密存放，密钥由 custodian 角色（时间锁）持有；解密条件 = 四策略输出的 MR 集合以 commit hash 封存完毕。
- 审计产物：`data/dve/split_commitment.json`（hash、时点、分层表），解盲后公开 salt 供第三方验证。

**论证**：这是对 EIC "非循环性"质疑的机制性回答——不是靠声明"我们没看"，而是靠密码学承诺与提交历史让"看不到"成为可第三方审计的事实。这也直接补齐提纲 §7 双盲协议中缺失的"时序可证明性"。

### 3.5 Phase 3：MR 候选目录 \(R_{\mathrm{cand}}\) 与初始集 \(R_0\)

- MR 设计者只读 \(P,\Sigma\) 与 MT 文献，产出 **40–60 条**候选 MR（每 PUT 覆盖 generic 关系与领域特定关系两层），每条按提纲定义 7 冻结 \((T_r,\rho_r,A_r,G_r,\Theta_r)\)。
- 原程序 false-positive 筛查（提纲命题 3）：原程序 fail 的 MR 标记 invalid，保留在目录中但永不产生 kill。
- \(R_0\)（初始 MR 集合）：模拟从业者起点——按预注册启发式（每 PUT 取文献最常用的 generic MR \(k_0\) 条）在任何执行前选定。\(R_0\) 的作用是制造"已有一个普通 MR 集合，问题是接下来加哪几条"的真实决策场景。

**关键设计决策及论证——为什么主实验用"目录内选择"而不是"自由人工 revision"**：

EIC 原文建议 "SMS/residual-guided MR revision"。本计划把确认性主实验操作化为**同一冻结目录上的算法化选择策略**，把自由人工 revision 降为次级 Tier-2 臂，理由：

1. **消除人的技能混淆**：四个策略若各由人执行 revision，检测差异无法归因于指导信号（SMS vs MS vs coverage）本身，而可能来自设计者水平、疲劳、顺序效应；算法化选择使唯一自变量就是指导信号。
2. **同预算可精确定义**：目录内选择使 \(k\) 条 MR 的预算在四臂间逐条可比；自由 revision 的"预算"只能用工时近似，噪声大且不可复现。
3. **完全可复现**：策略是确定性代码（随机臂给定种子），审稿人可重跑；这直接服务 TOSEM 的 reproducible/archival 要求。
4. **保留生态效度的补偿**：Tier-2 臂（§3.7）让一名盲化 MR 工程师仅凭 dev residual Fault Cards 自由设计新 MR，检验"人 + residual 信息"的端到端收益，作为次级证据报告，不进 primary endpoint。

### 3.6 Phase 4–6：策略定义、endpoint 与统计方案

**四策略（同一决策空间 \(R_{\mathrm{cand}}\setminus R_0\)，同预算 \(k\)，全部贪心/随机算法，代码冻结）**：

| 策略 | 指导信号 | 算法 |
|---|---|---|
| S1 residual-guided（treatment） | \(K_{\mathrm{dev}}\)（R_cand × M_dev kill matrix）中 \(U(R_0,M_{\mathrm{dev}})\) 的覆盖 | 贪心 set-cover：每步选新覆盖 dev 残余认证变异体最多的 MR；平局按执行成本低者 |
| S2 classical-MS-guided | 句法变异池（Cosmic Ray 默认一阶算子，配置冻结）对 \(R_0\) 的存活句法变异体覆盖 | 与 S1 同构的贪心，只是信号换成句法 kill matrix |
| S3 MR-coverage-guided | 预注册的 MR 覆盖度量（输入变换类别覆盖 + follow-up 执行代码覆盖），不使用任何变异体信息 | 贪心最大化覆盖增量 |
| S4 random / generic baseline | 无信号 | 随机抽 \(k\) 条（1000 次重抽给出分布）；另设固定 generic-MR 参照 |

S2 的存在回答"SMS 比经典 MS 好在哪"，S3 回答"比不看缺陷的覆盖启发好在哪"，S4 提供无信息下界。三个 baseline 恰好对应 EIC 点名的比较对象。

**预算**：primary 分析取预注册的 \(k^\*\)（拟定 \(k^\*=4\)，以 pilot 彩排校准后冻结）；\(k\in\{2,4,6,8\}\) 扫描进 RQ5。另报告执行成本归一化视角（每小时执行预算下的检测量）。

**Primary endpoint**：\(\Delta_{\mathrm{det}} = \) held-out 检测率差 \(\;\mathrm{DR}(R_0\cup S_1(k^\*)) - \mathrm{DR}(R_0\cup S_4(k^\*))\)，其中 \(\mathrm{DR}(R)=1-|U(R,M_{\mathrm{holdout}})|/|M_{\mathrm{holdout}}|\)。Secondary：对 S2、S3 的同型差；\(|U|\)、unique kills、每新检出缺陷的执行成本、per-class 覆盖。

**预注册假设**：

- **H-DV（primary，确认性）**：\(\Delta_{\mathrm{det}}>0\) 且点估计 ≥ MID（拟定 10 个百分点，功效模拟后冻结）。
- **H-DV2（secondary）**：S1 ≥ S2、S1 ≥ S3（Holm 校正族）。
- **H1'（区别性，承接原 H1）**：A–C 认证语义池与句法默认池的机理/patch 重叠有限（沿用提纲 RQ2 度量）。
- **H3'（稳健性）**：H-DV verdict 在证书等级（±D 级）、容差、\(k\) 扫描、组级判定重复策略下不翻转。

**统计分析（预注册，吸取 v4 的教训）**：

- 分析单位：holdout 变异体上的配对二值检测结果（同一批变异体过四个 MR 集合 → 天然配对）；PUT 为聚类单位（提纲 §4.10）。
- Primary 检验：S1 vs S4 配对差的 **PUT-cluster bootstrap**（BCa CI on risk difference）+ 配对 exact McNemar 作 companion；多重比较 Holm。
- GLMM（detection ~ strategy + (1|PUT) + (1|mutant)）作为 secondary，**预注册 singular-fit 回退路径 = cluster bootstrap**（v4 已知 mixed-effects singular 问题，不再临场决定）。
- S4 随机臂以重抽分布报告，S1 的分位数位置（超过多少比例的随机选择）作为直观效应量。
- **功效模拟**：以 pilot（旧 v4 kill 率 + dev 池首批认证率）为先验，模拟 baseline 检测率 0.3–0.6、MID=10pp、ICC(PUT) 0.1–0.3 情形下 80% 功效所需 \(|M_{\mathrm{holdout}}|\)；初算指向 120–150，由此反推 §3.3 的 ≥300 总池目标。模拟脚本与假设进预注册附件。

### 3.7 外部验证臂：真实历史缺陷（held-out 第二层）

- 从新招募 PUT 的上游仓库提取历史缺陷（bug-fix commit 反向应用），准入条件**只有**认证证据（C 级：真实缺陷 + 修复补丁 + 可复现违反 \(\Phi\)），**明确禁止**以"某条 MR 能检测它"为准入条件（EIC 的红线，也写进提纲 §4.8-4 的 baseline 条款）。
- 该池对全部策略同样 held-out；报告四策略检测率。样本量预期较小（10–30），只作外部效度佐证，不承载 primary 检验；如实以描述统计 + CI 呈现。
- **Tier-2 人工 revision 臂**挂在此处一并报告：盲化工程师凭 dev residual Fault Cards 设计 ≤ \(k^\*\) 条新 MR（工时记录），在两层 holdout 上评估；作为生态效度证据。

### 3.8 对"oracle problem 重新引入"的正面辩护（进论文正文）

论文必须在 §3.3（认证定义之后）或 §6.2 用一小节回答"既然有足够强的 oracle 证明程序错误，为什么还需要 MT"：

1. **对象不同**：证书 \(\kappa\) 认证的是**实验仪器**（denominator 中每个缺陷构造确实违反 \(\Sigma\)），是一次性、离线、每缺陷一个见证输入的构造物；MT 面向**任意生产输入**的持续测试，二者在输入覆盖、运行时机、成本结构上不同层。
2. **成本不对称**：A/B 级证据（解析解、参考实现）只需对少量见证点成立；把它们变成逐输入运行时 oracle 需要参考实现在全输入域可用且可信——这正是 MT 所回避的前提。实验室里为若干科学内核构造证书可行，不代表生产环境有通用 oracle。
3. **方法部署形态**：SMS-guided 实践在部署时消费的是**缺陷模型（Fault Cards）与 kill matrix**，不要求使用者拥有证书级 oracle；证书只出现在方法学评价（本文实验）中，用于让 denominator 可信。
4. 类比锚点（Related Work 引用）：mutation testing 评价测试套件时也依赖"已知缺陷注入 + 已知正确版本"这一实验室特权，从未因此否定被评价测试技术的价值。

### 3.9 Null 结果与失败模式的预注册解释规则

- 若 H-DV 不成立（CI 跨 0 或 < MID）：论文如实降级为"SMS 是诊断框架，未证明选择收益"（提纲 §5.5 / §6.3 的诚实条款），Discussion 分析失败机制（信号弱？目录同质？dev/holdout 分布移位？）。**不允许**换 endpoint、换 \(k\)、换 denominator 补救。
- 若全目录 \(R_{\mathrm{cand}}\) 在 holdout 上的天花板检测率过低（如 < 0.5）：说明缺陷域大幅超出关系可观察范围，报告为重要负结果 + residual 结构分析。天花板分析预注册为必报项。
- 若认证池不达 G1：按预注册收缩规则缩小缺陷类范围并如实报告，不降低认证标准。

### 3.10 主实验方案自查：EIC 四问逐条对照

| EIC 质疑 | 机制回答 |
|---|---|
| 独立性 | 分支 A 全程 MR 不可见（角色访问矩阵 + provenance ledger + git 时序）；§3.3 |
| 非循环性 | SMS 信号限于 dev；策略代码冻结先于解盲；holdout 密码学承诺；§3.4/3.6 |
| 外部效度 | holdout 分层 + 新 PUT + 无 MR-detectability 准入的历史缺陷臂；§3.7 |
| 决策价值 | endpoint 就是"加哪 k 条 MR"这个决策在未见缺陷上的收益，对照 MS/coverage/random 三类现有信号；§3.6 |

---

## 4. P1 项：认证规则与来源证明的冻结条款

### 4.1 认证规则冻结（进预注册 §"Certification Rules"）

- 证据等级表沿提纲 §7.3；**A/B/C → primary denominator；D → sensitivity-only 池；"不准入"行照抄**（仅 LLM/作者意图、或仅被某 MR 杀死的候选体，永不进任何 denominator）。
- 等价判定 \(\widehat{\mathrm{Eq}}_{\Sigma,B,\tau}\) 的样本量、参考 oracle、容差在 Phase 0 冻结；操作性等价的敏感性扫描进 RQ5。
- D 级双专家裁决报告 κ；κ < 预注册阈值（拟 0.6）的类整体降出 D 池。
- 冻结后任何规则变更 = 协议偏离，必须在论文 Deviations 小节披露。

### 4.2 Fault Card 外部来源证明（provenance ledger）

- 每张卡的 `prov` 必填：来源类型（需求/算法规范/历史缺陷/FMEA）、可解引用的出处（文档节号、DOI、issue/commit URL）、录入时间戳、录入角色。
- Ledger 以 append-only JSONL 存 `data/dve/fault_card_ledger.jsonl`，每批录入一个 commit，形成不可篡改时间线；MR 相关文件的 git 历史与之交叉核验"卡先于 MR 执行"。
- 论文 §4.3 报告来源分布表（四类来源 × 缺陷机理类的计数），审稿人可由 ledger 复核。

---

## 5. P2 项：最邻近工作差异（进 Related Work §2.3–2.4）

| 邻近族 | 代表性做法 | 与本文的差异（一句话定位） |
|---|---|---|
| Domain-specific / scientific-software mutation | 为数值/HPC 软件定义领域变异算子 | 他们供给**算子**；本文供给**独立认证的缺陷域 + MR 集合充分性准则**，算子只是实现层 |
| Specification mutation | 变异规范/契约以评估 oracle 强度 | 变异对象在 oracle 侧；本文变异程序侧且以独立语义证书准入，评价对象是 MR 集合 |
| Property-based testing 的 adequacy | 属性覆盖/代码覆盖/句法变异评估 property 套件 | 属性≈MR，但其 adequacy 信号要么句法、要么与属性共同设计；缺双盲独立缺陷域与 held-out 决策检验 |
| MR adequacy / MR 质量先前工作 | MR 数量、覆盖、co-designed mutants、MR 优先级 | kill 信号对 MR 设计者可见或由 MR 生成 → 循环；本文以程序性独立 + holdout 消除之，并首次给出决策价值证据 |

检索执行按 CLAUDE.md §7（paper-search-mcp 优先，dblp → arXiv → crossref），每族至少 3–5 篇近五年 + 奠基文献，产出检索审计表。

---

## 6. 旧材料迁移（承接提纲 §10，不重复论证）

提纲 §10 迁移表全盘采纳。本计划的补充执行细则：

- v4 292 变异体：只用于 (i) 功效模拟先验（§3.6）；(ii) 全流程 dry-run 彩排数据（§3.1 I4）。论文中的身份统一写作 "exploratory pilot informing power analysis and protocol rehearsal"。
- 60-cell / 5.14% AST overlap / invariant-flip 分布：按提纲进入 motivation 与 RQ2 的限定性观察。
- Studies 2–4（vendor/attribution/language）与 34-case industrial arm：移出正文，候选为补充材料或后续论文。
- 现有基础设施复用清单：`src/p2/{avp,equiv,stats}`（组级判定、等价估计、统计）、`scripts/cross_source_campaign.py`（改造为盲化执行器）、Cosmic Ray 流水线（S2 句法池）。新增模块：split committer（承诺/加密/解密）、strategy selectors（S1–S4）、holdout custodian、prereg 校验器。

---

## 7. P3 项：写作顺序与章节映射

章节骨架 = 提纲 §8 IMRaD，仅两处结构改动：

1. §4 Method 增 **§4.8' Decision-Value Experiment Design**（承载 §3 全部方案），原 §4.8 Baselines 并入其中；
2. §5 Results 按新 RQ1–RQ5 组织，**§5.3 决策价值为最长小节**；§5.5 baseline/ablation 并入 RQ3/RQ5。

写作顺序（严格后置正文扩写，遵守 EIC P3）：

| 序 | 产出 | 时机 |
|---|---|---|
| W1 | 预注册文档（含 §3.2 全部要素） | Phase 0，实验前 |
| W2 | §3 Formal Framework（提纲 §5–§6 已基本成文，微调符号即可） | 与 Phase 1 并行 |
| W3 | §4 Method（协议照抄预注册，时态改写） | Phase 3 后 |
| W4 | §5 Results | Phase 6 解盲分析后 |
| W5 | §2 Related Work（§5 差异表扩写 + 检索审计） | 与 Phase 4–5 并行 |
| W6 | §1/§6/§7 + Abstract | 全部数字冻结后 |
| W7 | Cover letter + 投稿材料 | 走 CLAUDE.md §3 五步流水线之后 |

写作纪律沿提纲 §12 全条款；另加一条：**凡引用 DVE 数字必须标注 dev/holdout 归属，holdout 数字禁止出现在任何 Phase 6 之前完成的章节草稿里**。

---

## 8. 里程碑与验收门槛

| 里程碑 | 内容 | 验收门槛 |
|---|---|---|
| M0 | 预注册冻结（含 §4.1/4.2 条款、功效模拟、策略伪代码） | tag + SHA-256 记录；ARS 五维扫描通过 |
| M1 | 缺陷池构建 + 认证完成 | **G1**：A–C 认证 ≥ 300，类配额达标，ledger 完整 |
| M2 | dev/holdout 划分承诺 | commitment hash 入库，holdout 加密封存 |
| M3 | \(R_{\mathrm{cand}}\) 冻结 + 原程序 FP 筛查 | 40–60 条，invalid 标记完成，\(R_0\) 选定 |
| M4 | dev 交叉执行 + 句法池执行 + 四策略代码冻结 | \(K_{\mathrm{dev}}\) 冻结；策略输出 hash 封存 |
| M5 | 解盲 + holdout 一次性评估 | salt 公开可验证；primary/secondary endpoint 落数 |
| M6 | 历史缺陷外部臂 + Tier-2 人工臂 | 准入证据审计通过（无 MR-detectability 准入） |
| M7 | 分析 + 初稿（W2–W6） | 提纲 §12 纪律自查 + Devil's Advocate + ARS |
| M8 | 投稿包 | CLAUDE.md §3 五步流水线全绿 |

## 9. 风险登记

| 风险 | 缓解 |
|---|---|
| 认证池达不到 300（认证率低） | 扩 Fault Card 库与 PUT 数；预注册收缩规则（缩类不降标准） |
| \(R_{\mathrm{cand}}\) 同质 → 四策略打平 | 设计阶段强制 generic + domain-specific 两层配额；天花板分析预注册必报 |
| GLMM singular（v4 旧病） | 预注册回退 = PUT-cluster bootstrap，不临场决定 |
| holdout 一次性烧毁（流程 bug 导致无效运行） | I4：全流程先在 pilot 数据彩排；执行器与判定协议在 dev 期已实测 |
| 单作者角色隔离可信度受质疑 | 时间锁 + hash 承诺 + 第二评者（D 级、κ）+ threat 显式披露 |
| LLM 生成候选体隐性携带 MR 知识（训练语料污染） | prompt 隔离审计（生成 prompt 不含任何 MR 文本）+ 该 threat 写入 §6.5 |
| 历史缺陷臂样本过小 | 定位为外部效度佐证而非 primary；描述统计 + CI，如实限定 |

---

## 10. 与 EIC 结论的对齐声明

EIC 判定"这份提纲已经具备 TOSEM 论文的'脑'，缺一项能证明它改变软件测试决策的主实验"。本计划不改动提纲的"脑"（形式框架、术语、双盲协议全部保留），只补上"手"：一项以密码学承诺保证非循环、以算法化同预算策略消除人为混淆、以双层 held-out（新变异体 + 无准入偏倚历史缺陷）承载外部效度的决策价值实验。H-DV 成立则论文进入 EIC 所说的 Major-to-Minor 区间；不成立则按 §3.9 如实降级——两种结局都可发表且都诚实。
