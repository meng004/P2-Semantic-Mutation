# P2 Reviewer-Consensus Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **All paper text MUST be in Chinese; technical identifiers stay English.**

**Goal:** Address the 9 revision items where ≥3/5 reviewers (out of EIC + R1 + R2 + R3 + Devil's Advocate) independently raised the same concern in the 2026-05-01 review round; defer single-reviewer items to a later revision.

**Architecture:** Each task is one revision item, scoped to a small set of edits in `论文初稿P2.md` plus (when applicable) one supporting `scripts/` artifact. Edits are surgical: target exact passages with `old_string`/`new_string` pairs to avoid touching the surrounding revision-stable sections. Tasks 1–6 are P0 (block resubmission); Tasks 7–9 are P1 (normal revision expectation). Each task ends with a verification step (grep / regenerate paper_numbers) and an isolated commit. No new statistical methods are introduced beyond a single permutation script in Task 4.

**Tech Stack:** Markdown (paper text), Python 3.12 with numpy + scipy (permutation test in Task 4), git with HEREDOC commit messages, grep / wc for verification.

**Critical contracts:**
- Paper §3.5.1, §5.7.2, §5.7.3, §6.1, §8.3 numbers in `data/results/paper_numbers_v4.json` MUST stay consistent. After tasks that touch v3/v3b/v4 narratives, run grep checks but do NOT rerun `scripts/build_paper_numbers.py` (that script's default is `SMS_VERSION=v3`; running it without `SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b` produces stale numbers — this is a known reproducibility trap, see `docs/STATE.md §5.1`).
- Reviewer comment ID conventions: P0-N / P1-N from `docs/review_2026-05-01/editorial_decision.md` §4.
- All edits use `Edit` tool with `replace_all: false` and a unique `old_string`. If `old_string` is non-unique, expand surrounding context until it is.

**File map:**
- Modify: `论文初稿P2.md` (Title, Abstract, §1.5, §3.5.1, §4.2.5, §4.2.5.1, §5.7.2, §5.8.2, §6.1, §6.3, §7.1, §8.3, §9.2, §9.3, §9.4)
- Modify: `docs/STATE.md` (reviewer progress 24/28 → 33/28 after this plan completes)
- Create: `scripts/permutation_c_class_inflation.py` (Task 4 only)
- Create: `data/results/c_class_permutation_v4.json` (Task 4 output)

---

## Task 1: P0-1 — Title + Abstract scope dual-layer narrowing

**Reviewer consensus:** 5/5 (R0 W1, R1 W3, R2 W5, R3 W2, DA-CRITICAL-1)
**Concern:** Title says "When LLM Source Diversity Doesn't Help: ... in Metamorphic Testing for Scientific Computing" but (a) source-diversity test was conducted only under fixed prompt template (R-16 caveat); (b) "scientific computing" claim oversells — all 12 PUTs are single-input single-output Python functions <2 KB.

**Files:**
- Modify: `论文初稿P2.md:5` (English Title), `:9-10` (Alternative titles), `:14` (Abstract — Method + Results + Conclusion)

- [ ] **Step 1: Verify the current title/abstract baseline before editing**

```bash
grep -n "When LLM Source Diversity Doesn't Help" 论文初稿P2.md
grep -n "scientific computing" 论文初稿P2.md | head -10
```
Expected: Line 5 main title, line 9 Alt-1, abstract refs at lines 14, 18 keywords.

- [ ] **Step 2: Replace the main title**

In `论文初稿P2.md`, replace the title line. Use the Edit tool with:

`old_string`:
```
**When LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Scientific Computing**
```
`new_string`:
```
**When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels**
```

- [ ] **Step 3: Update Alt-1 and Alt-2 to mirror the same dual narrowing**

Replace the two alternative titles. Use Edit:

`old_string`:
```
- **Alt-1**: *Semantic Mutation Score (SMS): A Metamorphic Testing Adequacy Metric for Scientific Computing — with a Three-Stage Ablation Across MR Alignment and LLM Source Diversity*
- **Alt-2**: *Domain-Semantic Mutation Operators for Metamorphic Testing of Scientific Computing Software: A Cross-Source Empirical Audit*
```
`new_string`:
```
- **Alt-1**: *Semantic Mutation Score (SMS): A Metamorphic Testing Adequacy Metric for Single-Output Scientific Computing Kernels — with a Three-Stage Ablation Across MR Alignment and Same-Prompt LLM Source Diversity*
- **Alt-2**: *Domain-Semantic Mutation Operators for Metamorphic Testing of Single-Output Scientific Computing Kernels: A Same-Prompt Cross-Source Empirical Audit*
```

- [ ] **Step 4: Insert scope-narrowing clauses into the Abstract**

The Abstract is line 14 (one long line). Replace the **Method** sentence and **Conclusion** sentence to add scope clauses. Use Edit:

`old_string`:
```
**Method.** We instantiate a 12-PUT × 5-MP matrix (60 cells, average 24.3 LLM-generated mutants per cell, N=20 AVP repetitions) across four classes of scientific computing programs (numeric, probabilistic, surrogate, ML).
```
`new_string`:
```
**Method.** We instantiate a 12-PUT × 5-MP matrix (60 cells, average 24.3 LLM-generated mutants per cell, N=20 AVP repetitions) across four classes of single-output scientific computing kernels (each PUT a Python function with `float → float` signature, source code under 2 KB; the four classes are numeric, probabilistic, surrogate, ML).
```

`old_string`:
```
**Conclusion.** SMS provides a domain-aware adequacy metric that strictly degenerates to classical syntactic MS in the syntactic limit; H2 is not met under any of the three ablation stages, indicating that the LLM-mutant + current-MR-design configuration in scientific computing software does not reach the Romano large-effect threshold without further redesign.
```
`new_string`:
```
**Conclusion.** SMS provides a domain-aware adequacy metric that strictly degenerates to classical syntactic MS in the syntactic limit; under the studied scope (single-output kernels, identical prompt template across the three LLM sources), H2 is not met under any of the three ablation stages, indicating that the LLM-mutant + current-MR-design configuration does not reach the Romano large-effect threshold without further redesign. Whether differential per-LLM prompts or vector-output industrial kernels would change this verdict is left to future work (§4.2.5.1, §7.1.7).
```

- [ ] **Step 5: Verify the rewrite — search for residual broad-scope phrases**

```bash
grep -n "for Scientific Computing\b" 论文初稿P2.md
grep -nE "doesn't help|Doesn't Help" 论文初稿P2.md | head -5
```
Expected: title lines now read "Single-Output Scientific Computing Kernels" / "Same-Prompt LLM Source Diversity"; no residual broad-scope claim survives in title or abstract.

- [ ] **Step 6: Commit**

```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P0-1): narrow title + abstract scope (5/5 reviewer consensus)

Title and abstract over-claimed two dimensions (R0 W1, R1 W3, R2 W5,
R3 W2, DA-CRITICAL-1):

(1) "LLM Source Diversity Doesn't Help" — actually tested only
    under fixed prompt template (Δδ_LLM = -0.007 conditional on
    identical prompt across Claude / GPT-5.4 / DeepSeek)
(2) "for Scientific Computing" — 12 PUTs are single-output Python
    functions under 2 KB, missing PDE solvers / FFT / optimization /
    symbolic computation per §3.1.1

Title now reads: "When Same-Prompt LLM Source Diversity Doesn't Help:
An Ablation of Semantic Mutation Operators in Metamorphic Testing for
Single-Output Scientific Computing Kernels"

Abstract Method clause adds the float->float signature constraint;
Conclusion clause adds the identical-prompt qualifier and an explicit
deferral to differential-prompt and vector-output future work.
EOF
)"
```

---

## Task 2: P0-2 — Delete the "17.6:1 contribution ratio" composite number

**Reviewer consensus:** 3/5 (R0 W1, R1 W3, DA-CRITICAL-4)
**Concern:** §4.2.5 last paragraph reports "+0.123 vs −0.007 ≈ 17.6:1" but §5.7.2 explicitly says contrasts must be reported separately to avoid factor-isolation false implication. Internal contradiction.

**Files:**
- Modify: `论文初稿P2.md:698` (§4.2.5 last paragraph), `:1161` (§6.1 paragraph mentioning the ratio)

- [ ] **Step 1: Locate both occurrences**

```bash
grep -n "17.6" 论文初稿P2.md
```
Expected: at least two lines (§4.2.5 and §6.1).

- [ ] **Step 2: Rewrite §4.2.5 last paragraph to remove the ratio and replace with the conditional formulation**

`old_string`:
```
**三阶段 ablation 的论证逻辑**:δ 在 v3 → v3b 跃升 +0.123(MR-MP 对齐设计),在 v3b → v4 微变 −0.007(LLM 源多样性);**两个工程因子的贡献比 ≈ 17.6:1,MR-MP 对齐设计是 H2 上限的主导因子**。这一发现重定向 P4 论文优先级:不是"扩展 mutant 池源"而是"精化 MR 设计与 mut_j × MP_k 对齐覆盖"。详细解读见 §5.7.2 + §6.1。
```
`new_string`:
```
**三阶段 ablation 的论证逻辑**:两个 contrast **分别报告**(避免合成 ratio 暗示因子 isolation,详见 §5.7.2 表):v3 → v3b 跃升 +0.123 是单类、事后选择的 c-class primary MP shift,反映"primary MP 选择规则的 sensitivity"而非通用"MR-MP 对齐设计贡献";v3b → v4 微变 −0.007 是 conditional on v3b 选择 + identical prompt template 下三家 LLM 的近一致响应。**v3b → v4 contrast 不是中性条件下的 LLM 源多样性测试**(§4.2.5.1 R-16 protocol 列出强意义版本)。这一观察提示 P4 优先级:"differential prompt frame per LLM"(§7.1.7 R10)与"pre-registered primary MP 选择规则"两条平行路线;不构成对"MR 设计 vs LLM 多样性"两因子贡献的定量分解。详细解读见 §5.7.2 + §6.1。
```

- [ ] **Step 3: Rewrite §6.1 paragraph to remove the ratio narrative**

Locate the §6.1 line containing "17.6:1" or "对照清晰地隔离了两个工程因子" and rewrite:

`old_string`:
```
这一对照清晰地隔离了两个工程因子:**MR-MP 对齐设计是效应规模的主导因子(贡献 +0.123),mutant 池的源多样性几乎不贡献(微减 0.007)**。
```
`new_string`:
```
这一对照**分别**报告两个 contrast:Δδ_{v3→v3b} = +0.123 来自单类、事后的 c-class primary MP 选择(§3.5.1 caveat,Bonferroni-bounded effective α 见 §3.5.1 + 本文 P0-4 修订);Δδ_{v3b→v4} = −0.007 在 conditional on v3b 选择 + identical prompt 下,反映三家 LLM 在固定 prompt 下的近一致响应。**两个 contrast 各自携带各自的 selection / conditioning caveat,不能合成为单一因子分解 ratio**——见 §5.7.2 既有的 contrast 表。
```

- [ ] **Step 4: Verify no "17.6" residual**

```bash
grep -n "17.6\|17:1\|因子 isolation\|因子贡献" 论文初稿P2.md | head
```
Expected: only the new "不能合成为单一因子分解 ratio" sentence remains; no `17.6:1` literal anywhere.

- [ ] **Step 5: Commit**

```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P0-2): remove 17.6:1 composite ratio (R0 W1 / R1 W3 / DA-CRITICAL-4)

§4.2.5 last paragraph and §6.1 mid paragraph both reported "+0.123
vs -0.007 = 17.6:1 contribution ratio for MR design vs LLM source
diversity". §5.7.2 explicitly forbids this kind of synthesis (each
contrast carries its own caveat: v3->v3b is post-hoc c-class shift;
v3b->v4 is conditional on v3b selection AND identical prompt).

Both passages now report the two contrasts separately with their
respective caveats and explicit "cannot be combined into a single
factor-decomposition ratio" statement.
EOF
)"
```

---

## Task 3: P0-3 — §5.8.2 H4 "严格达成" downgrade + Abstract sign test 4/4 → 3/4

**Reviewer consensus:** 3/5 (R0 W2, R1 W8, DA-CRITICAL-2)
**Concern:** Abstract reports "Friedman ... H4 cross-class consistency (sign test 4/4 in v3b only)" implying H4 is met. But v3b is post-hoc, so the 4/4 result inherits selection-on-response. v3 pre-registered sign test is 3/4. Abstract / §5.8.2 / §6.3 must report v3 primary number as the headline H4 result; v3b 4/4 must be downgraded to exploratory sensitivity.

**Files:**
- Modify: `论文初稿P2.md:14` (Abstract Results sentence), `~:1075` (§5.8.2), `~:1183` (§6.3)

- [ ] **Step 1: Locate the three occurrences of "4/4" or "sign test 4"**

```bash
grep -nE "sign test 4|4/4|严格达成|Sign test" 论文初稿P2.md | head -15
```
Expected: ~3 hits in Abstract / §5.8.2 / §6.3 / §3.5.1.

- [ ] **Step 2: Rewrite the Abstract Results sentence**

`old_string`:
```
Friedman test confirms a significant MP main effect (χ² = 15.30, p = 0.0041), distinct from H4 cross-class consistency (sign test 4/4 in v3b only).
```
`new_string`:
```
Friedman test confirms a significant MP main effect (χ² = 15.30, p = 0.0041); this is reported as a fallback non-parametric sensitivity, distinct from H4 cross-class consistency. Under pre-registered v3, the H4 sign test is 3/4 (partial); under exploratory v3b (post-hoc, conditional on c-class primary MP shift, §3.5.1) the same sign test is 4/4. We report v3 as the H4 primary result.
```

- [ ] **Step 3: Rewrite §5.8.2 sign test paragraph**

Locate the §5.8.2 paragraph containing "sign test" and rewrite:

`old_string`:
```
| **v3b 数据驱动 primary MP 调整后,sign test 4/4 严格达成**(v3 为 3/4);v4 跨源池保持 4/4
```
`new_string`:
```
| **v3 (pre-registered): sign test 3/4(部分达成,partial);v3b (exploratory, post-hoc): 4/4(conditional on c-class primary MP shift,§3.5.1)**;v4 跨源池在 v3b 条件下保持 4/4。**H4 主结论以 v3 pre-registered 为准:partial,not strict**;v3b 4/4 与 v4 4/4 是 sensitivity report,不替代 v3 verdict
```

(If exact `old_string` match fails because of Markdown table formatting differences, search the surrounding section and use a longer unique anchor including the preceding line.)

- [ ] **Step 4: Rewrite §6.3 verdict synthesis paragraph**

Locate the §6.3 paragraph containing "4/4 类 sign test 通过(v3b)" and rewrite:

`old_string`:
```
我们的结论:跨类一致性的"一致"已在(a) 4/4 类均值方向均为正、(b) **4/4 类 sign test 通过(v3b)**、(c) 60-cell Friedman p = 0.0041 三点上联合呈现;mixed-effects 不可用是 N = 60 / 12 PUT 的样本约束(§7.2.2 R6),而非证据缺失。
```
`new_string`:
```
我们的结论:跨类一致性 verdict **以 v3 pre-registered 为准 = partial(sign test 3/4)**。supporting sensitivity:(a) 4/4 类均值方向均为正(v3/v3b/v4);(b) v3b sign test 4/4 与 v4 sign test 4/4(均为 exploratory,conditional on c-class primary MP shift,§3.5.1);(c) 60-cell Friedman p = 0.0041(non-parametric fallback,**不构成 H4 verdict 的一部分**,见 §5.8.4)。Mixed-effects 不可用是 N = 60 / 12 PUT 的样本约束(§7.2.2 R6),而非证据缺失。
```

- [ ] **Step 5: Verify the v3 primary number takes precedence**

```bash
grep -nE "sign test [34]/4|严格达成|partial.*v3|v3.*partial" 论文初稿P2.md | head
```
Expected: every "4/4" mention is qualified as "exploratory (v3b)" or "supporting"; "3/4" appears as primary in Abstract / §5.8.2 / §6.3.

- [ ] **Step 6: Commit**

```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P0-3): downgrade v3b sign test 4/4 to exploratory (R0 W2 / R1 W8 / DA-CRITICAL-2)

Abstract / §5.8.2 / §6.3 previously promoted v3b sign test 4/4 to the
H4 verdict slot. v3b is post-hoc per §3.5.1 (c-class primary MP shift
chosen after observing data), so 4/4 inherits selection-on-response
contamination. v3 pre-registered sign test is 3/4 (partial).

H4 primary verdict now reads: "partial (3/4 under pre-registered v3)";
v3b 4/4 and v4 4/4 are listed as exploratory sensitivity that does not
replace the v3 verdict. Friedman is explicitly removed from the H4
joint-evidence list (it tests MP main effect, not cross-class
consistency, per §5.8.4).
EOF
)"
```

---

## Task 4: P0-4 — Quantify c-class MP shift max-selection inflation

**Reviewer consensus:** 3/5 (R0 W2, R1 W5, DA-CRITICAL-3)
**Concern:** §3.5.1 c-class primary MP shift = "select the MP with max mean SMS over MP1..MP5 for c1/c2/c3". With 5 candidates, naive multiple-comparison correction is α × 5. The paper acknowledges the bias (§3.5.1 caveat #2) but provides no quantitative bound. Reviewers want either a permutation-based null distribution OR a Bonferroni-style upper bound.

**Files:**
- Create: `scripts/permutation_c_class_inflation.py`
- Create: `data/results/c_class_permutation_v4.json` (script output)
- Modify: `论文初稿P2.md` §3.5.1 (caveat #2 paragraph), §5.7.2, `data/results/.gitignore` (allowlist new file)

- [ ] **Step 1: Write the permutation script**

Create `scripts/permutation_c_class_inflation.py`:

```python
"""P0-4 (R0 W2 / R1 W5 / DA-CRITICAL-3): permutation null for the
c-class primary MP shift.

Question: §3.5.1 selects, for each c-class PUT (c1/c2/c3), the MP
with maximum mean SMS over MP1..MP5. This is a max-over-5 statistic.
What is the percentile rank of the observed v3b mean (c-class
aligned mean SMS) under a permutation null where MP labels within each
c-class PUT are randomly permuted?

Method:
- Read sms_track2_v4.json filtered to c-class PUTs (15 cells).
- For each of N_PERM=10000 permutations, randomly shuffle MP labels
  within each c-class PUT, recompute "selected primary MP = argmax over
  5", record the resulting c-class aligned mean SMS.
- Report: observed v3b c-class aligned mean, percentile rank in null
  distribution, Bonferroni x 5 effective alpha bound.

Output: data/results/c_class_permutation_v4.json
Run: SMS_VERSION=v4 PYTHONPATH=src .venv/bin/python scripts/permutation_c_class_inflation.py
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

VERSION = os.environ.get("SMS_VERSION", "v4")
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "42"))
SMS_FILE = f"sms_track2_{VERSION}.json"
OUT_FILE = f"c_class_permutation_{VERSION}.json"

print(f"permutation_c_class: SMS_VERSION={VERSION} N_PERM={N_PERM}")

sms = json.loads((ROOT / "data/results" / SMS_FILE).read_text())

c_puts = ["c1", "c2", "c3"]
mp_indices = [1, 2, 3, 4, 5]
sms_by_put_mp = {}
for cell, v in sms.items():
    put = cell.split("_")[0].lower()
    if put not in c_puts:
        continue
    mp = int(cell.split("MP")[1])
    sms_by_put_mp.setdefault(put, {})[mp] = v["sms"]

assert all(len(sms_by_put_mp[p]) == 5 for p in c_puts), \
    f"Need 5 MPs per c-class PUT; got {[(p, len(sms_by_put_mp[p])) for p in c_puts]}"

# Observed: max-over-5 mean per c-class PUT (this is the v3b selection rule)
observed_per_put = [max(sms_by_put_mp[p].values()) for p in c_puts]
observed_c_aligned_mean = float(np.mean(observed_per_put))

# Null: shuffle MP indices within each c-class PUT, take max-over-5,
# average across the three PUTs
rng = np.random.default_rng(SEED)
null_means = np.empty(N_PERM)
for i in range(N_PERM):
    null_per_put = []
    for p in c_puts:
        vals = list(sms_by_put_mp[p].values())
        rng.shuffle(vals)
        null_per_put.append(max(vals))
    null_means[i] = float(np.mean(null_per_put))

percentile = float(np.mean(null_means >= observed_c_aligned_mean))

# Bonferroni: family of 5 MP candidates per PUT, alpha_effective = alpha / 5
alpha_naive = 0.05
alpha_bonf = alpha_naive / 5

report = {
    "version": VERSION,
    "n_perm": N_PERM,
    "seed": SEED,
    "method": "max-over-5 MP selection per c-class PUT, permute MP labels within PUT",
    "observed": {
        "per_put_max_sms": {p: float(max(sms_by_put_mp[p].values())) for p in c_puts},
        "c_class_aligned_mean": observed_c_aligned_mean,
    },
    "null_distribution": {
        "mean": float(null_means.mean()),
        "std": float(null_means.std(ddof=1)),
        "p25": float(np.percentile(null_means, 25)),
        "p50": float(np.percentile(null_means, 50)),
        "p75": float(np.percentile(null_means, 75)),
        "p95": float(np.percentile(null_means, 95)),
        "p99": float(np.percentile(null_means, 99)),
    },
    "permutation_p_value_one_sided_geq": percentile,
    "bonferroni": {
        "family_size": 5,
        "alpha_naive": alpha_naive,
        "alpha_effective": alpha_bonf,
    },
    "interpretation": (
        "permutation_p_value_one_sided_geq quantifies how often the "
        "max-over-5 rule (used in §3.5.1) achieves a c-class aligned "
        "mean SMS at least as large as observed when MP labels are "
        "exchangeable within each c-class PUT. Bonferroni-effective "
        "alpha is the conservative bound when no permutation is run. "
        "Both are sensitivity analyses for the c-class primary MP "
        "shift's selection-on-response inflation."
    ),
}

(ROOT / "data/results" / OUT_FILE).write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(f"observed c-class aligned mean: {observed_c_aligned_mean:.4f}")
print(f"permutation p (one-sided ≥): {percentile:.4f}")
print(f"Bonferroni effective alpha: {alpha_bonf:.4f}")
print(f"-> {OUT_FILE}")
```

- [ ] **Step 2: Run the script**

```bash
cd "<MT_ROOT>"
SMS_VERSION=v4 PYTHONPATH=src .venv/bin/python scripts/permutation_c_class_inflation.py
```
Expected: prints `observed c-class aligned mean`, `permutation p`, `Bonferroni effective alpha`; writes `data/results/c_class_permutation_v4.json` (~0.7 KB).

If `permutation p < 0.20`, the observed selection is unlikely under the null and the inflation concern is partially mitigated; report the number. If `p >= 0.20`, the selection effect is consistent with chance — report this honestly.

- [ ] **Step 3: Allow-list the new output in `.gitignore`**

`old_string`:
```
!data/results/h5_sensitivity_v4.json
```
`new_string`:
```
!data/results/h5_sensitivity_v4.json
!data/results/c_class_permutation_v4.json
```

- [ ] **Step 4: Insert the permutation result into §3.5.1 caveat #2**

Locate §3.5.1 caveat #2 (the post-hoc data-driven c-class primary MP shift caveat) and append a quantification paragraph.

Find the existing caveat text (use grep to locate exact phrasing):
```bash
grep -n "selection-on-response\|事后选择\|post-hoc\|c-class primary" 论文初稿P2.md | head
```

Once located, append after the existing caveat:

```
**Quantitative bound on selection inflation**(本文 P0-4 修订增):用 permutation 检验对 max-over-5 选择规则做事后量化。在 N_PERM = 10 000 次 within-PUT MP 标签置换下,观测的 c-class aligned mean SMS 在 null 分布中的 percentile rank 为 [插入 `permutation_p_value_one_sided_geq` × 100]%。Bonferroni 上界为 α_effective = α / 5 = 0.01。两种 sensitivity 共同的解读:c→MP1 选择的 effect size 不能在 α = 0.05 严格水平上视作 confirmatory;abstract 与 §5.8.2 已据此把 v3b 全部降级为 exploratory(P0-3)。详见 `data/results/c_class_permutation_v4.json`。
```

(Replace `[插入 ...]%` with the actual percentile from the script output.)

- [ ] **Step 5: Verify**

```bash
grep -n "permutation\|Bonferroni\|c_class_permutation" 论文初稿P2.md | head
ls -la data/results/c_class_permutation_v4.json
```
Expected: §3.5.1 mentions both the permutation result and Bonferroni bound; the JSON exists and is ~0.7 KB.

- [ ] **Step 6: Commit**

```bash
git add 论文初稿P2.md scripts/permutation_c_class_inflation.py data/results/c_class_permutation_v4.json .gitignore
git commit -m "$(cat <<'EOF'
analysis(P0-4): permutation null + Bonferroni bound for c-class shift (R0 W2 / R1 W5 / DA-CRITICAL-3)

§3.5.1 c-class primary MP shift uses max-over-5 selection per PUT.
The paper acknowledged selection-on-response in qualitative caveat
#2 but offered no quantitative bound. Reviewers across 3/5 panels
asked for either a permutation null or a Bonferroni multiplier.

scripts/permutation_c_class_inflation.py: 10000 within-PUT MP label
permutations, recompute max-over-5 c-class aligned mean per draw,
report the observed value's percentile rank in the null distribution.

data/results/c_class_permutation_v4.json: full report including
null mean / std / quantiles, Bonferroni effective alpha = 0.01.

§3.5.1 caveat #2 now includes both quantitative bounds and links to
the JSON. Combined with P0-3, v3b is consistently treated as
exploratory throughout the paper.
EOF
)"
```

---

## Task 5: P0-5 — Selection-on-response explicit declaration (no v4-pre rerun)

**Reviewer consensus:** 3/5 (R0 W1 fix-1, R1 W3 fix-3, DA-CRITICAL-1)
**Concern:** v4 cross-source pool was built **conditional on v3b's c-class primary MP shift** — i.e., the LLM-source contrast inherits the v3b selection. Reviewers ask for either (a) a v4-pre cell (cross-source × c→MP5 pre-shift) actually run, or (b) an explicit declaration that v4 is conditional. We choose (b) here to avoid a 2-3 day LLM rerun (~$20-30 cost). v4-pre rerun is deferred to R2 revision per editorial decision §4.

**Files:**
- Modify: `论文初稿P2.md` §4.2.5 (chained-conditioning declaration), §7.1 (new R11 limitation entry)

- [ ] **Step 1: Locate §4.2.5(b) and the §7.1 risk list end**

```bash
grep -nE "^#### 4\.2\.5|^### 7\.1|R11|R12" 论文初稿P2.md | head
```
Expected: §4.2.5 around line 676; §7.1 around line 1198; existing R11 / R12 entries around the same area.

- [ ] **Step 2: Add a "chained-conditioning declaration" paragraph at the end of §4.2.5(e)**

Locate the §4.2.5(e) paragraph (per-PUT pool sampling) and append:

`old_string`: (the §4.2.5(e) paragraph last sentence — find via grep)
```
**池采样**(`scripts/build_pools.py`,POOL_VERSION=v4):per-PUT 30 mutants 上限,实测平均 24.3,范围 10-30。c1(GPR)只 10 mutants,因为 c1_HP1 / c1_CE1 算子在三家 LLM 上 V1-V4 通过率均接近零(GPR PUT 的 WhiteKernel 噪声项 1e-4 → 1e-1 微扰对输出影响极小,几乎全部触发 V3 non-trivial 失败,本身是 §6.2 R_sem/R_kill 解耦的另一面证据)
```
`new_string`:
```
**池采样**(`scripts/build_pools.py`,POOL_VERSION=v4):per-PUT 30 mutants 上限,实测平均 24.3,范围 10-30。c1(GPR)只 10 mutants,因为 c1_HP1 / c1_CE1 算子在三家 LLM 上 V1-V4 通过率均接近零(GPR PUT 的 WhiteKernel 噪声项 1e-4 → 1e-1 微扰对输出影响极小,几乎全部触发 V3 non-trivial 失败,本身是 §6.2 R_sem/R_kill 解耦的另一面证据)

**Chained-conditioning 声明(P0-5,R0/R1/DA 共识修订)**:v4 跨源池在 c-class primary MP 上沿用 v3b 的事后选择(c1/c2/c3 → MP1)。因此 Δδ_{v3b → v4} = −0.007 不是中性条件下的 LLM 源多样性测试,而是 *conditional on v3b's c-class selection* + *identical prompt template* 的双重条件下的对照。本文不实跑 v4-pre (cross-source × c→MP5 pre-shift) 格点,因为(i) 相对当前 v3 → v3b → v4 链条,v4-pre 主要回答 "v3b 选择是否吃掉了一部分原本属于 LLM 多样性的方差",该问题与 P4 论文的 differential prompt 实验(§4.2.5.1)同构,P4 一并解决更经济;(ii) v4-pre 重跑成本 ~$20-30 + 2-3 days wall time,与本文已暴露的 narrative 收益不对称。**本声明使 v3b → v4 contrast 的 conditional 性质显式可见,不依赖 reader 推断**。
```

- [ ] **Step 3: Add R11 entry to §7.1 (or extend existing R11 if present)**

First check whether R11 already exists:
```bash
grep -n "R11\|7.1.7\|7.1.8" 论文初稿P2.md | head
```

If R11 exists, append a sub-bullet; else add a new R11 entry after the last R-numbered subsection. Insert format:

```markdown
#### 7.1.X R11 Selection-on-response chained conditioning(NEW,P0-5)

v3b 与 v4 数据均 conditional on §3.5.1 c-class primary MP 的事后选择(c1/c2/c3 → MP1)。具体后果:

(a) **v3b sign test 4/4** 与 **v4 sign test 4/4** 都 inherit max-over-5 selection inflation;Bonferroni 上界 α_effective = 0.01(§3.5.1 P0-4 修订),permutation p 值见 `data/results/c_class_permutation_v4.json`。

(b) **Δδ_{v3b → v4} = −0.007** 是 conditional on v3b 选择 + identical prompt 的双重条件 contrast,**不是中性条件下的 LLM 源多样性测试**。中性版本(v4-pre × c→MP5 pre-shift,以及 §4.2.5.1 differential prompt)留 P4 / R2 修订。

**缓解**:Abstract / §5.8.2 / §6.3(P0-3 修订)已把所有 v3b/v4 sign test 结果降级为 exploratory;§4.2.5(e)(P0-5 本节修订)已显式声明 chained-conditioning;§3.5.1(P0-4 修订)已加 permutation + Bonferroni 量化。**该威胁在本文版本的范围内已尽可能降低,但不能根除——根除需要 v4-pre 重跑或 P4 的 differential prompt 实验**。
```

(If §7.1 already has a numbered subsection for R11, append; if not, insert as the next available number — check existing numbering with grep first.)

- [ ] **Step 4: Verify**

```bash
grep -n "Chained-conditioning\|chained conditioning\|R11" 论文初稿P2.md | head
```
Expected: §4.2.5 contains the chained-conditioning declaration; §7.1 contains the R11 entry.

- [ ] **Step 5: Commit**

```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P0-5): chained-conditioning explicit declaration (R0 W1 / R1 W3 / DA-CRITICAL-1)

v4 cross-source pool inherits v3b's c-class primary MP selection.
Therefore Δδ_{v3b->v4} = -0.007 is NOT a neutral LLM source diversity
test — it is conditional on v3b's c-class selection AND identical
prompt template (per §4.2.5 fixed-template clause).

Two-part fix without rerunning v4-pre (deferred per editorial
decision §4 cost-benefit):

(a) §4.2.5(e) appends a "Chained-conditioning declaration" making
    the dual conditioning explicit and citing the cost-benefit reason
    for not running v4-pre in this revision.
(b) §7.1 adds R11 ("Selection-on-response chained conditioning")
    entry summarizing the conditioning, the consequences for v3b/v4
    sign tests and Δδ_LLM, and the mitigation steps (P0-3 + P0-4 +
    P0-5 + §4.2.5.1 R-16 protocol).

Combined effect: every v3b / v4 number in the paper is now annotated
with its conditioning chain; reader cannot infer "neutral LLM
diversity test" from any passage.
EOF
)"
```

---

## Task 6: P0-6 — IST 2024 review reference resolution

**Reviewer consensus:** 3/5 (R0 W4, R2 W6, DA-MAJOR-6)
**Concern:** §8.3 has `[Authors TBD]` placeholder for the IST 2024 LLM-mutant review. The review's "0.30-0.45 contextual support" is cited 4 times (§1.3.2, §5.7.2, §6.1, §7.1.6). If the reference cannot be resolved, the contextual-support narrative collapses.

**Files:**
- Modify: `论文初稿P2.md` §8.3 (reference entry), and the 4 in-text contextual-support citations

- [ ] **Step 1: Resolve the IST 2024 reference via DOI lookup**

The DOI URL on file is `https://www.sciencedirect.com/science/article/abs/pii/S0950584924000739`. Use `WebFetch` or open in browser to retrieve the canonical bibliographic entry. If `WebFetch` is available, use it; else flag the lookup as a manual step for the user before commit.

If you successfully retrieve full citation, proceed to Step 2A. If you cannot retrieve OR the retrieved paper is **not** an LLM-mutation review (e.g., it turns out to be a single case study), proceed to Step 2B (fallback: drop the reference and the 4 in-text citations).

- [ ] **Step 2A: If retrieval succeeds — fill in §8.3 entry**

Replace the placeholder. Use Edit:

`old_string`:
```
- (IST review) **[Authors TBD]** (2024). Effective test generation using pre-trained large language models and mutation testing. *Information and Software Technology*. https://www.sciencedirect.com/science/article/abs/pii/S0950584924000739
  - *Note:* full author list to be filled at typesetting; bibliographic record verified via DOI/URL on 2026-05-01.
```
`new_string`:
```
- **[ACTUAL_AUTHORS]** (2024). Effective test generation using pre-trained large language models and mutation testing. *Information and Software Technology*, [VOLUME](pp. [PAGES]). https://doi.org/[ACTUAL_DOI]
```

Also verify the paper actually contains the "Cliff's δ 0.30-0.45 LLM-mutant range" claim by reading the abstract / methods. Document this verification in the commit message.

- [ ] **Step 2B: If retrieval fails or the paper is not an LLM-mutant review — drop the contextual-support claim**

Remove the IST 2024 entry from §8.3 entirely. Then for each of the 4 in-text citations, replace with a Tip 2024 single-citation + estimand caveat.

Search for the 4 occurrences first:
```bash
grep -nE "Information and Software Technology\\(2024\\)|IST 2024|0.30-0.45" 论文初稿P2.md
```

For each occurrence (anchor by its surrounding sentence; use unique `old_string`), replace with:

```
Tip et al. (2024) LLMorpheus 在 JavaScript 上观察到 LLM-mutant Cliff's δ 处于 medium-effect 区间。**Estimand caveat**:Tip 2024 比较的是"LLM mutants vs traditional mutants on fault detection rate"(跨变异源比较),本文 §5.7.2 比较的是"aligned vs cross MP slice on the same mutant pool"(单源 within-pool 比较)。两个 δ 数值相近不构成 substantive support,仅作为 LLM-mutant 文献中 medium-effect 现象的参考。
```

- [ ] **Step 3: Verify**

```bash
grep -nE "\\[Authors TBD\\]|\\[ACTUAL_AUTHORS\\]" 论文初稿P2.md
```
Expected: zero hits. The placeholder is gone (either resolved or removed).

```bash
grep -c "0.30-0.45" 论文初稿P2.md
```
If Step 2A succeeded, count is ≤ 4 (resolved citations). If 2B succeeded, count is 0 (claim withdrawn).

- [ ] **Step 4: Commit**

If 2A succeeded:
```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P0-6): resolve IST 2024 LLM-mutant review citation (R0 W4 / R2 W6 / DA-MAJOR-6)

§8.3 [Authors TBD] placeholder replaced with full bibliographic entry
retrieved from DOI 10.1016/[ACTUAL_DOI]. Verified the cited paper
does report "LLM-mutant Cliff's δ in 0.30-0.45 range" claim used by
§1.3.2 / §5.7.2 / §6.1 / §7.1.6.
EOF
)"
```

If 2B was used:
```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P0-6): withdraw unverifiable IST 2024 reference (R0 W4 / R2 W6 / DA-MAJOR-6)

§8.3 [Authors TBD] entry could not be resolved to an LLM-mutation
review at DOI 10.1016/j.infsof.2024.[...]. Per editorial decision §4
fallback policy, the reference is removed and the 4 in-text
contextual-support citations are downgraded to Tip 2024 single-
citation + estimand caveat (LLM mutants vs traditional mutants on
fault detection rate is NOT the same estimand as aligned vs cross MP
slice on a single mutant pool).
EOF
)"
```

---

## Task 7: P1-3 — §9 SMS→MS theorem strict-vs-asymptotic + L1-L6 dependency

**Reviewer consensus:** 4/5 (R0 W8, R1 §4 final, R2 W3+W4, DA-MAJOR-3)
**Concern:** §9 claims "strictly degenerate" but the proof gives only asymptotic / measure-zero equivalence (continuous D_S → strict equality impossible). L1-L6 are listed as 6 axes but actually couple as 3 joint conditions (L1+L2 for equiv, L3+L4 for killed, L5+L6 for mut). Lemma 9.1 has a measure-theoretic gap.

**Files:**
- Modify: `论文初稿P2.md` Abstract (line 14), §9.2 (L1-L6 list), §9.3 (Lemma 9.1 statement), §9.4 (theorem statement)

- [ ] **Step 1: Modify Abstract "strictly degenerate" → "degenerate modulo measure-zero subsets"**

`old_string` (within line 14 Abstract):
```
SMS provides a domain-aware adequacy metric that strictly degenerates to classical syntactic MS in the syntactic limit
```
`new_string`:
```
SMS provides a domain-aware adequacy metric that degenerates to classical syntactic MS in the syntactic limit (modulo D_S-measure-zero subsets, see §9 for the formal statement)
```

- [ ] **Step 2: Reorganize §9.2 from "6 conditions" to "3 joint conditions"**

`old_string`:
```
### 9.2 退化极限定义(R-8)

定义**退化极限 L**为以下 6 条同时成立的参数与配置:

1. **L1**:ε_eq → 0(等价容差归零)
2. **L2**:K_eq → ∞(等价采样覆盖完整输入空间 D_S)
3. **L3**:ε_AVP^k → 0,所有 k ∈ MP(AVP 容差归零)
4. **L4**:MP 集合 = {等式判定 MP_eq}(R(y, y') ≡ y = y',即每个 MR 退化为输出严格等同)
5. **L5**:mut_j 切换为规则式语法算子(Mothra-style AOR/ROR/SDL/CRP 等),不依赖领域语义
6. **L6**:被测程序类 cls(I) ⊆ {命令式确定性程序}(无概率/surrogate/ML)
```
`new_string`:
```
### 9.2 退化极限定义(R-8 + P1-3 修订:从 6 axes 改写为 3 joint conditions)

退化极限 L 由 **3 个 joint conditions** 组成,每个 joint condition 控制 SMS 公式的一个层(分子 / 分母 mut / 分母 equiv);**L1–L6 不是 6 个独立 axes**,而是配对的 joint conditions(此修订回应 R0 W8 / R1 §4 / R2 W3 / DA-MAJOR-3 的依赖性质询)。

**Joint condition L_equiv**(控制 equiv 退化层,引理 9.1):
- **L1**:ε_eq → 0(等价容差归零)
- **L2**:K_eq → ∞(等价采样覆盖完整输入空间 D_S)
- 配对原因:在连续型 D_S 上,L1 单独成立但 L2 不成立时,equiv 仍是概率近似(K_eq 个采样不能覆盖整个 D_S);L2 单独成立但 L1 不成立时,逐位等同条件被 ε_eq 容差冲淡。两者必须同时取极限,equiv 才退化为经典行为等价(也仅在 D_S-measure-zero 集合外严格成立,见引理 9.1 修订陈述)。

**Joint condition L_killed**(控制 killed 退化层,引理 9.2):
- **L3**:ε_AVP^k → 0,所有 k ∈ MP(AVP 容差归零)
- **L4**:MP 集合 = {等式判定 MP_eq}(R(y, y') ≡ y = y')
- 配对原因:L3 在 L4 不成立时,ε_AVP → 0 仍允许非平凡 MP 关系存在(R 可以是单调性、收敛阶等),不退化到经典差异检出;L4 在 L3 不成立时,等式判定仍带 ε_AVP 容差,不严格化。两者必须同时取极限,killed 判定才退化为经典差异检出。

**Joint condition L_mut**(控制 mut 退化层,引理 9.3):
- **L5**:mut_j 切换为规则式语法算子(Mothra-style AOR/ROR/SDL/CRP 等),不依赖领域语义
- **L6**:被测程序类 cls(I) ⊆ {命令式确定性程序}(无概率/surrogate/ML)
- 配对原因:L5 在 L6 不成立时,语法算子在概率/ML 程序上仍可能触发领域语义算子的子集(如 dropout 概率的字面常量替换);L6 在 L5 不成立时,命令式确定性程序仍可被语义算子(OS/HP/TF/SI)变异,mut(S) ≠ syntactic mutants。两者必须同时取极限,mut(S) 才退化为 Jia & Harman 文献中的语法变异体集合。

**总极限 L = L_equiv ∧ L_killed ∧ L_mut**(三 joint conditions 同时成立)。
```

- [ ] **Step 3: Modify Lemma 9.1 statement to add measure-zero qualifier**

`old_string`:
```
**引理 9.1**(equiv 退化)。在 L1 ∧ L2 下,语义类等价 (E1 ∧ E2) 退化为经典行为等价。

**证明**:
- E1(类型一致性)在 ε_eq → 0 极限下平凡成立(L6 命令式程序输出空间为标量/向量,类型由编程语言静态保证)。
- E2(数值/语义近似等同)定义为:对 K_eq 个采样输入 x ~ D_S,有 |S_i(x) − s'(x)| < ε_eq。在 L1 (ε_eq → 0) ∧ L2 (K_eq → 全 D_S) 下,该条件等价于 ∀x ∈ D_S, S_i(x) = s'(x),即逐位行为等同——这正是 Jia & Harman (2011) §3 经典等价变异体定义。 ∎
```
`new_string`:
```
**引理 9.1**(equiv 退化,P1-3 修订:加 measure-zero 限定)。在 joint condition L_equiv (L1 ∧ L2) 下,语义类等价 (E1 ∧ E2) **几乎处处**(almost everywhere w.r.t. 测度 D_S)退化为经典行为等价。

**证明**:
- E1(类型一致性)在 ε_eq → 0 极限下平凡成立(L6 命令式程序输出空间为标量/向量,类型由编程语言静态保证)。
- E2(数值/语义近似等同)定义为:对 K_eq 个采样输入 x ~ D_S,有 |S_i(x) − s'(x)| < ε_eq。在 L1 (ε_eq → 0) ∧ L2 (K_eq → ∞ 与 D_S 同测度等价采样)下,该条件**几乎处处等价于** ∀x ∈ D_S \\ N, S_i(x) = s'(x),其中 N 是 D_S-测度零集(连续型 D_S 上严格逐位等同需要排除 measure-zero exceptions,如 numerical NaN propagation 点或 floating-point cancellation 病态点;离散型 D_S 上 N = ∅,严格逐位等同)——这与 Jia & Harman (2011) §3 经典等价变异体定义在 measure-zero 等价类下一致。 ∎
```

- [ ] **Step 4: Modify the main theorem statement (§9.4) to reflect "almost everywhere"**

`old_string`:
```
**定理 9.1**(SMS-MS 退化定理)。在退化极限 L 下,
```
`new_string`:
```
**定理 9.1**(SMS-MS 退化定理,P1-3 修订)。在退化极限 L = L_equiv ∧ L_killed ∧ L_mut 下,**几乎处处**(almost everywhere w.r.t. D_S)有
```

- [ ] **Step 5: Verify**

```bash
grep -nE "几乎处处|almost everywhere|Joint condition|measure-zero|D_S-measure" 论文初稿P2.md | head
```
Expected: ≥3 hits (Abstract, §9.2 L_equiv/L_killed/L_mut groupings, §9.3 Lemma 9.1, §9.4 theorem statement).

- [ ] **Step 6: Commit**

```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P1-3): §9 strict-vs-asymptotic + L1-L6 dependency (R0 W8 / R1 §4 / R2 W3+W4 / DA-MAJOR-3)

Three coordinated changes addressing 4/5 reviewer consensus:

(1) Abstract "strictly degenerates" -> "degenerates ... modulo
    D_S-measure-zero subsets" — continuous D_S admits strict
    pointwise equality only on a measure-1 set, not on every input.

(2) §9.2 reorganization from "6 independent axes (L1-L6)" to
    "3 joint conditions (L_equiv = L1 ∧ L2; L_killed = L3 ∧ L4;
    L_mut = L5 ∧ L6)". Each joint condition controls one layer of
    the SMS formula. Pair-coupling rationale documented per joint
    (e.g., L1 alone fails on continuous D_S because K_eq is finite;
    L4 alone fails because ε_AVP > 0 dilutes equality oracle).

(3) Lemma 9.1 statement and main theorem (§9.4) carry the "almost
    everywhere w.r.t. D_S" qualifier explicitly. Proof of Lemma 9.1
    notes the measure-zero exception set N (NaN propagation,
    floating-point cancellation pathologies on continuous D_S; N = ∅
    on discrete D_S).

The substantive theorem (SMS -> classical MS in the limit) is
preserved; only the "strictness" claim is calibrated to what
measure-theoretic continuous-input analysis can support.
EOF
)"
```

---

## Task 8: P1-5 — Zero-mass dominance propagation to §5.7.2 H2 verdict

**Reviewer consensus:** 3/5 (R0 W6, R1 W7, DA-3.1)
**Concern:** §5.6.1.1 already documents zero-mass dominance (75% cells = 0; effective n_aligned ≈ 12, not 60). But §5.7.2 reports H2 with n=12 / n=48 splits without propagating this caveat — the Cliff's δ CI is computed on the surface n, not the effective n.

**Files:**
- Modify: `论文初稿P2.md` §5.7.2 (verdict paragraph)

- [ ] **Step 1: Locate §5.7.2 H2 verdict paragraph**

```bash
grep -n "H2 verdict\|^**H2 verdict\|未达成大效应" 论文初稿P2.md | head
```

- [ ] **Step 2: Insert effective-sample-size note into §5.7.2 H2 verdict**

Find the paragraph beginning with "**H2 verdict: rejected**" and append after it:

`old_string`:
```
**H2 verdict: rejected**。在 pre-registered 主分析(v3,c→MP5,n_aligned=12,n_cross=48)下,Cliff's δ = 0.323 距 Romano (2006) large effect 阈值 0.474 差 0.151,95% CI 下限 0.017,效应规模归类为 small-to-medium。两次 exploratory sensitivity(v3b 数据驱动 primary MP shift,§3.5.1;v4 cross-source pool,§4.2.5)虽提升 δ 至 0.446 / 0.439,但均未越过 0.474 严格阈值,且 v3 → v3b 改动包含已知的事后选择 confound(c-class primary MP 选择基于已观察数据,见 §3.5.1)。
```
`new_string`:
```
**H2 verdict: pre-registered point-estimate criterion not met**(P0-8 修订:措辞从 "rejected" → "not met under pre-registered point-estimate criterion",原因见下文 effective-n 注与 P0-8 commit message)。在 pre-registered 主分析(v3,c→MP5,n_aligned=12,n_cross=48)下,Cliff's δ = 0.323 距 Romano (2006) large effect 阈值 0.474 差 0.151,95% CI 下限 0.017,效应规模归类为 small-to-medium。两次 exploratory sensitivity(v3b 数据驱动 primary MP shift,§3.5.1;v4 cross-source pool,§4.2.5)虽提升 δ 至 0.446 / 0.439,但均未越过 0.474 严格阈值,且 v3 → v3b 改动包含已知的事后选择 confound(c-class primary MP 选择基于已观察数据,见 §3.5.1 + P0-4 permutation 量化)。

**Effective sample size note**(P1-5 修订,R0 W6 / R1 W7 / DA-3.1 共识):surface n_aligned = 12 与 n_cross = 48,但 §5.6.1.1 已述 v4 数据中 75% cells (45 / 60) SMS = 0(零质量主导)。在 cross-slice 上,这意味着 48 cells 中约 88% (42 / 48) 是零,Cliff's δ 的 inference 实际由 12 个 aligned cells + 6 个非零 cross cells 主导,**effective n ≈ 12 + 6 ≈ 18 而非 surface 60**。这一实际样本规模约束:
- (a) 解释了 §5.7.3 power 分析中"对 large-effect (δ > 0.474) 检测功效仅 0.42"——并非样本规模的 nominal-vs-effective 误差导致;
- (b) 解释了 95% bootstrap CI [0.127, 0.740] 的宽度——上下限比例 ≈ 5.83,反映 effective n ≈ 18 时 percentile bootstrap 的已知 liberal 倾向;
- (c) **不改变** H2 verdict 方向(point estimate 0.439 < 0.474 是 effect-size ceiling 而非样本规模问题,§5.7.3 已论证),但 reader 应据此理解 CI 宽度的成因。

未来工作(P4)在扩样本到 n ≥ 30 PUT 时,zero-mass dominance 是否随 PUT 类多样化而稀释,是 effective-n 改善的 testable hypothesis。
```

- [ ] **Step 3: Verify**

```bash
grep -nE "effective n\|zero-mass\|effective sample size" 论文初稿P2.md | head
```
Expected: §5.7.2 now references both §5.6.1.1 zero-mass and the effective-n calculation.

- [ ] **Step 4: Commit**

```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P1-5): zero-mass dominance propagated to §5.7.2 H2 verdict (R0 W6 / R1 W7 / DA-3.1)

§5.6.1.1 documented 75% zero-SMS cells (mean cross 88% zero) but
§5.7.2 H2 verdict computed Cliff's δ CI on surface n=(12, 48). 3/5
reviewers asked for the effective-n implication to be propagated to
the verdict paragraph.

§5.7.2 now contains an "Effective sample size note":
- effective n ≈ 12 + 6 = 18 (12 aligned + non-zero cross cells)
- explains §5.7.3 power = 0.42 at δ > 0.474 threshold
- explains CI [0.127, 0.740] width via percentile-bootstrap liberal
  tendency at effective n ≈ 18
- does NOT change H2 verdict (effect-size ceiling argument is
  unaffected, see §5.7.3)

Also softens "rejected" -> "not met under pre-registered point-estimate
criterion" per P0-8 (already-listed P0 item; this revision touches the
same paragraph).
EOF
)"
```

---

## Task 9: P1-7 — v3 dual-blind / v4 no dual-blind protocol asymmetry

**Reviewer consensus:** 3/5 (R0 §4, R3 W8, DA §4.2)
**Concern:** §4.2.4 describes the original Phase-1 dual-blind reviewer pipeline (Claude-Opus generator + GPT-5.4 reviewer + DeepSeek arbitration). §4.2.5(b) for v4 cross-source notes "MVP 不调用 reviewer LLM (成本/速度优先,留 P4 完整三 LLM dual-blind 审核)". This is a protocol asymmetry that may itself explain Δδ_LLM = −0.007 (lower-quality v4 mutants → smaller δ vs lower-quality v3b mutants under the same magnitude).

**Files:**
- Modify: `论文初稿P2.md` §4.2.5(b) (clarify the asymmetry), §7.1 (extend R11 OR add R12 protocol-implementation gap)

- [ ] **Step 1: Locate §4.2.5(b) and the existing §7.1 numbered risks**

```bash
grep -n "MVP 不调用 reviewer LLM\|dual-blind\|双盲\|R11\|R12" 论文初稿P2.md | head
```

- [ ] **Step 2: Strengthen §4.2.5(b) protocol-asymmetry declaration**

`old_string`:
```
(b) **机械验证 V1-V4**(`src/p2/mutators/validation.py`):语法、可执行、非平凡(`|y_mutant - y_original| > 1e-6` 在探针集上)、签名一致性。**MVP 不调用 reviewer LLM**(成本/速度优先,留 P4 完整三 LLM dual-blind 审核)
```
`new_string`:
```
(b) **机械验证 V1-V4**(`src/p2/mutators/validation.py`):语法、可执行、非平凡(`|y_mutant - y_original| > 1e-6` 在探针集上)、签名一致性。

**Protocol asymmetry 声明(P1-7 修订,R0/R3/DA 共识)**:v4 跨源池**不调用 reviewer LLM**(成本/速度优先,留 P4 完整三 LLM dual-blind 审核);而 v3 / v3b 数据采集时使用了 §4.2.4 原始 Phase-1 dual-blind 协议(Claude-Opus 生成 + GPT-5.4 审核 + DeepSeek 仲裁)。这构成 v3 / v3b vs v4 之间的**协议不对称**:v4 mutant 池在 V1-V4 机械门下,但缺 LLM 审核环节。**潜在 confound**:Δδ_{v3b → v4} = −0.007 的 fraction 可能不是"LLM 源多样性贡献",而是"v4 池较 v3b 池在 mutant 质量上的小幅下行"。本文未隔离这一 confound;P4 将在 v4 全格点上重跑 dual-blind reviewer,届时可分离质量差与源多样性两个因素。该 confound 与 §7.1 R11 chained-conditioning 平行。
```

- [ ] **Step 3: Add §7.1 entry for the protocol-implementation gap**

Find the next available R-number after R11 (Task 5 added R11; this task adds R12, but if R12 already exists for HOM caveat per current §3.2.6, use R13 or rename — check first):

```bash
grep -nE "R12|R13|R14" 论文初稿P2.md | head
```

If R12 already in use for HOM, use R13. Add the entry (replace `RX` with the actual number):

```markdown
#### 7.1.X RX Protocol-implementation gap between v3/v3b and v4(NEW,P1-7)

v3 / v3b 数据采集时使用了 §4.2.4 原始 Phase-1 dual-blind 协议(Claude-Opus 生成 + GPT-5.4 审核 + DeepSeek 仲裁);v4 跨源池仅过 V1-V4 机械门,**缺 LLM reviewer 审核环节**(§4.2.5(b))。

**潜在 confound**:Δδ_{v3b → v4} = −0.007 的一部分变异可能不是"LLM 源多样性贡献",而是"v4 池较 v3b 池在 mutant 质量上的小幅下行"。

**缓解(本文范围内)**:
- v4 池**确实使用了三家 LLM 的源多样性**(Claude / GPT-5.4 / DeepSeek 各 ~1/3 mutant 数,§4.2.5(d) 三家贡献 101 / 98 / 99),从这个意义上,Δδ_{v3b → v4} 不是单源-vs-单源的 trivial 比较;
- §6.2 LRCA 数据显示 v4 池的 mean C1_share 0.209 高于 v3b 的 0.164(quality 不降反升),弱反对"v4 mutant 质量下行"假设;
- 但**完全分离 protocol asymmetry 与 source diversity 仍需 P4 在 v4 全格点上重跑 dual-blind reviewer**(估 60-100 mutant 抽样级别可达,~$5-8 USD)。

**与 R11 的关系**:R11 关注 v3b → v4 的 *selection* 不对称(c-class primary MP 选择继承);R[X] 关注 v3 / v3b → v4 的 *protocol* 不对称(dual-blind vs 仅 V1-V4)。两个不对称都贡献 Δδ_{v3b → v4} 的解释空间,**不能合并视为单一"LLM 多样性贡献"信号**。
```

- [ ] **Step 4: Verify**

```bash
grep -nE "Protocol asymmetry|protocol-implementation gap|dual-blind 协议" 论文初稿P2.md | head
```
Expected: §4.2.5(b) and §7.1 both contain the protocol-asymmetry declaration; the new R-numbered entry references R11 for cross-link.

- [ ] **Step 5: Commit**

```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(P1-7): protocol asymmetry between v3/v3b dual-blind and v4 V1-V4-only (R0 §4 / R3 W8 / DA §4.2)

§4.2.5(b) noted that v4 cross-source pool skips the §4.2.4 dual-blind
reviewer LLM step (cost/speed). 3/5 reviewers flagged this as a
potential confound: Δδ_{v3b->v4} = -0.007 may have a "v4 mutant
quality drop" component, not pure LLM source diversity.

Two-part fix:

(a) §4.2.5(b) "Protocol asymmetry declaration" makes the v3/v3b
    dual-blind vs v4 mechanical-only difference explicit.

(b) §7.1 adds a numbered protocol-implementation-gap risk entry
    (R12 or R13 depending on existing numbering) listing:
    - the source of the asymmetry,
    - the partial mitigation (v4 LRCA C1_share 0.209 actually higher
      than v3b 0.164, weakly contradicting the "quality drop"
      hypothesis),
    - the unresolved separation problem (deferred to P4),
    - the relationship with R11 chained-conditioning (the two are
      orthogonal contributions to Δδ_LLM uncertainty).

Combined with P0-2 (no synthesis ratio) and P0-5 (chained
conditioning), every Δδ_LLM ≈ -0.007 mention is now caveated with
both selection and protocol asymmetries.
EOF
)"
```

---

## Task 10: Update `docs/STATE.md` reviewer-progress counter

**Files:**
- Modify: `docs/STATE.md` §1 (reviewer progress closed/pending tally)

- [ ] **Step 1: Update the closed/pending counts**

`old_string`:
```
**已 close（24）：** P0: R-2, R-3, R-4, R-5, R-6, R-24 | P1: R-7, R-8, R-9, R-10, R-11 | P2: R-12, R-13, R-14, R-15, R-16(protocol), R-17, R-18, R-19, R-20, R-21, R-22, R-23, R-25(基础设施)

**Pending（4）：**
- **P0 blocker:** R-1（全文英文翻译，投稿必做；基础设施已就绪，待运行 ~$7 / 10 min；之后人审）
- **P2:** R-26/R-27/R-28（杂项，需 reviewer 原文核对）
```
`new_string`:
```
**已 close（24 + 9 reviewer-consensus revision items）：** Pre-2026-05-01 review: P0: R-2/3/4/5/6/24 | P1: R-7/8/9/10/11 | P2: R-12/13/14/15/16(protocol)/17/18/19/20/21/22/23/25(基础设施)

**2026-05-01 reviewer-consensus revision (plan: docs/superpowers/plans/2026-05-01-p2-reviewer-consensus-revision.md):**
P0: P0-1 (title scope) / P0-2 (17.6 ratio) / P0-3 (sign test downgrade) / P0-4 (permutation inflation) / P0-5 (chained conditioning) / P0-6 (IST 2024 resolved or withdrawn) | P1: P1-3 (§9 strict-vs-asymptotic) / P1-5 (zero-mass to §5.7.2) / P1-7 (protocol asymmetry)

**Pending：**
- **P0 blocker:** R-1（全文英文翻译，投稿必做；基础设施已就绪，待运行 ~$7 / 10 min；之后人审）
- **P0 from 2026-05-01 review:** P0-7 (pre-registration claim evidence — single-reviewer item, not in this plan), P0-8 (§5.7.2 verdict measure — partially handled by P1-5 in this plan, residual abstract wording)
- **P1 from 2026-05-01 review:** P1-1/2/4/6/8/9/10/11 (single-reviewer items, deferred)
- **P2 misc:** R-26/R-27/R-28（需 reviewer 原文核对）
```

- [ ] **Step 2: Verify and commit**

```bash
grep -nE "^已 close|reviewer-consensus" docs/STATE.md | head
git add docs/STATE.md
git commit -m "$(cat <<'EOF'
docs(STATE): reflect 9 reviewer-consensus revisions completed (2026-05-01 round)

Adds the 9 ≥3/5-consensus items from the 2026-05-01 review round
(plan: 2026-05-01-p2-reviewer-consensus-revision.md) to the STATE
ledger. Single-reviewer items remain deferred per editorial decision
§4 P0/P1/P2 prioritization.
EOF
)"
```

---

## Self-Review Checklist

After all tasks complete, verify:

- [ ] **Spec coverage**: Each of the 9 reviewer-consensus items in the editorial decision §4 P0/P1 list (5/5 P0-1 + 3/5 P0-2/3/4/5/6 + 4/5 P1-3 + 3/5 P1-5/7) is implemented by exactly one numbered task above. ✓
- [ ] **Placeholder scan**: No `TBD`, `TODO`, `implement later`, or unspecified-fix items remain in the plan. The only `[ACTUAL_AUTHORS]` and `[ACTUAL_DOI]` placeholders are inside Task 6 Step 2A and are explicitly conditional on a successful WebFetch lookup.
- [ ] **Type / numbering consistency**: §7.1 R-numbering: existing R10 = LLM-source diversity (per §7.1.7); this plan adds R11 (Task 5: chained conditioning) and R12 or R13 (Task 9: protocol asymmetry, depending on whether HOM-caveat already uses R12). Task 9 Step 3 explicitly checks numbering before adding.
- [ ] **Verification steps**: Every task has a grep / file-existence check before commit.
- [ ] **Number consistency**: After Task 4 runs `permutation_c_class_inflation.py`, the user must paste the actual `permutation_p_value_one_sided_geq` percentile into Task 4 Step 4 (the placeholder text in the new §3.5.1 paragraph). This is flagged inline.

If any of the above fails on review, fix in place before handing off.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-01-p2-reviewer-consensus-revision.md`. Two execution options:

1. **Subagent-Driven** (recommended) — I dispatch a fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** — Execute tasks in this session, batch with checkpoints

Which approach?
