# Policy: Per-Role Model Pinning (harness-aware)

Each of the four canonical roles ([`four-canonical-agents.md`](four-canonical-agents.md)) — planner, reviewer, coder, critic — may be **pinned to a model and optional reasoning effort**, and the pin is **scoped by which harness is orchestrating** `/kickoff`. The model code name implies its CLI. When a role resolves to a pin, `/kickoff` invokes that CLI with the resolved model and effort, using the invocation recipes in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md). When it resolves to `default`, the role runs native. **Orchestration and build gates — the `/kickoff` main loop itself — always run on the current session's model and are never pinnable.**

This is the single mechanism for choosing where any role runs. The harness-keyed structure expresses harness-*relative* routing ("when Claude Code orchestrates, review in Codex; when Codex orchestrates, review in Claude"), which is why the shipped default reproduces cross-vendor review out of the box for the two reviewer roles.

## Why pin at all

Review decorrelation is the headline reason: a critic on a different model family from the coder catches failure classes a same-family critic shares blind spots on, and that value *grows* as coding models get stronger — whatever a frontier coder still gets wrong is exactly what its own family is least able to see. But pinning is broader: a project may want a cheaper/faster model for mechanical planning, the strongest model for implementation, or a specific vendor for a role for any reason. The template ships safe defaults (cross-vendor review) and provides the mechanism; it does not prescribe which pins are wise.

## The config file

Pins live in **`role-models.yaml` at the repo root**, owned by `bin/role-models` and set through the `/roles` skill. It is a **two-level YAML mapping** — top-level *harness sections*, each mapping *role → model*:

```yaml
default:            # base layer — applies under every harness
  planner: default
  reviewer: default
  coder: default
  critic: default
claude:             # overrides when Claude Code orchestrates
  reviewer: codex
  critic: codex
codex:              # overrides when Codex orchestrates
  reviewer: opus
  critic: opus
```

An explicit GPT-5.6 pin uses the model's code name; the optional effort suffix
travels with the pin:

```yaml
claude:
  reviewer: sol@medium
  critic: terra@low
```

- **Harness sections:** `default` (a base layer applied under every harness), `claude`, `codex`. A section names *who is orchestrating* — not where the role runs.
- **Roles:** `planner` → `phase-planner`, `reviewer` → `plan-reviewer`, `coder` → `phase-coder`, `critic` → `code-critic`.
- **Models (the vocabulary):**
  - `default` — native: the orchestrator's own session model. No CLI call.
  - `claude` — the `claude` CLI, its configured default model (no `--model`).
  - `codex` — the `codex` CLI, its configured default model (no `-m`).
  - `opus`, `fable` — the `claude` CLI, a specific model (`claude --model opus|fable`; full ids `claude-opus-4-8` / `claude-fable-5` if an alias is unrecognized).
  - `sol`, `terra`, `luna` — the `codex` CLI with the corresponding GPT-5.6
    model (`codex --model gpt-5.6-sol|terra|luna`). The code name is the
    user-facing pin; the deterministic resolver owns the versioned CLI slug.
- **Reasoning effort suffix:** a Codex-routed value may append `@low`,
  `@medium`, `@high`, or `@xhigh` (for example `sol@medium` or `codex@high`).
  A Claude-routed value accepts those four plus `@max` (for example
  `opus@high`, `fable@max`, or `claude@medium`) and passes the value through
  Claude Code's `--effort` flag. Omission preserves the CLI/model's configured
  or default effort. The suffix is invalid only on `default`, because this
  mechanism cannot override the orchestrator's native session effort. `max` is
  Claude-only in this headless grammar; `Ultra` remains a product execution
  mode rather than a per-role effort.

The **model value determines the CLI**, independent of who orchestrates.
`default` → native subagent; Claude-family code names → the Claude CLI recipe;
GPT-family code names → the Codex CLI recipe; bare `claude` / `codex` values
select that CLI's configured default model. There is deliberately no "the pin
equals the session model, so skip the CLI" short-circuit — a non-`default`
value always goes through the CLI recipe (uniform, no fragile session-model
probing). Putting a bare harness value in its own section (e.g. `claude:` →
`reviewer: claude`) is pointless same-harness routing — use `default` for
native; it is documented, not special-cased.

The vocabulary is closed: `bin/role-models` rejects any harness, role, model,
effort, or invalid model/effort combination outside these sets non-zero and
leaves the file unchanged. Extending it is a deliberate, lockstep edit to
`bin/role-models`, this policy, and the `/roles` skill.

The file is a dedicated machine-owned surface — *not* a token in `CLAUDE.md` Project Context — because a script rewrites it repeatedly and it must not disturb the human-authored prose zone `/stamp` rewrites.

## Mechanistic/intelligence seam

Per [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md), the parse-validate-write is **mechanistic** and lives in `bin/role-models` (a Python + PyYAML script, run via `uv` with PEP 723 inline deps — deterministic, idempotent, harness-portable, testable, doing a robust two-level read-modify-write that preserves untouched sections). The `/roles` skill is the thin intelligence wrapper: it resolves a possibly-vague request ("put the coder on the big model") into concrete `[harness] role: model[@effort]` pairs, then shells out to the script. No model does the writing.

## Resolution (kickoff Step 0a)

Resolved **once per session**, before phase work. Detect the orchestrating harness `H`: `CLAUDECODE=1` in the environment → `claude`; otherwise → `codex`.

1. **Recursion guard.** If `KICKOFF_DELEGATION_DEPTH` is set, this session is *itself* a delegated role invoked by an outer `/kickoff`; **every role runs native** and no further delegation happens. Skip the rest.
2. **Merge, per role `R`:** `effective(R) = config[H].get(R)` if set, else `config['default'].get(R)` if set, else `default`. (The harness section overrides the base layer; the base layer overrides native.)
3. **Map the value to a venue and invocation.** `default` → native (in-harness
   subagent on the session model). `claude`/`opus`/`fable` → the Claude CLI
   recipe. `codex`/`sol`/`terra`/`luna` → the Codex CLI recipe; the GPT-5.6 code
   names add `--model gpt-5.6-<name>`. A Codex effort suffix adds
   `-c 'model_reasoning_effort="<effort>"'`; a Claude effort suffix adds
   `--effort <effort>`. Planner/reviewer/critic remain read-only and the coder
   remains write-enabled.
4. **CLI availability.** A role that resolves to a CLI whose binary is not on PATH → **native**, recorded as a *quiet* informational note (`native — <cli> not on PATH`). This is **not** a 🚨 disconnect: a missing other-CLI is an environment fact, and the shipped cross-review default must not alarm a single-CLI user every phase.

Every role's resolved `(venue, model, effort)` is remembered for Steps 3–6 and the Step 10 END block. Roles do not re-resolve mid-session.

## Invocation, resume, and the write-enabled coder

The command lines, flag rationale, auth scrubs, `</dev/null` trap, and session-id capture live in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md) §§2–4. Summary of what each role adds:

- **Read-only roles** (planner, reviewer, critic) use the read-only recipe with
  the resolved model and effort flags added when pinned
  (`claude --model <m> --effort <effort>`;
  `codex --model gpt-5.6-<name> -c 'model_reasoning_effort="<effort>"'`) and
  `--allowedTools` mirroring the role's tool stance (planner keeps
  `WebSearch,WebFetch`; reviewer/critic keep `Read,Grep,Glob`). Bare `claude`
  and `codex` pins add no model flag.
- **The coder writes**, so it uses the **write-enabled** variant: claude `--allowedTools "Read,Grep,Glob,Write,Edit,Bash"` with a higher `--max-turns`; codex `-s workspace-write` (initial) / `-c 'sandbox_mode="workspace-write"'` (resume). **Never** `--yolo` / `danger-full-access`. Single-writer guarantee: `/kickoff` is sequential, so the pinned coder owns the tree exclusively during its stage (build gates run afterward) — satisfying "never two writers on one tree" without a worktree.
- **Session resume across a phase.** A role invoked more than once in a phase — the planner across plan-revision rounds, the coder across code-revision and build-fix rounds, a reviewer/critic across review rounds — **resumes the same session** so its prior context stays live: capture the session id (codex `thread_id` via `--json`; claude `.session_id`), thread the latest id forward, re-capture each round, and honor the codex `resume` flag-surface trap (`-s`/`-C` rejected → `-c 'sandbox_mode=…'` + `cd`).
- **Recursion guard.** Every delegated child runs with `KICKOFF_DELEGATION_DEPTH=1` in its environment, so a delegated role that itself reads this config never re-delegates (resolution step 1).

## Fallback state machine

Success of a delegated call is gated on **three signals together**:

1. The output artifact (codex `--output-last-message` file / claude JSON `.result`) exists and is non-empty.
2. It carries the role's expected output shape — for a reviewer/critic, exactly one `## Verdict: APPROVED` / `## Verdict: REVISE` header; for a planner/coder, the plan / file-list-and-status report the role file defines.
3. The call returned within a wall-clock timeout — 600 s plan review, 900 s code critique, higher for the coder's implementation loop. The timeout is a **hang guard, not a performance target**: it only keeps a stalled subprocess from hanging the orchestrator; a working call takes as long as it takes. Tune upward freely; tighten only with evidence.

Any signal failing means the call failed. Triggers and handling:

| Trigger | Detected | Action |
|---|---|---|
| Resolved CLI not on PATH | Step 0a | Role runs **native** for the session. **Quiet** — END-block note `native (<cli> not on PATH)`, no 🚨. |
| Recursion guard (`KICKOFF_DELEGATION_DEPTH` set) | Step 0a | All roles native. Silent. |
| Non-zero exit, timeout, or network failure (incl. the macOS Seatbelt `workspace-write` network trap) | During a call | This **stage** finishes natively. Record `[fallback: <reason>]` and raise a **🚨** disconnect (a role that *was* reachable didn't run on its pin). Do not repair the sandbox mid-run. |
| Turn cap exhausted (claude `subtype: "error_max_turns"`, no verdict) | After a call | Investigation done but unreported and the session is live — **resume once** (`claude --resume <sid> -p "Conclude your review now: emit the exact verdict header and your essential findings only."`) before giving up. If the rescue also fails the gate: native, `[fallback: max-turns exhausted]`, 🚨. |
| Artifact missing/empty or output shape malformed | After a call | Native, `[fallback: malformed output]`, 🚨. |

Rules:

- **Absent CLI is quiet; a failed reachable call is 🚨.** The distinction is deliberate: "you don't have the other CLI installed" is an environment fact the shipped default shouldn't nag about, while "the model you pinned was there but the call broke" is a real disconnect between what you asked for and what ran.
- The `--max-turns` cap is a **runaway-loop guard, not a depth budget** — the wall-clock timeout is the binding guard. Calibrate generously (50 for review; higher for the coder).
- Fallback is **per stage**. A planner fallback does not force the coder native; each stage resolves its own venue.
- Once a stage falls back mid-way, **all remaining rounds of that stage run native** — no venue thrashing inside a stage.
- Fallback is never an error condition. The phase proceeds; the END block and the 🚨 summary tell the human what happened.

Convergence-based revision loops ([`four-canonical-agents.md`](four-canonical-agents.md)) govern delegated rounds unchanged, under the same 5-cycle runaway backstop. Handoff hygiene for delegated review (redact the implementer's self-assessment, adversarial framing, map-not-payload, flag regenerated blobs, scope the reading mandate) is in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md) §4.

## END-block reporting and 🚨 disconnect surfacing

Every `/kickoff` END block records the orchestrating harness and each role's resolved model/venue (format owned by `/kickoff`):

```
Role model/venue (per policies/role-models.md) — orchestrated by <claude|codex>:
- Planner:  native (<session model>) | claude | codex | opus | fable | sol[@effort] | terra[@effort] | luna[@effort]  [resolved: <CLI model and effort>] [fallback: <reason>]
- Reviewer (plan review): same vocabulary | skipped (light lane)  [resolved/note/fallback]
- Coder:    same vocabulary  [resolved: <CLI model and effort>] [fallback: <reason>]
- Critic (code review): same vocabulary  [resolved/note/fallback]
```

Because a *failed* pin means **what ran ≠ what was configured**, each such disconnect is *also* surfaced with a **🚨** line in the user-facing summary — e.g. `🚨 coder configured for opus but ran native (call timed out) — output was NOT produced by opus`. A CLI-absent fallback is the quiet exception (informational END-block note only). A clean run raises no 🚨.

## Propagation

`/roles`, `bin/role-models`, this policy, and the shipped `role-models.yaml` (with its cross-review harness sections) are **universal** — `/stamp` carries them into every derived project, and `/teach` can port them. Every project has the same four roles and the same cross-vendor-review default. The *values* are per-project state; the *machinery* is methodology.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) owns the roles, names, tool stances, verdict headers, and cycle caps; this policy chooses each role's model/harness without changing any of that.
- [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md) governs the `bin/role-models` (script) / `/roles` (skill) seam.
- [`review-lanes.md`](review-lanes.md): in a `light` lane the code critique is the only review that runs, so its resolved venue matters more, not less. Light-lane phases resolve venues like any other.
- [`human-in-the-loop.md`](human-in-the-loop.md) is unaffected: no delegated model may commit, advance gates, or claim subjective acceptance. The human decides done, whichever model ran.
- Invocation recipes, flag rationale, auth traps, and handoff hygiene: [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md).
