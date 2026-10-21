---
slug: ingenious-parakeet
title: A branch only some invocations need lives in a linked resource
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-10-21
source: user
occurrences:
  - date: 2026-10-21
    ref: "LOG.md 2026-10-21 11:34 METHODOLOGY — stamp interview when invoked without arguments; a no-argument interview branch was added inline to the always-loaded stamp SKILL.md, and the operator asked why it entered context on every invocation"
---

The no-argument interview was added to `stamp` as an inline section of `SKILL.md`, a file already past 500 lines. Every stamp invocation with a directory argument then loaded roughly thirty lines it would never execute. The operator asked whether the skill had been refactored so the interview loads only when needed. It had not.

The pattern was already established in this template: `kickoff` keeps each stage in an adjacent resource, links it directly from the entry, and orders it read before its branch runs. `policies/cross-harness-parity.md` states that load-before-use contract for kickoff's resources only, though, so nothing generalized it to other skills. The primary did not consult general skill-authoring guidance before editing a skill either. Directory-level mirrors already expose adjacent resources to Codex, so the shape costs nothing in parity.

**The rule candidate:** when a skill gains a branch that only some invocations take — a mode chosen by arguments, a recovery path, an optional interview — put the branch in an adjacent resource file one link from `SKILL.md`, and give the entry an explicit instruction to read that file before executing the branch. Keep the always-loaded entry to routing, obligations and the common path. Generalize the kickoff load-before-use rule to every canonical skill rather than restating it per skill.
