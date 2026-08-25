---
slug: manipulative-silkworm
title: A specification MUST that binds a writer is not a validity predicate a reader may assert
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-14
    ref: "Donor A — a plan reviewer required a reader to assert an exact header field value the format specification mandates for that version. Every document in the authoritative population declares a different value; the first corpus probe returned 0 of 134"
  - date: 2026-08-14
    ref: "Donor A — one round later, the code critic required exact version/count triples, which is what the specification obliges a *writer* to emit. Six of 134 real, readable documents carried a combination the specification gives for no version; strict pairing would have silently dropped them"
---

Twice in one phase, one review round apart, a correctly-cited specification
requirement was turned into a reader-side validity check, and both times it
rejected real, readable inputs — first all of them, then six of them.

The requirement was quoted accurately each time. That is what makes it
dangerous: nothing looks wrong. The error is not in reading the specification.
It is in **who the sentence binds**.

A format specification's `MUST` is almost always an obligation on the
**producer**. It tells a writer what to emit. It does not license a consumer to
refuse everything else, because the population a reader meets was written by real
tools over decades, non-conforming in ways the specification cannot enumerate.
Widely-used formats ship a separate "how to read this" procedure precisely
because the conformance rules are insufficient as a parsing strategy.

**The discipline: for every check in a parser, name what it protects.**

- A count that determines *where the following array begins* stays exact. A wrong
  value means reading the wrong bytes — a genuine reader-side predicate, because
  it protects a computation the reader performs.
- A count the reader indexes into becomes a **floor**: at least the mandated
  value for the declared version, and the declared array must lie inside the
  stream. That protects the two things actually consumed.
- Exact version/count pairing protects nothing the reader consumes. It
  authenticates the *writer*, and the reader does not need the writer
  authenticated.

If you cannot say which computation a check protects, it is a conformance
assertion wearing a validity check's clothes, and its cost is measured in correct
inputs refused.

**The tell: the check's failure population is large and readable.** A validity
check that protects a real computation refuses garbage. A conformance check
refuses inputs that parse fine — which is why the only thing that caught either
instance was running the parser over the authoritative population and counting,
rather than over fixtures the same assumption authored. That is the same corpus
that produced the vacuous-uniformity worked case already recorded in
[`policies/acceptance-empirical.md`](../policies/acceptance-empirical.md).

Sibling of the graduated rule *route on the authoritative property, not a
convenient stand-in* ([`CLAUDE.md`](../CLAUDE.md)), which is about reading the
wrong *field*. This is about applying the right field's rule to the wrong
*party*.
