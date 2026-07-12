# 论文初稿计划：MR 集合充分性 × held-out 决策价值主实验（TOSEM 重写）

> **范围更新（2026-07-12）：** 本文档降级为历史 DVE / portfolio-selection 设计与可选扩展实验，不再定义 P3 的确认性核心、论文标题、主 RQ 或贡献排序。P3 v1.2.0 的权威范围基线是 `research/p3-semantic-mutation-core-claims-rqs-v1.2.0.md`。B0/B1 与 held-out 策略只能作为语义变异系统的区分效度或扩展分析，不得取代“算子—等价—得分—真实缺陷一致性”主线。

> 状态：初稿计划 **v1.1.1**（2026-07-10；v1.1 经 EIC round-3 "Conditional Pass to Preregistration" 后小修）
> 上游文档：`research/paper-outline-semantic-mutation-mr-adequacy.md`（论证骨架 v0.1，branch `claude/paper-journal-acceptance-kxpveo` @ 0274196）
> 评审输入：
> - Round-1 EIC quick assessment（P0 = held-out decision-value 实验）
> - Round-2 EIC plan assessment：`docs/review_2026-07-10/r0_eic_round2_plan_assessment.md`
> - Round-3 EIC conditional pass：`docs/review_2026-07-10/r1_eic_round3_prereg_assessment.md`
> - 上一轮编辑决定 P0-1…P0-6：`docs/review_2026-07-10/editorial_decision_prior_round_excerpt.md`
> 前提约束：**忘记已有正文、附录和四项旧实验的叙事结构**；旧数据只按提纲 §10 的迁移决策充当 pilot / 探索性证据；新论文的确认性结论必须全部来自本计划定义的新双盲实验。
> **冻结条款（round-3）**：本版本经 EIC 确认后即冻结预注册；此后除功效模拟决定样本规模外，不再修改 endpoint、family 定义、策略算法、基线层级或结论判定规则。

**v1.1 → v1.1.1 变更摘要**（对应 round-3 四个技术点 + 两项操作性澄清）：

1. 置换检验单位改为 **PUT 级 sign-flip**：先聚合每 PUT 平均策略差 \(d_{p,S}\)，再对 PUT 整体翻转符号；17+ PUT 时精确枚举全部 \(2^{17}\) 种符号配置，无需 Monte Carlo（§3.6）；
2. **family registry 冻结时序修正**：registry 构建 → 边界/fidelity 审计 → registry 冻结 → 划分与承诺；family 合并/拆分只允许发生在划分前；family 嵌套于 PUT（ID = (PUT, mechanism/template cluster)），跨 PUT 同类机理改称 **mechanism class**（§3.3/§4.1/§8）；
3. family 检测 endpoint 改为 **family 内实例检测比例 + family 等权**（primary，统计稳健性最优）；sentinel mutant 判定为 secondary 构念核对；any-instance + family-size sensitivity 进 RQ5（§3.6）；
4. DVE-T 改名 **target-informed leave-PUT-out transfer（S1-T+）**，另增不读取目标机理类分布的 **S1-T0** 作探索性对照，分离"跨程序知识迁移"与"目标缺陷模型信息"的价值（§3.4）；
5. 操作性澄清：\(R_{\mathrm{cand}}\) 明确为 **40–60 个 MR 模板 × 每 PUT 实例化（每 PUT 有效候选 ≥ 12）**；定义 \(R_{\mathrm{valid}}=\{r\in R_{\mathrm{cand}}:\mathrm{AVP}(P,r)=\mathrm{pass}\}\)，四策略一律从 \(R_{\mathrm{valid}}\setminus R_0\) 选择（§3.5）；
6. MID 两级结论规则：统计优势（拒绝 \(H_0:\Delta\le 0\)）与实际重要优势（拒绝 \(H_0:\Delta\le 10\mathrm{pp}\)，即单侧 CI 下界 > MID）分离，仅"点估计超 MID 且相对零显著"不得声称超过 MID（§3.6）。

**v1.0 → v1.1 变更摘要**（对应 round-2 "预注册前必须修改的五点"）：

1. holdout 从变异体级随机划分改为 **Fault Card family 级分组隔离**，并新增 **leave-PUT-out 迁移臂 DVE-T**（§3.4）；
2. 确认性主比较从 "S1 vs 随机" 改为 **S1 vs {经典 MS-guided, MR-coverage-guided} 共同主基线**；随机降为 sanity-check（§3.6）；
3. 功效模拟与推断改为 **PUT × fault-family 两级依赖**结构，主推断用聚类置换/随机化检验（§3.6）；
4. 独立有效性审计从"仅 D 级第二评者"扩展为 **A/B/C/拒绝/未确定/LLM 失败/多效应全分层抽审**（§4.1）；
5. 新增与上一轮 P0-1…P0-6 逐项对应的 **closure ledger**（§11）。
6. 符号修正：全文以 \(M^{\mathrm{cert}}_{\Sigma,B}(P)\)（相对语义规范 \(\Sigma\) 与证据基 \(B\) 的**冻结认证样本**）替代"真实构建 \(M_\Sigma(P)\)"的表述；一切充分性与决策价值主张仅相对该有限、声明、认证的缺陷域成立。

---

## 0. 计划的一句话

在提纲 v0.1 的形式框架之上，本历史版本曾把 EIC 的 P0 要求落成一项**预注册、双盲、family 级 held-out 的 MR 决策价值实验（Decision-Value Experiment, DVE）**：证明（或证伪）“用 SMS/residual faults 指导冻结目录内的 MR portfolio selection，在同等预算下，对**未见过的缺陷机理家族**取得比经典 mutation score 与 MR coverage 指导更高的检测收益”。**该实验在本历史版本中曾被设为确认性核心；自 P3 v1.2.0 起已降级为可选区分效度或扩展分析，不再支配论文身份、主 RQ 或贡献排序。**

**主张范围的自我限定**（round-2 风险 4 的回应）：确认性结论的措辞固定为 *"MR portfolio selection within a frozen candidate catalogue"*，不外推为一般的 MR revision/design 效率；自由设计场景由 Tier-2 臂提供次级证据（§3.7）。

---

## 1. 评审意见 → 计划映射

### 1.1 Round-1 EIC 优先级

| EIC 优先级 | 意见要点 | 本计划的落点 |
|---|---|---|
| **P0** | 执行 held-out decision-value 实验 | §3（主实验 DVE 完整技术方案与论证） |
| **P1** | 冻结独立认证规则：A–C 级进 primary denominator，D 级只进敏感性分析 | §4.1 |
| **P1** | 证明 Fault Card 外部来源 + 时间戳 + 访问隔离记录 | §4.2 |
| **P2** | 最邻近工作差异 | §5 |
| **P3** | 最后再扩写正文、摘要与投稿信 | §7 |

### 1.2 Round-2 预注册前五点 → v1.1 落点

| # | Round-2 要求 | v1.1 落点 |
|---|---|---|
| 1 | holdout 分组隔离（family/模板级）+ leave-PUT-out | §3.4（DVE-W family 级划分；DVE-T 迁移臂） |
| 2 | 最强基线进确认性主比较 | §3.6（S2/S3 共同主基线，Holm 族；S4 sanity） |
| 3 | 两级依赖功效模拟 + 小样本置换推断 | §3.6（功效与推断段） |
| 4 | 分层独立有效性审计 | §4.1（审计分层表 + κ 门槛 + 后果规则） |
| 5 | closure ledger | §11 |
| — | \(M^{\mathrm{cert}}_{\Sigma,B}(P)\) 符号与主张限定 | 全文 + §7 写作纪律 |

### 1.3 Round-3 技术点 → v1.1.1 落点

| # | Round-3 要求 | v1.1.1 落点 |
|---|---|---|
| 1 | PUT 级 sign-flip 置换（唯一统计阻断项） | §3.6 推断段（\(d_{p,S}\) 聚合 + 精确枚举） |
| 2 | family registry 冻结先于划分；family 嵌套于 PUT | §3.3（ID 结构 + mechanism class 术语）、§4.1（审计时序拆分）、§8（M1.5a/M1.5b） |
| 3 | family 检测定义受 size 影响 | §3.6（比例 endpoint primary；sentinel secondary；any-instance 进 RQ5） |
| 4 | DVE-T 非 zero-shot | §3.4（改名 target-informed；增 S1-T0 探索对照） |
| 澄清 1 | R_cand 口径（模板 vs 实例） | §3.5 |
| 澄清 2 | \(R_{\mathrm{valid}}\) 选择空间 | §3.5 |
| 澄清 3 | MID 统计/实际两级结论 | §3.6 |

EIC round-1 指出的三个相互关联的问题，本计划的针对性回答：

1. **"缺陷域只存在于方法定义中"** → §3.3 Phase 1–2 构建冻结认证样本 \(M^{\mathrm{cert}}_{\Sigma,B}(P)\)，设验收门槛 G1。292 个旧变异体按提纲 §10 只作 pilot（功效先验 + 流程彩排），不进任何新 denominator。
2. **"独立认证可能重新引入 oracle problem"** → §3.8 三段论辩护，并规定论文正文以独立小节承载。
3. **"SMS=1 ⟺ U=∅ 是定义性结论"** → 经验主张整体迁移到可证伪的比较性假设 H-DV（§3.6）；定义性等价式只保留为框架性质。

---

## 2. 新论文的贡献与 RQ 重组

### 2.1 贡献收敛（在提纲 §9 三条之上增加第四条并调序）

1. **C1 概念与兼容性**：语义规范、Fault Card、认证语义变异体、SMS，作为经典 mutation-score 结构的保守扩展；SMS 的标量形式明确声明继承 classical MS（上轮 P0-1 的重定位要求），新颖性在缺陷域、独立性协议和充分性解释。
2. **C2 MT 充分性准则**：组级 MR verdict、kill、残余缺陷集、相对充分性——一切相对 \(M^{\mathrm{cert}}_{\Sigma,B}(P)\)。
3. **C3 双盲构建协议**：MR-free 缺陷构造、independent certification、freeze-before-crossing。
4. **C4 决策价值证据（headline）**：预注册 held-out 实验证明 residual-guided portfolio selection 相对最强现有指导信号的检测收益（或如实报告无收益并降级为诊断框架）。

### 2.2 RQ 重组

| 新编号 | 内容 | 性质 | 对应提纲 |
|---|---|---|---|
| RQ1 | 构造性：能否 MR-free 地构造并独立认证 \(M^{\mathrm{cert}}_{\Sigma,B}(P)\)？ | 构造性 | 原 RQ1 |
| RQ2 | 区别性：语义缺陷域与句法缺陷域的机理/覆盖差异 | 描述性 | 原 RQ2 |
| RQ3 | **决策价值：residual-guided 选择是否在 family 级 held-out 缺陷上优于 MS-guided 与 coverage-guided？** | **确认性（预注册主检验）** | 新增（EIC P0） |
| RQ4 | 充分性诊断：冻结 MR 集合对声明缺陷域的 SMS、残余缺陷结构 | 诊断性 | 原 RQ3 |
| RQ5 | 判定与结论稳健性：样本、容差、证据等级、预算、划分粒度的敏感性 | 稳健性 | 原 RQ4 + 扩展 |

原 H2（严格充分性 SMS=1）不作 headline：对 \(R_0\) 大概率被证伪（这正是 residual faults 存在、S1 有事可做的前提），作为 RQ4 诊断结果如实报告。

---

## 3. 主实验 DVE：技术方案与论证（P0，本计划的核心）

### 3.1 设计总览

两阶段、双盲、family 级 held-out、四策略、同预算，外加一个 leave-PUT-out 迁移臂：

```
Phase 0  角色冻结 + 预注册                    （§3.2）
Phase 1  双盲语义缺陷池构建 + 独立认证 + 分层审计（§3.3，分支 A，MR-free）
Phase 2  family 级 dev/holdout 划分 + 密码学承诺 + PUT 级保留（§3.4）
Phase 3  MR 候选目录 R_cand 独立构建           （§3.5，分支 B，mutant-free）
Phase 4  开发期交叉执行（R_cand × M_dev + 句法池）
Phase 5  四策略同预算选择（算法化，代码冻结）
Phase 6  解盲：holdout 一次性评估（DVE-W + DVE-T + 历史缺陷外部臂）
```

关键不变量（写入预注册，违反即实验作废）：

- **I1 独立性**：缺陷池构建全程不可见任何 MR 定义、实现、结果（提纲定义 6 角色访问矩阵照搬执行）。
- **I2 非循环性**：SMS/residual 信号只允许来自 \(M_{\mathrm{dev}}\)；四个策略以**冻结代码**形式在解盲前定稿（commit hash 封存）；holdout 在全部策略输出之后才解密。
- **I3 同预算**：所有策略在同一决策空间（同一 \(R_{\mathrm{cand}}\)）与相同预算 \(k\) 下比较；预算的完整成本核算（构造/执行/维护）作为 secondary 视角报告，确认性结论范围限定为目录内 portfolio selection。
- **I4 一次性**：holdout 只打开一次；全流程先在 pilot 数据上彩排（dry-run），再对真 holdout 执行。
- **I5 机理隔离（v1.1 新增）**：同一 Fault Card family 的任何实例不得跨 dev/holdout；"未见过"以缺陷机理家族为单位定义，不以变异体实例为单位。

### 3.2 Phase 0：对象、角色与预注册

**PUT 集合**：现有 12 个科学计算 PUT（`src/p2/puts/`）作为主载体（程序本身未被污染；污染在旧 mutant/MR 共同设计史，对策是全部材料重新冻结 + 新盲化角色），另招募 **8–12 个新 PUT**（v1.1 上调，服务两级依赖下的功效），选自带可考历史缺陷的开源科学计算内核（SciPy/NumPy/statsmodels 类）。其中 **2–3 个新 PUT 整体保留为 DVE-T 迁移臂**（§3.4），其余进入主实验并承担历史缺陷外部臂。PUT 选择标准沿提纲 §4.2。

**角色隔离**：变异生成者、语义认证者、MR 设计者、执行器、holdout 托管者（custodian）、解盲分析者。单作者现实下的操作化：时间锁 + 独立 git 分支 + hash 承诺实现程序性隔离；**独立审计（§4.1）与 D 级裁决必须由第二评者执行**；"同一人分时扮演多角色"作为 threat 显式披露。

**预注册内容**（`docs/prereg/DVE_prereg_v1.md`，冻结时打 tag + SHA-256；可选同步 OSF）：假设族 H-DV/H1'/H3'、primary endpoint、预算 \(k^\*\)、两级依赖功效模拟、聚类置换检验方案与 α、效应量与 MID、认证规则与审计分层方案（§4.1）、策略算法伪代码、family 划分规则与承诺机制、DVE-T 迁移策略定义、停止规则、null 结果解释规则（§3.9）、协议偏离披露模板。

### 3.3 Phase 1：双盲缺陷池（构建 \(M^{\mathrm{cert}}_{\Sigma,B}(P)\)）

流程沿提纲 §7.2，本计划的增量约束：

- **来源约束（P1）**：Fault Card 只允许四类外部来源——需求/领域约束文档、算法规范、历史缺陷（issue/commit URL）、FMEA。每张卡带 `prov` 字段（来源类型、可解引用出处、时间戳、录入角色）。LLM 可辅助起草但必须回溯锚定到四类来源之一。
- **Fault Card family（v1.1 新增，划分单位；v1.1.1 明确嵌套结构）**：录入时即为每张卡指派 family ID——同一来源条目、同一缺陷机理、同一变异模板或同一历史缺陷家族衍生的所有卡与其全部变异体实例构成一个 family。**family 严格嵌套于 PUT**：ID 结构为 `(PUT, mechanism/template cluster)`，与统计模型的 mutant ⊂ family ⊂ PUT 层级一致；跨 PUT 的同类缺陷机理称为 **mechanism class**（用于分层配额与 DVE-T 迁移映射），不是同一个 family。family 指派规则在预注册中定义并在生成前冻结；registry 的边界审计与冻结时序见 §4.1（任何 family 合并/拆分必须发生在 dev/holdout 划分之前）。
- **认证等级门槛（P1）**：A–C 级证书进 primary denominator；D 级单独成池只进 RQ5 敏感性。规则 Phase 0 冻结（§4.1）。
- **规模目标（v1.1.1 修订，已由真实功效模拟反推冻结）**：以 **family 为计数单位**。执行 `scripts/dve/power_simulation.py`（结果 `data/dve/power_simulation_results.json`；type-I 校准均值 0.0508 @ 名义 0.05）后确定——MID=0.10 时 80% 功效在保守情形（σ=0.25, ICC=0.3）需 **80 个 holdout family**，即 20 PUT × 4；50:50 划分后 **总认证 family ≥ 160**（dev+holdout），对应认证变异体预计 500–800。若 M1 后由 dev 侧估得 σ ≤ 0.20，holdout 目标可一次性下调至 40–48（总 ≥ 80–96）并披露。每缺陷机理大类仍要求 ≥ 10 个 family。详见 `docs/prereg/DVE_prereg_v1.md` §4。
- **验收门槛 G1**：A–C family 数、类配额、认证率、审计通过率（§4.1）达标才进 Phase 2；不达标触发预注册范围收缩规则（缩类不降标准）。

### 3.4 Phase 2：family 级划分、密码学承诺与 PUT 级保留（v1.1 重写）

**DVE-W（主臂，within-PUT、cross-family）**：

- 划分单位是 **Fault Card family**，不是变异体：每个 family 的全部实例整体进 dev 或整体进 holdout。同一模板、同一历史缺陷家族、补丁相似（预注册的 AST 相似度阈值复核）的实例永不跨侧。
- 划分时点：任何 MR 交叉执行之前。分层维度：PUT × 缺陷机理大类 × 证书等级众数；比例 family 数 50:50；随机种子预注册。
- 承诺机制：holdout family ID 列表 + salt 的 SHA-256 写入 git（timestamped commit + tag）；holdout 变异体 diff 加密存放，custodian 时间锁持钥；解密条件 = 四策略输出以 commit hash 封存完毕。解盲后公开 salt 供第三方验证。审计产物 `data/dve/split_commitment.json`。

**DVE-T（target-informed leave-PUT-out transfer 臂；v1.1.1 更名并分解）**：

- 2–3 个新 PUT 整体保留：其全部认证变异体（所有 family）均为 holdout，无 dev 池。
- **S1-T+（target-informed，secondary confirmatory）**：只允许读取 (i) dev PUT 们的 kill matrix 与残余缺陷的 mechanism-class 标签，(ii) 目标 PUT 的 Fault Card **mechanism-class 分布**（卡的存在性与类别，非变异体、非 kill 结果）——据此把"mechanism class → MR 模板覆盖"映射迁移到目标 PUT 的候选选择。**命名如实**：该臂支持的主张是 *target-informed cross-program transfer*，不是 zero-shot transfer——它未见目标变异体与 kill 结果，但获得了目标缺陷域的分布信息，论文措辞按此限定。
- **S1-T0（distribution-blind，exploratory）**：与 S1-T+ 同构，但**不读取**目标 PUT 的 Fault Card 分布，仅用 dev PUT 上学到的 mechanism-class→模板映射按 dev 侧频率迁移。与 S1-T+ 共同报告，用于分离"跨程序知识迁移"与"目标缺陷模型信息"两种价值来源；执行成本仅为多一组选定 MR 的 holdout 运行。
- 基线对照：S2-T 用目标 PUT 自身的句法变异池信号（句法池不属于保密对象）；S3-T 用目标 PUT 的覆盖度量；S4-T 随机。
- 作用：检验指导信号是否携带**跨程序**的决策价值，直接回应"holdout 变异体与训练池同分布"的解读风险。DVE-T 为确认性 **secondary** endpoint（主臂 DVE-W 为 primary），两臂结论合并解释规则见 §3.9。

**论证**：family 级隔离使"未见过"升级为"未见过的缺陷机理家族"；PUT 级保留使其进一步升级为"未见过的程序（target-informed 意义下）"。两层加上密码学承诺，把 round-2 风险 1 从设计层关闭。

### 3.5 Phase 3：MR 候选目录 \(R_{\mathrm{cand}}\) 与初始集 \(R_0\)

- **目录口径（v1.1.1 澄清）**：MR 设计者只读 \(P,\Sigma\) 与 MT 文献，产出 **40–60 个 MR 模板**（generic + 领域特定两层，类别配额预注册）；每个模板对适用的 PUT 逐一实例化，每条实例按提纲定义 7 冻结 \((T_r,\rho_r,A_r,G_r,\Theta_r)\)。**选择在 PUT 级实例空间进行**：每 PUT 的有效候选实例数必须 ≥ 12（可行性由模板可适用性矩阵在冻结前核验），以支撑 \(k^\*=4\) 的选择空间；总实例量预计 250–400。
- **有效选择空间（v1.1.1 澄清）**：原程序 false-positive 筛查（提纲命题 3）后，定义
  \[
  R_{\mathrm{valid}}(P)=\{r\in R_{\mathrm{cand}}(P):\mathrm{AVP}(P,r)=\mathrm{pass}\},
  \]
  invalid MR **从选择空间中删除**（不只是"保留但不产生 kill"）；四策略一律从 \(R_{\mathrm{valid}}(P)\setminus R_0(P)\) 中选择。每 PUT 的 ≥ 12 候选门槛以 \(R_{\mathrm{valid}}\) 计。
- \(R_0\)：按预注册启发式（每 PUT 取文献最常用 generic MR \(k_0\) 条，且 \(R_0\subseteq R_{\mathrm{valid}}\)）在任何变异体执行前选定，制造"已有普通 MR 集合，接下来加哪几条"的真实决策场景。

**关键设计决策——为什么主实验用"目录内选择"而不是"自由人工 revision"**（v1.0 论证保留，主张范围按 round-2 收紧）：

1. **消除人的技能混淆**：算法化选择使唯一自变量就是指导信号（SMS vs MS vs coverage）。
2. **同预算可精确定义**：目录内选择使 \(k\) 条 MR 的预算逐条可比；同时 v1.1 增加 secondary 成本核算——每策略报告所选 MR 的执行时长、样本量与（对 Tier-2）设计工时，避免"同预算=同条数"的简化被误读。
3. **完全可复现**：策略是确定性代码（随机臂给定种子）。
4. **主张范围相应限定**：确认性结论只覆盖 frozen-catalogue portfolio selection；自由 revision 的端到端收益由 Tier-2 臂（§3.7）作次级证据。

### 3.6 Phase 4–6：策略定义、endpoint 与统计方案（v1.1 重写主比较与推断）

**四策略**（同一决策空间 \(R_{\mathrm{valid}}(P)\setminus R_0(P)\)，同预算 \(k\)，全部算法化，代码冻结）：

| 策略 | 指导信号 | 算法 |
|---|---|---|
| S1 residual-guided（treatment） | \(K_{\mathrm{dev}}\) 中 \(U(R_0,M_{\mathrm{dev}})\) 的覆盖 | 贪心 set-cover（按 family 计覆盖增量，防同 family 实例重复计分）；平局按执行成本 |
| S2 classical-MS-guided（**共同主基线**） | 句法变异池（Cosmic Ray 默认一阶算子，配置冻结）对 \(R_0\) 的存活句法变异体覆盖 | 与 S1 同构贪心 |
| S3 MR-coverage-guided（**共同主基线**） | 预注册 MR 覆盖度量（输入变换类别覆盖 + follow-up 代码覆盖），不用变异体信息 | 贪心最大化覆盖增量 |
| S4 random / generic（**sanity-check**） | 无信号 | 随机 \(k\) 条 ×1000 重抽 + 固定 generic 参照 |

**M-infra dry-run 反馈的三条设计修订（v1.1.1，`docs/dve/M_infra_dry_run.md`）**：端到端 I4 彩排（`scripts/dve/dry_run_pipeline.py`）在合成世界上暴露三个混淆并已回灌——

1. **potency 混淆**：S1 天然选中宽 profile 强力 MR，S1-vs-S3（coverage 不针对 kill）的差含 potency 成分。**S1-vs-S2（kill 信号 vs kill 信号）升为决定性确认比较**；S1-vs-S3 保留但预注册其 potency+transfer 混合解释。
2. **对照须 coverage-matched**：确认性决策价值 estimand 的对照须"挑 k 个不同的非 R0 类"（与 S1 同样避开 R0 冗余），而非朴素随机；朴素随机仅作 S4 sanity 下界。因"residual"按定义相对 R0，朴素随机对照会把覆盖多样化误算成 transfer 收益（dry-run 实测 transfer=0 时 Δ≈+0.13）。
3. **per-PUT 选择是 sign-flip 有效性前提**：全局共用组合会使各 PUT 的 d_p 同号相关、type-I 膨胀至 ≈0.17；计划 §3.5 的逐 PUT `R_valid(P)\R_0(P)` 选择由此获得经验证成（per-PUT 恢复后 type-I 回落至 0.044）。

**Primary endpoint（DVE-W；v1.1.1 改为 size 不敏感定义）**：对 holdout family \(g\)（实例集 \(I_g\)），定义 **family 检测分数**为实例检测比例

\[
\mathrm{det}(R,g)=\frac{1}{|I_g|}\sum_{m\in I_g}\mathrm{det}_R(m)\in[0,1],
\]

family 等权聚合为 \(\mathrm{FDS}(R)=\frac{1}{|G|}\sum_{g\in G}\mathrm{det}(R,g)\)（family detection score）。primary 对比量：

\[
\Delta_{S1,S}=\mathrm{FDS}(R_0\cup S_1(k^\*))-\mathrm{FDS}(R_0\cup S(k^\*)),\quad S\in\{S2,S3\}.
\]

选择比例定义的理由：any-instance（"任一实例被杀死即 detected"）使实例多的 family 更易判为 detected，检测率随 family size 膨胀；比例 + family 等权对 size 不敏感且统计上最稳健。两个预注册伴随定义：(i) **sentinel 判定**（每 family 在划分承诺时随机冻结一个 sentinel mutant，\(\mathrm{det}(R,g)=\mathrm{det}_R(m_g^{\mathrm{sent}})\)）作为 secondary 构念核对——它对应"该机理至少有一个可观察见证"的理论解释；(ii) any-instance 定义 + family-size sensitivity 进 RQ5。三个定义的 verdict 一致性本身作为稳健性证据报告。

**预注册假设**：

- **H-DV（primary，确认性，共同基线族）**：\(\Delta_{S1,S2}>0\) **且** \(\Delta_{S1,S3}>0\)（Holm 校正，两者都成立 = 完全确认；只有其一 = 部分确认，结论措辞预注册分级）。
- **MID 两级结论规则（v1.1.1）**：区分两类主张并分别检验——(a) **统计优势**：拒绝 \(H_0:\Delta\le 0\)；(b) **实际重要优势**：拒绝 \(H_0:\Delta\le\mathrm{MID}\)（等价于单侧置信下界 > MID；MID 拟 10 个百分点 FDS 级，功效模拟后冻结）。论文措辞对应三档：仅 (a) 成立 = "statistically superior"；(a)+(b) 成立 = "superior by a practically important margin"；点估计超 MID 但 (b) 不成立时**禁止**声称超过 MID，写作 "point estimate exceeds the MID but practical importance is not confirmed"。
- **H-DV-T（secondary，确认性）**：DVE-T 臂上 S1-T 对 S2-T/S3-T 的同型差 > 0。
- **Sanity**：S1 显著超过 S4 随机分布的预注册分位数（如 90%）；不满足则整个信号体系存疑，触发 §3.9 失败分析。
- **H1'（区别性）**：沿提纲 RQ2 度量。
- **H3'（稳健性）**：H-DV verdict 在证书等级（±D）、容差、\(k\in\{2,4,6,8\}\) 扫描、family 划分规则敏感性（预注册的备选 family 定义重划分）下不翻转。

**统计推断（v1.1 重写，两级依赖）**：

- 依赖结构：变异体 ⊂ fault family ⊂ PUT。**有效独立单位按 family 与 PUT 计，不按变异体计。**
- Primary 检验（v1.1.1 修正为 **PUT 级 sign-flip**）：先在每个 PUT \(p\) 内把全部 holdout family 的配对差聚合为该 PUT 的平均策略差

  \[
  d_{p,S}=\frac{1}{|G_p|}\sum_{g\in G_p}\left[\mathrm{det}(R_0\cup S_1(k^\*),g)-\mathrm{det}(R_0\cup S(k^\*),g)\right],
  \]

  然后把**一个 PUT 内的全部观测作为整体**对 \(d_{p,S}\) 做 PUT 级 sign-flip 随机化检验，检验统计量为 \(\bar d_S=\frac{1}{|P|}\sum_p d_{p,S}\)（PUT 等权）。主实验 PUT ≥ 17 时**精确枚举**全部 \(2^{|P|}\)（如 \(2^{17}=131{,}072\)）种符号配置，不用 Monte Carlo 近似；Holm 校正 {S1 vs S2, S1 vs S3}。这样即使同一 PUT 内 family 相关，交换单位也是独立的 PUT 整体，构成严格的 cluster randomization test（round-3 技术点 1；v1.1 的"PUT 内 family 级 sign-flip"作废）。MID 层检验（\(H_0:\Delta\le\mathrm{MID}\)）用同一 sign-flip 框架对移位统计量 \(\bar d_S-\mathrm{MID}\) 执行。
- 效应量与 CI：family 级 risk difference，**两级 bootstrap**（先重抽 PUT，再抽 PUT 内 family，BCa）。
- GLMM（det ~ strategy + (1|PUT) + (1|family)）作为 secondary，预注册 singular-fit 回退 = 上述置换/bootstrap（v4 旧病不再临场决定）。
- **功效模拟（v1.1 重写）**：生成模型含 PUT 级与 family 级随机效应（ICC 先验各取 0.1–0.3 网格），参数先验来自 v4 pilot kill 率；模拟 family 检测基线率 0.4–0.7、MID=10pp 下 80% 功效所需 (PUT 数, holdout family 数) 组合。初步判断指向 ≥ 17 个主实验 PUT × ≥ 40 个 holdout family（故 §3.3 目标 ≥ 80 family、PUT 扩到 20 上下）；模拟脚本与全部假设进预注册附件，数字以冻结版为准。
- 成本 secondary endpoint：每新检出 holdout family 的执行成本；\(k\) 扫描与成本归一化视角进 RQ5。

### 3.7 外部验证臂与 Tier-2 人工臂

- **历史缺陷臂**：从新 PUT 上游仓库提取历史缺陷（bug-fix commit 反向应用），准入条件**只有**认证证据（C 级），**明确禁止**以 MR-detectability 为准入条件。对全部策略 held-out；历史缺陷按上游 issue 家族归 family。样本量预期小（10–30 family），只作外部效度佐证，描述统计 + CI 呈现。
- **Tier-2 人工 revision 臂**：盲化 MR 工程师凭 dev residual Fault Cards 自由设计 ≤ \(k^\*\) 条新 MR（工时记录），在 DVE-W/T 两层 holdout 上评估；生态效度次级证据，不进 primary。

### 3.8 对"oracle problem 重新引入"的正面辩护（进论文正文）

（v1.0 内容保留）论文在 §3.3 末或 §6.2 用独立小节回答"既然有足够强的 oracle 证明程序错误，为什么还需要 MT"：

1. **对象不同**：证书 \(\kappa\) 认证的是实验仪器（denominator 中每个缺陷构造确实违反 \(\Sigma\)），一次性、离线、每缺陷一个见证输入；MT 面向任意生产输入的持续测试。
2. **成本不对称**：A/B 级证据只需对少量见证点成立；把它们变成逐输入运行时 oracle 需要参考实现全域可用可信——正是 MT 回避的前提。
3. **部署形态**：SMS-guided 实践消费缺陷模型与 kill matrix，不要求使用者拥有证书级 oracle；证书只出现在方法学评价中。
4. 类比锚点：mutation testing 评价测试套件同样依赖"已知缺陷注入"的实验室特权。

### 3.9 Null 结果与失败模式的预注册解释规则

- H-DV 完全不成立（对 S2、S3 均无收益）：如实降级为"SMS 是诊断框架，未证明选择收益"，Discussion 分析机制；不换 endpoint/预算/denominator。
- 部分确认（仅胜其一）：按预注册分级措辞（如"优于 coverage 启发但未证明优于经典 MS 指导"）。
- DVE-W 成立但 DVE-T 不成立：结论限定为 within-program 决策价值，跨程序迁移列为 open problem——不得把 DVE-W 结果外推为一般化主张。
- Sanity 失败（S1 不敌随机分布高分位）：整个信号链失败分析（目录同质？dev 信号噪声？family 划分错误？），全部如实报告。
- 天花板分析（全体 \(R_{\mathrm{valid}}\) 在 holdout 上的最大 FDS）预注册为必报项；天花板过低（< 0.5）作为重要负结果 + residual 结构分析。
- 认证池不达 G1：按预注册收缩规则缩类，不降标准。

### 3.10 主实验方案自查：EIC 质疑逐条对照

| 质疑 | 机制回答 |
|---|---|
| 独立性 | 分支 A 全程 MR 不可见（角色矩阵 + provenance ledger + git 时序）；§3.3 |
| 非循环性 | SMS 信号限于 dev；策略代码冻结先于解盲；holdout 密码学承诺；§3.4/3.6 |
| 外部效度 | family 级隔离 + leave-PUT-out 迁移臂 + 无准入偏倚历史缺陷臂；§3.4/3.7 |
| 决策价值 | endpoint 是"加哪 k 条 MR"在未见缺陷机理上的收益，主对照 = 最强现有信号（MS、coverage）；§3.6 |
| 同分布人工变异体（round-2 风险 1） | family 隔离 + DVE-T + 历史缺陷臂三层递进；§3.4 |
| 弱基线（round-2 风险 2） | S2/S3 共同主基线，S4 仅 sanity；§3.6 |
| 伪功效（round-2 风险 3） | family/PUT 两级功效模拟 + 聚类置换推断；§3.6 |
| 预算口径（round-2 风险 4） | 主张限定为 frozen-catalogue portfolio selection + secondary 成本核算；§0/§3.5 |

---

## 4. P1 项：认证规则冻结与分层独立审计

### 4.1 认证规则与独立有效性审计（v1.1 大幅扩展，round-2 要求 4）

**规则冻结**（进预注册 §"Certification Rules"）：

- 证据等级表沿提纲 §7.3；A/B/C → primary denominator；D → sensitivity-only；"不准入"行照抄（仅 LLM/作者意图、或仅被某 MR 杀死的候选体永不进任何 denominator）。
- \(\widehat{\mathrm{Eq}}_{\Sigma,B,\tau}\) 的样本量、参考 oracle、容差 Phase 0 冻结；敏感性进 RQ5。
- 冻结后任何变更 = 协议偏离，论文 Deviations 小节披露。

**分层独立审计**（第二评者/领域专家执行，不再限于 D 级）：

| 审计层 | 抽样 | 审计内容 |
|---|---|---|
| A 级证书 | 全数或 ≥ 20 | 解析论证/误差表达式正确性复核 |
| B 级证书 | 每 PUT 分层抽 ≥ 15% 且 ≥ 20 | 参考 oracle 执行正确性**重跑**、见证输入可复现性 |
| C 级证书 | 全数 | 历史缺陷出处、补丁反向应用保真度 |
| REJECTED（拒绝候选） | 分层抽 ≥ 15% | 拒绝理由是否成立（防过度拒绝造成缺陷域塑形） |
| UNCERTAIN（未确定） | 全数 | 处置去向（不得默默滑入任何池） |
| LLM 生成失败/畸变 | 抽 ≥ 20 | 失败模式分类、是否泄漏 MR 知识（prompt 隔离核验） |
| 多效应对象 | 全数 | 多标签集合与 Fault Card 单一修改约束一致性 |
| Fault Card fidelity | 每 family 抽 1 实例 | 变异体是否忠实实现卡声明的编辑；family 边界指派正确性 |

- 每层报告一致率/κ；预注册阈值（拟 κ ≥ 0.6 或一致率 ≥ 0.9，冻结时定）；不达标 → 该层整体复审，仍不达标 → 相关对象降出 primary denominator 并披露。
- **审计时序（v1.1.1 修正，消除与划分的冲突）**，分两段：
  1. **划分前（改变 family 边界的审计）**：family registry 构建 → 第二评者完成 **family-boundary + Fault Card fidelity 审计**（上表最后一行）→ 处理全部合并/拆分 → **registry 冻结** → 才允许 dev/holdout 随机划分与承诺（§3.4）。任何 family 合并/拆分在划分后一律禁止。
  2. **划分后、解盲前（不改变 family 边界的审计）**：证书正确性复核各层（A/B/C 重跑、REJECTED、UNCERTAIN、LLM、多效应）可在划分承诺后进行，审计者不知 dev/holdout 归属（防审计塑形）；其结论只能整体升降对象的池归属（primary ↔ sensitivity），不能改动 family 结构。
- 产出：`docs/dve/certification_audit_report.md` + label-conditioned 敏感性表（论文 RQ5 报告审计前后 headline 数字差）。

### 4.2 Fault Card 外部来源证明（provenance ledger）

（v1.0 内容保留）`prov` 必填四元组；append-only JSONL 存 `data/dve/fault_card_ledger.jsonl`，逐批 commit 形成时间线；与 MR 文件 git 历史交叉核验"卡先于 MR 执行"；论文 §4.3 报告来源分布表。v1.1 增补：ledger 每条记录 family ID，family 指派变更同样 append-only。

---

## 5. P2 项：最邻近工作差异（进 Related Work §2.3–2.4）

| 邻近族 | 代表性做法 | 差异定位 |
|---|---|---|
| Domain-specific / scientific-software mutation | 为数值/HPC 软件定义领域变异算子 | 他们供给算子；本文供给独立认证的缺陷域 + MR 集合充分性准则 + 决策价值证据 |
| Specification mutation | 变异规范/契约评估 oracle 强度 | 变异对象在 oracle 侧；本文变异程序侧且独立语义证书准入 |
| Property-based testing 的 adequacy | 属性覆盖/代码覆盖/句法变异评估 property 套件 | 缺双盲独立缺陷域与 held-out 决策检验 |
| MR adequacy / MR 质量先前工作 | MR 数量、覆盖、co-designed mutants、优先级 | kill 信号对 MR 设计者可见或由 MR 生成 → 循环；本文以程序性独立 + family 级 holdout 消除 |

检索按 CLAUDE.md §7（paper-search-mcp 优先），每族 3–5 篇近五年 + 奠基文献，产出检索审计表。

---

## 6. 旧材料迁移（承接提纲 §10）

提纲 §10 迁移表全盘采纳。补充执行细则：

- v4 292 变异体：仅用于功效模拟先验与全流程 dry-run 彩排；论文身份 = "exploratory pilot informing power analysis and protocol rehearsal"。
- 60-cell / 5.14% AST overlap / invariant-flip 分布：进 motivation 与 RQ2 限定性观察；invariant-flip 三分层（170/93/29）正是上轮 P0-1 的证据，作为"为什么需要认证准入协议"的动机在 §1/§4 引用。
- Studies 2–4 与 34-case industrial arm：移出正文（上轮 P0-3 的处置），候选补充材料或后续论文；若在正文任何位置提及，必须带 exploratory/selection-conditioned 限定词。
- 基础设施复用：`src/p2/{avp,equiv,stats}`、`scripts/cross_source_campaign.py`（改造为盲化执行器）、Cosmic Ray 流水线（S2 句法池）。新增模块：family registry、split committer（承诺/加密/解密）、strategy selectors（S1–S4 + T 变体）、holdout custodian、审计抽样器、prereg 校验器。

---

## 7. P3 项：写作顺序与章节映射

章节骨架 = 提纲 §8 IMRaD，改动：

1. §4 Method 增 **§4.8' Decision-Value Experiment Design**（承载 §3 全部方案），原 §4.8 Baselines 并入；
2. §5 Results 按新 RQ1–RQ5 组织，§5.3 决策价值为最长小节；
3. §6 Discussion 增 oracle-problem 辩护小节与主张范围小节（frozen-catalogue portfolio selection 的边界）。

写作顺序（严格后置正文扩写）：

| 序 | 产出 | 时机 |
|---|---|---|
| W1 | 预注册文档 | Phase 0，实验前 |
| W2 | §3 Formal Framework（含 \(M^{\mathrm{cert}}_{\Sigma,B}\) 符号 + 独立形式审计闭环） | 与 Phase 1 并行 |
| W3 | §4 Method（协议照抄预注册改时态） | Phase 3 后 |
| W4 | §5 Results | Phase 6 解盲分析后 |
| W5 | §2 Related Work | 与 Phase 4–5 并行 |
| W6 | §1/§6/§7 + Abstract | 数字冻结后 |
| W7 | Cover letter + 投稿材料（§11 P0-6 清单逐项） | CLAUDE.md §3 五步流水线后 |

写作纪律沿提纲 §12 全条款，另加三条：

- 凡引用 DVE 数字必须标注 dev/holdout 归属；holdout 数字禁止出现在 Phase 6 之前完成的章节草稿里。
- 全文统一 \(M^{\mathrm{cert}}_{\Sigma,B}(P)\)；不得出现"穷尽/全部语义缺陷"式措辞；充分性与决策价值主张一律带"相对声明认证缺陷域"限定。
- 确认性结论措辞固定为 frozen-catalogue MR portfolio selection，不得升格为一般 MR design/revision 效率。

---

## 8. 里程碑与验收门槛（v1.1 修订）

| 里程碑 | 内容 | 验收门槛 |
|---|---|---|
| M0 | 预注册冻结（含两级功效模拟、审计分层方案、family 规则、策略伪代码） | tag + SHA-256；ARS 五维扫描通过 |
| M0.5 | **独立形式审计**：框架定义/命题（提纲 §5–§6）由外部形式方法/软件测试研究者逐条复核 | 审计意见闭环（上轮 P0-2 验收标准） |
| M1 | 缺陷池构建 + 认证完成 | **G1**：A–C family ≥ 80、类配额达标、ledger 完整 |
| M1.5a | **family-boundary + fidelity 审计 → registry 冻结**（§4.1 时序段 1） | 边界层 κ 过阈值；合并/拆分清零后 registry hash 冻结 |
| M2 | family 级 dev/holdout 划分承诺 + DVE-T PUT 封存 + sentinel 冻结 | commitment hash 入库，holdout 加密封存 |
| M2.5 | **证书分层审计**（§4.1 时序段 2，划分后、盲于归属） | 各层 κ/一致率过阈值；审计报告落盘 |
| M3 | \(R_{\mathrm{cand}}\) 冻结 + 原程序 FP 筛查（\(R_{\mathrm{valid}}\) 定型）+ \(R_0\) 选定 | 40–60 模板，每 PUT 有效实例 ≥ 12 |
| M4 | dev 交叉执行 + 句法池执行 + 四策略（含 T 变体）代码冻结 | \(K_{\mathrm{dev}}\) 冻结；策略输出 hash 封存 |
| M5 | 解盲 + holdout 一次性评估（DVE-W/T + 历史缺陷臂 + Tier-2） | salt 公开可验证；endpoint 落数 |
| M6 | 分析 + 初稿（W2–W6） | 提纲 §12 + §7 新增纪律自查 + DA + ARS |
| M7 | **closure ledger 终验**（§11 全行闭合） | 每行状态 = closed 或 explicitly-deferred + 理由 |
| M8 | 投稿包 | CLAUDE.md §3 五步流水线全绿 + §11 P0-6 行逐项勾销 |

## 9. 风险登记（v1.1 增补）

| 风险 | 缓解 |
|---|---|
| 认证 family 达不到 80 | 扩卡库与 PUT 数；预注册收缩规则（缩类不降标准） |
| \(R_{\mathrm{cand}}\) 同质 → 策略打平 | generic + domain-specific 配额；天花板分析必报 |
| S1 须同时胜 S2 和 S3，确认门槛高 | 预注册分级结论措辞（完全/部分确认），部分确认仍可发表且诚实 |
| DVE-T 迁移信号太弱 | 定位为 secondary；失败时按 §3.9 限定 within-program 主张 |
| PUT 数不足致置换检验分辨率低 | PUT 扩至 20 上下；PUT 等权统计量；功效模拟先行把关 |
| GLMM singular | 预注册回退 = 聚类置换/两级 bootstrap |
| holdout 一次性烧毁 | I4 彩排；执行器与判定协议 dev 期实测 |
| 单作者角色隔离可信度 | 时间锁 + hash 承诺 + 第二评者审计（§4.1）+ threat 披露 |
| LLM 生成候选体隐性携带 MR 知识 | prompt 隔离审计（§4.1 LLM 层）+ threat 写入 §6.5 |
| 审计发现某层系统性失效 | 预注册后果规则：层级降出 primary + label-conditioned 敏感性报告 |
| 历史缺陷臂样本过小 | 外部效度佐证定位；描述统计 + CI |

---

## 10. 与 EIC 结论的对齐声明

Round-2 EIC 判定本方案"回应设计 8/10、实际关闭 3/10"，并给出预注册前五点。v1.1 已在设计层落实全部五点（§1.2 映射）；实际关闭程度只能靠执行推进——M0–M8 的每个验收门槛就是把 3/10 逐步推向闭合的路径。两种实验结局（H-DV 成立/不成立）都预注册了诚实的发表路径。

---

## 11. Closure Ledger：上一轮 P0-1…P0-6 逐项对应（round-2 要求 5）

> 原意见全文见 `docs/review_2026-07-10/editorial_decision_prior_round_excerpt.md`。
> 状态取值：`design-closed`（方案层已关闭，待执行验证）/ `open`（尚未安排）/ `closed`（证据落地）。当前无一行达到 `closed`——这是诚实状态：执行前不宣称关闭。

### P0-1 denominator 与构念不一致

- **原意见**：定义要求 S3 witness，实际 292 池含 170 零翻转；三个 denominator 给出三个 δ；certified denominator 使 6/12 PUT 消失。
- **修改位置**：本计划 §3.3（\(M^{\mathrm{cert}}_{\Sigma,B}\) 单一 primary denominator，A–C 准入）、§2.1-C1（SMS 标量形式明确继承 classical MS，采纳上轮"推荐重定位方案"+ 新证据走"更强验证方案"双轨：重定位负责表述，新池负责证据）、提纲 §12（non-estimable 条款）。
- **新证据**：待 M1 产出（新池 + ledger）；旧 170/93/29 分布转为动机证据（§6）。
- **验收命令**：SSOT 校验脚本断言每个 primary statistic 绑定唯一 denominator ID；`grep` 全文仅一套术语（semantic candidate / certified semantic mutant / D-pool）；零招募单元 grep 无 "SMS=0"。
- **状态**：`design-closed`。
- **残余限制**：certified 池仍可能在部分 PUT 招募稀疏 → 预注册收缩规则 + non-estimable 呈现。

### P0-2 formal layer 错误

- **原意见**：killed subset 与 effect-map preimage 混用；Theorem 3.4 双向 duality 不成立；Lemma G.2 缺 r=id；HOM 主张过强。
- **修改位置**：上游提纲已删除 fiber/duality/identity-degeneration（提纲 §6 命题 5 改保守扩展；§1.3 非主张清单）；HOM 缩窄为"特定默认一阶工具池不可达"（提纲 §10 第 3 行）。本计划 M0.5 新增**独立形式审计**里程碑。
- **新证据**：待 M0.5 外部复核意见。
- **验收命令**：审计意见文档落盘 `docs/review_*/formal_audit.md`，逐条 resolved；全文 grep 无 fiber/duality/exactly-characterizes 残留。
- **状态**：`design-closed`（表述已改；独立审计待执行）。
- **残余限制**：保守扩展命题的价值有限，须避免在 Abstract 中夸大。

### P0-3 Study 4 confirmatory license

- **原意见**：H4‴ admission 未冻结、gate 不满足；H2-2 serving stack 与 arm 嵌套。
- **修改位置**：提纲 §10（Studies 2–4 移出正文）；本计划 §6（正文任何提及必须带 exploratory/selection-conditioned 限定）。
- **新证据**：新论文不再承载这些 claim；若作补充材料，逐条附 frozen admission universe / serving stack / gating status / cluster unit / licensed claim 表（上轮验收标准照搬为补充材料模板）。
- **验收命令**：正文 grep 无 vendor/H4‴/H2-2 confirmatory 措辞；补充材料 claim 表逐行核对。
- **状态**：`design-closed`（以移出方式关闭；若未来重跑 serving-stack 对称实验则升级为新证据）。
- **残余限制**：Studies 2–4 的沉没成本不回收；接受。

### P0-4 独立 human/跨模型 validity gate

- **原意见**：AI labels 一致性低且未进 gating；须分层独立审计（zero/one/multi-flip、REJECTED、UNCERTAIN、bounds、generation-defect）。
- **修改位置**：本计划 §4.1 八层分层审计（v1.1 从"仅 D 级"扩展）；准入本身已改为证书制（AI/LLM 标签不再是 gating 依据，见 §4.1 "不准入"行）。
- **新证据**：待 M1.5a/M2.5 审计报告 + label-conditioned 敏感性表。
- **验收命令**：`docs/dve/certification_audit_report.md` 各层 κ/一致率 ≥ 预注册阈值；RQ5 报告审计前后 headline 差。
- **状态**：`design-closed`。
- **残余限制**：第二评者仍是小样本人力；层级阈值不达标时的降级路径已预注册。

### P0-5 独立 decision value

- **原意见**：aligned-over-cross 来自设计；34/34 由 detectability admission 保证；需 held-out decision-value 证据（四选一）。
- **修改位置**：本计划 §3 DVE 整体——同时命中上轮四选项中的三项：held-out real-defect corpus（§3.7，无 detectability 准入）、SMS-guided 相对 classical MS/coverage 的 held-out 增益（§3.6，升为 primary）、independent blinded fault-stratum labels（family/机理类标签独立于 MR 产生，§3.3）。
- **新证据**：待 M5 解盲结果。
- **验收命令**：预注册 H-DV 检验按冻结脚本执行；split commitment salt 第三方可验证。
- **状态**：`design-closed`（这是全计划的主投资项）。
- **残余限制**：native multi-output/multi-module case（第四选项）不在本轮范围，列 future work；主张范围限定 frozen-catalogue portfolio selection。

### P0-6 投稿包 submission-ready

- **原意见**：Zenodo version DOI、`<VERSION-DOI-PENDING>` 占位符、NOETHER confidential disclosure、defect4MR bibliography、首页占位 ACM DOI、pages 字段、camera-ready 文案。
- **修改位置**：本计划 M8 从"笼统流水线"改为**逐项清单**（v1.1）：
  1. 铸造 Studies 2–4 补充材料的 Zenodo version DOI + 新 DVE artifact DOI，替换全部 `<VERSION-DOI-PENDING>`；
  2. registrations/amendments/raw packets/frozen labels/SSOT/incident log 打包可审（含本计划的 prereg、ledger、commitment、审计报告）；
  3. defect4MR bibliography entry 与归档 DOI 统一；
  4. cover letter 向编辑 confidentially 披露 NOETHER 作者身份、审稿状态、claim overlap；
  5. 去除首页占位 ACM DOI `10.1145/nnnnnnn.nnnnnnn`；
  6. bibliography pages 字段与匿名 companion camera-ready 文案核对。
- **新证据**：待 M8 执行；每项在 `docs/release_<DATE>/audit_table.md` 留验收行（CLAUDE.md §8.3.1 机制复用）。
- **验收命令**：`grep -r "VERSION-DOI-PENDING\|nnnnnnn" submission/` 零命中；audit table 全绿。
- **状态**：`open`（依赖投稿时点，暂无法 design-close；清单已固化）。
- **残余限制**：NOETHER 披露文本需用户本人确认后随投稿提交。
