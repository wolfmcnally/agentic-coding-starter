---
slug: pistachio-dove
title: Decide the starting effort for GPT-6.1 Sol
status: pending
category: decision
urgency: low
blocks:
  - none
filed: 2026-10-01
needed_at: now
source: methodology
refs:
  - briefs/astra-era-development.md
  - docs/openai-codex-model-selection.md
  - policies/role-models.md
---

## What needs deciding

Whether Sol should keep starting at `medium` now that the `sol` selector resolves to GPT-6.1 Sol.

## What is true today

Sol starts at `medium`, both as the guidance for a Codex primary and as the preset pin for delegated roles. That start was adopted on 2026-09-23 because OpenAI then recommended Medium for GPT-6 Sol.

## Why it came up

OpenAI's guidance for GPT-6.1 Sol no longer names a level. It says to start at the reasoning effort the client offers by default. On 2026-10-01 the Codex CLI's own model list gave `low` as that default for GPT-6.1 Sol, where GPT-6 Sol's was `medium`. Following the vendor literally would lower Sol's start to `low`.

## What each answer costs

Keeping `medium` spends more time and tokens per turn than the vendor's default and may buy nothing. Moving to `low` follows the vendor but lowers the reasoning given to the Codex primary's planning and coding on evidence this repository has not gathered. Either is reversible by one configuration change. An effort sweep on real phase work would settle it; none has been run.

## Dependencies

None. `medium` stays in force until this is decided.
