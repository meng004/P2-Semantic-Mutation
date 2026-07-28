# 理论增强-phaseT1-fable：THM-INT 区间健全性

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——证明起草与假设边界辨析）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0（符号闭集，禁止表外符号）与 §1.1/§1.2（本阶段负责 LEM-WIT、THM-INT；关闭 PO-INT-1–5）。内容冲突以 master 为准。

**前置门禁:** Phase T0 完成（`research/theory_drafts/notation_registry.md` 已 commit）。

**并行性:** 可与 T2/T3/T5（均 fable）并行；互不依赖。

**交接物:** `research/theory_drafts/thm_interval.md`（状态 → internal-review）、`data/results/interval_demo_v4.json`、CHECKPOINT T1 作者拍板记录 → 供 T6 整合。

---

## Task T1.1：起草引理与定理陈述

**Files:** Create: `research/theory_drafts/thm_interval.md`

- [ ] **Step 1:** 写入 LEM-WIT 与 THM-INT 陈述（下述 LaTeX 为定稿基准，`[·]` 占位符在 Task T6.1 换成正文编号；执行者可润色不可改语义）：

```latex
\textbf{Lemma [LEM-WIT] (kill witness upgrade).} Assume the AVP verdict is a
deterministic function of the $\mathrm{obs}$-observed outputs of the executions
in an MR tuple. If $\mathrm{killed}(P',\mathrm{MR}_{i,k})$ holds, then some
execution input $x$ satisfies
$\|\mathrm{obs}(\Phi_{P}(x))-\mathrm{obs}(\Phi_{P'}(x))\|>\varepsilon_{\mathrm{eq}}$,
hence $P'$ is CONFIRMED\_NON\_EQUIVALENT. Consequently the unresolved set
contains no killed mutants.

\textbf{Theorem [THM-INT] (interval soundness and monotonicity).} Let $n$ be the
number of confirmed non-equivalent mutants, $k$ the number killed by $R$,
and $u$ the number of unresolved survivors. Let $u_{\mathrm{neq}}\in[0,u]$ be the
(unknown) number of truly non-equivalent mutants among the unresolved.
Then the ground-truth score $k/(n+u_{\mathrm{neq}})$ satisfies
\[ \mathrm{SMS}_{\mathrm{cons}}=\tfrac{k}{n+u}\;\le\;\tfrac{k}{n+u_{\mathrm{neq}}}\;\le\;\tfrac{k}{n}=\mathrm{SMS}_{\mathrm{strict}}, \]
with width $\mathrm{SMS}_{\mathrm{strict}}\cdot\tfrac{u}{n+u}$. Each
equivalence certificate ($u\!\to\!u\!-\!1$) or divergence witness
($u\!\to\!u\!-\!1$, $n\!\to\!n\!+\!1$) weakly narrows the interval; and for
$R\subseteq R'$ both endpoints are non-decreasing.
```

- [ ] **Step 2:** 写证明（要点：宽度 \(k/n-k/(n+u)=k u/(n(n+u))\)；MR 扩张时 \((k+\Delta+j)/(n+j)\ge k/n\) 因 \(k\le n\)；证书两类分别验证两端点变化方向）
- [ ] **Step 3:** 自检清单：AVP 决定性假设是否已在 §2.3 有依据；随机 PUT 的 AVP 重复语义（N=20）是否破坏 LEM-WIT（若 kill 判定含统计聚合，需把"超容差"改为"按 AVP 判定语义超容差"并加脚注）。逐项在草稿"Obligations"节记录
- [ ] **Step 4:** Commit

## Task T1.2：区间演示计算（现有数据，development 身份）

**Files:** Create: `scripts/theory/interval_demo.py`；Output: `data/results/interval_demo_v4.json`

- [ ] **Step 1:** 从 v4 prescreen 台账统计每 mp-cell 的 (n, k, u)：u 取"仅由 K_eq 抽样判等、无 AST/证书"的候选数（输入=prescreen 计数台账，与论证线 Phase 0 的 δ 冲突正交，无需等其 CHECKPOINT 0，F-13）。数据源定位：`rg -l "equiv" data/ --glob "*v4*"`
- [ ] **Step 2:** 输出每 mp-cell（v4 遗产划分 12 PUT × 5 MP，F-8）与总体的 [SMS_cons, SMS_strict] 及宽度分布；写入 JSON（键名 `mp_cells`；新键，不改旧键）
- [ ] **Step 3:** 验证：`python scripts/theory/interval_demo.py && python -c "import json;d=json.load(open('data/results/interval_demo_v4.json'));print(len(d['mp_cells']))"` 期望 60（mp-cell 口径，F-8）
- [ ] **Step 4:** Commit（此结果只作 §2.10 演示图，标注 development-only）

**REVIEW CHECKPOINT T1：作者确认 THM-INT 陈述、假设与演示口径。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| LEM-WIT 在随机 PUT 的 AVP 聚合语义下不成立 | 把引理限定到确定性判定语义，随机情形降为"在 AVP 判定语义下的条件版本"，THM-INT 主体不受影响 |
