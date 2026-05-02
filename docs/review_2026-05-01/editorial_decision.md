# Editorial Decision Package — P2 Manuscript

**Manuscript**: *When LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Scientific Computing*
**Authors marker**: P2 主导作者 (本项目主作者)
**Target Venue**: *Information and Software Technology* (IST)
**Editorial date**: 2026-05-01
**Synthesis basis**: 5 independent reviewer reports (R0 EIC + R1 Methodology + R2 Domain + R3 Practical/Cross-disc + R4 Devil's Advocate),共 ~1491 行

---

## 1. Editorial Decision Letter

### Final Decision: **MAJOR REVISION**

#### Rationale (one paragraph)

本稿在 IST scope 内具有真实贡献:§9 SMS→MS 退化定理(formal degeneration theorem)、§4.2.5 三阶段 ablation(MR-design vs LLM-source factor decomposition)、§3.2.6 算子级工具对照(operator-level tool unreachability table)、§6.5 stakeholder analysis,以及高于 IST 平均水平的方法学透明度(pre-registration vs exploratory 区分、§5.6.2.1 cutoff sensitivity、§5.7.3 power analysis、§5.8.3 mixed-effects Singular 诚实声明)。**然而,5 位 reviewer 高度一致地识别出三个结构性问题**:(i) 主标题 "When LLM Source Diversity Doesn't Help" 是 strong negative claim,但 v4 实证只测了 prompt-fixed 弱形式,且 v3b→v4 contrast 受 v3b post-hoc selection 污染 — Devil's Advocate 将此列为 **CRITICAL-1 + CRITICAL-2 + CRITICAL-4**(R0/R1/R2/R3/DA 五位均独立指出,5/5 共识);(ii) §3.5.1 c-class primary MP shift 是 selection-on-the-response,缺 multiple-comparison 校正,但下游 verdict(§5.8.2 "严格达成"、§6.1 "17.6:1"、§6.3 联合呈现)未一致执行 caveat;(iii) §8.3 IST 2024 综述参考署名占位 "[Authors TBD]" 在投稿稿件中不可接受。**根据 IRON RULE 2,Devil's Advocate 标记 4 项 CRITICAL 均成立(均经 R0/R1/R2/R3 独立交叉确认),编辑决定不能为 Accept**。本稿在以上三类必修问题获实质回应后,具有 7.5+ 的接收潜力。

#### Strengths (3-5 sentences)

(1) **§9 退化定理**把 SMS 与经典 Jia & Harman MS 的兼容性从口头声明升格为可验证命题(L1-L6 + 三引理 + 主定理),五位 reviewer 一致认同这是 selling point(R0§S1 / R1§S7 / R2§S2 / R3§4 / DA§O-4)。(2) **§4.2.5 三阶段 ablation** 把 MR-MP 对齐设计与 LLM 源多样性两因子做工程解耦,设计精巧且在 LLM-mutant 文献(Tip 2024 LLMorpheus 单 LLM)中是首例(R0§S2 / R1§S6 / R2§S4 / R3§3.2)。(3) **方法学诚信高于平均水平**:pre-registered v3 与 exploratory v3b/v4 的分离、§3.5.1 四条 caveat、§5.7.3 power simulation、§5.8.3 mixed-effects Singular fallback 透明声明,在 IST 投稿中位水平之上(R0§S3 / R1§S1+S4 / R3§3.1 / DA§O-1+O-2+O-3)。(4) **§3.2.6.1 算子级对照表** 论证 OS/HP/TF/SI 4 类语义在 first-order 语法工具上结构性不可达,对工程读者可直接 actionable(R0§S5 / R2§S3 / R3§3.3)。(5) **Reproducibility 基础设施** 含 SSOT JSON、commit-hash、raw response store,超 IST 平均水平(R0§D5 / R1§6.4)。

#### Weaknesses (3-5 sentences)

(1) **Title-evidence misalignment**(5/5 共识):"Doesn't Help" 是全称否定式,实证只测 prompt-fixed 弱形式;且 v3b→v4 −0.007 是在 v3b post-hoc c→MP1 选择条件下计算,denominator 与 numerator 在选择空间上不对称,17.6:1 ratio 不是 clean factor decomposition(R0§W1 / R1§W3 / R2§W5 / R3§W2 / DA-CRITICAL-1+4)。(2) **Selection-on-response 污染半径未一致传导**:§3.5.1 caveat 写得专业,但 §5.8.2 "严格达成"、§6.1 "17.6:1"、§6.3 联合呈现 narrative 未按 caveat 执行,formal-claim vs caveat 自相矛盾(R0§W2 / R1§W3+W8 / DA-CRITICAL-2)。(3) **§8.3 IST 2024 综述署名占位 "[Authors TBD]"** 是论证链上的关键 anchor 引文(被 §1.3.2 / §5.7.2 / §6.1 / §7.1.6 反复引用),投稿前必须实名化(R0§W4 / R2§W6 / DA-MAJOR-6,3/5 reviewer 独立指出)。(4) **统计方法学 W**:§5.7.3 power 是 plug-in bootstrap from observed pool 而非 stipulated-alternative,与 R-13 真意不符(R1§W1);Cliff's δ CI [0.127, 0.740] 跨 H2 阈值未被 verdict 直面(R1§W2);Friedman 从 sensitivity 升格为 H4 联合证据违反 fallback hierarchy(R1§W4 / R2 implicit)。(5) **Title overreach 与 Practical deployability**:"scientific computing" 标题与 §3.1.1 4 章未覆盖 + 标量 `float→float` 签名不匹配;§6.5.3 auditor pathway 在现行 IEC 60880 / ISO 26262 / ASME V&V 文本中无 normative basis(R3§W1+W2 / DA-MAJOR-1)。

#### Mandatory Revision Schedule

- **Major revision deadline**: 4-6 个月(2026-09-01 至 2026-11-01 区间)
- **Round expectation**: 1 round of major revision → 1 round of minor revision → accept(若三类必修实质回应)
- **Resubmission as new manuscript** trigger:若 W1 fix 跑出的 v4-pre 数据显示 |Δδ_LLM_pre| > 0.05 且 95% CI 不覆盖零,则 headline 整体倒塌,届时建议 reject 后重新投稿(R0§8 reject trigger)

---

## 2. Reviewer Consensus & Disagreement Map

### 2.1 跨 reviewer 一致性映射表

| 议题 / Dimension | R0 (EIC) | R1 (Method) | R2 (Domain) | R3 (Practice) | R4 (DA) | 共识等级 |
|---|---|---|---|---|---|---|
| **Title 与证据基础不匹配 / "doesn't help" over-claim** | W1(主) | W3 | W5(estimand 错配)+ W7(toy scope) | W2(scientific computing 域) | **CRITICAL-1** + MAJOR-1 | **5/5 全 consensus(P0)** |
| **v3b post-hoc c→MP1 selection 污染下游 verdict** | W2 | W3+W8 | (隐含,W5 引用) | (W3 / W8 cross-source 协议脱节) | **CRITICAL-2** | **4/5(P0)** |
| **17.6:1 ratio 与 §5.7.2 caveat 自相矛盾** | W1(fix 3) | W3(fix) | (W5 over-translation) | — | **CRITICAL-4** | **3/5(P0)** |
| **c-class MP argmax 缺 multiple-comparison 校正** | W2(fix 2) | W5 | — | — | **CRITICAL-3** | **3/5(P0)** |
| **IST 2024 综述 [Authors TBD] 必须修复** | W4 | — | W6 | — | MAJOR-6 | **3/5(P0)** |
| **§9 退化定理 L1-L6 dependency / strict-vs-asymptotic** | W8 | §4 §9 注 | W3+W4+W10 | (S4 认可) | MAJOR-3 | **4/5(P1)** |
| **§5.7.3 power 是 plug-in 而非 stipulated-alternative** | (S4 总体认可) | W1(主) | — | — | MAJOR-2 | **2/5(P1,但 R1 力度强)** |
| **Cliff's δ CI [0.127, 0.740] 与阈值重叠未直面** | (W1 间接) | W2 | — | — | MAJOR-2 | **2/5(P1)** |
| **Friedman 从 sensitivity 升为 primary** | (§5.8.4 评注) | W4(主) | — | — | — | **2/5(P1)** |
| **K_eq sensitivity 表未实跑** | — | W6 | — | — | — | **1/5(P1)** |
| **Petrović 2018 numerical coincidence 论证克制不足** | W5 | — | (D6 认可作者已克制) | (W1 acknowledge) | — | **2/5(P1)** |
| **§6.5.3 Auditor pathway 在 IEC/ISO/ASME 无依据** | (§6 评注) | — | — | **W1**(主) | — | **2/5(P1)** |
| **REPRODUCIBILITY env-var 双 trap + 多版本 SSOT** | (W3 间接) | §6.2 | — | **W3**(主) | — | **2/5(P1)** |
| **§4.2.5(b) v4 未做 dual-blind 协议不对称** | §4 评注 | (隐含 W3) | — | **W8** | (4.2 missing stakeholder) | **3/5(P1)** |
| **CPH / coupling effect / Andrews 2005 / Papadakis 2019 引用缺失** | §8 评注 | — | **W9** + Lit table | — | — | **2/5(P2)** |
| **Higher-Order Mutation scope 未限定** | — | — | **W8** | — | — | **1/5(P2)** |
| **mut_j ↔ CE/OS/HP/TF/SI 双 taxonomy 桥接缺失** | — | — | **W1** | — | — | **1/5(P2)** |
| **mutmut/cosmic-ray default subset 标注** | — | — | **W2** | — | — | **1/5(P2)** |
| **§5.6.1.1 zero-mass dominance 未传导到 §5.7.2** | W6(部分) | W7 | — | — | (3.1 alt explanation) | **3/5(P1)** |
| **Air-gap incompatibility / Industrial deployability** | — | — | — | **W4+W7** | — | **1/5(P2)** |
| **Abstract / §3.4 mutant count 报告精度** | — | — | — | — | MINOR-5 | **1/5(P2)** |
| **§1.5 H3 撤回时间点形式化** | — | — | — | — | MAJOR-5 | **1/5(P2)** |

### 2.2 Cross-reviewer CONSENSUS Issues(≥3 reviewer 共识,共 7 项)

1. **C1 — Title 与证据基础 misalignment**(5/5)。R0/R1/R2/R3/DA 全部独立指出,五位 reviewer 共识程度最高。Devil's Advocate 标 CRITICAL-1。
2. **C2 — v3b selection-on-response 污染 verdict 一致性**(4/5)。R0/R1/R3/DA 独立指出;R2 在 W5 over-translation 中隐含。Devil's Advocate 标 CRITICAL-2。
3. **C3 — 17.6:1 ratio 与 §5.7.2 caveat 自相矛盾**(3/5)。R0/R1/DA 直接指出。Devil's Advocate 标 CRITICAL-4。
4. **C4 — IST 2024 综述 [Authors TBD] 必须修复**(3/5)。R0/R2/DA 独立强调,Domain reviewer 表达最强(W6)。
5. **C5 — §9 退化定理 L1-L6 dependency / strict-vs-asymptotic**(4/5)。R0/R1/R2/DA 独立指出,Domain reviewer 论证最严密(W3+W4)。
6. **C6 — §5.6.1.1 zero-mass dominance 未传导到 §5.7.2 verdict**(3/5)。R0/R1/DA 独立指出。
7. **C7 — §4.2.5(b) v4 未做 dual-blind 协议不对称**(3/5)。R0(§4 评注 + §7.1 R11 建议)/R1(隐含 W3)/R3(W8)/DA(4.2 missing perspective)。

### 2.3 DISAGREEMENT Points(reviewer 之间分歧 — 编辑仲裁)

#### Disagreement-1:Title 应改为何种程度?

- **R0 fix 选项**:三选一(补 v4-pre 格点 / 改标题为 "Under fixed prompt template" / 显式 limitation 段落)。
- **R1 fix**:倾向 v4' = cross-source × c→MP5 实跑(W3 fix 3),即补 v4-pre 格点。
- **R2 fix**:倾向 W5 estimand caveat 全面化,而非改标题。
- **R3 fix**:**重写主标题**为 *"Semantic Mutation Operators for Metamorphic Testing of Single-Output Scientific Computing Kernels"* 或加 "Toy-Scale";不仅是 LLM 源问题,是 "scientific computing" 域承诺问题。
- **DA fix**:重写主标题为 *"When Same-Prompt LLM Source Diversity Doesn't Help: ... for Small-Scale Python Scientific Computing PUTs"*。

**编辑仲裁**:**R3 + DA 的双层重写主张更合理**。理由:(a) Title 中存在两个独立 over-claim(scientific computing 域 + LLM source diversity),仅修一个不能解决另一个;(b) R0 的"补 v4-pre 格点"是最严格但工作量大;若作者愿意补 v4-pre 数据(c→MP5 cross-source),且数据支持,那么 LLM 源部分可保留;但 scientific computing → kernels/single-output 的 scope 收缩**与数据无关,无论是否补 v4-pre 都需要做**;(c) DA 提案语义最精确(显式 "same-prompt"),但 R3 的 "single-output kernels" 维度更必要。**最终建议主标题**:*"When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels"*,**作为 P0 必修项**。

#### Disagreement-2:v3b 是否仍可作为 sensitivity 报告?

- **R0**:v3b 作为 exploratory 报告 OK,但 §6.3 "v3b 4/4 严格达成" 必须降级,abstract 应只提 v3 primary 3/4。
- **R1**:v3b 不应作为 H4 sign test "严格达成" 的依据;Friedman 不应作为 H4 联合证据。
- **R2**:未直接表态(D6 评分 7,认可作者 caveat)。
- **R3**:未直接表态。
- **DA-CRITICAL-2**:v3b 完全不进 verdict,仅作为 robustness/sensitivity 段;v3 primary 是唯一 confirmatory baseline;考虑补 leave-one-class-out 重选(预注册规则)在新数据上重测。

**编辑仲裁**:**接受 R1+DA 的更严格立场**。理由:(a) IRON RULE 与方法学诚信要求 caveat 与 verdict 一致;(b) §3.5.1 的 caveat 已写"应作为 exploratory finding 而非 confirmatory result"——既然作者已声明,§5.8.2 "严格达成" / §6.1 "17.6:1" / §6.3 联合呈现就必须按声明执行;(c) v3b 可保留为 sensitivity report,但 verdict / abstract / title 须以 v3 primary 数字为准。R0 的"abstract 只提 v3 primary 3/4"可作为 P0 必修。

#### Disagreement-3:Auditor pathway / Practical deployability 的处理优先级?

- **R0**:认可 §6.5 stakeholder analysis 是 IST-fit selling point(S5),未列为必修。
- **R1**:未直接讨论。
- **R2**:未直接讨论。
- **R3-MAJOR-W1+W2+W4+W6**:严重 over-claim,在现行 IEC/ISO/ASME 无 normative basis,§6.5.3 必修。
- **DA**:未列为 CRITICAL,只在 missing stakeholder(LLM provider)层面提及。

**编辑仲裁**:**部分接受 R3 立场,但降级为 P1 而非 P0**。理由:(a) R3 的 W1 论证扎实(IEC 60880 全文未提 mutation,ISO 26262-6 Table 12 仅作 Annex method 无 score-based threshold,ASME V&V 全无 mutation)— 这些事实证据无可辩驳;(b) 但 §6.5 是 discussion 章节,可以容纳 aspirational positioning,只需诚实降级措辞 + 删除具体 ≥0.20/0.30 数字阈值即可解决,不需要重做实验;(c) R3 的 W3(REPRODUCIBILITY env-var trap)与 W4(air-gap)是 reproducibility 类问题,可在 artifact / appendix 阶段修复;(d) 因此把 R3 的 W1+W3 作为 P1(should fix),W2(title scope)作为 P0(已并入 Disagreement-1 的 title 重写)。

---

## 3. Devil's Advocate CRITICAL Findings — Special Treatment

> 根据 IRON RULE 2:若 DA 任何 CRITICAL 成立,Decision 不能为 Accept。**4 项 CRITICAL 经 R0/R1/R2/R3 交叉确认,均成立**。决定 = Major Revision(锁死)。

### CRITICAL-1 — 标题与正文承诺不一致(over-claim)

- **DA 立场**:主标题 "When LLM Source Diversity Doesn't Help" 是 strong 否定式,但 §4.2.5.1 / §7.1.7 / §5.7.2 自承 v4 仅测 prompt-fixed 弱形式。
- **交叉确认**:R0§W1(独立指出)、R1§W3(conditional on v3b)、R2§W5(estimand 错配)、R3§W2(scientific computing 域 + 标量签名)— **5/5 共识**。
- **编辑仲裁**:**CRITICAL-1 严格成立**。**修改不可妥协**。
- **隐含修订项**(P0):
  - (a) 重写主标题为 *"When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels"*。
  - (b) Abstract 第 1 句加 "12 single-input single-output Python functions, 50–400 LOC each"。
  - (c) Abstract 关于 −0.007 的描述加 "under identical prompt template across three LLMs"。
  - (d) §1.6.2 认识论声明加显式 scope:"本文 SMS 实证规模属 first audit on toy / textbook-scale scientific PUTs"。

### CRITICAL-2 — v3b post-hoc selection 污染下游 verdict

- **DA 立场**:§3.5.1 caveat 已声明 selection-on-the-response,但 §5.8.2 "严格达成"、§6.1 "MR-design 主导"、§6.3 联合呈现 verdict 仍依赖 v3b 数据。
- **交叉确认**:R0§W2、R1§W3+W8、R3 隐含(W8 protocol-implementation gap 也指向同方向)— **4/5 共识**。
- **编辑仲裁**:**CRITICAL-2 严格成立**。**修改不可妥协**。
- **隐含修订项**(P0):
  - (a) §5.8.2 "严格达成"改为"v3 pre-registered: 3/4 (partial); v3b exploratory: 4/4 (post-hoc, conditional on c→MP1 selection)"。删去"严格"二字。
  - (b) §6.3 联合呈现表中的 (b) "4/4 类 sign test 通过(v3b)" 改为 "3/4 (v3 pre-registered) / 4/4 (v3b post-hoc)";(c) Friedman 项移除或加 inline caveat "measures MP-rank dispersion, not cross-class consistency"。
  - (c) Abstract 仅报告 v3 primary 3/4,不以 v3b 4/4 为旗帜。
  - (d) §6.1 narrative 加显式 conditional 表述:"Conditional on v3b's data-driven c→MP1 selection, switching from same-source to cross-source pool changes δ by −0.007"。

### CRITICAL-3 — c-class primary MP shift 未做 multiple-comparison 校正

- **DA 立场**:argmax over 5 candidate MPs 是 max-statistic;在 H_0 下也以 ≈ 1−(1−α)^5 虚报率显著;§3.5.1 caveat #2 承认未做 Bonferroni/max-stat 校正,但 §5.7.2 / §6.1 仍把 v3b 数字当 robustness check 合法替代。
- **交叉确认**:R0§W2(fix 选项 2)、R1§W5(主)— **3/5 共识**。
- **编辑仲裁**:**CRITICAL-3 严格成立**。
- **隐含修订项**(P0):
  - (a) §3.5.1 加 permutation null:1000 次在每个 c-class PUT 内打乱 5 个 MP 标签,重新计算 argmax MP 的 mean SMS,得 null distribution,报告 percentile rank of observed 0.233(R1§W5 fix 2)。
  - (b) 若 (a) 不可跑,把 caveat #2 升级为"以 Bonferroni × 5 上界折算 effective α":δ_v3b unadjusted CI [0.154, 0.743]→Bonferroni 调整 99% CI ≈ [0.05, 0.85]。
  - (c) 在 v3b 引用处统一加注 "n=3 PUTs in c-class, max over 5 MPs without multiplicity correction; treat δ_v3b inflation upper bound at α_eff ≈ 0.23"。

### CRITICAL-4 — §6.1 "17.6:1 贡献比" 与 §5.7.2 "two contrasts reported separately" 自相矛盾

- **DA 立场**:§5.7.2 表注规定不要做合成 ratio,但 §4.2.5 末段 + §6.1 第 2 段都直接给出 17.6:1。论文自我违反。
- **交叉确认**:R0§W1(fix 3)、R1§W3(fix 2)— **3/5 共识(若计 R2 W5 的 over-translation,则 4/5)**。
- **编辑仲裁**:**CRITICAL-4 严格成立**。
- **隐含修订项**(P0):
  - (a) **删除 §4.2.5 与 §6.1 中的 "17.6:1" 合成数字**;两处都用 §5.7.2 的 contrast 表行文。
  - (b) §6.1 narrative 改为 "We report Δδ_MR = +0.123 (under v3b's post-hoc c-class selection) and Δδ_LLM = −0.007 (under fixed prompt template) as two separate contrasts; these are not combined into a ratio because the numerator includes a confounded data-driven adjustment and the denominator is conditional on the same confound."

---

## 4. Revision Roadmap (Prioritized for Author)

### P0 — Must Fix (blocks resubmission;最多 8 项)

| ID | 标题 | Rationale (Reviewer cite) | Suggested Fix | Location | Estimated Effort |
|---|---|---|---|---|---|
| **P0-1** | 重写主标题与 Abstract scope | R0§W1 / R1§W3 / R2§W5 / R3§W2 / DA-CRITICAL-1 (5/5) | 主标题加 "Same-Prompt" + "Single-Output Scientific Computing Kernels";Abstract 加签名规模 + identical prompt template 措辞 | Title + Abstract + §1.6.2 | 0.5 day |
| **P0-2** | 删除 §6.1 + §4.2.5 "17.6:1 ratio" 合成数字 | R0§W1 / R1§W3 / DA-CRITICAL-4 (3/5+) | 改为 §5.7.2 两个 contrast 分别报告;narrative 加 conditional 表述 | §4.2.5 末段, §6.1 第 2 段 | 0.5 day |
| **P0-3** | §5.8.2 "严格达成" 降级 + §6.3 联合呈现修订 | R0§W2 / R1§W8 / DA-CRITICAL-2 (3/5+) | 改为 "v3 pre-registered: 3/4 (partial); v3b exploratory: 4/4 (post-hoc, conditional on c→MP1 selection)";Abstract 仅报 v3 primary 3/4 | §5.8.2, §6.3, Abstract | 1 day |
| **P0-4** | c-class MP shift max-selection inflation 量化 | R0§W2 / R1§W5 / DA-CRITICAL-3 (3/5) | 跑 1000-permutation null 报告 percentile rank,或以 Bonferroni × 5 上界折算 effective α;v3b 引用统一加 inflation warning | §3.5.1 caveat #2, §5.7.2, §6.1 | 1-2 days(取决于是否实跑 permutation) |
| **P0-5** | 补 v4-pre (c→MP5 cross-source) 格点 OR 显式 limitation | R0§W1(fix 1) / R1§W3(fix 3) / DA-CRITICAL-1 (3/5) | 三选一:(a) 实跑 v4-pre 格点新 cell;(b) 在 §4.2.5(b) 加 "v3 dual-blind / v4 no dual-blind 不对称 + v4 是 conditional on v3b" 双声明;(c) §7.1 加 R11 selection-on-response 专章 | §4.2.5, §6.1, §7.1 | 2-3 days(若实跑) / 1 day(若仅声明) |
| **P0-6** | IST 2024 综述完整 citation | R0§W4 / R2§W6 / DA-MAJOR-6 (3/5) | 投稿前完成 [Authors TBD] 实名化(从 DOI URL S0950584924000739 检索 ScienceDirect 元数据);若验证发现非 LLM-mutation 综述,删除 §1.3.2 / §5.7.2 / §6.1 / §7.1.6 4 处 "0.30-0.45 区间" 引用,改用 Tip 2024 单点 + estimand caveat | §8.3 + 4 处正文引用 | 0.5 day |
| **P0-7** | Pre-registration claim 证据 | R0§W3 (1/5,但 R0 列为 P0) | (a) 列出 OSF/aspredicted 注册 URL + 日期;或 (b) 删除 "pre-registered" 措辞,改为 "fixed prior to data collection (see internal protocol document)" + 提供 git commit time | §1.5, §3.5.1, §5.2 | 0.5 day |
| **P0-8** | §5.7.2 verdict 修订 + δ CI vs threshold 关系 | R1§W2 (主) / R0§7 (间接) | Verdict 改为 "H2's point-estimate condition is not met; CI [0.127, 0.740] does not exclude truth ≥ 0.474, so rejection is in the operational pre-registered sense"; Abstract "is rejected" → "is not met under pre-registered point-estimate criterion"; 加 TOST-style 辅助 | §5.7.2, Abstract | 0.5 day |

**P0 总工作量估计**:5-8 个工作日。

### P1 — Should Fix(normal expectation,正常 revision 期望)

| ID | 标题 | Rationale (Reviewer cite) | Suggested Fix | Location | Effort |
|---|---|---|---|---|---|
| **P1-1** | §5.7.3 power 重新框架为 two-condition | R1§W1 (主) / DA-MAJOR-2 | (A) plug-in (当前) + (B) stipulated-alternative non-parametric simulation;后者构造 truth_δ = 0.474 的两个 score 分布 | §5.7.3 | 1-2 days |
| **P1-2** | Friedman 角色显式声明为 fallback,从 H4 联合证据剥离 | R1§W4 (主) | Abstract / §6.3 / §5.8.4 修订;Friedman 声明为 mixed-effects fallback;§5.3.2 列 fallback hierarchy | Abstract, §5.8.3-4, §6.3 | 1 day |
| **P1-3** | §9 退化定理 L1-L6 dependency 与 strict-vs-asymptotic | R0§W8 / R1§§4 / R2§W3+W4 / DA-MAJOR-3 (4/5) | (a) 改写为 3 个独立轴(equiv/killed/mut)对应 3 引理;(b) 摘要 "strictly degenerate" 改为 "degenerate ... modulo D_S-measure-zero subsets";(c) 引理 9.2 r ≠ id 段精确化 | §9.2, §9.3, §9.4, Abstract line 14 | 1-2 days |
| **P1-4** | K_eq sensitivity 表实跑 | R1§W6 | §5 或附录加 K_eq ∈ {500, 1000, 2000} 下 60-cell mean SMS / aligned / cross / Cliff's δ 表;给 Hoeffding 上界数字;若不跑,把 R2 promise 撤回为 limitation | §5(新), §7.5 | 1-2 days |
| **P1-5** | §5.6.1.1 zero-mass dominance 传导到 §5.7.2 verdict | R0§W6 / R1§W7 / DA-3.1 (3/5) | §5.7.2 verdict 段加 effective sample size note;考虑 BCa bootstrap 替代 percentile;或给 caveat 说明 percentile bootstrap 在 zero-mass 偏态下的已知 liberal 倾向 | §5.7.2 | 0.5-1 day |
| **P1-6** | §6.5.3 Auditor pathway 降级 | R3§W1 (主) (1/5,但论证扎实) | (a) 标题改为 "Research-grade evidence for V&V documentation (long-term aspiration)";(b) 删除 ≥0.20/0.30 具体数字阈值;(c) 加 "no current standard endorses these thresholds" 警示 + "Engagement with ASME V&V or IEC SC 45A working groups not yet initiated" | §6.5.3 | 0.5 day |
| **P1-7** | §4.2.5(b) v3 dual-blind / v4 no dual-blind 不对称声明 | R0§4 评注 / R3§W8 / DA§4.2 (3/5) | §4.2.5(b) 加 "v3 与 v4 协议非完全对称——v4 暂不含 dual-blind";§7.1 加 R11 "Protocol-implementation gap";retro-fit 60-100 mutant 抽样 dual-blind(若可) | §4.2.5(b), §7.1 | 1 day |
| **P1-8** | RQ4 Spearman ρ 95% CI + 从 abstract 删除 SMS-PC 描述 | R0§W6 / R1§W10 (2/5) | §5.9.2 加 95% CI for ρ (Fisher z + n=12);Abstract 删除 RQ4 / Spearman 提及,留正文 §5.9 future-work hook | Abstract, §5.9.2-3 | 0.5 day |
| **P1-9** | REPRODUCIBILITY env-var fail-loud + wrapper script | R3§W3 (主) (1/5,论证扎实) | (a) `scripts/build_paper_numbers.py` 顶部加 fail-loud env-var 检查;(b) 提供 `scripts/reproduce_paper.sh` single-entry wrapper;(c) DATASET.md 把 legacy 文件移到 `data/results/legacy/`;(d) Zenodo bundle 加 Dockerfile 与 frozen wheels | REPRODUCIBILITY.md, scripts/, DATASET.md | 1-2 days |
| **P1-10** | Petrović 数值近似论证克制升级 | R0§W5 (1/5) | Abstract 与 §1.3.2 删除 "高度吻合" 措辞;§6.1 加 "construct difference" 段(developer survey vs auto classifier);§6.1 加后续验证路径(developer survey 抽样) | Abstract, §1.3.2, §6.1 | 0.5 day |
| **P1-11** | per-class Friedman + Bonferroni × 4 校正 | R1§W10 | §5.8.4 加 Kendall's W;b 类 0.029 → adjusted 0.116 → verdict 弱化;若 b 类 Bonferroni 后不显著,§6.3 narrative 同步修订 | §5.8.4 | 0.5 day |

**P1 总工作量估计**:7-10 个工作日。

### P2 — Nice to Have(optional / typesetting 阶段)

| ID | 标题 | Rationale | Fix | Location | Effort |
|---|---|---|---|---|---|
| **P2-1** | §3.2.6.0 加桥接节(mut_j ↔ CE/OS/HP/TF/SI 双 taxonomy) | R2§W1 | 加 5×5 交叉表展示每个 mut_j 由哪几类 AST-operation 实例化 | §3.2.6 前 | 0.5 day |
| **P2-2** | §3.2.6.1 表头标注 default subset | R2§W2 | 表头加 "default operator subset of mutmut 2.4 / cosmic-ray 8.3"; 表后加 "Even when extended to ~25 default operators, structural limitation prevents OS/HP/TF/SI" | §3.2.6.1 | 0.25 day |
| **P2-3** | CPH / coupling effect / Andrews 2005 / Papadakis 2019 引用补全 | R2§W9 | §1.3.2 加 domain-CPH 段落;§6.1 引用 Andrews 2005 / Just 2014 FSE / Papadakis 2019;§8 References 补 DeMillo 1978 | §1.3.2, §6.1, §8 | 1 day |
| **P2-4** | §3.2.6 HOM scope 限定 | R2§W8 | 段首加 "scope of this comparison: limited to first-order syntactic mutation tools, not HOM";引用 Jia & Harman 2009 / Kintis 2018 | §3.2.6 | 0.25 day |
| **P2-5** | §3.1.1(e) 工业 PUT 比对短节 | R0§W7 | 加 1-2 篇工业级 mutation testing 工作的对比表(Petrović 2021 / Just 2014);或在 1-2 PUT 上做 vector-state interface toy 实验 | §3.1.1 | 1-2 days |
| **P2-6** | §3.4 mutant count 报告精度 | DA-MINOR-5 | Abstract 改为 "60 cells (12 PUT pools of average 24.3 mutants reused across 5 MPs)" | Abstract, §3.4 | 0.25 day |
| **P2-7** | §1.5 H3 撤回时间点形式化 | DA-MAJOR-5 | 加 "撤回决策记录在 git log commit hash <X>,时间戳早于 v3b/v4 数据采集";配套加 "H3 撤回的判停规则 = equiv-触发 cells < 10" | §1.5, §3.5.1 | 0.25 day |
| **P2-8** | §6.5 air-gap incompatibility 显式声明 | R3§W4 (1/5) | §6.5.1 workflow 步骤 1 加 "若 PUT 是新的,需要在 internet-connected build server 上一次性生成 mutant pool";§7 future work 加 "deterministic local LLM" 路径 | §6.5.1, §7 | 0.5 day |
| **P2-9** | §6.5.2 PR-CI cost / latency reframe | R3§W5 (1/5) | "Resource estimate" 子段;reframe 为 "low-frequency MR audits (quarterly), not per-PR gating" | §6.5.2 | 0.25 day |
| **P2-10** | §1.3 ASME V&V 引用 | R3§W10 (1/5) | 加 ASME V&V 20-2009 / V&V 40-2018 引用;§6.5 stakeholder 改为"V&V engineers"作为更现实 deployment target | §1.3, §6.5, §8 | 0.5 day |
| **P2-11** | requirements-frozen.txt + Docker bundle | R3§W9 (1/5) | Zenodo bundle 包含 wheel hash 与 Dockerfile,2028+ 兼容 | Zenodo artifact | 1 day |
| **P2-12** | DeepSeek 模型选择论证 5-10 算子 dry-run | DA-MINOR-6 | §4.2.5(c) 改为 "dry-run on a2_OS1 only; v4-pro 在 P4 重测";至少 5-10 算子 dry-run | §4.2.5(c) | 0.5 day |

**P2 总工作量估计**:6-8 个工作日(可选)。

**总修订工作量**:P0+P1 约 12-18 个工作日(2.5-4 周);加 P2 约 18-26 个工作日。Major revision 4-6 个月时限合理。

---

## 5. Score Aggregation

### 5.1 各 reviewer overall score(原文末页)

| Reviewer | Overall Score(1-10) | Verdict | Aggregation method |
|---|---|---|---|
| **R0 (EIC)** | **6.7** | Major Revision | Weighted across 7 dimensions(D1=6, D2=7, D3=7, D4=7, D5=8, D6=6, D7=7) |
| **R1 (Methodology)** | **7.0** | Major Revision | 几何均值(报告范围 6.0-7.5) |
| **R2 (Domain)** | **6.71** | Major Revision | 7-dim 算术均值(D1=7, D2=7, D3=6, D4=8, D5=7, D6=6, D7=6) |
| **R3 (Practical)** | **5.57** | Major Revision | 7-dim 算术均值(7+7+5+5+7+3+5) ÷ 7 |
| **R4 (Devil's Advocate)** | (未给数值,仅 verdict) | Major Revision | 接收概率 ~30% reject(标题不缩小) / ~60-70% accept(对齐后) |

### 5.2 聚合统计

- **算术均值**(R0 R1 R2 R3,共 4 数值):(6.7 + 7.0 + 6.71 + 5.57) / 4 = **6.50**
- **几何均值**:(6.7 × 7.0 × 6.71 × 5.57)^(1/4) = (1745.6)^0.25 ≈ **6.46**
- **范围**:[5.57, 7.0] = 1.43 spread
- **中位数**:中位 (6.7, 6.71) → **6.71**
- **加权几何均值**(R0 EIC 权重 1.5,其他 1.0):(6.7^1.5 × 7.0 × 6.71 × 5.57)^(1/4.5) ≈ **6.51**

### 5.3 决策映射

按 IST 标准 EIC scoring(1=fatal / 4=below threshold / 5-6=marginal / 7-8=publishable / 9-10=exemplary):

| 聚合分 | 决策映射 |
|---|---|
| ≥ 8.0 | Accept / Minor Revision |
| 7.0-7.9 | Minor Revision / Major Revision |
| 6.0-6.9 | **Major Revision** |
| 5.0-5.9 | Major Revision / Reject-and-Resubmit |
| < 5.0 | Reject |

**聚合分 6.46-6.51 映射为 Major Revision**,与 5/5 reviewer 独立 verdict 一致。

### 5.4 Reviewer verdict 一致性

**5/5 reviewer 独立给出 Major Revision verdict**,无分歧。这是 reviewer panel 高度一致的信号。**根据 IRON RULE 2,DA CRITICAL 成立锁死 ≠ Accept**;聚合分进一步独立确认 Major Revision 为合理决定。

---

## 6. Open Questions for Authors(Socratic seeds for §2.5 coaching)

1. **关于 v3b 角色的根本问题**:你愿意把 v3b 完全降级为 sensitivity report,abstract / verdict / §6.3 narrative 全部以 v3 primary 数字为准吗?如果 v3b 被严格降级,论文还能否支撑 "MR-MP 对齐设计是 H2 主导因子" 的 narrative,还是需要把这一论断改写为 "exploratory observation, not pre-registered finding"?(对应 P0-2/P0-3,触及论文 narrative 主轴)

2. **关于 v4-pre 格点的取舍**:补 v4-pre (c→MP5 cross-source) 数据需要新一轮实验(估计 2-3 days + cost)。如果你不补,headline "LLM source diversity doesn't help" 必须降级为 "Under fixed prompt template, three LLM sources contribute near-zero variance to SMS effect size — but this is conditional on v3b's c-class selection"。哪一条对你更重要?(对应 P0-5,触及 R0 reject trigger)

3. **关于标题的双层 over-claim 取舍**:R3+DA 主张主标题需同时收缩两个维度(LLM source diversity → same-prompt;scientific computing → single-output kernels)。如果只能修一个,你会修哪个?为什么?(对应 P0-1,触及 5/5 reviewer 共识)

4. **关于 §8.3 IST 2024 综述实名化的 fallback**:如果 [Authors TBD] 检索后发现这并非你以为的 LLM-mutation 综述(例如它是单一 case study 而非 综述),你的 §1.3.2 / §5.7.2 / §6.1 / §7.1.6 4 处 "0.30-0.45 区间" contextual support 论证将整体倒塌。你是否愿意预先准备一个 fallback narrative,只用 Tip 2024 LLMorpheus 单点对照 + estimand caveat?(对应 P0-6)

5. **关于 §9 退化定理的方法学定位**:R0 建议把 §9 缩到 1-1.5 页(empirical 期刊期待 "实证为主 + 理论为辅");R2 主张精化 L1-L6 dependency 与 strict-vs-asymptotic 区分。两者都需要工作。你认为 §9 在 IST 投稿语境下的最优篇幅与形式化深度是多少?是否考虑把详细证明放 appendix?(对应 P1-3)

---

## 7. Closing Note

本稿在 LLM-mutant + 科学计算软件交叉领域具有真实贡献,**方法学诚信高于 IST 同期投稿中位水平**(5/5 reviewer 一致认可)。但 5/5 reviewer 独立指出**头条命题(headline)与证据基底(evidence)之间存在结构性 misalignment**——这不是诚信问题,是 narrative 与 caveat 一致性问题。

**核心修订原则**:作者已经做了正确的方法学声明(§3.5.1 caveats、§5.7.2 contrast 表注、§7.5 limitations),但 headline / verdict / abstract / title 没有跟着 caveat 一致执行。**revision 的本质是把 caveat 的强度传导到下游每一句结论**,而非新增 caveat 或新做实验(除 P0-5 v4-pre 格点为可选实跑)。

如能在 revision 中实质回应 P0(尤其 CRITICAL-1/2/3/4 与 IST 综述实名化),本稿在 second-round review 中可走向 minor revision → accept,目标聚合分 7.5+。

**Final editorial verdict: MAJOR REVISION,timeline 4-6 个月。**

---

*Editorial Synthesizer — 2026-05-01,based on 5 independent reviewer reports*
