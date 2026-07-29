# CP2 评审（evidence-level）— 构念线 verdict 报告审查

**日期:** 2026-07-29 · **对象:** `docs/review_20260728/checkpoint2_construct_line.md`（commit `c1b30632`）
**方法:** 证据级复核——报告中每个数字从底层工件重算（不信任转录）；纪律时序用 git 时间戳验证；对边缘裁决做稳健性探针。复核脚本内联于评审会话，工件固化见 `data/v5/hcons_dedup_sensitivity.json`。

---

## 1. 数字复核（全部吻合）

| 声明 | 复算 | 状态 |
|---|---|---|
| 漏斗 918/918/889/775/460/443；33/51 ≥5；prompt SHA `06fa552d` | funnel_v5.json 重算一致 | ✅ |
| H-ZERO：BA=0.534，TPR=0.371，TNR=0.697，p=0.955 | kill_matrix 重算 TPR=13/35、TNR=23/33、BA=0.5342 | ✅ |
| H-ZERO 单元 68（ALN 35 + CRS 33）、排除 34、覆盖 46 cell | hzero_input.json + 重算一致 | ✅ |
| H-DISC：22 配对、12 非零、r_mp=−0.103、UNDERPOWERED | hdisc_results.json 一致 | ✅ |
| H-XI：303 kill、86 越块、ξ=0.2838 | kill_matrix 重算一致 | ✅ |
| H-FIX：eligible 20、抽 15、5/15 转正、CE 5/6 vs SI/TF 0/9、账目偏差 0 | fix_intervention_v5.json 重算一致；**seed 20260728 抽样可复现（重放匹配）** | ✅ |
| 2×2 双败句 | hxi_results.json `adjudication_2x2` 与 hypotheses.md §0.1 逐字一致 | ✅ |
| CE×b2 块结构 ALN=1.0 / CRS=0.0 | kill_matrix 直查一致 | ✅ |
| MP3 两套 0/12 | mr_funnel_v5.json 重算一致 | ✅ |
| 纪律时序 | git：MR 冻结 `c7aaa1ee` 05:37:01Z → kill 完成 05:41:47Z（工件内时间戳）→ 结果提交 `c1b30632` 05:45:28Z | ✅ |

**归因断言的直接证据补强（本评审新增）:**
- MP4"恒等式无杀伤"断言：set1 `c1_mp4` 的 `r(x)=return x`；set2 为 `clip(x+1e-10)`（ε 恒等式）——断言成立，非推测。
- CRS 映射无选择性攻击面：kill_matrix_v5.json 工件闭包显示每 cell 仅存在 `set{1,2}_{ALN,CRS}` 四个条件键，**从未评估任何备选 cross 层**——"按结果挑映射"在工件结构上不可能。

## 2. Devil's Advocate（论证内部一致性）

1. 报告各节与工件零冲突；2×2 格句、降级路径执行、旗标语义均与冻结文本一致。
2. 小注：H-ZERO 的 UNDERPOWERED 口径（"<40 measurable applicable cells"）冻结脚本操作化为"单元覆盖的 distinct cell 数=46"→ 无旗标。更严的读法（双条件可测=22）会触发旗标；两种读法都不改变 FAIL verdict（旗标仅信息性）。以脚本（冻结权威）为准，此差异记录备查。

## Reviewer 2 视角的最严苛审稿意见

- **[严重，非致命] H-CONS 边缘 PASS 对"去重口径"不稳健。** 冻结文本只说"≥5 confirmed non-equivalent mutants"，未钉扎 distinctness 口径；管线用 exact-SHA（在任何 kill 数据前提交于 `eea2d88e`，程序合规）。但换用项目自有的 EXP-STR AST 归一化指纹：33/51 → **28/51**，Wilson CI [0.414, 0.677]，**LB<0.5（该基准下会 FAIL）**；5 个 cell 跌破 5 线（OS×b2 13→2、OS×c3 16→4、TF×a1 8→2、TF×d1 6→2、OS×d3 6→3）——即这些 cell 的"多样性"大量来自注释/空白级文本差异。**处置（必须，投稿前）:** ① 敏感性工件已固化（`data/v5/hcons_dedup_sensitivity.json`）；② CP2 报告与 Phase 4 稿件必须以有界形式陈述 H-CONS（"exact-text 口径 PASS；AST 归一化口径不达线"），不得以单一 PASS 入稿；③ 冻结 verdict 本身不改（分析代码未动，输入操作化差异属披露义务而非 amendment）。
- **[严重，非致命] kill 规格的 ex-ante 地位缺独立 git 存证。** `run_kill_matrix.py`（含 CRS 循环映射、可测性规则）与 kill 结果同 commit（`c1b30632`）入库；不同于 MR 集有先行冻结提交。缓解证据：上表工件闭包（无备选层评估）+ 映射本身是唯一 canonical 确定性选择（1v1 基数匹配、层平衡、与功效锚一致）。**处置（必须，流程整改）:** 自本评审起，任何裁决前规格（Task 3.3 预测、Phase 3 切片冻结等）必须先于执行单独 commit——Phase 3 文件已有此纪律（"commit 必须早于 kill 执行"），Phase 2 执行侧本轮未对齐，记为过程偏差并披露。
- **[中] E1∧E2 确认与 kill 评估的 MR 集不同源**（确认用手写 5-MP 集，kill 用 v5 held-out 集）。方向分析：E1-only 通道确认的"输出恒等但 AVP 不相干"变异体会稀释 SMS 分子、抬高 H-CONS 分母侧计数；对 headline FAIL 无翻转风险，对 H-CONS 的边缘性是又一不利因素——并入上述有界化陈述即可，不另设动作。
- **[小] 对称清单第 6 项偏差**（max_tokens=16000 vs v4 800）已在清单与 commit 中双重披露，且有工件信封守卫（≤3200 字符）+ 作者指令背书——保留现状，稿件 §Threats 需一句话。
- **[小] 单实现算子类的密度上限**（OS 类 swap 型 m=16 结构性不可达）：属设计-现实差，漏斗诚实记录，稿件方法节应说明 m=16 是目标密度非保证密度。
- **霍桑维度:** 不适用（无人类受试）。
- **Benchmark 公正性:** held-out 双集同提示词、同 K、同温度、同信封；跨集对称成立。无不公正基线问题。

**结论：无致命 publication blocker。** 构念线主结论（2×2 双败=操作化失败，不裁决理论）不依赖上述任何一项；但两条"严重非致命"项的处置为 CP2 批准的**前置条件**。

## 4. 过度防御审计（CLAUDE.md §10.1）

| 处置 | 分类 | 辩护 |
|---|---|---|
| H-CONS 有界化陈述（双口径披露） | **效度修复** | 防止过强主张（单口径 PASS 会夸大操纵检验强度）；不删除、不降级任何冻结判据 |
| H-ZERO/H-DISC/H-XI/H-FIX 原样 FAIL 落账 | （无处置） | 零救援、零收缩；2×2 按预注册格执行 |
| 主张收缩类 | **0 项** | 本轮无任何"删可能失败的检验/只留稳赢子集"操作 |

## 5. 评审裁决

**CP2 = APPROVED WITH REQUIRED DISCLOSURES**（两条严重非致命项的处置落地后视为通过；最终仍待作者拍板）。要求的落地动作（本评审随附执行）：
1. `checkpoint2_construct_line.md` 增补 H-CONS 敏感性段 + 过程偏差披露段；
2. `GENERATION_LEDGER.md` 追记双口径计数；
3. 流程整改条款记入 Phase 3 执行注意（规格先行单独 commit）。
