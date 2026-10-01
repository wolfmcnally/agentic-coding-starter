---
slug: keen-crocodile
title: When an instruction does not take, read the model's stated reason before writing the next one
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-10-01
source: user
occurrences:
  - date: 2026-10-01
    ref: "METHODOLOGY — refactor skill wording: a sentence about the amount of work was written against a model whose logged reason was about overridable methods, and changed nothing"
---

One model kept proposing a change the other three applied. Its session log gave the reason in one line: hoisting the call changes how often an overridable method is called. The sentence written to move it said that the amount of work a function does is not something a caller observes. That answers an objection the model never made, and across two more runs its reading did not change.

The operator asked whether a more specific prompt would work. A sentence aimed at the stated reason — judge what can be observed by the callers, subclasses and overrides that exist, not by ones that could be written — moved the model on the next run, with no regression in the other three.

What should be done differently: before revising a skill or role instruction because a model did not follow it, read that model's own account of why in the session record, and write the revision against that account. An instruction that addresses the author's guess at the reason costs a run and leaves a sentence behind that does nothing.
