---
name: methodology
description: >-
  The eleven-step agentic coding methodology this repo implements: vague
  ideas → insights → brief → architecture → repo policies → phased plan →
  sub-phase decomposition → orchestrated planner/reviewer/coder/critic loops
  → acceptance → log → human evaluation → stay agile. Invoke when scoping a
  new project, setting up a repo's planning structure, breaking a large
  initiative into phases, or reviewing the steps without reading the full
  brief. Invoke as /methodology in Claude Code or $methodology in Codex.
last-reviewed: 2026-08-10
---

# The Agentic Coding Methodology

A methodology for writing software with AI coding agents in a way that scales beyond ad-hoc prompting. Each step involves conversing with or using LLMs. Apply it when scoping or structuring a coding project — not when answering one-off coding questions.

The authoritative source is [`briefs/methodology.md`](../../../briefs/methodology.md). Invoke this restatement as `/methodology` in Claude Code or `$methodology` in Codex.

## The eleven steps

1. **Vague ideas → insights.** Turn vague ideas into insights, including competitive analysis. What problem are you actually solving? Who has already tried? What do you need to learn before committing?

2. **Insights → brief.** Turn the insights into a brief: *what* to build. The brief lives under `briefs/`.

3. **Brief → architecture document.** Decide *how*. Research Best Current Practices (BCPs) for each technical aspect: libraries, protocols, data formats, platform conventions. Lives under `briefs/` or `ARCHITECTURE.md`.

4. **Repo-level policies.** Codify standards and practices. Lives under `policies/`. Every phase honors every policy.

5. **Brief + architecture → phased plan.** Break the work down by phase. Each phase is independently testable and has a clearly defined goal and acceptance criteria. Lives under `plan/`; the spine is `plan/INDEX.md`.

6. **Sub-phase breakdown at phase start.** At the start of every major phase, break it down into sub-phases. Resist decomposing future major phases at bootstrap. Bite size is capability-indexed: a coder model that routinely closes phases with first-cycle approvals can take bigger bites — see `briefs/methodology.md` §6.

7. **Orchestrator-driven sub-phase execution.** Use the high-level `kickoff` orchestrator skill (`/kickoff` in Claude Code; `$kickoff` in Codex), which delegates the initial implementation. It:
   - determines the current phase,
   - invokes a **planner agent**,
   - hands the plan to a **plan reviewer** (skipped when the phase declares the `light` review lane per `policies/review-lanes.md`),
   - hands the approved plan to a **coding agent**,
   - hands the result to a **code critic** (runs on every initial implementation; in `light`, it also guards the lane and can escalate back to `full`),
   - on any critic's complaint, sends the work back to the relevant agent with
     stable findings and a candidate-bound causal revision packet (bounded,
     fail-closed loops).

8. **Acceptance check.** While work converges, the coder runs the smallest
   behavioral and affected checks that can falsify the change. After critic
   approval, the orchestrator runs the complete phase-prescribed sequence and
   one authoritative full gate against the unchanged approved candidate.
   Test- or user-driven follow-ups are routed by risk and size: direct fix,
   coder only, or the full coder → critic cycle. A changed candidate
   invalidates prior gate evidence; a failed lightweight route upgrades to the
   full cycle.

9. **Append-only phase log and lessons harvest.** `LOG.md` opens and closes work on every phase. Closing requires recorded evidence plus the mandatory lessons question: harvest role Process Observations, revision failure analyses, wall-clock observations, and relevant dispositions into `lessons/`; `None` is valid, omission is not.

10. **Human evaluation where judgment is required.** Objective criteria may close autonomously after independent review and complete gates, and the phase is delivered. Named manual, subjective, product, custody, or owner-only criteria still park for the human, who evaluates each sub-phase at the seam. Delivery never substitutes for that judgment.

11. **Stay agile.** Add new phases, or break existing phases into more sub-phases, as the problem and solution space become clearer.

## How to apply this methodology

- If you have only a vague idea, push to step 1.
- If a brief exists but no architecture, do step 3 and research BCPs.
- If architecture exists but no phase plan, do step 5.
- If a phase exists but no sub-phases, do step 6.
- If a sub-phase is being executed, follow step 7's `kickoff` orchestrator pattern.
- Whenever a phase opens or closes, write to the append-only log (step 9) with explicit evidence; at close, run the lessons harvest and surface graduation-ready candidates for human ratification.

## The four canonical agents

The orchestrator delegates to four specialist roles. Their names are load-bearing:

| Role | Reads | Writes code | Job |
|---|---|---|---|
| `phase-planner` | Briefs, plan, repo | No | Turn one phase into a file-level implementation plan |
| `plan-reviewer` | Briefs, plan, repo, plan output | No | Approve the plan or send it back for revision |
| `phase-coder` | Briefs, plan, repo, approved plan | Yes | Implement the approved plan and run focused iteration checks |
| `code-critic` | Briefs, plan, repo, code diff | No | Approve the code or send it back for revision |

## Non-negotiables

- **Every completed phase is incremental and testable.**
- **Every initial phase implementation passes the code critic; repeat review on follow-ups is risk- and size-based.**
- **Review, findings, and gates are bound to exact candidate identity.**
- **Revision rounds use causal packets and widen when continuity is uncertain.**
- **The orchestrator, not the coder, owns the one complete acceptance-close gate.**
- **The human owns subjective and owner-only acceptance; objective acceptance is independently reviewed and gate-proved.**
- **The orchestrator writes code only for eligible small, low-risk follow-up corrections.**
- **Closing a phase requires recorded evidence and a lessons-harvest answer.**
- **Phases and sub-phases are mutable.**

## Orchestration runtime doctrine

Hard-won rules for step 7 when the loop runs fail-closed and unattended:

- **Fail-closed park, diagnosed self-resume.** Any first-encountered defect halts the run and writes an honest park record. A halt whose cause is *novel* for the phase, fully diagnosed with a recorded causal correction, and whose integrity proofs pass may self-resume without waiting for the human — against a small budget (three between human contacts is a working default). A *recurring* cause class always stops for the human: recurrence means a generator the cure didn't reach.
- **Never round-trip deterministic work through a model.** Bookkeeping rebases, identifier substitutions, and small revisions to large documents are orchestrator-performed, byte-diff-proven transforms; the displaced model role reviews the result instead of producing it.
- **No artifact larger than one model response travels a single-message channel.** Large documents are revised by delta plus deterministic merge; a model asked to re-emit a big document verbatim will summarize or paginate it, and either way the artifact is wrong.
- **Qualify every measuring instrument outside the evidentiary run** before it gates anything: exercise every branch, prove aim, and prove falsifiability (a deliberately wrong probe must fail). An assertion that can only pass is not evidence.
- **Embed every contract verbatim in the dispatch prompt**, rendered from the enforcing source — never model memory, never prose inference.
- **Designed human checkpoints are satisfying stops**, enumerated in advance. Every other stop is classified before it is cured — legitimate park, defect, contract mismatch, or model behavior — because each class takes a different fix, and retrying a generator-class cause can never converge.
- **Run an out-of-band supervisor** for long orchestrations: a second session with no write access to the worker's context that verifies claims against ground truth and drafts human-ratified steering, compiling incidents into standing rules.
- **Choose the weakest instrument that can falsify the defect class under test** — retire instruments when a design change eliminates their defect class; every instrument repair first re-asks whether the measured property still needs measuring. Altitude has a time axis: before repairing, check the roadmap for a scheduled change that obsoletes the repaired surface — a fix for what the plan deletes is the ratchet in a new coat.
- **Every falsification control must itself be provably satisfiable** — the wrong probe must fail for its intended reason AND the specified control must be able to succeed under the declared comparator; check at specification time.
- **A machine check fully shadowed by a designed human gate defaults to advisory** — recording rights, not parking rights.
- **Structure every ratification artifact orientation-first** — human gates degrade under density, not just volume ("approval snow blindness"): plain-language beats first, fixed decision-payload position, producer owns legibility, receiver read-back as the forcing function.
- **Preflight the environment before an unattended run** — a fail-closed probe ladder (repo baseline, identity, toolchain, platform capabilities, escalation mechanics, authoritative gate as pre-work baseline) runs before the tasking prompt; probes read-only or self-cleaning with a printed table; barriers surface one layer per round; fixes land as durable config, never session memory; after a green baseline, every failure is the run's own.
- **Well-specified isolated tasks may run as goal-armed one-shots** instead of the four-role loop — complete operator-reviewed spec (substitutes for plan review), new-files-only write set with a park on widening, designed parks as satisfying stops, a durable goal carrying outcome + printed proof + park clause, independent verification against the recorded baseline before push. Goal durability is harness-specific — know whether compaction clears it before trusting continuation to it.
- **Authoritative gates run in the native execution context** — sandboxed gate output can contain phantom failures in either direction; classify sandbox-vs-real with one native baseline before work; a gate that could not run is "not run," never "passed"; never cite in-sandbox gate output as evidence.
- **Doctrine and ceremony grow only against incidents, and every review prunes** — a new binding step enters only with its motivating incident cited and the park it prevents named; foresight proposals stay in the `lessons/` ledger, never become rules; every review pass (plan review, code review, `sweep`) treats steps whose failure families are structurally dead as deletion candidates, because fail-closed pressure ratchets ceremony and only deliberate pruning reverses it.

## Run-lifecycle vocabulary

- **Finalized** — lifecycle closed, outcome recorded, failure included.
- **Sealed** — passed its acceptance gate; digest-bound, immutable, cited downstream. Working shorthand for supply-chain *attestation*: git commits are the substrate (a commit seals *what*; a seal adds *why you may rely on it*); working-state tree hashes (`bin/kickoff-tree-id`) seal the uncommitted interval. Seal at every trust boundary; keep the sealer cheap enough that ubiquity is free.
- **Frozen** — tooling made byte-identical and read-only under a recorded manifest, so later runs provably execute the qualified instrument.
- **Parked** — the run-level stop discipline (written causal account, nothing disturbed, clean proven scene, explicit resume conditions) — distinct from interrupt/pause, checkpoint, and halt.

Full statement: `briefs/methodology.md` § Run-lifecycle vocabulary.

**Enforcement status:** mostly doctrine — self-resume budgets are mechanized (`policies/fail-closed-resume.md`; `kickoff.yaml` `run_budgets.self_resume` via `bin/kickoff-config`), while delta-merge tooling and qualification harnesses remain prose-and-relay. Full statement: `briefs/methodology.md` § Orchestration runtime doctrine.

## Source

This skill restates [`briefs/methodology.md`](../../../briefs/methodology.md). If that brief changes, update this skill.
