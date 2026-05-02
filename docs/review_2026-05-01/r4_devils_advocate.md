# Reviewer #4 — Devil's Advocate Report

- **Reviewer role**: Skeptical methodologist (post-hoc detection, garden-of-forking-paths, headline-vs-evidence drift)
- **Manuscript**: P2 论文初稿 — *When LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Scientific Computing*
- **Independence statement**: 本报告独立完成,未参考其他 reviewer 报告。
- **Date**: 2026-05-01

---

## 1. Strongest Counter-Argument(核心反方论证)

**论文的标题命题与其证据基底之间存在结构性 misalignment;主标题"When LLM Source Diversity Doesn't Help"是一个 *strong negative claim*,但 §4.2.5 + §4.2.5.1 + §5.7.2 自己承认所测试的只是该命题的 *弱形式*(weak form)。**

具体地说:作者得到 v3b → v4 的 Δδ = −0.007 这一"几乎为零"的结果,据此构造主标题与 §6.1 "MR 设计是主导因子,源多样性贡献几乎为零(贡献比 ≈ 17.6:1)"的核心叙事(§4.2.5 末段、§6.1 第 2 段)。但 §4.2.5.1 / §7.1.7 R10 / §5.7.2 多处承认:此 v4 实验在三家 LLM 上**使用同一份 prompt 模板**,因此 −0.007 反映的是"prompt 风格固定下三家 LLM 对同一 prompt 的同源响应",而**不是**"LLM 源多样性的真实上限"。要测后者需要 differential prompt 协议(§4.2.5.1 已写好却未跑)。

这造成三处不可忽视的悖论:

1. **标题断言多于证据所支持**。"Doesn't help" 是一个针对"source diversity"概念的全称否定式,但实证只覆盖"identical-prompt source diversity",一个真子集。在 IST/JSS 这类期刊上,标题层的这种 over-claim 通常会被独立审稿人挑出。
2. **数字论证不对称**。Δδ_MR = +0.123(单类、3 PUT、post-hoc 选择 §3.5.1)与 Δδ_LLM = −0.007(三家 LLM、同 prompt、12 PUT)的"17.6:1 贡献比"在 §4.2.5 与 §6.1 都被引用,但这两个数字的统计基础完全不同(分子是事后选择的 selection-on-the-response,分母是 prompt-fixed 下的同源响应)。论文 §5.7.2 的 contrast 表已警告"避免合成 ratio 暗示因子 isolation",但 §4.2.5 与 §6.1 仍然给出了 17.6:1 这个合成数字,**正文与 caveat 自相矛盾**。
3. **headline 反向 fitting 数据的嫌疑**。论文叙事是先建立 H2 rejected,再用 v3 → v3b → v4 的三阶段对照"诊断"上限因子,把"source diversity 不重要,MR design 才是 bottleneck"作为收束。但 v3 → v3b 的 +0.123 完全是事后选择 c-class primary MP 的产物(§3.5.1 已诚实声明),如果剔除这次 selection-on-the-response,实际 confirmatory 证据是 v3(δ=0.323)与 v4(δ=0.439)的 +0.116,既不能区分 MR-design 贡献与 source-diversity 贡献,也无法支撑标题的强否定式。换言之:**支撑标题命题的"diagnostic chain"高度依赖一个 §3.5.1 自己声明 confound 的 post-hoc 步骤**;若严格按 pre-registered 分析,作者并没有得到"source diversity doesn't help"的证据,只得到"在 c-class primary MP shift 之后, source diversity (under fixed prompt) 不再继续推动 δ"。

最干脆的修复是把主标题降级为 *"Under Fixed Prompts: ..."* 或 *"A First Cross-Source Audit Suggests..."*,并在 §6.1 把 17.6:1 这个合成比从正文移除(只保留 §5.7.2 的分别报告)。否则"标题命题 vs 实证强度"的 mismatch 会成为 IST 的接收阻力。

---

## 2. Issue List(分级:CRITICAL / MAJOR / MINOR)

### CRITICAL-1 — 标题与正文承诺不一致(over-claim)

- **Dimension**: 1 (Core argument), 8 (So-what)
- **Location**: 主标题 + Abstract + §6.1 第 2 段 + §4.2.5 末段
- **What's wrong**: 标题 *"When LLM Source Diversity Doesn't Help"* 是 strong 否定式;§4.2.5.1 / §7.1.7 / §5.7.2 自己承认 v4 只测了 prompt-fixed 弱形式。论文同时声明"本文不主张……"(§1.2)与"source diversity 几乎不贡献"(§6.1),这两条相互矛盾。
- **Suggested fix**:
  (a) 改主标题为 *"When Same-Prompt LLM Source Diversity Doesn't Help: ..."* 或 *"A First Cross-Source Audit ..."*;(b) 在 Abstract 把 "−0.007" 同时报告 "under identical prompt template" 措辞(目前 Abstract 已有 "under identical prompt" 措辞但标题未一致);(c) §6.1 删除 "17.6:1 贡献比" 单点合成,改用 §5.7.2 的分别报告表。

### CRITICAL-2 — §3.5.1 c-class primary MP shift 是 selection-on-the-response,且其 +0.123 跃升被反复用作核心叙事支柱

- **Dimension**: 2 (Cherry-picking), 3 (Confirmation bias)
- **Location**: §3.5.1, §5.7.2, §5.8.2, §6.1, §6.3
- **What's wrong**: 作者已诚实声明此为 exploratory(§3.5.1 caveats #1-#4 + §5.8.2 + §5.7.2 的 contrast 表),这非常好;但 §6.1 与 §4.2.5 仍把 +0.123 作为 "MR-MP 对齐设计是 H2 上限主导因子" 的主要论据,§5.8.2 同样把 v3b 4/4 严格达成作为 H4 verdict 的依据。**caveat 与 headline 论证使用不一致**:caveat 说"应作为 exploratory finding",headline 章节(§6.1, §6.3)却把它当 confirmatory 用。
- **Suggested fix**: §6.1 与 §6.3 的 verdict 必须以 v3 pre-registered 数字为准:H4 sign test = 3/4(部分通过),Δδ_MR 不可估计(因 v3b 是事后选择)。把 v3b 的 4/4 与 +0.123 移到 sensitivity / robustness 段,不进 verdict。或者补 leave-one-class-out 重选(预注册规则)在新数据上重测。

### CRITICAL-3 — §3.5.1 c-class primary MP 选择规则未做 multiple-comparison 校正

- **Dimension**: 2 (Cherry-picking), 6 (Alternative paths)
- **Location**: §3.5.1 caveat #2
- **What's wrong**: argmax over 5 candidate MPs 是典型的 max-statistic,在 H0(各 MP 同分布)下也会以 ≈ 1 − (1−α)^5 的虚报率产生显著效应。论文 caveat #2 承认未做 Bonferroni/max-statistic 校正,但既然没做,§5.7.2 / §5.8.2 / §6.1 / §6.3 报告的 v3b 数字应附 inflated-α warning,而不是把 v3b 当作 robustness check 的合法替代版本。
- **Suggested fix**: 在 v3b 引用处统一加注 "n=3 PUTs in c-class, max over 5 MPs without multiplicity correction; treat δ_v3b inflation upper bound at α_eff ≈ 0.23"。或者改 v3b 选择规则为 "use the MP that maximizes mean SMS averaged over 4-class baseline excluding c"——这至少是 leave-one-out 的近似。

### CRITICAL-4 — §6.1 "17.6:1 贡献比" 与 §5.7.2 "two contrasts reported separately" 自相矛盾

- **Dimension**: 1 (Core argument), 3 (Confirmation bias)
- **Location**: §4.2.5 末段 "贡献比 ≈ 17.6:1" + §6.1 第 2 段 + §5.7.2 表注 "reported separately rather than as a single ratio"
- **What's wrong**: §5.7.2 的 contrast 表注明"两个 contrast 分别报告而非合成 ratio",理由是分子是事后选择、分母是 prompt-fixed。但 §4.2.5 与 §6.1 都直接给出 17.6:1 的合成数字。论文自己规定不要做的事情,自己又做了。
- **Suggested fix**: 删除 §4.2.5 与 §6.1 中的 "17.6:1" 合成数字;两处都用 §5.7.2 的 contrast 表行文。

### MAJOR-1 — 标题中 "for Scientific Computing" 与 12-PUT × ~80–400 LOC × 标量签名的实证规模严重不匹配

- **Dimension**: 5 (Overgeneralization)
- **Location**: 主标题 + §3.1.1(d) "Limitation: program(x: float) → float 签名简化" + §7.2.1 R5
- **What's wrong**: 论文 §3.1.1(d) 自己承认"`program(x: float) → float` 签名简化是实质性约束,可能系统性低估工业 PUT 上的 SMS";§3.1.1(b) 只覆盖 *Numerical Recipes* 12 章中的 8 章。这就是说,实证基底是"小规模、单标量输入输出、Python 实现"的子集,**为科学计算软件全域代言**。即使 §7.2.1 R5 已声明 limitation,标题与 Abstract 并未对应缩小。
- **Suggested fix**: 标题加 "in Small-Scale Python Scientific Computing PUTs" 或 "A Pilot Audit"。Abstract 在 "Method" 段加 "12 single-input single-output Python functions, 50–400 LOC"。

### MAJOR-2 — H2 verdict 论证的"effect-size ceiling"叙事 vs §5.7.3 power 0.423 的"measurement-noise floor"替代解释

- **Dimension**: 6 (Alternative paths)
- **Location**: §5.7.3 §6.1
- **What's wrong**: §5.7.3 报告 H2 (large-effect 0.474) 在 (12, 48) 下的 power 仅 0.423,然后说"power 不足并不能反过来说功效是 H2 未达成的成因——观测 δ = 0.439 < 0.474,效应规模本身就低于阈值"。这一推断**逻辑上不严密**:在 power = 0.42 的样本规模下,即使真 effect 恰为 0.474,样本观测有 ~58% 概率落在 0.474 以下;论文不能仅凭"观测点估计 0.439 < 0.474"反推"effect-size 上限是 MR-design 主导,不是 sampling"。CI [0.127, 0.740](v4)上限 0.740 完全跨越 large-effect 阈值,本身就是"sampling 噪声不能排除真 δ ≥ 0.474" 的直接证据。
- **Suggested fix**: §5.7.3 第 3 点修改为 "在 power 0.42 下, δ 真值 ≥ 0.474 的可能性仍然存在(CI 上限 0.740);'effect-size 上限是 MR design 主导'是工程假设,不是 power 分析的结论"。§6.1 删除 "大效应阈值 0.474 在 LLM-mutant + 当前 MR 设计下可能是该领域的固有上限" 这一论断,改为 "在本数据上未达成,但 CI 与 power 不能排除"。

### MAJOR-3 — §9 退化定理 L1-L6 条件之间的相互依赖未论证

- **Dimension**: 4 (Logic chain)
- **Location**: §9.2 L1-L6 + §9.3 引理证明
- **What's wrong**: §9.3 引理 9.2 的"L4 下 R(y, y') ≡ y = y'"假设依赖于 L3(AVP 容差归零),否则 MP_eq 在 ε_AVP > 0 时仍是带容差等式;同样,引理 9.3 的"mut^syntax"集合在 L5 下定义为 Mothra-style 算子,但 L5 自身蕴含了 L6(命令式确定性程序)——AOR/ROR 在概率程序上的语义并不"自动退化"。**L1-L6 之间存在隐含蕴含关系,论文将它们并列陈述为 6 个独立条件,定理结构上松散。**特别是:
  - L4 (MP=equality) 与 L5 (syntactic operator) 的交互:Mothra 文献中"语法等价"是带容差的(实际工具 mutmut 用 byte-equiv),与 L1 (ε_eq → 0) 的严格等价并不同;
  - L4 + L5 共同蕴含 "MR_{i,k} 集合 = {input identity, output equality}" 这一极简形态,但 §9.4 主定理证明并未显式取此交。
- **Suggested fix**: §9.2 改写为 "L1 ⇒ L2"、"L4 ⇒ L3" 等依赖图;§9.4 证明显式说明哪些 L_j 是 minimum 必要、哪些是冗余。或者补一个 Remark 说明 "L 是充分但非最小条件集"。

### MAJOR-4 — H5 "未达成"被作为 LRCA 校准研究方向的"实证起点",但 §5.6.2.1 已显示是数据内属性

- **Dimension**: 3 (Confirmation bias), 6 (Alternative paths)
- **Location**: §5.6.2 + §5.6.2.1 + §6.2
- **What's wrong**: §5.6.2.1 cutoff sensitivity 显示 H5 pass-ratio 在 cutoff [0.05, 0.40] 完全平坦在 20%,"任何 cutoff 都不能把 H5 推到 80% 以上"是数据 bimodal 的内在属性。然而 §6.2 仍说"LRCA 阈值校准(OOD 边界 0.05、tolerance 倍数 10×)可能也过于敏感",暗示 LRCA 阈值还有调整空间。**这与 §5.6.2.1 的 evidence 不一致**:既然在 cutoff 全谱不变,LRCA 阈值的进一步校准不会救起 H5。
- **Suggested fix**: §6.2 修改为 "H5 未达成是 v4 数据的 bimodal 分布属性,不能通过 LRCA cutoff 调整改善;真实的改善路径是扩大 mutant 池或重设 root-cause 边界(P4)"。

### MAJOR-5 — §1.5 H3 撤回的时间点不透明,可能是 outcome-driven retraction

- **Dimension**: 2 (Cherry-picking)
- **Location**: §1.5 H3 撤回声明 "本文于 v3 数据采集后正式撤回 H3"
- **What's wrong**: H3 在"v3 数据采集后"撤回——这是在已经看到 60 单元格 equiv 触发 < 10 cells 之后。诚实声明已写明,但 IST 审稿可能质疑:**为什么不预注册一个 "H3 形式检验需要 ≥ N cells 触发, 否则降级为 descriptive observation" 的判停规则?** 现状是"看了数据,发现不能形式判定,撤回"——formally indistinguishable from outcome-driven retraction。
- **Suggested fix**: §1.5 加一句 "撤回决策记录在 git log commit hash <X>,时间戳早于 v3b/v4 数据采集",或在 §3.5.1 配套加 "H3 撤回的判停规则 = equiv-触发 cells < 10",使决策规则形式化。

### MAJOR-6 — §8.3 IST 综述 [Authors TBD] 引用是 placeholder,但被反复用作 "Cliff's δ 0.30-0.45 区间" 的 anchor

- **Dimension**: 文献整合
- **Location**: §8.3 "(IST review) [Authors TBD] (2024)" + §1.3.2 + §5.7.2 + §6.1
- **What's wrong**: 该文献被作者作为 "LLM-mutant 文献 Cliff's δ 0.30-0.45 区间" 的核心 anchor 在 §1.3.2、§5.7.2、§6.1 三处引用,但作者列名留空。Reviewer 无法独立验证该综述确实报告了这一区间。**这是论证链上的关键引文,在投稿前必须实名化**。
- **Suggested fix**: 投稿前完成 author 字段(以 DOI/URL 检索 ScienceDirect 元数据);若该文献无法在 IST 录用前实名化,**应整段移除"0.30-0.45 区间"对照,改用 Tip et al. (2024) LLMorpheus 单点对照**。

### MINOR-1 — §6.5 Stakeholder 分析缺 LLM provider 维度

- **Dimension**: 7 (Stakeholder blind spots)
- **Location**: §6.5(测试工程师 / MR 设计者 / 审计机构)+ §7.1.1 R1 残余风险
- **What's wrong**: §6.5.1-6.5.3 列了三类 stakeholder,§6.5.4 跨 stakeholder 接口。但 LLM provider(Anthropic / OpenAI / DeepSeek)作为 v4 cross-source pool 的构成方,如果模型版本演进(GPT-5.4 → 5.5、Claude Opus 4.6 → 4.7、DeepSeek chat → v4-pro),复现包能否长期维持 v4 数字稳定?§7.1.1 R1 仅说"LLM 训练数据可能在投稿期之后更新",未承诺具体可行的 reproducibility commitment(例如 raw response cache 是否绑定 git LFS、是否承诺 5 年内的 frozen mirror、是否有 fallback 协议指定 "若 GPT-5.4 deprecated,以 raw_response cache 为准")。
- **Suggested fix**: §6.5 加一节 6.5.5 "LLM provider as upstream stakeholder",承诺(a) raw_response cache 完整公开、(b) 复现脚本带 "offline mode" 直接读 cache 跳过 API、(c) §7.1.1 R1 残余风险显式量化(例如 "模型版本变更预期 5 年内对 SMS 主表的影响估计 < 10%")。

### MINOR-2 — Abstract 末句 "indicating that ... does not reach the Romano large-effect threshold without further redesign" 暗含因果声明

- **Dimension**: 1 (Core argument)
- **Location**: Abstract 倒数第 2 句
- **What's wrong**: "without further redesign" 暗示"redesign 之后能越过阈值"是一个未经 demonstration 的 causal claim;实际论文 §6.1 只是把 P4 作为研究方向("跨源不行,要重设 MR")。
- **Suggested fix**: 改为 "...does not reach the Romano large-effect threshold under the LLM-mutant + current-MR-design configuration tested here"(去掉 "without further redesign")。

### MINOR-3 — §3.2.6.2 "cosmic-ray on a1 PUT 实证补充"标记为 future-work hook,但 §3.2.6 / §6.1 已基于"工具不可达"做 categorical 论证

- **Dimension**: 8 (So-what)
- **Location**: §3.2.6 + §3.2.6.1 + §3.2.6.2
- **What's wrong**: §3.2.6.1 算子级对照表很扎实,但 §3.2.6.2 留 "可选实证" 给未来——既然 §3.2.6.1 categorical 论证已是充分证据,§3.2.6.2 的 "可选" 标签会让审稿人质疑 "是否担心实跑 cosmic-ray 反驳论证?"。建议至少跑 1 PUT(a1)证实 categorical 论证。
- **Suggested fix**: 在 R2 revision 跑 cosmic-ray on a1,把 4 元组数字 (mutants_generated, killed, survived, incompetent) 报到 §3.2.6.1。或彻底删除 §3.2.6.2,坦承 "categorical 论证 sufficient,实跑非必要"。

### MINOR-4 — §1.5 H3 撤回后保留 H1/H2/H4/H5 编号(空缺 H3)是行政便利,可能掩盖原 5 假设系统的 holistic coherence

- **Dimension**: 2 (Cherry-picking 边缘)
- **Location**: §1.5 末段
- **What's wrong**: "为保持与 §3 / §5 / §6 / §7 的引用一致性, 后续章节继续使用 H1, H2, H4, H5 编号(空缺 H3),不做全文重编号" 是技术合理的,但读者会问:H1+H2+H3 原本是 RQ2(MR-MP 对齐)的三角支撑(implementability + aligned-effect + equiv-pattern),撤掉 H3 后实质上 RQ2 只剩 H2 一个支撑点。论文未明确声明这一逻辑收缩。
- **Suggested fix**: §1.5 加一句 "撤回 H3 后,RQ2 的形式化检验缩小到 H2 单点;equiv-pattern 维度改在 §6.2 作描述性观察,不作正式判定"。

### MINOR-5 — §3.4 mutant 数声明 "60 单元格共 ~292 mutant 实例化(在 12 PUT × 5 MP 矩阵中重复使用同一 PUT 池)" 可能被误读为 "每 cell 独立 mutant 池"

- **Dimension**: 报告精确度
- **Location**: §3.4 第 2 行
- **What's wrong**: 同一 PUT 的 mutant 池在 5 个 MP 上复用,因此 60 单元格有效独立 mutant 数实质 = 12 PUT × 24.3 mutants ≈ 292,而不是 60 × 24.3。论文已说 "重复使用同一 PUT 池",但 Abstract / §1 的 "60 cells, average 24.3 LLM-generated mutants per cell" 措辞会让 quick reader 误以为 1458 mutants。
- **Suggested fix**: Abstract 改为 "60 cells (12 PUT pools of average 24.3 mutants reused across 5 MPs)";§3.4 补一行明确 "实质独立 mutant 数 ~292,非 ~1458"。

### MINOR-6 — §4.2.5(c) DeepSeek 模型选择论证薄弱

- **Dimension**: 6 (Alternative paths)
- **Location**: §4.2.5(c)
- **What's wrong**: 选 deepseek-chat 而非 v4-pro 的理由是 "成本/速度优先,质量等价(实测 dry-run 三家 LLM 在 a2_OS1 算子上输出语义相同的 sum-of-diagonal 替换)"。**单点 dry-run 一致不构成等价证据**;应至少 5-10 算子 dry-run 后再下"质量等价"结论。
- **Suggested fix**: §4.2.5(c) 改为 "在 a2_OS1 单算子 dry-run 上输出一致;v4-pro 在 P4 论文重测以验证 reasoning model 是否带来额外贡献",明确这是工程取舍而非已验证等价。

---

## 3. Ignored Alternative Explanations / Paths(被忽略的替代解释)

### 3.1 H2 未达成的 measurement-noise floor 假设(R-13 只半解决)

§5.7.3 power 分析做了样本规模功效,但**未做 measurement noise floor 估计**:

- 60 cells × 12 mutants × N=20 = 14400 AVP 调用,每个 cell 的 SMS 估计精度由 mutant pool 大小主导(每 mutant 贡献 ≈ 1/24 = 0.042),12 个 aligned cells 的 SMS 标准差至少为 0.042/√12 ≈ 0.012 量级——但 v4 aligned mean 仅 0.275,信噪比约 23。
- **更严重的是 cross 切片**:48 cells 中 88% 为 0 SMS(§5.6.1.1),这意味着 cross 切片的"mass" 几乎全堆在零点,Cliff's δ 在 zero-mass dominance 下退化为 *"#{aligned > 0}"* 这一极简统计。论文 §5.6.1.1 已注意到"effect-size inference 实质上由 n_aligned = 12 主导",但**未把这一观察反过来用作 H2 verdict 的替代解释**:δ ceiling 可能根本不是 MR-design 决定,而是 *"MR-MP 对齐性 + LLM-mutant + N=20 AVP 重复" 这套测量协议的方法学上限*。

替代假设:**如果换成 N=200 AVP 重复 + per-cell 独立 mutant 池(不复用),δ 上限可能突破 0.474**。论文未做此分析,直接归因到 "MR design bottleneck",是 confirmation bias 的可能体现。

### 3.2 v3 → v4 的 +0.116 没有被作为 confirmatory contrast 报告

如果剔除事后选择的 v3b 中间步骤,**v3 (pre-registered) → v4 (cross-source) 是一个完整的 confirmatory contrast**:Δδ = 0.439 − 0.323 = +0.116。这个数字结合了 c-class primary MP shift 与 cross-source pool 两个改动,**自身 CI 可计算且 confirmatory**。论文采取的"v3 → v3b → v4 三阶段分解"叙事是为了把两个改动 isolate,但代价是引入 §3.5.1 的 selection-on-the-response confound。**不分解的 v3 → v4 联合 contrast 反而是更诚实的报告**——只是它无法支撑标题"source diversity doesn't help" 的强否定式。

### 3.3 LLM-mutant + 标量签名的协同上限

§3.1.1(d) 的 program(x: float) → float 签名简化与 LLM-mutant 协议有可能存在协同偏置:LLM 在标量函数上更擅长生成"小幅扰动"型 mutant(常数微扰、方法替换),而非"高维状态破坏"型 mutant(mesh corruption、state-vector flip)。后者在工业 PUT 上才是主导 fault 形态。**δ ceiling 可能反映 "LLM × 标量签名" 的协同盲区,而非 MR-design 不足**。论文未隔离这两层 alternative。

---

## 4. Missing Stakeholder Perspectives(被忽视的利益相关者视角)

### 4.1 LLM provider(已在 MINOR-1 提)

GPT/Claude/DeepSeek 模型版本演进对论文 reproducibility 的影响,§7.1.1 R1 只用一句 "可能不可用"打发,§6.5 完全未列。一个 5-10 年的 reproducibility 计划应当至少声明:(a) raw_response cache 在 git LFS 或 OSF 上的 frozen mirror;(b) "如 v4-cross-source 的 GPT-5.4 deprecated,以本文 cache 为准" 的 fallback;(c) v4 数字与新模型的 forward-validation 计划。

### 4.2 mutant 池审核者(meta-reviewer)

§4.2.5(b) MVP 简化"不调用 reviewer LLM",直接以 V1-V4 自动验证收尾。这把 §4.2.4 双盲复核协议从 v3 协议中悄悄拿掉了——v3 还说"双 LLM 异源 + 20% 人工抽样",v4 没有对应步骤。论文没有声明 v4 是否做了 §4.2.4(d) 的"20% 人工抽样",也没说 V1-V4 自动验证能否替代双盲。**LRCA C1_share 0.164 → 0.209 的提升究竟来自 cross-source 还是来自验证协议的简化变更?未隔离**。

### 4.3 期刊数据共享委员会

IST 与 STVR 都有 artifact evaluation track。论文 REPRODUCIBILITY.md 在 §6.5.3 被引用,但全文未列具体 artifact license / DOI / 数据规模上限(例如 raw_response cache 的总字节数、是否超 OSF 50 GB 上限)。

### 4.4 P4 论文 reviewer

论文多次把"扩展到强 source diversity"、"differential prompt"、"扩大 PUT 规模" 推到 P4。但 P4 的 reviewer 无法验证 P2 的 v4 数据 claim 与 P4 的扩展是否方法学一致(version drift 风险)。建议 P2 至少声明 v4 → P4 的兼容性矩阵。

---

## 5. Observations(Non-Defects,审议后排除)

以下是初读时疑虑、深读后确认作者已合理处理或证据不支持作为 defect 的项目:

### O-1 — §5.7.3 的 power 0.423 报告本身

R-13 power 分析是诚实且方法学正确的。**质疑点不在 power 分析的存在**,而在 §5.7.3 第 3 点的解读(已记 MAJOR-2)。R-13 的工作量 + 报告结构(三档 power + sample size sweep)在同行评审标准上充分。

### O-2 — §1.5 H3 撤回的存在本身

撤回事先有 H3 假设、之后做 explicit 撤回声明 + 维持 H1/H2/H4/H5 编号——这是 *publishing-research-honestly* 的良好实践,不是 cherry-picking。**质疑点在撤回时间点的形式化**(MAJOR-5),不在撤回行为本身。

### O-3 — §3.5.1 caveats #1-#4 的诚实声明

§3.5.1 的四条 caveat 写得非常坦白(明确声明 "selection-on-the-response"、"未做 multiple-comparison correction"、"应作为 exploratory finding"、"v3 是 primary"),这是教科书级的事后调整声明范式。**问题不在 caveat 的存在**,而在 §6.1 / §6.3 的 verdict 没有遵守 caveat(已记 CRITICAL-2)。

### O-4 — §9 退化定理的存在

定理 9.1 是论文的正向贡献,经典 MS 是 SMS 的特殊解这一陈述形式上正确。**质疑点是 L1-L6 的相互依赖未论证**(MAJOR-3),不是定理本身错误。

### O-5 — §6.4 RQ4 conservative 解读

把 Spearman ρ = 0.107 / Kendall τ = 0.073 在 n=12 下定性为 "未检出 correlation,orthogonality 是 hypothesis 不是 finding" 是恰当的方法学保守。**值得肯定**,不构成缺陷。

### O-6 — §7.5 Limitations 6 条声明

§7.5 的 6 条 (equiv 概率近似 / LLM 同源偏置 / H4 功效 / LRCA 似然根因 / AVP 复用 / 工程价值代理) 覆盖了主要 internal threat。

### O-7 — §5.6.2.1 H5 cutoff sensitivity

R-14 应答非常充分:dense grid + 显示 H5 verdict cutoff-invariant,这是良好的 robustness check。**问题在 §6.2 的 LRCA 阈值 narrative 没跟上 §5.6.2.1 的 evidence**(MAJOR-4),不在 §5.6.2.1 本身。

### O-8 — §1.6.2 认识论声明 "SMS 不是工程价值代理量"

把 SMS 限定为认识论意义上的语义检测度量、把工程价值留给 P2-CN,这是对 construct threat (§7.3.1) 的恰当回应。

---

## 6. 总评(Overall Assessment)

**总体定性**:论文方法学诚实度在 LLM-mutant + scientific computing 这个交叉领域里**显著高于平均水平**。§1.5 H3 撤回、§3.5.1 c-class shift 的四条 caveat、§5.6.2.1 cutoff sensitivity、§5.7.3 power、§5.8.3 mixed-effects Singular 声明这些段落都是教科书级的诚实报告。

**主要风险**:正文叙事(尤其 §4.2.5 末段、§6.1、Abstract 结尾、主标题)与 caveat 段的 verdict 一致性不足。三处 CRITICAL 问题都是同一根源——**作者已经做了正确的方法学声明,但 headline 没跟着往下收缩**。

**建议处理**:Major Revision。修复 CRITICAL-1 / 2 / 4(核心叙事与 caveat 对齐)与 CRITICAL-3(v3b multiple-comparison 警告)是接收的必要条件;MAJOR-1 / 2 / 3 / 4 是质量提升;MINOR 项可在 typesetting / R2 revision 处理。

**接收概率**:在 IST,标题不缩小的话有 ~30% reject 风险(标题层 over-claim 通常致命);标题与叙事对齐后,~60-70% accept(IST 对 negative-result paper 接受度尚可,加上 §3.2.6 / §9 / Phase A cross-source 三个明确的 methodological 贡献)。

**最 actionable 的单条建议**:
> 把主标题改为 *"When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Small-Scale Python Scientific Computing PUTs"*;同步删除 §6.1 与 §4.2.5 的 "17.6:1 贡献比" 合成数字;v3b 在 verdict 段统一附 "single-class post-hoc, n=3 PUT, no multiplicity correction" 警告。

— Reviewer #4 (Devil's Advocate)
