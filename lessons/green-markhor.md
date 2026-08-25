---
slug: green-markhor
title: Nothing confirms that a closing phase's pinned decisions actually reached the downstream plan files
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-08-25
source: sweep
occurrences:
  - date: 2026-08-25
    ref: "sweep (policies) — policies/phase-ripple.md's Verification block was deleted as structurally incapable of failing, which left the ripple contract with no mechanical check at all. An END block claiming `AUTO: plan/phase-3.md — renamed the flag` is believed on its own word"
---

[`policies/phase-ripple.md`](../policies/phase-ripple.md) requires the orchestrator
to carry a closing phase's pinned decisions into downstream drafted phase files,
apply the mechanical ones, and record both halves in the END block. The END block's
`Ripple:` field is the *claim*. Nothing compares the claim to the diff.

That matters more than an ordinary missing check, because
[`policies/log-discipline.md`](../policies/log-discipline.md) § Rules names a
fabricated END-block claim as the most dangerous failure mode the log has, and this
is the one END-block field with no independent witness. `Build status:` is backed by
gate rows, `Acceptance:` by candidate-bound evidence, `Lessons:` by
`bin/lessons validate`. `Ripple:` is backed by nothing.

The shape is mechanically decidable and the inputs are already durable. A checker
can parse the most recent END block's `Ripple:` field, and for each `AUTO:` line,
confirm the named downstream plan file appears in the phase's delivered diff; for
each `DECIDE:` line, confirm it carries a follow-up condition; and confirm that a
`none — no downstream sketches` claim is true by checking whether any downstream
drafted phase file exists. What it cannot decide is whether a *needed* ripple was
missed entirely — an absence has no artifact — so the honest scope is "every claim
made is true", not "every ripple that should have happened did."

Filed rather than built: this repository has never run a phase, so there is no
END block to develop the checker against, and building one against invented
fixtures would produce a guard qualified only by its own fixtures. The right moment
is the first real phase close, in a repository that runs them.
