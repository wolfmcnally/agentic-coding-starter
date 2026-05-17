# Policy: User Blockers

[`user-blockers.md`](../user-blockers.md) at the repo root is the **live queue** of action items only the human can perform. Deploys, console / dashboard / GUI checks, manual reconciliations, third-party logins, pricing decisions, signups, anything outside an agent's reach. Every agentic project ships with this file from the first session.

This policy prescribes the file's location, format, lifecycle, and the agent-vs-human checkoff discipline. The policy *is* the format spec — there is no separate template.

## What `user-blockers.md` is

- The interrupt-driven queue of human-only follow-ups, parallel to `LOG.md` (history) and `plan/INDEX.md` (phase ledger).
- A live, mutable file: items get added as agents hit human-only walls; items get checked off as resolutions land; closed items stay in place strikethrough'd as a permanent audit trail of what was asked, when, and how it resolved.
- The single source of truth a session can scan to know "what is the human blocking right now."

## What `user-blockers.md` is not

- Not a status indicator. Phase status lives in `plan/INDEX.md` per [`phase-status.md`](phase-status.md).
- Not a history log. Append-only narrative lives in `LOG.md` per [`log-discipline.md`](log-discipline.md).
- Not a plan. Plans live in `plan/` per [`briefs-and-policies.md`](briefs-and-policies.md).
- Not a backlog of agent work. Anything an agent can do itself goes into the plan or gets done; only items requiring the human's hands belong here.

## Format

### Canonical light (default)

Each item is a checkbox + stable slug + one-line description:

```markdown
- [ ] `warping-butterfly` — Deploy the new CDK stack: `bin/deploy-infra rollup`.
- [x] `elfish-tench` — Immediately after deploy: `bin/rollup-smoke --allow-empty`.
```

Items are grouped into sections. Conventional sections:

- `## Pending` — items that can be acted on now.
- `## Deferred / not currently blocking` — items tracked here so they don't fall off the radar, but no calendar urgency yet.
- `## YYYY-MM-DD` — items date-deferred until a specific calendar date (e.g., post-deploy verification scheduled for the day after a tick). Always use absolute dates; convert relative dates ("Thursday") at write time.
- `## Phase N.M — <short label>` — items scoped to a specific phase, when several blockers share a context.

Within each section, sort top-down by dependency: a checked-off item unblocks the items below it within the same section.

### Structured expansion (when the item warrants it)

When an item is non-trivial — multi-step, dependent on owner judgment, or load-bearing for downstream work — expand the description inline below the checkbox using these fields:

```markdown
- [ ] `imperial-labradoodle` — Pick email platform.

  **Priority:** High — every day without email capture loses the day's traffic permanently.
  **Blocked:** Email capture system, which itself blocks the welcome sequence, drip campaigns, and newsletter sponsorships.

  **Steps:**
  1. Sign up for chosen platform.
  2. Return account API key.

  **Deliverables back:** Platform name + API key.

  **Unblocks:** Email capture, downstream automation, sponsorship surface.
```

Use the structured form whenever a short description would lose load-bearing detail. The structured fields are the same set every time, in the same order, so a reader sweeping the file knows where to look. No new field names without amending this policy.

### Source tag (optional)

When multiple loops or skills write to the same file and it helps the reader to know which one filed an item, append a single bracketed source tag after the slug:

```markdown
- [ ] `garrulous-seal` [critic] — Activate cost-allocation tag keys in AWS billing.
```

Conventional tags: `[plan]`, `[critic]`, `[deploy]`, `[skill-name]`. Single-loop projects can omit the tag entirely; over-tagging is worse than no tag.

## Slug discipline

Every item carries a **stable two-word slug** so it can be referenced unambiguously in conversation — "close out `warping-butterfly`," "did `elfish-tench` pass?" The slug is the item's handle for life.

Recipe (recommended, using the starter's standard Python tooling):

```bash
uv run --with coolname python -c "from coolname import generate_slug; print(generate_slug(2))"
```

Any deterministic two-word generator is acceptable as long as the resulting slug is unique across the file's live and closed items. Grep both sets to confirm uniqueness before writing:

```bash
grep -E '`[a-z]+-[a-z]+`' user-blockers.md
```

Slugs are not reused after closure. Closed-and-strikethrough items still hold their slug.

## Lifecycle

1. **Open.** Any agent that hits a human-only wall files a new item: pick a section (or create one), generate a unique slug, write the checkbox + slug + description, and surface the new item in the session's reply so the human sees it.
2. **In flight.** Items stay unchecked until the underlying action has been personally verified.
3. **Closed.** Wrap the title in `~~strikethrough~~` and append a closure marker:
   - `✅ DONE` — action completed.
   - `✅ CLOSED` — explicitly closed without action (cost-benefit failed, scope changed, no longer relevant).
   - `✅ SUPERSEDED` — replaced by a different item or a different approach.

   When the resolution is non-obvious (closed without action, partial completion, deferred indefinitely), add a `**Disposition:**` line explaining what happened. The disposition is the audit trail.

Closed items **stay in the file**. They are not archived, deleted, or moved. A grep across `user-blockers.md` should find every item that was ever filed.

### Who checks off

- **Agent** may check off only items where it *personally* completed the underlying action — e.g., a smoke script the agent ran and observed pass, a deploy whose CloudWatch logs the agent read directly, a manifest file the agent listed on S3.
- **Human** checks off any item requiring console / dashboard / GUI / pricing / billing verification — anything the agent cannot directly observe, even if a script "looks like" it did the work.

When in doubt, leave it unchecked and surface the question. Falsely checking a box that turns out to need human eyes is a high-cost failure mode this policy guards against.

## Agent contract at session start

Every agentic session — `/kickoff` invocation, a hand-driven skill, an ad-hoc edit pass — reads `user-blockers.md` before doing dependent work. If the session's task depends on an unchecked blocker, flag the dependency and wait; don't proceed silently. If the session creates new human-only follow-ups, file them as items before the session ends.

## Relationship to other artifacts

- `LOG.md` records *what happened* in past phases (append-only). `user-blockers.md` records *what's pending on the human right now* (live).
- `plan/INDEX.md` records *which phase is next* (ledger). `user-blockers.md` records interrupts and asks that cut across phases.
- A new policy goes under `policies/`. A new brief goes under `briefs/`. A new human-only action item goes here.

## Extension pattern (optional, for sub-domain projects)

Repos with bounded sub-domains — multi-book platforms, monorepos with per-package isolated cycles — may run a two-tier variant:

- Engine-level `policies/user-blockers.md` at the repo root for cross-cutting / platform-level items.
- Per-domain `<DOMAIN_ROOT>/policies/user-blockers.md` for items local to that domain.

Per-domain cycles confined to `DOMAIN_ROOT` (per a cycle-isolation policy) file their human-only requests in their own per-domain file. The owner reads both layers as one queue. When a per-domain entry asks for a change outside its `DOMAIN_ROOT`, the owner makes the cross-boundary edit at the right level and either closes the per-domain entry or moves a corresponding entry into the engine-level file.

This is not built into the universal template. Adopt it only when the repo already has the sub-domain isolation framework that motivates it.

## Verification

A clean state satisfies:

```bash
# File exists and is committed
test -f user-blockers.md && echo ok
```

```bash
# Every item has a slug in backticks
grep -E '^- \[[ x]\] ' user-blockers.md | grep -vE '`[a-z]+-[a-z]+`' && echo "REVIEW: items missing slug" || echo "all items slugged"
```

```bash
# No slug appears twice
grep -oE '`[a-z]+-[a-z]+`' user-blockers.md | sort | uniq -d | grep . && echo "REVIEW: duplicate slugs" || echo "slugs unique"
```

These greps are heuristics, not proofs. The real verification is human review: open the file, scan the open queue, confirm nothing was checked off that the agent could not have personally observed.

## Per-phase waiver

The human may grant a phase-specific waiver of any rule in this policy. For example: "Go ahead and check `loose-swift` off — I watched the log tail with you." Waivers are:

- **Explicit.** Stated in the current session, not inferred.
- **Scoped.** Apply to a named item or a named action.
- **Logged.** The phase's END block records the waiver.
- **One-shot.** The next item reverts to the policy's defaults unless the human grants another waiver.
