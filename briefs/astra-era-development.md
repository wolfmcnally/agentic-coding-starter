---
title: Astra-era development workflow
date: 2026-09-04
status: draft
scope: local
---

# Astra-era development workflow

The operator approved this design on 2026-09-04. It is a target contract, not a model benchmark. The work upgrades this template while preserving independent review, full close gates, candidate custody, and human acceptance.

## Model routing

Keep role_models as the single execution authority. Add apply-preset quality|balanced|economy with optional --review same-harness|cross-vendor. A preset expands to ordinary pins, preserving other configuration and comments. Omitted review mode is same-harness. Quality with same-harness review is the shipped/reset/stamp default.

Quality selects Astra for all Codex roles and Fable for all Claude roles; balanced changes only the coder to Sol/Opus respectively; economy selects Sol/Opus for every role. All begin at high effort. Cross-vendor changes reviewer and critic only: quality/balanced select Fable from Codex and Astra from Claude; economy selects Opus from Codex and Sol from Claude. Separate review contexts remain mandatory; vendor diversity is an explicit option whose incremental value remains a hypothesis to measure.

Add astra mapped to gpt-6-astra. Declare supported effort by model and venue, using supported CLI capability rather than API-only claims. Preserve selected model/effort on initial and resumed invocations. Record requested settings, harness version, and provider-reported actual model/effort when available; absent reports remain unreported. No silent model downgrade. Preflight is still required before phase mutation. Substitution requires governed recovery and satisfaction of the selected model and authority requirements; terminal policy refusals never justify generic retries or provider switching.

## Phase 2 source qualifications

As of 2026-09-04; retrieved 2026-09-04: the [official factual excerpt](../docs/openai-astra-model-settings.md) specifies `gpt-6-astra` and API reasoning effort through `max`. This establishes API identifiers/settings, not CLI execution or account entitlement. Local observations on that date found Codex CLI 0.151.0 and Claude Code 2.1.261. `~/.codex/models_cache.json`, under each model's `supported_reasoning_levels`, listed `max` for Sol, Terra and Luna; the app's model enum listed Astra with `max`. The absent Astra row in that local cache does not establish unavailability. The policy deliberately supports a subset and does not enable `ultra`.

A required Claude review invocation on that date emitted `type: system`, `subtype: init`, `model: claude-opus-5`, and `claude_code_version: 2.1.261`. This qualifies those primary field paths; it emitted no effort field. Auxiliary usage-model entries are not primary role identity. No Codex primary model field is qualified here. Missing observations remain unreported.

The operator approved shipping quality/same-harness defaults with fail-closed availability. Missing Astra or Fable entitlement prevents kickoff until the operator selects an available preset or explicit pins through the manager, `roles`, or direct editing. Preset editing requires no model call. These are preparation-time target contracts and dated observations, not a claim that Phase 2 implementation, live Astra qualification, or comparative evaluation has completed. This brief remains draft through the broader upgrade.

## Coherent outcomes

A phase represents one independently acceptable outcome and may span modules, tests, configuration, and documentation. Assess decomposition at phase entry; absent children do not require decomposition. Split only at an unresolved consequential decision, independently accepted prerequisite, distinct deployment/migration/human seam, or demonstrated model-coherence limit. Keep ordinary implementation steps inside the phase. Do not merge completed phases.

The planner settles intended behavior, exclusions, interfaces, invariants, consequential decisions, affected files/dependent contracts, prerequisites, acceptance, and designed human stops. Ordinary implementation choices belong to the coder inside approved scope, including approved deletions. Retain research freshness, dependent-contract tracing, and existing-proof reuse. Remove redundant instructions and pseudocode before splitting a plan that approaches the prose ceiling. Preserve the existing plan growth, scope-expansion, and stalled-review stops.

## Instruction delivery and review

Root instruction budget: 16 KiB maximum, retaining hard rules, zone markers, essential operating instructions, and concise complete catalogs. Kickoff entry budget: 8 KiB maximum, with detailed stages in adjacent skill resources loaded before use. Move extended material to its canonical policy/brief; do not duplicate authority. Mandatory execution contracts still render from their enforcing sources into dispatches. Canonical Claude sources, Codex discovery links/wrappers, and stamping remain aligned. Verify automatic injection separately from later retrieval.

Reviews discover broadly and then distinguish blocking defects from advisory improvements. Batch discoverable blockers on the first review. Each blocker identifies the violated requirement, consequence, evidence, and testable resolution. Revisions preserve stable findings and review changed dependencies, expanding when continuity is uncertain. Count false positives, missed defects, and operational failures as well as implementation errors. Cross-vendor value is a hypothesis to measure, not guaranteed decorrelation.

Focused checks run during implementation. Both full close gates, independent initial critique, active/bookkeeping partition, candidate receipts, proof-estate governance, and human acceptance remain required. Retain timeout and self-resume budgets until evidence supports recalibration. Refresh context guidance from supported harness behavior; advertised API context is not harness capacity.

## Qualification and evaluation

Extend existing proofs for routing combinations, invalid configuration, comment preservation, initial/resumed invocation, missing CLI/model, stale receipts, permission posture, role independence, phase selection/decomposition, instruction loading, catalogs, and stamping. Qualify wrong controls. No new proof family without governed admission or compensation.

Prepare a separately priced live qualification batch for all four models, initial/resume, disposable instruction-loading fixtures, reported identity, permissions, and observable failures. Synthetic events cover policy refusals. Missing entitlement is unqualified, never a local-test success.

Prepare four fixed tasks: mechanical edit, cross-file contract change, consequential design, difficult repair. Use independent behavioral acceptance and held-out checks where applicable. Initial comparative batch: four tasks across quality/balanced/economy in one selected harness, twelve complete runs. Cross-vendor/effort comparisons require separate budget approval. Compare per accepted outcome, aggregating phases: behavior/escaped defects, review rounds and cause, elapsed time, operator intervention, input/output/cache/reasoning usage, and actual cost when known. Reuse existing telemetry. Offline qualification can close independently; paid work and performance claims remain explicitly pending.

API-only asynchronous tools, WebSocket steering, cache-preserving effort changes, custom compaction infrastructure, automatic routing, mandatory supervision, and new parallel writers are excluded. Update the canonical public explanation after contracts settle. Source pins require permitted redistribution and separate evidence/retrieval dates.
