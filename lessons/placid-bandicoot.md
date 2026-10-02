---
slug: placid-bandicoot
title: The format gate's claim to skip ignored files rests on formatter behavior that is not stable
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-10-01
source: user
occurrences:
  - date: 2026-10-01
    ref: "writing the template's format-failure proof, 2026-10-01 — the same formatter command over the same two directories checked a git-ignored file in about half of some thirty runs and skipped it in the rest"
---

The build-gate contract says format checking covers staged, unstaged and nonignored untracked candidate files. The gate gets "nonignored" for free from the formatter, which reads the repository's ignore rules while it walks the directories it is given.

That exclusion is not deterministic. With the pinned formatter (ruff 0.15.13), two directory arguments, and an ignore rule anchored to a path, an ignored file was checked on some runs and skipped on others, from the repository root and from a subdirectory alike. With one directory argument it was skipped every time. The cause inside the formatter was not established.

The direction of the error is over-inclusion: an ignored file is sometimes checked, never the reverse, so no candidate escapes the gate. The cost is a full gate that can fail intermittently on a file the repository has declared out of scope, which reads as a flaky gate and invites a rerun instead of a diagnosis. The template has no ignored Python file under the directories the gate names, so it has not bitten here.

The proof written the same day asserts the three candidate states and deliberately does not assert the ignored case, because an assertion that passes half the time is worse than none.

What should be done differently: a property the gate claims but inherits from a tool needs its own check or its own wording. Either the gate passes the formatter an explicit candidate list it computed itself, or the contract stops promising the exclusion.
