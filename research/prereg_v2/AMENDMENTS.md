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
