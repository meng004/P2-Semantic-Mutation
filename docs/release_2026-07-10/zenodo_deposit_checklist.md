# Zenodo Deposit Scope for the Four-Study TOSEM Submission (2026-07-10)

Purpose: what the next Zenodo deposit (DOI 10.5281/zenodo.20250664 lineage)
must include so the artifact can meet ACM artifact badging (Artifacts
Available; Artifacts Evaluated - Functional/Reusable; Results Reproduced)
for the TOSEM Regular submission.

## Must-include inventory

1. **Registrations (frozen, with amendments)**
   - `docs/PREREGISTRATION_STUDY2_v1.1.md`
   - `docs/PREREGISTRATION_STUDY3_v2.md`
   - `docs/PREREGISTRATION_STUDY4_v1.md` (+ amendments v1.1, v1.2)
   - `docs/REGISTERED_VS_EXECUTED_STUDY1.md`
2. **Incident and deviation log**
   - `docs/PILOT_LOG.md` (incidents P1-P16, deviation D-A1)
3. **Mutant pools (frozen)**
   - Study 1 v4 cross-source pools; Study 2 v5; Study 3 v6; Study 4 v7
     (same, cross, recruitment, C-port) with frozen review labels
4. **SSOTs (`data/results/`)**
   - Study 1: `paper_numbers_v4.json`, `rq2_cliffs_delta_v4_mp5.json`,
     `rq3_friedman_v4.json`, `s5_purity_v4.json`, `h2_incidence_v4.json`,
     `lrca_60cell_v4.json`, `cosmic_ray_12put_ast_diff.json`,
     `industrial_percase_v1.json`
   - Study 2: `sms_track2_v5.json`, `dualblind_delta_delta_v5.json`,
     `h1_instantiability_v5.json`, `h3_class_consistency_v5.json`,
     `s5_purity_v5.json`, `h4_leakage_diagnosis_v5.json`,
     `power_study2_v11.json`
   - Study 3: `sms_track2_v6.json`, H4''-graded/strict outputs,
     `power_study3.json`
   - Study 4: `sms_track2_v7.json`, `sms_track2_v7_same.json`,
     `sms_track2_v7c.json`, `dualblind_delta_delta_v7.json`,
     `hlang_delta_v7c.json`, H4''' outputs and S1/S2 sensitivities
   - Editorial sensitivities: `cluster_sensitivity_v1.json`,
     `denominator_sensitivity_v1.json`, `review_shadow_kappa_v7.json`
5. **Scripts**
   - Full `scripts/` (campaign, admission, scoring, statistics, and the
     sensitivity generators `compute_cluster_sensitivity.py`,
     `compute_denominator_sensitivity.py`, `review_shadow_kappa.py`) and
     `src/` package, with `requirements-frozen.txt`
6. **Guides**
   - `REPRODUCIBILITY.md` (three tiers; 549-test suite),
     `DATASET.md`, `CITATION.cff`, `LICENSE`

## Badging mapping

| Badge | Supported by |
|---|---|
| Available | DOI-archived deposit containing 1-6 |
| Functional | Tier-1 smoke (549 tests) + tier-2 SSOT replay commands |
| Results Reproduced | Tier-2 byte-identical SSOT re-derivation (`git diff data/results/` empty) at seed 20260708 |

## Notes

- The industrial arm's dataset stays a separate deposit
  (10.5281/zenodo.21203424); include only the mirrored
  `industrial_percase_v1.json` and its SHA-256 provenance.
- Frozen review labels must ship as committed; the shadow-kappa SSOT is
  post-hoc and must be labelled as such in the deposit README.
- Deposit minting is a user-gated action (account credentials); this note
  defines scope only.
