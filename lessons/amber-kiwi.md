---
slug: amber-kiwi
title: The route check refuses a committed but undeclared cutover before it reads the provenance record
status: candidate
scope: methodology
proposed_surface: skill
filed: '2026-11-12'
source: user
occurrences:
- date: '2026-11-12'
  ref: two recipients migrating the same day — each cutover was committed with adoption left for the operator to declare, and the route check then refused the project as an unresolved transition without reporting provenance, so the skill's step of confirming that the check reads the new record could not run; both workers confirmed it with the check's own reader and on a scratch copy with adoption declared
---

Leaving adoption undeclared until the operator has seen the constitution load is the recommended sequence, so the skill's confirmation step must work in that state. Either the route check reports provenance for an undeclared cutover, or the skill names the scratch-copy confirmation as the step.
