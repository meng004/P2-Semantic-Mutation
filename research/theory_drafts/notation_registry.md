# P3 Notation Registry

This registry freezes the local notation contract for the P3 theory
enhancement. The normative specification is §0 of
[`2026-07-28-p3-theory-enhancement.md`](../../docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md);
the table below reproduces its §0.2 columns one-to-one and adds the current
manuscript-location column required for the T0 audit.

## Audit scope and source availability

The planned audit target,
`submission/TOSEM_regular_20260706/main.tex`, is not present in this
checkout or in reachable Git objects. The repository's own evidence register
describes `TOSEM_regular_20260706/` as retained but untracked
([`docs/review_20260709/evidence_support_assessment.md`](../../docs/review_20260709/evidence_support_assessment.md),
line 27). This registry therefore uses the tracked TOSEM successor
`submission/TOSEM_fastimpact_20260707/main.tex` for every current-line
reference, while preserving the master plan's requested future symbols and
renames without treating the successor as a silent replacement for the
missing baseline.

| Audit item | Result |
|---|---|
| Working TOSEM audit source | `submission/TOSEM_fastimpact_20260707/main.tex` |
| Working-source SHA-256 | `77476da998d8ae63eacb6a7a65b8ebcaf48a037675cdc6eaf189dc46a8ad3d85` |
| Authoring-source cross-check | `source/main.tex` (`97ef9497f4a1d37216bc43aaaa308e147b5891deab154ef00ac4419a9dc00a24`) contains the same existing theory, with different line offsets |
| Planned `TOSEM_regular_20260706` source | unavailable; line-level migration to it cannot be certified in this checkout |
| Unified Framework v1.2 Appendix A | unavailable under the supplied OneDrive path, workspace, home directory, and reachable Git objects |
| Four-Pillar v1.2 §2 and MR-validity v3.1 §3 proxy texts | unavailable in this checkout and reachable Git objects |
| Local authority used for collision resolution | master-plan §0.4 conflict table, treated as a non-independent proxy |

The missing external authorities do **not** license a new notation choice.
They leave the external-source comparison open for a later audit; T6 may not
claim the master plan's “zero conflict with Appendix A” acceptance criterion
until the appendix or its prescribed proxy sources are supplied. Locally, all
future drafts must use the closed set below. A proposed new symbol requires a
master-plan update followed by a registry update before it appears in a draft
or manuscript.

## Closed symbol table

| # | Symbol | Meaning | First definition / source | Note | Current manuscript occurrence(s) |
|---|---|---|---|---|---|
| 1 | \(P,\ P'\) | 原程序 / 变异体程序 | v3.1 §2；DEF-01 | 实证章节 PUT 编号名 \(S_i\) ≙ \(P\) 的实例；禁用 \(S\) 作程序符号（避让 v3.1 模型结构 \(S\)） | `main.tex:1004-1006,1042-1055` already uses \(P,P'\) semantically; \(S_i\) remains an empirical identifier |
| 2 | \(P^\star\) | 参照正确实现 | DEF-12 | — | planned DEF-12 symbol; no literal occurrence |
| 3 | \(\Phi_P\) | 程序计算映射 \(I\circ D_h\) | v3.1 §3.1 | 原稿 \(\Phi_{S_i}\) 统一为 \(\Phi_P\) | planned; the nearby existing denotational map is at `main.tex:999-1006` |
| 4 | \(x\) | 执行输入 | v3.1 §3 | — | `main.tex:820-821,1049` |
| 5 | \(\mathcal D_P,\ \mathcal X_{\mathrm{adm}}\) | 输入抽样分布、可采输入域 | 现稿 §2.6 | 原稿 \(D_S\) 改名 \(\mathcal D_P\)（避让 v3.1 适用域 \(D\) 与结构 \(S\)） | \(D_S\): `main.tex:821,940,1811,1865`; \(\mathcal X_{\mathrm{adm}}\): `main.tex:1006,1049-1050` |
| 6 | \(\alpha,\ \equiv_\alpha\) | 语义抽象（观测）映射、α-观测等价 | 现稿 §2.2 | 四柱统计误报率写 \(\alpha_{\mathrm{FPR}}\)，不与本 α 混用 | `main.tex:1002-1009` |
| 7 | \(\mathcal C,\ c\) | 等价证书集、单个证书 | DEF-01 | 与 v3.1 谱系对象 \(K_\rho\) 的字段 \(C\) 不同对象 | planned DEF-01 symbols; current empirical certificate record is prose at `main.tex:834-845` |
| 8 | \(\varepsilon_{\mathrm{eq}},\ K_{\mathrm{eq}}\) | 判等容差、判等抽样预算 | 现稿 §2.3 | \(K_{\mathrm{eq}}\) 与 v3.1 \(K_\rho\) 不同对象 | `main.tex:775-777,820-821,1810-1813` |
| 9 | \(\mathrm{killed}(P',\mathrm{MR}_{i,k})\) | kill 谓词（AVP fail 于第 i 个 PUT 的第 k 条 MR 元组） | 现稿 §2.3 | — | existing predicate with \(s'\): `main.tex:749,851-854,1839-1842`; formal drafts use \(P'\) |
| 10 | \(r,\ R\) | 单条 MR、MR 集 | 现稿 §2.4 | 四柱 T3 的采纳集 \(S\) ≙ 本文 \(R\) | \(r\) occurs in the existing strong-MR theorem at `main.tex:1130-1145`; \(R\) is reserved for the new MR-set notation |
| 11 | \(D_r\) | \(r\) 的适用域 | v3.1 §3.3 | — | planned definition |
| 12 | \(J_r\in\{\mathrm{out,pass,fail}\}\) | 执行判定 | v3.1 §3.6 | ≡ AVP verdict；\(\mathrm{flag}(r,P'):=(J_r=\mathrm{fail})\) | planned notation; existing AVP pass/fail semantics is at `main.tex:817-818,851-854` |
| 13 | \(\varepsilon_{\mathrm{tol}},\ \varepsilon_{\mathrm{AVP}}\) | MR 检查容差、AVP 数值容差 | 现稿 §2.9 / §2.3 | \(\varepsilon_{\mathrm{tol}}\equiv\) v3.1 的 \(\tau_r\)；保留 ε 族不改记 τ | `main.tex:775-777,1062-1067,1165-1180` |
| 14 | \(\models_\tau\) | 容差语义满足关系 | 现稿 §2.7 | DEF-05 使用 | existing unindexed \(\models\): `main.tex:1019,1046-1055`; indexed form is planned |
| 15 | \(\psi_j,\ \Psi\) | 第 j 个语义不变量（层）、不变量族 \(\Psi=\{\psi_1..\psi_5\}\) | 现稿 §2.7 | 原稿记 \(I\)，改 \(\Psi\)（避让 v3.1 实现 \(I\)） | \(\psi_j\): `main.tex:1011-1034,1042-1060`; current family name \(I\) is scheduled for T6 rename |
| 16 | \(\mathrm{eff},\ \mathrm{eff}^{-1}\) | 语义效应映射、fiber 取原像 | 现稿 §2.9 | 原稿记 \(\sigma\)，改 \(\mathrm{eff}\)（避让统一框架声明结构 \(\sigma\)） | current \(\sigma\) effect map/preimage: `main.tex:1071-1085,1110-1117`; scheduled for T6 rename |
| 17 | \(M_{\mathrm{neq}},\ M_j,\ m\) | 非等价变异体全集、第 j 层 fiber、单个变异体 | DEF-07 | \(M_j=\mathrm{eff}^{-1}(\psi_j\text{-viol})\cap M_{\mathrm{neq}}\) | planned DEF-07 symbols |
| 18 | \(n,\ k,\ u,\ u_{\mathrm{neq}}\) | 已证非等价数、被杀数、悬置存活数、悬置中真非等价数 | DEF-02 | 不用 \(e^*\)（避让 v3.1 结构命运字段 \(e\)） | planned DEF-02 symbols |
| 19 | \(\mathrm{SMS}_{\mathrm{strict}},\ \mathrm{SMS}_{\mathrm{cons}},\ \mathrm{SMS}_j\) | 严格/保守口径、第 j 层层内得分 | DEF-04 / DEF-07 | — | planned; current metric is only \(\mathrm{SMS}_{i,k,j}\) at `main.tex:763-764` |
| 20 | \(w_j\) | 层权重 | DEF-07 | — | planned DEF-07 symbol |
| 21 | \(\mathrm{Cov}(R)\) | 被 \(R\) 精确检查的层指标集 | DEF-06 | 原拟 \(F_R\)，改语义算子名；与统计协方差无关 | planned DEF-06 symbol |
| 22 | \(\mathrm{Gap}_{\mathrm{aln}}(R),\ \mathrm{Gap}_{\mathrm{str}}(R)\) | 对齐缺口、强度缺口 | DEF-08 | 原拟 \(A(R)/S(R)\)；\(\mathrm{Gap}_{\mathrm{aln}}\leftrightarrow\) 四柱 \(\Omega_{\mathrm{sel}}\) | planned DEF-08 symbols |
| 23 | \(\xi(R)\) | 精确性偏差（块外 kill 质量占比） | DEF-09 | 模型检验统计量，不入 SMS；pooled 口径升 secondary confirmatory 假设 H-XI（先验地标 0.10，B-1，见论证计划 §1.2），充当 A-PROV 的 ex-post 检验器；per-cell 分布仍描述性 | planned DEF-09 symbol |
| 24 | \(\mathrm{sig}(m)\) | kill 签名 | DEF-14 | — | planned DEF-14 symbol |
| 25 | \(\varepsilon_m\) | 违反幅度 | DEF-10 | — | planned DEF-10 symbol |
| 26 | \(\Delta_r\) | 正确程序结构保持残差 \(\sup_{x\in D_r}\varepsilon_r(x;P^\star)\) | DEF-12 | = v3.1 结构保持偏差 \(\Delta(S,P)\) 的实例；对接结构命运四分类 | planned DEF-12 symbol; existing \(\Delta\) is used only for empirical contrasts |
| 27 | \(\mu_r\) | 强度边际 \(\varepsilon_{\mathrm{tol}}-\Delta_r\) | DEF-12 | — | planned DEF-12 symbol |
| 28 | \(\eta,\ \bar\eta,\ \eta_{\mathrm{det}}\) | 执行噪声、噪声界、确定性噪声分量 | DEF-11 | ↔ v3.1 预算项 \(\tau_{\mathrm{stat}}/\tau_{\mathrm{round}}/\tau_{\mathrm{obs}}\) | planned DEF-11 symbols |
| 29 | \(N,\ c,\ \sigma_{\mathrm{out}}\) | 重复执行次数、噪声集中常数、随机 PUT 输出标准差 | DEF-11 | 标准差必须写 \(\sigma_{\mathrm{out}}\)，禁用裸 \(\sigma\) | \(N\): `main.tex:777,864`; \(c,\sigma_{\mathrm{out}}\) planned |
| 30 | \(L_r\) | 违反泛函对 \(\varepsilon_m\) 的 Lipschitz 常数 | THM-WIN | 命名沿四柱 \(L_\sigma\) 风格；与 #31 的退化极限 \(L\) 不同对象 | planned THM-WIN symbol |
| 31 | \(L,\ L_{\mathrm{lim}},\ L_{\mathrm{switch}}\) | 退化极限拼合（regime） | 现稿 §2.6 | THM-DEG-R 拆分后的两段 | current \(L=L_{\mathrm{equiv}}\wedge L_{\mathrm{killed}}\wedge L_{\mathrm{mut}}\): `main.tex:918-935`; split names planned |
| 32 | \(\varepsilon_{\mathrm{lo}},\ \varepsilon_{\mathrm{crash}}\) | 检测窗下沿、崩溃阈 | DEF-13 / 现稿 S4 | — | \(\varepsilon_{\mathrm{crash}}\): `main.tex:1062-1067`; \(\varepsilon_{\mathrm{lo}}\) planned |
| 33 | \(\mathrm{supp}(\mathcal D_P)\) | 抽样分布支撑 | 现稿 Lemma 9.1 | THM-DEG-R 新增假设使用 | planned repair; current distribution is \(D_S\) at `main.tex:821,940,1811,1865` |
| 34 | S1–S5 | sanity gate 编号 | 现稿 §2.8 | 门禁标签非数学符号，沿用 | `main.tex:1042-1059` |
| 35 | E1∧E2 | 判等程序编号 | 现稿 §2.3 | 与实验标签空间分离（实验一律 `EXP-` 前缀，见论证计划 §0.3） | `main.tex:817-831,1804-1827` |

## Reserved-symbol conflict audit

The source hierarchy in the master plan is: Unified Framework v1.2 Appendix
A > Four-Pillar v1.2 > MR-validity v3.1 > P3 internal usage. Since the first
three sources are unavailable here, the following is a local implementation
of the master plan's prescribed conflict resolutions, not a substitute for
the later external comparison.

| Token | Existing P3 use in audited source | Registry resolution |
|---|---|---|
| \(S\) | \(S_i\) names empirical PUTs (`main.tex:720-725,735-764`) | Retain \(S_i\) only as an empirical identifier; all new formal program variables are \(P,P'\). |
| \(\sigma\) | Effect map and preimage (`main.tex:1071-1085,1110-1117`) | T6 must rename it and each \(\sigma^{-1}\) to \(\mathrm{eff}\) and \(\mathrm{eff}^{-1}\). New theory must not reuse bare \(\sigma\). |
| \(\rho\) | Spearman correlation in descriptive results (`main.tex:1947,2024`) | No new theoretical object uses \(\rho\); retain existing statistical prose only with its named statistic. |
| \(I\) | Invariant family (`main.tex:1011-1012,1022,1055,1150,1153,1192`) | T6 must rename the family to \(\Psi\). |
| \(e\) | Existing finite edit and effect-map argument (`main.tex:1045,1071-1084`) | The proposed unresolved-non-equivalent count remains \(u_{\mathrm{neq}}\), never \(e^*\); the existing edit variable is not repurposed. |
| \(\alpha\) | Semantic abstraction and observation equivalence (`main.tex:1002-1009`) | Retain for the existing semantic meaning; any statistical false-positive rate must be \(\alpha_{\mathrm{FPR}}\). |
| \(\tau\) | Kendall \(\tau\) occurs only in descriptive statistical results (`main.tex:1947,2024`) | Keep tolerance notation in the ε family; no theorem-level tolerance uses bare \(\tau\). |
| \(\Delta\) | Empirical contrast notation \(\Delta\mathrm{SMS}\) (`main.tex:688,1945,1971,2017,2613-2618`) | The new structural residual is specifically \(\Delta_r\), the v3.1-aligned meaning. |
| \(R\) / \(S\) as MR set | New symbols only; existing manuscript uses \(\mathrm{MR}_{i,k}\) | New MR collection is \(R\); interface prose must state that Four-Pillar \(S\) corresponds to this paper's \(R\). |
| \(\kappa\) | No current literal occurrence | Reserve Four-Pillar \(\kappa(\Gamma,\mathcal R)\); distinguish any later Cohen's κ as inter-rater agreement. |
| \(\Gamma,\mathfrak G,\lambda\) | No current literal occurrence | Do not introduce them as P3 objects. |
| \(J_\rho\) | No current literal occurrence | Use \(J_r\) only for the AVP verdict mapping in DEF-03/05. |
| \(\Omega_{\mathrm{intr}},\Omega_{\mathrm{sel}},\Omega_{\mathrm{search}}\) | No current literal occurrence | Use only in the THM-GAP interface note; map \(\mathrm{Gap}_{\mathrm{aln}}(R)\) to \(\Omega_{\mathrm{sel}}\). |

## Required manuscript-integration flags

Literal searches of the audited TOSEM source found no
`\mathrm{SMS}_{\mathrm{strict}}`, `\mathrm{SMS}_{\mathrm{cons}}`, or
`EQUIVALENCE_UNRESOLVED`. Generic prose uses “conservative” in unrelated
sentences, but it does not define the requested interval metric. T5 must
therefore perform the master-plan integration:

1. In the equivalence section, introduce
   `CERTIFIED_EQUIVALENT`, `CONFIRMED_NON_EQUIVALENT`, and
   `EQUIVALENCE_UNRESOLVED`.
2. Treat E1∧E2 sample agreement without a machine-checkable certificate as
   unresolved evidence, not a proof of equivalence.
3. Map the legacy score to \(\mathrm{SMS}_{\mathrm{strict}}\), introduce
   \(\mathrm{SMS}_{\mathrm{cons}}\), and state the degenerate-limit collapse
   back to the classical binary accounting.

These changes are recorded for
[`理论增强-phaseT5-fable.md`](../../docs/superpowers/plans/理论增强-phaseT5-fable.md)
and must target a restored `TOSEM_regular_20260706` baseline or an
author-approved successor.

## T6 rename inventory

This inventory is a mechanical migration list, not an instruction to mutate
the manuscript during T0.

| Scheduled rename | Audited TOSEM locations | Required follow-up |
|---|---|---|
| \(\sigma\to\mathrm{eff}\), \(\sigma^{-1}\to\mathrm{eff}^{-1}\) | `main.tex:1072,1083,1085,1112,1114` | Rename the effect-map definition, prose “preimage,” and all fiber expressions together; re-run a zero-match search for the former effect-map uses. |
| \(I\to\Psi\) for the invariant family | `main.tex:1012,1022,1055,1150` (two occurrences), `1153,1192` | Rename only the invariant family and references to it; do not rename unrelated textual uses or empirical identifiers. |
| \(D_S\to\mathcal D_P\) | `main.tex:821,940,1811,1865` | Rename the distribution and its valid-domain variant consistently. Synchronize the corresponding supplementary locations: `supplementary.tex:113,143,203,1132,1289,1311,1317-1319,1347-1348,1366`. |

## T0 disposition

The local source-line audit and closed notation set are frozen at the
fingerprints above. The external Appendix A/proxy comparison and the missing
planned manuscript baseline remain explicit provenance limitations rather
than inferred facts. Any later phase that claims external notation
compatibility must close those two evidence gaps first.
