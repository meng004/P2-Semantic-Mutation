# 蜕变测试统一验证框架：理论构建对话纪要

> **范围**：科学计算程序（SCP）、概率程序（PP）、机器学习代理模型程序（SML）
> **核心目标**：建立基于蜕变关系元模式的跨程序类型统一验证框架
> **文件用途**：供后续对话引用与研究路线参考

---

## 目录

- [一、研究背景与起点](#一研究背景与起点)
- [二、双支柱框架：层次拓扑 × 元模式矩阵](#二双支柱框架层次拓扑--元模式矩阵)
- [三、充分性理论缺口与第三支柱引入](#三充分性理论缺口与第三支柱引入)
- [四、形式化理论体系](#四形式化理论体系)
- [五、研究优先级：MR 变异算子 vs 故障模式库](#五研究优先级mr-变异算子-vs-故障模式库)
- [六、MR 变异算子的类型依赖性](#六mr-变异算子的类型依赖性)
- [七、元模式的跨类型普适性审查](#七元模式的跨类型普适性审查)
- [八、新元模式的系统归纳方法论](#八新元模式的系统归纳方法论)
- [九、投稿策略与研究路线图](#九投稿策略与研究路线图)
- [十、遗留问题与后续方向](#十遗留问题与后续方向)

---

## 一、研究背景与起点

### 1.1 初始命题

基于蜕变关系层次分类模型与蜕变关系元模式，为科学计算程序、概率程序和机器学习代理模型程序分别建立正确性验证框架。

### 1.2 核心认识

- 蜕变关系对应的物理约束是**必要条件**，非充分条件
- 测试通过不能得出程序无缺陷的结论
- 蜕变测试是现有测试技术的**补充**

### 1.3 Meng 已有积累

- 42 篇论文审计，提炼 57 条经验证 MR（trivial 16 / semi-trivial 19 / non-trivial 22）
- 五大元模式命名：**P1 守恒、P2 单调、P3 收敛、P4 轨迹、P5 偏序**
- MR 命名规范：`方程缩写-层级-编号`（如 `Bur-Phy-01`）
- 工程适用性评估：SCALE/ORIGEN 96%、OpenMC 91%、OpenMOC 94%

---

## 二、双支柱框架：层次拓扑 × 元模式矩阵

### 2.1 哲学依据

P1–P5 能跨越三类程序的根本原因：它们是**数学结构上的不变量**，先于"物理定律"存在——是数学本身提供的约束类型。

- P1 守恒 ≡ 不变性（群作用下的代数等式）
- P2 单调 ≡ 方向性（偏序集之间的保序映射）
- P3 收敛 ≡ 渐近性（极限过程的拓扑行为）
- P4 轨迹 ≡ 形态性（序列/路径的几何约束）
- P5 偏序 ≡ 层次性（精度/保真度的格结构）

### 2.2 双支柱定位

| 支柱 | 功能 | 隐喻 |
|---|---|---|
| **层次拓扑** (L1–L4) | MR 的**来源库** | "MR 从哪里来" |
| **元模式** (P1–P5) | MR 的**结构形态库** | "MR 长什么样" |

### 2.3 SCP 验证矩阵（Meng 已建立）

|             | L1 数学物理模型 | L2 数值方法 | L3 软件实现 | L4 运行轨迹 |
| ----------- | --------------- | ---------- | ---------- | ---------- |
| **P1 守恒** | 质量/能量/动量/概率守恒 | 离散守恒格式 | 并行归约一致性 | 逐步守恒量稳定性 |
| **P2 单调** | 物理参数方向性 | 单调格式 TVD | 输入规模单调 | 单调量轨迹 |
| **P3 收敛** | 极限解析行为 | 离散化精化收敛阶 | 迭代求解器容差 | 时间步进渐近 |
| **P4 轨迹** | 对称响应、周期保持 | 算法步进形态 | 日志序列模式 | 状态演化形态 |
| **P5 偏序** | 模型精度排序 | 算法精度排序 | 实现变体排序 | 多保真输出偏序 |

### 2.4 PP 验证矩阵

|             | L1 概率模型 | L2 推断方法 | L3 软件实现 | L4 采样轨迹 |
| ----------- | ---------- | ---------- | ---------- | ---------- |
| **P1 守恒** | 概率归一化、边际一致性 | MCMC detailed balance、ELBO 下界 | 多链 log-prob 并行归约 | 各链后验统计量一致 |
| **P2 单调** | 似然对充分统计量单调、熵单调 | 退火温度↓→KL 单调下降 | 样本数↑→ESS 单调 | 接受率随步长单调响应 |
| **P3 收敛** | Bernstein-von Mises、后验契约 | 几何遍历性、VI 收敛阶 | R-hat<1.01、ESS 阈值 | 迹图混合、burn-in 平稳 |
| **P4 轨迹** | 可交换性、马氏链可逆性 | 对称 proposal、HMC 能量守恒 | reproducibility | 迹图形态 |
| **P5 偏序** | 精确推断 ≥ VI ≥ Laplace | HMC ≥ MALA ≥ RW-MH | 双精度 ≥ 单精度 | 多保真推断距离偏序 |

### 2.5 SML 验证矩阵

|             | L1 代理目标 | L2 训练算法 | L3 软件实现 | L4 训练/推理轨迹 |
| ----------- | ---------- | ---------- | ---------- | ---------- |
| **P1 守恒** | 物理守恒律保持（PINN、硬约束）、数据集总概率 | 分布式梯度归约、loss 加权和守恒 | 并行 dataloader 覆盖一致性 | 守恒损失项稳定下降 |
| **P2 单调** | 输入扰动与预测方向一致 | lr schedule 单调、loss 下降 | 数据量↑→泛化误差↓ | epoch↑→验证指标改善 |
| **P3 收敛** | 容量↑模型收敛至真模型 | 优化器收敛、early stopping | 训练容差、checkpoint 可复现 | loss 曲线渐近 |
| **P4 轨迹** | 等变性（旋转/平移/置换）、周期保持 | SGD 路径在对称变换下等价 | 推理对 batch 顺序不变 | loss 曲线形态、梯度范数 |
| **P5 偏序** | 高保真数据 ≥ 低保真；物理嵌入 ≥ 黑箱 | 大模型 ≥ 小模型、精调 ≥ 零样本 | FP32 ≥ FP16 | 多保真预测误差偏序 |

### 2.6 同值判定规则（三类程序关键差异）

| 程序类型 | 检验准则 | 容差来源 |
|---|---|---|
| SCP | $|f(x') - T(f(x))| < \varepsilon_{\mathrm{numeric}}$ | 机器精度、离散化误差 |
| PP | $\mathcal{D}(p(x'), T(p(x))) < \varepsilon_{\mathrm{stat}}$ | 有限样本统计涨落、显著性水平 |
| SML | $|f(x') - T(f(x))| < \varepsilon_{\mathrm{surrogate}}(x)$ | 代理误差上界（共形预测、PAC-Bayes） |

---

## 三、充分性理论缺口与第三支柱引入

### 3.1 双支柱不构成充分性理论

- 双支柱是 **MR 识别的系统性覆盖理论**，保证识别完备性
- 不回答 Goodenough-Gerhart 式的充分性问题：测试集能否暴露故障

### 3.2 第三支柱：故障模型（Fault Model）

| 支柱 | 内容 |
|---|---|
| 支柱 1 · 层次拓扑 | MR **从哪里来**（Source Library） |
| 支柱 2 · 元模式 | MR **长什么样**（Pattern Library） |
| **支柱 3 · 故障模型** | MR **要抓什么**（Target Library） |

### 3.3 选择故障模型的五点理由

1. **逻辑通路**：从必要条件到充分论证的唯一路径
2. **学科对接**：对接变异测试（mutation testing）主流充分性度量
3. **核工程传统**：与 FMEA/FMECA 失效模式分析自然衔接
4. **类型差异化承载**：前两支柱提供通用性，第三支柱承载三类程序的故障差异
5. **可论证性**：让"测试通过"成为可审查的监管陈述

### 3.4 三维立方体框架

```
           故障模型（WHY）
              ↑
              │
              │  (m, l, φ) 三元组
              │
              └────→ 元模式（WHAT）
             /
            /
          层次拓扑（WHERE）
```

每条工程化 MR 是立方体上的点 `(层次, 元模式, 故障类)`。

---

## 四、形式化理论体系

### 4.1 核心符号

- $P : \mathcal{X} \to \mathcal{Y}$ 待测程序
- $m = (R^m_{\mathrm{in}}, R^m_{\mathrm{out}})$ 蜕变关系
- $\mu_\varphi : \mathcal{P} \to \mathcal{P}$ 故障注入算子，$P_\varphi = \mu_\varphi(P)$
- $F = \{\varphi_1, \ldots, \varphi_K\}$ 故障模型
- $S \subseteq \mathcal{X}$ 源测试用例集
- $\mathrm{Eq}_\tau$ 类型参数化判等算子（SCP/PP/SML 三态）

### 4.2 关键定义

**MR 违反谓词**：
$$\mathrm{viol}_\tau(m, s, P) \triangleq \exists s' \in \mathcal{X}: (s, s') \in R^m_{\mathrm{in}} \land \lnot \mathrm{Eq}_\tau(\llbracket P \rrbracket(s), \llbracket P \rrbracket(s'), R^m_{\mathrm{out}})$$

**故障检出力**：
$$\mathrm{det}_\tau(m, \varphi, S) \triangleq \exists s \in S: \mathrm{viol}_\tau(m, s, P_\varphi) \land \lnot \mathrm{viol}_\tau(m, s, P)$$

**五类 MR 质量属性**：

| 属性 | 形式化 | 含义 |
|---|---|---|
| 平凡 MR | $\mathrm{Triv}(m)$ | 对任何程序、任何输入恒不违反 |
| 等价变异 MR | $\mathrm{EqvMut}(m, \varphi)$ | 故障 $\varphi$ 位于 $m$ 的语义零空间 |
| F-盲 MR | $\mathrm{Blind}(m, F, S)$ | 对 $F$ 内所有故障检出力为零 |
| F-有效 MR | $\mathrm{Eff}(m, F, S)$ | 至少检出 $F$ 中一类故障 |
| 冗余 MR | $\mathrm{Red}(m, M, F, S)$ | 从 $M$ 中移除不影响完备性 |

**充分性层级**：

$$\mathrm{Adeq}(M, \varphi, S) \iff \exists m \in M: \mathrm{det}_\tau(m, \varphi, S) \quad \text{（单故障充分）}$$

$$\mathrm{Comp}(M, F, S) \iff \forall \varphi \in F: \mathrm{Adeq}(M, \varphi, S) \quad \text{（故障模型完备）}$$

$$\mathrm{MinComp}(M, F, S) \iff \mathrm{Comp}(M, F, S) \land \forall M' \subsetneq M: \lnot\mathrm{Comp}(M', F, S)$$

**MR-变异得分**：
$$\mathrm{MMS}(M, F, S) = \frac{|\{\varphi \in F_{\mathrm{obs}}: \mathrm{Adeq}(M, \varphi, S)\}|}{|F_{\mathrm{obs}}|}$$

其中 $F_{\mathrm{obs}} = F \setminus (F_{\mathrm{unobs}} \cup F_{\mathrm{unreach}})$ 剔除不可观测故障与 MR 不可及故障。

### 4.3 核心定理

- **对偶定理**：最小完备 MR 集 ⟺ MR-故障二部图的最小支配集（NP-难，存在 $\mathcal{O}(\log|F|)$ 贪心近似）
- **单调性定理**：$\mathrm{MMS}$ 对 $M$、$S$ 扩张单调
- **类型不变性定理**：定义结构在 $\tau$ 下形式不变，类型特异性吸收于 $\mathrm{Eq}_\tau$
- **必要非充分性定理**：$\mathrm{Comp}(M, F, S) \not\Rightarrow \mathrm{Correctness}(P)$

### 4.4 质量向量

$$\mathbf{Q}(M, F, S) = (\mathrm{CellCov}(M), \mathrm{MMS}(M, F, S), |M|) \in [0,1]^2 \times \mathbb{N}$$

工程目标：
$$\arg\min_M |M| \quad \text{s.t.} \quad \mathrm{CellCov}(M) = 1 \land \mathrm{MMS}(M, F, S) = 1$$

### 4.5 与变异测试经典理论的同构映射

| 变异测试 | 蜕变测试对应物 |
|---|---|
| 变异算子 $\mu$ | 故障注入算子 $\mu_\varphi$ |
| 变异体 $P'$ | 故障程序 $P_\varphi$ |
| 测试用例杀死 $P'$ | MR 检出 $\varphi$ |
| 等价变异体 | 等价变异 MR |
| 无效测试用例 | F-盲 MR |
| 变异得分 MS | MR-变异得分 MMS |
| 变异充分测试集 | F-完备 MR 集 |
| 最小变异充分测试集 | 最小完备 MR 集 |

---

## 五、研究优先级：MR 变异算子 vs 故障模式库

### 5.1 判断：MR 变异算子是更高杠杆的研究方向

- **故障模式库**是本体论对象（"SCP 会出什么错"）
- **MR 变异算子**是方法论工具（"如何系统制造这些错以评估 MR"）
- 两者是目的-手段关系，而非并列关系

### 5.2 MR 变异算子的五点理由

1. **填补文献真正空白**：经典变异工具（MuJava、PIT）都是句法级，与 MR 捕获的语义故障错配
2. **让充分性理论"跑起来"**：$\mathrm{MMS}$、$\mathrm{MinComp}$ 的计算都依赖可执行的 $\mu_\varphi$
3. **工具化潜力**：可沉淀为开源工具（对标 PIT），形成长期引用
4. **差异化创新**：需要同时理解 MR 数学结构、数值缺陷、变异算子设计，跨学科壁垒高
5. **理论对称性**：元模式是 MR 的生成语法，变异算子是故障的生成语法

### 5.3 故障模式库作为副产品

主线：MR 变异算子 → 方法论 + 工具
副产品：SCP/PP/SML 故障模式库 → 算子的经验基础
回路：算子运行在真实程序 → 发现新故障类 → 回填故障库 → 催生新算子

---

## 六、MR 变异算子的类型依赖性

### 6.1 核心判断：双层架构

**第 0 层（跨类型共享的语义原语）**：

| 原语 | 符号 | 对偶元模式 |
|---|---|---|
| 不变量破坏 | $\mu_{\mathrm{inv}}$ | P1 |
| 方向翻转 | $\mu_{\mathrm{dir}}$ | P2 |
| 极限畸变 | $\mu_{\mathrm{lim}}$ | P3 |
| 形态扰动 | $\mu_{\mathrm{shp}}$ | P4 |
| 偏序颠倒 | $\mu_{\mathrm{ord}}$ | P5 |

**第 1 层（类型特化实例）**：

| 原语 | SCP 实现 | PP 实现 | SML 实现 |
|---|---|---|---|
| $\mu_{\mathrm{inv}}$ | 有限差分注入非守恒通量、破坏 ODE 辛结构 | MCMC 破坏 detailed balance、VI ELBO 注入未归一项 | 移除 PINN 物理损失、破坏 E(3)-GNN 群作用 |

### 6.2 类型依赖性的三个根源

- **输出空间本体论差异**：$\mathbb{R}^n$ vs 概率测度 vs 带容差数值
- **注入点结构差异**：代码扰动 vs 概率语义扰动 vs 数据+模型+优化扰动（SML 独有数据级变异）
- **可观测性判据差异**：严格不等 vs 统计检验 vs 容差超出

### 6.3 混合程序的新研究问题

- Monte Carlo + 代理模型加速：PP + SML 混合
- UQ 驱动数值仿真：PP 包裹 SCP
- 数字孪生：SCP + SML 双向耦合

**跨类型故障传播映射**构成独立研究课题。

### 6.4 SCP 研究路线图（四阶段）

1. **阶段 1｜算子分类学**：按层次 L1–L4 分类
2. **阶段 2｜元模式-算子交叉矩阵**：$5 \times 4$ 敏感性矩阵
3. **阶段 3｜高阶变异**：多层耦合故障
4. **阶段 4｜对齐性实证研究**：从 Git 历史挖掘真实 bug 修复，验证 $\theta$-对齐

---

## 七、元模式的跨类型普适性审查

### 7.1 两种普适性的区分

- **类型-1 普适性（结构普适性）**：数学结构是否存在？
- **类型-2 普适性（实操普适性）**：能否作为 MR 设计的有效指导？

### 7.2 五模式逐项审查结果

| 元模式 | SCP | PP | SML | 综合 |
|---|---|---|---|---|
| P1 守恒 | 强（原产地） | 强 | 中（仅物理感知模型） | **条件普适** |
| P2 单调 | 强 | 强 | 中（双下降反例） | **条件普适** |
| P3 收敛 | 强 | 强（BvM 等） | 中（需分叉：优化收敛 vs 统计收敛） | **需分叉普适** |
| P4 轨迹 | 强 | 强 | 强 | **完全普适** |
| P5 偏序 | 强 | 中（需真值参照） | 弱（反例多） | **弱普适** |

### 7.3 关键修正

- **P2 双下降陷阱**：SML 中简单搬用 P2 会产生假阳性
- **P3 分叉**：SML 需区分优化收敛与统计收敛
- **P5 条件化**：SML 中必须改写为 $P_5'$（条件偏序），显式声明条件域

### 7.4 诚实立场

- 三支柱的正确表述：**核心骨架跨类共享 + 类型参数化扩展**
- 非"五模式跨三类普适"

### 7.5 SCP 内部完备性审查（前置任务）

需先验证：57 条 MR 是否都能唯一归类到 P1–P5？是否存在孤儿 MR？这是向 PP/SML 推广的基准。

---

## 八、新元模式的系统归纳方法论

### 8.1 元模式身份的五项判据

1. **数学结构抽象性**：对应抽象数学结构，非具体物理/算法细节
2. **跨层次性**：能贯穿 L1–L4 每一层
3. **检错力独立性**：与现有模式捕获故障集近似正交
4. **实例密度**：语料 ≥5% MR 可归入
5. **生成性**：能为新程序生成 MR 候选，而非仅分类

### 8.2 五阶段归纳程序

**阶段 1｜语料构建**
- PP：Stan/Pyro 测试套件、arviz、SBC、PPC、贝叶斯教材
- SML：ML 测试文献、等变 NN 验证、PINN 验证、不确定性校准
- 每类 ≥ 50–80 条 MR
- 关键：盲审式录入，双研究者独立提取

**阶段 2｜开放编码**
- 变换类型（缩放、平移、置换、条件化……）
- 保持量（值、分布、形状、秩序、拓扑、信息量……）
- 关系类型（等式、不等式、偏序、分布等价……）
- 约束强度（严格/统计/近似）
- 定义域条件

**阶段 3｜聚类归纳**
- 定性：变换类型 × 保持量二维手工聚类
- 定量：MCA 多重对应分析、层次聚类
- 交叉验证：已有模式应为稠密簇，新模式为现有簇之外的稠密子群

**阶段 4｜判据审查**：候选模式通过五判据才能升格

**阶段 5｜理论饱和检验**：保留 20% 验证集，若归类孤儿 < 10% 则饱和

### 8.3 PP 和 SML 候选新元模式（假设性清单）

| 候选 | 所属类型 | 建议处理 |
|---|---|---|
| **校准性（Calibration）** | PP & SML | **升格为 P6**（SCP 完全无对应） |
| **外推降级（Extrapolation Degradation）** | SML | **升格为 P7**（SML 独有） |
| 可交换性（Exchangeability） | PP | 待验证：独立或 P4 子模式 |
| 训练动力学形态 | SML | 合并入 P4 子模式 |
| 稳健性-精度偏序 | SML | 合并入 $P_5'$ 子模式 |
| 信息单调性 | PP | 合并入 P2 子模式 |
| 公平性不变性 | SML | SCP 代理模型语境下暂不纳入 |

### 8.4 "5 + 2" 模型假设

- 核心骨架：P1–P5
- 扩展模式：P6（校准性，跨 PP/SML）、P7（外推降级，SML 独有）
- 最终验证需经五阶段严格归纳

### 8.5 方法论风险

- **归纳者视角偏差**：需跨学科合作（贝叶斯统计学者、ML 测试研究者）
- **元模式粒度不一致**：以层次 L1–L4 实例化为校准检验
- **集合规模膨胀**：核心骨架 + 类型子编号（如 $P_6^{\mathrm{PP}}$、$P_6^{\mathrm{SML}}$），总数 ≤ 7
- **生成性判据验证**：可通过本科生教学案例（Meng 的 AI 软工课程）进行实验验证

---

## 九、投稿策略与研究路线图

### 9.1 论文分工建议

| 论文 | 主题 | 目标期刊/会议 | 状态 |
|---|---|---|---|
| **A** | Metamorphic Mutation Operators for Scientific Computing | ISSTA / ICSE | Meng 现有 SCP 积累，优先起步 |
| **B** | Metamorphic Mutation for Surrogate Model Verification | TOSEM / IST | 接续 Progress in Nuclear Energy 综述 |
| **C** | Metamorphic Mutation for Probabilistic Programs | FSE / ASE | 需概率编程合作者 |
| **D** | Unified Framework of MR Mutation Operators Across Types | TSE | 三篇工作的理论综合 |
| **E** | Grounded-Theory Methodology for Inducing MR Meta-Patterns | TOSEM / ESE | 归纳方法论独立论文 |
| **F** | SCP 内部元模式完备性审计（57 条 MR 归类） | ANE / IST | 方向 A 的前置 |

### 9.2 优先级排序

1. **SCP 内部完备性审计**（前置，论文 F）
2. **SCP 侧 MR 变异算子**（论文 A）
3. **SML 侧代理模型变异**（论文 B，接续已有综述）
4. **归纳方法论论文**（论文 E，方法论贡献独立可立）
5. **PP 侧工作**（论文 C，需合作者）
6. **综合理论**（论文 D，收尾）

### 9.3 关键衔接点

- **42 篇论文审计的复用**：作为可复用资产，非一次性投入
- **Progress in Nuclear Energy 综述的接续**：在结尾埋下"代理模型缺乏专用变异算子"伏笔
- **AI 软件工程本科案例**：P5/P6 阶段引入学生动手设计 MR 变异算子
- **跨学科合作**：PP 侧需贝叶斯统计合作者（清华候选），SML 侧需 ML 测试合作者

---

## 十、遗留问题与后续方向

### 10.1 理论层面待解问题

- SCP 内部元模式集合的完备性尚未严格论证
- PP 中可交换性是否独立为元模式
- SML 中 $P_5'$ 的条件化形式尚需精确
- 高阶变异对 MMS 度量的影响
- 混合程序的跨类型故障传播理论

### 10.2 工程层面待开展工作

- **ScMT-Mut** 工具包：基于 MetBench 扩展，承载 SCP 侧 MR 变异算子
- 从 Git 历史挖掘真实 bug 修复，标注为故障类（OpenMC、MCNP、DeCART 候选）
- 二部图 $\mathcal{G}(M_{\mathrm{cand}}, F, S)$ 的自动构造与可视化
- 贪心近似算法实现最小支配集求解

### 10.3 方法论层面待验证

- 五阶段归纳程序的可复现性（需跨学科独立团队重复实验）
- 理论饱和检验的阈值（当前 10% 为经验值）
- 生成性判据的教学案例验证

### 10.4 核工程实务层面的对接

- 将三支柱框架纳入 ASME NQA-1、IEEE 7-4.3.2 V&V 流程
- 与 FMEA/FMECA 失效模式分析的对应表
- 监管语境下的"测试充分性报告"模板

---

## 附录 A：核心术语对照表

| 中文 | 英文 | 形式化符号 |
|---|---|---|
| 蜕变关系 | Metamorphic Relation | $m = (R^m_{\mathrm{in}}, R^m_{\mathrm{out}})$ |
| 元模式 | Meta-Pattern | $P_i \in \Pi$ |
| 层次拓扑 | Hierarchical Topology | $L_j \in \Lambda$ |
| 故障模型 | Fault Model | $F = \{\varphi_k\}$ |
| 故障注入算子 | Fault Injection Operator | $\mu_\varphi$ |
| MR 变异算子 | MR Mutation Operator | $\mu^m$ |
| 判等算子 | Equivalence Operator | $\mathrm{Eq}_\tau$ |
| 违反谓词 | Violation Predicate | $\mathrm{viol}_\tau$ |
| 故障检出力 | Fault Detection | $\mathrm{det}_\tau$ |
| 平凡 MR | Trivial MR | $\mathrm{Triv}(m)$ |
| 等价变异 MR | Equivalent-Mutant MR | $\mathrm{EqvMut}(m, \varphi)$ |
| F-盲 MR | F-blind MR | $\mathrm{Blind}(m, F, S)$ |
| F-有效 MR | F-effective MR | $\mathrm{Eff}(m, F, S)$ |
| 冗余 MR | Redundant MR | $\mathrm{Red}(m, M, F, S)$ |
| 单故障充分 | $\varphi$-Adequacy | $\mathrm{Adeq}(M, \varphi, S)$ |
| F-完备 | F-Completeness | $\mathrm{Comp}(M, F, S)$ |
| 最小完备 | Minimal Completeness | $\mathrm{MinComp}(M, F, S)$ |
| MR-变异得分 | MR-Mutation Score | $\mathrm{MMS}(M, F, S)$ |
| 矩阵覆盖 | Cell Coverage | $\mathrm{CellCov}(M)$ |
| 质量向量 | Quality Vector | $\mathbf{Q}(M, F, S)$ |

---

## 附录 B：三类程序故障模型符号

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

## 附录 C：关键判断速查

1. **双支柱识别论 + 第三支柱充分性论 = 完整蜕变测试方法论**
2. **MR 变异算子 > 故障模式库**（杠杆更高，故障库作为副产品）
3. **元模式是"核心骨架共享 + 类型参数化扩展"**，非完全跨类型普适
4. **P4 轨迹最稳定；P5 偏序在 SML 最脆弱；P6 校准 + P7 外推是最强新元模式候选**
5. **充分性理论与变异测试经典理论结构同构**，同构映射明确
6. **最小完备 MR 集 ⟺ 二部图最小支配集**（NP-难，对数近似算法可用）
7. **三类程序的 MMS 不可直接比较**（SML 的故障更难被 MR 捕获）
8. **归纳方法论本身是独立论文价值**，不依赖具体归纳结果
9. **SCP 内部完备性审计是推广 PP/SML 的前置任务**
10. **跨学科合作是 PP/SML 归纳严谨性的必要条件**，非锦上添花

---

*纪要整理日期：2026 年 4 月*
*用途：后续对话引用、研究路线参考、论文写作基础*
