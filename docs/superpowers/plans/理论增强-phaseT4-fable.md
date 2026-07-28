# 理论增强-phaseT4-fable：REM-IDF 辨识性重读（THM-GAP 之 Remark，R-9 后的轻量阶段）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——Remark 表述 + LRCA 重定位段起草，推理与行文并重）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0（符号闭集）与 §1.1/§1.2（本阶段负责 REM-IDF；R-9 后无独立 PO，论证并入 THM-GAP 讨论段）。内容冲突以 master 为准。

**前置门禁:** Phase T2 完成（REM-IDF 在 THM-GAP 假设下陈述，需 `research/theory_drafts/thm_gap.md` 已 internal-review）。

**并行性:** 可与 T5（fable）并行；CHECKPOINT T3 同时覆盖 T3 与 T4 的产出，拍板前确认 `理论增强-phaseT3-fable.md` 也已完成。

**交接物:** `research/theory_drafts/rem_identifiability.md`（状态 → internal-review）、CHECKPOINT T3 作者拍板记录 → 供 T6 整合（并入 §2.11 THM-GAP 小节，不设独立小节）。

---

## Task T4.1：起草 Remark 与 LRCA 重定位段

**Files:** Create: `research/theory_drafts/rem_identifiability.md`

- [ ] **Step 1:** 写入（定稿基准；Remark 环境，无独立定理编号，`[·]` 占位符在 Task T6.1 换成正文编号）：

```latex
\textbf{Remark [REM-IDF] (identifiability up to coverage classes).} Under the
assumptions of Theorem~[THM-GAP] let $\mathrm{sig}(m)=\{r\in R: r\ \text{kills}\ m\}$.
For any killed $m$, all members of $\mathrm{sig}(m)$ are checkers of the
same stratum, which identifies the fiber of $m$ exactly. For survivors,
fiber membership is identifiable only up to the partition of strata induced
by identical $R$-coverage; with a separating family (one exact checker per
stratum in $\mathrm{Cov}(R)$) the partition is trivial on $\mathrm{Cov}(R)$.
```

- [ ] **Step 2:** 论证以两句话并入 THM-GAP 讨论段（同层性=块对角矩阵直接重读；覆盖等价类粒度=survivor 行恒零的观测不可分辨），**无独立 PO**（R-9；由 T6 审计项 (8) 一并复核）；写 LRCA 重定位段：现稿贡献声明 C2–C5 = 对块结构偏离（ξ 质量）的诊断标注器，引用替换 §2.4 的功能描述句
- [ ] **Step 3:** Commit

**REVIEW CHECKPOINT T3：作者确认 THM-WIN 假设清单、REM-FPOS/REM-FNEG/REM-IDF 的 Remark 表述与既有 boundary cases 的覆盖（与 T3 联合拍板）。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| THM-GAP 前提在 T2 评审中被修订 | REM-IDF 陈述随 THM-GAP 终稿同步更新（依赖其假设集），改动量小 |
