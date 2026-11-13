---
title: Compare a transfer's own-lines report with indentation stripped
scope: methodology
proposed_surface: skill
source: teach
slug: liberal-pig
status: candidate
filed: '2026-11-13'
occurrences:
- date: '2026-11-13'
  ref: a recipient's 1.6.0 transfer; the worker's first audit of merged files against
    the ancestry report's recipient-own lines reported every indented line as missing
---

The ancestry report lists a recipient's own lines with leading whitespace removed. An audit that compares them to the merged file's raw lines reports every indented line as lost. The worker caught it; two earlier workers had used whitespace-normalized comparison without being told to.

Candidate correction: say in the teach skill, where the two-way audit is described, that the comparison is on stripped lines, or have the report state it in its own output.