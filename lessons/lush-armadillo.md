---
slug: lush-armadillo
title: The bootstrap brief still describes the retired constitution and log layout
status: candidate
scope: methodology
proposed_surface: brief
filed: 2026-10-31
source: user
occurrences:
  - date: 2026-10-31
    ref: "a stamp read briefs/agentic-bootstrap.md and the stamp skill side by side as the contract they claim to be"
---

`briefs/agentic-bootstrap.md` calls itself the contract the stamp implements, and parts of it contradict the current template. Its layout tree shows `AGENTS.md` as a symlink to itself and a root `LOG.md`; its pitfalls warn against `AGENTS.md` being a real file, while Step 4 of the same brief requires exactly that. Its layout omits `log/` and `collaboration/`, and it still lists `plan/phase-1.md` and the old status legend. The same mechanical rename left `bin/multioperator` repeated up to five times in one sentence, in both the brief and the skill, and the skill's thesis-stub still points at `../CLAUDE.md#project-briefs`.

The executable checks pass because they do not read these passages, so the drift is invisible until someone follows the prose. The skill wins in practice, and an agent that trusts the brief would build a retired layout. **Rewrite the brief's layout, pitfalls and legend against the live tree, and collapse the repeated script lists, in one change.**
