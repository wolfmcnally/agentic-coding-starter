---
name: roles
description: >-
  Pin a model/harness to any of the four canonical /kickoff roles (planner,
  reviewer, coder, critic), or show the current pins. Writes the repo's
  role-models.yaml config so the orchestrator invokes each pinned role on that
  model. Orchestration and build gates always stay on the current session's
  model. Invoke as /roles (show current), /roles <role>: <model>, ... (set),
  or /roles reset (clear all).
argument-hint: "[<role>: <model>, ...] | reset"
allowed-tools: Bash
---

# /roles — Pin models/harnesses to the four canonical roles

Set which model/harness `/kickoff` uses for each of its four roles. This is a
thin wrapper over the deterministic `bin/role-models` script — the parse,
validate, and write is mechanical (per [`policies/mechanistic-vs-intelligence.md`](../../../policies/mechanistic-vs-intelligence.md)), so this skill only translates the request and echoes the result. The rules the orchestrator obeys live in [`policies/role-models.md`](../../../policies/role-models.md).

## Vocabulary

- **Roles:** `planner` → `phase-planner`, `reviewer` → `plan-reviewer`, `coder` → `phase-coder`, `critic` → `code-critic`.
- **Models:**
  - `default` — native: the current `/kickoff` session's model (the current, unpinned behavior).
  - `opus`, `fable` — Claude Code harness (`claude --model opus|fable`).
  - `codex` — Codex harness (`codex`, its default/latest model).

Setting a role to `default` clears its pin. Roles you don't name keep their
current value. Unknown roles or models are rejected and the config is left
untouched.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- **Empty** → show the current pins: run `./bin/role-models --show`.
- **`reset`** (or `--reset`) → clear every pin: run `./bin/role-models --reset`.
- **One or more `<role>: <model>` pairs** (comma-separated) → set them: pass the
  arguments straight through to `./bin/role-models`. The script tolerates the
  shell splitting the pairs — it rejoins and re-parses — so
  `./bin/role-models <args>` is safe.

If the request is vague or uses a synonym (e.g. "make the reviewers use codex",
"put the coder on the big model"), resolve it to concrete `role: model` pairs
using the vocabulary above, state the mapping you chose, then run the script.
That interpretation is the only judgment this skill makes; everything else is
the script's deterministic job. If a synonym is genuinely ambiguous, ask rather
than guess.

## Run

Invoke the script with the resolved arguments, e.g.:

```
./bin/role-models planner: fable, reviewer: codex, coder: opus, critic: fable
```

The script validates every pair, rewrites `role-models.yaml`, and prints the
resulting four-role state. A non-zero exit means nothing was written — surface
its error message verbatim and do not retry with the same bad value.

## Report

Echo the script's final four-line state so the user sees what is now pinned.
When any role is pinned to a non-`default` model, add a one-line reminder:

> These pins take effect on the next `/kickoff`. A pinned role whose harness CLI
> is unavailable (or whose call fails) falls back to the session model, and
> `/kickoff` flags that disconnect with 🚨 in its summary.

Do **not** commit the change — the user owns commits ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)).

## Notes

- The config file is `role-models.yaml` at the repo root, fully owned by the script.
  Prefer `/roles` over hand-editing it.
- `/roles` is universal — it is carried into every project `/stamp` derives, and
  every derived project has the same four roles to pin.
- Pinning a **reviewer** or **critic** role overrides the `cross-harness-review:`
  token for that role. Pinning a **planner** or **coder** is what lets those
  roles — which otherwise always run native — execute on another model/harness.
