---
slug: fortunate-shoebill
title: Wholesale donor-file copies can silently revert destination-ahead hunks
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-10
source: learn
occurrences:
  - date: 2026-08-10
    ref: "LEARN from Donor A — porting a shared behavioral test file"
---

When `learn` or `teach` absorbs a donor's version of a file both repos share, the efficient move is a wholesale copy followed by targeted re-edits. The hazard: the destination may itself be ahead of the donor on some hunks — its own advances landed after the repos last synced — and a wholesale copy silently reverts them. Nothing fails; the destination just quietly loses work it already ratified.

Observed while porting a shared behavioral test file: the donor's copy was ahead on roughly thirty hunks (a new fixture parameter, call-site updates, six new tests), but one test in the destination's copy carried richer assertions the donor lacked, from an advance the destination made independently. A blind copy would have dropped those assertions while every test still passed — the regression would have been invisible to the gate.

The generalizable discipline: before replacing a shared file with the donor's version, diff the two and classify every hunk by direction. Donor-ahead hunks transfer; destination-ahead hunks are re-applied on top of the copy (or the copy is abandoned for hunk-level edits). "The donor is ahead on this file" is a claim about specific hunks, never about the whole file.

## Evidence

- The 2026-08-10 `learn` pass found exactly one destination-ahead hunk inside an otherwise donor-ahead file; it was restored after the copy in the same apply step.
- The failure mode is silent by construction: reverting a stronger assertion to a weaker one cannot fail any test.
