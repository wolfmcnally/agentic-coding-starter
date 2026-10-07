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

The one-time reset brings the estate within a declared test-lane time budget and gives every family a size class; a repository stamped yesterday declares the time its inherited estate already takes. That pressure is subordinate to effectiveness: no contract may lose its only proof, and every applicable critical-risk class keeps a direct proof. If the budget and those obligations cannot coexist, the repository parks for its owner instead of silently retaining the estate.

## Evidence makes removal reviewable

The frozen baseline records every proof identity. Its append-only ledger gives
each one a disposition, contract, oracle, red witness, nearest overlap,
replacement evidence, and rationale. Consolidation names a retained executable
replacement. Deletion states why no replacement is needed. A new post-baseline
proof names its active contract and risk and supplies the same evidence.
A post-reset retirement removes one currently active baseline or admitted proof
and names its consolidation replacement or deletion rationale. Replaying the
ledger must reproduce the live estate exactly.

Selectors, survivor identities, risk applicability, timings, witness receipts, and audit
judgments are always recipient-local; transfer carries the machinery and the
obligation to judge the recipient's own estate, never another repository's answer.

## A witness is an observation, and a mutant is scaffolding

A proof that has only ever been seen to pass has shown that it agrees with the code, not that it can catch anything. The check is old and simple: plant the defect the proof exists to catch and watch it fail. An agent that writes a check, runs it against correct code and sees green has not done this, and a sentence saying it was done is the same optimism written down. In this template, before the change this section describes, 47 of 52 proof families recorded no planted defect at all, and every admitted proof carried only such a sentence.

So the observation is made by a command and kept as a receipt. The command sees the proof's own test command pass, lets the author plant the defect in the working tree, requires the same command to fail with a named piece of text, puts the original bytes back, checks them, and sees the command pass again. Requiring the named text matters as much as requiring the failure: a test that goes red because the planted change broke something unrelated has witnessed nothing. The receipt records what was planted and what was seen. It is written by the tool and can be repeated by anyone who doubts it; it is not proof against deliberate forgery.

The mutant itself is thrown away. Industrial practice converged on this. Google generates mutants only for the lines a change touches, shows a few to the author and reviewer during code review, and treats them as goals for better tests, never as a stored battery or a score to reach (As of 2021-02; Retrieved 2026-10-06: [Practical Mutation Testing at Scale](https://arxiv.org/abs/2102.11378)); developers exposed to them this way went on to write tests that left fewer mutants alive (As of 2021-03; Retrieved 2026-10-06: [Does mutation testing improve testing practices?](https://arxiv.org/abs/2103.07189v1)). Meta's test-generation system uses each mutant as the prompt for a test that kills it, lands the test, and discards the mutant (As of 2025-01; Retrieved 2026-10-06: [Mutation-Guided LLM-based Test Generation at Meta](https://arxiv.org/abs/2501.12862)). The Thoughtworks Technology Radar places mutation testing in Trial and calls it the most honest signal of a suite's ability to detect faults, the more so where tests are machine-written and can stay green whatever the code does (As of 2026-04; Retrieved 2026-10-06: [Mutation testing](https://www.thoughtworks.com/radar/techniques/mutation-testing)).

This design first did the opposite, and the record is worth keeping. It held two dozen hand-written defect patches, half reintroducing past bugs and half held out, and required the pruned estate to catch a declared share of them. That measurement did its one job, which was to show that the reset had not thrown away the estate's ability to find faults. As a standing instrument it failed in the way a patch anchored on source lines must: ordinary edits to the code moved the lines, and three of the twelve held-out patches stopped applying within a week of a measurement. The instrument also misled twice, once counting a broken copy as a detection and once letting a new guard detect the planted defects by itself. A recall figure over twelve cases moves eight points when one case flips. Keeping every patch applicable would have taxed most changes to guard a number read only at maintenance time, so the patches and the figure were retired together.

What a stored mutant did offer was a standing guarantee that its test still catches its fault. That guarantee now comes from the tests: the direct proof for each critical risk drives the guard with input it must refuse, or switches the guard off in-process, and asserts the refusal on every run. A semantic check of that kind does not rot when lines move.

The command needs only files and a command to run, so it is the same in a Python, TypeScript or Rust repository, and working in the live tree keeps each language's build cache warm. Finding weak tests in bulk is a separate job for a mutation tool, which differs by language and may not exist for one; a repository without such a tool reports that measurement as not taken and still witnesses every proof it admits.

## Judging value without inverting it

The ledger makes a removal reviewable; it does not say which proofs deserve removal. That judgment needs a shared vocabulary, because agents write the same kinds of worthless proof repeatedly: assertions that cannot fail, expected values computed by the code under test, mocks that implement the behavior they are asked to check, negative controls that pass because a different guard refused, fixtures that hand the code the ordering it should have produced, and names that promise more than the assertions check. A named catalog of these shapes lets the author reject one before it lands and lets a later audit find the ones that did. Most of them share one root: the proof was written from the same understanding as the code, so it re-executes that understanding instead of checking it against the requirement.

The same judgment can point the wrong way. "Looks like the implementation" is the natural pruning signal, and the proofs that guard exact bytes, keys, paths, and wire formats look most like the code they protect, so a pruner scoring resemblance deletes the estate's sharpest contracts first. The counterweight is a retention bar that names the contract classes a proof may guard independently, and a rule that a kept proof failing on the baseline is a suspected defect in the product, not a stale proof. In the campaign this design draws on, every baseline failure in the pruned subsystem was a real delivery bug.

Two structural habits keep an estate from regrowing its redundancy. Each contract has one primary proof at its strongest boundary, and a second layer earns a place only with a risk the primary cannot reach; a periodic layer pass looks for whole suites that replay a shared helper through a mock beside a stronger real-boundary suite. And a proof that needs an export, flag, or injection hook no production caller uses is a sign the proof is at the wrong boundary, because the seam it demands becomes production surface that exists only to be tested.

A proof whose contract is real but whose assertion could not fail is neither kept as it is nor removed; it is repaired, and the ledger records the repair as its own disposition so a vacuous proof is never recorded as a sound one. Removal carries its own check: before a batch of retirements lands, someone who did not choose them compares the removed coverage against what remains, and each contract restored as a result is proved by one deliberate mutation of its owner that the remaining proof catches. This review guards each contract from the first batch, including in a repository too new to have any defect history.

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

Periodic reassessment repeats the inventory, size, time, ledger, risk, and receipt checks.
Every governed maintenance sweep runs the deterministic reassessment and reports
how many proofs still have no witness receipt. Shrinkage is therefore an executable
obligation rather than permission that can be deferred indefinitely.
