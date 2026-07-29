# REVIEW CHECKPOINT 2 — 构念线结果 verdict 汇报（Phase 2 完结）

**日期:** 2026-07-29（执行=cursor cloud agent，fable 系；grok 分派档位不可用已披露）
**数据 lineage:** 全部 verdict 出自冻结分析脚本（`scripts/prereg/`，FREEZE_MANIFEST 15/15 验证通过）对 v5 新 lineage 数据的一次性运行；无阈值移动、无数据删除、无 verdict 救援。
**等待作者拍板后进入 Phase 4 前置链（CP2 + Task 3.3 + 理论 T6.1 + SSOT 键迁移）。**

---

## 1. Verdict 总表

| 假设 | 角色 | 判据（冻结） | 结果 | verdict |
|---|---|---|---|---|
| H-CONS | 操纵检验 | ≥5 confirmed 的 cell 份额 Wilson95 LB > 0.5 | 33/51，p̂=0.647，CI [0.510, 0.764]（exact-SHA 口径）；AST 归一化敏感性 28/51，CI [0.414, 0.677]（见 §1.1） | **PASS（有界）** |
| H-ZERO | headline | BA ≥ 0.75 且 McNemar p < 0.05 | BA=0.534（TPR=0.371，TNR=0.697），p=0.955 | **FAIL** |
| H-DISC | headline | Wilcoxon(greater) p<0.05 且 r_mp ≥ 0.33 | r_mp=−0.103，p=0.654，HL=0.0；非零配对 12 | **FAIL** + UNDERPOWERED（<30） |
| H-DOSE | headline | 全局置换 p < 0.05 | p=9.999e-5（CE-B3/CE-C1 干净转变驱动） | **PASS**（Task 2.3，commit 2378065） |
| H-DOSE-CTR | secondary B-2 | ≥6/8 曲线中心包含 | 2/8 | **FAIL**（Task 2.3 已落账） |
| H-XI | secondary B-1 | pooled ξ ≤ 0.10 | ξ=0.284，CI [0.118, 0.505]，86/303 越块 | **FAIL** |
| H-FIX | secondary B-4 | SMS_j 0→正 份额 Wilson95 LB > 0.5（12/15 线） | 5/15，CI [0.152, 0.583]；账目恒等偏差 0 | **FAIL** |
| EXP-STR | 描述性 | 无判据 | v4 重叠 15/292=5.14%，HP/SI/TF 零重叠 | 已入 SSOT（Task 2.4） |

**H-ZERO × H-XI 2×2 预注册裁决（脚本原句输出）:** "Both fail: the operationalisation itself failed; no verdict on the theory is issued."（双败=操作化失败，不裁决理论。）

### 1.1 H-CONS 去重口径敏感性（CP2 评审要求的披露；冻结 verdict 不改）

冻结文本（`hypotheses.md` §4）规定"≥5 confirmed non-equivalent mutants"，**未钉扎 distinctness 口径**。管线采用 exact-SHA（在任何 kill 数据前于 commit `eea2d88e` 提交，程序合规）。CP2 证据级评审用项目自有 EXP-STR AST 归一化指纹（`ast.dump(annotate_fields=False, include_attributes=False)`）做探索性探针：

| 口径 | cells ≥5 | p̂ | Wilson 95% CI | LB > 0.5？ |
|---|---|---|---|---|
| exact-SHA（冻结输入） | 33/51 | 0.647 | [0.510, 0.764] | 是 → PASS |
| AST 归一化（敏感性） | 28/51 | 0.549 | [0.414, 0.677] | **否 → 该口径下 FAIL** |

5 个 cell 跌破 5 线（OS×b2 13→2、OS×c3 16→4、TF×a1 8→2、TF×d1 6→2、OS×d3 6→3）——其"多样性"大量来自注释/空白级文本差异。工件：`data/v5/hcons_dedup_sensitivity.json`。

**写作约束（Phase 4）：** H-CONS 必须以有界形式入稿——"exact-text 口径边缘 PASS；AST 归一化口径不达线"——不得以单一 PASS 陈述操纵检验强度。冻结 `analysis_hcons.py` 输出与输入操作化差异属披露义务，不触发 amendment（分析代码未动）。

## 2. 可测性记账（排除均有日志，绝无插补）

- H-ZERO 单元 68/102（34 排除）；覆盖 cell 46 个（≥40，无 UNDERPOWERED 旗标）。
- H-DISC 配对 22/51（29 排除）→ 非零配对 12 < 30 → UNDERPOWERED 旗标。
- 排除主因：**MP3 槽位两套全空（0/12 × 2）**——prescreen 记录全部为 `AVP_ORIG_FAIL`：冻结的 v4 AVP 调度器对 MP3 不消费 (r,R)，仅按 |program(h)−1.0| 的收敛阶裁决，除收敛形核外原程序即 FAIL。级联：HP 行（aligned=MP3）失 ALN，OS 行（cyclic cross=MP3）失 CRS。
- 空池 cell 4 个（CE×c1、HP×a3、SI×a3、SI×b3，Task 2.1 漏斗诚实损耗）。

## 3. 归因（讨论通道，不改任何 verdict；F-2）

1. **仪器分层清晰**：MP1（守恒）通道是真实仪器——CE 行呈现教科书块结构（如 CE×b2：ALN=1.0 / CRS=0.0；H-FIX 中 CE 类 5/6 转正）。MP4（轨迹）harness 要求 r 为输出保持变换（≤1e-6），held-out 模型合规产出恒等式 r → TF 行 ALN 可测但无杀伤（H-FIX TF 类 0/5）。MP5（渐近）方向性弱。与 EXP-DOSE 的"CE-A1 与全部 HP 曲线 aligned 检查器弱/近空"归因完全一致（REM-FPOS 素材，A-PROV 操作化失配）。
2. **越块 kill（ξ=0.284）**：held-out MR 的宽松 R 关系跨层杀伤（86/303），主要是 MP1/MP2 checker 对非目标层变异的过敏感——provenance-as-coverage 的"aligned-provenance ≈ exact checker"近似（A-PROV）在本操作化下不成立。
3. **与 power report 锚 B 的关系**：预注册明文（§1 reading discipline）"若 operator-targeted 生成不优于 v4 非定向 MR，H-ZERO/H-DISC 应当且将会失败"——本轮结果即该诚实证伪场景的实现。

## 4. 提供方与预算纪律（对称清单终态）

- 生成臂：`gpt-4o`（api_key_1），918/918 调用，prompt SHA 与台账一致（`06fa552d…`）。
- held-out 臂（作者 2026-07-29 指令的优先级过滤后）：set1 `gemini-3.5-flash` 44/60 槽位、set2 `grok-4.5` 46/60（gpt-5.5/deepseek-v4-flash 因 v4 家族约束不入 MR 臂；glm-5.2/qwen3.7-plus/minimax-m2.7 在 16K token 下仍无法交付工件，探针证据在案）。
- 清单第 6 项偏差已记录：max_tokens=16000 覆盖思考通道；**可交付工件以 prescreen 强制 ≤3200 字符（≈v4 的 800-token 信封）**；其余 6 项同值。稿件 §Threats 需一句话。
- 纪律时序可验证（MR 臂）：MR 冻结提交（`c7aaa1ee`，05:37:01Z）早于 kill 完成（工件内时间戳 05:41:47Z）。

### 4.1 过程偏差披露（CP2 评审要求）

`scripts/v5/run_kill_matrix.py`（含 CRS 循环映射、可测性规则）与 kill 结果同 commit（`c1b30632`）入库，**缺少独立于结果的规格先行 commit**——与 Phase 3 协议已写明的"commit 必须早于 kill 执行"纪律不对齐。缓解证据（评审核实）：kill 矩阵工件闭包仅含 `set{1,2}_{ALN,CRS}` 四键，从未评估备选 cross 层，"按结果挑映射"在工件结构上不可能；映射本身是唯一 canonical 确定性选择（1v1 基数匹配、层平衡、与功效锚一致）。**自本评审起强制整改**：Task 3.3 预测冻结、Phase 3 切片冻结、以及任何裁决前规格，必须先于执行单独 commit。

## 5. 过度防御审计（CLAUDE.md §10.1）

| 处置 | 分类 | 辩护 |
|---|---|---|
| H-CONS 有界化（双口径披露） | **效度修复** | 防止过强主张；不删、不降冻结判据 |
| H-ZERO/H-DISC/H-XI/H-FIX 原样 FAIL | （无处置） | 零救援、零收缩；2×2 按预注册格执行 |
| 主张收缩类 | **0 项** | 本轮无任何"删可能失败的检验 / 只留稳赢子集"操作 |

UNDERPOWERED 旗标是可测性事实（MP3 结构性空槽）而非检验回避。

## 6. 对 Phase 4 写作的输入（预注册降级叙事已生效）

- RQ3 主叙事按 2×2 双败格执行：**操作化失败，不裁决理论**——叙事重心转向（a）MP1 通道的干净块结构与 H-FIX 的 CE 类干预成功（THM-GAP 归因可行动性的有界正例）；（b）弱检查器机制的 REM-FPOS 讨论；（c）v5 held-out 仪器改进为后续工作。
- H-CONS 以有界形式入稿（§1.1）；不得以单一 PASS 陈述操纵检验强度。
- H-DOSE 仍为构念线唯一 headline PASS；H-DOSE-CTR 2/8 照实报告。
- 全部 8 个 verdict 无条件入稿（F-11 全报告纪律）。
- §Threats 需覆盖：对称清单第 6 项偏差、kill 规格同 commit 过程偏差、H-CONS 去重口径敏感性、m=16 为目标密度非保证密度。

## 7. CP2 评审状态

证据级评审见 `docs/review_20260728/checkpoint2_review.md`：**APPROVED WITH REQUIRED DISCLOSURES**（本文件 §1.1 / §4.1 已落地）。最终仍待作者拍板。
