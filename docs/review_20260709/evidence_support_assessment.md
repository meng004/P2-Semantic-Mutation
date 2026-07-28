# 实验证据对论点支持程度评估（Evidence Gate）

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-09 |
| 仓库 | `/Users/limeng/Papers/P3-SemanticMutation` |
| 分支 | `codex/tosem-acceptance-repair` @ `bf019eb` |
| 评估技能 | `research-evidence-gate`（claim-status taxonomy） |
| 主稿 | `submission/TOSEM_regular_20260707/main.tex`（tracked 最新 TOSEM regular） |
| SSOT | `data/results/paper_numbers_v4.json` + `rq2_cliffs_delta_v4_mp5.json` + `cosmic_ray_12put_ast_diff.json` + `rq3_friedman_v4.json` |
| 设计文档 | `docs/experiment_documentation/EXPERIMENT_DESIGN.md`（文中锚定 commit `0f250952…`） |
| 既有修复矩阵 | `docs/review_2026-07-08/experiment_repair_matrix.md` / `claim_disclosure_policy.md` |
| 范围 | 只读评估；未改论文正文；未 commit / push |

---

## A. 远程同步状态

| 项 | 结果 |
|---|---|
| `git fetch --all --prune` | 成功 |
| `git pull`（merge） | **Already up to date**；无冲突 |
| 当前分支 | `codex/tosem-acceptance-repair` |
| 相对 `origin/codex/tosem-acceptance-repair` | **ahead 0 / behind 0** |
| 相对本地 `main` | 本分支领先 1 commit（`bf019eb` Repair TOSEM acceptance evidence gates）；`main` 相对 `origin/main` 本地 ahead 1（与本任务无关） |
| 工作区已跟踪改动 | 无（clean tracked tree） |
| 未跟踪（保留未提交） | `submission/IST_regular_20260704/`、`JSS_regular_20260704/`、`TOSEM_regular_20260705/`、`TOSEM_regular_20260706/`、`arxiv-20260704/`、`arxiv-20260707/`、`arxiv-20260707-pdflatex-flat/` |
| `data/` | 已跟踪结果树存在（`data/results/` 约 62 文件）；本次 pull 未改动 |
| 权威投稿包 | tracked：`submission/TOSEM_regular_20260707/`（含 `main.tex` / PDF） |

本地未提交改动均为额外 submission 快照目录，**未与 pull 冲突**。

---

## B. 评估框架与材料映射

### B.1 Claim-status 口径（摘自 research-evidence-gate）

| 状态 | 含义（本报告中的支持强度映射） |
|---|---|
| `supported` | **强** — 证据足以支撑既定措辞与范围 |
| `observed` | **中** — 有直接观测，外推受限 |
| `qualified` | **中/弱** — 仅在显式限定下可用 |
| `insufficient` | **不足** — 证据不完整，不得作结果/贡献 |
| `blocked` | **不足/阻断** — 不得进入 Abstract/Contributions/Conclusion |
| `speculative` | 仅可作未来工作 |

### B.2 主稿论点骨架（TOSEM 20260707）

| 层 | RQ / H | 回答方式 |
|---|---|---|
| Layer 1 定义/理论 | **RQ1** | 形式化 + SMS–MS 退化定理（非统计假设） |
| Layer 3 结构 | **RQ2** | AST-normalized vs cosmic-ray 结构审计 |
| 60-cell 实证 | **RQ3 / H1** | 算子可实例化阈值 |
| 60-cell 实证 | **RQ4 / H2, H4** | aligned vs cross；LRCA suspect_share；边界/伴随/工业臂 |
| 60-cell 实证 | **RQ5 / H3** | 跨类方向一致性；SMS–PC 仅描述性 |

**注意：** `EXPERIMENT_DESIGN.md` 仍使用旧 RQ 编号（RQ1=60-cell 分布，RQ2=Cliff’s δ…），与 TOSEM 主稿 RQ1–RQ5 重编号不一致。本报告以 **TOSEM main.tex** 为准；SSOT 字段名仍沿用 `paper_numbers_v4.json::{rq1..rq4}` 历史键名。

### B.3 关键数字抽查（claim ↔ SSOT）

| 正文 claim | SSOT | 一致？ |
|---|---|---|
| mean SMS = 0.104；45/60 zero | `paper_numbers_v4.json::rq1` `mean_sms=0.104`, `n_zero_sms=45` | ✓ |
| mean C1_share = 0.209；suspect_share ≈ 0.791 | `rq1.mean_c1_share=0.2092`, `mean_suspect_share=0.7908`；`h5_sensitivity_v4.json` 同 | ✓ |
| H2 primary δ = 0.314，CI [0.014, 0.622]；aligned/cross mean 0.213/0.077 | `rq2_primary_mp5` / `rq2_cliffs_delta_v4_mp5.json`：δ=0.3142，lo=0.0138，hi=0.6215；means 0.2133/0.0767 | ✓ |
| MP1 sensitivity δ = 0.439；means 0.275/0.061 | `paper_numbers_v4.json::rq2` | ✓ |
| H2 δ≥0.474 **not met** | `h2_delta_pass: false` | ✓ |
| Friedman χ²=16.76，p=0.0022 | `rq3_friedman_v4.json` χ²=16.7586，p=0.00215；`paper_numbers_v4.json::rq3` 同 | ✓ |
| Spearman ρ=0.163，p=0.613，n=12 | `rq4` | ✓ |
| AST overlap 5.14%；292 vs 1,250；15 overlap | `cosmic_ray_12put_ast_diff.json`：rate=0.05137，n_p2=292，n_cr=1250，n_overlap=15 | ✓（正文写 1,250；STATE.md 曾写 1276，以 JSON 为准） |
| stipulated power ≈ 0.499（MP1 sensitivity） | `rq2_power_stipulated_v4.json`：0.4992 | ✓；且正文正确标明 **非** frozen-MP5 H2 功效 |

抽查结论：主叙事关键数字与 v4 SSOT **一致**；未见把 MP1 sensitivity 误作 H2 primary 的残留混用（相对 2026-07-08 P0-H2-SSOT 修复）。

---

## C. 分论点结构化评估表

| 论点 | 证据来源（路径 + 关键数字） | 支持强度 | 缺口或威胁 | 建议 |
|---|---|---|---|---|
| **C1 / RQ1：SMS 可形式化，且在退化极限下几乎处处退化为 MS** | 主稿 §Problem Formulation / §SMS–MS degeneration；supplementary Appendix G；设计文档 §2.1。无单一 JSON 数字，属证明链 | **强（理论 claim）/ observed（经验退化未直接测）** | 文中自承 criterion (i)“degeneration path failing empirically”**未直接测试**；理论支撑 ≠ 经验退化验证 | 保持“证明 + 构造”措辞；勿在 Abstract 暗示已做经验退化对照；后续可加 syntactic-limit 对照实验 |
| **C2 / RQ2：语义变异体相对默认一阶语法变异工具在 AST 层大体不可达（5.14% overlap）** | `data/results/cosmic_ray_12put_ast_diff.json`：15/292=5.14%；HP/SI/TF=0；CE/OS/CF 局部更高；292 vs 1250 cosmic-ray | **中（observed → qualified 外推）** | 仅 cosmic-ray 默认配置；mutmut 等未做；HOM 列为残余威胁；12-PUT toy kernels；overlap≠语义等价 | 维持“default first-order / AST-normalised / this cohort”限定；勿写“工业工具不可达” |
| **H1 / RQ3：≥4/5 算子在 ≥9/12 PUT 上产生 ≥5 非等价变异体** | 主稿 Table p2-32：仅 parameter/control 达 9/12；1/5 家族达标 → **not met**；`operator_metrics.json` 支撑 per-op 剖面 | **强（对“阈值未达”）**；对“算子普遍可实例化”为 **不足/否定** | 预注册阈值偏乐观（class-targeted 算子 vs 均匀 9/12）；applicability-adjusted 二次分母属 post-hoc 解释 | 主叙事继续报告 **H1 not met**；二次分母仅作机制解释，不得翻转 verdict |
| **H2 / RQ4：aligned vs cross，δ≥0.474 且 OR≥3（exploratory large-effect）** | Primary：`rq2_cliffs_delta_v4_mp5.json` δ=0.314，CI[0.014,0.622]，`h2_delta_pass=false`；OR 因 cross 中位 0 而退化；v3 δ=0.323。Sensitivity：`paper_numbers_v4.json::rq2` δ=0.439 | **中（方向 observed）；对“大效应达标”为不足/否定；整体 qualified** | n=(12,48) 欠功效；45/60 zero-mass；OR 无信息；power 文件锚定 MP1 非 MP5；vacant-cell 后 CI 可跨 0 | 继续：MP5=primary、MP1=sensitivity、H2 not met、underpowered exploratory；禁止用 δ=0.439 作 headline |
| **H2 附：跨源 LLM 不改变效应量，只改善 kill-set 质量** | v3→v4 Δδ≈−0.009，CI 宽；c-class mean SMS +91.5%；C1_share 0.164→0.209；文中声明 protocol asymmetry（v3 dual-blind vs v4 mechanical） | **弱–中（qualified）** | 协议不对称是已披露混淆；非对称设计不能支撑强“机制分离” | 保持“within this asymmetric design / deferred dual-blind rerun”；勿作因果机制贡献 |
| **H4 / RQ4：mean suspect_share ≤ 0.20** | `paper_numbers_v4.json` / `h5_sensitivity_v4.json`：mean=0.7908；12/60 过阈值；cutoff sweep 平坦 | **强（对“H4 失败”）** | 阈值预注册时未知池分布；双峰结构使“均值≤0.20”几乎不可达 | 作为边界发现保留；SMS_C1 敏感性可保留为诊断，不替代 raw SMS |
| **H3 / RQ5：sign test 4/4 且 CV(ΔSMS)<0.5** | 主稿：v3 sign 3/4；v4 MP1 sensitivity 4/4；frozen MP5 下 b-class 倒置；CV≫0.5 → **not met**；Friedman 为独立探索检验 | **强（对“H3 未达”）**；方向一致性仅 **弱/qualified** | 用 MP1 sensitivity 的 4/4 易被误读为 H3 通过；sign test df=3 极弱 | 明确 H3 在 frozen primary 下失败；4/4 仅标 sensitivity；Friedman 不得替代 H3 |
| **RQ5 描述：SMS 与 Pattern Coverage 相关** | `rq4`：ρ=0.163，p=0.613，n=12 | **不足（作正交/相关结论）**；**observed（无检出相关）** | 功效不足以区分零/中等相关 | 维持 hypothesis-generating；禁止“SMS 独立于 PC” |
| **RQ4 强边界 / 对偶经验面（6 程序）** | 主稿 Table p2-30：4 strong / 1 FP weak-MR / 1 FN；含真实库缺陷与教材对照 | **中（observed, case-level）** | 小样本个案；部分教材替代真实缺陷；非预注册 H | 作 duality 的经验插图，不作普遍边界估计 |
| **RQ4 工业臂：construct separation / 34/34 real-defect face** | 主稿明确 **selection-conditioned external sanity check**；repair matrix P1-INDUSTRIAL：**无**完整 `industrial_case_ledger.json` | **弱（sanity）/ 不足（validation）** | 缺 case-level ledger、admission 规则、artifact hash；selection-on-admission | 维持降级措辞；补 ledger 前不得写 industrial validation / benchmark contribution |
| **S5 / 语义对齐纯度** | repair matrix P1-S5-PURITY：仅有 intended-stratum 标签，无独立纯度审计 | **不足（作已验证对齐）** | 无 `s5_purity_audit.json` | 继续“labelling assumption”；对齐结果是该假设下的诊断 |
| **三层方法论 + 贡献边界（非工业阈值）** | Abstract/Intro 已前景化 H1/H4 失败、zero-mass、H2 未达大效应；Threats 承认 n=12 | **中–强（对“边界审计”叙事）** | 若读者把论文读成“SMS 已验证可用”，则过读 | 投稿信/Highlights 继续强调 validity-boundary study |

---

## D. 五维强制覆盖

### D.1 主效应是否被预注册分析直接支撑

| 预注册项 | 主分析是否直接支撑 | 判定 |
|---|---|---|
| H1 算子可实例化阈值 | 是：按家族计数，**明确 not met** | 否定性主效应被直接支撑 |
| H2 δ≥0.474 + OR≥3（exploratory） | 是：frozen MP5 primary，**not met**；方向为正但未达阈值 | 预注册大效应 **未获支持**；点估计方向有观测 |
| H3 sign 4/4 + CV<0.5 | 是：dispersion 失败 → **not met** | 否定性主效应被直接支撑 |
| H4 mean suspect_share≤0.20 | 是：0.791 → **not met** | 否定性主效应被直接支撑 |
| RQ2 AST overlap | 结构审计（非 H），数字可追溯 | 支撑“低重叠”观测，非统计 H |
| RQ1 理论 | 证明链，非预注册统计 | 与实验 SSOT 解耦 |

**结论：** 预注册统计主效应中，**无一正向阈值被达成**；论文诚实报告失败，并把贡献重心放在方法论框架 + 边界发现。这符合 evidence-gate 的“否定结果也须披露”，但意味着 **“SMS 实证有效/大效应可复现”类正向贡献不能标为 supported**。

### D.2 selection-on-the-response / HARKing / cherry-picking 风险

| 风险点 | 状态 | 评估 |
|---|---|---|
| v3b c-class primary MP5→MP1（data-driven） | 设计文档标为 selection-on-the-response；主稿将 MP1 降为 sensitivity；H* verdict 绑 MP5 | **已缓解**（若严格执行 MP5 primary） |
| 用 δ=0.439 或 sign 4/4 作 headline | 主稿已区分；Abstract 强调 frozen-primary H2 未达 | **低**（当前稿） |
| OR≥3 因零膨胀退化仍“满足” | 正文声明 OR 无证据权重 | **已披露** |
| applicability-adjusted H1 二次分母 | 标明 secondary，不翻转 verdict | **可接受解释，非 HARKing verdict** |
| 工业臂 34/34 | 自承 selection-conditioned | **风险仍在**：缺 ledger 时数字可审计性弱 |
| post-hoc falsifiability 四条 | 文中标 “stated post hoc” | 合规披露；不得伪装为预注册 |

### D.3 功效与 n=12 外推；文中是否诚实承认

| 点 | 文中处理 | 评估 |
|---|---|---|
| H2 underpowered | 假设段 + stipulated power（≈0.50，**MP1 sensitivity**）+ 明确非 confirmatory | **诚实**；需注意 power 不对应 MP5 primary |
| zero-mass 45/60 | Abstract + RQ3 前景化 | **诚实且必要** |
| n=12 / 工业转移 | Intro/Threats：toy kernels；industrial transfer = future；工业臂降级 sanity | **诚实** |
| SMS–PC | 明确 CI 过宽、hypothesis-generating | **诚实** |
| Friedman / per-class N=3 | Bonferroni 后无显著；Kendall W 标注 nominal | **合格** |

外推限制：**充分承认**。剩余问题是读者是否仍会把 5.14% overlap 或工业臂读成外部效度证明——属措辞纪律，非隐瞒。

### D.4 数字与正文一致性（抽查）

见 §B.3：**关键 claim ↔ SSOT 一致**。已知历史漂移（STATE.md 中 cosmic-ray 1276、旧 RQ 编号）存在于文档层，**不以 STATE 覆盖主稿/SSOT**。

残余文档债：

- `docs/STATE.md` / `EXPERIMENT_DESIGN.md` RQ 编号与 TOSEM 主稿不一致 → 复现者可能对错字段（建议后续文档同步，非本任务改稿）。
- 未跟踪的 IST/JSS/arxiv 旧包可能含过时数字；**以 tracked `TOSEM_regular_20260707` + v4 JSON 为准**。

### D.5 Appendix / sensitivity 与主叙事是否混淆

| 项 | 主叙事角色 | 是否混淆 |
|---|---|---|
| MP5 frozen primary | H2 / 主 δ | 清晰 |
| MP1 / v3b sensitivity | 明确 sensitivity；power 亦锚定于此 | **基本清晰**；读者需仔细读 power 小节标题 |
| Vacant-cell sensitivity | 同 verdict，CI 变宽 | 未翻转结论 |
| SMS_C1 | 诊断，非主度量 | 清晰 |
| Friedman | exploratory，非 H3/H4 | 清晰 |
| Industrial / adjoint / boundary | RQ4 扩展臂；工业降级 | 清晰；工业证据强度仍弱 |
| Appendix 二次 H1 分母 | 解释失败机制 | 未进入 Abstract 作通过声明 |

**结论：** 相对 2026-07-08 修复目标，主叙事与 sensitivity **未明显混淆**；最大残留是 **stipulated power 易被误读为 H2-MP5 功效**（正文已有纠正句，仍属沟通风险）。

---

## E. Claim ledger 摘要（evidence-gate 风格）

| Claim ID | 陈述（压缩） | Status | 可进入稿件位置 |
|---|---|---|---|
| CL-RQ1-theory | SMS 形式化 + 退化定理 | `supported`（理论） | Abstract / Contributions（理论） |
| CL-RQ1-emp-degen | 经验上 SMS≡MS in syntactic limit | `insufficient` | 仅 future / limitation |
| CL-RQ2-overlap | 5.14% AST overlap vs cosmic-ray default | `observed` / `qualified` | Results；外推须限定 |
| CL-H1-fail | H1 not met | `supported` | Abstract / Results |
| CL-H2-large | δ≥0.474 达成 | `blocked`（作为达标声明） | 禁止 |
| CL-H2-direction | aligned > cross，δ≈0.31 | `qualified` | Results（exploratory / underpowered） |
| CL-H2-source | 跨源不移 δ、只提质量 | `qualified` | Discussion（asymmetry 限定） |
| CL-H3-fail | H3 not met | `supported` | Results |
| CL-H4-fail | H4 not met（suspect≈0.79） | `supported` | Abstract / Results |
| CL-RQ5-PC | SMS⊥PC 或强相关 | `insufficient` | 禁止；仅 “no detectable correlation” |
| CL-industrial-valid | 工业验证 / benchmark | `blocked` | 禁止；仅 sanity check |
| CL-S5-pure | S5 已验证语义纯 | `insufficient`/`blocked` | 禁止；仅 labelling assumption |
| CL-framework | 三层方法 + 边界审计贡献 | `qualified`→接近 `supported`（在否定结果诚实披露前提下） | Contributions（边界研究定位） |

---

## F. 与既有 TOSEM repair 状态对齐

对照 `docs/review_2026-07-08/experiment_repair_matrix.md`：

| ID | 修复状态（矩阵） | 本次证据门控复核 |
|---|---|---|
| P0-H2-SSOT | Closed | ✓ 主稿与 MP5/MP1 分离正确 |
| P0-RQ3-DRIFT | Closed | ✓ Friedman 与 SSOT 一致 |
| P1-INDUSTRIAL | Downgraded；data gap | ✓ 仍无 ledger → validation **不足** |
| P1-S5-PURITY | Downgraded；data gap | ✓ 仍无纯度审计 |
| P1-LOW-POWER | Qualified | ✓ 仍成立 |
| P1-SOURCE-DIVERSITY | Downgraded | ✓ 仍成立 |
| P1-ZERO-MASS | Closed | ✓ 前景化充分 |
| P2-NEGATIVE-FRAMING | Closed | ✓ Abstract 含 H1/H4/H2 失败 |

---

## G. 总评（Verdict）

**一句话 verdict：**  
在当前 TOSEM 主稿的**边界审计 / 否定结果诚实披露**定位下，实验证据对整体论点的支持为 **中等偏强（qualified–supported）**；对“预注册正向阈值达成 / 工业验证 / 语义纯度已证”类论点则为 **不足或阻断（insufficient/blocked）**——论文已大体按此降级，剩余缺口主要在工业臂可审计性与 S5 纯度，而非主 60-cell 数字不一致。

**关键依据（5 条）：**

1. **预注册 H1–H4 均未达阈值**，且正文/Abstract 与 SSOT（`paper_numbers_v4.json`、`rq2_cliffs_delta_v4_mp5.json`、`h5_sensitivity_v4.json`）一致报告失败——否定性主效应证据链完整。  
2. **H2 方向性信号存在但欠功效**（MP5 δ≈0.314 < 0.474；45/60 zero-mass；n=12），文中已标 exploratory/underpowered；MP1 δ=0.439 正确降为 sensitivity，降低 cherry-picking 风险。  
3. **RQ2 结构分离（5.14% overlap，292 vs 1250）有可复现 JSON**，足以支撑 “本 cohort、默认 cosmic-ray、AST 层低重叠”，不足以支撑广泛工具不可达或工业外推。  
4. **关键数字抽查无主叙事–SSOT 冲突**；历史文档 RQ 编号/1276 计数属于文档债，不推翻主稿。  
5. **工业臂与 S5 纯度仍缺 ledger/审计文件**，与 repair matrix 一致：仅允许 selection-conditioned sanity / labelling assumption，不允许 validation-strength 贡献声明。

### 投稿前证据优先级（若要加强正向 claim）

1. 补 `industrial_case_ledger.json`（或继续维持降级，零成本）。  
2. S5 purity 抽样审计（或继续维持 labelling 措辞）。  
3. n≥30 或预声明 zero-aware 模型以收紧 frozen-MP5 H2（否则保持 qualified）。  
4. 对称 dual-blind 跨源协议后再谈 source-diversity 机制。  
5. 同步 `EXPERIMENT_DESIGN.md` / `STATE.md` 的 RQ 编号与 cosmic-ray 计数，避免复现歧义。

---

## H. 检索审计

本任务以仓库内 SSOT / 主稿 / 设计文档为主，**未调用** paper-search MCP（无新增文献真实性核查需求）。

| 材料 | 工具链 | 状态 |
|---|---|---|
| TOSEM main.tex claims | Read / Grep | ✓ |
| paper_numbers_v4 + mp5 + ast + friedman + power | Python JSON | ✓ |
| EXPERIMENT_DESIGN / STATE / repair matrix | Read / Grep | ✓ |
| git sync | fetch + pull | ✓ up to date |
