---
slug: talkative-magpie
title: A per-test time ceiling fails the full gate when other work loads the machine
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-10-03
source: learn
occurrences:
  - date: 2026-10-01
    ref: "Donor A — a full gate for a one-file bookkeeping change failed its test-time check while other sessions loaded the machine: the suite took 200 seconds against 104 to 132 earlier that evening, and one leaf measured 2.10 seconds against a two-second ceiling"
  - date: 2026-10-01
    ref: "teaching pass from this template to a derived project — its full gate ran beside another project's heavy gate; the suite took 241 seconds against 125 alone, two leaves crossed their ceilings at 20.35 against 20 and 2.44 against 2, and the same commit passed when rerun on a quiet machine"
---

The size rule gives each pytest family the smallest class whose ceiling is at least twice its slowest leaf, so that ordinary noise cannot cross it, and fails a leaf over its ceiling on any machine from a single run. A machine shared with other suites roughly doubles every timing, which is the whole margin the rule allows. The failure then reports truthfully what was measured and says nothing about the change under test.

Both sightings had the same shape: the total suite time was about double its recent unloaded value, every leaf that crossed did so by a small fraction, and a rerun on a quiet machine passed. In the second the load was the agent's own doing, two full gates scheduled at once.

What should be done differently: the single-run ceiling needs a way to tell a slow proof from a slow machine, for example confirming over the median of three runs as the lane budget already does, or judging a leaf against the same run's overall slowdown. Until then, a ceiling failure on a change that cannot affect timing is diagnosed by comparing the suite's total with recent runs, and the gate is rerun when the machine is quiet; neither the ceiling nor the family's size is changed to make it pass. Full gates in different repositories are not scheduled to run at the same time.
