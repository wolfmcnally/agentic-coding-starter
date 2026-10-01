---
slug: lively-gerbil
title: Size an instruction surface by running the bare model first; published failures of older models are not evidence about the current one
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-10-01
source: user
occurrences:
  - date: 2026-10-01
    ref: "METHODOLOGY — universal refactor skill: the first plan prescribed per-step verification from studies of older models until the operator asked that it not be over-built for the current ones"
---

The first plan for the `refactor` skill prescribed a baseline proof, a verification order for every step, a step ledger and a closing re-read of the diff. Each item traced to a published study in which a model refactoring without such a loop broke behavior. Every one of those studies measured models older than the four this repository names, or models that could not run anything. The operator asked that the skill not be over-built for current models, and to verify that independently.

Verification reversed the design. Both vendors' current prompting guides say verification instructions written for earlier models should be removed because they cause over-verification, and that skills should be audited for instructions that distort behavior. Run on a seeded package with no skill at all, all four models preserved behavior, avoided every trap and decoy, and verified their own work unasked. What they got wrong was not technique: one deleted a public module on its own authority, and two stopped after the most visible problems. The shipped skill states scope, authority and delivery, and nothing about how to refactor.

What should be done differently: before writing or extending a skill or role definition, read the vendors' current guidance for the models that will run it and run the bare model on a representative task. Admit an instruction only when it is a repository fact the model cannot know, a boundary of scope or authority, or the answer to a failure that baseline showed. A citation that an earlier model failed is a reason to test, not a reason to instruct. The same test applies in reverse when a model is replaced: an instruction the new model no longer needs is a cost and should be removed.
