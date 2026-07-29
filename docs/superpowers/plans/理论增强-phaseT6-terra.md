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

- [ ] **Step 1:** 写审计协议：审计人=未参与实证分析的合作者或外部同行；输入=五份草稿+main.tex §2；审计清单固定 8 项——(1) 每个定理前提在正文有定义，(2) 无循环（结论不作前提），(3) LEM-WIT 的 AVP 决定性假设成立范围，(4) THM-GAP 的 S5/exact-checker 前提与 ξ 报告一致，(5) THM-WIN 常数与 Lipschitz 假设可满足性，(6) THM-DEG-R 支撑假设与例外集表述，(7) 记号与 notation_registry（master §0.2 总表）零冲突，(8) 证明步骤逐行可复核
- [ ] **Step 2:** 审计执行（外部人工步骤，等待窗口 ≤2 周；期间可并行论证提升计划 Phase 0–2）。审计顺序要求：**优先审 THM-GAP**（清单第 4 项提前），使其尽早获得审计级确认——预注册包已依赖其内部评审版，THM-GAP 若出 blocker 需按预注册修订程序（amendment 记录，载体=论证计划 `research/prereg_v2/AMENDMENTS.md`，F-7）处理
- [ ] **Step 3:** 审计意见分级处理：blocker→回对应 Phase 修正后重审该项；minor→正文修订；全部关闭后在报告尾部签"AUDIT PASS + 日期 + 草稿 SHA256"（`shasum -a 256 research/theory_drafts/*.md`）
- [ ] **Step 4:** Commit

**REVIEW CHECKPOINT T4（终检）：审计报告全绿；作者确认理论章节冻结（写作期引用基线），通知论证提升计划。预注册冻结门禁唯一 = CHECKPOINT T2（THM-GAP 内部评审，R-5），T4 不重复充当冻结门禁；T4 审计若出 blocker，按预注册 amendment 程序（载体=论证计划 `research/prereg_v2/AMENDMENTS.md`，修订记录 + 正文披露，F-7）处理，不回溯撤销已生效的冻结。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| 审计超 2 周未回 | 启动第二审计人；两周为窗口非门槛，门槛是审计通过本身 |
| 跨阶段草稿（fable T1–T5）行文风格不一 | Step 1 移植时统一润色；语义不改，改动记录在 commit message |
