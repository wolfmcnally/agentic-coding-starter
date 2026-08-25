---
slug: ochre-polecat
title: Staging from `git status` is `git add -A` by another route — the working tree is shared state, not a record of your own work
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-19
    ref: "Donor A — a supervisor announced a concurrent operator-directed write to five phase files and asked the orchestrator to verify disjointness against its own work. The orchestrator ran `git status --short`, saw the five files dirty, and reported them as 'my uncommitted plan files'. They were the supervisor's in-flight writes, and went clean when that session committed moments later"
  - date: 2026-08-19
    ref: "Donor A — the latent defect that misread exposed. An earlier phase's commit had been staged by enumerating `git status --short` into a path list and passing it to `git add`: functionally identical to `git add -A` whenever another session has anything dirty, reached by a route that reads as explicit-path staging and satisfies a reviewer looking for one. It bundled nothing only because no concurrent write happened to be in flight"
---

The explicit-path staging rule exists because a shared working tree will silently
bundle another session's in-flight files into your commit under your message.
`git add -A` is the named way to violate it. **Enumerating `git status` into a
path list is the unnamed way, and it is more dangerous, because the resulting
command *looks* like compliance**: a list of literal paths, each one real, each
one dirty, passed individually to `git add`.

The defect is in the direction of the derivation. `git status` answers "what is
dirty in this tree" — a question about the tree. A commit needs the answer to
"what did this phase change" — a question about the work. The two coincide exactly
when you are the only writer, which is the condition the rule already assumes is
false.

The same misread produces the reporting error: dirty files get narrated as "my
changes" because the enumeration that found them cannot say whose they are. That
is how a disjointness check ran against the wrong set and still returned an
answer.

**Remedy.** Build a commit's path list from the phase's **own declared write
set** — the plan's file-changes section plus the coder's reports — and then
*intersect* it with `git status`. Never take `git status` as the source. Anything
dirty and not accounted for by the phase belongs to another session: exclude it
and report it, rather than assuming it is stale cruft. The intersection also
catches the opposite error — a declared file that never got written — which
enumeration alone cannot see.

This is now load-bearing rather than advisory: `kickoff` stages and commits the
phase itself ([`policies/human-in-the-loop.md`](../policies/human-in-the-loop.md)),
and that policy's first delivery park is an unexpected path in `git status`. The
park is only as good as the set it compares against.

Kin: `puzzling-unicorn` (a `git add` naming a moved path stages nothing, and
`git status` still lists every file). Same instrument, second independent
blindness — there the failure is "you staged nothing and could not tell"; here it
is "you staged someone else's work."
