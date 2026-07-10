# 编辑决定：与 ACM TOSEM 稳定接收之间的差距

**决定：高风险 Major Revision**
**合同动作：** `reject_or_major_revision`
**稳定接收状态：** 尚未达到。仅修辞、补充 limitation 或再做语言润色，不能把稿件推进到稳定接收区。

## 1. 决定依据

五位审稿人在 mandatory dimensions 上均给出至少一个 `block`。最强共识不是“实验量不够”，而是：论文定义、实际 denominator、验证设计和最终 novelty claim 尚未指向同一个构念。

本稿具备明显的可发表潜力：主题适配、数据与过程透明、负结果诚实、统计修正意识强、artifact 治理投入大。因此不建议直接放弃。但若作者坚持当前“new metric + strict generalization + declared semantic-effect fibers + confirmatory closure”的整体叙事，而只增加 caveat，真实外审结果更可能是 Reject。

## 2. 接收阻断项

### P0-1：必须固定 SMS 的 denominator 与构念

**证据：** §3.3.8（p.13）要求 semantic mutant 满足 S3，即对 declared invariant 有 witness；§5.9（pp.29–30）却显示 292 个 admitted mutants 中 170 个无 invariant flip、93 个单 flip、29 个多 flip。§9（p.43）的三个 denominator 给出 \(\delta=0.3142/0.4043/0.7917\)，且 certified denominator 使 6/12 PUT 消失。

**必须二选一：**

1. **推荐、较稳妥的重定位方案：** 把核心贡献改写为“audited domain-semantic fault model / intent-labelled nonequivalent mutant universe + MR-relative diagnostic”，明确 SMS 的标量形式继承 classical MS；放弃“所有 denominator 成员均属于 certified declared fiber”的主张。
2. **更强、但代价更大的验证方案：** 在不使用被评估 MR battery 的前提下，预先冻结独立 S3 certificate/fault ontology，只让 certified declared-stratum mutants 进入 primary denominator，然后重新运行主分析与外部验证。后验从 292 中挑 65 个不能作为 confirmatory 修复。

**验收标准：** 全文只能保留一套 semantic candidate / active mutant / certified effect mutant / multi-stratum mutant 定义；每个 primary statistic 明确对应唯一 denominator；零招募必须写作 non-estimable，而不是 adequacy=0。

### P0-2：修正 formal layer

必须完成：

- 把 §3.3.1 的 MR-observed killed subset 与 §3.3.9 的 effect-map preimage 分成两个术语。
- 将 Theorem 3.4 改为单向 soundness/closure：\(killed_r\subseteq active_\alpha\)，删除“exactly”与双向 duality 暗示。
- 在 degeneration limit 明确加入 \(r=id\)，否则 Lemma G.2 不是 classical same-input kill。
- 将 degeneration 定位为 backward-compatibility characterization，而非独立的强数学新颖性。
- 重写 HOM 段落：当前证据只支持“目标编辑未出现在该 default first-order pool”，不支持一般不可达。

**验收标准：** 由独立形式方法/软件测试研究者逐条复核定义、命题和 proof；主文与 supplement 不再出现相互冲突的 fiber、semantic mutant 或 reachability 用法。

### P0-3：修正 Study 4 的 confirmatory license

**H4‴：** v7 unscreened admission 未在 registration 中冻结；matched screened sensitivity 的 share=0 且 recruitment gate 不满足。当前应降为 exploratory/composite-regime result，或在预注册的 unscreened multi-stratum universe 上重新运行。

**H2-2：** Amendment v1.2 后 serving stack 与 arm 嵌套。当前只能称为 composite matched-specification protocol contrast，不能作为干净的 source/vendor-diversity estimand。若要保留 vendor claim，需要 serving-stack 对称的新运行。

**验收标准：** 每个 headline verdict 同时给出 frozen admission universe、generation serving stack、review gating status、cluster unit 与 exact licensed claim；abstract 和 conclusion 不得比 realized design 更强。

### P0-4：建立独立的人类/跨模型 validity gate

AI reviewer labels 对 contested family 的一致性很低，而这些 labels 又未进入 SMS gating。必须做分层独立审计，至少覆盖：zero-flip、one-flip、multi-flip、REJECTED、UNCERTAIN、`bounds="fixed"` 和 generation-defect cases。

**验收标准：**

- 预先声明 consensus/adjudication 规则；
- 给出 human/domain-expert 与 mechanical classifier、frozen labels、cross-vendor labels 的一致性；
- 报告 label-conditioned headline estimates；
- 若 labels 只是 diagnostic，abstract、method 与 conclusion 必须明确，不得用“dual-blind validated pool”造成 gating 幻觉。

### P0-5：证明独立的 decision value

当前 aligned-over-cross 关系部分来自 `align(j)=j` 的设计；industrial 34/34 又由 T1 detectability admission 保证。它们支持 internal consistency/construct separation，但不证明 SMS 能改善实际 MR 选择。

达到“稳定接收”最有价值的新增证据是以下至少一项：

- independent/blinded fault-stratum labels 下的 alignment ranking；
- 不以任何被评估 MR detectability 作为入选条件的 held-out real-defect corpus；
- SMS-guided MR revision 相对 classical MS、metamorphic coverage 或其他 adequacy criteria，在 held-out defect detection、cost 或 decision utility 上的增益；
- 一个 native multi-output / multi-module scientific software case，而非仅 scalar port。

没有这一项，论文仍可作为 construct-development framework 竞争 TOSEM，但难称“稳定接收”。

### P0-6：投稿包必须真正 submission-ready

提交前必须：

- 铸造 Studies 2–4 的最终 Zenodo version DOI，替换 main p.47、cover letter 与 declarations 中的 `<VERSION-DOI-PENDING>`；
- 确保 registrations、amendments、raw packets、first-draw records、frozen labels、SSOTs、scripts 和 incident log 可供审稿；
- 统一 defect4MR 的 bibliography entry 与已归档 DOI；
- 向编辑 confidentially 披露 NOETHER 的作者身份、审稿状态和 claim overlap；
- 去除或正确处理第一页的占位 ACM DOI `10.1145/nnnnnnn.nnnnnnn`；
- 核对 bibliography 中的异常 pages 字段和匿名 companion 的 camera-ready 文案。

## 3. 结构与篇幅差距

TOSEM Regular 的核心问题不是硬页数，而是 50 页主文 + 37 页 supplement 是否服务于一个清晰的 archival claim。当前 Introduction、Studies 2–4、Threats 和十点 Conclusion 多次重复同一 chronology 与 verdict。

**建议目标：** 主文压缩到约 32–38 页的可读密度，而不是机械追求页数；主文只保留：

1. 唯一构念与 denominator；
2. 一张 claim/provenance matrix；
3. 一条主验证链；
4. 一张 authoritative verdict ledger；
5. 三个明确 boundary results。

incident chronology、secondary sensitivities、完整 registrations、扩展证明和大部分 follow-up detail 放入 supplement/artifact。

## 4. 推荐修订路线图

| 顺序 | 修订任务 | 类型 | 预计工作量 | 未完成后果 |
|---|---|---|---:|---|
| R1 | 冻结唯一 denominator 与 novelty positioning | 核心理论/构念 | 1–2 周 | Reject 风险极高 |
| R2 | 修正 fibers、Theorem 3.4、Lemma G.2、HOM | Formal correctness | 1 周 | Domain reviewer block |
| R3 | 重算所有受 denominator 影响的 SSOT、表与结论 | Analysis | 1–2 周 | Claim–evidence 不一致 |
| R4 | 降级或重跑 H4‴ 与 H2-2 | Empirical design | 文本降级 3–5 天；重跑 3–8 周 | “confirmatory”不可信 |
| R5 | 分层独立 human/cross-vendor audit | Validity | 1–3 周 | AI evidence gate 不稳定 |
| R6 | 增加一项 held-out decision-value validation | External validity | 3–8 周 | 仍停留在 construct demonstration |
| R7 | 铸造完整 artifact、替换 placeholders、统一 citations | Submission gate | 1–3 天 | Desk hold / reviewer无法核验 |
| R8 | 主文重构与压缩 | Editorial | 1–2 周 | EIC 可读性/单一贡献风险 |

## 5. 分阶段判断

| 完成状态 | 预计审稿区间 |
|---|---|
| 当前版本 | 不具备稳定接收条件；F1 block；投稿包也未完成 |
| 仅完成 DOI、格式和语言修订 | 仍是 Major/Reject；核心构念问题未动 |
| 统一定义并修正文理，但不重算/不审计 | 仍是 Major Revision；证据与新定义不匹配 |
| 完成构念重定位、全量重算、Study-4 claim 校准、独立审计 | 进入有竞争力的 Major-to-Minor 区间 |
| 再加一项独立 held-out utility/external validation，并压缩成单一贡献 | 才接近“稳定接收候选” |

这里不提供伪精确的接收概率。当前 reviewer rubric 未经过 TOSEM gold-set calibration；数值概率会制造虚假确定性。可信结论是顺序性的：本稿的潜力高，但距离稳定接收仍隔着一次 substantive redesign，而不是一次 polishing pass。

## 6. 可保留的核心价值

修订时不要丢掉以下优势：诚实的 negative results、PUT-cluster correction、claim-evidence permissions、selection-conditioned 34/34 的克制表述、strong-boundary 案例、incident/SSOT 治理，以及 kill rate / alignment / real-defect detection 的构念分离。

最有希望的 TOSEM 版本不是“SMS 已被四个研究全面确认”，而是：

> 本文提出并审计一种面向 scientific-computing MR battery 的 domain-informed semantic fault-model framework，明确区分 operator intent、certified effect membership 与 MR observability，并用多研究证据揭示该框架在 attribution、tolerance、portability 和 real-defect transfer 上的有效边界。

这个版本的 novelty 更窄，但更可信，也更符合当前证据。
