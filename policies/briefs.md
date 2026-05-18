# Briefs — Policy

This file defines what `briefs/` is in this project, who writes there, and how briefs relate to `policies/`.

## What briefs are

`briefs/` is a **read-write working library** of internal documents — research, methodology, audits, decision records, source-material snapshots, and pinned positions — produced and consulted as the project evolves.

A brief captures *durable* analysis or reasoning that future work will refer back to. A brief is the answer to questions like:
- "What's the canonical way to do X, and where did we get that?"
- "Why did we decide Y? What did we evaluate?"
- "What was the state of the world when we last checked Z?"
- "Did we already research this?"

## What briefs are not

- **Code.** Anything executable lives in `bin/` or the eventual application tree.
- **A queue.** Work to be done lives in commit messages, a TODO list, or an issue tracker — not in `briefs/`.
- **A policy.** Operational rules — "always do X, never Y, here's the schema" — live in `policies/`. A brief *informs* policy; a brief is not policy.
- **A log.** Briefs capture durable positions, not running history.

## When to write one

Write a brief when:
- Research turns up a position or methodology the team will cite later (a BCP list, a measured number, a worked example).
- A non-trivial decision is made whose reasoning matters more than its outcome.
- An audit, evaluation, or discrepancy review produces findings that will inform future work.
- A snapshot of an external system (AWS infra state, a third-party service's behavior) is worth pinning at a specific date.

Don't write a brief for ephemeral state, single-session decisions, or anything that fits inside a commit message.

## Conventions

- **Filename:** kebab-case, descriptive (`s3-access-log-bcps.md`, not `notes-04.md`). No dates in filenames.
- **Frontmatter (YAML):** every brief opens with:
  - `title:` — short scannable title.
  - `date:` — ISO date authored or last revised.
  - `status:` — one of `draft` | `methodology` | `implemented` | `historical`.
  - `scope:` — one sentence describing the brief's purpose.
- **Body:** purpose paragraph, then numbered or named sections, then a Sources section if applicable.
- **Cross-references:** when one brief depends on another's numbers or methodology, link explicitly so the dependency is auditable.

## Status lifecycle

- `draft` — still being shaped; numbers and conclusions tentative.
- `methodology` — defines an approach the project defers to.
- `implemented` — the position has been realized in code or operational practice.
- `historical` — superseded by a later brief or by changed reality; kept for the audit trail.

When reality changes, prefer updating the brief to retiring it; mark superseded briefs `historical` rather than deleting them.

## Authority

Briefs are subordinate to active `policies/` for next-action questions. They are *authoritative* for cross-session reasoning, methodology, and snapshot-of-the-world claims.

When a brief and a more current source disagree, prefer the live source — but update or annotate the brief to reflect the new reality. Briefs decay if not maintained.
