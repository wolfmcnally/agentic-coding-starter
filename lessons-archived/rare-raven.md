---
slug: rare-raven
title: A search hit dismissed without reading its matched text is a sweep that looked and did not see
status: codified
scope: methodology
proposed_surface: policy
filed: 2026-09-29
closed: 2026-09-29
graduated_to: policies/verification-discipline.md
source: user
occurrences:
  - date: 2026-09-29
    ref: "Starter — migrating the gate wording, a grep for the stale phrase returned the shared brief preamble on nine files; the hits were read as unrelated because the visible prefix was a generic paragraph, and about fifteen stale statements survived until the same day's sweep audit"
---

A search is only a sweep of the hits someone actually reads. While updating every statement of the two-full-gates rule, the search returned a match on a paragraph repeated across nine briefs and a skill. The printed lines were truncated to their opening words, which were a generic statement about the primary use case, and the matching phrase sat past the cut. The hits were judged unrelated from the prefix and dropped. The migration was reported complete, and the same day's sweep audit found the stale phrase in all of them, plus several other stale statements the narrower search pattern never covered.

Two separable failures: printing matches truncated so the matched text itself is not shown, and dismissing a hit without locating why it matched. The cheap correction is mechanical: print only the matched span with a little context (`grep -o '.{0,60}PATTERN.{0,60}'`), so every line shown is the evidence, and treat an unexplained hit as unresolved rather than irrelevant.

Closed 2026-09-29 by the operator in the lessons sweep as already covered: `policies/verification-discipline.md` states this lesson's remedy. No new rule was written.
