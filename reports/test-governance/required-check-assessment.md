# Required-check assessment

As of 2026-11-06. Scope: the entire required estate, with targeted source comparison for proposed retirements. Existing measured run: 172 expanded pytest cases, 285.51 seconds. Historical baselines and judgments remain unchanged. This is not a claim that every retained scenario is minimally sufficient or has a measured marginal benefit.

## Decisions and uncertainty

Two proved low-value functions are retired below; one real-worker regression is admitted. Every other scenario remains executable. Screening found distinct risk-bearing boundaries, but did not establish all-pairs nonredundancy or a quantitative confidence gain for each assertion. Generic historical retention claims are not upgraded into evidence. In particular, large orchestration/migration scenarios and source-wording checks need contract-specific follow-up before further retirement; uncertainty means retain. No deletion quota, bulk mutation survey or independent methodology review is introduced.

The preservation assessment is primary-owned under the constitution. For each removed scenario the comparison includes its actual preconditions, oracle and nearest keeper. Untouched keepers require no new witness. New scheduling assertions receive real-worker causal controls and append-only admission.

## Retirements

- `pytest:tests/test_test_governance.py::test_parameterized_leaves_collapse_to_one_family`: consolidate. The direct helper string example has no additional boundary. The keeper inventories a real fixture with two parameterized leaves and asserts both collapsed family and expanded leaf counts. Leaving parameter suffixes intact breaks its family counts. No keeper assertion is added. Replacement: `pytest:tests/test_test_governance.py::test_inventory_counts_executable_families_and_expanded_leaves`.
- `pytest:tests/test_research_authority.py::test_policy_is_allow_by_default_without_assuming_any_named_server`: delete. Four phrase-presence assertions do not establish the policy semantics. Generated-command tests already check actual available capabilities and emitted directives for all roles; template-only contract checks retain the relevant rule/transfer coverage. The removed wording test adds no independent behavioral oracle; a harmless wording change could fail it. No security guard is removed.

## Gate applicability

| Required boundary | Applicability and reason |
|---|---|
| Lint and formatting | Language-adapted; reject actual source defects/invalid syntax and candidate rewriting. Exact style choices alone are not a confidence claim. |
| Full tests and supervised receipt | Universal for adopted test/delivery contracts; incomplete work, lost selected tests or stale receipts must not qualify delivery. |
| Log/phase and candidate partition | Universal for the adopted immutable record and candidate-classification contracts; wrong custody or omitted source changes invalidate acceptance. |
| Harness parity, configuration and toolchain callers | Universal while these shipped adapters exist; missing links, wrong role budgets or ambient interpreters can execute different authority. |
| Catalog, lesson and treatise validation | Universal while their writers/readers are shipped; independent shape/reference checks prevent silent corrupt records. Their capability behavior is tested separately. |
| Execution dashboard validation | Universal for adopted report machinery; archive/privacy integrity is distinct from a synthetic renderer regression. |
| Shell syntax and hook liveness | Universal for shipped shell/hooks; parse errors and an opted-in but displaced hook are separate silent failures. Hooks remain opt-in. |
| Documentation build | Universal for the shipped manual contract; live links/assets must work. Publication activation remains optional; deploy tests guard the shipped inactive-capable command. |
| Proof governance | Universal for governed selection/retirement; live inventory must agree with append-only judgments and actual witness bytes. |
| Timing report | Diagnostic only, never a performance correctness gate. Unknown timing is not zero and is not a reason to reject correct code. |
| Anonymization and template/history proofs | Starter-only. They protect this distributable template and its real history and are excluded from recipients. |
| Deliverable build, platform and publication gates | Conditional on the explicitly declared shipped capability; adapt at stamp time with its full dependency closure. No missing-file skip or default donor product test is justified. |

## Source screening and retained cost

The following table covers every current source module; the scenario inventory afterward ties every pre-change identifier to its disposition. Costs are summed per-case durations from one retained serial run, not benchmark estimates or independent confidence measurements.

| Module | Credible boundary risk / independent confidence | Serial seconds | Disposition / applicability |
|---|---|---:|---|
| `project/tests/test_cli.py` | The seeded deliverable must execute its public CLI through the package, not merely import. | 0.00 | Retain except named retirements; Portable while the owning capability is adopted; deliverable tests are rewritten for that product. |
| `project/tests/test_hermeticity.py` | An absent egress guard silently turns routine tests into external operations. | 0.00 | Retain except named retirements; Portable while the owning capability is adopted; deliverable tests are rewritten for that product. |
| `tests/test_check.py` | Gate composition, selected lanes, candidate immutability and failures must not issue false success. | 1.56 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_check_catalogs.py` | Broken references and misbound phase identities can make authority disappear or be misread. | 11.46 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_check_hooks_installed.py` | Unset opt-in and silently repointed hooks must remain distinguishable without ambient Python. | 0.16 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_check_plan_concreteness.py` | Unresolved identifiers and line ranges must be refused before a model dispatch. | 0.57 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_check_plan_delivery.py` | Unimplemented commitments or intentional deletions must not be misclassified by delivery checks. | 0.26 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_check_receipt.py` | A dirty, changed, corrupt or incomplete candidate must not reuse a passing delivery receipt. | 2.65 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_documentation.py` | Curated manuals must not expose private inputs or deploy a different release than approved. | 0.02 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_execution_dashboard.py` | Offline reports must preserve wait unions, identities and privacy, including named phases. | 0.19 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_execution_telemetry.py` | Concurrent writes, cross-boot clocks and process cleanup must not manufacture successful evidence. | 5.53 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_install_hooks.py` | Explicit installation must actually select the tracked hooks and remain idempotent. | 0.07 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_kickoff_config.py` | Real generated CLI arguments, bounded watches and registered sessions must preserve authority and lineage. | 24.01 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_kickoff_control_plane.py` | A runner must not start against an unadmitted command or authority manifest. | 0.22 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_kickoff_evidence.py` | Acceptance must join actual candidates, role attempts, findings, retained bytes and consumed budgets. | 157.83 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_kickoff_tree_id.py` | Candidate identity and classification must not depend on cwd or omit declared source changes. | 1.78 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_lessons.py` | Writing/recurring a lesson must preserve archived disposition, body bytes and attribution. | 0.56 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_log_control_plane.py` | Record conversion must preserve the shared terminal normalization behavior. | 0.14 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_methodology_toolchain_contract.py` | A template change must not copy broken dependency closures or omit required portable tools. | 6.82 | Retain except named retirements; Starter-only. |
| `tests/test_mirror_parity.py` | Generated mirrors must point to actual canonical resources and refuse custom/unsafe overwrites. | 0.78 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_multioperator.py` | Migration and maintenance must preserve histories, refuse false completion and validate ownership. | 14.34 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_mutation.py` | An opt-in survey must distinguish actual measurement, partial work, unavailability and failure. | 7.28 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_new_name.py` | Names must not collide with archived or active records across independently owned queues. | 0.25 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_pre_commit.py` | Staged candidate/proof invalidity must be detected without being masked by a later check. | 0.17 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_research_authority.py` | Generated commands must carry the declared role capabilities without inventing resources. | 0.61 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_review_verdicts.py` | Harvesting must avoid template echoes, excluded sessions and duplicate findings. | 0.17 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_shell_syntax.py` | The syntax checker must detect a real interpreter error and attribute its file. | 0.06 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_starter_migration_history.py` | The template itself must still convert its genuine historical corpus; this cannot travel. | 19.28 | Retain except named retirements; Starter-only. |
| `tests/test_test_governance.py` | Selections and evidence must reflect the actual executable estate, truthful failures and retained bytes. | 27.79 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_toolchain_callers.py` | Repository workflows must use the declared locked runtime instead of ambient interpreters. | 0.14 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_toolchain_entrypoints.py` | Installed symlink launch, runtime overrides and focused routes must select the owning repository. | 0.40 | Retain except named retirements; Portable for the shipped owning contract. |
| `tests/test_treatise.py` | Editorial metadata must retain unrelated content and refuse unsupported external-fact freshness claims. | 0.24 | Retain except named retirements; Portable for the shipped owning contract. |

## Complete pre-change scenario disposition

Identifiers are evidence joins, not value scores. A retain row means the executable stays under the source-screening rationale above, with marginal-value uncertainty preserved; it does not manufacture an observed witness. Gate/hook rows remain independently inventoried because runtime checking of the real candidate differs from synthetic tool tests.

| Scenario | Decision |
|---|---|
| `pytest:project/tests/test_cli.py::test_main_hello_default` | retain |
| `pytest:project/tests/test_hermeticity.py::test_real_network_egress_fails_loudly` | retain |
| `pytest:tests/test_check.py::test_all_is_default_locked_ordered_and_cwd_independent` | retain |
| `pytest:tests/test_check.py::test_all_policy_failure_cannot_be_masked_by_later_policy_output` | retain |
| `pytest:tests/test_check.py::test_format_rejects_staged_unstaged_and_untracked_candidates_without_rewriting` | retain |
| `pytest:tests/test_check.py::test_invalid_invocation_is_usage_error[arguments0]` | retain |
| `pytest:tests/test_check.py::test_invalid_invocation_is_usage_error[arguments1]` | retain |
| `pytest:tests/test_check.py::test_invalid_invocation_is_usage_error[arguments2]` | retain |
| `pytest:tests/test_check.py::test_invalid_invocation_is_usage_error[arguments3]` | retain |
| `pytest:tests/test_check.py::test_governed_iteration_lanes_dispatch_selected_tests_without_receipt[arguments0---tier vital --format lines]` | retain |
| `pytest:tests/test_check.py::test_governed_iteration_lanes_dispatch_selected_tests_without_receipt[arguments1---changed-from HEAD~1 --format lines]` | retain |
| `pytest:tests/test_check.py::test_authoritative_runtime_probe_failure_stops_before_gate_without_fallback` | retain |
| `pytest:tests/test_check.py::test_interrupted_tests_cannot_issue_a_passing_gate_receipt` | retain |
| `pytest:tests/test_check_catalogs.py::test_tracked_markdown_deleted_from_worktree_is_not_read_as_a_source` | retain |
| `pytest:tests/test_check_catalogs.py::test_structured_phase_order_and_events_are_checked_by_the_catalog` | retain |
| `pytest:tests/test_check_catalogs.py::test_a_phase_names_other_phases_by_id_and_a_path_is_refused` | retain |
| `pytest:tests/test_check_catalogs.py::test_missing_internal_inline_and_reference_links_are_reported` | retain |
| `pytest:tests/test_check_catalogs.py::test_the_citation_rule_is_directional_not_symmetric` | retain |
| `pytest:tests/test_check_catalogs.py::test_prospective_child_close_requires_real_parent_disposition` | retain |
| `pytest:tests/test_check_catalogs.py::test_imported_links_use_exact_git_history_without_legacy_aliases` | retain |
| `pytest:tests/test_check_hooks_installed.py::test_wrong_hooks_path_fails` | retain |
| `pytest:tests/test_check_hooks_installed.py::test_this_repository_passes_its_own_witness` | retain |
| `pytest:tests/test_check_plan_concreteness.py::test_unread_identifier_refuses_and_declared_new_passes` | retain |
| `pytest:tests/test_check_plan_concreteness.py::test_node_ids_and_line_ranges_resolve_to_members` | retain |
| `pytest:tests/test_check_plan_delivery.py::test_undeclared_narrowing_still_fails_with_a_report` | retain |
| `pytest:tests/test_check_plan_delivery.py::test_a_planned_deletion_is_delivered_when_the_file_is_gone` | retain |
| `pytest:tests/test_check_receipt.py::test_passed_run_is_durable_and_reusable_for_exact_clean_head` | retain |
| `pytest:tests/test_check_receipt.py::test_tampered_log_never_reuses_receipt` | retain |
| `pytest:tests/test_check_receipt.py::test_candidate_drift_is_terminal_and_never_creates_a_receipt` | retain |
| `pytest:tests/test_check_receipt.py::test_pre_push_hook_skips_only_a_verified_hit` | retain |
| `pytest:tests/test_documentation.py::test_curated_source_refuses_escape_and_private_inputs` | retain |
| `pytest:tests/test_documentation.py::test_generated_output_checks_links_assets_anchors_and_private_paths` | retain |
| `pytest:tests/test_documentation.py::test_deploy_binds_clean_latest_release_and_preserves_manual_mode` | retain |
| `pytest:tests/test_documentation.py::test_setup_installs_exact_versions_locally_without_global_upgrade` | retain |
| `pytest:tests/test_documentation.py::test_release_ci_requires_committed_publication_identity` | retain |
| `pytest:tests/test_execution_dashboard.py::test_payload_reports_each_operator_park_and_nonexact_total` | retain |
| `pytest:tests/test_execution_dashboard.py::test_render_is_byte_identical_and_recovers_interrupted_replacement` | retain |
| `pytest:tests/test_execution_dashboard.py::test_handoff_schema_rejects_private_or_malformed_content[<lambda>-private]` | retain |
| `pytest:tests/test_execution_dashboard.py::test_handoff_schema_rejects_private_or_malformed_content[<lambda>-kind]` | retain |
| `pytest:tests/test_execution_dashboard.py::test_handoff_schema_rejects_private_or_malformed_content[<lambda>-phase]` | retain |
| `pytest:tests/test_execution_dashboard.py::test_handoff_schema_rejects_private_or_malformed_content[<lambda>-unknown]` | retain |
| `pytest:tests/test_execution_dashboard.py::test_handoff_schema_rejects_private_or_malformed_content[<lambda>-missing fields]` | retain |
| `pytest:tests/test_execution_dashboard.py::test_handoff_schema_rejects_private_or_malformed_content[<lambda>-nonempty]` | retain |
| `pytest:tests/test_execution_dashboard.py::test_handoff_schema_rejects_private_or_malformed_content[<lambda>-out-of-scope]` | retain |
| `pytest:tests/test_execution_dashboard.py::test_content_scan_blanks_operation_labels_and_nothing_else` | retain |
| `pytest:tests/test_execution_dashboard.py::test_inline_planning_and_coding_are_attributed_to_their_activities` | retain |
| `pytest:tests/test_execution_dashboard.py::test_named_phase_identity_waits_and_reader_refusals` | retain |
| `pytest:tests/test_execution_telemetry.py::test_operator_park_open_close_is_idempotent_exact_and_fail_closed` | retain |
| `pytest:tests/test_execution_telemetry.py::test_operator_park_recovers_missing_runtime_state_and_marks_cross_boot` | retain |
| `pytest:tests/test_execution_telemetry.py::test_operator_park_exact_intervals_union_overlaps` | retain |
| `pytest:tests/test_execution_telemetry.py::test_lifecycle_idempotency_finalization_and_crash_recovery` | retain |
| `pytest:tests/test_execution_telemetry.py::test_atomic_state_and_first_ledger_creation_fsync_directories` | retain |
| `pytest:tests/test_execution_telemetry.py::test_concurrent_process_mutations_do_not_lose_spans` | retain |
| `pytest:tests/test_execution_telemetry.py::test_group_termination_escalates_when_descendant_ignores_sigterm` | retain |
| `pytest:tests/test_execution_telemetry.py::test_cli_malformed_ledger_fails_closed_without_traceback` | retain |
| `pytest:tests/test_install_hooks.py::test_install_is_idempotent` | retain |
| `pytest:tests/test_kickoff_config.py::test_show_validates_seed_config` | retain |
| `pytest:tests/test_kickoff_config.py::test_scoped_edit_preserves_extensions_comments_and_timeouts` | retain |
| `pytest:tests/test_kickoff_config.py::test_invalid_edit_is_atomic` | retain |
| `pytest:tests/test_kickoff_config.py::test_watch_extracts_fresh_claude_result_and_telemetry` | retain |
| `pytest:tests/test_kickoff_config.py::test_timeout_kills_descendant_after_group_leader_exits` | retain |
| `pytest:tests/test_kickoff_config.py::test_watch_preserves_codex_artifact_when_terminal_stream_is_incomplete` | retain |
| `pytest:tests/test_kickoff_config.py::TestGeneratedInvocationRecipes::test_claude_coder_is_the_only_write_enabled_role` | retain |
| `pytest:tests/test_kickoff_config.py::test_preflight_still_aborts_on_a_failed_sentinel` | retain |
| `pytest:tests/test_kickoff_config.py::test_cap_hit_continuation_requires_assessment_and_preserves_budget[productive]` | retain |
| `pytest:tests/test_kickoff_config.py::test_cap_hit_continuation_requires_assessment_and_preserves_budget[verdict]` | retain |
| `pytest:tests/test_kickoff_config.py::test_watch_registered_review_durability_and_child_environment` | retain |
| `pytest:tests/test_kickoff_control_plane.py::test_manifest_preflight_and_runner_admission_fail_closed` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_primary_continuation_carries_original_predecessors[1]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_primary_continuation_carries_original_predecessors[2]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_primary_continuation_refuses_unproved_predecessors` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_change_manifest_is_candidate_bound_and_detects_authority_drift` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_finding_state_is_stable_validated_and_reopen_is_counted` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_role_artifacts_feed_findings_and_change_metadata_without_reparsing` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_revision_round_requires_and_carries_failure_analysis` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_final_validation_rejects_blocking_findings[open]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_final_validation_rejects_blocking_findings[addressed]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_final_validation_rejects_blocking_findings[blocked-owner]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_validate_detects_corrupt_evidence` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_complete_synthetic_kickoff_cross_validates_roles_revision_and_gates` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_primary_mode_kickoff_records_advice_dispositions_and_stale_acceptance` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_child_close_moves_a_stranded_next_marker_only_in_pairs` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_nested_final_child_close_requires_an_accepted_parent_chain` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_owner_exception_uses_pinned_watcher_and_acceptance` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_owner_exception_budget_is_scoped_atomic_and_auditable` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_advice_attestation_preserves_originals[historical-gap]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_advice_attestation_refuses_unfaithful_evidence[self-historical-gap]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_advice_attestation_refuses_unfaithful_evidence[wrong-phase-historical-gap]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_advice_attestation_refuses_unfaithful_evidence[missing-claim-historical-gap]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_advice_attestation_refuses_unfaithful_evidence[not-earlier-historical-gap]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_advice_attestation_refuses_unfaithful_evidence[wrong-candidate-historical-gap]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_advice_attestation_refuses_unfaithful_evidence[missing-span-historical-gap]` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_registrar_refuses_gap_before_any_dispatch` | retain |
| `pytest:tests/test_kickoff_evidence.py::test_historical_distinct_role_predecessors[historical-two-roles]` | retain |
| `pytest:tests/test_kickoff_tree_id.py::test_identity_is_cwd_independent_and_manifest_is_ordered` | retain |
| `pytest:tests/test_lessons.py::test_valid_open_and_archived_lessons_pass` | retain |
| `pytest:tests/test_lessons.py::test_codified_lesson_requires_graduated_to` | retain |
| `pytest:tests/test_lessons.py::test_candidates_applies_graduation_threshold_to_open_lessons_only` | retain |
| `pytest:tests/test_lessons.py::test_aged_lists_open_lessons_with_no_new_occurrence_in_sixty_days` | retain |
| `pytest:tests/test_log_control_plane.py::test_shared_normalization_survives_record_migration` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_proof_estate_governance_propagates_without_local_judgments` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_every_universal_skill_propagates_with_its_codex_mirror` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_the_mechanical_copy_is_closed_over_links_and_fixtures` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_every_gate_required_executable_propagates` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_research_authority_contract_propagates_and_stays_allow_by_default` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_material_review_counts_are_reproducible` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_leak_scan_reads_new_files_before_they_are_staged` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_rust_profile_owns_output_across_checkouts` | retain |
| `pytest:tests/test_methodology_toolchain_contract.py::test_travelling_migration_proofs_run_without_donor_history` | retain |
| `pytest:tests/test_mirror_parity.py::test_repository_is_in_parity` | retain |
| `pytest:tests/test_multioperator.py::test_portable_rehearsal_preserves_source_and_guards` | retain |
| `pytest:tests/test_multioperator.py::test_transition_and_maintenance_refuse_false_state` | retain |
| `pytest:tests/test_multioperator.py::test_constitution_version_gate_and_loading_limits` | retain |
| `pytest:tests/test_mutation.py::test_a_survey_reports_the_faults_tests_miss_on_the_changed_lines` | retain |
| `pytest:tests/test_mutation.py::test_a_repository_with_no_tool_reports_unmeasured_and_never_measured` | retain |
| `pytest:tests/test_mutation.py::test_a_survey_that_cannot_be_taken_fails_and_an_unfinished_one_is_partial` | retain |
| `pytest:tests/test_new_name.py::test_avoids_collisions_across_all_ledger_dirs` | retain |
| `pytest:tests/test_pre_commit.py::test_pre_commit_runs_structural_governance_after_existing_checks` | retain |
| `pytest:tests/test_research_authority.py::test_generated_commands_enforce_the_role_authority_matrix` | retain |
| `pytest:tests/test_research_authority.py::test_retrieval_only_roles_reject_originating_search_budget` | retain |
| `pytest:tests/test_research_authority.py::test_policy_is_allow_by_default_without_assuming_any_named_server` | delete |
| `pytest:tests/test_review_verdicts.py::test_dedupes_across_harnesses_and_drops_template_echoes` | retain |
| `pytest:tests/test_review_verdicts.py::test_running_session_and_explicit_exclusions_are_skipped` | retain |
| `pytest:tests/test_shell_syntax.py::test_syntax_error_fails_with_named_file` | retain |
| `pytest:tests/test_starter_migration_history.py::test_actual_starter_rehearsal_preserves_source_and_history` | retain |
| `pytest:tests/test_test_governance.py::test_parameterized_leaves_collapse_to_one_family` | consolidate |
| `pytest:tests/test_test_governance.py::test_inventory_counts_executable_families_and_expanded_leaves` | retain |
| `pytest:tests/test_test_governance.py::test_live_reset_validates` | retain |
| `pytest:tests/test_test_governance.py::test_runtime_is_diagnostic_and_stale_records_are_unmeasured` | retain |
| `pytest:tests/test_test_governance.py::test_incomplete_disposition_evidence_fails_closed` | retain |
| `pytest:tests/test_test_governance.py::test_shadow_deleted_proof_fails_closed` | retain |
| `pytest:tests/test_test_governance.py::test_critical_risk_requires_a_retained_direct_proof` | retain |
| `pytest:tests/test_test_governance.py::test_lifecycle_replay_and_repairs` | retain |
| `pytest:tests/test_test_governance.py::test_changed_selection_maps_documents_to_readers_and_widens_on_unmapped_code` | retain |
| `pytest:tests/test_test_governance.py::test_changed_code_selects_the_families_of_files_that_use_it` | retain |
| `pytest:tests/test_test_governance.py::test_report_counts_the_frozen_baseline_and_current_estate` | retain |
| `pytest:tests/test_test_governance.py::test_a_mutation_declaration_names_its_tool_scope_and_budget_or_says_why_not` | retain |
| `pytest:tests/test_test_governance.py::test_witness_observes_red_restores_exactly_and_records_a_receipt` | retain |
| `pytest:tests/test_test_governance.py::test_witness_refuses_anything_short_of_the_named_failure` | retain |
| `pytest:tests/test_test_governance.py::test_witness_expect_must_appear_in_a_declared_failure_line` | retain |
| `pytest:tests/test_test_governance.py::test_a_pending_witness_blocks_validation_until_it_is_aborted` | retain |
| `pytest:tests/test_test_governance.py::test_receipts_are_validated_and_an_admitted_proof_must_have_one` | retain |
| `pytest:tests/test_test_governance.py::test_bounded_adoption_reports_pending_without_discarding_proofs` | retain |
| `pytest:tests/test_test_governance.py::test_modification_must_reference_its_own_unreused_observation` | retain |
| `pytest:tests/test_test_governance.py::test_hang_supervision_preserves_failures_and_stops_chattering_children` | retain |
| `pytest:tests/test_test_governance.py::test_incomplete_exit_cannot_supply_a_red_witness` | retain |
| `pytest:tests/test_test_governance.py::test_governance_child_incomplete_remains_incomplete` | retain |
| `pytest:tests/test_test_governance.py::test_outstanding_child_makes_completed_leader_incomplete[0]` | retain |
| `pytest:tests/test_test_governance.py::test_outstanding_child_makes_completed_leader_incomplete[1]` | retain |
| `pytest:tests/test_test_governance.py::test_governance_allows_nested_supervisor_cleanup` | retain |
| `pytest:tests/test_test_governance.py::test_real_supervisor_entrypoint_handles_deadlines_and_signals[timeout]` | retain |
| `pytest:tests/test_test_governance.py::test_real_supervisor_entrypoint_handles_deadlines_and_signals[term]` | retain |
| `pytest:tests/test_test_governance.py::test_real_supervisor_entrypoint_handles_deadlines_and_signals[double-term]` | retain |
| `pytest:tests/test_test_governance.py::test_real_supervisor_entrypoint_handles_deadlines_and_signals[hup]` | retain |
| `pytest:tests/test_test_governance.py::test_real_supervisor_entrypoint_handles_deadlines_and_signals[completed-error]` | retain |
| `pytest:tests/test_toolchain_callers.py::test_repository_runtime_callers_pass` | retain |
| `pytest:tests/test_toolchain_callers.py::test_ambient_or_versioned_operational_callers_fail[bin/workflow-python3 bin/task\n]` | retain |
| `pytest:tests/test_toolchain_callers.py::test_ambient_or_versioned_operational_callers_fail[policies/procedure.md-python tests/tool.py\n]` | retain |
| `pytest:tests/test_toolchain_callers.py::test_ambient_or_versioned_operational_callers_fail[plan/phase.md-output | python3 -c 'print(1)'\n]` | retain |
| `pytest:tests/test_toolchain_callers.py::test_ambient_or_versioned_operational_callers_fail[proposals/open-change.md-python3 bin/task\n]` | retain |
| `pytest:tests/test_toolchain_callers.py::test_ambient_or_versioned_operational_callers_fail[web/vite.config.js-python3 web/scripts/generate.py\n]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_test_defaults_to_every_repository_test_from_any_cwd` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_installed_symlink_chain_selects_the_owning_repository[setup-arguments0]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_installed_symlink_chain_selects_the_owning_repository[test-arguments1]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_installed_symlink_chain_selects_the_owning_repository[python-arguments2]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_test_governed_lanes_run_selected_proofs[arguments0]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_test_governed_lanes_run_selected_proofs[arguments1]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_authoritative_runtime_override_is_used_for_probe_and_command[setup-arguments0]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_authoritative_runtime_override_is_used_for_probe_and_command[test-arguments1]` | retain |
| `pytest:tests/test_toolchain_entrypoints.py::test_authoritative_runtime_override_is_used_for_probe_and_command[python-arguments2]` | retain |
| `pytest:tests/test_treatise.py::test_an_external_fact_without_a_retrieval_date_fails` | retain |
| `pytest:tests/test_treatise.py::test_the_repository_own_treatises_validate` | retain |
| `gate:changed` | retain |
| `gate:format` | retain |
| `gate:lint` | retain |
| `gate:policy-anonymization` | retain |
| `gate:policy-candidate-partition` | retain |
| `gate:policy-catalogs` | retain |
| `gate:policy-config` | retain |
| `gate:policy-docs` | retain |
| `gate:policy-execution-dashboards` | retain |
| `gate:policy-harness-parity` | retain |
| `gate:policy-hooks-installed` | retain |
| `gate:policy-lessons` | retain |
| `gate:policy-log` | retain |
| `gate:policy-shell-syntax` | retain |
| `gate:policy-test-governance` | retain |
| `gate:policy-test-time` | retain |
| `gate:policy-toolchain-callers` | retain |
| `gate:policy-treatise` | retain |
| `gate:test` | retain |
| `gate:vital` | retain |
| `hook:.githooks/pre-commit:./bin/check-harness-parity` | retain |
| `hook:.githooks/pre-commit:./bin/check-toolchain-callers` | retain |
| `hook:.githooks/pre-commit:./bin/multioperator validate --root . --staged` | retain |
| `hook:.githooks/pre-commit:./bin/check-candidate-partition --staged` | retain |
| `hook:.githooks/pre-commit:./bin/test-governance validate` | retain |

## Execution and transfer boundaries

Top-level independent Python tests use locked pytest-xdist. Disposable roots are per-case temporary directories; process-spool fixtures are independently scoped. No current test requires a global serial group after screening. Existing fixture-internal operation sequences remain sequential because order is the behavior they test. Single-function diagnostics and nested wrapper calls run serially to avoid startup cost and recursive pools. Explicit pytest worker arguments remain available. Calibration and exact selected identity/outcome results are durable local evidence, not committed host-specific defaults.

The stamp copy rule prevents accidental omissions; the applicability assessment decides why a check belongs. Fresh recipients author their own product tests, proof baselines and judgment records. Template history tests, historical ledgers and local proof choices remain excluded. The portable synthetic floor must execute without donor history; collection alone is insufficient. Existing consumers are not changed by this assessment.

## Qualified execution result

The retained suite has 171 expanded pytest cases: two old functions retired and one real-worker regression admitted. Six causal controls establish independent scheduling, resource grouping, nested-pool control, no crashed-worker replacement and truthful failure/interruption. Two failed witness attempts remain preserved: test-call counts did not detect worker replacement, and a broad false-green mutant also corrupted its observer. Neither rejected attempt is counted as a successful control; actual node-start observation and an isolated fault boundary corrected them.

| Workers | Elapsed seconds including startup | Cases | Outcome |
|---:|---:|---:|---|
| 0 | 285.95 | 171 | PASS; identities identical |
| 2 | 145.51 | 171 | PASS; identities identical |
| 4 | 102.76 | 171 | PASS; identities identical |
| 18 | 52.11 | 171 | PASS; identities identical |

These are one bounded comparison on the same source, not a recurring benchmark or universal performance promise. Automatic CPU-based workers were the fastest qualified choice on this host; explicit worker selection remains available. Required single-function diagnostics and nested wrapper calls stay serial for startup cost and resource bounding. No global serial group was needed for the retained suite; resource groups remain supported and are exercised against a real shared fixture.

A zero-donor-history fixture executes the full travelling estate with its own baseline, empty witness ledger, new-project manifest and no imported acceptance. Its manual and catalogs are recipient-authored. The fixture exposed a template-specific manual-chapter link; the shared tool catalog now points to the required manual index instead. Original fixture setup/lint/catalog failures and all later results remain separate durable evidence. No actual receiving repository was edited or adopted.

The final isolated Python fixture passed all 161 applicable travelling cases and its full lint/format/policy/documentation gate. The case-identity set exactly equals the retained source suite minus the two excluded template/history modules. Its locally generated baseline contains 185 test/gate/hook entries and zero imported witness receipts; it has one fixture genesis commit, no donor history and no remote. This does not claim native instruction loading, other language deployments or an actual receiving-project adoption.
