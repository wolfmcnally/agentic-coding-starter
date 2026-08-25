---
slug: rousing-bee
title: A status that names the record must be earned by a search, or it launders retrieval failure as record absence
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — two proof ladders were authored with most rungs marked blocked-on-record, and a contradiction reported between sources, while the distinguishing primary records sat unread inside the very scope the ladders were built over. Nothing had been searched for; the gaps in a handful of grep passes were recorded as gaps in the record"
  - date: 2026-08-16
    ref: "Donor A — same shape, different costume: a schema parser written against a hand-typed fixture rejected every real store of the format it validated, including a multi-gigabyte index in active use, because the fixture's casing was the author's own. The authoritative declaration was one read away"
---

A status field whose meaning is "absent" is **a claim about the world**. It was
used as a claim about the author's own effort. Those are different assertions,
and only one of them was true.

The failure has the same shape as a verification that can only return "good": a
status that can only mean *I did not find it* is not a status, because nothing
distinguishes it from *it is not there*, and the downstream reader — a human
deciding what to procure, a later pass deciding what to weigh — cannot tell which
one they were handed.

**The cost is not only a wrong label.** A rung marked blocked-on-record generates
an acquisition task, so under-retrieval **manufactures work**: it asks an operator
to go obtain something already filed. The error is self-concealing in exactly the
wrong direction — the more thorough the task list looks, the more confident the
whole structure appears.

**The rule.** Before asserting that a record lacks something, search the record
for it, and say what the search was. Any status, finding, or report whose meaning
is "absent" should be able to name the retrieval that justifies the word — which
index, which query, which population. A blocked status with no search behind it is
an opinion wearing a schema field. This is the absence-vs-ignorance conflation,
and it recurs wherever a system has a vocabulary for "not found."

Two aggravating details, kept because they shape how the rule should be written
if it graduates:

- **The instrument was ready and unused.** A semantic index over the corpus had
  been rebuilt to full coverage hours earlier. The search that would have found
  the documents was not merely omitted.
- **A twelve-category adversarial review missed it.** The critic attacked what
  the ladders *said* and never asked whether the corpus held something they had
  not looked for. **A reviewer contract that reviews assertions does not catch a
  missing search** — which suggests the check belongs at authoring time, not
  review time.

**The second occurrence generalizes the title.** There, a parser asserted a
property of an external format from an internal model of it, when an instance was
on disk in a store the author had opened the same session. The common core is
*asserting a property of an external artifact from an internal model of it, when
the artifact was available*. The remedy carries its own guard: when a parser must
read someone else's format, its fixture is a **captured instance**, not a composed
one — so a format change breaks the test rather than the gate.

Related but distinct: [`policies/verification-discipline.md`](../policies/verification-discipline.md)
already rejects blacklist-as-closed-world and treats grep as a lead. This is the
inverse direction — not "I found nothing bad" but "I record that nothing exists,"
asserted from a search that was never run.
