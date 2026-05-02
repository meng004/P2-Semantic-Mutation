# Editor-in-Chief Review Report — P2 Manuscript

**Manuscript**: *When LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Scientific Computing*
**Target Venue**: Information and Software Technology (IST)
**Review Date**: 2026-05-01
**Reviewer Role**: R0 — Senior Associate Editor (EIC perspective), independent review

---

## 0. Reviewer Identity (Configuration Card)

- 资深 Associate Editor,*Information and Software Technology* (IST),编辑经验 15+ 年(empirical SE 方向);
- 自研方向:mutation testing benchmarks(Defects4J 系产物的 second-order extension);熟悉 Jia & Harman 2011 综述脉络;
- 对照参考:Tip et al. (2024) LLMorpheus、IST 2024 LLM-mutant survey、Petrović & Ivanković (2018, 2021);
- 审稿关切:(i) IST 期刊 fit 与原创性边际;(ii) "negative/null result" 在方法学清洁度未达到时不可发表;(iii) v3 / v3b / v4 ablation 是否把 post-hoc 选择(c-class primary MP shift)与 headline contrast(LLM source diversity)混为一谈;(iv) 是否对 IST 读者群有足够 practical implication。
- **独立性声明**:本报告未读其他 reviewer 报告,亦未对其他 reviewer 的可能立场做预设。

---

## 1. Submission Summary(我对稿件的理解)

本稿提出 **Semantic Mutation Score (SMS)** 作为科学计算软件的 Metamorphic Testing (MT) adequacy 度量,公式上沿用 Jia & Harman (2011) 经典 `killed/(mut−equiv)` 结构,但在三个内涵维度做扩展:(a) mut(语法 → LLM 生成的领域语义算子,5 类:Conservation / Monotonicity / Convergence / Trajectory / Fidelity-order);(b) equiv(逐位等同 → E1∧E2 容差等价);(c) killed(等式 oracle → MP-AVP fail)。配套 **LRCA(Likely Root Cause Analysis)** 三层分类器(C1 真语义失效 vs C2-C5 容差/OOD/统计假设/伪影)作为工程归因层。§9 给出 SMS → MS 的退化定理。

实证基底:**12 PUT × 5 MP = 60 单元格**,跨 4 类科学计算程序(数值/概率/代理/ML),平均 24.3 mutants/cell(v4 跨源池),N=20 AVP 重复。

核心 ablation 设计(§4.2.5):

| 版本 | mutant 池 | c 类 primary MP | δ |
|---|---|---|---|
| v3(pre-registered) | Claude only | MP5(P1 沿用) | **0.323** |
| v3b(exploratory) | Claude only | **MP1**(post-hoc, argmax mean SMS) | 0.446 |
| v4(exploratory) | Claude+GPT+DeepSeek | MP1(继承 v3b) | 0.439 |

主要 verdict:**H2 rejected**(三阶段下 δ 均 < Romano 0.474 large-effect 阈值);v3 → v3b 的 +0.123 归因于 MR-MP 对齐设计,v3b → v4 的 −0.007 归因于 LLM 源多样性 → headline title:"When LLM Source Diversity Doesn't Help"。

H1(算子可行性,§4.8.2 R_sem > 0 全 37/37 算子)实质达成;H4 sign test v3 primary 3/4 partial、v3b exploratory 4/4;H5(suspect_share ≤ 0.20)校准最佳仍仅 12/60 通过,**未达成**;H3 在 §1.5 已正式撤回。

文章结构:§1-2 命题与符号;§3 PUT 矩阵;§4 流程(含 §4.2.5 跨源协议);§5 结果(§5.6 RQ1 / §5.7 RQ2 含 §5.7.3 power / §5.8 RQ3 / §5.9 RQ4);§6 讨论(含 §6.5 stakeholder analysis);§7 limitations;§8 references;§9 退化定理。

---

## 2. Strengths(具体优点)

**S1. 退化兼容性的正式化处理(§9 + §2.4.3)** 这是本稿真正区别于绝大多数"language-extension-style" mutation testing 论文的方法学贡献。§9.4 定理 9.1 明确给出退化极限 L1-L6,把 SMS → MS 的 "degenerate to classical" 从口头声明落到引理-定理结构。这对 IST 审稿群体极具说服力:它把作者的"经典扩展"叙事从 marketing 升格为 verifiable proposition。Jia & Harman 2011 综述发表 15 年来,语义 mutation 工作普遍只声称"兼容经典"而不证明,本稿的 §9 是少见的可信样本。

**S2. v4 跨源 ablation 的因子分解结构(§4.2.5(d) + §6.1)** 把 "LLM source diversity" 与 "MR-MP alignment design" 作为两个工程因子分别 ablate,得 +0.123 vs −0.007 的不对称对比,**首次在科学计算软件域上把两者解耦**。Tip 2024 LLMorpheus 是单 LLM,IST 2024 综述里的多个 LLM-mutant 工作均未做源多样性对照。这是真实的 IST-fit 贡献。三家 LLM 贡献近乎相等(Claude=101 / GPT=98 / DeepSeek=99,§4.2.5(d))也是值得记录的工程发现。

**S3. 对 v3b 的 confound 做了高度自觉的 caveat 报告(§3.5.1 + §5.7.2 + §5.8.4)** §3.5.1 明确写出 "此调整是 exploratory,不是 pre-registered;selection-on-the-response;未做 multiple-comparison 校正",并保留 v3 作为 primary verdict。审稿圈对 negative/null results 的方法学诚信门槛更高,而本稿在这一点上做得相当好——这是审稿人通常需要追问的问题,作者已主动给出。§5.8.4 把 Friedman 主效应与 H4 cross-class consistency 显式区分(两者逻辑独立),亦是诚实信号。

**S4. 多层 robustness 与 power 检查(§4.6.4 LRCA 校准、§5.6.2.1 H5 cutoff sweep、§5.7.3 power simulation、§7.1.6 pool 扩张)** 这一套四件式 robustness 报告是稿件能立得住的工程基础:LRCA 9-grid 校准显示 tolerance_multiplier 无影响而 ood_band 是唯一区分因子;H5 cutoff 在 [0.05, 0.40] 完全平坦在 20.0%,**任何 cutoff 都不能让 H5 通过 80%**——这把 "0.20 是 lucky pick" 的潜在质疑提前消解。§5.7.3 power simulation 给出 large-effect 检测功效仅 0.423,正确指出 "增加样本量不会让点估计自动突破 0.474"。

**S5. Stakeholder analysis(§6.5)与 §3.2.6 算子级对照(R-15 应)** §6.5.1-3 区分测试工程师 / MR 设计者 / 审计认证机构三类 stakeholder,各给 pain point + workflow + 不替代的内容。§6.5.2 甚至提供了 GitHub Actions YAML 模板。这正是 IST 审稿人持续询问的 "practical implication"。§3.2.6.1 算子级对照表把 mutmut / cosmic-ray 的 12 类默认算子逐项映射到 P2 的 OS/HP/TF/SI 类,论证 "这是结构上的不可达,不是算子集大小问题"——结构化论证强,对 R15 类 reviewer 有说服力。

---

## 3. Weaknesses(具体缺陷,WHAT / WHERE / FIX)

**W1. Title 与 headline finding 的 evidence 基础与 v3b confound 紧密耦合,论证在 EIC 视角下结构性脆弱。**

- **WHAT**:Title "When LLM Source Diversity Doesn't Help" 的核心证据是 v3b → v4 的 −0.007(§5.7.2)。但 v3b 本身是 post-hoc 数据驱动 c-class primary MP shift 的产物(§3.5.1),v3b 已在 c 类上 "把 c-class 推到 argmax(MP1)" 这个最有利于 alignment 的格式。**v4 与 v3b 在该最有利格式下比较时,几乎一致是预期内的(同 prompt 模板下三家 LLM 一致响应)**。换句话说,headline contrast 的 "denominator"(LLM source diversity 的贡献)与 "numerator"(MR-MP 对齐的贡献)在选择空间上不对称——前者在 v3b 已固定的 c→MP1 上检验,后者通过 v3 → v3b 的 selection 提取。
- **WHERE**:§4.2.5 表(680-684 行)、§6.1(1276-1281 行)的 "+0.123 vs −0.007 ≈ 17.6:1" 论断、Title 与 Abstract。
- **FIX**:三条任选其一 / 任选其二:
  1. 在 v3 (c→MP5, pre-registered) 基线上**也跑 v4-cross-source**(称为 v4-pre,c→MP5 cross-source)。如果 v4-pre 的 δ 与 v3 比较的 Δδ_LLM 仍 ≈ 0,本稿 headline 就有了 pre-registered 基础;若 v4-pre 显著 ≠ v3,headline title 必须修订。当前稿件**缺这一格点**,§4.2.5 表只列 v3 / v3b / v4 三阶段。
  2. 把 title 从 "When LLM Source Diversity Doesn't Help" 改为更克制的 "Under a fixed prompt template, three LLM sources contribute near-zero variance to SMS effect size",并把 §6.1 的 17.6:1 改报 95% CI 而非 ratio;
  3. 显式补一段 limitation 段落,声明 "ratio 17.6:1 是在 c→MP1 (v3b) 已选定的格式下计算,non-interaction 的因子分解不严格成立"。

**W2. Post-hoc c-class primary MP shift 的合理性论证不充分,§3.5.1 的 caveat 列表把责任甩给 R2 但稿件主结论仍依赖 v3b。**

- **WHAT**:§3.5.1 第 553 行写 "这是 selection-on-the-response,提高 H4 sign test 通过率与 δ 的同时引入 selection bias"——已经诚实声明,但仍把 v3b 作为 §6.3 H4 cross-class consistency 的 "严格达成 4/4" 的依据(§5.8.2 第 1188 行),这与 v3 primary 3/4 partial 的事实在 narrative 上有 dissonance。
- **WHERE**:§3.5.1(535-558 行)、§5.8.2(1184-1190 行)、§6.3(1300 行 "v3b 数据驱动 primary MP 调整后,sign test 4/4 严格达成")。
- **FIX**:在 §6.3 与 §6.1 中,把 "v3b 4/4 严格达成" 严格降级为 "v3b exploratory 4/4(post-hoc)";abstract 应只提 v3 primary 3/4。或者:补一个 leave-one-PUT-out cross-validation 实验,显示 c-class primary MP 在不同 LOO 数据划分下 argmax 是否稳定为 MP1。如不能补,**Title 不应以 v3b/v4 的强 4/4 信号为旗帜**。

**W3. Pre-registration claim 的强度与实际证据存在 gap。**

- **WHAT**:§3.5.1 多次称 "Pre-registered primary analysis(v3)"。但稿件内并未给出 pre-registration ID(OSF / aspredicted / 其它注册库)、注册时间、注册时确定的 H1-H5 阈值文档。如稿件仅仅 "在 v3 数据采集前确定 H1-H5 阈值",这只是 prospective 内部规则,**严格意义上并非 pre-registered**,与 OSF-style PRP 通常要求的注册凭证不同。
- **WHERE**:§1.5(85-88 行)、§3.5.1(537 行)、§5.2(953 行)。
- **FIX**:(a) 如已在 OSF / aspredicted 注册,**列出注册 URL 与日期**,放在 §1.5 footnote 或 §4 实验时序表;(b) 如未注册,删除 "pre-registered" 措辞,改为 "the v3 analysis plan was fixed prior to data collection (see internal protocol document `docs/protocols/p2_analysis_plan_v3.md`)" 并在 reproducibility package 给出该文件的 git commit time。

**W4. IST fit 与与 IST 2024 LLM-mutant survey 的 originality 边际未充分论证。**

- **WHAT**:§1.3.2 与 §6.1 多次引用 "Information and Software Technology(2024)综述报告 LLM-mutant 域 Cliff's δ 普遍落在 0.30-0.45 区间"。问题:(a) §8.3 第 1514-1515 行把该 IST 2024 综述记为 "[Authors TBD]","note: full author list to be filled at typesetting"——**这在 IST 投稿稿件里不可接受**,EIC 与 reviewer 会认为作者未完整阅读该综述;(b) 如该综述本身已系统化报告 LLM-mutant 在多领域上 δ 落在 0.30-0.45,本稿在 JS / Java 之外把同一规模 effect 推广到 Python 科学计算,**originality 较 marginal**(unless 解耦 MR-MP alignment vs source diversity 是真正 novel 贡献——这一点 W1 已质疑)。
- **WHERE**:§1.3.2(74 行)、§5.7.2(1131 行)、§6.1(1280 行)、§8.3(1514-1515 行)。
- **FIX**:(1) 立即补全 IST 2024 综述的完整 citation;(2) 在 §1.3.2 加一段 1/2 段子段落,**与 IST 2024 综述做点对点 contribution diff**:具体哪些 RQ 与那篇综述未覆盖、哪些 PUT class 是首次分析、对齐 vs 非对齐切片的 ablation 在那篇综述中是否报告;(3) 如 W1 的 ablation 不严格成立,**originality 必须改述为 "首次在科学计算软件域上系统报告 SMS"** 而不是 "首次解耦 MR vs LLM 因子贡献"。

**W5. SMS 度量与 Petrović & Ivanković Google 工业基线的对齐论证有过度声张风险。**

- **WHAT**:§1.3.2(74 行)与 §6.1(1286 行)反复引用 "Petrović & Ivanković (2018) 在 Google 50 万 mutant 数据上报告 productive mutant ~20%,与本文 §5.6.2 LRCA C1_share 实测水平(0.16 / 0.20)高度吻合"。§6.1 已诚实声明 "this is numerical coincidence not mechanism validation",但 abstract 与 §1.3.2 仍把这一对齐作为 contextual 支撑。Google 的 productive mutant 是 developer survey 主观判定,LRCA C1 是自动算法标注,**两者构念差异 + 数值近似 ≠ validity claim**。
- **WHERE**:Abstract(0.20 数值)、§1.3.2(74 行)、§5.6.2(1055 行)、§6.1(1286 行)。
- **FIX**:(1) 在 abstract 与 §1.3.2 删除该数值对齐;(2) §6.1 已自我声明不构成 validation,但当前 narrative 仍在 §1.3.2 / §6.1 之外用 "高度吻合" 措辞做暗示。建议把 §1.3.2 那一段重写为 "本文 LRCA C1 = 0.20 与 Google productive mutant ~20% 在 numerical scale 上接近,但二者构念差异(主观 developer survey vs 自动 classifier)使该对齐不构成 validity claim";(3) 在 §6.1 加一段子段落,提出后续验证路径(developer survey 抽样 + 算子-by-mutant 一致性测试)。

**W6. Mutant 池规模与 12 PUT 的 generalization 边界,与 RQ4 的 ρ = 0.107 / Spearman p = 0.74 的 negative-finding 价值缺乏 IST-readership 视角的论证。**

- **WHAT**:§5.9.3 已把原 "几乎独立" finding 弱化为 "未支持任何明确结论"(diligent move)。但这意味着 RQ4 实质上是 inconclusive,**完全成为占位**。abstract 与 keywords 列了 "Spearman" 但 RQ4 并未提供 actionable 信息。对 IST 读者(测试工程师 + MR 设计者)而言,RQ4 inconclusive 等于 "本稿在 SMS vs PC 的 diff 上无法给指导";同时 §5.6.1.1 的 75% zero-mass dominance 提示 RQ2 的 effect-size inference "实质上由 n_aligned = 12 主导",**这削弱了所有 RQ2 推断的实证强度**。
- **WHERE**:§5.6.1.1(1027-1045 行)、§5.9.3(1260-1266 行)、abstract 的 RQ4 表述。
- **FIX**:(1) RQ4 inconclusive 的话**从 abstract 删除**关于 SMS 与 PC 的描述,只在正文 §5.9 保留作为 "future-work hook";(2) §5.6.1.1 的 zero-mass dominance 已经相当于声明 "RQ2 的有效 n 是 12 而非 60",**这一点应在 §3 实验对象规模与 §5.7.3 power 章中前置声明**,而不是隐藏在 §5.6.1.1。审稿人若漏看 §5.6.1.1,可能在 reproducibility 复核时认为 "n_eff = 12" 是隐瞒。

**W7. §3.1 的 12 PUT 标量化签名(`program(x:float) → float`)对所有 SMS / Cliff's δ 结果产生的 systematic deflation 没有量化估计。**

- **WHAT**:§3.1.1(d) 第 401 行已声明 "本文标量化 PUT 强制 mutant 的语义复杂度上限,可能系统性低估工业 PUT 上的 SMS 与跨类差异"。但稿件未提供任何量化估计,例如:在工业级 mesh-IO 或 tensor-state PUT 上,典型 mutant 的 R_kill 与本文标量 PUT 的 R_kill 比值预期是多少?这把 "外推到工业代码" 完全推给 P3,但 IST 读者必然问 "这套 SMS 在 1-10 KLOC 工业代码上仍稳吗?"。
- **WHERE**:§3.1.1(d)(399-403 行)、§7.5 limitation 第 6 条。
- **FIX**:加一个 §3.1.1(e) 半页 subsection,引用 1-2 篇工业级 mutation testing 工作(Petrović 2021 Google;Just 2014 Defects4J;DeepCrime 2022),给出 "工业 PUT 平均 mutant 数 / 平均 R_kill" 与本稿的对比表,即使数字粗糙。或者,做一个 toy 实验:在 12 PUT 中选 1-2 个(如 A1 Lorenz)增量到 vector-state interface,观察 SMS 的变化方向。这一点可以是 "1-2 page addition" 而非 P3-scale work。

**W8. §9 退化定理的形式化深度与稿件其余内容的实证身份不匹配,可能产生 "形式 vs 实证" 错位审稿压力。**

- **WHAT**:§9 的引理 + 定理 + 推论 形式相当 polished,但 IST 是 empirical SE 期刊,审稿人通常期待 "实证为主 + 理论为辅"。当前 §9 的 weight 与 §5 实证章节相当,可能让 reviewer(尤其 R3 形式化 reviewer)在 §9 的引理 9.2 "killed 退化" 中找瑕疵(例如 r ≠ id 时 L4 的处理),从而拖累整体 verdict。
- **WHERE**:§9.3-9.5(1566-1614 行)。
- **FIX**:(a) 把 §9 缩到 1-1.5 页,定理 9.1 主体保留,引理证明放 appendix;(b) 在 §9 标题旁加一句 "this section is supplemental;empirical contributions are §5-§7";(c) 引理 9.2 关于 r ≠ id 时 L4 的论证(第 1581 行)需要更精确——当前 "将其视为一个由原程序构造的参考输出 oracle" 是含糊的,应改写为 "在 L3 ∧ L4 下,R(y, y') ≡ y = y' 强制 AVP 拒绝任何 r-induced 偏离;killed_{i,k,j} 退化为 ∃ x: S_i(x) ≠ s'(r(x)),与经典 mutation testing 中 transformed-input oracle 的 fail 准则同构(Ammann & Offutt 2008 §11.4)"。

---

## 4. Detailed Section-Level Comments

**§1 (Title / Abstract / Identity)**

- Title 与 abstract 的 "When LLM Source Diversity Doesn't Help" 与 "−0.007" 是 W1 的核心争点;请参见 W1 的 fix。
- §1.4 RQ1-RQ4 与 §1.5 H1-H5 的对应关系清晰。**H3 撤回的处理(§1.5 注)是 textbook-level 的好** —— 撤回理由(equiv 触发 < 10 cells / 双向阈值结构性塌陷)逻辑充分,保留 H 编号空缺也是正确选择。
- §1.6.1 创新归属 C-I 至 C-IV 中,**C-II "SMS + 向下兼容性" 与 §9 配对良好**。但 C-III LRCA 的归属仅声称 "工程归因层、纯描述、不进 SMS"——若 LRCA 不进 SMS 公式,它在 §6 的 narrative 中应为 secondary contribution,可考虑把 C-III 改称 "辅助归因工具"。

**§2 (符号系统)**

- §2.1.2 符号系统总表是稿件的严肃骨架,锁定层与开放层的分离做得清晰。
- §2.4.3 "向下兼容性声明" 段落与 §9 应在 §2 给出指针,目前 §2.4.3 描述为 prose,§9 形式证明在最末——§2.4.3 第 267 行末尾应加 "形式化证明见 §9 定理 9.1"。

**§3 (PUT 矩阵)**

- §3.1.1(c) 的 benchmark 对照表清晰且诚实(承认与 DeepCrime / DeepMutator 的 PUT 重叠)。
- §3.1.1(d) limitation 涉及 W7,见 W7 fix。
- §3.2.6 + §3.2.6.1 算子级对照是 R-15 应,做得扎实(见 S5)。§3.2.6.2 "可选实证" 是 future-work hook,可保留。
- §3.5.1 的 v3b shift 是 W2 核心,见 W2 fix。

**§4 (流程)**

- §4.2.4 双盲复核(方案 C)与 §4.2.5 跨源协议接口清晰。但 §4.2.5(b) "MVP 不调用 reviewer LLM" 是工程妥协——这意味着 v4 的 298 confirmed mutants 没有过 dual-blind,只过了机械 V1-V4(syntax / executable / non-trivial / signature)。**这是一个 hidden methodological asymmetry**:v3 通过 dual-blind 协议(§4.2.4),v4 没有。两者直接对比 δ 时,v4 的 mutant 池可能含更高比例的 syntactic-but-semantically-trivial 变异,**这有可能正是 v3b → v4 −0.007 几乎不动的另一种解释**(而非 LLM source diversity 真不贡献)。
- **FIX**(列在 W1 之外的独立点):在 §4.2.5(b) 加一段诚实声明:"v3 与 v4 的协议非完全对称——v3 含 dual-blind,v4 暂不含;v3b 与 v4 的 δ 比较因此可能受 mutant pool quality 而非 source diversity 主导"。或者 retro-fit:对 v4 cache 中 60-100 个随机 mutant 做事后 dual-blind 抽样,报告通过率。

**§5 (统计分析与结果)**

- §5.6.1 数据规模、§5.6.1.1 zero-mass dominance(W6 已涉及)。**§5.6.1.1 第 1039 行 "RQ2 的 effect-size inference 实质上由 n_aligned = 12(非 60)主导" 是稿件诚实信号最强的一句**——但应当从 §5.6.1.1 提到 §3.4 实验规模或 §5.3.2 power section,以避免 reviewer 漏看。
- §5.7.2 H2 verdict 处理诚实(见 S3)。但第 1142 行 "我们因此把 H2 定性为未达成大效应阈值,但中等效应稳定" 这种措辞接近 "softening the negative result",建议改为 "H2 rejected,observed effect falls in medium range and is consistent with LLM-mutant literature; this contextual coincidence does not weaken the rejection"——把 verdict 与 contextual observation 结构性分开。
- §5.7.3 power simulation 是 R-13 应,做得扎实(见 S4)。
- §5.8.3 mixed-effects Singular 的诚实声明、§5.8.4 Friedman 与 H4 的逻辑独立性表(1233 行)是稿件方法学诚信的强证据。
- §5.9 RQ4 inconclusive,见 W6 fix。

**§6 (讨论)**

- §6.1 是 W1 / W5 的核心争点。
- §6.2 R_sem / R_kill 解耦的工程启示与 §4.8.3 pilot 衔接清晰。
- §6.3 跨类一致性 H4 narrative 见 W2 fix。
- §6.5 stakeholder analysis 是 R-19 应(见 S5),做得扎实。

**§7 (Limitations)**

- §7.5 终稿 limitation 6 条 + §7.1.1-7.4.2 各 R 编号 risk 全列,结构清晰。
- 缺失:**Internal validity 的 §4.2.5(b) MVP 不对称(v3 dual-blind / v4 no dual-blind)未在 §7.1 列项**。建议加 "R11(NEW):跨源池协议非对称——v4 未做 dual-blind"。
- §7.1.7 R10 与 §4.2.5.1 differential prompt protocol 配套良好,但 R10 作为 limitation 的 weight 应升级到 R-1 / R-2 同档次(它直接关联 W1)。

**§8 (References)**

- §8.3 IST 2024 综述 [Authors TBD] **必须修复**(见 W4)。
- §8.5 Romano et al. 2006 引用为 "Annual Meeting of the Florida Association of Institutional Research" (FAIR 会议),非主流 venue。Cliff's δ thresholds 0.147 / 0.330 / 0.474 也常见于 Vargha & Delaney 2000(JEBS),建议添加该 cross-reference 以巩固阈值的引用合理性。
- 缺 Vargha & Delaney 2000 / Cliff 1993 的原始 δ 引用;缺 Hoeffding-style bound for K_eq false-equiv probability(§7.1.2 R2 提及但未引用)。
- 缺 Ammann & Offutt 2008 *Introduction to Software Testing*(§9.3 引理 9.2 的 "transformed-input oracle" 论证需要权威引用)。

**§9 (退化定理)**

- 见 W8 fix。

---

## 5. Originality Assessment

| 对照工作 | 本稿与之的差异 | 边际评估 |
|---|---|---|
| **Tip et al. (2024) LLMorpheus** | 单 LLM(Claude only)/ JS / fault-detection per-mutant focus | 本稿:三 LLM 跨源 + Python 科学计算 + MR-MP alignment ablation。**显著边际** |
| **IST 2024 LLM-mutant survey** | 系统综述,δ 区间 0.30-0.45 在多领域上报告 | 本稿数据落在该区间内但**首次因子分解 MR design vs LLM source**;边际**取决于 W1 是否能修复**。如 W1 不能修复,本稿 originality 退到 "首次在科学计算 Python 上系统报告 SMS",边际 modest |
| **Petrović & Ivanković (2018, 2021) Google** | 工业 50 万 mutant,productive mutant ~20%(developer survey) | 构念不同(主观 vs 自动 classifier),numerical coincidence 不构成 mechanism validation;**对齐论证有夸张风险**(W5)。边际 modest |
| **Hu et al. DeepCrime 2022** | 概率 mutation,真 fault | 本稿 B 类与之重叠(§3.1.1(c)),非独立扩展 |
| **Jia & Harman 2011 综述** | 经典语法 mutation | §9 退化定理给出严格化归;**显著理论边际** |

**EIC 综合评估**:本稿 originality 在 §9 退化定理(理论方向)与 §4.2.5 跨源 ablation(实证方向)上有两个潜在 selling points。前者稳固;后者依赖 W1 fix。**如 W1 不能修复**,本稿 originality 实质边际为 "Python 科学计算上 SMS 首次系统化 + §9 形式化兼容性",仍可发,但 contribution 应改述。

---

## 6. Significance Assessment(IST 读者群是否关心?)

**Yes, with caveats.** IST 主要读者群是 empirical SE / testing 研究者与工业测试工程师。本稿的 stakeholder 分析(§6.5)显式覆盖三类 stakeholder + GitHub Actions 模板,这是 IST-fit 的强信号。

**真正会让 IST 读者重视的内容**:

1. **Negative result on LLM source diversity contribution**(若 W1 fix 后仍稳)。这对 IST 读者是有用的 "saved budget" 信号:不要把研究投入花在堆叠更多 LLM 源上,该花在 MR 设计上。
2. **§3.2.6 算子级对照表**:测试工程师可以直接读出 "我手上的 mutmut + cosmic-ray 工具不能产生哪些类的 mutant",并据此评估自己的 test suite 在 OS/HP/TF/SI 类上的盲区。
3. **§9 退化定理**:研究者读出 "SMS 不是 yet-another mutation score variant,而是经典 MS 的真扩展"。
4. **§6.5 GitHub Actions 模板**:工程师可直接拿来部署 SMS-PR-gate。

**会让 IST 读者打折扣的内容**:

1. **RQ4 inconclusive**(W6):本稿原本承诺 "SMS vs Pattern Coverage 的 orthogonality",最终降级为 "未支持任何明确结论"——读者拿不到指导。
2. **W7 标量化 PUT limitation 未量化**:工程师无法判断 SMS 在自家 1-10 KLOC 工业代码上是否稳。
3. **75% zero-mass dominance**(§5.6.1.1):多数 cross-MP 单元格 SMS = 0,实战意义有限。

---

## 7. Methodology Assessment(高层评估;细节留 R1)

整体:**Above-average rigor,with one structural concern**。

- **统计方法**:Cliff's δ + bootstrap CI + Friedman + sign test + power simulation + LRCA 9-grid + H5 cutoff sweep,工具盒齐全。多重比较用 BH FDR(§5.3.1)正确。Mixed-effects Singular 的诚实退回(§5.8.3)罕见地坦诚。
- **Pre-registration / post-hoc 分离**:§3.5.1 caveats 与 §5.7.2 verdict 处理合规。但 W3 关于 "pre-registered" 措辞的强度需澄清。
- **Reproducibility**:有 `scripts/`、`data/`、commit-hash 引用、`paper_numbers_v4.json` SSOT 设计,这一点超出 IST 平均水平。
- **结构性顾虑**:W1(v3 / v3b / v4 ablation 的 selection 不对称)+ §4.2.5(b)(v3 dual-blind / v4 no dual-blind 不对称) 共同削弱了 headline contrast。这两点是 R1 (Methods Reviewer) 必然抓的命脉,**EIC 视角**是 "若不补 v4-pre 与 v4 dual-blind 抽样,headline 立不住"。

---

## 8. Decision Recommendation

**Major Revision (with strong potential to accept after revision)**

### Rationale

本稿在 IST scope 内有真贡献(§9 退化定理 + §4.2.5 跨源 ablation + §3.2.6 算子级对照 + §6.5 stakeholder analysis),写作诚实,robustness 检查齐全。但 EIC 视角下的三大结构性问题必须解决:

1. **W1**:headline ablation 的 selection asymmetry — 必须补 v4-pre (c→MP5 cross-source) 格点,或修改 title 与 §6.1 narrative。
2. **W4 + W5 + §8.3**:IST 2024 综述完整 citation + Petrović & Ivanković 的对齐论证克制 + Romano 2006 的 cross-reference 补全。
3. **W3**:pre-registration claim 的证据(注册 URL 或注册前协议文档 git commit time)。

如以上三点都能在 revision 中实质回应(不只是声明,而是数据/格点/citation 实质补全),本稿在 second-round review 中可走向 minor revision → accept。

### What would push to Reject

- 若 W1 的 v4-pre 格点跑出后 Δδ_LLM ≠ 0(具体 |Δ| > 0.05)且 95% CI 不覆盖零,则 headline finding 整体倒塌,需要重写 §1 / §6.1 / Title / Abstract,届时建议 reject 后重新投稿(资源消耗过大)。
- 若作者无法回应 W3 的 pre-registration 证据,**必须删除全文 "pre-registered" 措辞**;若仍坚持,reject。

### What would push to Minor Revision

- 仅 W4 / W5 / W8 类 citation + narrative 调整,W1-W3 实质合规,可直接降档至 minor revision。但当前稿件 W1-W3 还未到那一档。

---

## 9. Score Sheet(7-dimension,1-10 scale,verbal anchors)

> 由于工作目录 `references/quality_rubrics.md` 不存在(已 grep 验证),本表使用 IST 标准 EIC scoring(1=fatal / 4=below threshold / 5-6=marginal / 7-8=publishable / 9-10=exemplary)。

| 维度 | 分数 | 评语锚点 |
|---|---|---|
| **D1 Originality** | 6 / 10 | 双 selling point(§9 + §4.2.5)立得住但 W1 / W4 削弱实证 originality;若 W1 修复后可升到 7-8 |
| **D2 Significance(IST scope)** | 7 / 10 | Stakeholder analysis 与 §3.2.6 对照表对工程读者有真用;RQ4 inconclusive 拖累 |
| **D3 Methodological Rigor** | 7 / 10 | 工具盒齐全 + 诚实声明,但 v3/v3b/v4 selection 不对称 + dual-blind 不对称构成结构性问题 |
| **D4 Clarity & Writing** | 7 / 10 | §1-§7 narrative 连贯;符号系统(§2.1.2)严肃;偶有 IST 2024 [Authors TBD] 类粗陋之处需修 |
| **D5 Reproducibility** | 8 / 10 | SSOT(`paper_numbers_v4.json`)+ `scripts/` 完整 + commit-hash 引用,超出 IST 平均;只缺 W3 注册证据 |
| **D6 Soundness of Claims** | 6 / 10 | Title claim 的证据基础是 W1 核心争点;v3b 4/4 narrative 与 v3 primary 3/4 narrative 在 §6.3 有 dissonance |
| **D7 Practical Implications** | 7 / 10 | §6.5 三类 stakeholder + GitHub Actions 模板 + §3.2.6 工具不可达对照,工程读者可读到具体 actionable 内容;W7 标量化 limitation 拖累 |
| **Overall(weighted)** | **6.7 / 10** | **Major Revision** 档位;具有 7.5+ 改稿后潜力 |

---

## 10. Closing Note to Authors

本稿是一份**方法学诚信高于平均水平**的 negative-result 稿件。核心 verdict(H2 rejected)的诚实陈述是值得肯定的,但 negative result 的发表门槛恰恰要求 headline contrast 的实证基础**在最严格审查下立得住**。当前稿件的 v3 / v3b / v4 ablation 在 EIC 视角下存在 selection asymmetry 与 protocol asymmetry,这是必须修复的核心问题。如能补 v4-pre 格点 + v4 dual-blind 抽样 + 三件 citation 修复(W4 / W5 / W3),本稿在 IST 上有 publishable potential。

我的 final EIC verdict:**Major Revision**,timeline 建议 4-6 个月。

---

*Reviewer R0 (EIC) — 2026-05-01*
