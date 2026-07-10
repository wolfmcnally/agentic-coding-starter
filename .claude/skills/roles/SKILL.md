---
name: roles
description: >-
  Pin a model/harness to any of the four canonical /kickoff roles (planner,
  reviewer, coder, critic), scoped by which harness is orchestrating, or show
  the current pins. Updates the role_models section of the repo's kickoff.yaml
  while preserving human comments and other sections, so the orchestrator
  invokes each role on the resolved model. Orchestration and build gates always
  stay on the current session's model. Invoke as /roles (show), /roles
  [<harness>] <role>: <model> [effort <level>], ... (set), or /roles reset (restore
  defaults).
argument-hint: "[<harness>] <role>: <model> [effort <level>], ... | reset"
allowed-tools: Bash
---

# /roles — Pin models/harnesses to the four canonical roles

Set which model/harness `/kickoff` uses for each of its four roles, scoped by
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
  - `sol`, `terra`, `luna` — `codex --model gpt-5.6-sol|terra|luna`.
- **Reasoning effort:** set a separate `effort` field to `low`, `medium`, `high`,
  or `xhigh` when a Codex- or Claude-routed role needs an explicit effort. Claude
  additionally accepts `max`. Omit the field to preserve the model's
  configured/default effort. Effort is rejected for `default` because
  `/roles` cannot control the orchestrator's native session effort. `max` is
  Claude-only; `Ultra` is a product execution mode rather than a role-pin effort.

Resolution for a role under harness `H`: `H`'s section, else the `default`
section, else native. The shipped default routes reviewer + critic to the *other*
harness (cross-vendor review) and leaves planner + coder native.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- **Empty** → show current pins + the resolved view for this harness: run `./bin/kickoff-config show models`.
- **`reset`** (or `--reset`) → restore only the shipped model defaults: run `./bin/kickoff-config reset models`. Timeout calibration and data under `extensions` remain untouched.
- **One or more role assignments**, optionally preceded by a **harness token** (`default`/`claude`/`codex`) → translate to field-path assignments and run `./bin/kickoff-config set-models <harness> <role>.model=<model> [<role>.effort=<effort>] ...`. With no harness token, use `default`. Use `<role>.effort=default` to remove an explicit effort field.

If the request is vague or uses a synonym (e.g. "when I'm on Codex, review with opus at high effort", "put the coder on the big model"), resolve it to concrete harness/role/model/effort fields using the vocabulary above, state the mapping you chose, then run the manager. That interpretation is the only judgment this skill makes. If genuinely ambiguous, ask rather than guess.

## Run

Invoke the script with the resolved arguments, e.g.:

```
./bin/kickoff-config set-models codex reviewer.model=opus critic.model=opus
```

An explicit GPT-5.6 configuration uses the code names directly:

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

> These take effect on the next `/kickoff`. Its fail-closed preflight aborts before phase mutation if a required external CLI, authentication path, or model is unavailable; a later runtime failure falls back with a 🚨 in the `/kickoff` summary.

Do **not** commit the change — the user owns commits ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)).

## Notes

- The config file is `kickoff.yaml` at the repo root and is deliberately human-editable. `/roles` is a convenient validated editor for its `role_models` section, not its owner.
- `/roles` is universal — carried into every project `/stamp` derives; every derived project has the same four roles and the same cross-vendor-review default.
- The default `claude:`/`codex:` sections are what provide out-of-the-box cross-vendor review. Editing or clearing them changes the review venue; there is no separate on/off switch.
