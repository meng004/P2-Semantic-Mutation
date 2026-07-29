# 独立形式审计协议（Task T6.2）

- 日期：2026-07-29
- 审计人要求：未参与实证分析与定理起草的独立方。本轮执行：跨家族模型审计
  （起草=fable 系；审计=gpt 系 `gpt-5.6-sol-xhigh`，计划约定 terra 不可用时
  的同族最强替代），满足"审计者与被审产出不同源"的分派原则；外部人类同行
  复审可在此报告基础上追加，不被本轮替代性排除。
- 输入：
  1. `research/theory_drafts/notation_registry.md`（符号闭集 + 标签映射）
  2. `research/theory_drafts/thm_interval.md`
  3. `research/theory_drafts/thm_gap.md`
  4. `research/theory_drafts/thm_window.md`
  5. `research/theory_drafts/rem_identifiability.md`
  6. 整合稿 `submission/TOSEM_regular_20260706/main.tex` §2（含 §2.6 修补、
     §2.9 Theorem 3、§2.10–2.11）与 `supplementary.tex` Appendix G.2–G.8
- 审计顺序：**THM-GAP（Theorem 5）优先**（清单第 4 项提前）——预注册包依赖
  其内部评审版；若出 blocker 按预注册 amendment 程序处理（AMENDMENTS.md，
  F-7），不回溯撤销已生效冻结。

## 固定 8 项清单

| # | 项 | 通过标准 |
|---|---|---|
| 1 | 每个定理前提在正文有定义 | Theorem 3/4/5、Lemma 4.1/5.1、Corollary 5.1、两个窗口 Remark、辨识 Remark、Theorem 9.1(修) 的每个前提符号与条件均可在 §2 或 Appendix G 找到定义 |
| 2 | 无循环 | 结论不作前提：依赖图 Theorem 2→Lemma 5.1→Theorem 5→Corollary 5.1；G.8 regime→Lemma 4.1/Theorem 5(iii)；Theorem 3 不依赖 4/5；无回边 |
| 3 | Lemma 4.1 的 AVP 决定性假设成立范围 | 确定性 PUT 精确；随机 PUT 按 N=20 聚合语义（G.6 scope 段）；R2 稳定性条款在假设中显式且有不可删论证 |
| 4 | Theorem 5 的 S5/exact-checker 前提与 ξ 报告一致 | 前提理想化 + A-PROV 桥 + ξ 量化偏差的分工无自指；"S5 不满足者入 ξ"注记在场；ξ 不入 SMS |
| 5 | Theorem 3 常数与 Lipschitz 假设可满足性 | H-a/H-b/H-c(R1,R2)/H-d 表述一致；2η̄ 与 pη̄ 泛化自洽（MP_3 p=4）；L_r 仅承载剂量转移不承载 (i)–(iii) |
| 6 | Theorem 9.1(修) 支撑假设与例外集表述 | supp(𝒟_P)⊇X_adm 在陈述与 G.3/G.4 一致且被证明实际使用；例外集二选一表述主稿/附录一致；L_lim/L_switch 两读法恒等无歧义 |
| 7 | 记号与 registry 零冲突 | 整合稿新增符号全部落在 36 项闭集 + 标签映射内；保留符号（MLP α、σ_out、统计 α、附录 H 复数 α）逐处审计合规；k 计数与 k 索引的 local-scope 隔离在场 |
| 8 | 证明步骤逐行可复核 | G.6–G.8 每步引用已有定义/结果；不等式代数复算无误；无隐含假设 |

## 意见分级与处置

- **blocker**：健全性/循环/前提未定义/代数错误——回对应 Phase 修正后重审该项。
- **minor**：表述精度/一致性/可读性——正文修订即可，随修随记。
- 全部关闭后在报告尾部签：`AUDIT PASS + 日期 + 草稿 SHA256`
  （`shasum -a 256 research/theory_drafts/*.md`）。
