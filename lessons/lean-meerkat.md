---
slug: lean-meerkat
title: The sweep skill templates a LOG entry that log discipline does not authorize it to write
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-25
source: sweep
occurrences:
  - date: 2026-08-25
    ref: "sweep (lessons) — the skill's Stage 3 plan shape ends with a `## Proposed LOG.md entry` section, while `policies/log-discipline.md` opens by assigning `LOG.md` to `kickoff`. The first sweep in this repo (briefs, the same day) resolved the contradiction silently by writing no entry; this one resolved it the other way, on the precedent of the existing non-kickoff `LEARN` entries. Two sweeps, two different answers, neither of them written down anywhere"
---

`policies/log-discipline.md` states that `LOG.md` "is owned by `kickoff`" and
describes it as the record of phase entries and exits — a START/END pair per
phase. The `sweep` skill's plan template nonetheless ends with a
`## Proposed LOG.md entry` heading, and `LOG.md` already carries `LEARN` and
`TAUGHT FROM TEMPLATE` entries written by neither `kickoff` nor a phase.

So the policy's ownership sentence is narrower than the file's actual contents,
and a skill that follows its own template writes to a surface the policy hands to
someone else. Neither reading is unreasonable, which is the problem: the first
sweep skipped the entry, this one wrote one, and nothing records that a choice was
made either time. A contradiction that each session resolves privately is one that
gets resolved differently every time.

Two ways to close it, and the choice belongs to the operator:

- **Widen the policy.** State that `LOG.md` records non-phase repository
  operations too — `LEARN`, `TAUGHT FROM TEMPLATE`, `SWEEP` — and name which
  skills append which entry kinds. This matches what the file already holds.
- **Narrow the skill.** Drop the LOG section from the `sweep` plan template and
  route the sweep's record to its archived `user-actions` disposition instead,
  which is where the first sweep put it.

Filed rather than fixed: one sighting, and the fix is a rule edit either way,
which is the operator's to ratify.
