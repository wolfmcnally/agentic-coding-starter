# Policy: Lessons

The [`lessons/`](../lessons/) directory at the repo root is the **ledger of candidate process lessons** — durable learnings harvested from phase work, reviews, dispositions, and transfers that have not yet been ratified into a rule. Every agentic project ships with this directory from the first session.

A **lesson** is one such learning: a specific, generalizable observation about how work in this repo (or the methodology itself) should be done differently next time. The ledger is the capture stage of the repo's improvement flywheel. It exists so that learnings accumulate as discrete, addressable, provenance-carrying entries instead of evaporating at session end or being smeared into instruction files by ad-hoc rewrites. Rewriting rule documents wholesale from memory degrades them (brevity bias, context collapse); itemized capture with human-ratified graduation is the discipline that avoids both.

This policy prescribes the directory's layout, the per-file format, scope classification, the graduation rule, and who may write what. The policy *is* the format spec — there is no separate template.

## One file per lesson

Each lesson is its own markdown file:

- **Open lessons** live in `lessons/<slug>.md` with `status: candidate`.
- **Closed lessons** live in `lessons-archived/<slug>.md` with `status: codified | rejected | superseded`.

The **filename is the slug** (a two-word code-name): `sandbox-phantom.md`. There is intentionally **no index file** — same contention rationale as [`user-actions.md`](user-actions.md): one-file-per-lesson lets concurrent agents append to the ledger without editing a shared list. Each file is fully self-contained.

## What `lessons/` is

- The repo's structured memory of "what we keep re-learning," parallel to `LOG.md` (history) and `user-actions/` (human-only follow-ups).
- The input queue for rule-making: a lesson that recurs graduates — with the human's explicit approval — into a policy, brief, skill, agent definition, `bin/` script, test, or `CLAUDE.md` invariant.
- In a derived project, the `scope: methodology` subset is the standing export surface the starter harvests via the `learn` skill.

## What `lessons/` is not

- Not a bug tracker or work backlog. Work an agent can do goes in `plan/`; human-only actions go in `user-actions/`.
- Not a rule surface. A candidate lesson binds nothing; only graduation makes it binding, and only the human graduates.
- Not agent-side memory. Per [`CLAUDE.md`](../CLAUDE.md)'s "Rules, not memory" invariant, the ledger is a committed repo surface visible to every operator and harness — never a local memory store.

## Format

### Frontmatter (all metadata)

```yaml
---
slug: sandbox-phantom          # matches the filename
title: Distrust in-sandbox test failures without a host-side rerun
status: candidate              # candidate  (open)  ·  codified | rejected | superseded  (archived)
scope: methodology             # local | methodology
proposed_surface: policy       # policy | brief | skill | agent | bin | test | invariant
filed: 2026-08-10              # ISO date first filed
source: kickoff                # kickoff | sweep | disposition | learn | teach | user
occurrences:                   # every observation of this lesson, in order
  - date: 2026-08-10
    ref: "Phase 10.3 END"      # a phase id, LOG entry, verdict, or disposition slug
---
```

Archived files additionally carry:

```yaml
status: codified               # codified | rejected | superseded
closed: 2026-08-21             # ISO date closed
graduated_to: policies/role-timeouts.md   # required when codified — the surface the rule landed on
```

- `scope: local` — the lesson binds only this project (a convention, a quirk of this codebase or its tooling).
- `scope: methodology` — the lesson generalizes to the methodology itself and is an upstream candidate for the starter template. In the starter itself, most lessons are `methodology`.
- `proposed_surface` names where the rule would land if ratified; the graduating human may override it.

No other new frontmatter keys without amending this policy.

### Body

Below the frontmatter, one to a few paragraphs stating the lesson: what happened, why, and what should be done differently. Concrete beats abstract — "run X before Y because Z bit us in Phase N," not "be careful with X." An optional `## Evidence` section may cite transcripts, logs, or diffs.

## Slug discipline

Same recipe and rules as [`user-actions.md`](user-actions.md): a stable two-word slug, unique across both `lessons/` and `lessons-archived/`, never reused after closure.

```bash
uv run --with coolname python -c "from coolname import generate_slug; print(generate_slug(2))"
```

## Lifecycle

1. **File or recur.** When a harvest (see "Who writes" below) surfaces a candidate lesson, first check both directories for an existing entry stating the same lesson. If one exists, **append an occurrence** to it rather than filing a duplicate; if it is archived as `rejected`, appending a new occurrence with fresh evidence is how the case for reconsideration is made. Otherwise file a new `lessons/<slug>.md` with `status: candidate` and one occurrence.
2. **Stabilize.** A lesson graduates on the strength of recurrence, not eloquence. The working threshold is **three occurrences** — codifying on first sight tends to lock in rules that haven't seen their variations. The human may graduate a lesson earlier at their discretion; agents may not.
3. **Graduate (human-only).** Graduation is a user-ratified edit to the target surface plus archival of the lesson: set `status: codified`, add `closed:` and `graduated_to:`, and move the file to `lessons-archived/`. Agents *propose* graduation — as `DECIDE`-style items in a phase's END block or a `sweep` plan — and never apply it. A rejected proposal is archived `status: rejected`; a lesson absorbed by another is `status: superseded`.

Archived files **stay on disk** — they are the audit trail linking every rule back to the incidents that earned it, and the record of what was considered and declined.

### Who writes

- **Any agent** may file a candidate lesson or append an occurrence: `kickoff`'s harvest step at phase close, `sweep` during a maintenance pass, a `user-actions` disposition, `learn`/`teach` during a transfer, or the user directly.
- **`learn` keeps two inputs distinct.** Donor-ledger lessons are harvested as
  direct rule proposals or destination-ledger candidates. New methodology
  defects exposed while adapting the approved bundle are filed separately in
  the destination ledger with `source: learn` and `scope: methodology`; the
  donor remains read-only. The aggregate LOG entry reports both counts.
- **Only the human** graduates, and only the human edits `policies/`, `briefs/`, `CLAUDE.md`, skills, or agent definitions *because of* a lesson. Filing and occurrence-appending are the only ledger writes an agent performs autonomously.

## Anonymization on the upstream path

A `scope: methodology` lesson in a derived repo is destined for the starter template, which is public. When such a lesson is harvested into the starter (via `learn` or by hand), it obeys [`anonymize-log-references.md`](anonymize-log-references.md) *before being written*: no external project names, commit SHAs, or proprietary identifiers. The starter's `bin/check-anonymization.sh` scans the whole tree, so `lessons/` and `lessons-archived/` are inside its net. Write the lesson so the learning survives that translation — state the mechanism and the failure mode, not just the local names, so a reader with no context from the originating project can still act on it.

## Relationship to other artifacts

- A lesson that must bind **now** isn't a lesson — it's a rule; take it straight to the human as a proposed policy/brief edit.
- A human-only follow-up goes in `user-actions/`; if its disposition reveals a recurring learning, the disposition files a lesson here (see [`user-actions.md`](user-actions.md)).
- Ripple (per [`phase-ripple.md`](phase-ripple.md)) propagates *content* into downstream plan files; lessons capture *process* learnings. The same phase close runs both, and neither substitutes for the other.

## Verification

```bash
./bin/lessons validate
```

```bash
./bin/lessons list --status candidate
```

```bash
./bin/lessons candidates
```

`validate` enforces this policy's schema mechanically (closed key set, enums, slug uniqueness across both directories, well-formed occurrences); `candidates` lists graduation-ready lessons (≥3 occurrences, still `candidate`). The judgment calls — is this lesson true, has it stabilized, which surface — remain human, per [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md).

## Per-phase waiver

The human may grant a phase-specific waiver of any rule in this policy (for example, authorizing immediate codification of a first-occurrence lesson). Waivers are explicit, scoped, logged in the phase's END block, and one-shot — same contract as [`user-actions.md`](user-actions.md).
