---
title: "The Agentic Coding Methodology — Eleven Steps"
date: 2026-06-09
status: methodology
scope: The canonical statement of the methodology this template implements. Authoritative reference for every skill, agent, and policy in the repo.
---

# The Agentic Coding Methodology

A methodology for writing software with AI coding agents in a way that scales beyond ad-hoc prompting. Each step involves conversing with or using LLMs. Apply it when scoping or structuring a coding project — not when answering one-off coding questions.

## The eleven steps

1. **Vague ideas → insights.** Turn vague ideas into insights, including competitive analysis. What problem are you actually solving? Who has already tried to solve it, and how? What do you need to learn before committing to a direction?

2. **Insights → brief.** Turn the insights into a brief: *what* to build. A brief is a durable document — it describes the product, the user, the goal, the constraints, the success criteria. It lives under `briefs/`.

3. **Brief → architecture document.** Decide *how*. This probably involves the LLM researching Best Current Practices (BCPs) for each technical aspect: which libraries, which protocols, which data formats, which platform conventions. The architecture document lives under `briefs/` too (or `ARCHITECTURE.md` at the root for very large efforts).

4. **Repo-level policies.** Put policies in place that enforce standards and practices. Examples: each completed phase must be incremental and testable; the repo tracks which phases are complete, in progress, up next, or yet to start; **the human, not the agent, decides when work is committed as "done."** Policies live under `policies/`. Every phase honors every policy.

5. **Brief + architecture → phased plan.** Break the work down by phase. Each phase is independently testable, mostly independently deliverable, and has a clearly defined goal and acceptance criteria. Phases live under `plan/`; the spine is `plan/INDEX.md`. Major phases are written *after* the brief (step 2) and architecture (step 3) exist — without those, the phase plan is speculation. If you find yourself wanting to plan phases before there's a primary brief, go back to step 2.

6. **Major phases up front, sub-phases just-in-time, ripple at every close.** Two scales, two rules:

   - **Major phases are drafted up front** to *general specificity* from the brief and architecture. Same shape as a full phase file (frontmatter + Goal + Deliverables + Acceptance + brief refs), at lower fidelity than the in-flight phase. The dependency graph in `plan/INDEX.md` enumerates them from the start. Some major phases stay monolithic — small phases that fit one session never need sub-phase decomposition.
   - **Sub-phases are JIT, one at a time.** At the start of a major phase, decompose only `phase-N.1` in full. Subsequent sub-phases (`phase-N.2`, `phase-N.3`, …) get drafted at *close* of the previous one, with the benefit of its outcomes. Pre-decomposed sub-phases lock in premature assumptions and resist the very revisions that doing the work earlier reveals.
   - **Bite size is capability-indexed.** Size sub-phases to the executing coder model's demonstrated coherence, not to a fixed calendar. Acceptance criteria, not session length, define a bite. The signal to coarsen: a model class that routinely closes phases of the current size with first-cycle approvals and green gates can safely take bigger bites — fewer, larger sub-phases, more major phases left monolithic. The signal to split finer: revision loops hitting their caps, build-gate fix cycles recurring. Per-phase ceremony (planning, review, logging) is a fixed cost; over-fine decomposition under a strong coder pays that cost more often than the work needs.
   - **Ripple propagation at every phase close.** When a phase (sub or major) closes, pinned decisions and surfaced concerns from its END block — plan-reviewer Observations, code-critic findings, deliberate scope changes — are propagated into downstream drafted phase files. Mechanical edits (renaming a path the closing phase pinned; adding a brief ref it introduced; tightening an Acceptance criterion to a now-pinned value) land automatically (AUTO). Judgment-level changes (a downstream Goal needs revision; a Deliverable becomes obsolete; the dependency graph shifts) surface to the user as named follow-ups (DECIDE). The contract lives in [`policies/phase-ripple.md`](../policies/phase-ripple.md); the orchestrator executes it at each phase close.

   Net effect: the major-phase roadmap is visible at bootstrap; the orchestrator works one sub-phase at a time with each predecessor's outcomes baked in; the downstream sketches stay fresh as work proceeds rather than diverging from reality.

7. **Orchestrator-driven sub-phase execution.** Use a high-level orchestrator skill (`/kickoff`) that does **no coding itself**. It:
   - determines the current phase,
   - invokes a **planning agent** to turn the current sub-phase into a file-level plan,
   - hands the plan to a **plan-reviewer agent**,
   - hands the (possibly revised) plan to a **coding agent**,
   - hands the result to a **code-critic agent**,
   - on any critic's complaint, sends the work back to the relevant agent for revision (with bounded loops).

   *One step, a lot happening. Each of those four roles is a specialist with its own tool stance, reading protocol, and verdict format.*

   Review intensity is risk-adaptive: a phase may declare a **review lane** ([`../policies/review-lanes.md`](../policies/review-lanes.md)). The default `full` lane runs all four roles; a `light` lane — mechanical phases only — skips plan review while always keeping the code critic, who also guards the lane and escalates back to `full` when the work exceeded mechanical scope.

8. **Acceptance check.** The orchestrator runs the tests and the build gates that the sub-phase declares. If anything fails, the orchestrator classifies the failure (coder error, plan error, environment error) and routes back through the appropriate revision loop, with a cap on iterations before surfacing to the human.

9. **Append-only phase log.** Use an append-only log (`LOG.md`) to **open and close** work on every phase. Closing requires recording the **evidence** of what happened and **why** the orchestrator believes the success criteria were met. The human reads the END block before accepting the phase.

10. **Human evaluation.** The human evaluates each sub-phase, and re-invokes the orchestrator (or specific agents) to refine or fix anything found before moving on. This is where the human exercises engineering, UX, and product judgment. **The orchestrator does not decide done.**

11. **Stay agile.** Add new phases, or break existing phases into more sub-phases, as the problem and solution space become clearer. The phase plan is mutable. Phases that turn out to be wrong are split, merged, or rewritten.

## How to apply this methodology

When you're starting or scoping a coding project, work through these steps in order — don't jump to coding. Concretely:

- If you have only a vague idea, push to step 1: surface insights and do competitive analysis before committing to a brief.
- If a brief exists but no architecture, do step 3 and research BCPs.
- If architecture exists but no phase plan, do step 5.
- If a phase exists but no sub-phases, do step 6.
- If a sub-phase is being executed, follow step 7's orchestrator pattern (planner → planning critic → coder → coding critic, with revision loops).
- Whenever a phase opens or closes, write to the append-only log (step 9) with explicit evidence.

## The four canonical agents

The methodology's orchestrator delegates to four specialist roles. Their names are load-bearing — the orchestrator invokes them by name. See [`../policies/four-canonical-agents.md`](../policies/four-canonical-agents.md) for tool stances and verdict formats.

| Role | Reads | Writes code | Job |
|---|---|---|---|
| `phase-planner` | Briefs, plan, repo | No | Turn one phase into a file-level implementation plan |
| `plan-reviewer` | Briefs, plan, repo, plan output | No | Approve the plan or send it back for revision |
| `phase-coder` | Briefs, plan, repo, approved plan | Yes | Implement the approved plan and run build gates |
| `code-critic` | Briefs, plan, repo, code diff | No | Approve the code or send it back for revision |

The orchestrator (`/kickoff`) is the fifth participant. It does no coding either — its job is delegation, verdict-handling, build-gate execution, and `LOG.md` upkeep.

## Non-negotiables

- **Every completed phase is incremental and testable** (step 4).
- **Every phase passes the code critic**, whichever review lane it declares (step 7).
- **The human decides when work is "done"**; the orchestrator does not (step 4, step 10).
- **The orchestrator never writes code itself** (step 7).
- **Closing a phase requires recorded evidence**, not just a green test run (step 9).
- **Phases and sub-phases are mutable**; refactor the plan as understanding grows (step 11).

## What this methodology gives up

Honest accounting of the cost.

- **Speed of a single throwaway iteration.** A one-line ad-hoc prompt is faster than spinning up a brief, a plan, and a phase. Use ad-hoc for one-off scripts; use this methodology for projects that will exist next month.
- **Autonomy.** The methodology assumes a human reviewer per phase. It's the wrong tool if your goal is unattended overnight code generation.
- **Flexibility within a session.** The orchestrator follows the plan. If you want to wander, do it before `/kickoff` starts or in between phases — not mid-orchestration.

What you get in exchange: each phase leaves a reviewable artifact pair (END block + commit diff), the next session resumes from a known state without re-explaining anything, and the structural surface (briefs, policies, plan, log) tells the next human contributor — or the next session of you — what's true about the project.

## Related skills

- **`/kickoff`** — runs steps 7–9 for one sub-phase, end-to-end.
- **`/starter`** — runs the bootstrap procedure described in [`agentic-bootstrap.md`](agentic-bootstrap.md) to stand up a new repo under this methodology.
- **`/methodology`** — re-states this brief as a slash-command, for sessions that need a reminder of the steps without reading the whole file.
