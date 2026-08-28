# Policy: Activity Log Discipline

`LOG.md` is the **append-only** record of what has been done to this repository. It is written by skills, never by hand. Do not hand-edit historical entries.

## What `LOG.md` is

`LOG.md` carries two kinds of entry, and every entry belongs to exactly one skill.

**Phase entries**, written by `kickoff`:

- A START/END pair per phase, plus append-only `END (correction)` blocks when explicit user feedback corrects an already closed phase.
- The primary artifact the human reviews after `kickoff` finishes.

**Repository-operation entries**, written by the skill that performed the operation. These record work done *to* the repository rather than *through* the plan, which is why they carry no phase id and no status transition:

| Entry heading | Written by | Records |
|---|---|---|
| `LEARN` | `learn` | Patterns absorbed from a donor repository. |
| `TAUGHT FROM TEMPLATE` / `TAUGHT FROM DONOR` | `teach` | Patterns exported to a target repository. |
| `SWEEP (<focus>)` | `sweep` | A maintenance pass over the rule surfaces: what was retired, graduated, and left open. |
| `SWEEP-CODING (<kind>)` | `sweep-coding` | The same longitudinal pass over the coder ↔ critic loop: harvested code-review verdicts and coder failure analyses, reason categories, attributions, corrections. Reads its latest entry the same way. |
| `SWEEP-PLANNING (<kind>)` | `sweep-planning` | A longitudinal pass over harvested review verdicts: window, coverage, reason categories with counts, attributions, and the corrections applied or filed. The next run reads the latest entry to set its window and compute deltas. |

The `Only finalized evidence may claim exact timing` rule and the START/END formats below govern phase entries. A repository-operation entry has no fixed schema beyond a `## <YYYY-MM-DD HH:MM> — <HEADING>` line and the same append-only, no-back-dating, no-fabrication rules; each owning skill defines its own body.

A skill that is not in that table does not write to `LOG.md`. Adding a row is a policy amendment, not a skill author's decision — the point of the table is that a reader can tell, from this file alone, whether an entry had authority to exist.

## What `LOG.md` is not

- A status indicator. Status lives in `plan/INDEX.md` ([`phase-status.md`](phase-status.md)).
- A planning document. Plans live in `plan/` and per-session conversational planning context.
- A commit message. `kickoff` writes a separate factual commit message when it delivers the phase ([`human-in-the-loop.md`](human-in-the-loop.md)). The END block records the standing delivery policy or an explicit user restriction *before* the handoff gate; the actual delivery outcome happens afterward, is reported to the user, and is never written back into tracked state.
- A general-purpose changelog. (A `CHANGELOG.md` is a different artifact, owned by humans for end-user audiences.)
- An action queue for the human. The live set of items only the user can resolve lives in [`../user-actions/`](../user-actions/) (one file per action; closed in `../user-actions-archived/`), governed by [`user-actions.md`](user-actions.md). `LOG.md` records what happened; `user-actions/` records what's pending on the human.

## START block format

`kickoff` appends this when a phase enters `🚧`:

```markdown
## <YYYY-MM-DD HH:MM> — START
<Phase heading>

Execution trace: <trace-id>
Baseline: <commit id> — <baseline-dependent criteria that reference it>

Planned work:
- <deliverable 1>
- <deliverable 2>
- ...
```

The planned-work list is the phase file's Deliverables list, copied verbatim (trimmed to bullet text). If the phase has no Deliverables section, fall back to the phase's Goal paragraph rephrased as bullets.

`Execution trace:` records the trace id opened for the phase ([`execution-telemetry.md`](execution-telemetry.md)), so START and END are mechanically joinable. The `Baseline:` line appears only when the phase carries a baseline-dependent acceptance criterion ("unchanged before and after", "byte-identical across the edit"): it records the commit id the comparison is against, per [`acceptance-empirical.md`](acceptance-empirical.md) § Baseline-dependent criteria. Omit the line when no criterion depends on a baseline.

**Only finalized evidence may claim exact timing.** An END block's trace timing
is the machine-generated projection from a finalized trace. Awaiting-user-input
timing comes from the separate closed operator-park ledger: same-boot intervals
may claim exact monotonic duration; cross-boot intervals must say non-exact
calendar duration. Open, malformed, or unknowable intervals may not claim zero
or an exact total. Narrative wall-clock observations remain separate and are
never presented as exact.

**Multi-session phases use suffixed blocks.** A phase that pauses and resumes across sessions appends `## <ts> — START (resumed)` when work re-enters, paired with its own END; a continuation that re-derives evidence rather than re-doing work may annotate the suffix (`START (evidence continuation)`). Suffixed blocks keep every session's record distinct instead of overwriting or re-editing the original START — the same append-only discipline, extended to the phase's whole lifetime. The most recent unmatched START of any suffix is the resume anchor.

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
- Handoff gate: runs after this tracked END block; completion is contingent on
  the ignored receipt from the final bare `./bin/check all`
- ...

Awaiting user input:
- <opened UTC> → <closed UTC|open>: <duration|unavailable> (<stable reason>; <basis>)
- Total: <union duration|unavailable> (<basis>)

Acceptance:
- Objective (independently reviewed, gate-proved, candidate-bound): <named criteria> | None
- Parked for the user: <named manual, perceptual, product, or custody criteria, and the `User Demo:` protocol when unrun> | None

Delivery:
- default — commit + fast-forward push after the handoff gate | restricted: <user's words, verbatim> | parked: <reason>

Lessons:
- <slug> filed/recurred — <one-line lesson, scope> | none
- graduation DECIDE: <slug> → <proposed surface> | none

Remaining:
- <anything significant left incomplete, or "None">
```

Build-status lines are project-specific. A Python project might list `ruff check`, `ruff format`, `pytest`. A polyglot project lists every surface's gate. Use `N/A` for gates that don't apply to this phase.

The `Lessons:` field is part of every truthful END or PARK contract because the harvest question is mandatory at every terminal seam ([`lessons.md`](lessons.md)): `none` is a valid answer, but the field may not be omitted. Ledger content and graduation mechanics are governed by `policies/lessons.md`; `kickoff` may extend the block with additional evidence fields.

The `Acceptance:` field is likewise mandatory, and both halves are written even
when one is `None`. It is the per-phase record of the boundary in
[`human-in-the-loop.md`](human-in-the-loop.md): what the orchestrator closed on
its own evidence, and what is waiting on the user's judgment. Writing only the
objective half would let "delivered" read as "accepted"; writing only the parked
half would hide what the gate actually proved. The `Delivery:` field records the
policy in force *before* the handoff gate — never a predicted outcome.

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

Delivery:
- default — commit + fast-forward push after validation | restricted: <user's words, verbatim> | parked: <reason>

Remaining:
- <anything significant left incomplete, or "None">
```

This block records a correction to an already authorized goal; it does not reopen the phase or change its `✅` marker. New scope gets a new phase and a normal START/END pair.

## Rules

1. **Append-only by exact bytes.** New blocks enter through `bin/log-append` at true EOF. The working and staged candidates must begin with the exact committed bytes; a semantically equivalent rewrite is still a violation. A committed mistake gets a later correction block. An uncommitted block may be relocated only by one unique content digest through `bin/log-relocate`, which preserves the committed prefix and every block identity.
2. **Skills write; humans read.** Only the skills named in the table above append to `LOG.md`, each writing only its own entry kind. Humans don't write to it directly. The exceptions are bootstrapping (creating the initial `# Activity Log` header) and recovery (when a skill failed partway and left an inconsistent state).
3. **Timestamps are real.** Use the orchestrator's actual wall-clock time when the block was written. Do not back-date.
4. **The END block is a contract.** When the orchestrator writes an END block claiming the phase is done, the human is entitled to expect that every claim in the block is true. Fabricated evidence is the most dangerous failure mode this policy guards against; the orchestrator must never claim a build gate passed when it didn't, never claim a manual check was performed by the orchestrator, never embellish the file list.
5. **The handoff gate closes the current block.** The active uncommitted END and
   other close writes remain contingent until a bare `./bin/check all` passes
   against the actual handoff tree. No tracked write follows that pass. A
   failure reopens and corrects the current uncommitted close; committed
   historical blocks remain append-only.
6. **Chronology corrections move effective time, never bytes.** A later exact `LOG CHRONOLOGY CORRECTION` block binds one earlier block digest, repeats its recorded anchor, and supplies a strictly later effective anchor no later than the correction record. Duplicate, missing, ambiguous, or backward corrections refuse.
7. **One bounded mechanical repair.** A novel bookkeeping failure may receive one in-memory-validated atomic repair under `policies/orchestration-control-plane.md`. A second attempt, ambiguity, substantive change, recurring signature, or failed byte verification parks.

## Why append-only

Two reasons:

- **Audit trail.** When the human asks "when did we decide to do X?", the log is the source of truth. Edited history loses the answer.
- **Restart robustness.** When `kickoff` is re-run after a crashed session, it reads the most recent unmatched START block to know what to resume. Editing blocks invalidates the heuristic.

## Length

`LOG.md` grows monotonically over the project's life. That is expected and fine. The file is for grep, not for browsing.

If a project's log grows so large that it slows down agent reads, split it: archive entries from year N into `LOG-<year>.md` and keep `LOG.md` for year N+1. Reference the archive from `LOG.md`'s header.
