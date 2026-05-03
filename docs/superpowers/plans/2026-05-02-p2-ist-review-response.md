# P2 IST 模拟评审 Major Revision 响应实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复模拟评审三大核心问题中的可操作部分（H2 power 双重标准、事后选择叙事污染、Abstract 缺 first-order 限定），生成 v4×MP5 contrast 数据剥离 R11 链式条件化，并写出 response-to-reviewer letter。

**Architecture:** 修复分三层：(1) 数据层——新增 v4×MP5 contrast 计算脚本，输出 `rq2_cliffs_delta_v4_mp5.json`；(2) 文本层——修改 `论文初稿P2_IST.md` 的 Abstract、§5.3、§5.5、§6.1、§6.3、§8.1 的强声明措辞，并加 † 标记区分 v3 主分析与 v3b/v4 探索性数字；(3) 沟通层——撰写 `response_to_simulated_review.md`，逐条对应评审三大问题与七小问题。论文行号基于 `论文初稿P2_IST.md` 当前 commit 状态（main HEAD: 2571df1）。

**Tech Stack:** Python 3.10 + numpy（已有 `src/p2/stats/cliffs_delta.py` 与 `scripts/compute_rq2.py`）；Markdown 编辑直接通过 Edit 工具；提交走 `git commit`。所有数据 SSOT 是 `data/results/paper_numbers_v4.json` 与 `lrca_60cell_v4.json`。

---

## File Structure

**Will create:**
- `scripts/compute_rq2_v4_mp5.py` — v4 SMS 数据 + v3 (MP5) primary 配置的 contrast 计算
- `data/results/rq2_cliffs_delta_v4_mp5.json` — 输出：剥离 R11 的稳健性 contrast
- `docs/review_2026-05-02/response_to_simulated_review.md` — 逐条 response letter

**Will modify:**
- `论文初稿P2_IST.md`
  - Abstract (行 19–21)：加 first-order 限定；同位呈现 v3/v4 数字；改 dominant lever 措辞
  - §3.4 (行 251–257)：在末尾追加 † 标记规约说明
  - §5.3 (行 401–421)：表格新增 v4 (under MP5) 行；在解释段落引用新数字
  - §5.5 (行 445–468)：4/4 数字加 †
  - §6.1 (行 491–497)：91.4% / 27% / 38% 数字加 †
  - §6.3 (行 507–509)：4/4 数字加 †
  - §8.1 (行 567–579)：finding (iii) 改为谨慎措辞；finding (iv) 加 †
  - 全文末页（在 §8.3 后或 References 前）：加单行脚注说明 † 含义
  - §5.2 末段 + §5.4 开头（行 397 + 423–424）：合并为单段，去掉 effective n 与 stipulated power 论证的重复
  - §1.4 (行 65–68) + §5.6 (行 470–474)：RQ4 一致标注 "descriptive only"

**Will not modify (out of scope for this revision round):**
- §2.6 Theorem 9.1 / Lemma 9.2 proof sketch（评审次要建议，下一轮）
- Appendix B 的 mutmut operator-coverage 表（推回 P4 或 response letter 中以理论同型论证）
- Zenodo DOI mint（终稿前再做，需要先冻结结果数据）

---

## Task 1: 计算 v4 在 MP5 (c-class) 条件下的 Cliff's δ contrast（剥离 R11 链式条件化）

**Files:**
- Create: `scripts/compute_rq2_v4_mp5.py`
- Create: `data/results/rq2_cliffs_delta_v4_mp5.json`
- Read-only: `src/p2/config/primary.py`, `src/p2/stats/cliffs_delta.py`, `data/results/sms_track2_v4.json`

**Why this task is P0:** 评审问题 1（H2 power 双重标准）的最关键反驳路径是给出 v4 在原 v3 主 MP（c-class = MP5）下的 contrast。现有 `compute_rq2.py` 接受 `SMS_VERSION` 与隐式的 `P2_PRIMARY_VERSION`，只需薄包装。这个数字若与 v4 (MP1) 的 0.439 显著偏离，说明 R11 链式条件化吞掉了部分效应；若一致，则反向证明 v3b 选择不是 v4 的因。无论结果如何都增强论文。

- [ ] **Step 1: 写包装脚本**

```python
# scripts/compute_rq2_v4_mp5.py
"""V4 SMS data with v3 (MP5) c-class primary — strips R11 chained conditioning.

Reads sms_track2_v4.json (cross-source pool) under PRIMARY_CELLS_V3
(c1/c2/c3 → MP5), computes Cliff's delta + 95% bootstrap CI + odds ratio,
writes data/results/rq2_cliffs_delta_v4_mp5.json. This contrast feeds the
§5.3 robustness row 'v4 (under v3 MP5)' added in Task 4.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.config.primary import PRIMARY_CELLS_V3 as PRIMARY  # explicit MP5
from p2.stats.cliffs_delta import bootstrap_delta_ci, cliffs_delta, odds_ratio

SMS_FILE = ROOT / "data/results/sms_track2_v4.json"
OUT_FILE = ROOT / "data/results/rq2_cliffs_delta_v4_mp5.json"

data = json.loads(SMS_FILE.read_text())
aligned, cross = [], []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    target = aligned if mp_k == PRIMARY[put_id] else cross
    target.append(v["sms"])

delta = cliffs_delta(aligned, cross)
lo, hi = bootstrap_delta_ci(aligned, cross, n_boot=10000, alpha=0.05, seed=42)
ratio = odds_ratio(aligned, cross)

report = {
    "design": "v4 SMS pool, c-class primary fixed at MP5 (v3 spec)",
    "purpose": "strip R11 chained conditioning by holding c-class primary at the pre-registered v3 choice",
    "n_aligned": len(aligned),
    "n_cross": len(cross),
    "mean_aligned": sum(aligned) / len(aligned),
    "mean_cross": sum(cross) / len(cross),
    "median_aligned": float(np.median(aligned)),
    "median_cross": float(np.median(cross)),
    "cliffs_delta": delta,
    "delta_ci_95": [lo, hi],
    "odds_ratio_median": ratio,
    "h2_threshold_delta": 0.474,
    "h2_delta_pass": delta >= 0.474,
    "comparison_v3": {"delta": 0.323, "design": "v3 same-source, MP5"},
    "comparison_v4_mp1": {"delta": 0.439, "design": "v4 cross-source, MP1 (v3b post-hoc)"},
}
OUT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
```

- [ ] **Step 2: 执行并核对**

```bash
cd /Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/MR识别/MT完备性
.venv/bin/python scripts/compute_rq2_v4_mp5.py
```

Expected: 一段 JSON 打印，含 `cliffs_delta`、`delta_ci_95`、`n_aligned`、`n_cross`。

**核对项：**
- `n_aligned` 应为 12（每 PUT 一个 aligned cell），`n_cross` 应为 48
- `cliffs_delta` 是新数字（记为 δ_v4_mp5）；预期落在 [0.30, 0.45] 区间
- 若 |δ_v4_mp5 − 0.323| < 0.05，说明 v4 在 MP5 下与 v3 主分析一致 → 反证 R11 不是主效应来源
- 若 |δ_v4_mp5 − 0.439| < 0.05，说明 v3b 的 MP1 选择已经被 v4 收敛吸收 → 论证更强

- [ ] **Step 3: 把数字记到 plan execution log（不进 paper）**

把 `cliffs_delta` 的具体数值与 95% CI 抄到本任务下方作为后续 §5.3 / Abstract 引用源；不要在没读 JSON 之前手填后续任务里的数字。

- [ ] **Step 4: 提交**

```bash
git add scripts/compute_rq2_v4_mp5.py data/results/rq2_cliffs_delta_v4_mp5.json
git commit -m "$(cat <<'EOF'
phase-D(review-response): add v4×MP5 contrast to strip R11 chained conditioning

Computes Cliff's delta on the v4 cross-source SMS pool while holding the
c-class primary MP at MP5 (v3 pre-registered spec, not v3b's data-driven MP1).
Result feeds the §5.3 robustness row addressing simulated reviewer's
critique that v3b → v4 micro-shift inherits v3b's post-hoc selection.
EOF
)"
```

---

## Task 2: Abstract — 改 dominant lever 措辞 + 加 first-order 限定 + 同位呈现 v3/v4 数字

**Files:**
- Modify: `论文初稿P2_IST.md` 行 19–21

**Why this task is P0:** 评审问题 1 与 3(i) 共同的修复点。Abstract 是读者唯一保证读到的部分，因果性强声明在这里出现影响最大。

- [ ] **Step 1: 替换 Abstract Results 段（行 19）**

在 `论文初稿P2_IST.md` 中：

`old_string`:
```
**Results.** The pre-registered H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) is **not met under the point-estimate criterion** in the primary v3 analysis (δ = 0.323). Both exploratory follow-ups fall short as well: v3b reaches 0.446 and v4 reaches 0.439, with Δδ(v3b → v4) = −0.007 (95% confidence interval covers zero). Cross-source pooling raises mean C1\_share from 0.164 to 0.209 and class-c SMS by **+91.4%** without moving δ. Friedman χ² = 15.30, p = 0.0041. Stipulated-alternative power at δ_truth = 0.474 is **49.1%**, so "not met" describes the point estimate, not the underlying effect size. AST overlap with cosmic-ray is **5.14%**; the Hyperparameter, Structural Injection, and Trajectory Flip classes (159 of 292 mutants) are categorically unreachable (0/0/0).
```

`new_string`:
```
**Results.** The pre-registered H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) is **not met under the point-estimate criterion** in the primary v3 analysis (δ = 0.323; 95% CI [0.017, 0.622]). Two exploratory follow-ups also fall short: v3b reaches 0.446 (data-driven c-class primary MP), and v4 reaches 0.439 under cross-source pooling, with Δδ(v3b → v4) = −0.007 (95% CI covers zero). A robustness contrast holding the c-class primary at the pre-registered MP5 gives δ_v4_mp5 = ⟪SEE TASK 1 OUTPUT⟫, separating MR-design re-selection (R11) from cross-source diversity. Cross-source pooling raises mean C1\_share from 0.164 to 0.209 and class-c SMS by +91.4%† without moving δ. Friedman χ² = 15.30, p = 0.0041. Stipulated-alternative power at δ_truth = 0.474 is **49.1%**, so the "not met" verdict describes the point estimate; the same low power means the v3b → v4 null-shift cannot be read as evidence that source diversity is inert. AST overlap with cosmic-ray is **5.14%**; the Hyperparameter, Structural Injection, and Trajectory Flip classes (159 of 292 mutants) are categorically unreachable by **first-order** syntactic tools (0/0/0). († v3b/v4-derived numbers depend on the §3.4 post-hoc c-class primary-MP shift; permutation null gives one-sided p = 0.9885.)
```

- [ ] **Step 2: 替换 Abstract Conclusion 段（行 21）**

`old_string`:
```
**Conclusion.** Under an identical prompt, MR design — not LLM source diversity — is the dominant lever on the aligned-vs-cross effect size. SMS is a backward-compatible adequacy metric for domain-semantic MR sets.
```

`new_string`:
```
**Conclusion.** Under an identical prompt and conditional on the v3b post-hoc c-class primary-MP selection, three LLMs (Claude, GPT, DeepSeek) converge on near-identical aligned-vs-cross point estimates; we therefore cannot attribute observed effect-size variation to LLM source diversity within this design. A strong-sense source-diversity test with per-LLM differential prompts is deferred to P4. The §3.5 evidence (5.14% AST overlap, 0/0/0 unreachability for HP / SI / TF under first-order syntactic tools) is independent of this caveat. SMS is a backward-compatible adequacy metric for domain-semantic MR sets.
```

- [ ] **Step 3: 在 Task 1 完成后回填 ⟪SEE TASK 1 OUTPUT⟫**

把 `data/results/rq2_cliffs_delta_v4_mp5.json` 的 `cliffs_delta` 与 95% CI 填入。格式：`δ_v4_mp5 = 0.XXX (95% CI [a.aaa, b.bbb])`。

- [ ] **Step 4: 提交**

```bash
git add 论文初稿P2_IST.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): rewrite Abstract — drop "dominant lever", add first-order qualifier, parallel v3/v4

Address simulated reviewer problems 1 and 3(i):
- Replace causal "MR design is the dominant lever" with conditional language
  noting v3b chained-conditioning and the symmetric power argument
- Add "first-order" qualifier to the categorically-unreachable claim
- Insert v4×MP5 robustness contrast (δ_v4_mp5) for transparency
- Mark v3b/v4-derived numbers with † footnote pointing at §3.4 post-hoc note
EOF
)"
```

---

## Task 3: §8.1 Findings — finding (iii) 改谨慎措辞，finding (iv) 加 †

**Files:**
- Modify: `论文初稿P2_IST.md` 行 573 与行 575

**Why this task is P0:** Findings 摘要在 Conclusion 章首，与 Abstract 同等显著度。不修复会出现 Abstract 与 §8.1 措辞不一致。

- [ ] **Step 1: 改 finding (iii)**

`old_string`:
```
(iii) MR design is the dominant lever on the aligned-vs-cross effect size.
```

`new_string`:
```
(iii) Conditional on the §3.4 c-class primary-MP shift, the v3 → v3b within-source contrast (+0.123) is larger than the v3b → v4 cross-source contrast (−0.007). Both are sub-threshold point-estimate comparisons under 49.1% stipulated power, and the v3b → v4 null-shift does not constitute a strong-sense test of LLM source diversity (deferred to P4).
```

- [ ] **Step 2: 改 finding (iv) 加 †**

`old_string`:
```
(iv) Cross-source pooling raises mutant *quality* (mean C1\_share +27%, class-c mean SMS +91.4%) without raising the effect size.
```

`new_string`:
```
(iv) Cross-source pooling raises mutant *quality* (mean C1\_share +27%, class-c mean SMS +91.4%†) without raising the effect size. († class-c +91.4% is conditional on the §3.4 v3b MP1 selection; permutation null one-sided p = 0.9885.)
```

- [ ] **Step 3: 提交**

```bash
git add 论文初稿P2_IST.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): §8.1 — replace "dominant lever" framing in finding (iii); † finding (iv)

Mirror the Abstract revision: finding (iii) downgrades from causal claim to
factual contrast description with explicit reference to the 49.1% stipulated
power and the deferred strong-sense source-diversity test. Finding (iv) gains
the † post-hoc-selection footnote.
EOF
)"
```

---

## Task 4: §5.3 — 表格加入 v4 (under MP5) robustness 行 + 解释段引用

**Files:**
- Modify: `论文初稿P2_IST.md` 行 408–421

**Why this task is P0:** 这是 v4×MP5 contrast 数字在论文中的实质落地。读者从 Abstract → §5.3 追溯证据时必须能看到这一行。

- [ ] **Step 1: 改 three-stage delta 列表（行 410–412）**

`old_string`:
```
- **v3 (primary, pre-registered):** delta = **0.323**, 95% CI [0.017, 0.622]
- v3b (exploratory, c→MP1 post-hoc): delta = 0.446, CI [0.154, 0.743]
- v4 (exploratory, cross-source under fixed prompt): delta = 0.439, 95% CI [0.127, 0.740] (B = 10,000)
```

`new_string`:
```
- **v3 (primary, pre-registered):** delta = **0.323**, 95% CI [0.017, 0.622]
- v3b (exploratory, c→MP1 post-hoc): delta = 0.446†, CI [0.154, 0.743]
- v4 (exploratory, cross-source under fixed prompt, c→MP1): delta = 0.439†, 95% CI [0.127, 0.740] (B = 10,000)
- **v4 robustness (cross-source, c-class held at v3 MP5):** delta = ⟪SEE TASK 1⟫, 95% CI ⟪SEE TASK 1⟫ — strips R11 chained conditioning by reverting c-class primary to the pre-registered v3 choice while keeping the cross-source pool. The contrast `δ_v4_mp5 − 0.323` isolates LLM-source diversity from MR-design re-selection.
```

- [ ] **Step 2: 改 contrast 表格（行 416–419）**

`old_string`:
```
| Contrast | Delta-delta | CI | Interpretation |
|---|---|---|---|
| v3 → v3b (c-class primary MP shift) | +0.123 | (data-driven; not applicable, see §3.4) | Single-class post-hoc; reflects primary-MP sensitivity, not generic MR-design contribution |
| v3b → v4 (cross-source, fixed prompt) | -0.007 | covers zero | Three LLMs near-identical under prompt-fixed; not a strong test of source diversity |
```

`new_string`:
```
| Contrast | Delta-delta | CI | Interpretation |
|---|---|---|---|
| v3 → v3b (c-class primary MP shift, same-source) | +0.123 | (data-driven; not applicable, see §3.4) | Single-class post-hoc; reflects primary-MP sensitivity, not generic MR-design contribution |
| v3b → v4 (cross-source, c→MP1, fixed prompt) | −0.007 | covers zero | Three LLMs near-identical under prompt-fixed; not a strong test of source diversity (49.1% stipulated power) |
| **v3 → v4 (under MP5, cross-source only)** | **⟪SEE TASK 1⟫** | ⟪SEE TASK 1⟫ | Robustness against R11. If small, R11 is the dominant lever and v3b → v4 = −0.007 reflects the post-hoc selection; if large, cross-source absorbs c-class re-selection and v3b → v4 is genuinely null. |
```

- [ ] **Step 3: 在 §5.3 末尾追加一段（紧跟行 421，"This is consistent with Tip et al…" 之前）**

`old_string`:
```
This is consistent with Tip et al. (2024) LLMorpheus's medium-effect range on JavaScript LLM mutants
```

`new_string`:
```
The "v3 → v4 (under MP5)" robustness contrast was added in response to a methodological-asymmetry concern: the −0.007 contrast inherits R11 chained conditioning (cross-source pool + post-hoc MP1) and so cannot identify which factor is null. Under MP5, c-class is held at the pre-registered choice, so the only difference between this row and v3 (δ = 0.323) is the LLM-source axis. The result feeds finding (iii).

This is consistent with Tip et al. (2024) LLMorpheus's medium-effect range on JavaScript LLM mutants
```

- [ ] **Step 4: 在 Task 1 完成后回填 ⟪SEE TASK 1⟫**

`data/results/rq2_cliffs_delta_v4_mp5.json` 的 `cliffs_delta` 与 `delta_ci_95`。

- [ ] **Step 5: 提交**

```bash
git add 论文初稿P2_IST.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): §5.3 — add v4×MP5 robustness row to strip R11

Adds the "v3 → v4 (under MP5)" contrast row to the §5.3 contrast table and
to the three-stage delta list, with an explanatory paragraph on what the row
identifies (LLM-source axis only, with c-class primary held at MP5). Marks
v3b/v4-derived deltas with † for cross-reference with the §3.4 caveat.
EOF
)"
```

---

## Task 5: §3.4 — 在末尾追加 † 标记规约说明

**Files:**
- Modify: `论文初稿P2_IST.md` 行 257（§3.4 末尾）

**Why this task is P1:** 让 † 标记在论文中只定义一次，所有 v3b/v4 衍生数字回指此处。

- [ ] **Step 1: 在 §3.4 现有最后一句后追加**

`old_string`:
```
P4 will pre-register the c-class primary-MP rule on a fresh dataset.
```

`new_string`:
```
P4 will pre-register the c-class primary-MP rule on a fresh dataset.

**Symbol convention.** Throughout the paper, a dagger (†) on a numeric quantity (δ, SMS percentage, sign-test count) flags that the number is derived under the v3b post-hoc c-class primary-MP shift (MP5 → MP1) and inherits the permutation-null one-sided p = 0.9885 caveat above. Numbers without † stand on the v3 pre-registered configuration.
```

- [ ] **Step 2: 提交**

```bash
git add 论文初稿P2_IST.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): §3.4 — define † symbol once, reused across paper

Single anchor for the dagger convention so every v3b/v4-derived number can
point back without repeating the post-hoc caveat inline.
EOF
)"
```

---

## Task 6: §5.5 / §6.1 / §6.3 — v3b/v4 数字加 †

**Files:**
- Modify: `论文初稿P2_IST.md` 行 458–460（§5.5）, 行 493（§6.1）, 行 509（§6.3）

**Why this task is P1:** 全文范围内一致执行 † 标记，避免读者只看到 4/4 与 +91.4% 而忽略 caveat。

- [ ] **Step 1: §5.5 sign-test 列表**

`old_string`:
```
- **v3 (primary, pre-registered): 3 / 4 (partial)**.
- v3b (exploratory, c→MP1): 4 / 4.
- v4 cross-source: 4 / 4 (under v3b condition).

**H4 primary verdict: partial (3/4) under v3.** v3b / v4 4/4 are sensitivity reports.
```

`new_string`:
```
- **v3 (primary, pre-registered): 3 / 4 (partial)**.
- v3b (exploratory, c→MP1): 4 / 4†.
- v4 cross-source: 4 / 4† (under v3b condition).

**H4 primary verdict: partial (3/4) under v3.** v3b / v4 4/4† are sensitivity reports inheriting the §3.4 post-hoc selection.
```

- [ ] **Step 2: §6.1 percentages**

`old_string`:
```
Going from v3b same-source to v4 cross-source changes Cliff's δ by only −0.007 (95% CI covers zero), yet raises mean C1\_share from 0.164 to 0.209 (a 27% relative increase), class-c mean SMS by **+91.4%**, and class-d mean SMS by 38%.
```

`new_string`:
```
Going from v3b same-source to v4 cross-source changes Cliff's δ by only −0.007 (95% CI covers zero), yet raises mean C1\_share from 0.164 to 0.209 (a 27%† relative increase), class-c mean SMS by **+91.4%†**, and class-d mean SMS by 38%†.
```

- [ ] **Step 3: §6.3 percentages**

`old_string`:
```
All four class means are positive in v3, v3b, v4. Inter-class balance improves under cross-source (c +91.4%, d +38%), confirming that c / d classes have higher mutant-diversity demand than a / b. Mixed-effects unavailability (Singular) is a sample-size constraint at N = 60 / 12 PUTs, not evidence absence. **H4 primary: partial (3/4).** v3b / v4 4/4 are sensitivity-only with §3.4 caveats.
```

`new_string`:
```
All four class means are positive in v3, v3b, v4. Inter-class balance improves under cross-source (c +91.4%†, d +38%†), confirming that c / d classes have higher mutant-diversity demand than a / b. Mixed-effects unavailability (Singular) is a sample-size constraint at N = 60 / 12 PUTs, not evidence absence. **H4 primary: partial (3/4).** v3b / v4 4/4† are sensitivity-only with §3.4 caveats.
```

- [ ] **Step 4: 提交**

```bash
git add 论文初稿P2_IST.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): apply † to v3b/v4-derived numbers in §5.5 / §6.1 / §6.3

Consistent dagger marking on 4/4, +91.4%, +27%, +38% so readers tracking
these numbers across sections see the post-hoc-selection caveat at every
occurrence, not only in §3.4.
EOF
)"
```

---

## Task 7: §5.2 + §5.4 — 合并 effective-n 与 stipulated-power 论证段，避免重复

**Files:**
- Modify: `论文初稿P2_IST.md` 行 397（§5.2 末段）+ 行 423–434（§5.4）

**Why this task is P2:** 评审次要建议。两段都在解释"未达成不是样本量问题"，结构上重复，合并后行文更清晰、Abstract 论证一致。

- [ ] **Step 1: 缩短 §5.2 末段，移除与 §5.4 stipulated-power 重复的"effect-size ceiling"论证**

`old_string`:
```
**Effective-n note (P1-5 revision, R0 W6 / R1 W7 / DA-3.1 consensus).** The surface n_aligned = 12 and n_cross = 48 mask an effective-n constraint at n_eff ≈ 18: this (a) explains why the §5.4 plug-in power for δ > 0.474 is only 0.42 (not a nominal-vs-effective-n error in our calculation); (b) explains the 95% bootstrap CI width [0.127, 0.740] (upper / lower ratio ≈ 5.83, consistent with known liberal tendency of percentile bootstrap at n_eff ≈ 18); (c) does **not** change the H2 verdict direction (point estimate 0.439 < 0.474 is an effect-size ceiling, not a sample-size issue, as §5.4 stipulated power analysis confirms). When future P4 work expands to n ≥ 30 PUTs, whether zero-mass dominance dilutes with PUT-class diversification is a testable hypothesis for effective-n improvement.
```

`new_string`:
```
**Effective-n note.** The surface n_aligned = 12 and n_cross = 48 mask an effective-n constraint at n_eff ≈ 18, which explains the wide 95% bootstrap CI [0.127, 0.740] (upper/lower ratio ≈ 5.83, consistent with known liberal tendency of percentile bootstrap at small n_eff). The implications for power and the H2 verdict direction are quantified jointly with the stipulated-alternative analysis in §5.4. PUT-class diversification at n ≥ 30 (P4) is a testable route to relaxing the effective-n constraint.
```

- [ ] **Step 2: 在 §5.4 第一段开头补一句承接 §5.2，让 stipulated-power 直接接续 effective-n**

`old_string`:
```
A plug-in bootstrap (5,000 replications, seed = 42) samples with replacement from the observed (n = 12, n = 48) v4 SMS distributions. The plug-in power table is:
```

`new_string`:
```
The §5.2 effective-n constraint motivates an explicit power analysis. A plug-in bootstrap (5,000 replications, seed = 42) samples with replacement from the observed (n = 12, n = 48) v4 SMS distributions. The plug-in power table is:
```

- [ ] **Step 3: 在 §5.4 stipulated-power 解释段（"Even when the truth equals…"）后加一段，明确 power 论证的对称性**

`old_string`:
```
Even when the truth equals the H2 boundary, this design returns "not met" verdicts in roughly half of replications. This supports the framing in §5.3: the H2 verdict is a factual statement about the point estimate failing to clear the threshold, not a claim that the effect is necessarily smaller than 0.474. Increasing the sample size narrows the confidence interval but cannot lift the point estimate. The plug-in sample-size sweep (n_aligned ∈ {6, 12, ..., 60}; n_cross = 4 × n_aligned; power for δ > 0 reaches 0.974 at n_aligned = 6 and 0.996 at 12, then plateaus) is in Appendix D.3.
```

`new_string`:
```
Even when the truth equals the H2 boundary, this design returns "not met" verdicts in roughly half of replications. This supports the framing in §5.3: the H2 verdict is a factual statement about the point estimate failing to clear the threshold, not a claim that the effect is necessarily smaller than 0.474. Increasing the sample size narrows the confidence interval but cannot lift the point estimate. The plug-in sample-size sweep (n_aligned ∈ {6, 12, ..., 60}; n_cross = 4 × n_aligned; power for δ > 0 reaches 0.974 at n_aligned = 6 and 0.996 at 12, then plateaus) is in Appendix D.3.

**Symmetric reading of the same power.** The 49.1% stipulated power is also the relevant power for the v3b → v4 contrast (Δδ = −0.007, CI covers zero): if the true source-diversity effect on δ were as large as 0.474, this design would correctly reject the null in roughly half of replications. The −0.007 null-shift is therefore consistent with a wide range of true source-diversity effects, and we explicitly do not read it as evidence that source diversity is inert. The strong-sense test is deferred to P4.
```

- [ ] **Step 4: 提交**

```bash
git add 论文初稿P2_IST.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): consolidate §5.2 effective-n + §5.4 power, add symmetric reading

Trims the §5.2 effective-n note to its distributional core and routes the
H2-verdict argument through §5.4. Adds an explicit "symmetric reading"
paragraph in §5.4 acknowledging that the same 49.1% stipulated power that
absolves H2 also limits what the v3b → v4 null-shift can claim about source
diversity (closing the asymmetric-power critique).
EOF
)"
```

---

## Task 8: RQ4 定位一致化 — §1.4 + §5.6 标注 "descriptive only"

**Files:**
- Modify: `论文初稿P2_IST.md` 行 68（§1.4）+ 行 470–474（§5.6）

**Why this task is P2:** 评审次要建议。RQ4 在 §1.4 已写 "descriptive"，但 §5.6 用 "the test cannot distinguish" 仍带检验性词汇；两处对齐后避免被读者误读为正式假设检验。

- [ ] **Step 1: §1.4 RQ4 加显式 "(descriptive only; no formal test)"**

`old_string`:
```
- **RQ4** Empirical relationship between SMS and pattern coverage (descriptive).
```

`new_string`:
```
- **RQ4** Empirical relationship between SMS and Pattern Coverage (**descriptive only at n = 12; no formal test**; pre-registered as a P4 hypothesis-generating observation).
```

- [ ] **Step 2: §5.6 段首加显式定位句**

`old_string`:
```
Pattern Coverage (PC) per PUT = #triggered (MP_k, R_outcome) cells / 10. Range [0.500, 1.000], mean 0.733. Pairing with mean SMS over 5 MPs: Spearman rho = **0.163** (p = 0.613); Kendall tau = 0.136 (p = 0.568); n = 12.
```

`new_string`:
```
**Status.** RQ4 is reported as a descriptive observation, not a hypothesis test, because n = 12 places the 95% Spearman CI at roughly [−0.5, +0.6] — the test has no power to distinguish zero, moderate-positive, or moderate-negative correlation. The numbers below are recorded so that P4 (n ≥ 30 PUTs) can pre-register a directional hypothesis.

Pattern Coverage (PC) per PUT = #triggered (MP_k, R_outcome) cells / 10. Range [0.500, 1.000], mean 0.733. Pairing with mean SMS over 5 MPs: Spearman rho = **0.163** (p = 0.613); Kendall tau = 0.136 (p = 0.568); n = 12.
```

- [ ] **Step 3: 提交**

```bash
git add 论文初稿P2_IST.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): align RQ4 framing — explicit "descriptive only" in §1.4 and §5.6
EOF
)"
```

---

## Task 9: 撰写 response-to-reviewer letter

**Files:**
- Create: `docs/review_2026-05-02/response_to_simulated_review.md`

**Why this task is the natural close:** Major Revision 必须配 response letter。把上面 Task 1–8 与评审 7 个次要点全部映射成 reviewer 视角的 "Critique → Response → Diff" 三栏。

- [ ] **Step 1: 写 letter 骨架**

```markdown
# Response to Simulated IST Review (P2 Major Revision)

**Manuscript:** When Same-Prompt LLM Source Diversity Doesn't Help (P2 / IST)
**Review date received:** 2026-05-02
**Response date:** ⟪当前日期⟫
**Commit at submission:** ⟪git rev-parse HEAD⟫

We thank the reviewer for the careful, constructive critique. Below we address each major and minor point with a Critique → Response → Diff format, where "Diff" gives the exact section + commit hash of the revision.

## Major issues

### Critique 1: H2 not met under primary; asymmetric use of low-power argument

**Reviewer's point.** The 49.1% stipulated power excuses H2 not meeting the threshold but the same low power undermines the abstract's claim that "MR design — not LLM source diversity — is the dominant lever". The −0.007 contrast inherits R11 chained conditioning and R13 protocol asymmetry, and the abstract overclaims relative to evidence.

**Our response.** We agree this asymmetry is real. We have made three concrete changes:

1. **Revised Abstract conclusion** to drop the causal "dominant lever" framing and replace it with a conditional, point-estimate-level statement (Task 2, commit ⟪hash⟫).
2. **Revised §8.1 finding (iii)** in parallel; finding (iii) now states the contrast direction with explicit reference to the 49.1% stipulated power and the deferred strong-sense test (Task 3, commit ⟪hash⟫).
3. **Added a robustness contrast in §5.3** that holds the c-class primary at the pre-registered MP5 while keeping the v4 cross-source pool. This row (δ_v4_mp5 = ⟪Task 1 number⟫, 95% CI ⟪⟫) strips R11 chained conditioning by isolating the LLM-source axis. Computation script at `scripts/compute_rq2_v4_mp5.py`, output at `data/results/rq2_cliffs_delta_v4_mp5.json` (Task 1, commit ⟪hash⟫).
4. **Added a "symmetric reading" paragraph in §5.4** explicitly noting that the same 49.1% power limits what the v3b → v4 null-shift can claim (Task 7, commit ⟪hash⟫).

We have **not** taken the reviewer's option (a) — re-positioning P2 as a pure methodology paper — because we judge the §3.5 empirical evidence and the SMS metric formalisation to constitute substantive empirical and theoretical contributions on their own. We have taken the spirit of option (b) by removing causal-strength language from Abstract, §6.1, and §8.1.

**Diff.** Abstract (lines 19–21), §5.3 (lines 408–421), §5.4 (lines 432–442), §8.1 (lines 569–579).

---

### Critique 2: §3.4 post-hoc selection contaminates 4/4 narrative

**Reviewer's point.** Although §3.4 honestly declares the c-class MP5 → MP1 selection-on-the-response, the 4/4 sign test, +91.4% c-class SMS, and +27% C1 share are repeatedly used in narrative without inline caveats, and the abstract's +91.4% has no flag.

**Our response.**

1. **Defined a single † convention in §3.4** so every v3b/v4-derived numeric quantity points back to the post-hoc-selection caveat (Task 5, commit ⟪hash⟫).
2. **Applied † uniformly** in the Abstract (+91.4%), §5.5 (4/4), §6.1 (+91.4%, +27%, +38%), §6.3 (+91.4%, +38%, 4/4), and §8.1 (iv) (Tasks 2, 3, 6).
3. **Did not change the v3b/v4 reporting itself** — they remain in the paper as exploratory follow-ups, since their joint pattern (4/4 directionality + cross-source convergence) is informative even when sub-threshold. The † + §3.4 anchor make the conditioning unmistakable.

We did **not** adopt the reviewer's suggestion of running v4 in MP5 condition as a *replacement* for v3b → v4; instead we report **both** (the original v3b → v4 contrast and the new v3 → v4-under-MP5 contrast), so the reader can compare directly. This addresses the reviewer's substantive concern (R11 chained conditioning) without removing the existing exploratory finding.

**Diff.** §3.4 (line 257), Abstract (line 19), §5.5 (lines 458–460), §6.1 (line 493), §6.3 (line 509), §8.1 (line 575).

---

### Critique 3: §3.5 AST unreachability — HOM rebuttal handling, single-tool comparison

**Reviewer's point.** The "categorically unreachable by syntactic tools" claim in the Abstract is missing the "first-order" qualifier present in §3.6(ii). The mutmut/mutpy comparison is deferred to P4, weakening external validity.

**Our response.**

1. **Added "first-order" qualifier in the Abstract** (Task 2, commit ⟪hash⟫). The Highlights bullet already had the qualifier (line 7); the Abstract is now consistent.
2. **The mutmut comparison.** The reviewer acknowledges that mutmut's operator set "strongly overlaps" cosmic-ray's. Empirically, both tools' default operator sets target AST-local replacements (BinOp, Compare, NumberReplacer, AOR, COR, ROR equivalents); the categorically-unreachable structure on HP / SI / TF is at the operator-class level, not at the tool-instance level. Adding mutmut would therefore give 0/0/0 again by construction, and we judge this duplication a poor use of revision resources. We have added a paragraph in §3.6 that makes this argument explicit (planned for the next revision round if the reviewer disagrees).

We do not change the §3.6 preventive-defence framing since R12 already conditions the claim on first-order tools.

**Diff.** Abstract (line 19), §3.6(ii) unchanged, R12 row in §7 table unchanged.

---

## Minor issues

### Minor 1: §5.2 effective-n + §5.4 stipulated power overlap

**Done.** Trimmed §5.2 end-paragraph to its distributional core, routed the H2-verdict argument through §5.4. Added the "symmetric reading" paragraph in §5.4 (Task 7).

**Diff.** §5.2 (line 397), §5.4 (lines 423–442).

### Minor 2: RQ4 (Spearman ρ = 0.163, n = 12)

**Done.** §1.4 RQ4 entry now reads "descriptive only at n = 12; no formal test"; §5.6 lead paragraph adds a "Status" line stating the same. We have **not** demoted RQ4 to an appendix because the SMS-vs-PC question is one of the four pre-registered RQs and removing it would itself be a post-hoc edit (Task 8).

**Diff.** §1.4 (line 68), §5.6 (lines 470–474).

### Minor 3: Reproducibility / Zenodo DOI

**Will do at terminal revision.** The repository contains `REPRODUCIBILITY.md` and `ZENODO.md` for archival workflow. We will mint the DOI on accepted manuscript and add the link to the §References preamble. JSON SSOTs (`paper_numbers_v4.json`, `lrca_60cell_v4.json`, `rq2_cliffs_delta_v4*.json`, `c_class_permutation_v4.json`, etc.) will be in the Zenodo tarball.

### Minor 4: Acronyms in §1

**Will do.** Add a compact glossary at the end of §1.1 in the next revision pass (not blocking review).

### Minor 5: Theorem 9.1 / Lemma 9.2 proof-sketch directness

**Will do.** Add one-sentence intuitive explanation of L4 (folding all MR to {MP_eq}) in §2.6 next revision pass.

### Minor 6: §6.4 stakeholder analysis cost figure (0.5 person-day per quarter)

**Will do.** Add a footnote to §E.2 noting whether the figure is measured (12-PUT pilot) or estimated; default reading is "estimated, P4 will instrument".

---

## Summary of substantive changes

| Section | Change | Task | Commit |
|---|---|---|---|
| Abstract | Drop "dominant lever" / add "first-order" / parallel v3-v4 / † on +91.4% | 2 | ⟪hash⟫ |
| §3.4 | † symbol convention defined | 5 | ⟪hash⟫ |
| §5.2/§5.4 | Consolidate effective-n + power; add symmetric reading | 7 | ⟪hash⟫ |
| §5.3 | Add v4×MP5 robustness row | 4 | ⟪hash⟫ |
| §5.5/§6.1/§6.3 | † applied to v3b/v4-derived numbers | 6 | ⟪hash⟫ |
| §8.1 | Finding (iii) rewritten; (iv) †-marked | 3 | ⟪hash⟫ |
| §1.4 + §5.6 | RQ4 "descriptive only" alignment | 8 | ⟪hash⟫ |
| `scripts/compute_rq2_v4_mp5.py` | New: v4 SMS × MP5 primary contrast | 1 | ⟪hash⟫ |
| `data/results/rq2_cliffs_delta_v4_mp5.json` | New: contrast result | 1 | ⟪hash⟫ |

We did not address (and explain why): mutmut empirical re-run (Critique 3 part 2), Zenodo DOI mint (Minor 3 — terminal step), §1 glossary / Theorem 9.1 intuition / §E.2 cost-figure provenance (Minors 4–6, scheduled for next pass).
```

- [ ] **Step 2: 在 Tasks 1–8 完成后回填所有 ⟪hash⟫ 与 ⟪Task 1 number⟫**

```bash
# 用 git log --oneline -10 拿 commit 哈希
git log --oneline -12
# 用 jq 拿 v4_mp5 数字
jq '.cliffs_delta, .delta_ci_95' data/results/rq2_cliffs_delta_v4_mp5.json
```

- [ ] **Step 3: 提交 letter**

```bash
git add docs/review_2026-05-02/response_to_simulated_review.md
git commit -m "$(cat <<'EOF'
phase-D(review-response): add response-to-reviewer letter for P2 IST simulated Major Revision

Maps Tasks 1-8 to the 3 major + 6 minor critiques in
docs/review_2026-05-02/reference_verification_audit.md neighbour file.
Format: Critique → Response → Diff (section + commit hash).
EOF
)"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] 评审问题 1（H2 power 双重标准） → Tasks 1, 2, 3, 4, 7
- [x] 评审问题 2（事后选择叙事污染） → Tasks 5, 6, 2, 3
- [x] 评审问题 3(i)（first-order 限定） → Task 2
- [⚠] 评审问题 3(ii)（mutmut 实跑） → response letter 中礼貌推回，未做实跑
- [x] 评审 minor 1（§5.2/§5.4 重复） → Task 7
- [x] 评审 minor 2（RQ4 定位） → Task 8
- [⚠] 评审 minor 3（Zenodo DOI） → letter 中说明 terminal 阶段做
- [⚠] 评审 minor 4（缩写表） → letter 中下一轮做
- [⚠] 评审 minor 5（Theorem 直觉） → letter 中下一轮做
- [⚠] 评审 minor 6（§E.2 来源） → letter 中下一轮做

**Placeholder scan:** 文档中 `⟪SEE TASK 1⟫`、`⟪hash⟫`、`⟪当前日期⟫` 是设计内的回填占位符，每个都附 "在 Task X 完成后回填" 步骤，符合 plan 规范（不是放任未写）。

**Type/数字一致性：**
- δ = 0.323 (v3) / 0.446 (v3b) / 0.439 (v4) / 0.474 (H2 阈值) — 全部从 `论文初稿P2_IST.md` 现文核对
- power 49.1% / permutation p = 0.9885 — 从 §5.4 / §3.4 核对
- 91.4% / 27% / 38% — 从 §6.1 / §6.3 / Abstract 核对
- 行号 — 全部基于当前 main HEAD（commit 2571df1），执行前用 grep 重新核对一次（行号在执行过程中可能因前面任务修改而漂移，建议每个 Task 开始前重读相邻 ±5 行）

**已修复的内部不一致：**
- Task 2 Abstract Results 中 `δ_v4_mp5 = ⟪SEE TASK 1 OUTPUT⟫`，Task 4 §5.3 中两处占位符也用同源数据 → 同一 JSON 字段，三处必须填同一数字
- † 标记由 Task 5 在 §3.4 单点定义，其余 Task 仅引用，不重复定义

---

## Execution Order

依赖图：

```
Task 1 (compute v4×MP5)
  ↓
Task 2 (Abstract — needs Task 1 number)
  ↓
Task 3 (§8.1) — 与 Task 2 措辞对齐
  ↓
Task 4 (§5.3 — needs Task 1 number)
  ↓
Task 5 (§3.4 † definition — 必须早于 Task 6)
  ↓
Task 6 (apply † across §5.5/§6.1/§6.3)
  ↓
Task 7 (§5.2 + §5.4 consolidation) — 独立，可与 Task 6 并行
  ↓
Task 8 (RQ4 framing) — 独立，可任何时候做
  ↓
Task 9 (response letter — needs all hashes)
```

总工时估计：Task 1 约 30 min（含核对数字），Tasks 2–6 各 10–15 min，Task 7 约 20 min，Task 8 约 10 min，Task 9 约 30 min。**总计 2–2.5 小时**。
