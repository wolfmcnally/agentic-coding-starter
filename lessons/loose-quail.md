---
title: A transfer applied from a private rehearsal skips or delays the recipient's
  scope record
scope: methodology
proposed_surface: skill
source: teach
slug: loose-quail
status: candidate
filed: '2026-11-14'
occurrences:
- date: '2026-11-14'
  ref: Recipient A's 1.7.0 transfer; the worker wrote the scope record after copying
    the approved bytes and running the admission, and recorded the true order; it
    reported that this recipient's 1.5.1 transfer had the same departure, which the hub did not check
- date: '2026-11-14'
  ref: Recipient B's 1.7.0 transfer; the delivered commit carries one terminal log
    entry and no scope record at all, found by the hub when it compared the two results
---

The log policy requires a scope record before the work for every transfer. Both transfers of one release missed it on the same day: one wrote it late, one never wrote it. The gates passed in both, because nothing executable checks that a transfer's close has a scope record before it.

Two causes are visible and one occurrence each cannot separate them. The worker that wrote it late said that building the whole change in a private copy made applying it feel like a copy rather than the first write. And the hub's worker brief named only "the terminal log entry", while the transfer skill's apply stage does not name the scope record at all, so a worker following both had no step that asked for it.

Candidate correction: the transfer skill's apply stage names the recipient's scope record as the step before the first write to the real checkout, whether or not the change was rehearsed elsewhere, and worker briefs repeat it. A stronger form is executable: the record tool refuses a transfer's terminal record when no scope record from the same writer precedes it. The recipient that has none cannot gain one truthfully after the fact; a later record can only state the omission.
