# Prereg v2 Amendments Log (F-7)

**Carrier for all post-freeze changes** to any file hashed in
`FREEZE_MANIFEST.sha256`. This file is **deliberately excluded from the
FREEZE_MANIFEST hash set** (F-7a): it is born to be appended after the
freeze; its integrity is guaranteed by the git history — **each amendment
must be a single, separate commit** touching this file (plus the amended
artifact), so the ledger and the change share one auditable commit.

Rules:
1. One amendment = one row = one commit. No batching.
2. Any change to frozen analysis code demotes the affected analysis to
   exploratory unless the amendment documents why validity is preserved
   (validity-repair vs claim-shrinkage per CLAUDE.md §10.1).
3. Every row carries the manuscript §6 disclosure sentence verbatim.
4. Author signature field is mandatory; unsigned rows are void.

| # | Date | Trigger event | Scope (files / hypotheses) | Change summary + diff SHA-256 | §6 disclosure sentence | Author sign-off |
|---|---|---|---|---|---|---|
| 1 | 2026-07-29 | CHECKPOINT 1 integrity verification found the matrix in-header content hash self-referential (the marker string's first occurrence sits in the header prose, so the original recipe hashed a scope containing the hash placeholder itself and can never re-verify) | `applicability_matrix.md` header lines only; **no ruling below the marker changed** (body hash `670e5748…` byte-identical to creation commit `2b36c81`); `FREEZE_MANIFEST.sha256` regenerated accordingly | Header hash recipe redefined to "everything after the first standalone marker line"; new body hash `670e5748437e409e03bd36a202273b9a428112c3e1433aa8fc386c3a87e85b2f`; old file hash `0367c538…` → new file hash recorded in regenerated manifest; validity-repair class (documentation defect), no claim touched | "An in-header checksum recipe in the applicability matrix was repaired post-freeze for a self-reference defect; matrix rulings were not altered (Amendment #1); the operative integrity control is the freeze manifest plus git history." | Delegated execution under author instruction 2026-07-29 ("请评审checkpoint 1。通过，则并行phase2和phase3."); explicit countersign pending |
| 2 | 2026-07-29 | H-DOSE-CTR window freeze (`WINDOWS_FROZEN.json`, commit `f7ca7cc`, pre-unblinding) exposed near-degenerate theory windows (2×10⁻⁶–3.4×10⁻⁴) on 6/8 deterministic-kernel curves, below centre-estimation granularity (sd 0.03–0.16·ε_tol) → frozen containment test guaranteed-FAIL under BOTH theory-true and theory-false: uninformative instrument (a §10.1 validity defect symmetric to unfalsifiability) | `hypotheses.md` §5.2 only (secondary B-2); `FREEZE_MANIFEST.sha256` regenerated; frozen analysis code untouched (`window_halfwidth` input field now carries the effective radius) | Effective containment radius r_c = max(Δ_r + 2η̄, ε_tol·(√g − 1)), g = (4/0.25)^{1/5} (log-grid half-step floor ≈ 0.3195·ε_tol); B3 curves keep their wider own windows; decided + committed BEFORE any dose execution artifact (git-verifiable), so no selection-on-the-response | "The pre-registered containment radius for the dose-transition-centre secondary was floored at the dose grid's location-resolution before any dose execution, because the theory windows froze at values below instrument resolution; the change is recorded as Amendment #2 with git-verifiable pre-unblinding timing." | Delegated execution under author instruction 2026-07-29; explicit countersign pending |
