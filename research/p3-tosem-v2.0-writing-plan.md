# P3+P6 合并稿撰写计划（TOSEM v2.0）

> 状态：执行计划（2026-07-28）。基线稿：`submission/TOSEM_regular_20260706/main.tex`（2,645 行，IST 拒稿后已并入部分 P6 理论）。
> 上游：`research/p3-tosem-redesign-rqs-v2.0.md`（RQ 与定理群设计）、四柱理论 v1.2、`research/fable-p3-p12-new-argumentation-plan.md`（证据规则）。
> 纪律：旧 H1–H4 原样保留为 Prior Audit；新假设另行预注册；旧 60-cell 数据 development-only；全部数字出自单一 SSOT。

---

## 0. 现稿基线盘点（keep / revise / new）

| 现稿章节 | 现状 | 处置 |
|---|---|---|
| §1 Intro + three-layer framework + claim-evidence map | 已收缩为构念论文 | **Revise**：换旗舰主张、新 RQ 表、加论文 2 边界段（concurrent TOSEM submission） |
| §1.4 RQ1–RQ5 | RQ1 理论、RQ2 AST、RQ3–5 实证 | **Revise**：重编为 RQ1–RQ5 新版（见 §2） |
| §1.5 H1–H4 | H2 已标 exploratory | **Keep as Prior Audit**（移入 §4 开头小节），新增预注册假设组 |
| §2.1–2.6 SMS 度量、E1∧E2、LRCA、退化定理 | 完整 | **Keep + Repair**：9.1 补支撑假设与 a.e. 表述；L 拆为 L_lim/L_switch |
| §2.7–2.9 fiber 理论、Thm 1/2、Prop 1/2 | P6 种子已并入 | **Keep + Extend**：Prop 2 升级为 Thm C 定量版 |
| （无） | — | **New**：§2.10 Thm A 区间健全性；§2.11 Thm B 缺口归因；§2.12 Prop D 可辨识性 |
| §3 Study design | 60-cell、cosmic-ray、cross-source、prescreen、LRCA | **Keep + Extend**：适用矩阵、剂量反应、held-out source、外部切片准入协议、baseline 扩充 |
| §4 Results | 按旧 RQ3–5 组织 | **Restructure**：按新 RQ；两部分口径；Prior Audit 小节 |
| §5 Discussion | 解耦、stakeholder | **Revise**：加缺口归因解读（零膨胀的理论确认部分）、SMS vs MS 有界比较、T1/T2/T4 接口段 |
| §6 Threats | R1–R13 | **Extend**：双重使用防火墙、外部切片选择披露 |
| Appendix G | 9.1 证明 | **Extend**：A/B/C/D 全证明 + 独立形式审计报告 |
| Real-defect slice（D0） | result-level，选择偏差 | **Demote**：development/校准角色，披露循环风险；validation 由新切片承担 |
| Adjoint arm | 确证演示 | **Keep** |

---

## 1. 理论增强工作包（WP-T）

| 编号 | 内容 | 放置 | 证明路线 | 难度/工时 |
|---|---|---|---|---|
| WP-T1 | **Thm 9.1 修补**：D_S 支撑假设显式化；浮点域 a.e. 改有限例外集表述；L = L_lim ∧ L_switch 两段式 | §2.6 + App G | 现证明局部修订 | 低 / 3 天 |
| WP-T2 | **Thm A（区间健全性）**：真实 SMS ∈ [SMS_cons, SMS_strict]；被杀 unresolved 自动升格引理；证书单调收窄；MR 扩张两端点单调不减 | 新 §2.10 | 初等组合论证，(k+1)/(n+1)≥k/n | 低 / 4 天 |
| WP-T3 | **Thm B（缺口归因，核心）**：S5 纯性 + 精确检查器 ⟹ kill matrix 块对角；1−SMS = 对齐残余 ⊕ 强度残余，可由 kill matrix + fiber 标签分离；推论：cross MR 预测 SMS=0；块外 kill = 纯性/精确性偏差的可测量 | 新 §2.11 | 由 Thm 2 闭包论证 + S5 展开；对接四柱 T3 残余分解（引用为接口注记） | 中 / 1.5 周 |
| WP-T4 | **Thm C（检测窗定量版）**：Prop 2 升级；Lipschitz 观测 + 噪声界 η 下，必杀/必不杀阈值 (ε_lo, ε_crash)；推论 1 弱 MR FP；推论 2 RNG FN 及 N^{-1/2} 重复处方 | §2.9 原位升级 | 误差预算三角不等式 + 现有 latency window | 中 / 1 周 |
| WP-T5 | **Prop D（可辨识性）**：块结构下 fiber 隶属由 kill signature 辨识至检测矩阵等价类；separating family 时精确；LRCA 重定位为块偏离标注器 | 新 §2.12 | 由 Thm B 直接推论 | 低 / 3 天 |
| WP-T6 | **独立形式审计**：与实证作者隔离的审计人过一遍 A/B/C/D + 9.1；审计报告入 App G.5 | App G.5 | — | 2 周（并行） |

顺序约束：WP-T3 必须在预注册（WP-P）之前完成成文——两部分 estimand 与零预测检验的合法性从它推导。

---

## 2. 新研究问题（论证提升主轴）

| RQ | 表述 | 载体 | 相对现稿的变化 |
|---|---|---|---|
| **RQ1 形式保证** | SMS 作为 MR 集充分性度量给出何种健全性、单调性、退化与归因保证？ | Thm 9.1(修) + A + B；独立审计 | 现 RQ1 扩容：从"能否形式化"升为"给出什么保证" |
| **RQ2 双向对应** | MR 强度与变异体活性的对偶在容差域内何时双向成立？kill 模式能否反推缺陷层？ | Thm C + Prop D + 剂量反应 + 块结构检验 | 新增（吸收现 RQ1(c) 与 RQ4 的 strong boundary 部分） |
| **RQ3 可构造性** | 按预冻结适用矩阵，定向合成能否在 applicable cell 中稳定产出非等价变异体？ | 适用矩阵 + 漏斗审计 | 现 RQ3 改造：分母从 60 cell 全集改为 applicable 子集，"不适用"单列 |
| **RQ4 判别效度（两部分）** | SMS 是否按 Thm B 预测的两部分形式区分对齐/非对齐 MR 集？held-out source 是否复制？ | 零预测分类 + 条件效应 hurdle | 现 RQ4 改造：pooled δ 退位为 Prior Audit，两部分口径上位 |
| **RQ5 外部锚** | SMS 盲测预测能否在准入解耦的真实缺陷切片上校准？SMS 排序是否优于经典 MS 排序？ | 2×2 设计 + 冻结预测协议 | 新增（取代 D0 slice 的 result-level 角色）；现 RQ5 跨类一致性降为 RQ4 的分层报告 |
| （保留）RQ-S 语法不可达 | AST 归一化重叠（多引擎版） | 结构审计 | 现 RQ2 保留为 supporting audit，不再占独立 RQ 位 |

### 新预注册假设组（全部从定理推导，模拟法定功效）

| 假设 | 内容 | 判据草案（预注册时定稿） |
|---|---|---|
| H-B1 | Thm B 零预测：cell 级零/非零分类准确率优于多数类 | balanced accuracy ≥ 0.75，McNemar p<0.05 |
| H-B2 | 条件判别：aligned vs cross 在双方 applicable 且预测非零的 cell 上，条件 SMS 差 ≥ MID | Cliff's δ ≥ 0.33（模拟定功效 ≥0.8 后锁定） |
| H-C1 | applicable cell 非等价实例化率 ≥ 0.5 | Wilson 95% 下界 > 0.5 |
| H-C2 | kill 概率随违反幅度单调（剂量反应） | isotonic 优于常数模型，置换 p<0.05；Page's L |
| H-X1 | 外部切片冻结预测准确率优于多数类基线 | accuracy + Brier，双侧检验 |
| H-X2 | SMS 排序与真实检出排序一致性 τ ≥ MID；对比经典 MS 排序（secondary） | 项目等权 Kendall τ；τ_SMS − τ_MS 描述性报告 |

---

## 3. 评价指标（按 RQ）

| RQ | 主指标 | 辅指标 |
|---|---|---|
| RQ1 | 审计通过/未通过；证明无循环 | 区间宽度 vs 证书预算曲线（Thm A 演示） |
| RQ2 | 块外 kill 率（≤ 预注册上界）；剂量反应单调拟合优度 | 检测窗预测 vs 实测 kill 转折点误差 |
| RQ3 | applicable cell 非等价实例化率（H-C1） | 全漏斗：parse/build/trigger/equiv/unresolved 分层损耗；inapplicable 单列 |
| RQ4 | Part1 balanced accuracy、Brier；Part2 条件 Cliff's δ + BCa CI | hurdle 模型系数；held-out source 方向一致性；SMS_strict/cons 区间宽度 |
| RQ5 | 预测 accuracy/Brier（H-X1）；项目等权 Kendall τ（H-X2） | OUT_OF_SCOPE 份额；映射 κ（≥0.6 门禁）；per-fiber 校准表 |
| RQ-S | AST 归一化精确重叠率（分引擎、分算子族） | 重叠样本的定性归类 |

---

## 4. 实验对象

| 对象 | 规模 | 角色 | 状态 |
|---|---|---|---|
| 12 PUT（4 类 × 3） | 现有 | 主审计域（RQ2–4） | 复用 |
| 追加紧凑核 +4~8 个 | 视功效模拟 | 仅当 H-B2 功效 <0.8 时启用（门禁决定，保持 <2KB float→float 范围） | 条件新增 |
| 参数化算子 HP、CE | 2 算子 × 4 PUT（每类 1）× 幅度网格 ≥6 点 × 20 重复 | 剂量反应（H-C2） | 新增 |
| v4 MR 集（aligned/cross） | 现有 | development：冻结适用矩阵、精确性估计、模拟功效 | 降级复用 |
| held-out MR source（v5） | 新 provider，同 prompt/parser/预算对称协议 | RQ4 确认性判别 | 新增 |
| Defect4MR 重裁切片 | 目标 n≥20 缺陷、≥8 项目（64 候选池按新准入重裁 + 少量新挖掘） | RQ5 validation（准入解耦：真实 + 双臂可复现 + in-scope；可检出性 = 观测结果） | 新增 |
| verified_full 35 缺陷 | 现有 | RQ5 development/校准 only，披露选择条件 | 降级复用 |
| adjoint arm（scipy/pylops/jax） | 现有 | ψ₆ 扩展确证演示 | 保留 |

---

## 5. Baselines

| 实验 | Baseline | 角色 | 理由 |
|---|---|---|---|
| RQ-S 结构重叠 | cosmic-ray 默认（现有）+ **mutmut 默认**（新增） | 语法可达性参照 | 单引擎主张过窄是既有审稿风险；两引擎 + 明示"higher-order 未反驳"边界 |
| RQ4 Part 1 | 多数类预测器；分层随机预测器 | 零预测准确率下限 | 四柱 SQ2 盲测纪律的标准对照 |
| RQ4 Part 2 | cross MR 集（主对照）；**seeded random MR 集**（sanity floor，新增） | 判别效度 | random floor 防"任何对照都赢"质疑 |
| 剂量反应 | 常数模型（无响应零假设） | 单调性检验 | 标准 |
| RQ5 预测 | 多数类；**Pattern Coverage 排序**；**经典 MS 排序（mutmut kill rate）** | "SMS 是否带来增量"的有界比较 | 审稿人必问"为什么不用 MS 就够"；有界样本上正面回答，不做普适优越主张 |
| 等价判定 | E1-alone、E2-alone（现有 App A.3） | 消融 | 保留 |

---

## 6. 执行顺序与门禁（约 14–16 周）

| 阶段 | 内容 | 工时 | 门禁 |
|---|---|---|---|
| G0 | SSOT 冲突修复（v4 δ）+ CI 数字比对管线 | 1 周 | diff=0 才启动后续 |
| G1 | WP-T1–T5 定理成文 | 3–4 周 | 内部证明完整 |
| G2 | WP-T6 独立形式审计（并行启动） | 2 周 | 审计通过；否则回 G1 |
| G3 | 预注册包冻结：适用矩阵（由 v4 数据 development 冻结）、H-B/C/X 全组、MID、功效模拟、分析代码、外部切片准入条件、fiber 映射协议 | 1–2 周 | 预注册文档 + 时间戳 |
| G4 | E2/E3 构念线：新变异体生成、held-out source、剂量反应 | 4–6 周 | 漏斗与结果入 SSOT |
| G5 | E4 外部线（与 G4 并行启动）：重裁准入 → 双评者盲映射（κ≥0.6）→ 冻结预测 → 执行 → 揭盲 | 6–10 周 | κ 门禁；预测冻结哈希 |
| G6 | 手稿重构写作（§0 处置表执行）+ 图表重生 | 3–4 周（与 G4/G5 尾部重叠） | 全数字 SSOT 注入 |
| G7 | 提交前流水线（CLAUDE.md §3）：academic-pipeline → 引文核验 → proofread → humanizer → 构建验证 | 1–2 周 | 全绿 |

---

## 7. 写作层面的关键决策

1. **旗舰主张一句话**：SMS 是对声明语义层健全（区间）、可归因、可经验校准的 MR 集充分性度量；证据为定理群 + applicability-aware 审计 + 准入解耦真实缺陷校准。
2. **零膨胀叙事翻转**：§4 先报 H-B1（预测准确率），再报 Prior Audit 的 H1–H4——让审稿人先看到"理论预测了零"，再看到旧阈值失败的历史。
3. **贡献边界段**（§1）：论文 2（TOSEM 在审）回答"MR 从哪里来"；本文消费其元模式为词汇，回答"MR 集够不够"；论文 5 的证书体系以轻量资格协议（来源/适用域/容差）接口化，一段带引即可。
4. **D0 切片降级措辞**："development-only calibration evidence, selection-conditioned"；validation 语义全部让位给新切片。
5. **双重使用防火墙声明**（§6 Threats 新条目）：旧 60-cell 数据的全部用途列表（适用矩阵、精确性估计、功效模拟），确认性结论零依赖。
6. **符号注册表冻结**：≡_α、strong/weak、τ、fiber 与论文 2/4/5 共用口径，提交前 diff 一次统一框架附录 A。
7. **arXiv 预印本**与 TOSEM 投稿同步挂出（合并稿），给论文 5 写作提供可引锚点。

## 8. 降级路径（预注册进论文）

| 触发 | 路径 |
|---|---|
| H-C1 失败 | 身份降为"构念 + Thm B 归因的负结果论文"；RQ4/5 降 Appendix |
| H-C2 不单调 | Thm C 前提失效诊断入 Threats；构念效度只靠 H-B1 |
| H-X1/X2 无信号 | 主张收缩为有界不一致 + Thm B 归因（哪种残余主导）；仍为可发表效度边界结果 |
| κ<0.6 | 协议迭代一轮重测；仍不达则 DIRECT 主分析降敏感性分析 |
