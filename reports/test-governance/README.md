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

As of 2026-09-05, `assay` preserves symlinks in each disposable copy and requires each case command to pass on that copy before applying the frozen mutation. A failing baseline stops measurement instead of increasing recall. The effectiveness rows report the subsequent mutated command outcomes; inspect their full diagnostics to distinguish intended detections from unrelated failures. A stored report is the most recent assay observation, not something `validate` or either full close gate regenerates. The frozen reset summary remains a historical snapshot; use `reassess` for current totals and recall.

As of 2026-09-05, readiness qualification detects 12/12 historical defects and 11/12 held-out mutations, with the original corpus and thresholds unchanged. The preflight inventory and receipt-candidate cases are now detected by strengthened existing proofs. `vital-substitutes-for-full` remains a recorded miss: its frozen command runs the governance-manager tests rather than the modified full-gate entry point. A separate disposable control ran `tests/test_check.py::test_all_is_default_locked_ordered_and_cwd_independent`: the unmodified command passed, and the frozen mutation failed its ordered-call assertion because it selected the vital lane instead of the full test estate. This diagnoses the corpus command's scope; it does not credit the frozen assay with an extra detection.

Run long assays from a frozen disposable source snapshot. Review corrections made while an earlier live-tree assay was running required replacing that preliminary evidence; the final report was generated from the independently reviewed code snapshot. Qualification also exercised major, child and nested final-child acceptance, exact ledger application, repeated closes, tampered records, and actual fast-forward delivery to seeded disposable remotes. An isolated product gate and a root-level lifecycle fixture cover both product layouts; recipient-local delivery tests separately qualified preservation of a recipient's stronger delivery identity. These are local workflow checks, not live-model performance measurements or completed teaching passes.

As of 2026-09-29, the count caps and one-for-one growth budget were replaced by per-family size ceilings and a test-lane time budget (`policies/test-suite-governance.md` § Time budget). The two holdout mutants that seeded defects into the removed count cap were retired from the corpus and replaced by two that seed defects into the time budget (`single-run-confirms-overrun`, `foreign-machine-budget-judged`); four others were re-anchored to the same defects after manager edits moved their context lines, two of them already stranded by the previous commit. The assay was then rerun from the live tree with no edits during the run.
