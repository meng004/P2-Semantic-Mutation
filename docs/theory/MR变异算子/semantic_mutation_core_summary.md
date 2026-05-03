# 核心数据汇总表

基于报告内容，整理如下核心数据表，包含编号、研究、变异算子/方法、类型（语义/语法）、实验对象与关键创新。

## 核心数据汇总表

| 编号 | 研究 | 变异算子/方法 | 类型 | 实验对象 | 关键创新 |
|---|---|---|---|---|---|
| 1 | Asma Hamidi et al., 2025 | Intent-Based Mutation Testing | 语义 | 29个程序 | 使用 LLM 改变程序意图而非语法 |
| 2 | Loh Zheung Yik et al., 2025 | Transformer A | 混合语义/语法 | Bug-fix 数据集 | 强调局部和全局代码上下文的 Transformer 架构 |
| 3 | Miloš Ojdanić et al., 2023 | PiTest / IBIR / μBERT / DeepMutation | 混合 | Defects4J V2（592个故障） | 比较语法与语义相似性 |
| 4 | Sourav Deb et al., 2024 | universalmutator | 语法 | 24个 GitHub 项目（C++ / Java / Python / Rust） | 通用语言变异生成器 |
| 5 | Serhat Uzunbayir & Kaan Kurtel, 2024 | 遗传算法搜索 | 语法 | 7个 C# 测试程序 | 高阶变异测试的遗传算法 |
| 6 | Subhasish Mohanty et al., 2025 | SQUMUTH | 混合语义/语法 | 8个 Java 基准程序 | 松鼠搜索算法（SSA） |
| 7 | Jing Liu & Zi-Jia Wang, 2023 | MOEA/D | 未指定 | 未指定 | 多目标差分进化算法 |
| 8 | Mohammad Khorsandi et al., 2024 | 解析树和语法模糊测试 | 语法 | 通用编程语言 | 解析树节点选择和粒度控制 |
| 9 | Zicong Gao et al., 2024 | FA-fuzz | 未指定 | 8个真实程序 | 萤火虫算法优化变异算子概率 |
| 10 | Guofan Lv et al., 2026 | HavocEDA | 语法 | 9个开源 C/C++ 程序 | 分布估计算法（EDA） |
| 11 | Shiyu Wang et al., 2025 | VarFuzz | 语义 | GCC 和 LLVM 编译器 | 语义距离矩阵和 Thompson 采样 |
| 12 | Wei Zheng et al., 2023 | AST 静态模糊变异 | 语法 | Linux 内核代码 | 基于抽象语法树的变异 |
| 13 | Song Tang et al., 2023 | EASTer | 语法 | JavaScript 引擎 | 启发式算法最优组合 |
| 14 | Yu Li et al., 2024 | SQLPass | 语义 | 4个数据库系统 | 弱语义关联节点和语义关系表 |
| 15 | Qingchao Shen et al., 2022 | QAQA | 语义 | 3个 QA 数据集 | 元变形关系和语义引导搜索 |
| 16 | Miloš Ojdanić et al., 2021 | PiTest / IBIR / DeepMutation / CodeBERT | 语法 | Defects4J V2 | 语法与语义相似性对比 |
| 17 | Mingmin Lin et al., 2022 | GSA-Fuzz | 未指定 | 10个开源程序 | 引力搜索算法（GSA） |
| 18 | Dandan Gong et al., 2022 | 加权软件行为图 | 未指定 | 手工评估等价变异体数据集 | 程序行为跟踪检测等价变异体 |
| 19 | Fadi Wedyan et al., 2022 | GaSubtle | 语法 | 10个 Java 程序 | 新交叉机制的遗传算法 |
| 20 | D. Mishra et al., 2022 | RGA-MS | 语法 | C/C++ 小规模程序 | 实数编码遗传算法 |
| 21 | Patrick Jauernig et al., 2022 | DARWIN | 语法 | GNU binutils 套件 | 进化策略优化变异算子概率 |

## 关键发现

### 语义变异算子的存在证据

- **5个研究**明确提出了语义变异算子。
- **3个研究**采用混合语义/语法方法。
- **关键发现**：语义相似性与语法相似性不匹配，**55%** 的意图变异不被传统变异覆盖。

### 性能提升数据

- **VarFuzz** 在 GCC 和 LLVM 上分别提升 **10.46%** 和 **6.2%** 的代码覆盖率。
- **SQLPass** 比现有工具的语义正确性提升 **5.7%–94.2%**。
- **QAQA** 的真阳性率达到 **97.67%**，远高于传统方法的 **49%**。

## 结论

这些数据表明，语义变异算子确实存在，并且在近三年研究中呈现快速发展趋势；其在多个应用领域中均表现出显著的性能提升与方法创新价值。
