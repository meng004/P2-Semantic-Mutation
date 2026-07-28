# REVIEW CHECKPOINT T3 — 拍板记录（委托执行；与 T4 联合裁定）

- 日期：2026-07-28
- 评审对象：`research/theory_drafts/thm_window.md`（THM-WIN、REM-FPOS、
  REM-FNEG；PO-WIN-1–6）、`research/theory_drafts/rem_identifiability.md`
  （REM-IDF，T4）、既有 boundary cases（现稿 §4.8 PINN/RNG）的覆盖
- 评审身份：作者委托的检查点评审；评审线独立验算全部不等式与源码事实
- 源码事实核验：MP_3 收敛关系每判定执行 p=4 网格
  （`src/p2/avp/dispatcher.py:15-16`）✓；flag 严格超出约定
  （`mp1_conservation.py` 的 `≤ε⇒pass`）✓；N=20 严格多数票
  （`src/p2/avp/repeat.py`）✓

## 1. 验算结论（Devil's Advocate 线）

- (i)/(ii)/(iii) 的误差预算推导复核通过（H-a 上下两侧 + R1 边际 ⇒ 两侧界；
  下沿开区间由严格超出约定；上沿由 S4 crash-oracle 排除）。
- REM-FNEG 代数复核：\(\varepsilon^\dagger>\varepsilon_{\mathrm{tol}}+\Delta_r+2(c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}})\iff\sqrt N>2c\sigma_{\mathrm{out}}/(\varepsilon^\dagger-\varepsilon_{\mathrm{tol}}-\Delta_r-2\eta_{\mathrm{det}})\)，
  分母为正的侧条件已显式；RNG 案例作为侧条件失败实例（换观测面而非加重复）
  读法正确。
- REM-FPOS：sup 不需达到性论证正确；采样/噪声掩蔽告诫诚实。
- 剂量反应"kill 概率单调"是模型级预测（location-shift + 幅度无关噪声），
  非定理推论——草稿已按预测措辞，H-DOSE 正是其受检渠道。合格。

## 2. 发现与处置

### B2（precision，已修）：regime 定义把两个独立条款混在括注里

原 §4 用"provided 2η̄ 吸收 ε_eq 级扰动"的括注把 LEM-WIT 需要的
ε_eq-稳定性塞进边际条款，混淆两个逻辑独立的条件。修复：regime 拆为
**(R1) 边际支配** \(\mu_r>2\bar\eta\)（p-execution 关系读 \(p\bar\eta\)）
与 **(R2) ε_eq-分离**（执行残差与阈值距离 > ε_eq ⇒ 判定对 ≤ε_eq 逐点扰动
不变），并给出消费映射：THM-WIN(i)/(iii) 与 THM-GAP(iii) 消费 R1（+H-a）；
LEM-WIT（A1 条款）消费 R2。跨草稿引用链经复核自洽。

### B3（minor，已修）：噪声界的置信读法

\(|\eta|\le\bar\eta\) 对无界噪声是集中式模型假设；REM-FNEG 的
"guaranteed" 属模型内保证（随 c 的置信水平）。已在 DEF-11 加一句读法说明。

### A3（validity 修订，已按 master-first 落地）：REM-IDF survivor 从句过度主张

原拟从句"survivor fiber 可辨识至 R-coverage 诱导划分；separating family
下划分在 Cov(R) 上平凡"不成立：空签名与所有 uncovered fiber 及每个
covered fiber 的窗下残留（THM-WIN(ii)）同时一致，观测不决定任何
coverage 类。修订为：killed 侧保持精确辨识 + separating family 使 killed
子群分离全部 covered 层；survivor 侧改述为"签名恒空、零 fiber 信息，归属
由生成期 eff 标签（A-PROV ex-ante 通道）承担"。此修订反而强化了实证设计
的一致性——survivor 归属本就设计为标签承载。已同步 master §Phase T4 块、
phase T4 文件、`rem_identifiability.md`。

## 3. 五个开放问题的裁定（thm_window.md §9）

| 问题 | 裁定 | 理由 |
|---|---|---|
| Q1 H-a 加性 vs 单侧对 | **保留加性** | 消费的两条单侧不等式由其蕴含；乘性交互作为可检偏差（剂量残差曲率）留给 EXP-DOSE，是额外可证伪面 |
| Q2 \(2\bar\eta\) vs \(p\bar\eta\) | **保留冻结陈述 + scope note** | 重冻结会波及 DEF-13/THM-GAP(iii)/LEM-WIT 全链无增益；MP_3 的 p=4 与回归条件数告诫已入 §3 note 与 R1 括注 |
| Q3 严格超出约定入 DEF-05 | **采纳，T6.1 handoff** | 已核对管线实现；整合文本须记录该约定（入 T6.1 检查单） |
| Q4 GPR 冻结超参 vs 换 PCE | **建议冻结超参，决定权归论证线冻结** | 换核会改预注册对象集；冻结超参保留 KER-SCIML 代表核；最终由论证计划 Task 1.2/2.3 在预注册前锁定 |
| Q5 REM-FPOS 告诫位置 | **留证明层** | Remark 保持简洁；T6.1 若审稿压力再提升一句 |

## 4. 边界案例覆盖确认（检查点授权范围）

- PINN（§4.8，ε_tol=10⁻⁴ flag 合法训练模型、10⁻³ 存活）→ REM-FPOS 实例
  （μ_r<0 ⟺ Δ_r>ε_tol，soft-BC 残差 ≈5×10⁻⁴ 即 Δ_r）✓
- numpy-RNG（§4.8）→ REM-FNEG 侧条件失败实例（结构观测面上
  ε† < ε_tol+Δ_r+2η_det，任何 N 不解，修复=换观测面）✓
- REM-IDF 表述（A3 修订后）✓；LRCA 重定位段与 §2.4 替换句对准
  main.tex:646–649 ✓

## 5. Reviewer 2 视角的最严苛审稿意见

- （已修复，本轮内关闭）A3：REM-IDF survivor 从句的可辨识性主张在观测语义
  下不成立——若带入正文将是审稿人一击即中的反例点；修订后主张与观测内容
  精确对齐。
- （已修复，本轮内关闭）B2：regime 括注混淆两个独立条款，跨定理引用会被
  审稿人追问"到底假设了什么"；拆分后消费映射显式。
- 外部效度：L_r 不可估清单（C3/D1/D2；C1 条件可估）与论证线 POOL-DOSE
  对象（含 GPR）存在真实接口张力——已作为 Q4 裁定移交论证线冻结前决定，
  不是理论线 blocker，但**必须在剂量预注册前关闭**（已在两份计划中留痕）。
- 统计选择偏差 / benchmark 公正 / 霍桑：不适用或通过（无数据端选择；
  boundary cases 为既有 §4.8 材料的理论重读）。
- 修复后无 publication blocker：Reviewer 2 视角扫描通过——5 类维度均无
  publication blocker。

## 6. 过度防御审计（CLAUDE.md §10.1）

| 处置 | 类别 | 辩护 |
|---|---|---|
| A3 survivor 从句改述 | 效度修复 | 原句为假主张（观测反例成立）；修订不是收缩而是纠错，且把归属责任显式压到 A-PROV ex-ante 通道，使其更可证伪 |
| B2 两条款拆分 | 效度修复 | 假设可见性；无主张变化 |
| B3 置信读法 | 效度修复 | 无界噪声下"guaranteed"如实限定；REM-FNEG 判据不变 |
| Q1/Q2 保持冻结陈述 | 反过度防御 | 拒绝以重冻结换取表面严格性；泛化以 scope note 承载 |

无主张收缩项。

## 7. 门禁判定

**CHECKPOINT T3 = PASS（与 T4 联合；附修复 B2/B3 与修订 A3；Q1–Q5 裁定如上）。**

- T3/T4 交接物齐备：`thm_window.md`（internal-review，含 B2/B3）、
  `rem_identifiability.md`（internal-review，含 A3）、L_r 不可估清单、
  本记录。
- 下游解锁：T6（整合与独立审计）的全部前置——T1–T5 完成 + CHECKPOINT
  T1/T2/T3 通过——现已满足。
- 移交论证线（非阻塞、但有 deadline 语义）：Q4（GPR 冻结超参或换 PCE）
  必须在其剂量反应预注册冻结前锁定；L_r 不可估清单（C3/D1/D2）为其
  Task 2.3 对象替换输入。
- 作者保留否决权：对 A3/B2/B3 或 Q1–Q5 裁定另有偏好时，按"先改 master
  再同步"程序修订。
