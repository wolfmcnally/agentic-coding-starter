---
slug: skilled-skylark
title: A field name copied from prose is an assertion, and a wrong field name returns absence, not an error
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-20
    ref: "Donor A — a plan and its phase file both named the authoritative gate-status field by a name that does not exist in the gate ledger; the rows carry two differently-named fields. The coder found it and reported it as plan errata"
  - date: 2026-08-20
    ref: "Donor A — the orchestrator RELAYED that errata correctly, then copied the plan's wording verbatim into a handoff document whose entire purpose was telling the next reader where authoritative status lives. Caught only because its own probe of its own final gate returned a null where the authority was supposed to be, and a null there looked wrong"
---

Two rules from one defect.

**A probe of an authoritative field must assert the field exists before
interpreting its value.** A dictionary `.get()` on a wrong name returns `None`,
and `None` reads as *"no data"* rather than *"wrong question."* Compared against a
verdict it fails open or closed depending on which way the comparison was written,
and either way the reader learns nothing true. Print the key set, or index rather
than `.get()`, before believing a field's value. A verification that cannot
distinguish an absent field from a falsy value is the never-default-to-reassuring
defect in miniature — the same family
[`policies/acceptance-empirical.md`](../policies/acceptance-empirical.md) names as
a check that cannot fail.

**Knowing an errata is not the same as having applied it.** The orchestrator
relayed this exact correction and then reproduced the defect within the hour, in
the one document written to stop someone else hitting it. Corrections propagate as
**messages** but persist as **text**, and the text you are writing right now is not
covered by the message you just sent. **When you relay a correction, grep your own
in-flight artifacts for the thing you just corrected.**
