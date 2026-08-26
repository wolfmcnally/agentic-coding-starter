---
slug: wealthy-koel
title: An operator protocol is executable content
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — a demo's later commands could not resolve, and its repair step expected an outcome a correct implementation could not produce"
---

A try-it-yourself protocol looked coherent in prose but failed when executed.
Its first command ran through a project wrapper while later steps assumed the
wrapper had changed the parent shell. It had not, so every later command was
unresolvable.

The same protocol accumulated several destructive variations and then promised
a repair command that could restore only one of them. A correct implementation
therefore produced the protocol's supposed failure signal.

**The rule candidate:** treat every expected result in an operator protocol as
an assertion about correct behavior. Execute the complete route before
shipping it. Isolate destructive variations so one does not contaminate the
next, and state plainly when a repair cannot restore a prior mutation.

A protocol that expects the wrong result spends more than time: it turns
correct behavior into evidence against the build.
