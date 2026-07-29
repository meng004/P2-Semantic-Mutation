# 独立形式审计报告（Task T6.2）

- 协议：`docs/review_20260728/formal_audit_protocol.md`（固定 8 项清单，THM-GAP 优先）
- 审计人：gpt 系模型 `gpt-5.6-sol-xhigh`（独立子代理，未参与 T1–T5 起草；起草方为 fable 系）
- 被审对象：五份理论草稿 + 整合稿 main.tex §2（§2.3/2.6/2.7–2.11）+ supplementary.tex Appendix G.2–G.8
- 轮次：3 轮（Round 1 全量审计 → Round 2 处置复核 → Round 3 终验）
- 结论：**AUDIT PASS**（全部发现闭合）

## Round 1 逐项裁定（2026-07-29）

| # | 项 | Round 1 裁定 | 终裁 |
|---|---|---|---|
| 1 | 前提定义 | BLOCKER（B2/B6） | PASS（修复后） |
| 2 | 无循环 | PASS | PASS |
| 3 | AVP 决定性范围 | PASS | PASS |
| 4 | THM-GAP 前提与 ξ 一致 | BLOCKER（B1） | PASS（修复后） |
| 5 | THM-WIN 常数可满足性 | BLOCKER（B2/B3） | PASS（修复后） |
| 6 | THM-DEG-R 支撑假设与例外集 | BLOCKER（B4/B5） | PASS（修复后） |
| 7 | 记号 vs registry | BLOCKER（B6 记号部分） | PASS（闭集扩至 40 项） |
| 8 | 证明逐行可复核 | BLOCKER（与 B1–B5 同源） | PASS（指定代数全部复算通过） |

## 发现与处置（全 9 项）

| ID | 发现 | 级别 | 处置 | 状态 |
|---|---|---|---|---|
| B1 | ξ 零分母未定义；"S5 违规 kill 全部入 ξ"过强（对角 kill 不可见） | blocker | ξ 定义补 NA-when-zero-kills 约定 + 单侧性声明（观测 ξ 是前提违背质量的下界）；main §2.11、supp G.7、thm_gap.md §2/§3/§7/§9b 五处同步 | CLOSED（R2 复核发现 §9b 残句，R2 后闭合） |
| B2 | THM-WIN 陈述缺承重假设（H-a/R1/H-d 仅在证明中使用）；P⋆ 与被评估原程序关系未锚定 | blocker | **修订 A4**：假设升入陈述，P⋆ 钉为 cell 原程序（S2 正确性假设）；master→phase T3→thm_window.md→main §2.9 四处同步 | CLOSED |
| B3 | REM-FPOS 过强：μ_r<0 只保证存在超 ε_tol 残差输入，不保证被采样且抗噪标记 | blocker | **修订 A5**：分层表述——超 ε_tol 输入存在；执行残差超 ε_tol+2η̄ 时保证标记；该级输入存在 ⟺ μ_r<−2η̄；带内噪声可掩盖。R2 发现证明段先断言后收回的矛盾，R3 改为单遍分层论证后闭合 | CLOSED（3 轮） |
| B4 | Lemma 9.2 的 L4 允许 r≠id，退化目标非经典同输入差分 | blocker（既有稿件缺口） | L4 定义强制 identity source transformation（r=id）；main §2.6 两处、supp G.2 表+重组段、G.3 Lemma 9.2 证明重写 | CLOSED |
| B5 | Lemma 9.1 证明借用未假设的 L6、误称 E1 为类型一致性、连续域"遍历"表述不实 | blocker（既有稿件缺口） | 陈述补"fix L_switch"；E1 改为 AVP coherence 的极限平凡性论证；E2 分浮点有限域（almost-sure 穷尽）与连续域（𝒟_P-a.e.，显式声明不主张逐点等式）两支 | CLOSED |
| B6 | THM-INT 缺 n≥1；SMS(R) 未定义 | blocker | **修订 A6**：n≥1 入陈述（master/phase/draft/main 同步）；main §2.11 首用处定义 SMS(R) | CLOSED |
| M1 | N≥A² 整数边界的充分性 | minor | G.8 已有"necessary in general, sufficient with strict inequality"，采纳为处置 | CLOSED |
| M2 | L_r 逐 PUT 可估性清单未入附录 | minor | G.8 H-b 段补 per-class 可估性句（dose-response 消费限于可估子集并预注册） | CLOSED |
| M3 | kill 矩阵 incidence 语义不明 | minor | main §2.11 声明 binary incidence + OR 聚合 | CLOSED |

记号闭集：#37 SMS(R)、#38 ε†、#39 Φ_Q、#40 p 补录（均为冻结陈述/范围注记
中已使用符号的显式入册，非新增理论对象）；闭集 36→40 项。

## 完整性抽查（Round 1，(a)–(e) 全过）

(a) "Proposition 2" 两份 .tex 零出现；(b) Theorem 3 与冻结基线语义一致；
(c) §2.10–2.11 含 A1/A2/A3 修订；(d) claim-evidence map 三行 Supported
(formal)；(e) RQ1 含 soundness/monotonicity/degeneration/attribution。
em-dash（U+2014）两份 .tex 零出现（R2 复验）。

## 修复 commit 链

`7faf32f`（A4–A6 + D 组主修复）→ `4a27604`（B1/B3 残余）→ `57c5717`
（B3 单遍分层论证终稿）。修复类别核对（CLAUDE.md §10.1）：全部 9 项均为
**效度修复**（前提显式化、定义补全、单侧性承认、论证矛盾消除），无主张收缩
——THM-WIN/INT/GAP 的可证伪预测（H-DOSE/H-XI/H-ZERO/H-DISC 通道）不受影响，
REM-FPOS 分层化使其*更*可检验（μ_r<−2η̄ 是可测条件）。

## 签署

**AUDIT PASS — 2026-07-29**

草稿指纹（SHA-256，签署时点 = commit `57c5717`）：

```
b41630d3d2c40dd54f14bef9d5199573b63ec5dcb2ee2b8097b19d6d7eb50756  notation_registry.md
e26d76756a7655cdecb8b3f8c1fc0c30badef7e4294e7555acd4ba427bef3a4a  thm_interval.md
8415d1d5a9b1e70d2d7d3362029a2eab30e7ae94a88dccd659515c0715690ba5  thm_gap.md
24fb826d9cb4aedf95bbd36ce3538301e9256f3d9a10bd8422d924d0eec4c4b0  thm_window.md
8a2dbca9534dc005d2acb10c371ac72626e2699b2ce701a13f40a69d7e9eb58c  rem_identifiability.md
```

外部人类同行复审可在本报告基础上追加（协议保留 ≤2 周窗口选项）；本轮
跨家族模型审计满足"审计者与被审产出不同源"的独立性要求。
