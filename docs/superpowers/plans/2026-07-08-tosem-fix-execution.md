# 2026-07-08 TOSEM 修复方案执行计划（LOOP 工程）

状态：DONE（2026-07-08 13:55，W1/W2/W3 全过审 + Phase B 构建验证全绿；commit 待用户确认）· 协调者：foreground agent · Worker 模型：claude-opus-4-8-thinking-high
评审节奏：每个 worker 完成即触发一次验收评审（验收命令 + 主题漂移检查）；LOOP 心跳兜底。

## 0. 全局政策（所有 worker 必须遵守）

1. **实事求是**：每条写进论文的数字/结论，必须在本回合内用真实命令验证（rg / gh api 拉取
   Defect4MR 归档报告原文比对），并在完成报告中附证据。不允许凭记忆写数字。
2. **两条术语轴不得混淆**：
   - `mut_C/M/G/T/F` ↔ 五个语义效应族一一对应（supplementary B.2 L361-378 逐行证实：
     C=Conservation→inv, M=Monotonicity→mono, G=Convergence→conv,
     T=Trajectory→dyn, F=Fidelity-order→cmp）。**允许改名**为
     `\mathrm{mut}_{\mathrm{inv}}` 等。
   - `CE/OS/HP/TF/SI` 是**编辑机制轴**（patch-shape 故障实现族，AST-overlap 审计的键），
     与 MP 族不同轴。**禁止映射改名**。处理方式：概念性表述改写为不依赖该缩写的措辞；
     保留处按 Gate C 加本地披露 "historical internal campaign IDs retained for
     reproducibility only"。
3. **文件所有权**：W1 只改 `submission/TOSEM_regular_20260707/main.tex`；
   W2 只改 `submission/TOSEM_regular_20260707/supplementary.tex`；
   W3 只改 `docs/decisions/2026-07-08-noether-mp-terminology-precheck.md`、
   `docs/naming_convention.md`、`RELEASE_CHECKLIST.md`。越界即漂移，评审 FAIL。
4. **文风**：新增文本零 em-dash (U+2014)；禁 delve/crucial/pivotal/leverage/robust signal
   等 AI 高频词；en-dash 复合修饰允许；学术过渡词允许。
5. 不 commit；只改文件。commit 由协调者在全部评审通过后统一处理（等用户确认）。

## 1. 任务分解

### W1 — main.tex（6 项）

| # | 任务 | 位置 | 验收命令 | 期望 |
|---|---|---|---|---|
| T1.1 | `\mathrm{mut}_C..F` → `\mathrm{mut}_{\mathrm{inv}}..\mathrm{cmp}`（含 `mut\_C` 文本形式） | L647、L668 等 18 处 | `rg -c 'mathrm\{mut\}_[CMGTF]\|mut\\\\_[CMGTF]' main.tex` | 0 |
| T1.2 | CE/OS/HP/TF/SI：概念句改写（L1623、L2846）；保留处加 Gate C 披露（L1477、1517、1541、1980-84、2353） | 11 处 | 每处保留必须与 "historical internal campaign ID" 同段；`rg -n 'five \(CE, OS'` | 0 命中 |
| T1.3 | exAS 双口径披露段（含 vacuous-hash caveat 一句） | L2416 后 | 数字与 gh api 拉取的归档报告 Appendix B.2 逐一比对 | 完全一致 |
| T1.4 | 双向构念分离反例（E-PETSC-001/004；C-GSL-001/C-SCIPY-002 先验证再写） | L2440-2452 段内 | 逐案与 REALDEFECT-FACE.md 行比对 | 只写验证通过的 |
| T1.5 | `rev.traj`→`rev.time`（L2218、2224）+ ψ6 措辞（L2280 改 "the adjoint MetaPattern $m_{\mathrm{adj}}$, whose invariant is $\psi_6$"） | 3 处 | `rg -c 'rev\.traj' main.tex` | 0 |
| T1.6 | 工业臂/主实验 MP 坐标映射句 + `f_` 前缀注；A1-b 17/34 补入 L2427 附近 | L2396、L2427 | `rg -n '17 of 34\|f_' main.tex` | 命中 |

exAS 参考数字（worker 必须重新拉取核对，不得直接照抄）：34 案 exAS 口径
T1 377/438=0.861、B1 274/438=0.626、B2 228/438=0.521、A1 348/438=0.795；
T1−B1 Holm 0.113（不显著）、B1−B2 Holm 0.047（显著）；all 为预登记主口径。

### W2 — supplementary.tex（3 项）

| # | 任务 | 位置 | 验收命令 | 期望 |
|---|---|---|---|---|
| T2.1 | mut 记号改名（L125 链式定义、L361-378 B.2 表、L464-467 等 26 处） | 全文 | `rg -c 'mathrm\{mut\}_[CMGTF]\|mut\\\\_[CMGTF]' supplementary.tex` | 0 |
| T2.2 | CE/OS/HP/TF/SI 21 处：同 T1.2 政策（编辑机制轴、Gate C 披露、概念句改写） | L326-439、523-527、611、768-771、1231、1300 | 保留处与披露句同段 | 全部合规 |
| T2.3 | Appendix I：34 案计数口径注（=35 verified_full − F-EIGEN-001）；E-PETSC-004 上游 MR !9403 已合并（2026-07-06，回移 diff 逐字节一致）provenance 句；工业臂五层 vs 主实验五轴映射行；`f_` 前缀对照注 | L1487-1509 | 逐条与 upstream-rescan-2026-07-06.md 核对 | 一致 |

### W3 — docs 门禁与术语文件（3 项）

| # | 任务 | 位置 | 验收命令 | 期望 |
|---|---|---|---|---|
| T3.1 | Gate A regex 修复：补 `mathrm\{mut\}_[CMGTF]`、`mut\\_[CMGTF]` 模式；扫描对象加 supplementary.tex | 决策文档 §Gate A | 新 regex 对改前 main.tex 能命中（用 git stash 前快照或字面串自测） | 能命中 |
| T3.2 | naming_convention.md 加 Rosetta 注：CE/OS/HP/TF/SI 为编辑机制 campaign ID，与 MP 族不同轴、不可映射 | §3.3 附近 | grep 该注存在 | 命中 |
| T3.3 | RELEASE_CHECKLIST.md NOETHER gate 条目指向更新后的 regex | — | grep | 命中 |

### Phase B — 构建验证（W1+W2 评审通过后启动 W4）

xelatex 双遍编译 main + supplementary（TOSEM acmart）→ 0 "Missing character"、0 未解析引用；
Gate A-D 全量重跑（新 regex）；全文 em-dash 扫描 = 0 新增。

## 2. 评审协议（每任务一次）

worker 完成 → 协调者执行：
1. 跑该 worker 全部验收命令，逐项记录实际输出；
2. `git diff --stat` 漂移检查：改动文件 ⊆ 所有权清单；
3. 抽查内容型改动（T1.3/T1.4/T2.3）与 Defect4MR 归档报告原文一致性；
4. PASS → 标记完成；FAIL → resume 同一 worker 定点修复，重评。

## 3. 结束条件

全部 T1-T3 验收 PASS + Phase B 构建全绿 + 本计划文件状态改为 DONE。
