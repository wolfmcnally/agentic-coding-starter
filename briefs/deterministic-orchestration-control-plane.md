---
title: Deterministic Orchestration Control Plane
date: 2026-08-28
status: methodology
scope: methodology
---

# Deterministic Orchestration Control Plane

## Primary ownership and independent advice

As of 2026-09-07, the primary use case is a configured SOTA instance that owns orchestration, planning, implementation and acceptance. A comparable or stronger model in another permitted provider's harness normally supplies independent plan and code advice; a single-provider environment uses fresh instances of the primary model. One comprehensive pass per stage is normal, a second needs recorded cause, and two is the maximum. Advisers report evidence and severity without veto; the primary decides corrections and records consequential dispositions. Objective requirements and both full gates remain binding.

A constrained primary uses separate planner/coder roles and the established approval-gated reviewer/critic loops. Detailed references to mandatory reviewer approval or four-role delegation below describe that constrained product branch. Eligibility is maintained configuration, not a benchmark claim. Backend and handling restrictions prevail over preferred routing. Optional kickoff usage checks refuse a primary at >=95% of any applicable limit and substitute the primary for a secondary above 95% weekly; absent tooling does not prevent execution.

All methodology work itself, including teach/learn knowledge transfer, is always one-shot by the invoking primary across harnesses and capability tiers, without delegated production or independent review. The primary owns adaptation, self-checks, required gates, commit and fast-forward push within authorized scope. This standing delivery grant does not expand scope or waive custody and human decisions. No product phase or repeated approval ceremony is needed for authorized methodology work.


## Decision

The orchestrator must establish executable authority before it spends the
phase's expensive acceptance budget. A run therefore carries one immutable,
content-addressed command manifest, a real-read venue receipt, separate product
and full-tree identities, and a fixed cheap preflight called command zero.

These controls are one bundle. A manifest without a runner is advisory; a
runner without immutable authority can execute drifted commands; a product
identity without a full-tree identity can conceal delivery drift; a semantic
log checker without an exact-byte witness permits rewritten history.

## Command authority

The active manifest contains exact argument vectors. Each managed gate is
identified by operation, attempt, final/non-final status, and argv. Activation
is append-only and binds the exact manifest bytes by SHA-256. A successor names
the digest it supersedes. The evidence manager rejects:

- an argv absent from the active manifest;
- a changed content-addressed artifact;
- a successor that does not name the current digest;
- a full-evidence gate without manifest authority; and
- a final receipt bound to an older manifest.

Arguments remain structured data throughout. A display string is derived with
shell quoting and never becomes the execution authority.

## Command zero

Before expensive acceptance, command zero runs the cheapest candidate-killing
checks in fixed order and stops at the first failure:

1. manifest, venue receipt, and stage topology;
2. every side-effect-free selector dry-run declared by the manifest;
3. formatting;
4. exact committed-log prefix; and
5. effective log chronology.

The ordering is economic, not cosmetic. A malformed selector or incomplete
run composition should cost seconds rather than an entire full gate.

## Venue qualification

A predictable echoed sentinel proves only that a venue can repeat prompt text.
Preflight instead creates unpredictable ASCII text in an isolated directory, names the file without disclosing its contents, and requires the venue to read and return the exact text. The manager validates the response and computes the file SHA-256 for the receipt. This proves read access using the declared read tools, without requiring binary decoding, model-side hashing, or additional shell permission.
The receipt binds the resolved venue targets and the routing-configuration
digest. An all-native run receives the same receipt shape with an empty target
set. Starter's separate write-enabled coder toolchain probe remains in force.

## Two candidate identities

The full-tree candidate remains the delivery and handoff identity. It includes
all tracked and nonignored-untracked files.

The root `candidate-partition.yaml` supplies the active/bookkeeping boundary. Product identity binds review and implementation evidence; full-tree identity proves gate non-mutation and the delivered tree. The declaration remains active and is digest-bound. Unclassified tracked paths refuse; unclassified nonignored untracked paths remain included as active. Bookkeeping-only edits preserve product identity without an exception ledger. Declared-authority checks and full snapshots for explicitly reviewed bookkeeping prevent an exclusion from hiding a meaningful change. Both full close gates remain mandatory. The repair tools retain their narrower permissions.


## Append-only construction evidence

`LOG.md` has one writer and two independent readers:

- `bin/log-append` appends a complete block at true EOF;
- `bin/check-log-prefix` proves the candidate starts with the exact committed
  bytes; and
- `bin/check-log-monotonic` proves effective chronology.

Stable block digests authenticate relocation and later chronology corrections.
A committed timestamp is never edited: a later correction record binds the
target block digest, repeats its recorded anchor, and moves its effective anchor
forward. Terminal END and PARK blocks carry a `Lessons:` witness.

## Bounded deterministic repair

One novel bookkeeping failure may receive one repair when the complete result
is mechanically derivable. The tool constructs and validates the replacement
in memory, makes one atomic write, and verifies the exact bytes afterward.
Implementation/product identity must remain unchanged.

The admitted repairs are:

- relocating one uncommitted log block by unique block identity; and
- normalizing the final newline of `LOG.md`, `EXECUTION_LOG.jsonl`, or
  `plan/INDEX.md`.

An ambiguous target, contextual patch, recurring signature, second attempt,
substantive change, or failed byte verification parks for the operator.

## Recipient-local adaptation

`learn`, `teach`, and `stamp` transfer the obligation and procedure, not a
project's command list or bookkeeping boundary. Each recipient defines and
tests its own exact commands, selectors, venues, privacy boundary, and proof
estate. The transfer remains atomic across policy, brief, managers, hooks,
tests, catalogs, and evidence schemas.
