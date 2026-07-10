# P2 项目状态（单一会话入口）

> 每次会话开始**只读这一个文件**即可定位。任何重大 commit 后请同步本文件 + 末尾 `last_synced` 日期。

**Last synced:** 2026-07-10（phase-W editorial：四研究稿 Major-Revision 指令全量落地，TOSEM Regular 唯一权威包重建）
**Stage:** **四研究稿 submit-ready（phase-W）**；P0-2 形式修正 + P1 敏感性 SSOT + P0-3 claim 降级 + P0-1/4/5 全闭合

**2026-07-10 editorial-integration wave（本轮）：**
- **研究数**：四研究（S1 12-PUT 划界 → S2 28-PUT 方向性确认 → S3 归因双面边界 → S4 跨厂商/分级归因/跨语言收官），每研究仅在自身注册内 confirmatory（"sequential registered validation"，非前瞻统一确认链）
- **判定（当前措辞）**：H2-1' CONFIRM（δ=+0.4295，PUT-cluster 单侧下界 +0.2777 为引用口径）| H4' NOT_CONFIRMED | H4''-strict CONFIRM（仅 CE/HP；CF 无可认证样本，inestimable）| H4''-graded NOT_CONFIRMED（0.0833，下界 0，n_rich=6，"did not reach the confirmation threshold"）| H2-2 BOUNDED_NULL（Δδ=+0.0147，CI [-0.021,+0.0686]⊂[-0.20,+0.20] sound containment；注册 half-width 规则 caveat 已披露；MR-design-lever 降级为待因果检验假设）| H4'''-graded CONFIRM（class D 主导 0.4211/19 units，class C 0.1026 低于 bar，co-participation 措辞，永不 dominance）| H-LANG NOT_CONFIRMED（cluster 下界 0.0 a fortiori；"failed to confirm replication under the registered rule"）
- **P1 整合**：PUT-cluster CI 为 headline 引用（cluster_sensitivity_v1.json supersedes cell-level）；denominator 敏感性段落入 construct-validity threats（6/12 PUT 零 certified primary-flipping）；shadow-κ 全貌（0.44/0.36 overall，0.80 shadow-shadow，contested family 近零）
- **词汇**：经验"certificate"→"audit record"（非 correctness proof 一次性声明）；标题改 "...for Scientific-Computing Kernels"
- **Track/包**：TOSEM Regular（Fast-Impact 措辞全删，45 页解读段删除，页数平述：正文至 p47，主稿 50 页，附录 37 页）；唯一权威包 `submission/TOSEM_regular_20260710/`（tectonic 编译，零 Missing character）；20260709 两旧包已从工作树移除（git history 保留）
- **归档同步**：REPRODUCIBILITY.md 三档覆盖 S1-S4 SSOT + 新敏感性 SSOT + 549 测试；CITATION.cff/CHANGELOG 四研究态；docs/release_2026-07-10/zenodo_deposit_checklist.md（ACM badging 清单）
- **验证**：pytest 549 passed；build.py precheck 零错误
- **用户门槛项**：(a) Zenodo 铸造（预注册 + 复制包，见 release note）;(b) 实际投稿 TOSEM Regular;(c) commit 本轮工作树改动

**（前史 phase-Q 状态：）**
**Last synced（前史）:** 2026-07-09（study3 收官：三研究稿 submit-ready，TOSEM Regular track，终评 8/10 SUBMIT NOW）
**Stage（前史）:** 三研究稿 submit-ready（phase-Q）；NOEther 术语全稿对齐；四项终评 minor 全闭合

**Study-3（2026-07-09,注册 v2.0 分级归因研究）：**
- 动机：H4' NOT_CONFIRMED + P8 事故（v5 滤器静默 no-op）+ L2 诊断（117/117 构念级耦合）
- 执行：28 包一次性生成,765 valid → 720 admitted,v6 池 633（修复后全族筛真实生效：81 筛除 + 6 cap 裁剪）,720 盲评审零仲裁
- **判定**：H4''-strict **CONFIRM**（纯度 1.0,CP 下界 0.9673,{CE,HP,CF-带筛}）| H4''-graded **NOT_CONFIRMED**（富类份额 0.0833）——归因构念有效域双面刻画
- 主张阶梯：Study 1 划界 → Study 2 方向性确认 → Study 3 归因边界双面刻画
- **NOEther 对齐**：MP1-5→m_inv/m_mono/m_conv/m_dyn/m_cmp,ψ6→m_adj;注册标签保留;匿名 companion 引用
- 事故台账 P1-P9 + D-A1 全披露;主稿 56 页 + 附录 25 页,包 submission/TOSEM_regular_20260709
- **用户门槛项**：(a) Zenodo 铸造三份预注册 + 复制包;(b) 实际投稿 TOSEM Regular;(c) 可选跨厂商 H2-2

**（前史 phase-K 状态：）**

**Study-2（2026-07-08 当日完成，预注册验证性研究）：**
- 预注册 v1.1 冻结于数据前（commits 072a015/c904bba；**Zenodo 铸造待用户**，稿中已如实声明自证状态）
- 30-PUT 池（18 新增盲编写）、{a2,b4} 校准试点（P1-P5 缺陷修复）、28-PUT 一次性验证性生成（774→756 admitted，747 盲评审，6 仲裁全 CONFIRM）
- **判定（预冻结脚本，零调参）**：H2-1' CONFIRM（δ=+0.4295，单侧下界 +0.2653）| H1' CONFIRM（5/5 族）| H3' CONFIRM（3/4 类）| **H4' NOT_CONFIRMED**（suspect_share 0.1714，泄漏泛化到 TF/OS——真实发现，前置呈现）| H2-2 NOT-RUN（same-vendor 门控，无替代）
- 事故台账：P6（track 默认值写覆 Study-1 文件，git restore 恢复）、P7（盲化断言拦截 docstring 泄漏，导出层脱敏）、D-A1（gated CLI 数据后补，披露为 deviation）——全部在 PILOT_LOG.md 与稿中披露
- **正文 51 页 + 附录 24 页，超 fast-impact 45 页限 → 已转 TOSEM Regular track**（cover letter/declarations 已改）；AI 生成数据披露已如实改写；slot-label 透明句已加
- 包：`submission/TOSEM_regular_20260708/`（tectonic 零警告）
- **用户门槛项**：(a) Zenodo 铸造预注册与复制包；(b) 实际投稿操作；(c) 可选：跨厂商凭证到位后补跑 H2-2

**（前史）tosem-r3 单研究版状态如下，已被双研究版取代：**

**tosem-r3 摘要（commits 3014fa3 / 855df4a / d7ecb56 / 9337a8e）：**
- **S5 purity 已验证**（不再是 unverified hedge）：σ 在 263/292=90.1% mutant 上单值；29 个多层例外全部来自 CF(9/9)+TF(20/54)；RQ2 off-diagonal 实测拆分 57:31；SSOT `data/results/s5_purity_v4.json`
- **H2 incidence 数据错误修正**：原稿 "aligned 9/12 vs cross 6/48, OR=21" 系 2×2 标签写反；SSOT 正确值 aligned 6/12 vs cross 9/48 → OR≈4.2、单侧 p=0.035（稳健网格 OR 4.1-7.0）；升级为一等 detection-incidence 敏感性（独立 family、post-hoc 标注、two-part hurdle）；H2 magnitude 判定仍 "not met"；SSOT `data/results/h2_incidence_v4.json`
- **工业臂仓库内 SSOT 化 + 精确推断加强**：per-case 矩阵自 Zenodo 10.5281/zenodo.21203424 导入（`data/results/industrial_percase_v1.json`,provenance 含 sha256）;全部 23-24 项聚合校验零错配;加强统计:精确 sign-flip 置换 p=0.014(2^27 DP)、MC p=0.005、BCa δ CI [+0.068,+0.461] 排除 0、Wilcoxon V=279.5/z=2.162/p=0.015 —— p=0.046 非刀口
- **Friedman v3→v4**（χ²=16.76, p=0.0022）；tab:p2-09 均值改用 MP5 池 0.213/0.077 与 δ=0.314 同源；rank_means 改 scipy rankdata
- **文献**：µBERT (degiovanni2022mubert) + Meta ACH (foster2025ach) 已引；16 个 hash citation key 全部改可读键
- **包**：`submission/TOSEM_fastimpact_20260708/` acmart 单 documentclass、tectonic 编译 rc=0、零 Missing character/未定义引用；主稿 45 页（正文 42,规则为 45 页正文不含参考文献,达标）;坏包 20260707 与陈旧 zip 已退役
- **叙事**：Intro 已在散文中前置 H1-H4 四项阈值未达;冗余(mixed-effects/H3/HOM)已合并
- **遗留（均为 future work,非投稿 blocker）**：source-diversity 双盲重跑需 n≥30 PUT(文中已声明);工业语料扩展 34→70+;评审历史见 docs/review_2026-07-08/(r0-r4 + d1-d3 验收)
**Repo:** `<P2_ROOT>`
**Paper file (中文权威版)：** `论文初稿P2.md`（1853 行；historical authoritative draft）
**Paper file (英文长稿)：** `论文初稿P2_EN.md`（1844 行；pre-IST compaction）
**Paper file (IST 投稿版)：** `论文初稿P2_IST.md`（main, 8.5k 词）+ `论文初稿P2_IST_appendix.md`（A-G, 4.2k 词）
**Final LaTeX bundle:** `submission/p2_ist_final.{tex,pdf,docx}` + `submission/cover_letter_final.{md,pdf}`

**2026-05-02 Round-2 minor revision pass（commit a0fb8ed）：**
- **Group A（已 commit a20e795,Round-2 ESCALATED 修复）**：§3.5.1 + §5.9.2/3 翻译、Abstract H2 wording、§3.2.6.1 OS 表格单元、LLM 源数字校对、Line 1185 dangling "IST 2024"
- **Group B（R1 method）**：§5.7.3 stipulated-alternative power simulation（power point=0.491 / CI-lower=0.868）、§5.8.4 per-class Friedman + Bonferroni × 4 + Kendall's W、§7.1.2 K_eq sweep 下调 limitation
- **Group C（R2 lit）**：§1.3.2 CPH grounding + 4 经典（DeMillo 1978/Andrews 2005/Just FSE 2014/Papadakis 2019）+ Ammann & Offutt 2008 + Vargha & Delaney 2000；§1.6.2 toy-scope；§9.5 Corollary 9.1 generic statement
- **Group D（R3 §6.5）**：§6.5.3 阈值删除 + retitle "long-term aspiration"、§6.5.2 YAML 删除 + quarterly batch audit reframe、§6.5.1 air-gap incompatibility declaration、§1.1 scope 收紧、§8.6 ASME V&V 20-2009 reference

**Round-2 reviewer 合议（docs/review_2026-05-02/editorial_decision.md）**：
- R0 EIC: Major → **Minor**（6.7→7.4）
- R1 Method: Major → **Minor**（6 items, 已修复）
- R2 Domain: Major → **Minor**（6.71→7.43, 已修复）
- R3 Persp: Major round-2 §6.5（D-6 3/10）→ **Minor**（Round-3 verification 后,D-6 升至 6/10,dissent 已撤回；docs/review_2026-05-02/r3_perspective_round3_verification.md）
- R4 DA: NOT Accept → **Minor**（5 conditional fixes 已修复）

**5/5 一致 verdict: Minor Revision conditional Accept**。Round-3 残余 nits 仅 2 项 non-blocking:
- (i) §6.5 W6 ISO 26262-8 §11 TCL 2/3 verbatim language 未调用（实质内容已正确披露,non-blocking）
- (ii) §6.5.2 line 1499 "scientific computing domains" 改为 "single-output scientific computing kernels of the type covered by §3.1.1"（已 fix pending commit）

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

**Round-9 submission-ready (2026-05-03) 之后的发布路径：**

1. **GitHub release-prep（已完成 2026-05-03）**：仓库整理 + README/CONTRIBUTING/CHANGELOG/PROJECT_STRUCTURE/RELEASE_CHECKLIST 补齐 + .github 模板 + archive/ 历史归档
2. **GitHub 发布**：tag `v1.0.0-submission`，push 公开仓库，等待社区检查
3. **IST 投稿**：使用 `submission/p2_ist_final.{tex,pdf,docx}` + `cover_letter_final.pdf` 走 EVISE
4. **Zenodo 上传**：`replication/build_zip.sh` → 上传 → 拿到 DOI → 替换 README/ZENODO/DATASET/Paper §8 中的 PLACEHOLDER
5. **接收期间**：监控 Issues / PR；任何复现失败 ≤ 24h 响应

**Post-acceptance（待启动 P3）：**
- 工业 Java/C++ port + LRCA 二评者 κ
- n ≥ 30 PUTs（应对 H2 underpowered limitation）
- 形式理论：minimal MR-subset 存在 + 三柱耦合（targeted TOSEM）
