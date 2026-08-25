---
name: sweep
description: >-
  Run a user-gated maintenance pass over the repo's accumulated rule surfaces:
  policies, briefs, skills, agent definitions, catalogs, and the lessons
  ledger. Finds staleness, contradiction, dead rules, aging ledger candidates,
  and catalog drift; settles every judgment call with the user first, then
  proposes retirements, merges, and graduations as one complete plan the user
  ratifies before anything is applied. In a template repo it additionally
  audits the methodology corpus that propagates to derived projects. Invoke as
  /sweep in Claude Code or $sweep in Codex; an optional focus argument narrows
  the pass (e.g. "skills", "lessons", "policies").
argument-hint: "[<focus>]"
last-reviewed: 2026-08-25
---

# Sweep — Prune and graduate the rule surfaces

Codified knowledge rots: rules contradict each other, skills drift out of step with the repo they describe, briefs outlive their status, ledger candidates age without a decision, and catalogs fall out of sync with the files on disk. `sweep` is the maintenance half of the improvement flywheel described in [`briefs/harness-self-improvement.md`](../../../briefs/harness-self-improvement.md): the capture half (`kickoff`'s lessons harvest) only compounds if something also prunes. Without a recurring sweep, the compounding asset becomes a compounding liability.

`sweep` is **plan-first and user-gated**: it audits, classifies, settles the judgment calls in conversation, and only then proposes a plan. It never silently edits a rule surface.

`sweep` deletes where its siblings add. `learn` imports a pattern and the mistake shows up in the diff; `sweep` retires a rule and the mistake shows up as a rule that has silently stopped binding — invisible until the thing it prevented happens again. That asymmetry is why the judgment calls are settled one at a time *before* the plan exists, rather than bundled into a single accept.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- If empty, run the full pass over every audit area below.
- If a focus is named (`skills`, `lessons`, `policies`, `briefs`, `catalogs`, `corpus`), run only that area plus the mechanical checks (which are cheap and always run).

## Plan-mode lifecycle (Stages 1–4)

Stages 1, 2, and 3 are read-only; Stage 4 surfaces the plan for approval; Stage 5 is the only stage that writes. This maps onto the harness's plan-mode contract — enter at the start of Stage 1, exit at Stage 4.

- **If the current harness exposes an `EnterPlanMode`-like tool** (Claude Code does today; Codex does not yet — see [openai/codex#11180](https://github.com/openai/codex/issues/11180)), **call it now** before starting Stage 1. The harness then enforces no-write through Stages 1–3; the bespoke "read-only until the approval gate" rule below becomes belt-and-braces.
- **If the harness does not expose programmatic plan-mode entry**, proceed without calling anything — the bespoke read-only discipline through Stages 1–3 carries the contract. The user may have entered plan mode interactively (Codex CLI's `/plan`; the Codex desktop app's plan mode); that's fine and orthogonal to this skill.
- **At Stage 4**, if you entered plan mode in Stage 1 (or detected the user did so interactively and the harness exposes `ExitPlanMode`), place the Stage 3 plan body where the harness's plan-mode contract specifies — Claude Code names a plan file to write; other harnesses may differ — and then call `ExitPlanMode`. The user's accept / revise / reject from the plan-mode UI is the Stage 4 approval signal. If `ExitPlanMode` is not available, fall back to the free-text approval described in Stage 4.
- **Stage 5 (Apply) always runs outside plan mode.** Either the harness has handed control back after `ExitPlanMode`, or no plan mode was entered. Either way, edits are permitted only after the user has approved.

The Stage 3 plan stays the canonical plan body in both paths. Plan mode is a harness affordance layered on top, not a replacement for it.

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

Output of Stage 1 is internal. The user sees Stage 3's plan.

## Stage 2 — Classify and decide

### Three-way triage

Classify every finding into one of three tiers. The `AUTO` / `DECIDE` vocabulary is the one from [`policies/phase-ripple.md`](../../../policies/phase-ripple.md); `sweep` splits `DECIDE` in two because a maintenance pass surfaces far more judgment calls than a phase ripple does, and treating them all alike makes the pass either unusable or dangerous.

- **AUTO** — mechanical, with one correct shape (a dead link, a renamed path in a skill step, a catalog entry the checker flagged). Never discussed item by item; batched into the plan and applied on approval.
- **Batched DECIDE** — judgment-bearing but low-consequence and homogeneous. Presented as **one** grouped question with a numbered list and a single recommendation covering the group, answerable in a word ("all", "all but 3", "none").
- **Individual DECIDE** — settled one at a time, in the dialogue below.

### The line between the two DECIDE tiers

> **Does the item change what binds future work?** If it retires, weakens, creates, or re-scopes a rule, or changes a brief's authority status while something still cites it — it is decided individually. Otherwise it batches.

The test is checkable rather than a matter of feel, and it tracks the actual risk this skill carries: the silent loss of a binding rule.

**Individually decided:** retiring or demoting a policy; graduating a lesson into any rule surface; rejecting a lesson (which closes it permanently); merging two rules into one; deleting or demoting a binding orchestration step under the doctrine growth rule.

**Batched:** homogeneous status transitions nothing currently cites (five briefs moving `implemented` → `historical`); near-duplicate lesson merges whose remedies coincide and where neither is being graduated; aging ledger candidates proposed for the same disposition; catalog and wording drift the mechanical checkers already flagged.

When a batched group turns out to be heterogeneous once written down — the items need different recommendations, or one of them trips the line above — split it. A grouped question whose single recommendation doesn't actually cover every member is an individual queue wearing a batch's clothes.

### Plain language is the form of every individual DECIDE

An explanation must be readable by someone who has not opened the file being changed — the [`plain`](../../../.claude/skills/plain/SKILL.md) register, applied to a decision. State, in this order:

1. **What is true today**, as behavior — "today, every phase must X."
2. **What changes** — "nothing would require X any more."
3. **Why it came up** — contradicted by, superseded by, or has never fired since adoption.
4. **What breaks if the call is wrong.**
5. **The recommendation.**

Not acceptable as an explanation: naming a file path, quoting the rule's own text as though it were self-evident, or citing a frontmatter field. Paths and quotes appear as *evidence*, never as the explanation — this is [`policies/treatise.md`](../../../policies/treatise.md) § "Explain decisions, not files" applied to a conversation instead of a document.

### Decision dialogue

Work through the individual DECIDE items **one at a time**, with the batched groups taking one turn each:

1. Explain one decision in the plain-language form above.
2. Stop for the user's decision. Answer questions about that decision without advancing to the next one.
3. Advance only after the user gives an explicit decision.
4. If a rendered question appears to have been swallowed, interrupted, or answered ambiguously, re-present the entire decision — context, options, and recommendation — rather than referring to a missing question.
5. When a structured question control is used, the plain-language explanation goes in the message *preceding* it. Option labels are too short to carry it, and a short label is exactly how a consequential retirement gets waved through.

User-added requests during the dialogue join the same queue and are decided before the plan. If no judgment calls exist, skip directly to the plan. The dialogue remains read-only; an individual "yes" adopts that decision, not the write set.

## Stage 3 — Plan

Regenerate the **complete** plan from the resolved decisions. Do not offer an incremental patch or assume the user can reconstruct the plan from the dialogue. Every formerly-DECIDE item appears with its recorded decision, so the approval gate shows what was settled rather than re-asking it.

Use this shape:

```markdown
# Sweep: <repo-name> — <YYYY-MM-DD>

**Scope**: <full pass | focus: "<focus>">
**HEAD**: `<sha or "untracked">`

## Summary

<One paragraph: what the pass found, what it did not.>

## Mechanical checks

- `./bin/check-catalogs` — <pass | N findings>
- `./bin/lessons validate` — <pass | N findings>
- `./bin/lessons candidates` — <N graduation-ready>

## Settled decisions

- **<decision>** — decided: <the user's call>. <One line of consequence.>

## AUTO batch

- `<file>` — <the mechanical edit>

## Findings left open

- `<area>` — <what was found, why nothing is proposed this pass, whether a lesson was filed>

## Proposed write set

- `<file>` — NEW | MODIFY (diff size)

## Proposed LOG.md entry
```

An empty plan ("nothing stale") is a valid, reportable outcome.

End the plan with one line: **"Approve this plan to apply, ask for revisions, or reject."**

## Stage 4 — Approve (gate)

Write nothing until the user clearly approves.

**Two paths, by harness capability** (per the Plan-mode lifecycle section above):

- **Plan-mode path.** Place the Stage 3 plan body where the harness's plan-mode contract specifies, then call `ExitPlanMode`. The harness presents accept / revise / reject affordances; the user's choice is the approval signal. Revise routes back to Stage 3 with the user's constraints; reject means write nothing.
- **Free-text path** (when plan mode is unavailable in the current harness). Wait for a clear approval signal in chat, or a specific opt-in like "apply everything but item 4."

Graduating a lesson into a rule surface and retiring a policy are exactly the human-ratification acts [`policies/lessons.md`](../../../policies/lessons.md) and [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md) reserve for the user — `sweep` is the proposal mechanism, never the authority. The Stage 2 dialogue settles *which* items are proposed; this gate is still the one that authorizes the write.

## Stage 5 — Apply

On approval:

1. Apply the approved edits (AUTO batch plus each ratified DECIDE).
2. For each graduated lesson: make the ratified edit to the target surface, then archive the lesson (`status: codified`, `closed:`, `graduated_to:`) into `lessons-archived/`. For each rejected lesson: archive with `status: rejected`. Run `./bin/lessons validate`.
3. Update `last-reviewed:` to today's date on every skill the sweep actually re-read — including ones with no findings.
4. Re-run the mechanical checks (`./bin/check-catalogs`, `./bin/lessons validate`) and finish with `./bin/check all`.
5. After the unchanged approved sweep passes `./bin/check all`, stage only its explicit paths, create an ordinary factual commit, and make a non-force push to one unambiguous configured upstream, then verify clean aligned tips ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)). Park delivery on any unexpected path, unresolved gate, missing or ambiguous upstream, divergence, or destructive Git need. Then report: findings by area, what was applied, what was declined, what remains open, and delivery status.

## Rules

- **Read-only until the approval gate.** Stages 1–3 write nothing, the decision dialogue included.
- **Batch the trivial, isolate the binding.** Mechanical items never get a question; homogeneous low-consequence items get one grouped question; anything that changes what binds future work gets its own.
- **Plain language is a gate.** An explanation an outsider could not follow is not a presented decision — rewrite it before asking. A decision the user could only evaluate by opening the file has not actually been surfaced.
- **Retirement requires evidence.** "Old" is not a finding; contradicted, orphaned, superseded, or provably dead is. Cite the evidence in the plan.
- **Never weaken the evaluator.** The sweep may not propose loosening `./bin/check` gates, test coverage, or review independence to make a finding disappear — the improvement loop's evaluator stays isolated from the thing being improved.
- **One sweep, one report.** Findings deferred by the user stay findable: file or recur a lesson for anything the user wants remembered rather than re-discovered next sweep.
- **Cadence.** Run when the user invokes it; suggest it in a phase report only when a mechanical check is already failing or `./bin/lessons candidates` is non-empty. A reasonable default cadence is once per handful of completed phases, or before a `teach` pass exports surfaces to another repo.
- Cross-harness: this canonical skill drives both harnesses. Codex discovers it through the `.agents/skills/sweep` directory symlink and invokes it as `$sweep`.
