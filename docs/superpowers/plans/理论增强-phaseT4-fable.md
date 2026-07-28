# 理论增强-phaseT4-fable：PROP-IDF 可辨识性

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——短证明 + LRCA 重定位段起草，推理与行文并重）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0（符号闭集）与 §1.1/§1.2（本阶段负责 PROP-IDF；关闭 PO-IDF-1–2）。内容冲突以 master 为准。

**前置门禁:** Phase T2 完成（PROP-IDF 在 THM-GAP 假设下陈述，需 `research/theory_drafts/thm_gap.md` 已 internal-review）。

**并行性:** 可与 T5（fable）并行；CHECKPOINT T3 同时覆盖 T3 与 T4 的产出，拍板前确认 `理论增强-phaseT3-fable.md` 也已完成。

**交接物:** `research/theory_drafts/prop_identifiability.md`（状态 → internal-review）、CHECKPOINT T3 作者拍板记录 → 供 T6 整合。

---

## Task T4.1：起草与证明

**Files:** Create: `research/theory_drafts/prop_identifiability.md`

- [ ] **Step 1:** 写入（定稿基准，`[·]` 占位符在 Task T6.1 换成正文编号）：

```latex
\textbf{Proposition [PROP-IDF] (identifiability up to coverage classes).} Under the
assumptions of Theorem~[THM-GAP] let $\mathrm{sig}(m)=\{r\in R: r\ \text{kills}\ m\}$.
For any killed $m$, all members of $\mathrm{sig}(m)$ are checkers of the
same stratum, which identifies the fiber of $m$ exactly. For survivors,
fiber membership is identifiable only up to the partition of strata induced
by identical $R$-coverage; with a separating family (one exact checker per
stratum in $\mathrm{Cov}(R)$) the partition is trivial on $\mathrm{Cov}(R)$.
```

- [ ] **Step 2:** 证明（块对角矩阵直接推论）；写 LRCA 重定位段：现稿贡献声明 C2–C5 = 对块结构偏离（ξ 质量）的诊断标注器，引用替换 §2.4 的功能描述句
- [ ] **Step 3:** Commit

**REVIEW CHECKPOINT T3：作者确认 THM-WIN/PROP-IDF 假设清单与推论对既有 boundary cases 的覆盖（与 T3 联合拍板）。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| THM-GAP 前提在 T2 评审中被修订 | PROP-IDF 陈述随 THM-GAP 终稿同步更新（依赖其假设集），改动量小 |
