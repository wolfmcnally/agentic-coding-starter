---
slug: able-heron
title: Progress needs a position against a known total; activity and new-work both lie, in opposite directions
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-12
    ref: "Donor A — a runaway long-running ingest read as healthy because its operation count kept rising; activity was mistaken for progress"
  - date: 2026-08-12
    ref: "Donor A — a healthy resume of the same run read as stalled because ledger rows were not growing; new-work was mistaken for progress — the same error inverted, hours later on the same run"
---

Watching one long-running job twice in one day, the orchestrator picked the wrong
progress signal twice, in opposite directions, and was confidently wrong both
times.

**Activity said healthy; the run was dead.** The signal was raw operation count:
18,763 of them, arriving steadily. The run had produced **8 ledger rows in two
hours**. An operation count measures that something is happening, not that
anything is being accomplished.

**New work said stalled; the run was fine.** The correction was to watch ledger
rows, with a ten-minute flat window as the alarm. It fired. But a resume over an
already-complete batch legitimately writes **zero** new rows: every member it
walks is already filed, so each step is a verified skip. The instrument built to
catch the first failure would condemn every healthy resume.

**The third signal — a monotonic cursor — looked sound and was also wrong, for
the subtlest reason.** The orchestrator had *itself* established hours earlier
that the index carries across resumes and so cannot imply population; it then
used the highest index seen during the earlier runaway as a ceiling, concluded a
run was "minutes from the end," and let it walk well past. **Using a number one
has personally discredited as a safety bound is worse than having no bound**,
because it converts an unknown into a false reassurance.

What actually resolved it was structural, not statistical: reading the code to
ask whether the walk *traverses a fixed set* or *allocates as it goes*. It
allocated — the drain loop re-enqueued split children from inside itself — so the
cursor was never a position at all.

**The generalizable shape: progress is position over a known total.** Activity
counts and new-work counts are each valid only under an assumption about the
workload — that it is producing, or that it is novel — and a long run violates one
or the other routinely. Before instrumenting a loop, establish what bounds it; if
the total is unknown or the loop can extend its own workload, no rate metric can
distinguish progress from thrash, and the question must be answered structurally.

Corollary worth its own line: **an instrument's own failure mode is part of its
design.** "Flat for N minutes" must be paired with what legitimately produces
flatness, or the alarm is a coin flip with authority. That is the same defect
[`policies/acceptance-empirical.md`](../policies/acceptance-empirical.md) names as
a check that cannot fail, met here from the false-red side.
