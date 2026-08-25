---
name: sweep
description: >-
  Run a user-gated maintenance pass over the repo's accumulated rule surfaces:
  policies, briefs, skills, agent definitions, catalogs, and the lessons
  ledger. Finds staleness, contradiction, dead rules, aging ledger candidates,
  and catalog drift; proposes retirements, merges, and graduations as a plan
  the user ratifies before anything is applied. In a template repo it
  additionally audits the methodology corpus that propagates to derived
  projects. Invoke as /sweep in Claude Code or $sweep in Codex; an optional
  focus argument narrows the pass (e.g. "skills", "lessons", "policies").
argument-hint: "[<focus>]"
last-reviewed: 2026-08-10
---

# Sweep — Prune and graduate the rule surfaces

Codified knowledge rots: rules contradict each other, skills drift out of step with the repo they describe, briefs outlive their status, ledger candidates age without a decision, and catalogs fall out of sync with the files on disk. `sweep` is the maintenance half of the improvement flywheel described in [`briefs/harness-self-improvement.md`](../../../briefs/harness-self-improvement.md): the capture half (`kickoff`'s lessons harvest) only compounds if something also prunes. Without a recurring sweep, the compounding asset becomes a compounding liability.

`sweep` is **plan-first and user-gated**: it audits, classifies, and proposes; the user ratifies; only then does it apply. It never silently edits a rule surface.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- If empty, run the full pass over every audit area below.
- If a focus is named (`skills`, `lessons`, `policies`, `briefs`, `catalogs`, `corpus`), run only that area plus the mechanical checks (which are cheap and always run).

## Stage 1 — Audit (read-only)

Run the mechanical checks first — they are deterministic and their output anchors the rest:

1. `./bin/check-catalogs` — catalog/file sync, tracked internal-link integrity,
   and the lifecycle-aware phase-ledger state machine.
2. `./bin/lessons validate` — ledger schema health.
3. `./bin/lessons candidates` — graduation-ready lessons (≥3 occurrences).

Then the judgment audits, each producing candidate findings:

4. **Policies.** Read `policies/` against `LOG.md`, `lessons/`, and the repo's current shape. Flag: rules that contradict each other or a newer policy; rules describing machinery that no longer exists; rules that have never prevented anything (no LOG/lesson/finding has referenced them since adoption — a candidate for merging or retirement, not automatic deletion); policy examples that have drifted from the files they cite. Apply the doctrine's growth rule ([`briefs/methodology.md`](../../../briefs/methodology.md) § Orchestration runtime doctrine) to every binding orchestration step: a step that cannot name the park it prevents or cite its motivating incident, or whose failure family a later structural fix made dead, is a deletion or demote-to-advisory candidate.
5. **Briefs.** Check each brief's `status` against reality per [`policies/briefs.md`](../../../policies/briefs.md): an `implemented` brief whose design has been superseded belongs at `historical`; a `draft` that has quietly become load-bearing needs promotion or a decision. Briefs decay if not maintained — this is the check behind that warning.
6. **Skills and agents.** Compare each `.claude/skills/*/SKILL.md` `last-reviewed:` date against the sweep date; re-read any skill past ~90 days or whose subject matter changed since its stamp. For agent definitions (no frontmatter date), use `git log -1 --format=%cs -- <file>` as the staleness heuristic. Flag steps that reference renamed files, retired tools, or contradicted policies.
7. **Lessons ledger.** Beyond the mechanical candidates list: flag `candidate` lessons that have sat unratified across multiple sweeps (propose graduate or reject — an undecided ledger is a silent backlog), and near-duplicate lessons that should merge (only when their *remedies* coincide — [`policies/lessons.md`](../../../policies/lessons.md) § Named families). **Read each occurrence `ref` against its own body**: a row that narrates several distinct instances is under-counting the lesson and silently suppressing the three-occurrence graduation trigger (the counting rule in `policies/lessons.md`) — this audit is the only enforcement that has ever caught it, because the lexical detectors built for it were all cut as hopeless. Treat catalog completeness and internal-link integrity as separate claims even though one deterministic checker now enforces both.
8. **Hub-only — methodology corpus.** Only when this repo is itself a template (detect: `.claude/skills/stamp/` exists). Audit the surfaces that propagate to every derived project: the universal policies, the methodology briefs, and the orchestration runtime doctrine in [`briefs/methodology.md`](../../../briefs/methodology.md) — applying the doctrine's own anti-ratchet rule: an instrument or rule whose defect class a design change eliminated is retired, not accumulated. A defect that ships from a template multiplies into every spoke; this audit exists because of that leverage.

## Stage 2 — Classify and plan

Classify every finding with the AUTO/DECIDE vocabulary from [`policies/phase-ripple.md`](../../../policies/phase-ripple.md):

- **AUTO** — mechanical with one correct shape (a dead link, a renamed path in a skill step, a catalog entry the checker flagged). Listed in the plan and applied on approval without item-by-item discussion.
- **DECIDE** — judgment-bearing (retire a policy, demote a brief, graduate or reject a lesson, merge near-duplicate rules). Each is presented with its evidence and a specific recommendation. When in doubt, DECIDE.

Present one plan: findings grouped by area, each tagged AUTO or DECIDE, with the exact proposed edit or disposition. An empty plan ("nothing stale") is a valid, reportable outcome.

## Stage 3 — Approve (gate)

Stop and wait for the user. The user may approve the whole plan, approve with exclusions, or reject. Graduating a lesson into a rule surface and retiring a policy are exactly the human-ratification acts [`policies/lessons.md`](../../../policies/lessons.md) and [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md) reserve for the user — `sweep` is the proposal mechanism, never the authority.

## Stage 4 — Apply

On approval:

1. Apply the approved edits (AUTO batch plus each ratified DECIDE).
2. For each graduated lesson: make the ratified edit to the target surface, then archive the lesson (`status: codified`, `closed:`, `graduated_to:`) into `lessons-archived/`. For each rejected lesson: archive with `status: rejected`. Run `./bin/lessons validate`.
3. Update `last-reviewed:` to today's date on every skill the sweep actually re-read — including ones with no findings.
4. Re-run the mechanical checks (`./bin/check-catalogs`, `./bin/lessons validate`) and finish with `./bin/check all`.
5. After the unchanged approved sweep passes `./bin/check all`, stage only its explicit paths, create an ordinary factual commit, and make a non-force push to one unambiguous configured upstream, then verify clean aligned tips ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)). Park delivery on any unexpected path, unresolved gate, missing or ambiguous upstream, divergence, or destructive Git need. Then report: findings by area, what was applied, what was declined, what remains open, and delivery status.

## Rules

- **Read-only until the approval gate.** Stages 1–2 write nothing.
- **Retirement requires evidence.** "Old" is not a finding; contradicted, orphaned, superseded, or provably dead is. Cite the evidence in the plan.
- **Never weaken the evaluator.** The sweep may not propose loosening `./bin/check` gates, test coverage, or review independence to make a finding disappear — the improvement loop's evaluator stays isolated from the thing being improved.
- **One sweep, one report.** Findings deferred by the user stay findable: file or recur a lesson for anything the user wants remembered rather than re-discovered next sweep.
- **Cadence.** Run when the user invokes it; suggest it in a phase report only when a mechanical check is already failing or `./bin/lessons candidates` is non-empty. A reasonable default cadence is once per handful of completed phases, or before a `teach` pass exports surfaces to another repo.
- Cross-harness: this canonical skill drives both harnesses. Codex discovers it through the `.agents/skills/sweep` directory symlink and invokes it as `$sweep`.
