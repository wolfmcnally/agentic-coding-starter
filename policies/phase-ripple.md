# Policy: Phase Ripple — Pinned Decisions Propagate Downstream

When a phase closes, the orchestrator scans downstream drafted phase files and applies (or surfaces) the pinned decisions the just-closed phase captured. Downstream sketches stay fresh as work proceeds rather than diverging from reality.

This policy is the companion to [`phase-status.md`](phase-status.md). That policy governs status-marker flips in `plan/INDEX.md`. This one governs *content propagation* into downstream `plan/phase-*.md` files at phase close.

## What ripples

Source: the closing phase's END block in `LOG.md` plus the reviewer/critic verdict bodies. Specifically:

- **Plan-reviewer Observations** addressed to a later phase ("revisit X in the 2.2 planner", "the M.N renderer should pick up the new schema").
- **Code-critic findings** that constrain a downstream phase's approach.
- **Deliberate scope changes** the user or the orchestrator made during the phase (a deliverable moved between phases; a brief was amended; a build-gate was added).
- **Pinned values, names, paths, flags** that the closing phase fixed in place and that downstream phases reference (a CLI flag name; a module path; an API contract; a data-format version).

Source: the closing phase file itself. Specifically Acceptance items that named "to be decided in phase X" placeholders the closing phase has now decided.

## Where ripples land

- **Sibling sub-phases not yet run** (`plan/phase-N.(M+1).md` and later). If the parent's Deliverables are being addressed sub-phase by sub-phase, each closure may pin decisions the remaining sub-phases reference.
- **Downstream major phases** (`plan/phase-(N+1).md` and later) that were sketched at bootstrap to general specificity. Their Goal / Deliverables / Acceptance lists may reference surfaces the closing phase has now pinned or renamed.
- **`plan/INDEX.md`'s dependency graph and critical-files map** when a pinned decision adds or removes a dependency edge.

Ripples never land in the *closing* phase's own file (its history is fixed once `🚧 → ✅`), in `LOG.md` (append-only — the closing phase's END block already contains the source), or in `briefs/` (briefs are the upstream contract; the closing phase's brief refs may be added to downstream phase files, but the briefs themselves are not edited as a ripple side-effect).

## AUTO vs DECIDE classification

Mirrors `teach`'s stale-sweep model. Every potential ripple gets one classification:

- **AUTO** — mechanical edit with one correct shape and no judgment call. Examples:
  - Renaming a path the closing phase pinned that a downstream phase references verbatim.
  - Adding a brief ref the closing phase introduced to a downstream phase's "Brief refs" section when the downstream phase's Deliverables genuinely depend on it.
  - Tightening a downstream Acceptance criterion from "TBD in phase N" to the actual value phase N just pinned.
  - Updating a flag/value/version number the downstream phase references.
  AUTO ripples land as edits in the same `kickoff` session, before the END block is written, so the END block can list them.

- **DECIDE** — touches judgment-bearing content. Examples:
  - The closing phase reveals a downstream Goal needs revision (its scope shifted).
  - A downstream Deliverable became obsolete or was absorbed by the closing phase.
  - The dependency graph changes (a downstream phase no longer depends on this one, or vice versa).
  - Multiple acceptable shapes exist for the downstream edit and the orchestrator can't pick.
  DECIDE ripples are *not* applied. They are listed in the closing phase's END block as named manual follow-ups for the user to resolve before the next `kickoff`.

When in doubt, classify as DECIDE. The cost of surfacing a mechanical edit for human approval is one extra round-trip; the cost of an unwanted auto-edit to a downstream draft is silent drift.

## Who owns ripple application

`kickoff` Step 9a (sub-phase close) and Step 9b (major-phase close) execute the ripple pass.

`phase-planner` is invoked when the AUTO edit requires more than a one-line mechanical change — e.g., reshaping an Acceptance section to incorporate a now-pinned value. The planner is given the closing phase's END block, the downstream phase file, and the specific ripple description; it produces the edit.

`phase-coder` and `code-critic` are *not* invoked during a ripple pass. Ripples touch only `plan/` files, not project code. Code-impacting changes belong to the next phase's own kickoff cycle.

The user owns DECIDE resolution and may also override any AUTO edit by editing the downstream file directly before the next `kickoff`.

## Cross-references

- [`phase-status.md`](phase-status.md) — sibling policy governing status-marker flips. A phase's status is flipped *before* the ripple pass runs (so AUTO edits to downstream files don't accidentally land on the closing phase itself).
- [`acceptance-empirical.md`](acceptance-empirical.md) — downstream Acceptance criteria tightened by an AUTO ripple must still be empirical, not aspirational.
- [`log-discipline.md`](log-discipline.md) — the END block is append-only; AUTO ripples are recorded there in the same write that closes the phase, not as a later amendment.
- [`human-in-the-loop.md`](human-in-the-loop.md) — DECIDE items are surfaced to the user; the user owns commits and may roll back AUTO ripples before committing.

## Verification

A clean state after a phase close satisfies all of:

```bash
# Every AUTO ripple recorded in the closing phase's END block has a corresponding
# edit visible in `git status` (uncommitted) or in the immediately preceding
# commit if the user committed the kickoff's output.
grep -A20 -E '^## .*— END$' LOG.md | tail -40 | grep -E '^- AUTO ' && echo "AUTO ripples claimed; verify with git diff"

# No phase file references a name, path, or value the closing phase explicitly
# renamed in its END block. (Run after kickoff completes; before committing.)
# This is a manual sweep — the closing phase's END block names what was pinned;
# grep each pinned name across plan/phase-*.md to spot stragglers.

# DECIDE ripples are listed in the END block under a dedicated heading.
grep -A20 -E '^## .*— END$' LOG.md | tail -40 | grep -E '^- DECIDE ' || echo "no DECIDE ripples this close (clean)"
```

A clean repo prints "no DECIDE ripples this close (clean)" or lists each DECIDE item with its follow-up condition. AUTO claims correspond to real edits. DECIDE items reappear in the next kickoff's reading protocol until resolved.
