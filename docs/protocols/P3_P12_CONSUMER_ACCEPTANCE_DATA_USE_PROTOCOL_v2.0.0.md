# P3–P12 Consumer Acceptance and Data-Use Protocol v2.0.0

> Status: **ADOPTED — custodian-approved 2026-08-13 (Asia/Shanghai); becomes
> binding via the §11 freeze procedure (release commit + consumer lock + P3
> protocol V3 re-emission)**
> Draft date: 2026-08-12 (Asia/Shanghai)
> Consumer: P3 Semantic Mutation (P3-V3 execution stream)
> Producer: P12 Defect4MR benchmark (`github.com/meng004/P12-Defect4MR`)
> Succeeds: `P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md` **for
> P3-V3 execution only**; v1.1.2 remains the historical authority for its own
> deliveries and estimands and is not rewritten.
> Compatibility rule satisfied: P3 scientific plan review-remediation row 38
> ("Require an explicitly compatible successor P12 contract; otherwise retain
> v1.1.2 only under its own estimand and downgrade P3 RQ4").

## 1. Purpose and binding effect

This protocol fixes, before any P3 confirmatory MR outcome exists, how P3
receives, validates, classifies, analyzes, and cites evidence from the
Defect4MR benchmark release identified in §4. It prevents P3 from selecting
favorable P12 artifacts, changing denominators after seeing outcomes,
promoting exploratory evidence to confirmation, or strengthening manuscript
claims beyond the accepted evidence. P12 is the evidence producer; P3 is a
read-only consumer. P3 never edits a delivered P12 artifact; corrections
require a new P12 release with a new pinned identity.

## 2. Definitions

The domain terms `P12`, `Defect4MR`, `P3`, formal item, executable reference
MR, `P12_FULL`, `P12_PAIRED`, `P12_DIRECT`, `ADMISSION_POSITIVE_CONTROL`,
`PINNED_GIT_RELEASE`, and blinded bridge carry the meanings frozen in the
producer repository's `CONTEXT.md` at the pinned release commit. Where this
protocol restates a definition, the restatement is a convenience; the pinned
`CONTEXT.md` text governs.

## 3. Benchmark domain declaration

The release in §4 is declared as a benchmark of **MR-detectable real
semantic defects**: every formal item is a real, independently sourced
defect admitted under the producer's frozen rule — stable identity, exact
buggy/fixed version identities, reproducible two-arm execution, at least one
executable reference MR whose violation/satisfaction discriminates the buggy
and fixed arms, and complete provenance and compliance records. P3 results
on `P12_FULL` generalize to this declared domain and no further. Failed,
timed-out, inconclusive, and excluded candidates remain visible in the
producer ledger and are not formal items.

## 4. Pinned release identity (PINNED_GIT_RELEASE)

The only accepted origin rule is one immutable Git release identity,
supplied to P3 as a consumer lock outside the bridge file:

- normalized repository identity: `github.com/meng004/P12-Defect4MR`;
- exact release commit SHA (40 hex);
- bridge path and Git blob SHA;
- this contract's path and Git blob SHA;
- `p12_package_root_sha256`: the canonical manifest hash (domain
  `P12-PACKAGE-ROOT-v1`, `{path, byte_sha256}` rows sorted by path) over the
  release's declared benchmark package directory. The directory and method
  are published in the release receipts.

No generic signing or PKI subsystem is introduced. A self-hash alone is
never accepted as evidence of origin or completeness.

## 5. `P12_FULL` membership

`P12_FULL` is the set of all formal items at the pinned release — at draft
time the 35 `verified_full` ledger entries. Membership is decided only by
the producer's frozen admission rule, before and independently of any P3 MR
outcome, and is immutable at the release: no addition, removal, or
substitution afterwards. Every member carries
`eligible_for_construct = true` and `eligible_for_criterion = true` in the
bridge unless the producer records a prior-evidence reservation in the
item's `eligibility_reason`; execution difficulty is not a permissible
reason (execution failures remain visible in the intention-to-evaluate
denominator, §9).

## 6. Blinded bridge duties (producer)

For every `P12_FULL` member's exact fixed-version snapshot the producer
publishes, inside the pinned release, one bridge record containing exactly:
`neutral_snapshot_id` (domain `P3-NEUTRAL-SNAPSHOT-v1` over package root and
the normalized-source/archive hashes), `fixed_tree_commitment`
(`SHA256("P3-FIXED-TREE-v1" || package_root_hex || fixed_git_tree_oid_hex ||
reveal_nonce_32_bytes)`), `normalized_source_tree_sha256` (P3's frozen
`P3-NORMALIZED-SOURCE-TREE-v1` formula), `source_archive_sha256`,
`build_descriptor_sha256`, `eligibility_reason`, and the two eligibility
booleans. The bridge and its records exclude: issue/PR identity, buggy
commit, fixed commit, defect patch, changed symbols, defect family,
reference MRs, and every outcome. Alongside the bridge, the producer
delivers each record's source archive and build descriptor whose SHA-256
values match the record. The producer keeps the per-record
`fixed_git_tree_oid` and fresh `reveal_nonce` sealed (Package C) until §8.

## 7. Reference-MR isolation (both sides)

Producer reference MRs, their implementation variants, and canonical
semantic-signature equivalents are `ADMISSION_POSITIVE_CONTROL`. Before P3
freezes any evaluated-MR portfolio, P3 sends the candidate-MR canonical
signatures to the producer; the producer returns an exclusion receipt
listing admitted and excluded candidates. Excluded MRs never enter P3
confirmatory portfolios. Positive controls never enter P3 primary models.

## 8. Phase 7 reveal duties (producer)

After P3 delivers its controlled-freeze receipt (Package B sealed,
denominators and portfolios frozen), the producer reveals, for every bridge
record exactly once: `neutral_snapshot_id`, `fixed_git_tree_oid`,
`reveal_nonce` (64 hex), and `normalized_source_tree_sha256`, together with
the buggy/fixed execution material required by the P3 protocol. P3 verifies
every commitment opening, tree identity, and renormalized source. A missing
record, extra eligible item, or commitment/tree mismatch is retained as an
unpaired failure; it cannot be repaired by substitution.

## 9. RQ4 estimand compatibility

P3's primary RQ4 estimand on this release is the prespecified
**intention-to-evaluate lower bound** over the prospectively paired,
constructible subdomain `P12_PAIRED` ⊆ `P12_FULL`, with the denominator
frozen before reveal; upper-bound and complete-case analyses are labelled
sensitivities. `P12_PAIRED` coverage against `P12_FULL` is reported. No
outcome changes membership or weight; no P12-specific replacement input is
added. This estimand binds P3, not the producer's own P12 publications;
v1.1.2's S1–S2/RFDS estimand remains valid for v1.1.2-scope claims.

## 10. Data use, citation, and corrections

P3 cites the pinned release identity (repository, release commit, package
root) in every manuscript use. Producer data retain their upstream licenses;
per-item upstream license notes travel with the release. Any producer
correction requires a new release commit and a new bridge; P3 must then
re-run consumer acceptance from §4. P3 never republishes sealed Package C
material.

## 11. Freeze procedure

This contract becomes binding when (a) the producer commits it, together
with the bridge, into the pinned release; (b) the consumer lock records the
release commit and both blob SHAs; and (c) P3 re-emits its Phase 0 protocol
(V3) binding this contract's byte hash as `p12_contract_sha256`. Until all
three occur, this document is a draft with no evidentiary force.
