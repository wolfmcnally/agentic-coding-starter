---
slug: strategic-magpie
title: Scope command-arity exceptions to the mode that needs them
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-08-27
source: learn
occurrences:
  - date: 2026-08-27
    ref: "Learn application — adding one two-argument check mode relaxed the global argument ceiling and made an existing one-argument mode accept ignored input"
---

A command with several one-argument modes gained one mode that accepts a
reference as its second argument. Raising the parser's global maximum made the
new form possible, but also made every old mode accept an extra argument it
silently ignored. The executable still ran the requested gate and returned
success, so the regression looked harmless unless the old negative invocation
test was retained.

When one command mode needs a different arity, validate argument count inside
each dispatch branch. Do not widen a global ceiling and assume the branches
will reject what they do not consume. Preserve negative tests for every older
mode while adding the new mode's valid and invalid forms.
