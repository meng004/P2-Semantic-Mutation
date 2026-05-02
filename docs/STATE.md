# P2 项目状态（单一会话入口）

> 每次会话开始**只读这一个文件**即可定位。任何重大 commit 后请同步本文件 + 末尾 `last_synced` 日期。

**Last synced:** 2026-05-02（commit 37fa9bb 后）
**Stage:** Major Revision response 完整提交，5-reviewer parallel re-review 进行中
**Repo:** `/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/MR识别/MT完备性`
**Paper file (中文权威版)：** `论文初稿P2.md`（134 KB，中文，仅 abstract+keywords 英文）
**Paper file (英文翻译版)：** `论文初稿P2_EN.md`（150 KB,1700 行，commit 37fa9bb)

---

## 1. Reviewer 28 项进度

**Pre-2026-05-01 review (24)：** P0: R-2/3/4/5/6/24 | P1: R-7/8/9/10/11 | P2: R-12/13/14/15/16(protocol)/17/18/19/20/21/22/23/25(基础设施)

**2026-05-01 reviewer-consensus revision round (9 ≥3/5 items, plan: docs/superpowers/plans/2026-05-01-p2-reviewer-consensus-revision.md):**
- **P0:** P0-1 (title scope, 5/5) | P0-2 (17.6:1 删) | P0-3 (sign test 4/4 降级) | P0-4 (permutation null + Bonferroni) | P0-5 (chained conditioning) | P0-6 (IST 2024 撤掉, fabricated literature)
- **P1:** P1-3 (§9 strict-vs-asymptotic + L1-L6 dependency, 4/5) | P1-5 (zero-mass to §5.7.2) | P1-7 (protocol asymmetry §7.1 R13)

**2026-05-01 R2 methodology framework restructure (plan: docs/superpowers/plans/2026-05-01-p2-r2-methodology-framework.md):** 3-layer methodology backbone surfaced as paper main contribution; H1/H2/H4/H5 60-cell audit demoted to auxiliary demonstration:
- **T1** §3.2.0 — necessary conditions (a)(b)(c) for semantic mutation (Layer 1 — Definitional)
- **T2** §3.2.6.0 — systematic vs incidental distinction (positive complement to §3.2.6.1 negative argument)
- **T3** §3.2 / §3.3 — 5 classes lifted to meta-mutation operators + specialization framing
- **T4** §2.3 / §4.4 — E1 ∧ E2 equivalence judgment as Layer 2 instantiation; 3-candidate trade-off
- **T5** §3.2.6.3 — mutant traceability empirical (Layer 3 — Applied; **NEW-MAJOR-1 generalization closed 2026-05-02**: 12-PUT cosmic-ray full empirical, |P2|=292 / |CR|=1276 / overall AST overlap = **5.14%**; HP/SI/TF=0/0/0 categorically unreachable, CE=7.81% (boundary), OS=11.67% (88.33% disjoint + 11.67% incidental, §3.2.6.1 OS row downgraded honestly), CF=33.33% (b2 only n=9))
- **T6** §1.2 / §6 / Abstract Conclusion — narrative reorganization around 3-layer backbone

**Pending：**
- ~~**P0 blocker:** R-1（全文英文翻译）~~ ✓ **CLOSED 2026-05-02 commit 37fa9bb** — 论文初稿P2_EN.md 1,700 行,通过 BLTCY proxy + Anthropic Opus 4.7 streaming
- **P0 from 2026-05-01 review:** P0-7（pre-registration claim 证据，单 reviewer，未入此 plan）
- **P1 from 2026-05-01 review:** P1-1/2/4/6/8/9/10/11（单 reviewer items，已 deferred）
- **P2 misc:** R-26/R-27/R-28（需 reviewer 原文核对）

**2026-05-02 strict 5-reviewer parallel re-review（进行中）:**
- 输入: 论文初稿P2_EN.md(post-revision)
- 5 reviewer subagent 已在后台启动（agentId: a9a9278f6a87a5d6c R0 EIC, a1b29cf2169f4679d R1 Methodology, adc2441a0abe19804 R2 Domain, a83c7ee32fe13a053 R3 Perspective, a069925dd6784db02 R4 Devil's Advocate）
- 输出目录: docs/review_2026-05-02/
- 后续: 5 份完成后做 editorial synthesis,确定是否解除 Major Revision

## 2. 论文章节状态（13 个 H1/H2）

| 章节 | 状态 |
|------|------|
| English Title / Abstract / Keywords | ✓ 已英文化（commit 64d580d） |
| §1 论文身份与命题 | ✓ 完整，H3 已撤回 |
| §2 语义变异符号系统 | ✓ 完整 |
| §3 实验对象与 60 单元格矩阵 | ✓ 完整（含 §3.1.1 PUT、§3.2.6 preventive defense） |
| §4 实验流程 | ✓ 完整（含 §4.2.5 cross-source v4 协议） |
| §5 统计分析方法 | ✓ 完整（§5.6/5.7/5.7.2/5.8/5.9 全部已落数字） |
| §6 讨论 | ✓ 完整（含 §6.1 v4 cross-source 叙事 + Petrović 重构） |
| §7 风险与缓解 + Limitations | ✓ 完整（含 R8-R10） |
| §8 参考文献 / References | ✓ NEW（R-7 close）；APA-7，11 学术引用 + 3 软件工具 + 2 P-series companions |
| §9 SMS-MS 退化定理 | ✓ NEW（R-8 close）；6 退化条件 L1-L6 + 3 引理 + 主定理 + LRCA 平凡化推论 |
| 全文英文版 | ✓ 已提交（commit 37fa9bb，论文初稿P2_EN.md 1700 行 / 150 KB） |

## 3. 关键 artifacts（v4 = primary）

**最新数字源：** `data/results/paper_numbers_v4.json`
- RQ1: mean SMS = 0.104, n_zero=45/60, mean C1_share = 0.209
- RQ2: Cliff's δ = **0.439**（CI [0.109, 0.748]，未达 0.474 阈值，H2 rejected）
- RQ3: Friedman χ² = 15.30, **p = 0.0041**（b 类内 p=0.029）；mixed-effects singular
- RQ4: Spearman ρ = 0.163, p = 0.613（H6 几乎独立 ✓）

**v4 cross-source LRCA：** `data/results/lrca_60cell_v4.json`
**v4 SMS：** `data/results/sms_track2_v4.json`

## 4. 代码主线

- PUTs: `src/p2/puts/{a1-d3}.py`（12 个）
- MRs: `src/p2/mrs/{a1-d3}.py`（12 个）
- AVP / LRCA / equiv / stats: `src/p2/{avp,lrca,equiv,stats}/`
- LLM 三家客户端: `src/p2/mutators/llm_client.py`（Claude Opus G / GPT-5.4 R1 / DeepSeek R2）
- Campaign 脚本: `scripts/{cross_source_campaign,sms_campaign,run_lrca,build_paper_numbers,compute_rq{2,3,4}}.py`

## 5. 已弃数据（避免误用）

- `paper_numbers.json` / `_v3.json` / `_v3b.json` → 已被 v4 supersede
- 早期 manual pilot（`a2_MP1_mut1`, `b2_MP2_mut1`）→ 仅为 pipeline 验证，**不入论文**
- LLM-only 单源 v2（`*_pool/`）→ 已被 cross-source v4（`*_pool_v4/`）supersede

## 5.1 ✅ 复现陷阱（已定位，2026-05-01）

正确复现论文 v4 数字需要**两个**环境变量同时设置：
```
SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b
```
- `SMS_VERSION=v4`：选 v4 跨源数据文件
- `P2_PRIMARY_VERSION=v3b`：选 c-class 数据驱动 primary MP（c1/c2/c3 → MP1，§3.5.1）

**漏设 `P2_PRIMARY_VERSION=v3b`** → c-class 仍按默认 v3（→ MP5）分组 → `mean_aligned ≈ 0.213` ≠ 论文的 0.275（`cliffs_delta=0.439` 与 `friedman_chi2=15.30` 不受影响，只 aligned/cross 分组变）。

`paper_numbers_v4.json` 与论文一致；上游 `sms_track2_v4.json` / `lrca_60cell_v4.json` 也未被改动。已在 REPRODUCIBILITY.md §4 显式记录这一双环境变量约定。

## 5.2 R-1 翻译基础设施（2026-05-01 就绪）

- 术语表：`docs/terminology_zh_en.md`（authoritative glossary）
- 翻译脚本：`scripts/translate_paper.py`（Anthropic SDK + prompt caching，分章节、可断点续跑）
- 输出目标：`论文初稿P2_EN.md`（待生成）
- 章节切分：8 段（s0_prelude + §1–§7），总 57k Chinese chars

**运行命令：**
```bash
PYTHONPATH=src .venv/bin/python scripts/translate_paper.py --dry-run         # 验证切分
PYTHONPATH=src .venv/bin/python scripts/translate_paper.py                   # 全文翻译（~$7, ~10 min）
PYTHONPATH=src .venv/bin/python scripts/translate_paper.py --section 1       # 单节 calibration sample（~$0.5）
PYTHONPATH=src .venv/bin/python scripts/translate_paper.py --assemble-only   # 拼接 partials → 论文初稿P2_EN.md
```

partials 缓存于 `.translate_cache/`（已 gitignore）。失败重试只重跑该节。

## 6. 下一步候选（按 ROI）

1. **R-1 全文英文翻译**（P0 blocker；基础设施就绪，待运行 ~$7 / 10 min；之后人审）
2. **R-25 artifact 公开包**（REPRODUCIBILITY 扩充 + Zenodo DOI；~3-5 h）
3. **R-7/R-8 引用 + 定理证明**（P1；~1-2 天）
4. **R-12/R-13 bootstrap + power analysis**（P2；~半天，提升 H2 可辩护性）
