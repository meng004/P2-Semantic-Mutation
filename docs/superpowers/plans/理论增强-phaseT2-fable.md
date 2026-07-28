# 理论增强-phaseT2-fable：THM-GAP 缺口归因（核心，跨计划门禁所在）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——全计划最核心定理，其内部评审是论证提升计划 Phase 1 冻结的门禁）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0（符号闭集）与 §1.1/§1.2（本阶段负责 LEM-CLO、THM-GAP、COR-ZERO；关闭 PO-GAP-1–6）。内容冲突以 master 为准。

**前置门禁:** Phase T0 完成（notation_registry 已 commit）。

**并行性:** 可与 T1/T3/T5（均 fable）并行。THM-GAP 前提 (iii) 引用 THM-WIN 的窗口陈述：T3 未完成时按 master §1.1 的 THM-WIN 陈述占位引用（`Theorem~[THM-WIN]`），不需其证明完成。

**交接物:** `research/theory_drafts/thm_gap.md`（状态 → internal-review）、CHECKPOINT T2 作者拍板记录 → **此拍板是论证提升计划 Phase 1 Task 1.3（假设与分析代码冻结）的启动条件**，完成后立即通知论证线。

---

## Task T2.1：起草陈述与推论

**Files:** Create: `research/theory_drafts/thm_gap.md`

- [ ] **Step 1:** 写入定义与定理（定稿基准）：

```latex
\textbf{Definition (exact checker).} $r$ is an exact checker for stratum
$\psi_j$ if its violation predicate flags $P'$ iff
$[\![P']\!]\not\models_{\tau}\psi_j$ within the tolerance regime of
Theorem~[THM-WIN]. $\mathrm{Cov}(R)=\{j: R$ contains an exact checker for $\psi_j\}$.

\textbf{Theorem [THM-GAP] (block structure and gap attribution).} Assume (i)
stratum purity S5 for all $m\in M_{\mathrm{neq}}$, (ii) every $r\in R$ is
an exact checker for some stratum, (iii) non-degenerate tolerance margins
(Theorem~[THM-WIN]). Then no $m$ in fiber $M_j$ with $j\notin \mathrm{Cov}(R)$
is killed, the fiber-by-stratum kill matrix is block-diagonal, and
\[ 1-\mathrm{SMS}(R)=\underbrace{\textstyle\sum_{j\notin \mathrm{Cov}(R)} w_j}_{\mathrm{Gap}_{\mathrm{aln}}(R)\ \text{(alignment gap)}}
 +\underbrace{\textstyle\sum_{j\in \mathrm{Cov}(R)} w_j\,(1-\mathrm{SMS}_j(R))}_{\mathrm{Gap}_{\mathrm{str}}(R)\ \text{(strength gap)}},
 \qquad w_j=\tfrac{|M_j|}{|M_{\mathrm{neq}}|}, \]
both computable from the kill matrix and fiber labels alone.

\textbf{Corollary [COR-ZERO] (cross-zero prediction).} If
$\mathrm{Cov}(R)\cap\{j:w_j>0\}=\varnothing$ then $\mathrm{SMS}(R)=0$.

\textbf{Definition (exactness defect).} $\xi(R)=$ block-off-diagonal kill
mass / total kills; $\xi$ measures deviation from (i)-(ii) and is reported
as a model-check statistic, not folded into SMS.
```

- [ ] **Step 2:** 写证明（要点：\(m\in M_j, j\notin \mathrm{Cov}(R)\)；任取 \(r\) 为 \(\psi_l\) 的 exact checker，\(l\ne j\)；S5 纯性给 \([\![m]\!]\models\psi_l\)，故 r 不 flag m；r 在原程序上 pass；killed 需存在 flag → 无。分解式由块对角直接展开）
- [ ] **Step 3:** 写接口注记（一段）：\(\mathrm{Gap}_{\mathrm{aln}}(R)\) 对应四柱 T3 的选择残余 \(\Omega_{\mathrm{sel}}\)（加对齐 MR 可消除），\(\mathrm{Gap}_{\mathrm{str}}(R)\) 是声明层内检测力缺口；注明"四柱之采纳集 \(S\) ≙ 本文 \(R\)"；引用四柱框架为 companion technical report，不承重
- [ ] **Step 4:** 写"经验含义"小节：cross/非对齐 MR 的 SMS 预测为 0 ⟹ 60-cell 零膨胀中 cross cell 的零质量属理论预测；为论证提升计划的 H-ZERO/H-DISC 提供推导来源（明确引用行）
- [ ] **Step 5:** Commit

## Task T2.2：现稿一致性核对

- [ ] **Step 1:** 核对现稿 Thm 2（THM-DUAL）的 strong MR 定义（violation set 对 ≡_α 封闭）与 exact checker 的关系：exact checker ⊂ strong MR；在草稿中写 LEM-CLO 链接两者（exact checker 的 violation set = \(\{P':\not\models_\tau\psi_j\}\)，对 ≡_α 封闭因 \(\models_\tau\) 经 α 定义）
- [ ] **Step 2:** 核对 S5 在 §2.8 的表述（"required where stratum labels feed downstream"）——THM-GAP 把 S5 从可选升为前提，需在正文注明"S5 不满足的变异体计入 ξ 偏差质量"
- [ ] **Step 3:** Commit

**REVIEW CHECKPOINT T2：作者确认 THM-GAP 前提强度（S5+exact checker 是否过强）与 ξ 的报告方式。此检查点通过后，论证提升计划 Phase 1 方可启动（通知 `论证提升-phase1-fable.md` 的执行者）。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| THM-GAP 前提被评审/审计判定过强 | 保留定理，增加"偏差质量 ξ 的经验上界"作为适用性检验；H-ZERO 判据改用 ξ 校正后的预测 |
| T3 的 THM-WIN 陈述后续有语义变化 | 本阶段引用为占位标签；T6.1 整合时统一核对（iii) 前提的表述与 THM-WIN 终稿一致 |
