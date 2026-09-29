---
title: Test-Suite Value Governance
date: 2026-08-27
status: methodology
scope: Universal design for resetting and governing an attributable proof estate without allowing test accumulation to become permanent.
---

# Test-Suite Value Governance

A test suite is a proof estate, not an accumulating file count. Every executable
proof needs a contract, an independent oracle, a red witness, and a reason it is
not subsumed by a cheaper proof. The estate stays useful only when those claims
are tested against failures that matter and dominated proofs are physically
removed.

## Adoption begins with a reset

A repository adopting this method freezes its whole pre-reset estate, inventories
both parameter-collapsed families and expanded executable leaves, and dispositions
every proof as retain, repair, consolidate, or delete. Retaining everything for a later
audit is not adoption. The reset removes dominated test bodies together with dead
fixtures, helpers, and caller wiring; skipped, deselected, renamed,
or hidden proofs still count as present.

The one-time reset brings the estate within a declared test-lane time budget and gives every family a size class; a repository stamped yesterday declares the time its inherited estate already takes. That pressure is subordinate to effectiveness: the retained estate must meet its declared recall over a frozen local historical-defect corpus and a held-out local mutant corpus, and keep direct proof for every applicable critical-risk class. The corpus sizes are declared too, and a new repository declares none, because it has no defect history yet and borrowing another project's is not evidence about its own code. A class with no cases reports as unmeasured rather than as zero or as passing, and the declaration grows as the repository accumulates real defects to freeze. If the budget and those floors cannot coexist, the repository parks for its owner instead of changing the denominator or silently retaining the estate.
Corpus case metadata and mutation-patch bytes are digest-bound to the observed
effectiveness report so a nominally frozen holdout cannot drift after execution.
The corpus is measured, not maintained: its patches are anchored on source lines, so ordinary edits strand them, and keeping every one applicable between measurements would tax most changes to guard a number that is only read at maintenance time. Each sweep reruns the assay, repairs or retires stranded cases, and records the date, so recall is always reported as of a measurement.

## Evidence makes removal reviewable

The frozen baseline records every proof identity. Its append-only ledger gives
each one a disposition, contract, oracle, red witness, nearest overlap,
replacement evidence, and rationale. Consolidation names a retained executable
replacement. Deletion states why no replacement is needed. A new post-baseline
proof names its active contract and risk and supplies the same evidence.
A post-reset retirement removes one currently active baseline or admitted proof
and names its consolidation replacement or deletion rationale. Replaying the
ledger must reproduce the live estate exactly.

Historical cases may guide the retained selection. The holdout selection is
frozen before its mutants run, then the result is recorded without tuning. The
corpora, selectors, survivor identities, risk applicability, timings, and audit
judgments are always recipient-local; transfer carries the machinery and the
obligation to perform a new assay, never another repository's answer.

## Judging value without inverting it

The ledger makes a removal reviewable; it does not say which proofs deserve removal. That judgment needs a shared vocabulary, because agents write the same kinds of worthless proof repeatedly: assertions that cannot fail, expected values computed by the code under test, mocks that implement the behavior they are asked to check, negative controls that pass because a different guard refused, fixtures that hand the code the ordering it should have produced, and names that promise more than the assertions check. A named catalog of these shapes lets the author reject one before it lands and lets a later audit find the ones that did. Most of them share one root: the proof was written from the same understanding as the code, so it re-executes that understanding instead of checking it against the requirement.

The same judgment can point the wrong way. "Looks like the implementation" is the natural pruning signal, and the proofs that guard exact bytes, keys, paths, and wire formats look most like the code they protect, so a pruner scoring resemblance deletes the estate's sharpest contracts first. The counterweight is a retention bar that names the contract classes a proof may guard independently, and a rule that a kept proof failing on the baseline is a suspected defect in the product, not a stale proof. In the campaign this design draws on, every baseline failure in the pruned subsystem was a real delivery bug.

Two structural habits keep an estate from regrowing its redundancy. Each contract has one primary proof at its strongest boundary, and a second layer earns a place only with a risk the primary cannot reach; a periodic layer pass looks for whole suites that replay a shared helper through a mock beside a stronger real-boundary suite. And a proof that needs an export, flag, or injection hook no production caller uses is a sign the proof is at the wrong boundary, because the seam it demands becomes production surface that exists only to be tested.

A proof whose contract is real but whose assertion could not fail is neither kept as it is nor removed; it is repaired, and the ledger records the repair as its own disposition so a vacuous proof is never recorded as a sound one. Removal carries its own check: before a batch of retirements lands, someone who did not choose them compares the removed coverage against what remains, and each contract restored as a result is proved by one deliberate mutation of its owner that the remaining proof catches. Recall over a defect corpus measures the estate statistically once a corpus exists; this review guards each contract from the first batch, including in a repository too new to have any defect history.

## Governing time rather than count

The complaint that started this design was that agents wrote so many tests that the suite took too long to run. The first answer was a count budget: after the reset, a new proof had to be paid for by retiring an old one. Counting is a stand-in for time, and it points the wrong way in two places. It weighs a proof that launches subprocesses for a minute the same as one that checks a pure function in a millisecond; in this template one proof took nearly half the suite's wall time while counting as one of about a hundred. And it makes the cheapest way to add a check to fold it into an existing proof, whose name then stops describing what it guards and whose fixtures the new check silently inherits.

Governing time directly means living with a noisy instrument. Wall-clock time varies by around 1.5% between runs on one virtual machine and by as much as half between machines, and a single sample of a short operation cannot separate a regression from scheduler load (As of 2026-02-24; Retrieved 2026-09-29: [CI for performance: reliable benchmarking in noisy environments](https://pythonspeed.com/articles/consistent-benchmarking-in-ci/)). The established responses shape the design:

- **Coarse classes instead of tight thresholds.** Bazel gives each test a size whose timeout sits roughly an order of magnitude above the next (60, 300, 900 and 3600 seconds), tells authors to set it as tight as they can without flakiness, and warns when a test's size is larger than its runs need (Retrieved 2026-09-29: [Bazel test encyclopedia](https://bazel.build/reference/test-encyclopedia)). Google's small, medium and large sizes pair the time limit with what a test may touch: a small test is one process with no network, filesystem or sleeping (As of 2010-12; Retrieved 2026-09-29: [Google Testing Blog, Test Sizes](https://testing.googleblog.com/2010/12/test-sizes.html)). Here a family's size is chosen with twice its slowest measured leaf as headroom, so ordinary noise cannot cross a ceiling and a crossing means something real changed.
- **Compare like with like, and repeat before concluding.** A budget measured on one machine says nothing about another, so the lane budget is judged only on the machine that set it and reports unmeasured elsewhere. One run over budget is an advisory; the median of three confirms.
- **Count work, where the work is CPU.** Instruction counts from a cache simulator are nearly noise-free, but they miss disk and other non-CPU time (same pythonspeed source). An agentic repository's proofs are mostly subprocesses and files, so instruction counting is noted and not adopted.
- **Select before running.** The larger lever on feedback time is running less of the suite per change. Predictive test selection at Meta halved the cost of testing changes while still reporting over 99.9% of faulty changes (As of 2018-10; Retrieved 2026-09-29: [Predictive Test Selection](https://arxiv.org/abs/1810.05286)). The template's selection is deterministic rather than learned: a change runs the families mapped to its paths, and a document runs the families of the files that read it.

The feedback target those choices serve is the continuous-delivery commit stage, which should finish in under five minutes and never more than ten (Retrieved 2026-09-29: [The Commit Stage, Continuous Delivery](https://www.informit.com/articles/article.aspx?p=1621865&seqNum=4)).

## Fast feedback, one full run per push

A local commit runs only the proofs its change could break. Invalid inventory, an unavailable comparison, an unmapped or ambiguously covered code path, or an unrunnable selector widens to the full retained estate. A phase's implementation candidate is judged by the same selection. The full retained estate runs once, on the exact tree about to be pushed, and its receipt is what lets the push through; a failure it finds is fixed before anything leaves the machine.

Periodic reassessment repeats the inventory, size, time, ledger, risk, and corpus checks.
Every governed maintenance sweep runs the deterministic reassessment and reruns
the local assay when proof code, selection, corpus, or critical-risk applicability
changes. Shrinkage is therefore an executable obligation rather than permission
that can be deferred indefinitely.
