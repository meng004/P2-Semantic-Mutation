# 论证提升-phase0-grok：SSOT 冲突修复与数字管线

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `cursor-grok-4.5-high-fast`（分派类别：**执行**——脚本编写 + 数据复算 + 溯源，速度优先，判断点小而明确）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（符号与标识系统）与 §1.7（Phase 0 验收度量：SSOT 重生 diff=0、`check_ssot_consistency` exit 0、根因文档含两冲突值复算命令）。内容冲突以 master 为准。

**前置门禁:** 无（本阶段是论证线最先启动的阶段，与理论线 Phase T0 可同日并行）。

**并行性:** 与理论线全部阶段并行无冲突。

**交接物:** `docs/review_20260728/ssot_reconciliation.md`（根因与裁定值）、`scripts/check_ssot_consistency.py`（此后全部稿件数字改动的门禁）→ 供 Phase 1–5 与理论线 T1.2（区间演示读 SSOT）使用。

---

## Task 0.1：定位并复现冲突

- [ ] **Step 1:** 定位结果生成脚本与两个冲突数源：

```bash
rg -ln "0\.4392|0\.314" data/results/ submission/ scripts/ --glob "!*.pdf"
rg -ln "cliff|delta" scripts/ --glob "*.py" | head
```

- [ ] **Step 2:** 重跑结果脚本重生 `data/results/paper_numbers_v4.json`，`git diff data/results/paper_numbers_v4.json` 记录是否漂移
- [ ] **Step 3:** 追溯 0.314 的来源（脚本版本 / 数据切片 / 聚合口径），在 `docs/review_20260728/ssot_reconciliation.md` 写明根因与裁定值，两个数字各附计算命令

## Task 0.2：CI 式数字比对

**Files:** Create: `scripts/check_ssot_consistency.py`

- [ ] **Step 1:** 实现：从 main.tex 提取全部统计数字（正则匹配 `\d+\.\d{2,4}` 邻接关键词 delta/CI/p/mean），与 SSOT JSON 键值比对，不一致则非零退出并列出差异表
- [ ] **Step 2:** 验证：`python scripts/check_ssot_consistency.py submission/TOSEM_regular_20260706/main.tex data/results/paper_numbers_v4.json`，当前应报出 δ 冲突（若 20260706 稿沿用旧值）；修正 main.tex 后重跑，期望 exit 0
- [ ] **Step 3:** Commit：`fix(ssot): reconcile v4 cliff delta + add manuscript-SSOT consistency gate`

**REVIEW CHECKPOINT 0：作者确认裁定值与根因说明。此后任何稿件数字改动必须过 check_ssot_consistency。**

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| SSOT 重生出现 diff（脚本或数据漂移） | 停止裁定，先把漂移根因写进 ssot_reconciliation.md 交作者，不得静默取新值 |
| 0.314 溯源无果 | 如实记"来源不可复现"，裁定值取可复算侧（0.4392），稿面改动过 Task 0.2 门禁 |
