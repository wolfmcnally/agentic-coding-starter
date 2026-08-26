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
  - date: 2026-08-23
    ref: "Donor A — a donor-base probe ran in the recipient's object database instead of naming the source repository explicitly, making an existing commit appear absent"
  - date: 2026-08-24
    ref: "Donor A — two verification probes inherited a run-artifact directory and failed as not-a-repository before being rerun against the repository explicitly"
  - date: 2026-08-26
    ref: "Learn application — an absolute path selected a candidate manager executable but not the cwd-rooted repository it measured, yielding a plausible identity for the wrong tree"
---

Verification built on the shell's inherited cwd fails invisibly, because
almost every directory of interest on an operator's machine is inside *some*
repository: a `git log` or `git status` run after an earlier `cd` returns a
plausible, well-formed answer about the wrong repo instead of an error.

The discipline: every verification-grade git command names its target
explicitly — `git -C <repo-path> …` — regardless of where the shell believes
it is. Apply the same rule to repository managers whose executable path and
target repository are independent: set or verify their working directory
explicitly. A wrong-repo answer is worse than a failed command: it survives
review, reads as evidence, and points every downstream conclusion at the wrong
tree.
