# Policy: Per-Role Model Pinning (harness-aware)

Each canonical `/kickoff` role may select a model and optional reasoning effort, scoped by which harness is orchestrating. The model determines the delegated CLI; `{model: default}` runs natively. Orchestration and build gates always stay on the current session model.

## Human-editable configuration

Model routing lives under `role_models` in the repo-root [`kickoff.yaml`](../kickoff.yaml). The file is deliberately human-editable. Model and effort are separate fields:

```yaml
role_models:
  default:
    planner:
      model: default
    reviewer:
      model: default
    coder:
      model: default
    critic:
      model: default
  claude:
    reviewer:
      model: codex
    critic:
      model: codex
  codex:
    reviewer:
      model: opus
      effort: high
    critic:
      model: opus
      effort: high
```

- **Harness sections:** `default` is the base layer; `claude` and `codex` override it when that harness orchestrates.
- **Roles:** `planner`, `reviewer`, `coder`, `critic` map to the four canonical agent definitions.
- **Models:** `default`, `claude`, `codex`, `opus`, `fable`, `sol`, `terra`, `luna`.
- **Effort:** optional `low`, `medium`, `high`, or `xhigh`; Claude-routed models additionally accept `max`. Effort is invalid with `model: default`.

`default` means native. `claude` uses the Claude CLI's configured model; `opus` and `fable` add their Claude model flag. `codex` uses the Codex CLI's configured model; `sol`, `terra`, and `luna` map to `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`. A non-default model always uses its implied CLI even when it matches the orchestrator's vendor.

The routing and timeout schemas are strict: unknown harnesses, roles, or fields fail validation so direct-edit typos cannot disappear silently. Project-specific data belongs under top-level `extensions`, where arbitrary keys are preserved and ignored by the current resolver. Invalid configuration fails before any command runs or write occurs.

## Manager and direct edits

`bin/kickoff-config` validates the complete document and owns mechanistic operations:

- `show models` resolves the current harness;
- `set-models` updates only `role_models`;
- `reset models` resets only model routing;
- `preflight` validates live external venues.

It uses round-trip YAML parsing, preserves comments, ordering, quoting, and data under `extensions`, and atomically replaces the file only after full validation. `/roles` is its thin natural-language wrapper. Direct human edits are equally supported and take effect after `show models` validates them.

## Resolution (kickoff Step 0a)

Resolve once per session. `CLAUDECODE=1` means Claude orchestrates; otherwise Codex does.

1. If `KICKOFF_DELEGATION_DEPTH` is set, every role runs native and no child delegates again.
2. For role `R`, use `role_models[H][R]`, else `role_models.default[R]`, else `{model: default}`.
3. Map the model to its implied CLI and add the separate effort field to the CLI invocation.
4. Preserve the resolved `(venue, model, effort)` for every round and the END block.

Planner, reviewer, and critic remain read-only; the coder remains write-enabled.

## Mandatory live preflight (kickoff Step 0b)

Before phase identification, decomposition, status mutation, log writes, or agent invocation, `/kickoff` runs:

```bash
./bin/kickoff-config preflight
```

The manager groups unique non-native `(CLI, model, effort, access mode)` targets and makes one live sentinel call per group. It uses production credential scrubs, model/effort flags, stdin closure, approval posture, and read-only/write-enabled access in an empty temporary directory. Success requires the exact `KICKOFF_PREFLIGHT_OK` result within 120 seconds.

Preflight is fail-closed. A missing CLI, unusable authentication, unavailable model, network or sandbox error, flag incompatibility, timeout, malformed response, or wrong sentinel aborts `/kickoff` before phase state exists. There is no native fallback for an upstream prerequisite failure.

## Invocation, resume, and fallback

Production commands and auth traps live in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md). Every external call runs through `bin/kickoff-config watch` under [`role-timeouts.md`](role-timeouts.md). Roles resume the same external session across revision rounds, repeating both model and effort flags.

A delegated call succeeds only when all three hold:

1. its output artifact exists and is non-empty;
2. it has the role's required output shape or exact verdict header; and
3. it stayed inside its first-event, idle-progress, and hard deadlines.

After successful preflight, a non-zero exit, timeout, network failure, missing artifact, or malformed output makes the rest of that stage native and produces a 🚨 disconnect. A Claude review that exhausts its turn cap may resume once only to emit its verdict. Fallback is per stage; once a stage falls back, it does not venue-thrash.

## END-block reporting

Every END block records the preflight result, orchestrating harness, and each role's resolved model, effort, venue, and fallback status. It also carries the timing summary required by [`role-timeouts.md`](role-timeouts.md). Any post-preflight difference between configured and actual venue is repeated as a 🚨 in the user-facing summary.

## Propagation

`kickoff.yaml`, `bin/kickoff-config`, `/roles`, this policy, the timeout policy, and the invocation brief are one universal configuration/execution bundle. `/stamp` carries it. `/teach` upgrades its schema and mechanics while preserving target values, comments, `extensions` data, and telemetry. `/learn` may absorb general mechanics but not donor operational state.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) owns role names, semantics, tool stances, verdicts, and convergence limits.
- [`role-timeouts.md`](role-timeouts.md) owns execution budgets, process-group termination, telemetry, and recalibration.
- [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md) puts validation and editing in `bin/kickoff-config`; model-choice judgment stays with the human or `/roles` interpretation.
- [`human-in-the-loop.md`](human-in-the-loop.md) still governs completion and commits.
