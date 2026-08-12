# Authority Lock Round-5 复盘评审：P1 根因、19.7 小时耗时与目标偏离裁定

- Date: 2026-08-12
- Review mode: read-only 复盘评审；评审过程未修改任何代码、测试、设计或计划字节
- 冻结对象: commit `bdf6a7cb9f34ab31e52a7b75a6e32369840b9b65`
  （tree `6e0ecc2de6083f5a100e0ef586cc11bd6d6d626e`，
  design SHA-256 `7cc6389b…a208490`，plan SHA-256 `61412a09…eaa8a612`）
- 冻结点回执: **849/849 P3 v3 tests pass**（干净 worktree
  `.worktrees/p3-v3-mef-align-repair-01`，`PYTHONPATH=src pytest tests/p3_v3 -q`，
  沙箱外运行，exit 0，344.01 s，2026-08-12；与 round-5 verification log 的
  `849 passed in 388.77s` 相互印证）
- 上游审计输入（SDD 工作区，git-ignored）:
  `.worktrees/p3-v3-mef-align-repair-01/.superpowers/sdd/2026-08-11-p3-v3-external-authority-lock-implementation/`
  — 61 个文件：24 份 review diff、round-2/3/4/5 验证报告、
  round-2/4/5 双审计、Repair A–I 报告
- Round-5 双审计判定: specification **PASS (0 load-bearing findings)**；
  operational/security **BLOCKED（3×P1 + 1×N 非阻塞 durability 残留）**
- 处置决定: **采纳出口 (b)** — Authority Lock 冻结于当前状态（round-6 不启动）；
  回归科学计划关键路径
- 后续文档: 冻结记录见
  `docs/superpowers/plans/2026-08-11-p3-v3-external-authority-lock-implementation.md`
  末尾 "Freeze Record (2026-08-12)"；回归计划见
  `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`

---

## 0. 评审问题与结论摘要

本评审回答三个问题：

1. **三项 round-5 P1 的根因是什么，如何避免复发？**
   → 全部是 round-2 已识别缺陷类被"点补丁"修复后的同类实例复发。
   对策：按类修不按例修、对称性检查清单、复审升级为全类对抗重扫。
2. **一个"验证步骤"（Task 6）为何执行超过 18 小时？**
   → Task 6 从有界验证退化为对无界威胁模型的对抗式加固漏斗，
   叠加慢测试、代码体量爆炸与十几轮三段式修复循环。
3. **计划目标是什么，实施是否偏离？**
   → 相对计划自身目标没有偏离（工程达标）；相对"实质推进论文论证"
   严重偏离——且该偏离恰是上游科学计划 review-remediation 矩阵第 41 行
   明令防范的失败模式。

处置：采纳出口 (b)。锁冻结于 `bdf6a7cb`，F1 记入 backlog（效度修复，
如恢复锁工作则按类修），F2/F3 依右规模化威胁模型裁定为非阻塞并
记入未来论文 §Limitations 素材；工作重心回到科学计划关键路径。

---

## 1. 三项 P1 的根因：round-2 旧缺陷的"点补丁"复发

Round-5 operational audit（`task-6-final-audit-round-5-operational.md`）
的三项 P1（本评审记为 F1/F2/F3，对应该审计 Findings 1/2/3）与
round-2 operational audit（`task-6-final-audit-round-2.md`，第一次真独立
审计，4×P1 + 1×P2）的旧发现一一对应，全是同一缺陷类被"只补被展示的
那个探针"后残留的口子：

| round-5 P1 | 对应 round-2 P1 | 当时的"修复" | 为何复发 |
|---|---|---|---|
| **F1** `APIKey`/`APIToken` 全大写缩写绕过凭证扫描（`_reject_credential_metadata` 的拆词正则 `([a-z0-9])([A-Z])`） | #4 凭证只查少数精确键，不查复合键 | Repair G/G2/I 加了 `api_key`/`apiKey`/`client_secret` 等字面量 | 拆词正则结构上拆不开全大写缩写串：`APIKey`→单组件 `apikey`，不与 `{key, secret, token, …}` 相交 |
| **F2** freeze 校验后、四条 git 查询前 `.git` 元数据可被竞态改写（`_run_fixed_git_queries` 无描述符/快照绑定） | #2 五条 git 查询未中和仓库可控的 fsmonitor/config 面 | Repair D/D2/E 挡住了子进程执行（绝对 `/usr/bin/git`、最小环境、四查询架构） | 只堵了"执行"，没堵"被查询的 `.git` 字节 = 被校验的字节"，留下 TOCTOU 窗口改身份输入 |
| **F3** verify 侧 subject 清单 `_capture_tracked_source_manifest` 路径可竞态藏文件（目录枚举按路径名而非持有的父 FD） | #5 用两次实时读而非一次锚定快照 | Repair A/H 用 dirfd 锚定单读 | 只锚了 controller 侧，subject 侧原样保留（非对称修复）；`run_records.py`/`packages.py` 同款模式残留 |

**共同根因（一句话）**：审计给出一个失败探针 → 实施者对"这个探针"写
RED/GREEN → 独立复审只看这段 scoped diff 就 PASS → 没有人把"整个缺陷类"
用枚举/模糊的心态重跑一遍。于是每轮审计只要换一个同类实例就会重新命中。
凭证是"只处理展示过的驼峰形式，没归一化 ALL-CAPS"；git 是"只挡执行，
没绑字节身份"；源捕获是"改了 controller 忘了 subject"。

### 避免复发的三条做法

1. **按类修，不按例修**：凭证应改成"键 → 归一化 token 集合"的统一函数
   （同时覆盖 snake/camel/ALL-CAPS/连字符），并对该函数做属性测试
   （随机大小写/分隔符生成，断言含 key/secret/token/password/authorization
   语素者必拒），而不是逐个字面量加 RED。
2. **对称性检查清单**：任何"controller 侧修了"的加固，必须显式回答
   "subject 侧/其他调用点是否同款"。三处里两处是遗漏兄弟调用点。
3. **复审升级**：独立复审除了看 scoped diff，必须对被触碰的缺陷类做一次
   全量对抗重扫（把该类的所有输入形态、所有调用点列出来逐一验证），
   否则 "scoped PASS" 名不副实——round-4 会话内做的正是 scoped 式复核，
   没抓到，这就是教训。

---

## 2. 为什么一个"验证步骤"跑了 18+ 小时

**时间线**（authority-lock 谱系 39 个 commit，含两个设计 commit）：
设计 `2db498bd` 08-11 10:15 → 最新 `bdf6a7cb` 08-12 05:57，
净墙钟约 **19.7 小时**。其中 Task 6 一个步骤（自 `b98ec3eb` 08-11 18:13 起）
就吃掉约 **11.7 小时**，衍生出 Repair A、B、C、D、D2、D3、E、F、F2、G、
G2、H、I 共 **13 个修复子循环**、24 份 review diff、多版验证报告
（round-2/3/4/5）、三轮双审计（round-2/4/5）。

四个原因，按影响排序：

1. **Task 6 从"验证"退化成"无界加固"。** 它本该是"冻结→跑测试→双审→
   记结论"（计划原文 Step 1–6），却变成对抗式安全加固的漏斗。因为威胁
   模型是"证据包作者是敌手，控制 `.git`、能协同 reseal、能打 TOCTOU"——
   这个攻击面本质无界，每轮审计都能发明新边角，所以永远收不了口。
   第 §1 节的点补丁又让旧洞复发，进一步拉长。
2. **测试太重且慢。** 849 个 P3 测试在干净 worktree 约 6 分钟
   （实测 344–389 s），在主仓因为要遍历 1.4 GB 未跟踪内容做逐字节哈希
   达 39 分钟。13 个修复
   循环里每次都跑全量 P3（多次 340 s+），仅测试执行累计就是数小时。
3. **代码体量爆炸。** `scripts/p3_v3/evidence.py` 4886 行、
   `src/p3_v3/bridge_and_frames.py` 4322 行、`tests/p3_v3` 合计 16952 行，
   全为一个"验证器"服务。体量本身来自加固螺旋，反过来又拖慢每轮迭代。
4. **RED/GREEN + 独立复审 + 全量回归的三段式被重复了十几遍**，本是好流程，
   但套在一个无界目标上就成了时间黑洞。

### 完善意见

1. **给 Task 6 类验证步骤设硬性收敛准则**：预先冻结威胁模型清单（N 条），
   审计只在这 N 条内判 PASS/BLOCK；新发现的攻击向量若不在清单内，记入
   backlog 而非无限追加 Repair。否则对抗式审计对无界面永远能产出新 P1。
2. **右规模化威胁模型（关键，见 §3）**：证据包作者就是研究者本人。
   防"研究者用 `.git` symlink TOCTOU 伪造自己的结果"不对应任何评审要求。
   把威胁模型从"敌手自证"降到"防意外篡改/防传输损坏"，攻击面立刻有界，
   三项 P1 里 F2/F3 直接降级为非阻塞。
3. **拆快慢测试层**：把遍历真实大目录的测试隔离成单独 marker，日常迭代
   只跑核心逻辑层（秒级），全量只在冻结前跑一次。
4. **合并冗余 Repair 提交**：13 个子循环说明缺陷是分批发现的；根因批处理
   （先全类扫描列全清单再统一修）能把轮次从十几个压到两三个。

---

## 3. 计划目标是什么，实施是否偏离

**计划自身的目标（逐字，plan L8–11）**：

> Replace the circular sole-index evidence verifier with a deterministic
> external Authority Lock whose independently supplied SHA-256 binds
> controller and subject bytes, complete job intents, retry policy, origin
> authority, and observational completion counts.

设计 §2 的声明天花板写死（design L48–56）：它只能证——

> Given an independently frozen Authority Lock digest, the verifier detects
> divergence between the locked execution authority and the indexed evidence
> package.

——不证任何实验跑过、P12 访问过、任何 RQ 被支持。claim ledger v1.3
（`research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md` 对应 ledger）
8 条声明全部 `blocked`，且明确注记合成基础设施路径不记录任何科学结果、
不能升级任何声明。

判断分两层：

1. **相对计划自身目标——没有偏离。** 实施忠实地在造这把锁，Task 1–5
   交付了 freeze/verify、机械 job 派生、attempt 重建、Origin/Index V3、
   原子写入、受锁 adapter。规格审计 round-2/4/5 均判 PASS。工程上是达标的。
2. **相对上位目标"实质推进论文论证"——严重偏离。** 这把锁是证据完整性
   工具，按设计对 RQ1–RQ4 和 C1–C8 的贡献恒等于零。它是在还没有任何证据
   时先造一个防篡改保险箱。论文要的是实验结果（RQ 被回答），而这 19.7
   小时没有产生一个语义变异体、一次 MR 执行、一个 RQ 数据点。

**最有力的证据**：治理这一切的科学计划
（`docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md`）
在 review-remediation 矩阵第 41 行自己预警过这个失败模式：

> | Audit infrastructure could delay the scientific experiment indefinitely
> | Adopt a minimum-evidence foundation and defer generic schema, governance,
> and orchestration frameworks |

翻译：审计基础设施会把科学实验无限期拖住，对策是"采用最小证据基础，
推迟通用 schema/治理/编排框架"。而 Authority Lock 计划恰恰造出了被叮嘱
要推迟的那类治理/验证框架，并如预言般被拖住。**这不是实施偏离了计划，
是计划本身偏离了它上游科学计划的明令。**

同计划 §18 亦规定："Each deliverable must demonstrate one end-to-end
synthetic or pilot path **before additional framework work is considered**"，
且 deferred 清单点名 generic claim-state framework、one-shot authorization
protocol、launch-packet self-hashing 等——均为本轮加固螺旋触及的方向。

---

## 4. CLAUDE.md §10.1 过度防御审计分类

按项目规则 §10.1，对本轮处置逐条分类：

| 项 | 处置 | 分类 | 辩护 |
|---|---|---|---|
| F1 凭证缩写绕过 | 记入 backlog：如恢复锁工作，改"键→归一化 token 集合"统一函数 + 属性测试（按类修） | **效度修复（保留）** | 凭证泄漏是真问题，与威胁模型规模无关；修复保护证据包不携带秘密 |
| F2 `.git` 元数据 TOCTOU | 依右规模化威胁模型裁定为**非阻塞**，记入 §Limitations 素材，不再打补丁 | **主张收缩（辩护通过）** | 证据包作者即研究者本人，"防研究者对自己 TOCTOU"不对应任何评审要求；防意外篡改由现有四查询+字节哈希已覆盖 |
| F3 subject 清单路径竞态 | 同 F2 | **主张收缩（辩护通过）** | 同上；对诚实作者的复现包，传输损坏由包级 SHA-256 覆盖 |
| 继续 round-6 无界加固 | **停止** | **过度防御（禁止）** | 属"逃避证伪风险式过度防御"的镜像——以无限加固回避收口；不保护任何推断效度 |
| N（crash-durability 残留） | 保持审计记录原状 | 非阻塞 | 审计自身已裁定 "not a path to an incorrect verification PASS" |

结论：F1 保留为效度修复类 backlog；F2/F3 的非阻塞裁定属于有辩护的主张
收缩（威胁模型右规模化），不属于逃避证伪；round-6 停止。

---

## 5. 处置（出口 (b)）

用户在两个务实出口中选定 **(b)**：

- (a) 若确需此锁：按 §2 右规模化威胁模型，F1 按类修一轮收口，
  F2/F3 显式裁定为非阻塞并记入 §Limitations。
- **(b) 冻结这把锁于当前状态，回到科学计划的关键路径——实际执行语义
  变异实验去产出 RQ 证据。** ← 已采纳

落地动作：

1. 本评审文档落档（本文件）。
2. Authority Lock 实施计划追加 Freeze Record：终态 `FROZEN — 出口 (b)`，
   冻结 commit `bdf6a7cb`，849/849 测试回执，F1→backlog，F2/F3→非阻塞
   裁定，round-6 不授权。
3. 回归计划 `2026-08-12-p3-return-to-scientific-critical-path.md`：
   按科学计划 §14/§18 恢复 Phase 0（协议冻结）→ Phase 1（P12 盲桥）→
   Phase 2（preflight/剖析）→ Phase 3（语义变异体构造）的推进次序，
   并内置本评审 §2 的四条收敛准则（有界威胁模型、审计范围冻结、
   快慢测试分层、根因批处理）。
4. Authority Lock 定位重述：**reproducibility 支撑件**，不在论文论证
   关键路径上；对诚实作者复现包，当前对抗式加固程度已超出需要，
   冻结态足以服务后续 replication 包装配。

---

## Provenance 与证据锚点

- 评审证据采集与结论形成于 read-only 会话（2026-08-12），未改任何代码；
  本文件为该评审的落档，落档前已逐项核实以下锚点：
  - 谱系时间线：`git log 2db498bd..bdf6a7cb`（39 commits 含设计双 commit；
    08-11 10:15 → 08-12 05:57）
  - Task 6 起点：`b98ec3eb` 08-11 18:13 "test(p3-v3): close authority lock
    evidence matrix"
  - round-2 审计原文：4×P1+1×P2，#2/#4/#5 措辞与 §1 表格逐字一致
  - round-5 operational 审计原文：3×P1（F1/F2/F3）+1×N，verdict BLOCKED；
    round-5 specification 审计 verdict PASS (0 load-bearing findings)
  - 代码体量：`evidence.py` 4886 行 / `bridge_and_frames.py` 4322 行 /
    `tests/p3_v3` 16952 行（`wc -l` 实测）
  - 科学计划矩阵第 41 行原文（文件物理第 41 行，逐字核对）
  - 冻结点测试回执：`849 passed in 344.01s`，pytest exit 0（2026-08-12，
    干净 worktree，anaconda Python 3.12 + pytest 8.4.2，**沙箱外**运行；
    注意：Cursor shell 沙箱内同一 commit 会假性报 158 failed + 57 errors，
    集中于 preflight/capability 探针，勿以沙箱内结果作回执）
- SDD 审计工作区（git-ignored，位于 mef-align-repair-01 worktree）为
  round 级审计与 repair 报告的持久痕迹；本文件不复制其全文，仅存索引。
