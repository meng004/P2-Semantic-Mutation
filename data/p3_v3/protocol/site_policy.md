# P3 v3 Phase 0 authority: Subject, site identity, behavior frame, and evaluation-input policy

> Authority ID: p3-v3-phase0-site-policy-v1
> Date frozen: 2026-08-12
> Governing plan: docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md
> Governing plan SHA-256: fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830
> Source sections (verbatim, 1-based inclusive plan lines): Section 5.2.1 Experimental unit and site identity (L321-L344); Section 5.2.2 Public Behavior Frame, Profiling Workload, and Evaluation Inputs (L345-L447)
> Scope: verbatim extract for hash-binding and operational reference; the
> governing plan remains the sole scientific authority. All claims remain
> blocked (research/evidence/p3_claim_ledger_v1.3.0.yml).

### 5.2.1 Experimental unit and site identity

The controlled subject is a program-version profile, not a mutation site. Before
proposal, P3 freezes the Profiling Workload definition independently of its
execution results and computes:

```text
controlled_subject_id = SHA256(canonical_json({
  normalized_source_tree_sha256,
  build_descriptor_sha256,
  profiling_workload_sha256,
  domain: "P3-SUBJECT-v1"
}))
```

The same normalized source/build/profiling-workload triple always denotes the
same controlled subject, including when several P12 faults share it. Profiling
success or failure cannot change this identity. Candidate mutation sites are
separate objects. Each `site_id` is derived from
`controlled_subject_id`, canonical relative path, resolved symbol, and source
span. A frozen syntax-aware enumerator orders sites by path, symbol, span, and
site hash. Subject rows, mutation rows, and revealed real-fault rows are never
treated as interchangeable independent units.

### 5.2.2 Public Behavior Frame, Profiling Workload, and Evaluation Inputs

The plan freezes three distinct authorities; none may substitute for another.

1. **Public Behavior Frame.** Mechanically enumerate publicly evidenced
   `PUBLIC_API`, `CLI`, `EXAMPLE`, `BENCHMARK`, and `PROJECT_TEST` behaviors from
   the fixed source, build/dependency metadata, and public documentation. Every
   discovered behavior has public provenance. The category accounting retains
   zero-count categories, while unsupported adapters and invalid public
   declarations remain explicit. This is completeness relative to the frozen
   discovery rule, not a claim that repository materials represent all use.
2. **Profiling Workload.** Before bridge intake, freeze the exact adapter
   registry and source hashes. Confirmatory adapters are
   `PYTHON_PEP517_V1`, `CMAKE_CTEST_V1`, `MESON_TEST_V1`, and
   `AUTOTOOLS_MAKECHECK_V1`; every other ecosystem is retained as
   `ADAPTER_UNSUPPORTED` and receives no hand-selected fallback. Use exact
   subject budgets `B_S=10`, `B_M=15`, and `B_L=20`. The frozen category order is
   `PUBLIC_API`, `CLI`, `EXAMPLE`, `BENCHMARK`, then `PROJECT_TEST`. Select one
   row from each nonempty executable category in that order, choosing the lowest
   `(diversity_signature_sha256, behavior_id)`, then cycle through categories,
   preferring unseen diversity signatures before the lowest remaining
   `behavior_id`, until the budget or frame is exhausted. The diversity
   signature hashes category, normalized entrypoint, sorted static dependency
   tags, input-schema hash, and domain `P3-PROFILE-DIVERSITY-v1`. Dynamic
   coverage, execution success, project identity, desired technique, mutant/MR
   outcomes, P12 identities, and real-fault outcomes cannot affect selection.
   Every selected failure remains in the profiling-result funnel. These are
   fixed resource budgets, not a power or representativeness claim.
3. **`E_COMMON` primary inputs.** Immediately after the Public Behavior Frame
   and before contracts or sites, generate exactly 30 subject-level candidates
   with ordinals `0..29`. The generator reads only normalized fixed source/build
   metadata, public input schemas, and public documentation; it cannot read
   `PROJECT_TEST` bodies or fixtures, profiling results, contracts, patches,
   MRs, P12 identities, or outcomes. The seed is the first unsigned 64 bits of
   `SHA256(canonical_json({domain: "P3-E-COMMON-SEED-v1",
   controlled_subject_source_id, ordinal}))`. Invalid or unavailable ordinals
   remain in the denominator and are never manually replaced. Only `E_COMMON`
   supplies primary RQ3 and RQ4 jobs.
4. **`E_CONTRACT` certification inputs.** For each statically applicable slot,
   after site and contract freeze but before patch proposal, generate exactly
   five candidates with ordinals `0..4`. The seed is the first unsigned 64 bits
   of `SHA256(canonical_json({domain: "P3-E-CONTRACT-SEED-v1",
   controlled_subject_id, slot_id, ordinal}))`. The generator may read the
   contract/domain/site but no patch, MR, P12 identity, profiling outcome, or
   experimental outcome. Invalid/nonactivating candidates remain without
   replacement. `E_CONTRACT` is limited to prepatch activation,
   certification support, and a separately labelled contract-conditioned
   sensitivity; it cannot enter primary SMS, P12 detection, or `Delta_sem`.

Before bridge intake, freeze `input-generator-registry.json`: each generator ID,
accepted schema/domain kind, implementation path and source SHA-256, canonical
output schema, and failure code. `E_COMMON` permits only
`JSON_SCHEMA_DRAFT2020_12_V1`, `CLI_TOKEN_GRAMMAR_V1`,
`NUMERIC_ARRAY_DOMAIN_V1`, `TEXT_IO_SCHEMA_V1`, and
`BINARY_RECORD_SCHEMA_V1`; `E_CONTRACT` permits only
`CONTRACT_ENUM_DOMAIN_V1`, `CONTRACT_NUMERIC_DOMAIN_V1`,
`CONTRACT_ARRAY_DOMAIN_V1`, `CONTRACT_SEQUENCE_DOMAIN_V1`, and
`CONTRACT_RELATION_PAIR_DOMAIN_V1`. No model/author fallback is permitted.

For `E_COMMON`, canonicalize eligible public schema records, deduplicate by raw
schema SHA-256, order by `(schema_selection_key, raw_schema_sha256)` using a selection
key that excludes subject/project aliases, and assign ordinal `i` to schema
index `i mod k`. The registered implementation receives only frozen schema bytes
and seed and returns one canonical input envelope/payload hash or a stable failure
code. Each applicable contract names exactly one registered domain generator;
all five `E_CONTRACT` ordinals invoke it with frozen contract/domain bytes and
their seeds. An unsupported domain yields five `CONTRACT_INPUT_UNAVAILABLE`
records, not a new generator, site, contract, or manual input.

A post-patch certification witness belongs to neither input inventory. A public
test can coincide with `E_COMMON` only when the public-schema generator
independently emits byte-identical input at its predetermined ordinal. Thirty and
five are fixed exposure budgets, not power guarantees; achieved valid,
invalid, and unavailable counts are reported.

After all 30 ordinals freeze, a separate pre-outcome fixed-source validation
classifies each as executable, invalid, or unavailable. Primary controlled and
P12 job inventories use only executable fixed-source identities, while the full
30-row generation/validity funnel remains mandatory. Validity cannot alter sites,
contracts, strata, patches, or MR inventories.

Before behavior discovery, compute the source/build identity independently of
any workload:

```text
controlled_subject_source_id = SHA256(canonical_json({
  normalized_source_tree_sha256,
  build_descriptor_sha256,
  domain: "P3-SOURCE-v1"
}))
```

Every behavior row binds this identity. `profiling_workload_sha256` hashes only
the selected canonical behavior rows and their declared inputs, never execution
success, trace, or output.

A reached static site is `OBSERVED_REACHABLE`. A statically enumerated but
unreached site is `UNPROFILED`, not `NOT_APPLICABLE`. Only failure of the frozen
static semantic applicability predicate yields `NOT_APPLICABLE`. Dynamic claims
are limited to behavior exercised by the frozen Profiling Workload, `E_COMMON`,
or explicitly labelled `E_CONTRACT` sensitivity inputs; whole-source dynamic
coverage is never inferred.
