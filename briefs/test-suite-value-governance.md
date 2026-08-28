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
every proof as retain, consolidate, or delete. Retaining everything for a later
audit is not adoption. The reset removes dominated test bodies together with dead
fixtures, helpers, mutation rows, and caller wiring; skipped, deselected, renamed,
or hidden proofs still count as present.

The one-time reset targets no more than 20% of both frozen family and leaf counts.
That pressure is subordinate to effectiveness: the retained estate must recall at
least 80% of a frozen local historical-defect corpus, kill at least 80% of a held-
out local mutant corpus, and keep direct proof for every applicable critical-risk
class. If the cap and those floors cannot coexist, the repository parks for its
owner instead of changing the denominator or silently retaining the estate.
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
