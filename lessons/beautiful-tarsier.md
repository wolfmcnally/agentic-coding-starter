---
slug: beautiful-tarsier
title: An instrument whose production firings are all comparator false positives is measuring its model, not the work
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-11
source: learn
occurrences:
  - date: 2026-08-11
    ref: "LEARN from Donor A — donor-ledger methodology lesson harvested during the assessment pass"
---

A binding strictness instrument in a donor project fired repeatedly in
production, and every firing was a false positive: every recorded fix was to
the comparator (baseline-invisible paths, normalization mismatches,
byte-identical staging treated as change), never to the guarded work. The
firing *history* is itself a detectable smell: when an instrument's cumulative
production record is comparator repairs with zero caught defects, the
instrument is measuring the fidelity of its own world-model, and its expected
value is negative — each firing costs a remediation cycle and finds nothing.

The candidate rule, if a second instrument shows the same shape: track
fired→real-defect vs fired→comparator-fix outcomes per binding instrument, and
treat an all-comparator record over N firings as an automatic demotion trigger
(binding → advisory) rather than waiting for an operator-directed audit.
`policies/acceptance-empirical.md` already names the *static* version of this
defect (a false-red comparison against a moving reference); this is the
longitudinal version, detectable only from the instrument's outcome record
over time. One family observed so far — filed, not codified.
