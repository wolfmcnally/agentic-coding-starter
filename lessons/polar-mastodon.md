---
slug: polar-mastodon
title: Record diagnostic observations after execution without inventing another run
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-09-06
source: user
occurrences:
  - date: 2026-09-06
    ref: "Balanced Codex design comparison — a gate required a warning count before execution, then two environment warnings required correction and imported corrections inflated a draft execution count"
  - date: 2026-09-06
    ref: "Quality Codex design comparison — the same premature zero-warning claim recurred and required a separate correction"
---

Keep an execution and the later assessment of its diagnostics separate. An API that requires a warning count before starting the command demands information the caller cannot yet possess. Treating a later correction as another gate record then changes execution counts without another execution having happened.

The operator-approved repair records a managed execution with an unknown count, then binds a diagnostic review to its exact record hash. Acceptance requires the review. Explicitly linked corrections preserve history without increasing execution or timing totals. The diagnostic assessment remains a judgment based on complete output; the tool does not pretend a generic warning-word detector can establish whether a gate is clean.
