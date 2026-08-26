---
slug: spiritual-sturgeon
title: A fault seam must assert the state it stands in before raising
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — three fault-injection tests raised immediately, so their clean-state assertions also passed when the protected sequence never began"
---

A test replaced a function with a fake that raised immediately, then asserted
that no residue or record remained. The same result occurs if the protected
sequence never reached the function at all, so the test could pass for an
unrelated early failure.

The injected fault named a point in a sequence but proved only that something
failed.

**The rule candidate:** a fault-injection fake first asserts the state the real
function would have observed, then raises. Check that staging completed, the
destination existed, or the relevant transition was reached before simulating
failure.

Pair this positive precondition with a falsifier that shows the test going red
when the guard is removed. One establishes that the intended seam was reached;
the other establishes that the outcome binds to the guard.
