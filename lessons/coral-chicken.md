---
slug: coral-chicken
title: Do not try out a command that records proof against the live repository
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-11-10
source: user
occurrences:
  - date: 2026-11-10
    ref: "this template — while building test reuse under an operator-approved plan, the new recording command was run by hand in the working repository to see its output, with a passing exit status supplied as an argument; it recorded the half-edited, untested tree as one on which every proof family passes, and the next reuse run reported nothing to run until the record was deleted"
---

The command did exactly what it was built to do. Its job is to write down that a tree is proven when the run it brackets has passed, and it takes the run's exit status as an argument because the caller is the only party that knows it. Typed by hand with a zero, it has no way to tell a real pass from a claimed one.

Nothing was committed and the record was deleted within the same minute, so the cost was nil. The exposure was real, though: the full gate now trusts that record to decide which tests to run, and a forged one would have let the gate certify a tree whose tests never ran. The uncached run would have caught it only if someone ran it.

**A command whose effect is to record that something passed is exercised in a throwaway copy, never in the working repository.** The same applies to receipts, witness records and acceptance records. When building such a command, try it first inside a test fixture, and keep the recording step reachable only from the entry point that actually ran the work.
