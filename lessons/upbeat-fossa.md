---
slug: upbeat-fossa
title: Assess a target's product prerequisites before applying a transfer, not at its gate
status: candidate
scope: methodology
proposed_surface: skill
filed: '2026-11-11'
source: user
occurrences:
- date: '2026-11-11'
  ref: a recipient during a batch transfer — the transfer was fully applied and its methodology checks passed before the full test run revealed that the product suite needed an external executable the worker's session did not have; the applied change then sat uncommitted until the operator supplied the selection
---

A transfer ends in the target's full gate, so anything that gate needs from outside the tree is a precondition of the transfer. Stage 1 should run or inspect the target's gate prerequisites and surface a missing one in the plan, where it can be settled before anything is written.
