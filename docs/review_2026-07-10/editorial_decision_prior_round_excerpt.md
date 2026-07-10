# 上一轮编辑决定（转录，2026-07-10 用户提供）

> 来源：用户本地 `docs/review_2026-07-10_academic_reviewer/editorial_decision_and_roadmap.md`（原件不在本仓库；本文件为 closure ledger 的引用锚点）。
> 决定：**高风险 Major Revision**；合同动作 `reject_or_major_revision`；稳定接收状态：尚未达到。

## 决定依据

五位审稿人在 mandatory dimensions 上均给出至少一个 block。最强共识：论文定义、实际 denominator、验证设计和最终 novelty claim 尚未指向同一个构念。

## 接收阻断项

### P0-1：必须固定 SMS 的 denominator 与构念

证据：§3.3.8（p.13）要求 semantic mutant 满足 S3（对 declared invariant 有 witness）；§5.9（pp.29–30）显示 292 个 admitted mutants 中 170 无 invariant flip、93 单 flip、29 多 flip。§9（p.43）三个 denominator 给出 δ=0.3142/0.4043/0.7917，certified denominator 使 6/12 PUT 消失。

必须二选一：
1. （推荐）核心贡献改写为 audited domain-semantic fault model / intent-labelled nonequivalent mutant universe + MR-relative diagnostic；SMS 标量形式继承 classical MS；放弃"所有 denominator 成员均属于 certified declared fiber"。
2. （更强）不使用被评估 MR battery，预先冻结独立 S3 certificate/fault ontology，只让 certified declared-stratum mutants 进 primary denominator，重跑主分析与外部验证。后验从 292 挑 65 个不能作为 confirmatory 修复。

验收标准：全文只保留一套 semantic candidate / active mutant / certified effect mutant / multi-stratum mutant 定义；每个 primary statistic 唯一 denominator；零招募写 non-estimable。

### P0-2：修正 formal layer

- MR-observed killed subset 与 effect-map preimage 分成两个术语；
- Theorem 3.4 改单向 soundness/closure（killed_r ⊆ active_α），删 "exactly" 与双向 duality；
- degeneration limit 明确加入 r=id，否则 Lemma G.2 不是 classical same-input kill；
- degeneration 定位为 backward-compatibility characterization；
- HOM 段落重写：证据只支持"目标编辑未出现在该 default first-order pool"。

验收标准：独立形式方法/软件测试研究者逐条复核；主文与 supplement 不再有冲突的 fiber / semantic mutant / reachability 用法。

### P0-3：修正 Study 4 的 confirmatory license

- H4‴：v7 unscreened admission 未冻结于 registration；matched screened sensitivity share=0 且 recruitment gate 不满足 → 降为 exploratory/composite-regime result，或在预注册 unscreened multi-stratum universe 上重跑。
- H2-2：Amendment v1.2 后 serving stack 与 arm 嵌套 → 只能称 composite matched-specification protocol contrast；保留 vendor claim 需 serving-stack 对称的新运行。

验收标准：每个 headline verdict 给出 frozen admission universe、generation serving stack、review gating status、cluster unit、exact licensed claim；abstract/conclusion 不得比 realized design 更强。

### P0-4：建立独立的人类/跨模型 validity gate

AI reviewer labels 对 contested family 一致性低且未进 SMS gating。分层独立审计至少覆盖：zero-flip、one-flip、multi-flip、REJECTED、UNCERTAIN、bounds="fixed"、generation-defect cases。

验收标准：预先声明 consensus/adjudication 规则；给出 human/domain-expert 与 mechanical classifier、frozen labels、cross-vendor labels 的一致性；报告 label-conditioned headline estimates；若 labels 只是 diagnostic，abstract/method/conclusion 必须明确。

### P0-5：证明独立的 decision value

aligned-over-cross 部分来自 align(j)=j 设计；industrial 34/34 由 T1 detectability admission 保证。需至少一项：
- independent/blinded fault-stratum labels 下的 alignment ranking；
- 不以被评估 MR detectability 为入选条件的 held-out real-defect corpus；
- SMS-guided MR revision 相对 classical MS / metamorphic coverage / 其他 adequacy criteria 在 held-out detection、cost、decision utility 上的增益；
- native multi-output / multi-module scientific software case。

### P0-6：投稿包必须真正 submission-ready

- 铸造 Studies 2–4 最终 Zenodo version DOI，替换 main p.47、cover letter、declarations 中的 `<VERSION-DOI-PENDING>`；
- registrations、amendments、raw packets、first-draw records、frozen labels、SSOTs、scripts、incident log 可供审稿；
- 统一 defect4MR bibliography entry 与已归档 DOI；
- 向编辑 confidentially 披露 NOETHER 作者身份、审稿状态、claim overlap；
- 去除/正确处理第一页占位 ACM DOI `10.1145/nnnnnnn.nnnnnnn`；
- 核对 bibliography 异常 pages 字段与匿名 companion 的 camera-ready 文案。

## 结构与篇幅

主文压缩到约 32–38 页可读密度；主文只保留：唯一构念与 denominator、claim/provenance matrix、一条主验证链、authoritative verdict ledger、三个 boundary results。incident chronology、secondary sensitivities、registrations、扩展证明入 supplement/artifact。

## 修订路线图（原表）

| 顺序 | 修订任务 | 类型 | 工作量 | 未完成后果 |
|---|---|---|---|---|
| R1 | 冻结唯一 denominator 与 novelty positioning | 构念 | 1–2 周 | Reject 风险极高 |
| R2 | 修正 fibers、Theorem 3.4、Lemma G.2、HOM | Formal | 1 周 | Domain reviewer block |
| R3 | 重算受 denominator 影响的 SSOT/表/结论 | Analysis | 1–2 周 | Claim–evidence 不一致 |
| R4 | 降级或重跑 H4‴ 与 H2-2 | Empirical | 3–5 天 / 3–8 周 | confirmatory 不可信 |
| R5 | 分层独立 human/cross-vendor audit | Validity | 1–3 周 | AI evidence gate 不稳定 |
| R6 | held-out decision-value validation | External validity | 3–8 周 | 停留在 construct demonstration |
| R7 | artifact 铸造、占位符替换、citation 统一 | Submission gate | 1–3 天 | Desk hold |
| R8 | 主文重构与压缩 | Editorial | 1–2 周 | 单一贡献风险 |

## 可保留的核心价值

诚实 negative results、PUT-cluster correction、claim-evidence permissions、selection-conditioned 34/34 克制表述、strong-boundary 案例、incident/SSOT 治理、kill rate / alignment / real-defect detection 构念分离。

最有希望的 TOSEM 版本："本文提出并审计一种面向 scientific-computing MR battery 的 domain-informed semantic fault-model framework，明确区分 operator intent、certified effect membership 与 MR observability，并用多研究证据揭示该框架在 attribution、tolerance、portability 和 real-defect transfer 上的有效边界。"
