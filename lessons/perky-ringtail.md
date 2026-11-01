---
slug: perky-ringtail
title: The non-Python profile leaves three Python-deliverable couplings unnamed
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-10-31
source: user
occurrences:
  - date: 2026-10-31
    ref: "a stamp of a TypeScript project — the catalog link surfaced as a gate failure; the other two were found by reading the template and a prior recipient"
---

The stamp's two-runtime section covers setup, test routing and split gates. Three members it does not name also assume the Python deliverable:

- `collect_pytest` in `lib/agentic_starter/test_governance.py` passes `project/tests` to collection, a directory that holds no pytest proofs in a non-Python deliverable. The fixture in `tests/test_test_governance.py` plants its proof in the same place, so removing the argument without moving the fixture fails six tests.
- `bin/README.md` links `manual/src/documentation.md`, a chapter of the template's own manual that a recipient does not receive, so `bin/check-catalogs` fails on the catalog rather than on the omission.
- `bin/mutate` needs a wrapper once `lib/agentic_starter/mutation.py` is removed as the procedure instructs. The removal is stated; what prints the `unmeasured` document afterward is not.

A previously stamped TypeScript recipient had already made the first change independently, which suggests the fix belongs upstream. **Make the governance collection root and its fixture read the deliverable's profile, ship a language-neutral `unmeasured` path behind `bin/mutate`, and move the manual link out of the copied catalog.**
