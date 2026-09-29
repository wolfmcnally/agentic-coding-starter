---
slug: garrulous-armadillo
title: Editing proof-manager code can silently strand line-anchored frozen mutants; the gate never checked that they still apply
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-09-29
source: learn
occurrences:
  - date: 2026-09-29
    ref: "Starter — a four-line edit to the test-governance manager (adding a repair disposition) changed context lines that two frozen holdout mutants anchor on; the commit passed both full gates and was pushed with an effectiveness report describing mutations that could no longer be applied"
---

The effectiveness corpus stores each mutant as a unified diff anchored on source lines. Validation bound each patch's bytes to the corpus by digest and bound the report to the corpus, but never asked whether the patch still applied to the code. The policy asks for the assay to be rerun when proof code changes, but only a governed sweep enforced that, so a phase or methodology edit to the very code the mutants seed defects into could leave the recorded recall describing code that no longer exists, with every gate green.

It surfaced one change later, when a larger edit to the same manager broke three more patches and a manual `git apply --check` loop found the first two already stale at the previous commit.

Containment: the two stale patches were re-anchored to the same defects and the assay was rerun. Prevention applied in the same change, as an executable guard rather than a rule: validation now runs `git apply --check` on every corpus patch and names each one that no longer applies, so the full gate refuses the stale state. Proved by tripping it on the five stale patches before any were repaired.

Open for ratification: whether a patch that no longer applies should also require the assay rerun within the same change (today the guard forces re-anchoring, and re-anchoring changes the patch digest, which forces a report update, which in practice forces the rerun, but the chain is indirect).

The guard's first version inverted its own evidence. It refused any patch that did not apply forward, but inside an assay copy the mutant is already applied, so every mutant whose command ran the governance tests was "detected" by the guard itself rather than by a proof: holdout recall read 12/12, including a case the corpus has recorded as a miss since the reset. The tell was a known miss turning into a detection with no change to the proof that should catch it. The shipped guard accepts a patch that applies forward or in reverse, and its admitted proof checks both directions. A check added to the code the assay mutates has to be read as a potential detector in every assay copy, not only against the live tree.
