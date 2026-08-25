---
slug: gigantic-puma
title: Whichever success/failure surface sits outside the failure-replacement boundary will eventually lie
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-17
    ref: "Donor A — the wrapper-exit family (already graduated there): a wrapper's exit code sat outside the child's failure path, so a red gate read as green. The READ side lying in the reassuring direction; five instances, two mechanisms"
  - date: 2026-08-18
    ref: "Donor A — a telemetry tool validated a confinement property OUTSIDE the fail-replacement boundary, so a failed rerun exited nonzero while leaving a prior PASS at the stable output path. The WRITE side lying in the reassuring direction: the file says PASS, the exit says fail, and the file is what a human reads later"
---

Two defects a night apart are mirror images of one law. A process communicates
outcomes through **multiple surfaces** — exit status, result files, log verdict
lines — and each surface is truthful only if it is produced *inside* the code path
that replaces success with failure.

The graduated wrapper-exit rule fixes the **read** side: status is read from the
captured artifact, never from a wrapper's exit. The second occurrence is the same
defect on the **write** side: a result file written before, or outside, the
failure boundary survives the failure and testifies to a success that did not
happen. **Both lie only in the reassuring direction, which is what makes the
family dangerous: no one investigates a PASS.**

**The rule.** Enumerate every surface on which a command reports its outcome, and
verify each is written or replaced *inside* the failure path. An artifact that can
survive its process's failure unmodified is a **stale witness**, and the fix is
structural — atomic replace-with-failure-result at the boundary — never
procedural.

**Review heuristic.** For any "writes a result file" code path, ask what the file
says after every nonzero exit. If the answer is "whatever it said before," the
defect is present.

The repair also shows the right decomposition: properties that *authorize* writing
(is the output path confined?) belong before the write; properties that *are*
evidence belong inside the replacement boundary. This repo's full-gate receipts
([`policies/build-gates.md`](../policies/build-gates.md)) are exactly such a
durable success record, and are the first place to apply the heuristic.
