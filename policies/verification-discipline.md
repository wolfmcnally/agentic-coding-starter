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

## A name you did not read is not a name

An identifier that follows the naming conventions of a real one is evidence of
nothing. Convention-consistency is the mechanism that generates a plausible
wrong name, not a defense against it: the model that infers `--recursive` from
every other CLI it has seen is using exactly the machinery that would have
produced the flag had it existed.

Before citing any function, method, class, flag, environment variable,
configuration key, endpoint, package, schema field, or command in code, a plan,
a brief, a report, or a message, either read it from the authority that defines
it — the source file, `--help`, the schema, the documentation page — or mark it
unverified and say which. "I inferred this from naming conventions" is a
complete and acceptable answer; presenting it as read is not.

The check is cheap and the failure is not. One grep, one `--help`, one open
documentation tab settles it, while an unread name reaches a reviewer wearing
the same confidence as a verified one and is indistinguishable until it runs.
Reach for this hardest exactly where the surrounding work looks most finished:
a fluent, correctly-structured, idiomatically-named artifact is where a
fabricated reference is least visible.

Two corollaries:

- **The authority is the definition, not another mention.** A name recovered
  from your own earlier summary, a sibling file's usage, or a plausible
  neighbor's docs is still unread. Read where it is defined.
- **Absence of a match is a finding, not a formatting problem.** When the grep
  comes back empty or `--help` does not list the flag, that is the answer.
  Do not widen the pattern until something matches.

## Never reason over output you truncated yourself

A view you narrowed is not the thing you narrowed it from. When output is passed
through `head`, `tail`, `sed -n`, a line cap, or any other cut, the cut is part of
the instrument, and a conclusion drawn from the remainder is scoped to the
remainder. State the cut in the same breath as the conclusion, and re-read the
output whole before any claim that depends on what might have been outside it.

This is distinct from the pipe-status defect in
[`acceptance-empirical.md`](acceptance-empirical.md) § "A check must be able to
fail". There the exit status is lost and the command's own verdict disappears.
Here the status is fine and the *content* is missing, so nothing about the run
looks wrong — which is why the same reader can commit it twice.

Motivating incidents, cited per the doctrine's growth rule (donor project,
2026-08-16 and 2026-08-20): a field read as whole after the reader's own `sed` cut
it, with the cut falling exactly where two candidates diverge; a gate battery piped
through `tail -6`, removing the gate's own verdict from what the reader then
reasoned over; and four days later a process listing cut by the reader's own
`head -5`, from which the orchestrator concluded that all surviving processes were
the operator's editor and no cleanup was needed — two of its own probe processes
had been running the whole time. The third was committed by a reader who had cited
the first earlier that same day, which is the argument for stating this at its
class rather than at any one command.

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
