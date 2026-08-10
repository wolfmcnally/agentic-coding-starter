# Policy: Activity Log Discipline

`LOG.md` is the **append-only** record of phase work in this repo. It is owned by `kickoff`. Do not hand-edit historical entries.

## What `LOG.md` is

- The narrative record of phase entries and exits.
- A START/END pair per phase, plus append-only `END (correction)` blocks when explicit user feedback corrects an already closed phase.
- The primary artifact the human reviews after `kickoff` finishes.

## What `LOG.md` is not

- A status indicator. Status lives in `plan/INDEX.md` ([`phase-status.md`](phase-status.md)).
- A planning document. Plans live in `plan/` and per-session conversational planning context.
- A commit message. Commits are written separately by the human.
- A general-purpose changelog. (A `CHANGELOG.md` is a different artifact, owned by humans for end-user audiences.)
- An action queue for the human. The live set of items only the user can resolve lives in [`../user-actions/`](../user-actions/) (one file per action; closed in `../user-actions-archived/`), governed by [`user-actions.md`](user-actions.md). `LOG.md` records what happened; `user-actions/` records what's pending on the human.

## START block format

`kickoff` appends this when a phase enters `🚧`:

```markdown
## <YYYY-MM-DD HH:MM> — START
<Phase heading>

Planned work:
- <deliverable 1>
- <deliverable 2>
- ...
```

The planned-work list is the phase file's Deliverables list, copied verbatim (trimmed to bullet text). If the phase has no Deliverables section, fall back to the phase's Goal paragraph rephrased as bullets.

## END block format

`kickoff` appends this when a phase leaves `🚧`:

```markdown
## <YYYY-MM-DD HH:MM> — END
<Phase heading>

Files changed:
- <path> — <brief description of change>
- ...

Build status:
- <gate name>: OK | N/A | failed (<short reason>)
- ...

Manual checks for user:
- <named check that needs human eyes> | None

Lessons:
- <slug> filed/recurred — <one-line lesson, scope> | none
- graduation DECIDE: <slug> → <proposed surface> | none

Remaining:
- <anything significant left incomplete, or "None">
```

Build-status lines are project-specific. A Python project might list `ruff check`, `ruff format`, `pytest`. A polyglot project lists every surface's gate. Use `N/A` for gates that don't apply to this phase.

The `Lessons:` field is part of the minimum END contract because the harvest question is mandatory at every close ([`lessons.md`](lessons.md)): `none` is a valid answer, but the field may not be omitted. Ledger content and graduation mechanics are governed by `policies/lessons.md`; `kickoff`'s Step 10 may extend this block with additional evidence fields.

When a phase pauses (not completes), the END block uses the same format but adds a `Pause reason:` line and leaves the phase row in `plan/INDEX.md` at `🚧`.

## Follow-up correction format

When concrete user feedback changes code after a phase has already closed, preserve the historical START/END pair and append:

```markdown
## <YYYY-MM-DD HH:MM> — END (correction)
<Phase heading>

Follow-up route:
- direct fix | coder only | full cycle — <risk/size reason>

Role model/venue:
- Coder: skipped (direct fix) | model=<model> effort=<effort|default> venue=<native|claude|codex>
- Critic: skipped (direct fix or coder only) | model=<model> effort=<effort|default> venue=<native|claude|codex>

Files changed:
- <path> — <brief description of correction>

Build status:
- <focused and touched-surface validation evidence>

Remaining:
- <anything significant left incomplete, or "None">
```

This block records a correction to an already authorized goal; it does not reopen the phase or change its `✅` marker. New scope gets a new phase and a normal START/END pair.

## Rules

1. **Append-only.** Never edit a historical START or END block. Mistakes get a follow-up END block ("END (correction)") with the corrected information.
2. **`kickoff` writes; humans read.** Humans don't write to `LOG.md` directly. The exceptions are bootstrapping (creating the initial `# Activity Log` header) and recovery (when `kickoff` failed and left an inconsistent state).
3. **Timestamps are real.** Use the orchestrator's actual wall-clock time when the block was written. Do not back-date.
4. **The END block is a contract.** When the orchestrator writes an END block claiming the phase is done, the human is entitled to expect that every claim in the block is true. Fabricated evidence is the most dangerous failure mode this policy guards against; the orchestrator must never claim a build gate passed when it didn't, never claim a manual check was performed by the orchestrator, never embellish the file list.

## Why append-only

Two reasons:

- **Audit trail.** When the human asks "when did we decide to do X?", the log is the source of truth. Edited history loses the answer.
- **Restart robustness.** When `kickoff` is re-run after a crashed session, it reads the most recent unmatched START block to know what to resume. Editing blocks invalidates the heuristic.

## Length

`LOG.md` grows monotonically over the project's life. That is expected and fine. The file is for grep, not for browsing.

If a project's log grows so large that it slows down agent reads, split it: archive entries from year N into `LOG-<year>.md` and keep `LOG.md` for year N+1. Reference the archive from `LOG.md`'s header.
