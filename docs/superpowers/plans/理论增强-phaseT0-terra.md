# 理论增强-phaseT0-terra：符号系统与基线冻结

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪。
> **执行模型:** `gpt-5.6-terra-max`（分派类别：**逻辑评审或审计**——跨文档符号逐项核对是审计作业；跨家族视角独立于后续起草证明的 fable）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0 全部（0.1 命名规约、0.2 符号总表、0.3 定义与方法学假设清单、0.4 冲突消解表、0.5 标签映射）。内容冲突以 master 为准，修订先改 master 再同步本文件。

**前置门禁:** 无（本阶段是理论线全部后续阶段的前置）。

**并行性:** 本阶段完成并 commit 后，T1/T2/T3/T5（均 fable）方可启动。

**交接物:** `research/theory_drafts/README.md`（工作区索引）、`research/theory_drafts/notation_registry.md`（含 §0.2 总表落地 + 现稿出现行号 + 待改名清单）→ 供 T1–T6 全部阶段作符号闭集依据。

---

## Task T0.1：建立理论草稿工作区

**Files:** Create: `research/theory_drafts/README.md`

- [x] **Step 1:** 创建目录与索引文件，索引列出五个草稿文件名与状态列（draft / internal-review / audited / integrated）
- [x] **Step 2:** `git add research/theory_drafts/ && git commit -m "theory(v2): open theory draft workspace"`

## Task T0.2：记号审计与冻结

**Files:** Create: `research/theory_drafts/notation_registry.md`

- [x] **Step 1:** 提取现稿全部理论符号及首次定义位置（现以已追踪的 `submission/TOSEM_regular_20260706/main.tex` 为审计源；指纹与行号见 registry）：

```bash
rg -n "\\\\equiv_|varepsilon_|mathrm\{SMS\}|K_\{?\\\\mathrm\{eq\}|M_\{\\\\mathrm\{neq\}|sigma\^\{-1\}|psi_" submission/TOSEM_regular_20260706/main.tex | head -60
```

- [x] **Step 2:** 在 `notation_registry.md` 落地 master §0.2 符号总表（序号、符号、含义、首定义/来源、备注五列一对一照搬），并加"现稿出现行号"列。新增符号闭集 = §0.2 的 #17–#32 中标注 DEF/THM 来源者；任何草稿引入表外符号即违规，先补表再用
- [ ] **Step 3:** 定位《MT基础理论统一框架》v1.2 附录 A（OneDrive `0-论文/MR识别/theory/` 目录），对 registry 逐符号 diff；重点核对保留符号 \(\sigma,\Gamma,\mathfrak G,\lambda,S,I,\rho,e,\kappa\) 未被 P3 新文本挪用。附录 A 不可达时以四柱 v1.2 §2 + v3.1 §3 为代理权威并在 registry 头部注明
  - 当前状态：已按用户给定定位器查询 `meng004/mr-theory`，但 GitHub API 与 `git ls-remote` 均返回 `Repository not found`；附录 A、四柱 v1.2 §2、MR-validity v3.1 §3 因而仍未取得。registry 已记录本地冲突审计与该外部证据缺口；不能把它误报为完成的逐符号外部 diff。
- [x] **Step 4:** 检查现稿是否已有 `SMS_strict / SMS_conservative` 与 `EQUIVALENCE_UNRESOLVED` 词汇（`rg -n "strict|conservative|UNRESOLVED" submission/TOSEM_regular_20260706/main.tex`）。若无：登记"需在 §2.3 引入三态等价（certified-equivalent / confirmed-non-equivalent / unresolved），把现 E1∧E2 样本等价降格为 unresolved 的证据"这一集成任务到 Task T5.2（`理论增强-phaseT5-fable.md`）
- [x] **Step 5:** 盘点现稿待改名符号的出现范围：`rg -c "sigma\^\{-1\}|\\\\sigma\\b" submission/TOSEM_regular_20260706/main.tex`（effect map σ→\(\mathrm{eff}\)）与 `rg -n "invariant family|I = \\\\\{|\\\\mathcal\{?I\}?" submission/TOSEM_regular_20260706/main.tex`（不变量族 I→\(\Psi\)）与 `rg -n "D_S" submission/TOSEM_regular_20260706/main.tex`（\(D_S\to\mathcal D_P\)），把出现清单写入 registry 附录，改名动作归 Task T6.1（`理论增强-phaseT6-terra.md`）
- [x] **Step 6:** Commit

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| 统一框架 v1.2 附录 A 找不到 | 按 Step 3 降级：四柱 v1.2 §2 + v3.1 §3 为代理权威，registry 头部注明；不阻塞后续阶段 |
| 现稿符号盘点遗漏 | T6.1 改名前会二次 rg 复查；本阶段清单标注"初版" |
