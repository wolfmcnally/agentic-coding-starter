---
slug: able-crocodile
title: Derive instrumentation from the thing being protected, not from the thing being tested
status: candidate
scope: methodology
proposed_surface: agent
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — a test derived its interception surface by parsing the module under test, so an implementation using an unseen route could evade the control"
---

A test needed to prove that no library call occurred before a guard ran. Its
first control parsed the module under test to discover which library entry
points to intercept. A wrong implementation could evade that control by using
an alias, a pre-bound attribute, or a dynamic lookup the parser never saw.

The stronger control derived the interception set from the protected library's
own namespace, which the implementation under test could not edit or shrink.

**The lesson has two parts.** A derived control needs the right direction
(enumerating more makes the assertion harder) and a closed evasion surface
(the subject cannot remove an element by changing how it reaches the protected
thing). Derive from the protected surface rather than from the subject.

When the protected surface cannot be closed completely, state exactly what the
instrument covers and pair it with a structural prohibition on the routes it
cannot observe. Do not promote partial observation into a universal claim.
