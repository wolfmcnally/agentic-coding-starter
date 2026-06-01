# Policy: User Actions

The [`user-actions/`](../user-actions/) directory at the repo root is the **live queue** of action items only the human can perform. Deploys, console / dashboard / GUI checks, manual reconciliations, third-party logins, pricing decisions, signups, anything outside an agent's reach. Every agentic project ships with this directory from the first session.

A **user action** is one such item. Some user actions are *blocking* (work waits on them) and some are merely *tracked* (deferred until later) — the name does not presume which, the `status` / `needed_at` frontmatter says.

This policy prescribes the directory's layout, the per-file format, the lifecycle, and the agent-vs-human checkoff discipline. The policy *is* the format spec — there is no separate template.

## One file per action

Each user action is its own markdown file:

- **Open items** live in `user-actions/<slug>.md`.
- **Closed items** live in `user-actions-archived/<slug>.md`.

The **filename is the slug** (the two-word code-name): `warping-butterfly.md`. There is intentionally **no index file**. A central index would be a single point of contention when multiple agents edit the queue concurrently; one-file-per-action is precisely what avoids that. Each file is fully self-contained — all metadata is in its YAML frontmatter, and cross-item dependencies are expressed in `blocks:`, so nothing needs a shared list to be understood.

## What `user-actions/` is

- The interrupt-driven queue of human-only follow-ups, parallel to `LOG.md` (history) and `plan/INDEX.md` (phase ledger).
- A live, mutable directory: files get added as agents hit human-only walls; files get moved to `user-actions-archived/` as resolutions land; archived files are the permanent audit trail of what was asked, when, and how it resolved.
- The set a session can glob to know "what is the human blocking right now."

## What `user-actions/` is not

- Not a status indicator. Phase status lives in `plan/INDEX.md` per [`phase-status.md`](phase-status.md).
- Not a history log. Append-only narrative lives in `LOG.md` per [`log-discipline.md`](log-discipline.md).
- Not a plan. Plans live in `plan/` per [`briefs-and-policies.md`](briefs-and-policies.md).
- Not a backlog of agent work. Anything an agent can do itself goes into the plan or gets done; only items requiring the human's hands belong here.

## Format

### Frontmatter (all metadata)

Every file opens with YAML frontmatter. All structured metadata lives here; the body holds only human-readable prose.

```yaml
---
slug: warping-butterfly        # matches the filename
title: Deploy the new CDK stack
status: pending                # pending | deferred  (open)  ·  done | closed | superseded  (archived)
category: infra                # freeform short label — e.g. infra | tooling | credentials | decision | access
urgency: high                  # high | medium | low
blocks:                        # what this gates — free text and/or other slugs
  - The rollup smoke test
filed: 2026-01-31              # ISO date filed
needed_at: now                 # now | "Phase 3" | 2026-02-15  (when it can/should be acted on)
source: critic                 # optional — which loop filed it: plan | critic | kickoff | <skill-name>
refs:                          # optional — related files
  - bin/deploy-infra
---
```

Archived files additionally carry:

```yaml
status: done                   # done | closed | superseded
closed: 2026-01-31             # ISO date closed
```

`status` absorbs the old section headings (`## Pending`, `## Deferred`) and `needed_at` absorbs date- and phase-deferral (`## YYYY-MM-DD`, `## Phase N.M`). `category` is a freeform short label — a project may settle on its own working set. No other new frontmatter keys without amending this policy.

### Body

Below the frontmatter, write the human-readable description: the context, the steps, what the human returns. For a non-trivial item, structure it with prose or a short list; the body is where load-bearing detail lives. For a closed item whose resolution is non-obvious, add a `## Disposition` section explaining what happened — the disposition is the audit trail.

## Slug discipline

Every action carries a **stable two-word slug** so it can be referenced unambiguously in conversation — "close out `warping-butterfly`," "did `elfish-tench` land?" The slug is the file's name and the item's handle for life.

Recipe (recommended, using the starter's standard Python tooling):

```bash
uv run --with coolname python -c "from coolname import generate_slug; print(generate_slug(2))"
```

Any deterministic two-word generator is acceptable as long as the slug is unique across both `user-actions/` and `user-actions-archived/`. Confirm uniqueness before writing — a slug is just a filename, so a basename collision across the two directories is the thing to avoid:

```bash
ls user-actions user-actions-archived 2>/dev/null | grep -E '^[a-z]+-[a-z]+\.md$' | sort | uniq -d
```

Slugs are not reused after closure. An archived file keeps its slug forever.

## Lifecycle

1. **Open.** Any agent that hits a human-only wall generates a unique slug and writes `user-actions/<slug>.md` with full frontmatter + a prose body, then surfaces the new action in the session's reply so the human sees it. No index to update — that is the point.
2. **In flight.** The file stays in `user-actions/` until the underlying action has been personally verified. Update `status` between `pending` and `deferred` (and `needed_at`) as the situation changes.
3. **Closed.** Set `status:` to the closure kind, add a `closed:` date, add a `## Disposition` section when the resolution is non-obvious, and **move the file** from `user-actions/` to `user-actions-archived/`:
   - `done` — action completed.
   - `closed` — explicitly closed without action (cost-benefit failed, scope changed, no longer relevant).
   - `superseded` — replaced by a different action or approach.

Archived files **stay on disk**. They are not deleted. A glob across `user-actions-archived/` should find every action ever closed.

### Who closes

- **Agent** may close only actions where it *personally* completed the underlying action — e.g., a smoke script the agent ran and observed pass, a deploy whose logs the agent read directly, a manifest file the agent listed on S3.
- **Human** closes any action requiring console / dashboard / GUI / pricing / billing verification — anything the agent cannot directly observe, even if a script "looks like" it did the work.

When in doubt, leave it open and surface the question. Falsely closing an action that turns out to need human eyes is a high-cost failure mode this policy guards against.

## Agent contract at session start

Every agentic session — `/kickoff` invocation, a hand-driven skill, an ad-hoc edit pass — globs `user-actions/*.md` and reads frontmatter before doing dependent work. If the session's task depends on an open action, flag the dependency and wait; don't proceed silently. If the session creates new human-only follow-ups, file them as files before the session ends.

## Relationship to other artifacts

- `LOG.md` records *what happened* in past phases (append-only). `user-actions/` records *what's pending on the human right now* (live).
- `plan/INDEX.md` records *which phase is next* (ledger). `user-actions/` records interrupts and asks that cut across phases.
- A new policy goes under `policies/`. A new brief goes under `briefs/`. A new human-only action item goes here as a file.

## Extension pattern (optional, for sub-domain projects)

Repos with bounded sub-domains — multi-book platforms, monorepos with per-package isolated cycles — may run a two-tier variant:

- An engine-level `user-actions/` at the repo root for cross-cutting / platform-level items.
- A per-domain `<DOMAIN_ROOT>/user-actions/` for items local to that domain.

Per-domain cycles confined to `DOMAIN_ROOT` (per a cycle-isolation policy) file their human-only requests in their own per-domain directory. The owner globs both layers as one queue. When a per-domain entry asks for a change outside its `DOMAIN_ROOT`, the owner makes the cross-boundary edit at the right level and either closes the per-domain entry or moves a corresponding action into the engine-level directory.

This is not built into the universal template. Adopt it only when the repo already has the sub-domain isolation framework that motivates it.

## Verification

A clean state satisfies:

```bash
# The directories exist
test -d user-actions && test -d user-actions-archived && echo ok
```

```bash
# Every file is named like a two-word slug
ls user-actions user-actions-archived | grep -E '\.md$' | grep -vE '^[a-z]+-[a-z]+\.md$' && echo "REVIEW: non-slug filenames" || echo "all filenames are slugs"
```

```bash
# No slug appears in both directories
ls user-actions user-actions-archived 2>/dev/null | grep -E '^[a-z]+-[a-z]+\.md$' | sort | uniq -d | grep . && echo "REVIEW: duplicate slugs" || echo "slugs unique"
```

```bash
# Frontmatter parses for every file
uv run --with pyyaml python -c "import yaml,glob; [yaml.safe_load(open(f).read().split('---')[1]) for f in glob.glob('user-actions*/*.md')]" && echo "frontmatter ok"
```

These greps are heuristics, not proofs. The real verification is human review: glob the open queue, confirm nothing was moved to the archive that the agent could not have personally observed.

## Per-phase waiver

The human may grant a phase-specific waiver of any rule in this policy. For example: "Go ahead and close `loose-swift` — I watched the log tail with you." Waivers are:

- **Explicit.** Stated in the current session, not inferred.
- **Scoped.** Apply to a named action or a named step.
- **Logged.** The phase's END block records the waiver.
- **One-shot.** The next action reverts to the policy's defaults unless the human grants another waiver.
