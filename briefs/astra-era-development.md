---
title: Astra-era development workflow
date: 2026-09-07
status: implemented
scope: local
---

# Astra-era development workflow

## Primary ownership and independent advice

As of 2026-09-07, the primary use case is a configured SOTA instance that owns orchestration, planning, implementation and acceptance. A comparable or stronger model in another permitted provider's harness normally supplies independent plan and code advice; a single-provider environment uses fresh instances of the primary model. One comprehensive pass per stage is normal, a second needs recorded cause, and two is the maximum. Advisers report evidence and severity without veto; the primary decides corrections and records consequential dispositions. Objective requirements and both full gates remain binding.

A constrained primary uses separate planner/coder roles and the established approval-gated reviewer/critic loops. Detailed references to mandatory reviewer approval or four-role delegation below describe that constrained product branch. Eligibility is maintained configuration, not a benchmark claim. Backend and handling restrictions prevail over preferred routing. Optional kickoff usage checks refuse a primary at >=95% of any applicable limit and substitute the primary for a secondary above 95% weekly; absent tooling does not prevent execution.

All methodology work itself, including teach/learn knowledge transfer, is always one-shot by the invoking primary across harnesses and capability tiers, without delegated production or independent review. The primary owns adaptation, self-checks, required gates, commit and fast-forward push within authorized scope. This standing delivery grant does not expand scope or waive custody and human decisions. No product phase or repeated approval ceremony is needed for authorized methodology work.


The operator approved this design on 2026-09-04. It is a target contract, not a model benchmark. The work upgrades this template while preserving independent review, full close gates, candidate custody, and human acceptance.

## Model routing

Keep role_models as the delegated execution authority, alongside workflow authority and adviser routing. Add apply-preset quality|balanced|economy with optional --review same-harness|cross-vendor. A preset expands to ordinary pins, preserving other configuration and comments. Omitted review mode is same-harness. These presets retain delegated-mode utility. The shipped/reset/stamp default is now auto primary ownership with configured cross-provider advisers and same-primary fallback.

Quality selects Astra for all Codex roles and Fable for all Claude roles; balanced changes only the coder to Sol/Opus respectively; economy selects Sol/Opus for every role. All begin at high effort. Cross-vendor changes reviewer and critic only: quality/balanced select Fable from Codex and Astra from Claude; economy selects Opus from Codex and Sol from Claude. Separate review contexts remain mandatory; vendor diversity is an explicit option whose incremental value remains a hypothesis to measure.

Add astra mapped to gpt-6-astra. Declare supported effort by model and venue, using supported CLI capability rather than API-only claims. Preserve selected model/effort on initial and resumed invocations. Record requested settings, harness version, and provider-reported actual model/effort when available; absent reports remain unreported. No silent model downgrade. Preflight is still required before phase mutation. Substitution requires governed recovery and satisfaction of the selected model and authority requirements; terminal policy refusals never justify generic retries or provider switching.

## Phase 2 source qualifications

As of 2026-09-04; retrieved 2026-09-04: the [official factual excerpt](../docs/openai-astra-model-settings.md) specifies `gpt-6-astra` and API reasoning effort through `max`. This establishes API identifiers/settings, not CLI execution or account entitlement. Local observations on that date found Codex CLI 0.151.0 and Claude Code 2.1.261. `~/.codex/models_cache.json`, under each model's `supported_reasoning_levels`, listed `max` for Sol, Terra and Luna; the app's model enum listed Astra with `max`. The absent Astra row in that local cache does not establish unavailability. The policy deliberately supports a subset and does not enable `ultra`.

A required Claude review invocation on that date emitted `type: system`, `subtype: init`, `model: claude-opus-5`, and `claude_code_version: 2.1.261`. This qualifies those primary field paths; it emitted no effort field. Auxiliary usage-model entries are not primary role identity. No Codex primary model field is qualified here. Missing observations remain unreported.

The earlier upgrade shipped quality/same-harness defaults with fail-closed availability; the primary-ownership update above replaces that default. Missing Astra or Fable entitlement prevents kickoff until the operator selects an available preset or explicit pins through the manager, `roles`, or direct editing. Preset editing requires no model call. These remain dated observations about API identifiers and local CLI state, not a claim of account entitlement, live Astra qualification, or completed comparative evaluation.

## Coherent outcomes

A phase represents one independently acceptable outcome and may span modules, tests, configuration, and documentation. Assess decomposition at phase entry; absent children do not require decomposition. Split only at an unresolved consequential decision, independently accepted prerequisite, distinct deployment/migration/human seam, or demonstrated model-coherence limit. Keep ordinary implementation steps inside the phase. Do not merge completed phases.

The planner settles intended behavior, exclusions, interfaces, invariants, consequential decisions, affected files/dependent contracts, prerequisites, acceptance, and designed human stops. Ordinary implementation choices belong to the coder inside approved scope, including approved deletions. Retain research freshness, dependent-contract tracing, and existing-proof reuse. Remove redundant instructions and pseudocode before splitting a plan that approaches the prose ceiling. Preserve the existing plan growth, scope-expansion, and stalled-review stops.

## Instruction delivery and review

Root instruction budget: 20 KiB maximum (raised from 16 KiB on 2026-09-05), retaining hard rules, zone markers, essential operating instructions, and concise complete catalogs. Kickoff entry budget: 10 KiB maximum (raised from 8 KiB on 2026-09-05), with detailed stages in adjacent skill resources loaded before use. Move extended material to its canonical policy/brief; do not duplicate authority. Mandatory execution contracts still render from their enforcing sources into dispatches. Canonical Claude sources, Codex discovery links/wrappers, and stamping remain aligned. Verify automatic injection separately from later retrieval.

Reviews discover broadly and then distinguish blocking defects from advisory improvements. Batch discoverable blockers on the first review. Each blocker identifies the violated requirement, consequence, evidence, and testable resolution. Revisions preserve stable findings and review changed dependencies, expanding when continuity is uncertain. Count false positives, missed defects, and operational failures as well as implementation errors. Cross-vendor value is a hypothesis to measure, not guaranteed decorrelation.

Focused checks run during implementation. Both full close gates, independent initial critique, active/bookkeeping partition, candidate receipts, proof-estate governance, and human acceptance remain required. Retain timeout and self-resume budgets until evidence supports recalibration. Refresh context guidance from supported harness behavior; advertised API context is not harness capacity.

## Qualification and evaluation

### Offline qualification — complete as of 2026-09-05

The surfaces this contract named for extended proof are qualified in the governed estate, and the map below is that audit: each row cites a proof a later reader can open and check rather than trust. It is an enumeration, not a completeness claim over the whole contract — a surface absent from the table is unaudited here, not thereby unqualified. No new proof family was admitted: the coverage was reached by widening existing families' source paths, which is what the zero post-reset budget requires.

| Named surface | Executable proof |
|---|---|
| Routing combinations | `tests/test_kickoff_config.py` — all six preset x review-mode expansions, asserted pin by pin |
| Invalid configuration | `tests/test_kickoff_config.py::test_invalid_edit_is_atomic`; unknown preset, model and effort rejections |
| Comment preservation | `tests/test_kickoff_config.py::test_scoped_edit_preserves_extensions_comments_and_timeouts` |
| Initial and resumed invocation | `tests/test_kickoff_config.py` — per-model and per-venue loops assert the selected model and effort survive `--resume-session` |
| Missing CLI or model | `tests/test_kickoff_config.py` — empty `PATH` yields `CLI not on PATH` and writes no receipt |
| Stale receipts | `tests/test_check_receipt.py` — tampered log and candidate drift are terminal and never reuse a receipt |
| Permission posture | `tests/test_research_authority.py::test_generated_commands_enforce_the_role_authority_matrix` |
| Role independence | `tests/test_kickoff_evidence.py::test_complete_synthetic_kickoff_cross_validates_roles_revision_and_gates` — distinct per-role dispatches, span joins and review-convergence records |
| Phase selection and decomposition | `tests/test_check_catalogs.py` — coherent major work needs no child files; multiple arrows refuse |
| Instruction loading | `tests/test_check_catalogs.py` (byte ceilings, zone markers, stage-resource table rows) and `tests/test_mirror_parity.py` |
| Catalogs | `tests/test_check_catalogs.py`, enforced at every gate by `bin/check-catalogs` |
| Stamping | `tests/test_methodology_toolchain_contract.py` — skills, mirrors, gate executables and the authority contract propagate |
| Reported model, effort and harness version | `tests/test_kickoff_config.py::test_watch_extracts_fresh_claude_result_and_telemetry` — six event cases covering an absent primary record, a failed version command, and `observation_errors` |

**A wrong control is qualified explicitly.** `tests/test_mirror_parity.py` deletes each kickoff stage resource in a copied tree and asserts that the harness-parity checker still reports success while the resource assertion fails. Directory parity is thereby proved *insufficient* for resource delivery — the automatic-injection question and the later-retrieval question are separate, and the proof says so in executable form rather than in prose.

### Live instruction-loading qualification — observed, with limits

As of 2026-09-07: the authorized eight invocations ran in four native paired sessions. All eight retrieved the current instructed resource and wrote the correct JSON file. Six terminal responses also matched the exact JSON-only contract; Opus wrapped both correct objects in Markdown fences. Requested Codex model identity remained unreported by provider events; Claude model identities were observed. These are narrow instruction-loading observations, not general model rankings. Actual subscription billing was unavailable; CLI dollar estimates are not billed cost.

The concrete [evaluation pack](../tests/fixtures/astra_evaluation/README.md) fixes the disposable loading files, native prompts, initial/resumed oracles and local wrong controls. Matrix: four models (Astra, Fable, Sol, Opus) x initial and resumed invocation. Each cell runs a disposable instruction-loading fixture outside the reviewable tree and records the provider-reported model and effort, the harness version, the permission posture actually granted, and any observable failure. Policy refusals are covered by synthetic events rather than by provoking a live refusal, so the batch never depends on a provider declining to answer.

Fail-closed reading rules, which matter more than the runs themselves:

- Missing entitlement is **unqualified**. It is never a local-test success, never an inferred capability, and never a reason to substitute another model.
- An absent provider report is **unreported**, not a default. A cell with no effort field says so; it does not inherit the requested effort.
- A model that answers under a different identity than the one requested is a **silent-downgrade finding**, not a pass.

Cost shape before authorization: the batch is dominated by per-invocation model charges across eight invocations (four paired initial/resumed sessions), not by repository work. Price it per model from current published rates on the day it runs, present the total to the operator, and record the actual spend against the estimate afterward.

### Comparative evaluation — attempted, qualification incomplete

As of 2026-09-07: the original attempts and the first pair in a separately identified corrected batch did not complete delivery within their fixed budgets. The corrected pair produced identical runtime implementations, both approved at first code critique with passing full implementation gates. Generated-log formatting and an invalid documentation substring oracle were exposed and corrected for future use. The [evaluation pack status](../tests/fixtures/astra_evaluation/README.md) preserves failed, interrupted and unstarted outcomes. Full comparative qualification remains open; these samples do not support a preset ranking or phase-size claim.

Four fixed tasks, intended to separate capability from ceremony: a **mechanical edit** (a rename and its forced call sites), a **cross-file contract change** (a required member added to a contract with independent fixture inventories), a **consequential design** task (an unresolved decision the workflow must surface rather than settle, recording which role asked), and a **difficult repair** (a defect whose obvious fix is wrong). The [evaluation pack](../tests/fixtures/astra_evaluation/README.md) supplies exact public starting files and prompts, private executable checks, manual rubrics, reference solutions and wrong-repair controls. Keep evaluator artifacts outside a verified implementer filesystem boundary; without that boundary held-out qualification is unavailable. The consequential-design task requires a separately observed decision request before the fixed ruling is revealed. Local control qualification does not constitute a model result.

Initial batch: four tasks across quality, balanced and economy in one selected harness — twelve complete runs. Cross-vendor review and effort variation are a separate batch requiring separate budget approval; vendor diversity remains a hypothesis to measure, never a presumed benefit.

Comparison is **per accepted outcome**, aggregating whatever phases a run took, because a workflow that reaches acceptance in three cheap phases is not worse than one that takes a single expensive phase. Metrics, and the existing telemetry each one reuses:

| Metric | Source | Availability |
|---|---|---|
| Behavior and escaped defects | Fixed evaluation checks plus independent manual rubrics | Partial observed outcomes; documentation-oracle failure qualified separately |
| Review rounds and their cause | `bin/review-verdicts`, including `--coder-evidence` | Complete |
| Elapsed time | `bin/execution-telemetry` spans; overlap-safe unions | Complete |
| Operator intervention | `bin/execution-telemetry` park intervals, reported separately from run time | Complete |
| Input and output tokens | `bin/kickoff-config watch`, `usage_scope: invocation` | **Claude venue only** |
| Cache and reasoning tokens | Not captured by any current surface | **Unavailable — do not report** |
| Actual cost | Provider billing; token-derived figures are estimates only | Unavailable for the observed subscription runs |

The two limitations in that table are load-bearing. Token counts come from the Claude result stream, so a Codex-venue run reports `usage_scope: unavailable` and its usage is unknown rather than zero. Cache and reasoning breakdowns are read by nothing today; a comparison that wants them must first extend the telemetry, and until then the honest output omits the column. Missing measurement is unknown, never zero.

### What remains explicitly pending

Offline qualification is complete. Instruction-loading observations and incomplete workflow attempts are recorded above. Complete native workflow qualification, a comparative delivery matrix and cost per accepted outcome remain unproved. Preserve the failed attempts and frozen scoring; any repaired experiment requires a separately identified batch and its own authorized call count and budget. Existing model pins remain unchanged. Local controls establish instrument behavior, not general model performance or optimal phase size.

### Exclusions

API-only asynchronous tools, WebSocket steering, cache-preserving effort changes, custom compaction infrastructure, automatic routing, mandatory supervision, and new parallel writers are excluded from this contract. Source pins require permitted redistribution and separate evidence and retrieval dates.
