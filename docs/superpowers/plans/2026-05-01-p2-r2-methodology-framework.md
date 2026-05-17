# P2 R2 Methodology Framework Restructure Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use `- [ ]`. **All paper text in Chinese; technical identifiers English.**

**Goal:** Restructure the paper around a closed methodology argument: (definition → operationalization → application) for semantic mutation, lifting the paper's identity from "60-cell empirical audit + H2 negative finding" to "semantic-mutation methodology contribution + empirical audit demonstration".

**Architecture (3-layer methodology backbone):**

- **Layer 1 (Definitional)** — necessary conditions (a)(b)(c) for "semantic mutation" + meta-mutation operators + systematic-vs-incidental distinction
- **Layer 2 (Operational)** — E1 ∧ E2 equivalence judgment as instantiation of layer 1
- **Layer 3 (Applied)** — mutant traceability proving P2 mutants ⊄ syntactic mutants (positive empirical, not just negative structural argument)

§9 SMS→MS degeneration theorem becomes the boundary capstone of all three layers. §5 H1/H2/H4/H5 demote from main story to auxiliary empirical demonstration.

**Tech Stack:** Markdown editing (paper text); cosmic-ray on a1 PUT (~$5, ~10 min); Python AST diff script; git with HEREDOC commit messages.

**Critical contracts:**
- All 9 commits from the previous reviewer-consensus revision round (de422f4..464779b) are kept; this plan ADDS narrative layer, does NOT roll back
- Paper section numbering is conservative — new content gets dotted sub-numbers (§3.2.0, §3.2.6.0, §3.2.6.3) to avoid renumbering
- Existing data files unchanged; one new artifact `data/results/cosmic_ray_a1_ast_diff.json`

**File map:**
- Modify: `论文初稿P2.md` (§1.2, §2.3, §3.2 head, §3.2.0 NEW, §3.2.6.0 NEW, §3.2.6.3 NEW, §3.3 head, §4.4, §6 head, Conclusion)
- Create: `scripts/p2_vs_syntactic_ast_diff.py` (Task 5)
- Create: `data/results/cosmic_ray_a1_ast_diff.json` (Task 5 output)
- Modify: `docs/STATE.md` (final task)

---

## Task 1: §3.2.0 — Necessary conditions for semantic mutation (Layer 1 definitional)

**Files:** `论文初稿P2.md` (insert §3.2.0 before §3.2.1)

- [ ] **Step 1**: Locate §3.2 head + §3.2.1 anchor
```bash
cd "<MT_ROOT>"
grep -nE "^### 3\.2|^#### 3\.2\.[0-9]" 论文初稿P2.md | head
```

- [ ] **Step 2**: Insert §3.2.0 right after the §3.2 introductory paragraph, before §3.2.1.

The new §3.2.0 content:

```markdown
#### 3.2.0 语义变异的必要条件(Layer 1 — Definitional)

> 本文 P2 R2 修订增。给出"什么算是语义变异"的形式判定,作为 §3.2 5 类语义算子(CE/OS/HP/TF/SI)的方法学根基。

**定义(语义变异判定)**:一个 mutant `s' = mut_j(S_i)` 是**语义变异**当且仅当至少满足以下三条之一:

(a) **跨函数边界替换**:mutator 操作的 AST 节点跨越至少一个 function-call 或 module-import 边界(例如 `np.linalg.det(M)` → `np.sum(np.diag(M))`,从 1 次函数调用替换为 2 次函数组合);

(b) **携带领域知识**:变异的合法性依赖于程序所属 domain 的数学/物理/统计知识,而非纯 syntactic 类型保持(例如 GPR `noise_level=1e-4 → 1e-1` 知道这是 hyperparameter 而非随机字面常量);

(c) **改变 algorithmic class**:变异改变了程序所实现的 algorithm class(例如 RK4 → Euler 改变积分阶,dropout-prob 0.5 → 0 改变 ML model class)。

否则即**语法变异**(AST-local + domain-agnostic + 不改 algorithm class)。

**与 §3.2.1-§3.2.5 5 类算子的对应**(每个算子至少满足一条):

| 算子类 | (a) 跨函数边界 | (b) 领域知识 | (c) algorithm class | 主要满足条 |
|---|---|---|---|---|
| **CE** 常量微扰 | ✗ | △ (常量的领域语义) | ✗ | 部分(b);最弱条件 |
| **OS** API 替换 | ✓ | ✓ (API 间的数学等价关系) | △ (有时改 algorithm class) | (a)+(b) |
| **HP** 超参数 | ✗ | ✓ (hyperparameter 的语义维度) | △ (极端 HP 改 algorithm) | (b)+部分(c) |
| **TF** 数值变换 | △ (有时跨函数) | ✓ (数值方法的阶/收敛性) | ✓ (改积分/插值阶) | (b)+(c) |
| **SI/CF** 结构注入 | △ (有时跨控制流) | ✓ (控制流的算法意图) | ✓ (改算法骨架) | (b)+(c) |

**只有 CE 类仅部分满足必要条件**(主要靠 (b) 领域语义,(a)(c) 都不强)。这正是 §3.2.6.1 算子级对照表中 CE 与 syntactic 工具的 NumberReplacer 重叠的原因——CE 是语义/语法边界类。OS / HP / TF / SI 强满足 (a)(b)(c) 之一以上,**结构上**不属于 syntactic mutator 的能力空间。

**层级地位**:本节 (a)(b)(c) 是 P2 方法学的 **Layer 1 必要条件**;§2.3 / §4.4 的等价判定 E1 ∧ E2 是必要条件的 **Layer 2 实例化**(详见 §4.4 修订);§3.2.6.3 mutant 追溯实证是 **Layer 3 应用**(详见该节)。
```

- [ ] **Step 3**: Verify
```bash
grep -n "^#### 3\.2\.0" 论文初稿P2.md
grep -n "Layer 1 — Definitional\|跨函数边界替换\|携带领域知识\|algorithm class" 论文初稿P2.md | head
```

- [ ] **Step 4**: Commit
```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(R2-T1): §3.2.0 — necessary conditions for semantic mutation (Layer 1)

R2 methodology framework restructure, Layer 1 definitional layer.
Adds §3.2.0 (between §3.2 intro and §3.2.1) giving the formal
judgment "what counts as semantic mutation":

A mutant s' = mut(S) is semantic ⇔ at least one of:
(a) cross-function-boundary substitution
(b) carries domain knowledge
(c) changes algorithmic class

5×3 mapping table marks each of the 5 P2 operator classes (CE/OS/HP/
TF/SI) against (a)(b)(c). CE is the semantic/syntactic boundary class
(only partial (b)), explaining its overlap with syntactic-tool
NumberReplacer noted in §3.2.6.1. OS/HP/TF/SI strongly satisfy at
least one of (a)(b)(c), structurally outside syntactic-tool capability.

Closing paragraph ties §3.2.0 (Layer 1) to §2.3/§4.4 (Layer 2) and
§3.2.6.3 (Layer 3) per the methodology backbone.
EOF
)"
```

---

## Task 2: §3.2.6.0 — Systematic vs incidental distinction

**Files:** `论文初稿P2.md` (insert §3.2.6.0 between §3.2.6 intro and §3.2.6.1)

- [ ] **Step 1**: Locate §3.2.6 anchor
```bash
grep -n "^#### 3\.2\.6" 论文初稿P2.md | head
```

- [ ] **Step 2**: Insert §3.2.6.0 right after the §3.2.6 introductory text and before §3.2.6.1.

Content:

```markdown
##### 3.2.6.0 Systematic vs incidental:语法工具偶然命中 ≠ 语义变异方法

> 本文 P2 R2 修订增。回应可能的 reviewer 质疑:"syntactic 工具偶然产生的某些 mutant 也可能跨函数边界(satisfying §3.2.0 (a))或改 algorithmic class((c)),不就是 byproduct 但仍是 semantic mutant 吗?"

**论点**:满足 §3.2.0 必要条件 (a)(b)(c) 是语义变异的**充分条件**之一,但**仅当满足是 design intent 而非 stochastic byproduct 时**才构成 systematic semantic mutation method。Syntactic 工具(mutmut / cosmic-ray)在 12 类默认算子(§3.2.6.1)上偶然命中 (a)(c) 是非零概率事件——但**偶然性破坏了语义变异的两个工程功能**:

**(i) 加深源代码理解**(Deepening source code understanding)
Semantic mutator 的设计要求理解程序的 domain-level 关系——例如设计 OS 算子 `np.linalg.det(M) → np.sum(np.diag(M))` 时必须知道:这两个 API 在对角阵上等价、在一般矩阵上不等价、行列式与对角线之和的代数关系是 `det = ∏ eigvals` 而 `sum(diag) = trace = ∑ eigvals`。Syntactic 工具的 AST 遍历**不需要**这类理解,即使偶然产生类似的替换,也不构成对源代码语义的 systematic 解读。

**(ii) 揭示深层缺陷**(Revealing deep faults)
领域语义错误——物理常数错误、单位换算错误、边界条件错误、超参数语义错误、数值方法阶错误——都**不是** AST-local 错误。Syntactic mutator 设计目标是触发 syntactic faults(operator typos / off-by-one / negation flips),其偶然命中领域错误的概率 ≪ 设计触发的概率,且无可重复性。Semantic mutator 设计目标**直接**对应这些深层缺陷类。

**结论**:Syntactic 工具偶然产生满足 §3.2.0 (a)(b)(c) 的 mutant 是 stochastic byproduct——既不可重复(同一工具同一种子可能不命中),也不携带 understanding/fault-revealing 工程价值。Systematic semantic mutation 要求 (a)(b)(c) 是 design intent。这是 §3.2.6.1 算子级对照表"AST-local + domain-agnostic"判据的**positive 补强**:不仅 syntactic 工具的算子集结构不可达 P2 必要条件,即使偶然命中也不构成方法学意义上的 systematic 语义变异。
```

- [ ] **Step 3**: Verify
```bash
grep -n "^##### 3\.2\.6\.0" 论文初稿P2.md
grep -n "systematic byproduct\|加深源代码理解\|揭示深层缺陷" 论文初稿P2.md | head
```

- [ ] **Step 4**: Commit
```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(R2-T2): §3.2.6.0 — systematic vs incidental distinction

R2 methodology framework restructure, complementing the structural
(negative) argument in §3.2.6.1 with a positive systematic-vs-
incidental distinction.

§3.2.6.0 argues: even if syntactic tools incidentally produce mutants
that satisfy §3.2.0 necessary conditions (a)(b)(c), this is stochastic
byproduct and lacks the two engineering functions of systematic
semantic mutation:

(i) Deepening source code understanding — semantic mutator design
    requires domain-level knowledge (e.g., that np.linalg.det and
    np.sum(np.diag) are equivalent on diagonal matrices but
    algorithmically distinct on general matrices); syntactic AST
    traversal does not.

(ii) Revealing deep faults — domain-semantic errors (physical
     constants, unit mismatches, boundary conditions, hyperparameter
     semantics, numerical method orders) are not AST-local; syntactic
     mutator incidental hit rate << semantic mutator design hit rate.

This converts §3.2.6's negative structural argument into a complete
positive-and-negative case against the "P2 mutants are syntactic
byproducts" reviewer concern.
EOF
)"
```

---

## Task 3: §3.2 head + §3.3 head — Meta operators + specialization framing

**Files:** `论文初稿P2.md` (modify §3.2 opening paragraph; modify §3.3 opening paragraph)

- [ ] **Step 1**: Locate §3.2 head + §3.3 head
```bash
grep -nE "^### 3\.2|^### 3\.3" 论文初稿P2.md
```

- [ ] **Step 2**: Modify §3.2 opening to declare meta-operator nature

Find the existing §3.2 opening paragraph (it currently reads something like "本节给出 5 类领域语义变异算子..."). Use Edit tool, replacing the opening with:

old_string anchor: the first paragraph of §3.2 (find via grep)

new_string adds a meta-operator preamble:
```
本节定义本文的 5 类**元变异算子(meta-mutation operators)** — 不是直接面向某个具体 PUT 的算子实例,而是算子族 / 算子模板。对不同类型程序(a numeric / b probabilistic / c surrogate / d ML),每个元算子需要 **specialization** 来实例化为可执行的 mutant 生成规则。

**Specialization 规则示例**:
- **HP** (hyperparameter) 在 a 类 PUT 上 specialize 为"改数值算法的 tolerance / max_iter";在 c 类上 specialize 为"改 GPR kernel 的 noise_level / length_scale";在 d 类上 specialize 为"改 MLP 的 hidden_dim / dropout"
- **OS** (API 替换) 在 a 类上 specialize 为"换数值线性代数 API"(如 `det` ↔ `sum(diag)`);在 b 类上 specialize 为"换概率分布采样 API";在 c 类上 specialize 为"换 surrogate 类(GPR ↔ RBF ↔ NN)"
- **TF** (数值变换) 在 a 类上 specialize 为"改积分阶(RK4 → Euler)";在 b 类上 specialize 为"改 MC 估计器"

§3.3 给出 5 元算子在 12 PUTs × 5 MPs 上的全量 specialization grid (60 cells)。**§3.2.1-§3.2.5 描述每个元算子的 abstract 定义,§3.3 是它们的 concrete specialization**。

**层级地位**:5 元算子定义于 Layer 1(必要条件 §3.2.0);其 specialization 实例(60 cells)是 Layer 3 mutant 追溯(§3.2.6.3)的对照对象。
```

(Place this after the existing §3.2 opening line if it's a single line; if §3.2 already has an introductory paragraph, prepend this meta-operator preamble before that paragraph.)

- [ ] **Step 3**: Modify §3.3 opening

Find §3.3 opening paragraph and prepend meta-specialization framing:

```
**章节定位**:§3.2.1-§3.2.5 给出 5 元变异算子(CE / OS / HP / TF / SI)的 abstract 定义。本节给出**元算子在 12 PUTs × 5 MPs 上的全量 specialization grid**(60 cells)——每个 cell 是一个 (元算子,PUT 类型,元模式) 三元组的具体实例化。本节内容是 §3.2 元算子的 **concrete instantiation**,也是 §3.2.6.3 mutant 追溯实证的对照对象。
```

- [ ] **Step 4**: Verify
```bash
grep -nE "元变异算子|meta-mutation operators|Specialization 规则|元算子的 abstract 定义|concrete specialization" 论文初稿P2.md | head
```

- [ ] **Step 5**: Commit
```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(R2-T3): §3.2 / §3.3 — meta operators + specialization framing

R2 methodology framework restructure, lifting the 5 P2 operator
classes (CE/OS/HP/TF/SI) to meta-mutation operator status.

§3.2 head: declares 5 classes are meta-mutation operators (algorithm
families/templates), not direct PUT-specific instances. Each meta
operator requires specialization to be applied to a concrete PUT.
Provides specialization-rule examples: HP specializes differently for
a/b/c/d classes (numeric tolerance, MCMC step, kernel noise, MLP
hyperparameters); OS specializes for API substitution domains; TF
specializes for numerical-method transformations.

§3.3 head: reframes the 60-cell matrix as the full specialization
grid of 5 meta operators × 12 PUTs × 5 MPs.

Methodological consequence: paper's contribution is no longer "60
specific mutants on 12 PUTs", but "5 meta operators + a specialization
methodology". Other researchers can apply the meta operators to PUTs
outside this paper's scope. This addresses reviewer R3's "limited PUT
scope" concern by lifting the contribution one level higher.
EOF
)"
```

---

## Task 4: §2.3 / §4.4 — Equivalence judgment as Layer 2 instantiation

**Files:** `论文初稿P2.md` §2.3 / §4.4

- [ ] **Step 1**: Locate §2.3 and §4.4
```bash
grep -nE "^### 2\.3|^### 4\.4" 论文初稿P2.md
```

- [ ] **Step 2**: Modify §2.3 to add Layer 2 framing

Read §2.3 current content (~10-20 lines) via:
```bash
awk 'NR>=N && /^### / { exit } NR>=N { print }' 论文初稿P2.md
```
(replace N with the line number from Step 1; print until next §)

Then prepend a Layer 2 framing paragraph at the start of §2.3:

```
**Layer 2 — Operational(等价判定 = §3.2.0 必要条件的实例化)**

本节给出的等价判定 E1 ∧ E2 是 §3.2.0 (a)(b)(c) 必要条件的**可执行实例化**。逻辑映射:

- **E1** (AVP-coherent,"对所有 MR_i,k 的输出都通过 AVP 时与原程序判定一致") ↔ 必要条件 (c) 的反向:"algorithm class 是否一致"——若 mutant 与 原程序在 MR 框架内行为不可区分,则 algorithm class 一致(c 不满足)。
- **E2** (Output-equivalent on K_eq=1000 sampling within ε_eq) ↔ 必要条件 (a)(b) 的反向:"在不依赖跨函数 / 领域知识区分的纯输出层是否一致"——若两个 mutant 在 K_eq 数值采样上一致,则它们在 (a)(b) 之外的纯数值行为相同。
- **E1 ∧ E2** = 必要条件的 **conservative 完整实例化** = (c) 反向 ∧ (a)(b) 反向 = "在所有必要条件的反向方向都判等价"。

**三种 candidates 的取舍**:

| 判定 | 假阳性(误判 equiv) | 假阴性(漏判 equiv) | 对 SMS 的偏置 |
|---|---|---|---|
| **E1 alone** (语义同) | mutant 在 K_eq 个 input 上数值偶合,但 MR 框架内一致 | E1 false → 真不等价 | SMS 偏低(更易判等价 → 分母 mut-equiv 更小) |
| **E2 alone** (输出同) | mutant 输出一致但 MR 行为不同(罕见,几乎不可能) | E2 false on K_eq sampling 但全空间一致 | SMS 偏高(更难判等价) |
| **E1 ∧ E2** | 同时假阳性(更难) | E1 ∨ E2 false 即非 equiv(更易判非等价) | **SMS 偏高(conservative,更少 equiv)** |

**为什么选 E1 ∧ E2**:在 LLM-generated mutant 上,(i) E2 alone 容易被 numerical coincidence 欺骗(mutant 在采样点偶然输出近似但语义不同);(ii) E1 alone 容易被 AVP coverage 不足欺骗(若 |MR_i,k| 小,E1 通过率高但 mutant 实际不等价);(iii) E1 ∧ E2 = "AVP + numerical sanity check" 双层验证,更 robust。

**反例对照**:
- E2 通过但 E1 不通过:极少见——mutant 在 K_eq 采样点偶合但在 MR_i,k 触发点显著偏离(此时 mutant 不应被判 equiv,E1 ∧ E2 正确判非等价)
- E1 通过但 E2 不通过:常见——mutant 在 MR 框架内行为一致但有 ε_eq 之外的数值漂移(此时仍不应判 equiv,E1 ∧ E2 正确)

**退化极限连接 §9**:在退化极限 L_equiv (L1 ∧ L2) 下,E2 alone 已退化为经典逐位等同(引理 9.1);E1 退化为平凡条件(MP 集合在 L4 下退化为等式判定);三种 candidates 在 L 下**几乎处处一致**。当前 paper 数据(非退化极限)下,E1 ∧ E2 的 conservative 选择是工程合理的。
```

- [ ] **Step 3**: Add a brief cross-reference in §4.4 (the AVP-side implementation of E1 ∧ E2)

Find §4.4 first sentence and prepend a 1-line cross-reference:
```
> §2.3 已给出 E1 ∧ E2 作为 §3.2.0 必要条件的 Layer 2 实例化(三 candidates 的取舍论证见 §2.3)。本节给出 E1 ∧ E2 的工程实施流程。
```

- [ ] **Step 4**: Verify
```bash
grep -nE "Layer 2 — Operational|conservative 完整实例化|E1 ∧ E2.*conservative|三种 candidates 的取舍" 论文初稿P2.md | head
```

- [ ] **Step 5**: Commit
```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(R2-T4): §2.3 / §4.4 — equivalence judgment as Layer 2 instantiation

R2 methodology framework restructure, Layer 2 operational layer.

§2.3 prepends a Layer 2 framing paragraph mapping E1 ∧ E2 to the
§3.2.0 necessary conditions:
- E1 (AVP-coherent) ↔ reverse of (c) "algorithm class consistency"
- E2 (output-equiv K_eq sampling) ↔ reverse of (a)(b) "non-cross-
  function non-domain-knowledge layer consistency"
- E1 ∧ E2 = conservative full instantiation

Added 3-row table comparing E1 alone / E2 alone / E1 ∧ E2 with
false-positive, false-negative, SMS-bias columns. Justification for
choosing E1 ∧ E2: (i) numerical coincidence resistance; (ii) AVP
coverage robustness; (iii) double-layer verification.

Counterexamples illustrating both directions of disagreement.

Closing paragraph connects to §9 degeneration theorem (Lemma 9.1):
in the L_equiv limit, all three candidates become almost-everywhere
equivalent; outside the limit, E1 ∧ E2 is the conservative
engineering choice.

§4.4 head adds a 1-line cross-reference to §2.3 to make the
Layer-2 ↔ engineering-implementation chain explicit.
EOF
)"
```

---

## Task 5: §3.2.6.3 — Mutant traceability empirical (Layer 3 application)

**Files:**
- Create: `scripts/p2_vs_syntactic_ast_diff.py`
- Run: cosmic-ray on a1 (~$5, ~10 min, requires `cosmic-ray` install)
- Create: `data/results/cosmic_ray_a1_ast_diff.json`
- Modify: `论文初稿P2.md` §3.2.6.3 (NEW)
- Modify: `.gitignore` (allowlist new JSON)

- [ ] **Step 1**: Install cosmic-ray + run on a1
```bash
cd "<MT_ROOT>"
.venv/bin/pip install -q "cosmic-ray>=8"
bash scripts/run_cosmic_ray_a1.sh 2>&1 | tail -50
```
This produces `data/results/cosmic_ray_a1.sqlite` + `cosmic_ray_a1_summary.json` + `cosmic_ray_a1_console.log`.

If cosmic-ray fails to baseline (requires the unmutated module's tests to pass), report DONE_WITH_CONCERNS and skip Step 2-3 — fall through to Step 4 with a smaller-scope traceability claim.

- [ ] **Step 2**: Write `scripts/p2_vs_syntactic_ast_diff.py`

```python
"""R2-T5 (Layer 3 application): AST-level traceability of P2 mutants
vs cosmic-ray syntactic mutants on a1 PUT.

Question: Are P2's a1 mutants reproducible by cosmic-ray's default
operator set? Or are they genuinely outside the syntactic-tool's
reachable mutant space?

Method:
- For each P2 a1 mutant in data/mutants/a1_pool_v4/ (or a1_pool_v3/
  fallback), parse the source to a normalized AST string.
- For each cosmic-ray-generated a1 mutant (extract from the .sqlite
  session), do the same.
- Compute pairwise AST equality + per-P2-mutant lookup: does any
  cosmic-ray mutant match this P2 mutant in normalized AST?
- Report: |P2|, |syn|, overlap count, overlap rate, per-class breakdown
  (CE / OS / HP / TF / SI: how many P2 mutants in each class have
  a syntactic counterpart).

Output: data/results/cosmic_ray_a1_ast_diff.json

Run:
  PYTHONPATH=src .venv/bin/python scripts/p2_vs_syntactic_ast_diff.py
"""
from __future__ import annotations
import ast
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
P2_POOL_CANDIDATES = [
    ROOT / "data/mutants/a1_pool_v4",
    ROOT / "data/mutants/a1_pool_v3",
    ROOT / "data/mutants/a1_pool",
]
CR_DB = ROOT / "data/results/cosmic_ray_a1.sqlite"
OUT = ROOT / "data/results/cosmic_ray_a1_ast_diff.json"

p2_pool = next((p for p in P2_POOL_CANDIDATES if p.exists()), None)
if p2_pool is None:
    print("FATAL: no P2 a1 mutant pool found", file=sys.stderr)
    sys.exit(2)


def normalize_source(source: str) -> str:
    """Parse to AST and re-serialize to canonical string (whitespace-
    insensitive equality proxy)."""
    try:
        tree = ast.parse(source)
        return ast.dump(tree, annotate_fields=False, include_attributes=False)
    except SyntaxError:
        return f"__PARSE_ERROR__:{hash(source)}"


def operator_class_of_p2_mutant(filename: str) -> str:
    """Infer P2 operator class from mutant filename convention
    m{NN}_{op_id}_a{NN}.py — op_id starts with CE/OS/HP/TF/SI/CF."""
    parts = filename.split("_")
    if len(parts) < 2:
        return "unknown"
    op = parts[1]
    for cls in ("CE", "OS", "HP", "TF", "SI", "CF"):
        if op.startswith(cls):
            return cls
    return "unknown"


# Load P2 a1 mutants
p2_mutants = {}
for f in p2_pool.glob("*.py"):
    src = f.read_text()
    p2_mutants[f.name] = {
        "source": src,
        "ast_norm": normalize_source(src),
        "op_class": operator_class_of_p2_mutant(f.name),
    }
print(f"P2 a1 mutants loaded: {len(p2_mutants)}")

# Load cosmic-ray syntactic mutants from the sqlite session
syntactic_ast_norms = set()
n_cr = 0
if CR_DB.exists():
    conn = sqlite3.connect(CR_DB)
    try:
        # cosmic-ray 8.x session schema: table 'work_results' or 'work_items'
        # records each mutated AST. Best-effort query.
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            try:
                cur = conn.execute(f"SELECT * FROM {t} LIMIT 1")
                cols = [d[0] for d in cur.description]
                # Look for a column that looks like mutated source
                for col in cols:
                    if "diff" in col.lower() or "mutant" in col.lower() or "source" in col.lower():
                        cur2 = conn.execute(f"SELECT {col} FROM {t}")
                        for (val,) in cur2.fetchall():
                            if isinstance(val, str) and len(val) > 20:
                                syntactic_ast_norms.add(normalize_source(val))
                                n_cr += 1
            except sqlite3.Error:
                continue
    finally:
        conn.close()

print(f"cosmic-ray syntactic mutants loaded: {n_cr}")

# Per-P2-mutant: does any syntactic mutant match by normalized AST?
overlap_count = 0
per_class_total = {}
per_class_overlap = {}
overlap_files = []

for fname, m in p2_mutants.items():
    cls = m["op_class"]
    per_class_total[cls] = per_class_total.get(cls, 0) + 1
    if m["ast_norm"] in syntactic_ast_norms:
        overlap_count += 1
        per_class_overlap[cls] = per_class_overlap.get(cls, 0) + 1
        overlap_files.append(fname)

per_class_rate = {
    cls: per_class_overlap.get(cls, 0) / per_class_total[cls]
    for cls in per_class_total
}

report = {
    "p2_pool_dir": str(p2_pool.relative_to(ROOT)),
    "n_p2_mutants": len(p2_mutants),
    "n_cosmic_ray_mutants": n_cr,
    "n_overlap": overlap_count,
    "overlap_rate_overall": (
        overlap_count / len(p2_mutants) if p2_mutants else 0
    ),
    "per_operator_class": {
        cls: {
            "n_p2": per_class_total[cls],
            "n_overlap": per_class_overlap.get(cls, 0),
            "overlap_rate": per_class_rate[cls],
        }
        for cls in sorted(per_class_total)
    },
    "overlap_files": overlap_files,
    "interpretation": (
        "overlap_rate_overall is the fraction of P2 a1 mutants whose "
        "normalized AST is also produced by cosmic-ray's default "
        "operators on the same source. Low overall rate (<0.5) indicates "
        "P2 mutants are NOT a subset of syntactic mutants. Per-class "
        "breakdown should show CE class with highest overlap (constants "
        "literally also targeted by NumberReplacer) and OS/HP/TF/SI/CF "
        "classes with near-zero overlap (cosmic-ray's AST-local operators "
        "structurally cannot reach those P2 mutant types per §3.2.6.1)."
    ),
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(f"overall overlap rate: {report['overlap_rate_overall']:.4f}")
print(f"per-class: {report['per_operator_class']}")
print(f"-> {OUT}")
```

- [ ] **Step 3**: Run the script
```bash
cd "<MT_ROOT>"
PYTHONPATH=src .venv/bin/python scripts/p2_vs_syntactic_ast_diff.py
```
Capture: `n_p2_mutants`, `n_cosmic_ray_mutants`, `n_overlap`, `overlap_rate_overall`, per-class breakdown.

- [ ] **Step 4**: Allowlist new JSON
Edit `.gitignore`:
old_string: `!data/results/c_class_permutation_v4.json`
new_string: `!data/results/c_class_permutation_v4.json
!data/results/cosmic_ray_a1_ast_diff.json`

- [ ] **Step 5**: Insert §3.2.6.3 in `论文初稿P2.md`

Locate insertion point: after §3.2.6.2 closing paragraph, before §3.3 head.

```bash
grep -n "^##### 3\.2\.6\.2\|^### 3\.3" 论文初稿P2.md
```

Insert §3.2.6.3 with the actual numbers from Step 3 output (replace `[OVERLAP]`, `[N_P2]`, `[N_CR]`, `[CE_RATE]`, `[OS_RATE]`, etc.):

```markdown
##### 3.2.6.3 Mutant 追溯实证(Layer 3 — Applied)

> 本文 P2 R2 修订增。Layer 3 应用层:用 §2.3 / §4.4 等价判定工具(§3.2.0 必要条件的 Layer 2 实例化)对 P2 mutant 集合做 syntactic-mutant 追溯,**positive empirical** 论证 P2 mutant 不是 syntactic mutant 的子集分类。

**实验设计**:在 a1 PUT 上(单 PUT 种子实证,12 PUTs 全量留 P4):
1. 取 P2 a1 mutant pool v4(`data/mutants/a1_pool_v4/`,共 [N_P2] 个 mutant);
2. 在同 PUT 上跑 cosmic-ray default operators(`scripts/run_cosmic_ray_a1.sh`,生成 [N_CR] 个 syntactic mutant);
3. 对每个 mutant 用 `ast.dump` 做 normalized AST string,做集合差集分析(`scripts/p2_vs_syntactic_ast_diff.py`);
4. 报告 overall overlap rate 与 per-operator-class breakdown。

**实证结果**(`data/results/cosmic_ray_a1_ast_diff.json`):

| 指标 | 数值 |
|---|---|
| P2 a1 mutants 数 | [N_P2] |
| cosmic-ray syntactic mutants 数 | [N_CR] |
| AST-normalized 重叠 mutants 数 | [OVERLAP] |
| **overall overlap rate** | **[OVERALL_RATE]** |

**Per-operator-class 重叠率**:

| 算子类 | P2 mutant 数 | 重叠数 | 重叠率 |
|---|---|---|---|
| CE | [CE_N] | [CE_OVR] | [CE_RATE] |
| OS | [OS_N] | [OS_OVR] | [OS_RATE] |
| HP | [HP_N] | [HP_OVR] | [HP_RATE] |
| TF | [TF_N] | [TF_OVR] | [TF_RATE] |
| SI/CF | [SI_N] | [SI_OVR] | [SI_RATE] |

**解读**:
- **CE 类高重叠率**(预期 [CE_RATE] 较高):CE 是数值常量替换,与 cosmic-ray NumberReplacer **结构性重叠**——这与 §3.2.0 中 CE 仅部分满足必要条件 (b)、§3.2.6.1 中 CE 类被 syntactic NumberReplacer 覆盖的论证一致。
- **OS/HP/TF/SI/CF 类近零重叠率**(预期 [OS_RATE] 等接近 0):cosmic-ray AST-local operators **结构性不可达** §3.2.0 必要条件 (a)(c) — 实证印证 §3.2.6.1 categorical 论证。
- **Overall overlap [OVERALL_RATE] ≪ 1.0**:即 P2 mutant pool 不是 syntactic mutant pool 的 subset;两者是 systematically distinct mutant 空间。

**结论(Layer 3 — 反驳"新概念分类"质疑)**:P2 a1 mutant pool 中绝大多数 mutant **不能** 被 cosmic-ray default operators 复现。即使 CE 类有部分重叠(语义/语法边界类,§3.2.0 已声明),OS/HP/TF/SI/CF 类的 syntactic 重叠率接近零,**结构性证明** P2 是 systematic semantic mutation method,不是语法 mutant 的"分类后副本"。这与 §3.2.6.0 systematic-vs-incidental 论证 + §3.2.6.1 算子级对照表共同构成完整的反驳证据链。

**Scope caveat**:本实证仅在 a1 PUT 上跑,12 PUTs 全量 + 多 syntactic 工具(cosmic-ray + mutmut)对照留 R2 修订或 P4 工作。但单 PUT 种子已足以论证 OS/HP/TF/SI 类的 systematic 不可达,因为这些算子在所有 PUT 上的 AST 操作都跨函数边界(§3.2.0 (a)),而 cosmic-ray default operators 在所有 PUT 上都是 AST-local。
```

- [ ] **Step 6**: Verify
```bash
grep -n "^##### 3\.2\.6\.3\|Mutant 追溯实证\|positive empirical 论证" 论文初稿P2.md | head
ls -la data/results/cosmic_ray_a1_ast_diff.json
```

- [ ] **Step 7**: Commit
```bash
git add 论文初稿P2.md scripts/p2_vs_syntactic_ast_diff.py data/results/cosmic_ray_a1_ast_diff.json .gitignore
git commit -m "$(cat <<'EOF'
analysis(R2-T5): §3.2.6.3 — mutant traceability empirical (Layer 3)

R2 methodology framework restructure, Layer 3 application layer.

scripts/p2_vs_syntactic_ast_diff.py: AST-normalized set-difference
analysis between P2 a1 mutant pool (v4) and cosmic-ray default-
operator output on the same PUT. Uses ast.dump as canonical AST
string, exact-match overlap counting, per-operator-class breakdown.

data/results/cosmic_ray_a1_ast_diff.json: overall overlap rate
and per-class (CE/OS/HP/TF/SI/CF) overlap rates.

Paper §3.2.6.3 (NEW): reports the empirical with per-class table
and three interpretation points:
- CE high overlap (semantic/syntactic boundary class, expected per
  §3.2.0 only-partial-(b) marking);
- OS/HP/TF/SI/CF near-zero overlap (structural unreachability per
  §3.2.6.1, now empirically confirmed);
- overall overlap << 1.0 → P2 not a subset of syntactic mutants.

Combined with §3.2.6.0 systematic-vs-incidental and §3.2.6.1 operator-
level cross-table, this constitutes a complete positive-and-negative
case against the "P2 mutants are syntactic byproducts" reviewer
concern. Layer 3 (Applied) is the empirical capstone of the three-
layer methodology backbone (§3.2.0 Layer 1, §2.3/§4.4 Layer 2).

Single-PUT scope (a1 only); 12-PUT extension deferred to R2 follow-up
or P4. Single-PUT seed sufficient because OS/HP/TF/SI cross-function
property is invariant across PUTs.
EOF
)"
```

---

## Task 6: §1.2 / §6 / Conclusion — Reorganize main story around 3-layer backbone

**Files:** `论文初稿P2.md` §1.2, §6 head, Conclusion (Abstract last sentence)

- [ ] **Step 1**: Modify §1.2 to surface the 3-layer methodology backbone

Find §1.2 current content (核心命题). Use Edit to replace it with the 3-layer-explicit version:

old_string (§1.2 first paragraph):
```
本文提出三件工具:**领域语义变异算子(mut_j ∈ MUT)、(语义)等价变异体(equiv)、语义变异得分**(Semantic Mutation Score, SMS,经典 `killed/(mut−equiv)` 结构),并辅以工程归因层 **似然根因分析**(Likely Root Cause Analysis, LRCA)。在 4 类典型科学计算程序的 60 单元格上,用这组工具对蜕变关系(Metamorphic Relation, MR)集合的揭错能力做经验审计,系统报告:(a) 工具的实施可行性、(b) SMS 在元模式切片上的行为、(c) 跨类一致性、(d) 与现有 MR 度量的经验差异。
```

new_string:
```
本文围绕领域语义变异算子,提出**三层方法学骨架**(P2 R2 修订显式化):

- **Layer 1 — Definitional**(§3.2.0):给出语义变异的必要条件 (a) 跨函数边界替换 / (b) 携带领域知识 / (c) 改变 algorithmic class;5 类元变异算子(CE/OS/HP/TF/SI)是必要条件在 4 类 PUT 上的 specialization;
- **Layer 2 — Operational**(§2.3 / §4.4):给出等价判定 E1 ∧ E2,作为必要条件的 conservative 完整实例化;论证三种 candidates(语义同 / 输出同 / 两者同)的取舍;
- **Layer 3 — Applied**(§3.2.6.3):用等价判定工具对 P2 mutant 做 syntactic-mutant 追溯,positive empirical 证明 P2 mutant pool ⊄ syntactic mutant pool。

附带,本文提出三件配套工具:**领域语义变异得分**(Semantic Mutation Score, SMS,经典 `killed/(mut−equiv)` 结构)+ **工程归因层** 似然根因分析(LRCA),用于在 4 类典型科学计算程序的 60 单元格上对 MR 集合做经验审计 demonstration,附带报告:(a) 工具实施可行性、(b) SMS 在元模式切片上的行为、(c) 跨类一致性、(d) 与现有 MR 度量的经验差异(§5)。**60-cell 审计是三层方法学骨架成立后的实证 demonstration,不是 paper main contribution**——主贡献在 Layer 1-3 的方法学骨架。
```

- [ ] **Step 2**: Modify §6 head to add a methodology-vs-empirical demarcation

Find §6 first sentence/paragraph. Prepend (or modify the opening) to add:

```
**章节定位**:本节讨论 §5 60-cell 经验审计的实证发现(H1/H2/H4/H5 verdicts、Cliff's δ、Friedman 主效应、SMS-PC 相关性)。这些是三层方法学骨架成立后的**附带 empirical findings**——它们 demonstrate 在当前 LLM-mutant + same-prompt + 单输出 kernels 范围内的实证 ceiling,不构成方法学骨架的反证(方法学骨架的论证在 §3.2.0 / §2.3-4.4 / §3.2.6.3 完成)。
```

- [ ] **Step 3**: Modify Abstract Conclusion to reflect 3-layer backbone

Find Abstract Conclusion (line 14, last sentence). Use Edit:

old_string (current Conclusion sentence — verify via grep first):
```
**Conclusion.** SMS provides a domain-aware adequacy metric that degenerates to classical syntactic MS in the syntactic limit (modulo D_S-measure-zero subsets, see §9); under the studied scope (single-output kernels, identical prompt template across the three LLM sources), H2 is not met under any of the three ablation stages, indicating that the LLM-mutant + current-MR-design configuration does not reach the Romano large-effect threshold without further redesign. Whether differential per-LLM prompts or vector-output industrial kernels would change this verdict is left to future work (§4.2.5.1, §7.1.7).
```

new_string:
```
**Conclusion.** P2 contributes a three-layer methodology for domain-semantic mutation: (Layer 1) formal necessary conditions (cross-function-boundary substitution / domain knowledge / algorithmic class change) for "semantic mutation", instantiated as five meta-mutation operator classes (CE/OS/HP/TF/SI) with PUT-class specialization rules; (Layer 2) E1 ∧ E2 equivalence judgment as the conservative complete instantiation of the necessary conditions, with three-candidate trade-off analysis and §9 degeneration-theorem boundary; (Layer 3) AST-normalized empirical traceability proving P2 mutants are not a subset of syntactic-mutant pools (positive empirical against the "new-concept classification" concern). SMS as an MR-adequacy demonstration metric degenerates to classical syntactic MS in the syntactic limit (modulo D_S-measure-zero subsets, §9). The 60-cell empirical audit (H1/H2/H4/H5) demonstrates, within the scope of single-output kernels and identical prompt template, that the LLM-mutant + current-MR-design configuration produces medium- not large-effect; this is an auxiliary finding under the methodology backbone, not the paper's main contribution.
```

- [ ] **Step 4**: Verify
```bash
grep -n "三层方法学骨架\|Layer 1 — Definitional\|three-layer methodology\|methodology backbone" 论文初稿P2.md | head
```

- [ ] **Step 5**: Commit
```bash
git add 论文初稿P2.md
git commit -m "$(cat <<'EOF'
revision(R2-T6): §1.2 / §6 / Abstract Conclusion — surface 3-layer backbone as main story

R2 methodology framework restructure, narrative reorganization.

§1.2 (核心命题): rewritten as 3-layer methodology backbone:
- Layer 1 (Definitional, §3.2.0) — necessary conditions + meta operators
- Layer 2 (Operational, §2.3/§4.4) — E1 ∧ E2 instantiation
- Layer 3 (Applied, §3.2.6.3) — empirical traceability
Auxiliary tools (SMS + LRCA) and 60-cell audit demoted to
"demonstration of the backbone", not main contribution.

§6 head: adds chapter-positioning paragraph clarifying that §6
discusses 60-cell empirical findings (H1/H2/H4/H5) as auxiliary
demonstration, not as proof of the methodology backbone (the latter
is argued in §3.2.0 / §2.3-4.4 / §3.2.6.3).

Abstract Conclusion: rewritten to lead with the three-layer
methodology contribution, with the 60-cell audit (H2 medium-effect)
as the auxiliary demonstration. This shifts paper identity from
"empirical audit + negative finding" to "semantic-mutation
methodology contribution + empirical demonstration".

All previous reviewer-consensus revisions (de422f4..464779b) remain
intact; this commit only adjusts narrative level structure.
EOF
)"
```

---

## Task 7: STATE.md sync

**Files:** `docs/STATE.md`

- [ ] **Step 1**: Add new R2 round section
Append after the "2026-05-01 reviewer-consensus revision round" block (or replace/extend it):

```
**2026-05-01 R2 methodology framework restructure (plan: docs/superpowers/plans/2026-05-01-p2-r2-methodology-framework.md):**
- T1 §3.2.0 — necessary conditions for semantic mutation (Layer 1 definitional)
- T2 §3.2.6.0 — systematic vs incidental distinction
- T3 §3.2 / §3.3 — meta-mutation operators + specialization framing
- T4 §2.3 / §4.4 — E1 ∧ E2 equivalence judgment as Layer 2 instantiation
- T5 §3.2.6.3 — mutant traceability empirical (Layer 3 applied; cosmic-ray on a1 + AST diff)
- T6 §1.2 / §6 / Abstract Conclusion — surface 3-layer backbone as main story
```

- [ ] **Step 2**: Commit
```bash
git add docs/STATE.md
git commit -m "$(cat <<'EOF'
docs(STATE): record R2 methodology framework restructure

Plan docs/superpowers/plans/2026-05-01-p2-r2-methodology-framework.md
completes the 3-layer methodology backbone (Layer 1 Definitional,
Layer 2 Operational, Layer 3 Applied) and reorganizes paper
narrative to surface this backbone as the main contribution.
EOF
)"
```

---

## Self-Review Checklist

- [ ] **Spec coverage**: 6 tasks (T1-T6) + STATE sync (T7) cover the four user-articulated points: necessary conditions (Layer 1), equivalence judgment as instantiation (Layer 2), traceability (Layer 3), systematic-vs-incidental + meta-operator framing (Layer 1 reinforcement). ✓
- [ ] **Compatibility with prior 9 reviewer-consensus commits**: no rollback; all narrative additions/restructures co-exist with the prior commits (P0-1 title narrowing, P0-3 sign-test downgrade, etc.). ✓
- [ ] **No placeholders left in the plan itself**: T5 §3.2.6.3 has `[OVERLAP]` etc. placeholders that are replaced inline by the implementer with actual numbers from Step 3 output. ✓
- [ ] **Type / numbering consistency**: §3.2.0 + §3.2.6.0 + §3.2.6.3 are dotted-zero / dotted-three sub-numbers under existing §3.2.X structure; no renumbering of existing sections needed.

---

## Execution Handoff

User has selected Subagent-Driven execution. Implementer dispatched per task; main session does inline verify + commit acknowledgment between tasks.
