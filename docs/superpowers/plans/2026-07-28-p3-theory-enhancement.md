# P3 理论增强执行计划（区间/归因/检测窗/辨识四定理 + 退化定理修补 + 独立审计）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans。任务用 checkbox 跟踪；每个 REVIEW CHECKPOINT 必须停下等作者拍板。

**Goal:** 在 `submission/TOSEM_regular_20260706/main.tex` 基线上完成三个新主定理（THM-INT 区间健全性、THM-GAP 缺口归因、THM-WIN 检测窗）+ 辨识性重读 REM-IDF（THM-GAP 之 Remark）与退化定理修补（THM-DEG-R），通过独立形式审计，产出可进入预注册阶段的**最小理论核心**（R-9）章节。

**Architecture:** 先在 `research/theory_drafts/` 用 Markdown+LaTeX 起草定理陈述与证明（便于审计者独立阅读），评审通过后整合进 main.tex §2.10–2.12 与 Appendix G，最后跑一致性与编译验证。

**上游输入:** `research/p3-tosem-redesign-rqs-v2.0.md`（定理设计）、`research/p3-tosem-v2.0-writing-plan.md`（章节处置表）、main.tex §2.1–2.9 现有构造。

**硬约束:** THM-GAP 成文并通过内部评审之前，不得启动论证提升计划的 Phase 1（预注册冻结）——两部分 estimand 的合法性从 THM-GAP 推导。

**执行分派（按模型拆分）:** 本计划为规格权威（§0 符号系统、§1 定理清单与 PO 台账、任务定义源）；逐阶段执行在下列拆分文件中进行（checkbox 在拆分文件中打勾），内容冲突以本计划为准，修订先改本计划再同步拆分文件。

**分派原则（三类，两计划共用）:** ① **最强推理**（证明起草、方法学/统计设计、手稿写作）→ `claude-fable-5-thinking-max`；② **逻辑评审或审计**（符号审计、独立交叉检验、整合核对、准入重裁）→ `gpt-5.6-terra-max`（跨家族独立视角，审计者与被审产出不同源）；③ **执行**（跑批、脚本、管线、构建打包）→ `cursor-grok-4.5-high-fast`。同类阶段可由同一模型的多个实例并行执行。

| Phase | 拆分文件 | 模型（类别） | 前置 | 可并行于 |
|---|---|---|---|---|
| T0 符号与基线 | `理论增强-phaseT0-terra.md` | gpt-5.6-terra-max（审计） | — | 论证 Phase 0 |
| T1 THM-INT | `理论增强-phaseT1-fable.md` | claude-fable-5-thinking-max（推理） | T0 | T2/T3/T5 |
| T2 THM-GAP | `理论增强-phaseT2-fable.md` | claude-fable-5-thinking-max（推理） | T0 | T1/T3/T5 |
| T3 THM-WIN | `理论增强-phaseT3-fable.md` | claude-fable-5-thinking-max（推理） | T0 | T1/T2/T5 |
| T4 REM-IDF（THM-GAP Remark） | `理论增强-phaseT4-fable.md` | claude-fable-5-thinking-max（推理） | T2 | T5 |
| T5 THM-DEG-R | `理论增强-phaseT5-fable.md` | claude-fable-5-thinking-max（推理） | T0 | T1–T4 |
| T6 整合与审计 | `理论增强-phaseT6-terra.md` | gpt-5.6-terra-max（审计） | T1–T5 + CHECKPOINT T1–T3 | 审计等待窗口内：论证 Phase 0–2 |

---

## 0. 符号系统（两计划共用的符号说明总表；论证提升计划 §0 引用本节为唯一权威）

### 0.1 命名规约

1. **禁止无语义孤立字母命名**：数学对象不得以裸的 A、B、C、D、E、F、S 等单字母命名；一律用语义算子名（\(\mathrm{Cov}\)、\(\mathrm{Gap}\)、\(\mathrm{eff}\)、\(\mathrm{sig}\)，沿四柱 \(\operatorname{Det}_\Gamma\)/\(\operatorname{Complete}_\Gamma\) 的命名风格）或带语义下标的字母（\(\Delta_r\)、\(\mu_r\)、\(\sigma_{\mathrm{out}}\)、\(u_{\mathrm{neq}}\)）。
2. **符号闭集**：全部数学符号以 §0.2 总表为闭集；新增符号必须先入表（补序号、含义、来源、冲突检查）再入草稿/正文。Task T0.2 的 `notation_registry.md` 与本表一对一同步。
3. **定理族标签**：`THM-`（定理）、`LEM-`（引理）、`COR-`（推论）、`PROP-`（命题）、`REM-`（Remark，正文不占定理环境计数）+ 语义缩写。正文最终编号由 LaTeX 自动分配，Task T6.1 产出"标签 → 正文编号"映射表。既有结果登记：`THM-UND`（现稿 Thm 1 不可判定）、`THM-DUAL`（现稿 Thm 2 对偶）、`THM-DEG`（现稿 Thm 9.1 退化）。
4. **其他标识**：定义 `DEF-nn`；证明义务 `PO-<定理缩写>-n`；假设 `H-<语义缩写>`、实验 `EXP-<语义缩写>`（见论证提升计划 §0.3）。
5. **权威源优先级**：统一框架 v1.2 附录 A > 四柱 v1.2 > MR有效性理论 v3.1 > P3 内部惯用。

### 0.2 符号总表（序号 | 符号 | 含义 | 首定义/来源 | 备注）

| # | 符号 | 含义 | 首定义/来源 | 备注 |
|---|---|---|---|---|
| 1 | \(P,\ P'\) | 原程序 / 变异体程序 | v3.1 §2；DEF-01 | 实证章节 PUT 编号名 \(S_i\) ≙ \(P\) 的实例；禁用 \(S\) 作程序符号（避让 v3.1 模型结构 \(S\)） |
| 2 | \(P^\star\) | 参照正确实现 | DEF-12 | — |
| 3 | \(\Phi_P\) | 程序计算映射 \(I\circ D_h\) | v3.1 §3.1 | 原稿 \(\Phi_{S_i}\) 统一为 \(\Phi_P\) |
| 4 | \(x\) | 执行输入 | v3.1 §3 | — |
| 5 | \(\mathcal D_P,\ \mathcal X_{\mathrm{adm}}\) | 输入抽样分布、可采输入域 | 现稿 §2.6 | 原稿 \(D_S\) 改名 \(\mathcal D_P\)（避让 v3.1 适用域 \(D\) 与结构 \(S\)） |
| 6 | \(\alpha,\ \equiv_\alpha\) | 语义抽象（观测）映射、α-观测等价 | 现稿 §2.2 | 四柱统计误报率写 \(\alpha_{\mathrm{FPR}}\)，不与本 α 混用 |
| 7 | \(\mathcal C,\ c\) | 等价证书集、单个证书 | DEF-01 | 与 v3.1 谱系对象 \(K_\rho\) 的字段 \(C\) 不同对象 |
| 8 | \(\varepsilon_{\mathrm{eq}},\ K_{\mathrm{eq}}\) | 判等容差、判等抽样预算 | 现稿 §2.3 | \(K_{\mathrm{eq}}\) 与 v3.1 \(K_\rho\) 不同对象 |
| 9 | \(\mathrm{killed}(P',\mathrm{MR}_{i,k})\) | kill 谓词（AVP fail 于第 i 个 PUT 的第 k 条 MR 元组） | 现稿 §2.3 | — |
| 10 | \(r,\ R\) | 单条 MR、MR 集 | 现稿 §2.4 | 四柱 T3 的采纳集 \(S\) ≙ 本文 \(R\) |
| 11 | \(D_r\) | \(r\) 的适用域 | v3.1 §3.3 | — |
| 12 | \(J_r\in\{\mathrm{out,pass,fail}\}\) | 执行判定 | v3.1 §3.6 | ≡ AVP verdict；\(\mathrm{flag}(r,P'):=(J_r=\mathrm{fail})\) |
| 13 | \(\varepsilon_{\mathrm{tol}},\ \varepsilon_{\mathrm{AVP}}\) | MR 检查容差、AVP 数值容差 | 现稿 §2.9 / §2.3 | \(\varepsilon_{\mathrm{tol}}\equiv\) v3.1 的 \(\tau_r\)；保留 ε 族不改记 τ |
| 14 | \(\models_\tau\) | 容差语义满足关系 | 现稿 §2.7 | DEF-05 使用 |
| 15 | \(\psi_j,\ \Psi\) | 第 j 个语义不变量（层）、不变量族 \(\Psi=\{\psi_1..\psi_5\}\) | 现稿 §2.7 | 原稿记 \(I\)，改 \(\Psi\)（避让 v3.1 实现 \(I\)） |
| 16 | \(\mathrm{eff},\ \mathrm{eff}^{-1}\) | 语义效应映射、fiber 取原像 | 现稿 §2.9 | 原稿记 \(\sigma\)，改 \(\mathrm{eff}\)（避让统一框架声明结构 \(\sigma\)） |
| 17 | \(M_{\mathrm{neq}},\ M_j,\ m\) | 非等价变异体全集、第 j 层 fiber、单个变异体 | DEF-07 | \(M_j=\mathrm{eff}^{-1}(\psi_j\text{-viol})\cap M_{\mathrm{neq}}\) |
| 18 | \(n,\ k,\ u,\ u_{\mathrm{neq}}\) | 已证非等价数、被杀数、悬置存活数、悬置中真非等价数 | DEF-02 | 不用 \(e^*\)（避让 v3.1 结构命运字段 \(e\)） |
| 19 | \(\mathrm{SMS}_{\mathrm{strict}},\ \mathrm{SMS}_{\mathrm{cons}},\ \mathrm{SMS}_j\) | 严格/保守口径、第 j 层层内得分 | DEF-04 / DEF-07 | — |
| 20 | \(w_j\) | 层权重 | DEF-07 | — |
| 21 | \(\mathrm{Cov}(R)\) | 被 \(R\) 精确检查的层指标集 | DEF-06 | 原拟 \(F_R\)，改语义算子名；与统计协方差无关 |
| 22 | \(\mathrm{Gap}_{\mathrm{aln}}(R),\ \mathrm{Gap}_{\mathrm{str}}(R)\) | 对齐缺口、强度缺口 | DEF-08 | 原拟 \(A(R)/S(R)\)；\(\mathrm{Gap}_{\mathrm{aln}}\leftrightarrow\) 四柱 \(\Omega_{\mathrm{sel}}\) |
| 23 | \(\xi(R)\) | 精确性偏差（块外 kill 质量占比） | DEF-09 | 模型检验统计量，不入 SMS；pooled 口径升 secondary confirmatory 假设 H-XI（先验地标 0.10，B-1，见论证计划 §1.2），充当 A-PROV 的 ex-post 检验器；per-cell 分布仍描述性 |
| 24 | \(\mathrm{sig}(m)\) | kill 签名 | DEF-14 | — |
| 25 | \(\varepsilon_m\) | 违反幅度 | DEF-10 | — |
| 26 | \(\Delta_r\) | 正确程序结构保持残差 \(\sup_{x\in D_r}\varepsilon_r(x;P^\star)\) | DEF-12 | = v3.1 结构保持偏差 \(\Delta(S,P)\) 的实例；对接结构命运四分类 |
| 27 | \(\mu_r\) | 强度边际 \(\varepsilon_{\mathrm{tol}}-\Delta_r\) | DEF-12 | — |
| 28 | \(\eta,\ \bar\eta,\ \eta_{\mathrm{det}}\) | 执行噪声、噪声界、确定性噪声分量 | DEF-11 | ↔ v3.1 预算项 \(\tau_{\mathrm{stat}}/\tau_{\mathrm{round}}/\tau_{\mathrm{obs}}\) |
| 29 | \(N,\ c,\ \sigma_{\mathrm{out}}\) | 重复执行次数、噪声集中常数、随机 PUT 输出标准差 | DEF-11 | 标准差必须写 \(\sigma_{\mathrm{out}}\)，禁用裸 \(\sigma\) |
| 30 | \(L_r\) | 违反泛函对 \(\varepsilon_m\) 的 Lipschitz 常数 | THM-WIN | 命名沿四柱 \(L_\sigma\) 风格；与 #31 的退化极限 \(L\) 不同对象 |
| 31 | \(L,\ L_{\mathrm{lim}},\ L_{\mathrm{switch}}\) | 退化极限拼合（regime） | 现稿 §2.6 | THM-DEG-R 拆分后的两段 |
| 32 | \(\varepsilon_{\mathrm{lo}},\ \varepsilon_{\mathrm{crash}}\) | 检测窗下沿、崩溃阈 | DEF-13 / 现稿 S4 | — |
| 33 | \(\mathrm{supp}(\mathcal D_P)\) | 抽样分布支撑 | 现稿 Lemma 9.1 | THM-DEG-R 新增假设使用 |
| 34 | S1–S5 | sanity gate 编号 | 现稿 §2.8 | 门禁标签非数学符号，沿用 |
| 35 | E1∧E2 | 判等程序编号 | 现稿 §2.3 | 与实验标签空间分离（实验一律 `EXP-` 前缀，见论证计划 §0.3） |

### 0.3 形式化定义与方法学假设清单（先于定理正文冻结；A-PROV 为方法学假设，非 DEF 条目，F-12）

- **DEF-01（三态等价）**：候选体 \(P'\) 处于且仅处于一态：`CERTIFIED_EQUIVALENT`（存在机器可核验证书 \(c\in\mathcal C\) 证 \(P'\equiv_\alpha P\)）、`CONFIRMED_NON_EQUIVALENT`（存在见证 \(x:\ \|\alpha(\Phi_P(x))-\alpha(\Phi_{P'}(x))\|>\varepsilon_{\mathrm{eq}}\)）、`EQUIVALENCE_UNRESOLVED`（两者皆无；含现行 E1∧E2 抽样一致者）。
- **DEF-02（计数）**：\(n=|\text{confirmed non-equiv}|\)，\(k=\) 其中被 \(R\) 杀死数，\(u=|\text{unresolved 存活}|\)，\(u_{\mathrm{neq}}\in[0,u]\) 为 unresolved 中真非等价数（未知量）。
- **DEF-03（AVP 决定性假设）**：MR 判定是执行元组 α-观测输出的确定函数（随机 PUT 按 §2.3 的 N 重复聚合语义解释）；对应 v3.1 §3.6 判定 \(J_r\) 的确定性。
- **DEF-04（区间口径）**：\(\mathrm{SMS}_{\mathrm{strict}}=k/n\)，\(\mathrm{SMS}_{\mathrm{cons}}=k/(n+u)\)。
- **DEF-05（exact checker）**：\(r\) 是 \(\psi_j\) 的精确检查器 ⟺ \(\mathrm{flag}(r,P')\iff [\![P']\!]\not\models_\tau \psi_j\)，其中 \(\mathrm{flag}(r,P')\equiv(J_r=\mathrm{fail})\)（AVP fail）。
- **DEF-06（被检层集）**：\(\mathrm{Cov}(R)=\{j: \exists r\in R\ \text{为}\ \psi_j\ \text{的 exact checker}\}\)（covered strata）。
- **DEF-07（fiber、层权重与层内得分）**：fiber \(M_j:=\mathrm{eff}^{-1}(\psi_j\text{-viol})\cap M_{\mathrm{neq}}\)；\(w_j=|M_j|/|M_{\mathrm{neq}}|\)；\(\mathrm{SMS}_j(R)=\) 限制在 \(M_j\) 的杀死率。
- **DEF-08（缺口分解）**：对齐缺口 \(\mathrm{Gap}_{\mathrm{aln}}(R)=\sum_{j\notin \mathrm{Cov}(R)}w_j\)；强度缺口 \(\mathrm{Gap}_{\mathrm{str}}(R)=\sum_{j\in \mathrm{Cov}(R)}w_j\,(1-\mathrm{SMS}_j(R))\)。
- **DEF-09（精确性偏差）**：\(\xi(R)=\) 块外 kill 质量 / 总 kill 质量（模型检验统计量，不入 SMS）。
- **DEF-10（违反幅度）**：\(\varepsilon_m\) 为编辑模板在 latency window 语义下的违反幅度参数（沿用 §2.8）。
- **DEF-11（噪声模型）**：\(|\eta|\le\bar\eta\)；确定性 \(\bar\eta=\eta_{\mathrm{det}}\)，随机 \(\bar\eta=c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}\)。**预算对应（v3.1 §4.3）**：\(\eta_{\mathrm{det}}\approx\tau_{\mathrm{round}}+\tau_{\mathrm{obs}}\)，随机项 ≙ \(\tau_{\mathrm{stat}}\)，\(\Delta_r\)（DEF-12）由 \(\tau_{\mathrm{disc}}\) 主导。
- **DEF-12（边际与结构保持残差）**：\(\mu_r=\varepsilon_{\mathrm{tol}}-\Delta_r\)，其中 \(\Delta_r:=\sup_{x\in D_r}\varepsilon_r(x;P^\star)\) 为正确程序 \(P^\star\) 上的关系残差上确界，**即 v3.1 的结构保持偏差 \(\Delta(S,P)\) 在 \(r\) 的诱导结构上的实例**。
- **DEF-13（检测窗）**：\((\varepsilon_{\mathrm{lo}},\varepsilon_{\mathrm{crash}})\)，\(\varepsilon_{\mathrm{lo}}=\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta\)。
- **DEF-14（签名与分离族）**：\(\mathrm{sig}(m)=\{r\in R: r\ \text{kills}\ m\}\)；分离族 = \(\mathrm{Cov}(R)\) 中每层至少一个 exact checker。
- **A-PROV（构念桥接假设，R-6；方法学假设，不进入任何定理的数学前提）**：实证操作化中，aligned 出处的 MR 集近似其目标层的 exact checker（DEF-05 的经验近似）；\(\mathrm{Cov}(R)\) 的操作化 = 适用矩阵 × MR 出处（provenance-as-coverage）；证据双通道（F-2）：**ex-ante 通道**=出处与构造审计（对称清单、生成期 eff 标签、适用矩阵哈希），与 kill 结果无关，决定 A-PROV 是否被断言；**ex-post 通道**=\(\xi(R)\)（DEF-09）作结果侧诊断，其 pooled 口径为 secondary confirmatory 预测 H-XI（先验地标 0.10，B-1），消费规则预注册于论证计划 Task 1.3 Step 1b——H-ZERO/H-DISC verdict 无条件，ξ 不改变 verdict，H-ZERO × H-XI 2×2 裁决表预注册。登记于此供两计划统一引用；实证落地见论证提升计划 Task 1.3。

### 0.4 跨文档符号冲突消解表（权威源优先级见 §0.1 第 5 条）

| 符号 | 四柱 / v3.1 含义 | P3 现稿含义 | 消解 |
|---|---|---|---|
| \(S\) | v3.1：模型结构 \(S:X\to X\) | PUT 程序 \(S_i\) | 新定理文本一律用 \(P,P'\)；\(S_i\) 限实证章节作编号名（#1） |
| \(\sigma\) | 统一框架：声明结构（关系对）；v3.1 已将层位改记 \(\lambda\) 归还 \(\sigma\) | effect map \(\sigma:e\mapsto\) 效应类（§2.9） | **P3 effect map 改记 \(\mathrm{eff}\)**（#16）；正文改名于 Task T6.1 执行；标准差写 \(\sigma_{\mathrm{out}}\)（#29） |
| \(\rho\) | v3.1：候选/可执行 MR | （新增 THM-WIN 曾拟 \(\rho_0\)） | 残差改用 \(\Delta_r\)（#26）；P3 不以 \(\rho\) 命名其他对象 |
| \(I\) | v3.1：程序实现（\(P=(M,D_h,I)\)） | 不变量族 \(I=\{\psi_1..\psi_5\}\)（§2.7） | 新文本不变量族改记 \(\Psi\)（#15）；正文改名于 Task T6.1 执行 |
| \(e\) | v3.1：结构命运（\(K_\rho\) 字段） | （新增曾拟 \(e^*\)） | 改 \(u_{\mathrm{neq}}\)（#18） |
| \(\alpha\) | 四柱统计情形：误报率 \(\mathrm{StatValid}_{\alpha,\delta}\) | 语义抽象/观测 \(\alpha\)、\(\equiv_\alpha\) | P3 保留 \(\alpha\)=抽象（先占且遍布）；引用统计资格时写 \(\alpha_{\mathrm{FPR}}\) |
| \(\tau\) | v3.1：误差预算/容差（\(\tau_r\)） | \(\varepsilon_{\mathrm{tol}}\)（ε 族内聚） | P3 保留 ε 族；对应表注明 \(\varepsilon_{\mathrm{tol}}\equiv\tau_r\)，不拆散 ε 系统 |
| \(\Delta\) | v3.1：结构保持偏差 \(\Delta(S,P)\) | （新增） | **直接采用**：\(\Delta_r\)（#26），实现实质对接 |
| \(S\)（集合） | 四柱 T3：已采纳关系集合 \(S\subseteq\mathcal A_\Gamma\) | MR 集 \(R\) | P3 用 \(R\)；接口注记时写"四柱之 \(S\) ≙ 本文 \(R\)" |
| \(\kappa\) | 四柱 T4：最小完备基数 \(\kappa(\Gamma,\mathcal R)\) | （论证计划：Cohen's κ） | 语境隔离；论证计划 §0.2 统计符号表已注明二者无关 |
| \(\Gamma,\ \mathfrak G,\ \lambda\) | 统一框架保留（理论上下文/生成映射/层位） | 未用 | P3 禁用这三个符号命名新对象 |
| \(J_\rho,\ \mathrm{out/pass/fail}\) | v3.1 执行判定 | AVP pass/fail | 等同；DEF-03/DEF-05 已建立映射 |
| \(\Omega_{\mathrm{intr}},\Omega_{\mathrm{sel}},\Omega_{\mathrm{search}}\) | 四柱 T3 三层残余 | （新增接口） | THM-GAP 接口注记使用四柱原符号，映射 \(\mathrm{Gap}_{\mathrm{aln}}(R)\leftrightarrow\Omega_{\mathrm{sel}}\) |

### 0.5 标签系统与旧标签映射（v2.0 设计稿 / 本计划初稿 → 现行）

| 旧标签 | 新标签 | 语义 |
|---|---|---|
| Thm A / T-A | **THM-INT** | SMS 区间健全性与单调性（interval） |
| Thm B / T-B | **THM-GAP** | 块对角与缺口归因（gap attribution） |
| Thm C / T-C | **THM-WIN** | 容差索引检测窗（window） |
| Prop D / P-D | **REM-IDF**（原拟 PROP-IDF，R-9 降为 THM-GAP 之 Remark） | kill 签名可辨识性（identifiability 重读） |
| Lemma A.1 / L-A1 | **LEM-WIT** | kill witness upgrade |
| L-B1 | **LEM-CLO** | exact checker 的 violation set 闭包性 |
| C-B1 | **COR-ZERO** | cross-zero 预测 |
| C-C1 | **REM-FPOS**（原拟 COR-FPOS，R-9 改为 THM-WIN 内 Remark） | 弱 MR 假阳性 |
| C-C2 | **REM-FNEG**（原拟 COR-FNEG，R-9 改为 THM-WIN 内 Remark） | 随机假阴性与 \(N^{-1/2}\) 处方 |
| T-9.1′ | **THM-DEG-R** | 退化定理修补版（现稿 THM-DEG 的替换） |
| D1–D14 | DEF-01–DEF-14 | 形式化定义 |
| \(F_R\)；\(A(R)/S(R)\)；\(\rho_0\)；\(e^*\)；σ(effect map)；I(不变量族)；\(D_S\) | \(\mathrm{Cov}(R)\)；\(\mathrm{Gap}_{\mathrm{aln}}/\mathrm{Gap}_{\mathrm{str}}\)；\(\Delta_r\)；\(u_{\mathrm{neq}}\)；\(\mathrm{eff}\)；\(\Psi\)；\(\mathcal D_P\) | 数学符号语义化 |
| PO-A1..A5 / B0..B5 / C1..C6 / D1..D2 / F1..F3 | PO-INT-1..5 / PO-GAP-1..6 / PO-WIN-1..6 / PO-DEG-1..3；PO-IDF-1..2（旧 D1..D2）撤销——R-9 后 REM-IDF 无独立 PO，论证并入 THM-GAP 讨论 | 证明义务 |
| H-B1 / H-B2 / H-C1 / H-C2 / H-X1 / H-X2 | H-ZERO / H-DISC / H-CONS / H-DOSE / H-CAL / H-RANK | 假设（论证计划 §0.3） |
| 实验 E2 / E3 / E3c / E4 / RQ-S 审计 | EXP-CON / EXP-DIS / EXP-DOSE / EXP-EXT / EXP-STR | 实验（论证计划 §0.3） |
| Phase A–G / Task A1–G2 / CHECKPOINT 1–4 | Phase T0–T6 / Task T0.1–T6.2 / CHECKPOINT T1–T4 | 计划结构 |

---

## 1. 可度量目标（计划级验收）

| 目标 | 度量 | 验收值 |
|---|---|---|
| 新增形式化定义 | §0.3 定义清单落入正文/附录 | 14/14，每条有编号可交叉引用 |
| 新增/修补定理 | §1.1 清单 | 新增 3 主定理 + 1 推论（COR-ZERO）+ 2 引理 + 3 Remark（REM-IDF/REM-FPOS/REM-FNEG）；THM-DEG-R 修补 3 项全闭合（R-9 最小理论核心） |
| 证明义务 | §1.2 台账 | 20/20 状态=closed（R-9 撤销 PO-IDF-1..2），每条证明无前向引用、无循环 |
| 独立审计 | 8 项清单（Task T6.2） | 8/8 ✓，报告含草稿 SHA256 签署 |
| 正文体积 | 新增理论正文 | ≤ 3 页（TOSEM acmsmall 版式，R-9）；完整证明全部入 Appendix G；正文只载证明链上符号，§0.2 全表以 notation table 入附录 |
| 构建 | 编译 + 字符 | 两遍编译零 error；`grep -c "Missing character" main.log` = 0 |
| 记号一致 | notation_registry 比对 | §0.2 总表为符号闭集，草稿/正文零溢出；与统一框架附录 A 零冲突 |

### 1.1 定理清单（唯一权威索引）

| 标签 | 名称 | 依赖定义 | 依赖既有结果 | 证明义务 | 状态 |
|---|---|---|---|---|---|
| LEM-WIT | kill witness upgrade（被杀即非等价见证） | DEF-01–03 | §2.3 AVP 语义 | PO-INT-1, 2 | draft |
| **THM-INT** | SMS 区间健全性与单调性 | DEF-02–04 | LEM-WIT | PO-INT-3–5 | draft |
| LEM-CLO | exact checker ⊂ strong MR | DEF-05 | THM-DUAL（现稿 Thm 2，≡_α 闭包） | PO-GAP-1 | draft |
| **THM-GAP** | 块对角与缺口归因分解 | DEF-05–09, S5 | THM-DUAL、LEM-CLO、THM-WIN(iii) | PO-GAP-2–5 | draft |
| COR-ZERO | cross-zero 预测（非对齐 SMS=0） | — | THM-GAP | PO-GAP-6 | draft |
| **THM-WIN** | 容差索引检测窗（现稿 Prop 2 升级） | DEF-10–13 | latency window（§2.8） | PO-WIN-1–4 | draft |
| REM-FPOS（THM-WIN 内 Remark） | 弱 MR 假阳性 | DEF-12 | THM-WIN | PO-WIN-5 | draft |
| REM-FNEG（THM-WIN 内 Remark） | 随机假阴性与 \(N^{-1/2}\) 处方 | DEF-11 | THM-WIN | PO-WIN-6 | draft |
| REM-IDF（THM-GAP 内 Remark） | kill 签名可辨识性（重读） | DEF-14 | THM-GAP | —（无独立 PO，论证并入 THM-GAP 讨论段） | draft |
| THM-DEG-R | 退化定理（修补版） | 支撑假设 | 现稿 Lemma 9.1–9.3 | PO-DEG-1–3 | repair |

### 1.2 证明义务台账（执行时逐条置 closed）

| PO | 义务（一条=一个可独立核验的断言） | 所属 | 预计篇幅 |
|---|---|---|---|
| PO-INT-1 | DEF-03 假设在 §2.3 现行 AVP 语义下成立范围的论证（含随机聚合情形的限定） | LEM-WIT | ≤10 行 |
| PO-INT-2 | killed ⟹ ∃x α-分歧超 ε_eq（经 MR 关系谓词分解） | LEM-WIT | ≤15 行 |
| PO-INT-3 | \(k/(n+u_{\mathrm{neq}})\) 单调于 \(u_{\mathrm{neq}}\) ⟹ 区间成立且两端可达 | THM-INT | ≤8 行 |
| PO-INT-4 | 宽度 \(=ku/(n(n+u))=\mathrm{SMS}_{\mathrm{strict}}\cdot u/(n+u)\) | THM-INT | ≤5 行 |
| PO-INT-5 | 单调性 4 情形：等价证书 / 分歧见证 / unresolved 被新 MR 杀 / \(R\subseteq R'\)，两端点方向逐一验证 | THM-INT | ≤20 行 |
| PO-GAP-1 | exact checker 的 violation set 对 ≡_α 封闭（故为 strong MR） | LEM-CLO | ≤8 行 |
| PO-GAP-2 | (i)S5+(ii)exact+(iii)窗非退化 ⟹ 无跨层 kill | THM-GAP | ≤15 行 |
| PO-GAP-3 | kill matrix 块对角形式化陈述 | THM-GAP | ≤5 行 |
| PO-GAP-4 | \(1-\mathrm{SMS}=\mathrm{Gap}_{\mathrm{aln}}+\mathrm{Gap}_{\mathrm{str}}\) 代数恒等 | THM-GAP | ≤8 行 |
| PO-GAP-5 | \(\mathrm{Gap}_{\mathrm{aln}},\mathrm{Gap}_{\mathrm{str}}\) 仅由 kill matrix+fiber 标签可计算（构造性） | THM-GAP | ≤8 行 |
| PO-GAP-6 | \(\mathrm{Cov}(R)\cap\{j:w_j>0\}=\varnothing\Rightarrow \mathrm{SMS}=0\) | COR-ZERO | ≤4 行 |
| PO-WIN-1 | Lipschitz（\(L_r\)）与噪声假设的形式化及可满足性说明（逐 PUT 类） | THM-WIN | ≤12 行 |
| PO-WIN-2 | 必杀界（三角不等式） | THM-WIN | ≤10 行 |
| PO-WIN-3 | 必不杀界 | THM-WIN | ≤10 行 |
| PO-WIN-4 | 窗含入（与 ε_crash、S4 对接） | THM-WIN | ≤6 行 |
| PO-WIN-5 | \(\mu_r<0\) ⟹ 原程序被标记 ⟹ 退出可采纳评价集 | REM-FPOS | ≤6 行 |
| PO-WIN-6 | N 下界代数推导 | REM-FNEG | ≤6 行 |

（PO-IDF-1/2 已撤销——R-9：REM-IDF 的同层性与覆盖等价类论证以两句话并入 THM-GAP 讨论段，由 T6 审计项 (8) 一并复核，不设独立台账行。）
| PO-DEG-1 | Lemma 9.1 增补 \(\mathrm{supp}(\mathcal D_P)\supseteq\mathcal X_{\mathrm{adm}}\) 假设 + 无假设反例注记 | THM-DEG-R | ≤8 行 |
| PO-DEG-2 | a.e. 改二选一表述（浮点有限例外集 / 连续化测度零），G.3 同步 | THM-DEG-R | ≤10 行 |
| PO-DEG-3 | \(L=L_{\mathrm{lim}}\wedge L_{\mathrm{switch}}\) 两段式重述及证明适配 | THM-DEG-R | ≤12 行 |

**每条 PO 的关闭标准**：证明写入对应草稿文件"Proof"节 → 自检（无前向引用、每步引用已有定义/结果编号）→ 内部评审通过 → 审计对应项 ✓。

---

## Phase T0：符号系统与基线冻结

### Task T0.1：建立理论草稿工作区

**Files:** Create: `research/theory_drafts/README.md`

- [ ] **Step 1:** 创建目录与索引文件，索引列出五个草稿文件名与状态列（draft / internal-review / audited / integrated）
- [ ] **Step 2:** `git add research/theory_drafts/ && git commit -m "theory(v2): open theory draft workspace"`

### Task T0.2：记号审计与冻结

**Files:** Create: `research/theory_drafts/notation_registry.md`

- [ ] **Step 1:** 提取现稿全部理论符号及首次定义位置：

```bash
rg -n "\\\\equiv_|varepsilon_|mathrm\{SMS\}|K_\{?\\\\mathrm\{eq\}|M_\{\\\\mathrm\{neq\}|sigma\^\{-1\}|psi_" submission/TOSEM_regular_20260706/main.tex | head -60
```

- [ ] **Step 2:** 在 `notation_registry.md` 落地 §0.2 符号总表（序号、符号、含义、首定义/来源、备注五列一对一照搬），并加"现稿出现行号"列。新增符号闭集 = §0.2 的 #17–#32 中标注 DEF/THM 来源者；任何草稿引入表外符号即违规，先补表再用
- [ ] **Step 3:** 定位《MT基础理论统一框架》v1.2 附录 A（OneDrive `0-论文/MR识别/theory/` 目录），对 registry 逐符号 diff；重点核对保留符号 \(\sigma,\Gamma,\mathfrak G,\lambda,S,I,\rho,e,\kappa\) 未被 P3 新文本挪用。附录 A 不可达时以四柱 v1.2 §2 + v3.1 §3 为代理权威并在 registry 头部注明
- [ ] **Step 4:** 检查现稿是否已有 `SMS_strict / SMS_conservative` 与 `EQUIVALENCE_UNRESOLVED` 词汇（`rg -n "strict|conservative|UNRESOLVED" submission/TOSEM_regular_20260706/main.tex`）。若无：登记"需在 §2.3 引入三态等价（certified-equivalent / confirmed-non-equivalent / unresolved），把现 E1∧E2 样本等价降格为 unresolved 的证据"这一集成任务到 Task T5.2
- [ ] **Step 5:** 盘点现稿待改名符号的出现范围：`rg -c "sigma\^\{-1\}|\\\\sigma\\b" submission/TOSEM_regular_20260706/main.tex`（effect map σ→\(\mathrm{eff}\)）与 `rg -n "invariant family|I = \\\\\{|\\\\mathcal\{?I\}?" submission/TOSEM_regular_20260706/main.tex`（不变量族 I→\(\Psi\)）与 `rg -n "D_S" submission/TOSEM_regular_20260706/main.tex`（\(D_S\to\mathcal D_P\)），把出现清单写入 registry 附录，改名动作归 Task T6.1
- [ ] **Step 6:** Commit

---

## Phase T1：THM-INT 区间健全性

### Task T1.1：起草引理与定理陈述

**Files:** Create: `research/theory_drafts/thm_interval.md`

- [ ] **Step 1:** 写入 LEM-WIT 与 THM-INT 陈述（下述 LaTeX 为定稿基准，`[·]` 占位符在 Task T6.1 换成正文编号；执行者可润色不可改语义）：

```latex
\textbf{Lemma [LEM-WIT] (kill witness upgrade).} Assume the AVP verdict is a
deterministic function of the $\alpha$-observed outputs of the executions
in an MR tuple. If $\mathrm{killed}(P',\mathrm{MR}_{i,k})$ holds, then some
execution input $x$ satisfies
$\|\alpha(\Phi_{P}(x))-\alpha(\Phi_{P'}(x))\|>\varepsilon_{\mathrm{eq}}$,
hence $P'$ is CONFIRMED\_NON\_EQUIVALENT. Consequently the unresolved set
contains no killed mutants.

\textbf{Theorem [THM-INT] (interval soundness and monotonicity).} Let $n$ be the
number of confirmed non-equivalent mutants, $k$ the number killed by $R$,
and $u$ the number of unresolved survivors. Let $u_{\mathrm{neq}}\in[0,u]$ be the
(unknown) number of truly non-equivalent mutants among the unresolved.
Then the ground-truth score $k/(n+u_{\mathrm{neq}})$ satisfies
\[ \mathrm{SMS}_{\mathrm{cons}}=\tfrac{k}{n+u}\;\le\;\tfrac{k}{n+u_{\mathrm{neq}}}\;\le\;\tfrac{k}{n}=\mathrm{SMS}_{\mathrm{strict}}, \]
with width $\mathrm{SMS}_{\mathrm{strict}}\cdot\tfrac{u}{n+u}$. Each
equivalence certificate ($u\!\to\!u\!-\!1$) or divergence witness
($u\!\to\!u\!-\!1$, $n\!\to\!n\!+\!1$) weakly narrows the interval; and for
$R\subseteq R'$ both endpoints are non-decreasing.
```

- [ ] **Step 2:** 写证明（要点：宽度 \(k/n-k/(n+u)=k u/(n(n+u))\)；MR 扩张时 \((k+\Delta+j)/(n+j)\ge k/n\) 因 \(k\le n\)；证书两类分别验证两端点变化方向）
- [ ] **Step 3:** 自检清单：AVP 决定性假设是否已在 §2.3 有依据；随机 PUT 的 AVP 重复语义（N=20）是否破坏 LEM-WIT（若 kill 判定含统计聚合，需把"超容差"改为"按 AVP 判定语义超容差"并加脚注）。逐项在草稿"Obligations"节记录
- [ ] **Step 4:** Commit

### Task T1.2：区间演示计算（现有数据，development 身份）

**Files:** Create: `scripts/theory/interval_demo.py`；Output: `data/results/interval_demo_v4.json`

- [ ] **Step 1:** 从 v4 prescreen 台账统计每 mp-cell 的 (n, k, u)：u 取"仅由 K_eq 抽样判等、无 AST/证书"的候选数（输入=prescreen 计数台账，与论证线 Phase 0 的 δ 冲突正交，无需等其 CHECKPOINT 0，F-13）。数据源定位：`rg -l "equiv" data/ --glob "*v4*"`
- [ ] **Step 2:** 输出每 mp-cell（v4 遗产划分 12 PUT × 5 MP，F-8）与总体的 [SMS_cons, SMS_strict] 及宽度分布；写入 JSON（键名 `mp_cells`；新键，不改旧键）
- [ ] **Step 3:** 验证：`python scripts/theory/interval_demo.py && python -c "import json;d=json.load(open('data/results/interval_demo_v4.json'));print(len(d['mp_cells']))"` 期望 60（mp-cell 口径，F-8）
- [ ] **Step 4:** Commit（此结果只作 §2.10 演示图，标注 development-only）

**REVIEW CHECKPOINT T1：作者确认 THM-INT 陈述、假设与演示口径。**

---

## Phase T2：THM-GAP 缺口归因（核心）

### Task T2.1：起草陈述与推论

**Files:** Create: `research/theory_drafts/thm_gap.md`

- [ ] **Step 1:** 写入定义与定理（定稿基准）：

```latex
\textbf{Definition (exact checker).} $r$ is an exact checker for stratum
$\psi_j$ if its violation predicate flags $P'$ iff
$[\![P']\!]\not\models_{\tau}\psi_j$ within the tolerance regime of
Theorem~[THM-WIN]. $\mathrm{Cov}(R)=\{j: R$ contains an exact checker for $\psi_j\}$.

\textbf{Theorem [THM-GAP] (block structure and gap attribution).} Assume (i)
stratum purity S5 for all $m\in M_{\mathrm{neq}}$, (ii) every $r\in R$ is
an exact checker for some stratum, (iii) non-degenerate tolerance margins
(Theorem~[THM-WIN]). Then no $m$ in fiber $M_j$ with $j\notin \mathrm{Cov}(R)$
is killed, the fiber-by-stratum kill matrix is block-diagonal, and
\[ 1-\mathrm{SMS}(R)=\underbrace{\textstyle\sum_{j\notin \mathrm{Cov}(R)} w_j}_{\mathrm{Gap}_{\mathrm{aln}}(R)\ \text{(alignment gap)}}
 +\underbrace{\textstyle\sum_{j\in \mathrm{Cov}(R)} w_j\,(1-\mathrm{SMS}_j(R))}_{\mathrm{Gap}_{\mathrm{str}}(R)\ \text{(strength gap)}},
 \qquad w_j=\tfrac{|M_j|}{|M_{\mathrm{neq}}|}, \]
both computable from the kill matrix and fiber labels alone.

\textbf{Corollary [COR-ZERO] (cross-zero prediction).} If
$\mathrm{Cov}(R)\cap\{j:w_j>0\}=\varnothing$ then $\mathrm{SMS}(R)=0$.

\textbf{Definition (exactness defect).} $\xi(R)=$ block-off-diagonal kill
mass / total kills; $\xi$ measures deviation from (i)-(ii) and is reported
as a model-check statistic, not folded into SMS.
```

- [ ] **Step 2:** 写证明（要点：\(m\in M_j, j\notin \mathrm{Cov}(R)\)；任取 \(r\) 为 \(\psi_l\) 的 exact checker，\(l\ne j\)；S5 纯性给 \([\![m]\!]\models\psi_l\)，故 r 不 flag m；r 在原程序上 pass；killed 需存在 flag → 无。分解式由块对角直接展开）
- [ ] **Step 3:** 写接口注记（一段）：\(\mathrm{Gap}_{\mathrm{aln}}(R)\) 对应四柱 T3 的选择残余 \(\Omega_{\mathrm{sel}}\)（加对齐 MR 可消除），\(\mathrm{Gap}_{\mathrm{str}}(R)\) 是声明层内检测力缺口；注明"四柱之采纳集 \(S\) ≙ 本文 \(R\)"；引用四柱框架为 companion technical report，不承重
- [ ] **Step 4:** 写"经验含义"小节：cross/非对齐 MR 的 SMS 预测为 0 ⟹ v4 遗产 mp-cell 划分（12 PUT × 5 MP = 60，F-8）零膨胀中 cross mp-cell 的零质量属理论预测；为论证提升计划的 H-ZERO/H-DISC 提供推导来源（明确引用行）；同小节显式声明 **A-PROV 桥接假设**（§0.3：provenance-as-coverage）是把 COR-ZERO 应用到实证数据的前提，ξ 为其 ex-post 诊断（证据双通道与 verdict 无条件规则见 §0.3 A-PROV 条目，F-2）
- [ ] **Step 5:** Commit

### Task T2.2：现稿一致性核对

- [ ] **Step 1:** 核对现稿 Thm 2（THM-DUAL）的 strong MR 定义（violation set 对 ≡_α 封闭）与 exact checker 的关系：exact checker ⊂ strong MR；在草稿中写 LEM-CLO 链接两者（exact checker 的 violation set = \(\{P':\not\models_\tau\psi_j\}\)，对 ≡_α 封闭因 \(\models_\tau\) 经 α 定义）
- [ ] **Step 2:** 核对 S5 在 §2.8 的表述（"required where stratum labels feed downstream"）——THM-GAP 把 S5 从可选升为前提，需在正文注明"S5 不满足的变异体计入 ξ 偏差质量"
- [ ] **Step 3:** Commit

**REVIEW CHECKPOINT T2：作者确认 THM-GAP 前提强度（S5+exact checker 是否过强）与 ξ 的报告方式。此检查点通过后，论证提升计划 Phase 1 方可启动。**

---

## Phase T3：THM-WIN 检测窗（现稿 Prop 2 原位升级）

### Task T3.1：现有 Prop 2 资产盘点

- [ ] **Step 1:** `rg -n "Proposition 2|strong boundary|varepsilon_\{?\\\\mathrm\{tol\}" submission/TOSEM_regular_20260706/main.tex`，摘录 Prop 2 全文与其非形式假设进草稿
- [ ] **Step 2:** 在 `research/theory_drafts/thm_window.md` 列假设清单：观测泛函对 ε_m 的 Lipschitz 性（常数 \(L_r\)）、噪声界 \(\bar\eta\)（确定性=舍入；随机=\(c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}\)）、checker 阈值形式

### Task T3.2：起草定理与推论

**Files:** Create: `research/theory_drafts/thm_window.md`

- [ ] **Step 1:** 写入（定稿基准）：

```latex
\textbf{Theorem [THM-WIN] (tolerance-indexed detection window).} Let $m$ carry
violation magnitude $\varepsilon_m$ at stratum $\psi$, let $r$ be an exact
checker with tolerance $\varepsilon_{\mathrm{tol}}$, let
$\Delta_r:=\sup_{x\in D_r}\varepsilon_r(x;P^\star)$ be the correct-program
structure-preservation residual (the instantiation of $\Delta(S,P)$ from the
MR-validity theory on the structure inducing $r$), and $|\eta|\le\bar\eta$
the execution noise, with the violation functional $L_r$-Lipschitz in
$\varepsilon_m$. Then
(i) $\varepsilon_m>\varepsilon_{\mathrm{tol}}+\Delta_r+2\bar\eta$ implies
$r$ kills $m$; (ii) $\varepsilon_m<\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta$
implies $r$ does not kill $m$; (iii) with the crash threshold
$\varepsilon_{\mathrm{crash}}$ (S4), the kill region lies within
$(\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta,\ \varepsilon_{\mathrm{crash}})$.

\textbf{Remark [REM-FPOS] (weak-MR false positive).} If
$\mu_r=\varepsilon_{\mathrm{tol}}-\Delta_r<0$ the correct program is flagged
and $r$ exits the admissible evaluation set (empirically: the PINN case).

\textbf{Remark [REM-FNEG] (stochastic false negative and repeat prescription).}
For stochastic PUTs $\bar\eta=c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}$;
guaranteed detection at target magnitude $\varepsilon^\dagger$ requires
$N\ge\bigl(2c\sigma_{\mathrm{out}}/(\varepsilon^\dagger-\varepsilon_{\mathrm{tol}}-\Delta_r-2\eta_{\mathrm{det}})\bigr)^2$
(empirically: the RNG case).
```

（R-9：两条原拟推论改为 THM-WIN 定理环境内的 Remark，不占独立定理编号；其论证义务 PO-WIN-5/6 保留。）

- [ ] **Step 2:** 写证明（误差预算三角不等式两次；对接 §2.9 latency window 定义，(iii) 由 S4 直接）
- [ ] **Step 3:** 写"经验预测"小节：kill 概率沿 ε_m 单调、转变区宽 \(O(\Delta_r+\bar\eta)\)、中心 \(\approx\varepsilon_{\mathrm{tol}}\) —— 论证提升计划剂量反应实验 EXP-DOSE（H-DOSE）的预测来源；现有 boundary cases（PINN、RNG）改述为 Remark 实例
- [ ] **Step 4:** 写"结构命运对应"注记（≤1 段）：以 \(\mu_r\) 与 \(\Delta_r\) 把 P3 的 MR 分类形式对接 v3.1 §4.2 结构命运四分类——\(\Delta_r=0\) ↔ 精确保持（strict MR）、\(0<\Delta_r\le\varepsilon_{\mathrm{tol}}\) ↔ 近似保持（strong/tolerance MR）、\(\Delta_r>\varepsilon_{\mathrm{tol}}\) ↔ 结构破坏（weak MR，即 REM-FPOS）、\(\Delta_r(h)\to0\) ↔ 渐近保持；注明这使 THM-WIN 成为 v3.1 引理 1（\(\Delta\le\tau\Rightarrow\mathrm{Valid}\)）在变异检测语境下的定量细化
- [ ] **Step 5:** Commit

---

## Phase T4：REM-IDF 辨识性重读（THM-GAP 之 Remark，R-9 后的轻量阶段）

### Task T4.1：起草 Remark 与 LRCA 重定位段

**Files:** Create: `research/theory_drafts/rem_identifiability.md`

- [ ] **Step 1:** 写入（定稿基准；Remark 环境，无独立定理编号）：

```latex
\textbf{Remark [REM-IDF] (identifiability up to coverage classes).} Under the
assumptions of Theorem~[THM-GAP] let $\mathrm{sig}(m)=\{r\in R: r\ \text{kills}\ m\}$.
For any killed $m$, all members of $\mathrm{sig}(m)$ are checkers of the
same stratum, which identifies the fiber of $m$ exactly. For survivors,
fiber membership is identifiable only up to the partition of strata induced
by identical $R$-coverage; with a separating family (one exact checker per
stratum in $\mathrm{Cov}(R)$) the partition is trivial on $\mathrm{Cov}(R)$.
```

- [ ] **Step 2:** 论证以两句话并入 THM-GAP 讨论段（同层性=块对角矩阵直接重读；覆盖等价类粒度=survivor 行恒零的观测不可分辨），**无独立 PO**（R-9；由 T6 审计项 (8) 一并复核）；写 LRCA 重定位段：现稿贡献声明 C2–C5 = 对块结构偏离（ξ 质量）的诊断标注器，引用替换 §2.4 的功能描述句
- [ ] **Step 3:** Commit

**REVIEW CHECKPOINT T3：作者确认 THM-WIN 假设清单、REM-FPOS/REM-FNEG/REM-IDF 的 Remark 表述与既有 boundary cases 的覆盖。**

---

## Phase T5：退化定理修补（THM-DEG-R）与三态等价集成

### Task T5.1：修补退化定理

**Files:** Modify: `submission/TOSEM_regular_20260706/main.tex:688-739`（§2.6）、Appendix G 对应节

- [ ] **Step 1:** L 拆分：\(L=L_{\mathrm{lim}}\wedge L_{\mathrm{switch}}\)，\(L_{\mathrm{lim}}=(\varepsilon_{\mathrm{eq}}\to0)\wedge(K_{\mathrm{eq}}\to\infty)\wedge(\varepsilon_{\mathrm{AVP}}\to0)\)，\(L_{\mathrm{switch}}=\)（MP 集置换 ∧ 算子切换 ∧ PUT 类限制）；定理陈述改为"在 \(L_{\mathrm{switch}}\) 固定下沿 \(L_{\mathrm{lim}}\) 取极限"
- [ ] **Step 2:** Lemma 9.1 增加显式假设："\(\mathcal D_P\)（原稿 \(D_S\)，随程序记号统一改名）的支撑覆盖 \(\mathcal X_{\mathrm{adm}}\)"；无此假设时给反例注记（一行）
- [ ] **Step 3:** "almost everywhere" 改为二选一表述（浮点域有限例外集 / 连续化模型下测度零），Appendix G.3 同步
- [ ] **Step 4:** 编译验证：`cd submission/TOSEM_regular_20260706 && pdflatex -interaction=nonstopmode main.tex | tail -3`，期望无 error
- [ ] **Step 5:** Commit

### Task T5.2：三态等价状态集成（依 Task T0.2 Step 4 的登记）

**Files:** Modify: main.tex §2.3（E1∧E2 节）、§2.5

- [ ] **Step 1:** §2.3 增加三态声明：CERTIFIED_EQUIVALENT（仅证书）/ CONFIRMED_NON_EQUIVALENT（分歧见证）/ EQUIVALENCE_UNRESOLVED（E1∧E2 样本一致但无证书）；现 mp-cell（60，F-8）的 E1∧E2 判等在新口径下=unresolved，旧 SMS = SMS_strict
- [ ] **Step 2:** §2.5 向后兼容声明补一句：三态在退化极限下坍缩回经典二态（与 Lemma 9.1 一致）
- [ ] **Step 2b:** 通知论证线执行 SSOT 双口径键迁移核对（其 Task 0.2 Step 2b：旧 SMS 键 → \(\mathrm{SMS}_{\mathrm{strict}}\)、新增 \(\mathrm{SMS}_{\mathrm{cons}}\)；该核对是论证线 Phase 4 注数的前置门禁，R-7）
- [ ] **Step 3:** 编译验证 + Commit

---

## Phase T6：整合、一致性与独立审计

### Task T6.1：草稿整合进正文

**Files:** Modify: main.tex（新增 §2.10 THM-INT、§2.11 THM-GAP（含 REM-IDF Remark，R-9 不设独立小节）；§2.9 Prop 2→THM-WIN 原位升级（含 REM-FPOS/REM-FNEG）；Appendix G 新增 G.6–G.8 完整证明；正文编号由 LaTeX 分配）

- [ ] **Step 1:** 按草稿逐节移植；`[标签]` 占位符替换为正文编号，并在 notation_registry 附"标签 → 正文编号"映射表；正文只放陈述+证明思路 ≤5 行，完整证明入 Appendix
- [ ] **Step 2:** 执行 §0.4 决议的三处全文改名（按 Task T0.2 Step 5 的出现清单）：effect map \(\sigma\to\mathrm{eff}\)（含 \(\sigma^{-1}\to\mathrm{eff}^{-1}\)，§2.9 与 Appendix G 相关证明）；不变量族 \(I\to\Psi\)（§2.7 及其引用处）；\(D_S\to\mathcal D_P\)（§2.6）。改后复查：`rg -n "sigma\^\{-1\}|D_S" submission/TOSEM_regular_20260706/main.tex` 应为 0；改名单独成 commit 以便独立 revert
- [ ] **Step 3:** 更新 §1 claim-evidence map：新增三行（THM-INT、THM-GAP（含 REM-IDF）、THM-WIN → Supported (formal)）；更新 RQ1 表述为"健全性、单调性、退化与归因保证"；正文符号最小化：只保留证明链上符号，§0.2 全表导出为 Appendix notation table（R-12）
- [ ] **Step 4:** 交叉引用检查：`rg -n "Proposition 2" submission/TOSEM_regular_20260706/main.tex` 应为 0（已升级为 THM-WIN 编号并全文改引）
- [ ] **Step 5:** 编译两遍 + `grep -c "Missing character" main.log` 期望 0；Commit

### Task T6.2：独立形式审计

**Files:** Create: `docs/review_20260728/formal_audit_protocol.md`、`docs/review_20260728/formal_audit_report.md`

- [ ] **Step 1:** 写审计协议：审计人=未参与实证分析的合作者或外部同行；输入=五份草稿+main.tex §2；审计清单固定 8 项——(1) 每个定理前提在正文有定义，(2) 无循环（结论不作前提），(3) LEM-WIT 的 AVP 决定性假设成立范围，(4) THM-GAP 的 S5/exact-checker 前提与 ξ 报告一致，(5) THM-WIN 常数与 Lipschitz 假设可满足性，(6) THM-DEG-R 支撑假设与例外集表述，(7) 记号与 notation_registry（§0.2 总表）零冲突，(8) 证明步骤逐行可复核
- [ ] **Step 2:** 审计执行（外部人工步骤，等待窗口 ≤2 周；期间可并行论证提升计划 Phase 0–2）。审计顺序要求：**优先审 THM-GAP**（清单第 4 项提前），使其尽早获得审计级确认——预注册包已依赖其内部评审版，THM-GAP 若出 blocker 需按预注册修订程序（amendment 记录，载体=论证计划 `research/prereg_v2/AMENDMENTS.md`，F-7）处理
- [ ] **Step 3:** 审计意见分级处理：blocker→回对应 Phase 修正后重审该项；minor→正文修订；全部关闭后在报告尾部签"AUDIT PASS + 日期 + 草稿 SHA256"（`shasum -a 256 research/theory_drafts/*.md`）
- [ ] **Step 4:** Commit

**REVIEW CHECKPOINT T4（终检）：审计报告全绿；作者确认理论章节冻结（写作期引用基线），通知论证提升计划。预注册冻结门禁唯一 = CHECKPOINT T2（THM-GAP 内部评审，R-5），T4 不重复充当冻结门禁；T4 审计若出 blocker，按预注册 amendment 程序（载体=论证计划 `research/prereg_v2/AMENDMENTS.md`，修订记录 + 正文披露，F-7）处理，不回溯撤销已生效的冻结。**

---

## 风险与回退

| 风险 | 处置 |
|---|---|
| LEM-WIT 在随机 PUT 的 AVP 聚合语义下不成立 | 把引理限定到确定性判定语义，随机情形降为"在 AVP 判定语义下的条件版本"，THM-INT 主体不受影响 |
| THM-GAP 前提被审计判定过强 | 保留定理；冻结前=修订 A-PROV 操作化与讨论段设计（设计变更）；冻结后=按论证计划 AMENDMENTS.md 程序记录，判据不变（F-2） |
| THM-WIN 的 Lipschitz 常数 \(L_r\) 在个别 PUT 不可估 | 该 PUT 退出剂量反应实验对象清单（在论证提升计划 Phase 2 联动更新） |
| 审计超 2 周未回 | 启动第二审计人；两周为窗口非门槛，门槛是审计通过本身 |
