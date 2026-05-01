# 统一蜕变测试理论体系：三支柱形式化框架与核工程 V&V 对接

**A Unified Metamorphic Testing Theory: Three-Pillar Formal Framework and Nuclear V&V Alignment**

---

## 摘要

本文提出一个面向**科学计算程序（SCP）**、**概率程序（PP）** 与**机器学习代理模型程序（SML）** 的统一蜕变测试（Metamorphic Testing, MT）理论体系。该体系以**三支柱架构**为骨架——层次拓扑（支柱 I，回答 *Where*）、元模式矩阵（支柱 II，回答 *What*）、故障模型（支柱 III，回答 *Why*）——辅以基于变异测试同构映射的形式化充分性度量。本文区分**演绎完备、结构完备、经验饱和完备与监管完备**四种层级，论证 MT 完备性的正确操作化方式：不是"穷尽一切可能故障"，而是"在任何时刻均能清晰声明自身不完备之所在"。**可证伪性**与**边界显式性**构成完备性的工程接口，与 ASME NQA-1、NRC RG 1.203、FMECA、PIRT 形成可审计的结构同构。本文贡献有四：（i）提出三支柱 + 形式化度量的公理化体系；（ii）给出类型参数化的同构继承、对偶、单调性、类型不变性、必要非充分性五个核心定理；（iii）构造 $(l, p, \varphi)$ 立方体闭合性作为可证伪的完备性断言；（iv）建立理论—监管结构映射表，实现研究成果向核工程 V&V 主流的可传递性。

**关键词**：蜕变测试；验证与确认；元模式；故障模型；完备性；核软件；变异得分

---

## 缩写对照表

| 缩写 | 英文全称 | 中文 |
|------|---------|------|
| MT | Metamorphic Testing | 蜕变测试 |
| MR | Metamorphic Relation | 蜕变关系 |
| SCP | Scientific Computing Program | 科学计算程序 |
| PP | Probabilistic Program | 概率程序 |
| SML | Surrogate Machine Learning program | 机器学习代理模型程序 |
| V&V | Verification and Validation | 验证与确认 |
| MMS | MR Mutation Score | MR 变异得分 |
| FMECA | Failure Mode, Effects and Criticality Analysis | 失效模式、影响与危害度分析 |
| NQA-1 | Nuclear Quality Assurance-1 | 核质量保证标准 |
| RG 1.203 | NRC Regulatory Guide 1.203 | 美国核管会管理导则 1.203 |
| PIRT | Phenomena Identification and Ranking Table | 现象识别与排序表 |
| MCMC | Markov Chain Monte Carlo | 马尔可夫链蒙特卡洛 |
| VI | Variational Inference | 变分推断 |
| ESS | Effective Sample Size | 有效样本量 |
| PINN | Physics-Informed Neural Network | 物理信息神经网络 |
| TVD | Total Variation Diminishing | 总变差减小（格式） |

---

## 1. 引言

### 1.1 研究背景

科学计算程序作为核工程、航空航天、气候建模等**安全关键**领域的核心工具，其正确性验证长期面临**测试预言问题**（test oracle problem）：多数情况下无法先验地知道"正确输出"应当是什么，因为解析解不存在、实验测量昂贵、或物理系统处于新运行体制。Chen 等（1998）提出的 MT 通过利用程序必须满足的**输入—输出关系**（蜕变关系）绕过预言困境。

然而 MT 长期缺乏一个兼具**形式严谨性**与**工程可操作性**的完备性理论：MR 识别多依赖领域专家直觉；MR 集合的充分性评估多依赖经验性变异测试；跨程序类型（SCP、PP、SML）的理论统一鲜有系统论述。这一理论空白直接影响 MT 在核安全软件 V&V 语境下的**监管可接受性**。

### 1.2 完备性立场

本文采取如下哲学立场：

> **MT 的完备性不是 Gödel 式的演绎完备，而是可审计的结构完备与经验饱和完备的合取。**

这一立场与核工程 V&V 传统严格对齐——后者从未追求柏拉图式完备，仅要求"已对所有识别到的失效模式进行评估"（NQA-1 Req 11）。完备性因此被操作化为：

> 一个测试理论是完备的，当且仅当它在任意时刻均能清晰声明自身不完备之所在。

**可证伪性**与**边界显式性**因此构成完备性的工程接口。

### 1.3 本文贡献

1. 提出基于三支柱架构的 MT 完整公理化体系，涵盖 SCP、PP、SML 三类程序；
2. 建立 MR 测试与经典变异测试之间的同构映射，由此获得形式化充分性理论的遗传；
3. 构造 $(l, p, \varphi)$ 立方体闭合性作为可证伪的完备性断言，并证明五大核心定理；
4. 建立理论框架与 NQA-1、RG 1.203、FMECA、PIRT 的结构同构映射表，实现研究成果向工程 V&V 主流的可传递性。

---

## 2. 符号系统

### 2.1 基础集合与程序对象

| 符号 | 含义 |
|------|------|
| $\mathcal{X}, \mathcal{Y}$ | 输入空间、输出空间 |
| $P : \mathcal{X} \to \mathcal{Y}$ | 待测程序 |
| $\left[\!\left[ P \right]\!\right]$ | 程序 $P$ 的语义（输入—输出映射） |
| $\tau \in \{\mathrm{SCP}, \mathrm{PP}, \mathrm{SML}\}$ | 程序类型标签 |

### 2.2 蜕变关系相关

| 符号 | 含义 |
|------|------|
| $m = (R^m_{\mathrm{in}}, R^m_{\mathrm{out}})$ | 单条 MR |
| $R^m_{\mathrm{in}} \subseteq \mathcal{X} \times \mathcal{X}$ | MR 的输入关系 |
| $R^m_{\mathrm{out}} \subseteq \mathcal{Y} \times \mathcal{Y}$ | MR 的输出关系 |
| $T_R : \mathcal{Y} \to \mathcal{Y}$ | 由 $R^m_{\mathrm{out}}$ 派生的输出变换 |
| $M = \{m_1, \ldots, m_N\}$ | MR 集合 |

### 2.3 三支柱要素

| 符号 | 含义 |
|------|------|
| $\Lambda = \{L_1, L_2, L_3, L_4\}$ | 层次拓扑（支柱 I） |
| $\Pi = \{P_1, P_2, P_3, P_4, P_5\}\ [\cup\ \{P_6, P_7\}]$ | 元模式集合（支柱 II），方括号表候选扩展 |
| $F = \{\varphi_1, \ldots, \varphi_K\}$ | 故障模型（支柱 III） |
| $\mu_\varphi : \mathcal{P} \to \mathcal{P}$ | 故障注入算子 |
| $\ell : \mathcal{M} \to \Lambda$ | MR 的层次归属函数 |
| $p : \mathcal{M} \to \Pi$ | MR 的元模式归属函数 |

### 2.4 测试集、判等与度量

| 符号 | 含义 |
|------|------|
| $S \subseteq \mathcal{X}$ | 源测试用例集 |
| $\mathrm{Eq}_\tau$ | 类型参数化判等算子 |
| $\varepsilon_\tau$ | 类型参数化容差 |
| $\mathrm{viol}_\tau(m, s, P)$ | MR 违反谓词 |
| $\mathrm{det}_\tau(m, \varphi, S)$ | 故障检出力 |
| $\mathrm{MMS}(M, F, S)$ | MR 变异得分 |
| $\mathcal{C} = \Lambda \times \Pi \times F$ | 三维工程化立方体 |

---

## 3. 本体论基础

### 3.1 程序类型学

**定义 3.1（三类程序）**。本理论涵盖以下三类程序：

- **SCP**：以偏微分方程、常微分方程或积分方程的离散化为核心、输出确定性数值场的程序；
- **PP**：以概率模型与推断算法（MCMC、VI 等）为核心、输出概率分布或其样本的程序；
- **SML**：以可训练参数化模型为核心、在数据上训练并提供代理预测的程序。

三类程序的输出本体论存在根本差异：SCP 输出位于 $\mathbb{R}^n$；PP 输出为概率测度；SML 输出为带有泛化误差界的数值。此差异被完全吸收于类型参数化判等算子 $\mathrm{Eq}_\tau$（见 3.3 节）。

**备注 3.1（混合程序）**。数字孪生中的 SCP+SML 耦合、UQ 驱动仿真中的 PP 包裹 SCP、贝叶斯代理模型中的 PP+SML 嵌入等混合程序，不构成新的独立类型，而是通过算子组合 $\mathrm{Eq}_{\tau_1 \otimes \tau_2}$ 处理。

### 3.2 蜕变关系的形式化定义

**定义 3.2（MR）**。一条蜕变关系 $m$ 是一个二元组

$$m = \bigl(R^m_{\mathrm{in}},\ R^m_{\mathrm{out}}\bigr),$$

其中 $R^m_{\mathrm{in}} \subseteq \mathcal{X} \times \mathcal{X}$ 规定允许的源—跟随输入对，$R^m_{\mathrm{out}} \subseteq \mathcal{Y} \times \mathcal{Y}$ 规定对应输出对必须满足的约束。

**定义 3.3（MR 满足）**。程序 $P$ 在输入对 $(s, s') \in R^m_{\mathrm{in}}$ 上满足 $m$，当且仅当

$$\mathrm{Eq}_\tau\bigl(\left[\!\left[ P \right]\!\right](s),\ \left[\!\left[ P \right]\!\right](s'),\ R^m_{\mathrm{out}}\bigr) = \top .$$

### 3.3 类型参数化判等算子

**定义 3.4（$\mathrm{Eq}_\tau$）**。判等算子根据 $\tau$ 取下列三态之一：

$$
\mathrm{Eq}_\tau(y_1, y_2, R) \triangleq
\begin{cases}
\bigl\lVert y_1 - T_R(y_2) \bigr\rVert < \varepsilon_{\mathrm{numeric}}, & \tau = \mathrm{SCP} \\[6pt]
\mathcal{D}\bigl(y_1,\ T_R(y_2)\bigr) < \varepsilon_{\mathrm{stat}}, & \tau = \mathrm{PP} \\[6pt]
\bigl\lVert y_1 - T_R(y_2) \bigr\rVert < \varepsilon_{\mathrm{surrogate}}(x), & \tau = \mathrm{SML}
\end{cases}
$$

其中 $\mathcal{D}$ 为概率测度距离（如 Kolmogorov–Smirnov 距离、Wasserstein 距离），$\varepsilon_{\mathrm{surrogate}}(x)$ 为依赖输入的泛化误差上界（由共形预测或 PAC-Bayes 界给出）。

**命题 3.1（容差来源）**。

- $\varepsilon_{\mathrm{numeric}}$：机器精度加离散化截断误差；
- $\varepsilon_{\mathrm{stat}}$：有限样本统计涨落加预设显著性水平；
- $\varepsilon_{\mathrm{surrogate}}(x)$：输入依赖的泛化误差上界。

---

## 4. 三支柱架构

三支柱分别回答三个本体问题：MR 从哪里来（支柱 I）、MR 长什么样（支柱 II）、MR 要抓什么（支柱 III）。

### 4.1 支柱 I：层次拓扑（Where）

**定义 4.1（层次拓扑）**。MR 的生成源域被划分为四个层次：

$$\Lambda = \{L_1: \text{数学物理模型},\ L_2: \text{数值方法},\ L_3: \text{软件实现},\ L_4: \text{运行轨迹}\}.$$

层次拓扑具有偏序结构 $L_1 \prec L_2 \prec L_3 \prec L_4$，其中 $\prec$ 表示从抽象到具体的语义距离。

层次拓扑构成 MR 的**生成性语义库**，回答"MR 从何而来"。

### 4.2 支柱 II：元模式矩阵（What）

**定义 4.2（元模式核心骨架）**。元模式是 MR 在数学结构层面的类型学分类。核心骨架由五项构成：

| 元模式 | 名称 | 数学对应 |
|--------|------|---------|
| $P_1$ | 守恒性（Conservation） | 群作用下的代数不变性 |
| $P_2$ | 单调性（Monotonicity） | 偏序集之间的保序映射 |
| $P_3$ | 收敛性（Convergence） | 极限过程的拓扑行为 |
| $P_4$ | 轨迹性（Trajectory） | 序列/路径的几何约束 |
| $P_5$ | 偏序性（Partial Order） | 保真度/精度的格结构 |

**定义 4.3（候选扩展元模式）**。$P_6$（校准性，Calibration，跨 PP/SML）与 $P_7$（外推降级，Extrapolation Degradation，SML 独有）为待经验验证的候选扩展。

**命题 4.1（核心骨架跨类型共享）**。$P_1$ 至 $P_5$ 在 SCP、PP、SML 中均存在结构对应（详见附录 A）；然而强度不一：$P_4$ 在三类中均普适；$P_5$ 在 SML 中需条件化为 $P_5'$；$P_2$ 在 SML 中存在双下降（double descent）反例；$P_3$ 在 SML 中需分叉为优化收敛与统计收敛两支。

元模式矩阵构成 MR 的**形态语义库**，回答"MR 长什么样"。

### 4.3 支柱 III：故障模型（Why）

**定义 4.4（故障模型）**。故障模型 $F$ 是一组故障注入算子的参数化集合：

$$F = \{\varphi_1, \ldots, \varphi_K\},\quad \forall \varphi \in F:\ \mu_\varphi \in \mathcal{P} \to \mathcal{P},\ P_\varphi = \mu_\varphi(P).$$

**定义 4.5（类型特化故障模型）**。

- **SCP**：$\varphi_{\mathrm{disc}}$（离散化截断）、$\varphi_{\mathrm{round}}$（浮点舍入累积）、$\varphi_{\mathrm{bc}}$（边界条件误处理）、$\varphi_{\mathrm{par}}$（并行同步/归约缺陷）、$\varphi_{\mathrm{iter}}$（迭代收敛判据错误）；
- **PP**：$\varphi_{\mathrm{prior}}$（先验错配）、$\varphi_{\mathrm{irrev}}$（推断器不可逆）、$\varphi_{\mathrm{prop}}$（proposal 有偏）、$\varphi_{\mathrm{burnin}}$（burn-in 不足）、$\varphi_{\mathrm{mix}}$（链混合失败）；
- **SML**：$\varphi_{\mathrm{leak}}$（数据泄漏）、$\varphi_{\mathrm{overfit}}$（过拟合）、$\varphi_{\mathrm{shift}}$（分布偏移）、$\varphi_{\mathrm{sym}}$（对称性破坏）、$\varphi_{\mathrm{phys}}$（物理约束违反）、$\varphi_{\mathrm{extrap}}$（外推失效）。

故障模型构成 MR 的**目标语义库**，回答"MR 要抓什么"。

### 4.4 三维立方体与矩阵覆盖

**定义 4.6（工程化立方体）**。每条工程化 MR 对应立方体 $\mathcal{C} = \Lambda \times \Pi \times F$ 上的一点 $(l, p, \varphi) \in \mathcal{C}$。MR 集合 $M$ 的立方体覆盖率定义为：

$$\mathrm{CellCov}(M) \triangleq \frac{\bigl|\{(l, p, \varphi) \in \mathcal{C} : \exists m \in M,\ \bigl(\ell(m), p(m), \mathrm{Target}(m)\bigr) = (l, p, \varphi)\}\bigr|}{|\mathcal{C}|}.$$

---

## 5. 形式化度量与充分性

### 5.1 违反谓词与检出力

**定义 5.1（MR 违反谓词）**。

$$\mathrm{viol}_\tau(m, s, P) \triangleq \exists\, s' \in \mathcal{X} : (s, s') \in R^m_{\mathrm{in}} \ \land\ \lnot\,\mathrm{Eq}_\tau\bigl(\left[\!\left[ P \right]\!\right](s),\ \left[\!\left[ P \right]\!\right](s'),\ R^m_{\mathrm{out}}\bigr).$$

**定义 5.2（故障检出力）**。

$$\mathrm{det}_\tau(m, \varphi, S) \triangleq \exists\, s \in S : \mathrm{viol}_\tau(m, s, P_\varphi) \ \land\ \lnot\,\mathrm{viol}_\tau(m, s, P).$$

**备注 5.1（差分检出）**。定义的关键在于差分结构：仅当 $m$ 在故障程序 $P_\varphi$ 上违反、而在原程序 $P$ 上不违反时，才算作真正检出。这排除了平凡 MR 导致的假阳性。

### 5.2 MR 质量属性

| 属性 | 形式化定义 | 释义 |
|------|-----------|------|
| 平凡 | $\mathrm{Triv}(m) \triangleq \forall P,\forall s:\ \lnot\,\mathrm{viol}_\tau(m, s, P)$ | 对任何程序任何输入恒不违反 |
| 等价变异 | $\mathrm{EqvMut}(m, \varphi) \triangleq \forall S:\ \lnot\,\mathrm{det}_\tau(m, \varphi, S)$ | $\varphi$ 位于 $m$ 的语义零空间 |
| F-盲 | $\mathrm{Blind}(m, F, S) \triangleq \forall \varphi \in F:\ \lnot\,\mathrm{det}_\tau(m, \varphi, S)$ | 对 $F$ 内所有故障检出力为零 |
| F-有效 | $\mathrm{Eff}(m, F, S) \triangleq \exists \varphi \in F:\ \mathrm{det}_\tau(m, \varphi, S)$ | 至少检出一类故障 |
| 冗余 | $\mathrm{Red}(m, M, F, S) \triangleq \mathrm{Comp}(M \setminus \{m\},\ F,\ S)$ | 移除不影响完备性 |

### 5.3 充分性层级

**定义 5.3（单故障充分性）**。$\mathrm{Adeq}(M, \varphi, S) \iff \exists\, m \in M:\ \mathrm{det}_\tau(m, \varphi, S).$

**定义 5.4（故障模型完备性）**。$\mathrm{Comp}(M, F, S) \iff \forall\, \varphi \in F:\ \mathrm{Adeq}(M, \varphi, S).$

**定义 5.5（最小完备性）**。

$$\mathrm{MinComp}(M, F, S) \iff \mathrm{Comp}(M, F, S)\ \land\ \forall\, M' \subsetneq M:\ \lnot\,\mathrm{Comp}(M', F, S).$$

### 5.4 MR 变异得分与质量向量

**定义 5.6（可观测故障子集）**。设 $F_{\mathrm{unobs}}$ 为不可观测故障子集（输出粗糙度导致），$F_{\mathrm{unreach}}$ 为 MR 不可及故障子集（$M$ 结构局限导致），则

$$F_{\mathrm{obs}} \triangleq F \setminus (F_{\mathrm{unobs}} \cup F_{\mathrm{unreach}}).$$

**定义 5.7（MMS）**。

$$\mathrm{MMS}(M, F, S) \triangleq \frac{\bigl|\{\varphi \in F_{\mathrm{obs}} : \mathrm{Adeq}(M, \varphi, S)\}\bigr|}{|F_{\mathrm{obs}}|}.$$

**定义 5.8（质量向量）**。

$$\mathbf{Q}(M, F, S) \triangleq \bigl(\mathrm{CellCov}(M),\ \mathrm{MMS}(M, F, S),\ |M|\bigr) \in [0, 1]^2 \times \mathbb{N}.$$

**工程优化目标**：

$$M^* = \arg\min_{M}\, |M|\quad \text{s.t.}\quad \mathrm{CellCov}(M) = 1\ \land\ \mathrm{MMS}(M, F, S) = 1.$$

---

## 6. 核心定理

### 6.1 同构继承定理

**定理 6.1（同构继承）**。存在显式结构映射 $\Phi : \mathcal{T}_{\mathrm{MT}} \to \mathcal{T}_{\mathrm{Mutation}}$，使 MR 测试的充分性理论同构于经典变异测试：

| MR 测试 | 经典变异测试 |
|---------|-------------|
| 故障注入算子 $\mu_\varphi$ | 变异算子 |
| 故障程序 $P_\varphi$ | 变异体 $P'$ |
| $\mathrm{det}_\tau(m, \varphi, S)$ | 测试用例"杀死"$P'$ |
| 等价变异 MR | 等价变异体 |
| F-盲 MR | 无效测试用例 |
| $\mathrm{MMS}$ | 变异得分 $\mathrm{MS}$ |
| F-完备 MR 集 | 变异充分测试集 |
| 最小完备 MR 集 | 最小变异充分测试集 |

**证明概要**。同构 $\Phi$ 通过保持检出关系的结构被完全确立：$\mathrm{det}_\tau$ 对应"杀死"关系；$\mathrm{Adeq}$ 对应变异充分性；$\mathrm{MMS}$ 对应 $\mathrm{MS}$。经典变异测试已证结果（耦合效应假设、competent programmer hypothesis 等）在 MR 测试中具有对偶表达。$\square$

**推论 6.1**。MT 的形式化充分性理论继承了经典变异测试近四十年的成熟结果，包括 NP-难性、近似算法与实证基线。

### 6.2 对偶定理

**定义 6.1（MR-故障二部图）**。

$$\mathcal{G}(M_{\mathrm{cand}}, F, S) = (M_{\mathrm{cand}} \cup F,\ E),\quad (m, \varphi) \in E \iff \mathrm{det}_\tau(m, \varphi, S).$$

**定理 6.2（对偶）**。最小完备 MR 集等价于 $\mathcal{G}$ 的最小支配集：

$$\mathrm{MinComp}(M^*, F, S) \iff M^*\ \text{为}\ \mathcal{G}\ \text{的最小支配集}.$$

**证明**。完备性条件 $\mathrm{Comp}(M, F, S)$ 要求 $F$ 中每个节点被 $M$ 中至少一个节点支配（即存在边连接）；最小性即支配集规模最小。结构同构。$\square$

**推论 6.2（计算复杂度）**。最小完备 MR 集求解为 NP-难问题。存在 $\mathcal{O}(\log|F|)$ 的贪心近似算法（Chvátal 1979）。

### 6.3 单调性定理

**定理 6.3（单调性）**。$\mathrm{MMS}$ 对 $M$ 与 $S$ 的扩张均单调非降：

$$M_1 \subseteq M_2\ \Rightarrow\ \mathrm{MMS}(M_1, F, S) \leq \mathrm{MMS}(M_2, F, S),$$

$$S_1 \subseteq S_2\ \Rightarrow\ \mathrm{MMS}(M, F, S_1) \leq \mathrm{MMS}(M, F, S_2).$$

**证明**。由 $\mathrm{Adeq}$ 的存在量词结构 $\exists\, m \in M, \exists\, s \in S$，扩张覆盖仅可能增加被满足的故障数，不可能减少。$\square$

### 6.4 类型不变性定理

**定理 6.4（类型不变性）**。第 5 节所有定义在 $\tau \in \{\mathrm{SCP}, \mathrm{PP}, \mathrm{SML}\}$ 下形式不变，类型特异性被完全吸收于 $\mathrm{Eq}_\tau$ 与 $\mu_\varphi$ 的类型特化实例。

**证明**。检视定义 5.1 至 5.8，唯一依赖 $\tau$ 的原子谓词是 $\mathrm{Eq}_\tau$；其余皆为布尔组合与计数操作。替换 $\tau$ 仅改变底层判等语义，不改变上层逻辑结构。$\square$

**推论 6.3**。跨程序类型的理论统一无需重造上层公理，仅需在 $\mathrm{Eq}_\tau$ 层实现类型适配。

### 6.5 必要非充分性定理

**定理 6.5（必要非充分性）**。

$$\mathrm{Comp}(M, F, S) \ \not\Rightarrow\ \mathrm{Correctness}(P).$$

**证明**。反例构造。存在 $P^\dagger \neq P^{\mathrm{true}}$ 使 $\forall\, m \in M, \forall\, s \in S: \lnot\,\mathrm{viol}_\tau(m, s, P^\dagger)$，因为 $M$ 仅覆盖 $F$ 内故障类；超出 $F$ 的故障模式 $\varphi^\ddagger \notin F$ 可使 $P^\dagger$ 在 MR 集下保持"看似正确"。$\square$

**备注 6.1**。本定理不是理论缺陷，而是**边界的显式声明**。MT 始终是正确性论证的**必要条件检测器**，而非充分性保证器。该定理与核 V&V 传统中"测试不能证明程序无错"（Dijkstra 立场）完全一致。

### 6.6 闭合性断言与可证伪性

**猜想 6.1（$(l, p, \varphi)$ 立方体闭合性）**。对任意实际工程中出现的 MR $m$，其在立方体 $\mathcal{C} = \Lambda \times \Pi \times F$ 上有唯一归属：

$$\forall\, m \in M_{\mathrm{engineering}}:\ \exists!\ (l, p, \varphi) \in \mathcal{C}:\ m\ \text{realizes}\ (l, p, \varphi).$$

**可证伪性条件**。若存在无法归类到 $\mathcal{C}$ 的"孤儿 MR"，则猜想被证伪，需扩展 $\Lambda$ 或 $\Pi$。

---

## 7. 四层完备性论证

### 7.1 论证分层

| 层级 | 论证类型 | 强度 | 代表结论 |
|------|---------|------|---------|
| L-I | 演绎完备 | 严格证明 | 定理 6.1–6.5 |
| L-II | 结构完备 | 准形式化 | W-问题穷尽、猜想 6.1 |
| L-III | 经验饱和完备 | 归纳 | $\Pi$ 与 $F$ 的穷尽性 |
| L-IV | 监管完备 | 结构同构 | 与 NQA-1、RG 1.203、FMECA、PIRT 的映射 |

### 7.2 L-I：演绎完备性

通过定理 6.1（同构继承），MT 继承经典变异测试的形式结构；定理 6.2（对偶）将完备性求解归约为组合优化经典问题；定理 6.4（类型不变性）使跨类型推广无需重做公理系统；定理 6.5（必要非充分性）显式固定理论边界。

### 7.3 L-II：结构完备性

**W-问题穷尽论证**。任何测试活动必须回答三个本体问题：

- *Where does it come from?* $\to$ 支柱 I（层次拓扑）；
- *What does it look like?* $\to$ 支柱 II（元模式）；
- *What does it target?* $\to$ 支柱 III（故障模型）。

若存在第四本体问题 $Q_4$ 无法被三支柱吸收，则结构完备性被证伪。当前文献综述未发现此类 $Q_4$。

**立方体闭合性的可证伪结构**。每条工程化 MR 均可表示为 $\mathcal{C}$ 上的点，每次 V&V 活动均可表示为 $\mathcal{C}$ 的一个切片。闭合性若被孤儿 MR 证伪，则理论体系被显式告知扩展需求。

### 7.4 L-III：经验饱和完备性

$\Pi$ 的穷尽性依赖扎根理论（Grounded Theory）五阶段归纳方法（详见附录 B）。候选语料包括 OpenMC、MCNP、DeCART（SCP），Stan、Pyro（PP），PINN-bench（SML）。此层完备性是 Popper 意义上的"迄今未被证伪"，而非演绎必然。

### 7.5 L-IV：监管完备性

核工程 V&V 传统从不追求 Platonic 完备，仅要求可审计完备。**NQA-1 Req 11** 要求"已对所有识别到的失效模式进行评估"——与 F-完备性 $\mathrm{Comp}(M, F, S)$ 在定义结构上**完全同构**（见第 8 节）。

### 7.6 综合立场

> 完备性证明的实质**不是穷尽一切可能故障，而是在任何时刻均能清晰声明自身不完备之所在**。

可证伪性与边界显式性构成完备性的操作化定义，亦即完备性的工程接口。

---

## 8. 工程应用与监管对接

### 8.1 理论—监管结构同构映射

**表 8.1 理论—监管映射表**

| 理论要素 | ASME NQA-1 | NRC RG 1.203 | IEEE 7-4.3.2 | FMECA |
|---------|-----------|--------------|--------------|-------|
| 支柱 I（层次拓扑） | Part II Req 3（软件工程过程） | 生命周期阶段 | Clause 5 | — |
| 支柱 II（元模式） | — | PIRT 现象分类 | 验收准则分类 | 失效机理 |
| 支柱 III（故障模型 $F$） | Req 11（失效模式评估） | PIRT 排序 | — | 失效模式库 |
| F-完备性 | Req 11（全覆盖要求） | — | V&V 充分性 | 危害度矩阵 |
| $\mathrm{MMS}$ | — | — | 测试充分性报告 | RPN 评分 |
| 必要非充分性定理 | 独立验证原则 | 纵深防御 | — | — |

### 8.2 测试充分性报告模板

基于本理论体系，**测试充分性报告**应包含如下结构化内容：

1. **立方体覆盖声明**：列出工程化 MR 集 $M$ 在 $\mathcal{C} = \Lambda \times \Pi \times F$ 上的覆盖切片；
2. **MMS 报告**：在可观测故障子集 $F_{\mathrm{obs}}$ 上的 $\mathrm{MMS}$ 值，附 $F_{\mathrm{unobs}}$ 与 $F_{\mathrm{unreach}}$ 的显式声明；
3. **最小完备性声明**：$M^*$ 是否为 $\mathcal{G}$ 最小支配集的近似解，及近似算法的选择；
4. **边界显式性声明**：本次 V&V 所覆盖的故障类与**未覆盖**的故障类，及后者的风险影响评估；
5. **独立验证声明**：基于定理 6.5，声明本报告不构成正确性证明，仅为必要条件检测结果。

### 8.3 与 FMECA 的衔接流程

FMECA 已在核工程中建立成熟的失效模式目录。将其嵌入 MT 理论的流程为：

1. **导入**：FMECA 失效模式列表 $\to F$；
2. **映射**：每条失效模式 $\to \varphi \in F$；
3. **目标化**：为每条 $\varphi$ 设计对应的故障注入算子 $\mu_\varphi$；
4. **MR 生成**：在 $\Lambda \times \Pi$ 矩阵上识别可检出 $\varphi$ 的候选 MR；
5. **最小完备优化**：求解 $M^* = \arg\min_M |M|\ \text{s.t.}\ \mathrm{Comp}(M, F, S) = 1$；
6. **反馈**：运行中发现的新故障类反哺 FMECA 与 $F$。

该流程使 MT 理论成为 FMECA 方法论的**定量测试延伸**，而非并列方法。

### 8.4 研究—工程双循环

本理论体系在研究端与工程端之间建立了可操作的双循环：

- **自下而上（监管 $\to$ 研究）**：FMECA/PIRT 导出 $F$；NQA-1 Req 11 导出完备性要求；RG 1.203 导出层次分解原则；
- **自上而下（研究 $\to$ 监管）**：$\mathrm{MMS}$ 提供可审计的定量指标；立方体覆盖提供结构化报告格式；最小完备性提供成本优化依据。

---

## 9. 局限性与扩展方向

### 9.1 理论层局限

1. **$\Pi$ 的完备性仍为猜想**。$P_1$–$P_7$ 的穷尽性依赖经验饱和，未有演绎证明。
2. **$F$ 的开放性**。故障模型随工程实践演化，$\mathrm{MMS} = 1$ 非永恒完备。
3. **混合程序的跨类型故障传播**。当前类型不变性定理覆盖单类型；数字孪生、UQ 包络、贝叶斯代理等混合程序需独立研究。
4. **高阶变异对 $\mathrm{MMS}$ 的影响**。单故障注入不捕获故障间耦合。

### 9.2 方法论层局限

1. **$\mu^m$ 与 $\mu_\varphi$ 的区分**。MR 变异算子 $\mu^m$（作用于 MR 自身以测试 MR 鲁棒性）与故障注入算子 $\mu_\varphi$（作用于程序以评估 MR 检出力）形式对称但工程语义不同。
2. **算子经济性**。SCP 仿真代价高昂；单位 $\mu_\varphi$ 的 mutant 生成成本与其检出增量的 ROI 尚未形式化。

### 9.3 扩展方向

- **新程序类型**：量子程序、神经符号 AI 程序的 $\mathrm{Eq}_\tau$ 定义；
- **监管语言扩展**：ISO 26262（汽车）、DO-178C（航空）的对接；
- **自动化工具链**：基于本理论的 ScMT-Mut 工具包、自动 MR 生成器与立方体可视化器。

---

## 10. 结论

本文提出了基于三支柱架构的蜕变测试完备性理论体系，明确区分演绎完备、结构完备、经验饱和完备与监管完备四种层级，并给出类型参数化的核心定理集。理论体系通过立方体闭合性猜想与 $(l, p, \varphi)$ 可证伪性，在研究与工程之间建立了可审计的映射通道。

核心立场可凝练如下：

> **MT 完备性的实质不是穷尽可能故障，而是在任何时刻均能清晰声明自身不完备之所在。**

可证伪性与边界显式性构成完备性的操作化定义——这正是核工程 V&V 传统所要求的监管完备性形态。未来工作将围绕 $\Pi$ 的穷尽性证伪实验、混合程序的跨类型故障传播理论、以及基于本理论的工具链工程化展开。

---

## 参考文献（选录）

1. Chen, T. Y., Cheung, S. C., & Yiu, S. M. (1998). *Metamorphic testing: A new approach for generating next test cases*. Technical Report HKUST-CS98-01, Hong Kong University of Science and Technology.
2. Offutt, A. J. (1991). *Investigations of the software testing coupling effect*. ACM Transactions on Software Engineering and Methodology, 1(1): 5–20.
3. Jia, Y., & Harman, M. (2011). *An analysis and survey of the development of mutation testing*. IEEE Transactions on Software Engineering, 37(5): 649–678.
4. Segura, S., Fraser, G., Sanchez, A. B., & Ruiz-Cortés, A. (2016). *A survey on metamorphic testing*. IEEE Transactions on Software Engineering, 42(9): 805–824.
5. Kanewala, U., & Bieman, J. M. (2014). *Testing scientific software: A systematic literature review*. Information and Software Technology, 56(10): 1219–1232.
6. Chvátal, V. (1979). *A greedy heuristic for the set-covering problem*. Mathematics of Operations Research, 4(3): 233–235.
7. ASME NQA-1 (2019). *Quality Assurance Requirements for Nuclear Facility Applications*. The American Society of Mechanical Engineers.
8. U.S. Nuclear Regulatory Commission (2005). *Regulatory Guide 1.203: Transient and Accident Analysis Methods*.
9. IEEE Std 7-4.3.2 (2016). *Standard Criteria for Digital Computers in Safety Systems of Nuclear Power Generating Stations*. IEEE.

---

## 附录 A：三类程序验证矩阵

### A.1 SCP 验证矩阵

| | $L_1$ 数学物理模型 | $L_2$ 数值方法 | $L_3$ 软件实现 | $L_4$ 运行轨迹 |
|---|---|---|---|---|
| **$P_1$ 守恒** | 质量/能量/动量/概率守恒 | 离散守恒格式 | 并行归约一致性 | 逐步守恒量稳定性 |
| **$P_2$ 单调** | 物理参数方向性 | 单调格式 TVD | 输入规模单调 | 单调量轨迹 |
| **$P_3$ 收敛** | 极限解析行为 | 离散化精化收敛阶 | 迭代求解器容差 | 时间步进渐近 |
| **$P_4$ 轨迹** | 对称响应、周期保持 | 算法步进形态 | 日志序列模式 | 状态演化形态 |
| **$P_5$ 偏序** | 模型精度排序 | 算法精度排序 | 实现变体排序 | 多保真输出偏序 |

### A.2 PP 验证矩阵

| | $L_1$ 概率模型 | $L_2$ 推断方法 | $L_3$ 软件实现 | $L_4$ 采样轨迹 |
|---|---|---|---|---|
| **$P_1$ 守恒** | 概率归一化、边际一致性 | MCMC detailed balance、ELBO 下界 | 多链 log-prob 并行归约 | 各链后验统计量一致 |
| **$P_2$ 单调** | 似然对充分统计量单调、熵单调 | 退火温度 $\downarrow \Rightarrow$ KL 单调下降 | 样本数 $\uparrow \Rightarrow$ ESS 单调 | 接受率随步长单调响应 |
| **$P_3$ 收敛** | BvM、后验契约 | 几何遍历性、VI 收敛阶 | $\hat{R} < 1.01$、ESS 阈值 | 迹图混合、burn-in 平稳 |
| **$P_4$ 轨迹** | 可交换性、马氏链可逆性 | 对称 proposal、HMC 能量守恒 | reproducibility | 迹图形态 |
| **$P_5$ 偏序** | 精确推断 $\geq$ VI $\geq$ Laplace | HMC $\geq$ MALA $\geq$ RW-MH | 双精度 $\geq$ 单精度 | 多保真推断距离偏序 |

### A.3 SML 验证矩阵

| | $L_1$ 代理目标 | $L_2$ 训练算法 | $L_3$ 软件实现 | $L_4$ 训练/推理轨迹 |
|---|---|---|---|---|
| **$P_1$ 守恒** | 物理守恒律保持（PINN、硬约束）、数据集总概率 | 分布式梯度归约、loss 加权和守恒 | 并行 dataloader 覆盖一致性 | 守恒损失项稳定下降 |
| **$P_2$ 单调** | 输入扰动与预测方向一致 | lr schedule 单调、loss 下降 | 数据量 $\uparrow \Rightarrow$ 泛化误差 $\downarrow$ | epoch $\uparrow \Rightarrow$ 验证指标改善 |
| **$P_3$ 收敛** | 容量 $\uparrow \Rightarrow$ 模型收敛至真模型 | 优化器收敛、early stopping | 训练容差、checkpoint 可复现 | loss 曲线渐近 |
| **$P_4$ 轨迹** | 等变性（旋转/平移/置换）、周期保持 | SGD 路径在对称变换下等价 | 推理对 batch 顺序不变 | loss 曲线形态、梯度范数 |
| **$P_5$ 偏序** | 高保真数据 $\geq$ 低保真；物理嵌入 $\geq$ 黑箱 | 大模型 $\geq$ 小模型、精调 $\geq$ 零样本 | FP32 $\geq$ FP16 | 多保真预测误差偏序 |

---

## 附录 B：元模式归纳的扎根理论五阶段

**阶段 1（语料构建）**：每类程序收集 $\geq 50$ 条 MR，盲审式录入，双研究者独立提取，确保覆盖 $L_1$–$L_4$ 四个层次。

**阶段 2（开放编码）**：编码维度包括变换类型（缩放、平移、置换、条件化等）、保持量（值、分布、形状、秩序、拓扑、信息量等）、关系类型（等式、不等式、偏序、分布等价等）、约束强度（严格/统计/近似）、定义域条件。

**阶段 3（聚类归纳）**：定性手工聚类结合多重对应分析（MCA）与层次聚类。已有元模式应呈现为稠密簇，候选新元模式表现为现有簇之外的稠密子群。

**阶段 4（判据审查）**：候选元模式须通过下列五项判据方可升格：

1. **数学结构抽象性**：对应抽象数学结构，而非具体物理/算法细节；
2. **跨层次性**：能贯穿 $L_1$–$L_4$ 每一层；
3. **检错力独立性**：与现有模式捕获故障集近似正交；
4. **实例密度**：语料中 $\geq 5\%$ MR 可归入；
5. **生成性**：能为新程序生成 MR 候选，而非仅分类既有 MR。

**阶段 5（理论饱和检验）**：保留 $20\%$ 验证集，若归类为孤儿的 MR 比例 $< 10\%$，则判定 $\Pi$ 在当前语料范围内饱和。

---

## 附录 C：故障符号索引

| 符号 | 含义 | 所属类型 |
|------|------|---------|
| $\varphi_{\mathrm{disc}}$ | 离散化截断误差 | SCP |
| $\varphi_{\mathrm{round}}$ | 浮点舍入累积 | SCP |
| $\varphi_{\mathrm{bc}}$ | 边界条件误处理 | SCP |
| $\varphi_{\mathrm{par}}$ | 并行同步/归约缺陷 | SCP |
| $\varphi_{\mathrm{iter}}$ | 迭代收敛判据错误 | SCP |
| $\varphi_{\mathrm{prior}}$ | 先验错配 | PP |
| $\varphi_{\mathrm{irrev}}$ | 推断器不可逆 | PP |
| $\varphi_{\mathrm{prop}}$ | proposal 有偏 | PP |
| $\varphi_{\mathrm{burnin}}$ | burn-in 不足 | PP |
| $\varphi_{\mathrm{mix}}$ | 链混合失败 | PP |
| $\varphi_{\mathrm{leak}}$ | 数据泄漏 | SML |
| $\varphi_{\mathrm{overfit}}$ | 过拟合 | SML |
| $\varphi_{\mathrm{shift}}$ | 分布偏移 | SML |
| $\varphi_{\mathrm{sym}}$ | 等变/对称性破坏 | SML |
| $\varphi_{\mathrm{phys}}$ | 物理约束违反 | SML |
| $\varphi_{\mathrm{extrap}}$ | 外推失效 | SML |

---

*文档版本*：统一版 v1.0  
*编制日期*：2026 年 4 月  
*适用范围*：科学计算程序、概率程序、机器学习代理模型程序的 V&V 理论框架与监管报告编制  
*研究—工程桥接*：ICSE / IST / ANE / Progress in Nuclear Energy 理论投稿及核软件 V&V 报告编制
