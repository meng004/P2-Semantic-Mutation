# Fable 输入计划书：P3/P12 新论证方案与证据边界

> 文档用途：供 Fable 重新规划 P3 与 P12 的论文论证、章节结构和后续实验。  
> 文档性质：证据约束型计划书，不是论文成稿，也不是对未执行实验的结果预测。  
> 当前判断：原计划中的“系统有效性—真实缺陷优越性”主张没有得到证据支持；但理论构造、边界性实验、失败图谱、离线合同和可审计治理仍可形成两个边界清晰的论文方向。

---

## 0. Fable 必须遵守的证据规则

1. 必须把 P3 与 P12 作为两篇贡献类型不同的论文处理，不能把二者拼接成一条已经闭合的实证链。
2. 必须严格区分：
   - **科学结果**：直接回答研究问题的观测或统计结果；
   - **工程结果**：测试、验证器、合同、哈希、可移植性和失败关闭机制通过；
   - **准备度证据**：候选对象已经整理，但尚未执行映射、生成、验证或 MT；
   - **未执行计划**：已设计但因前置门禁失败而没有运行的实验。
3. “门禁正确阻止后续实验”只能支持治理或可审计性论点，不能支持语义变异、MR 生成或真实缺陷检测有效性。
4. “0 个非干扰失败”不能写成非干扰门禁通过。D1 中传播、非干扰、等价性阶段均为 `NOT_REACHED`。
5. P12 的 RFDS 确证性实验没有发生。不得报告 S1 优于 S2，不得报告真实缺陷检测效应量，也不得把 D2 的 77 个 ready family 当成已检测的缺陷。
6. P3/P12 既有真实缺陷证据属于 **D0 development evidence**，具有筛选条件和选择偏差，不能表述为独立确证或无偏总体外推。
7. Cosmic Ray 重叠实验只比较了一个默认一阶语法变异配置。不得据此宣称“语义变异普遍不可由语法变异实现”。
8. 对等价变异必须采用 certificate-first 的表述。有限输入上的行为一致只能作为未发现差异的证据，不能作为等价证明。
9. 文稿中的所有数字必须从唯一 SSOT 自动生成。在解决 `main.tex` 与 `paper_numbers_v4.json` 的数值冲突前，Fable 不得自行挑选一个数写入结论。
10. 任何新增实验必须建立新的版本和证据 lineage；不得改写 V125、V132 或已经密封的历史终态。

---

## 1. 总体诊断与论文组合决策

### 1.1 原始总论证为什么没有闭合

原始方案希望建立如下证据链：

> 语义变异算子可操作化  
> → 可稳定生成受控语义变异体  
> → 能处理等价性  
> → SMS 能区分 MR 质量  
> → 这种区分与真实缺陷检测一致  
> → 残差引导策略在未见真实缺陷上优于经典 MS 引导策略。

目前证据在第一条实证箭头处即中断：

- D1 冻结了 142 个项目、584 个执行单元、14 个 variant 和 8 个 family；
- 584 个单元全部未形成 development-valid unit；
- 传播、非干扰和等价性阶段均未到达；
- 因而没有资格冻结 core operators，也没有资格开放后续 validation、operator mapping 或 MT；
- P12 最终以 `P12_POST_V132_RECOVERY_TERMINATED_D1_DEVELOPMENT_GATE_NOT_MET` 终止。

这不等于“所有历史工作都无效”，但意味着不能再把现有材料包装为一个已验证的端到端有效性故事。

### 1.2 推荐的两篇论文定位

| 论文 | 推荐身份 | 当前决策 | 可以主张什么 | 不能主张什么 |
|---|---|---:|---|---|
| P3 | SMS 理论构造、边界分析与负结果论文 | **Qualified Go** | SMS 的形式定义、与经典 MS 的关系、语义空间的部分结构差异、12-PUT 审计揭示的适用边界和失败模式 | 跨项目有效性、工业普适性、优于语法变异、真实缺陷外部效度 |
| P12 | 可审计的失败关闭实验基础设施、准备度与失败图谱论文 | **Qualified Go** | 角色隔离、内容寻址、合同验证、证据治理、D1 失败分布、D2 准备度、离线 MR 合同的鲁棒性 | RFDS 优越性、真实 B0/B1 生成质量、operator mapping、MT 有效性、真实缺陷检测收益 |
| 原 P3 v1.2“完整系统有效性论文” | 端到端系统论文 | **No-Go** | — | 中央实证链尚未建立 |
| 原 P12“真实缺陷确证性优越性论文” | S1 对 S2 的真实缺陷实验 | **No-Go** | — | D1 门禁失败，D2/MT 未开放，主效应不存在 |

### 1.3 两篇论文的贡献边界

- P3 回答“这个构念是什么、怎样度量、与经典 MS 有何形式关系、在哪些条件下失效”。
- P12 回答“如何避免在证据链不完整时产生虚假的正结果，以及跨项目语义算子工程化具体失败在哪里”。
- P12 可以在 related work 或 motivation 中引用 P3 的构念；P3 只能把 P12 作为后续确证尝试被门禁终止的边界证据，不能摄取 P12 未执行实验的结论。
- 不建议合并两篇论文。合并会造成理论贡献、负结果和治理贡献竞争篇幅，并增加重复发表与贡献重叠风险。

---

## 2. P3 新论文计划：SMS 的构念、边界与负结果

### 2.1 论文目标

定义一种面向语义层次和蜕变关系充分性的变异度量 SMS，说明它与经典 Mutation Score 的形式关系，并通过受控审计检验：

1. 所定义的语义变异空间是否与一个常用语法变异基线存在结构差异；
2. 语义算子能否在不同科学计算/机器学习 PUT 上稳定实例化；
3. SMS 是否在现有小样本中表现出预期的判别性；
4. 哪些算子、程序类别、MR 强度和实验设计因素会使该构念退化或失真。

论文目标不再是证明 SMS 已经具有工业有效性，而是给出一个可检验构念、有限的实证支持和明确的反例/边界条件。

### 2.2 核心论点

#### 主论点 P3-A：SMS 是一个构念级度量，而不是已经证实的优越性指标

SMS 将变异体按声明的语义 strata/fiber 组织，并度量 MR 测试在这些语义扰动上的充分性。它解决的是“MR 对声明的语义变化覆盖得怎样”，而不是直接取代传统 Mutation Score。

#### 主论点 P3-B：SMS 与经典 Mutation Score 具有可解释的形式关系

在语义分层退化、所有变异体落入同一经典杀死/存活判定框架的特定条件下，SMS 可退化到传统 MS。该关系应以定义、命题和证明呈现，并接受独立形式审计。

#### 主论点 P3-C：现有语义变异空间与一个默认一阶语法基线只有有限重叠

292 个 v4 语义变异体与 1,250 个 Cosmic Ray 默认一阶语法变异体进行 AST 归一化精确重叠审计，仅观察到 15 个重叠。该结果支持“部分结构差异”，不支持“普遍不可达”。

#### 主论点 P3-D：现有 60-cell 审计主要揭示构念边界，而非证实强假设

H1–H4 均未达到预设阈值，SMS 分布高度零膨胀，算子在不同类别上的适用性差异大。论文应把这些结果作为构念校准和失败模式，而不是弱化阈值或事后改写为成功。

#### 主论点 P3-E：强 MR、弱 MR 和随机性边界展示了容差与误判之间的结构性权衡

六个真实/教材程序和小规模 adjoint 演示可说明 SMS 对 MR 语义质量和容差设置敏感，但由于规模小、手工构造且具有选择性，只能作为机制演示。

### 2.3 研究问题

| RQ | 研究问题 | 证据类型 | 当前状态 |
|---|---|---|---|
| P3-RQ1 | SMS 如何形式化？它与经典 Mutation Score 有何关系？ | 定义、命题、证明 | 手稿内已有；需独立形式审计 |
| P3-RQ2 | 语义变异体与默认一阶语法变异体在 AST 归一化后有多大重叠？ | 结构审计 | 已执行 |
| P3-RQ3 | 五类语义 meta-pattern 能否跨 PUT 稳定实例化并形成非等价变异体？ | 12 PUT × 5 pattern 审计 | 已执行；原强假设未满足 |
| P3-RQ4 | SMS 能否区分 aligned MR 与 cross/non-aligned MR？来源变化是否改变结论？ | 60-cell 对照、source ablation | 已执行；方向性信号存在，强阈值未满足 |
| P3-RQ5 | 该判别方向能否跨程序类别保持？ | 分层/非参数分析 | 已执行；稳定性不足 |
| P3-RQ6 | LRCA、MR 强弱和随机性如何影响 SMS 的误判边界？ | 机制演示、诊断指标 | 已执行；仅限边界展示 |

### 2.4 预注册假设及其当前结论

| 假设 | 原始判据 | 结果 | 新论文中的写法 |
|---|---|---|---|
| H1：语义算子具有跨 PUT 可实例化性 | 至少 4/5 operators 各自在至少 9/12 PUT 上产生 ≥5 个非等价变异体 | **未满足**；只有 HP 达到 9/12 | 作为阈值与 class-targeted applicability 不匹配的负结果 |
| H2：aligned MR 的 SMS 显著高于 cross MR | Cliff’s δ ≥ 0.474 且 OR ≥ 3 | **未满足**；v4 SSOT 中 δ≈0.439，OR 因 cross 中位数为 0 而退化 | 只能说观察到中等方向性差异，未达到预设强效应 |
| H3：判别方向跨四类 PUT 稳定 | 4/4 类方向一致且 CV < 0.5 | **未满足**；3/4 同向，B 类反向，CV > 1 | 报告类别异质性，不宣称跨域稳定 |
| H4：LRCA 可将 suspect burden 控制在低水平 | mean suspect share ≤ 0.20 | **未满足**；mean suspect≈0.7908 | LRCA 尚不能作为可靠自动筛选器 |

说明：不得重新定义阈值以把 H1–H4 改写成“支持”。可以提出新的探索性假设，但必须明确属于后续研究。

---

## 3. P3 已执行实验方案与结果

### 3.1 E-P3-1：形式构造与退化关系

**研究问题**

- 如何定义面向语义 strata/fiber 的变异充分性？
- 在什么条件下 SMS 与经典 MS 一致？
- 等价性、杀死关系和 MR 充分性在定义中如何分离？

**实验对象/数据**

- 不是经验数据实验；
- 对象为 SMS、semantic fiber、MR 判别关系和经典 Mutation Score 的形式定义。

**Baseline**

- 经典 Mutation Score；
- 不涉及统计 baseline。

**评价方式**

- 定义是否完备；
- 命题是否可证明；
- 退化关系是否成立；
- 符号、分母、等价类和未决状态是否一致。

**结果**

- 手稿内部形成了 SMS 构造和向传统 MS 退化的理论叙述；
- 当前证据台账将该构造视为可支持内容；
- 但尚不能把“手稿中存在证明”写成“已经通过独立形式验证”。

**论文使用**

- 作为 P3 的首要贡献；
- 投稿前安排与实证作者独立的形式审计，特别审查等价性定义和退化定理的边界条件。

### 3.2 E-P3-2：AST 归一化结构重叠审计

**研究问题**

语义变异体是否只是默认语法变异体的重命名，还是包含结构上不同的变换？

**实验对象/被测程序集**

12 个紧凑、单输出、`float -> float` 形式的 PUT，分为四类：

| 类别 | PUT |
|---|---|
| Numeric | Lorenz ODE、LU、FDM heat |
| Probabilistic | Beta-Binomial、MCMC、Monte Carlo integration |
| Surrogate | GPR、PCE、NN surrogate |
| Machine Learning | MLP、SVM、Logistic Regression |

**数据规模**

- 292 个 v4 语义变异体；
- Cosmic Ray 默认配置产生的 1,250 个一阶语法变异体。

**Baseline**

- Cosmic Ray 默认一阶语法变异。

**评价指标**

- AST 归一化后的精确结构重叠数；
- 总体和按 meta-pattern 的 overlap rate。

**结果**

| 指标/算子 | 结果 |
|---|---:|
| 总体重叠 | 15/292 = 5.14% |
| HP | 0/72 |
| SI | 0/33 |
| TF | 0/54 |
| CE | 5/64 = 7.81% |
| OS | 7/60 = 11.67% |
| CF | 3/9 = 33.33% |

**可支持结论**

- 对此特定 PUT 集和此特定 Cosmic Ray 配置，绝大多数语义变异体没有 AST 归一化精确匹配项；
- 不同 meta-pattern 的重叠率差异明显。

**不可支持结论**

- 所有语法变异工具都无法产生这些变异；
- 高阶变异、定制算子或其他语言的语法变异无法覆盖语义变异空间；
- 低结构重叠自动意味着更高缺陷检测价值。

### 3.3 E-P3-3：12 PUT × 5 meta-pattern 的 60-cell 实例化审计

**研究问题**

五类语义 meta-pattern 能否在不同科学计算与机器学习 PUT 上稳定生成可用、非等价的语义变异体？

**实验对象/数据**

- 上述 12 个 PUT；
- 每个 PUT × 5 个 meta-pattern，共 60 个 cell；
- 292 个 v4 语义变异体，约 24.3 个/cell，范围约 10–30；
- AVP 重复次数 `N=20`；
- 等价性抽样参数 `K_eq=1000`。

**Baseline**

- 预注册 H1 的绝对阈值；
- 各 meta-pattern 之间的横向比较；
- 不以某个外部变异工具作为该实验的主要 baseline。

**评价指标**

- instantiation rate；
- equivalent rate；
- C1 share；
- survive rate；
- SMS；
- 每个 operator 在多少 PUT 上产生至少 5 个非等价变异体。

**结果**

- mean SMS = 0.104；
- median SMS = 0；
- standard deviation = 0.2127；
- 45/60 cell 的 SMS 为 0；
- CE、OS、HP、TF、SI 分别只在 4/12、5/12、9/12、5/12、1/12 PUT 上达到 H1 的单元标准；
- H1 未满足。

**解释边界**

- 结果揭示明显的 zero inflation 和 operator–program applicability 交互；
- 原阈值要求 class-targeted operator 广泛跨类成功，可能与算子设计意图不一致；
- 但阈值不匹配不能事后转化为 H1 成立。正确处理是保留负结果，并在新实验中预注册 applicability-aware 设计。

### 3.4 E-P3-4：aligned/cross MR 判别与来源消融

**研究问题**

- 与 PUT/语义变异对齐的 MR 是否获得更高 SMS？
- 生成来源变化是否显著改变这一关系？

**实验对象/数据**

- 同一 60-cell 框架；
- aligned MR 与 cross/non-aligned MR；
- v3、v3b、v4 三个来源阶段：
  - v3：同源 Claude；
  - v3b：中间版本；
  - v4：Claude/GPT/DeepSeek，采用相同 prompt 的跨来源设置。

**Baselines**

- cross/non-aligned MR 为主对照；
- v3 与 v3b 为来源消融/历史对照。

**评价指标**

- aligned/cross mean 与 median SMS；
- Cliff’s delta；
- bootstrap confidence interval；
- odds ratio；
- 在预设效应下的 power。

**结果**

- v4 aligned mean SMS = 0.275；
- v4 cross mean SMS = 0.0612；
- aligned median≈0.2666，cross median=0；
- SSOT 结果文件记录的 Cliff’s delta：
  - v3：0.3229，CI [0.0174, 0.6217]；
  - v3b：0.4462，CI [0.1544, 0.7431]；
  - v4：0.4392，CI [0.1267, 0.7396]；
- H2 的预注册阈值为 δ≥0.474 且 OR≥3，未满足；
- cross median=0 导致 OR 为无穷或退化，不应被当作强证据；
- 历史分析给出的预设 δ=0.474 下 power 约为 0.491，说明样本对强确认也不足。

**重大 SSOT 冲突**

`submission/arxiv-20260704/main.tex` 曾报告 v4 δ=0.314、CI [0.014, 0.622]，并出现 source contrast=-0.009；这与 `data/results/paper_numbers_v4.json` 中的 δ=0.4392 不一致。

在重新生成结果表、追溯脚本版本和确认 SSOT 前：

- 不得在标题、摘要或结论中使用任一冲突数值；
- 不得把差异解释为“稳健复制”；
- Fable 应为此处生成 `[SSOT_RECONCILIATION_REQUIRED]` 占位符。

### 3.5 E-P3-5：跨程序类别稳定性

**研究问题**

aligned/cross 的判别方向是否可跨 Numeric、Probabilistic、Surrogate 和 ML 四类 PUT 保持？

**Baseline**

- H3：4/4 类方向一致且变异系数 CV<0.5。

**评价指标**

- 各类 mean SMS；
- aligned/cross 方向；
- CV；
- mixed model；
- Friedman test；
- 按类非参数检验及多重校正。

**结果**

| 类别 | v4 mean SMS |
|---|---:|
| A | 0.0667 |
| B | 0.1478 |
| C | 0.0894 |
| D | 0.1122 |

- 3/4 类与总体方向一致，B 类反向；
- CV>1；
- mixed model 出现 singular fit；
- Friedman PUT×meta-pattern：χ²=15.30，p=0.0041；
- 各类检验在 Bonferroni 校正后不显著；
- H3 未满足。

**附加相关性**

- Pattern Coverage 与目标指标在 n=12 下：
  - Spearman ρ=0.163，p=0.613；
  - Kendall τ=0.136，p=0.568。

该结果只能表述为“未检测到关系”，不能表述为“二者独立”。

### 3.6 E-P3-6：LRCA 诊断

**研究问题**

LRCA 能否把疑似不可靠/低质量 MR 控制到可接受水平？

**Baseline**

- H4：mean suspect share ≤0.20。

**评价指标**

- C1 share；
- suspect share；
- 满足 suspect≤0.20 的 cell 数量；
- 阈值敏感性。

**结果**

- mean C1 share = 0.2092；
- mean suspect share = 0.7908；
- 仅 12/60 cell 达到 suspect≤0.20；
- H4 未满足。

**问题**

- LRCA 阈值曾在 9-point grid 上校准，存在开发集过拟合风险；
- 必须保留原控制和失败结果，不能把重新挑选阈值当作独立验证。

### 3.7 E-P3-7：强/弱 MR、随机性与 adjoint 边界演示

**研究问题**

SMS 在明确强 MR、弱 MR、随机程序和 adjoint 场景中表现出什么边界行为？

**实验对象**

- 六个真实/教材程序：
  - 4 个 strong-MR case；
  - 1 个 weak-MR false-positive case（PINN）；
  - 1 个 RNG false-negative case；
- adjoint arm 涵盖 scipy、pylops、jax；
- 3 个真实已修复缺陷。

**Baselines**

- strong MR 与 weak MR；
- forward behavior；
- 手工等价集上的 false-positive 检查。

**评价指标**

- SMS；
- false positive/false negative；
- 对等价集的判别；
- forward/adjoint 对照。

**结果**

- adjoint arm 报告 forward SMS=1.00；
- 手工等价集上观察到 0 false positive；
- 同时出现 weak-MR false positive 和 RNG false negative 边界案例。

**证据等级**

- 机制演示，不是总体效度证据；
- 样本基数低、场景手工选择、部分为 extracted-diff，不能宣称工业普适性。

### 3.8 E-P3-8：历史真实缺陷切片（D0 development evidence）

**研究问题**

pattern-derived 方法在既有筛选缺陷上是否优于 literature-generic 对照？

**实验对象/数据集**

- Defect4MR 历史归档；
- 35 个 verified defects、20 个项目；
- 34 个 mutation case、1,124 个 mutants；
- 报告过 30/30 real-defect face。

**Baselines**

- literature-generic baseline；
- 若干 ablation。

**评价指标**

- paired mean difference；
- Holm-adjusted p-value；
- Cliff’s delta；
- face-level 命中。

**结果**

- pattern-derived 相对 literature-generic：
  - mean paired difference≈+0.101；
  - Holm-adjusted p≈0.046；
  - Cliff’s delta≈+0.247；
- ablation 未显示显著支配；
- 30/30 face 形成明显 ceiling。

**关键偏差**

`verified_full` 的进入条件包含 MR-discriminating oracle，因此结果受到选择条件影响。该切片只可作为开发证据，不可作为：

- 无偏真实缺陷总体估计；
- 独立外部验证；
- P12 的确证性结果；
- 对未知项目和未知缺陷族的泛化证明。

---

## 4. P3 的建议章节结构

1. **Introduction**
   - MR 测试充分性的构念缺口；
   - 为什么经典 MS 不能直接表达声明的语义 strata；
   - 本文目标是定义、校准和暴露边界，不是宣称工业优越性。
2. **Construct and Formal Properties**
   - semantic fiber/strata；
   - SMS 定义；
   - 未决等价性处理；
   - 向经典 MS 的退化条件。
3. **Study Design**
   - 12 PUT、五类 meta-pattern、60-cell；
   - Cosmic Ray baseline；
   - aligned/cross 与 source ablation；
   - H1–H4 和统计方案。
4. **Results**
   - RQ2 结构重叠；
   - RQ3 实例化与 zero mass；
   - RQ4 判别性；
   - RQ5 跨类异质性；
   - LRCA 和边界案例。
5. **Negative Results and Construct Boundaries**
   - H1–H4 未满足；
   - operator applicability；
   - RNG、弱 MR、容差和等价性；
   - 统计功效不足。
6. **Development-Only Real-Defect Evidence**
   - 明确标记 D0；
   - 选择偏差、ceiling 和不可外推范围。
7. **Threats to Validity**
   - baseline 狭窄；
   - n=12、zero inflation、singular model；
   - source/protocol asymmetry；
   - SSOT 漂移；
   - 人工构造和筛选偏差。
8. **Implications and Future Confirmation**
   - applicability-aware 算子设计；
   - 多工具语法 baseline；
   - 独立 held-out real-defect study；
   - P12 的终止说明为什么需要新的端到端 pilot。

### P3 摘要中允许出现的结论级别

- “We introduce/define …”
- “Under the evaluated configuration, exact AST overlap was limited …”
- “The audit revealed substantial zero inflation and operator–program heterogeneity …”
- “None of the four preregistered strong hypotheses met its threshold …”
- “The results delimit, rather than establish, cross-project validity …”

### P3 摘要中禁止出现的结论

- “SMS is superior to MS.”
- “Semantic mutants cannot be generated syntactically.”
- “The approach generalizes across domains.”
- “The method has been validated on unseen real defects.”
- “P12 confirms real-fault effectiveness.”

---

## 5. P12 新论文计划：失败关闭治理、准备度与开发失败图谱

### 5.1 论文目标

构建并评估一种内容寻址、角色隔离、授权驱动、失败关闭的跨仓实验工作流，回答：

1. 它能否阻止缺失授权、证据不足和越序输入被误认为科学结果；
2. 跨项目语义算子开发具体在哪些阶段失败；
3. 在不开放 D2、不进行 operator mapping、不执行 MT 的情况下，可以诚实地建立何种准备度证据；
4. 离线 MR 合同能否在正向和对抗性测试中保持一致、可重放和 fail-closed。

P12 的新目标不是证明残差引导方法优越，而是呈现一个可审计的负结果与实验治理案例。

### 5.2 核心论点

#### 主论点 P12-A：可审计的失败关闭机制防止了无效科学结论

当 D1 产生 0 个有效单元时，系统没有继续开放 D2、mapping、MR live generation 或 MT；最终终止状态与授权字段一致。这是治理正确性，而非算法有效性。

#### 主论点 P12-B：跨项目语义算子开发的主要瓶颈发生在科学阶段之前

584 个执行单元全部在 build、原始输入、公开 API 证书、binding、site/trigger 等前置环节失败，传播/非干扰/等价性均未到达。失败图谱说明未来方案必须先证明“可构建、可绑定、可触发”的最小端到端可行性。

#### 主论点 P12-C：D2 可以建立准备度，但准备度不等于实验结果

94 个 family 中 77 个属于 `strict_current_asset_ready`，17 个保留为当前重执行失败；由于 open_count=0、mapping_count=0，且未摄取 MR/mutation/MT，唯一合法结论是“数据准备度已审计”。

#### 主论点 P12-D：离线 MR 合同通过了对抗性测试，但尚未产生真实科学 MR

7/7 positive 和 17/17 negative fail-closed 测试可支持合同、schema、parser、sandbox、timeout、repair 和 admission 机制；provider_calls=0、real B0/B1=false，因此不能支持 MR 科学质量。

#### 主论点 P12-E：预先冻结大规模队列不能替代小规模端到端可行性验证

P12 的失败不是“统计上没有发现优势”，而是“实验操作链没有建立”。新的研究顺序必须先完成不计入确证样本的小型 pilot，再冻结大规模 confirmatory population。

### 5.3 P12 研究问题

| RQ | 研究问题 | 当前证据 |
|---|---|---|
| P12-RQ1 | 内容寻址、授权绑定和角色隔离能否使实验输入与终态可审计？ | receipt、哈希、clean-clone verifier、tamper/alternate-cwd/TMPDIR 测试 |
| P12-RQ2 | 跨项目 operator development 的失败集中在哪些阶段？ | 584-unit failure atlas |
| P12-RQ3 | 在不开放 D2 的条件下，可建立何种缺陷族准备度？ | 94-family 四分区审计 |
| P12-RQ4 | 离线 MR 合同能否通过正向与对抗性 fail-closed 测试？ | 24/24 MR contract tests |
| P12-RQ5 | 原 RFDS 确证性问题能否被回答？ | **不能**；D1 gate 未满足，实验未执行 |

### 5.4 P12 假设/命题

P12 新论文不应把原来的 S1>S2 当作已有结果。建议将其分为已检验工程命题和未检验科学假设。

#### 已检验的工程命题

| 命题 | 判据 | 当前结果 |
|---|---|---|
| G1：授权缺失时系统失败关闭 | 缺少正式授权不执行真实单元 | 通过；历史状态停在 missing authority |
| G2：正式授权可被内容哈希和来源 commit 绑定 | receipt/hash/tree 可复核 | 通过 |
| G3：输入篡改和执行环境变化不会静默通过 | 一字节篡改非零退出；alternate cwd/TMPDIR 可验证 | 通过 |
| G4：未满足 D1 科学门禁时后续权限保持关闭 | D2 open/mapping/MT/live provider flags 均为 false/0 | 通过 |
| G5：离线 MR 合同对正向与负向用例行为一致 | 7/7 positive，17/17 negative fail-closed | 通过 |

#### 未检验的科学假设

| 假设 | 原计划 | 当前状态 |
|---|---|---|
| S1 的 RFDS 高于 S2 | equal budget 下比较 residual-guided 与 classical-MS-guided | 未执行 |
| S1 相对 S2 的项目等权差异超过 0 | 两级 BCa bootstrap 的单侧下界 >0 | 未执行 |
| 实际提升超过 MID=0.10 | 单侧下界 >0.10 | 未执行 |
| S3、S4 的次要/底线比较 | MR-coverage-guided、random/generic | 未执行 |

---

## 6. P12 已执行实验方案与结果

### 6.1 E-P12-1：POST-V132 授权、consumer rebind 与审计链

**研究问题**

多仓输入能否通过 commit/tree/hash/receipt 被绑定，并在授权边界内完成重新摄取？

**对象**

- P12-Defect4MR；
- P12-D1-Staging-private；
- P12-D2-Staging-private；
- P12-MR-Staging-private；
- POST-V132 D1 与 MR 授权 handoff。

**Baseline**

- 缺失授权和旧授权的 fail-closed 路径；
- 正式 P12 授权绑定路径；
- 一字节篡改、alternate cwd、alternate TMPDIR。

**评价指标**

- receipt/hash/tree 一致性；
- clean-clone verifier；
- credential scan；
- tamper detection；
- authorization flags；
- 是否发生未授权 provider、D2、mapping 或 MT。

**结果**

- 正式 D1 授权 SHA256：`aecff71b0b1a4518f28cfff992d97240e95a048bf09a12c7a3ee4b17a6228885`；
- 正式 MR 授权 SHA256：`8acc41379b9e5be6b921dc318ca7fab7a0ae231e87ac5e1aeaf05171906c83b0`；
- consumer rebind、audit intake、credential scan、alternate cwd/TMPDIR 和 tamper 检查通过；
- 全程未在产物中输出凭据；
- 这些结果只支持审计基础设施，不支持科学效果。

### 6.2 E-P12-2：MR 离线合同重建与独立审计

**研究问题**

共享 B0/B1 pipeline 的 schema、parser、AST、sandbox、timeout、repair 和 admission contract 能否在离线对抗场景中稳定失败关闭？

**对象/数据**

- MR 正向用例 7 个；
- 负向/对抗用例 17 个；
- 失败类别包括：
  - `B1_MISSING_TOLERANCE_EPSILON`；
  - `MISSING_SEVEN_REQUIRED_CALLABLES`；
  - `SCHEMA_VALID_SANDBOX_LOAD_FAILURE`；
  - `PARSER_REPAIR_STILL_ILLEGAL`；
  - `PROVIDER_ARM_ASYMMETRY`；
  - `COORDINATOR_MODEL_FIELD_OWNERSHIP_CONFUSION`。

**Baseline**

- 正常合同路径；
- 各类破坏合同的负向输入；
- 旧授权与正式授权的绑定差异。

**评价指标**

- positive pass rate；
- negative fail-closed rate；
- checks passed；
- credential hit count；
- provider/live-generation flags。

**结果**

- audited MR commit：`b7e8be973f9247f74ea6af61de269adbbd9a954f`；
- 7/7 positive PASS；
- 17/17 negative FAIL-CLOSED；
- 合计 24/24，底层 checks 66/66；
- credential hit_count=0；
- `provider_calls=0`；
- `real_b0_generated=false`；
- `real_b1_generated=false`；
- `scientific_project_prompt_sent=false`。

**结论边界**

支持“离线合同实现与对抗性行为通过审计”；不支持“LLM 生成的真实 MR 有效、对称或科学上可用”。

### 6.3 E-P12-3：D2 readiness 四分区审计

**研究问题**

在不开放 commitment、不进行 operator mapping、不读取 MR 结果和不执行 MT 的条件下，D2 缺陷族资产达到什么准备度？

**对象/数据集**

- 94 个 defect family；
- 20 个项目。

**Baseline**

- 既有 durable verification 基线；
- current reexecution 状态；
- 四分区互斥、完备和求和检查。

**评价指标**

- `strict_current_asset_ready`；
- `fresh_but_asset_incomplete`；
- `retained_only`；
- `current_reexecution_failed`；
- failure category；
- project/family/open/mapping counts；
- clean-clone verifier。

**结果**

| 分区 | 数量 |
|---|---:|
| strict_current_asset_ready | 77 |
| fresh_but_asset_incomplete | 0 |
| retained_only | 0 |
| current_reexecution_failed | 17 |
| 合计 | 94 |

17 个失败的分类：

- `TRIGGER_UNEXERCISED=13`；
- `INFRA_UNRESOLVED=3`；
- `BUGGY_BUILD_FAILED=1`。

其他结果：

- projects=20；
- open_count=0；
- operator_mapping_count=0；
- clean-clone `VERIFY.py` 32/32 PASS；
- D2 audit commit：`44d8b50c6b83cf46cb1f384ffe814ec20f7985b9`；
- governance status：`OBSERVED_OUT_OF_SEQUENCE_D2_READINESS_MAINTENANCE`。

**结论边界**

- 77 表示资产准备度，不表示检测成功；
- 17 个失败 family 被保留，没有替换；
- receipt 不是事前授权或追溯授权；
- 没有 commitment 开封、MR 摄取、mutation kill、mapping 或 MT。

### 6.4 E-P12-4：D1 跨项目 operator development

**研究问题**

正式授权后，冻结的跨项目 population 能否产生满足开发门禁的 exact-site、可传播、非干扰、可判定等价性的有效单元？

**实验对象/数据集**

- 142 个项目；
- 584 个 queue unit；
- 14 个 variants；
- 8 个 families；
- 17 个 adapters；
- 582 个 fresh post-authorization unit；
- 2 个 ledger replay unit；
- 0 个 pre-authorization unit；
- 0 个 unresolved provenance unit。

**Baseline/门禁**

- 至少 12/14 variants admitted；
- exactly 8 families；
- 每个 admitted variant 至少 2 个 source-disjoint project；
- 至少 24 个 exact-site development-valid unit；
- admitted unit 上 0 noninterference failure；
- provenance 必须为 fresh post-authorization，replay 不得伪装成 fresh。

**评价指标**

- attempted/valid/failed units；
- variants/families/projects admitted；
- exact-site execution；
- propagation/noninterference/equivalence stage；
- failure atlas；
- provenance classification；
- conservative upper bound。

**结果**

- attempted/valid/failed = 584/0/584；
- admitted variants/families/projects = 0/0/0；
- fresh_post_auth=582；
- replay=2；
- pre_auth=0；
- unresolved=0；
- propagation/noninterference/equivalence reached count 均为 0；
- `noninterference_gate_status=NOT_REACHED`。

失败图谱：

| 失败类别 | 数量 | 占 584 的比例 |
|---|---:|---:|
| ORIGINAL_INPUT_FAILURE | 197 | 33.73% |
| BUILD_FAILURE | 165 | 28.25% |
| PUBLIC_API_CERTIFICATE_MISSING | 146 | 25.00% |
| API_BINDING_FAILURE | 42 | 7.19% |
| EXACT_SITE_NOT_EXECUTED | 19 | 3.25% |
| MUTATION_SITE_NOT_FOUND | 8 | 1.37% |
| TRIGGER_EVIDENCE_INSUFFICIENT | 5 | 0.86% |
| DEPENDENCY_OR_RUNTIME_UNAVAILABLE | 2 | 0.34% |
| 合计 | 584 | 100% |

门禁结论：

- ≥12 variants：FAIL，实际 0；
- exactly 8 families：FAIL，实际 0；
- 每 variant ≥2 source-disjoint projects：FAIL；
- ≥24 valid units：FAIL，实际 0；
- 非干扰不是 PASS，而是 NOT_REACHED。

即使对两个 replay 单元作最宽松解释，仍有：

- valid≤2<24；
- variants≤2<12；
- families=1≠8；
- 每 replay variant 仅 1 个项目<2。

因此 D1 development gate 在任何合理 replay 解释下都不可能通过。

**证据锚点**

- D1 audit commit：`48eaba272220c0d50e783abdabffa0b3b35cdbed`；
- FULL-FAILURE-ATLAS SHA256：`7afdc89d079a05ee43efebb6ea884d1df4505d47c5a1c15c8612041dba72acf8`；
- EXECUTION-PROVENANCE-AUDIT SHA256：`c1cab4c1ed0645cc0e6738feb38a457de529600ff1601b74a12fa1e1aa28bf80`；
- UNITS-LEDGER-COMPARISON SHA256：`814f726fdde74147d30f91471bbc2eea4abe91aaa1c28a4268039251f20d49a8`。

### 6.5 E-P12-5：P12 终态摄取与终止证明

**研究问题**

P12 是否能够独立摄取 D1 失败证据，并在不改写历史的条件下证明后续科学阶段必须关闭？

**对象**

- D1 commit/tree；
- 五个冻结输入产物；
- P12 intake/verifier；
- 全部 authorization flags。

**Baseline**

- D1 门禁要求；
- 对 replay 的最宽松上界；
- 未授权后续阶段必须为 false/0。

**评价指标**

- 输入哈希一致性；
- 独立检查；
- conservative upper bound；
- authorization flags；
- 是否改写 MR 审计或历史 stop。

**结果**

- P12 commit：`899dd079386b6365bd1298921a21435004400cde`；
- terminal：`P12_POST_V132_RECOVERY_TERMINATED_D1_DEVELOPMENT_GATE_NOT_MET`；
- 独立检查 24/24 PASS；
- `CORE_OPERATORS_FROZEN=false`；
- `validation_execution_authorized=false`；
- `target_mutant_generation_authorized=false`；
- `D2_open_count=0`；
- `operator_mapping_count=0`；
- `mt_execution_authorized=false`；
- `live_pilot_authorization_issued=false`；
- `provider_calls=0`；
- `mr_offline_audit_rewritten=false`。

**合法结论**

P12 正确终止并保留了证据链；不能据此推断算法失败率、RFDS、MR 质量或 MT 效果。

---

## 7. 原 P12 已设计但未执行的确证性实验

本节只能放在“planned study / terminated protocol”中，不能放在 Results。

### 7.1 原研究问题

在相等选择预算下，S1 residual-guided portfolio 是否比 S2 classical-MS-guided portfolio 检测更多未见真实语义缺陷族？

### 7.2 实验对象与规模

- D0：既有开发证据；
- D1：新的、MR-free 的开发 families；
- D2：独立 admission 的真实缺陷 families；
- 原计划 20 个项目、80 个 D2 families、160 个 D1 units/families；
- 最低执行 floor：17 个项目、60 个 D2 families。

### 7.3 Strategies/Baselines

| 策略 | 角色 |
|---|---|
| S1 residual-guided | 主方法 |
| S2 classical-MS-guided | 唯一 primary comparator |
| S3 MR-coverage-guided | secondary comparator |
| S4 random/generic | sanity floor |

预算原计划为每项目 `k=4`。

### 7.4 评价指标与决策规则

- Primary endpoint：RFDS；
- project-equal `Delta_real`；
- MID=0.10 RFDS；
- two-level BCa bootstrap；
- superiority：单侧置信下界 >0；
- practical superiority：单侧置信下界 >0.10。

### 7.5 未执行原因

- D1 development-valid unit=0；
- core operators 未冻结；
- validation 未授权；
- D2 未开放且 mapping=0；
- MR 仅离线合同审计，未生成真实 B0/B1；
- MT 未授权。

### 7.6 Fable 的正确表述

> The confirmatory real-defect comparison was prospectively specified but was not executed because the development gate failed. Consequently, no RFDS effectiveness claim is made.

不得把协议设计的严谨性写成效应存在的证据。

---

## 8. 现有方案的主要问题与根因

### 8.1 论文身份漂移

P3 在“SMS 构念论文”“语义变异系统论文”“MR 质量判别论文”“真实缺陷有效性论文”之间摆动，导致一篇论文承担过多证据责任。P12 又试图同时承担恢复合同、operator development、D2 数据、MR 生成和 MT 确证。

**修正**：先冻结 paper identity、primary claim 和唯一主 RQ，再设计实验。

### 8.2 中央实证链在 D1 处断裂

584/584 单元失败，0 个 development-valid unit，说明问题不是“效应不显著”，而是 intervention 没有被成功实例化。

**修正**：在大规模 population freeze 之前，先完成不计入正式样本的最小端到端 feasibility pilot。

### 8.3 冻结规模过大，但缺乏独立的前置资格筛选

失败主要集中在 original input、build、public API certificate 和 API binding。这些本应在冻结科学执行队列前由与结果无关的资格检查识别。

**修正**：设置独立的 buildability、public API、site existence、triggerability eligibility stage，并报告完整漏斗分母。

### 8.4 工程 PASS 与科学 PASS 容易混淆

大量 verifier/test/receipt 通过，但没有真实 provider call、真实 B0/B1、operator mapping 或 MT。

**修正**：论文中的每个表格增加 `evidence_type={engineering, readiness, scientific, planned}` 字段。

### 8.5 SSOT 与手稿数字漂移

v4 Cliff’s delta 在 `main.tex` 与 `paper_numbers_v4.json` 中冲突。这会直接损害可复现性和审稿可信度。

**修正**：

- 只允许结果脚本生成 JSON；
- 表格、正文和摘要数字从 JSON 模板化注入；
- CI 比较 manuscript-derived numbers 与 SSOT；
- 不一致时阻断构建。

### 8.6 语法 baseline 过窄

Cosmic Ray 默认一阶配置只能支持局部结构比较，不能支撑语义变异普遍独特性。

**修正**：后续至少包含多个 mutation engine、定制算子和 higher-order mutation；若资源不足，收窄主张。

### 8.7 等价性标准发生概念漂移

早期材料存在把有限行为一致近似为等价的风险；后期协议采用 certificate-first。两套定义不能混用。

**修正**：证明型等价、测试未区分和 unresolved 三态分离；有限抽样永远不能升级为数学等价证书。

### 8.8 D0 真实缺陷样本具有选择偏差和 ceiling

`verified_full` 依赖 MR-discriminating oracle，30/30 face 也缺少可辨识空间。

**修正**：D0 只用于开发；真正的验证必须来自独立、盲化、预先定义 admission 的 holdout。

### 8.9 样本量和统计模型与数据分布不匹配

n=12、有效 cell 数有限、45/60 SMS=0、OR 退化、mixed model singular、power≈0.491。

**修正**：使用 zero-inflated/hurdle 或两阶段 estimand；先估计可实例化概率，再分析条件 SMS；按 cluster/project 做功效设计。

### 8.10 H1 与 class-targeted operator 的适用域不匹配

若 operator 本来只针对特定程序类别，要求其在 9/12 PUT 上都成功，会把“不适用”与“实现失败”混为一谈。

**修正**：在观察结果前冻结 operator applicability matrix；主分母只包含理论上适用的 PUT，同时单独报告全体覆盖率。

### 8.11 来源版本的审核协议不完全对称

v3 与 v4 的来源、审核和机械门禁并非完全一致，source ablation 可能混入 protocol effect。

**修正**：后续来源比较必须固定 prompt、parser、review、admission、budget 和 temperature，仅改变 source。

### 8.12 LRCA 阈值存在开发集过拟合风险

在同一数据上网格选择阈值再报告性能，会高估泛化。

**修正**：开发集选阈值，独立 calibration/validation set 锁定评估。

### 8.13 D2 readiness 发生在科学顺序之外

D2 维护被正确标注为 `OBSERVED_OUT_OF_SEQUENCE_D2_READINESS_MAINTENANCE`，虽未开封，但容易在叙述上造成“D2 已经完成”的误解。

**修正**：只报告 asset readiness，不报告检测、映射或效应。

### 8.14 MR 仅完成离线合同

24/24 对抗测试证明实现行为，但 provider_calls=0、真实 B0/B1 均未生成。

**修正**：未来必须把“contract validation”和“scientific MR validation”设计为不同 RQ、不同表和不同 authorization。

### 8.15 版本、分支和合同层级过多

V125、V132、POST-V132、多级 intake/rebind/audit 增加了可审计性，也增加了叙述成本和操作错误面。

**修正**：新 lineage 采用一页 state machine、一份 machine-readable manifest 和单一顶层证据索引。

### 8.16 两个 replay unit 的 provenance 不完整

两个单元属于 `REPLAY_LEDGER` 而非 fresh。虽然保守上界证明表明它们不影响 gate 结论，但必须永久保留该限定。

**修正**：新执行的每个 unit 在运行前分配不可变 run ID，并绑定 authorization timestamp、commit、container digest 和 input hash。

### 8.17 潜在的 salami slicing 与贡献重叠

P3 和 P12 若重复报告相同 D0/P12 结果，容易造成重复贡献。

**修正**：P3 只引用 P12 的“confirmatory extension terminated”事实；P12 只把 SMS 当被治理的研究对象，不重新宣称 P3 构念贡献。

---

## 9. 避免重蹈覆辙的新研究顺序

### Stage 0：冻结论文身份和 claim ledger

在任何新实验前固定：

- 唯一 primary RQ；
- 唯一 primary endpoint；
- 主比较对象；
- 可证伪假设；
- success/failure/termination 条件；
- 每类证据允许支持的 claim；
- 哪些结果只能进入 appendix 或 artifact paper。

### Stage 1：独立资格筛选

对候选项目只检查与结果无关的属性：

- reproducible build；
- pinned dependencies/container；
- public API certificate；
- original input 可运行；
- mutation site 存在；
- trigger 可执行；
- license 和 archival availability。

筛选脚本、阈值和排除理由必须在看到 mutation/MR outcome 前冻结。

### Stage 2：最小端到端 feasibility pilot

使用新的、明确标记为 **pilot-only** 的 lineage：

- 2–3 个项目；
- 至少 2 个理论适用 variant；
- 每个 variant 至少 2 个 source-disjoint project（若资源允许）；
- 完整贯通：
  `build → API bind → site → trigger → propagation → noninterference → equivalence disposition`。

Pilot 的目标不是估计效应，而是证明操作链可执行。Pilot 数据不得进入正式 confirmatory effect estimate。

### Stage 3：冻结 applicability-aware operator population

- 先定义 operator × program-class applicability matrix；
- “不适用”“实现失败”“触发失败”“传播失败”“未决等价”分别编码；
- 只有在 pilot 达到门禁后才能冻结正式 D1 population。

### Stage 4：D1 开发与独立校准

- D1 用于算子开发、阈值和预算校准；
- 保留 source-disjoint 要求；
- 预注册每阶段漏斗及最低有效样本；
- 失败即终止，不以补样替换 family；
- D1 不进入最终真实缺陷效应估计。

### Stage 5：真实 MR 的独立验证

在 provider call 被明确授权后：

- 生成真实 B0/B1；
- B0/B1 共享除实验变量外的全部 pipeline；
- 盲化项目标识和策略标签；
- 人工语义审核与机械 admission 分离；
- 报告 inter-rater agreement、repair rate、timeout 和 rejection funnel；
- 先证明 MR 质量，再把 MR 用于 D2。

### Stage 6：D2 holdout 和 mapping

- D2 admission 在看不到 operator/MR outcome 的角色中完成；
- commitment 在 D1 和 MR gate 通过后才开封；
- mapping 规则预注册；
- 失败 family 保留，不后验替换；
- 记录 family、project、language、failure type 的分层信息。

### Stage 7：确证性 MT

- 固定 S1/S2/S3/S4；
- 固定预算 k；
- 以 S1 vs S2 为唯一 primary comparison；
- RFDS 和 project-equal difference 为主；
- 使用 cluster-aware BCa/bootstrap 或与零膨胀相容的预注册模型；
- 同时报告绝对效果、置信区间、失败漏斗和未决等价比例；
- 达不到最低样本 floor 时只报告描述性结果，不做优越性结论。

### Stage 8：独立审计与自动生成论文数字

- 审计者只能读取冻结 evidence package；
- 所有数字从同一 SSOT 生成；
- manuscript build 在数字、哈希、样本数或状态冲突时失败；
- artifact DOI/commit 与论文版本一一绑定。

---

## 10. 后续研究的建议假设

以下是假设草案，不是已有结论。正式执行前需单独预注册。

### Feasibility hypotheses

- **F-H1**：通过独立资格筛选的 pilot unit 中，至少 80% 能到达 exact-site execution。
- **F-H2**：到达 exact-site 的 unit 中，至少 70% 能到达 propagation assessment。
- **F-H3**：每个冻结 variant 至少在两个 source-disjoint project 上形成 development-valid unit。

### Construct hypotheses

- **C-H1**：在预先声明为 applicable 的 operator–program cell 中，非等价实例化率高于 0.5。
- **C-H2**：SMS 的 aligned/cross 差异在 held-out source 上方向一致，且置信区间不跨越预注册最小效应。
- **C-H3**：certificate/unresolved 分层后，SMS 结论对等价处理敏感性保持在预设界限内。

### Confirmatory real-defect hypothesis

- **R-H1**：相等预算下，S1 相对 S2 的 project-equal RFDS difference 的单侧 95% 下界 >0。
- **R-H2**：若要主张实践优越性，则同一下界必须 >0.10；否则只能主张统计方向，不主张实践重要性。

建议先通过 Stage 2 feasibility，再决定是否值得重新启动 R-H1/R-H2。

---

## 11. Fable 应产出的具体文档

### 11.1 P3 argument blueprint

应包含：

1. 一句话论文身份；
2. 一个 primary claim；
3. 3–4 个 secondary claims；
4. RQ–evidence–claim 对照表；
5. H1–H4 未满足的诚实叙述；
6. 理论贡献、局部实证证据和负结果的章节安排；
7. 需要删除或降级的旧强表述；
8. SSOT 冲突修复前的占位符；
9. 投稿前所需的形式审计和复现检查。

### 11.2 P12 argument blueprint

应包含：

1. 一句话论文身份；
2. 治理/基础设施型 primary claim；
3. 584-unit failure atlas 的核心结果；
4. MR offline contract 和 D2 readiness 的证据边界；
5. 原 RFDS 实验“planned but not executed”的单独章节；
6. authorization state machine；
7. 工程 PASS 与科学未执行的明确区分；
8. 新 pilot 的 preregistration outline。

### 11.3 Claim–evidence matrix

每个 claim 至少包含：

| 字段 | 要求 |
|---|---|
| claim_id | 唯一编号 |
| claim_text | 可证伪、避免绝对化 |
| evidence_type | theory / scientific / engineering / readiness / planned |
| source | 文件、commit、table 或 artifact |
| result | 数值或状态 |
| limitations | 选择偏差、样本量、baseline、未到达阶段等 |
| allowed_location | abstract / results / discussion / appendix only |
| status | supported / qualified / blocked / contradicted / not executed |

### 11.4 Fable 不应直接生成的内容

- 不生成虚构引用、DOI、数据集或统计结果；
- 不为 H1–H4 重新选择更宽松阈值；
- 不把 verifier 通过写成科学有效性；
- 不把 77 个 D2 ready family 写成 77 个成功检测；
- 不把 584 次失败写成“方法的缺陷检测失败率”；
- 不把未执行的 RFDS 计划写入 Results；
- 不在 SSOT 冲突解决前固定 v4 delta；
- 不把有限抽样一致写成等价证明。

---

## 12. 建议的最终论文主张

### P3 可用的一句话主张

> 本文提出 SMS 作为面向语义分层的 MR 充分性构念，证明其与经典 Mutation Score 的条件关系，并通过 12-PUT 受控审计表明：该构念捕获了一个与默认一阶语法变异仅部分重叠的空间，但其当前实例化表现出显著零膨胀、类别异质性和 MR/容差依赖，因此尚不能支持跨项目或真实缺陷优越性主张。

### P12 可用的一句话主张

> 本文报告一套内容寻址、角色隔离、授权驱动的失败关闭实验工作流；该工作流通过离线对抗审计并在 584 个开发单元均未达到科学门禁时阻止了 D2 映射和 MT，从而提供了可复核的失败图谱和准备度证据，但不提出真实缺陷检测有效性主张。

---

## 13. 证据来源索引

Fable 应优先从以下本地来源读取和引用数字，不应依赖聊天转述：

1. `research/p3-semantic-mutation-core-claims-rqs-v1.2.0.md`
2. `research/evidence/p3_claim_ledger_v1.2.0.yml`
3. `docs/decisions/2026-07-07-p12-tosem-boundary.md`
4. `docs/protocols/P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md`
5. `docs/superpowers/specs/2026-07-11-tosem-v1.1.2-real-fault-dve-design.md`
6. `data/results/paper_numbers_v3.json`
7. `data/results/paper_numbers_v3b.json`
8. `data/results/paper_numbers_v4.json`
9. `submission/arxiv-20260704/main.tex`
10. P12 commit `b7e8be973f9247f74ea6af61de269adbbd9a954f`（MR offline audit）
11. P12 commit `44d8b50c6b83cf46cb1f384ffe814ec20f7985b9`（D2 readiness）
12. P12/D1 commit `48eaba272220c0d50e783abdabffa0b3b35cdbed`（D1 failure atlas）
13. P12 commit `899dd079386b6365bd1298921a21435004400cde`（终止摄取）

若本地源、冻结 artifact 和聊天报告冲突，优先级应为：

> 冻结 artifact + verifier  
> → claim ledger/SSOT result JSON  
> → 生成的手稿  
> → 聊天转述。

任何冲突必须显式报告，不得静默调和。

---

## 14. 启动 Fable 时可直接使用的任务说明

> 请依据本计划书生成两个相互独立的论文论证蓝图：P3 为“SMS 构念、形式关系、受控边界审计与负结果”，P12 为“失败关闭实验治理、准备度与跨项目开发失败图谱”。先生成 claim–evidence matrix，再生成论文大纲，不要直接扩写完整论文。所有 H1–H4 均保持未满足；P12 RFDS 比较标记为 planned but not executed；MR 24/24 仅为离线合同测试；D2 77/94 仅为 readiness；D1 的传播、非干扰和等价性均为 NOT_REACHED。发现 SSOT 数值冲突时保留占位符并输出修复清单。最后分别给出每篇论文的 primary claim、允许进入摘要的三条结果、禁止出现的五条强主张，以及继续实验前必须满足的 gate。

