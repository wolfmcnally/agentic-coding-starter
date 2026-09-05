---
name: roles
description: >-
  Pin a model/harness to any of the four canonical kickoff roles (planner,
  reviewer, coder, critic), scoped by which harness is orchestrating, or show
  the current pins. Updates the role_models section of the repo's kickoff.yaml
  while preserving human comments and other sections, so the orchestrator
  invokes each role on the resolved model. Orchestration and build gates always
  stay on the current session's model. Invoke as /roles in Claude Code or
  $roles in Codex; arguments show, set, reset, or apply a preset to the pins.
argument-hint: "[<harness>] <role>: <model> [effort <level>], ... | preset <quality|balanced|economy> [same-harness|cross-vendor] | reset"
allowed-tools: Bash
last-reviewed: 2026-08-10
---

# Roles — Pin models/harnesses to the four canonical roles

Set which model/harness the `kickoff` skill uses for each of its four roles, scoped by
which harness is orchestrating. This is a thin wrapper over the deterministic
`bin/kickoff-config` manager — the parse, validate, round-trip-safe section update, and atomic write are mechanical (per
[`policies/mechanistic-vs-intelligence.md`](../../../policies/mechanistic-vs-intelligence.md)), so this skill only translates the request and echoes the result. The rules the orchestrator obeys live in [`policies/role-models.md`](../../../policies/role-models.md).

## Vocabulary

- **Harness sections** (which harness is orchestrating): `default` (base layer, applies under every harness), `claude`, `codex`.
- **Roles:** `planner` → `phase-planner`, `reviewer` → `plan-reviewer`, `coder` → `phase-coder`, `critic` → `code-critic`.
- **Models:**
  - `default` — native: the orchestrator's own session model (no CLI).
  - `claude` — `claude` CLI, its configured default model.
  - `codex` — `codex` CLI, its configured default model.
  - `opus`, `fable` — `claude --model opus|fable`.
  - `astra` — `codex --model gpt-6-astra`.
  - `sol`, `terra`, `luna` — `codex --model gpt-5.6-sol|terra|luna`.
- **Reasoning effort:** a separate optional field, validated against the selector-specific supported subset in [`policies/role-models.md`](../../../policies/role-models.md#human-editable-configuration). Native `default` rejects explicit effort; `ultra` is not enabled. Omission retains configured effort.

Resolution for a role under harness `H`: `H`'s section, else the `default` section, else native. The shipped/reset preset is quality/same-harness. The authoritative matrix and cross-vendor selection are in [`policies/role-models.md`](../../../policies/role-models.md#independent-review-and-portable-presets).

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- **Empty** → show current pins + the resolved view for this harness: run `./bin/kickoff-config show models`.
- **`reset`** (or `--reset`) → restore only the shipped model defaults: run `./bin/kickoff-config reset models`. Timeout calibration and data under `extensions` remain untouched.
- **Preset request** (`quality`, `balanced`, or `economy`, optionally prefixed by `preset`) → run `./bin/kickoff-config apply-preset <name> [--review same-harness|cross-vendor]`. Omitted review mode is same-harness. Explain that this replaces all role pins in both concrete harness sections, retaining the base layer, other sections and comments; it makes no model call.
- **One or more role assignments**, optionally preceded by a **harness token** (`default`/`claude`/`codex`) → translate to field-path assignments and run `./bin/kickoff-config set-models <harness> <role>.model=<model> [<role>.effort=<effort>] ...`. With no harness token, use `default`. Use `<role>.effort=default` to remove an explicit effort field.

If the request is vague or uses a synonym (e.g. "when I'm on Codex, review with opus at high effort", "put the coder on the big model"), resolve it to concrete harness/role/model/effort fields using the vocabulary above, state the mapping you chose, then run the manager. That interpretation is the only judgment this skill makes. If genuinely ambiguous, ask rather than guess.

## Run

Invoke the script with the resolved arguments, e.g.:

```
./bin/kickoff-config set-models codex reviewer.model=opus critic.model=opus
```

Preset examples:

```
./bin/kickoff-config apply-preset balanced
./bin/kickoff-config apply-preset quality --review cross-vendor
```

Explicit model selections use code names directly:

```
./bin/kickoff-config set-models claude reviewer.model=sol reviewer.effort=medium critic.model=terra critic.effort=low
```

Claude Code models use the same separate-field grammar:

```
./bin/kickoff-config set-models codex reviewer.model=opus reviewer.effort=high critic.model=fable critic.effort=max
```

The manager validates the complete document, updates only `role_models`, preserves
comments, ordering, quoting, and data under `extensions`, then
atomically replaces the file and prints the resolved view. A non-zero exit means nothing was written — surface
its error message verbatim and do not retry with the same bad value.

## Report

Echo the script's output so the user sees the config and the resolved view.
When any role resolves to a non-`default` model, add a one-line reminder:

> These take effect on the next `kickoff`. Its fail-closed preflight aborts before phase mutation if a required external CLI, authentication path, or model is unavailable; a later runtime failure preserves evidence and follows governed recovery without silently changing model or effort. If a model is unavailable, select an available preset or explicit pins before restarting.

Once `./bin/kickoff-config show` validates the edited configuration, commit that one file by explicit path and non-force-push it ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)). The change is small, mechanically validated, and exactly what the user asked for; park delivery and report instead if validation fails, if `git status` shows a path this skill did not touch, or if the upstream is missing or ambiguous.

## Notes

- The config file is `kickoff.yaml` at the repo root and is deliberately human-editable. `roles` is a convenient validated editor for its `role_models` section, not its owner.
- `roles` is universal — carried into every project `stamp` derives; every derived project has the same four roles and the same portable quality/same-harness default.
- Presets are an editor operation over `claude:`/`codex:` role pins, not a second runtime setting. Existing target pins remain authoritative until explicitly edited.
