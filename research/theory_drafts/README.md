# P3 Theory Draft Workspace

This workspace holds the independently readable sources for the P3 theory
enhancement. The master specification is
[`docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`](../../docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md).
The notation registry is the closed symbol set for every draft below.

| File | Responsible phase | Purpose | Status |
|---|---|---|---|
| `notation_registry.md` | T0 | Frozen notation registry (40-entry closed set), label-to-body map, rename inventory | audited |
| `thm_interval.md` | T1 | LEM-WIT and THM-INT (body: Lemma 4.1, Theorem 4) | audited + integrated |
| `thm_gap.md` | T2 | LEM-CLO, THM-GAP, and COR-ZERO (body: Lemma 5.1, Theorem 5, Corollary 5.1) | audited + integrated |
| `thm_window.md` | T3 | THM-WIN with REM-FPOS and REM-FNEG (body: Theorem 3) | audited + integrated |
| `rem_identifiability.md` | T4 | REM-IDF and LRCA repositioning (body: §2.11 unnumbered Remark) | audited + integrated |

Status progression is `draft` → `internal-review` → `audited` → `integrated`.
The theory chapter was frozen on 2026-07-29 (CHECKPOINT T4); the audit
signature and draft SHA-256 fingerprints are in
`docs/review_20260728/formal_audit_report.md` (independent formal audit,
three rounds, final verdict AUDIT PASS).
Phase T5 directly repairs the existing manuscript and Appendix G; it therefore
does not introduce a separate draft file in this workspace.
