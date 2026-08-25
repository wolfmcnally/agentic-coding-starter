---
slug: rugged-gharial
title: A guard patched at the site the reviewer named will regrow at the next site; convert the class or it recurs
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-12
    ref: "Donor A — one code finding recurred four times at four different sites, then burned the phase's whole convergence lease and parked it"
  - date: 2026-08-12
    ref: "Donor A — a separate run, two findings, same shape: each regrew four times as the reviewer named one site after another"
---

The finding said one thing throughout: a fail-closed probe must distinguish "I
could not read" from "there is nothing there." It was closed and reopened four
times — an absent journal, then an empty journal over a populated store, then a
false positive on benign sidecar files, then a suppressed directory scan — and the
critic reopened it once more on the one traversal deliberately left alone. **Each
round the coder did exactly what was asked, and each fix was correct.** The phase
parked anyway.

**The generator was never the site.** The language's recursive-glob helpers
silently drop the contents of an unreadable directory, so *every* traversal in the
module had the defect; the reviewer could only ever name the instance it happened
to look at. Two independent sweeps each missed a different instance while working
from a list. When the last round finally asked for a **rule** — "every traversal in
these modules yields complete data or raises" — instead of a site, the coder's own
audit found eleven traversals, including ones neither sweep had considered because
both were grepping for the other helper's name.

**The generalizable shape.** When a finding reopens twice at different sites with
the same failure sentence, the finding is naming a **class**, and the remaining
cycles will be spent enumerating its members. The cheap move is to stop routing
"fix this site" and route instead: *state the invariant, apply it everywhere in the
touched surface, and report an audit of every site marked converted or
sound-and-why.* The expensive move is to trust that the reviewer's list is the
population.

Candidate rule: **a second reopening of one finding id at a new site is an
automatic trigger to re-scope that finding from site to invariant**, before
spending another cycle. Distinct from the stall and recurrence tests in
[`policies/four-canonical-agents.md`](../policies/four-canonical-agents.md) §
Revision loops, which say *escalate to the human* — this says *change the
instruction shape first*, because the loop was converging on symptoms the whole
time.

Kin to `fractal-beetle` (a mode-conditional relaxation must reach every
enforcement site) — there the class is enumerated by the fix's own scope; here the
class is discovered only when the instruction stops naming sites.
