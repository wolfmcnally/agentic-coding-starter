---
slug: merciful-cicada
title: Verification git commands address the repo explicitly with -C, never the shell's inherited cwd
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-11
    ref: "Donor A supervision — a git log intended to verify the supervised repository silently read a different repository twice in one night, because a prior cd in the same shell had left the cwd inside another git repo; the query returned a plausible, well-formed, wrong answer"
---

Verification built on the shell's inherited cwd fails invisibly, because
almost every directory of interest on an operator's machine is inside *some*
repository: a `git log` or `git status` run after an earlier `cd` returns a
plausible, well-formed answer about the wrong repo instead of an error.

The discipline: every verification-grade git command names its target
explicitly — `git -C <repo-path> …` — regardless of where the shell believes
it is. A wrong-repo answer is worse than a failed command: it survives review,
reads as evidence, and points every downstream conclusion at the wrong tree.
