---
title: Deterministic Orchestration Control Plane
date: 2026-10-27
status: methodology
scope: Deterministic command authority, custody and evidence for orchestration, and where scripts end and judgment begins.
---

# Deterministic Orchestration Control Plane

Primary ownership, independent advice and the one-shot route for methodology work are stated once, in [the methodology brief](methodology.md#primary-ownership-and-independent-advice).

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
The receipt binds the resolved venue targets, the executable and version each
resolved to, and the routing-configuration digest. An all-native run receives the same receipt shape with an empty target
set. Starter's separate write-enabled coder toolchain probe remains in force.

## Two candidate identities

The full-tree candidate remains the delivery and handoff identity. It includes
all tracked and nonignored-untracked files.

The root `candidate-partition.yaml` supplies the active/bookkeeping boundary. Product identity binds review and implementation evidence; full-tree identity proves gate non-mutation and the delivered tree. The declaration remains active and is digest-bound. Unclassified tracked paths refuse; unclassified nonignored untracked paths remain included as active. Bookkeeping-only edits preserve product identity without an exception ledger. Declared-authority checks and full snapshots for explicitly reviewed bookkeeping prevent an exclusion from hiding a meaningful change. Both close gates remain mandatory. The repair tools retain their narrower permissions.


## Append-only construction evidence

`log/entries/` holds immutable activity bodies and per-writer predecessor chains. `bin/multioperator append` publishes one new attributed body; `validate` verifies every body digest, sequence, predecessor and timezone-aware timestamp. Indexed validation also refuses committed history rewrites and verifies retained acceptance inputs against indexed tracked bytes. A later correction is a new attributed entry, never an edit or relocation of published history. Terminal END and PARK bodies retain their `Lessons:` witness.

## Bounded deterministic repair

The shared final-newline repair is limited to `EXECUTION_LOG.jsonl` under the declared bookkeeping contract. Phase discovery context and immutable activity entries are outside that repair set. Preserve original failed or incomplete evidence and use the owning supported append-only correction or interruption path; never normalize away qualifying history or infer success from missing bytes. An ambiguous target, substantive change or failed byte verification parks the affected action for the owner.

## Recipient-local adaptation

`learn`, `teach`, and `stamp` transfer the obligation and procedure, not a
project's command list or bookkeeping boundary. Each recipient defines and
tests its own exact commands, selectors, venues, privacy boundary, and proof
estate. The transfer remains atomic across policy, brief, managers, hooks,
tests, catalogs, and evidence schemas.
