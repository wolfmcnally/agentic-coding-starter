---
slug: vengeful-shoebill
title: Never compose a timestamped record in the same command that reads the clock
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-13
    ref: "Donor A — an END correction block was stamped 13 minutes forward of the clock"
  - date: 2026-08-13
    ref: "Donor A — the next START block was stamped 34 minutes backward, by the identical mechanism, in the block written immediately after the correction that fixed the first one"
---

Twice in one donor session, by the identical mechanism: `date` and the heredoc
that consumed its value were issued in the **same** command, so the timestamp
was written from estimate before the clock's output was ever visible. The log
policy requires real timestamps and forbids back-dating, and the log is
append-only — so a committed error costs a correction block, and a correction
block with its own wrong timestamp costs a second one. That is exactly what
happened: the first fix had to be disclosed and re-committed.

**The rule: read the clock, then write the record with the value you read.**
One extra round trip. Never interpolate a remembered or estimated time into an
append-only log.

Generalizes past timestamps to any record whose field is *measured* rather
than *chosen*: capture the measurement, look at it, then write. Composing the
record and taking the measurement in one breath means writing what you expect
instead of what is true — the small, cheap form of the failure the
instrument-trust rules keep finding at larger scale.
