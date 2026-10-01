---
name: refactor
description: >-
  Improve the structure of working code without changing what it does. Finds
  duplication, needless complexity, fixes made at the wrong depth, leftover
  generated-code residue, introduced waste, and breaks of the project's written
  conventions; applies the changes that are local, proposes the ones another
  module or caller could observe, and hands cross-cutting work to a phase. Use
  when the user asks to refactor, simplify, tidy, clean up, or de-slop code, or
  to survey a code base for such work. Invoke as /refactor in Claude Code or
  $refactor in Codex; an optional argument names a path, module or symbol, or
  `survey` for a proposal-only pass over the whole deliverable.
argument-hint: "[<path|module|symbol> | survey]"
last-reviewed: 2026-10-01
---

# Refactor — change the structure, keep the behavior

Refactoring changes how code is written and nothing about what it does. An ordinary task leaves unrelated cleanup alone; this skill is the grant to do it, so what follows is how far the grant goes. How to refactor is yours to judge. The reasoning and its sources are in [`briefs/refactoring-methodology.md`](../../../briefs/refactoring-methodology.md).

## Scope

- **No argument:** the current change — commits not yet upstream plus the working tree — and the functions those changes sit in.
- **A path, module or symbol:** that target.
- **`survey`:** the whole deliverable, proposals only. Start where the history shows the code changing most.

Policies, briefs and skills are not code. They belong to [`sweep`](../sweep/SKILL.md).

## What to look for

Go through all of these; stopping at the first few leaves most of the value behind.

- Code that repeats or re-implements something the project already has.
- Structure nothing present requires, by the tests in [`policies/simplicity-and-consolidation.md`](../../../policies/simplicity-and-consolidation.md): dead code, a parameter every caller passes the same way, an interface with one implementation, state that could be derived, nesting that early returns would flatten.
- A fix at the wrong depth: a special case repeated at call sites where the mechanism should change, or a module that adds an interface and hides nothing.
- Residue of generated code: comments that narrate the code, state that is written and never read, scaffolding left behind.
- Waste the change introduced: the same work repeated, independent work run in sequence.
- A break of a rule the project's instruction files state.

## Who decides

- **Apply** a change that stays inside one module and alters nothing that another module, a caller outside the project, or a stored format can observe.
- **Propose** anything else, and leave the code as it is: a renamed, moved or removed public name, a changed signature, a deleted module or test, anything touching concurrency, security, or a decision the project has recorded. Say what would change and what it buys; the operator decides.
- **Hand off** work that is cross-cutting or high-risk by the follow-up test in [`policies/review-lanes.md`](../../../policies/review-lanes.md): give a phase sketch — goal, write set, the behavior that must not change, the checks that would show it — and do not start it.

In `survey`, apply nothing.

## Done

Behavior is unchanged, and the existing tests pass with their assertions as they were. A bug found on the way is reported, not fixed: fixing it changes behavior, which is a different task.

## Delivery

- **During a phase** (its row in `plan/INDEX.md` is in progress): the pass is part of that phase's implementation. Stay inside its write set, finish before code review starts, and make no commits; the phase's own close delivers the work.
- **Outside a phase:** commit refactoring on the current branch, separately from any behavior change, staging only the paths you edited, once the checks the change could break pass; one full gate precedes a push. [`policies/build-gates.md`](../../../policies/build-gates.md) and [`policies/commit-staging.md`](../../../policies/commit-staging.md) govern.
- **Methodology code** — the repository's own tooling and its tests — follows the methodology route in [`policies/review-lanes.md`](../../../policies/review-lanes.md).
- Run tests through the repository's own wrapper. To undo, reverse your own edits; the git commands [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md) reserves to the operator stay reserved, and an unexpected path in `git status` stops the pass.

## Report

Address the operator in the [`plain`](../plain/SKILL.md) register: what was applied and what shows behavior held; what is proposed and what each proposal would change; what is handed off; what was deliberately left alone; which checks ran.
