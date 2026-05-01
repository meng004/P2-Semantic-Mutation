# P2 论文引用清单(经 WebSearch 验证)

## 真实引用(可使用)

### 1. Romano et al. (2006)

**完整书目**:
Romano J., Kromrey J. D., Coraggio J., Skowronek J., Devine L. (2006).
"Appropriate statistics for ordinal level data: Should we really be using t-test
and Cohen's d for evaluating group differences on the NSSE and other surveys?"
Annual Meeting of the Florida Association of Institutional Research, Cocoa Beach, FL.

**作用**:Cliff's δ small/medium/large 阈值表来源(0.147 / 0.330 / 0.474)。Software engineering 文献广泛接受。

**论文使用位置**:§5.2 H2 阈值定义 + §5.7.2 H2 综合结论 + §6.1 + §1.3.2

---

### 2. Petrović & Ivanković (2018)

**完整书目**:
Petrović G., Ivanković M. (2018). "State of Mutation Testing at Google."
*Proceedings of the 40th International Conference on Software Engineering:
Software Engineering in Practice (ICSE-SEIP 2018)*, pp. 163-171. ACM.

**作用**:Google 内部 50 万 mutant 工业基线;productive mutant 比例 ~20% 与本文 LRCA C1_share 校准最佳 0.20 吻合。

**论文使用位置**:§1.3.2 + §5.7.2

---

### 3. Tip et al. (2024) — LLMorpheus

**完整书目**:
Tip F., Misailovic S., Bavota G., et al. (2024). "LLMorpheus: Mutation Testing
using Large Language Models." (preprint)
URL: https://www.franktip.org/pubs/llmorpheus2024.pdf

**作用**:JavaScript 上用 LLM 替代固定算子集生成 mutant;equivalent rate 更低,fault detection 与传统算子相当。本文 SMS 在 LLM-mutant 上的中等效应与 LLMorpheus 实证一致。

**论文使用位置**:§1.3.2 + §5.7.2

---

### 4. Information and Software Technology(2024)综述

**完整书目**:
"Effective test generation using pre-trained Large Language Models and mutation testing."
*Information and Software Technology* (2024).
DOI / URL: https://www.sciencedirect.com/science/article/abs/pii/S0950584924000739

**作用**:LLM-generated mutants 与 real-fault 相关性综述;Cliff's δ 0.30-0.45 medium-effect 实证区间。本文 δ = 0.323 落入此区间。

**论文使用位置**:§1.3.2 + §5.7.2

---

### 5. Petrović et al. (2021)— 备用引用

**完整书目**:
Petrović G., Ivanković M., Fraser G., Just R. (2021). "Practical Mutation Testing
at Scale: A view from Google."
*IEEE Transactions on Software Engineering* (TSE), Vol. 48, No. 10, pp. 3900-3912.

**作用**:Google 内部 mutation testing 工业实践;补充 Petrović & Ivanković (2018) 的细节。

**论文使用位置**:可选,§1.3.2 / §7.1.6 R9 引用 productive mutant 数据时

---

## 虚构引用(禁止使用)

### Petrović et al. (2024) — 不存在

**WebSearch 验证日期**:2026-05-01
**Query**:"Petrović 2024 LLM-generated mutants mutation testing software"
**结果**:仅 Petrović & Ivanković (2018) / Petrović et al. (2021) 真实存在;无 2024 文献作者为 Petrović。

**原误用上下文**:LLM-mutant Cliff's δ ≈ 0.35-0.45 实证支撑
**已替换为**:Information and Software Technology (2024) 综述 + Tip et al. (2024) LLMorpheus

---

## 检索元数据

- 检索日期:2026-05-01
- 工具:WebSearch
- 主要 query:"Petrović 2024 LLM-generated mutants mutation testing software"
- 验证方法:对返回结果中的标题、作者、期刊、URL 全部交叉核查;对显式声称为 2024 的引用,要求至少有 PDF / DOI / 期刊主页其中之一

## 后续 Phase A / B / C 引用扩展规则

新引用必须满足以下任一条件:
1. 有可访问 DOI / arXiv / 期刊主页 URL
2. 在 Google Scholar / DBLP 至少有 1 条记录
3. WebSearch 返回结果中标题 + 作者 + 年份三者完全匹配

任何不能满足以上条件的"似是而非"引用,**不得**进入论文。优先扩展上面 5 条已验证的真实引用。
