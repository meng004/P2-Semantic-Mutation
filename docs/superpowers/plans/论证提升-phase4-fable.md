# 论证提升-phase4-fable：手稿重构写作

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪；REVIEW CHECKPOINT 必须停下等作者拍板。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——学术英文写作与叙事重排是本阶段唯一瓶颈，降级措辞需最强行文控制；与理论章节（同为 fable 起草）保持口径一致）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`。开工前必读其 §0（标识系统——正文假设/实验一律用 H-/EXP- 语义标签，统计符号首现限定词规则见 §0.2）、§1.1（对象集合语义命名 KER-*/POOL-*/MRSET-*/DEF-*，正文对象命名口径）、§1.2（RQ→假设→对象→方法→指标 链路总表，claim-evidence map 骨架）、§1.3.1（两段式标识，§3 外部协议小节素材）、§1.4（对象构建原则 P1–P7，§3 写作素材）。另必读理论计划 §0.2 符号总表（正文数学符号闭集）。内容冲突以 master 为准。

**前置门禁:** Phase 2/3 主体完成（可与其尾部重叠：CHECKPOINT 2 已过、Phase 3 至少完成 Task 3.3 冻结）；理论线 T6.1 整合完成（§2 新定理已入稿）；SSOT 双口径键迁移核对（master Task 0.2 Step 2b，理论 T5.2 联动）已通过。全部数字注入必须过 `scripts/check_ssot_consistency.py`。

**并行性:** 工期 3–4 周；与 Phase 3 尾部（Task 3.4 执行揭盲）重叠推进，外部线小节最后填数。

**交接物:** `submission/TOSEM_regular_v2_workdir/` 全稿 + 新图 4 幅 + CHECKPOINT 4 通读拍板 → 供 Phase 5 流水线。

---

## Task 4.1：建立 v2 工作副本

- [ ] **Step 1:** `cp -r submission/TOSEM_regular_20260706 submission/TOSEM_regular_v2_workdir && git add -A && git commit -m "docs(v2): open manuscript workdir"`（理论计划的 §2 改动若已落在 20260706 目录则以其为源）

## Task 4.2：章节改写（按 writing-plan §0 处置表执行）

- [ ] **Step 1:** §1：旗舰主张一句话替换摘要与贡献段；新 **RQ1–RQ4 表（4+1 结构，R-11；口径=master §0.3）**；**论文 2 与论文 4 边界段（R-12）**（P2 concurrent TOSEM submission 声明 + "元模式作为给定词汇消费"；P4 TSE 在审分工：P3 度量 MR 集"够不够"，P4 选"最小够用集"，互不承重）；claim-evidence map 增补 THM-INT/THM-GAP（含 REM-IDF）/THM-WIN 行与外部锚行（骨架=master §1.2 链路总表）
- [ ] **Step 2:** §3 新增五小节：适用矩阵（引 prereg 哈希）、**A-PROV 桥接假设声明（provenance-as-coverage + ξ 诊断，R-6）**、剂量反应设计、held-out source 对称协议、外部切片准入与盲化协议（含 master §1.3.1 两段式标识）；baseline 小节并入 random-floor/MS 排序（cosmic-ray）两基线 + PC 描述性次级 + 算子族文档论证（R-10）；对象选取原则段=master §1.4 的 P1–P7 压缩版（≤1 段）；对象命名一律用 master §1.1 语义集合名（KER-*/POOL-*/MRSET-*/DEF-*）
- [ ] **Step 3:** §4 按新 RQ 顺序重排（R-11）：**RQ2（H-DOSE 剂量反应 + ξ 诊断）→ RQ3（H-CONS 操纵检验开场 → H-ZERO 零预测 → H-DISC 条件判别 → 结构定位段 EXP-STR）→ RQ4（κ 门禁 → H-CAL → H-RANK）→ Prior Audit 小节（旧 H1–H4 原样 + 一段"为什么旧阈值与理论错配"）**；全部数字模板注入自 SSOT
- [ ] **Step 4:** §5：缺口归因解读段（零膨胀的 \(\mathrm{Gap}_{\mathrm{aln}}(R)\) 部分=理论确认）、SMS vs MS 有界比较段（明示不做普适优越主张）、T1/T2/T4 接口段（各一句+引用）
- [ ] **Step 5:** §6 Threats 新增：双重使用防火墙（旧数据用途清单）、外部切片选择披露（准入解耦声明+就绪失败案保留）、v5 provider 单一性、标注者安排披露（双人类 or 降级 test–retest + LLM 辅助声明）
- [ ] **Step 6:** 每节改完即编译 + `python scripts/check_ssot_consistency.py` 过门禁（SSOT 含 \(\mathrm{SMS}_{\mathrm{strict}}/\mathrm{SMS}_{\mathrm{cons}}\) 双口径键；键迁移核对须已按 master Task 0.2 Step 2b 执行，R-7）；分节 commit

## Task 4.3：图表重生

- [ ] **Step 1:** 新图清单：区间宽度 vs 证书预算（THM-INT 演示）、块结构热图（fiber × MR 层 kill matrix + ξ 标注）、剂量反应曲线（4 PUT × 2 算子）、外部校准图（预测 vs 观测 + Kendall τ 对比条）；沿用 `figs/` 现有生成脚本风格，300dpi PNG + PDF 双格式
- [ ] **Step 2:** Commit

**REVIEW CHECKPOINT 4：全稿通读稿交作者；确认叙事顺序与降级措辞。**

---

## 本阶段风险

| 风险 | 触发点 | 处置 |
|---|---|---|
| 外部线揭盲晚于写作进度 | Task 4.2 Step 3 | 外部小节以 SSOT 模板占位（编译可过），揭盲后一次性注入并复跑 consistency 门禁 |
| 任一确认性假设失败改变叙事 | Task 4.2 | 严格按 hypotheses.md 预注册降级路径措辞（有界不一致 + THM-GAP 归因），不改阈值、不删数据 |
