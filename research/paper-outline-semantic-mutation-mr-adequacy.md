# 论文提纲：基于独立语义变异的蜕变测试充分性准则

> 状态：论证骨架 v0.1（2026-07-10）  
> 用途：作为后续 IMRaD 重写、实验重构、证据审计和投稿材料的统一上游文档。  
> 核心约束：语义缺陷构造与 MR 设计相互不可见，分别冻结，只在盲化执行后的 kill matrix 中相交。

## 0. 拟定标题与一句话主张

### 中文标题

**MR 集合何时充分？基于独立语义变异的蜕变测试充分性准则**

### 英文标题

**When Is a Metamorphic-Relation Set Sufficient? An Independent Semantic-Mutation Criterion for Metamorphic Testing**

### 一句话主张

> 语义变异独立构造“程序可能错在哪里”，MR 集合独立回答“哪些错误能够被关系性测试观察到”；对于一个预先声明、独立认证且非空的目标语义缺陷集合，当且仅当每个缺陷都使至少一条有效 MR 在稳定的组级判定下由通过转为失败时，该 MR 集合才相对充分。

### 读者应记住的结论

MR 集合的充分性不是 MR 数量、执行覆盖率或普通句法变异得分，而是对一个独立目标缺陷域的覆盖。语义变异负责提供可控、可重复、可审计的目标缺陷；MR 只负责盲测，不参与缺陷生成、认证或等价判定。

## 1. 论文身份、范围与非主张

### 1.1 论文身份

本文是一篇“概念定义 + 方法框架 + 双盲实证评价”的经验软件工程论文。核心贡献是 MT 充分性问题的形式化对象、独立语义变异协议和相对充分性准则，而不是 LLM 变异体生成器、特定 MR 分类体系或四项实验的时间线。

### 1.2 研究范围

- 研究对象：程序 $P$、独立构造的语义变异体集合 $M_\Sigma(P)$ 和冻结的 MR 集合 $R$。
- 评价对象：MR 集合对声明缺陷域的相对充分性，而非程序本身的绝对正确性。
- 判定层级：单次 MR 观测、MR 的组级程序判定、单个缺陷检测、MR 集合充分性。
- 实证范围：先以科学计算程序为受控对象；跨语言、工业系统和多输出程序作为外部验证或未来工作。

### 1.3 明确不作的主张

- 不声称有限 MR 集合对所有可能缺陷普遍完备。
- 不声称所有程序修改都能被唯一分配到一个语义类别。
- 不声称语义变异是一种脱离语法修改的代码编辑机制。
- 不声称一个 MR 只能识别一类缺陷，或一个缺陷只能被一条 MR 识别。
- 不用正在评价的 MR 结果生成、筛选、认证语义变异体或判断其等价性。
- 不把 selection-conditioned 的真实缺陷检测率解释为总体缺陷覆盖率。
- 不把 SMS 的标量公式本身包装为独立的数学创新；创新在于缺陷域、独立性协议和充分性解释。

## 2. 研究问题与待检验假设

### 2.1 研究问题

**RQ1（构造性）**：能否在不访问被评价 MR 定义、实现和结果的条件下，为给定程序构造并独立认证一个可审计的语义变异体集合？

**RQ2（区别性）**：独立构造的语义变异体与传统句法变异体在缺陷机理、代码修改、语义效应和覆盖范围上有何不同？

**RQ3（充分性）**：冻结的 MR 集合能识别目标语义变异体集合中的哪些缺陷、遗漏哪些缺陷，是否达到相对充分？

**RQ4（判定稳健性）**：样本规模、组级聚合、重复策略、容差与操作性等价判定如何影响 MR kill、SMS 和充分性结论？

### 2.2 待预注册假设

> 下列假设是新实验的候选假设；只有在样本、阈值、统计单位和停止规则冻结后，才能称为预注册假设。

**H1（缺陷域区别）**：独立语义变异体集合不是默认一阶句法变异体集合的子集，并包含句法 baseline 未系统表达的缺陷机理。

**H2（严格充分性）**：对冻结的认证语义变异体集合 $M_\Sigma(P)$，被评价 MR 集合满足 $\mathrm{SMS}=1$。这是严格、可证伪的有限集合命题；任何一个存活变异体都足以否定它。

**H3（判定稳健性）**：主要充分性结论在预注册的样本量、重复数和容差敏感性范围内保持不变。

“SMS 等于 1 当且仅当有限目标集合中每个变异体均被至少一条 MR 杀死”是定义推论，不是经验假设。

## 3. 术语体系

### 3.1 基础对象

| 术语 | 建议英文 | 定义 |
|---|---|---|
| 被测程序 | Program Under Test, PUT | 在准入输入域上接受评价的程序 $P$。 |
| 程序语义 | program semantics | 程序从输入到输出或行为轨迹的偏函数 $\llbracket P\rrbracket$。 |
| 语义规范 | semantic contract | 独立于 MR 的程序需求集合，规定输入域、可观察量、领域约束、容差和参考证据。 |
| 语义缺陷 | semantic fault/defect | 由代码修改引入、使程序违反至少一项语义规范且仍可运行的潜伏缺陷。 |
| 语义效应 | semantic effect | 缺陷在语义规范层造成的可观察偏离；一个缺陷可以产生多个效应。 |
| Fault Card | semantic fault card | 描述适用前提、修改位置、变换规则、缺陷机理、认证义务和来源证据的审计单元。 |

### 3.2 变异对象

| 术语 | 建议英文 | 定义 |
|---|---|---|
| 语义变异算子 | semantic mutation operator | 根据 Fault Card 对程序生成候选修改的映射；算子不得访问被评价 MR。 |
| 候选语义变异体 | semantic-mutant candidate | 由语义变异算子产生、尚未完成独立语义认证的程序版本。 |
| 语义等价候选体 | semantically equivalent candidate | 在声明语义规范与输入域下没有可观察语义差异的候选体；不进入主要 denominator。 |
| 无效候选体 | invalid/unverified candidate | 不能运行、越出接口、包含额外修改、缺少独立证书或无法确认违反语义规范的候选体。 |
| 认证语义变异体 | certified semantic mutant | 通过机械有效性、非等价性与独立语义证书三项门槛的候选体。 |
| 语义变异体集合 | semantic-mutant universe | 针对程序与语义规范预先声明、冻结的认证语义变异体集合。 |

### 3.3 MR 与判定对象

| 术语 | 建议英文 | 定义 |
|---|---|---|
| 蜕变关系 | metamorphic relation, MR | 由输入变换、输出关系、组级聚合规则及判定参数组成的关系性测试规范。 |
| 样本级违反 | sample-level violation | 某个源输入/后续输入执行组不满足 MR 输出关系。 |
| 组级 MR 判定 | group-level MR verdict | 在预先声明的样本集、统计检验、容差和重复策略下得到的程序级 pass/fail。 |
| 有效 MR | valid MR | 在未变异原程序上通过组级判定的 MR；原程序失败的 MR 不得产生 kill。 |
| 杀死 | kill | 原程序通过而变异程序在同一 MR 判定协议下失败。 |
| 存活 | survive | 认证非等价语义变异体没有被 MR 集合中任何有效 MR 杀死。 |
| Kill matrix | kill matrix | 行为语义变异体、列为 MR 的二值检测矩阵。 |

### 3.4 充分性对象

| 术语 | 建议英文 | 定义 |
|---|---|---|
| 单缺陷可检测性 | defect detectability | 给定缺陷是否被 MR 集合中至少一条有效 MR 杀死。 |
| 相对充分性 | relative MR-set sufficiency | MR 集合是否杀死声明且非空的目标集合中每个认证语义变异体。 |
| 语义变异得分 | Semantic Mutation Score, SMS | MR 集合杀死的认证语义变异体比例。 |
| 残余缺陷集 | residual fault set | 未被 MR 集合杀死的认证语义变异体集合。 |
| 独有检测 | unique kill | 只被某一条 MR 杀死的变异体。 |
| 最小充分子集 | minimal sufficient MR subset | 在目标缺陷域上达到 SMS=1 且基数最小的 MR 子集；作为扩展分析，不是本文必需主张。 |

## 4. 符号系统

### 4.1 程序与语义规范

| 符号 | 含义 |
|---|---|
| $P$ | 原始被测程序。 |
| $P'$ 或 $P_m$ | 候选或认证变异程序。 |
| $\mathcal{X},\mathcal{Y}$ | 输入域与输出/行为域。 |
| $\mathcal{X}_{\mathrm{adm}}\subseteq\mathcal{X}$ | 准入输入域。 |
| $D_X$ | 在准入输入域上的采样分布。 |
| $\llbracket P\rrbracket:\mathcal{X}_{\mathrm{adm}}\rightharpoonup\mathcal{Y}$ | 程序的偏函数语义。 |
| $\alpha:\mathcal{Y}\rightarrow\mathcal{Z}$ | 从原始输出/轨迹到领域语义可观察量的抽象。 |
| $\Phi=\{\phi_1,\ldots,\phi_q\}$ | 独立于 MR 声明的领域需求或语义约束集合。 |
| $\tau_\Sigma$ | 语义规范中的单位、精度、离散化与容差政策。 |
| $\Sigma=(\mathcal{X}_{\mathrm{adm}},D_X,\alpha,\Phi,\tau_\Sigma)$ | 程序语义规范。 |

### 4.2 缺陷、算子与认证

| 符号 | 含义 |
|---|---|
| $f\in\mathcal{F}_\Sigma$ | 语义规范下的一张 Fault Card。 |
| $f=(\mathrm{pre}_f,\mathrm{loc}_f,e_f,\mathrm{mech}_f,\mathrm{obl}_f,\mathrm{prov}_f)$ | Fault Card 的前提、位置、编辑、机理、认证义务和来源。 |
| $\mu_f:\mathrm{Prog}\rightarrow 2^{\mathrm{Prog}}$ | 与 Fault Card 对应的语义变异算子。 |
| $C_\Sigma(P)=\bigcup_{f\in\mathcal{F}_\Sigma}\mu_f(P)$ | 候选语义变异体集合。 |
| $\kappa$ | 独立语义证书，包括违反需求、见证输入/证据、认证 oracle 和来源记录。 |
| $\mathrm{Cert}_\Sigma(P,P',f,\kappa)\in\{0,1\}$ | 独立语义认证谓词。 |
| $P\equiv_\Sigma P'$ | 在声明语义规范上语义等价。 |
| $\widehat{\mathrm{Eq}}_{\Sigma,B,\tau}(P,P')$ | 在有限样本、参考 oracle 与容差下的操作性等价估计。 |
| $E_\Sigma(P)$ | 被判为语义等价的候选体集合。 |
| $A_\Sigma(P)$ | 无效或未认证候选体集合。 |
| $M_\Sigma(P)$ | 冻结的认证非等价语义变异体集合。 |

### 4.3 MR、样本与组级判定

| 符号 | 含义 |
|---|---|
| $r\in R$ | 一条 MR；$R=\{r_1,\ldots,r_n\}$ 为冻结的 MR 集合。 |
| $r=(T_r,\rho_r,A_r,G_r,\Theta_r)$ | MR 的输入变换、样本关系、批内聚合器、重复聚合器和判定参数。 |
| $B=(x_1,\ldots,x_s)\sim D_X^s$ | 一批源输入。 |
| $T_r(B)$ | 对应的后续输入批。 |
| $z_r(P,x)$ | 程序在源/后续执行上产生的样本级 MR 残差或布尔结果。 |
| $A_r$ | 将一个批次的样本级结果聚合为批次 verdict 的规则。 |
| $G_r$ | 将多批次或多次重复聚合为稳定程序级 verdict 的规则。 |
| $\mathrm{AVP}(P,r;B_{1:q},\Theta_r)$ | MR 对程序的组级 pass/fail 判定。 |

### 4.4 检测、得分与充分性

| 符号 | 含义 |
|---|---|
| $K_{ij}$ | 变异体 $m_i$ 是否被 MR $r_j$ 杀死。 |
| $\mathrm{kill}(m_i,r_j)$ | 单个变异体—MR 的 kill 谓词。 |
| $\mathrm{det}_R(m_i)=\max_j K_{ij}$ | 变异体是否被 MR 集合检测。 |
| $U(R,M)$ | 相对于 $R$ 的残余变异体集合。 |
| $\mathrm{SMS}(R,M)$ | $R$ 在认证变异体集合 $M$ 上的语义变异得分。 |
| $\mathrm{Suff}(R,M)$ | $R$ 是否对 $M$ 相对充分。 |
| $b_M,b_R$ | 变异体和 MR 的盲化标识映射。 |
| $\perp_{\mathrm{proc}}$ | 程序性非干扰/独立构建；不是概率独立符号。 |

## 5. 形式化定义

### 定义 1：语义规范满足

原程序满足语义规范，记作 $P\models\Sigma$，当且仅当 $P$ 在 $\mathcal{X}_{\mathrm{adm}}$ 上满足 $\Phi$ 中所有适用约束，并遵循 $\tau_\Sigma$ 声明的单位、精度、离散化和容差政策。

### 定义 2：语义等价与操作性等价

理论上，若 $P$ 与 $P'$ 在 $\Sigma$ 所声明的全部语义可观察量上不可区分，则

\[
P\equiv_\Sigma P'.
\]

由于一般程序等价不可判定，实验仅计算操作性估计

\[
\widehat{\mathrm{Eq}}_{\Sigma,B,\tau}(P,P'),
\]

其证据可来自解析解、可信参考实现、独立实现的差分比较、历史修复或领域专家裁决，但不得调用被评价 MR 集合的 pass/fail 结果。理论概念与有限估计必须在全文中保持不同名称。

### 定义 3：Fault Card

Fault Card

\[
f=(\mathrm{pre}_f,\mathrm{loc}_f,e_f,\mathrm{mech}_f,
\mathrm{obl}_f,\mathrm{prov}_f)
\]

规定缺陷适用前提、代码位置、变换规则、预期缺陷机理、独立认证义务和来源证据。Fault Card 来自程序需求、算法规范、历史缺陷、FMEA 或领域专家分析，不得来自被评价 MR 的定义或运行结果。

### 定义 4：语义变异算子

语义变异算子 $\mu_f$ 根据 Fault Card $f$ 将程序映射为零个或多个候选程序：

\[
\mu_f(P)=\{P'_1,\ldots,P'_k\}.
\]

“语义”描述算子的缺陷目标与认证义务，不表示存在一种非语法的代码编辑机制；每个 $P'$ 仍由有限语法编辑实现。

### 定义 5：认证语义变异体

给定 $P\models\Sigma$，候选程序 $P'\in C_\Sigma(P)$ 是 Fault Card $f$ 下的认证语义变异体，当且仅当：

1. **可实现性**：$P'$ 由 $P$ 的有限代码编辑得到；
2. **潜伏有效性**：$P'$ 可编译/加载，在准入输入域终止，保持接口，不依赖崩溃暴露；
3. **非等价性**：$P'\not\equiv_\Sigma P$，且操作性证据达到预注册门槛；
4. **规范违反**：存在至少一个 $\phi\in\Phi$，使 $P'\not\models\phi$；
5. **独立证书**：存在 $\kappa$，使 $\mathrm{Cert}_\Sigma(P,P',f,\kappa)=1$；
6. **修改完整性**：候选体只包含 Fault Card 声明的目标修改或被批准的等价实现变化。

不要求一个变异体只违反一项 $\phi$。多语义效应是允许的，并在证书中记录为多标签集合。

### 定义 6：双盲程序性独立

语义变异分支与 MR 分支满足程序性独立，记作

\[
M_\Sigma(P)\perp_{\mathrm{proc}}R,
\]

当且仅当：

1. 变异生成者只能访问 $P,\Sigma,\mathcal{F}_\Sigma$，不能访问 $R$、MR 源码或 MR 结果；
2. 语义认证者不能用 $R$ 中 MR 的执行结果完成准入、分层或等价判断；
3. MR 设计者只能访问 $P,\Sigma$ 及其独立 MR 设计材料，不能访问 Fault Card、变异体、缺陷标签或预期效果；
4. 两个集合在交叉执行前分别冻结；
5. 执行阶段只使用盲化 ID，分析阶段在 kill matrix 冻结后解盲。

两条分支可以共享程序规范 $\Sigma$ 作为共同祖先；禁止的是分支之间的直接反馈和结果驱动调整。

### 定义 7：MR 与组级判定

一条 MR 定义为

\[
r=(T_r,\rho_r,A_r,G_r,\Theta_r),
\]

其中 $T_r$ 生成后续输入，$\rho_r$ 比较源输出与后续输出，$A_r$ 在一个样本批次内聚合，$G_r$ 在多个批次或重复之间聚合，$\Theta_r$ 固定容差、显著性水平、效应量门槛与重复策略。令

\[
z_r(P,x)=\rho_r\!\left(
\alpha(\llbracket P\rrbracket(x)),
\alpha(\llbracket P\rrbracket(T_r(x)))
\right),
\]

则稳定程序级判定为

\[
\mathrm{AVP}(P,r;B_{1:q},\Theta_r)
=G_r\left(
A_r(\{z_r(P,x):x\in B_1\}),\ldots,
A_r(\{z_r(P,x):x\in B_q\})
\right).
\]

对于确定性、逐点成立的 MR，一个样本违反可以构成反例；对于浮点、随机、统计或轨迹型 MR，必须使用预先声明的样本集和组级聚合。本文的充分性判定统一使用程序级 verdict，而不是任意单样本结果。

### 定义 8：Kill

认证语义变异体 $m_i$ 被 MR $r_j$ 杀死，当且仅当原程序通过而变异程序失败：

\[
K_{ij}=\mathrm{kill}(m_i,r_j)=1
\iff
\mathrm{AVP}(P,r_j)=\mathrm{pass}
\land
\mathrm{AVP}(P_{m_i},r_j)=\mathrm{fail}.
\]

若原程序在 $r_j$ 上失败，则 $r_j$ 对该程序无效，不能对任何变异体贡献 kill。

### 定义 9：MR 集合检测

\[
\mathrm{det}_R(m_i)=
\max_{r_j\in R}K_{ij}.
\]

当且仅当 $\mathrm{det}_R(m_i)=1$，缺陷 $m_i$ 被 MR 集合中至少一条 MR 识别。

### 定义 10：残余缺陷集

\[
U(R,M)=\{m\in M:\mathrm{det}_R(m)=0\}.
\]

残余集不是噪声，而是 MR 集合不足的直接证据，应按 Fault Card、语义效应和程序结构解释。

### 定义 11：Semantic Mutation Score

对于非空认证语义变异体集合 $M$：

\[
\mathrm{SMS}(R,M)
=\frac{\sum_{m\in M}\mathrm{det}_R(m)}{|M|}
=1-\frac{|U(R,M)|}{|M|}.
\]

若 $M=\varnothing$，SMS 为 **non-estimable/undefined**，不得记为 0 或 1。

### 定义 12：MR 集合相对充分性

\[
\mathrm{Suff}(R,M)=1
\iff
M\neq\varnothing
\land
\forall m\in M,\ \exists r\in R:\mathrm{kill}(m,r)=1.
\]

对于有限非空 $M$：

\[
\mathrm{Suff}(R,M)=1
\iff
\mathrm{SMS}(R,M)=1
\iff
U(R,M)=\varnothing.
\]

该结论只对声明的 $M$ 成立，不推出对未知真实缺陷总体的普遍完备性。

### 定义 13：独有检测与冗余

\[
\mathrm{Unique}(r_j)=
\{m_i:K_{ij}=1\land\sum_{\ell\neq j}K_{i\ell}=0\}.
\]

MR 的独有检测用于判断其不可替代贡献；列向量高度重合表示检测冗余，但冗余本身可能为稳定性和容错提供价值。

## 6. 基本性质与拟证明命题

### 命题 1：充分性等价

对有限非空认证集合 $M$，$\mathrm{Suff}(R,M)=1$、$\mathrm{SMS}(R,M)=1$ 与 $U(R,M)=\varnothing$ 三者等价。证明由定义展开即可。

### 命题 2：MR 集合扩张单调性

若 $R_1\subseteq R_2$，且每条 MR 的冻结判定保持不变，则

\[
\mathrm{SMS}(R_1,M)\leq\mathrm{SMS}(R_2,M).
\]

该命题只说明增加 MR 不会减少 OR 聚合的 kills，不说明新增 MR 具有成本效益或外部有效性。

### 命题 3：有效 MR 约束

若 $\mathrm{AVP}(P,r)=\mathrm{fail}$，则对所有 $m\in M$，规定 $\mathrm{kill}(m,r)=0$。因此，原程序上的 MR false positive 不能提高 SMS。

### 命题 4：多对多性

Kill matrix 不要求行或列单值：一个变异体可以被多条 MR 杀死，一条 MR 可以杀死多类变异体。多效应语义缺陷不得仅因多条 MR 失败而从 denominator 中删除。

### 命题 5：经典 Mutation Score 的结构特化

定义一般化比率函数

\[
\mathrm{Score}(\mathcal{M},\mathcal{E},\mathcal{K})
=\frac{|\mathcal{K}|}{|\mathcal{M}|-|\mathcal{E}|}.
\]

经典 MS 取句法变异体集合、经典等价变异体集合和测试 oracle 的 killed 集合；SMS 取独立语义候选集合中经认证且非等价的 denominator 与 MR kill 集合。若语义算子限制为传统句法算子、等价谓词恢复为经典行为等价、kill 谓词恢复为经典测试杀死，则 SMS 在定义上特化为 MS。

这一向下兼容结论是“度量结构与概念分类的保守扩展”，不是把 MR 人为退化为 identity relation 的强定理，也不是独立数学新颖性。

## 7. 双盲构建和执行协议

### 7.1 共享上游：语义规范

由领域专家、需求文档、算法规范和可信实现共同形成 $\Sigma$。语义变异分支和 MR 分支均可读取 $\Sigma$，但不得读取对方的中间产物。

### 7.2 分支 A：语义缺陷与变异体构建

1. 从需求、历史缺陷、算法规范和 FMEA 建立 Fault Card 库。
2. 对程序进行可变异位置识别：参数、API、边界、状态更新、算法选择、数据流和数值策略。
3. 使用确定性代码变换、历史补丁逆向或 LLM 生成候选体。
4. 运行编译、接口、终止、非崩溃、单目标修改和基本非平凡性检查。
5. 使用独立 oracle 完成语义认证和操作性非等价判断。
6. 冻结候选、拒绝、等价、未认证和认证集合以及全部审计记录。

### 7.3 独立认证证据等级

| 等级 | 证据 | 主要用途 |
|---|---|---|
| A | 解析证明、误差表达式、形式化 proof obligation | 最强认证。 |
| B | 高精度/可信参考实现、独立实现差分、可复现实验 oracle | 主要经验认证。 |
| C | 真实历史缺陷及修复补丁、版本对照 | 外部真实性认证。 |
| D | 双领域专家独立裁决并达成共识 | 无直接 oracle 时的补充认证。 |
| 不准入 | 仅有 LLM/作者“缺陷意图”，或仅被某条 MR 杀死 | 只能作为候选体，不进入主要 denominator。 |

### 7.4 分支 B：MR 集合构建

1. MR 设计者只读取 $P,\Sigma$ 及独立 MR 文献/设计材料。
2. 在接触 Fault Card 和变异体前冻结 MR 定义、输入变换、样本政策、容差、统计检验与停止规则。
3. 在原程序上验证 MR 的适用性与 false-positive 风险。
4. 冻结完整 MR 集合，失败 MR 不在看到变异体后替换或调参。

### 7.5 盲化和角色访问矩阵

| 产物 | 变异生成者 | 语义认证者 | MR 设计者 | 执行器 | 解盲分析者 |
|---|:---:|:---:|:---:|:---:|:---:|
| 程序 $P$、语义规范 $\Sigma$ | 可见 | 可见 | 可见 | 可见 | 可见 |
| Fault Cards、变异算子 | 可见 | 可见 | 不可见 | 不可见 | 冻结后可见 |
| 变异 diff、缺陷标签、证书 | 可见 | 可见 | 不可见 | 仅执行所需代码 | 冻结后可见 |
| MR 定义、源码、参数 | 不可见 | 不可见 | 可见 | 可见 | 冻结后可见 |
| MR 执行结果 | 不可见 | 不可见 | 冻结前不可见 | 产生 | 冻结后可见 |
| blind-ID 映射 | 不可见 | 不可见 | 不可见 | 仅匿名 ID | 可见 |

### 7.6 交叉执行

对每个 $m_i\in M$ 与每条 $r_j\in R$ 运行相同冻结协议，生成 $K\in\{0,1\}^{|M|\times|R|}$。不得使用结果补生成缺失变异体、重写 Fault Card、重选 MR、修改容差或重新定义主要 denominator。

### 7.7 解盲分析

Kill matrix 冻结后连接 Fault Card、语义效应、代码编辑表面和 MR 标识，计算 SMS、per-class coverage、unique kills、重叠、残余缺陷和成本。任何“某类 MR 与某类缺陷对齐”的结论均为事后观察或预注册交互分析，而非生成阶段的预设映射。

## 8. IMRaD 论文结构

### Abstract

摘要严格采用五句功能结构：第一句说明 MT 留下 MR-set adequacy 问题；第二句指出传统句法 mutant universe 与 co-designed mutants 的不足；第三句概述 MR-free semantic-mutant construction、independent certification 和 frozen blind cross-execution；第四句报告 RQ1–RQ4 的主要数字和充分性 verdict；第五句只陈述相对于声明缺陷域的理论与实践意义。结果未冻结前不预写确认性数字。

**Keywords**：metamorphic testing；metamorphic-relation adequacy；semantic mutation；mutation score；test sufficiency；blind evaluation。

### 1 Introduction

#### 1.1 背景：MT 解决 oracle problem，但留下 adequacy problem

MT 可以在缺少单次输出 oracle 时检查执行关系，但“拥有并运行若干 MR”不等于“MR 集合足以识别目标缺陷”。论文从这一基础问题出发：对于一个给定缺陷，是否至少有一条 MR 在原程序通过、缺陷程序失败？

#### 1.2 问题陈述：充分性必须相对于缺陷域定义

如果目标缺陷域未声明，MR 集合的充分性没有量词范围；如果缺陷由被测 MR 自己定义，则结论循环。本文把 MR 集合充分性定义为对独立认证语义缺陷集合的覆盖。

#### 1.3 现有研究不足

传统 MS 的 denominator 主要由句法算子决定，MR 质量研究则常使用数量、覆盖、相关性或 co-designed mutants。缺少一种将“独立语义缺陷域”“组级 MR 判定”和“集合充分性”连接起来、又保持经典 mutation-score 结构的框架。

#### 1.4 核心思想

语义缺陷和 MR 从同一程序规范出发但分别构建、分别冻结；前者回答可能错在哪里，后者盲测哪些错误可被关系性执行观察。二者只在 kill matrix 中相交。

#### 1.5 RQ、贡献与非主张

列出 RQ1–RQ4、三项核心贡献和有限集合相对充分性的范围。引言中不展开 LLM vendor、实验事故时间线、复杂归因或跨语言叙事。

### 2 Related Work

#### 2.1 Metamorphic testing 与 MR 质量

回顾 MR 选择、优先级、覆盖、有效性、false positive 和多 MR 组合研究，指出现有指标与“对独立缺陷域的充分性”之间的差距。

#### 2.2 Classical mutation testing 与 adequacy

回顾 mutation score、等价变异体、coupling effect、higher-order mutation 和 domain-specific operators。明确本文继承 killed/equivalent/surviving/score 的结构，而不是重新发明比例公式。

#### 2.3 Semantic/domain-specific mutation

区分语言语义变异、模型语义变异、数据变异、深度学习变异和本文的“由独立程序语义规范认证的代码级缺陷”。强调所有代码变异最终都由语法编辑实现，差异在缺陷选择和认证层。

#### 2.4 研究空白

现有研究尚未同时满足：缺陷构造不看 MR、MR 设计不看缺陷、等价与语义准入不使用 MR 结果、组级判定可复现、集合充分性形式化。该五项缺口构成本文位置。

### 3 Formal Framework

#### 3.1 程序语义与语义规范

给出 $P,\Sigma,\alpha,\Phi,\tau_\Sigma$ 及规范满足关系。

#### 3.2 Fault Card 与语义变异算子

给出 Fault Card、候选池和算子定义，说明“语义”是缺陷目标和证书，不是另一种编辑机制。

#### 3.3 等价、无效候选体与认证变异体

区分理论语义等价、操作性等价估计、未认证候选和认证语义变异体，固定唯一 primary denominator。

#### 3.4 双盲非干扰约束

给出 $M_\Sigma(P)\perp_{\mathrm{proc}}R$ 的角色视图、冻结顺序和禁止信息流。

#### 3.5 MR 与组级 failure criterion

形式化 $r=(T_r,\rho_r,A_r,G_r,\Theta_r)$、样本级 witness、批次聚合和重复稳定判定，回答“单样本还是一组样本”。

#### 3.6 Kill matrix、SMS 与充分性

给出 kill、集合 OR 聚合、残余集、SMS 和相对充分性定义。

#### 3.7 基本性质与向下兼容

证明充分性等价、集合扩张单调性和有效 MR 约束；将经典 MS 表述为一般比率结构的句法特化，不再使用有争议的 identity-MR degeneration。

### 4 Method

#### 4.1 总体研究设计

采用两个独立分支加一个冻结交叉执行阶段：MR-free semantic-mutant construction、mutant-free MR design、blind cross-execution。

#### 4.2 实验对象

说明程序选择标准、领域类别、规模、输入域、参考实现和语义规范来源。现有 12 PUT 可作为 pilot；主要确认性实验需使用未被旧 MR/变异设计共同污染的 held-out 程序或重新冻结的材料。

#### 4.3 语义缺陷库与 Fault Card 构建

报告 Fault Card 来源、缺陷类别、适用程序、编辑表面、证书类型和拒绝规则。缺陷类别与 MR 类别不建立一一对应。

#### 4.4 语义变异体生成

分别报告确定性变换、历史补丁逆向和 LLM-assisted generation；LLM 仅是实现方式，统一接受同一独立认证门槛。

#### 4.5 独立认证与等价判定

报告证据等级、双人裁决、样本/参考 oracle、操作性等价敏感性和 audit record。任何仅凭 MR kill 才能确认的候选体均排除在 primary denominator 外。

#### 4.6 MR 集合独立构建

报告 MR 来源、设计者角色、冻结时点、输入变换、样本政策、容差与原程序适用性验证。

#### 4.7 双盲执行与数据冻结

报告 blind ID、访问控制、运行顺序、失败运行、不可重抽规则、停止条件和解盲时点。

#### 4.8 Baselines

1. **缺陷域 baseline**：一种或多种默认一阶句法变异工具及其经典 mutant pool；
2. **MR baseline**：文献通用 MR、随机 MR、目标 MR 的机械消融或不同 MR 子集；
3. **评分 baseline**：经典 MS、MR 数量/覆盖率及其他可复现 adequacy 指标；
4. **外部 baseline**：独立 held-out 真实缺陷，且不得以“目标 MR 已能检测”作为入选条件。

#### 4.9 评价指标

- 构造：generation yield、机械有效率、认证率、等价率、拒绝原因；
- 区别：AST/patch overlap、fault-mechanism overlap、semantic-effect coverage；
- 检测：SMS、per-fault-class coverage、unique kills、overlap、residual set；
- MR 质量：原程序 false-positive rate、flakiness、容差敏感性；
- 工程：执行时间、样本量、MR 设计成本、每个 unique kill 的成本；
- 统计：效应量、置信区间、PUT-cluster bootstrap 或适合配对/聚类结构的方法。

#### 4.10 分析单位与推断权限

固定缺陷集合上的 SMS=1 是有限集合事实，不需要把它伪装成总体推断。跨程序推广时以 PUT 为聚类单位；变异体级结果不能被当成相互独立的总体样本。

### 5 Results

#### 5.1 RQ1：能否独立构造并认证语义变异体？

报告 Fault Card 数量、生成数量、有效率、独立认证率、等价/未认证比例、证书等级和多效应分布。重点不是生成数量，而是有多少候选在完全不查询 MR 的情况下获得可审计证书。

#### 5.2 RQ2：语义变异与句法变异有何不同？

报告代码 patch overlap、缺陷机理覆盖、修改跨度、API/算法/配置层分布及句法 baseline 的 unique categories。结论必须限定到具体工具版本和配置，不能从一个 default pool 推广到所有句法或 higher-order mutation。

#### 5.3 RQ3：MR 集合是否充分？

展示完整 kill matrix、SMS、残余缺陷集、per-class coverage 和 unique kills。若任一认证变异体存活，则严格充分性假设失败，并以存活缺陷类型作为主要结果，而不是把失败阈值隐藏在平均数中。

#### 5.4 RQ4：判定对样本与容差是否稳健？

报告单样本 witness、组级 verdict、重复稳定性、样本量和容差敏感性。区分“一个反例足以推翻确定性 MR”与“统计/随机 MR 必须基于一组样本判定”。

#### 5.5 Baseline 与 ablation

比较不同 MR 子集、通用/随机/消融 MR、经典 MS 与 SMS 的排序和独有检测。若 SMS 不能带来独立的 MR 选择或缺陷发现价值，应如实限定为诊断框架。

### 6 Discussion

#### 6.1 核心发现

回答三个问题：是否能独立构造缺陷域；语义缺陷域是否补充句法缺陷域；现有 MR 集合对该域是否充分。

#### 6.2 理论意义

充分性被重写为两个独立有限集合之间的覆盖，而非 MR 自我验证。语义变异不是 MR 的镜像类别，kill matrix 的多对多结构比预设对角线更符合真实缺陷机制。

#### 6.3 实践意义

SMS 的价值首先是暴露 residual fault set，并指导补充 MR，而不是直接作为工业 release gate。只有 held-out decision-value 实验完成后，才能声称 SMS 改善 MR 选择。

#### 6.4 负结果的解释

SMS<1 不是方法失败，而是对“该 MR 集合不充分”的直接回答；non-estimable 则表示缺陷构造或认证不足。两者不能混为 0 分。

#### 6.5 有效性威胁

- 两分支共享 $\Sigma$ 可能带来共同规范偏差，但不等于直接信息泄漏；
- 独立 oracle 仍可能不完整或存在专家判断误差；
- 操作性等价存在有限采样误判；
- 语义缺陷库可能不代表真实缺陷总体；
- MR 适用性、容差和随机性可能改变 verdict；
- 同一 PUT 内多个变异体存在聚类依赖；
- 小型单输出科学计算程序限制外部有效性；
- 句法 baseline 的工具、版本和 operator set 限制“区别性”结论；
- LLM 生成分布不能代表人类真实缺陷分布。

#### 6.6 未来工作

1. 扩展 proof-carrying 或 reference-backed 语义证书；
2. 构建不以目标 MR detectability 入选的 held-out 真实缺陷集；
3. 检验 SMS-guided MR revision 相对经典 MS、覆盖率和随机选择的决策收益；
4. 扩展到多输出、多模块、跨语言和工业科学软件；
5. 研究最小充分 MR 子集、成本约束充分性和动态缺陷域；
6. 比较多种句法工具与 higher-order mutation，而非只使用单一 default pool。

### 7 Conclusion

结论只保留一条主线：MR 集合是否充分，取决于它能否覆盖独立声明并认证的目标语义缺陷域。语义变异提供缺陷域，组级 MR verdict 提供稳定观察，kill matrix 和 SMS 给出相对充分性与残余缺陷；任何超出该有限域的普遍完备性都不在本文主张范围内。

## 9. 论文贡献的最终收敛版本

1. **概念与兼容性**：定义语义规范、Fault Card、语义变异算子、候选体、认证语义变异体、语义等价候选体和 SMS，并把它们表述为经典 mutation-score 结构的保守扩展。
2. **MT 充分性准则**：定义样本级违反、组级 MR verdict、kill、残余缺陷集和相对充分性，严格区分单缺陷可检测、得分与集合充分性。
3. **双盲方法与实证**：提出 MR-free 缺陷构造、independent certification、mutant-free MR design 和 freeze-before-crossing 协议，并用 kill matrix 展示语义变异实例、检测覆盖与遗漏边界。

## 10. 现有证据的迁移决策

| 现有材料 | 新论文中的地位 | 原因 |
|---|---|---|
| Study 1 的 292 个 v4 变异体 | pilot/探索性候选池 | 生成意图和准入部分使用 MR/MP 信息，不能作为新双盲主实验 denominator。 |
| 60-cell aligned/cross 结果 | 探索性内部区分证据 | `align(j)=j` 来自设计，不能单独证明独立充分性。 |
| 5.14% Cosmic Ray AST overlap | 限定性观察 | 只支持特定工具默认一阶配置下的分布区别。 |
| 170/93/29 invariant-flip 分布 | 构念诊断证据 | 证明旧 denominator 混合无翻转、单翻转和多翻转对象，支持重建准入协议。 |
| Studies 2–4 的 vendor、attribution、language 结果 | 补充材料或后续论文 | 与“独立缺陷域上的 MR 集合充分性”主线关系较弱，继续保留会恢复缝合结构。 |
| 34-case industrial arm | selection-conditioned 外部描述 | 案例以 MR-detectable 为准入条件，不能证明 prospective coverage。 |

新论文的主要实证结论必须来自重新冻结的 MR-free 认证变异体池与独立 MR 集合。旧结果可以说明为什么需要新协议，但不能被措辞升级为双盲验证结果。

## 11. 建议图表

1. **Figure 1**：共享语义规范、双分支独立构建、冻结交叉执行和解盲分析流程。
2. **Figure 2**：候选体、等价体、无效体、认证语义变异体与 denominator 的集合关系。
3. **Figure 3**：kill matrix 及 many-to-many 缺陷—MR 映射示意。
4. **Table 1**：术语和符号表。
5. **Table 2**：角色访问矩阵与双盲非干扰约束。
6. **Table 3**：程序、语义规范、Fault Cards、证书等级和认证变异体数量。
7. **Table 4**：句法 baseline、MR baseline 和评分 baseline。
8. **Table 5**：per-class coverage、unique kills、residual faults、SMS 与充分性 verdict。
9. **Table 6**：样本、重复、容差和操作性等价敏感性。

## 12. 写作纪律

- 全文固定使用“认证语义变异体”指 primary denominator；“候选体”不得省略为“语义变异体”。
- 全文固定使用“MR violation/program-level fail”，避免把随机单样本偏离直接写成 MR failure。
- 每个 SMS 数字必须同时声明 denominator、程序集合、MR 集合、采样政策和等价/认证规则。
- 所有 0 招募单元写作 non-estimable，不写作 SMS=0。
- 不把多效应缺陷称为 artefact；除非独立证据证明它违反 Fault Card 的单一修改约束。
- 不在摘要、贡献和结论中使用未通过 evidence ledger 的结果。
- 任何 baseline 结论均绑定工具、版本、operator set 和配置。
- 新正文按 RQ 组织，不按 Study 1→2→3→4 的时间线组织。
