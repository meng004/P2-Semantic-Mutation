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

---

## 8. arXiv + GitHub 发布准备（Release-Prep Policy）

适用阶段：论文 *submission-ready* 之后、社区检查 / 投稿启动之前。

### 8.1 触发条件（关键词扫描）

用户回合中出现以下任一意图时，**必须**进入本节流程：

- 中文：`发布到 github`、`发到 arxiv`、`公开仓库`、`接受大家检查`、`上传 github`、`传到 github`、`发预印本`、`挂 arxiv`
- 英文：`publish to github`、`upload to arxiv`、`go public`、`open the repo`、`release the bundle`、`mint a doi`

### 8.2 Step 1：意图确认（强制）

**禁止静默假设**用户走哪条发布路径。先输出一段 ≤ 200 字的**三选项摘要**让用户选择：

| 渠道 | 承载 | 标识符 | 适合 |
|---|---|---|---|
| **arXiv (cs.SE)** | 论文 PDF preprint | arXiv ID | 学术可见性 / 同行预审 |
| **GitHub public** | 整个仓库 | URL + commit hash | 协作 / Issue / 持续公开 |
| **Zenodo** | replication.zip | 强 archival DOI | 期刊 §Data Availability 引用支撑 |

明确**告知互替代价**：单 arXiv 失去代码引用 / 单 GitHub 失去 archival DOI / 单 Zenodo 失去学术可见性。

**等用户给出"做哪几样"的明确回复后再继续**。不要替用户决定"全做 / 不做 / 部分做"。

### 8.3 Step 2.5：执行元流程（4 步，强制）

用户确认意图后，**禁止**直接动手。必须按以下 4 步走，且步骤之间是 *门槛*（前一步通过才能进下一步）：

#### 8.3.1 生成发布审计表（Audit Table）

将 §8.5-§8.8 各分项展开成一份逐项可勾选的清单，写入 `docs/release_<DATE>/audit_table.md`。每行格式：

```
| 项 | 检查命令 / 验证标准 | 期望结果 | 状态 |
|---|---|---|---|
| arXiv tarball 含 .bbl | `tar tf p2_arxiv.tar.gz | grep '\.bbl$'` | 至少一个 .bbl | ⬜ |
| README §1 动机 ≥ 2 prior-art | grep `\\cite\\|prior` README.md | ≥ 2 命中 | ⬜ |
| .gitignore 含 `.env` | `git check-ignore .env` | 输出 `.env` | ⬜ |
| 敏感 base URL 扫描 | §8.8 的 grep 命令组 | 0 命中 | ⬜ |
| pytest | `PYTHONPATH=src .venv/bin/pytest tests/ -q` | 全绿 | ⬜ |
| ... | ... | ... | ⬜ |
```

审计表行数 = §8.5+§8.6+§8.7+§8.8 所有子项之和；**不允许**省略。

#### 8.3.2 调用 `superpowers:writing-plans` 制定计划

把审计表交给 `superpowers:writing-plans` 技能，要求生成：
- 阶段划分（≥ 3 个阶段：scrub / write / verify-and-push）
- 每阶段的 review checkpoint（人工拍板点）
- 每个待修改文件的具体改动 diff 描述
- 失败回滚策略（每个 commit 应可独立 revert）

计划文件落地在 `docs/superpowers/plans/<DATE>-release-prep.md`。

#### 8.3.3 调用 `superpowers:executing-plans` 执行计划

按计划逐阶段执行，每个 review checkpoint 处**必须停下**等用户确认。**禁止**：
- 跳过 checkpoint 直接做下一阶段
- 一次 commit 跨越多个阶段
- 把破坏性操作（push / 删除 history）放在 checkpoint 之前

#### 8.3.4 用审计表逐项验证

执行完成后，对照 §8.3.1 审计表**每一行**跑一次检查命令，更新状态列：

- 全部 ✅ → 进入 §8.9 推送步骤
- 任一 ❌ → 回到 §8.3.2 修订计划，再走一遍 §8.3.3-§8.3.4

最终审计结果（全绿快照）写入 `docs/release_<DATE>/audit_table.md` 同一文件，作为发布前的诚信凭证。

### 8.4 Step 3：账号 / 凭证边界（不可代办清单）

以下 **必须** 用户本人完成；助手只给清晰步骤指引：

- GitHub 账号注册（浏览器 CAPTCHA / 邮箱验证 / 密码自设 / 2FA）
- arXiv endorsement（需要既存 cs.SE 作者推荐；首投者要联系学科端有发表的同事）
- Zenodo 账号（同 arXiv，邮箱验证）
- SSH key 私钥生成（`ssh-keygen` 必须由用户运行，绝不能由助手代劳）
- Personal Access Token 创建（GitHub 设置面板手动）

可代办：
- 写 `README.md`、`CONTRIBUTING.md`、`CHANGELOG.md`、`RELEASE_CHECKLIST.md`
- 配置 / 检查 `.gitignore`
- 跑敏感信息扫描
- 用户给出 `<USERNAME>` + 已配 SSH 之后，执行 `git remote add origin` + `git push -u origin main`
- 创建 GitHub Release（gh CLI）
- 在用户给出 arXiv ID 后，替换 README / bibtex 中的占位符

### 8.5 Step 4：arXiv 稿件准备清单

确认走 arXiv 后（仅在 §8.3 元流程的 §8.3.3 执行阶段），**必须**完成：

| 项 | 验证 |
|---|---|
| 论文 PDF 与 IST 投稿版一致 | `diff submission/p2_ist_final.tex submission/p2_arxiv.tex` 应为 0（如做 cosmetic 调整需说明） |
| LaTeX 源能在 arXiv build 通过 | 本地 `xelatex` 改 `pdflatex` 测试一遍（arXiv 默认用 pdflatex；elsarticle.cls 兼容） |
| BibTeX 文件已 inline 或 .bbl 一并上传 | `\bibliography{...}` 引用的 .bib 必须在 tarball 里 |
| Figures 路径正确 | arXiv 解压不保留嵌套深路径，建议 `figures/figN.png` 平铺 |
| Abstract ≤ 1920 字符（arXiv 上限） | `wc -c` 验证 |
| Primary category：cs.SE | 如有 ML 内容可加 cs.LG secondary |
| ancillary files：可选挂 replication.zip（≤ 100 MB） | 注意 arXiv 一旦上传不能删除，只能 supersede |
| 作者 ORCID / affiliation 确认 | 与 IST 投稿一致 |

### 8.6 Step 5：GitHub README 必含 9 章

GitHub-facing `README.md` **必须**包含以下 9 节，缺一不可：

| § | 标题 | 内容要点 |
|---|---|---|
| 1 | **动机**（Motivation） | 为什么做这项研究；指出领域 gap；引 ≥ 2 prior-art |
| 2 | **核心贡献**（Core Contributions） | 编号列 C1...Cn（n ≥ 3），每条一句话 |
| 3 | **重要结论**（Key Findings） | headline result（含 effect size / p / CI 数字） |
| 4 | **仓库布局**（Repository Layout） | tree 输出 + 关键目录用途表 |
| 5 | **复现流程**（Replication） | 至少三档：smoke / cache replay / re-run |
| 6 | **构建命令**（Build Commands） | 论文 build script + figure 重生 + SSOT 重生 |
| 7 | **敏感信息策略**（Sensitive Information Policy） | `.env` 不上传；占位符约定；扫描脚本 |
| 8 | **引用**（Citation） | bibtex + CITATION.cff 路径 + arXiv / DOI 占位符 |
| 9 | **协议**（License） | 论文 **CC-BY-4.0**；代码 **MIT**；数据 CC-BY-4.0 |

### 8.7 Step 6：`.gitignore` 必含基线

发布前 `.gitignore` **必须**屏蔽以下条目（不分 OS / 项目）：

```gitignore
# === Secrets ===
.env
.env.*
!.env.example
*.key
*.pem
credentials.json
secrets/

# === Python ===
__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
.venv.*/
venv/
env/

# === LaTeX byproducts ===
*.aux
*.bbl
*.blg
*.log
*.out
*.toc
*.spl
*.fls
*.fdb_latexmk
*.synctex.gz

# === 论文项目本地工作目录 ===
已有论文/
相关论文/
references_pdfs/
旧稿/
草稿/

# === macOS / Editor ===
.DS_Store
.idea/
.vscode/

# === Claude Code 内部 ===
.claude/
.superpowers/
.translate_cache/

# === Build / dist ===
dist/
build/
node_modules/
```

如发布前发现已 tracked 但应屏蔽的文件 → `git rm --cached <file>` + 加入 `.gitignore` + 单独 commit。

### 8.8 Step 7：敏感信息扫描（强制门槛）

push 前**必须**通过：

```bash
# (1) API key 模式
git ls-files | xargs grep -lE "sk-[a-zA-Z0-9]{20,}" 2>/dev/null \
    | grep -v "\.env\.example" | grep -v "\.md\.bak"

# (2) 真实 base URL（按项目维护一份禁词表）
git ls-files | xargs grep -lEn "(api\.bltcy\.ai|api\.deepseek\.com|api\.openai\.com|api\.anthropic\.com|company-internal\.[a-z]+)" 2>/dev/null

# (3) 第三方邮箱（除主作者外）
git ls-files | xargs grep -EHn "[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.(com|edu|cn|org|net)" 2>/dev/null \
    | grep -v "<MAINTAINER_EMAIL>"

# (4) 内网 IP / 数据库连接串
git ls-files | xargs grep -lE "(192\.168\.|10\.[0-9]+\.|172\.(1[6-9]|2[0-9]|3[01])\.|postgres://|mysql://|mongodb://)" 2>/dev/null
```

任一命中 → 替换为 `<YOUR_BASE_URL>` / `<YOUR_API_KEY>` 占位符 + 单独 commit `release-prep: scrub <type>`。

### 8.9 Step 8：发布顺序（推荐）

1. 仓库整理 + 历史归档（已有 `archive/`）
2. 敏感信息扫描 + 替换
3. README 9-section 重写
4. `.gitignore` 基线核对
5. `pytest` 全绿（验证整理无破坏）
6. 一次或多次 `release-prep:` commit（不混业务改动）
7. 用户确认 GitHub 用户名 → `git push` + tag `v1.0.0-submission`
8. 用户确认 arXiv → 构建 arXiv tarball → 用户上传
9. （IST 接受后）Zenodo upload → DOI 替换占位符 → 重编 PDF → 重 push

**禁止**：
- 把 push / arXiv 上传等不可逆操作放在初次执行流；必须分步等用户确认
- 在用户没明确给 GitHub username 时静默假设仓库 URL
- 把 Zenodo / arXiv / GitHub 三个动作打包成一次"全自动"流；学术诚信场景下用户必须逐步签字
