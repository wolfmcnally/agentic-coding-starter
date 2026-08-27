---
title: "Harness Self-Improvement: The Two-Tier Flywheel"
date: 2026-08-11
status: implemented
scope: How this template captures process lessons at phase scale, prunes its rule surfaces on a cadence, and propagates both disciplines to every derived project.
---

# Harness Self-Improvement: The Two-Tier Flywheel

This repo is a harness — skills, agents, policies, briefs, and deterministic scripts wrapped around whichever coding-agent CLI hosts a session. A harness that only accumulates rules by hand improves at the speed of its operator's memory. Current best practice is to make improvement *structural*: every unit of work ends by asking what was learned, learnings accumulate as addressable entries rather than prose rewrites, recurring ones graduate into rules under human ratification, and the rule surfaces themselves are pruned on a cadence so the compounding asset never turns into a compounding liability.

This brief records the design: what the loop is, where each stage lives, what was deliberately declined, and the one decision deferred.

## 1. The two tiers

The improvement flywheel runs at two scales, and the template owns both:

- **Phase scale (inner tier, runs in every repo).** `kickoff` closes each phase with a harvest step: the four roles' Process Observations, the coder's failure analyses, review verdicts, dispositions, and wall-clock observations are distilled into candidate lessons in the `lessons/` ledger. Recurring lessons surface as graduation proposals the human ratifies (or doesn't). The `sweep` skill periodically audits the accumulated rules, skills, and briefs and proposes retirements.
- **Repo scale (outer tier, runs between repos).** The starter is the hub. `stamp` ships the machinery to new projects; `teach` retrofits it onto existing ones; `learn` harvests both derived projects' `scope: methodology` lessons and new defects exposed while applying a donor bundle. Once ratified, those findings improve the template every future project is stamped from.

The seam between the tiers is the lesson's `scope` field. A `local` lesson stays in its repo. A `methodology` lesson is a standing export: pre-digested, provenance-carrying input that `learn` reads as a first-class source instead of rediscovering patterns from raw files. This is the template's answer to the portability problem — knowledge is repo-local by default, and the hub-and-spoke transfer channel is what makes phase-scale learning compound across the whole family of projects. The return path earns its cost precisely because of where defects surface first: a methodology defect a spoke hits — a timeout recalibration contract, an evidence schema, a review lane — is worth exporting because the spoke exercises the machinery at a scale the template itself never does.

## 2. The loop, stage by stage

1. **Capture.** Roles emit Process Observations (friction or ambiguity in briefs, policies, plans, tooling, or the methodology itself) as structured output fields; on revision rounds the coder states *why* the previous attempt failed, and that analysis travels in the revision packet. `kickoff`'s harvest step files or recurs lessons in `lessons/` — one file per lesson, scope-classified `local` or `methodology`, with a new occurrence row appended rather than a second file filed. "No lessons this phase" is a permitted, recorded answer; skipping the question is not.
2. **Distill.** `bin/lessons` mechanically validates the ledger and tallies occurrences; `bin/lessons candidates` lists graduation-ready entries (three or more occurrences). Three is the stabilization threshold: a lesson codified on first sight tends to be wrong in ways its variations would have revealed.
3. **Codify.** Graduation is human-ratified, one lesson at a time, onto a named surface: a policy, a brief, a skill, an agent definition, a `bin/` script, a test, or a `CLAUDE.md` invariant. Agents propose; the human edits (or approves the edit); the lesson archives with `graduated_to:` pointing at the rule it became. Every rule stays traceable to the incidents that earned it.
4. **Prune.** `sweep` runs the maintenance half: stale or contradictory rules, skills past their review cadence, briefs due for `historical` status, aging ledger candidates, catalog drift, internal-link integrity (`bin/check-catalogs`), and the proof estate's executable reassessment and shrinkage obligation (`bin/test-governance reassess`) where that machinery exists. In the starter itself, `sweep` additionally audits the methodology corpus — the universal policies, methodology briefs, and the orchestration runtime doctrine's instruments — because defects here propagate to every spoke. A third pass, `sweep-planning`, reads the review loop itself rather than the rules: `bin/review-verdicts` harvests every genuine plan-review verdict from the machine's harness traces, and the skill categorizes why plans were sent back over the window, attributes each category to a correctable planner defect or a reviewer false positive (including a proxy that can invert — a reviewer whose bar surfaces the planner's best work as a defect), and proposes persona, script, and policy corrections the human ratifies. Its first run, over one month and three derived projects, found that most rejections were the planner citing code it never read and acceptance blocks that could not execute, and that the costliest reviewer habit was re-aiming a stable finding id at a new objection each round; the corrections became `bin/check-plan-concreteness`, the planner's `Definitions Read` table, and the ingest refusal of substituted evidence. `sweep-coding` is its sibling over the coder ↔ critic loop, adding the coder's own failure analyses as a sensor; its first run found tests that could not fail as the largest category, subset delivery and unverified handoff as the structural leaks, and one threat-model overreach as the critic's costliest habit — which became the coder's falsifier and gate-status fields, `bin/check-plan-delivery`, the critic's threat-model boundary, and `kickoff`'s unverified-handoff guard. Both sweeps enter plan mode first and present their analysis and plan together for ratification. The audit's sharpest test is the doctrine's growth rule: every binding step must name the park it prevents or cite its motivating incident, and a step whose failure family a structural fix made dead is a deletion candidate. The worked form is a ceremony audit — one pass that walks an orchestration protocol step by step under that test; a donor repo's first such audit deleted or demoted four binding steps.
5. **Propagate and return.** The machinery is Methodology Contract content: `stamp` copies it verbatim into new projects, `teach` proposes it to existing ones, and `learn` closes the return loop. After applying an approved bundle, `learn` separately harvests generalizable defects discovered by the adaptation itself; applying the pattern is evidence about its source contract. Anonymization on the upstream path is mandatory and happens before the file is written — a methodology lesson leaves its repo's project names, commit SHAs, internal paths, and proprietary identifiers behind before it enters the public template.

## 3. Why itemized capture, not instruction-file rewrites

The naive loop — "agent, update the instruction file with what you learned" — degrades under iteration: each rewrite shortens and blands the document (brevity bias) until accumulated knowledge collapses into generic filler (context collapse). The remedy is structural: lessons are discrete, addressable files with provenance and occurrence counters; the author of a lesson is never the authority that ratifies it; and rule documents are only ever edited by the human, deliberately, one graduation at a time. The ledger grows; the rules are curated. This is also why the ledger lives in committed repo files rather than any agent-side memory or derived index: anything that must bind future sessions belongs where every harness, operator, and machine reads it — not in a store that a retrieval change could silently stop surfacing.

## 4. Grounding

The design instantiates named patterns from the Encyclopedia of Agentic Coding Patterns, checked against the 2026 self-improving-harness literature:

- **Compound Engineering** — codification as a closing condition of every unit of work; the five-surface routing question. The harvest step is that closing condition made mandatory.
- **Feedback Flywheel** — capture → distill → codify with a recurrence threshold before rules land.
- **Reflexion** — the coder's failure analysis on revision rounds, stored and fed forward.
- **Garbage Collection / Skill Fitness** — `sweep` and the skills' `last-reviewed` cadence; the anti-ratchet duty over the runtime doctrine's instruments.
- **Incident-to-Eval Synthesis** — dispositions and post-mortems route into lessons, and mechanizable fixes land with regression tests in the same change.
- **Agentic Context Engineering** — itemized, tagged, counter-scored entries with a separated curator role (here: the human), replacing monolithic self-rewrites.
- **Self-Harness (arXiv 2606.09498) and successors** — weakness mining from execution traces (`recommend-timeouts` surfacing at phase close is the first instance), bounded minimal proposals, regression-gated acceptance, and strict separation between the thing evolving and the evaluator judging it (`./bin/check all` never bends to a lesson).

## 5. Deliberately declined

- **Autonomous self-modification.** The fully closed loop — agent mines weaknesses, edits its own rules, validates, merges — contradicts the rule that a human owns every subjective and custody-bearing judgment, and imports the literature's own top risks (reward hacking, evaluator contamination). Humans move up the stack, not out of the loop: the human is the Curator, and that is a design choice, not a maturity gap.
- **First-pass-acceptance-rate tracking.** The flywheel's canonical metric needs a denominator of phases that doesn't exist yet in a young repo, and gaming pressure makes it a trend indicator at best. Revisit once derived projects have accumulated enough END blocks for the number to mean something.
- **Skill lift measurement.** Measuring each skill's marginal effect on task pass-rate requires an eval harness this template doesn't carry. `last-reviewed` cadence plus `sweep` retirement proposals is the proportionate version at this scale.
- **Hooks as a codification surface.** The template's hooks remain opt-in (`bin/install-hooks`); lessons that need deterministic enforcement route to `bin/` scripts and gates instead.

## 6. DECIDE — methodology-contract versioning (deferred)

When several derived projects exist, "is this spoke running the current methodology?" has no mechanical answer: `teach`'s parity-heal catalog repairs known drift classes, but nothing marks *which revision* of the Methodology Contract a stamped repo carries. A contract-version marker (bumped on methodology changes, taught outward, checked by `teach` to compute deltas instead of full rescans) is the pinning discipline applied to the contract itself.

**Deferred** until at least two derived projects are active. With one spoke, the marker is ceremony that every methodology edit must remember to maintain; `teach`'s full scan covers the interim. Revisit at the second spoke.

## 7. Acceptance criteria for this design

- A phase close in any derived repo cannot complete without answering the lessons question: the END block's `Lessons:` field is part of the log's minimum contract, and omitting it is not a valid close.
- `./bin/lessons validate` and `./bin/check-catalogs` pass in this repo and
  in a freshly stamped project, covering ledger schema, catalog membership,
  current-candidate internal links, and phase-lifecycle state.
- A `scope: methodology` lesson filed in a derived repo is visible to `learn` Stage 1 without bespoke exploration.
- A `learn` application that exposes a new methodology defect records it as a
  distinct return-path candidate and reports it separately from donor-ledger
  lessons.
- No agent-authored change to `policies/`, `briefs/`, `CLAUDE.md`, skills, or agent definitions cites a lesson as its authority without a recorded human ratification.

## Sources

- Encyclopedia of Agentic Coding Patterns (aipatternbook.com): `compound-engineering`, `feedback-flywheel`, `garbage-collection`, `skill-fitness`, `incident-to-eval-synthesis`, `agentic-context-engineering`, `reflexion`, `harness-engineering`.
- *Self-Harness: Harnesses That Improve Themselves*, arXiv:2606.09498 (2026) — the weakness-mining → bounded-proposal → regression-validation loop.
- Lilian Weng, "Harness Engineering for Self-Improvement" (July 2026) — editable-surface taxonomy, evaluator isolation, "humans move up the stack."
- Fowler/Boeckeler, "Harness engineering for coding agent users" (martinfowler.com) — the three-loop model; this brief's machinery is the outer loop given repo surfaces.
