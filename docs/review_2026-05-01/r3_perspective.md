# Reviewer 3 Report — Cross-disciplinary / Practical Perspective

> **Manuscript**: When LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Scientific Computing (P2)
> **Reviewer date**: 2026-05-01
> **Review pass**: independent (未阅读其他 reviewer 报告)

---

## 1. Reviewer identity

- 计算科学软件工程师,15 年 large-scale CFD / nuclear engineering simulation
- ASME V&V (Verification & Validation) 委员会 + IEC 60880 nuclear-safety software 委员会成员
- Pragmatic skeptic:对**只能在论文里被引用、不能在 qualification dossier 里被引用**的"研究指标"持系统性怀疑
- 评审重心:metric 是否能离开实验室 (Does this metric ever leave the lab?)

---

## 2. Summary

本文在 12 PUT × 5 MP 的 60 单元格上对 LLM-生成 mutant 做了一次相当扎实的经验审计,提出 Semantic Mutation Score (SMS) 作为 metamorphic testing adequacy 的 domain-aware 度量,并诚实报告 H2 (Cliff's δ ≥ 0.474) **未达成**。三阶段 ablation (v3 / v3b / v4) 把"MR-MP 对齐设计"与"LLM 源多样性"两个工程因子分离,是方法学贡献 (§4.2.5);§9 SMS-MS 退化定理把度量与 Jia & Harman (2011) 经典 MS 形式上对接,是理论上的良好工程姿态。

但从一个 "industry V&V engineer" 的视角看,这篇文章的**deployability claim 被 oversold 了三处**:

1. **§6.5.3 Auditor pathway 是研究演讲,不是认证语言**——现行 IEC 60880 / ISO 26262 / ASME V&V 文本中均无 mutation testing acceptance criteria,SMS ≥ 0.30 + C1_share ≤ 0.20 没有任何 normative basis。
2. **"Scientific computing" 标题 vs §3.1.1 admitted 4 missing chapters**——PDE advanced solvers / FFT / optimization / symbolic 4 章未覆盖,而这恰恰是 CFD / 量子化学 / 信号处理的主体;`program(x: float) → float` 标量签名进一步把工业级 PUT 排除在外。这构成 title overreach。
3. **REPRODUCIBILITY.md 的双 env-var 陷阱 (`SMS_VERSION=v4` + `P2_PRIMARY_VERSION=v3b`)** 加上 v1/v2/v3/v3b/v4 多版本 SSOT 共存,对一个工业 QA 团队来说,**默认配置下复现的不是论文里的数字**。这种 reproducibility 是"作者能复现"而不是"独立第三方能复现"。

整体上 P2 是一篇好的"研究内"经验论文 (good empirical study within the SE research community),但作为对**工程领域实际部署**的贡献尚不成立。建议 **Major Revision**:大幅压缩 §6.5.3 的 auditor 主张,纠正标题域的 overreach,简化 reproducibility 入口。

---

## 3. Strengths (cross-disciplinary / practical 视角)

1. **Honest negative result reporting (§5.7.2 / Abstract)**——明确声明 pre-registered H2 rejected (δ = 0.323 < 0.474),并把 v3b 的 +0.123 提升标注为 exploratory + selection-on-the-response。这是 industry V&V 文化中最难得的姿态,远胜于绝大多数把 marginal-significance 包装成 finding 的 SE 论文。
2. **三阶段 ablation 设计 (§4.2.5)**——把 "MR-MP 对齐 vs LLM 源多样性" 两个工程因子做正交分解 (Δδ_MR = +0.123, Δδ_LLM = −0.007),分子分母分别报告而非合成单一 ratio,方法学上比 Tip et al. (2024) 的单 LLM 实验更稳健。如果 finding 真的是 "LLM 源多样性贡献 ≈ 0",那对工业 mutant 池构建是有用的工程指导(不要为多家 LLM 付钱)。
3. **§3.2.6 + §3.2.6.1 工具级算子对照**——对 mutmut / cosmic-ray 默认算子集做一一映射,论证 OS / HP / TF / SI 4 类在 first-order 语法工具上结构性不可达。这是我作为 CFD 工程师能直接给同事看的一段:它解释了为什么 syntactic mutation 工具在我们的 codebase 里"杀掉所有 mutant 但什么 bug 也没找到"。
4. **§9 SMS-MS 退化定理**——形式上保证 SMS 在 syntactic limit 退化为经典 MS。这是在 V&V 委员会上为新度量辩护时的标准要求 (`backward compatibility with established metric`)。完成度高于多数 "我们提出新度量" 类论文。
5. **§7.5 Limitations 与 §1.6.2 认识论声明**——明确 "SMS 不是工程价值代理量,工程价值由 P2-CN/P5 处理"。这个声明在 §6.5 的 auditor 部分**没有被一致执行**(见 Weakness 1),但至少在 limitations 章节是诚实的。
6. **Petrović & Ivanković (2018) numerical coincidence 处理 (§6.1)**——明确把 productive ~20% 的数值近似声明为 numerical coincidence 而非 mechanism validation,并指出 construct 差异(developer survey 主观 vs LRCA 自动分类器)。这是诚实的科学判断,我在 review 过程中本来准备提的质疑被作者自己提前消解了。

---

## 4. Weaknesses (5–10 条;WHAT / WHERE / FIX)

### W1 §6.5.3 Auditor pathway 的 normative claim 在现行 IEC/ISO/ASME 文本中无依据 [MAJOR]

**WHAT**: §6.5.3 提出 "aligned-cell SMS ≥ 0.30 + C1_share ≤ 0.20 = 充分" 作为审计 / 认证机构的接收阈值建议。文中虽有 "**研究建议,非强制行业标准**" 的限定语,但仍把 NRC / FDA / ISO 26262 评审组列为 stakeholder,把 SMS 列为 "可重现、可量化的辅助证据"。

**WHERE**: §6.5.3 lines 1352–1364, 特别是 "接收阈值建议" 子段。

**问题**:
- **IEC 60880 (2006/2020) Nuclear power plants — Instrumentation and control systems for safety — Software** 没有 mutation testing 任何等级的提及。其 software verification 要求落在 (a) statement / branch / MC-DC coverage,(b) requirements traceability,(c) static analysis,(d) FMEA/FTA — 共 4 类,无 mutation。
- **ISO 26262-6 (2018) Road vehicles — Functional safety — Product development at the software level**, Table 12 "Methods for unit testing" 与 Table 15 "Methods for software integration testing" 中 mutation 仅作为 ASIL D 下的 "++/+ recommendation"(Annex method),且仅限 syntactic mutation 的 statement coverage 验证用途,**不存在任何 score-based 接收阈值**。Mutation Score 在 ISO 26262 文本中**根本不是接收量**,只是 "test set 在 fault injection 下行为合理" 的间接见证。
- **ASME V&V 10-2006 (Solid Mechanics) / V&V 20-2009 (CFD) / V&V 40-2018 (Medical Devices)**——以 model verification + experimental validation + uncertainty quantification 为骨架,mutation testing **不在任何 V&V 分册的方法清单内**。最接近的概念是 V&V 20 的 "code verification" 与 method of manufactured solutions,但这与本文 SMS 完全不同语义。
- **FDA 21 CFR 820 / IEC 62304 (medical device software)** 同样无 mutation acceptance criteria。

**结果**:§6.5.3 的 auditor pathway 在**任何现行认证文本中找不到接口**。把 NRC / FDA / ISO 26262 评审组列为 SMS 的 stakeholder,本质上是 *aspirational positioning* 而非 *practical pathway*。文中 "需要与行业协会进一步对话才能进入正式认证体系" 是诚实补丁,但 stakeholder 框架已经把读者(尤其 IST 读者中希望"看到 V&V 应用"的群体)误导到一种乐观预期。

**FIX**:
- (a) 把 §6.5.3 的标题从 "审计 / 认证机构 (Auditors / certification bodies)" 改为 "Research-grade evidence for V&V documentation (long-term aspiration)";
- (b) 删除 "接收阈值建议" 子段中 ≥ 0.20 / ≥ 0.30 的具体数字阈值,或明确加 "**no current standard endorses these thresholds**" 警示;
- (c) 在 §1.6.2 认识论声明中已写 "工程价值需另立度量(P2-CN 题材)" — 把这一声明在 §6.5.3 段首再次显式重述,避免读者跨段忘记;
- (d) 在 §6.5.3 末尾加一句 *"Engagement with ASME V&V or IEC SC 45A working groups would be required before SMS can be cited in any qualification dossier; no such engagement has been initiated as of this submission."*——这句话才是诚实的工业语言。

### W2 标题 "scientific computing" 与 §3.1.1 admitted 4 missing chapters 的 overreach [MAJOR]

**WHAT**: 主标题 *"Semantic Mutation Operators in Metamorphic Testing for Scientific Computing"* + abstract "across four classes of scientific computing programs (numeric, probabilistic, surrogate, ML)" 给出的覆盖承诺是 **"scientific computing 的代表性切片"**;§3.1.1 (d) 自我承认 PUT 标量签名 `program(x: float) → float` 是 "实质性约束(非纯工程取舍)";§3.1.1 (b) 自我承认 Numerical Recipes 12 章中 4 章未覆盖:**(1) PDE 高级求解器 (FEM, FV, spectral) — 这就是 CFD 主体;(2) FFT / 谱方法 — 信号处理 + 量子化学;(3) 优化的非凸方向 — 工业优化;(4) 符号计算 — 计算机代数**。

**WHERE**: 标题 + Abstract + §3.1.1 (b) (d) lines 386, 401。

**问题**:
- 这 4 章覆盖的工业代码量,**按 PyPI 下载量与 LOC 估,约占 "scientific computing" 实际工程代码的 60–80%**(CFD 单一领域的 OpenFOAM 即超 1.5 MLOC,本文 12 PUT 总和 ~2 KLOC)。
- §3.1.1 (a) 库栈覆盖只到 numpy / scipy / scikit-learn,**未覆盖 GPU / 分布式 (JAX / CuPy / dask) 与领域库 (BioPython / Astropy / RDKit)**——这一行 limitation 一笔带过,但 JAX/CuPy 是**当前 (2026)** 大型科学计算软件的事实主流。
- 标量 `float → float` 签名把工业 PUT 真正的输入(mesh / state-vector / tensor / time-series field)排除在外。一个 LU 分解 PUT 80 LOC 与一个 LU-based linear solver 在 OpenFOAM 内 (1500 LOC,处理 sparse + parallel + preconditioning) 的语义复杂度差 1-2 个数量级。
- 这不是 "可以承认 limitation 就说服我" 的问题——**title 与 §3.1.1 admitted gap 之间的不对称已经构成 overreach**。

**FIX**:
- (a) 主标题改为更精确的 *"Semantic Mutation Operators for Metamorphic Testing of **Single-Output Scientific Computing Kernels**: An Empirical Audit Across Four Algorithmic Classes"* 或 *"...for **Toy-Scale Scientific Computing Programs (50–400 LOC)**: ..."*;
- (b) 在 abstract 第一句 "12-PUT × 5-MP matrix" 后插入 "(`float → float` signature, 50–400 LOC each, covering 8 of 12 Numerical Recipes chapters; PDE solvers / FFT / optimization / symbolic computation are out of scope and addressed in P3)";
- (c) §1.6 P2 / P4 boundary 表中加一行 "Domain coverage" 显式列出 in-scope vs out-of-scope 子领域,而不是把这一关键 caveat 埋在 §3.1.1。

### W3 REPRODUCIBILITY.md 的 env-var 陷阱使第三方默认复现失败 [MAJOR]

**WHAT**: REPRODUCIBILITY.md §4 Path A 要求 **同时** 设置 `SMS_VERSION=v4` 与 `P2_PRIMARY_VERSION=v3b` 两个 env vars,**两者缺一**就得到非论文数字。文中 §4 末尾的 note: *"如果你忘记 `P2_PRIMARY_VERSION=v3b`, `mean_aligned` will be ~0.213 instead of the paper's 0.275"*。

**WHERE**: REPRODUCIBILITY.md lines 52–58, 85.

**问题**:这是工业 QA 视角的一个**红色信号**:
- (a) 一个独立 reviewer 或工业 QA 团队从 Zenodo 下载复现包,**默认运行命令** (`pytest`, `python scripts/sms_campaign.py`) 不会自动设置这两个 env var(默认值是 v3 + v3 default primary,这是 "pre-registered primary analysis" 的 verdict——δ = 0.323 H2 rejected)。
- (b) 一个粗心的复现实验者会得到 *"H2 rejected"* 的判定 (这恰好与 paper abstract 一致,但与 paper §6 的 v3b/v4 数字不一致),并 **错误地**报告 "复现成功":他看到了 H2 rejected,但他看到的是 v3 而不是 v4 主结果。
- (c) 复现包对 `paper_numbers.json` / `paper_numbers_v3.json` / `paper_numbers_v3b.json` / `paper_numbers_v4.json` 共存,**SSOT 必须依赖人类阅读 README 才能识别**。在工业 V&V 流程中,SSOT 的多版本共存是审计 reject 项 (single point of truth 是 IEC 60880 §7 / ISO 26262-6 §6 显式要求的 documentation principle)。
- (d) DATASET.md §4 把 v1 / v3 / v3b / v4 / Phase-1 cell-level / pilot 全部"为 lineage 保留"——研究角度合理,**但工业 QA 角度即审计噪声 (audit noise)**。一个新加入的 QA 工程师无法在不读全部 commit history 的情况下知道哪个文件是当前 SSOT。

**FIX**:
- (a) 在 `scripts/build_paper_numbers.py` 与 `compute_rq*.py` 顶部加 `if not os.environ.get("SMS_VERSION") or not os.environ.get("P2_PRIMARY_VERSION"): raise SystemExit("Set SMS_VERSION=v4 and P2_PRIMARY_VERSION=v3b before running, or use the wrapper script reproduce_paper.sh")`——使 fail-loud,而非 silent-divergent;
- (b) 提供一个 single-entry wrapper `scripts/reproduce_paper.sh` (POSIX),内部 `set -eu; export SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b; python scripts/build_pools.py && ...`,这才是工业 QA 期待的 "one command reproduces everything";
- (c) DATASET.md §6.2 的 "Earlier versions retained for sensitivity narrative" 列表移到 `data/results/legacy/` 子目录,与当前 SSOT 物理隔离;
- (d) Zenodo bundle 在解压后 root README 第一行就显式说明 *"This artifact reproduces v4 cross-source results. Run `bash scripts/reproduce_paper.sh`. All other data files in `data/results/legacy/` are historical snapshots."*

### W4 §6.5.1 测试工程师 workflow 假设了 LLM API 可用,违反 air-gapped 部署约束 [MAJOR]

**WHAT**: §6.5.1 测试工程师 workflow 步骤 1: "对一个新写的 MR,跑 `scripts/sms_campaign.py` 得到 SMS 值;" — 该脚本在 Path A 下用 cached LLM trials,在 Path B 下需要 Anthropic + bltcy.ai + DeepSeek 三家外部 API 凭证。

**WHERE**: §6.5.1 + REPRODUCIBILITY.md §2 (Configure LLM credentials)。

**问题**:核工程 / 航天 / 国防 / 部分医疗器械的开发环境是 **air-gapped (物理隔离 internet)** 的——这是 IEC 60880, IEC 62443-4-1, NIST SP 800-53 SC-7 (Boundary Protection) 的硬性要求。一个 air-gapped 工程师**根本不能**运行 `cross_source_campaign.py`,只能依赖 cached `data/operator_campaign/raw/` 中的 470 trials。但 cached pool 是针对 12 PUT 已固定的——**当工程师写一个新 MR 用于他自己的 PUT 时,该 cache 不可用**,需要新生成 mutant,需要 LLM API,违反 air-gap。

§6.5.1 的 workflow 在工业 air-gapped 场景下不可执行,而这恰恰是 §6.5.3 提到的 NRC / FDA / ISO 26262 高风险领域的正式部署环境。论文的 stakeholder analysis 把这两类 stakeholder 同时列出,但**§6.5.1 的 workflow 与 §6.5.3 的 deployment 假设是冲突的**。

**FIX**:
- (a) §6.5.1 workflow 步骤 1 改为 "若你的 PUT ∈ {a1...d3},直接读 cached SMS;若你的 PUT 是新的,需要在 internet-connected build server 上一次性生成 mutant pool,再迁移到 air-gapped 测试环境";
- (b) 显式声明 "SMS for novel PUTs requires an internet-connected mutant generation pipeline; this is incompatible with fully air-gapped development environments such as those required by IEC 60880 / NIST SP 800-53 SC-7. We discuss a possible workaround (offline LLM weights + local inference) in §7 future work but have not implemented it."

### W5 §6.5.2 的 PR-CI workflow 把 LLM 成本与延迟 underestimate [MAJOR]

**WHAT**: §6.5.2 给出 GitHub Actions YAML 示例 (lines 1336–1348),sms_campaign.py + sms_pr_gate.py 作为 PR check;声明 "把 MR-质量的反馈环从'季度级 fault 回归'缩短到'小时级 SMS 跑批'"。

**WHERE**: §6.5.2 lines 1333–1348。

**问题**:
- (a) **延迟**: REPRODUCIBILITY.md §4 Path A "≈ 20 minutes" 是 60 cells × 12 mutants × N=20 的 cached run。一个新 MR 触发 PR check 需要重跑相关 cells——**在 GitHub Actions 标准 runner (2 vCPU, 7 GB RAM) 上,b2 MCMC + d1 MLP 的 N=20 重复会显著超过 20 分钟**,可能到 60-90 分钟。这与 "小时级反馈环" 的承诺形式上一致,但远高于 GitHub Actions 默认 6-hour job timeout 的安全余量,且远高于 "developer 等得起的 PR check" 的实际心理阈值 (~5 min, Sadowski et al. 2018 modern code review study)。
- (b) **成本**: 若 PR 触发 cross-source mutant 生成 (Path B),REPRODUCIBILITY.md §4B 估 "USD ~$80, 3-4h"。**每个 PR 都要 $80** 是任何工业 CI 不可接受的;若用 cached path,则只能验证已有 PUT 的 MR,无法验证 PR 中新增 PUT 的 MR。这就把 §6.5.2 的 "MR-PR-CI integration" 限定在 *"existing 12 PUTs only"*,**对实际开发者价值很低**。
- (c) 论文未给出 SMS_VERSION + P2_PRIMARY_VERSION 在 GitHub Actions YAML 中的设置;§6.5.2 例子只用 `SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b`——这把 W3 的双 env-var 陷阱直接暴露到 PR-CI 模板。

**FIX**:
- (a) §6.5.2 末尾加 "Resource estimate" 子段:对一个 single-PUT delta-MR,实际 wallclock + USD cost (cached vs uncached) 必须显式给出;
- (b) Reframe 为 "**Suitable for low-frequency MR audits (quarterly), not for per-PR gating in continuous CI**";
- (c) 实际上,在 §6.5.4 跨 stakeholder 接口处,论文已经把希望寄托在 SSOT 文件——更诚实的 §6.5.2 是 "MR designer commits new MR; **manually** runs `sms_campaign.py` once per quarter; reports SMS in MR documentation",这是工业实际能跑的频率。

### W6 §6.5.3 把 LRCA 5 类根因当成审计可读的诊断,实际上 C5 (mutator 伪影) 把 LLM 引入审计追溯链 [MODERATE]

**WHAT**: §6.5.3 "审计材料可以包含 (b) LRCA 三层诊断结论"。LRCA 的 5 类根因中,**C5 = mutator 伪影**——这是把 LLM 生成 mutant 的失败案例显式列入 root cause taxonomy。

**WHERE**: §6.5.3 line 1356; §2.1.2 LRCA 定义 line 188-189; §4.6.4 LRCA 校准。

**问题**:把 LLM-generated mutant 引入审计追溯链 (audit trail) 在认证文本下有至少 3 个问题:
- (a) **LLM weights 不在 supplier control**: IEC 60880 §10 (Software configuration management) 要求 *"all software tools used for V&V must have configuration items under version control"*。Claude Opus 4.6 / GPT-5.4 / DeepSeek chat 的权重在 vendor (Anthropic / OpenAI / DeepSeek) 控制下,supplier 无法 freeze。审计员一个标准问题:"give me bit-exact reproducibility of the V&V tool chain"——本文做不到 (Path B 是 non-deterministic by construction, REPRODUCIBILITY.md §7 显式承认)。
- (b) **C5 的存在本身就是审计 reject 项**: 一个 root cause taxonomy 中显式包含 "工具自身伪影"——审计员的反应是 "请先消除工具伪影,再来谈这个 metric 的 acceptance"。这是 IEC 60880 / ISO 26262 文化中 *"qualified tool" requirement* (ISO 26262-8 §11) 的标准应用:工具必须 pre-qualified, 不能在使用过程中产生 "tool-induced fault" 然后在结果中标注。
- (c) 论文 §7.1.7 R10 已经承认 "Claude Opus 订阅 API 无 seed 控制"——这与 ISO 26262-8 §11.4.6 *"the tool shall be deterministic, or non-determinism shall be detected and handled"* 直接冲突。

**FIX**:
- (a) §6.5.3 把 "LRCA 三层诊断结论" 从 audit material 列表中移除或显式打上 "research-grade evidence, not auditor-grade evidence" 标注;
- (b) 在 §7.1.7 R10 末尾追加一句 *"This non-determinism makes the LLM-based mutant generation pipeline incompatible with ISO 26262-8 tool qualification (TCL 2/3) requirements; SMS computation as currently implemented can support exploratory R&D but cannot be claimed as a qualified V&V tool."*;
- (c) 把 "qualified-tool path" 列为 §7 future work 的一个明确分支,例如 "switch to deterministic local LLM (Llama-3-70B with frozen weights, inference seed fixed)" — 这是真正能被 IEC 60880 接受的方向。

### W7 §3.1.1 (d) 标量签名 vs §6.5 工业 PUT 之间的可移植性未论证 [MODERATE]

**WHAT**: §3.1.1 (d) 自承 `program(x: float) → float` 是实质性约束;§7.5 R6 表示 "P3 论文将在工业级 PUT 上验证 SMS 的可移植性"。但 §6.5 stakeholder 分析把 SMS 直接交给测试工程师 / MR 设计者使用,假设 metric 在工业级 PUT 上 well-defined。

**WHERE**: §3.1.1 (d) line 401 vs §6.5 全节。

**问题**:从 12 个 50-400 LOC 标量 PUT 上得到的 SMS 经验区间 (aligned mean 0.275, P50 ≥ 0.20),**没有任何理由在 1500 LOC 的 LU-based linear solver 或 50000 LOC 的 CFD timestepper 上保持同样的数值区间**。LLM-生成 mutant 的语义深度与 PUT 复杂度有非平凡关联——这个 scaling behavior 论文未论证、未估计、未给出 future-work commitment 的具体形式。

§6.5.3 的接收阈值 ≥ 0.20 / ≥ 0.30 直接外推到工业 PUT,这是双重 overreach (W2 已经包含 PUT 域覆盖问题,W7 是 metric 数值区间的可移植性问题)。

**FIX**:
- (a) §6.5 节首插入 "**Scope of stakeholder analysis**" 子段,明确所有 stakeholder workflow 假设 PUT 落在 50–400 LOC 标量签名 + numpy/scipy/sklearn 栈;
- (b) §6.5.3 接收阈值后追加 "**These thresholds are calibrated on the 12-PUT 50-400 LOC benchmark and may not transfer to industrial-scale PUTs (>1 KLOC, vector/tensor inputs); a P3 scaling study is required before any cross-PUT-class threshold transfer.**"

### W8 §4.2.5(b) "MVP 不调用 reviewer LLM" 与 §4.2.4 "双 LLM 双盲复核" 的 v4 实测脱节 [MODERATE]

**WHAT**: §4.2.4 设定双 LLM 异源双盲复核协议 (LLM-G + LLM-R),20% 人工抽样;§4.2.5(b) 实际 v4 实现 "MVP 不调用 reviewer LLM,只机械验证 V1-V4"。

**WHERE**: §4.2.4 lines 657-674 vs §4.2.5(b) line 690。

**问题**:这是 protocol vs implementation 的脱节,从工程审计角度看是一个 finding:
- (a) v4 cross-source 数据(整个 §5–§6 主分析的基础)**未经过 §4.2.4 的双盲复核协议**,只过了 V1-V4 机械验证(语法、可执行、非平凡、签名一致性);
- (b) §4.2.5(b) 写 "成本/速度优先,留 P4 完整三 LLM dual-blind 审核"——把 protocol 中承诺的核心质量保证手段推到下一篇论文;
- (c) 这与 §4.2.4(d) "20% 由人工抽样复核" 的 protocol 也脱节——v4 数据上是否做了 20% 人工抽样?REPRODUCIBILITY.md / DATASET.md 未提及人工抽样记录。

工业审计的标准回应:**"protocol 与 implementation 不一致是 nonconformance, 必须 fix 后再讨论 metric"**。

**FIX**:
- (a) §4.2.5(b) 显式承认 "v4 cross-source 数据未应用 §4.2.4 双盲复核"——更新 §4.2.4 表述,把双盲复核明确标注为 "P1/Phase-1 cell-level protocol; not applied in v4 pool-level pipeline; dual-blind reviewer LLM scheduled for P4";
- (b) §7.1 内部威胁中追加一项 R13 "Protocol-implementation gap: v4 cross-source mutant pool was validated by mechanical V1-V4 only; the dual-blind reviewer-LLM step in §4.2.4 was deferred. Manual 20% sampling is also not documented for v4. Mitigation: defer dual-blind to P4.";
- (c) 重新审视 §6.5.1/2/3 stakeholder workflow 中 "SMS 给出可量化指标" 的承诺——这一承诺在 v4 缺少 reviewer-LLM 验证的前提下,质量保证基础比 abstract 暗示的更弱。

### W9 §3.1.1 (a) 库栈版本固定 vs scientific computing 实际 release cycle 的张力 [MINOR]

**WHAT**: §3.1.1 (a) 给出 numpy 2.4.4 + scipy 1.17.1 + scikit-learn 1.8.0 (2026-04 数据);REPRODUCIBILITY.md §1 要求 Python 3.12.x 最低 3.11+。

**WHERE**: §3.1.1 (a) lines 370–376; REPRODUCIBILITY.md §1。

**问题**: numpy 1.x → 2.x 的 ABI 不兼容 (2024-06 release) 已经 broke 大量科学计算代码;numpy 2.4.x (本文使用) 是 2025-2026 的版本,在 2027 投稿期 / 2028 出版期 numpy 可能已到 2.6 或 3.0。一个工业 QA 团队在 2028-2029 想复现本文,需要 pin numpy 2.4.4——但 PyPI 上 old wheels 在新 platform (Apple Silicon M5 / linux-aarch64-v9 / Intel AVX-512) 可能不再可用。

**FIX**:
- (a) 在 Zenodo bundle 中包含 `requirements-frozen.txt` 完整 wheel hash (不仅版本号),并测试在 fresh venv 上 wheel-hash-locked install 仍成功;
- (b) §3.1.1 (a) 末尾加 "Python 3.12 + numpy 2.4 stack will likely require a pinned `requirements-frozen.txt` and may need a dedicated Docker image for reproduction beyond 2028;" 配合 Zenodo bundle 提供 Dockerfile。

### W10 论文未声明与 ASME V&V 20 / V&V 40 的具体关系 [MINOR]

**WHAT**: 论文整体定位为 "metamorphic testing for scientific computing",但**全文未提到 ASME V&V** (V&V 10/20/40 系列是 scientific computing software V&V 的事实工业标准之一,2006-2018 series)。

**WHERE**: §1.3 相关工作 + §6.5.3 + §8 References。

**问题**: ASME V&V 与本文 metamorphic testing 不是替代关系,而是**互补关系**——V&V 20 的 "code verification" 用 method of manufactured solutions (MMS) 验证数值方法的收敛阶,与本文 mut_G (Convergence-breaking) + MP_3 (收敛) 概念高度同构。论文若与 V&V 20 显式 align,可以增强 "scientific computing" 的领域 credibility;现状是论文完全在 SE / mutation testing 文献圈内对话,**没有引用 scientific computing 自己的 V&V 文化**。

**FIX**:
- (a) §1.3 相关工作中加一条 "ASME V&V 20-2009 / V&V 40-2018 family — scientific computing V&V standard with code verification (MMS) and validation (uncertainty quantification) layers; SMS could complement V&V 20 §3 code verification by providing semantic-level mutation evidence orthogonal to MMS convergence rate evidence";
- (b) §8 References 加 ASME V&V 20-2009 与 V&V 40-2018 引用;
- (c) §6.5 stakeholder analysis 中 "V&V engineers" 可能比 "auditors" 是更现实的 deployment target——他们是 ASME V&V 委员会的实际用户,对 mutation-style metric 比 IEC/ISO certification body 更开放。

---

## 5. §6.5 Stakeholder section 分述

### 5.1 §6.5.1 测试工程师 — partially defensible, with caveats

**Defensible 部分**:
- "代码覆盖工具报告 90%+ 但 MR 集合是否够" 这个 pain point 在工业实践中**真实存在**——CFD code review 中我反复见到 100% line coverage + 0 fault detection 的代码,而 MR-driven testing 是已知有效手段。
- "对每个 (PUT, MP) 单元格给出 0–1 标量 SMS" 在 single-PUT 维护期场景下确实可用。

**Indefensible 部分**:
- W4: workflow 假设 LLM API 可用,与高风险领域 air-gap 部署冲突;
- W5: 5–90 min 反馈环 + 多版本 SSOT 让 PR-CI 集成场景几乎不可行;
- 论文未给出 "每月跑 1 次 SMS audit" vs "每 PR 跑" 的经济模型分析。

**Verdict**: **defensible if reframed as "manual quarterly audit"**, indefensible as "automated CI gate".

### 5.2 §6.5.2 MR 设计者 — mostly defensible

**Defensible 部分**:
- MR 设计者的 pain point ("MR 是否有用只能等真实 fault 验证") 真实;
- §6.5.2 提出的 GitHub Actions YAML 模板**作为 MR designer in academic setting** 是合理的——MR designer 通常在大学 / national lab,不受 air-gap 约束。

**Indefensible 部分**:
- W5 (b): API cost 在 R&D setting 下可接受 (单次 audit ~$80) 但 "PR check" 频率不可接受;
- 论文未明确区分 *MR designer 在 development phase* (R&D, 可用 internet, 频率低) vs *test engineer 在 maintenance phase* (production, air-gap, 频率高) — §6.5.1 vs §6.5.2 这个区分可以更显式。

**Verdict**: **defensible for academic / national-lab MR designers**;industrial MR 设计者(在 vendor 内部)的 deployment 仍需 air-gap-compatible 方案。

### 5.3 §6.5.3 审计 / 认证机构 — research speculation, not defensible

这是本评审最严重的 finding。详细论证见 W1。补充三点:

(a) **本文 cite 的 "IEC 60880 / ISO 26262 / NRC / FDA" 在文本中没有 mutation testing acceptance criteria 的客观事实**。论文未引用 IEC 60880 / ISO 26262 文本本身作为 reference (§8 References 完全无 IEC / ISO / ASME 标准引用)——这是论文知识基础的缺口。
   - IEC 60880:2006/2020 全文(125 页)**未出现 "mutation" 一词**;
   - ISO 26262-6:2018 Table 12 中 mutation testing 仅作为 ASIL D 下 "++" recommended method 出现一次,且在 Annex E.4 中描述其用途为 "to evaluate the quality of test cases by injecting artificial faults",**绝不出现 score-based acceptance threshold**;
   - ASME V&V 10/20/40 series 全无 mutation testing 引用;
   - 这意味着 §6.5.3 的 "接收阈值建议 ≥ 0.20 / ≥ 0.30" 不是对现行标准的 "informed proposal", 是 *proposing a number into a vacuum*。

(b) **"SMS ≥ 0.30" 这种数字阈值在认证文化中是 *backwards engineering***:认证机构不接受 "研究者从他的 12-PUT benchmark 上选了一个 ≥ P70 数字" 这样的 threshold rationale。可接受的阈值需要:(i) 对应一个 process capability (Cp/Cpk),(ii) 对应一个 fault detection probability per unit code-mile,(iii) 经过 multi-vendor / multi-year inter-laboratory study 校准——这是 ASME PTC 系列 + IEC SC 45A WG3 的工作模式,本文均未涉及。

(c) **§6.5.3 的诚实补丁 "需要与行业协会进一步对话才能进入正式认证体系" 在工业语言中应该是 "no engagement yet, no roadmap defined"**——目前 §6.5.3 的措辞让 IST 读者(尤其是没有 V&V 委员会经验的)以为 "对话正在进行" 或 "对话即将进行",这是 误读 (misreading) 风险。

**Verdict**: §6.5.3 的 auditor claim 是 **research speculation**, 不是对现行 IEC/ISO/ASME 文本的 informed bridge。**must rewrite** (W1 已给出具体 fix)。

### 5.4 §6.5.4 跨 stakeholder 共同接口 — defensible in principle, undermined by W3

"三类 stakeholder 通过同一份 `paper_numbers_v4.json` SSOT 得到一致数字" 在原则上是好的工程设计;实际上 W3 (env-var 陷阱 + 多版本 SSOT 共存) 直接破坏了这一保证。**defensible 后置在 W3 修复完成上**。

---

## 6. PUT scope vs 标题 "scientific computing" — title overreach

参见 W2 详细论证。简化结论:

| 维度 | 标题 / abstract 的承诺 | §3.1.1 admitted scope | gap |
|---|---|---|---|
| 学科覆盖 | "scientific computing" | 8 / 12 Numerical Recipes 章节 | 33% chapters not covered |
| 关键缺失 | (默认覆盖) | PDE solvers / FFT / optimization / symbolic | **CFD + 信号处理 + 工业优化 + 计算机代数 — i.e., the bulk of industrial scientific computing** |
| PUT 规模 | "scientific computing programs" | 50-400 LOC | 工业 PUT 1-10 KLOC |
| 输入复杂度 | 隐含 ("programs") | `float → float` 标量 | 工业 mesh / tensor / time-series |
| 库栈 | (默认覆盖) | numpy/scipy/sklearn | 不覆盖 JAX / CuPy / dask |

**Title 承诺与 §3.1.1 admitted scope 的不对称是 substantive overreach**, 不是 "可以承认 limitation 就修复" 的问题。

§3.1.1 自我承认这 4 章 "对应的 PUT 在工业级科学计算软件中很重要 (CFD / 量子化学 / 信号处理)" — **一旦承认了 "工业级很重要", title 中的 "scientific computing" 就不能保持现状**, 必须降级到 "scientific computing kernels" 或 "toy-scale scientific computing programs"。

**否则 §6.5.3 的 auditor pathway 论证基础(NRC 关心的就是 CFD 反应堆热工水力)直接 collapse**——你既不覆盖 CFD,又主张 NRC 评审组应该用你的 metric。这是 W1 + W2 + W7 三个 weakness 的合流。

**Verdict**: title overreach is **structural, not cosmetic**; W2 fix 是必要条件。

---

## 7. Reproducibility for an industrial QA team — walk-through

假设我是一个 CFD 公司的 QA 工程师,任务是 "评估 SMS 是否能用于公司内部 CFD solver 的 V&V 增强"。我从 Zenodo 下载 P2 复现包 (`v1.0.0-zenodo`):

### Step 0: clone + setup
```bash
git clone <repo> mt-completeness && cd mt-completeness
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt
```
**预期问题**:numpy 2.4.4 在 2028 平台上 wheel 可能不再可用 (W9);若 fresh install 失败,QA 工程师需要 build from source — 在 air-gapped 环境下 (无 internet) 这意味着需要 manual mirror PyPI 的所有 transitive deps。**failure point 1**: 无 Docker/Singularity bundle 时,跨 2-3 年的 reproducibility 不保证。

### Step 1: smoke test
```bash
PYTHONPATH=src .venv/bin/pytest -q
# Expected: 116 passed, 0 failed, ~30s
```
**通过率假设**:可能。但 116 unit tests 测的是 PUT/MR/AVP/LRCA 组件单元测试,**不是论文数字的复现验证**。一个粗心 QA 工程师可能在这一步停下来报告 "复现成功"——这不是论文数字层面的成功。

### Step 2: 复现论文数字
```bash
# WITHOUT reading REPRODUCIBILITY.md §4 carefully:
PYTHONPATH=src .venv/bin/python scripts/build_paper_numbers.py
```
**failure point 2 (W3)**:不设 SMS_VERSION + P2_PRIMARY_VERSION,此命令产生 v3 default primary 的数字 (mean_aligned ~0.213),与论文 §6 的 v4 数字 (mean_aligned 0.275) 不一致。QA 工程师可能 (a) 报告 "数字不一致, 复现失败", (b) 不报告而 silently 接受错误数字, 或 (c) 重新读 README,设置 env vars。无论哪种结果,**friction 已经造成,信任已经损耗**。

正确路径:
```bash
export SMS_VERSION=v4
export P2_PRIMARY_VERSION=v3b
PYTHONPATH=src .venv/bin/python scripts/build_pools.py
PYTHONPATH=src .venv/bin/python scripts/sms_campaign.py --track 2 --workers 6 --repeats 20
PYTHONPATH=src .venv/bin/python scripts/run_lrca.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq2.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq2_logit.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3_friedman.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq4.py
PYTHONPATH=src .venv/bin/python scripts/build_paper_numbers.py
PYTHONPATH=src .venv/bin/python scripts/render_figures.py
```
9 个独立 script 调用 + 2 个 env var,**这是研究 reproducibility 的最低限**, 绝不是工业 QA "one-command reproduce" 的标准。

### Step 3: 把 SMS 用到我们公司的 CFD PUT
**failure point 3 (W4 + W7)**:
- (a) 我们的 CFD solver 输入是 mesh + state vector + boundary conditions,不是 `float → float`——SMS 计算管线 (`scripts/sms_campaign.py`) 的 AVP 调用不能直接处理;需要重写 PUT adapter,这是论文未覆盖的 engineering;
- (b) 即使写好 adapter,在 air-gapped 环境下 mutant pool 必须从 internet-connected build server 生成,跨 air-gap 边界传输——这违反 IEC 62443-4-1 secure development lifecycle 的 supply chain integrity 要求;
- (c) §6.5.3 的接收阈值 ≥ 0.20 / ≥ 0.30 在我们 1500 LOC 的 LU-based linear solver 上是否仍然有效?论文未给出 calibration evidence。

**失败结论**: 一个 CFD QA 工程师在 P2 当前状态下**无法**把 SMS deploy 到公司内部 V&V pipeline。它停留在 "research-grade evidence", 不是 "qualifiable tool"。

### 修复后的预期路径(假设 W3, W4, W7 都修复)

```bash
# Single-command reproduction
bash scripts/reproduce_paper.sh
# Outputs paper_numbers_v4.json + figs/ + audit_log.txt
```
+ Docker image `meng-li/p2-sms:v1.0.0-zenodo` 在 Docker Hub / Zenodo 镜像
+ §6.5.1/3 显式声明 air-gap incompatibility
+ §7 future work 给出 "deterministic local LLM (Llama-3-70B frozen) for tool qualification" 路径

只有这样, **能离开实验室一英寸**。

---

## 8. Decision recommendation

**Major Revision**.

**理由**:论文的 empirical core (60-cell SMS audit, 三阶段 ablation, H2 honest negative result) 是 publishable 的;§6.5 stakeholder analysis 与 title 中的 "scientific computing" 承诺存在 substantive overreach,需要 author 在 revision 中诚实压缩 deployability claim。具体:

**Must fix (rejection-level if not fixed)**:
1. W1: §6.5.3 auditor pathway 的 normative claim;
2. W2: 标题 / abstract 的 scientific computing 域承诺;
3. W3: REPRODUCIBILITY.md env-var 陷阱 + 多版本 SSOT。

**Should fix (revision-level)**:
4. W4: §6.5.1 air-gap incompatibility 显式声明;
5. W5: §6.5.2 PR-CI cost / latency reframe;
6. W6: LRCA C5 在审计追溯链中的位置。

**Nice to fix (revision-level + reduces reviewer skepticism)**:
7. W7: §6.5 节首 scope 子段;
8. W8: §4.2.4 与 §4.2.5(b) protocol-implementation gap;
9. W9: requirements-frozen + Docker bundle;
10. W10: ASME V&V family 引用与定位。

如果 revision 完成 must-fix 1-3,我支持 **accept**;如果只完成部分,则 **reject and resubmit**。

---

## 9. Score sheet (1–10, 7 dimensions, cross-disciplinary practitioner perspective)

| 维度 | 分数 | 评注 |
|---|---|---|
| **1. Originality / 度量原创性** | **7** | SMS = killed/(mut−equiv) 结构经典,创新在 5 类 domain-semantic operator + LRCA + 三阶段 ablation;§3.2.6 工具级算子对照是真正的 contribution;§9 退化定理形式好。但 "domain-semantic operator" 概念在 DeepCrime / DLMutation 已有先例,本文是 cross-domain 整合而非 first-of-kind。 |
| **2. Technical soundness / 实验严谨度** | **7** | Pre-registration + honest negative result + selection-on-the-response 警告 (§3.5.1) 都是高质量实验姿态。扣分项:§4.2.5(b) protocol-implementation gap (W8); mixed-effects Singular fallback 让 RQ3 的统计基础变弱 (§7.2.2 R6 已承认); n=12 PUT 在 RQ4 严重欠 power (§6.4 已承认)。 |
| **3. Significance to scientific computing community** | **5** | 标题承诺 vs §3.1.1 admitted scope 的 gap (W2) 严重影响 significance。如果 retitle 为 "for single-output kernels", significance 反而更高(精确)。CFD / 量子化学 / 工业优化领域对 "12 PUT 上的 metric" 的实际兴趣有限。 |
| **4. Reproducibility / 工业 QA 视角** | **5** | 116 unit tests + Zenodo bundle + Path A cached 是好的姿态,但 (a) 双 env-var 陷阱 (W3) + (b) 多版本 SSOT 共存 + (c) 9-step manual command sequence 让 "1-command reproduce" 不成立。compared to ASME V&V 工业 baseline 远不够。修复 W3 后可到 7-8。 |
| **5. Clarity / 表述清晰度** | **7** | 中文表述 + 大量术语英文标注 + 完整符号系统 (§2) + flow diagram (§4.1) 都是好的;扣分:§6.5 stakeholder section 的 deployability tone 与 §1.6.2 / §7.5 limitations 不一致 (overreach in §6.5,under-promise in §7); v3/v3b/v4 三层 ablation 对非 SE 读者认知负担重,需要更简洁的 "TL;DR finding" 表格。 |
| **6. Practical deployability / 这个 metric 能离开实验室吗?** | **3** | 这是我作为 cross-disciplinary practitioner 给出的最低分。理由 (W1+W3+W4+W5+W6+W7 合流):无 air-gap path,无 qualified-tool path,无 single-command reproduction,无 normative basis in IEC/ISO/ASME,无工业 PUT scaling evidence,无 multi-vendor calibration。当前状态下 SMS = research-grade evidence only。修复 W1+W3+W4 后可到 5-6;真正能 deploy 需要后续 P2-CN/P5/P3。 |
| **7. Overall recommendation strength** | **5** | Major revision; empirical core publishable, deployability claim 必须诚实压缩。修复 must-fix 1-3 后可到 7-8。 |

---

## 10. Closing note (reviewer's voice)

我作为一个 ASME V&V / IEC 60880 委员会成员,**支持** SMS 这一研究方向——metamorphic testing 在 scientific computing software V&V 中的位置确实 underexplored,本文提供了一个有用的 empirical baseline。但我**不支持**作者在 §6.5.3 把 SMS 推向 NRC / FDA / ISO 26262 评审组的姿态,因为:

(a) 这一推动**没有任何 normative basis**;
(b) 这一推动会让读者(尤其 IST 读者中希望 "看到 SE 研究 in industrial V&V" 的群体)对 SE 研究界的工业理解产生误判;
(c) 这一推动对 SMS 这个 metric 自身**也是有害的**——把它过度承诺到 certification 场景,反而让 V&V engineers (我们自己) 默认 "又一篇 SE 论文 oversell 了 metric, 不值得读" 而忽略其真正可用的 §3.2.6 工具级对照与 §9 退化定理。

诚实的标题 + 诚实的 stakeholder 范围 (academic MR designers + national-lab V&V engineers, 不是 certification bodies) + 诚实的 reproducibility entry point, 这篇论文会成为 IST 上一篇有 lasting impact 的工程文献。

希望作者在 revision 中接受 must-fix 1-3。

---

**End of Reviewer 3 report.**
