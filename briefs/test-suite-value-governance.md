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

The one-time reset targets a declared fraction of both frozen family and leaf counts — a fifth in a repository pruning an overgrown estate, all of it in one that was stamped yesterday and whose baseline is already someone else's reset. That pressure is subordinate to effectiveness: the retained estate must meet its declared recall over a frozen local historical-defect corpus and a held-out local mutant corpus, and keep direct proof for every applicable critical-risk class. The corpus sizes are declared too, and a new repository declares none, because it has no defect history yet and borrowing another project's is not evidence about its own code. A class with no cases reports as unmeasured rather than as zero or as passing, and the declaration grows as the repository accumulates real defects to freeze. If the cap and those floors cannot coexist, the repository parks for its owner instead of changing the denominator or silently retaining the estate.
Corpus case metadata and mutation-patch bytes are digest-bound to the observed
effectiveness report so a nominally frozen holdout cannot drift after execution.

## Evidence makes removal reviewable

The frozen baseline records every proof identity. Its append-only ledger gives
each one a disposition, contract, oracle, red witness, nearest overlap,
replacement evidence, and rationale. Consolidation names a retained executable
replacement. Deletion states why no replacement is needed. A new post-baseline
proof names its active contract and risk, supplies the same evidence, and spends
an explicit positive budget or names a compensating retirement.

Zero-net-growth remains executable after the initial reset through append-only
lifecycle replay. A post-reset retirement removes one currently active baseline
or admitted proof, names its consolidation replacement or deletion rationale,
and creates one budget. One later admission consumes that retirement once.
Reset-era removals fund only reset-era admissions; they are not a permanent bank
for later growth. Replaying the ledger must reproduce the live estate exactly.

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

## Fast feedback does not narrow acceptance

Vital and changed lanes select retained proofs for iteration. Invalid inventory,
an unavailable comparison, an empty or ambiguous mapping, or an unrunnable
selector widens to the full retained estate. The full retained estate remains the
authoritative close and pre-push gate.

Periodic reassessment repeats the inventory, cap, ledger, risk, and corpus checks.
Every governed maintenance sweep runs the deterministic reassessment and reruns
the local assay when proof code, selection, corpus, or critical-risk applicability
changes. Shrinkage is therefore an executable obligation rather than permission
that can be deferred indefinitely.
