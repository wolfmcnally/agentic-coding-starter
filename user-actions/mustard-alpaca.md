---
slug: mustard-alpaca
title: Decide whether the role watcher should refuse a role write to its own output file
status: open
filed: 2026-09-05
blocks: none
---

## What needs deciding

A role's report path is also the file the external venue writes its last message to. A role that writes its report there during its turn has it destroyed by the terminal summary. As of 2026-09-05 the only control is an instruction, now stated in the governing policy and in all four role definitions.

The open question is whether the watcher should additionally refuse such a write — detecting a role write to the required-output path before turn end and either blocking it or dispatching to a distinct path.

## Why it is yours

It is unscoped code in the path every role dispatch runs through. During the graduation review on 2026-09-05 the operator chose to ship the instruction now and scope the machinery change separately rather than fold it into a lessons graduation.

## What the instruction does not cover

Three donor-project sightings in two weeks each destroyed a complete handoff report, one of 10.7 KB. All three were caught only because the orchestrator had read the report minutes earlier. Read after turn completion instead, the loss is silent and the change evidence is unrecoverable. An instruction fails exactly when a role does not follow it, which is what happened three times; a refusal would not depend on compliance.

## Dependencies

None. The instruction is in force regardless of the outcome.
