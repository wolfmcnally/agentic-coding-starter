# Policy: Phase Status — One Source of Truth

Phase status lives in **`plan/INDEX.md`** and nowhere else. This is a hard rule, not a convention.

## The status legend

```text
⏳ Not Started
⬅️ Next (at most one at a time; required only while idle and incomplete)
🚧 In Progress
✅ Completed
```

## Where status lives

- **`plan/INDEX.md`'s phase table.** The phase table is the *single source of truth*. Each row carries one status emoji in its rightmost column.
- **Nowhere else.** Per-phase files (`plan/phase-*.md`) do *not* carry a `status` field in their frontmatter. Their frontmatter is `id`, `title`, `depends_on`, `informs`, and optionally `review_lane` (a phase property, not a status — see [`review-lanes.md`](review-lanes.md)) — no more.

## Why one place

Duplicating status across files invites drift. The orchestrator (`kickoff`) reads exactly one file to know what to do next; humans read exactly one file to know what the project's state is; reviewers read exactly one file to verify the orchestrator did the right thing.

## Who flips the markers

`kickoff` owns all status transitions:

- On phase entry: `⬅️` → `🚧` and append a START block to `LOG.md`.
- On phase completion: `🚧` → `✅`, advance `⬅️` to the lowest-numbered `⏳` row whose dependencies are complete, and append an END block to `LOG.md`.
- On phase pause: leave the row at `🚧` and append an END block to `LOG.md`
  documenting the pause reason. Do not advance `⬅️`; zero next rows is valid
  while work remains active.

Humans may flip markers manually only in two cases:

- **Bootstrap.** When a brand-new `plan/INDEX.md` is created, the human assigns `⬅️` to Phase 1.
- **Recovery.** When `kickoff` failed partway through and left the state inconsistent, the human corrects the table — and ideally adds a note to `LOG.md` explaining the recovery.

## The phase-ledger state machine

Every phase-table data row carries exactly one recognized status marker. The
number of `⬅️` rows depends on lifecycle state:

- **Idle and incomplete:** exactly one row is `⬅️`.
- **Active:** zero or one row may be `⬅️`. Zero is normal after the executable
  row changes to `🚧`; one is normal when a decomposed parent remains `🚧`
  while its next child is queued.
- **Complete:** zero rows are `⬅️` because no work remains to advance.
- **Always invalid:** more than one `⬅️`, a phase-table row with no recognized
  status, or a row carrying multiple recognized statuses.

The dependency graph may expose parallel opportunities, but the orchestrator
queues at most one executable phase. If recovery finds two `⬅️` rows, the
ledger is invalid; `kickoff` stops and the human corrects it rather than letting
the orchestrator choose through ambiguity.

## Numbers follow the order of upcoming work

Among phases that have not started, a phase's number says when it runs. A reader who sees Phase 5 and Phase 6 both waiting should be able to assume 5 comes first, and the next marker advances to the lowest-numbered waiting phase whose dependencies are complete. Doing a higher-numbered phase while a lower-numbered one is ready is running the plan out of sequence, and the remedy is to renumber, not to explain the order in a note. (Operator ruling, 2026-10-07.)

So a phase inserted ahead of waiting work takes the number of the first phase it must precede, and that phase, every later waiting sibling, and all their sub-phases move up by one. The same holds one level down: a sub-phase inserted at 3.2 moves the waiting 3.2 to 3.3. A deterministic script does the whole move:

```bash
./bin/renumber-phases insert-before 5 --reason "<one sentence on why the phase is inserted>"
```

It renames the phase files, rewrites their `id`, `depends_on` and `informs` fields, the phase table, the dependency graph and every plan link, and adds a dated renumbering record to the ledger that says how to read the old numbers. The author then adds the new phase's file and row at the number that was opened. Renumbering by hand is how a `depends_on` gets left pointing at the wrong phase.

What does not move:

- **A phase that is in progress or completed keeps its number.** Logs, commits, reports and lessons already refer to it. The script refuses when a started phase would move, so an insertion goes after the last started phase at that level; work that must precede an in-progress phase is a sub-phase of it or a decision for the operator.
- **An abandoned path keeps its numbers.** A phase that was retired or set aside is history; its number is not reclaimed, and closing the gap it leaves is not a reason to renumber.
- **Dated history is never rewritten.** `LOG.md`, lessons, user actions and earlier ledger notes keep their wording. The renumbering record is the decoder ring, and the script lists the prose mentions it left alone so each can be read.
- **The unstarted children of an in-progress parent are upcoming work** and do renumber among themselves.

The checker enforces the two parts of this that can be read mechanically: phase-table rows run in ascending phase order, and no waiting phase depends on a waiting phase numbered after it. Whether an undeclared ordering exists between two waiting phases is a judgment the checker cannot make; declare the dependency, and the numbering follows.

## Verification

The deterministic catalog checker validates the lifecycle state and
one-status-per-row invariant, rejects a `status:` field in any per-phase
frontmatter, and rejects status-declaration lines in phase bodies. Narrative
mentions of the status emojis in prose are fine — only a *declaration* (a
frontmatter key or a `Status: ✅`-shaped line) creates a second source of
truth, and quoted forms inside fenced blocks or inline code spans are exempt:

```bash
./bin/check-catalogs
```

When a child phase closes, the close operation additionally runs
`./bin/check-catalogs --closing-phase <id>`. The child must already be `✅`,
and its direct parent must either be `✅` too or remain `🚧` with another
drafted, incomplete direct child. A close may not strand a decomposed parent
whose ledger promises work but names no executable continuation.

The same checker refuses a phase table whose rows are out of ascending phase
order, and a not-started phase whose `depends_on` names a not-started phase
numbered after it.

The checker runs inside the authoritative full gate:

```bash
./bin/check all
```

## Prospective accepted closure

Accepted evidence close may validate an external proposed ledger using `--ledger-after`. The live captured ledger remains unchanged through acceptance. Only the closing active phase's completion marker may change. A child still requires a completed parent or an active parent with another real drafted incomplete child. A simultaneous parent completion additionally requires `--parent-run` identifying separately accepted, current parent evidence from this repository. The successor child must be prepared before final review, not invented after acceptance.

The close record binds both ledger digests and the accepted product. Apply the exact proposed ledger and run the same close command with `--verify-handoff` before any further ripple or arrow edits. This verification checks the actual ledger, product and child continuation; it does not certify delivery or replace the final full handoff gate. The ordinary catalog checker and standalone log writer retain their checks against the live ledger.

A prospective close may additionally advance at most one existing not-started phase to next, selected in dependency order during close preparation. This exact marker transition is bound with the completion markers; it prevents a final-child close from creating an idle incomplete ledger without a next phase. A close that must *move* an existing marker binds one paired transition instead: exactly one ⬅️→⏳ alongside exactly one ⏳→⬅️, leaving at most one marker in the result. An unpaired unqueue refuses, because it would leave the ledger with no truthful continuation.

## Where the next marker must sit after a child close

A close asks where the marker *must be now*, never where it already sat. A phase started by name rather than by following the marker leaves the marker somewhere else for the whole phase, and a closing orchestrator that reasons from the ledger's current state records that it "stays where it was" — three times running, in a donor project, while the count-based ledger check passed each time because exactly one marker was present.

So the rule is positional, not numeric: when a child closes and its parent stays 🚧, the ⬅️ marker must sit on a non-completed direct child of that parent, or on nothing, and it moves in the same edit as the status flip. `bin/check-catalogs --closing-phase` refuses a marker stranded elsewhere and names both where it sits and which children were available. A close that deliberately queues work outside the parent's subtree — the dependency-ordered successor is elsewhere — passes `--next-marker-reason` (to `bin/check-catalogs` directly, or through `bin/kickoff-evidence close`, which forwards it) and records that reason in the close block.
