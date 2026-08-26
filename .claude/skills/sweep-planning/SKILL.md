---
name: sweep-planning
description: >-
  Longitudinal, user-gated sweep of the plan-review loop: harvest every
  genuine plan-review verdict from the machine's
  Claude Code and Codex traces over a window, categorize why plans were sent
  back, attribute each category to a correctable planner defect or a reviewer
  false positive, and propose the persona, script, and policy corrections as
  one plan the user ratifies. In a template repo the corrections land here and
  propagate via teach; in a derived project they file as scope-methodology
  lessons for learn. Invoke as /sweep-planning in Claude Code or
  $sweep-planning in Codex; optional arguments set the window in days and
  project=<name> filters. Enters plan mode first, analyzes inside it, and
  presents the analysis and the improvement plan together for approval. Also
  the canonical home of the review-loop sweep lifecycle that sweep-coding
  follows.
argument-hint: "[<days>] [project=<name> ...]"
last-reviewed: 2026-08-26
---

# Sweep-planning — Calibrate the review loop from its own record

This file is two things: the `sweep-planning` skill, and the **review-loop
sweep lifecycle** that its sibling `sweep-coding` follows by citation rather
than by copy (one procedure, two invocations — `policies/simplicity-and-consolidation.md`).
The lifecycle sections (§Plan mode first, §Stage 0, §Stage 1, §Stage 4,
§Stage 5, §The `LOG.md` entry) are parameterized by **kind**:

| kind | invocation | loop swept | finding ids | personas corrected | extra sensors | LOG heading |
|---|---|---|---|---|---|---|
| `plan` | `sweep-planning` | planner ↔ reviewer | `PLAN-F` | `phase-planner.md`, `plan-reviewer.md` | none | `SWEEP-PLANNING (plan)` |
| `code` | `sweep-coding` | coder ↔ critic | `CODE-F` | `phase-coder.md`, `code-critic.md` | coder Failure Analyses and Change Evidence (`--coder-evidence`) | `SWEEP-CODING (code)` |

Stages 2 and 3 carry the kind-specific taxonomy and attribution shapes: this
file holds the `plan` ones; `sweep-coding/SKILL.md` holds the `code` ones.

Every plan review the methodology runs is recorded verbatim in the harness's
session transcript — the reviewer's narrative, its `## Finding Evidence`
batch, its verdict, and the planner's revision after it. Across a month and
several projects that record answers a question no single phase can: **what
does the reviewer keep sending plans back for, and is each of those reasons a
defect in the planner or a habit of the reviewer?** `sweep` prunes the rule
surfaces; `sweep-planning` reads the loop those rules drive and corrects the
roles at the seam where the rounds are actually being spent.

The skill is plan-first and user-gated like `sweep`: it harvests, categorizes,
attributes, settles every judgment call in conversation, and proposes one
write set the user ratifies before anything is edited. Its first run is the
worked example: over 31 days and three derived projects, ~80% of rejections
were the planner citing code it never opened or writing acceptance blocks that
could not execute, and the costliest reviewer habit was re-aiming one finding
id at a new objection every round. Those became `bin/check-plan-concreteness`,
the planner's `Definitions Read` table, the reviewer's classification rules,
and the `evidence-substituted` ingest refusal — see
[`briefs/harness-self-improvement.md`](../../../briefs/harness-self-improvement.md).

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- A bare integer is the window in days (default: from the last sweep, see
  Stage 0; 31 with no prior sweep); it becomes `--since-days`. A wider window
  costs only harvest time, a narrower one loses the longitudinal view —
  below ~14 days the weekly trend is noise.
- The kind is the invocation: `sweep-planning` sweeps `plan`, `sweep-coding`
  sweeps `code`.
- `project=<name>` (repeatable) restricts the harvest to sessions whose
  working directory basename matches; each becomes a `--project` flag. In
  derived-project mode the current repository is the default filter.

## Where the corrections land — template mode vs. derived-project mode

Decide the mode before Stage 1 and say which one you are in:

- **Template mode** — this repository *is* the template (it carries the
  `stamp` skill). Sweep every project on the machine that the template's
  roles run in, because the roles' definitions are copies of this repo's and
  a defect seen in three projects is a defect here. Corrections land in
  `.claude/agents/*.md`, `.claude/skills/kickoff/SKILL.md`, `bin/`,
  `policies/`, and their tests, and propagate outward through `teach`.
- **Derived-project mode** — this repository was stamped from a template.
  Sweep this project's own traces (`--project <basename>`), and file each
  correction as a `lessons/<slug>.md` entry with `scope: methodology` plus,
  where the fix is project-local (a convention the planner keeps missing, a
  surface the reviewer keeps flagging), `scope: local`. Methodology lessons
  are the standing export the template's `learn` harvests; do not edit the
  universal personas or skills here — that is the operator-routed methodology
  change the architectural invariants reserve, and a local edit is overwritten
  by the next `teach`.

The mechanics are identical in both modes; only the write set differs.

## Plan mode first

The sweep begins by entering plan mode, before Stage 0 — call
`EnterPlanMode` where the harness exposes it (Claude Code does; Codex does
not yet, see the `sweep` skill's plan-mode notes). Stages 0–3 then run
read-only inside plan mode: reading the log, harvesting, categorizing,
attributing. Stage 4 writes **the analysis and the improvement plan as one
document** into the plan-mode body and calls `ExitPlanMode`; the operator's
accept / revise / reject is the approval. Stage 5 applies only after
approval, outside plan mode. Where the harness has no plan mode, the
read-only discipline through Stage 3 carries the contract and approval is
free-text. While the operator is AFK, park the Stage 4 document as an
artifact and do not raise an interactive gate.

The head of that document is written for the operator in the `plain`
register ([`.claude/skills/plain/SKILL.md`](../plain/SKILL.md)): a
**Summary** and a **Recommendations** block that read without the repo, the
dataset, or the transcript open — what the loop keeps rejecting for, which
side owns it, what changes, what it costs the operator. No finding ids, file
paths, or finding-schema vocabulary above that fold. Everything below it —
coverage, category table, attributions with evidence, write set — is as
technical as the evidence requires. The same rule binds the first paragraph
of the `LOG.md` entry.

## Stage 0 — Read the last sweep

Before harvesting, find the most recent `## <ts> — <LOG heading for this
kind>` entry in `LOG.md` (in template mode, also in each swept project's `LOG.md`
where one exists — a derived project's own sweep is evidence too). It fixes
three things:

- **The default window.** With no `<days>` argument, the window runs from the
  last entry's timestamp to now, so consecutive sweeps tile the record
  without a gap or an overlap; with no prior entry, 31 days. An explicit
  `<days>` always wins. Say which rule set the window and what it is.
- **The baseline.** The entry's category table, attributions, and
  approval-rate-by-week are the comparison for this run — Stage 3 reports
  every category as *new*, *recurring* (with the delta in count and blocking
  share), or *gone*, and checks whether each correction the last entry
  applied actually moved its category. A correction that did not move its
  category is the first finding of this run.
- **Open items.** Corrections the last entry declined or left as `DECIDE`
  are re-asked before new ones are proposed.

If the last sweep is younger than fourteen days and no `<days>` argument was
given, say so and ask whether to widen — a fortnight rarely holds enough
verdicts to distinguish a trend from one phase's weather.

## Stage 1 — Harvest (mechanistic)

Run the deterministic harvester; do not hand-grep the traces.

```bash
./bin/review-verdicts --since-days <days> --kind <kind> [--coder-evidence] [--project <name> ...] --json <scratch>/verdicts.json
```

Use the session scratch directory for `<scratch>`, never a bare filename in
the repository — an untracked capture moves the candidate id. Read the summary
it prints and the dataset it wrote:

- **Coverage.** Verdict counts by project, harness, kind, and week; the count
  of genuine verdicts the harvester could not classify (no finding ids — legacy
  narrative verdicts). Open a sample of the unclassified ones; if they are
  plan reviews from before the evidence plane, they are part of the corpus and
  you categorize them by hand from their `### Required Changes`.
- **The finding records** with `severity`, `classification`, `state`,
  `authority`, `evidence`, and `required_outcome`, deduplicated by
  `(project, id, evidence)`.
- **Re-aimed ids** — finding ids that carried more than one distinct evidence
  text while they stayed actionable, within one session transcript (ids
  restart per phase, so a cross-session match is a different phase, not a
  re-aim). Each is a round the ledger cannot explain.
- **Excluded sessions.** The harvester drops the running session's own
  transcript — a sweep prints verdict text while it works and would
  otherwise measure itself. Check the `Excluded sessions:` line names this
  session.
- **Coder evidence** (`--coder-evidence`, kind `code`): the coder's Failure
  Analysis statements, the loop's own root-cause sensor.

Name the blind spots before going further, per
[`policies/verification-discipline.md`](../../../policies/verification-discipline.md):
verdicts emitted before the finding schema existed carry no ids and are
under-counted by kind; a review run in a venue whose transcript is not on this
machine is invisible; and the harvester's genuine-filter is a proxy — a real
verdict quoted with line numbers is dropped, a template echo that happens to
carry none of the markers is kept. State the counts with the command that
produced them.

## Stage 2 — Categorize (intelligence)

*Procedure for every kind; the taxonomy table below is the `plan` one.
`sweep-coding` substitutes its own table and follows the rest verbatim.*

Read every distinct root finding — collapse the rounds: one root finding per
`(project, id)`, with its evidence history — and every legacy `Required
Changes` bullet. Sort each into a reason category. Start from this taxonomy,
which the first run derived, and extend it only when an item fits none:

| Category | What it looks like | Typical mechanism |
|---|---|---|
| **Cites what it never read** | wrong signature, nonexistent field/enum/column, a payload the shipped validator refuses, a regex narrower than the live data | planner named by convention instead of opening the file |
| **Underspecified or self-contradictory design** | totals with no reconciliation rule, a case rule stated two ways, a state unreachable by construction, a step bound to no command | planner stopped at the description |
| **Acceptance that cannot run** | `<placeholder>` in a command, a flag the script does not define, a candidate id pinned before implementation, a test proxy that cannot fail, a demo that mutates a fixture | planner wrote acceptance as prose |
| **Scope, authority, inventory** | reassigning a parent deliverable as settled, asserting an approval nobody recorded, an inventory (`CLAUDE.md`, a manifest, a floor) not updated | planner did not sweep the inventories the change makes required |
| **Owner decision** | "obtain the operator-level contract decision", an authorization for a write or probe | neither role can answer it |
| **Verification-discipline nit** | a relayed number, an unattributed negative control, a missing producing command | low severity; rarely drives a round |

For each item, quote the finding's `evidence` from the dataset — never from
your own earlier summary — and record the category, severity, whether it
blocked, and how many rounds it survived.

Then read the categories as a bare column of "why"s with the items stripped,
per the Epistemics rule on proxies: real categories read as distinct
failure mechanisms; a category whose entries all say the same thing as the
one above is padding, and a category that keeps surfacing the planner's *best*
work (a deliberate carve-out, a documented limitation, a refusal to weaken a
gate) is a reviewer proxy that has inverted — flag it as such in Stage 3, do
not "fix" the planner for it.

## Stage 3 — Attribute (intelligence)

*Procedure for every kind; the shapes listed are the `plan` ones.
`sweep-coding` substitutes its own shapes and follows the rest verbatim.*

Every category gets one of three attributions, with the evidence for it:

1. **Correctable planner defect.** The finding was refutable from the tree or
   the authorities before the plan was submitted. Test: could a script or a
   one-line rule in `phase-planner.md` have refused the plan? If a script
   could, the fix is a script (`policies/mechanistic-vs-intelligence.md`) —
   check whether `bin/check-plan-concreteness` already covers the shape and
   whether its refusal rows would have fired on the actual plan artifact
   (run it against a surviving artifact when one exists under the run
   directories).
2. **Reviewer false positive or bad habit.** Shapes to look for, each seen on
   the first run:
   - a refuted premise — a count or a name the reviewer asserted that the
     tree did not hold (the finding's `evidence` names no producing command);
   - a stable id carrying a new objection each round while classified
     `initial` (`re-aimed ids` in the harvest) — the first pass was not
     complete, and `kickoff-evidence` now refuses the substitution;
   - an owner decision sent back to the planner as `REVISE` instead of
     `blocked-owner` — check whether the same finding text recurs across
     rounds unchanged;
   - an over-engineering ask: a demand for a mechanism, test, or abstraction
     the phase did not require and whose second present-tense use the
     reviewer cannot name (`policies/simplicity-and-consolidation.md`) —
     count these separately from findings where the reviewer *struck*
     redundant state, which is the opposite habit;
   - severity inflation: `blocking` used for underspecification rather than
     for a policy or invariant violation.
3. **Structural.** Neither role is wrong; the loop lacks a mechanism (a venue
   without an escalation surface, an ingest rule that cannot express the
   state). The fix is in `kickoff`, `bin/kickoff-evidence`, or a policy.

Record the longitudinal view with the numbers: approval rate by week, rounds
per phase where `LOG.md` END blocks state them, and how the category mix moved
across the window. A rising approval rate with unchanged rounds per phase
means the reviewer got easier, not that the planner got better; say which.

Cross-check the projects' own `lessons/` and `lessons-archived/` ledgers:
a category one project has already filed as a lesson at one or two
occurrences, seen again elsewhere, is a graduation candidate — cite the slug.

## Stage 4 — Plan and approve (gate)

Compose one document — the analysis and the improvement plan together — and
surface it through the plan-mode approval described in §Plan mode first (or
free-text approval where there is none). Every proposed write names the
surface, the exact change, and the finding ids that motivate it.

- **Summary** (`plain` register) — the three or four sentences an operator
  needs: what the loop keeps rejecting for, which side owns it, what changes.
- **Recommendations** (`plain` register) — what to change, in the order
  that cuts the most rounds, each with its cost to the operator; no ids,
  paths, or schema words.
- **Coverage and blind spots** — the harvest counts with their commands.
- **Categories** — the table from Stage 2 with counts, share, blocking share,
  and rounds survived.
- **Attributions** — per category: planner / reviewer / structural, with the
  evidence.
- **Proposed write set** — grouped by surface: `.claude/agents/*.md`,
  `.claude/skills/kickoff/SKILL.md`, `bin/` scripts and their tests,
  `policies/`, transfer documents (`stamp`, `teach`,
  `briefs/agentic-bootstrap.md`, `bin/README.md`). In derived-project mode,
  the `lessons/` entries instead, each with its scope.
- **Declined** — corrections you considered and rejected, with the reason
  (usually: the count does not justify a rule, or the proxy inverts).
- **Settled decisions** — every judgment call the user resolved in
  conversation, verbatim.
- **Proposed LOG.md entry** — the block below under this kind's LOG heading,
  filled in. It is an authorized `LOG.md` entry kind (the entry-kind table in
  [`policies/log-discipline.md`](../../../policies/log-discipline.md)); write
  it, do not re-decide whether a sweep earns one.

Settle judgment calls one at a time before composing the plan, as `sweep`
does: whether a category is a planner defect or a reviewer habit is often
exactly the call the operator wants to make.

## Stage 5 — Apply

Only after approval. Edit the canonical surfaces, never a mirror
(`policies/cross-harness-parity.md`); add or extend tests for every script
change; register a new script in `bin/README.md`, `bin/check`'s lint and
format lists, and the transfer documents; run `./bin/check all` in its own
block and read the refusal; run `bin/check-anonymization.sh` where the repo
carries it — the categories' examples must not name another project's
identifiers. Deliver per Hard rule 1 and `policies/commit-staging.md`: re-check
the live tree, stage explicit paths, inspect the staged diff, commit, verify the
resulting file set, and push; park on anything unexpected or on unresolved
shared-file ownership.

In derived-project mode, Stage 5 writes `lessons/` entries via `bin/new-name`
slugs and `./bin/lessons validate`, and nothing else — plus the `LOG.md`
entry, in both modes.

### The `LOG.md` entry

Append it last, after the write set has landed and the gate is green, so it
records what was actually done. It is what the next run's Stage 0 reads, so
keep the category table and the numbers machine-findable:

```markdown
## <YYYY-MM-DD HH:MM TZ> — SWEEP-PLANNING (plan)   ← or SWEEP-CODING (code)

<One plain-register paragraph: what the loop kept rejecting for, who owned it,
what was changed.>

Window: <from> → <to> (<N> days; set by <argument | last entry | default>).
Harvest: `./bin/review-verdicts --since-days <N> --kind <kind> [...]` —
<G> genuine verdicts (<R> REVISE / <A> APPROVED) across <projects>; <U>
unclassified legacy verdicts, <of which hand-sorted>; <F> finding records,
<D> distinct root findings; <M> re-aimed ids. Blind spots: <named>.

Approval rate by week: <w1> <r1>%, <w2> <r2>%, … Rounds per phase where
stated: <list or "not stated">.

| Category | Root findings | Share | Blocking | Rounds survived | Attribution | vs. last sweep |
|---|---|---|---|---|---|---|
| … | … | … | … | … | planner / reviewer / structural | new / +n / −n / gone |

Corrections applied: <surface — change — motivating ids>, one line each; in
derived-project mode, the `lessons/<slug>.md` entries filed with their scope.
Declined: <correction — reason>. Open (DECIDE): <items the operator deferred>.
Delivered as <commit> (or: parked — <reason>).
```

## Rules

- Harvest with the script; categorize and attribute with judgment. Do not
  hand-grep the traces and do not let a script assign categories.
- Quote evidence from the dataset, never from your own earlier summary.
- One observation cannot identify a mechanism: a category with one member is
  reported, not corrected.
- Test every proxy for inversion before correcting the side it points at.
- Never write into `~/.claude` or `~/.codex`; the traces are read-only input.
- Anonymize before writing anything committed: `Donor A` / `the donor` for
  other projects' names, no commit SHAs, no proprietary identifiers in
  examples.
- The user ratifies; the skill proposes. Nothing is edited before Stage 5.
