# CLAUDE.md — P-series 论文协作规则（项目级）

适用范围：本目录及其子目录的所有论文写作任务（P1-P5 共用 12-PUT × 5-MP 实验基础设施）。

---

## 1. 写作规范

### Abstract / 摘要

- **逻辑结论优先**：以"做了什么、得出什么结论、为什么可信"为骨架，每段 1–2 句。
- **具体数字下放正文**：effect size、CI、p 值、count、percentage 不进 Abstract；正文相应章节才承载。
- **保留**：定性结论性陈述（"达到 / 未达到阈值"、"X 不显著影响 Y"、"X 在 Z 配置下不可达"）。
- **结构化标签**：Context / Objective / Method / Results / Conclusion，IST 偏好。

### 标记符号节制

- `†`、`R[0-9]+` 等内部记号在添加前必须验证：该数值是否 *真的* 依赖被标记的条件。
- 常见反例：class-mean SMS 在所有 cells 上求平均 → *与 primary-MP 选择无关* → 不应加 `†`。
- 主叙事不引 `†` 数字；如需保留 sensitivity，下放到 Appendix。

### 模拟评审 vs 真评审

- **模拟评审**：可激进删除被污染分析（无外部 selective-reporting 嫌疑）。
- **真评审**：保留 Appendix transparency demotion 优于删除。
- 区分明确写在 response letter，避免混淆。

### 诚实优先于救援

- H 阈值不达 → 承认欠功效，不 retroactive 改预注册。
- v3b 类 selection-on-the-response → 删除或下放到 Sensitivity，不 disguise。

---

## 2. 期刊合规硬约束

### IST (Information and Software Technology)

| 项 | 约束 |
|---|---|
| Title | ≤ 15 词建议 |
| Highlights | **3–5 条，每条 ≤ 85 字符**（投稿系统硬截断）|
| Abstract | ≤ 350 词，结构化 |
| Keywords | 5–8 个 |
| Main body | 8k–12k 词 |
| References | 30+ 推荐 |

### 投稿前自检脚本

```python
import re
content = open("论文.md").read()
title = content.split("\n")[0].lstrip("# ")
# Highlights bullet 长度
m = re.search(r"## Highlights\s*\n(.*?)\n## ", content, re.DOTALL)
for b in [b.lstrip("- ") for b in m.group(1).strip().split("\n")]:
    assert len(b) <= 85, f"Highlight 超 85 char: {b}"
# Abstract 词数
m = re.search(r"## Abstract\s*\n(.*?)\n## Keywords", content, re.DOTALL)
words = len(re.sub(r"\*+", "", m.group(1)).split())
assert words <= 350, f"Abstract 超 350 词: {words}"
```

---

## 3. 提交前流水线（5 步，必须按序执行）

### 步骤 1：academic-pipeline 整体审视

调用 `academic-pipeline` skill 做 stage 检测；如已是终稿，直接进入 stage 4.5 (FINAL INTEGRITY)。

### 步骤 2：参考文献真实性校验（paper-search MCP）

后台 agent 任务，对 References 每条调用：
- DOI 条目：`mcp__paper-search__get_crossref_paper_by_doi`
- 标题查找：`mcp__paper-search__search_crossref` / `search_google_scholar` / `search_semantic`
- arXiv preprint：`mcp__paper-search__search_arxiv`
- 软件仓库：直接 WebFetch GitHub URL

输出审计表：每条标 ✓ / △ / ✗ + 修订建议。审计报告存 `docs/review_*/reference_verification_*.md`。

**通过门槛**：✗ = 0；△ ≤ 5（且每条有合理解释）。

### 步骤 3：proofread 校对正文

调用 `academic-paper` skill 的 peer-reviewer 模式 *或* 直接读 §1-§8 + Appendix，扫描：
- 拼写、语法、标点
- 内部一致性（数字、章节交叉引用、symbol 定义先用后定义）
- 假设链完整性（每个 RQ → H → 实验 → 结论 → 反思）
- 表格 / 图 caption 与正文叙述匹配

### 步骤 4：humanizer 去 AI 化

调用 `humanizer_academic` skill。重点扫描：
- **em-dash (—, U+2014) 零容忍** — 全部替换为 `,` / `;` / `:` / `(...)` / 句号
- AI 高频词：delve / crucial / pivotal / landscape / underscore / leverage / showcase / robust signal / intricate / tapestry / testament
- Throat-clearing 起手：`It is important to note that` / `In this section, we will`
- "via" 过用 → "through"
- "linked to" → "associated with"
- 多层 hedging 堆叠
- Negative parallelism (`not only ... but also`)
- "Beyond X," 转折 → "In addition to X,"

**保留**：技术术语、Notably/Furthermore/Specifically 等学术过渡词、合规 en-dash (U+2013) 复合修饰。

### 步骤 5：构建 + 验证 + 提交

```bash
bash scripts/build_ist_submission_v{N}.sh
cd submission && \
  TEXINPUTS=./texmf//: xelatex -interaction=nonstopmode p2_ist_v{N}.tex && \
  TEXINPUTS=./texmf//: xelatex -interaction=nonstopmode p2_ist_v{N}.tex
grep -c "Missing character" /tmp/v{N}p2.log    # 必须为 0
```

提交 message 模板：

```
phase-D(round-{N}): {一句话主题}

{2-3 段说明：动机 → 改动范围 → 验证结果}

Affected sections:
  {章节 1} — {改动}
  {章节 2} — {改动}
  ...

Build: {pages}, {size}, zero "Missing character" warnings
```

---

## 4. 已知陷阱速查

- `scripts/postprocess_unicode.py` 模块的 `mod.TEX = ...` 必须在 `spec.loader.exec_module(mod)` *之后* 设置，否则被模块体重写。
- `build_ist_submission_v{N}.sh` 硬编码 LaTeX preamble 的 Highlights / Abstract / Keywords；markdown 源修订需 *两处同步*。
- `" — " → ", "` 全局替换在含逗号列表的 appositive 里产生 ambiguity；先按上下文分类（heading 用 `:`，clause-break 用 `;`，appositive 用 `,`）再批量。
- 大改前 grep audit 影响范围（`v3b|†|R\d+|旧锚点`），出清单再统一编辑，避免漏改。

---

## 5. P-series roadmap 锚点

- **P1**: MR meta-pattern audit (12-PUT 基础设施) — Progress in Nuclear Energy / SANER 2027 在审
- **P2**: SMS 度量 + 退化定理 + 12-PUT 实证 — IST 投稿就绪
- **P3**: 工业 Java / C++ port + LRCA 二评者 κ — 未启动
- **P4**: 形式理论 (minimal MR-subset 存在 + 三柱耦合) + n ≥ 30 — 未启动，targeted TOSEM
- **P5 / P2-CN**: 法规转化 (IEC 60880 / ISO 26262 / DO-178C) — 中文在审
