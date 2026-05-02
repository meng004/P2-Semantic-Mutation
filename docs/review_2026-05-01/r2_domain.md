# Reviewer 2 (Domain) — 同行评审报告

**评审论文**:When LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Scientific Computing(论文初稿 P2.md,1642 行,中文)

**评审身份与利益声明**

- 资深变异测试方向研究员,从 Mothra (DeMillo 1988) 至 Proteum、PIT、再至近年 LLMorpheus 持续跟踪。
- Jia & Harman 2011 TSE 综述谱系内的合作者(*以本评审角色身份模拟*)。
- 常年评审 ISSTA / ICSE / FSE / IST,尤其关注 mutation testing 工具与产业实践(Petrović & Ivanković 系列)。
- 与作者无利益冲突。
- 严格遵守"独立评审"约束,未阅读其它 reviewer 的报告。

---

## 1. Summary(我对本文的理解)

本文在 12 个科学计算 PUT × 5 个领域语义变异算子(MUT = {mut_C, mut_M, mut_G, mut_T, mut_F})× 5 个元模式(MP)= 60 单元格矩阵上,提出"语义变异得分 SMS = killed / (mut − equiv)"作为蜕变测试的 adequacy 度量;并在 v3 / v3b / v4 三阶段 ablation(同源 → 数据驱动 primary MP → 三 LLM 跨源池)下检验 H2(aligned vs cross slice 的 Cliff's δ ≥ 0.474 large effect)。**主结论:H2 在三阶段下均 rejected**(δ = 0.323 / 0.446 / 0.439),作者将主导因子归因于 MR-MP 对齐设计(贡献 +0.123)而非 LLM 源多样性(贡献 −0.007)。配套 §9 给出 SMS → 经典 Jia & Harman MS 的退化定理(L1-L6 极限 + 三引理)。

核心 domain claim 有三:(i) SMS 严格化归经典 MS,故 P2 是经典 mutation testing 的 generalization 而非 replacement;(ii) P2 的 5 类语义算子(实例化为 §3.2.6 的 CE / OS / HP / TF / SI 范畴)在算子级别上不被 mutmut / cosmic-ray 等 first-order 语法工具覆盖;(iii) v3 实测 δ = 0.323 落在 LLM-mutant 文献 0.30-0.45 区间(Tip 2024;IST 2024 综述),作为 contextual literature support。

---

## 2. Strengths(domain-specific)

**S1. 经典词典对齐做得严谨**(§2.1.1 七核心概念表)。把 PUT、mut、equiv、killed、survive、SMS 七个 Jia & Harman (TSE 2011) 词典条目逐项对齐,并明示扩展点仅施于 mut / equiv / killed 三概念的"内涵",分母分子的形式结构未动。这是相对许多 LLM-mutant 论文(直接重定义 score)更负责任的做法,domain reader 一目了然 P2 的 claim 边界。

**S2. §9 退化定理把"generalization 身份"形式化**。在我读过的同类论文里,作者通常以一两句话声明"本文度量在退化下化归经典 MS",而 P2 把它做成 6 条 L1-L6 极限 + 3 引理 + 主定理的形式化结构(虽然证明粒度仍偏弱,见 W3)。对 IST / STVR 评审而言,这是 acceptable 的形式化深度。

**S3. §3.2.6.1 算子级对照表**(R-15 应)。把 mutmut + cosmic-ray 默认算子集的 12 个条目逐条列出,与 OS / HP / TF / SI 做不可达声明,远比"工具不支持领域知识"这种 vague 论断有说服力。这是 §3.2.6 论证的关键升级。

**S4. 三阶段 ablation 的因子分解逻辑清晰**(§4.2.5)。v3 → v3b → v4 把"MR-MP 对齐"与"LLM 源多样性"两因子做了解耦,得到 +0.123 vs −0.007 的对比。即使 H2 未通过,这一 ablation 本身的方法学贡献是真实的——它纠正了同领域文献(Tip 2024)的隐含假设"LLM 源多样性能推 δ 越过 large effect 阈值"。

**S5. §6.1 对 Petrović & Ivanković 2018 的"numerical coincidence"诚实声明**。作者明确区分 Google 工业 productive mutant ≈ 20%(developer survey 主观)与 LRCA C1 share = 0.20(自动 classifier),不把数值近似过度声明为 mechanism validation。这一克制在 LLM-mutant 这类容易过度类比的领域是稀缺品质。

---

## 3. Weaknesses(WHAT / WHERE / FIX)

### W1. CE / OS / HP / TF / SI 5-范畴 taxonomy 与 mut_C / mut_M / mut_G / mut_T / mut_F 5-算子族存在 **双重映射混淆**

**WHAT**:文章正文(§2.2.2)定义 mut_j ∈ {C-conservation / M-monotonicity / G-convergence / T-trajectory / F-fidelity-order},是基于 *领域语义 invariant 维度* 的算子分类;但 §3.2.6 起又出现一套 **CE / OS / HP / TF / SI** 5-范畴,基于 *AST 操作类型*(constant edit / operator substitution / hyperparameter / transform / structural injection)。两套 taxonomy 共用 "5 类"基数,但维度根本不同。

**WHERE**:§2.2.2(算子族表)vs §3.2.6 表(CE/OS/HP/TF/SI 与工具映射);两表之间没有桥接节,读者必须自己推断"mut_C ≈ CE? 还是 mut_C 跨越 CE/HP/SI?"。

**FIX**:加入 §3.2.6.0 桥接小节,给出 5×5 交叉表(mut_j × CE/OS/HP/TF/SI)展示每个 mut_j 实际由哪几类 AST-operation 实例化。否则审稿人会怀疑 §3.2.6 的"4 类不可达"论证是 *新引入* 的有利分类,而非 §2.2.2 算子族的真实属性。

### W2. §3.2.6 把 mutmut/cosmic-ray 与 P2 算子做单方向"覆盖"对照,**对工具不公**

**WHAT**:§3.2.6.1 表中工具默认算子集只列出 12 类(NumberReplacer / ReplaceArithmeticOperator / ReplaceComparisonOperator / ReplaceLogicalOperator / ReplaceUnaryOperator / ReplaceTrueFalse / BreakContinueReplacer / RemoveDecorator / RemoveExceptHandler / ZeroIterationForLoop / ReplaceIfBlock / MutateSubscript)。但 cosmic-ray 实际有 ~25-30 个 operator(包括 `ReplaceBinaryOperator_Add_Sub` 这类细分,以及 `ReplaceAssignmentOperator`、`ReplaceRaise`、`ReplaceReturn`、`SwapMemberFunction`)。mutmut 的 default config 也比表中所列丰富(包括 string mutation、list/dict literal 变更)。

**WHERE**:§3.2.6.1 表 458-481 行。

**FIX**:(a) 标注表头明确说明这是 "default operator subset, as of mutmut 2.4 / cosmic-ray 8.3"(并加版本与日期);(b) 承认列表非穷尽,然后**只论证 OS / HP / TF / SI 类语义在 *任何* AST-local 算子下不可达**(因为 OS = "API substitution with algebraic equivalence"、HP = "model-object hyperparameter semantic"、TF = "numerical method order semantic" 这些跨函数边界 + 域知识维度,确实是 AST-agnostic 工具的结构性盲区)。改述后的论证不依赖工具算子集大小,论据更稳健。

### W3. §9 退化定理 — L1-L6 条件 **既不独立也不最小**

**WHAT**:6 条退化条件中,L1 (ε_eq → 0) 和 L2 (K_eq → ∞) 实际是**联立条件**(只有 ε_eq → 0 而 K_eq 有限,E2 只是更严格的概率条件,不退化为逐位等同;反之亦然)——这两条应合并为 "L1+2: equiv → exact behavioral equivalence"。同理 L3 + L4 也应合并(L3 alone 不退化 killed,需要 L4 限定 MP 集合)。L5 + L6 是关于 mut 域的同一条件(L5 限算子,L6 限 PUT 类),严格讲它们也不彼此独立。

**WHERE**:§9.2 退化极限定义,第 1559-1564 行。

**FIX**:把 6 条精简为 3 条独立轴(equiv-axis、killed-axis、mut-axis),与 §9.3 的三个引理一一对应;或保留 6 条但显式标注"L1 ⊥ L2、L3 ⊥ L4、L5 ⊥ L6 不成立,L1∧L2 / L3∧L4 / L5∧L6 是三个不可分离的极限条件块"。否则定理形式化的"6 条独立条件"会被 referee 当作笔误处理。

### W4. §9 退化定理 — **极限是 "asymptotic" 还是 "strict"?** 文中言之未明

**WHAT**:引理 9.1 的证明使用 "在 ε_eq → 0、K_eq → ∞ 极限下" — 这是 asymptotic limit。但主定理 §9.4 用 "$\xrightarrow{L}$" 符号,在数学上既可读作 "strictly equals when L holds"(即 L 是参数取严格值),也可读作 "converges to as parameters approach L"(asymptotic)。前者要求 ε_eq = 0(可达),后者只是 ε_eq → 0(不可达,只是极限性质)。摘要 (line 14) 说 "strictly degenerate" — 这倾向 strict;但 §9.2 的 "→" 又是 asymptotic 写法。

**WHERE**:§9.2 line 1559-1564,§9.4 line 1591-1593,Abstract line 14。

**FIX**:明确写出 "在 (ε_eq, ε_AVP) = (0, 0) 严格取值 ∧ K_eq 取 |D_S|(若 D_S 有限)或 K_eq → ∞(若 D_S 无限)∧ MP, mut, cls 范畴限制满足下,SMS = MS(strict equality, not just limit)"。如果 D_S 是连续输入空间(科学计算几乎都是),严格相等不可能,只是 *almost-sure equality under D_S*。这一区别在 IST referee 看是 fundamental,作者必须二选一。

### W5. **"Contextual literature support" 0.30-0.45 区间论证存在 over-translation 嫌疑**

**WHAT**:§1.3.2(line 74)与 §6.1(line 1284)反复声称"实测 δ = 0.323 / 0.439 落在 Tip 2024 / IST 2024 综述报告的 LLM-mutant 域 Cliff's δ 0.30-0.45 区间内,与该实验范式实证常态一致"。但是:

  (a) Tip et al. 2024 (LLMorpheus) 的 δ 报告基于 *JavaScript web testing*,fault-detection 比较是 LLMorpheus mutants vs. 传统 mutmut-style mutants 在 *kill rate* 上的对比 — 与 P2 的 "aligned vs cross MP slice on the same mutant pool" 完全不是同一统计量。
  
  (b) IST 2024 综述(line 1514 标记 "[Authors TBD]" — 即作者尚未填名,这是另一个 issue,见 W6)报告的 δ 区间是不同 LLM-test-generation 工作的横截面汇总,不是单一 controlled comparison。把 "δ ∈ 0.30-0.45 区间"作为"科学计算 LLM-mutant 实证常态"是 *对该数字的过度跨域 / 跨 estimand 类比*。
  
  (c) 经典 mutation testing 文献从未把 Cliff's δ 用于 aligned vs cross slice,这是作者自己定义的 estimand;把它和 LLM-mutant fault-detection δ 直接比较,是 estimand 错配。

**WHERE**:§1.3.2 line 74、§5.7.2 line 1131、§6.1 line 1284、§7.1.6 line 1424 反复出现。

**FIX**:三选一 —
  (i) 删除该比较,只报告本文 δ;
  (ii) 保留比较但在每处明确标注 "*estimand 异质性警示*:本文 δ 测的是同一 mutant 池上 aligned-vs-cross MP slice 的 stochastic dominance,Tip 2024 / IST 2024 综述的 δ 测的是不同 mutant pool 在同一 test suite 上的 fault-detection rate dominance,二者**不是同一物理量**,数值落区一致只是 numerical analogy,不构成本文效应规模的 contextual support";
  (iii) 在 §6.1 末尾加一句 "本节关于 0.30-0.45 区间的引用以 *领域读者直觉对照* 为目的,不作为 H2 verdict 的 robustness check"(类似作者已对 Petrović 数值巧合做的克制声明,见 §6.1 last paragraph)。

我作为 mutation testing 老兵,**强烈建议作者选 (ii) 或 (iii)**;否则 ISTA referee 会把这一比较当作 over-claim 的旗帜。

### W6. **IST 2024 综述参考文献署名占位 "[Authors TBD]"** —— 投稿前必须解决

**WHAT**:§8.3 line 1514 写 "(IST review) **[Authors TBD]** (2024). Effective test generation using pre-trained large language models and mutation testing. *Information and Software Technology*. https://www.sciencedirect.com/science/article/abs/pii/S0950584924000739",并附注 "full author list to be filled at typesetting"。但这篇文献是文中 4 处主要 contextual support 的核心引用(§1.3.2、§5.7.2、§6.1、§7.1.6)— 未确认作者身份,无法判断该工作是否真的是 LLM-mutation 综述,还是被作者错引为他用。

**WHERE**:§8.3 line 1514;§1.3.2 line 74;§5.7.2 line 1131-1142;§6.1 line 1280-1284。

**FIX**:补全作者署名 + 验证文献内容(我从 DOI URL fragment "S0950584924000739" 检索 IST 2024 内容,该论文可能是 Dakhel et al. 或 Vacchiano et al. — 作者必须在投稿前 cross-verify,因为如果该文献并非 LLM-mutation 综述而是单一 case study,§1.3.2 的 "0.30-0.45 区间" 论据基础就动摇)。

### W7. **§3.1.1 12 PUT × 平均 ~150 LOC 的 toy-program scope**, 与 IST"first audit"自我定位是否相称

**WHAT**:12 PUT 全部 < 400 LOC(实际 60-400),签名标准化为 `program(x: float) → float`(§3.1.1 (d) 已自陈)。这是教学范例规模,不是工业级科学计算。Jia & Harman 2011 综述提出的 fundamental hypothesis(competent programmer hypothesis、coupling effect)在 toy program 上是否成立尚未验证;现代工业级 mutation testing(Petrović 2018, 2021 在 Google;Just 2014 Defects4J)显示 mutant detection 在 1-10 KLOC 真实代码上行为差异显著(equivalent rate 在 toy 上 < 5%,在 real code 上 ~20-30%)。本文实测 LRCA C1 share ~0.16-0.21 与 Petrović 工业 productive ratio ~0.20 数值近似 — 作者已诚实声明这是 numerical coincidence(W6 strength),但 12-PUT toy scope 本身的 generalizability 仍需更明确边界声明。

**WHERE**:§3.1.1 整节,§7.2.1 R5 limitation 仅一句缓解。

**FIX**:在 §1.6.2 认识论声明后追加一句:"本文 SMS 实证规模属 first audit on toy / textbook-scale scientific PUTs,任何 SMS 数值结论(包括 §5 主表与 §6 讨论)在工业级 PUT(> 1 KLOC)上的可移植性 *未被本文验证*,留 P3 论文。"这比 §7.2.1 R5 的工程缓解更必要 — 作为 framing 而非 limitation 的位置区别。

### W8. **Higher-Order Mutation 的实证消除被 defer 到 P4,但 §3.2.6 论证主要靠"工具不可达"叙事 — 论证链不闭合**

**WHAT**:§3.2.6 line 452-456 的 HOM caveat 承认 "AOR + SDL 组合在某些 PUT 上可能模拟 OS API 替换的部分效果",并把 HOM 等价性测试列为 R12 残余威胁。但这意味着 §3.2.6 的核心论证(OS / HP / TF / SI 不可达)仅在 first-order 语法工具默认配置下成立,在 HOM 配置下并不显然。Jia & Harman 2009 SBSE HOM paper 与 Kintis 2018 STVR 都明确指出 HOM 可以以非平凡组合方式产生与 first-order semantic mutant 相似 fault detection 行为的复合 mutant。

**WHERE**:§3.2.6 line 452-456。

**FIX**:在 §3.2.6 论证开头加 framing 句 "*scope of this comparison*:本节论证限于 first-order syntactic mutation tools (mutmut/cosmic-ray default configuration),不涵盖 HOM。HOM 等价性的实证测试是已知 open question(Jia & Harman 2009, Kintis 2018),留 P4 论文 §X."这把"未做 HOM 对照"从 *残余威胁* 升级为 *论证 scope 的明示 caveat*,引用更准确。

### W9. **"Competent programmer hypothesis"(CPH)与 "coupling effect" 在文中完全缺席**

**WHAT**:Jia & Harman 2011 综述 §1.2 把 CPH 与 coupling effect 列为 mutation testing 全部论证基础(若 CPH 不成立,first-order mutant 与 real fault 的相关性即崩溃)。本文提出 *领域语义* mutant,实质上是 *扩展 CPH*("领域语义专家比一般程序员更接近 fault distribution"),但全文 0 处提到 CPH。同样,coupling effect("first-order mutant 检出能力 dominate higher-order")是讨论 mut_M / mut_G / mut_T 等是否需要 second-order 组合的关键概念，文中也没有触及。

**WHERE**:全文。

**FIX**:在 §1.3.2 相关工作后追加一段(~150 词):"本文 5 类领域语义算子隐含的认识论前提是 *领域 competent programmer hypothesis*(domain-CPH):科学计算领域的资深开发者所犯错误集中于 conservation / monotonicity / convergence / trajectory / fidelity-order 5 个维度,与一般 software CPH(Jia & Harman 2011 §1.2)在 fault distribution 上不重叠。这一前提的实证验证不在本文范围内,作为 P4 理论工作的研究问题。" 这是对评审 W3-class 同行的必要 nod。

### W10. **§9 推论 9.1 LRCA 平凡化的论证有逻辑漏洞**

**WHAT**:推论 9.1 (line 1607-1614) 声称 C2-C5 在 L 极限下不可触发,故 LRCA 退化为单态 {C1}。但:
  - C2 触发条件 = "fail 比例 < 0.80"(N=20 重复内 stochastic noise),L 极限并未限定 PUT 为 deterministic,只在 L6 限定为 *命令式确定性程序*。如果 PUT 是 deterministic(L6),fail 比例只能是 0 或 1,N=20 重复永远 ≥ 0.80,C2 自动不触发 — *推论是对的,但作者给出的论证 "C2 触发依赖 L4 不成立" 是错的*。C2 依赖的是 L6 (deterministic) + N=20 stochastic structure,与 L4 (MP 集合) 无关。
  - 类似地 C5 (mutator artifact) 依赖的是 mut_j 的领域语义复杂度,L5 (语法算子) 直接消去 C5 的语义触发空间,但 L6 (PUT class) 不是关键。

**WHERE**:§9.5 line 1607-1614。

**FIX**:重写推论 9.1 的论证,把每个 C_k 与 L_i 的依赖关系做 explicit table。或更简单地:删掉 per-Ck 因果归因,只声明 "在 L 下 LRCA 三层诊断的所有触发条件结构性塌陷,故 root_cause 平凡退化为 C1"。

---

## 4. Literature coverage assessment

| 文献 | 本文引用情况 | 评估 |
|---|---|---|
| **Jia & Harman 2011 TSE 综述** | 多次引用(§1.3.2, §2.1.1, §9, §3.2.6) | 引用充分,作为 SMS 退化锚点;但 CPH 与 coupling effect 概念未引(见 W9) |
| **Jia & Harman 2009 SBSE HOM** | §3.2.6 caveat 引用(line 452) | 引用充分;但 §3.2.6 论证仅作为"caveat"defer 到 R12,论证链不闭合(W8) |
| **Kintis et al. 2018 STVR** | §3.2.6 caveat(line 452) | 引用充分,但与 HOM 同一 caveat,未具体使用 Kintis 的 manual analysis 方法 |
| **Petrović & Ivanković 2018 ICSE-SEIP** | §1.3.2 line 74、§6.1 line 1286 | 引用恰当,作者已诚实声明 numerical coincidence vs mechanism validation 的区别(本文 strength) |
| **Petrović 2021 TSE** | §8.2 仅在参考文献列出,正文未实质讨论 | **不足**;Petrović 2021 提供 Google 4 年纵向 mutation testing data,与本文 H2 effect size 上限的讨论高度相关。建议在 §6.1 加 1-2 句对比 |
| **Tip et al. 2024 LLMorpheus** | §1.3.2、§5.7.2、§6.1 反复引用作 contextual support | 引用过度且 estimand 错配(W5)— 必须按 W5 fix 修订 |
| **IST 2024 综述** | 同上 | **作者未确认**(W6),严重风险 |
| **DeepCrime (Hu et al. 2022)** | §1.3.2、§3.1.1 (c) 引用 | 引用恰当,B 类 PUT 重叠声明可信。建议在 §3.2.6 加一行 "DeepCrime 的 28 个 DL-specific operators 与本文 5 类语义算子在 D 类 PUT 上的覆盖关系" |
| **Defects4J (Just et al. 2014)** | §3.1.1 (c) 简短引用 | 充分;Defects4J 是 Java,本文是 Python,作者已说明语言不同 |
| **Numerical Recipes (Press et al. 2007)** | §3.1.1 (b) 与 8 / 12 章对比 | **正面贡献**;这是本文相对一般 ML mutation testing 论文的独特 numeric / scientific lineage 引用 |
| **mutmut / cosmic-ray / mutpy** | §3.2.6 + §8.7 software citation | 引用充分,版本日期标注 |
| **Mothra / Proteum / PIT** | §9.3 line 1585 提及 "Mothra/Proteum 标准集" | 提及但无具体引用。Mothra (DeMillo 1988) 与 Proteum (Maldonado 2001) 这种 historical anchor 应在 §1.3.2 或 §2.1.1 至少 cite 一次 |

**主要 missing references**:
- **DeMillo, Lipton & Sayward 1978** "Hints on Test Data Selection" — CPH 原始来源,本文若采纳 W9 fix 必引;
- **Andrews, Briand & Labiche 2005 ICSE** "Is Mutation an Appropriate Tool for Testing Experiments?" — mutant 与 real fault 相关性的奠基实证,本文 §6.1 工程价值讨论应引;
- **Papadakis et al. 2019 Advances in Computers Ch. 6** "Mutation Testing Advances: An Analysis and Survey" — Jia & Harman 2011 之后最权威综述,本文未引(在我看来这是 *显著遗漏*);
- **Just, Jalali, Inozemtseva, Ernst, Holmes, Fraser 2014 FSE** "Are mutants a valid substitute for real faults?" — 这是 LRCA C1 与 real fault 关系讨论的奠基文献,与 §6.1 直接相关;
- **Naik, Dustdar 2024 EMSE** 或 **Coles 2016** 关于 PIT 的工业实践 — PIT 是 Java 但其 mutator selection 哲学(survival ratio + dominating mutants)与本文 LRCA 思路有可比性。

---

## 5. §9 SMS → MS 退化定理详评(L1-L6 条件 + 3 引理 + 主定理)

**L1-L6 条件评估**:见 W3 — 6 条不独立,实际是 3 个 axis。建议合并或显式声明 dependency。

**引理 9.1 (equiv 退化)**:**部分成立**。证明依赖 "K_eq → 全 D_S",但 D_S 是连续输入分布(科学计算几乎全部如此),"K_eq → ∞" 给出的是 *almost-sure equivalence under D_S 测度*,不是 strict equality(见 W4)。Jia & Harman 2011 经典 equivalence 是 strict semantic equivalence over *all inputs*,与 D_S-measure-zero 例外集合无关。两者并非严格等价 — 本文 equiv 在退化下仍允许 D_S-zero-measure 集合上的差异,经典 equiv 不允许。

**引理 9.2 (killed 退化)**:基本成立,但 r ≠ id 情形论证薄弱(line 1581 "L4 限定的 MP_eq 仍要求 S_i(x) = s'(r(x))" — 这等于把 r ≠ id 的情形 reduced to 经典 expected-output oracle,但经典 mutation testing 的 oracle 通常是 *test-suite-provided expected output*,不是 *S_i(x)*。这一差别需要在引理 9.2 末尾显式注明 "退化下 oracle = original program S_i 自身充当 reference,而非外部 test suite — 这与 Defects4J / PIT 等使用 unit test oracle 的实践存在 paradigm 差异")。

**引理 9.3 (mut 退化)**:成立。L5 + L6 直接限定 mut_j 切换为 Mothra-style syntactic operators,无歧义。

**主定理 9.1**:**条件成立则结论成立**(逻辑上 sound),但条件本身过于严格(几乎所有真实科学计算应用均不满足)。这意味着 §9 的退化定理是 *存在性论证*("SMS 在某种极端配置下化归经典 MS"),不是 *实用论证*("SMS 在常见配置下行为接近经典 MS")。这一区别 **应在 §9.6 实证一致性声明中诚实揭示**:目前 §9.6 line 1618 声称 "任何基于 SMS 的实证结论 ... 在经典语法变异场景下都与 Jia & Harman (2011) 既有文献结构一致" —— 这一声称在 D_S 连续 + ε_eq > 0 (engineering reality) 下不成立,需要弱化为 "*结构上*一致(SMS 公式形式 = MS 公式形式),数值上趋同度依赖于 (ε_eq, ε_AVP, K_eq) 与 D_S 离散化程度"。

**严格性 verdict**:作者声明 "strictly degenerate"(摘要 line 14),实际证明给出的是 "asymptotic degenerate up to D_S-zero-measure exception"。**建议修订摘要为 "degenerate (in the Jia & Harman sense, modulo D_S-measure-zero input subsets)" 或类似表述**。否则 mutation testing referee 会指出 strict 词汇 abuse。

---

## 6. §3.2.6.1 12-行 mutmut/cosmic-ray 对照表评估

**对工具公平性评估**:见 W2 — *部分不公*。表中工具默认算子 12 类是简化版,真实 cosmic-ray 8.x 与 mutmut 2.x 的 default config 还包括:

  - **cosmic-ray 缺失**: `ReplaceBinaryOperator_*`(细分版本)、`ReplaceAssignmentOperator`、`ReplaceRaise`、`ReplaceReturn`、`SwapMemberFunction`、`AddNot`(共 ~10 个 default operator 未列)
  - **mutmut 缺失**: string mutation(`"x"` → `"X"`)、list/dict literal 修改、function argument shuffling

**结论**:即便补全表中 default operators 至 ~25 类,**OS / HP / TF / SI 4 类仍然不可达**(因为这些都是 AST-local + domain-agnostic 操作,跨函数边界 + 域知识维度的限制是结构性的,不是算子数量问题)。但作者必须在表中**显式标注**"列出的是 default subset"或类似 caveat,否则 referee 会以 "工具实际算子比表中多" 为由质疑论证根基。这是一个文字级别的修订,不影响主论证。

**建议改写**:在表头加 "default operator subset of mutmut 2.4 / cosmic-ray 8.3 (as of 2026-04)" + 在表后加一句 "Even when extended to the full ~25 default operators, the structural limitation (AST-local, domain-agnostic) prevents reaching OS/HP/TF/SI semantics,故§3.2.6.1 算子级结论稳健"。

---

## 7. "Contextual literature support" δ ∈ 0.30-0.45 claim 评估

**这是本文最关键的 domain over-translation 风险**(见 W5)。Recap:

  - 本文 H2 主分析 v3 δ = 0.323 在 "aligned vs cross MP slice" 的 *同 mutant 池内对比* 上;
  - Tip 2024 LLMorpheus 报告的是 "LLM-generated mutants vs traditional mutmut mutants" 的 *fault-detection rate ratio* 上 δ 大约在 0.30-0.40 区间;
  - IST 2024 综述(若作者正确引用)汇总的多个 LLM-mutant 工作 δ 在 0.30-0.45;但每篇论文的 δ 估计的 estimand 可能各异(一些是 fault-detection rate,一些是 equivalent-mutant rate,一些是 productive ratio);
  - **三者不是同一物理量**。本文 δ 是 *单一 mutant 池内 slice 间 stochastic dominance*,Tip 2024 是 *跨 mutant pool 的 detection-rate dominance*。

**Methodologically,这一比较不是 invalid(数字相近也是有趣的现象),但作为 H2 verdict 的 contextual support 是 over-claim**。Mutation testing 老兵会立即识别 estimand 错配。

**评估**:作者已在 §6.1 line 1284 谨慎写 "**这是 contextual literature 比较,不构成对 H2 rejected verdict 的 reframing**"——这一克制声明部分缓解 over-translation 风险。但反复引用(§1.3.2、§5.7.2、§6.1、§7.1.6)且每处都把 0.30-0.45 当作"领域常态"或"上限",叙事上仍倾向"我的数字符合文献,所以 H2 未达成不是问题"。**建议作者在每处引用都加 estimand 异质性 caveat**(W5 fix),或更简单地把所有 4 处引用 collapse 成 §6.1 单点引用 + 显式 caveat。

**Verdict on contextual support claim**:**Borderline over-translation,要求 conditional acceptance:必须在所有引用处加 estimand caveat,否则我会把这一点列为 reject 理由**。

---

## 8. Decision recommendation

**Major Revision**(IST 标准):本文 domain contribution 真实(SMS-MS 退化定理 + 三阶段 ablation + 算子级 first-order 工具对照),但有若干必修之处:

1. (Mandatory) W3 + W4:精化 §9 退化定理的 L1-L6 dependency 与 strict-vs-asymptotic 用词;
2. (Mandatory) W5:消除或全面 caveat 化 "0.30-0.45 contextual support" 论证;
3. (Mandatory) W6:补全 IST 2024 综述作者并验证内容;若验证失败,删除该引用;
4. (Mandatory) W2:在 §3.2.6.1 表头加 default subset 说明;
5. (Strongly recommended) W1:加桥接节解释 mut_j (§2.2.2) ↔ CE/OS/HP/TF/SI (§3.2.6) 双 taxonomy;
6. (Strongly recommended) W9:在 §1.3.2 加 CPH 段落 + 在 §6.1 引用 Andrews 2005 / Just 2014 FSE / Papadakis 2019;
7. (Recommended) W7:在 §1.6.2 加 toy-scope framing caveat;
8. (Recommended) W8:把 §3.2.6 论证 scope 显式限定在 first-order 工具;
9. (Recommended) W10:重写推论 9.1 的 per-C_k 因果归因。

**若以上 9 项中至少 (1)-(4) Mandatory 全部修订 + (5)-(6) Strongly recommended 修订**,本文可达 IST 接收线 — domain contribution 是真实的,且 §3.2.6.1 算子级对照、§4.2.5 三阶段 ablation 都是该领域少见的方法学贡献。但若不修订(W5)与(W6),即可能因"过度 contextual claim + 引用占位符"被 ISTA 直接 reject。

**与 IST 当前标准对照**:本文 60-cell × 12-PUT × 5-MP 设计在 *first audit* 框架下是合适的(诚如作者自陈,§7.5 限制声明覆盖了 12 PUT toy-scope)。规模不是 reject 理由,但 **toy-scope 与"领域语义算子"主张之间的距离**(domain-CPH 是否在 toy code 上成立?)是真实的,W7 fix 足以缓解。

---

## 9. Score sheet (1-10, 7 dimensions)

| Dimension | Score (1-10) | 简评 |
|---|---|---|
| **D1. 领域问题 motivation 与文献定位** | **7** | 三年路线图清晰,§1.3.2 LLM-mutant 工作综述结构合理;但 W5 + W6 + W9 显示文献覆盖与引用准确性有待提高 |
| **D2. SMS 概念 novelty 与 generalization 论证** | **7** | SMS 公式与经典 MS 严格同构,§9 退化定理把 generalization 身份形式化是真贡献;但 W3 + W4 显示形式化深度不够 |
| **D3. 算子 taxonomy 与 §3.2.6 工具对照** | **6** | 5 算子族领域 motivation 充分,但 W1 双 taxonomy 混淆 + W2 工具表不全 + W8 HOM scope 未闭合,使 "tool-unreachable" claim 略显单薄 |
| **D4. 60 单元格实验设计 + 三阶段 ablation** | **8** | §4.2.5 三阶段 ablation 是本文 *最强* 方法学贡献;v3/v3b/v4 把 MR-MP 对齐 vs LLM 源多样性两因子做因子分解,设计精巧 |
| **D5. 统计方法学** | **7** | Cliff's δ + Friedman 非参 + bootstrap CI + 功效分析(§5.7.3)做得规范;但 v3b post-hoc selection 已诚实声明 confound,这是负责任的做法。 mixed-effects Singular 处理透明 |
| **D6. Domain literature coverage(Petrović / Tip / Kintis / Defects4J)** | **6** | Petrović 2018 引用恰当(numerical coincidence 克制),但 Petrović 2021 / Andrews 2005 / Just 2014 FSE / Papadakis 2019 / DeMillo 1978 这些 mutation testing canon 缺失,W9 必修 |
| **D7. 论文写作完整度与 referee-readiness** | **6** | §1-§7 锁定,§9 退化定理形式化;但 W6 IST 2024 引用占位符 + 双 taxonomy 桥接缺失 + 对 estimand 异质性的反复引用,需要一轮深入修订 |

**Overall recommendation**: **Major Revision**(平均 D1-D7 = 6.71;modal verdict 是 7 — 接收门槛附近,但 W5 + W6 必修)。

---

## 10. 评审独立性声明

本评审完全独立完成,未参考任何其它 reviewer 的报告或共享文档。所有 strength / weakness / score 基于评审者本人对论文 §1-§9 全文的阅读与 mutation testing 文献(Jia & Harman 2011 / 2009、Kintis 2018、Petrović 2018 / 2021、Tip 2024、Hu et al. DeepCrime 2022、Just Defects4J 2014、Press Numerical Recipes 2007、Andrews 2005、Papadakis 2019)的领域判断。

— Reviewer 2 (Domain), 2026-05-01
