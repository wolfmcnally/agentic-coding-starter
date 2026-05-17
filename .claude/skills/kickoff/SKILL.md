---
name: kickoff
description: >-
  Orchestrate a single phase of plan/ end-to-end: pick up the next phase,
  plan, review plan, implement, review code, build/test, update status
  markers in plan/INDEX.md, and log. Language- and surface-agnostic; the
  project's CLAUDE.md and phase file declare which build gates to run.
  Invoke as /kickoff (picks up the ⬅️ phase) or /kickoff phase N (targets
  a specific phase).
---

# Kickoff: Single-Phase Session

Orchestrate a full implementation of one phase under `plan/`, from plan through working code, following the plan → plan-review → code → code-review → build pipeline.

This skill is language- and surface-agnostic. The project's `CLAUDE.md` declares the conventions; the phase file declares the deliverables; the planner picks the build gates; the orchestrator runs them.

## Current context

- Branch: `git branch --show-current`
- Phase markers: `grep -E '^\| \[Phase ' plan/INDEX.md 2>/dev/null || echo "(plan/INDEX.md missing)"`
- Recent log: `tail -20 LOG.md 2>/dev/null || echo "(no log)"`

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- If empty, Step 1 picks up the `⬅️` phase.
- If `phase N` or `phase N.M` (e.g., `phase 1`, `phase 1.3`), target that specific phase file `plan/phase-<id>.md`.
- If free text, treat it as a phase description and try to match it against a phase row in `plan/INDEX.md`. If nothing matches, ask the user which phase they mean rather than guess.

## Workflow

### Step 1: Identify the phase

Read `plan/INDEX.md` (the authoritative phase ledger) and locate the phase to work on. Status markers live in the `INDEX.md` phase table, not in the per-phase files (see [`policies/phase-status.md`](../../../policies/phase-status.md)).

- **No arguments**: find the row whose status is `⬅️` in the phase table. If multiple rows are marked `⬅️` (should never happen), pick the earliest in the dependency graph and warn the user.
- **`phase N` / `phase N.M`**: find the row whose link is `[Phase <id>](phase-<id>.md)`.
- **Free text**: resolve to a phase row or ask the user.

Tell the user which phase you are picking up and the path to its file (`plan/phase-<id>.md`).

### Step 2: Flip marker and open the log

Update `plan/INDEX.md` so the target row's status cell is `🚧`. **Do not edit the target `plan/phase-<id>.md` file's frontmatter or body** — status is stored only in `INDEX.md` (see [`policies/phase-status.md`](../../../policies/phase-status.md)).

Append a START entry to `LOG.md`. Create `LOG.md` if it does not exist (with the header described in [`policies/log-discipline.md`](../../../policies/log-discipline.md)). Format:

```
## <YYYY-MM-DD HH:MM> — START
<Phase heading>

Planned work:
- <deliverable 1>
- <deliverable 2>
- ...
```

Use the phase's "Deliverables" list from `plan/phase-<id>.md` verbatim (trimmed to the bullet text). If the phase has no Deliverables section, fall back to the phase's Goal paragraph rephrased as bullets.

### Step 3: Plan

Delegate the planning stage to the `phase-planner` subagent (Claude Code) / the `phase-planner` agent (Codex). Pass it:

- The phase identifier (e.g., `Phase 1.3`) and heading.
- The full phase text from `plan/phase-<id>.md` (copy/paste, do not summarize).
- Nothing about the agent's own procedure — the role definition already covers the reading protocol and output format.

Wait for the plan.

### Step 4: Review the plan

Delegate the review stage to the `plan-reviewer` agent. Pass it:

- The phase reference and heading.
- The full phase text from `plan/phase-<id>.md`.
- The full plan text from Step 3.

**If `APPROVED`**: proceed to Step 5. Show the user a brief summary plus any Minor Corrections (do not wait for explicit approval unless the user asked to review plans themselves).

**If `REVISE`**: re-run `phase-planner` with the reviewer's feedback appended to the prompt, then re-run `plan-reviewer`. Allow up to 2 revision cycles. If still not approved after 2, present the plans and outstanding issues to the user for a manual decision.

### Step 5: Implement

Delegate implementation to the `phase-coder` agent. Pass it:

- The approved plan (full text, including any Minor Corrections from the plan-reviewer appended as a note).

Wait for the coder. Collect the list of files created or modified, the Build Status block, and the Manual Checks list.

### Step 6: Review code

Delegate code review to the `code-critic` agent. Pass it:

- The approved plan (full text).
- Any Minor Corrections the plan-reviewer issued.
- The list of files the coder created or modified.

**If `APPROVED`**: proceed to Step 7.

**If `REVISE`**: re-run `phase-coder` with the critic's feedback, then re-run `code-critic`. Allow up to 2 revision cycles. If still not approved, present the issues to the user.

### Step 7: Final build gate

Even though the coder ran the build commands, re-run them in the orchestrator context to guarantee the merged state is green. Build commands depend on the surfaces the phase touched.

Identify "touched surfaces" by looking at the files the coder reported plus `git status`. Then run the gates declared in the plan's **Build Gate Sequence** section, in order.

The project's primary build gates come from the project's actual tooling. For the **Agentic Coding Starter Template itself**, the example Python project lives under `project/` per [`policies/project-isolation.md`](../../../policies/project-isolation.md), so the gates are:

```
cd project && uv run ruff check example tests && uv run ruff format --check example tests && uv run pytest -q
```

The `cd project && ...` pattern is the canonical shape (single executable line; uniform across language ecosystems). Projects that opt out of the `project/` convention put the metadata at the root and drop the `cd project &&` prefix. A project derived from this template via `/starter` may have different gates — Node, Rust, Go, polyglot. The planner is responsible for listing them; the orchestrator runs whatever the planner listed.

If any build gate fails:

1. Classify the failure:
   - **Coder error** (syntax, type mismatch, missing import, wrong signature, failing test assertion) → re-run `phase-coder` with the error output and the plan.
   - **Plan error** (wrong file path, missing module, architectural mismatch) → re-run `phase-planner` with the error, then `phase-coder` with the updated plan. Counts as one cycle.
   - **Environment error** (missing toolchain, missing system dependency, missing credential) → report to the user immediately; do not retry.
2. Re-run the failing gate after the fix.
3. On success, re-run `code-critic` on the files the coder touched during the fix. If `REVISE`, back to coder (counts against revision cycles).
4. Allow up to 3 fix cycles. If still failing, present to the user.

### Step 8: Phase-specific acceptance gates

Each phase declares its own empirical acceptance checks under `Acceptance` in `plan/phase-<id>.md`. The orchestrator runs whichever of those checks are mechanically executable (shell commands, smoke scripts, curl probes, deterministic comparisons) and reports the rest as **manual checks** for the user.

A failed acceptance gate routes back through Step 7's fix loop.

Per [`policies/acceptance-empirical.md`](../../../policies/acceptance-empirical.md), every acceptance criterion is either executable or named manual. Treat ambiguous criteria as manual and flag them in the END block.

### Step 9: Update status markers

In `plan/INDEX.md`'s phase table (and only there):

1. Flip the completed phase's status cell from `🚧` to `✅`.
2. Find the next `⏳` row in the linear order implied by the phase dependency graph at the top of `INDEX.md` (honoring parallel opportunities). Change it to `⬅️`. Only one row is `⬅️` at a time.

If the phase is only partially complete (the user paused mid-way), leave it `🚧` and do not advance `⬅️`.

**Never edit the per-phase file's frontmatter or body to record status.** Per-phase frontmatter is `id` / `title` / `depends_on` / `informs` only.

### Step 10: Close the log and report

Append an END entry to `LOG.md`:

```
## <YYYY-MM-DD HH:MM> — END
<Phase heading>

Files changed:
- <path> — <brief>
- ...

Build status:
- <gate 1>: OK | N/A | failed (<short reason>)
- <gate 2>: OK | N/A | failed (<short reason>)
- ...

Manual checks for user:
- <named check> | None

Remaining:
- <anything significant left incomplete, or "None">
```

Then report to the user:

- Which phase was completed and which is next (`⬅️`).
- Files created/modified, grouped by surface.
- Build and gate status.
- Any Minor Corrections or Observations the reviewers noted that the user may want to track.
- Manual checks the user needs to perform that the orchestrator couldn't.

**Do not auto-commit.** The user drives commits, per [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md).

---

## Operating notes

- The four canonical role names (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`) are load-bearing. See [`policies/four-canonical-agents.md`](../../../policies/four-canonical-agents.md).
- The verdict header (`## Verdict: APPROVED` or `## Verdict: REVISE`) is parsed by string match. Mis-cased or rephrased verdicts break orchestration.
- Cross-harness: this same skill drives both Claude Code and Codex (the Codex entry point lives at `.codex/prompts/kickoff.md` and is a thin pointer to this file). Edit this canonical skill, not the wrapper.
- If your harness does not expose named subagents, perform the same role sequence locally by reading each `.claude/agents/<role>.md` directly and adopting that role's reading protocol and output format for the duration of the step.

## Local fallback

If the current platform does not expose named subagents, perform the same role sequence locally and follow the canonical role procedures in `.claude/agents/phase-planner.md`, `.claude/agents/plan-reviewer.md`, `.claude/agents/phase-coder.md`, and `.claude/agents/code-critic.md` directly. The agents' tool-stance and verdict format apply just the same.
