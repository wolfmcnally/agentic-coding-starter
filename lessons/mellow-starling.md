---
slug: mellow-starling
title: Grep the suite for the mechanism before recording an untestability claim
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-17
    ref: "Donor A — a coder reported a parent-directory fsync 'untestable without crashing a kernel'; the delta critic refuted it with two precedents already in that suite: one discriminating directory fsyncs via S_ISDIR on the descriptor, one fault-injecting the exact fsync point. The claim would have shipped as a recorded limitation while the repository already contained two working counterexamples"
---

"This cannot be tested" is a factual claim about the repository, not about
physics — and it is checkable the same way any repository claim is: search
for the mechanism. A suite that has ever needed to observe the same effect (a
directory fsync, a fault injection, a signal-timing window) has already built
the instrument. In the donor incident, the claim's author cited a precedent
for the *fix* while missing the precedent for the *test* — the search was run
for implementation help and not re-run for the verification claim.

The rule: before recording that a behavior is untestable (in a review
response, an END block, or a documented limitation), grep the suite for the
mechanism's fingerprints — the syscall, the fault-point name, the fixture
pattern. An untestability claim that survives that search is worth recording;
one that was never subjected to it is a guess wearing a limitation's clothes.
