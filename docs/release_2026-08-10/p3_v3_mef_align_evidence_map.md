# P3-V3-MEF-ALIGN-01 Task 9 Evidence Map

Date: 2026-08-10
Branch: `cursor/p3-v3-minimum-evidence-foundation-alignment`
Collection command: `PYTHONPATH=src python3 -m pytest tests/p3_v3 --collect-only -q`
Focused suite: `129 passed`
Full repository suite: `609 passed`
Ruff: clean on `src/p3_v3 scripts/p3_v3 tests/p3_v3`

Node IDs use the pytest form `tests/p3_v3/<module>.py::<test_name>`.

## Section 12 — Tests 1–25

| # | Governing requirement | Exact pytest node ID(s) and/or source invariant | Status |
|---|------------------------|--------------------------------------------------|--------|
| 1 | Canonical bytes / exact types / durable writes | `tests/p3_v3/test_artifacts.py::test_canonical_file_has_sorted_keys_and_one_terminal_lf`; `::test_exclusive_write_preserves_existing_bytes`; `::test_reader_rejects_noncanonical_json_bytes`; `::test_canonical_json_rejects_nonfinite_numbers[*]`; `::test_exact_object_rejects_extra_key_and_bool_as_integer`; `::test_sha256_and_canonical_hash_require_lowercase_hex` | Covered |
| 2 | Pinned repository/release/path/blob/package-root mutations fail | `tests/p3_v3/test_bridge_and_frames.py::test_bridge_is_read_from_exact_pinned_git_release`; `::test_bridge_rejects_wrong_external_blob_pin` | Covered |
| 3 | Visible bridge secret rejection + reveal commitment opening | `tests/p3_v3/test_bridge_and_frames.py::test_visible_bridge_rejects_fixed_tree_oid_even_when_rehashed`; `::test_reveal_binds_nonce_oid_commitment_and_normalized_source`; synthetic reveal in `tests/p3_v3/test_synthetic_phase_path.py::test_synthetic_phase0_to_phase7_evidence_path` | Covered |
| 4 | Public-behavior discovery order-invariant; missing/unsupported/invalid retained; provenance required | `tests/p3_v3/test_bridge_and_frames.py::test_public_behavior_frame_accounts_all_categories_and_retains_unsupported`; `::test_public_behavior_rejects_missing_provenance`; `::test_public_behavior_frame_is_input_order_invariant` | Covered |
| 5 | Adapter registry four frozen IDs/exact hashes; unsupported ecosystem has no hand-command fallback | `tests/p3_v3/test_bridge_and_frames.py::test_adapter_registry_binds_exact_implementation_paths_and_source_hashes`; `::test_adapter_registry_rejects_one_field_mutations[*]`; `::test_unsupported_ecosystem_has_no_hand_command_fallback` | Covered |
| 6 | Profiling budgets/order/diversity/outcome-blind + retain failures | `tests/p3_v3/test_bridge_and_frames.py::test_profiling_workload_selection_is_balanced_and_outcome_blind`; `::test_profiling_workload_prefers_unseen_diversity_then_behavior_id`; failure retention via `::test_classify_technique_is_category_equal_not_row_weighted` | Covered |
| 7 | Category-balanced technique intervals; failed rows kept; robust winner or `TECH_UNCERTAIN` | `tests/p3_v3/test_bridge_and_frames.py::test_classify_technique_is_category_equal_not_row_weighted`; `::test_classify_technique_requires_success_in_every_selected_category`; `::test_classify_technique_overlapping_intervals_are_uncertain`; `::test_classify_technique_strict_lower_bound_winner`; `::test_classify_technique_tie_breaks_with_frozen_technique_order`; `::test_classify_technique_is_result_order_invariant` | Covered |
| 8 | `E_COMMON` 30 ordinals before contracts/sites; registry round-robin; no forbidden material | `tests/p3_v3/test_bridge_and_frames.py::test_input_generator_registry_binds_exact_five_e_common_ids_and_source_hashes`; `::test_build_common_inputs_ordinals_seeds_dedupe_and_round_robin`; `::test_build_common_inputs_rejects_forbidden_generator_inputs`; `::test_generator_failure_occupies_ordinal_as_common_input_invalid`; `::test_zero_eligible_schemas_yield_thirty_unavailable_rows`; `::test_validate_common_inputs_on_fixed_source_preserves_identities` | Covered |
| 9 | Applicable slot materializes five `E_CONTRACT`; unsupported domain unavailable; inapplicable path closed | `tests/p3_v3/test_bridge_and_frames.py::test_close_slot_two_paths_not_applicable_or_site_frozen`; `::test_build_contract_inputs_five_ordinals_seeds_and_named_generator`; `::test_unsupported_domain_yields_five_contract_input_unavailable`; `::test_build_contract_inputs_rejects_not_applicable_slot` | Covered |
| 10 | Primary job rejects contract/witness confusion; sensitivity rejects role confusion | `tests/p3_v3/test_run_records.py::test_primary_controlled_and_p12_jobs_require_e_common`; `::test_contract_sensitivity_requires_e_contract`; `::test_rejects_profiling_or_certification_witness_input_classes`; `tests/p3_v3/test_packages.py::test_primary_package_b_rejects_contract_sensitivity`; `::test_sensitivity_package_b_rejects_primary_and_contract_confusion` | Covered |
| 11 | Unexecuted static site is `UNPROFILED`; only failed static semantic predicate → `NOT_APPLICABLE` | `tests/p3_v3/test_bridge_and_frames.py::test_unexecuted_static_site_is_unprofiled_not_not_applicable`; `::test_only_failed_static_semantic_predicate_yields_not_applicable` (independent reconstruction asserted); also exercised in `tests/p3_v3/test_synthetic_phase_path.py::test_synthetic_phase0_to_phase7_evidence_path` | Covered |
| 12 | `controlled_subject_id` stable across aliases; conflicting source/build/workload fails; site_id change does not alter stratum | `tests/p3_v3/test_bridge_and_frames.py::test_subject_frames_are_input_order_invariant_and_use_subject_id`; `::test_subject_frame_rejects_missing_feature_record`; `::test_build_subject_frames_prefers_technique_profile_over_feature_label` | Covered |
| 13 | `C_CONSTRUCT` order-invariant; neutral-ID independent; exact tie order | `tests/p3_v3/test_bridge_and_frames.py::test_construct_selection_continues_strict_round_robin_by_cell`; `::test_subject_frames_are_input_order_invariant_and_use_subject_id` | Covered |
| 14 | `C_CRITERION` includes every unique eligible controlled subject; no sampling path | `tests/p3_v3/test_bridge_and_frames.py::test_subject_frames_are_input_order_invariant_and_use_subject_id` (`c_criterion` assertion) | Covered |
| 15 | Custodian workloads cannot influence selection; first applicable site or `NOT_APPLICABLE` | `tests/p3_v3/test_bridge_and_frames.py::test_slot_selects_first_applicable_canonical_site_or_none`; `::test_close_slot_two_paths_not_applicable_or_site_frozen`; `::test_profiling_workload_selection_is_balanced_and_outcome_blind` | Covered |
| 16 | Slot chronology: `E_COMMON` before sites/contracts; `E_CONTRACT` before patch; consumers reject forbidden material | `tests/p3_v3/test_bridge_and_frames.py::test_verify_slot_chronology_accepts_exactly_one_of_two_paths`; `::test_inapplicable_slot_carrying_downstream_artifacts_fails`; `::test_applicable_slot_missing_e_contract_before_patch_fails`; `::test_post_patch_witness_in_either_input_inventory_fails` | Covered |
| 17 | Candidate-MR → custodian receipt → final inventory → portfolios exact order | `tests/p3_v3/test_cli.py::test_verify_mr_inventory_accepts_exact_chronology`; MR validation in `tests/p3_v3/test_synthetic_phase_path.py::test_synthetic_phase0_to_phase7_evidence_path`; source invariant `validate_mr_inventory` in `src/p3_v3/bridge_and_frames.py` | Covered |
| 18 | Proposal records reject missing prompt/context/response hashes; use literal `UNAVAILABLE_NOT_CLAIMED` | `tests/p3_v3/test_bridge_and_frames.py::test_proposal_record_rejects_missing_hashes_and_fabricated_provider_parameters`; proposal acceptance in synthetic path | Covered |
| 19 | Package A/B forbidden content and Package C early presence fail | `tests/p3_v3/test_packages.py::test_package_role_rejects_holdout_content_in_package_a`; `::test_package_c_classes_remain_forbidden_from_a_and_b`; `tests/p3_v3/test_preflight.py::test_preflight_rejects_package_c_path_in_ab_before_smoke[*]` | Covered |
| 20 | Job cannot produce result without earlier immutable intent | `tests/p3_v3/test_run_records.py::test_result_requires_existing_intent`; `::test_intent_and_result_are_exclusive`; `::test_result_identity_must_match_intent` | Covered |
| 21 | Failed/interrupted/inconclusive jobs survive reduction | `tests/p3_v3/test_run_records.py::test_reducer_retains_failed_attempt_before_success`; `::test_reducer_rejects_noncontiguous_or_scientific_retry` | Covered |
| 22 | Phase 7 denominator/`P12_PAIRED` immutable after outcomes; lower/upper/complete-case frozen rules | `tests/p3_v3/test_run_records.py::test_freeze_p12_denominator_before_results_and_summary_covers_five_outcomes`; `::test_p12_denominator_rejects_role_membership_and_reweight_mutations`; `::test_phase7_p12_result_requires_scientific_outcome_and_others_forbid_it` | Covered |
| 23 | Ledger suffix truncation detected by phase-close receipt | `tests/p3_v3/test_run_records.py::test_phase_close_rejects_pending_and_then_binds_complete_ledger`; `::test_ledger_tampering_breaks_event_hash`; `::test_ledger_rejects_rehashed_non_digest_artifact_identity` | Covered |
| 24 | Corrected preflight can pass without modifying scientific ledger | `tests/p3_v3/test_preflight.py::test_corrected_preflight_passes_without_intent_or_ledger_mutation`; `::test_preflight_passes_without_creating_scientific_intent`; `::test_preflight_module_does_not_import_create_intent` | Covered |
| 25 | Synthetic Phase 0→Phase 7 path verifies commitment opening, pairing, missingness estimand | `tests/p3_v3/test_synthetic_phase_path.py::test_synthetic_phase0_to_phase7_evidence_path` | Covered |

**Section 12 blocking gaps:** none.

## Section 13 — Acceptance criteria 1–20

| # | Criterion | Exact pytest node ID(s) and/or source invariant | Status |
|---|-----------|--------------------------------------------------|--------|
| 1 | P12 bridge authenticated, complete, exact-version verifiable | `tests/p3_v3/test_bridge_and_frames.py::test_bridge_is_read_from_exact_pinned_git_release`; CLI `verify-bridge` in synthetic path | Covered |
| 2 | Visible bridge discloses no fixed tree OID; reveal opens commitment/source | `tests/p3_v3/test_bridge_and_frames.py::test_visible_bridge_rejects_fixed_tree_oid_even_when_rehashed`; `::test_reveal_binds_nonce_oid_commitment_and_normalized_source`; synthetic reveal step | Covered |
| 3 | Public behavior frame regenerates from permitted evidence; retains missing/unsupported/invalid | `tests/p3_v3/test_bridge_and_frames.py::test_public_behavior_frame_accounts_all_categories_and_retains_unsupported`; `::test_public_behavior_frame_is_input_order_invariant`; CLI `build-frames` writes `public-behavior-frame.json` (`tests/p3_v3/test_cli.py::test_build_frames_writes_declared_artifacts_under_output_root_only`) | Covered |
| 4 | Profiling workload exact registry/budgets/round-robin/diversity; byte-identical; failure funnel | `tests/p3_v3/test_bridge_and_frames.py::test_profiling_workload_selection_is_balanced_and_outcome_blind`; `::test_profiling_workload_prefers_unseen_diversity_then_behavior_id` | Covered |
| 5 | Technique classification category-equal; never drops failed rows; `TECH_UNCERTAIN` when needed | classify-technique suite listed under Section 12 test 7 | Covered |
| 6 | 30 `E_COMMON` before sites/contracts; applicable slot five `E_CONTRACT` before patch | Section 12 tests 8–9 node IDs; synthetic path freezes 30 common + 5 contract rows | Covered |
| 7 | Terminal slot paths reject contract/input/patch for `NOT_APPLICABLE`; reject missing `E_CONTRACT` for applicable | `tests/p3_v3/test_bridge_and_frames.py::test_inapplicable_slot_carrying_downstream_artifacts_fails`; `::test_applicable_slot_missing_e_contract_before_patch_fails`; `::test_verify_slot_chronology_accepts_exactly_one_of_two_paths` | Covered |
| 8 | Input inventories cannot alter profiles/strata/site order; no post-patch witness in inventories | `tests/p3_v3/test_bridge_and_frames.py::test_build_common_inputs_rejects_forbidden_generator_inputs`; `::test_post_patch_witness_in_either_input_inventory_fails`; `::test_profiling_workload_selection_is_balanced_and_outcome_blind` | Covered |
| 9 | Profile coverage/`UNPROFILED` funnels bound dynamic claims; unobserved ≠ `NOT_APPLICABLE` | `tests/p3_v3/test_bridge_and_frames.py::test_unexecuted_static_site_is_unprofiled_not_not_applicable`; `::test_only_failed_static_semantic_predicate_yields_not_applicable` | Covered |
| 10 | Subject frames and site enumerations regenerate byte-identically from shuffled inputs | `tests/p3_v3/test_bridge_and_frames.py::test_subject_frames_are_input_order_invariant_and_use_subject_id`; `::test_public_behavior_frame_is_input_order_invariant` | Covered |
| 11 | Contracts/input identities phase-close in declared chronology before candidate-MR/first job | Slot chronology suite + `tests/p3_v3/test_cli.py::test_verify_mr_inventory_accepts_exact_chronology`; synthetic path order | Covered |
| 12 | Reference MRs/semantic duplicates cannot enter portfolios; chronology proven | `validate_mr_inventory` chronology enforcement + `tests/p3_v3/test_cli.py::test_verify_mr_inventory_accepts_exact_chronology` | Covered |
| 13 | Package A and B materialize/verify without forbidden content | `tests/p3_v3/test_packages.py::*`; Package A/B primary/sensitivity/proposer views in synthetic path | Covered |
| 14 | Repeatable preflight completes actual synthetic end-to-end CLI path | `tests/p3_v3/test_synthetic_phase_path.py::test_synthetic_phase0_to_phase7_evidence_path` (`run-preflight` with Task 8 fields); `tests/p3_v3/test_preflight.py::test_preflight_passes_without_creating_scientific_intent` | Covered |
| 15 | Scientific intent precedes every synthetic job side effect | `tests/p3_v3/test_run_records.py::test_result_requires_existing_intent`; synthetic path `create_intent` before `write_result` | Covered |
| 16 | Phase close detects missing/duplicate/pending/truncated records | `tests/p3_v3/test_run_records.py::test_phase_close_rejects_pending_and_then_binds_complete_ledger`; `::test_ledger_tampering_breaks_event_hash`; CLI `close-phase`/`verify-run-records` in synthetic path | Covered |
| 17 | All claim entries remain blocked until result predicates are implemented | `tests/p3_v3/test_cli.py::test_verify_evidence_validates_complete_evidence_set` (`claims_status == blocked`); synthetic path asserts every claim `blocked`; protocol `claims_initial_status` invariant in `validate_protocol` | Covered |
| 18 | RQ4 inference limited to frozen `P12_PAIRED`; lower-bound primary; upper/complete-case + unresolved counts | `tests/p3_v3/test_run_records.py::test_freeze_p12_denominator_before_results_and_summary_covers_five_outcomes`; `::test_p12_denominator_rejects_role_membership_and_reweight_mutations`; synthetic summary regeneration | Covered |
| 19 | Focused and repository test suites pass | Focused: `129 passed` under `tests/p3_v3`; repository: `609 passed` under `pytest -q` | Covered |
| 20 | No live P12 Holdout, real outcome, or Cursor launch used | Synthetic-only fixtures; `tests/p3_v3/test_synthetic_phase_path.py` autouse socket block (`create_connection`/`getaddrinfo`); no network/real P12/mutant/MR in suite | Covered |

**Section 13 blocking gaps:** none.

## CLI command surface (frozen ten)

Verified by `tests/p3_v3/test_cli.py::test_cli_help_lists_only_frozen_commands`:

`validate-protocol`, `verify-bridge`, `build-frames`, `verify-mr-inventory`, `build-package`, `verify-package`, `run-preflight`, `verify-run-records`, `close-phase`, `verify-evidence`.

## Notes

- Tests 11 and 18 were the Task 9 blocking gaps; both now have dedicated independent-reconstruction tests plus synthetic-path exercise.
- `verify-evidence` validates protocol, manifests, ledger, phase receipts, slot chronology, common-input roles, denominator, P12 summary binding, and blocked claims as one evidence set (`tests/p3_v3/test_cli.py::test_verify_evidence_validates_complete_evidence_set`).
- No self-declared-only rows remain for Section 12 or 13.
