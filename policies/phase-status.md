# Policy: Phase Status — One Source of Truth

Phase status lives in **`plan/INDEX.md`** and nowhere else. This is a hard rule, not a convention.

## The status legend

```text
⏳ Not Started
⬅️ Next (only one at a time)
🚧 In Progress
✅ Completed
```

## Where status lives

- **`plan/INDEX.md`'s phase table.** The phase table is the *single source of truth*. Each row carries one status emoji in its rightmost column.
- **Nowhere else.** Per-phase files (`plan/phase-*.md`) do *not* carry a `status` field in their frontmatter. Their frontmatter is `id`, `title`, `depends_on`, `informs` — no more.

## Why one place

Duplicating status across files invites drift. The orchestrator (`/kickoff`) reads exactly one file to know what to do next; humans read exactly one file to know what the project's state is; reviewers read exactly one file to verify the orchestrator did the right thing.

## Who flips the markers

`/kickoff` owns all status transitions:

- On phase entry: `⬅️` → `🚧` and append a START block to `LOG.md`.
- On phase completion: `🚧` → `✅`, advance the next `⏳` row to `⬅️` per the dependency graph, and append an END block to `LOG.md`.
- On phase pause: leave the row at `🚧` and append an END block to `LOG.md` documenting the pause reason. Do not advance `⬅️`.

Humans may flip markers manually only in two cases:

- **Bootstrap.** When a brand-new `plan/INDEX.md` is created, the human assigns `⬅️` to Phase 1.
- **Recovery.** When `/kickoff` failed partway through and left the state inconsistent, the human corrects the table — and ideally adds a note to `LOG.md` explaining the recovery.

## "Only one `⬅️` at a time"

This is invariant. The dependency graph at the top of `plan/INDEX.md` permits parallel phases in principle (`P3` and `P4` both depend on `P2`), but the orchestrator works on one phase per session.

If two rows are `⬅️` after a recovery, `/kickoff` picks the earliest one in the dependency graph and warns the human.

## Verification

A clean state satisfies all of:

```bash
# Exactly one ⬅️ phase-table row in INDEX.md
[ "$(grep -E '^\| \[Phase ' plan/INDEX.md | grep -c '⬅️')" = 1 ] || echo "wrong ⬅️ count in phase table"

# No status: field in any per-phase frontmatter
for f in plan/phase-*.md; do
  awk 'BEGIN{n=0} /^---$/{n++; next} n==1 && /^status:/{print FILENAME ": status field in frontmatter"; exit}' "$f"
done

# No status-declaration line in per-phase bodies. (Narrative mentions of the
# status emojis inside prose are fine; declarations like "Status: 🚧" or a
# frontmatter "status: in_progress" are the failure modes we guard against.)
grep -nE '^[Ss]tatus *: *(⏳|⬅️|🚧|✅|not started|next|in progress|completed)' plan/phase-*.md && \
  echo "status-declaration line in phase body" || true
```
