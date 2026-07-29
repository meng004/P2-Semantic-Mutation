# ACM TOSEM 审稿意见：source/main.tex

- 日期：2026-07-29
- 评审对象：`source/main.tex`（唯一可信来源；必要处对照 `source/supplementary.tex` 与 `data/results/*.json`）
- 评审架构：三个互相隔离的只读评审线程（方法与统计 / 形式理论 / 贡献与呈现），主线程取证复核后合成
- 推荐等级：**Major Revision（大修）**
- 置信度：高（复核了全部证明链并对照冻结数据逐值核算）

---

## 一、论文概述（审稿人复述）

论文提出 Semantic Mutation Score（SMS）：把变异测试的分母从句法变异体改为"经认证的领域语义效应层"，用于度量金属关系（MR）集合对声明语义风险的充分性。贡献分四层：(1) 形式层——SMS→MS 退化定理、不可判定性、strong-MR 对偶、检测窗/区间健全性/缺口归因定理；(2) 度量与证书模型（三态等价、LRCA 诊断层、ξ 精确性缺陷审计）；(3) 12 PUT × 5 MP 的 60 格实证审计（四个预注册假设：H1–H3 未达标，H4 判不可评估）；(4) 边界研究、伴随扩展臂与 34 案工业真缺陷臂支撑"kill-rate、语义对齐、真缺陷检出是相关但不同构念"。

## 二、总体评价

这是一篇**诚实性和基础设施质量显著高于平均水平**的投稿：推断权限表逐统计量限定读法、预注册失败如实报告、数据驱动选择用置换检验撤回、ξ=0.765 这种对自家理论前提不利的测量主动披露。核心概念（分母语义化 + 向后兼容）有真实缺口，相关工作以"计数对象"划界令人信服。

但它现在**达不到稳定接收线**，原因集中在三类：**(A) 数字-证据错位仍有三处触及统计呈现诚信**（均为旧配置残留，非造假，但 TOSEM artifact 复核必败）；**(B) 四个预注册假设全灭之后，正向贡献完全由度量+定理+审计承重，而理论层数学增量薄、机制叙事与 ξ 测量存在张力**；**(C) 篇幅与结构**（正文约 2.3 万词，理论 10 个 subsubsection 嵌在 §3.3 之下）。全部问题可**不做新实验**修复，故为大修而非拒稿。

## 三、优点

- **S1** 推断权限表与 claim-evidence map（含非主张清单）是近年少见的自律装置，抽查无超许可表述。
- **S2** 负结果处理成体系：H2 点估计判定+功效分析、H4 estimand 不可评估的处置（撤回 0.791 编码伪影、报告跨阈值敏感区间、拒绝事后择优）在统计伦理上是对的。
- **S3** RQ2 的 AST 审计（5.14%，HP/SI/TF 0/72、0/33、0/54）确定性强，与冻结 JSON 逐值吻合。
- **S4** ξ 精确性缺陷作为缺口定理的模型检验被真实测量并披露（0.765），而非停留在"premise assumed"。
- **S5** 边界研究用真实修复缺陷（scipy #20660/#8900、numpy #17478）与教科书对照，PINN 假阳性按 validation-reject 语义处理，理论-案例对应干净。
- **S6** 双 Zenodo DOI、冻结 commit、AVP 源码内嵌，复现姿态到位；全文无 em-dash、无明显机器腔。

## 四、必须修改（Major）

**M1｜功效与 stipulated-alternative 数字建立在已撤回的配置上。** §6.4 的超越概率表（0.997/0.966/0.759/0.423）与 stipulated power 0.491 来自 `rq2_power_v4.json`，其观测基底是 δ=0.4392 的 MP1 事后配置——即正文 §5.3 已明确撤回、"supports no verdict" 的那个配置；且 `rq2_power_stipulated.json` 在数据目录中缺失，0.491 无 SSOT 可溯。在冻结 MP5 主配置（δ=0.314）下重算，超越概率约为 0.977/0.854/0.461/0.151：正文当前把"接近大效应"的概率高估约 3 倍。**要求**：在冻结配置下重算全表与混合权重校准，重写 §6.4 及结论第 3 条中引用它的句子，补齐 stipulated JSON。

**M2｜tab:p2-13 表内自相矛盾，"+27% kill-set 质量提升"叙事失效。** 表中 "Mean C1_share (v4, evaluable cells) 0.209" 与同表 "Macro-mean suspect_share (v4, evaluable cells) 0.163" 不能同真（1−0.209≠0.163）。0.164/0.209 实为零杀格记 C1=0 的**旧编码 60 格均值**（`paper_numbers_v4.json: mean_c1_share=0.2092`），与论文自己宣布的 NA 约定矛盾。按 NA 口径重算：可评估格宏均 C1 为 v3 0.821 → v4 0.837（+1.9%），而非 0.164→0.209（+27%）。依赖该数字的三处叙事（§5.7 跨源分析、§5.8 decoupling、结论第 4 条"raising mean C1_share by 27%"）需要重写；真实的跨源效应更像"可评估格 12→15（多 3 个有杀格）+ 宏均 C1 微升"，这仍支持"质量而非效应量"的方向，但幅度语言必须换。**要求**：统一 NA 口径重算并改写全部下游句子与表标签。

**M3｜被宣布的唯一真源与正文冲突（artifact 阻断级）。** §5.10 声明三类干系人消费 `paper_numbers_v4.json` + `lrca_60cell_v4.json` 为 single source of truth，但该文件仍存 mean_aligned 0.275、δ 0.4392、suspect 0.791、h5_cells_pass 12/60、Friedman 15.30——五处与正文修正后的主数冲突；修正数散在 `audit_fix_numbers.json` 旁路文件。TOSEM 的 artifact evaluation 将直接失败。**要求**：在冻结主配置下重生成 paper_numbers（或正式改宗 SSOT 指针并在 Data Availability 说明谱系），保证"论文引用的每个数字命中 SSOT"。

**M4｜主对比的区间证据脆弱，方向性主张需要有效推断或降级。** δ=0.314 的 CI [0.014, 0.622] 依赖 9 个按构造 SMS=0 的 vacant cells（8 个在 cross 侧）；剔除后区间跨零（[-0.011, 0.648]，论文自己披露）；且 cell 级 bootstrap 忽略 12-PUT 簇依赖（推断权限表承认非独立但区间未作簇校正）。结论第 3 条"positive but not large effect"目前没有有效区间支撑。**要求**（二选一）：做 PUT 级 cluster bootstrap 给出带依赖校正的区间；或把方向性主张全面收敛为点估计陈述并同步 Abstract/结论措辞。**不建议**借机删除方向性预测本身——保留可失败的检验优于描述化（见第七节）。

**M5｜ξ=0.765 与 alignment 机制解释的张力未出清。** 正文一边用 Corollary(cross-zero) 给 45/60 零格提供"qualitative zero-prediction read"（§3.3 gap 小节末），一边测得 aligned 格 ξ=0.723、cross 格 0.795——混合池下多数 cross 格 w_k>0，推论前件并不成立，9 个非零 cross 格在字面上就是反例。目前的兜底句（"apply only to the premise-conforming sub-population"）方向正确但不够：**要求**逐格报告前件 Cov(R)∩{w_j>0}=∅ 真正成立的格数，把"zero-prediction read"限定到该子集；§5.8 的机制解释（aligned>cross 源于 fiber 观测）改为与"MR 强度差"不可辨识的双解释并存。

**M6｜理论层定位过高，两处 lemma 级对齐缺陷。** (a) 六个定理均为定义展开+初等不等式（窗口定理把加性预算设为假设 H-a；缺口定理前提近乎设定结论），作为"theory contribution"在 TOSEM 会被理论向审稿人打薄——**要求**把 RQ1 与贡献叙述降格为 "formal measurement scaffolding / guarantees"，或补一个非平凡结果（例如标签噪声率 ρ 下缺口分解的鲁棒界，正好与 ξ=0.765 呼应）。(b) Lemma G.1 陈述只设 L1∧L2+固定 L_switch，证明却调用 ε_AVP→0（L3）——把 L3 纳入引理假设或重写 E1 论证。(c) kill-witness 引理把"定义性分类事实"（killed⇒E1 失败⇒CONFIRMED）与"需要 R2 的 ε_eq 见证升级"混在一个陈述里——拆分为无条件部分与条件部分。

**M7｜§4.8（LRCA 三层诊断）残留旧矛盾段。** "lifts H4 from 10/60 to 12/60 cells ... The calibration ceiling (12/60 = 20%) remains far below the 80% pre-registered threshold; H4 is unattainable on this dataset"（main.tex 2162–2168）：其一，预注册 H4 是"均值 ≤0.20"，不存在"80% 阈值"；其二，与 §5.5 的 not-evaluable 裁定直接冲突；其三，在设计章预判结果。**要求**：删除或改写为中性校准描述，统一 not-evaluable 口径。

**M8｜结构、长度与浮动体卫生。** 正文约 2.3 万词、§3 约 7 千词且理论以 10 个 subsubsection 嵌于 §3.3；E1∧E2 保守性与 killed 公式在 §3.3 与 §4.7 近逐字重复，协议不对称讲了三遍；15/19 表、2/3 图无 `\ref` 引用（"This table also marks..." 这类指代在 acmart 浮动后会漂移），fig1/fig3 缺 `\Description`。**要求**：理论独立成节并把 lemma 级材料下放 Appendix G；删重复段；全部浮动体补 `\ref` 与 `\Description`；目标正文压回 1.6–1.8 万词。

## 五、次要修改

- m1　结论第 6 条 "detects all 34 tabled real defects" 句内补 selection-conditioned 限定（§5.9 有，结论漏）。
- m2　`h5_sensitivity_v4.json` 仍存撤回编码且 H5/H4 命名漂移；`rq3_friedman_v4.json` 的 interpretation 字段与正文 caveat 冲突——随 M3 一并清理。
- m3　𝒟_P、𝒳_adm 在 §3.3.3/退化定理先用、§3.3.7 才定义；检测窗定理前向引用 exact checker（§3.3.10 才定义）——加一句前向指针即可。
- m4　p=4 回归判决的 conditioning constant 在 G.8 有说明但未入正文窗口陈述的预算式，建议在正文加半句限定。
- m5　随机 Remark 的 "necessary in general" 缺必要性论证，改 "sufficient with strict inequality; necessity holds under the boundary-attaining noise model"。
- m6　不可判定定理对受限 edit 模板域需一句 Rice 归约的 padding 说明。
- m7　双命名体系（CE/OS/HP/TF/SI ≡ mut_C/M/G/T/F，且 HP=mut_G 对应 convergence）认知负担大，建议正文统一用一套、表格给映射。
- m8　部署基线 0.213（n=12 均值）作为工程阈值参考过重，加不确定度或改区间表述。
- m9　Highlights 7 条超 3–5 上限；节 label 沿旧 RQ 编号（rq1-* 实答 RQ3），不影响读者但影响维护。
- m10　li2026minmrcomplete（"Unknown Journal"）与 defect4mr2026（设计笔记）两处自引缺可核验元数据，补 arXiv 号/DOI 或获取方式。

## 六、Reviewer 2 视角的最严苛审稿意见

- M1/M2/M3 属 publication blocker：三者都是"正文主数与声明的数据源不一致"，无论成因多么无辜，投稿前必须修复，脚注化或 limitations 化不可接受。
- 四个预注册假设全灭后，本文的可发表性完全押在"度量+形式保证+诚实审计"上；若 M6 的理论降格被采纳，作者需要在 Intro 里正面回答"一个所有假设都没通过的度量论文为什么值得 TOSEM 发表"——目前 §5.1 的回答（结构性验证目标）是可用的，但要前移。
- 60 格共享 12 PUT、混合算子池导致 per-operator 构念不可识别——论文已如实披露，但任何"operator-MP alignment"字样的残留（结论第 3 条标题式表述）都会被抓住；请全文再扫一遍。
- 无霍桑效应问题（非人因实验）；benchmark 公平性方面，cosmic-ray 默认配置作为对照已声明 first-order 限定，可过。

## 七、过度防御审计（主张校准）

两处**不得**借修改趋弱：(1) M4 若选择降级路线，必须保留"aligned>cross 方向为正"这一可失败预测（点估计+方向陈述），不得整体描述化；(2) H4 的 not-evaluable 裁定是效度修复，但**重新预注册的 estimand 必须在修改稿中承诺**（哪种聚合、何时检验），否则"不可评估"会被读成永久免检。反向看，"binarized OR≈4.3 不作裁定"与"ξ 只作模型检验不入 SMS"的克制是对的，维持。

## 八、结语

修复 M1–M3（重算+SSOT 重生成，纯计算）、M4（一次 cluster bootstrap 或措辞收敛）、M5/M6/M7（措辞与一处补计数）、M8（结构手术）后，本文可以达到稳定接收线；以上均不需要新实验。若作者愿意在修改轮补做 operator 分层重跑（恢复真 (i,k,j) 轴）或 n≥30 扩样，那是加分项而非本轮门槛。

**推荐：Major Revision。**

---

## 附录：分线程单项评级

| 线程 | 关注面 | 单项建议 |
|---|---|---|
| 方法与统计 | 设计识别力、H1–H4、ξ、功效、工业臂、SSOT | Major |
| 形式理论 | 定理陈述-证明对齐、新颖度、理论-实证耦合 | Major |
| 贡献与呈现 | 贡献叙事、一致性、结构长度、写作卫生 | Major |

合成后维持 **Major Revision**（非 Reject）：边界框架与透明基建扎实，阻断项均为可计算/可措辞修复，无需新实验。
