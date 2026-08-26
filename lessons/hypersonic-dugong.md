---
slug: hypersonic-dugong
title: Test which guard fired when guards share an error taxonomy
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-24
    ref: "Donor A — implementation and test agreed on an error family while exercising the wrong pre-parser guard"
  - date: 2026-08-25
    ref: "Donor A — a malformed-input control passed through an already-covered selection guard until the test pinned the intended parse refusal"
---

When two validation guards can emit the same error family, asserting only the
reported kind is a noisy proxy for the intended control flow. A test and an
implementation can mutually ratify the wrong guard.

Tests for precedence should observe the intended guard directly, exercise the
generic validator separately, and prove downstream parsing or effects remain
unreachable. The taxonomy matters, but does not identify its speaker.
