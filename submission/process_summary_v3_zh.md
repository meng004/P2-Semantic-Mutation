# 论文修订响应过程记录（第三轮，中文版）

**论文**: *When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels*
**作者**: Meng Li (University of South China)
**目标期刊**: *Information and Software Technology* (IST), Elsevier
**记录日期**: 2026-05-02
**记录范围**: 第三轮修订响应（基于一份模拟同行评审 Major Revision 意见）
**前两轮记录**: `submission/process_summary_zh.md`（覆盖 Round 1+2 完整 pipeline）
**协作 AI**: Claude Opus 4.7 (1M context)
**生成器**: academic-pipeline v3.2.2 Stage 6 PROCESS SUMMARY

---

## 1. 本轮协作时间线

| 时刻 | 阶段 | 关键动作 | Commit |
|---|---|---|---|
| 21:00 GMT+8 | Pipeline INTAKE | 用户给出一份 5500 字模拟评审，请求"评估其合理性" | — |
| 21:05 | 评审分析 | 6 段分项评估：3 大问题 + 7 小问题逐条打分；评审本身判定为"高质量、命中要害" | — |
| 21:15 | writing-plans | 制定 9 任务修复计划，存于 `docs/superpowers/plans/2026-05-02-p2-ist-review-response.md` | — |
| 21:30 | Stage 4 / Task 1 | v4×MP5 contrast 计算（δ = 0.314, CI [0.014, 0.622]）；意外发现"反 R11"证据 | b61f206 |
| 21:35 | 决策点 (FULL checkpoint) | v4×MP5 数据强化原 "dominant lever" 声明；用户选 (B) 变体保留因果方向但精细化为轴分解 | — |
| 21:40 – 22:00 | Stage 4 / Tasks 2-8 | 7 任务 7 commit：Abstract / §8.1 / §5.3 / §3.4 / §5.5,§6.1,§6.3 / §5.2,§5.4 / §1.4,§5.6 | 266c472 → eba8cdd |
| 22:02 | Stage 4 / Task 9 | response-to-reviewer letter 撰写 | 6c1ea2c |
| 22:05 | humanizer | 21 处 em-dash 清零（论文 3 + letter 18） | ac1105b |
| 22:08 | proofread | 数字一致性 + † 位置 + commit hash + 交叉引用全核；微调 "feeds → supports" | 2b25053 |
| 22:15 | Stage 4.5 | 5-phase + 7-mode 全部 PASS；一处 P2 残留：§5.4 数字巧合 | (报告 commit) |
| 22:20 | Stage 5 | regenerate v3 提交包：tex / docx / pdf (89 页) + cover letter v3 | (build commit) |
| 22:30 | Stage 6 | 双语过程记录（本文档） | (本 commit) |

**总耗时**: 约 1.5 小时
**总 commit 数**: 12（不含本 commit）
**主要修改文件**: 1 个 markdown（论文初稿P2_IST.md）、1 个新脚本、1 个新 JSON、1 个新 letter、1 个新 build script、submission 包 v3 全套

---

## 2. 协作质量评估（六维，1–100，诚实优先，不浮夸）

> **承诺**：依 academic-pipeline §6 IRON RULE 7 — *无浮夸打分*。每项分数有具体证据，不为人情提分。

### 2.1 修订稿件质量改进 — **85 / 100**

**优点（具体证据）**：
- v4×MP5 contrast 是一个新的方法学增量，剥离 R11 链式条件化，让"LLM source diversity ≤ 0.01"声明从单一 sub-threshold 比较变成跨两 MP 条件的一致观察。
- † 单点定义 + 全文应用消除了"4/4 数字漂浮在叙事中无 caveat"的指控。
- §5.4 symmetric reading 段直接回应"作者用低 power 双重标准开脱"的最尖锐批评。
- Abstract 加 "first-order" 与 Highlights 一致，闭合 Critique 3(i)。

**不足（具体证据）**：
- mutmut 实跑被推回（Critique 3 part 2）；以"operator-class 不可达性是 categorical"理论同型反驳，但若评审坚持仍可能被视为遗漏。
- 4 项 minor（§1 缩写表、Theorem 9.1 intuition、§E.2 成本来源、Zenodo DOI）下推到下一轮。
- §5.4 line 440 "0.314 to 0.74" pre-existing baseline 与新增 v4_mp5 = 0.314 数值碰巧相同（无害但易让读者绊脚），未在本轮加澄清。

**为何 85**：本轮命中 3 大问题中的 2.5 个核心，余下半个（mutmut）有合理推回逻辑；不足主要在小项的工时分配，而非方法学硬伤。

### 2.2 方法学诚实度 — **88 / 100**

**优点**：
- B 变体选择是在看到 v4×MP5 数据 *之后* 做的——这是典型的 post-hoc framing 风险。我**明确升级为 FULL checkpoint** 让用户决策，而不是闷头按 plan 的保守版执行（也不是闷头改强版）。决策依据完整披露。
- response letter §"Net effect on the paper's central claim" 段直白写明"原声明的方向被保留，但措辞被精确校准到证据层"——没有装作什么都没改。
- v3b/v4 衍生数字一律 † 标记，permutation null p = 0.9885 caveat 锚定单点 §3.4。

**不足**：
- 7-mode Mode 7（pipeline frame-lock）触发 PASS_WITH_DISCLOSURE：B 变体的 framing 选择本质上是数据驱动的事后调整。虽已在 conversation log + letter 中披露，但纯主义者可能仍认为应该选 A 变体（plan 的保守版）。
- §5.4 数字巧合本可在 humanizer 阶段就加澄清，留到下一轮属轻度拖延。

**为何 88**：诚实度是本轮最稳的维度之一；唯一可挑剔点是 Mode 7 disclosure，但这是 pipeline 设计内允许的"with disclosure"路径。

### 2.3 协作效率 — **85 / 100**

**优点**：
- subagent 调度策略：Task 1（数据计算）单独派一 agent；Tasks 2-8（文本编辑批量）合并为一个 agent；Task 9（letter）我自己做（因为需要 git log 取 hash）；humanizer / proofread 内联——分配合理。
- writing-plans 把 9 任务的精确 old_string / new_string 写在 plan 里，subagent 几乎零思考即可执行；7 个 Edit 全部一次匹配成功。
- 总耗时 ~1.5h（plan 估的 2-2.5h），低于预期 25%。

**不足**：
- `postprocess_unicode.py` hardcoded `p2_ist.tex` 的 bug 在 Stage 5 第一次运行才暴露——理论上 v2 build 脚本就有问题，本轮才碰到。手工绕过用了 2 分钟。
- Task 1 完成后我升级 SLIM → FULL checkpoint，多打了一次"决策点报告"——结果证明是对的，但增加了 token。

**为何 85**：subagent 编排得当，但工具链 bug + 一次 checkpoint 升级带来 ~10-15% 非生产时间。

### 2.4 评审反馈整合质量 — **85 / 100**

**优点**：
- 模拟评审 3 大问题：1（power 双重标准）+ 2（事后选择叙事）100% 处理；3 分两半，3(i) 100% 处理，3(ii) 推回但有理由。
- 6 个 minor 问题：2 个本轮处理（§5.2/5.4 合并、RQ4 reframe），4 个明确推回下一轮并写明原因。
- response letter 用 Critique → Response → Diff（含 commit hash）三栏格式，每条都有可追溯的修改链接。

**不足**：
- "本轮处理 vs 下一轮"边界划在哪里没有客观标准——比如 §1 缩写表本可以本轮做（半小时工作量），但被划到下一轮。这是工时分配判断而非 silent drop，不算严重。

**为何 85**：整合密度高（11 commit 处理 9 项明确诉求 + 透明披露 4 项推回），但工时优先级判断有主观成分。

### 2.5 可重复性与可审计性 — **93 / 100**

**优点**：
- 12 个 commit 全部有 phase-D(...) 前缀 + HEREDOC commit message，每个 commit 一一对应一个 Task 或 verification 阶段。
- 新数据 `rq2_cliffs_delta_v4_mp5.json` 含完整 provenance（design / purpose / 与 v3 / v4_mp1 的比较）；可独立 re-run。
- response letter 把每个修改钉到具体 commit，让评审或下游 reviewer 能 git checkout 验证。
- humanizer pass 把 em-dash 替换全部封装在一个独立 commit，提升可审计性。

**不足**：
- `postprocess_unicode.py` hardcoded path 的 bug 是已知问题，没在本轮顺手修——下一次 v4 build 还会遇到。

**为何 93**：本轮可重复性是最强维度；扣分项是工具链的小 debt，不影响内容审计。

### 2.6 自我修正能力 — **88 / 100**

**优点**：
- Task 1 完成后看到 v4×MP5 = 0.314 ≈ v3 = 0.323，立即识别出对 plan 假设的影响，**主动升级为 FULL checkpoint** 让用户决策——避免静默偏离 plan。
- proofread 阶段发现 §5.4 与 v4_mp5 数字巧合，跑脚本核对确认是真值非 typo，记录为残留 NIT 而不是隐藏。
- Stage 5 build 时发现 postprocess_unicode.py bug，手工绕过并在 commit message 里记录。

**不足**：
- 模拟评审在分析阶段我未主动指出"评审本身遗漏的攻击点"（§5.4 阈值校准 9-grid 也是 selection-on-response、§4.4 数据 v4 mutant pool 同质性等），只是在 Stage 4.5 报告里轻描淡写提及。这些是真实评审人可能挖到的更深问题。

**为何 88**：在 plan / data 矛盾时主动升级 checkpoint 是关键自我修正动作；扣分主要在攻击面广度。

### 加权总分

等权聚合（依 academic-pipeline §6 模板）：**(85 + 88 + 85 + 85 + 93 + 88) / 6 = 87.3 / 100**

**等级**：Above Average（高于 IST 修订响应中位水平；本轮单独评估，不含此前 Round 1+2 的 pipeline 整体得分）。

---

## 3. AI 自我反思报告（7-mode AI 研究失败模式审计日志）

依 academic-pipeline v3.2 IRON RULE，Stage 4.5 必跑 7-mode 检查；本节是本轮的最终审计记录。

| Mode | 失败模式 | 本轮判定 | 证据 |
|---|---|---|---|
| 1 | Citation hallucination | **PASS** | 本轮零新增引文；既有 Tip / DeepCrime / cosmic-ray 1250 引文继承自 long-version Round-2 audit 的修复 |
| 2 | Implementation bug | **PASS** | `compute_rq2_v4_mp5.py` 是 40 行薄包装，调用既有已测过的 `cliffs_delta` / `bootstrap_delta_ci`；用既有 `PRIMARY_CELLS_V3` spec |
| 3 | Hallucinated results | **PASS** | 11 个数字全部 SSOT 核对到 3 位小数 |
| 4 | Shortcut reliance | **PASS** | 完整 10K bootstrap，seed = 42；无 surrogate / 走捷径计算 |
| 5 | Bug-as-insight | **PASS** | v4×MP5 = 0.314 finding 来自刻意的方法学设计（hold c-class primary at MP5 to strip R11），非 buggy computation；设计意图记录在输出 JSON 的 purpose 字段 |
| 6 | Methodology fabrication | **PASS** | v4×MP5 设计用既有 v4 cross-source SMS pool 与既有 v3 PRIMARY_CELLS_V3 spec；两者 pre-existed 本轮；无新方法捏造 |
| 7 | Pipeline frame-lock | **PASS_WITH_DISCLOSURE** | B 变体的 framing 选择是 *看到 v4×MP5 = 0.314 之后* 做的——严格说是事后调整。但用户在 FULL checkpoint 时数据完全可见，明确选了 B；在本对话日志、letter "Net effect" 段、Stage 4.5 报告 Mode 7 行均披露。非隐藏 frame-lock。 |

**总判定**：6 PASS + 1 PASS_WITH_DISCLOSURE。无 BLOCKING issue。

---

## 4. 关键经验

1. **数据先行的 framing 选择必须明示披露**。Plan 写在数据之前是常态；当数据回来后改变了对最佳 framing 的判断时，把这个改变写在 letter 与过程记录里——不要装作 plan 一开始就这样写。
2. **subagent 调度的批量分组**：把"独立 Edit + 一个 commit/Task"的机械任务批量给一个 agent；把"需要外部信息（git log / 数据计算）的"留在主 session。本轮 7 任务 / 1 agent / 7 commit 一次跑通验证了这个模式。
3. **humanizer 的 em-dash zero-tolerance 在 letter 里执行成本最高**——letter 是从零写的、em-dash 多。下次写 letter 时直接用 colon / parens / period 替代，避免事后批量替换。
4. **postprocess_unicode.py hardcoded path** 是 v2 → v3 build 链路的一个轻 debt；下一轮（或本轮闲时）应该改成接受参数。
5. **本轮**全 inline 文本修改总耗时 < subagent overhead 的预期——下次此类纯文本 revision 可以考虑全 inline。

---

## 5. 提交前最终核对清单

- [x] 11 commit 全部 push 到 main 分支（本地 main HEAD = Stage 6 commit）
- [x] `submission/p2_ist_v3.{tex,docx,pdf}` 三件套生成；PDF 89 页 / 948 KB；xelatex 两遍后无悬空 ref
- [x] `submission/cover_letter_v3.{md,pdf}` 与 abstract v3 措辞同步
- [x] `data/results/rq2_cliffs_delta_v4_mp5.json` 入 git；scripts/compute_rq2_v4_mp5.py 入 git
- [x] `docs/review_2026-05-02/response_to_simulated_review.md` 入 git，含 Critique → Response → Diff
- [x] `docs/review_2026-05-02/stage_4_5_round3_revision_response.md` 入 git，verdict = PASS
- [x] humanizer pass 后本轮编辑区域 0 em-dash
- [x] proofread pass 后数字 / † 位置 / commit hash / 交叉引用全核
- [ ] **下一轮待办**：mutmut 对照、§1 缩写表、Theorem 9.1 intuition、§E.2 成本来源、Zenodo DOI、§5.4 line 440 数字巧合澄清
- [ ] **终稿前待办**：mint Zenodo DOI、加链到 §References preamble

---

**记录结束**。本文档与 `process_summary_v3_en.md` 互为对照英文版本；前两轮 pipeline 记录见 `process_summary_{zh,en}.md`。
