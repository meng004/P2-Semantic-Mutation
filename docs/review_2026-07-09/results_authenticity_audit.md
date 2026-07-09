# 实验结果真实性/可信性逐笔审计 — 2026-07-09

**触发**:作者要求"认真核对每一笔实验结果是否真实、可信"。
**方法**:对每个 paper-cited SSOT 做仓库内独立重算(冻结脚本 + 已提交原始数据),
diff 至字节级;对生成缓存做 cache↔campaign-log 逐笔对账;对预注册做 commit
时序验证;对进行中的 Study-4 评审做 schema/blind-map 完整性校验。
审计过程中产生的所有重算文件均写入会话 scratchpad,不触碰已提交 SSOT
(仅 rq3_friedman.json 一例除外,见 F-1)。

## A. 判定层 SSOT(冻结分析脚本重算)

| SSOT | 重算方式 | 结果 |
|---|---|---|
| h1_instantiability_v5.json | compute_h1_instantiability.py | **IDENTICAL** |
| h3_class_consistency_v5.json | compute_h3_class_consistency.py | **IDENTICAL** |
| h4_graded_v6.json | compute_h4_graded.py | **IDENTICAL** |
| dualblind_delta_delta_v5.json | compute_dualblind_delta.py --gated-h2-2 (D-A1) | **IDENTICAL** |
| h2_incidence_v4.json | compute_h2_incidence.py(原地重写) | **git diff 空** |
| s5_purity_v4.json | compute_s5_purity.py | **IDENTICAL**(sans _meta) |
| s5_purity_v5.json | compute_h4_attribution.py(其 generated_by) | **IDENTICAL** |
| rq2_cliffs_delta_v4_mp5.json | compute_rq2_v4_mp5.py(原地重写) | **git diff 空**(δ=0.3142) |
| rq3_friedman_v4.json | SMS_VERSION=v4 compute_rq3_friedman.py | **git diff 空**(χ²=16.76, p=0.0022) |

## B. SMS 矩阵(全量重算,offline AVP/equiv)

| 矩阵 | 参数 | 结果 |
|---|---|---|
| sms_track2_v4(Study-1) | repeats=20(注册值) | **60/60 注册网格 cell 逐字节一致**;90 个网格外扩展-PUT cell 在已提交 SSOT 中如实为 null(审计跑未限 --puts 所致,非数据问题) |
| sms_track2_v5(Study-2) | repeats=1 | **全部验证性 cell 一致**;{a2,b4} 试点 cell 已提交为 null(注册防火墙),重算证实 |
| sms_track2_v6(Study-3) | repeats=1 | 同上,**一致** |

## C. 工业臂(34 案)

从已提交 `industrial_percase_v1.json`(每案 kills/n_applied)独立复算:
n=34,Wilcoxon V=279.5(精确 p=0.01423 / 正态 p=0.0153,scipy 复算 p=0.0148
同数量级同判定),mean paired diff=0.1005 vs 已提交 0.101。**吻合**。
稿件引用 p=0.014 为精确检验值的舍入。

## D. 预注册冻结时序(git commit 时间)

| 注册件 | 注册 commit | 首个数据 commit | 先后 |
|---|---|---|---|
| Study-2 | 2026-07-08 13:49 (072a015) | v5 pools 2026-07-08 18:25 (ff1aab3) | ✓ 注册在前 |
| Study-3 v2 | 2026-07-09 01:06 (8b776c9) | v6 pools 2026-07-09 02:42 (a806d77) | ✓ |
| Study-4 v1 | 2026-07-09 05:36 (f4a6b19) | cache_study4 2026-07-09 09:04 (a088d9e) | ✓ |

## E. 生成缓存 ↔ 日志逐笔对账(Study-4)

- **same 臂**:网关 checkpoint 173 文件 + harness 回包准入 557 = **730,当前缓存精确 730,零重叠零孤儿**。
- **cross 臂**:255 (op,slot) pair 全部恰好 3 attempts(canonical 765 draws),638 准入文件;日志含 P15 冗余行(143)与零成本 transport-error 行(534),均已在 PILOT_LOG P15 中披露且不计入抽取。
- **recruit**:540 = 15 包 × 36 槽,ingest 日志 540 准入。**精确**。
- **C 臂**:122 网关 + 6 harness = 128。**精确**。
- P15 隔离区 59+27+7 文件与事件记录一致。

## F. 发现与处置

1. **F-1(已修复)**:陈旧 `rq3_friedman.json`(v3 时代)的 `rank_means` 字段
   系旧 tie-handling 约定(ordinal argsort,对全零行跨 numpy 版本不稳定)产物;
   脚本修复后重算 χ²=15.30/p=0.0041 逐字节不变,仅 rank_means 变化。
   论文只引用 v4 SSOT(零 diff 重生),旧字段无任何 paper-cited 依赖。
   已用修复约定重生并单独 commit 说明。
2. **F-2(记录在案)**:`compute_h2_incidence.py`/`compute_rq2_v4_mp5.py` 忽略
   `--out` 直写注册路径——重写结果与已提交逐字节一致,故无影响;属脚本
   工效学问题,不改(冻结脚本不动)。

## G. Study-4 评审层(进行中,滚动校验)

- 已落盘回包全部通过 schema 校验(8 必需键、值域、blind_id↔packet 1:1、
  blind-map 成员资格):same 730/730(711 CONFIRMED / 19 REJECTED / 0 UNCERTAIN),
  cross 滚动中(首个 UNCERTAIN 将按注册进 gpt-5.5 仲裁)。
- 盲评审自证有效:独立评审者以差分实验一致否决 `bounds="fixed"` 类未注册
  额外改动(19 REJECT 的主体),并捕获网关生成缺陷(额外改种子、打错目标、
  数值发散)。评审者间对该模式存在一处真实分歧(1 批 CONFIRM vs 5 批
  REJECT),将在冻结 commit 量化披露;SMS 池以机械 AVP/equiv 管线为权威,
  不受此分歧影响。

## H. 未决项(审计完成前必须关闭)

- [ ] pytest 全套(因评审证据脚本占满 CPU 两次超时;评审波次收敛后重跑)
- [ ] cross/recruit/C 评审回包完整性终扫 + 判定分布
- [ ] Study-4 三个判定 SSOT 生成后,以同法重算验证

**中期结论**:所有已完结研究(Study 1–3 + 工业臂)的 paper-cited 数字均可
从仓库内已提交原始数据 + 冻结脚本零差异重算;预注册均先于数据;缓存与
日志逐笔闭合。未发现任何不可追溯或不可重算的结果。
