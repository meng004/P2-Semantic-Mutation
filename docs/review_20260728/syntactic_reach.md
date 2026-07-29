# EXP-STR constructive reach argument (R-10)

**Role.** Document-level substitute for a second syntactic-engine run. Locates the reachable set of default first-order AST-local editors (cosmic-ray measured; mutmut by public operator list) and argues why Hyperparameter (HP), Structural-Injection (SI), and Trajectory-Flip (TF) class edits lie outside that set. This supports a *reachability-boundary* claim, not a superiority claim.

**Scope limits (read first).** (i) Argument is about *default first-order AST-local* operators, not higher-order mutation (HOM) or custom operator plugins — **HOM is not refuted**. (ii) Empirical overlap below is v4 POOL-SEM only; v5 addendum is pending (`syntactic_overlap_v2.v5_addendum`). (iii) Toy `float→float` kernels; no industrial-tool universality claim.

---

## 1. Empirical anchor (cosmic-ray, measured)

Source: `data/results/cosmic_ray_12put_ast_diff.json` → packaged as `data/results/syntactic_overlap_v2.json`.

| Quantity | Value |
|---|---|
| Semantic pool (v4) | 292 |
| cosmic-ray default pool | 1,250 |
| AST-normalised exact overlap | **15 / 292 = 5.14%** |
| HP / SI / TF overlap | **0 / 0 / 0** |
| CE / OS / CF overlap | partial (5 / 7 / 3) |

Normaliser pin: `ast.dump(..., annotate_fields=False, include_attributes=False)` over post-diff sources (`scripts/p2_vs_syntactic_ast_diff_batch.py`).

---

## 2. cosmic-ray default operator families

Upstream listing (core plugin package):
https://github.com/sixty-north/cosmic-ray/tree/master/src/cosmic_ray/operators

| Family (module) | Edit class | AST-local? |
|---|---|---|
| `number_replacer` | numeric literal ± | yes — single `Num`/`Constant` |
| `binary_operator_replacement` | `+`/`-`/`*`/`/`/… swap | yes — single `BinOp.op` |
| `unary_operator_replacement` | `+`/`-`/`~`/`not` swap | yes — single `UnaryOp.op` |
| `comparison_operator_replacement` | `<`/`<=`/`==`/… swap | yes — single `Compare.op` |
| `boolean_replacer` | `True`↔`False`, `and`↔`or` | yes — constant / `BoolOp` |
| `break_continue` | `break`↔`continue` | yes — single stmt keyword |
| `exception_replacer` | exception type swap | yes — local name in `Raise`/`Except` |
| `keyword_replacer` | keyword constant swap | yes — local keyword node |
| `remove_decorator` | drop one decorator | yes — single decorator entry |
| `variable_inserter` / `variable_replacer` | local name insert/replace | yes — single `Name` site |
| `zero_iteration_for_loop` | force empty iteration | yes — local iterable rewrite |
| `no_op` | identity (control) | yes — trivial |

**Closure.** Every default family is a *first-order AST-local edit*: one node (or one narrowly scoped sibling rewrite) replaced by another of the same syntactic category, without requiring domain legality, cross-file consistency, or algorithmic-class change.

---

## 3. mutmut public operator list (not run)

Documentation (example mutations + pointer to full list):
https://mutmut.readthedocs.io/en/latest/index.html#example-mutations

Publicly documented examples:

| Example (docs) | Edit class | AST-local? |
|---|---|---|
| Integer literal `n → n+1` | constant tweak | yes |
| `<` → `<=` | comparison op | yes |
| `break` ↔ `continue` | keyword stmt | yes |

Docs state the full set lives in `node_mutation.py` and is designed to stay “as subtle as possible” — i.e., the same first-order local class as cosmic-ray. mutmut was **not executed** here (R-10); the list is used only as a constructive coverage argument that a second mainstream engine occupies the same edit class.

---

## 4. Mapping semantic families → reachability

| Semantic family | Typical edit | Inside first-order AST-local class? |
|---|---|---|
| **CE** (conservation erosion) | literal / coefficient tweak on a conserved site | **Sometimes** — when the site is a single numeric/binop node (explains partial CE overlap) |
| **OS** (operator substitution) | API/arithmetic substitution | **Sometimes** — when the substitution is a single `BinOp`/`Call` name swap (partial OS overlap) |
| **CF** (legacy) | control-flow keyword tweak | **Often** — overlaps `break_continue` / boolean class (highest per-family rate in v4) |
| **HP** (hyperparameter) | rtol, `C`, `length_scale`, `N_SAMPLES`, architecture knobs | **Outside as a class** — the *failure semantics* require a domain-legal numeric regime change (solver accuracy order, regularisation, sample budget). A blind `n→n+1` on a literal may hit a constant, but does not systematically enact the HP mechanism; observed HP overlap = 0 |
| **SI** (structural injection) | fidelity-tier / aggregation-structure change (e.g. AM→GM, solver-order tier) | **Outside** — cross-boundary structural rewrite of an algorithm tier, not a single-node op swap; observed SI overlap = 0 |
| **TF** (trajectory flip) | state-order / training-row / chain-segment reordering with phase semantics | **Outside** — multi-site or ordering-constraint edit whose legality depends on domain trajectory structure; observed TF overlap = 0 |

---

## 5. Reachability-boundary claim (engineering-precise)

1. Default cosmic-ray (measured) and mutmut (documented) operators are first-order AST-local edits.
2. On this 12-PUT v4 cohort, 94.86% of semantic mutants are AST-disjoint from the cosmic-ray pool; HP/SI/TF contribute zero overlaps.
3. Therefore HP/SI/TF-class edits — cross-boundary, domain-legality-dependent, or algorithmic-class-changing — lie outside the *default first-order AST-local* reachable set.
4. Residual threats (explicitly open): custom operator plugins; higher-order mutation (HOM); non-AST equivalence (two different ASTs, same behaviour); other engines not listed here.

**Non-claim.** This does not say “no syntactic tool can ever reach HP/SI/TF,” nor that semantic mutants are “better.” It pins a boundary for the default first-order class used as EXP-STR’s reference.
