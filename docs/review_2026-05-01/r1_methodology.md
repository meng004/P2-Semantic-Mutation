# Reviewer 1 — Methodology Review Report

**Manuscript**: *When LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Scientific Computing* (P2 初稿,1642 行,中英混排)
**Target venue**: *Information and Software Technology* (IST)
**Review date**: 2026-05-01
**Reviewer file**: `论文初稿P2.md`
**Reviewer focus (per Configuration Card #2)**: 推断统计与变异测试方法学;pre-registration 与 selection-on-response;Cliff's δ + bootstrap CI 报告标准;mixed-effects 退化与 Friedman 替代;H2 阈值不被 p-hacking 的稽核

---

## 0. Reviewer 身份

- 经验类型:经验型软件工程方法学(empirical SE methodology),10 年从事 mutation/MT 研究的推断统计审稿
- 最相关贡献:ICSE/FSE 论文「bootstrap-CI reporting standards in mutation testing」联合作者
- 熟练领域:Cliff's δ 渐近性质 + 95% bootstrap percentile CI;Romano 2006 阈值的 SE 校准争议;Friedman / Iman-Davenport / Wilcoxon-signed-rank 替代;mixed-effects 在小 N 下的 Singular / Boundary degeneracy;Benjamini-Hochberg vs Bonferroni 在小族系上的功效折衷
- 利益声明:与作者无合作关系;仅基于稿件做盲审

---

## 1. Summary(独立判断)

本文提出 SMS 度量(经典 Mutation Score 的语义内涵扩展)与 LRCA 工程归因层,以 12 PUT × 5 MP × 5 mut_j = 60 单元格的实证矩阵审计 MR 在科学计算软件上的揭错能力,并以三阶段 ablation(v3 / v3b / v4)隔离「MR-MP 对齐设计」与「LLM 源多样性」对 H2 large-effect 阈值的相对贡献。SMS-MS 退化定理(§9)做得整洁。在统计报告的**透明度**上,作者已经远远高于 IST 同期投稿的中位水平——pre-registered v3 与 exploratory v3b/v4 区分清晰,Cliff's δ 与 95% bootstrap CI 显式给出,H2 rejected 的 verdict 没有被 v3b/v4 的微升所掩盖,mixed-effects Singular 与 fallback boundary degeneracy 也都做了诚实声明。

但是,本文的方法学呈现仍有若干**结构性问题**未被充分处理,集中在四点:

1. **selection-on-response 的影响半径未在每个下游 δ-contrast 中被一致追踪**:v3b 的事后选择影响不仅作用于 H2 δ 与 H4 sign test,还作用于 v4 的整个 ablation 解读(因为 v4 沿用了 v3b 的 c→MP1 主轴),但 §6.1「MR-MP 对齐设计是主导因子」一句把这一污染半径压缩了——更准确的表述应当是「在 v3b 的 c-class 选择条件下,跨源对 δ 几乎无贡献」。
2. **§5.7.3 power analysis 是 parametric bootstrap from observed empirical pool,在「检测 δ ≥ 0.474」这一目标问题上是循环的**:从已观测到 δ ≈ 0.439 的样本中重抽样,得到的功效曲线是「在 truth = 0.439 附近能否检出 0.474」的近似,而不是「若 truth = 0.474 能否检出」的标准 power。这两个量的解读不同。
3. **Cliff's δ = 0.439, 95% CI [0.127, 0.740] 跨越 H2 阈值 0.474**:CI 的上半段进入 large-effect 区,这意味着「effect 严格 < 0.474」并未被数据排除。verdict 「H2 rejected」是基于点估计 vs 阈值,而非 CI 与阈值的关系——本文在 §5.7.2 末尾用 power 分析回应这一点,逻辑上仅在 truth < 0.474 的零假设下成立,稿件需要把这一推断结构讲清楚。
4. **Friedman 的角色被静默升格为 primary**:§5.8.3 Mixed-effects 因 Singular 不可用,§5.8.4 Friedman χ² = 15.30, p = 0.0041 成为 RQ3 唯一形式化的 p 值。作者已声明「Friedman ≠ H4」的 caveat,但摘要、§5.8、§6.3 都把它当作主结果叙述,这在 dual-reporting / sensitivity-promoted-to-primary 的方法学边界上是临界违规。

我倾向于 **Major Revision**(详细见 §11 决定建议)。论文的统计透明度好,问题不在「藏」,而在「叙述层未把已知 caveat 一致地穿到下游每一句结论里」。这是可修订的。

---

## 2. Strengths(方法学层面)

**S1. Pre-registered v3 与 exploratory v3b/v4 的分离做得清晰。** §3.5.1 显式列出 4 条 caveats,§5.7.2 在 verdict 中保留「v3 primary δ = 0.323」作为决定性数字,而非用 v3b/v4 替换。这是 mutation testing 文献中少见的诚实做法(Petrović & Ivanković 2018 没做 pre-registration;Tip et al. 2024 LLMorpheus 没做 ablation)。

**S2. Bootstrap CI 报告完整。** §5.7.2 给出 v4 δ = 0.439, 95% percentile CI [0.127, 0.740],B = 10000 重复(R-12 应),并且把 v3 / v3b / v4 三档同时摆出。这符合本人合著 ICSE bootstrap-reporting 标准的 minimum acceptable disclosure。CI 不是 quote-out 而是与 verdict 共置。

**S3. Cliff's δ rank-invariance 的处理正确(§6.1 末尾)。** 作者明确指出 logit 变换下 δ_logit ≡ δ_raw 是构造结果而非经验发现,这一处避免了一类常见的「sensitivity analysis 假象」(部分 ML 论文会拿恒等结果当 robustness 证据)。Romano 2006 引用得当,小/中/大效应阈值表(0.147 / 0.330 / 0.474)在 §5.2 做了 declarative pre-commit。

**S4. Mixed-effects Singular 的诚实声明(§5.8.3)。** 作者没有把 Singular 后退化为 OLS 的 fallback p 值当作 primary,而是显式说「不把 fallback 的 p 值作为正式假设检验报告」,并改以四件式(类别均值 + sign test + Friedman + forest plot)展示。这是教科书级处理。

**S5. LRCA 阈值校准(§4.6.4 + §5.6.2.1 H5 cutoff sensitivity)。** 9-grid (ood_band × tolerance_multiplier) + dense cutoff sweep 给出「H5 不是 0.20 的 lucky pick,而是数据 bimodal 的内在结果」的论证——这种「确认结论不是 cutoff 选择 artifact」的做法比同类论文罕见。

**S6. v3 → v3b → v4 三阶段 ablation 的因子分解逻辑(§4.2.5)。** Δδ_MR = +0.123 vs Δδ_LLM = −0.007 的对比清晰,作者主动把「合成 ratio」拒绝(§Abstract:「reported separately rather than as a single ratio because the numerator reflects a confounded data-driven adjustment...」)。这是高质量的方法学反思。

**S7. SMS-MS 退化定理(§9)的形式化层级清楚。** 引理 9.1-9.3 + 主定理 9.1 + 推论 9.1 把「向下兼容」从修辞上升为形式陈述,且 6 条退化条件 (L1-L6) 都是 falsifiable 的。这一节是 P2 区别于 LLMorpheus / DeepCrime 等先前 LLM-mutant 工作的关键科学贡献。

---

## 3. Weaknesses(WHAT / WHERE / FIX)

### W1. parametric bootstrap from empirical pool 不是检测 δ ≥ 0.474 的正确 power operationalization

**WHAT**: §5.7.3 的 power 分析从 observed v4 SMS pool 有放回采样,计算「simulated δ 超过阈值的频率」。这本质上是 plug-in estimator 在样本分布下的检验通过率,**只能近似「若真实分布等于经验分布(δ ≈ 0.439)时,样本统计量超阈值的频率」**——这正是为什么表中「δ > 0.474 在 (12, 48) 下的功效 = 0.423」会落到 ~50%(因为点估计 0.439 离阈值 0.474 仅 0.035,bootstrap noise 让 ~42% 的重抽样越线)。

**问题**:这不是「若真实 δ = 0.474,我有多大把握检出大效应」的标准功效,而是「在已观测分布下,样本越线频率」。两者**在 truth = 0.474 时相等,在 truth ≠ 0.474 时偏离**。作者其实在 §5.7.3 第 3 条 caveat 中部分意识到了这一点(「即使真实 δ 在 0.474 附近,样本量也只有约 42% 概率检出。但这并不能反过来说『功效不足是 H2 未达成的成因』」),但叙述没有说清「这条曲线是 plug-in 而非 alternative-stipulated」。

**WHERE**: §5.7.3 整节,特别是「方法」段「从观测的 aligned (n=12) 与 cross (n=48) v4 SMS 池中**有放回采样**」一句,以及「关键解读」第 3 条。

**FIX**:
1. 把 §5.7.3 重新框架为 **two-condition power analysis**:
   - **(A) Observed-distribution plug-in**(当前做法,保留):告诉读者「在我们看到的数据下,如果重抽样 K 次,会有多少次 δ_observed 超阈值」。这刻画 sampling variability,不是 power。
   - **(B) Stipulated-alternative non-parametric simulation**(新增):构造两个 score 分布 F_aligned, F_cross 使得 truth_δ(F_aligned, F_cross) = 0.474 严格成立(可以用 shift-and-rescale on observed cross 拟合),然后在 (12, 48) 下抽样,计算 P(observed_δ > 0.474)。**这才是 R-13 实质要求的「样本量是否足以检出 large effect」**。
2. 用 (A) + (B) 双轨报告,把当前表的标题从「功效」改成「在已观测分布下越阈频率(plug-in approximation)」,把新表标为「Stipulated-alternative power at δ_truth = 0.474」。
3. 后者大概率会显示功效 ~ 0.55-0.70(δ 在 0.474 处的渐近分布在 (12, 48) 下变异较大),这反而**强化** H2 rejected 的说服力——「即使真有大效应,我们也大概率检出,但我们没检出,因此真效应大概率 < 0.474」。这是 R-13 想看到的逻辑。
4. 把这段加入 §5.7.3 后约 200 字,引用 Cliff (1996) Ordinal Methods 第 5 章的 δ 抽样分布讨论或 Mukherjee & Wong (2020) 的 simulation-based power for non-parametric statistics。

### W2. Cliff's δ CI 与 H2 阈值的重叠未被 verdict 直面

**WHAT**: §5.7.2 给出 v4 δ = 0.439, 95% CI **[0.127, 0.740]**。CI 上限 0.740 远高于 0.474,即「真效应 ≥ 0.474」并未被数据排除。然而 verdict 「H2 rejected」是基于「点估计 < 0.474」而非「CI 上限 < 0.474」。作为 reviewer,我不反对作者的最终 verdict,但**呈现方式让读者无法看到 CI 与阈值的张力**。

**问题位置**:这是**呈现层而非分析层**的问题。在 H2 严格意义下「δ ≥ 0.474」是单侧主张,CI 上限 0.740 在单侧 95% 区间下也仍跨过 0.474,即「真 δ < 0.474」与「真 δ ≥ 0.474」在 95% 置信下都不能被排除。把 verdict 写成「rejected」而不补充「但 CI 与阈值重叠,数据对 truth 在阈值上下方都未做出显著区分」会让读者误以为是断然的拒绝。

**WHERE**: §5.7.2 verdict 段,以及 §1 Abstract 的「**The pre-registered H2 large-effect threshold ... is rejected**」(粗体)。

**FIX**:
1. 把 verdict 改为「**H2's point-estimate condition is not met (δ_v3 = 0.323, δ_v4 = 0.439, both below 0.474); however, the 95% bootstrap CI of v4 [0.127, 0.740] does not exclude truth ≥ 0.474, so the rejection is in the operational pre-registered sense (compare point to threshold) rather than in the strict frequentist sense (CI exclusion of threshold)**」。
2. 给一个 equivalence-test 风格的辅助检验:Two One-Sided Tests (TOST) for δ < 0.474,看 CI 上限是否 < 0.474。当前 v4 CI 上限 0.740 显然不满足,所以 TOST 也不能等价宣告「δ 显著 < 0.474」。把这条结果加进 §5.7.2 作为 «non-inferiority style» 补充。
3. Abstract 把「is rejected」改为「is not met under the pre-registered point-estimate criterion」,避免「rejected」在 hypothesis-testing 行业语境下被误读为「significantly less than」。
4. 这一修改不会改变本文 H2 不达成的主张,但把方法学读者可能问的问题(「点估计 vs CI vs threshold,哪种 verdict?」)显式回答了。

### W3. selection-on-response 的污染半径在 v4 解读中被压缩

**WHAT**: v3 → v3b 是 c-class primary MP 数据驱动 shift(§3.5.1 caveats 1-4 已声明)。但 v4 是在 **v3b 已选择 MP1 之后** 的跨源池——即 v4 的 c→MP1 不是独立选择,而是承接 v3b 的事后选择。这意味着 v3b → v4 的 Δδ = −0.007 不是「在中性条件下衡量 LLM 源多样性」,而是「在 c→MP1 已被选过的条件分布下衡量」。

**WHERE**: §6.1 「v3 → v3b 的飞跃来自 c 类 primary MP 数据驱动调整,即 MR-MP 对齐设计本身;v3b → v4 的跨源扩展几乎不改变 δ,即 mutant 池的源多样性」 这一段;以及 §4.2.5 「**MR-MP 对齐设计是 H2 上限的主导因子**」一句。

**问题**:更精确的表述应当是:
- 「**Conditional on v3b's data-driven c→MP1 selection**, switching from same-source to cross-source pool changes δ by −0.007 (CI overlaps zero).」
- 「The 17.6:1 contribution ratio is computed against the v3 baseline that includes a confounded data-driven step in the numerator and a near-null cross-source step in the denominator on top of the same confound; **the ratio is not a clean factor decomposition**.」

**FIX**:
1. §6.1 增补「The v3b → v4 contrast is conditional on the v3b c-class primary selection; it does not isolate LLM-source contribution from MR design contribution in a fully orthogonal sense, because the cross-source pool is built on top of the v3b primary axis.」
2. §4.2.5 「贡献比 ≈ 17.6:1」一句加 caveat:「This 17.6:1 ratio is between the *exploratory + confounded* numerator and the *prompt-fixed* denominator; it should not be read as a clean decomposition of MR-design vs LLM-source.」
3. **更彻底的方法学修订(可选,留 R2)**:报告一个 v4' = cross-source pool **with c→MP5** 的对照(即在 P1 默认 primary 下做跨源)。这才是「LLM 源多样性」的纯净测试。当前 v4 把两个事后选择糅在一起。
4. 在 §3.5.1 把 caveat 4 升级为「Pre-registered 主结论(v3)是 H2 verdict 的唯一基础;v3b 与 v4 的所有 δ-contrast 都受 v3b 选择 confound 影响,不应作为 H2 的稳健性证据。」

### W4. Friedman 从 sensitivity 升格为 primary 的边界

**WHAT**: §5.8.3 mixed-effects Singular,作者退到 Friedman χ² = 15.30, p = 0.0041 (df=4, n=12 PUT × 5 MP)。§5.8.4 caveat 写得清楚:「Friedman 主效应 ≠ H4 cross-class consistency」「Friedman 的方法学贡献是为 RQ3 提供形式化非参 p 值,不是直接验证 H4」。但**实际叙述中**:
- Abstract:「Friedman test confirms a significant MP main effect (χ² = 15.30, p = 0.0041)」——这句没说「这不是 H4」。
- §6.3 末尾:「跨类一致性的『一致』已在 (a) 4/4 类均值方向均为正、(b) 4/4 类 sign test 通过(v3b)、(c) 60-cell Friedman p = 0.0041 三点上联合呈现」——把 Friedman 列为「跨类一致性」的支持证据,但 Friedman 测的是 MP 间差异,**与跨类一致性逻辑独立**。

**WHERE**: Abstract 第 9 句;§5.8.4 解读段;§6.3 末尾联合呈现。

**问题**:这是「sensitivity analysis upgraded to primary」的临界违规。Mixed-effects 是预计划的 RQ3 主分析,Singular 后改用 Friedman 是 fallback,Friedman 测的是 MP 主效应而非 H4——但作者在叙述中把 Friedman 的显著 p 当作「RQ3 / H4 综合证据的一员」,读者会误以为 Friedman 是 H4 的形式化检验。

**FIX**:
1. Abstract 改为:「Friedman test (PUT × MP design, n=12 × 5) **identifies a significant MP main effect** (χ² = 15.30, p = 0.0041), **which is logically distinct from H4 cross-class consistency (the latter resting on a 4/4 sign test, exploratory under v3b)**」。
2. §6.3 把「(c) 60-cell Friedman p = 0.0041」从「跨类一致性」三件式中**移除**,或加 inline caveat:「(c) An auxiliary Friedman test on PUT × MP confirms MP main effect exists (p = 0.0041), but this measures MP-rank dispersion across all PUTs, not cross-class consistency in the H4 sense.」
3. §5.8.3 加一段:「**Statement on Friedman as primary**: Because Mixed-effects degenerates and Friedman occupies the only formal non-parametric position in RQ3, we explicitly disclose that Friedman has been promoted from sensitivity to primary for this RQ. The pre-registration document (`pre-registration_v3.md`) listed Mixed-effects as primary; this is a deviation. Readers should treat the χ² = 15.30 result as the strongest formal evidence for *MP main effect*, but **not** as H4 evidence.」
4. 在 §5.3.2 列出 fallback hierarchy:Mixed-effects 主 → Friedman fallback → sign test (H4-specific) → forest plot 描述。让读者看到决策树,而非读到 verdict 时去拼凑。

### W5. v4 c-class primary MP 选择的 multiple-comparison 校正缺失

**WHAT**: §3.5.1 caveat 2「未做 multiple-comparison 校正」承认了这一点,但只用一句话掠过(「严格的 max-statistic 零分布或 Bonferroni × 5 校正未应用」)。在事后选择 5 个候选 MP 中 mean SMS 最大者作为 primary 后,**该选择本身的 selection bias 未被 size-corrected**。结果:Δδ_MR = +0.123 中含有由 max 选择带来的 upward bias。

**WHERE**: §3.5.1 caveat 2;§5.7.2 「v3 → v3b 的 +0.123」 解读;§6.1 「贡献比 ≈ 17.6:1」。

**问题**:这是 selection-on-response 的具体形态。在 5 个 MP 上取 argmax(mean SMS),即使 truth 是 5 个 MP 等同分布(零假设),max 的期望也大于均值——具体地说,5 个独立 N(μ, σ²) 的 max 期望比 μ 高 ~1.16σ(Order statistics)。Δδ_MR 的 +0.123 中,**有多少来自真实 MR-MP 对齐效应,有多少来自 max 选择 inflation**,在不做 max-stat 零分布或 step-down (Westfall-Young) 校正前无法分离。

**FIX**:
1. §3.5.1 增补一个段落:「**Magnitude of max-selection inflation**: under H_0 of equal MP means within c-class, a permutation null on c1/c2/c3 × 5 MPs gives an expected max-mean inflation of ~Δ_inflation ∈ [0.0X, 0.1X] (compute on observed permutations of MP labels within (c-class × PUT) blocks). The observed mean-MP1 = 0.233 is X percentile of the permutation null. This sets a lower bound on how much of Δδ_MR = +0.123 is *not* attributable to selection.」
2. 跑一个 1000-permutation null:在每个 c-class PUT 内打乱 5 个 MP 的标签,重新计算 argmax MP 的 mean SMS,得到 null distribution。报告 percentile rank of observed 0.233。如果 percentile < 5%,可以说「max selection inflation 解释不掉观察值」;如果 > 50%,需要承认 v3b 主要是 selection artifact。
3. **如果 (2) 不可跑**(数据已锁),把 caveat 2 从「未应用」升级为「以 Bonferroni × 5 上界折算 effective α」:δ_v3b = 0.446 在 unadjusted 95% CI [0.154, 0.743]; 把 CI 按 Bonferroni 5-test 调整为 99% CI ≈ [0.05, 0.85](粗略),让读者看到 selection 的 cost。
4. 在 §6.1 「17.6:1」 旁边写:「This ratio's numerator includes max-selection inflation that is not corrected for; under permutation null the inflation is ~Δ_inflation, so the *adjusted* numerator is +0.123 − Δ_inflation = X.」

### W6. equivalent-mutant 判定的 false-equiv / false-non-equiv 偏差未给定量

**WHAT**: §7.1.2 R2 声明「K_eq=1000 是工程近似,存在 false-equiv 与 false-non-equiv 双向偏差」「§5 附录提供 K_eq ∈ {500, 1000, 2000} 三组灵敏度分析」「§7 Limitations 引用 Hoeffding-style 上界估计 false-equiv 概率」。但**正文 §5 未见 K_eq sensitivity 表**(我搜了 §5 子节,没找到),而 Hoeffding 上界的具体数字也未给出。

**WHERE**: §7.1.2 R2 promise vs §5 actual reporting.

**问题**:H2 verdict 依赖 SMS = killed/(mut − equiv)。equiv 集合的 false-non-equiv(把真等价 mutant 误标为非等价进入分母)会下推 SMS;false-equiv(把真非等价 mutant 误标为等价剔除)会上推 SMS。两个偏差对 H2 阈值跨越的影响**方向相反**,但量级未知。如果 K_eq = 500 vs 2000 的 SMS 差异 < 0.01,可以放心忽略;如果 > 0.05,会改变 H2 verdict。

**FIX**:
1. **必须**在 §5 或附录加一个表:K_eq ∈ {500, 1000, 2000} 下的 60-cell mean SMS、aligned-mean、cross-mean、Cliff's δ。
2. 给 Hoeffding 上界的具体数字:对一个真等价 mutant,K_eq = 1000 误判为非等价的概率上界是多少(取决于 ε_eq 与输出空间分布)。这个数字一段就够。
3. 如果 sensitivity 跑不出来,**把 R2 的 promise 撤回到 limitation**:在 §7.5 写「we did not run K_eq sensitivity; this is a residual threat that may shift δ by ±X bound」,并保留 H2 verdict 的 caveat。

### W7. zero-mass dominance 的统计后果未传递到 §5.7.2

**WHAT**: §5.6.1.1 给了一段非常好的分析——「Cliff's δ 的 effect-size inference 实质上由 n_aligned = 12(非 60)主导」「median odds ratio 因 median(cross) = 0 不可定义」。但 §5.7.2 仍然写「n_aligned=12, n_cross=48」做 H2 verdict,没有把「实质 n = 12」的信号引到 H2 sample-size 解读。

**WHERE**: §5.7.2 verdict 段「在 pre-registered 主分析(v3,c→MP5,n_aligned=12,n_cross=48)下」。

**问题**:这不是计算错误(Cliff's δ 数学上仍 well-defined,bootstrap 也合规),但**effective sample size 显著小于 60**,这影响:
- §5.7.3 power 解读:n_effective ≈ 12-15 而非 60,功效进一步下降
- bootstrap CI 的 coverage:在 cross 切片 88% 零的情况下,resample 时 cross 几乎总是 0,bootstrap 的 percentile coverage 对 lower CI bound 偏紧

**FIX**:
1. §5.7.2 verdict 段加一句:「**Effective sample size**: due to zero-mass dominance in cross slice (median(cross) = 0, 88% zeros, §5.6.1.1), the rank-based δ statistic's variance is dominated by n_aligned = 12; bootstrap CI coverage on the lower bound may be slightly liberal (i.e., true coverage < nominal 95%).」
2. 跑一个 BCa(bias-corrected and accelerated)bootstrap 替代 percentile bootstrap,看 CI 是否变化。BCa 在偏态分布上更可靠;如果 BCa CI 与 percentile CI 差距 < 0.02 可放心,否则重新报告。
3. 如果不愿改 CI 类型,加 caveat 说明 percentile bootstrap 在 zero-mass 偏态下的已知 liberal 倾向(参 Efron & Tibshirani 1993, §14.3)。

### W8. v3b sign test 4/4 的「严格达成」表述与 selection 关系不一致

**WHAT**: §5.8.2 写「H4(4/4 类 aligned 均值 > cross 均值):**严格达成**(v3b 4/4)」。但 v3b 的 c 类 aligned 均值变正完全是因为 c→MP1 的事后选择(MP5 下 c 类 aligned mean = 0,与 cross mean 0 平局,sign test 是 3/4 平 1)。把 4/4 用「**严格**」修饰,与 §3.5.1 caveat 3 「应作为 exploratory finding 而非 confirmatory result 解读」直接冲突。

**WHERE**: §5.8.2 verdict 段「严格达成」。

**FIX**:
1. 把「严格达成」改为「**v3b exploratory: 4/4 (post-hoc, conditional on c→MP1 selection); v3 pre-registered primary: 3/4 (partial)**」。删去「严格」二字。
2. §6.3 「跨类一致性的『一致』已在 (a) 4/4 类均值方向均为正、(b) **4/4 类 sign test 通过(v3b)**、(c) 60-cell Friedman p = 0.0041 三点上联合呈现」——把 (b) 改为「3/4 (v3 pre-registered) / 4/4 (v3b post-hoc)」并去除「联合呈现」的合成感。
3. 这是一个 verbal 修订,影响主要在 verdict 表述的一致性,不改变数据。但如果不改,methodology reviewer 会逐句对照 §3.5.1 caveat 与 §5.8.2 verdict,发现不一致。

### W9. SMS_unfiltered 附录与 LRCA 的「不进 SMS 公式」声明的张力

**WHAT**: §5.4.2 定义 SMS_unfiltered = SMS without LRCA filtering(killed 不区分 C1/C2-C5),并承诺「附录提供 SMS_unfiltered 与 SMS 的逐单元格差异表;若两者相对差异 < 5%,确认 LRCA 不影响主结论的鲁棒性」。但 §2.6.4 与 §4.6.3 都强调「**LRCA 不修改 SMS 公式,killed 集合不剔除 suspect**」——意思是 SMS 与 SMS_unfiltered 应该数学上**完全相等**(都用 |killed|/(|mut|−|equiv|)),只是 C1_share / suspect_share 是辅助标注。

**WHERE**: §2.6.4 + §4.6.3 vs §5.4.2.

**问题**:如果 LRCA 真的不进 SMS 公式,那 SMS_unfiltered ≡ SMS,差异表恒为 0,鲁棒性检查无内容。如果 §5.4.2 的「逐单元格差异」非零,说明 SMS 实际上**有一个版本剔除了 suspect**。这种内部表述的不一致让读者无法判断到底哪个 SMS 是 primary。

**FIX**:
1. 澄清:§2 锁定的 SMS 是「unfiltered」版本(killed 集合包含 C1-C5 全部),C1-only filtered 版本是辅助度量(可命名 SMS_C1)。
2. 把 §5.4.2 改为「附录提供 SMS_C1 = |killed ∩ {root_cause = C1}| / (|mut| − |equiv|) 与 SMS 主版本的逐单元格差异表;若两者相对差异 < 5%,确认 LRCA 标注不会逆转主 verdict」。
3. 这一处不影响数据,但影响读者对「SMS 到底是什么」的理解。是个 100-word 的修订。

### W10. APA-7 / triplet reporting 的几处遗漏

**WHAT**:
- §5.7.2 v3b δ = 0.446, CI [0.154, 0.743] —— 缺 effective sample size
- §5.8.4 Friedman per-class:Class b χ² = 10.78, p = 0.029 —— 缺 effect size(Kendall's W),且 0.029 在 Bonferroni × 4 之后 = 0.116(不显著),作者未做校正
- §5.9 RQ4 Spearman ρ = 0.107, p = 0.741 —— 给了 p,但未给 95% CI(用 Fisher z 变换可得)
- §5.7.2 H2 verdict 缺一个三元组 (effect size + CI + sample size + p-value-or-equivalent) 在同一行的 declarative summary

**WHERE**: §5.7.2, §5.8.4, §5.9.2.

**FIX**:
1. §5.7.2 增加 declarative summary line:「**v3 primary**: δ = 0.323, 95% CI [0.017, 0.622], n_aligned = 12, n_cross = 48, B = 10000 bootstrap; H2 threshold 0.474 not crossed by point estimate, CI does not exclude truth ≥ 0.474.」
2. §5.8.4 per-class Friedman:加 Kendall's W = χ²/(n*(k-1)) 作为 effect size;补 Bonferroni × 4 校正后的 adjusted p。如果 b 类 0.029 在 Bonferroni 后 = 0.116,verdict 「仅 b 类显著」要弱化。
3. §5.9.2 加 95% CI for ρ:Fisher z 变换 + n=12 给出 ρ ∈ [−0.49, +0.62](粗算),把它写出来,与 §5.9.3 的「Spearman ρ 的 95% CI 大约覆盖 [−0.5, +0.6]」对齐。这一处 §5.9.3 已经口头说了但没在 §5.9.2 数字行上落地。

---

## 4. 详细方法学批注(分节)

### §1.4-1.5 RQ / 假设系统

- **OK**:H1-H5(撤 H3)的阈值表达式做了 declarative,事前 commit。Romano 0.474 来自 §5.2 引用 Romano (2006),不在事后修改——这是符合 pre-registration 标准的行为。
- **小问题**:H2 是合取条件「δ ≥ 0.474 AND median odds ratio ≥ 3.0」。median odds ratio 在 median(cross)=0 时不可定义,作者改用「aligned median > cross median」作为辅助方向证据(§5.7.2)。这个 fallback 不在事前 specification 里,严格意义上 H2 的 second leg 是 unevaluable;应该在 §5.2 加一句「If median(cross)=0, median odds ratio is undefined; in that case, condition 2 is replaced by 'aligned median > cross median' as a declarative auxiliary, but this is a *mid-study replacement* and not a pre-registered rule.」
- **H4 阈值**:CV(ΔSMS) < 0.5 在 4 个类均值上是个粗糙度量,小 N 下 CV 高度敏感于一个类的 outlier。建议改为 IQR/median 或直接报告 4 类原始数字 + bootstrap range。

### §3 设计

- §3.1.1 选址论证写得专业(Numerical Recipes 12 章覆盖 8 章,工业代码 limitation 显式声明 §7.2.1 R5)。
- §3.5.1 c 类 primary MP shift 的 caveats 极佳(4 条 explicit)。但 caveat 4「Pre-registered 主结论(v3):H4 sign test 3/4(部分达成),δ = 0.323(H2 rejected)。这是本文的 primary analysis verdict;v3b/v4 仅作 sensitivity 报告」**说得对,但稿件下游(§5.8.2 「严格达成」、§6.3 联合呈现、Abstract 「two exploratory follow-ups produce δ = 0.446 and 0.439」)没有完全按这个原则执行**。详见 W3, W4, W8。

### §4.6-4.8 LRCA + AVP

- §4.6.4 9-grid 校准是亮点(W5/Strength 之外的好实践)。
- §4.6.3 LRCA 输出 C1_share 与 suspect_share——但「不进 SMS 公式」与 §5.4.2 SMS_unfiltered 差异表有张力(W9)。
- §4.8.3 R_sem / R_kill 解耦在 HP 类算子上的 pilot 发现是论文最有意思的经验观察,叙述清晰。但 pilot 是 K=10/20 small N,§4.8.4 「这给出 H2 的预提示证据」的预提示性表述合适——不要在 §5 主分析中倒回去用 pilot 反向校准 verdict(目前没做,保持不做)。

### §5 统计(主要靶子)

- §5.6.2 LRCA 数字 16.7% / 20.0%,远低于 H5 80% 阈值——verdict「未达成」明确。
- §5.6.2.1 H5 cutoff sensitivity 是范例性的稳健性检查(W5/Strength S5)。
- §5.7.2 H2 verdict —— 见 W2, W7, W8。
- §5.7.3 power analysis —— 见 W1。
- §5.8.3 mixed-effects Singular —— 见 W4。
- §5.8.4 Friedman χ² —— 见 W4。
- §5.9.2-3 RQ4 Spearman ρ + power caveat —— 已在 §5.9.3 把「orthogonality 是 hypothesis 而非 finding」做了 conservative 改写,这是好事;但 §5.9.2 数字行缺 ρ 的 95% CI(W10)。

### §7 Limitations

- §7.1.6 R9 mutant pool 规模 + §7.1.7 R10 LLM 非确定性 —— 都写了。
- §7.2.2 R6 跨类一致性功效弱 —— mixed-effects Singular 已记入此节。
- 但**整章 §7 没有一个 weakness 专门讲「v3 → v3b 的 selection-on-response 是 the threat」**(只在 §3.5.1 caveats 处理,§7 没有同等显式声明)。建议增加 §7.1.8 「R11 selection-on-response in c-class primary MP shift」,把 W3 + W5 的内容专章化。

### §9 退化定理

- 形式化 OK(Strength S7)。
- 一个小数学注:引理 9.2 证明中「当 r ≠ id 时,L4 限定的 MP_eq 仍要求 S_i(x) = s'(r(x))」—— 严格说,如果 r 是恒等之外的输入变换,经典 MS 框架下没有「r」存在,killed 是「∃x: S_i(x) ≠ s'(x)」。L4 把所有 MR 退化为「输出严格等同」,但当 r 不是 id 时,这个等式是 S_i(x) = s'(r(x)) 还是 S_i(r(x)) = s'(r(x))?后者才是「mutant 在 r(x) 这个新输入上的差异检出」,前者引入了一个原程序的「参考输出」概念。建议把引理 9.2 的「当 r ≠ id 时」段落改写,显式说「在 L4 + r=id 下,killed 退化为经典差异检出;r ≠ id 的情况在退化极限 L 下不出现(因为 L4 把 MR 限制为 R(y, y') ≡ y = y',MR 不再带有 input transformation)」——这样消除歧义。

---

## 5. 统计报告标准检查(APA-7 / triplet)

| 检查项 | 状态 | 备注 |
|---|---|---|
| Effect size + 95% CI + sample size + p-value 同行 | △ 部分 | §5.7.2 v4 完整;v3 / v3b 有 CI 没有 inline n;Friedman per-class 没有 effect size(应加 Kendall's W) |
| Bootstrap n(本文 B = 10000)显式声明 | ✓ | §5.7.2 R-12 应处明确 |
| Multiple-comparison 校正 | △ | §5.3.1 声明 BH-FDR α=0.05;但 §5.8.4 Friedman per-class 4 个 p 值未做 Bonferroni × 4(b 类 0.029 → adjusted 0.116);§3.5.1 caveat 2 c-class max selection 未做 max-stat 校正 |
| 单边 vs 双边 | ✓ | 大多数地方未明确,但 H2 是单侧主张(δ ≥ 0.474),bootstrap percentile CI 是 two-sided 95%——若改用单侧 95%,CI 上限会变(下限不变);建议 §5.7.2 明确「two-sided percentile CI used for δ; H2 itself is one-sided (δ ≥ 0.474)」 |
| Pre-registered vs exploratory 标注 | ✓ | §3.5.1, §5.7.2 做得清晰,但下游叙述有压缩(W3, W8) |
| Verdict 与 effect size + CI 关系 | △ | 见 W2 |
| 报告 effect size 与样本量,而非仅 p | ✓ | Cliff's δ + Friedman χ² 都给了 effect size |
| Cliff's δ 阈值来源声明 | ✓ | §5.2 引用 Romano 2006,不在事后修改 |
| Ranking-based stats 在 zero-mass 下的 caveats | △ | §5.6.1.1 给了讨论,但未传导到 §5.7.2 verdict 段(W7) |

**综合**:报告标准 7/10——上半部好(透明 + 引用 + pre-registration),下半部弱(校正一致性 + verdict-CI 关系 + zero-mass 后果传导)。修订后可达 8.5/10。

---

## 6. 可重现性评估

### 6.1 SSOT 与 env-var 复合需求

§6.5.2 CI YAML 给出了 `SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b` 的复合环境变量。这是 SSOT(single source of truth)+ pre-reg/exploratory 区分的合理工程实现。**问题**:稿件没有给出 REPRODUCIBILITY.md 的内容大纲——建议:

1. 必须有 `REPRODUCIBILITY.md` 显式列举:
   - SMS_VERSION ∈ {v3, v3b, v4} 各自对应的 input data, primary MP, mutant pool source,以及如何切换
   - P2_PRIMARY_VERSION ∈ {v3, v3b} 决定 c-class primary MP 选择(MP5 vs MP1)
   - **复合需求**:跑 v3 primary verdict 必须 SMS_VERSION=v3 ∧ P2_PRIMARY_VERSION=v3,否则结果是 exploratory 版本——这是个 trap,默认值应当是 v3 / v3 (pre-registered),不是 v4 / v3b
   - 跑 sensitivity 时显式声明 SMS_VERSION=v4 ∧ P2_PRIMARY_VERSION=v3b
2. 给一个 `reproduce_v3_primary.sh` 与 `reproduce_v4_exploratory.sh` 双脚本,避免 reviewer / 后续读者用错版本组合得到不同 verdict。
3. 在 `paper_numbers_v3.json` / `paper_numbers_v4.json` 各自的 schema 中明确 contract:每个数字标注「pre-registered」或「exploratory」。

### 6.2 env-var traps

- 稿件 §6.5.2 暴露的 `SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b` 是一个 **two-knob coupling**:两者都会影响 H2 verdict,但耦合关系未文档化。如果用户仅设 SMS_VERSION=v4 而忘了 P2_PRIMARY_VERSION,会得到「v4 数据 + v3 primary」的混合版本——这个组合**未在论文中报告**,会产生 unreported δ 值。
- **缓解**:在 `scripts/sms_campaign.py` 入口检查两个变量是否成对;不一致时报 fatal error,而不是默认其中之一。

### 6.3 LLM 复现性

- §7.1.7 R10 三件套(multi-turn de-dup + K=10/20 + raw response storage in `data/operator_campaign/raw/`)合理。`raw/` 提供完整 prompt + raw response 让后续读者**绕过 LLM 非确定性**直接复用本文 mutant 集合——这是 LLMorpheus 范式中没做到的。
- 但 §4.2.4(g)「LLM-G 使用关闭检索增强生成 (RAG) / 关闭 web 搜索的 API 路径」——bltcy.ai 代理是否真能保证 close-RAG?如果代理在后端开了 web context,prompt leakage 可能仍存在。建议 §7 加 caveat 明示「we cannot fully verify RAG-off on the proxy infrastructure; this is residual」。

### 6.4 Reproducibility 评估总结

- **代码 / 数据**:据 §7 R9 R10 描述,`data/operator_campaign/cache/`(212 个 confirmed mutant) + `scripts/build_pools.py` + `data/results/paper_numbers_v4.json` 都已就绪。我没看到完整 README 内容,假设它存在并合理。
- **评分**:7.5/10。扣分项:(a) two-knob coupling 未显式 trap,(b) RAG-off 未 verify,(c) K_eq sensitivity 表未在 §5 实跑(W6),(d) BH-FDR 与 Bonferroni 在 cross-table 上的一致应用文档化不足。

---

## 7. 决定建议

**Major Revision**(rating: 4 of 5 — between accept-with-major-revision and reject-resubmit;但本文方法学透明度足以承载 Major Revision 框架,而非 reject)。

### 7.1 强制必改(reject-if-not-fixed)

- **W1**:§5.7.3 power analysis 重新框架为 (A) plug-in + (B) stipulated-alternative 双轨。
- **W3**:§6.1 v4 解读改为 conditional-on-v3b;17.6:1 ratio 加 caveat;考虑加 v4'(c→MP5 cross-source)对照。
- **W4**:Friedman 角色显式声明为 Mixed-effects 的 fallback,Abstract / §6.3 修订把 Friedman 从「H4 联合证据」中剥离。
- **W5**:c-class primary MP shift 的 max-selection inflation 给定量(permutation null 或 Bonferroni × 5 上界),不能只用一句话掠过。
- **W8**:§5.8.2 「严格达成」改为「v3b post-hoc 4/4, v3 pre-registered 3/4」;§6.3 联合呈现表述同步修订。

### 7.2 强烈建议(should fix)

- **W2**:Abstract 与 §5.7.2 的「rejected」改为「not met under pre-registered point-estimate criterion」;给 TOST-style 辅助。
- **W6**:K_eq sensitivity 表必须在 §5 或附录实跑,或撤回 §7.1.2 的 promise 转为 limitation。
- **W7**:effective sample size 与 BCa bootstrap CI 的传导。
- **W10**:per-class Friedman 加 Bonferroni × 4;Spearman ρ 加 95% CI inline。

### 7.3 可选(nice to have)

- **W9**:SMS_unfiltered 与 SMS_C1 命名清理。
- §9.2 引理 9.2 中「r ≠ id」段的形式化清理。
- §7 加 R11 「selection-on-response」专章。

### 7.4 H2 verdict 是否被 p-hacked across §5.7.2 / §6.1 / §6.3?

**答**:**没有 p-hack 阈值(0.474 始终来自 Romano 2006,事前固定),但有 selection-on-response 影响 v3b/v4 的 δ**。verdict「H2 rejected」自身不被 p-hack 威胁——v3 0.323 < 0.474 是清晰的。问题在于 v3b/v4 的「sensitivity」叙述把 δ 推到 0.439-0.446,接近阈值,作者用文字声明保留 v3 verdict,但语调上(尤其 Abstract 与 §6.1)读起来像是「δ 离阈值很近,只差一点点,P4 就能跨过」——这种表述虽然不是 p-hack,但是 narrative-hack on the threshold proximity。

**真正稳健的 verdict**:「Pre-registered v3 primary δ = 0.323, well below Romano large-effect threshold 0.474. Two exploratory ablations (v3b, v4) push δ to ~0.44 but neither crosses 0.474, **and v3b → v4 is conditional on v3b's c-class selection so does not provide a clean isolation of LLM-source contribution**. We therefore conclude H2 is not met; whether H2 could be met under a pre-registered c-class selection rule and a per-LLM differential prompt is left to future work, with no strong claim that the threshold is „close to crossing".」

如果作者按 W3 + W4 + W8 修订后,H2 verdict 的 narrative 风险就被消除。

---

## 8. Score sheet(7 维度,1-10)

| 维度 | 分数 | 简评 |
|---|---|---|
| **方法学严谨性** (Methodological rigor) | 6.5 | 退化定理 + bootstrap + pre-registration 框架做得好;扣分在 W1 power operationalization 循环、W4 Friedman 升格、W5 max-selection 未 corrected |
| **统计推断正确性** (Statistical inference correctness) | 6.0 | δ 与 χ² 计算正确;但 W2 CI-vs-threshold 关系、W7 zero-mass 传导、W10 校正一致性都需修订 |
| **报告标准 (APA-7 / triplet)** | 7.0 | 透明度好,大多数 effect size + CI + n 配齐;Friedman per-class 缺 W,Bonferroni × 4 未应用 |
| **Pre-registration 与事后选择处理** | 7.5 | §3.5.1 caveats 写得专业;但下游叙述(Abstract、§5.8.2「严格」、§6.3 联合呈现)未一致执行 caveats |
| **可重现性** | 7.5 | SSOT JSON + raw response store 好;扣分在 two-knob env-var coupling 未 trap,REPRODUCIBILITY.md 内容未 audit,K_eq sensitivity 缺 |
| **威胁论证完备性** | 7.0 | §7 涵盖大多数;缺 R11 selection-on-response 专章,缺 K_eq sensitivity 实证 |
| **方法学贡献的可信度** (相对 LLMorpheus / DeepCrime / Petrović) | 7.5 | SMS-MS 退化定理 + 三阶段 ablation 是真贡献;但「17.6:1 因子分解」叙述需要按 W3 弱化为「conditional ratio」 |

**总分(几何均值)**: 7.0 / 10。分布:6.0 (统计推断) / 7.5 (退化定理 + reproducibility)——属于「方法学概念好,执行细节有重要漏洞但可修订」的 IST 范式 paper。

---

## 9. Recommended decision letter line

> Major Revision. The paper's pre-registration discipline and SMS-MS degeneration theorem are strong methodological contributions, and the dual-reporting of v3 pre-registered vs v3b/v4 exploratory analyses is admirably transparent. However, the manuscript falls short on three methodological fronts that should be fixed before acceptance: (1) the §5.7.3 power analysis is a plug-in bootstrap from the empirical pool rather than a stipulated-alternative simulation, conflating sampling variability with power against H2's threshold; (2) the v3b → v4 contrast is conditional on v3b's data-driven c-class primary MP selection, so the headline „17.6:1 MR-design vs LLM-source contribution ratio" is not a clean factor decomposition; (3) Friedman χ² has been promoted from sensitivity to primary inference for RQ3 due to mixed-effects singularity, but the manuscript's Abstract and §6.3 still narrate Friedman as part of the H4 cross-class consistency evidence — these are logically distinct. We recommend the authors (a) re-frame §5.7.3 as a two-condition power analysis (observed-distribution plug-in plus stipulated δ = 0.474 alternative); (b) report a v4' = cross-source × c→MP5 contrast as the clean LLM-source-only ablation, or explicitly mark the current v4 as conditional; (c) declare Friedman as the de facto primary for the MP main effect (with a caveat that it is the fallback for the singular mixed-effects model) and remove it from the H4 evidence list; (d) quantify the c-class max-selection inflation under a 1000-permutation null. With these revisions the manuscript should meet IST methodology standards.

---

*End of Reviewer 1 Report*
