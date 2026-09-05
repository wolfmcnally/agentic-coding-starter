---
slug: strategic-jaguarundi
title: Report headroom against a hard ceiling, not just compliance with it
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-09-05
source: user
occurrences:
  - date: 2026-09-05
    ref: "Instruction-delivery work left CLAUDE.md at 16376 bytes against the 16384-byte gate ceiling — 8 bytes of headroom, so the next cataloged policy or brief breaks the gate with no warning beforehand"
---

A ceiling check answers one question: are we over it. That answer is identical at 8 bytes remaining and at 8000, and only one of those is a healthy state. The condition that actually predicts trouble — how close the next ordinary edit will push us — is invisible to a pass/fail gate, so it is discovered by a failing build rather than by a maintainer.

The cost is concentrated where the ceiling interacts with a mandatory catalog: every brief and policy must be indexed in the root instructions, so adding either one is a required edit to the file that is nearly full. The gate then fails on an unrelated change, and whoever hits it is trimming prose under deadline pressure — which is exactly when an obligation gets deleted to make room.

**A gate that enforces a budget should report the remaining margin on every run, and should warn well before the margin reaches zero.** Compliance is the pass condition; headroom is the number a maintainer needs. Emitting it costs nothing and converts a surprise failure into a scheduled cleanup.

The general form: whenever a check compares a measurement to a fixed limit, print the measurement. A verification that only says "good" tells you less than the number it already computed.
