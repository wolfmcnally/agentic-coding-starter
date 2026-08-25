---
slug: expensive-pogona
title: An entry with no timestamp cannot participate in a sequence claim
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-20
    ref: "Donor A — a supervising session reconstructed a causal account of a tool-call rejection by reading a `last-prompt` row in FILE ORDER after the rejection, calling it 'the very next entry', and telling the owner 'the timestamps are conclusive' about a line that carries no timestamp. The referenced prompt was six minutes EARLIER; the account was inverted"
  - date: 2026-08-20
    ref: "Donor A — the same incident's other session printed those same rows with '-' in the timestamp column during its own forensics and did not remark on it. Its conclusion was correct only because its method happened to filter on timestamp strings. Immunity from method, not from noticing"
---

A session transcript's metadata rows — `last-prompt`, `custom-title`, `ai-title`,
`agent-name`, `agent-setting`, `mode`, `permission-mode`, and similar — are
**position-stable metadata rewritten near the file tail**. They carry no timestamp
and are not chronological events. Reading one in file order as "the next entry"
produces a confident, specific, and wrong causal account — and the wrongness is
invisible, because the surrounding rows *are* genuine events in genuine order.

**Mechanical rule: an entry with no timestamp cannot participate in a sequence
claim.** Filter a transcript by timestamp presence before ordering anything, and
**state the filter when reporting the result** — the same obligation
[`policies/verification-discipline.md`](../policies/verification-discipline.md)
places on a material count.

**The second occurrence is the more instructive one.** The reader who got the
right answer had the anomaly on screen — dashes where timestamps should be — and
said nothing about it. **Getting the right answer by a method that happens to be
immune is not the same as having a control**, and it will not generalize to the
next reader who greps differently.

The general form beyond transcripts: any file that interleaves *events* with
*mutable state rows* will be read as a sequence by someone, and file order is not
a clock.
