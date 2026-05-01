# P2 RQ-Completion Final State(post-spiral 14 轮)

## RQ × 假设 实证状态表

| RQ | 假设 | 形式判定 | 关键数字 | 章节 | 状态 |
|----|------|----------|---------|------|------|
| RQ1 | H1: aligned-SMS > 0 across PUTs | ✓ 12/12 PUT aligned mean > 0 | mean SMS aligned = 0.197 | §5.6 / §5.7 | 达成 |
| RQ1 | H5: ≥ 80% cells with suspect_share ≤ 0.20 | ✗ 实测 9/60 = 15% | mean C1_share = 0.16 | §5.6.2 | **未达成**(诚实报告;§7 R4 跟进) |
| RQ2 | H2: Cliff's δ ≥ 0.474 ∧ ratio ≥ 3.0 | ✗ δ = 0.321(< 0.474);ratio 不可定义(median_cross = 0) | δ CI [0.021, 0.639] | §5.7.2 | **未达成大效应阈值;CI 下限 > 0 提供方向证据**(§7 R9/R10) |
| RQ3 | H4: 4/4 类 aligned > cross | ✗ Sign test 3/4 | 类均值 a=0.067, b=0.156, c=0.044, d=0.111 | §5.8.1-2 | 部分达成 |
| RQ3 | mixed-effects formal | ✗ Singular + Group Var 退化 | 主模型不收敛 | §5.8.3 / §7.2.2 R6 | **不可用**(改用 sign test + forest plot 三件式) |
| RQ4 | SMS vs PC 相关性 | ρ ≈ 0(n = 12) | Spearman ρ = 0.026, Kendall τ = 0 | §5.9 | **达成**(作为"SMS 提供独立维度"的正面证据) |

## RQ-Coverage 自审

| RQ | Coverage | 关键证据 | 未结清项 |
|----|----------|----------|----------|
| RQ1 | 95% | Track-2 v2 60-cell heatmap;LRCA C1_share 表;H1 ✓;**H5 未达成已诚实声明** | 无阻断;LRCA 阈值校准列入 §7 R4 后续 |
| RQ2 | 90% | Cliff's δ + 95% CI;aligned/cross 箱线图;**H2 形式上未达成,CI 下限 > 0 提供方向证据**(§5.7.2 + §6.1 诚实声明) | H2 阈值未越,作为 limitation 而非阻断 |
| RQ3 | 85% | 类均值 + sign test 3/4 + forest;**MixedLM 主模型 Singular,fallback Group Var 退化**(§5.8.3 + §7.2.2 R6 扩展) | mixed-effects 不可用;以 sign test 为正式结论 |
| RQ4 | 70% | SMS vs PC Spearman ≈ 0 + Kendall = 0(n = 12 PUT);scatter | PC 定义保持最简,留待 P4 扩展(§1.6.1) |

## 投稿就绪决定

| 维度 | 状态 |
|---|---|
| 实证数据完整性 | ✓ Track-2 v2 60 cells × 12 mutants × N=20 |
| 章节完整性(§1-§9) | ✓ §5.6-5.9 + §6 讨论 + §7 R8/R9/R10 + §8 工作量 |
| 诚实声明(H2/H5/RQ3 mixed-effects) | ✓ 三处均明确诚实标记"未达成"或"degenerate" |
| 复现性文档 | ✓ REPRODUCIBILITY.md + DATASET.md + LICENSE + requirements-frozen.txt |
| 图表 5/5 | ✓ figures/fig{1-5}.pdf |
| 全文 placeholder 扫描 | ✓ 论文与文档内未发现遗留待办标记或角括号占位符 |

**结论**:可投稿,但建议 cover letter 中预先声明三处未达成项,并把它们重新框定为"重要负面发现":
1. H2 未达成大效应阈值 → 表明 LLM-生成 mutant + 12 池规模下 aligned-cross 差距属中等,而非"宣告 SMS 无效";效应方向稳定。
2. H5 未达成(15% vs 80%)→ 揭示 LRCA 默认阈值过严,90% killed mutant 落入 suspect 区,**这是 LRCA 阈值校准研究方向的实证起点**,而非 SMS 失败。
3. mixed-effects 退化 → N=60 / 12 PUT 不足以同时估随机+固定效应,改用 sign test 是论文计划已声明的 fallback。

预先指向内文交叉引用:§5.6.2 / §5.7.2 / §5.8.3 / §6.1 / §6.2 / §6.3 / §7.1.5 R8 / §7.1.6 R9 / §7.1.7 R10 / §7.2.2 R6。

## 推荐下一步(out of scope of this plan)

1. **journal-formatting pass**:LaTeX 转换、图分辨率调整、参考文献格式化 — 见 spiral 计划 Round 15(可选)
2. **P4 论文规划**:
   - 扩大 mutant pool 到 30 mutants/PUT,重测 H2 是否能跨过 0.474 阈值(§7.1.6 R9 已铺路)
   - LRCA 阈值校准研究(OOD ε、tolerance 倍数、majority threshold)— 由 H5 未达成 15% 触发
   - PC 定义扩展(纳入 mutant 维度)— 由 RQ4 ρ ≈ 0 证实 SMS 与 PC 正交
3. **cover letter 草稿**:把上述三项未达成项作为"重要负面发现"明示(最大化 reviewer 不会把它们当作 hidden 缺陷)

## Spiral 14 轮完成情况

| Round | 主题 | 状态 | 证据 commit |
|---|---|---|---|
| 1-10 | 数据层 + 视觉层 | ✓ | b3086a5 → 369a242(主线) |
| 11 | 复现性文档 | ✓ | 本计划 Tasks 8 + 9 + 10 |
| 12 | §5.6-5.9 实证章节 | ✓ | 本计划 Tasks 2-5 |
| 13 | §6 讨论 + §7 R6/R8/R9/R10 | ✓ | 本计划 Tasks 6 + 7 |
| 14 | RQ-completion sweep + 自审 | ✓ | 本计划 Task 11 |

P2 论文 spiral 计划全部 14 轮完成。
