---
slug: magenta-ferret
title: A policy's own Verification block is not subject to the verification rules the policy corpus states
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-08-25
source: sweep
occurrences:
  - date: 2026-08-25
    ref: "sweep (policies) — policies/repo-relative-paths.md § Verification shipped a grep that could never print its own declared clean result: it matched the policy's own text, the CLAUDE.md catalog line describing it, the code-critic checklist quoting it, the dashboard sanitizer's regex, and two tests asserting absence. Fifteen hits on a repo that was actually clean. The policy asserted 'a clean repo prints no absolute paths found'"
  - date: 2026-08-25
    ref: "sweep (policies) — policies/phase-ripple.md § Verification shipped two greps matching '- AUTO ' and '- DECIDE ' with a trailing space, while kickoff's END-block template writes '- AUTO:' and '- DECIDE:' with a colon. One branch could never fire; the other printed 'no DECIDE ripples this close (clean)' on every run regardless of truth. Never once told the truth since it was written"
---

`policies/acceptance-empirical.md` states the rule at length: a check earns trust
only if it can report the failure it claims to guard against, and an instrument
whose output space has one reachable member carries no information.
`policies/verification-discipline.md` adds that a detector must never key solely on
a token the subject itself legitimately emits.

Both defects were found in **the policy corpus's own Verification blocks**, in the
same pass, in opposite directions — one instrument stuck at "bad", one stuck at
"good". Neither had ever produced a true result. Nothing in the repository looks at
those blocks: `./bin/check all` runs the real checkers under `bin/`, and a fenced
shell block inside a Markdown policy is prose to every gate the repo owns.

The generator worth naming: a Verification section is written at the moment the
policy is written, when the author is reasoning about the rule rather than about
the corpus, and it is then never executed again by anyone. It reads as enforcement
and is documentation, and its rot is invisible because nothing runs it. The two
found here had drifted in the ordinary way — one because the corpus grew around a
token, one because the END-block template gained a colon — and both drifts were
mechanical enough that a runner would have caught them the day they happened.

Why this is a `bin` candidate rather than a prose rule: it is mechanically
decidable. A checker can extract every fenced shell block under `policies/` that
declares an expected clean output, run it in the repo, and refuse when the observed
output does not match the declared one. The narrower and cheaper version — refuse a
block whose only reachable branch is its fallback — catches the always-green shape
alone. A written reminder to "check your verification blocks" is the rule wired to
nothing that [`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md)
warns against.

Counting note: two occurrences, deliberately filed as two rows. They are one
sweep's findings but two independent instruments in two policies failing in
opposite directions, which is exactly the shape
[`policies/lessons.md`](../policies/lessons.md) § "One row per instance" says must
not be batched.

Both instruments were deleted in the sweep that found them; the graduation question
is whether the *class* earns a guard, not whether these two are fixed.
