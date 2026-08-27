---
slug: pastoral-tarantula
title: Trace test-to-test dependencies before consolidating structural proofs
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-27
source: learn
occurrences:
  - date: 2026-08-27
    ref: "Donor A — a proof-estate audit found that apparent test overlap did not reveal which tests produced fixtures or assumptions consumed by other tests"
---

Two tests can look redundant when their names, target code, or assertions
overlap while still participating in different proof flows. One may construct a
fixture, establish a baseline, qualify an instrument, or preserve an artifact
that another test consumes. Deleting it on surface similarity can therefore
remove the producer while leaving the consumer in place, producing either a
misleading pass or an unrelated failure.

Before consolidating structural tests, trace test-to-test dependencies as well
as source-to-test coverage. Name each produced artifact or assumption and each
consumer, then prove that the retained replacement preserves the same contract,
oracle, and red witness. Test counts, runtime, age, and lexical similarity are
only proxies for that value and may invert the judgment.
