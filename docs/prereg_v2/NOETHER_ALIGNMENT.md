# NOETHER Terminology Alignment Plan (P3 ← NOETHER)

**Purpose.** Align *all* meta-pattern / MR-family terminology, symbols, definitions,
and concepts in P3 (SMS manuscript) to the canonical system of the companion theory
paper NOETHER, so the two papers do not run parallel taxonomies. NOETHER is the
normative source for the MetaPattern / operator-block vocabulary; P3 adopts it at the
**presentation layer only** (frozen artifacts keep their registered labels — see §B).

- NOETHER source (extracted text): `noether.txt`, 8851 lines (line numbers below cite it).
- P3 manuscript: `source/main.tex` (3509 lines), `source/supplementary.tex` (1678 lines).
- Author directive resolved here: the "10 MR Family" question (§E), MP1–MP5 → m_xxx
  mapping (§A), and the MP5 adjudication (§A, row MP5).

---

## JOB 1 — NOETHER's canonical system (precise extraction)

### 1.1 The eight operator blocks (Def. of `𝒟(𝒜_P)`, NOETHER §3.1.9)

Decomposition (L256, L1190–1193; canonical block ordering L1626):

```
𝒟(𝒜_P) = { G , O≤ , T* , 𝒯*rev , ℒ* , 𝒟* , ℰ* , ℬ*rel }
ordering:  G  >  O≤  >  T*  >  𝒯*rev  >  ℒ*  >  𝒟*  >  ℰ*  >  ℬ*rel
```

| # | Block symbol | Block name (structural invariant) | Def. line | MetaPattern it yields | MP line |
|---|---|---|---|---|---|
| 1 | `G`      | symmetry subgroups (finite-group / Lie)                | L1192 | `m_inv`  (invariance/equivariance)               | L866, L1249, L2218 |
| 2 | `O≤`     | order — monotone & linear operators                    | L1192, L1197 | `m_mono` (parameter-monotonicity)         | L2218, L2291 |
| 3 | `T*`     | self-adjoint operators                                 | L1192 | `m_adj`  (self-adjoint duality / adjoint reciprocity) | L866–867, L2219, L2500 |
| 4 | `𝒯*rev`  | time-reversal (anti-unitary involution of time)        | L1192 | `m_rev`  (time-reversal compatibility)           | L2219, L2521 |
| 5 | `ℒ*`     | limit operators, `ℒ_θ → ℒ*` (Def. 7)                   | L1126, L1206 | `m_conv` (discretisation convergence)     | L2219, L2292 |
| 6 | `𝒟*`     | qualitative-dynamics operators (Def. 8)                | L1147, L1209 | `m_dyn`  (qualitative-dynamics shape invariants) | L2219, L2293 |
| 7 | `ℰ*`     | method-comparison operators (Def. 9)                   | L1185, L1212 | `m_cmp`  (method-comparison error-bound partial orders) | L2220, L2309, L2470 |
| 8 | `ℬ*rel`  | relational-equivalence block (Def. 10, idempotent semiring) | L1193, L1312 | `m_rel` (relational-equivalence)      | L497, L2382, L3052 |

"Conservation laws are **not** a ninth block": a conservation/invariance relation *is*
the `G`-block MetaPattern `m_inv` by the Noether-style symmetry↔conserved-quantity
correspondence (L1249). "The eight blocks are an empirical curation … currently
sufficient" (L1319–1325) — not claimed exhaustive.

### 1.2 The MetaPattern concept

- `𝕄(𝒜_P) = CONSTRUCT-MP(𝒟(𝒜_P))` — the MetaPattern set produced from a program-family
  operator algebra (L231, L266, L298, L1631).
- **Closure theorem** (Theorem 1, L491): `𝕄(𝒜_P)` is closed under Translate over the
  algebra-induced MR space `MR(𝒜_P)`. Poly-time constructibility of CONSTRUCT-MP when
  the algebra has a finite generating set (Theorem 2, L383, L494).
- **Per-instance count law** (L1338): `|𝕄(𝒜_P)|` = number of **non-empty** blocks for
  that instance. Worked instances: `𝒜Boltz` → 7 (L2215); `𝒜equi` → 5 (L2627);
  `𝒜rel` → 3 (L3052); `𝒜sort` → 2 (L6505).
- Each MetaPattern `m_{s,[ι]} = ℛ(ι)` is a `∼_s`-equivalence class over `MR(𝒜_P)`
  (L1609–1612, Remark 10 L2116). NOETHER uses **"MR class"** and **"MetaPattern"**
  interchangeably (L48 "MR classes / MetaPatterns").
- **Invariance-Blindness Theorem** (Theorem 3, L390, L499): scoped to the **`G` and `T*`
  blocks only** — an algebra-derived MR's detection kernel equals exactly the
  structure-preserving faults (faithfulness-tight, linear-fault class). Tightness beyond
  `{G, T*}` is explicitly *not* claimed.

### 1.3 The canonical MetaPattern roster (total count = 8)

Running CONSTRUCT-MP on `𝒜Boltz` yields **seven** MetaPatterns (L2218–2220):

```
m_inv , m_mono , m_adj , m_rev , m_conv , m_dyn , m_cmp
```

plus `m_rel` from the relational block `ℬ*rel` (L2382 "one of the seven canonical
MetaPatterns or m_rel"; four-way audit "eight classes" L2299). **Canonical total = 8.**

### 1.4 Re-classification of the prior inductive reactor-physics catalogue (Table 3, §3.4.3)

The prior inductive catalogue [7,35] enumerated five patterns —
**conservation, monotonicity, convergence, trajectory, partial-order** (L386–391).
NOETHER Table 3 (L2280–2330) re-projects them; contribution C3 summary at L813–816
("reproduces three, refines two, de-duplicates two"):

| Prior pattern (Pk) | NOETHER placement | Verdict | Evidence |
|---|---|---|---|
| **P1** conservation/invariance | `m_inv`  (`G` block) | **Reproduced** | L2287, L2296 |
| **P2** monotonicity            | `m_mono` (`O≤` block) | **Reproduced** | L2291 |
| **P3** convergence             | `m_conv` (`ℒ*` block) | **Reproduced** | L2292 |
| **P4** trajectory              | `m_dyn`  (`𝒟*` block) | **Refined** — inductive P4 conflated qualitative-dynamics with time-reversal; NOETHER separates them, trajectory → `m_dyn` | L2293, L2297 |
| **P5** partial-order/bounding  | `m_cmp`  (`ℰ*` block) | **Refined** — inductive P5 grouped method-accuracy partial orders with adjoint reciprocity; NOETHER places method-comparison partial orders → `m_cmp` | L2299, L2309 |
| *(none prior)* | `m_adj` (`T*`) | **Predicted / de-duplicated** (adjoint reciprocity, structurally distinct class) | L2320, L2370 |
| *(none prior)* | `m_rev` (`𝒯*rev`) | **Predicted / de-duplicated** (collisionless time-reversal) | L2324, L2370 |

**This table is the direct bridge to P3's MP1–MP5** (P3 *is* an instance of that prior
inductive reactor-physics catalogue).

### 1.5 "MR family" in NOETHER

`MR(𝒜_P)` is the algebra-induced MR space; a **MR class = MetaPattern** = `∼_s`
equivalence class of MRs (L48, L1609–1612). NOETHER does **not** use "MR family" as a
distinct primitive — "MR class" and "MetaPattern" are the operative terms. (P3's
`MR_{i,k}` "MR family" is a *finer, per-PUT × per-MP* object — a terminology collision,
see §2 and §A row **MR family**.)

### 1.6 Definitions P3 may import / adapt

- **MR class / MetaPattern** — `m_{s,[ι]} = ℛ(ι)`, closure-guaranteed equivalence class
  over `MR(𝒜_P)` (L1609–1612, Thm 1 L491).
- **Operator block** — one of the eight structural cells of `𝒟(𝒜_P)` (§3.1.9, L1188–1193).
- **Applicability / scope boundary** — governing-equation-derived scope precondition
  making MR applicability explicit (L44, C4 scope precondition L497). Aligns with P3's
  per-class operator applicability (main L2084–2092).
- **Instantiation gate (interface-exposure check)** — NOETHER phrases MR executability as
  the SUT interface *exposing* the relevant structure (forward-hook / probe), e.g.
  "executable on any transformer whose attention layer **exposes** the bilinear form"
  (L2870); kill-rate correlates with "SUT-side symmetry **exposure**" (L5210). This is
  the concept P3 should adopt for its instantiability/exposure gate.

---

## JOB 2 — P3 current usage and collision inventory

P3 runs **two** five-element sets held in one-to-one alignment (main L242–244):
(i) **operator families** CE/OS/HP/TF/SI (= `mut_C/M/G/T/F`, L237–241) — the *mutation*
operators; and (ii) **meta-patterns** MP1–MP5 (= invariants `ψ1…ψ5`, L949–953) — the
*MR strata*. P3 also carries a sixth invariant `ψ6` adjoint consistency (L960–975).

P3's five meta-patterns (main L951–953, L661–666):

| P3 label | P3 gloss / `ψ` | main.tex evidence |
|---|---|---|
| MP1 | conservation (`ψ1`) | L952, L1305, L1359 |
| MP2 | monotonicity (`ψ2`) | L952, L1365 |
| MP3 | convergence order (`ψ3`) | L952, L1370 |
| MP4 | trajectory determinism (`ψ4`) | L953, L1375 |
| MP5 | partial-order consistency / "partial-order (asymptotic)" (`ψ5`) | L953, L1380, L1402, L2475–2477 |
| (ext) | adjoint consistency (`ψ6`) | L960–975, L1626–1633, L2406 |

**Collisions / divergences with NOETHER (7):**

1. **MP1–MP5 labels** vs NOETHER `m_inv/m_mono/m_conv/m_dyn/m_cmp` — parallel taxonomy;
   P3 uses ordinal MPk, NOETHER uses semantic `m_xxx`. (main L949–953, L1305 etc.)
2. **`ψ6` adjoint consistency** = NOETHER `m_adj` (`T*` block) — same concept, unlinked.
   (main L960–975.)
3. **"MR family" `MR_{i,k}`** (main L661) collides with NOETHER "MR family/MR class":
   P3's object is indexed by PUT `i` *and* MP `k` (finer than a MetaPattern); NOETHER's
   MR class = a whole MetaPattern. Term reuse at different granularity.
4. **`ψ_k` invariant symbols** (`ψ1…ψ6`) — P3-internal; no NOETHER equivalent symbol,
   but each `ψ_k` = the invariant *defining* a NOETHER MetaPattern.
5. **Operator-family names** CE/OS/HP/TF/SI and `mut_C/M/G/T/F` (main L237–241) — these
   are P3-specific *mutation* operators, **not** NOETHER blocks; note the confusing
   internal skew (`mut_G` = Hyperparameter = convergence-breaker; `mut_M` = Operator
   Substitution = monotonicity-breaker). **Keep** (P3-specific), do not map to blocks.
6. **`ψ6` sub-labels** `adj.self` / `adj.dual` (main L1633, suppl L1422) — P3 sub-MRs of
   `m_adj`; keep as sub-instances.
7. **Supplementary already half-aligned**: `supplementary.tex` L1482 *already* prints
   `m_mono, m_conv, m_inv, m_adj, m_rev` for the defect4MR 34-defect corpus — a
   *different* five-set than MP1–MP5 (drops `m_dyn/m_cmp`, adds `m_adj/m_rev`). This is an
   **internal inconsistency** the alignment must reconcile (main body = MPk; one suppl
   table = `m_xxx`).

---

## JOB 3 — Alignment plan

### (A) Master mapping table

| P3 term / symbol | NOETHER canonical | Block | Mapping type | Evidence (P3 → NOETHER) |
|---|---|---|---|---|
| MP1 Conservation (`ψ1`) | `m_inv` | `G` | **identical concept, rename-in-prose** | main L952 → L1249, L2287 |
| MP2 Monotonicity (`ψ2`) | `m_mono` | `O≤` | **identical, rename-in-prose** | main L952 → L2291 |
| MP3 Convergence order (`ψ3`) | `m_conv` | `ℒ*` | **identical, rename-in-prose** | main L952 → L2292 |
| MP4 Trajectory determinism (`ψ4`) | `m_dyn` | `𝒟*` | **identical, rename-in-prose** (NOETHER "refined" P4→m_dyn; P3's MP4 is already the pure qualitative-dynamics reading, so no content change) | main L953 → L2293, L2297 |
| **MP5 Partial-order / asymptotic (`ψ5`)** | **`m_cmp`** | `ℰ*` | **identical, rename-in-prose** — *adjudicated below* | main L953, L1402, L2475 → L2299, L2309 |
| `ψ6` Adjoint consistency | `m_adj` | `T*` | **identical, rename-in-prose** | main L960–975 → L2500, L866 |
| `MR_{i,k}` "MR family" | (per-PUT instance of a MetaPattern `m_xxx`) | — | **P3-specific, keep with note** — clarify it is a per-PUT × per-MP MR *set*, an *instantiation* of MetaPattern `k`, not the class itself | main L661 → L1609 |
| Operator families CE/OS/HP/TF/SI (`mut_*`) | (no NOETHER analogue — mutation operators) | — | **P3-specific, keep** | main L237–241 |
| `adj.self` / `adj.dual` | sub-MRs of `m_adj` | `T*` | **P3-specific, keep** | main L1633 → L2500 |
| (P3 has no MP for) | `m_rev` (`𝒯*rev`), `m_rel` (`ℬ*rel`) | — | NOETHER-only; P3 simply does not exercise these blocks — state so, do not invent | — → L2324, L2382 |

**MP5 adjudication (`m_lim` vs `m_conv` sub-case vs `m_cmp`) → `m_cmp`.**
P3's MP5 is registered as *partial-order consistency / fidelity-order*, with registered
instances that are method/fidelity comparisons: LU partial-pivoting fidelity order
(main L1380), "fidelity ordering" (L162), "partial-order meta-pattern" (L1402, L2136).
NOETHER's re-classification places exactly the prior "P5 partial-order/bounding" pattern
into **`m_cmp`** (method-comparison error-bound partial orders), *explicitly refining* it
away from adjoint reciprocity (L2299, L2309). It is **not** `m_conv` — that is the `ℒ*`
convergence block already claimed by MP3. **Caveat to footnote, not to relabel:** where a
specific P3 MP5 instance degrades to a pure *asymptotic residual-ratio* rate check
(suppl L229 "convergence-order + asymptotic residual ratio"; main L2475–2477 "asymptotic
or statistical relation"), that instance borders `ℒ*`/`m_conv`; the *registered stratum*
remains fidelity/partial-order, so canonical mapping is `m_cmp` with a one-line note that
rate-only instances are `ℒ*`-adjacent. There is **no** `m_lim` symbol in NOETHER
(the limit block's MetaPattern is `m_conv`).

### (B) HARD CONSTRAINT — frozen artifacts keep their labels (presentation-layer only)

The alignment is **presentation-layer**. The following are **IMMUTABLE** and MUST keep
their registered `MPk` (and class-rule) labels verbatim:

- Pre-registrations: `docs/experiment_documentation/EXPERIMENT_DESIGN.md`,
  `docs/prereg_v2/PREREGISTRATION_STUDY2_v1.1.md`, `PREREGISTRATION_STUDY2.md`,
  `REGISTERED_VS_EXECUTED_STUDY1.md`.
- SSOT JSON keys and cell IDs: `A2_MP1`, `B2_MP1`, `C1_MP1`, `C1_MP2`, `D1_MP5`, `D3_MP5`,
  etc. (referenced main L2501–2502).
- Scripts / cell selectors: `PRIMARY_CELLS_V3` and all committed data / result files.
- The registered class rule `A→MP1, B→MP2, C→MP5-held, D→MP2` (main L2879–2880) — the
  **MPk labels stay** as the registration reference; a NOETHER gloss may be *added* but
  the rule text must still read as the registered `MPk` rule.

**Mechanism.** The manuscript adopts NOETHER `m_xxx` as the **primary** narrative name,
introduces a **one-time mapping table** ("registered label MPk = NOETHER `m_xxx`") at
first use, and keeps `MPk` in every **provenance / registration** reference.

**FORBIDDEN sentence class.** No sentence may claim or imply that the *pre-registration*,
*EXPERIMENT_DESIGN*, *SSOT keys*, or *executed protocol* used NOETHER `m_xxx` names —
they used `MPk`. Any wording like "we pre-registered `m_cmp`" is **false and prohibited**;
write "we pre-registered MP5 (= `m_cmp` in NOETHER's taxonomy)". Provenance is `MPk`;
exposition is `m_xxx`.

### (C) Citation handling (NOETHER = anonymous companion)

P3 already cites its P-series companions as `@misc` entries with `journal = {Unknown
Journal}` / project notes (`li2026sms` L1, `li2026minmrcomplete` L9, `defect4mr2026` L17
in `source/references.bib`), cited in prose as `\citep{li2026minmrcomplete}` (main L500,
L1238). NOETHER differs in one respect: the author directive marks it an **anonymous**
companion (its own byline is "Anon.", noether.txt L380).

**Proposed entry** (append to `source/references.bib`, mirroring the P-series `@misc`
shape but author-blind):

```bibtex
@misc{noether2026,
  author       = {Anon.},
  title        = {{NOETHER}: Constructive Metamorphic Pattern Identification from
                  Operator Algebras and a Falsifiable Invariance-Blindness Theorem},
  howpublished = {Companion submission, under review},
  year         = {2026},
  note         = {Anonymous companion; author byline withheld for double-blind review.
                  De-anonymise at camera-ready.}
}
```

Cite in prose as `\citep{noether2026}` at the terminology-bridge paragraph and wherever
`m_xxx` naming or the re-classification claim is invoked.

**Flag for the integrator / author:** P3 currently *de-anonymises* `li2026*`. Keeping
`noether2026` anonymous while naming the other companions is internally inconsistent
under a single blinding policy. Two consistent options — (i) anonymise `noether2026` only
because it is the one still under blind review (recommended, per directive), adding the
camera-ready de-anonymisation note; or (ii) if P3's venue is single-blind, name NOETHER's
authors like the other companions. **Do not** silently pick; surface to author.

### (D) Concrete edit inventory for the manuscript integrator

**Terminology-bridge paragraph — DRAFT** (insert at `main.tex` L666, right after the
"Meta-pattern (MP)" definition, before "Semantic operator"):

> The five meta-patterns are the instance, on the scientific-computing program family, of
> the canonical MetaPattern taxonomy of the companion framework NOETHER \citep{noether2026},
> which derives MetaPatterns as closure-guaranteed equivalence classes over an operator
> algebra. We adopt NOETHER's names as primary and record the correspondence to our
> registered labels once, here: MP1 conservation $= m_{\mathrm{inv}}$ (symmetry block $G$),
> MP2 monotonicity $= m_{\mathrm{mono}}$ (order block $O_{\le}$), MP3 convergence order
> $= m_{\mathrm{conv}}$ (limit block $\mathcal{L}^{*}$), MP4 trajectory determinism
> $= m_{\mathrm{dyn}}$ (qualitative-dynamics block $\mathcal{D}^{*}$), and MP5 partial-order
> consistency $= m_{\mathrm{cmp}}$ (method-comparison block $\mathcal{E}^{*}$); the adjoint
> extension $\psi_6$ is $m_{\mathrm{adj}}$ (self-adjoint block $T^{*}$). The registered
> labels MP1--MP5 are retained throughout for all pre-registration, dataset-key, and
> provenance references, since the pre-registered protocol was authored under those labels;
> NOETHER's $m_{xxx}$ names carry the semantic narrative. Our framework does not exercise
> NOETHER's time-reversal ($m_{\mathrm{rev}}$) or relational-equivalence ($m_{\mathrm{rel}}$)
> blocks.

**Edit locations** (reword to NOETHER-primary, keeping registered labels where noted):

| main.tex loc | Current | Action |
|---|---|---|
| L135, L137, L161–162 | Abstract lists "conservation, monotonicity, convergence, trajectory, fidelity-order" | Keep prose adjectives (readable); add `m_xxx` only if space — **low priority**, no MPk here to protect |
| L237–244 | operator families CE/OS/HP/TF/SI; "reserve *meta-pattern* for the five MR strata" | **Keep**; optionally add one clause: these strata are NOETHER MetaPatterns (fwd-ref bridge) |
| **L661–666** | "MR family `MR_{i,k}`"; "Meta-pattern (MP)" def | **Insert bridge paragraph** (above); add note that `MR_{i,k}` is a per-PUT *instance* of MetaPattern `k`, not the class |
| **L949–967** | `ψ1…ψ5` invariant family list | Annotate each `ψ_k` with `= m_xxx`; state `ψ_k` defines NOETHER MetaPattern |
| **L960–975** | `ψ6` adjoint consistency | Annotate `ψ6 = m_adj` (`T*` block), `\citep{noether2026}` |
| L1305 | coverage-matrix caption "five meta-patterns" | Add "(MP1–MP5 $= m_{\mathrm{inv}},m_{\mathrm{mono}},m_{\mathrm{conv}},m_{\mathrm{dyn}},m_{\mathrm{cmp}}$)" |
| L1402, L2136–2140, L2475–2477 | "partial-order meta-pattern" | First occurrence: append "($m_{\mathrm{cmp}}$)"; add the rate-only `ℒ*`-adjacency footnote at L2475 |
| L2879–2880 | registered rule `A→MP1 … D→MP2` | **Keep MPk verbatim** (registration reference); gloss allowed but rule text unchanged |
| L3197, L3340 | discussion invariant lists | Optional: align adjectives; low priority |

**supplementary.tex:**

| suppl.tex loc | Action |
|---|---|
| L229 | "asymptotic residual ratio" — add `ℒ*`-adjacency note tie-in to MP5=`m_cmp` caveat |
| L1387–1436 (Adjoint Extension Study) | Annotate `ψ6 = m_adj`; `\citep{noether2026}` |
| **L1482** | defect4MR strata already print `m_inv/m_mono/m_conv/m_adj/m_rev`. **Reconcile**: add a note that this corpus spans a *different* block subset than MP1–MP5 (adds `m_adj/m_rev`, omits `m_dyn/m_cmp`), so the reader is not misled that MP1–MP5 = these five |

**DO NOT TOUCH:** SSOT keys `A2_MP1`/`D1_MP5`/… (L2501–2502); registered class-rule label
text (L2879–2880); `PRIMARY_CELLS_V3` and all script/data file names; any sentence
describing what the pre-registration declared (must stay `MPk`); the operator-family names
`mut_C/M/G/T/F` / CE-OS-HP-TF-SI.

### (E) The "10 MR families" verdict

**No — "10 MR families" is not a real NOETHER MetaPattern/MR-class count.**

- NOETHER's canonical MetaPattern roster is **8**: `m_inv, m_mono, m_adj, m_rev, m_conv,
  m_dyn, m_cmp` (the seven from CONSTRUCT-MP on `𝒜Boltz`, L2218–2220) **+ `m_rel`** (the
  relational block, L2382). Equivalently "eight blocks" / "eight classes" (L444, L1319,
  L2299).
- The recurring **"ten"** in NOETHER is **"ten Translate-extension dimensions"** (L388,
  L509, L3153): five signature-obstruction dimensions proved pairwise-independent on
  `𝒜PWR` **+** five candidate dimensions on `𝒜equi`/`𝒜rel`. These are *negative-theory*
  obstructions to Translate's completeness (Theorem 1′ / Conjecture B), **not** MetaPatterns
  or MR families. The author's "10个MR Family" almost certainly conflates these **ten
  Translate-extension dimensions** with the MetaPattern roster.
- NOETHER's EQ / classification tables enumerate **8** classes (four-way audit reserves a
  ninth "orphan" slot for MRs fitting none, L2299), **7** on `𝒜Boltz`, **5** on `𝒜equi`
  (L2627), **3** on `𝒜rel` (L3052), **2** on `𝒜sort` (L6505). **Nothing enumerates 10
  MetaPatterns.**

**Correct terms/counts to use in P3:** the canonical set has **8 operator blocks / 8
MetaPatterns**; P3 exercises **6** of them (MP1–MP5 = `m_inv, m_mono, m_conv, m_dyn,
m_cmp`; plus `ψ6 = m_adj`), and does **not** exercise `m_rev` or `m_rel`.
