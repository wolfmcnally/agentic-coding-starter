# Policy: Verification Discipline

Verification must inspect the property that determines the answer, not a
convenient stand-in. Every review, audit, and formal finding follows these
rules.

## State the blind spot

No finite verification proves universal absence. A clean report names what was
actually inspected and any material surface the instrument could not see. Do
not turn unavailable evidence, an empty query, or an unsupported format into
"none found."

## A grep lead is not a finding

Search output identifies candidates for inspection. It becomes evidence only
after the matching material is read in context and the asserted behavior is
confirmed. Counts of matches are counts of a text pattern, not counts of the
underlying defect.

Never key a detector solely on a token the subject itself legitimately emits.
If the rule under review discusses `TODO`, a grep for `TODO` will select the
rule along with unfinished code. If a safety document discusses a prohibited
term, matching the term does not establish the prohibited act.

## Blacklists do not prove a closed world

A denylist can establish that named bad cases were absent. It cannot establish
that no other bad case exists unless the domain is demonstrably closed and the
list is complete by construction. State the narrower claim, then inspect the
authoritative inventory when a closed-world claim is required.

## Test proxies for sign inversion

Every filter, score, heuristic, bucket, and detector measures a proxy. Name the
proxy, characterize an innocent item that triggers it, and ask whether it can
invert the sign: systematically surface the best or safest material as the
worst while gaining confidence from more evidence.

The cheap audit is to strip the selected items and read every justification as
a bare column. Independent findings have independent reasons. Synonymous
reasons, "same as above," or reasons that only restate the bucket indicate that
the classifier is doing the judging instead of the evidence.

When inversion is possible, the instrument is not merely noisy. It is unsafe
for destructive or blocking decisions until tested against known-positive and
known-negative fixtures that demonstrate the intended direction.

## Material counts are reproducible

Any material count in a plan review, code review, formal report, or finding
includes the exact command or deterministic procedure that produced it. A
relay either re-runs that procedure or attributes the number plainly as
unverified. Do not launder an earlier summary into fresh evidence.

## Sweep every embodiment of a changed contract

Changing a shared contract is not complete when the contract's own file and its
own test file are updated. The places that embody a contract are **independent
inventories** that no single obvious search unifies: a tool's behavioral tests, a
different tool's suite that initializes the contract as a fixture, a gate's
stub-executable list, and that same gate's expected call-log assertions can each
hold their own copy.

Two moves carry this risk, and they fail in opposite directions:

- **Making a member required** — a new mandatory flag, a required schema field, a
  new entry in a gate's preflight list. Every call site that exercises the
  contract breaks, and the failure is loud: the authoritative gate catches it.
- **Relaxing an enforcement for one mode** — a lane that demotes a required
  measurement, a documented exemption, a compatibility window. The relaxation is
  itself a contract member and must reach every site that enforces the underlying
  check. A relaxation implemented at N−1 of N sites **reads as implemented
  everywhere**, because the ordinary mode exercises all sites identically and only
  the demoted mode's rare path reaches the unguarded one.

The discipline is the same for both: grep the contract's **distinctive tokens** —
the command name, a neighboring flag, the executable list, the check's own name —
across the whole tree rather than the contract's own file or the policy's name,
and treat every hit file as an independent inventory to update in the same change.

The gate catching a miss is the backstop working as designed, but each round-trip
costs a full gate run and the sweep is cheap by comparison. The cost is concrete:
adding `bin/treatise` to `bin/check`'s required-executable preflight and policy
lane broke fourteen `test_check.py` cases across four independent inventories
**inside one file** — in a session where the same lesson had been re-filed hours
earlier.

## Relationship to acceptance

[`acceptance-empirical.md`](acceptance-empirical.md) defines what makes a gate
capable of failing and how to avoid vacuous green results. This policy governs
the evidentiary step before and around those gates: inspect actual matches,
state coverage limits, validate detector direction, and make counts
reproducible.
