# Test-governance reports

This directory records the recipient's own proof-estate reset. The frozen
pre-reset baseline is immutable. The append-only reset ledger dispositions every
baseline proof and records admissions, repairs and retirements. Replaying the
ledger must reproduce the live inventory exactly; a missing event, repeated
retirement, or shadow proof fails validation. The witness ledger holds one receipt per
observed red witness: the proofs, the named defect, the command, the text its failure
had to contain, the files the defect was planted in, digests of the planted bytes and of
the failing output, and the date. Receipts are appended only by
`./bin/test-governance witness finish`; no planted defect is stored. Per-test timings are machine-local and live in the
ignored `.kickoff/test-timing/` record, never here.

These files are evidence, not portable judgments. A stamped, taught, or learning
recipient regenerates them from its own estate and never copies survivors,
selectors, witness receipts, timings, risk applicability, or dispositions.

The executable authority is:

```bash
./bin/test-governance validate
./bin/test-governance report
./bin/test-governance reassess
```

Routine vital and changed lanes never replace the full handoff gate. The frozen reset summary remains a historical snapshot; use `reassess` for current totals and for the count of proofs that still have no receipt.

A witness plants its defect in the live tree. While one is pending, `validate` refuses, so neither the commit hook nor the full gate can pass a planted defect; `./bin/test-governance witness abort` restores an interrupted run. To witness a proof of the governance manager itself, run the command from an untouched copy of the manager with `--root` pointing here, so the planted defect cannot change how the observation is made.
