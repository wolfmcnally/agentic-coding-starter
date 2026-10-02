# Test-governance reports

This directory records the recipient's own proof-estate reset. The frozen
pre-reset baseline is immutable. The append-only reset ledger dispositions every
baseline proof and records admissions, repairs and retirements. Replaying the
ledger must reproduce the live inventory exactly; a missing event, repeated
retirement, or shadow proof fails validation. The effectiveness report is the
observed result of the frozen historical and held-out corpora; misses remain
visible, each observation binds the exact mutation-patch digest and carries the date it
was measured. Recall is reported as of the oldest observation; patches stranded
by later edits are repaired or retired at the next sweep's assay. Per-test timings are machine-local and live in the
ignored `.kickoff/test-timing/` record, never here.

These files are evidence, not portable judgments. A stamped, taught, or learning
recipient regenerates them from its own estate and never copies survivors,
selectors, corpora, timings, risk applicability, or dispositions.

The executable authority is:

```bash
./bin/test-governance validate
./bin/test-governance report
./bin/test-governance reassess
```

`assay` reruns corpus patches in disposable copies. Run it at every governed sweep. Routine vital and
changed lanes never replace the full handoff gate.

`assay` preserves symlinks in each disposable copy and requires each case command to pass on that copy before applying the frozen mutation. A failing baseline stops measurement instead of increasing recall. The effectiveness rows report the subsequent mutated command outcomes; inspect their full diagnostics to distinguish intended detections from unrelated failures. A stored report is the most recent assay observation, not something `validate` or either full close gate regenerates. The frozen reset summary remains a historical snapshot; use `reassess` for current totals and recall.

Run long assays from a frozen disposable source snapshot.
