# Policy: Activity Log Discipline

Authority mode follows [four-canonical-agents.md](four-canonical-agents.md). Product primary mode uses independent advice and primary acceptance; delegated product mode retains approval verdicts and bounded revision loops. References below to reviewer assent or mandatory re-review govern delegated work only. Required objective gates and truthful evidence apply in both modes. All methodology work, including teach/learn, follows [review-lanes.md](review-lanes.md): one-shot by the primary, no delegated production or review, and commit/fast-forward-push authority after required checks.

`log/entries/` is the **append-only** record of what has been done to this repository. It is written by the writers named in the table below, never by hand. Do not hand-edit historical entries.

## What `log/entries/` is

`log/entries/` carries two kinds of entry, and every entry belongs to exactly one named writer.

**Phase entries**, written by `kickoff`:

- A START/END pair per phase, plus append-only `END (correction)` blocks when explicit user feedback corrects an already closed phase.
- The primary artifact the human reviews after `kickoff` finishes.

**Repository-operation entries**, written by the writer that performed the operation. These record work done *to* the repository rather than *through* the plan, which is why they carry no phase id and no status transition:

| Entry heading | Written by | Records |
|---|---|---|
| `LEARN` | `learn` | Patterns absorbed from a donor repository. |
| `TAUGHT FROM TEMPLATE` / `TAUGHT FROM DONOR` | `teach` | Patterns exported to a target repository. |
| `SWEEP (<focus>)` | `sweep` | A maintenance pass over the rule surfaces: what was retired, graduated, and left open. |
| `SWEEP-CODING (<kind>)` | `sweep-coding` | The same longitudinal pass over the coder ↔ critic loop: harvested code-review verdicts and coder failure analyses, reason categories, attributions, corrections. Reads its latest entry the same way. |
| `SWEEP-PLANNING (<kind>)` | `sweep-planning` | A longitudinal pass over harvested review verdicts: window, coverage, reason categories with counts, attributions, and the corrections applied or filed. The next run reads the latest entry to set its window and compute deltas. |
| `METHODOLOGY SCOPE` / `END — METHODOLOGY <subject>` | the agent invoking the direct-implementation route ([review-lanes.md](review-lanes.md) § Methodology improvements) | The records of one direct methodology change. The terminal block is always written at close; the scope block (approved outcome, surfaces in scope, explicit exclusions) is written before the work only for a transfer, for work spanning sessions, or for agent-initiated work, and otherwise its content is stated in the close ([review-lanes.md](review-lanes.md) § Methodology improvements). The terminal block is written at close, carrying changed paths, primary self-checks, candidate, gate results and remaining human criteria. The close is composed by `bin/multioperator append-terminal`, which supplies the `Lessons:` structure; `append` refuses a methodology close under any other heading (2026-11-10), because a bare `METHODOLOGY` heading skipped the Lessons contract. Closes already recorded under earlier headings stand. |

The `Only finalized evidence may claim exact timing` rule and the START/END formats below govern phase entries. A repository-operation entry has no fixed schema beyond a `## <YYYY-MM-DD HH:MM> — <HEADING>` line and the same append-only, no-back-dating, no-fabrication rules; each owning writer defines its own body.

A writer that is not in that table does not write to `log/entries/`. Adding a row is a policy amendment, not a skill author's decision — the point of the table is that a reader can tell, from this file alone, whether an entry had authority to exist. The `METHODOLOGY` row is the one non-skill writer, added by operator amendment on 2026-09-05 because the direct-implementation route is a route rather than a skill and its close still owes a terminal record. That route's first close, written the same day under an `END —` heading before this row existed, is authorized by this amendment and is not rewritten; append-only means the heading it carries stands.

## What `log/entries/` is not

- A status indicator. Status is folded from `plan/events/` ([`phase-status.md`](phase-status.md)).
- A planning document. Plans live in `plan/` and per-session conversational planning context.
- A commit message. `kickoff` writes a separate factual commit message when it delivers the phase ([`human-in-the-loop.md`](human-in-the-loop.md)). The END block records the standing delivery policy or an explicit user restriction *before* the handoff gate; the actual delivery outcome happens afterward, is reported to the user, and is never written back into tracked state.
- A general-purpose changelog. (A `CHANGELOG.md` is a different artifact, owned by humans for end-user audiences.)
- An action queue for the human. The live set of items only the user can resolve lives in [`../user-actions/`](../user-actions/) (one file per action; closed in `../user-actions-archived/`), governed by [`user-actions.md`](user-actions.md). `log/entries/` records what happened; `user-actions/` records what's pending on the human.

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

**Only finalized evidence may claim exact timing.** An END block's trace timing is the machine-generated projection from a finalized trace. Awaiting-user-input timing comes from the separate closed operator-park ledger: same-boot intervals may claim exact monotonic duration; cross-boot intervals must say non-exact calendar duration. Open, malformed, or unknowable intervals may not claim zero or an exact total. Narrative wall-clock observations remain separate and are never presented as exact.

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

The `Acceptance:` field is likewise mandatory, and both halves are written even when one is `None`. It is the per-phase record of the boundary in [`human-in-the-loop.md`](human-in-the-loop.md): what the orchestrator closed on its own evidence, and what is waiting on the user's judgment. Writing only the objective half would let "delivered" read as "accepted"; writing only the parked half would hide what the gate actually proved. The `Delivery:` field records the policy in force *before* the handoff gate — never a predicted outcome.

When a phase pauses (not completes), the END block uses the same format but adds a `Pause reason:` line and leaves the canonical event head in progress.

## Follow-up correction format

For an inter-phase correction, preserve the historical START/END pair and completed phase status, and append the record below. If the operator chose an inserted phase/sub-phase instead, use its own normal START/END records with formal planning and reviews; do not present it as an unreviewed inter-phase correction.

Use `./bin/multioperator append-terminal --root . --writer <operator> --content <content.json>` for direct terminal entries instead of copying boilerplate. Supply the shared semantic content contract: `title` (a one-line terminal label beginning with `END` or `PARK`, such as `END (correction)`), `body` (substantive Markdown without a handwritten Lessons field), and `lessons` (an explicit nonempty array of learning strings, or `["none"]` only when that is the actual supplied answer). The script composes the header and standalone fields, validates with the shared terminal predicate, and appends through the locked immutable writer to `log/entries/`; it never supplies a lessons answer or claims acceptance. For phase acceptance, use `compose-terminal --content <content.json> --output <fresh-block.md>` first, then pass that exact prepared file to the existing evidence close operation, which owns acceptance and publication. Both commands accept `--at <observed-UTC>`; omitted timestamps are read from the current clock. Existing raw `append` remains for nonterminal records and already prepared evidence-close bodies, with the same terminal guard.

```markdown
## <YYYY-MM-DD HH:MM> — END (correction)
<Phase heading>

Follow-up route:
- inter-phase implementation without formal review — <risk/size reason>
- Phase recommendation: <inserted sub-phase normally recommended for high-risk/large work, or not needed for a small low-risk correction>
- Operator ruling: <attributable route/scope decision, or existing authority for a small low-risk correction>

Role model/venue:
- Implementation: <primary or already-authorized delegate>
- Formal planning/reviews: not invoked — inter-phase route

Files changed:
- <path> — <brief description of correction>

Build status:
- <focused and touched-surface validation evidence>

Delivery:
- default — commit + fast-forward push after validation | restricted: <user's words, verbatim> | parked: <reason>

Lessons:
- <actual lesson and disposition, or an explicitly supplied "none">

Remaining:
- <anything significant left incomplete, or "None">
```

This block records the approved inter-phase scope and route; it does not reopen the phase or change its `✅` marker. High-risk or large/cross-cutting work normally receives an inserted sub-phase recommendation, but the operator may choose inter-phase implementation without formal review. That ruling never waives tests, applicable gates, safety/permissions or preservation of earlier evidence and consumed review accounting. New consequential scope needs explicit authorization, not a silently invented phase.

## Rules

1. **Immutable entries by exact bytes.** Use `./bin/multioperator append --root . --writer <operator> --body <body.md> --at <observed-UTC>`; a fresh entry records its writer, sequence, exact predecessor and body digest. Writers produce only the entry kinds authorized above. A log envelope is attribution, not a grant. Never patch, relocate, delete or rewrite a published entry; a correction is another record. The staged validator checks committed entry immutability.
2. **Named writers only; humans read.** The table names authorized operation kinds; the envelope names the actual current operator. A migration import has explicit unknown historical authorship and exact original byte offsets, never fabricated attribution. New entries use a real current writer, not `unattributed-import`.
3. **Timestamps are real.** Read the current clock before writing; the envelope stores timezone-aware UTC. Per-writer time cannot regress. Cross-writer presentation order is not exact causal timing. Imported old clock disagreements remain exact old bytes.
4. **The END block is a contract.** Report actual checks, failed commands, warnings, remaining human criteria and evidence honestly. Never claim manual observation or acceptance on another person's behalf. Exact timing comes only from finalized measured evidence.
5. **The handoff gate closes the candidate.** Terminal entries and all tracked close writes precede the bare `./bin/check all`. No tracked write follows a successful final gate. If a gate fails, retain the failed entry/evidence and append a truthful correction after fixing the attributable defect; never rewrite the earlier record to conceal the failure.
6. **Corrections preserve originals.** A new correction can identify the earlier entry and its digest and explain a wrong recorded time or outcome. It never changes that earlier envelope, effective history or consumed accounting. No flat-file chronology relocation or permanent old-format reader remains.
7. **Bounded repair keeps custody and history.** Follow [orchestration-control-plane.md](orchestration-control-plane.md) and the actual owner authority. Ambiguity, unknown ownership or a substantive scope change is reported; mechanical success does not grant the next action.
8. **A diagnosed hook refusal is work to finish safely.** Preserve rejected originals, correct the attributable unpublished input, publish an explicit later correction when a record already exists, and rerun `./bin/multioperator validate --root . --staged` plus every affected candidate gate. Never bypass a hook, mutate committed history or edit another writer's record.

9. **Read the clock, then write the record.** Capture a measured field, look at the value, and write the record from what you read. Never compose a timestamped block and the command that reads the clock in one breath: the value written is then an estimate, and in an append-only log a wrong one costs a correction block — which can carry its own wrong timestamp and cost a second. This generalizes past timestamps to any field that is *measured* rather than chosen. *(Graduated from `vengeful-shoebill`, 3 occurrences — `lessons-archived/vengeful-shoebill.md`.)*

## Why append-only

Two reasons:

- **Audit trail.** When the human asks "when did we decide to do X?", the log is the source of truth. Edited history loses the answer.
- **Restart robustness.** When `kickoff` is re-run after a crashed session, it reads the most recent unmatched START block to know what to resume. Editing blocks invalidates the heuristic.

## Discovery and retention

Entries remain in their canonical durable home. `./bin/multioperator render --root .` creates ignored `.collaboration-views/LOG.md` for reading; it is reproducible and never authoritative. Filter named entry metadata or search bodies instead of loading the entire history. Required unique evidence and immutable historical records are retained under the normal durability and delivery-resource policies; neither age nor a generated view authorizes purging them.
