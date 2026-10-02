---
slug: traditional-prawn
title: The stamp denylist is kept by hand, so template-local content added later travels or dangles
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-10-01
source: user
occurrences:
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — a universal policy links to a brief the denylist leaves behind, so the copied policy carried a link the catalog check reports as broken until the sentence was removed by hand"
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — a fixture directory that implements that same template-local brief is on no list, so it copied and then had to be found and removed"
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the template's own dated phase report directory and its root execution log are mentioned nowhere in the skill; the agent removed them and regenerated the report index for an empty archive"
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the governance report README is described as the report contract only, but it carries the template's own dated results, which had to be replaced"
---

`stamp` copies every universal surface whole and leaves behind what a denylist names. The skill defends that direction on the ground that a forgotten entry "copies one harmless extra file" while a forgotten allowlist entry breaks the destination's gate. Four omissions in one stamp show the extra file is not reliably harmless.

Two of them broke something. `policies/role-models.md` is universal and links to `briefs/astra-era-development.md`, which the denylist excludes, so the destination's catalog check fails on a link to a file it was told not to receive. `tests/fixtures/astra_evaluation/` implements that same brief and links to it, and is not on the list at all. The other two were silent: `reports/execution/2026-09-05/` and `EXECUTION_LOG.jsonl` are the template's own execution history, and `reports/test-governance/README.md` carries the template's dated results under a description that says it is only the contract. A destination that kept them would present another repository's history as its own.

Each was added to the template after the denylist was written, by a change that had no reason to open the stamp skill. The list is the only thing that knows which content is template-local, and nothing fails when it falls behind.

What should be done differently: the classification of template-local content needs an executable witness. The cheapest candidate is a test that performs the skill's mechanical copy into a temporary directory and runs the destination's catalog check there, so a universal file that links to an excluded one fails in the template's own gate on the day the link is written. A declared inventory of template-local paths that the gate checks for completeness, the way `candidate-partition.yaml` is checked, would cover the silent cases the link check cannot see.
