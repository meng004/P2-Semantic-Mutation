# REVIEW CHECKPOINT T2 — 拍板记录（委托执行）

- 日期：2026-07-28
- 评审对象：`research/theory_drafts/thm_gap.md`（LEM-CLO、THM-GAP、COR-ZERO、ξ；
  PO-GAP-1–6）及其与现稿（committed baseline `8758bc6` 及 T5 修补后稿面）、
  `thm_window.md`（regime 依赖）、`thm_interval.md`（LEM-WIT 依赖）的接口
- 评审身份：作者委托的检查点评审（用户指令"请评审checkpoint T2和T3，发现问题
  及时修复"）；评审线独立重做全部证明步骤与前提依赖检查
- 本检查点地位：预注册冻结的唯一门禁（R-5）——通过后论证提升计划 Phase 1
  方可启动

## 1. 验算结论（Devil's Advocate 线）

逐条复核通过：无跨层 flag 引理（S5 ⇒ 零违反贡献 ⇒ 残差 ≤ Δ_r+2η̄ ⇒
不 flag）；块对角（kill 只落对角）；分解恒等式（fiber 划分 + Σw_j=1 +
uncovered SMS_j=0 的直接展开）；可计算性（标签 + kill 矩阵，无额外 oracle）；
COR-ZERO（覆盖层零质量 ⇒ SMS=0）；LEM-CLO（violation set 经可观测行为定义
对 ≡_obs 封闭，严格包含于 strong 类）。kill 谓词 pass-on-original 合取的
引用（main.tex:620–626）核实无误。

## 2. 发现与处置

### B1（precision，已修）：premise (iii) 的引入链不显式

原 §3 只说"非退化边际使'直接满足 ⇒ 带边际满足'"，跳过了一个真实台阶：
变异体在非目标层 ψ_l 上的检查器残差为何有界。补全后的链条：premise (iii)
对**每个** r ∈ R 引入 THM-WIN 的 H-a（加性残差预算）与 μ_r>2η̄；S5 给
ψ_l 上零违反贡献，H-a 以 ε_viol=0 实例化得执行残差 ≤ Δ_r+2η̄，边际给
< ε_tol。已写入 §3 与 §4 证明（同步 p-execution 关系读 pη̄）。该修复不改
冻结陈述——premise (iii) 的文字本就是"(Theorem [THM-WIN])"整体引用，修复
只是把引用的假设集列明。

### 次要（已修）："alone" 措辞的可审计性

陈述说 gaps "computable from the kill matrix and fiber labels alone"，而
§6 输入清单含 checker 标签。已补一句：fiber-by-stratum kill 矩阵的列索引
即 checker 标签，(b) 内嵌于 (c)，故 "alone" 精确成立。

## 3. 三个决策问题的裁定

| 问题 | 裁定 | 理由 |
|---|---|---|
| Q1 前提强度（理想化前提 + A-PROV 桥 + ξ 量化偏差 vs 带 ξ 的近似块陈述） | **保留干净陈述** | ξ 同时入陈述会使其既当前提偏差度量又当结论项，模型检验角色被自指化；干净理想化 + 声明桥接假设 + 可测偏差与 v3.1/四柱的"先验界 + 实测偏差"风格一致；F-2 双通道已防 ξ 反噬 verdict |
| Q2 ξ 报告方式 | **确认草稿口径** | pooled ξ = secondary confirmatory H-XI（地标 0.10，B-1）；per-cell 描述性；对 H-ZERO/H-DISC verdict 无条件（F-2）；任何变更须在论证计划冻结前走其预注册文本 |
| Q3 Ψ 非冗余（各层容差违反类两两不同） | **作为不变量族的 standing convention 保留在 §3 一行** | 它是声明族 Ψ 的性质而非 R 的性质，不入定理陈述；T6.1 整合时在 Ψ 引入处声明一次（已入 T6 handoff） |

## 4. Reviewer 2 视角的最严苛审稿意见

- （已修复，本轮内关闭）B1：premise (iii) 的引用若不列明引入的假设集，
  审稿人可指"证明用了未声明的 H-a"；修复后引入链显式。
- 前提理想化质疑（"S5-for-all + all-exact 在真实池上不成立"）：已由设计
  应答——理想化前提 + A-PROV（方法学桥，master §0.3，F-12）+ ξ（可测偏差，
  H-XI 受检且可失败）构成完整的"大胆假设、小心求证"闭环；不构成 blocker。
- 循环依赖扫描：THM-GAP → THM-WIN(regime) → 无回边；LEM-CLO → THM-DUAL
  （现稿既有）→ 无回边；COR-ZERO → THM-GAP。无环 ✓。
- 统计选择偏差：v4 零膨胀读法明确标注 development-only（F-8/F-9），
  H-ZERO/H-DISC 判据引用行指向预注册行而非事后构造 ✓。
- 修复后无 publication blocker：Reviewer 2 视角扫描通过——5 类维度均无
  publication blocker。

## 5. 过度防御审计（CLAUDE.md §10.1）

| 处置 | 类别 | 辩护 |
|---|---|---|
| B1 引入链显式化 | 效度修复 | 证明依赖必须可见；不缩主张 |
| Q1 保留干净陈述（拒绝弱化为近似块陈述） | 反过度防御的正向决定 | 弱化版会把可失败预测（COR-ZERO/H-ZERO）稀释成不可证伪的带参描述 |
| ξ 地标 0.10 保持 secondary confirmatory | 大胆假设保留 | B-1 既定，不降级 |

无主张收缩项。

## 6. 门禁判定

**CHECKPOINT T2 = PASS（附修复 B1 与 "alone" 措辞补句；Q1–Q3 裁定如上）。**

- 效力：预注册冻结门禁开启——论证提升计划 Phase 1（`论证提升-phase1-fable.md`）
  自本记录起可启动（R-5）。THM-GAP 若在 T6.2 外部审计出 blocker，按预注册
  amendment 程序处理（AMENDMENTS.md，F-7），不回溯撤销本冻结授权。
- T4（REM-IDF）依赖满足；T6 待 T3/T4 检查点与整合。
- 作者保留否决权：对 Q1–Q3 裁定或 B1 表述另有偏好时，按"先改 master 再同步"
  程序修订。
