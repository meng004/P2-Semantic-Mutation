# CLAUDE.md — P-series 论文协作规则（项目级）

适用范围：本目录及其子目录的所有论文写作任务（P1-P5 共用 12-PUT × 5-MP 实验基础设施）。

---

## 0. 不允许只说不做（ANTI-CLAIM-WITHOUT-ACTION，最高优先级）

任何回复中出现以下表述时，必须 *在同一回合内* 真实执行对应工具调用并将证据回显给用户：

**触发表述**（中英文均触发）：
- 中文：`已记住`、`已保存`、`已添加`、`已修改`、`已写入`、`已更新`、`已删除`、`已重命名`、`已提交`
- 英文：`I've noted`、`I've saved`、`I'll remember`、`I've added`、`I've modified`、`I've updated`、`I've committed`、`I've removed`

**强制验证规则**：

| 触发表述 | 必须执行的验证 |
|---|---|
| "已修改文件 X" / "I've modified X" | 紧接 `Read` 工具调用，显示修改后的相关行段（≥ 3 行上下文）|
| "已记住偏好 Y" / "I'll remember Y" | 紧接 `Write` 工具调用，写入 `~/.claude/projects/.../memory/feedback_*.md` 并更新 `MEMORY.md` 索引 |
| "已添加任务 Z" / "I've added Z" | 紧接 `TaskCreate` 工具调用，并在响应中给出 task ID |
| "已提交 commit ABC" | 紧接 `Bash git log --oneline -1` 显示实际 commit hash |
| "已删除 / 已移除" | 紧接 `Bash ls` 或 `grep` 验证目标已消失 |
| "已重命名 X → Y" | 紧接 `Bash ls` 验证两个名字的存在状态 |

**禁止行为**：
1. 只说不做：声称"已记住"但未写入 memory 文件
2. 假执行：声称"已修改"但实际未调用 Edit / Write 工具
3. 推迟：用"稍后会..."、"将会..."替代立即执行
4. 模糊化：用"已处理"、"已完成"等不可验证的笼统表述

**例外**：仅当所述操作 *已在前序回合中以工具调用形式完成*，且本回合只是回顾汇报时，可免重复执行——但必须以 `（前序 commit ABC / Edit at L123 已完成）` 之类的引用替代裸声明。

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

---

## 6. 增强对抗审议（Adversarial Review Strengthening, ARS）

`academic-paper-reviewer` 的 Devil's Advocate 阶段完成后，**必须额外执行** Reviewer 2 视角的严苛审视。Devil's Advocate 关注论证一致性；Reviewer 2 关注 *学术诚信* 与 *可发表性硬伤*。

### 扫描维度（5 类，逐项核对）

1. **方法论缺陷**
   - 控制变量是否充分？是否有未声明的混淆因素？
   - 关键操作是否可重现？protocol 是否完整记录在 Appendix？
   - 实验组 / 对照组是否可比？

2. **外部效度问题**
   - 样本代表性：n 是否足够？覆盖的子群是否典型？
   - 泛化能力：结论能否外推到声称的目标域？
   - PUT / 数据集 / 群体的选择是否引入了 selection bias？

3. **统计选择偏差**
   - Cherry-picking：是否只报告显著结果，遗漏不显著的？
   - 多重比较：是否做了 Bonferroni / FDR 校正？
   - Sub-group 分析：是否预注册？事后分组是否被标记？
   - HARKing (Hypothesizing After Results are Known)：假设是否在数据收集前固定？

4. **Benchmark 不公正**（核行业 / 工业控制系统 / 安全关键软件常见痛点）
   - 对比基线是否是该领域的 SOTA？还是挑了较弱的对手？
   - 评估指标是否对自己有利？是否报告对自己不利的指标？
   - 测试集是否独立于训练 / 调参集？

5. **霍桑效应**（教改 / 行为干预 / 流程改造类论文常见痛点）
   - 实验对象是否知道自己在被观察？
   - 观察行为本身是否改变了被观察对象的行为？
   - 长期可持续性 vs 短期热度效应是否区分？

### 输出格式（强制）

```
## Reviewer 2 视角的最严苛审稿意见

- [致命问题 1]
- [致命问题 2]
...

（无致命问题时明确写：Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。）
```

### 处理原则

| 识别结果 | 必须做 | 禁止做 |
|---|---|---|
| 致命问题（publication blocker） | **投稿前修改**正文 / 设计 / 数据 / 假设 | 装作没看见；用脚注 disclaim 替代修改；藏到 "limitations" 段绕过 |
| 严重但非致命 | 在 §Threats / §Limitations 显式承认 + 提出后续验证路径 | 弱化措辞使其不可见 |
| 已知小瑕疵 | 一句话脚注或 Appendix 提及 | — |

### 与 Devil's Advocate 的分工

| 阶段 | 关注点 | 典型问题 |
|---|---|---|
| Devil's Advocate | 论证内部一致性 | "你的 H2 verdict 与 Abstract 表述矛盾" |
| Reviewer 2 (ARS) | 学术诚信 + 外部效度 | "n=12 的 cohort 凭什么外推到工业级" |

ARS 是 *补充* 不是 *替代*——两者都必须执行。

---

## 7. 文献检索优先级（Paper-Search-First Policy）

所有文献检索任务（含 ARS 13-Agent 研究队、reference verification、related-work 扩充、prior-art 防御），**必须优先调用 `paper-search-mcp` 工具**；Web 搜索仅作为降级 fallback。

### 调用顺序（强制）

```
1. paper-search-mcp 学科首选数据库（见下表）
2. paper-search-mcp 通用兜底：search_crossref / search_openalex / search_google_scholar
3. WebSearch / WebFetch（仅当上述全部失败）
```

### 学科 → 首选数据库映射

| 学科领域 | 首选 paper-search-mcp 工具（按优先级） | 备注 |
|---|---|---|
| **软件工程 / 计算机科学** | `search_dblp` → `search_arxiv` → IEEE / ACM via `search_crossref` | dblp 对 SE 顶会覆盖最全；arXiv 对最新 preprint |
| **核行业 / 安全关键系统** | `search_crossref` → `search_openalex` → IEEE via `search_crossref` | Scopus 经 OpenAlex 间接覆盖；IEEE 对核仪控 |
| **教改 / 教育研究** | ERIC（如可达）→ `search_crossref` → `search_openalex` | ERIC 是教育领域权威库 |
| **生物医学 / 临床** | `search_pubmed` → `search_europepmc` → `search_medrxiv` / `search_biorxiv` | preprint 用 medrxiv / biorxiv |
| **数学 / 物理 / 理论** | `search_arxiv` → `search_crossref` → `search_semantic` | arXiv 优先 |
| **DOI 已知** | `get_crossref_paper_by_doi`（直查） | 跳过 search 阶段 |

### ARS 13-Agent 研究队的硬约束

**禁止**：将 `WebSearch` / `WebFetch` 作为首选检索工具。

**必须**：先用 `paper-search-mcp` 学科首选 → 通用兜底 → 三连失败后才允许降级 Web 搜索；降级时必须在审计日志中记录"paper-search-mcp 在 [tool A, tool B, tool C] 上失败"。

### 工具失败处理

- **rate limit / timeout**：等 30 秒重试 1 次，仍失败则切换下一个 paper-search 工具
- **DOI not found**：用 title + 第一作者 fuzzy search（`search_crossref`）
- **author 名字变体**（如 Romanisation 不同）：尝试两种拼写
- **conference paper without DOI**：用 `search_dblp` + venue 缩写
- **textbook / standard / software repo**：跳过 paper-search，直接用 WebFetch 出版社页 / 标准官网 / GitHub 仓库

### 审计日志格式

每次文献检索任务结束须输出：

```
## 检索审计

| Ref | 工具链 | 命中工具 | 耗时 | 状态 |
|-----|--------|---------|------|------|
| Sun 2024 | crossref(doi) | crossref | 0.8s | ✓ |
| Romano 2006 | crossref(title) → openalex → google_scholar | google_scholar | 4.2s | △ no DOI |
| ASME V&V 20 | webfetch(asme.org) | webfetch | 2.1s | ✓ standard |
```
