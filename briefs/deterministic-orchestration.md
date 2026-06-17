---
title: "Deterministic Orchestration of the Kickoff Loop"
date: 2026-06-09
status: draft
scope: Design and decision criteria for encoding /kickoff's delegate → verdict → route-back loop as a deterministic workflow program instead of orchestrator prose; deferred until every supported harness has a parity workflow primitive.
---

# Deterministic Orchestration of the Kickoff Loop

This brief proposes — and deliberately defers — moving `/kickoff`'s control flow from prose executed by the orchestrating model to a deterministic workflow program executed by the harness. It exists so the decision can be made quickly when its trigger condition lands, rather than re-derived from scratch.

## 1. Problem

`/kickoff` is a state machine written in prose. The orchestrating model reads `.claude/skills/kickoff/SKILL.md` and *performs* the machine: resolve venue (Step 0a), resolve phase and lane (Step 1), decompose (Step 1a), delegate to four roles, parse verdicts by string match, run convergence-based revision loops (a judgment call — iterate while objections narrow, escalate on stall or divergence — bounded by a deterministic 5-cycle runaway backstop), run the cross-harness fallback state machine, run the ripple pass, assemble the END block.

Field use across this template and its derived projects shows the prose machine executing faithfully — END blocks match status flips, revision caps hold, fallbacks degrade gracefully. But the state count has grown monotonically: venue resolution, per-stage fallback, turn-cap rescue, review lanes with escalation, AUTO/DECIDE ripple classification. Prose execution risk grows with the number of states the orchestrating model must track, and every addition is paid on every phase. The known failure classes — none yet observed at damaging scale, all structurally possible — are: a skipped step, a mis-parsed verdict (`## Verdict:` is matched by string; [`../policies/four-canonical-agents.md`](../policies/four-canonical-agents.md) already warns that any deviation breaks orchestration), a forgotten ripple pass, a revision loop that loses count, venue thrash after a fallback.

## 2. What a deterministic encoding buys

- **Control flow in code.** Loops, caps, timeouts, and the fallback state machine become mechanical — incapable of being forgotten, miscounted, or reordered.
- **Schema-validated verdicts.** A structured-output contract (`{verdict: "APPROVED" | "REVISE", required_changes: [...]}`) replaces string matching. The reviewer model is *forced* into the shape; malformed verdicts become retries at the tool layer instead of orchestration breaks.
- **Resumability.** A journaled workflow re-runs from the first changed step after an interruption, instead of the human reconstructing where the prose machine stopped.
- **Cheaper orchestration.** The orchestrating model spends judgment on content (what the critic found, what ripples mean) rather than bookkeeping (which step, which count, which venue).

## 3. What stays model-driven

The program orchestrates; it does not judge. These remain model (or human) work:

- The four roles' actual work — planning, reviewing, coding, critiquing.
- AUTO vs. DECIDE ripple classification ([`../policies/phase-ripple.md`](../policies/phase-ripple.md)) — judgment-bearing by definition.
- Build-failure classification (coder / plan / environment) — the *routing* on each classification is deterministic; the classification itself is judgment.
- Human-facing reporting and everything in [`../policies/human-in-the-loop.md`](../policies/human-in-the-loop.md). A reviewer's product question must still reach the human; a deterministic loop must surface it, never swallow it.

## 4. Harness state of the art (as of 2026-06)

- **Claude Code** ships a workflow primitive: a deterministic script that spawns subagents, enforces JSON-schema structured outputs per agent call, supports sequential/parallel/pipelined composition, journals execution, and resumes from the journal. Everything §2 needs exists today on this harness.
- **Codex CLI** has no announced parity primitive. Orchestration there is prose or external scripting.

This asymmetry is the blocker. [`../policies/cross-harness-parity.md`](../policies/cross-harness-parity.md) requires one canonical `/kickoff` to drive both harnesses; a deterministic path that exists on one harness only is acceptable **only** in the shape cross-harness review already proved out: a config-gated enhancement with graceful fallback to the prose path, where the canonical contract stays in `SKILL.md`.

## 5. Design sketch (tentative — to be re-validated at implementation time)

- `SKILL.md` remains the **canonical contract**: the steps, the policies they bind to, the END-block format. The workflow program is an *implementation* of that contract, not a second authority.
- The program lives at a well-known repo path (e.g., `workflow/kickoff` in whatever format the harness requires) and is activated by a Project Context token mirroring the cross-harness-review pattern — e.g., `deterministic-orchestration: enabled` — resolved in a Step 0b: token enabled **and** the current harness has the primitive → program path; otherwise → prose path, silently.
- Step granularity maps 1:1 to today's Steps 0a–10, so the END block, LOG discipline, and status-marker transitions are byte-identical regardless of path. A human reading `LOG.md` cannot tell which path ran except by the venue/path line that reports it.
- Verdicts move to the structured-output schema in the program path. **Open question (greenfield rule):** if the schema becomes the real contract, the prose path and the role files should adopt the same shape at the same time — one verdict contract everywhere, not a compat split. That migration touches `four-canonical-agents.md`, both reviewer role files, and `cross-harness-review.md`'s three-signal gate, and must land in the same phase that lands the program.
- **Drift guard:** a parity check (same family as `cross-harness-parity.md`'s verification sweep) asserting the program's step graph matches `SKILL.md`'s step list — mechanically extractable from both sides. Without this, prose and program *will* diverge silently; the guard is a precondition, not a nice-to-have.

## 6. Decision criteria — when to take this out of draft

Implement when **all** of:

1. **Codex (or whatever the second supported harness is) ships a workflow-parity function** — deterministic script, subagent spawning, schema-enforced outputs, resume. This is the trigger this brief waits on.
2. Both harnesses' primitives can express the cross-harness-review fallback state machine and the review-lane escalation path — the two most stateful parts of the loop.
3. The drift guard (§5) has a concrete mechanical design.
4. Re-validation of §4: harness APIs churn; the sketch above describes 2026-06 reality and must be re-checked, not trusted.

Until then, the prose loop stands — the field evidence says it is executing faithfully, so there is no urgency, only an improving cost/robustness trade to claim when parity arrives.

## 7. Risks

- **Two sources of truth.** The central hazard; mitigated only by the drift guard and by keeping `SKILL.md` canonical.
- **Harness API churn.** A program path breaks louder than prose when the primitive's API moves. The config gate plus silent prose fallback bounds the blast radius.
- **Mid-loop human steering.** Plan-reviewer escalations (`AskUserQuestion`) and pause-mid-phase must survive the program path. If the primitive cannot surface a human question mid-run, the program must end the run with the question as its result — never answer it itself.
- **Debugging opacity.** A prose orchestrator narrates; a program journals. Acceptance for the implementing phase must include a failure-injection demo (kill a reviewer mid-call, malform a verdict) showing the journal tells the human what happened at least as clearly as today's END blocks.
