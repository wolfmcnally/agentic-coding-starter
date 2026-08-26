---
name: sweep-coding
description: >-
  Longitudinal, user-gated sweep of the code-review loop: harvest every
  genuine code-critic verdict and every coder failure analysis from the
  machine's Claude Code and Codex traces over a window, categorize why
  implementations were sent back, attribute each category to a correctable
  coder defect, a critic false positive, or a structural gap, and propose the
  persona, script, and policy corrections as one plan the user ratifies.
  Enters plan mode first, analyzes inside it, and presents the analysis and
  the improvement plan together for approval; the plan's head is written for
  the operator in the plain register. In a template repo the corrections land
  here and propagate via teach; in a derived project they file as
  scope-methodology lessons for learn. Invoke as /sweep-coding in Claude Code
  or $sweep-coding in Codex; optional arguments set the window in days and
  project=<name> filters.
argument-hint: "[<days>] [project=<name> ...]"
last-reviewed: 2026-08-26
---

# Sweep-coding — Calibrate the coder ↔ critic loop from its own record

The code critic's verdicts and the coder's revision reports are both in the
harness transcripts verbatim: every `CODE-F` finding with its evidence and
state history, and every Failure Analysis in which the coder says why the
previous attempt earned it. Read together over a month they answer what no
single phase can: **what does the critic keep sending code back for, which of
those are the coder's to fix, which are the critic's habits, and where does
the loop itself leak rounds?** `sweep-planning` asks the same of the planning
loop; this skill is its sibling for the implementation loop.

The first run is the worked example: over 31 days and four derived projects,
the largest category was tests that could not fail (the coder scoring a
stand-in for the property — its own self-diagnosis in forty percent of the
failure analyses), then real defects, then planned items never delivered,
prose left describing the old behavior, and error paths that fall back to a
reassuring value. The one large critic false positive was a threat-model
overreach that cost five rounds before the owner amended it away, and the
coder's push-back channel had been used zero times in 328 findings. Those
became the coder's falsifier and gate-status fields, `bin/check-plan-delivery`,
the critic's threat-model boundary, and the unverified-handoff guard in
`kickoff` — see [`briefs/harness-self-improvement.md`](../../../briefs/harness-self-improvement.md).

## The lifecycle is shared — follow it by citation

This skill runs the **review-loop sweep lifecycle** defined in
[`sweep-planning/SKILL.md`](../sweep-planning/SKILL.md) with `kind = code`:

- **§Plan mode first** — enter plan mode before anything else; Stages 0–3
  read-only inside it; Stage 4 presents the analysis and the improvement plan
  as one document through `ExitPlanMode`; Stage 5 applies after approval. The
  document's Summary and Recommendations are in the `plain` register.
- **§Parse arguments** — `[<days>] [project=<name> ...]`; the kind is this
  invocation.
- **§Where the corrections land** — template mode edits `phase-coder.md`,
  `code-critic.md`, `kickoff` Steps 5–6, `bin/`, `policies/`; derived-project
  mode files `lessons/` entries.
- **§Stage 0** — read the latest `SWEEP-CODING (code)` entry in `LOG.md`.
- **§Stage 1** — harvest with the flag this kind needs (below).
- **§Stage 2 / §Stage 3** — the procedure verbatim, with the taxonomy and the
  attribution shapes from this file.
- **§Stage 4 / §Stage 5 / §The `LOG.md` entry** — verbatim, heading
  `SWEEP-CODING (code)`.

What follows is only what differs.

## Stage 1 — Sensors for the code loop

```bash
./bin/review-verdicts --since-days <days> --kind code --coder-evidence [--project <name> ...] --json <scratch>/code-verdicts.json
```

Read, in addition to the coverage and finding records the lifecycle names:

- **Coder evidence** — every Failure Analysis statement (`coder_evidence` in
  the dataset). This is the coder's own root-cause sensor; count how often it
  names a proxy ("scored a stand-in", "followed the implementation's shape",
  "treated X as evidence of Y").
- **State usage** — how many findings ever reached `rejected-with-evidence`
  (the coder refusing with evidence) and `superseded` (an owner amendment
  killing findings — read the amendment; it names a critic overreach).
- **Revision regressions** — `introduced-by-revision` and
  `newly-exposed-by-resolution` counts; each is a round the fix itself cost.
- **Rounds and routes** — code-review rounds and follow-up routes from each
  swept project's `LOG.md` END blocks; the projects' `lessons/` titles that
  mention the critic, the coder, tests, or proxies.
- **Gate status** — where the coder's Change Evidence carries `gate_status`,
  how often `not-run` appeared and what the reason was; where it does not yet,
  the Failure Analyses that say the venue could not run the toolchain.

## Stage 2 — Taxonomy for the code loop

| Category | What it looks like | Typical mechanism |
|---|---|---|
| **Real correctness defect** | races, ordering, a wrong branch, a fail-closed gap, liveness decided on the wrong process | the coder's, and legitimately the critic's to find |
| **A test that cannot fail** | asserts the implementation's own output, a source-substring "mutation proof", `assert x is not None`, a `**kwargs` lambda that accepts any signature, a timing test that never enters the window | verification followed the implementation's shape |
| **Planned item not delivered** | a named test, fixture, loop, or function absent; dead fixtures shipped unused | subset delivery — mechanizable (`check-plan-delivery`) |
| **Prose out of sync with changed behavior** | policy/plan/README/docstring still describing the old contract; a derivation comment contradicted by the committed fixture | revision without a doc sweep |
| **Reassuring default on an error path** | `except Exception: return 0`, `.get(…, [])`, `exists()` for absence, an exit code multiplexed and read as clean | fail-open habit |
| **Scope / style nit** | `__all__` order, encoding symmetry, docstring counts | rides along; rarely drives a round |
| **Environment / orchestrator** | gate never ran (sandbox), ledger text not passed to a carry-forward pass | structural |

## Stage 3 — Attribution shapes for the code loop

1. **Correctable coder defect.** Shapes seen on the first run: verification
   follows the implementation's shape rather than the plan's matrix; subset
   delivery; handing off with the gate never run; site-by-site repair that
   recurs at the next site; a revision that regresses a neighbor (mutation
   patches not re-anchored, prose not updated); focused test selection too
   narrow to reach a serialized type's consumers. Test: could
   `bin/check-plan-delivery`, a `falsifiers` row, or a one-line rule in
   `phase-coder.md` have refused the handoff? Run `check-plan-delivery`
   against a surviving run directory's approved plan when one exists.
2. **Critic false positive or bad habit.** Threat-model overreach — a
   finding that defends against an actor no phase, brief, or policy names
   (look for `superseded` runs and owner amendments); non-findings entered as
   `open` ("none required", "optional", "outside this phase"); placeholder
   carry-forward ("text not supplied to this pass"); an unexecuted runtime
   claim at `blocking`; severity inflation; re-verifying every untouched
   finding on every delta round. Count separately the findings the coder
   refuted in prose while still "fixing" them — each is a push-back the ledger
   never saw.
3. **Structural.** The delegated venue cannot run the toolchain; the
   orchestrator dispatched a pass without the ledger; the push-back route
   exists but nothing tells the coder to use it. The fix is in `kickoff`,
   `bin/kickoff-config`, `bin/kickoff-evidence`, or a policy.

Report the longitudinal view as the lifecycle says, plus: rounds per phase
against approval rate — a falling approval rate concentrated in one or two
phases is those phases' weather, not a trend; say which.

## Rules

Those of the lifecycle, plus one: **quote the coder's Failure Analysis when
attributing a category to the coder** — it is the only sensor in this loop
that speaks in the first person, and a category the coder already diagnosed
in its own words is a rule waiting to be written, not a finding to argue.
