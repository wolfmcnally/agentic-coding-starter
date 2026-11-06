---
title: Test-Suite Value Governance
date: 2026-10-12
status: methodology
scope: Marginal test value, bounded attempted work, diagnostic timing and qualified hang safety.
---

# Test-Suite Value Governance

Keep tests for the failures they distinguish. A useful test protects an active contract, reaches the relevant condition, uses an independent oracle and adds evidence the nearest existing proofs do not supply. Complete code coverage is a non-goal. A test count, assertion count, coverage percentage or mutation score cannot decide whether a scenario earns its maintenance and execution cost.

## Value is a contextual judgment

Judge semantic scenarios, including additions inside existing test functions. Several assertions may explain one result; unrelated scenarios packed into one function still carry separate evidence and cost obligations. Compare only the nearest relevant overlaps. To retire a test, explain why its actual keepers preserve its inputs, boundary, oracle, ordering, concurrency, execution lanes and diagnostic benefit. A counterexample where it fails and its keepers pass disproves domination. Retain uncertain cases rather than performing an expensive exhaustive redundancy search.

Mechanical inventories remain useful identifiers, not measures of value. Exact-byte, source or protocol checks may look implementation-shaped while guarding an independent public contract. Resemblance is a noisy proxy that can invert, recommending deletion of the strongest evidence. Review the contract and failure behavior before judging its syntax.

## Authoring evidence has a defined occasion

When a test is created or modified, demonstrate that each authored assertion can fail when the protected behavior is broken. Include repaired vacuous assertions and carried assertions in modified keepers. Record the targeted defect, reached precondition, intended assertion failure and restored success. A failure at the first assertion says nothing about later assertions; receipts must explain which observations establish which claims. Existing unchanged tests do not incur a retroactive witness sweep.

A targeted authoring witness and a mutation-tool survey serve different purposes. The witness establishes one authored check against a chosen defect. The survey searches for missed faults and can be costly or incomplete. Mutation tools run only on an explicit operator request, over any requested new or committed subset and for any requested duration. No routine gate, sweep or generic implementation approval supplies that request. A mutation score is never an acceptance target.

Historical reset ledgers and observation receipts remain recoverable evidence. No committed mutant corpus is restored: source-anchored defect patches previously became stale, and apparent detections could arise from unrelated failures. New modifications link their own receipts; an old matching test name does not prove a new assertion. Structural checks verify recorded shape and linkage, while the selected review lane verifies semantic relevance and freshness (primary self-inspection for methodology work).

## Work, elapsed time and hang safety answer different questions

Concrete attempted-work limits bound the operations that can multiply: input generation, rejects, shrinking, retry attempts, polling, fixture expansion, subprocess calls and teardown. Count transitive work, not only the top-level test body. An opaque operation can still hang or perform unbounded internal work, and a limit on accepted cases may conceal rejected attempts. Name those limitations rather than claiming a stronger bound.

Ordinary elapsed time is diagnostic because hardware, resource contention and the environment can change it without changing test value. Do not fail a correct slow test, rerun a completed suite to beat a budget or move work into a fixture to evade a metric. Explicit product-performance requirements keep controlled performance tests. Comparable trends can inform an owner decision; they do not automatically contain cumulative suite growth.

A separately qualified monotonic deadline stops a hung invocation. Output chatter does not renew it. Timeout and interruption are incomplete evidence, neither a correctness pass nor proof of a product defect. Preserve output, terminate owned children and report the supervised boundary honestly. Runtime startup and independently detached processes need enclosing guards; a process-group supervisor alone does not prove those boundaries. A bounded retry requires a concrete changed condition, and a repeated cause stops the loop.

## Adoption preserves useful history

Apply the method to new and modified tests immediately. Freeze a recipient-local inventory; explicitly distinguish completed judgments from pending baseline review. Inspect existing suites in bounded batches when a concrete reason warrants it. Completed resets are preserved, and inherited suites may retain every proof. No retirement quota, automatic whole-estate rewrite or retroactive observed-red campaign applies.

Transfer universal machinery, not another project's judgment. Families, selectors, risk applicability, timings, witness receipts, survivors and dispositions remain recipient-local. The full retained suite remains the handoff gate; focused lanes provide earlier feedback. Review pending groups and available cost trends at existing close/sweep seams without creating a new recurring benchmark campaign.

## Evidence informing the design

Retrieved 2026-10-12. The sources support the distinctions above; the authoring and adoption boundaries are operator decisions, not claims established by a metric.

- [Software Engineering at Google, testing overview](https://abseil.io/resources/swe-book/html/ch11.html) (2020): testing trades confidence against maintenance and execution cost.
- [Inozemtseva and Holmes, Coverage Is Not Strongly Correlated with Test Suite Effectiveness](https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf) (2014): after controlling suite size in five Java programs, coverage had only weak to moderate correlation with mutation-based effectiveness; this is evidence against treating coverage as value, not against every coverage use.
- [Hypothesis settings](https://hypothesis.readthedocs.io/en/latest/reference/api.html) and [libFuzzer options](https://llvm.org/docs/LibFuzzer.html) (retrieved 2026-10-12): example/run limits have specific semantics and do not necessarily count every attempted operation.
- [pyperf benchmarking guidance](https://pyperf.readthedocs.io/en/latest/run_benchmark.html) (retrieved 2026-10-12): environmental noise matters when interpreting runtime comparisons.
- [Practical Combinatorial Testing](https://www.nist.gov/publications/practical-combinatorial-testing) (2010): systematic interaction selection can reduce work where the fault model justifies it; it is not a reason to maximize combinations.
