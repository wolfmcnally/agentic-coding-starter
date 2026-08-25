---
slug: perfect-sloth
title: Ratify the briefs-only sweep plan (3 AUTO fixes, 3 DECIDE items)
status: done
category: decision
urgency: medium
blocks:
  - Applying any briefs edit from this sweep
filed: 2026-08-25
needed_at: now
closed: 2026-08-25
source: sweep
refs:
  - briefs/BRIEF.md
  - briefs/eacp-pattern-map.md
  - briefs/deterministic-orchestration.md
  - briefs/methodology.md
  - briefs/harness-self-improvement.md
  - policies/briefs.md
---

A `sweep briefs only` pass ran to Stage 2 (audit + classify) and parked at the
approval gate because the AFK marker was up — [`policies/human-in-the-loop.md`](../policies/human-in-the-loop.md)
reserves retirement and status changes for the operator, and an unattended
interactive gate is forbidden while the marker stands. Nothing was written to
`briefs/`. Approve, exclude, or reject the items below and the apply stage can
run in one pass.

## Mechanical checks — all green

`./bin/check-catalogs`, `./bin/lessons validate`, and `./bin/treatise validate`
all pass. `./bin/lessons candidates` lists one graduation-ready entry
(`macho-collie`, 3 occurrences, `scope: methodology`) — out of scope for a
briefs-only pass, noted so it is not lost.

## AUTO — mechanical, one correct shape

**A1. Dead anchor in `briefs/BRIEF.md:20`.** The Catalog section points at
`../CLAUDE.md#briefs-catalog`. `CLAUDE.md` has no "Briefs catalog" heading; the
index is split across `## Project briefs` and `## Methodology briefs`. Proposed
fix: point at both anchors. (`bin/check-catalogs` validates tracked internal
links but not intra-file anchors, which is why this survived — see the optional
lesson below.)

**A2. Count mismatch in `briefs/eacp-pattern-map.md:24`.** The Method bullet
says "the five highest-stakes entries" and then lists six slugs
(`orchestrator-workers`, `generator-evaluator`, `prompt-chaining`,
`externalized-state`, `compound-engineering`, `harness-engineering`). §13
Sources lists the same six. Proposed fix: "five" → "six".

**A3. Five `date:` fields lag their last substantive edit.** [`policies/briefs.md`](../policies/briefs.md)
defines `date:` as "ISO date authored or last revised". Proposed fix — set each
to the date of its last content-changing commit:

| Brief | `date:` | last edit |
|---|---|---|
| `briefs/BRIEF.md` | 2026-08-23 | 2026-08-24 |
| `briefs/methodology.md` | 2026-08-23 | 2026-08-24 |
| `briefs/eacp-pattern-map.md` | 2026-08-23 | 2026-08-24 |
| `briefs/harness-self-improvement.md` | 2026-08-10 | 2026-08-11 |
| `briefs/deterministic-orchestration.md` | 2026-06-09 | 2026-08-17 |

The pattern is systemic rather than five separate slips: the field is not being
bumped when a brief is edited as part of a larger change.

## DECIDE — judgment required

**D1. `briefs/BRIEF.md` carries `status: methodology` but holds project-specific
content.** [`policies/briefs.md`](../policies/briefs.md) states the marker also
signals *portable Methodology Contract content*, and warns explicitly that a
cross-repo `learn` pass trusting it as a selector would mis-transfer domain
content into the template. Three pieces of evidence say this brief is not
portable: `CLAUDE.md` lists it under **Project briefs**, not Methodology briefs;
`.claude/skills/stamp/SKILL.md:262` writes a *fresh* `BRIEF.md` at
`status: draft` for a derived project rather than copying this one; and its body
is this repository's own product brief (two operating modes, acceptance for
*this template*, anti-goals).

*Recommendation: change to `status: implemented`.*

Adjacent question, worth one ruling rather than five: the four other briefs
`CLAUDE.md` groups as Methodology briefs carry `implemented` or `draft`
(`incremental-orchestration`, `harness-self-improvement`, `deterministic-orchestration`).
That is legal under the status lifecycle, but it means the `methodology` marker
cannot actually serve as the portability selector the policy describes. Either
the marker is the selector (and those briefs should carry it), or the
Project/Methodology split in `CLAUDE.md` is the selector (and the policy's
paragraph should say so). Worth deciding once.

**D2. `briefs/deterministic-orchestration.md` §4 is a stale harness snapshot,
and criterion 4 of its own decision list demands re-validation.** Re-checked
2026-08-25 against current vendor docs:

- **The trigger condition has not landed.** Codex subagent orchestration is
  model-driven — the docs state "ChatGPT or Codex handles orchestration across
  agents, including spawning new subagents, routing follow-up instructions,
  waiting for results, and closing agent threads" — with no per-call
  schema-enforced structured outputs and no resume-from-journal. The deferral
  stands.
- **But the snapshot is materially incomplete.** Since 2026-06 Codex ships
  native subagents (`spawn_agent`, custom agents at `.codex/agents/*.toml` —
  the shape this repo already uses for its four role mirrors) plus an external
  Agents SDK scripting path. §4's "Codex CLI has no announced parity primitive"
  now reads as "no subagents at all," which is wrong.
- Claude Code's half of §4 re-verified accurate: the workflow primitive still
  spawns subagents, enforces JSON-schema structured outputs per agent call,
  composes sequential/parallel/pipelined stages, journals, and resumes.

*Recommendation: keep `status: draft` and keep the deferral. Retitle §4 to
"as of 2026-08-25", add the Codex-subagents fact with its retrieval date, and
restate criterion 1 as the narrower bar that is still genuinely unmet
(deterministic script + schema enforcement + journal/resume), so a future
session does not read "Codex has subagents now" as the trigger firing.*

**D3. `briefs/eacp-pattern-map.md`'s completeness claim is stale.** §1 asserts
"coverage of the *named* corpus is complete" as of a 2026-07-23 retrieval of
295 articles (292 draft). Checked today via the `eacp` MCP server: the corpus is
now **316 articles, 313 draft** across the same 14 sections — 21 articles the
map has never seen.

Sharper measure: of the 97 articles in the two most repo-relevant sections
(Agentic Software Construction, 67; Agent Governance and Feedback, 30),
**28 appear nowhere in the map by either slug or title**. That figure is a grep
lead, not a verdict — the map is a selective reading of what this repo
showcases, and several absences are correct (`graph-rag`, `react`,
`prompt-caching` have no bearing here). But several land directly on shipped
machinery and look like real gaps:

- `evaluation-gate` — `./bin/check all` blocking phase close is precisely this.
- `steering-loop` — the convergence-bounded revision loop.
- `loop-engineering` — `kickoff`'s outer loop, including the independent-verify
  and real-done-check halves.
- `plan-and-execute` — the planner/coder separation.
- `agent-workflow-graph` — the subject of `deterministic-orchestration.md`.
- `premature-termination` (antipattern) — what the fail-closed park and
  turn-ending rules structurally guard against.
- `trusted-monitoring` — the critic and the out-of-band supervision posture.
- `incident-to-eval-synthesis` — already cited in
  `briefs/harness-self-improvement.md` §4, but absent from the map itself.

*Recommendation: authorize a scoped re-run of the map against the current
corpus — re-enumerate the manifests, refresh the Retrieved stamp and counts,
and adjudicate the 28 named absences into "covered", "deliberately declined",
or "new gap". This is a real work item, not a one-line edit; it can also be
deferred to its own user action rather than folded into the apply stage.*

## Verified clean — no finding

Two claims that looked like drift and turned out correct on checking, recorded
so a later sweep does not re-litigate them:

- `briefs/session-context-compaction.md` §1 hook facts hold against current
  Claude Code documentation: `PreCompact` is real, matches on `manual`/`auto`,
  and blocks on exit code 2; `PostCompact` is a real event that runs after
  compaction and cannot block. (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` was not
  re-verified — the brief already flags it as third-party-documented.)
- `briefs/harness-self-improvement.md` §4's two external citations are genuine
  and accurately characterized: *Self-Harness: Harnesses That Improve
  Themselves*, arXiv:2606.09498 (June 2026), whose weakness-mining →
  bounded-proposal → regression-validation loop is described correctly; and
  Lilian Weng, "Harness Engineering for Self-Improvement"
  (`lilianweng.github.io/posts/2026-07-04-harness/`, July 2026).

## Blind spots in this pass

`briefs/agentic-bootstrap.md`, `briefs/cross-agent-invocation.md`,
`briefs/incremental-orchestration.md`, `briefs/methodology.md`, and
`briefs/methodology-treatise.md` were checked for status accuracy, date
accuracy, and link integrity only — their bodies were not re-read against the
repo. All five carry content-changing commits within the last two days and
their `status` values match reality, so the cost/benefit favored depth on the
older briefs. A later sweep should re-read them in full.

## Optional lesson

`bin/check-catalogs` validates tracked internal links but not intra-file
anchors, which is how A1's dead `#briefs-catalog` anchor survived every prior
check. If that is worth remembering rather than re-discovering, say so and a
`lessons/<slug>.md` entry gets filed; graduating it into an actual anchor check
in `bin/check-catalogs` would be a separate ratified change.

## Disposition

Ratified by the operator in-session on 2026-08-25 via `/ask`, and applied the
same session. Four of the five decisions took the recommendation; one did not.

- **A1, A2, A3 — applied.** `briefs/BRIEF.md`'s dead `#briefs-catalog` anchor now
  points at `#project-briefs` and `#methodology-briefs`; the EACP map's method
  bullet says "six"; the five stale `date:` fields are corrected. Three of those
  five briefs were edited again in this same pass, so their `date:` is 2026-08-25
  rather than the historical last-edit date the plan proposed.
- **D1 — applied as recommended.** `briefs/BRIEF.md` moved to `status: implemented`.
- **D2 — applied as recommended.** `briefs/deterministic-orchestration.md` §4 is
  restamped to 2026-08-25 and now records that Codex ships native subagents
  without a workflow-program primitive, with an explicit warning against
  misreading that as the trigger. Criterion 1 is narrowed to the deterministic
  control plane; criterion 4 carries a re-check history. The brief stays `draft`
  and the deferral stands.
- **D3 — operator overrode the recommendation.** The plan proposed filing a
  scoped re-run of the EACP map as its own user action; the operator chose to
  soften the completeness claim instead. `briefs/eacp-pattern-map.md` §1 now
  scopes its coverage claim to the 2026-07-23 snapshot and carries a dated
  currency bullet recording the 295→316 corpus growth, the 28 unaddressed
  articles in the two most relevant sections, and which of them look like real
  gaps. **The re-run is therefore not scheduled anywhere.** A future sweep that
  wants it must file it fresh.
- **Marker-semantics follow-up — applied as recommended.**
  [`policies/briefs.md`](../policies/briefs.md) § Status lifecycle now states that
  `status` is purely lifecycle and that portability is decided by the `CLAUDE.md`
  Project/Methodology catalog split. Verified first that nothing mechanical
  selects briefs by status: no script, skill, test, or policy greps for
  `status: methodology` on a brief — `learn` and `teach` key off `scope:
  methodology` on *lessons*, which is a different field on a different artifact.

**Recurring learning: yes.** The dead anchor survived every prior
`bin/check-catalogs` run because that checker validates a link's path and not its
`#fragment`. Filed as [`lessons/crimson-shrew.md`](../lessons/crimson-shrew.md)
(`scope: methodology`, `proposed_surface: bin`) — one occurrence, not
graduation-ready.
