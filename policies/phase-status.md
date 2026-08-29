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
- On phase completion: `🚧` → `✅`, advance the next `⏳` row to `⬅️` per the dependency graph, and append an END block to `LOG.md`.
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

The checker runs inside the authoritative full gate:

```bash
./bin/check all
```
