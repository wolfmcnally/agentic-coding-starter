---
slug: warping-albatross
title: A staged rename lists its path under --name-only while the index still holds the pre-edit bytes
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-09-21
source: sweep
occurrences:
  - date: 2026-09-21
    ref: "Sweep delivery — six lessons were moved with git mv, then edited; the add named only the modified files, --name-only listed all eighteen paths, and the pushed commit carried the six moved files at their pre-edit content. The pushed tree would fail ./bin/lessons validate; the working tree was correct throughout, so every gate passed"
---

`git mv` stages a rename immediately. Edits made to the moved file afterward are ordinary unstaged modifications, and naming that path in a later `git add` is forbidden by the rule that prevents the atomic-abort defect — so the correct-looking delivery stages only the *other* paths and never picks the content up.

The instruments then agree with each other and with the intent. `git diff --cached --name-only` lists the path, because a staged rename is a staged change. `git show --stat HEAD` lists it too. The intended file list matches exactly. The only surfaces that disagree are `git diff --cached --stat`, which shows the insertion count, and `git status` after the commit, which still reports the path as modified.

Two things this exposes beyond the staging rule itself. **The build gate cannot see it**: `./bin/check all` validates the working tree, which was correct the whole time, so a repository whose *pushed* tree fails its own validator passes every gate. And **the verification ran too late**: commit, push and `git status` were one block, so the residual-modification rows printed after the push had already happened.

**The rule candidate, beyond the clauses already added to `policies/commit-staging.md`:** when a delivery includes a rename, the staged-content read is mandatory rather than advisory, and the post-commit clean-tree check belongs before the push in its own block. Consider whether the delivery step should assert a clean `git status` for every path the commit claims, since that assertion is cheap, mechanical, and is the one surface that was telling the truth.
