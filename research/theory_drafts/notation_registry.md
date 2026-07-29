# P3 Notation Registry

This registry freezes the local notation contract for the P3 theory
enhancement. The normative specification is §0 of
[`2026-07-28-p3-theory-enhancement.md`](../../docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md);
the table below reproduces its §0.2 columns one-to-one and adds the current
manuscript-location column required for the T0 audit.

## Audit scope and source availability

The planned audit target is now tracked at
`submission/TOSEM_regular_20260706/main.tex`. It entered the base branch in
`d4c8f14`; the current audit runs against the version merged into this branch
from `8758bc6`. All current-line references below point to that committed
baseline. The earlier provisional references to the FastImpact package are
superseded.

| Audit item | Result |
|---|---|
| Working TOSEM audit source | `submission/TOSEM_regular_20260706/main.tex` |
| Main-source SHA-256 | `8c5839319455b3080e5b6915e1ef821b6b931ad5563efa558e891e97a7c7b0f8` |
| Supplementary-source SHA-256 | `dada0f9c32c95fe2ef539bfc7459617ac153e370cd163112ebe16d79d89fd33a` |
| Planned `TOSEM_regular_20260706` source | available and line-level audited |
| Authority repository | private `meng004/MR-theory@66abf5743a56576935e723ebd6f9ae789bc2e6e9`, read through the user-provided `github_token` without persisting the token |
| Unified Framework v1.2 Appendix A | `MT基础理论统一框架v1.1.md` (file-name legacy; document heading v1.2), blob `e73f77a72e21a3c00991909f2ca001f11491a497` |
| Four-Pillar v1.2 §2–§5 | `MT四柱基础理论_v1.0.md` (file-name legacy; document heading v1.2), blob `41219ecc713cc4b0e22ca9e3ae896f6d01f338fa` |
| MR-validity v3.1 §3–§4 | `MR有效性理论_v3.0_理论收敛版.md` (file-name legacy; document heading v3.1), blob `412d833ba4dd9921661007461c4ecf2cd6618b96` |
| Authority used for collision resolution | Unified Framework v1.2 Appendix A, confirmed by the Four-Pillar and MR-validity cross-references |

Drift note (2026-07-28, post-T5): the Phase T5 manuscript edits to §2.3, §2.5,
§2.6 (main.tex) and G.2–G.4 (supplementary.tex) shift line numbers after
main.tex:592 relative to the fingerprinted baseline above. The occurrence
columns below record the pre-T5 baseline; Task T6.1 must re-run the occurrence
scans before executing the migrations (already a T6.1 step).

Both the baseline source and the external authority source are now available.
The authority comparison found three additional collisions in the initial P3
contract: \(\alpha\) is reserved for the unified framework's effect
abstraction, bare \(m\) is reserved for MetaPattern, and bare \(e\) is a
v3.1 structure-fate field. The resolutions below are binding on all later
drafts and the T6 manuscript migration. A proposed new symbol requires a
master-plan update followed by a registry update before it appears in a draft
or manuscript.

## External authority comparison

| Authority symbol | Authority meaning | Prior P3 use | Resolution |
|---|---|---|---|
| \(\sigma\) | Unified Framework Appendix A: model structure \((R_X,R_Y)\) | Effect map | Keep the planned \(\sigma\to\mathrm{eff}\) migration. |
| \(I\) | MR-validity Appendix A: program implementation in \(P=(M,D_h,I)\) | Invariant family | Keep the planned \(I\to\Psi\) migration. |
| \(\alpha\) | Unified Framework Definition 10: effect abstraction \(\alpha:\mathcal P_\Gamma\to E\) | Observation mapping and equivalence | Rename P3's mapping and equivalence to \(\mathrm{obs}\) and \(\equiv_{\mathrm{obs}}\); reserve \(\alpha\) for quoted external statistical semantics only. |
| \(m\) | Unified Framework Appendix A: MetaPattern only | A single mutant | Rename to \(m_{\mathrm{mut}}\); rename the associated magnitude to \(\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\). |
| \(e\) | MR-validity §3.8: structure-fate field of \(K_\rho\) | Finite AST edit and \(P_e\) | Rename to \(\mathrm{edit}\) and \(P_{\mathrm{edit}}\). |
| \(S\) | v3.1 model structure; Four-Pillar T3 adopted relation set | PUT identifier \(S_i\) | Retain \(S_i\) only as an empirical identifier; all new formal program variables are \(P,P'\), and the P3 MR collection is \(R\). |
| \(\rho,\Gamma,\mathfrak G,\lambda,\kappa\) | Candidate MR, theory context, generation map, layer, minimum-completeness cardinality | No new P3 theory object | Preserve the existing ban and scoped interface-only use. |
| \(\tau,\Delta,J_\rho\) | Error budget, structure-preservation deviation, execution verdict | ε-family tolerance, \(\Delta_r\), \(J_r\) | Preserve the ε-family, the v3.1-aligned \(\Delta_r\), and the typed AVP verdict adaptation \(J_r\). |

## Closed symbol table

| # | Symbol | Meaning | First definition / source | Note | Current manuscript occurrence(s) |
|---|---|---|---|---|---|
| 1 | \(P,\ P'\) | 原程序 / 变异体程序 | v3.1 §2；DEF-01 | 实证章节 PUT 编号名 \(S_i\) ≙ \(P\) 的实例；禁用 \(S\) 作程序符号（避让 v3.1 模型结构 \(S\)） | `main.tex:759-761,797-810` already uses \(P,P'\) semantically; \(S_i\) remains an empirical identifier |
| 2 | \(P^\star\) | 参照正确实现 | DEF-12 | — | planned DEF-12 symbol; no literal occurrence |
| 3 | \(\Phi_P\) | 程序计算映射 \(I\circ D_h\) | v3.1 §3.1 | 原稿 \(\Phi_{S_i}\) 统一为 \(\Phi_P\) | planned; the nearby existing denotational map is at `main.tex:754-761` |
| 4 | \(x\) | 执行输入 | v3.1 §3 | — | `main.tex:604-605,804` |
| 5 | \(\mathcal D_P,\ \mathcal X_{\mathrm{adm}}\) | 输入抽样分布、可采输入域 | 现稿 §2.6 | 原稿 \(D_S\) 改名 \(\mathcal D_P\)（避让 v3.1 适用域 \(D\) 与结构 \(S\)） | \(D_S\): `main.tex:605,709,719,1486,1538`; \(\mathcal X_{\mathrm{adm}}\): `main.tex:761,804-805` |
| 6 | \(\mathrm{obs},\ \equiv_{\mathrm{obs}}\) | 语义观测映射、观测等价 | 现稿 §2.2；统一框架 v1.2 Definition 10 / Appendix A | 原稿 \(\alpha,\equiv_\alpha\) 改为 \(\mathrm{obs},\equiv_{\mathrm{obs}}\)，避让统一框架唯一效应抽象 \(\alpha\) | current semantic-\(\alpha\) uses: `main.tex:757-764,768,781,804,829-920,2566`; T6 migration pending |
| 7 | \(\mathcal C,\ c\) | 等价证书集、单个证书 | DEF-01 | 与 v3.1 谱系对象 \(K_\rho\) 的字段 \(C\) 不同对象 | planned DEF-01 symbols; no literal occurrence |
| 8 | \(\varepsilon_{\mathrm{eq}},\ K_{\mathrm{eq}}\) | 判等容差、判等抽样预算 | 现稿 §2.3 | \(K_{\mathrm{eq}}\) 与 v3.1 \(K_\rho\) 不同对象 | `main.tex:559-560,604-605,1485-1488` |
| 9 | \(\mathrm{killed}(P',\mathrm{MR}_{i,k})\) | kill 谓词（AVP fail 于第 i 个 PUT 的第 k 条 MR 元组） | 现稿 §2.3 | — | existing predicate with \(s'\): `main.tex:532,622-625,1512-1514`; formal drafts use \(P'\) |
| 10 | \(r,\ R\) | 单条 MR、MR 集 | 现稿 §2.4 | 四柱 T3 的采纳集 \(S\) ≙ 本文 \(R\) | \(r\) occurs in the existing strong-MR theorem at `main.tex:862-872`; \(R\) occurs in `supplementary.tex:117` and is reserved for the new MR-set notation |
| 11 | \(D_r\) | \(r\) 的适用域 | v3.1 §3.3 | — | planned definition |
| 12 | \(J_r\in\{\mathrm{out,pass,fail}\}\) | 执行判定 | v3.1 §3.6 | ≡ AVP verdict；\(\mathrm{flag}(r,P'):=(J_r=\mathrm{fail})\) | planned notation; existing AVP pass/fail semantics is at `main.tex:601-602,622-625` |
| 13 | \(\varepsilon_{\mathrm{tol}},\ \varepsilon_{\mathrm{AVP}}\) | MR 检查容差、AVP 数值容差 | 现稿 §2.9 / §2.3 | \(\varepsilon_{\mathrm{tol}}\equiv\) v3.1 的 \(\tau_r\)；保留 ε 族不改记 τ | `main.tex:559-560,817-822,891-906` |
| 14 | \(\models_\tau\) | 容差语义满足关系 | 现稿 §2.7 | DEF-05 使用 | existing unindexed \(\models\): `main.tex:774,798-810`; indexed form is planned |
| 15 | \(\psi_j,\ \Psi\) | 第 j 个语义不变量（层）、不变量族 \(\Psi=\{\psi_1..\psi_5\}\) | 现稿 §2.7 | 原稿记 \(I\)，改 \(\Psi\)（避让 v3.1 实现 \(I\)） | \(\psi_j\): `main.tex:766-790,797-815`; current family name \(I\) is scheduled for T6 rename |
| 16 | \(\mathrm{eff},\ \mathrm{eff}^{-1}\) | 语义效应映射、fiber 取原像 | 现稿 §2.9 | 原稿记 \(\sigma\)，改 \(\mathrm{eff}\)（避让统一框架声明结构 \(\sigma\)） | current \(\sigma\) effect map/preimage: `main.tex:826-834,848-855`; scheduled for T6 rename |
| 17 | \(M_{\mathrm{neq}},\ M_j,\ m_{\mathrm{mut}}\) | 非等价变异体全集、第 j 层 fiber、单个变异体 | DEF-07；统一框架 v1.2 Appendix A | \(M_j=\mathrm{eff}^{-1}(\psi_j\text{-viol})\cap M_{\mathrm{neq}}\)；不用裸 \(m\)（该符号仅指 MetaPattern） | planned DEF-07 symbols |
| 18 | \(n,\ k,\ u,\ u_{\mathrm{neq}}\) | 已证非等价数、被杀数、悬置存活数、悬置中真非等价数 | DEF-02 | 不用裸 \(e\) 或 \(e^*\)（避让 v3.1 结构命运字段 \(e\)） | planned DEF-02 symbols |
| 19 | \(\mathrm{SMS}_{\mathrm{strict}},\ \mathrm{SMS}_{\mathrm{cons}},\ \mathrm{SMS}_j\) | 严格/保守口径、第 j 层层内得分 | DEF-04 / DEF-07 | — | planned; current metric is only \(\mathrm{SMS}_{i,k,j}\) at `main.tex:547` |
| 20 | \(w_j\) | 层权重 | DEF-07 | — | planned DEF-07 symbol |
| 21 | \(\mathrm{Cov}(R)\) | 被 \(R\) 精确检查的层指标集 | DEF-06 | 原拟 \(F_R\)，改语义算子名；与统计协方差无关 | planned DEF-06 symbol |
| 22 | \(\mathrm{Gap}_{\mathrm{aln}}(R),\ \mathrm{Gap}_{\mathrm{str}}(R)\) | 对齐缺口、强度缺口 | DEF-08 | 原拟 \(A(R)/S(R)\)；\(\mathrm{Gap}_{\mathrm{aln}}\leftrightarrow\) 四柱 \(\Omega_{\mathrm{sel}}\) | planned DEF-08 symbols |
| 23 | \(\xi(R)\) | 精确性偏差（块外 kill 质量占比） | DEF-09 | 模型检验统计量，不入 SMS；pooled 口径升 secondary confirmatory 假设 H-XI（先验地标 0.10，B-1，见论证计划 §1.2），充当 A-PROV 的 ex-post 检验器；per-cell 分布仍描述性 | planned DEF-09 symbol |
| 24 | \(\mathrm{sig}(m_{\mathrm{mut}})\) | kill 签名 | DEF-14 | — | planned DEF-14 symbol |
| 25 | \(\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\) | 违反幅度 | DEF-10 | — | planned DEF-10 symbol |
| 26 | \(\Delta_r\) | 正确程序结构保持残差 \(\sup_{x\in D_r}\varepsilon_r(x;P^\star)\) | DEF-12 | = v3.1 结构保持偏差 \(\Delta(S,P)\) 的实例；对接结构命运四分类 | planned DEF-12 symbol; existing \(\Delta\) is used only for empirical contrasts |
| 27 | \(\mu_r\) | 强度边际 \(\varepsilon_{\mathrm{tol}}-\Delta_r\) | DEF-12 | — | planned DEF-12 symbol |
| 28 | \(\eta,\ \bar\eta,\ \eta_{\mathrm{det}}\) | 执行噪声、噪声界、确定性噪声分量 | DEF-11 | ↔ v3.1 预算项 \(\tau_{\mathrm{stat}}/\tau_{\mathrm{round}}/\tau_{\mathrm{obs}}\) | planned DEF-11 symbols |
| 29 | \(N,\ c,\ \sigma_{\mathrm{out}}\) | 重复执行次数、噪声集中常数、随机 PUT 输出标准差 | DEF-11 | 标准差必须写 \(\sigma_{\mathrm{out}}\)，禁用裸 \(\sigma\) | \(N\): `main.tex:560,635`; \(c,\sigma_{\mathrm{out}}\) planned |
| 30 | \(L_r\) | 违反泛函对 \(\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\) 的 Lipschitz 常数 | THM-WIN | 命名沿四柱 \(L_\sigma\) 风格；与 #31 的退化极限 \(L\) 不同对象 | planned THM-WIN symbol |
| 31 | \(L,\ L_{\mathrm{lim}},\ L_{\mathrm{switch}}\) | 退化极限拼合（regime） | 现稿 §2.6 | THM-DEG-R 拆分后的两段 | current \(L=L_{\mathrm{equiv}}\wedge L_{\mathrm{killed}}\wedge L_{\mathrm{mut}}\): `main.tex:688-705`; split names planned |
| 32 | \(\varepsilon_{\mathrm{lo}},\ \varepsilon_{\mathrm{crash}}\) | 检测窗下沿、崩溃阈 | DEF-13 / 现稿 S4 | — | \(\varepsilon_{\mathrm{crash}}\): `main.tex:817-822`; \(\varepsilon_{\mathrm{lo}}\) planned |
| 33 | \(\mathrm{supp}(\mathcal D_P)\) | 抽样分布支撑 | 现稿 Lemma 9.1 | THM-DEG-R 新增假设使用 | planned repair; current distribution is \(D_S\) at `main.tex:605,709,719,1486,1538` |
| 34 | S1–S5 | sanity gate 编号 | 现稿 §2.8 | 门禁标签非数学符号，沿用 | `main.tex:792-815` |
| 35 | E1∧E2 | 判等程序编号 | 现稿 §2.3 | 与实验标签空间分离（实验一律 `EXP-` 前缀，见论证计划 §0.3） | `main.tex:601-615,1479-1505` |
| 36 | \(\mathrm{edit},\ P_{\mathrm{edit}}\) | 有限 AST 编辑算子、其作用后的程序 | 现稿 §2.8；MR-validity v3.1 §3.8 | 原稿 \(e,P_e\) 改为语义命名，避让 v3.1 结构命运字段 \(e\) | current bare-\(e\) uses: `main.tex:800,827-840,869-872,917`; T6 migration pending |

## Reserved-symbol conflict audit

The source hierarchy in the master plan is: Unified Framework v1.2 Appendix
A > Four-Pillar v1.2 > MR-validity v3.1 > P3 internal usage. The preceding
Git-backed comparison applies that hierarchy directly; this table records the
concrete P3 migration work that follows from it.

| Token | Existing P3 use in audited source | Registry resolution |
|---|---|---|
| \(S\) | \(S_i\) names empirical PUTs (`main.tex:520-547,601-605`) | Retain \(S_i\) only as an empirical identifier; all new formal program variables are \(P,P'\). |
| \(\sigma\) | Effect map and preimage (`main.tex:826-834,848-855`) | T6 must rename it and each \(\sigma^{-1}\) to \(\mathrm{eff}\) and \(\mathrm{eff}^{-1}\). New theory must not reuse bare \(\sigma\). |
| \(\rho\) | Spearman correlation in descriptive results (`main.tex:1609`) | No new theoretical object uses \(\rho\); retain existing statistical prose only with its named statistic. |
| \(I\) | Invariant family (`main.tex:766-767,777,810,831,876,879,917`) | T6 must rename the family to \(\Psi\). |
| \(e\) | MR-validity v3.1 structure-fate field; P3 finite edit and effect-map argument (`main.tex:800,826-840`) | Rename the P3 edit and its result to \(\mathrm{edit},P_{\mathrm{edit}}\); retain \(u_{\mathrm{neq}}\), never \(e^*\), for unresolved non-equivalence. |
| \(m\) | Unified Framework v1.2 MetaPattern-only symbol | Do not use bare \(m\) for a mutant; use \(m_{\mathrm{mut}}\) and \(\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\). |
| \(\alpha\) | Unified Framework v1.2 effect abstraction; current P3 semantic observation (`main.tex:757-920,2566`) | Rename the P3 observation to \(\mathrm{obs}\) and its equivalence to \(\equiv_{\mathrm{obs}}\). Keep only scoped external/statistical identifiers such as \(\alpha_{\mathrm{FDR}}\) after per-use review. |
| \(\tau\) | Kendall \(\tau\) occurs only in descriptive statistical results (`main.tex:1609`) | Keep tolerance notation in the ε family; no theorem-level tolerance uses bare \(\tau\). |
| \(\Delta\) | Empirical contrast notation \(\Delta\mathrm{SMS}\) (`main.tex:484,1120,1607,1842,1882-1887`) | The new structural residual is specifically \(\Delta_r\), the v3.1-aligned meaning. |
| \(R\) / \(S\) as MR set | New symbols only; existing manuscript uses \(\mathrm{MR}_{i,k}\) | New MR collection is \(R\); interface prose must state that Four-Pillar \(S\) corresponds to this paper's \(R\). |
| \(\kappa\) | No current literal occurrence | Reserve Four-Pillar \(\kappa(\Gamma,\mathcal R)\); distinguish any later Cohen's κ as inter-rater agreement. |
| \(\Gamma,\mathfrak G,\lambda\) | No current literal occurrence | Do not introduce them as P3 objects. |
| \(J_\rho\) | No current literal occurrence | Use \(J_r\) only for the AVP verdict mapping in DEF-03/05. |
| \(k\) (subscript/index) | Manuscript MP/relation index in \(\mathrm{MR}_{i,k}\), \(\mathrm{SMS}_{i,k,j}\), \(\varepsilon_{\mathrm{AVP}}^k\) | #18 killed count \(k\) collides in prose | Context isolation (checkpoint consolidated review, repair C3): the count symbols \(n,k,u\) appear only inside the integrated theory sections with a local-scope sentence at first use (T6.1 duty); the §2.3 three-state paragraph uses prose, no count formulas. |
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
and target the committed `submission/TOSEM_regular_20260706` baseline.

## T6 rename inventory

This inventory is a mechanical migration list, not an instruction to mutate
the manuscript during T0.

| Scheduled rename | Audited TOSEM locations | Required follow-up |
|---|---|---|
| \(\sigma\to\mathrm{eff}\), \(\sigma^{-1}\to\mathrm{eff}^{-1}\) | `main.tex:827,832,834,850,852` | Rename the effect-map definition, prose “preimage,” and all fiber expressions together; re-run a zero-match search for the former effect-map uses. |
| \(I\to\Psi\) for the invariant family | `main.tex:767,777,810,831,876` (two occurrences), `879,917` | Rename only the invariant family and references to it; do not rename unrelated textual uses or empirical identifiers. |
| \(D_S\to\mathcal D_P\) | `main.tex:605,709,719,1486,1538` | Rename the distribution and its valid-domain variant consistently. Synchronize the corresponding supplementary locations: `supplementary.tex:111,141,201,1247,1249,1269,1275-1277,1305,1323`. |
| \(\alpha,\equiv_\alpha\to\mathrm{obs},\equiv_{\mathrm{obs}}\) | `main.tex:757-764,768,781,804,829-920,2566` | Rename only the semantic-observation usage. Review the unrelated MLP hyperparameter at `main.tex:2126` and the supplementary statistical/scale parameters individually. |
| \(e,P_e\to\mathrm{edit},P_{\mathrm{edit}}\) | `main.tex:800,827-840,869-872,917` | Rename the finite AST-edit operator, the derived-program subscript, and every theory reference as one scoped change. |

## T0 disposition

The committed-baseline source-line audit and the external authority comparison
are frozen at the fingerprints and Git blob identifiers above. The comparison
found and resolved the \(\alpha\), \(m\), and \(e\) collisions before any
theorem drafting. T6 must implement the five scoped manuscript migrations
listed above before it can claim notation compatibility.
