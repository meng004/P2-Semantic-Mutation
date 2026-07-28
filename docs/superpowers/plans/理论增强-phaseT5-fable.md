# 理论增强-phaseT5-fable：退化定理修补（THM-DEG-R）与三态等价集成

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——测度论表述改写与退化前提修补，需与 T1–T4 新定理群同一推理口径）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0（符号闭集——本阶段涉及 \(L=L_{\mathrm{lim}}\wedge L_{\mathrm{switch}}\)（#31）、\(\mathcal D_P\)（#5）、\(K_{\mathrm{eq}}/\varepsilon_{\mathrm{AVP}}\)（#8/#13））与 §1.2（关闭 PO-DEG-1–3）。内容冲突以 master 为准。

**前置门禁:** Phase T0 完成（Task T5.2 依赖 T0.2 Step 4 的三态等价登记结论）。

**并行性:** 可与 T1/T2/T3/T4 并行（本阶段直接修改 main.tex §2.3/§2.5/§2.6，不触碰新定理草稿目录；T6.1 整合新定理时以本阶段修改后的 main.tex 为基）。

**交接物:** main.tex §2.6 修补版（THM-DEG-R 三项闭合）+ §2.3/§2.5 三态等价声明 + 编译验证记录 → 供 T6 整合与审计项 (6)。

---

## Task T5.1：修补退化定理

**Files:** Modify: `submission/TOSEM_regular_20260706/main.tex:688-739`（§2.6）、Appendix G 对应节

- [ ] **Step 1:** L 拆分：\(L=L_{\mathrm{lim}}\wedge L_{\mathrm{switch}}\)，\(L_{\mathrm{lim}}=(\varepsilon_{\mathrm{eq}}\to0)\wedge(K_{\mathrm{eq}}\to\infty)\wedge(\varepsilon_{\mathrm{AVP}}\to0)\)，\(L_{\mathrm{switch}}=\)（MP 集置换 ∧ 算子切换 ∧ PUT 类限制）；定理陈述改为"在 \(L_{\mathrm{switch}}\) 固定下沿 \(L_{\mathrm{lim}}\) 取极限"
- [ ] **Step 2:** Lemma 9.1 增加显式假设："\(\mathcal D_P\)（原稿 \(D_S\)，随程序记号统一改名）的支撑覆盖 \(\mathcal X_{\mathrm{adm}}\)"；无此假设时给反例注记（一行）
- [ ] **Step 3:** "almost everywhere" 改为二选一表述（浮点域有限例外集 / 连续化模型下测度零），Appendix G.3 同步
- [ ] **Step 4:** 编译验证：`cd submission/TOSEM_regular_20260706 && pdflatex -interaction=nonstopmode main.tex | tail -3`，期望无 error
- [ ] **Step 5:** Commit

## Task T5.2：三态等价状态集成（依 Task T0.2 Step 4 的登记）

**Files:** Modify: main.tex §2.3（E1∧E2 节）、§2.5

- [ ] **Step 1:** §2.3 增加三态声明：CERTIFIED_EQUIVALENT（仅证书）/ CONFIRMED_NON_EQUIVALENT（分歧见证）/ EQUIVALENCE_UNRESOLVED（E1∧E2 样本一致但无证书）；现 60-cell 的 E1∧E2 判等在新口径下=unresolved，旧 SMS = SMS_strict
- [ ] **Step 2:** §2.5 向后兼容声明补一句：三态在退化极限下坍缩回经典二态（与 Lemma 9.1 一致）
- [ ] **Step 3:** 编译验证 + Commit

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| §2.6 行号区间与实际稿面漂移 | 以 `rg -n "degenerate|Lemma 9.1" main.tex` 重定位后再改；不按行号盲改 |
| 与 T6.1 的 \(D_S\to\mathcal D_P\) 全文改名撞车 | 本阶段只改 §2.6 内出现；全文扫尾归 T6.1 Step 2，两处 commit 分开 |
