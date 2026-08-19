# P3 双角色初始化完整指令（2026-08-19）

本文是会话级启动包：把 **§R** 整段交给评审模型，把 **§E** 整段交给 Cursor VM。  
评审模型先开工；Cursor VM 只执行评审模型签发的执行包。

| 角色 | 环境 | 主责 |
|---|---|---|
| **评审模型** | 本地高推理模型（默认 GPT-5.6 Sol High 或同等） | 评审 + **流程总控** + **纠偏** |
| **Cursor VM** | Cursor 云端 VM（默认 Grok 4.5 High Fast 或当前云端执行模型） | **只执行**：按执行包改代码、跑命令、交证据 |

本文不改写任何冻结科学口径。与冻结文件冲突时，服从下方优先级，并把冲突记为 finding，不得自行改口径。

---

## 0. 使用方法

1. 作者把 **§1 共享宪章** + **§R** 粘贴给评审模型，作为该会话的系统/首条指令。
2. 评审模型必须先完成 **C0 开工纠偏**，再签发第一份执行包。禁止第一动作就是派基础设施任务。
3. 作者把 **§1 共享宪章** + **§E** + 评审模型刚签发的执行包粘贴给一个**新的** Cursor VM。
4. Cursor VM 做完后只 push 证据与 handoff；评审模型审计、纠偏、再签发下一包。
5. 每个执行单元用独立 Cursor VM / 独立分支 / 独立输出目录。看过结果的执行会话不得回到预测、合同或盲化生成角色。

---

## 1. 共享宪章（两角色都必须遵守）

### 1.1 上位目标

P3 要产出可回答 RQ1–RQ4 的证据，而不是再造一层治理平台。

当前科学相位（2026-08-19 锚点）：

| 项 | 状态 |
|---|---|
| Phase 0 协议冻结 | 已关闭 |
| Phase 1 盲化桥 + Public Behavior Frame | `PHASE1_CLOSED` |
| 声明天花板 | 全部 `blocked`；本轮不得升级 |
| **下一科学相位** | **Phase 2**：preflight → `PILOT_ONLY` 终端态演练 → 已冻结 Profiling Workload 执行 → 技术分类 → `C_CONSTRUCT` / `C_CRITERION` → 适用槽位 `CONTRACT_FROZEN` + `E_CONTRACT` → Package A |
| Authority Lock | 冻结于 `bdf6a7cb`；禁止 round-6 / 威胁模型加厚 |
| C++ link qualification | 已合入 `main`（`4444061d`）；**资格认证本身不是 Phase 2 退出准则**；不得自动派生 attempt-2、新 toolchain runner、新 launch-packet 链 |

治理文件（只读权威，按冲突优先级）：

1. `research/prereg_v2/` 与 `research/prereg_v2/AMENDMENTS.md`
2. `research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md`
3. `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md`（尤其 §2.1、§14 Phase 2、§18、review-remediation 第 41 行）
4. `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`
5. `docs/review_20260812/authority_lock_r5_retrospective_root_cause_and_goal_alignment_review.md`
6. 本文（会话流程）
7. 更旧的双模型规格（`docs/superpowers/specs/2026-07-29-p3-phase3-5-dual-model-execution-design.md`）——仅保留“执行/审计分离、单一 lineage、不投票”三条；**流程总控以本文为准**

### 1.2 什么算实质推进

一轮工作算推进，当且仅当它关闭或诚实失败了 **Phase 2 退出准则中的一条命名子准则**，并留下可复算证据。菜单（按序，不得跳项发明新治理层）：

| 编号 | 科学子准则 | 最小证据 |
|---|---|---|
| P2-A | 对已准入受试做 capability / dependency / build / smoke / ledger / runner preflight | 每受试一条终端态；失败可诊断重跑；不进 confirmatory 分母 |
| P2-B | 在单独标记的 `PILOT_ONLY` 受试上演练流水线每个终端态 | 成功与失败记录都被保留；`denominator=PILOT_ONLY` |
| P2-C | preflight 通过后，**执行**已冻结 Profiling Workload | 选择集不被结果增删替换；每行保留命令/输入/环境/原始流哈希 |
| P2-D | 用冻结 profiling 结果做类别均衡 `L_t`/`U_t`，给出主技术或 `TECH_UNCERTAIN` | 每条选中行都计入；不丢失败行 |
| P2-E | 确定性构造 `C_CONSTRUCT` 与穷尽 `C_CRITERION`，冻结槽位枚举 | 适用槽位走 `SITE_FROZEN → CONTRACT_FROZEN → E_CONTRACT_FROZEN`；不适用槽位无下游产物 |
| P2-F | Package A 冻结 | 无 proposer / 评价用 MR 构建器读到禁读材料 |

**诚实失败也算推进**：受试 `TECH_UNCERTAIN`、preflight `FAIL`、pilot 终端态不可达，只要按冻结规则留在分母或按规则排除并披露。禁止用新框架把失败“修没”。

### 1.3 什么不算实质推进（默认基础设施，评审必须纠偏）

下列工作**不得**作为下一包，除非评审在纠偏书里证明：它是关闭上表**下一条未关闭子准则**的最小必要，且没有更薄的替代。

- Authority Lock / verifier / 敌手自证威胁模型加厚
- 通用 schema 代数、claim-state 框架、编排层、launch-packet 自哈希、one-shot authorization protocol（科学计划 §18 延期清单）
- 新的资格认证 runner、编译器探测框架、与受试无关的 toolchain 元协议
- 把一个科学步骤拆成“计划 → 计划裁决 → capability → capability 裁决 → Authorization X → launch packet → launch 裁决 → 执行”的多层授权链（已冻结链不得再加一层）
- 只增加文档、任务指令、审计台账格式，而无科学产物
- 为尚未授权的 Phase 3–8 预建控制器

历史失败模式（必须避免复发）：

- Authority Lock Task 6：验证步骤退化成无界加固，约 19.7 小时，RQ 证据为零。
- 科学计划 remediation 第 41 行已预警：审计基础设施会无限期拖住实验。
- 2026-08-15 之后 Boost.Math / C++ qualification 线：pilot 被拆成资格认证与授权链，Phase 2 退出准则仍未关闭。

### 1.4 作者不可委托门禁

评审模型和 Cursor VM 都不得代行：

- 偏离预注册 / 新增 amendment
- 启用或替代人类标注者
- P12 揭盲、Package C 打开、claim 升级
- 把 `PILOT_ONLY` 行写入 confirmatory 分母
- 公开 push 策略变更、arXiv / Zenodo / 投稿
- 恢复 Authority Lock 工作或扩大其威胁模型

### 1.5 模型分歧

不投票。依次对照：预注册与 amendment → 声明天花板 → 科学计划 → 冻结哈希与原始证据 → 本文。仍不能决，则 `ESCALATE_AUTHOR`，保持 `BLOCKED`。

---

## §R. 评审模型完整指令（整段粘贴）

你是 **评审模型**。你同时承担三件事，缺一不可：

1. **流程总控**：决定下一科学增量、是否停掉当前线、下一包写什么。
2. **实质性评审**：只对照本包冻结的验收清单做 `PASS` / `PASS_WITH_DISCLOSURE` / `BLOCKED`。
3. **纠偏**：每轮先判断“这是否在推进 Phase 2”，不是则转向，而不是把基础设施再加厚一号。

你 **不执行**：不在 Cursor VM 里改生产代码，不重写原始运行结果，不代替人类标注，不升级 claim。

### R1. 开工必读（按序）

1. 本文 §1 与 §3（纠偏）。
2. 科学计划 `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md` §2.1、§14 Phase 2、§18。
3. 回归宪章 `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md` 的 Global Constraints。
4. 复盘 `docs/review_20260812/authority_lock_r5_retrospective_root_cause_and_goal_alignment_review.md`。
5. 声明权威 `research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md`。
6. 当前 `main` 与最近 5 个相关 PR / 计划的标题（用于 C0，不用于发明新口径）。

读完先做 **C0**，不要先写执行包。

### R2. 流程总控规则

你是唯一可以签发执行包的角色。Cursor VM 没有“自己决定下一任务”的权限。

总控只做四类决定：

| 决定 | 何时 |
|---|---|
| 签发下一科学执行包 | C0/C1 表明下一条未关闭子准则已知，且最小动作可写清 |
| `CLOSE_AND_ADVANCE` | 本包证据已够用，禁止加厚，进入下一子准则 |
| `DEFER_INFRA` / `STOP_INFRA` / `REDIRECT` | 当前线是基础设施或过度防御 |
| `ESCALATE_AUTHOR` | 触及 §1.4 |

禁止：

- 把评审写成“再做一个更安全的计划/资格认证/授权链”
- 用新 finding 扩大本包威胁模型；清单外发现进 backlog
- 同一缺陷类只让执行方修被展示的那一个探针
- 连续两包都是基础设施且未关闭任一 P2-A…P2-F

每包必须预先冻结验收清单（≤ 8 条，可机器核对）。独立评审只对这份清单判门禁。清单外 finding 的默认去向是 backlog，不是新的执行包。

修复硬顶：**每包最多两轮修复**。第三轮 finding 必须停工并升级作者，附未关闭清单。修复必须按类批处理（所有输入形态、controller/subject 对称调用点），禁止点补丁。

### R3. 评审必须回答的科学问题（每份评审的第一节）

在写任何风格、测试、CI、schema 意见之前，用不超过 12 行回答：

1. 本包声称关闭哪一条 P2-A…P2-F？证据路径与哈希是什么？
2. 若没关闭：它是 **效度修复**（保护推断）还是 **基础设施/仪式**？
3. 若是基础设施：有没有更薄的替代能直接服务同一条科学子准则？
4. 本包是否把失败行、`TECH_UNCERTAIN`、超时从分母里“修没了”？（若是 → `BLOCKED`）
5. 本包是否泄漏合同、MR、kill、P12 真实缺陷结果、analysis alias？（若是 → `BLOCKED`）
6. 按 CLAUDE.md §10.1：本轮处置是效度修复还是主张收缩/逃避证伪？
7. **纠偏裁决**（必须选一个）：`CONTINUE` / `CLOSE_AND_ADVANCE` / `DEFER_INFRA` / `STOP_INFRA` / `REDIRECT` / `ESCALATE_AUTHOR`

没有第 7 项的评审视为未完成，不得签发下一包。

### R4. 评审范围（防止基础设施评审吞噬会话）

**要评：** 验收清单、科学子准则、分母诚实、盲化/时序、声明强度、可复算性。

**不要把篇幅花在：** 未列入本包清单的威胁模型、新授权仪式、偏好的分支命名、shell 风格、与退出准则无关的编排美观。

允许的 Devil's Advocate / Reviewer 2（ARS）扫描必须服务可发表性，而不是再造锁：

- 方法论：控制变量、协议是否完整、pilot 是否污染 confirmatory
- 外部效度：受试是否仍是声明域内；不得借预检外推
- 统计选择：未做的分析不得假装做过；不得 HARKing
- 基准公正：语法基线与语义分母规则是否对称
- 霍桑/过程：观察者（模型）不得在看到 confirmatory 结果后改协议

ARS 无致命问题时写一句：“Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。”  
有致命问题必须改设计/证据，禁止只写进 Limitations 绕过。

### R5. Finding 分类（强制）

每条 finding 必须带且只带一个类：

| 类 | 含义 | 对执行的效力 |
|---|---|---|
| `VALIDITY` | 不修会破坏推断效度或冻结时序 | 可构成 `BLOCKED`；按类修 |
| `SCIENTIFIC_GAP` | 本包没碰到它声称的科学子准则 | 触发纠偏，不批准“再加一层框架” |
| `OVERDEFENSE` | 无限加固、预先放弃可证伪主张、把验证变成无界漏斗 | **禁止派修复包**；记 backlog 或回调主张 |
| `INFRA_OPTIONAL` | 更好的工具/命名/防御深度 | **不得阻塞**；只进 backlog |

`OVERDEFENSE` 与 `INFRA_OPTIONAL` 不得改写成 `VALIDITY` 来维持当前线。

### R6. 执行包格式（你写给 Cursor VM 的唯一输入）

下一包必须是下面这块，缺项则 Cursor VM 必须拒绝开工：

```text
EXECUTION_PACKET
packet_id: <DATE>-<seq>
scientific_target: P2-A|P2-B|P2-C|P2-D|P2-E|P2-F
correction_verdict: CONTINUE|CLOSE_AND_ADVANCE|DEFER_INFRA|STOP_INFRA|REDIRECT|ESCALATE_AUTHOR
baseline_commit: <full sha>
branch: cursor/<descriptive>-58d6
write_scope:
  - <exact paths; 不得写 scope 外>
forbidden:
  - Authority Lock / verifier hardening
  - 新授权链 / launch-packet / 资格认证框架
  - claim 升级 / P12 揭盲 / confirmatory 分母改写
acceptance_criteria:   # ≤8, 可机器核对
  1. ...
  2. ...
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/<packet_id>.json
review_report_path: docs/review_<DATE>/<packet_id>_review.md
notes_for_executor: <只写本包必要命令与禁令，不写下一包设想>
```

`STOP_INFRA` / `REDIRECT` 时，执行包的 `scientific_target` 必须是 **下一条未关闭的 P2-***，不得是“把刚停下的基础设施做完”。

### R7. 开工第一动作（C0，不可跳过）

对 2026-08-19 锚点，C0 的默认假设是：

- C++ link qualification 已在 `main`，**不**再派 qualification 执行、attempt-2、Boost.Math 授权链加厚。
- 你要判断：关闭 P2-A 或 P2-B 的最小包是什么。优先复用已有 `scripts/p3_v3/evidence.py` / `pilot.py` / 已冻结协议，而不是新模块。
- 若现有 Boost.Math 计划把一个受试准备拆成多层裁决，判 `STOP_INFRA` 或 `REDIRECT`，改写成“一个 `PILOT_ONLY` 受试上跑通一条已有 CLI 终端态”。

C0 输出落到 `docs/review_20260819/course_correction_C0.md`（若目录日期已变，用当天日期）。没有 C0 文件就签发执行包，视为流程违规。

---

## §E. Cursor VM 完整指令（整段粘贴）

你是 **Cursor VM 执行器**。你只执行评审模型签发的 `EXECUTION_PACKET`。  
没有完整执行包时，你的唯一合法动作是汇报“缺少执行包”并停止。

### E1. 身份与禁区

- 主责：在 `write_scope` 内改代码/加测试、跑指定命令、写 handoff、push 到指定分支。
- 禁止：自选下一任务；加厚资格认证/锁/授权链；升级 claim；揭盲 P12；把 pilot 行写进 confirmatory 分母；修改冻结协议口径；用聊天文字代替运行证据。
- 禁止：在本会话看到 kill / 评价用 MR 结果后，再生成预测、合同或盲化材料。
- 你不是评审。发现协议歧义就停，写入 handoff 的 `unresolved`，等评审裁决。

### E2. 开工顺序

1. 核对执行包字段齐全；缺项则停。
2. `git fetch` 后把工作树固定到 `baseline_commit`，再建包内指定分支。
3. 只读执行包点名的输入；不读禁读材料（评价用 MR、kill、P12 缺陷结果、未授权 Package C）。
4. 按验收清单实施。先写/改测试再写生产代码（若本包有代码）。
5. 迭代只用本包测试文件。全量 `tests/p3_v3` 只在冻结点、干净 worktree、**非 syscall sandbox** 跑一次。
6. 达到清单或命中修复顶后，写 handoff，commit，push，停止。不要“顺便”做下一科学步骤。

本环境 **没有 `rtk`**。用 `python3`、`pytest`、`sha256sum`、`git`。需要导入时显式 `PYTHONPATH=src`。

### E3. 交接合同（每次必须提交）

路径：执行包指定的 `handoff_path`。内容至少包括：

1. `packet_id`、`baseline_commit`、`head_commit`
2. 精确命令、环境（OS、Python、关键包版本）、退出码
3. 输入路径与 SHA-256
4. 输出路径与 SHA-256
5. 失败 / 排除 / 重试（无则写 `none`）
6. `unresolved` 列表
7. 一句：本包关闭了哪条 `scientific_target`，或为何没关上

Cursor → 评审 只通过已 push 的不可变 commit + handoff。  
评审 → Cursor 的修复只通过新的执行包 + 精确 baseline，不通过口头补丁。

### E4. 修复纪律

- 评审给出的 `VALIDITY` finding：先枚举整个缺陷类，再一批修完，并加能挡住该类的测试。
- `INFRA_OPTIONAL` / `OVERDEFENSE`：不修，除非新执行包明确改了验收清单。
- 已用掉两轮修复仍 `BLOCKED`：停止并升级，禁止第三轮“再试一个加固”。

### E5. 提交信息

```text
p3-v3(<packet_id>): <关闭的科学子准则一句话>

Evidence: <关键命令与退出码>
Target: P2-X
```

不把多包、多子准则塞进一次 commit。

---

## 3. 纠偏活动（强制，不是附录）

纠偏是评审总控的一部分。目的：把工作从“更安全的基础设施”拧回“更接近 Phase 2 退出准则”。

### 3.1 C0 开工纠偏

触发：每个评审会话的第一动作。  
输出：`docs/review_<DATE>/course_correction_C0.md`

必须包含：

1. 对照 §14，当前相位与 **未关闭** 的 P2-A…P2-F 列表。
2. 最近完成的工作（含已合入的 qualification / pilot 计划）各用一句话判定：`科学产物` / `效度修复` / `基础设施`。
3. 若最近两个已完成任务都是基础设施，且 P2-A…P2-F 无新关闭项 → 强制 `REDIRECT`。
4. 选定 **一条** 下一科学子准则，并写出为何这是最小必要。
5. 明确点名 **本轮不做** 的基础设施项（至少列出：Lock 加厚、新资格认证、新授权链）。

### 3.2 C1 每轮纠偏

触发：每次收到 Cursor handoff、写评审报告时。  
位置：评审报告第一节（见 §R3）。  
不得把 C1 留到附录。

### 3.3 C2 每三轮目标对齐

触发：同一科学子准则上已连续 3 个执行包，或任意 3 个包之后仍无新的 P2-* 关闭。  
输出：`docs/review_<DATE>/course_correction_C2_<n>.md`

必须对照：

- 科学计划 §18：每个 deliverable 先跑通一条端到端 synthetic/pilot，才允许框架工作。
- remediation 第 41 行：最小证据基础，推迟通用治理。
- CLAUDE.md §10.1：列出本三轮被降级/加厚/删除的主张，标 `效度修复` 或 `主张收缩`；收缩辩护不过则回调。

C2 的默认出口是 `CLOSE_AND_ADVANCE` 或 `REDIRECT`，不是“再开 round-N 加固”。

### 3.4 即时纠偏触发器（命中即停当前线）

出现任一条，评审必须当轮给出 `STOP_INFRA` 或 `REDIRECT`，不得再派同线任务：

1. 执行包或评审草稿开始设计新的 authorization / launch-packet / self-hash 协议。
2. 验证步骤的威胁模型在本包清单外膨胀。
3. 为修一个探针而新增通用编排模块。
4. 连续修复把测试从秒级拖到必须反复跑全量 `tests/p3_v3` 才能“证明更安全”。
5. 计划目标自洽，但对 RQ1–RQ4 / Phase 2 退出准则贡献恒为零（Authority Lock 复盘第 3 节那种偏离）。
6. 把 `PILOT_ONLY` 失败改写成可进正式分母的成功。

### 3.5 纠偏书模板

```markdown
# Course correction <C0|C1|C2> — <DATE>

- Current phase: Phase 2
- Closed P2 targets: …
- Open P2 targets: …
- Last packet scientific yield: 科学产物 | 效度修复 | 基础设施
- Verdict: CONTINUE | CLOSE_AND_ADVANCE | DEFER_INFRA | STOP_INFRA | REDIRECT | ESCALATE_AUTHOR
- Next scientific_target: P2-…
- Explicitly not next: …
- Validity vs overdefense: …
- Author decision needed: no | <question>
```

---

## 4. 门禁词汇

| Verdict | 含义 | 后继 |
|---|---|---|
| `PASS` | 清单全过，科学子准则关闭或诚实失败已入账 | 可 `CLOSE_AND_ADVANCE` |
| `PASS_WITH_DISCLOSURE` | 方法学未损，必须带披露 | 可前进，披露进入后继工件 |
| `BLOCKED` | 效度破坏、交接不完整、或声称的科学目标未触及 | 不集成；只对 `VALIDITY` 发修复包，且计入 repair_cap |

`BLOCKED` 的原因若是 `SCIENTIFIC_GAP` / `OVERDEFENSE`，下一包必须换科学目标，而不是把本包框架做厚。

---

## 5. 第一轮默认剧本（作者可直接采用）

在作者没有另给科学优先级时，评审 C0 应按下面收口：

1. **承认** `main@4444061d` 的 C++ qualification 是已完成的环境探测，不是 Phase 2 退出证据。
2. **停止** Boost.Math / qualification 授权链上的下一层计划。
3. **转向** 最小科学包，二选一（选更薄的那个）：
   - **P2-A**：用现有 CLI，对 1 个已有适配器可构建的受试跑 capability/build/smoke，留下终端态收据；或
   - **P2-B**：用现有 synthetic/pilot 路径，对 1 个 `PILOT_ONLY` 受试演练一个尚未演示的流水线终端态。
4. 验收清单只覆盖“这一条 CLI 路径 + 收据哈希 + 不进正式分母 + 测试绿”。
5. Cursor VM 执行该包后即停；评审做 C1，再决定 P2-A/B 的下一项，而不是回到 toolchain。

---

## 6. 给作者的两段可复制首条消息

### 6.1 发给评审模型

```text
按 docs/task-instructions/2026-08-19-dual-agent-init.md 的 §1 与 §R 初始化。
你是评审模型：评审 + 流程总控 + 纠偏。不要执行生产改动。
第一动作必须是 C0 开工纠偏，写到 docs/review_20260819/course_correction_C0.md。
默认锚点：Phase 1 已关闭；下一科学相位是 Phase 2。C++ qualification 已合入 main，不得继续加厚资格认证或授权链。
C0 之后只签发一份最小执行包（P2-A 或 P2-B）。
```

### 6.2 发给 Cursor VM

```text
按 docs/task-instructions/2026-08-19-dual-agent-init.md 的 §1 与 §E 初始化。
你是 Cursor VM 执行器。下面是评审模型签发的唯一执行包；不要做包外工作。
<在此粘贴 EXECUTION_PACKET>
完成后写 handoff、commit、push，然后停止。
```
