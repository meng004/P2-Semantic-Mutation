# MT 理论框架（优选整合版）

## 1. 核心主张

**完备的蜕变测试（Metamorphic Testing, MT）理论，不是“穷尽一切可能错误”的绝对完备，而是相对于给定程序域、故障模型与观测语义的**相对完备**。

其最简而完整的表达为：

> **三支柱 + 两类闭合 + 一套度量 + 一个边界声明**
>
> - 三支柱：层次拓扑、元模式、故障模型；
> - 两类闭合：识别闭合、目标闭合；
> - 一套度量：`CellCov`、`Adeq`、`Comp`、`MMS`、`Q`；
> - 一个边界声明：$\operatorname{Comp}(M,F,S) \nRightarrow \operatorname{Correct}(P)$。

这一定义保留了三份稿件的共同内核：**三支柱骨架**、**相对完备性立场**、**类型参数化统一**、**可计算的充分性度量**，同时删除了过重的论文式展开，使之更适合作为后续论文、项目与工具实现的统一总纲。

---

## 2. 研究对象与基本符号

### 2.1 研究对象

本文框架统一覆盖三类程序：

- **SCP**：Scientific Computing Programs，科学计算程序；
- **PP**：Probabilistic Programs，概率程序；
- **SML**：Surrogate Machine Learning Programs，代理模型/机器学习程序。

三类程序共享“测试预言机不足”这一根本特征，但输出语义不同，因此需要统一高层框架、参数化底层判等。

### 2.2 基本符号

- $\mathcal{X}$：输入空间；
- $\mathcal{Y}$：输出空间；
- $P: \mathcal{X} \to \mathcal{Y}$：待测程序；
- $\left[\!\left[ P \right]\!\right]$：程序语义；
- $m=(R_{in}^m,R_{out}^m)$：一条蜕变关系（MR）；
- $M=\{m_1,\dots,m_n\}$：MR 集；
- $F=\{\varphi_1,\dots,\varphi_K\}$：故障模型；
- $S \subseteq \mathcal{X}$：源测试集；
- $\tau \in \{\mathrm{SCP},\mathrm{PP},\mathrm{SML}\}$：程序类型；
- $\Lambda$：层次拓扑集合；
- $\Pi$：元模式集合。

---

## 3. 第一支柱：层次拓扑（MR 从哪里来）

层次拓扑用于回答：**MR 的来源是什么**。

定义四层来源空间：

$$
\Lambda = \{L_1,L_2,L_3,L_4\}
$$

其中：

- $L_1$：数学/物理/概率模型层；
- $L_2$：数值方法/推断方法/训练算法层；
- $L_3$：软件实现层；
- $L_4$：运行轨迹层。

定义来源映射：

$$
\sigma: \mathcal{M} \to \Lambda
$$

若 MR 具有跨层性质，可扩展为多值映射：

$$
\sigma^*: \mathcal{M} \to 2^{\Lambda}
$$

### 定义 1：来源闭合性

若对任意合法 MR $m \in \mathcal{M}$，都存在某个层次 $L_i$ 使得 $\sigma(m)=L_i$，或 $L_i \in \sigma^*(m)$，则称层次拓扑对 MR 宇宙是**来源闭合**的。

**作用**：把 MR 的发现从“凭经验想关系”转变为“按来源分层搜索关系”。

---

## 4. 第二支柱：元模式（MR 长什么样）

元模式用于回答：**MR 的结构类型是什么**。

### 4.1 核心元模式

建议采用“**5 个核心 + 2 个扩展**”的分层设计。

#### 核心 5 模式

$$
\Pi_{core}=\{P_1,P_2,P_3,P_4,P_5\}
$$

- $P_1$：**守恒**（Conservation）
- $P_2$：**单调**（Monotonicity）
- $P_3$：**收敛**（Convergence）
- $P_4$：**轨迹**（Trajectory）
- $P_5$：**偏序**（Partial Order）

#### 扩展 2 模式

$$
\Pi_{ext}=\{P_6,P_7\}
$$

- $P_6$：**校准性**（Calibration），主要服务于 PP / SML；
- $P_7$：**外推降级**（Extrapolation Degradation），主要服务于 SML。

于是总元模式集为：

$$
\Pi = \Pi_{core} \cup \Pi_{ext}
$$

### 4.2 结构映射

定义结构映射：

$$
\pi: \mathcal{M} \to \Pi
$$

### 定义 2：结构闭合性

若对任意合法 MR $m \in \mathcal{M}$，都存在某个元模式 $P_j \in \Pi$ 使得 $\pi(m)=P_j$，则称元模式集合对 MR 宇宙是**结构闭合**的。

**作用**：把大量零散 MR 归并为少数可复用的结构原型。

---

## 5. 第三支柱：故障模型（MR 要捕获什么）

故障模型用于回答：**MT 的目标故障是什么**。

定义故障模型：

$$
F=\{\varphi_1,\varphi_2,\dots,\varphi_K\}
$$

其中每个 $\varphi_k$ 表示一类语义故障，而不是单个句法变异体。

### 5.1 典型故障族

- **SCP**：离散化误差、边界条件误处理、并行归约错误、迭代终止判据错误；
- **PP**：先验错配、proposal 偏置、详细平衡破坏、链混合失败；
- **SML**：数据泄漏、过拟合、分布偏移、对称性破坏、物理约束违反、外推失效。

### 5.2 故障注入算子

定义故障注入算子：

$$
\mu_{\varphi}: \mathcal{P} \to \mathcal{P}, \qquad P_{\varphi}=\mu_{\varphi}(P)
$$

它把“故障模型”变成可执行对象，从而把 MT 充分性问题转化为可计算的检出问题。

### 定义 3：目标闭合性

若所有被关注故障都被纳入某个显式定义的 $F$ 中，则称该理论在当前研究设定下满足**目标闭合**。

---

## 6. 三支柱的统一定位

任意工程化 MR 都应能被定位到一个三元单元：

$$
\eta(m)=(\sigma(m),\pi(m),\rho(m)) \in \Lambda \times \Pi \times F
$$

其中 $\rho(m)$ 表示该 MR 的主目标故障类。

这意味着：

- 层次拓扑给出 **来源解释**；
- 元模式给出 **结构解释**；
- 故障模型给出 **目标解释**。

三者共同构成 MT 理论的最小完整骨架。

---

## 7. 类型参数化判等（跨类型统一的关键）

三类程序输出语义不同，因此“MR 是否满足”不能使用单一判等准则，而应采用类型参数化判等算子：

$$
\mathrm{Eq}_{\tau}(y_1,y_2,R_{out}^m)
$$

典型实现为：

$$
\mathrm{Eq}_{\tau}(y_1,y_2,R)=
\begin{cases}
\|y_1-T_R(y_2)\|<\varepsilon_{numeric}, & \tau=\mathrm{SCP} \\
\mathcal{D}(y_1,T_R(y_2))<\varepsilon_{stat}, & \tau=\mathrm{PP} \\
\|y_1-T_R(y_2)\|<\varepsilon_{surrogate}(x), & \tau=\mathrm{SML}
\end{cases}
$$

其中：

- $T_R$：由输出关系诱导的输出变换；
- $\mathcal{D}$：分布距离或统计检验准则；
- $\varepsilon$：相应类型的容差。

> 注：SML 行中的右花括号在不少草稿中容易排版出错，正式论文中应写为
> $\|y_1-T_R(y_2)\|<\varepsilon_{surrogate}(x)$。

**要点**：高层定义保持统一，类型差异被吸收到 $\mathrm{Eq}_{\tau}$ 中。

---

## 8. 充分性度量体系

### 8.1 MR 违反谓词

$$
\mathrm{viol}_{\tau}(m,s,P)
\triangleq
\exists s' \in \mathcal{X}: (s,s')\in R_{in}^m \land \neg \mathrm{Eq}_{\tau}(\left[\!\left[ P \right]\!\right](s),\left[\!\left[ P \right]\!\right](s'),R_{out}^m)
$$

### 8.2 故障检出力

$$
\mathrm{det}_{\tau}(m,\varphi,S)
\triangleq
\exists s \in S:\mathrm{viol}_{\tau}(m,s,P_{\varphi}) \land \neg \mathrm{viol}_{\tau}(m,s,P)
$$

该定义强调“差分检出”：MR 必须能区分原程序与故障程序。

### 8.3 充分性层级

单故障充分性：

$$
\mathrm{Adeq}(M,\varphi,S) \iff \exists m \in M:\mathrm{det}_{\tau}(m,\varphi,S)
$$

故障模型完备性：

$$
\mathrm{Comp}(M,F,S) \iff \forall \varphi \in F,\ \mathrm{Adeq}(M,\varphi,S)
$$

最小完备性：

$$
\mathrm{MinComp}(M,F,S) \iff \mathrm{Comp}(M,F,S) \land \forall M'\subsetneq M,\ \neg \mathrm{Comp}(M',F,S)
$$

### 8.4 两个核心指标

#### 1）识别覆盖率

定义 MR 在“层次 × 元模式”上的覆盖率：

$$
\mathrm{CellCov}(M)=\frac{|\{(\sigma(m),\pi(m)):m\in M\}|}{|\Lambda \times \Pi_{target}|}
$$

它衡量 **MR 识别是否全面**。

#### 2）MR 变异得分

设可观测故障集为：

$$
F_{obs}=F\setminus(F_{unobs}\cup F_{unreach})
$$

则：

$$
\mathrm{MMS}(M,F,S)=\frac{|\{\varphi\in F_{obs}:\mathrm{Adeq}(M,\varphi,S)\}|}{|F_{obs}|}
$$

它衡量 **MR 集对目标故障的检出是否充分**。

### 8.5 质量向量

$$
\mathbf{Q}(M,F,S)=\bigl(\mathrm{CellCov}(M),\mathrm{MMS}(M,F,S),|M|\bigr)
$$

三维含义分别是：

- **广度**：识别覆盖；
- **力度**：故障检出；
- **成本**：MR 数量。

因此，MT 设计的最优化目标可写为：

$$
\arg\min_M |M|\quad \text{s.t.}\quad \mathrm{CellCov}(M)=1,\ \mathrm{MMS}(M,F,S)=1
$$

---

## 9. 完备性的最简定义

### 定义 4：相对完备的 MT 理论体系

给定程序域 $\mathcal{P}$、MR 宇宙 $\mathcal{M}$、故障模型 $F$、判等准则 $\mathrm{Eq}_{\tau}$ 与测试域 $\mathcal{S}$，若一套 MT 理论同时满足：

1. **来源闭合**：任意合法 MR 都可追溯到某个层次拓扑单元；
2. **结构闭合**：任意合法 MR 都可归入某个元模式；
3. **目标闭合**：任意关注故障都属于显式定义的故障模型；
4. **度量闭合**：检出力、充分性、完备性与最小性均可统一定义与计算；
5. **类型统一**：跨类型差异由 $\mathrm{Eq}_{\tau}$ 参数化吸收；

则称该体系在 $(\mathcal{P},\mathcal{M},F,\mathrm{Eq}_{\tau},\mathcal{S})$ 下是**相对完备的 MT 理论体系**。

---

## 10. 核心命题

### 命题 1：双支柱给出识别完备框架

若层次拓扑来源闭合，且元模式结构闭合，则二者共同构成 MR 的**识别完备框架**。

### 命题 2：第三支柱给出目标充分性语义

故障模型不是附属物，而是 MT 从“关系发现”走向“测试充分性论证”的关键桥梁。

### 命题 3：高层统一，底层参数化

MT 的跨类型统一性，不要求 SCP、PP、SML 拥有相同输出语义；它只要求高层逻辑结构一致，而把差异吸收到 $\mathrm{Eq}_{\tau}$、$F$ 与容差机制中。

### 命题 4：边界必须显式写出

$$
\mathrm{Comp}(M,F,S) \not\Rightarrow \mathrm{Correct}(P)
$$

这说明：

- MT 可以证明“在当前故障模型下未暴露已建模故障”；
- MT 不能推出“程序在更大故障空间中绝对正确”。

这不是缺陷，而是**完备性边界的诚实表达**。

---

## 11. 一个更稳健的“完备性”表述

建议采用下列表述作为理论总纲：

> **MT 的完备性不是绝对正确性的充分证明，而是相对于给定程序域、故障模型与观测语义的可审计完备性。**
>
> **一个 MT 理论是完备的，当且仅当它能够系统说明：MR 从哪里来、属于什么结构、面向哪些故障、如何计算其充分性，以及它在何处仍然不完备。**

这一表述兼容三份原稿中最强的部分：

- 保留了“三支柱”的骨架；
- 保留了“相对完备性”的严格边界；
- 保留了“类型参数化”的统一能力；
- 保留了“可证伪/可审计”的工程取向；
- 同时避免把总框架写成过重的长篇论文。

---

## 12. 推荐的最小使用流程

1. **确定程序域与类型**：SCP、PP 或 SML；
2. **构建 MR 候选集**：按 $L_1$–$L_4$ 分层抽取；
3. **完成元模式归类**：映射到 $P_1$–$P_5$，必要时扩展到 $P_6$、$P_7$；
4. **定义故障模型**：形成显式 $F$；
5. **设定判等规则**：实例化 $\mathrm{Eq}_{\tau}$；
6. **计算充分性矩阵**：得到 $\mathrm{det}_{\tau}(m,\varphi,S)$；
7. **报告质量向量**：输出 $\mathbf{Q}(M,F,S)$；
8. **声明边界**：明确 $F$、$F_{obs}$、未覆盖单元及未建模风险。

---

## 13. 结论

优中选优之后，最值得保留的 MT 理论框架不是“术语最多”的版本，也不是“证明最长”的版本，而是下面这一定式：

$$
\boxed{\text{MT 完备理论} = \text{层次拓扑} + \text{元模式} + \text{故障模型} + \text{类型参数化度量}}
$$

其中：

- **层次拓扑**保证 MR 来源可追溯；
- **元模式**保证 MR 结构可归类；
- **故障模型**保证测试目标可说明；
- **度量体系**保证充分性可计算；
- **边界声明**保证理论诚实、可审计、可扩展。

