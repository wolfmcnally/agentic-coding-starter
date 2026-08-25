---
slug: curvy-zebra
title: An independent oracle validates arithmetic, not semantics — it can agree perfectly and still answer the wrong question
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-12
    ref: "Donor A — a pre-implementation acceptance oracle confirmed every acceptance number while encoding a wrong definition of the phase's key term"
  - date: 2026-08-13
    ref: "Donor A — a hand-written structural check reported a close artifact 'valid'; the real validator, one command away, then refused it three times on rules the check never had"
---

The orchestrator derived a phase's acceptance figures independently, before any
code existed, through its own separate implementation, and recorded the result
as a gate row. The coder's implementation later reproduced every number exactly.
Two independent derivations, perfect agreement.

Both were wrong about what the number *meant*. The phase asked how every
selected item terminated; the oracle counted an explicitly non-terminal state as
terminal, so the "all terminal" figure could read true while the downstream work
had not happened at all. Worse, the orchestrator had resolved that specification
ambiguity itself and instructed the coder accordingly — so the oracle's
agreement was not confirmation but the same misreading executed twice. The code
critic caught it four rounds in.

**The generalizable shape.** An oracle built by the same mind that resolved the
spec inherits that resolution's semantics. Numerical agreement between two
implementations tests transcription, arithmetic, and data access — never whether
the quantity is the one the specification asked for. The failure is invisible
precisely because agreement *feels* like triangulation.

This complements [`policies/acceptance-empirical.md`](../policies/acceptance-empirical.md)
rather than restating it: that policy guards against an instrument that cannot
fail; this guards against two instruments that agree.

**The cheaper variant: the surrogate validator.** Closing a later phase, the
orchestrator wrote a close artifact and then confirmed it with a short
hand-written check that counted entries and printed "valid". The real validator —
one command away, inside the tool about to consume the file — refused it three
times: forbidden vocabulary, a forbidden word in one field, and a partially-null
object where the schema wanted a complete object or a plain null. The
hand-written check was not wrong about what it measured; the counts were right.
It simply was not the question the consumer asks, and its cheerful "valid" spent
the orchestrator's confidence on a file that could not be published.

The remedy for that variant is much smaller than for the first: **when the real
validator is one command away, do not write your own.** A surrogate check is
defensible only where no authoritative one exists.

Candidate rule, if this recurs here: an orchestrator-built acceptance oracle is
handed to the reviewer as a claim to attack on semantics, not as a target to
match — and any spec gap the orchestrator resolves before dispatch is labeled a
*resolution under test*, with the reviewer asked explicitly whether the quantity
is the right one, not merely whether the code computes it correctly.
