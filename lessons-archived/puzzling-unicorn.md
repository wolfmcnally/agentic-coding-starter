---
slug: puzzling-unicorn
title: A `git add` naming one path that no longer exists stages NOTHING, and `git status` still lists every file
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — a nine-path `git add` included one file whose deletion `git mv` had already staged; git aborted and staged none of the other eight. Loud: the fatal printed and was caught immediately"
  - date: 2026-08-21
    ref: "Donor A — the silent direction. A five-path `git add` named ledger files `git mv` had already moved. The add aborted, the commit captured only the pre-staged renames — 19 insertions instead of ~127 — and the missing content was reported as landed. `git status --porcelain` had been read as confirmation, but every content row's index column was a space"
---

`git add` is **atomic over its pathspec list**: one path that matches nothing
aborts the entire invocation and stages none of the others. That is correct
behavior. The defect is what it composes with.

**`git status --porcelain` lists a file whether it is staged or not.** The
difference is one character — the index column. ` M policies/lessons.md` (leading
space) is worktree-only; `M  policies/lessons.md` is staged. Scanning that output
for "are my files there?" answers *yes* in both cases, so the check that feels
like verification is blind to the thing that went wrong.

The two directions differ in cost, and only one is dangerous:

- **Loud** — the pathspec no longer exists on disk. Git prints `fatal: pathspec …
  did not match any files` and the failure is unmissable.
- **Silent** — a `git mv` earlier in the same session already moved the path. Git
  prints the same fatal, but inside a longer block whose output scrolls, or with
  attention on the status listing that follows, the abort reads as a no-op. The
  commit then succeeds, is *smaller than intended*, and is reported as landed. **A
  commit that silently omits most of its content is worse than one that fails**,
  because it ships and is believed.

The mitigation is not "be careful with pathspecs." It is to stop verifying stages
and commits with an instrument that cannot distinguish them:

- **Verify staging by the index, not the file list.** `git diff --cached
  --name-only` lists exactly what will be committed and nothing else. If reading
  `git status --porcelain`, read the **first column**, not the filename.
- **Verify a commit by its own content.** `git show --stat HEAD` is what the
  commit actually captured; a file count or insertion count far below expectation
  is visible at a glance, before the push.
- **Never name a path in `git add` that another command moved or deleted in the
  same session.** `git mv` and `git rm` stage their own halves; re-naming them is
  not merely redundant, it is what triggers the abort.

This matters more here now that `kickoff` delivers accepted phases itself
([`policies/human-in-the-loop.md`](../policies/human-in-the-loop.md)): the
delivery step stages explicit paths, and archiving a `user-actions/` or
`lessons/` file with `git mv` during the same close is exactly the setup for the
silent direction.
