# 理论增强-phaseT6-terra：整合、一致性与独立审计

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `gpt-5.6-terra-max`（分派类别：**逻辑评审或审计**——对 fable 起草的全部证明作跨家族独立核对（整合即逐行重读）；LaTeX 整合与全文改名按 registry 执行；外部人工审计的协议与意见闭环由本阶段编排）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0 全部与 §1（含 §1.1 定理清单、§1.2 证明义务台账——本阶段核对 22/22 closed）。内容冲突以 master 为准。

**前置门禁:** T1–T5 全部完成且 CHECKPOINT T1/T2/T3 已过；五份草稿状态均为 internal-review。

**并行性:** Task T6.2 的审计等待窗口（≤2 周）内，论证提升计划 Phase 0–2 可并行推进。

**交接物:** main.tex 理论章节冻结版 + `docs/review_20260728/formal_audit_report.md`（AUDIT PASS 签署）+ "标签 → 正文编号"映射表 → CHECKPOINT T4 通过后通知论证提升计划可进入预注册冻结（其 Phase 1 门禁的审计级确认）。

---

## Task T6.1：草稿整合进正文

**Files:** Modify: main.tex（新增 §2.10 THM-INT、§2.11 THM-GAP、§2.12 PROP-IDF；§2.9 Prop 2→THM-WIN 原位升级；Appendix G 新增 G.6–G.9 完整证明；正文编号由 LaTeX 分配）

- [ ] **Step 1:** 按草稿逐节移植；`[标签]` 占位符替换为正文编号，并在 notation_registry 附"标签 → 正文编号"映射表；正文只放陈述+证明思路 ≤5 行，完整证明入 Appendix
- [ ] **Step 2:** 执行 master §0.4 决议的三处全文改名（按 Task T0.2 Step 5 的出现清单）：effect map \(\sigma\to\mathrm{eff}\)（含 \(\sigma^{-1}\to\mathrm{eff}^{-1}\)，§2.9 与 Appendix G 相关证明）；不变量族 \(I\to\Psi\)（§2.7 及其引用处）；\(D_S\to\mathcal D_P\)（§2.6）。改后复查：`rg -n "sigma\^\{-1\}|D_S" submission/TOSEM_regular_20260706/main.tex` 应为 0；改名单独成 commit 以便独立 revert
- [ ] **Step 3:** 更新 §1 claim-evidence map：新增四行（THM-INT、THM-GAP、THM-WIN、PROP-IDF → Supported (formal)）；更新 RQ1 表述为"健全性、单调性、退化与归因保证"
- [ ] **Step 4:** 交叉引用检查：`rg -n "Proposition 2" submission/TOSEM_regular_20260706/main.tex` 应为 0（已升级为 THM-WIN 编号并全文改引）
- [ ] **Step 5:** 编译两遍 + `grep -c "Missing character" main.log` 期望 0；Commit

## Task T6.2：独立形式审计

**Files:** Create: `docs/review_20260728/formal_audit_protocol.md`、`docs/review_20260728/formal_audit_report.md`

- [ ] **Step 1:** 写审计协议：审计人=未参与实证分析的合作者或外部同行；输入=五份草稿+main.tex §2；审计清单固定 8 项——(1) 每个定理前提在正文有定义，(2) 无循环（结论不作前提），(3) LEM-WIT 的 AVP 决定性假设成立范围，(4) THM-GAP 的 S5/exact-checker 前提与 ξ 报告一致，(5) THM-WIN 常数与 Lipschitz 假设可满足性，(6) THM-DEG-R 支撑假设与例外集表述，(7) 记号与 notation_registry（master §0.2 总表）零冲突，(8) 证明步骤逐行可复核
- [ ] **Step 2:** 审计执行（外部人工步骤，等待窗口 ≤2 周；期间可并行论证提升计划 Phase 0–2）。审计顺序要求：**优先审 THM-GAP**（清单第 4 项提前），使其尽早获得审计级确认——预注册包已依赖其内部评审版，THM-GAP 若出 blocker 需按预注册修订程序（amendment 记录）处理
- [ ] **Step 3:** 审计意见分级处理：blocker→回对应 Phase 修正后重审该项；minor→正文修订；全部关闭后在报告尾部签"AUDIT PASS + 日期 + 草稿 SHA256"（`shasum -a 256 research/theory_drafts/*.md`）
- [ ] **Step 4:** Commit

**REVIEW CHECKPOINT T4（终检）：审计报告全绿；作者确认理论章节冻结，通知论证提升计划可进入预注册冻结（其 Phase 1 门禁）。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| 审计超 2 周未回 | 启动第二审计人；两周为窗口非门槛，门槛是审计通过本身 |
| 跨阶段草稿（fable T1–T5）行文风格不一 | Step 1 移植时统一润色；语义不改，改动记录在 commit message |
