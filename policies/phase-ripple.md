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
- [`human-in-the-loop.md`](human-in-the-loop.md) — DECIDE items are surfaced to the user and are an unresolved gate: an open DECIDE ripple parks the phase, so it also parks delivery. AUTO ripples ride along in the delivered commit, and the user may revert them like any other part of the phase.

## Verification

Verification here is a **manual sweep**, and there is deliberately no command for
it. Read the closing phase's `Ripple:` block in `LOG.md`, then:

- For every `AUTO:` line, confirm a corresponding edit is in the phase's delivered
  diff. An AUTO claim with no edit behind it is a false END block, which
  [`log-discipline.md`](log-discipline.md) § Rules treats as the most dangerous
  failure mode in the file.
- For every name, path, or value the closing phase pinned, search `plan/phase-*.md`
  for stragglers the classifier missed.
- For every `DECIDE:` line, confirm it names a follow-up condition. DECIDE items
  reappear in the next kickoff's reading protocol until resolved.

**No grep against `LOG.md` substitutes for that read.** The previous version of
this section shipped two, and both were structurally incapable of reporting a
problem: they matched `- AUTO` and `- DECIDE` followed by a space, while the
orchestrator writes those lines with a colon, so one branch never fired and the
other printed "clean" on every run regardless of the truth. A check that can only
return one answer carries no information —
[`acceptance-empirical.md`](acceptance-empirical.md) § "A check must be able to
fail". Mechanizing this properly means comparing END-block claims against the
delivered diff, which is a real checker and not a one-liner; until one exists, the
honest form is the read above.
