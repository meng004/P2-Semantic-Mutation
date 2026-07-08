# Decision — NOETHER-aligned MR MetaPattern terminology and pre-submission check

Date: 2026-07-08 · Status: ADOPTED · Owner: Meng Li

## Background

The paper previously used a five-class semantic-mutation vocabulary
(`CE/OS/HP/TF/SI`) to describe semantic-effect mutants. After comparison
with the NOETHER manuscript, this is no longer the reader-facing
terminology. The paper should instead describe MR design and adequacy
using NOETHER's MetaPattern / operator-block vocabulary.

The conceptual decision from the discussion is:

1. Syntactic mutation and semantic mutation are different classification
   dimensions, not a subset/superset pair.
2. A concrete semantic-effect fault may be implemented as a small source
   edit, but its identity is determined by the certified semantic
   contract it violates, not by the textual patch shape.
3. The MR side of the paper should be expressed in terms of MR
   MetaPatterns and MR Families derived from NOETHER operator blocks.
4. `CE/OS/HP/TF/SI` are no longer MR MetaPatterns, semantic mutation
   operators, or reader-facing abbreviations in the paper. Existing
   `CE1/OS1/HP1/TF1/SI1` suffixes may remain only as historical internal
   campaign IDs in file names, logs, and reproducibility notes.

Authoritative terminology files:

- `docs/naming_convention.md`
- `docs/terminology_zh_en.md`

## Definitions

### MR MetaPattern

An MR MetaPattern is a NOETHER-aligned equivalence class of metamorphic
relations derived from an invariant of an operator block through
Translate. It is a structural relation family over program behavior, not
a mutation-operator class and not a code-edit category.

### Semantic-effect fault

A semantic-effect fault is an admitted mutant/fault instance whose
certificate states the intended semantic contract it stresses or
violates. It can be implemented by a syntactic edit, but it is classified
by its intended semantic effect.

### MR Family

An MR Family is the second-level specialization under an MR MetaPattern.
Use names of the form:

```text
<mp>.<family>
```

Examples:

- `inv.con`, `inv.eqv`
- `mono.shape`, `mono.stat`
- `conv.lim`, `conv.rate`, `conv.repr`
- `dyn.shape`, `dyn.traj`
- `cmp.err`, `cmp.order`
- `adj.self`, `adj.dual`
- `rev.time`
- `rel.rewrite`

## Approved abbreviations and definitions

| Abbrev. | English term | NOETHER block | Definition |
|---|---|---|---|
| `inv` | invariance / equivariance | `G` symmetry group | Inputs transformed by an admitted symmetry, conservation, or equivariance operation must produce outputs satisfying the corresponding isomorphism, conserved quantity, or equivariant response. Conservation is an instance of the `G` block, not a separate ninth block. |
| `mono` | monotonicity / order | `O_le` order | Inputs, parameters, or statistics ordered by a partial order must induce monotone, anti-monotone, linear, rank-preserving, or order-consistent outputs. |
| `conv` | convergence / limit | `L_lim` limit | Mesh size, step size, sample size, iteration count, tolerance, or asymptotic parameters approach a limit under an expected convergence or error-decay relation. |
| `dyn` | qualitative dynamics | `D_dyn` qualitative dynamics | Trajectory shape, extrema, overshoot, phase, monotone-then-saturating profile, or other qualitative dynamical structures are preserved under admitted perturbations. Ordinary trajectory-shape MRs belong here; reserve `rev` for true time reversal. |
| `cmp` | method comparison | `E_cmp` method comparison | Two numerical or algorithmic methods are related by a no-worse-than, error-bound, approximation-order, or method-quality partial order. |
| `adj` | self-adjoint / adjoint reciprocity | `T_adj` self-adjoint | Inner-product, transpose-graph, reciprocity, or detailed-balance structure yields a self-adjoint or adjoint-reciprocity MR. |
| `rev` | time reversal | `T_rev` time reversal | A reversible sub-family of the dynamics constrains forward and reversed executions through a fixed bijection on outputs. |
| `rel` | relational equivalence | `B_rel` relational equivalence | Identity-preserving rewriting over relational algebra or an idempotent semiring preserves evaluation in all valid input contexts. |

## Required manuscript wording

Use:

- "MR MetaPattern axes"
- "NOETHER-aligned MR MetaPatterns"
- "semantic-effect faults"
- "certified semantic-effect fault"
- "syntactic edits vs semantic-effect faults"
- "historical internal IDs" for legacy `CE1/OS1/HP1/TF1/SI1` suffixes

Avoid as reader-facing concepts:

- "five semantic mutation operators"
- "domain-semantic mutation operators" for this paper's own taxonomy
- "CE/OS/HP/TF/SI" as a concept list
- "Conservation Erosion", "Operator Substitution", "Hyperparameter",
  "Trajectory Flip", "Structural Injection" as official class names
- `mut_C/mut_M/mut_G/mut_T/mut_F` as official names

Allowed exception: related-work prose may mention another paper's own
term if it is clearly attributed to that paper and not adopted as this
paper's taxonomy.

## Pre-submission check rule

Before any TOSEM / IST / arXiv submission package is finalized, run this
terminology gate after the usual LaTeX, citation, and packaging checks.

### Gate A — banned reader-facing taxonomy

Run against the manuscript and outward-facing metadata. Use single quotes
around the pattern so the LaTeX-form patterns reach `rg` unmodified:

```bash
rtk rg -n 'Conservation Erosion|Operator Substitution|Trajectory Flip|Structural Injection|domain-semantic mutation operator|semantic mutation operators|meta-operator|mut_C|mut_M|mut_G|mut_T|mut_F|mathrm\{mut\}_[CMGTF]|mut\\_[CMGTF]|HP, SI|HP/SI|CE class|OS row|CE / OS' \
  README.md DATASET.md CITATION.cff docs/terminology_zh_en.md docs/naming_convention.md \
  submission/TOSEM_regular_20260707/main.tex submission/TOSEM_regular_20260707/supplementary.tex
```

Expected result: no hits, except deliberate historical-ID explanations
in `docs/naming_convention.md`, `README.md`, or `DATASET.md`.

Two escape routes were closed on 2026-07-08 after an audit found live
violations that the earlier pattern missed:

1. **LaTeX-typeset subscripts.** The plain `mut_C` alternative never matched
   the typeset forms `\mathrm{mut}_C` (a `}` separates `mut` from `_C`) or
   `mut\_C` (an escaped underscore). The two added alternatives
   `mathrm\{mut\}_[CMGTF]` and `mut\\_[CMGTF]` cover both. In a shell,
   keep the whole pattern in single quotes; inside double quotes the shell
   collapses `\\` to `\` and the backslash-underscore form silently stops
   matching.
2. **Unscanned supplementary file.** `submission/TOSEM_regular_20260707/supplementary.tex`
   was absent from the file list, so 21 residual `CE/OS/HP/TF/SI` mentions
   and the `mut_*` subscript definitions there were never inspected. It is
   now part of the scan set.

### Gate B — required NOETHER vocabulary appears

```bash
rtk rg -n "NOETHER-aligned MR MetaPattern|semantic-effect fault|invariance/equivariance|monotonicity/order|convergence/limit|qualitative dynamics|method comparison" \
  README.md DATASET.md CITATION.cff docs/terminology_zh_en.md docs/naming_convention.md submission/TOSEM_regular_20260707/main.tex
```

Expected result: all five primary axes (`inv`, `mono`, `conv`, `dyn`,
`cmp`) and the term `semantic-effect fault` are represented in the
reader-facing terminology layer.

### Gate C — legacy ID containment

If `CE1/OS1/HP1/TF1/SI1` appears in a reader-facing document, the same
local passage must state that these are historical internal IDs retained
for reproducibility only. They must not be expanded into concept names.

### Gate D — MR Family consistency

Check that any newly added MR family name follows:

```text
inv.* | mono.* | conv.* | dyn.* | cmp.* | adj.* | rev.* | rel.*
```

and that it maps to exactly one definition in `docs/naming_convention.md`.

## Relationship to the previous semantic/syntactic discussion

The paper may still explain that syntactic mutation and semantic-effect
fault generation differ by classification axis:

> Syntactic mutation classifies mutants by edit patterns, whereas
> semantic-effect fault generation classifies them by certified
> violations of semantic contracts. Some semantic-effect faults may be
> implemented as small syntactic edits; the distinction lies in the
> certified semantic effect, not in patch size or textual form.

Do not translate this into a claim that semantic mutation is a subset of
syntactic mutation, or that semantic mutation operators are specialized
versions of classical syntactic operators.

