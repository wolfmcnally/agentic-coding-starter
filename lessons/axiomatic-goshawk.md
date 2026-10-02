---
slug: axiomatic-goshawk
title: A policy gate that reads the committed log cannot pass before the first commit
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-10-01
source: user
occurrences:
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the log check refused with a message that it could not read the committed log because the new repository had no commit yet, so the full gate could not be green before the initial commit it is meant to qualify"
---

`bin/check-log` proves the log is append-only by comparing the working file against the committed one. In a repository with no commit it refuses: `LOG-PREFIX REFUSED cannot read committed LOG.md`, exit 1. That is reproducible by extracting the template's tree into an empty directory, running `git init`, and running the check.

The stamp skill orders the initial commit in Step 6 and the full gate in Step 7, so an agent following it exactly commits first and never sees the refusal. The order a careful agent would choose, prove the tree and then commit it, fails. So does an initial commit in a checkout that has opted into the tracked hooks, because the pre-commit hook runs the same check against the same absence.

The refusal is the right behavior for a repository with history: an unreadable committed log must not read as an empty one. It is the wrong behavior for the one state where no committed log can exist. The check cannot currently tell "there is no HEAD" from "HEAD exists and the log could not be read".

What should be done differently: the check should distinguish an unborn branch from a failed read, and treat the first as an empty committed prefix. More generally, a gate that compares against committed state needs a defined answer for the state before any commit, and the bootstrap's acceptance should exercise the gate in that state at least once.
