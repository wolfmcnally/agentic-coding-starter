---
name: roles
description: >-
  Pin a model/harness to any of the four canonical /kickoff roles (planner,
  reviewer, coder, critic), scoped by which harness is orchestrating, or show
  the current pins. Writes the repo's role-models.yaml so the orchestrator
  invokes each role on the resolved model. Orchestration and build gates always
  stay on the current session's model. Invoke as /roles (show), /roles
  [<harness>] <role>: <model>, ... (set), or /roles reset (restore defaults).
argument-hint: "[<harness>] <role>: <model>, ... | reset"
allowed-tools: Bash
---

# /roles — Pin models/harnesses to the four canonical roles

Set which model/harness `/kickoff` uses for each of its four roles, scoped by
which harness is orchestrating. This is a thin wrapper over the deterministic
`bin/role-models` script — the parse, validate, and write is mechanical (per
[`policies/mechanistic-vs-intelligence.md`](../../../policies/mechanistic-vs-intelligence.md)), so this skill only translates the request and echoes the result. The rules the orchestrator obeys live in [`policies/role-models.md`](../../../policies/role-models.md).

## Vocabulary

- **Harness sections** (which harness is orchestrating): `default` (base layer, applies under every harness), `claude`, `codex`.
- **Roles:** `planner` → `phase-planner`, `reviewer` → `plan-reviewer`, `coder` → `phase-coder`, `critic` → `code-critic`.
- **Models:**
  - `default` — native: the orchestrator's own session model (no CLI).
  - `claude` — `claude` CLI, its configured default model.
  - `codex` — `codex` CLI, its configured default model.
  - `opus`, `fable` — `claude --model opus|fable`.

Resolution for a role under harness `H`: `H`'s section, else the `default`
section, else native. The shipped default routes reviewer + critic to the *other*
harness (cross-vendor review) and leaves planner + coder native.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- **Empty** → show current pins + the resolved view for this harness: run `./bin/role-models --show`.
- **`reset`** (or `--reset`) → restore the shipped default: run `./bin/role-models --reset`.
- **One or more `<role>: <model>` pairs**, optionally preceded by a **harness token** (`default`/`claude`/`codex`) → pass the arguments straight through: `./bin/role-models <args>`. With no harness token the pins land in the `default` section. The script tolerates the shell splitting the pairs — it rejoins and re-parses.

If the request is vague or uses a synonym (e.g. "when I'm on Codex, review with opus", "put the coder on the big model"), resolve it to concrete `[harness] role: model` pairs using the vocabulary above, state the mapping you chose, then run the script. That interpretation is the only judgment this skill makes. If genuinely ambiguous, ask rather than guess.

## Run

Invoke the script with the resolved arguments, e.g.:

```
./bin/role-models codex reviewer: opus, critic: opus
```

The script validates every pair, rewrites `role-models.yaml` (preserving the
sections you did not touch), and prints the resulting config plus the resolved
view for the current harness. A non-zero exit means nothing was written — surface
its error message verbatim and do not retry with the same bad value.

## Report

Echo the script's output so the user sees the config and the resolved view.
When any role resolves to a non-`default` model, add a one-line reminder:

> These take effect on the next `/kickoff`. A role whose harness CLI is not
> installed falls back to the session model with a quiet note; a role whose CLI
> was reachable but whose call fails falls back with a 🚨 in the `/kickoff` summary.

Do **not** commit the change — the user owns commits ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)).

## Notes

- The config file is `role-models.yaml` at the repo root, fully owned by the script. Prefer `/roles` over hand-editing it.
- `/roles` is universal — carried into every project `/stamp` derives; every derived project has the same four roles and the same cross-vendor-review default.
- The default `claude:`/`codex:` sections are what provide out-of-the-box cross-vendor review. Editing or clearing them changes the review venue; there is no separate on/off switch.
