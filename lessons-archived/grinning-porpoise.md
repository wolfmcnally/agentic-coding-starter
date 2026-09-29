---
slug: grinning-porpoise
title: A test helper's file location is not evidence that pytest executed it
status: codified
scope: methodology
proposed_surface: policy
filed: 2026-09-20
closed: 2026-09-29
graduated_to: policies/build-gates.md
source: learn
occurrences:
  - date: 2026-09-20
    ref: "Donor A — a changed expectation lived in a helper defined in one test module and invoked from another; the focused run covered the defining module, passed, and the full gate found the failure"
---

Folding a new case into an existing helper is the intended way to add proof without spending a family or a leaf, but it separates where an assertion is *written* from where it is *collected*. A focused selection chosen by the changed file therefore runs the module that defines the helper and not the module whose collected test calls it.

**The rule candidate:** when a retained proof is a helper, identify and run its collected callers in focused verification — selection follows the call graph, not the file the edit landed in. A focused lane that cannot name which collected node executed the changed assertion has not proved it.

This is the focused-selection case of the general rule that a check must state what it examined.

Closed 2026-09-29 by the operator as covered: the changed-path selection now also selects the families of files that name changed code, so a shared helper's users are tested at commit, and the full gate before the push still backstops anything reached by a computed name.
