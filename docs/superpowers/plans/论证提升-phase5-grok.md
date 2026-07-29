# 论证提升-phase5-grok：投稿前流水线（CLAUDE.md §3 五步）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪。
> **执行模型:** `cursor-grok-4.5-high-fast`（分派类别：**执行**——引文逐条核验（paper-search MCP 批量调用）、构建门禁、打包等工具驱动步骤为主，速度优先；humanizer/proofread 按既有 skill 规则执行，不做开放式改写）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §1.7（Phase 5 验收：引文审计 ✗=0、△≤5；`Missing character`=0；em-dash=0；arXiv tarball 含 .bbl）。另遵守 CLAUDE.md §3 提交前流水线与 §7 文献检索优先级（paper-search-mcp 优先，Web 兜底）。内容冲突以 master 为准。

**前置门禁:** Phase 4 完成（REVIEW CHECKPOINT 4 已过，全稿通读拍板）。

**并行性:** 无（终末串行阶段）。

**交接物:** 投稿包（编译验证过的 main.pdf + supplementary + cover letter 素材）+ arXiv tarball + tag `tosem-v2-submitted`。

---

## 流水线五步

- [ ] **Step 1:** academic-pipeline stage 检测（终稿 → stage 4.5 FINAL INTEGRITY）
- [ ] **Step 2:** 参考文献真实性校验（paper-search MCP 逐条，审计表落 `docs/review_<DATE>/reference_verification.md`；门槛 ✗=0、△≤5；工具链依 CLAUDE.md §7：DOI 直查 → dblp/arXiv → crossref/openalex 兜底 → 三连失败才允许 WebFetch，降级须记录审计日志）
- [ ] **Step 3:** proofread：数字/交叉引用/符号先用后定义（对照理论计划 §0.2 总表逐项）/图表 caption 一致性；**标签一致性门禁（F-14）**：rg 全稿核查——旧标签零残留（`PROP-IDF|COR-FPOS|COR-FNEG`=0；`H1`–`H4` 仅限 Prior Audit 小节；`E3c`、旧 `RQ5`=0）、H-/EXP-/THM-/RQ 标签与论证 master §0.3 + 理论 master §0.5 注册表一致、对象仅用语义集合名（KER-*/POOL-*/MRSET-*/DEF-*）、mp-cell 与新 cell 不混称
- [ ] **Step 4:** humanizer 去 AI 化（em-dash 零容忍、AI 高频词清单、连接词保留规则；调用 `humanizer_academic` skill 执行，保留学术过渡词与合规 en-dash）
- [ ] **Step 5:** 构建验证：两遍编译 + `grep -c "Missing character" main.log`=0 + `python scripts/check_ssot_consistency.py`=exit 0；arXiv 预印本 tarball 同步构建（.bbl 内联、图平铺）；Commit + tag `tosem-v2-submitted`

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| 引文审计 ✗>0 或 △>5 | 逐条修订参考文献后重审；不得以"改措辞规避引用"方式绕过 |
| humanizer 改写引入语义漂移 | 逐 diff 复核技术语句；数字改动一律回滚（数字只能来自 SSOT） |
| tarball 在 pdflatex 下编译失败 | 按 CLAUDE.md §8.5 排查（.bbl 随包、图平铺、字体依赖），修复后重打包 |
