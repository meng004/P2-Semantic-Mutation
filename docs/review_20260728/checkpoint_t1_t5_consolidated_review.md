# T1–T5 检查点联合复审记录（委托执行，2026-07-29）

- 指令："请先执行完整phase-T4，评审T1-T5的checkpoint。"
- 范围：CHECKPOINT T1 / T2 / T3(+T4) 三份既有记录的交叉再验证 + T5 交付物
  评审（计划未给 T5 设专属 checkpoint，其正式审计位=T6.2 清单项 (6)；本节
  按同等纪律补做交付物复核，不替代 T6.2）。
- 前置动作：Phase T4 完整化——Task T4.1 Step 2 的"论证并入 THM-GAP 讨论段"
  由指针升级为实际并入（`thm_gap.md` §9c：A3 修订后 Remark 全文 + 两句论证；
  commit `48effbb`）。T4 至此三步全闭合。

## 1. 交叉再验证结果（修订相互作用）

| 检查项 | 结果 |
|---|---|
| A1/A2（T1 修订）在 B2 拆分后仍自洽 | ✓ LEM-WIT 的稳定性条款经消费映射对应 R2；`thm_interval.md` §3 原以"the non-degenerate-margin regime"整体指称，已精确改指 R2（修复 **C1**） |
| A3（T4 修订）对 T2 记录的传播 | ✓ 过时标题 "identifiability up to coverage classes" 全库零残留（T4 并入时一并消解，即 C2）；`thm_gap.md` §9c 与 master/phase/rem 三处陈述一字一致（特征短语四处命中） |
| B1（T2 修复）与 B2（T3 修复）的接口 | ✓ THM-GAP premise (iii) 引入链指名 R1+H-a；LEM-WIT 指名 R2；无循环（THM-WIN 不依赖二者） |
| T1 演示可复现性 | ✓ `interval_demo.py` 重跑，`git diff data/results/interval_demo_v4.json` 为空（确定性） |
| 草稿符号闭集 | ✓ 四份定理草稿零违规（registry 冲突表自述条目除外） |
| .tex em-dash（U+2014） | ✓ main/supplementary 均为 0 |

## 2. T5 交付物评审（补做；正式审计仍归 T6.2 项 (6)）

| 项 | 结果 |
|---|---|
| L 拆分（L_lim/L_switch，两读法恒等，箭头 \(\xrightarrow{L_{\mathrm{lim}}}\)） | ✓ main §2.6 + supp G.2/G.4；遗留 "L=L1∧L2∧L3" 撞名两处已修 |
| supp(𝒟_P) ⊇ X_adm 显式假设 + 不可删反例 | ✓ Thm 9.1（main+G.4）与 Lemma 9.1（G.3）；G.3 证明的 \(\forall x\in\mathcal X_{\mathrm{adm}}\setminus N\) 类型修正使假设真正承重 |
| a.e. → 二选一例外集表述 | ✓ 定理/引理层全部替换；§1/§4 顺带提法留 T6 写作层（有意） |
| scoped rename（D_S→𝒟_P 限 §2.6+G.2–G.4） | ✓ 范围内零残留；范围外残留=main.tex:605（§2.3 E2）、1543、1595 与注记行 709，全部属 T6.1 全文扫尾清单 |
| 三态声明（§2.3）与坍缩句（§2.5） | ✓ 状态名与 DEF-01 逐字一致；v4 空集事实（无回溯数字改动）如实入文 |
| **C3（实质发现，已修）** | §2.3 段落原用 \(k/n\)、\(k/(n+u)\)，与同小节 \(\mathrm{MR}_{i,k}\)/\(\mathrm{SMS}_{i,k,j}\) 的关系索引 \(k\) 撞名——改为散文表述（killed fraction / divides the same killed count by …），公式留给 T6 整合的定理节；registry 冲突表新增 \(k\)（索引 vs 计数）行，T6.1 承担 local-scope 首用限定句 |
| 编译复验（C3 修后） | ✓ 仍恰 1 个 pre-existing `\Bbbk` preamble 错误（与基线同环境对照一致）、0 新增、0 Missing character；归档 PDF 恢复未动 |
| SSOT 双口径键迁移通知（Step 2b） | ✓ 已由 commit `076a8d6` message trailer + phase 文件记录承载 |

## 3. 修订与修复台账（累计）

| 编号 | 层级 | 内容 | 状态 |
|---|---|---|---|
| A1 | 陈述修订（T1） | LEM-WIT margin 稳定性条款升入假设 | 落地，三处同步 |
| A2 | 陈述修订（T1） | THM-INT R⊆R′ 句加三态分类冻结限定 | 落地，三处同步 |
| A3 | 陈述修订（T4/T3 检查点） | REM-IDF survivor 从句过度主张改述 | 落地，四处同步（含 §9c） |
| B1 | 草稿修复（T2 检查点） | premise (iii) 显式引入 H-a+R1 链 | 落地 |
| B2 | 草稿修复（T3 检查点） | regime 拆 R1/R2 + 消费映射 + pη̄ 括注 | 落地 |
| B3 | 草稿修复（T3 检查点） | 噪声界置信读法 | 落地 |
| C1 | 一致性修复（本轮） | thm_interval §3 指名 R2 | 落地 |
| C2 | 一致性消解（本轮，随 T4 并入） | 过时 Remark 标题清零 | 验证 |
| C3 | 稿面修复（本轮） | §2.3 计数符号撞 \(k\) 索引 → 散文化 + registry 行 | 落地，编译复验 |

## 4. T6 handoff 检查单（自各记录汇总，供 T6.1/T6.2 直接消费）

1. 五处全文改名（σ→eff、I→Ψ、D_S→𝒟_P 扫尾、α→obs、e/P_e→edit/P_edit）——
   行号以 registry 漂移注记为准，改前重扫。
2. 严格超出约定写入 DEF-05 整合文本（T3 记录 Q3）。
3. 计数符号 \(n,k,u\) 在理论节首用处加 local-scope 限定句（C3）。
4. THM-WIN §4 regime（R1/R2）须随定理落稿，保证 LEM-WIT/THM-GAP 引用在正文
   内解析。
5. "S5 不满足者计入 ξ" 正文注记（T2.2 handoff）；LRCA §2.4 替换句
   （rem_identifiability.md §3，对准 main.tex:646–649，行号改前重扫）。
6. 草稿移植时执行 em-dash 纪律（草稿 md 中的"—"不得带入 .tex）。
7. Ψ 非冗余 standing convention 在 Ψ 引入处声明一次（T2 记录 Q3）。
8. 区间宽度-证书预算曲线素材需非零 u 数据源（T1 记录移交项）。

## 5. Reviewer 2 视角的最严苛审稿意见

- （已修复，本轮内关闭）C3：\(k\) 计数与 \(k\) 关系索引在同一小节撞名——
  若带入投稿属"符号系统失控"级低级伤；已散文化并入 registry 裁决。
- （已修复，本轮内关闭）C1：跨修订指称漂移（整体 regime vs R2）。
- 其余：三份检查点记录的结论在修订相互作用下均保持成立；T5 稿面改动与
  基线对照编译零新增错误；无新的效度或诚信问题。
- Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。

## 6. 过度防御审计（CLAUDE.md §10.1）

C1/C2/C3 均为一致性/效度修复，无主张收缩；A/B 台账维持原判定（A3 为纠错
非缩水，B 组为假设可见性）。无需回调项。

## 7. 结论

- **Phase T4 = 完整**（三步全勾，讨论段实际并入 §9c）。
- **CHECKPOINT T1 / T2 / T3(+T4) = PASS 维持**（交叉再验证通过，C1–C3 修复
  后无遗留不一致）。
- **T5 交付物 = 评审通过**（C3 修复后；正式审计位仍为 T6.2 项 (6)）。
- **T6 前置全部满足**，可执行；预注册冻结门禁（R-5）维持开启状态。
- 作者保留否决权：对任何裁定或修复另有偏好，按"先改 master 再同步"程序修订。
