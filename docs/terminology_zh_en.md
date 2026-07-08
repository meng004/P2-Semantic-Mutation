# P2 Terminology — Chinese ↔ English

> Authoritative term mapping for the R-1 full-paper translation. Used by
> `scripts/translate_paper.py` as a prompt-cached glossary. Update this
> file BEFORE rerunning translation; never edit `论文初稿P2_EN.md` directly
> for terminology changes.

## A. Core MT / mutation testing concepts

| Chinese | English | Notes |
|---|---|---|
| 蜕变测试 | metamorphic testing (MT) | |
| 蜕变关系 | metamorphic relation (MR) | |
| 元模式 | meta pattern (MP) | |
| 变异测试 | mutation testing | |
| 变异算子 | mutation operator | |
| 语义效应故障 | semantic-effect fault | preferred reader-facing term; do not use CE/OS/HP/TF/SI as concept names |
| MR 元模式 | MR MetaPattern (MP) | NOETHER-aligned term |
| 算子块 | operator block | NOETHER structural source of an MP |
| 变异体 | mutant | |
| 等价变异体 | equivalent mutant | |
| 等价检测 | equivalence detection | |
| 测试充分性 | test adequacy | |
| 充分性度量 | adequacy metric | |
| 杀死(变异体) | kill (a mutant) | |
| 存活(变异体) | survive | |
| 高阶变异 | higher-order mutation (HOM) | R-9 caveat |
| 一阶语法变异工具 | first-order syntactic mutation tools | R-9 |

## B. P2-specific symbols and metrics

| Chinese | English | Notes |
|---|---|---|
| 语义变异得分 | Semantic Mutation Score (SMS) | core P2 contribution |
| 自动验证管线 | Automated Verification Pipeline (AVP) | |
| 三态分解 | three-state decomposition | killed / equiv / survive |
| 似然根因清单 | likely root cause inventory | C1..C5 |
| C1 share / suspect share | C1 share / suspect share | keep English literals |
| 对齐(单元格) | aligned (cell) | j = k |
| 跨(单元格) | cross (cell) | j ≠ k |
| 跨源 | cross-source | LLM diversity (Claude+GPT-5.4+DeepSeek) |
| 模式覆盖 | pattern coverage (PC) | RQ4 |
| 算子-程序实例化矩阵 | operator-program instantiation matrix | 60 cells |
| 单元格 | cell | (PUT, MP) pair |
| 被测程序 | program under test (PUT) | |

## B1. NOETHER-aligned MR MetaPatterns

| Chinese | English | Notes |
|---|---|---|
| 不变性 / 等变性元模式 | invariance / equivariance MetaPattern (`m_inv`, `inv`) | from the `G` symmetry block; conservation is an instance of this block |
| 单调 / 次序元模式 | monotonicity / order MetaPattern (`m_mono`, `mono`) | from the `O_le` order block |
| 收敛 / 极限元模式 | convergence / limit MetaPattern (`m_conv`, `conv`) | from the `L_lim` limit block |
| 定性动力学元模式 | qualitative-dynamics MetaPattern (`m_dyn`, `dyn`) | from the `D_dyn` block; use for trajectory-shape MRs |
| 方法比较元模式 | method-comparison MetaPattern (`m_cmp`, `cmp`) | from the `E_cmp` block; use for partial-order / no-worse-than MRs |
| 伴随互易元模式 | self-adjoint / adjoint-reciprocity MetaPattern (`m_adj`, `adj`) | from the `T_adj` self-adjoint block |
| 时间反演元模式 | time-reversal MetaPattern (`m_rev`, `rev`) | from the `T_rev` time-reversal block; not a synonym for general trajectory |
| 关系等价元模式 | relational-equivalence MetaPattern (`m_rel`, `rel`) | from the `B_rel` relational-equivalence block |

## C. Paper-stage / methodology

| Chinese | English | Notes |
|---|---|---|
| 实证审计 | empirical audit | |
| 主用 / 探索性 | primary / exploratory | for v3/v3b distinction |
| 数据驱动 c 类主元模式 | data-driven c-class primary MP | §3.5.1 |
| 选择对应答偏倚 | selection-on-response | §3.5.1 caveat |
| 多重比较 | multiple comparisons | |
| 三方双盲审核 | three-party double-blind review | LLM-LLM-LLM pipeline |
| 仲裁 | arbitration | DeepSeek role |
| LLM 多样性 | LLM source diversity | paper title |
| 预防性防御 | preventive defense | §3.2.6 |
| 语法编辑 vs 语义效应故障 | syntactic edits vs semantic-effect faults | avoids treating semantic mutation as a syntactic-operator subclass |

## D. Hypotheses & RQs (NEVER translate IDs themselves)

| Chinese | English | Notes |
|---|---|---|
| 研究问题 RQ1-RQ4 | research question RQ1-RQ4 | keep IDs untranslated |
| 假设 H1-H5 | hypothesis H1-H5 | keep IDs untranslated |
| H3 已撤回 | H3 retired | §1.5 |
| 假设达成/未达成 | hypothesis met / not met | |
| 已锁定决定 | locked decision (D1-D8, W-2) | keep IDs untranslated |
| 风险 R6/R8/R9/R10 | risk R6/R8/R9/R10 | §7 risks |

## E. Statistics

| Chinese | English | Notes |
|---|---|---|
| 效应量 / 大效应阈值 | effect size / large-effect threshold | |
| Cliff's δ | Cliff's δ | keep symbol |
| 符号检验 | sign test | |
| Friedman 检验 | Friedman test | |
| 混合效应模型 | mixed-effects model | |
| 主模型奇异 | primary model singular | RQ3 caveat |
| 退化为边界 | degenerate / boundary | RQ3 |
| 自助 / Bootstrap 置信区间 | bootstrap confidence interval | R-12/13 |
| logit 变换 | logit transform | R-22 |
| 秩不变 / 单调不变 | rank-invariant / monotone-invariant | R-22 theorem |
| 零质量主导 | zero-mass dominance | §5.6.1.1 (R-18) |

## F. Phrases that must NOT be literal-translated

| Chinese phrase | Preferred English rendering |
|---|---|
| 三支柱框架 | three-pillar framework (NOT "three-support framework") |
| 双根本原则 | dual fundamental principles |
| 锁定 (符号系统) | "fixed" (preferred) or "frozen"; NOT "locked" |
| 命题 | claim or thesis (context-dependent), NOT "proposition" unless mathematical |
| 立场 | position (academic stance), NOT "standpoint" |
| 共识 | consensus, NOT "common knowledge" |
| 边界 (理论边界) | scope, NOT "boundary" unless mathematical |

## G. Citation style for the EN version

- Use APA-7 in-text: `(Author, YEAR)`; in the EN paper convert all `(作者, YEAR)` accordingly.
- Multi-author: `(Smith & Jones, 2024)` for two authors; `(Smith et al., 2024)` for 3+.
- DOI links: keep as-is, do not Anglicize URL.

## H. Numbers and units

- Decimal point in EN: `0.275`, `15.30`, never `0,275`.
- 60-cell matrix: `60-cell matrix`, NOT `60-cell matrices`.
- "n=12 PUTs" not "12 PUTs (n=12)".
- Significance: `p = 0.0041` (italics on p in LaTeX; in markdown plain).

## I. Don't-translate list

- All filenames: `论文初稿P2.md`, `paper_numbers_v4.json`, etc.
- Code identifiers: `PRIMARY_CELLS`, `SMS_VERSION`, `AVP`, `LRCA`.
- Greek letters: keep `δ`, `χ²`, `ε`, `ρ`, `τ` literal in markdown.
- Reference list entries when already in English-language venues.
