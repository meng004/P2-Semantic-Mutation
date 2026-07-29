# 理论增强-phaseT6-terra：整合、一致性与独立审计

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `gpt-5.6-terra-max`（分派类别：**逻辑评审或审计**——对 fable 起草的全部证明作跨家族独立核对（整合即逐行重读）；LaTeX 整合与全文改名按 registry 执行；外部人工审计的协议与意见闭环由本阶段编排）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0 全部与 §1（含 §1.1 定理清单、§1.2 证明义务台账——本阶段核对 20/20 closed，R-9 后 PO-IDF-1..2 已撤销）。内容冲突以 master 为准。

**前置门禁:** T1–T5 全部完成且 CHECKPOINT T1/T2/T3 已过；五份草稿状态均为 internal-review。

**并行性:** Task T6.2 的审计等待窗口（≤2 周）内，论证提升计划 Phase 0–2 可并行推进。

**交接物:** main.tex 理论章节冻结版 + `docs/review_20260728/formal_audit_report.md`（AUDIT PASS 签署）+ "标签 → 正文编号"映射表 → CHECKPOINT T4 通过后通知论证提升计划：理论章节冻结（写作期引用基线）。**预注册冻结门禁唯一 = CHECKPOINT T2（R-5）**；本阶段审计 blocker 走预注册 amendment 程序（载体=论证计划 `research/prereg_v2/AMENDMENTS.md`，F-7），不回溯撤销冻结。

---

## Task T6.1：草稿整合进正文

**Files:** Modify: main.tex（新增 §2.10 THM-INT、§2.11 THM-GAP（含 REM-IDF Remark，R-9 不设独立小节）；§2.9 Prop 2→THM-WIN 原位升级（含 REM-FPOS/REM-FNEG）；Appendix G 新增 G.6–G.8 完整证明；正文编号由 LaTeX 分配）

- [x] **Step 1:** 按草稿逐节移植；`[标签]` 占位符替换为正文编号（THM-WIN→Theorem 3（§2.9 原位替换 Prop 2）、LEM-WIT/THM-INT→Lemma 4.1/Theorem 4（新 §2.10）、LEM-CLO/THM-GAP/COR-ZERO/REM-IDF→Lemma 5.1/Theorem 5/Corollary 5.1/unnumbered Remark（新 §2.11）、三个 Remark 均不占独立编号），notation_registry 已附"标签 → 正文编号"映射表；正文只放陈述+证明思路 ≤5 行，完整证明入 Appendix G.6–G.8（另设 G.5 审计小节）；C3 裁决的计数符号 local-scope 句、T3-Q3 严格超出约定、S5→ξ 注记、LRCA §2.4 替换句、Ψ 非冗余（§2.7 引入处）一并落稿
- [x] **Step 2:** 执行 master §0.4 决议的五处全文改名：effect map \(\sigma\to\mathrm{eff}\)（含 \(\sigma^{-1}\)）；不变量族 \(I\to\Psi\)；\(D_S\to\mathcal D_P\)（全文扫尾，含 §2.3/程序节/LRCA 节与 supplementary A.1/A.2，scoped NOTE 注释移除）；\(\alpha\to\mathrm{obs}\)、\(\equiv_\alpha\to\equiv_{\mathrm{obs}}\)（§2.7–2.9 + 未来工作段）；\(e,P_e\to\mathrm{edit},P_{\mathrm{edit}}\)。逐处审计保留：MLP 超参 \(\alpha\)（main:2343）、\(\sigma_{\mathrm{out}}\)、Wilcoxon α=0.05 / \(\alpha_{\mathrm{FDR}}\)（supplementary A.3/D）、附录 H 复数标量 α。复查全零（\(\sigma^{-1}\)、语义 \(\equiv_\alpha\)/\(\alpha\circ\)/through α、P_e、= e(P)、D_S 均 0）；改名单独成 commit（`3043f49`）
- [x] **Step 3:** 更新 §1 claim-evidence map：新增三行（Theorem 3 检测窗、Theorem 4 区间健全、Theorem 5 缺口归因 → Supported (formal)）；RQ1 标题与正文改述为"soundness, monotonicity, degeneration, and attribution guarantees"并补 (d) 子问；正文符号最小化：只保留证明链上符号，§0.2 全表以"Theory-extension symbols"块导出至 supplementary A.1（R-12）
- [x] **Step 4:** 交叉引用检查：`grep -c "Proposition 2"` main/supplementary 均为 0（§1 roadmap、RQ1、RQ4、§4.8 ×3 全部改引 Theorem 3 或其 Remark）
- [x] **Step 5:** 编译两遍（main+supplementary）：各仅 1 个 pre-existing `\Bbbk` preamble 错误（与基线同环境一致，非本次引入）；`Missing character` = 0；归档 PDF 恢复未动；Commit

## Task T6.2：独立形式审计

**Files:** Create: `docs/review_20260728/formal_audit_protocol.md`、`docs/review_20260728/formal_audit_report.md`

- [x] **Step 1:** 写审计协议（`formal_audit_protocol.md`）：审计人=跨家族独立模型（gpt 系 `gpt-5.6-sol-xhigh`，未参与 T1–T5 起草；外部人类同行复审可追加）；输入=五份草稿+整合稿 main.tex §2+supplementary G；固定 8 项清单全文落稿；THM-GAP 优先次序写入
- [x] **Step 2:** 审计执行（3 轮）：Round 1 全量审计返回 **AUDIT BLOCKED**（6 blocker + 3 minor，含两项既有稿件老缺口 B4/B5：L4 允许 r≠id、Lemma 9.1 借用未假设的 L6 且误称 E1）；THM-GAP 项（B1）最先裁定。THM-GAP 的 blocker 为 ξ 统计量定义卫生（NA 约定 + 单侧性），不触及 Theorem 5 结论与预注册预测通道（H-ZERO/H-DISC/H-XI 判读不变），经审计人确认无需预注册 amendment
- [x] **Step 3:** 分级处置：修订 A4（THM-WIN 承重假设入陈述 + P⋆ 锚定）、A5（REM-FPOS 分层化，终稿单遍论证）、A6（THM-INT n≥1）；修复 D 组（ξ NA+单侧、SMS(R) 定义、kill 矩阵 incidence、L4 强制 r=id、Lemma 9.1 前提/证明重写、L_r 可估性句、registry #37–40）。Round 2 复核余 B1/B3 残句，Round 3 终验 **AUDIT PASS**。报告含 9 项处置表 + 修复类别核对（全部效度修复，无主张收缩）+ SHA256 签署：`docs/review_20260728/formal_audit_report.md`
- [x] **Step 4:** Commit（`7faf32f` → `4a27604` → `57c5717` → 报告+G.5 结果句 commit）

**REVIEW CHECKPOINT T4（终检）：✅ PASS（2026-07-29）。审计报告全绿（8/8 项，9/9 发现闭合）；理论章节冻结为写作期引用基线（Theorem 3/4/5 + Lemma 4.1/5.1 + Corollary 5.1 + 三 Remark + Theorem 9.1(修) + Corollary 9.1，编号与标签映射见 notation_registry）；论证提升计划自此按冻结基线引用理论章节。T4 审计的全部 blocker 已当轮闭合，无需动用预注册 amendment 程序（CHECKPOINT T2 的冻结不受影响）。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| 审计超 2 周未回 | 启动第二审计人；两周为窗口非门槛，门槛是审计通过本身 |
| 跨阶段草稿（fable T1–T5）行文风格不一 | Step 1 移植时统一润色；语义不改，改动记录在 commit message |
