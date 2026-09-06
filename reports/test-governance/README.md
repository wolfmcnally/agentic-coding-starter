# Test-governance reports

This directory records the recipient's own proof-estate reset. The frozen
pre-reset baseline is immutable. The append-only reset ledger dispositions every
baseline proof and records compensated admissions. After the reset, the same
ledger replays each physical retirement before the admission that consumes its
one-for-one budget; a missing target, reused retirement, unspent exchange, or
shadow proof in the active inventory fails validation. The effectiveness report is
the observed result of the frozen historical and held-out corpora; misses remain
visible, and each observation binds the exact mutation-patch digest. The current
inventory and reset summary make both 20% ceilings and both 80% floors
reproducible.

These files are evidence, not portable judgments. A stamped, taught, or learning
recipient regenerates them from its own estate and never copies survivors,
selectors, corpora, timings, risk applicability, or dispositions.

The executable authority is:

```bash
./bin/test-governance validate
./bin/test-governance report
./bin/test-governance reassess
```

`assay` reruns corpus patches in disposable copies. Run it whenever proof code,
selection, corpus, or critical-risk applicability changes. Routine vital and
changed lanes never replace the full retained close gate.

As of 2026-09-05, `assay` preserves symlinks in each disposable copy and requires each case command to pass on that copy before applying the frozen mutation. A failing baseline stops measurement instead of increasing recall. The effectiveness rows report the subsequent mutated command outcomes; inspect their full diagnostics to distinguish intended detections from unrelated failures. A stored report is the most recent assay observation, not something `validate` or either full close gate regenerates. The frozen reset summary remains a historical snapshot; use `reassess` for current totals and recall.
