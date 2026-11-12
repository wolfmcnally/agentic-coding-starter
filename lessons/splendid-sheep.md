---
slug: splendid-sheep
title: A product suite in another language needs one supplied way to run under supervision outside the worker pool
status: candidate
scope: methodology
proposed_surface: bin
filed: '2026-11-12'
source: user
occurrences:
- date: '2026-11-11'
  ref: a recipient with a browser-launching product suite — its first parallel run failed inside the worker pool; the suite was moved to a supervised command family in the project's own test script, with both lanes required before a tree is recorded
- date: '2026-11-12'
  ref: a recipient with a native app suite — built as a command family after the parallel run, with its own two-lane bracket and proof
- date: '2026-11-12'
  ref: a recipient with a browser-free script-language product suite — built as a new library module wrapping the supervisor, which also had to repeat the fixture no-signing override for that lane
---

Three recipients each wrote their own version of the same thing: run the product suite through the project's runner after the parallel methodology tests, under the hang supervisor, and record a tree as proven only when both lanes pass. Three copies is the cue to supply it once: a supported two-lane full run in the test entry point, the both-lanes proof, and the no-signing override applied to the native lane. The transfer skill should then say to declare a native suite this way before the first parallel run, not after it fails.
