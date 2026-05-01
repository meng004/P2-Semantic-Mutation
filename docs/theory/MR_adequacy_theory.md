# 蜕变测试充分性理论：一个统一的形式化框架

## 摘要

本文借鉴经典变异测试（Mutation Testing）的充分性理论体系，为蜕变测试（Metamorphic Testing, MT）建立一套跨程序类型的充分性形式化框架。框架以语义故障模型为锚点，严格定义平凡蜕变关系（Trivial MR）、等价变异蜕变关系（Equivalent-Mutant MR）、F-充分性（F-Adequacy）、F-完备性（F-Completeness）以及最小完备蜕变关系集（Minimal Complete MR Set）等核心概念，并给出面向科学计算程序（SCP）、概率程序（PP）与机器学习代理模型程序（SML）三类程序的统一实例化接口。该框架既保持与 DeMillo–Lipton–Sayward 变异测试理论的结构同构，又充分反映蜕变测试特有的"多执行–关系判定"语义。

---

## 1. 符号约定与预备定义

### 1.1 基础符号

令 $P : \mathcal{X} \to \mathcal{Y}$ 为待测程序，$\llbracket P \rrbracket$ 表示其指称语义。设 $\mathcal{P}$ 为所有语法合法程序构成的空间，$P \in \mathcal{P}$。

令 $\tau \in \mathcal{T} = \{\mathrm{SCP}, \mathrm{PP}, \mathrm{SML}\}$ 表示程序类型（科学计算、概率程序、机器学习代理模型）。

### 1.2 蜕变关系的形式化

**定义 1（蜕变关系）**  一个蜕变关系（Metamorphic Relation, MR）是一个二元组

$$
m \;\triangleq\; \big(R^m_{\mathrm{in}},\, R^m_{\mathrm{out}}\big),
$$

其中 $R^m_{\mathrm{in}} \subseteq \mathcal{X} \times \mathcal{X}$ 为输入关系，$R^m_{\mathrm{out}} \subseteq \mathcal{Y} \times \mathcal{Y}$ 为输出关系，且满足语义规约

$$
\forall (x, x') \in R^m_{\mathrm{in}} : \; \big(\llbracket P \rrbracket(x),\, \llbracket P \rrbracket(x')\big) \in R^m_{\mathrm{out}}.
$$

记所有合法 MR 构成的集合为 $\mathcal{M}$。一个有限 MR 集合 $M \subseteq \mathcal{M}$ 是本文充分性分析的基本对象。

### 1.3 判等算子的类型多态

由于三类程序对"输出相等"的语义不同，定义类型参数化判等算子 $\mathrm{Eq}_\tau$：

$$
\mathrm{Eq}_\tau\!\left(y_1, y_2, R\right) \;\triangleq\;
\begin{cases}
(y_1, y_2) \in R, & \tau = \mathrm{SCP} \\[4pt]
\mathcal{D}\!\left(y_1, y_2\right) < \varepsilon_{\mathrm{stat}}\ \text{at level}\ \alpha, & \tau = \mathrm{PP} \\[4pt]
\left\lVert y_1 - T_R(y_2) \right\rVert \leq \varepsilon_{\mathrm{surr}}(x), & \tau = \mathrm{SML}
\end{cases}
$$

其中 $\mathcal{D}(\cdot, \cdot)$ 为分布距离（如 KS、Wasserstein、KL），$\varepsilon_{\mathrm{surr}}(x)$ 为位置相关的代理模型误差界（可由共形预测或 PAC-Bayes 给出）。

### 1.4 违反谓词

**定义 2（MR 违反）**  给定 MR $m$、源测试用例 $s \in \mathcal{X}$、程序 $P$ 与类型 $\tau$，违反谓词定义为

$$
\mathrm{viol}_\tau(m, s, P) \;\triangleq\; \exists\, s' \in \mathcal{X} : (s, s') \in R^m_{\mathrm{in}} \;\land\; \lnot\, \mathrm{Eq}_\tau\!\left(\llbracket P \rrbracket(s),\, \llbracket P \rrbracket(s'),\, R^m_{\mathrm{out}}\right).
$$

---

## 2. 故障模型

### 2.1 语义故障类

借鉴变异测试中"变异算子"的思想，但将其从句法层提升至语义层。

**定义 3（故障注入算子）**  故障注入算子是一个程序变换映射

$$
\mu_\varphi : \mathcal{P} \to \mathcal{P}, \qquad P \mapsto P_\varphi \triangleq \mu_\varphi(P),
$$

其中 $\varphi$ 标识一个**语义故障类**（semantic fault class），刻画三类程序中被蜕变关系可捕获的典型缺陷模式。

**定义 4（故障模型）**  一个故障模型是一个有限语义故障类集合

$$
F = \{\varphi_1, \varphi_2, \ldots, \varphi_K\}, \qquad F \subseteq \Phi_\tau,
$$

其中 $\Phi_\tau$ 为类型 $\tau$ 对应的故障类全集。

### 2.2 三类程序的故障模型实例

类型 $\tau$ 对应的故障模型 $\Phi_\tau$ 分别实例化为：

$$
\Phi_{\mathrm{SCP}} = \{\varphi_{\mathrm{disc}}, \varphi_{\mathrm{round}}, \varphi_{\mathrm{bc}}, \varphi_{\mathrm{par}}, \varphi_{\mathrm{iter}}, \ldots\}
$$
$$
\Phi_{\mathrm{PP}} = \{\varphi_{\mathrm{prior}}, \varphi_{\mathrm{irrev}}, \varphi_{\mathrm{prop}}, \varphi_{\mathrm{burnin}}, \varphi_{\mathrm{mix}}, \ldots\}
$$
$$
\Phi_{\mathrm{SML}} = \{\varphi_{\mathrm{leak}}, \varphi_{\mathrm{overfit}}, \varphi_{\mathrm{shift}}, \varphi_{\mathrm{sym}}, \varphi_{\mathrm{phys}}, \varphi_{\mathrm{extrap}}, \ldots\}
$$

（各符号含义详见附录 A。）

### 2.3 故障模型的对齐性

**元性质 1（对齐性, Alignment）**  故障模型 $F$ 相对于真实缺陷分布 $\mathcal{D}_{\mathrm{real}}$ 是 $\theta$-对齐的，当且仅当

$$
\Pr_{\varphi \sim \mathcal{D}_{\mathrm{real}}}\!\left[\, \exists\, \varphi' \in F : \varphi \equiv_{\mathrm{sem}} \varphi' \,\right] \;\geq\; \theta,
$$

其中 $\equiv_{\mathrm{sem}}$ 为语义等价关系，$\theta \in (0, 1]$ 由领域专家设定。

对齐性是充分性理论的外部前提，它保证了下述内部度量的工程意义。

---

## 3. 核心概念：MR 质量的五类属性

仿照变异测试区分"等价变异体（equivalent mutants）"与"有效变异体（effective mutants）"的思路，此处对 MR 与故障之间的交互作出细粒度分类。

### 3.1 MR 对单个故障的检出力

**定义 5（故障检出力, Fault Detection）**  给定 MR $m$、故障类 $\varphi$、源测试用例集 $S \subseteq \mathcal{X}$ 及程序类型 $\tau$，$m$ 相对于 $\varphi$ 在 $S$ 上的检出力为

$$
\boxed{\;
\mathrm{det}_\tau(m, \varphi, S) \;\triangleq\; \exists\, s \in S : \;
\mathrm{viol}_\tau(m, s, P_\varphi) \;\land\; \lnot\, \mathrm{viol}_\tau(m, s, P).
\;}
$$

第二合取项排除了 MR 在原程序上即已违反的情形，从而避免假阳性。

### 3.2 平凡 MR

**定义 6（平凡蜕变关系, Trivial MR）**  MR $m$ 是**平凡的**，当且仅当其输出关系在语义上等价于恒等，即

$$
\mathrm{Triv}(m) \;\iff\; \forall P \in \mathcal{P},\; \forall s \in \mathcal{X}:\; \lnot\, \mathrm{viol}_\tau(m, s, P).
$$

记平凡 MR 全集为 $\mathcal{M}_{\mathrm{triv}} \subset \mathcal{M}$。平凡 MR 对任何故障模型的检出力恒为零：

$$
\forall m \in \mathcal{M}_{\mathrm{triv}},\; \forall \varphi,\; \forall S:\; \mathrm{det}_\tau(m, \varphi, S) = \bot.
$$

### 3.3 等价变异 MR

此概念是变异测试中"等价变异体"在蜕变测试语境下的对偶物。

**定义 7（等价变异蜕变关系, Equivalent-Mutant MR）**  MR $m$ 相对于故障类 $\varphi$ 是**等价变异的**，当且仅当故障注入后 $m$ 仍被满足，即

$$
\mathrm{EqvMut}(m, \varphi) \;\iff\; \forall s \in \mathcal{X}:\; \lnot\, \mathrm{viol}_\tau(m, s, P_\varphi).
$$

这意味着故障 $\varphi$ 位于 MR $m$ 的**语义零空间**（semantic kernel）中，无论如何选取测试用例都无法通过 $m$ 暴露 $\varphi$。

### 3.4 F-盲 MR

**定义 8（F-盲, F-blind）**  MR $m$ 相对于故障模型 $F$ 在测试用例集 $S$ 上是 **F-盲的**，当且仅当

$$
\mathrm{Blind}(m, F, S) \;\iff\; \forall \varphi \in F:\; \lnot\, \mathrm{det}_\tau(m, \varphi, S).
$$

F-盲是一个比平凡性更弱、但对具体故障模型仍无揭错能力的性质。由定义直接得到：

$$
\mathrm{Triv}(m) \;\Longrightarrow\; \forall F, S:\; \mathrm{Blind}(m, F, S).
$$

反之不成立：一个非平凡 MR 可能恰好对某个 $F$ 全部盲。

### 3.5 F-有效 MR

**定义 9（F-有效, F-effective）**  MR $m$ 是 **F-有效的**，当且仅当

$$
\mathrm{Eff}(m, F, S) \;\iff\; \exists\, \varphi \in F:\; \mathrm{det}_\tau(m, \varphi, S).
$$

显然 $\mathrm{Eff}(m, F, S) \iff \lnot\, \mathrm{Blind}(m, F, S)$。

---

## 4. 充分性理论

### 4.1 单故障充分性

**定义 10（对 $\varphi$ 的充分性, $\varphi$-Adequacy）**  MR 集合 $M \subseteq \mathcal{M}$ 在测试用例集 $S$ 下对故障类 $\varphi$ 是**充分的**，当且仅当

$$
\boxed{\;
\mathrm{Adeq}(M, \varphi, S) \;\iff\; \exists\, m \in M:\; \mathrm{det}_\tau(m, \varphi, S).
\;}
$$

### 4.2 故障模型层级的完备性

**定义 11（F-完备性, F-Completeness）**  MR 集合 $M$ 在 $S$ 下对故障模型 $F$ 是**完备的**，当且仅当

$$
\boxed{\;
\mathrm{Comp}(M, F, S) \;\iff\; \forall \varphi \in F:\; \mathrm{Adeq}(M, \varphi, S).
\;}
$$

这是变异测试中"杀死所有非等价变异体"（killing all non-equivalent mutants）的蜕变版本。

### 4.3 不可观测与 MR-不可及故障

借鉴变异测试对"等价变异体"的处理，定义两类应从分母中剔除的故障：

$$
F_{\mathrm{unobs}} = \big\{\varphi \in F : \forall s \in \mathcal{X},\; \llbracket P_\varphi \rrbracket(s) = \llbracket P \rrbracket(s)\big\},
$$

$$
F_{\mathrm{unreach}} = \big\{\varphi \in F : \forall m \in \mathcal{M},\; \mathrm{EqvMut}(m, \varphi)\big\}.
$$

前者对应**不可观测故障**（句法变异但语义不变），后者对应**MR-不可及故障**（所有 MR 都对其盲）。定义**可观测故障模型**

$$
F_{\mathrm{obs}} \;\triangleq\; F \,\setminus\, \big(F_{\mathrm{unobs}} \cup F_{\mathrm{unreach}}\big).
$$

### 4.4 MR-变异得分

**定义 12（MR-变异得分, MR-Mutation Score）**  MR 集合 $M$ 在 $S$ 下对故障模型 $F$ 的变异得分为

$$
\boxed{\;
\mathrm{MMS}(M, F, S) \;=\; \frac{\big|\{\varphi \in F_{\mathrm{obs}} : \mathrm{Adeq}(M, \varphi, S)\}\big|}{\big|F_{\mathrm{obs}}\big|}.
\;}
$$

显然 $\mathrm{MMS}(M, F, S) \in [0, 1]$，且

$$
\mathrm{Comp}(M, F, S) \;\iff\; \mathrm{MMS}(M, F, S) = 1.
$$

这是变异测试 Mutation Score 在蜕变测试的直接推广。

### 4.5 完备性的谱

由 MMS 诱导 MR 集合完备性的谱状划分：

$$
\mathrm{MMS}(M, F, S) =
\begin{cases}
0 & \Longrightarrow M\text{ 是 } F\text{-盲集合} \\
\in (0, 1) & \Longrightarrow M\text{ 是部分 F-充分} \\
1 & \Longrightarrow M\text{ 是 F-完备} \\
\end{cases}
$$

---

## 5. 最小完备 MR 集

### 5.1 定义

**定义 13（最小完备性, Minimal Completeness）**  MR 集合 $M$ 对故障模型 $F$ 在 $S$ 下是**最小完备**的，当且仅当

$$
\boxed{\;
\mathrm{MinComp}(M, F, S) \;\iff\; \mathrm{Comp}(M, F, S)\ \land\ \forall\, M' \subsetneq M:\; \lnot\,\mathrm{Comp}(M', F, S).
\;}
$$

### 5.2 冗余 MR

**定义 14（冗余 MR, Redundant MR）**  MR $m \in M$ 相对于 $F$ 是冗余的，当且仅当

$$
\mathrm{Red}(m, M, F, S) \;\iff\; \mathrm{Comp}(M, F, S)\ \land\ \mathrm{Comp}(M \setminus \{m\}, F, S).
$$

由此得到最小完备性的等价刻画：

**命题 1**  $\mathrm{MinComp}(M, F, S) \iff \mathrm{Comp}(M, F, S) \land \forall m \in M:\; \lnot\,\mathrm{Red}(m, M, F, S).$

### 5.3 MR-故障对偶与支配集问题

**定义 15（MR-故障二部图）**  给定候选 MR 集合 $M_{\mathrm{cand}}$、故障模型 $F$ 与测试用例集 $S$，构造二部图

$$
\mathcal{G}(M_{\mathrm{cand}}, F, S) \;=\; (M_{\mathrm{cand}} \cup F, E), \qquad
E = \big\{(m, \varphi) : \mathrm{det}_\tau(m, \varphi, S)\big\}.
$$

**定理 1（对偶定理）**  $M \subseteq M_{\mathrm{cand}}$ 是 $F$ 的最小完备 MR 集合，当且仅当 $M$ 是二部图 $\mathcal{G}$ 中 $F$ 侧节点的**最小支配集**（minimum dominating set）。

**推论 1**  最小完备 MR 集合构造问题为 NP-难；存在 $\mathcal{O}(\log |F|)$ 因子贪心近似算法。

---

## 6. 与识别支柱的耦合：双维度覆盖

蜕变测试的整体质量由两个正交维度联合刻画：

### 6.1 识别维度：矩阵覆盖

设 $\Pi = \{P_1, \ldots, P_5\}$ 为五大元模式，$\Lambda = \{L_1, \ldots, L_4\}$ 为四层抽象层次。每条 MR 归属一个单元格 $c(m) \in \Pi \times \Lambda$。

$$
\mathrm{CellCov}(M) \;=\; \frac{\big|\{c(m) : m \in M\}\big|}{\big|\Pi \times \Lambda\big|}.
$$

### 6.2 评估维度：变异得分

如定义 12。

### 6.3 联合质量向量

**定义 16（MR 集合质量向量）**

$$
\mathbf{Q}(M, F, S) \;=\; \big(\mathrm{CellCov}(M),\; \mathrm{MMS}(M, F, S),\; |M|\big) \;\in\; [0,1]^2 \times \mathbb{N}.
$$

工程实践上追求

$$
\arg\min_{M \subseteq \mathcal{M}} |M| \quad \text{s.t.} \quad \mathrm{CellCov}(M) = 1 \,\land\, \mathrm{MMS}(M, F, S) = 1.
$$

该多目标优化对应支配集问题在双约束下的扩展。

---

## 7. 与变异测试经典理论的同构映射

| 变异测试概念 | 蜕变测试对应物 | 本文定义编号 |
|---|---|---|
| 变异算子 $\mu$ | 故障注入算子 $\mu_\varphi$ | 定义 3 |
| 变异体 $P'$ | 故障程序 $P_\varphi$ | 定义 3 |
| 测试用例 $t$ 杀死 $P'$ | MR $m$ 检出 $\varphi$ | 定义 5 |
| 等价变异体 | 等价变异 MR | 定义 7 |
| 无效测试用例 | F-盲 MR | 定义 8 |
| 变异得分 $\mathrm{MS}$ | MR-变异得分 $\mathrm{MMS}$ | 定义 12 |
| 变异充分测试集 | F-完备 MR 集 | 定义 11 |
| 最小变异充分测试集 | 最小完备 MR 集 | 定义 13 |

本理论的结构同构性使其能无缝接入现有软件测试充分性话语体系，同时其语义故障模型基底又保持了蜕变测试相对于变异测试的独立性。

---

## 8. 理论基本性质

**定理 2（单调性）**  充分性、完备性、变异得分对 MR 集合扩张单调：

$$
M_1 \subseteq M_2 \implies
\begin{cases}
\mathrm{Adeq}(M_1, \varphi, S) \implies \mathrm{Adeq}(M_2, \varphi, S), \\[2pt]
\mathrm{Comp}(M_1, F, S) \implies \mathrm{Comp}(M_2, F, S), \\[2pt]
\mathrm{MMS}(M_1, F, S) \leq \mathrm{MMS}(M_2, F, S).
\end{cases}
$$

**定理 3（测试用例单调性）**  充分性对源测试用例集扩张单调：

$$
S_1 \subseteq S_2 \implies \mathrm{MMS}(M, F, S_1) \leq \mathrm{MMS}(M, F, S_2).
$$

**定理 4（类型不变性）**  定义 5–16 的结构在 $\tau \in \{\mathrm{SCP}, \mathrm{PP}, \mathrm{SML}\}$ 下形式不变；类型特异性完全吸收于 $\mathrm{Eq}_\tau$ 算子。

**定理 5（必要非充分性）**  即使 $\mathrm{MMS}(M, F, S) = 1$，仍可能存在 $\varphi^* \notin F$ 使程序真实错误不被检出：

$$
\mathrm{Comp}(M, F, S) \not\Rightarrow \text{Correctness}(P).
$$

此定理明确了蜕变测试的边界：充分性是相对于 $F$ 而言的，绝对正确性需要 $F \equiv \Phi_\tau$ 且 $\Phi_\tau$ 与真实缺陷分布完全对齐，这在现实中不可达。

---

## 9. 工程化使用协议

整合前三节，给出"按图索骥"的六步法：

1. **类型判定** $\tau \leftarrow$ 程序输出语义分类
2. **故障模型实例化** $F \leftarrow \Phi_\tau$ 的工程子集，并论证 $\theta$-对齐性（元性质 1）
3. **候选 MR 生成** $M_{\mathrm{cand}} \leftarrow$ 层次拓扑 $\times$ 元模式矩阵扫描
4. **检出力计算** 构造二部图 $\mathcal{G}(M_{\mathrm{cand}}, F, S)$（定义 15）
5. **最小完备集求解** 贪心近似 $M^\star \leftarrow \arg\min |M|$ s.t. $\mathrm{Comp}(M, F, S)$
6. **质量向量报告** $\mathbf{Q}(M^\star, F, S)$（定义 16）

---

## 10. 结语

本文提出的蜕变测试充分性理论以语义故障模型为第三支柱，与已有的层次拓扑（MR 来源库）和元模式（MR 形态库）共同构成三维框架。理论在保持与变异测试经典理论结构同构的同时，通过判等算子的类型多态化与故障模型的语义化，将其统一推广至科学计算程序、概率程序与机器学习代理模型三类程序。平凡 MR、等价变异 MR、F-盲 MR、F-充分、F-完备、最小完备 MR 集等概念形成一个紧致的形式化词汇表，使工程实务中"MR 设计是否足够"这一核心问题首次获得可计算、可审查、可度量的回答。

---

## 附录 A：三类程序故障模型符号释义

| 符号 | 含义 | 类型 |
|---|---|---|
| $\varphi_{\mathrm{disc}}$ | 离散化截断误差 | SCP |
| $\varphi_{\mathrm{round}}$ | 浮点舍入累积 | SCP |
| $\varphi_{\mathrm{bc}}$ | 边界条件误处理 | SCP |
| $\varphi_{\mathrm{par}}$ | 并行同步/归约缺陷 | SCP |
| $\varphi_{\mathrm{iter}}$ | 迭代收敛判据错误 | SCP |
| $\varphi_{\mathrm{prior}}$ | 先验错配 | PP |
| $\varphi_{\mathrm{irrev}}$ | 推断器不可逆 | PP |
| $\varphi_{\mathrm{prop}}$ | Proposal 有偏 | PP |
| $\varphi_{\mathrm{burnin}}$ | Burn-in 不足 | PP |
| $\varphi_{\mathrm{mix}}$ | 链混合失败 | PP |
| $\varphi_{\mathrm{leak}}$ | 数据泄漏 | SML |
| $\varphi_{\mathrm{overfit}}$ | 过拟合 | SML |
| $\varphi_{\mathrm{shift}}$ | 分布偏移 | SML |
| $\varphi_{\mathrm{sym}}$ | 等变/对称性破坏 | SML |
| $\varphi_{\mathrm{phys}}$ | 物理约束违反 | SML |
| $\varphi_{\mathrm{extrap}}$ | 外推失效 | SML |

---

## 附录 B：核心概念速查

| 概念 | 形式化符号 | 含义 |
|---|---|---|
| 平凡 MR | $\mathrm{Triv}(m)$ | 对任何程序、任何输入恒不违反 |
| 等价变异 MR | $\mathrm{EqvMut}(m, \varphi)$ | 故障 $\varphi$ 位于 $m$ 的语义零空间 |
| F-盲 MR | $\mathrm{Blind}(m, F, S)$ | 对 $F$ 内所有故障检出力为零 |
| F-有效 MR | $\mathrm{Eff}(m, F, S)$ | 至少检出 $F$ 中一类故障 |
| 故障检出力 | $\mathrm{det}_\tau(m, \varphi, S)$ | $m$ 在 $S$ 上检出 $\varphi$ |
| $\varphi$-充分 | $\mathrm{Adeq}(M, \varphi, S)$ | $M$ 中至少一条 MR 检出 $\varphi$ |
| F-完备 | $\mathrm{Comp}(M, F, S)$ | $M$ 对 $F$ 内每类故障均充分 |
| 最小完备 | $\mathrm{MinComp}(M, F, S)$ | 去除任何一条均破坏完备性 |
| 冗余 MR | $\mathrm{Red}(m, M, F, S)$ | 从 $M$ 中移除不影响完备性 |
| 变异得分 | $\mathrm{MMS}(M, F, S)$ | 被检出的可观测故障比例 |
| 矩阵覆盖 | $\mathrm{CellCov}(M)$ | 元模式 $\times$ 层次矩阵覆盖率 |
| 质量向量 | $\mathbf{Q}(M, F, S)$ | $(\mathrm{CellCov}, \mathrm{MMS}, |M|)$ 三元组 |
