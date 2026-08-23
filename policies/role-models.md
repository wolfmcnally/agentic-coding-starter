# Policy: Per-Role Model Pinning (harness-aware)

Each canonical `kickoff` role may select a model and optional reasoning effort, scoped by which harness is orchestrating. The model determines the delegated CLI; `{model: default}` runs natively. Orchestration and build gates always stay on the current session model.

## Review diversity scales with coder capability

A reviewer from the *same* model family shares the coder's blind spots, and its marginal catches shrink as the coder's baseline quality rises. Cross-model review's value is decorrelation, and decorrelation does not shrink: whatever class of error a frontier coder still makes is precisely the class it is least able to see in its own family's review. Two consequences:

- **The stronger the coding model, the stronger the case for cross-vendor review.** Do not read a strong coder's streak of clean first-cycle reviews as a reason to clear the reviewer pins — read it as same-family review running out of things only a different family would catch.
- **The shipped default routes `reviewer` and `critic` to the other harness** — that default *is* the second-family mechanism, not a stylistic preference.

Interaction with review lanes ([`review-lanes.md`](review-lanes.md)): in a `light` lane the code critique is the only review that runs, which makes its venue diversity matter more, not less.

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

The routing, timeout, run-budget, and research-budget schemas are strict:
unknown harnesses, roles, or fields fail validation so direct-edit typos cannot
disappear silently. Project-specific data belongs under top-level `extensions`,
where arbitrary keys are preserved and ignored by the current resolver. Invalid
configuration fails before any command runs or write occurs.

## Manager and direct edits

`bin/kickoff-config` validates the complete document and owns mechanistic operations:

- `show models` resolves the current harness;
- `show research` reports role capability and originating-query budgets;
- `set-models` updates only `role_models`;
- `reset models` resets only model routing;
- `preflight` validates live external venues.

It uses round-trip YAML parsing, preserves comments, ordering, quoting, and data under `extensions`, and atomically replaces the file only after full validation. `roles` is its thin natural-language wrapper. Direct human edits are equally supported and take effect after `show models` validates them.

## Resolution (kickoff Step 0a)

Resolve once per session. `CLAUDECODE=1` means Claude orchestrates; otherwise Codex does.

1. If `KICKOFF_DELEGATION_DEPTH` is set, every role runs native and no child delegates again.
2. For role `R`, use `role_models[H][R]`, else `role_models.default[R]`, else `{model: default}`.
3. Map the model to its implied CLI and add the separate effort field to the CLI invocation.
4. Preserve the resolved `(venue, model, effort)` for every round and the END block.

Planner, reviewer, and critic remain read-only; the coder remains write-enabled.

Read/write posture and research authority are independent. Per
[`research-authority.md`](research-authority.md), planner and reviewer may
originate search and retrieval; coder and critic may retrieve plan/brief-named
resources but may not originate search. Ambient MCP servers and plugins are
allow-by-default and are not disabled by model routing. A project or phase may
explicitly narrow them.

**A tool stance is only as guaranteed as its venue's enforcement.** Measured in a donor project: a delegated Claude-venue role launched with a restricted `--allowedTools` list still executed tools outside it — a planner launched without `Bash` made twenty-four Bash calls of which one was denied, despite an explicit taboo in its role definition. Treat that flag as a strong hint and the role's tool stance as self-policed discipline, not a sandbox; the Codex venue's `-s read-only` enforces the read-only stance structurally. Where a stance must be guaranteed rather than requested, route the role to a venue that enforces it.

**Native fallback carries the resolved tier.** Any `model:` pin in an agent wrapper's frontmatter is a default for ordinary native dispatch, not a routing decision, and it goes stale as model generations advance. When a delegated venue fails and a stage falls back to native, the orchestrator passes the `role_models`-resolved tier explicitly rather than inheriting a wrapper pin — observed otherwise in a donor project: a wrapper pinned a superseded model generation, so the fallback silently downgraded the role at exactly the moment its delegated venue had already failed.

## Mandatory live preflight (kickoff Step 0b)

Before phase identification, decomposition, status mutation, log writes, or agent invocation, `kickoff` runs:

```bash
./bin/kickoff-config preflight
```

The manager probes every non-native role target with its resolved `(CLI, model,
effort, access mode, research capability)`. It uses production credential
scrubs, model/effort and research flags, stdin closure, approval posture, and
read-only/write-enabled access in an empty temporary directory. Success
requires the exact `KICKOFF_PREFLIGHT_OK` result within 120 seconds.

Preflight is fail-closed. A missing CLI, unusable authentication, unavailable model, network or sandbox error, flag incompatibility, timeout, malformed response, or wrong sentinel aborts `kickoff` before phase state exists. There is no native fallback for an upstream prerequisite failure.

## Invocation, resume, and fallback

`bin/kickoff-config` owns the production command. `render-command` emits the
exact inspectable argv; `watch` generates and launches it from role, venue,
model, effort, prompt, artifact, resume, and timeout metadata. Callers never
hand-build a Claude or Codex command. The manager alone owns auth scrubs,
recursion depth, access posture, research capability flags/directives,
artifact wiring, and model/effort flags. Roles
resume the same external session across revision rounds.

Before dispatch, `kickoff-evidence register-role-attempt` creates an immutable
per-attempt registration. The watcher accepts that registration—not the
append-only ledger—and binds it to exact intelligence and nested wait spans.
Review roles receive a strict structured-output schema generated from the same
finding vocabularies the evidence validator enforces — constraint at
generation, because post-hoc validation makes the cheapest repair (one more
turn saying "invalid token, re-emit") unavailable, and a single invented
vocabulary token can discard an entire expensive review batch. The post-hoc
validator stays in the path for what strict structured-output subsets cannot
express (id shapes, non-empty text, transition legality). A missing
registration, routing mismatch, stale artifact, malformed schema result, or
bad span join fails closed.

### Credential precedence

Both CLIs rank an environment API key **above** their subscription OAuth, and
*set does not mean valid*. Claude Code injects a session-scoped
`ANTHROPIC_API_KEY` into its children, so any delegation chain beginning in a
Claude Code session can carry a key that fails direct API auth; a stale
`OPENAI_API_KEY` likewise outranks a ChatGPT-plan login, flipping billing or
failing outright — while the CLI's status display still reports the plan
login. Neither CLI's status display reliably reveals which credential is live.

Under the subscription auth model an environment key is never the intended
credential, so the dispatch manager scrubs it unconditionally at the spawn
point: `ANTHROPIC_API_KEY`, `CLAUDECODE`, and `CLAUDE_CODE_ENTRYPOINT` for the
Claude venue; `OPENAI_API_KEY` and `CODEX_API_KEY` for the Codex venue. The
scrub costs nothing when no key is present and never harms keychain OAuth or
an explicit OAuth token. Do not rely on the parent's hygiene: Codex strips
key-shaped variables from its children's environment, but Claude Code forwards
the full environment *and adds* its own key. An API-key-authenticated project
inverts this: pass the key inline to a single invocation, never as a job-level
export.

### Review handoff

Pass a review role the raw artifact and the requirements, adversarially
framed — never the implementer's self-assessment, and never its build-status
narrative. This is measured, not stylistic: the strongest published experience
report (cited in [`../briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md) §1)
found a cold artifact produced roughly 9.4 mean findings against 2.4–4.0 when
the implementer's narrative was included, and critical-severity tagging
roughly halved under even mild framing.

**Hand the reviewer a map, not a payload, and never reject a venue on diff
size.** An external reviewer runs against a read-only checkout with its own
Read and Grep, exactly like a native subagent, so a large change travels as
the changed-file list plus `git diff --stat`; inline a full diff only when it
is small enough to read whole. Flag machine-regenerated blobs — fixtures,
snapshot data, lockfiles — as spot-check material so a diff dominated by
generated data does not *read* as unreviewably large. Computing the diff's
byte count and falling back to native without ever making the external call
confuses an on-disk artifact with tokens in a context window; a reviewer never
loads a whole diff at once. Delegation is discarded on the three-signal
success gate below, never on a pre-computed size estimate.

**Generate each round's invocation from explicit parameters.** Deriving round
N's launcher from round N−1 by search-replacing a token silently no-ops when
the token does not match, and the new round is then handed the *previous*
round's prompt. The symptom mimics model misbehavior exactly — a reviewer
re-raising already-fixed findings, a coder reporting "already done" — and gets
misdiagnosed as drift. Assert the prompt file exists before spawning. When a
delegated agent's output contradicts what you believe you sent it, suspect the
plumbing before the model.

A delegated call is an ordinary success only when all three hold:

1. its output artifact exists and is non-empty;
2. it has the role's required output shape or exact verdict header; and
3. its child succeeded and its terminal event stream completed inside the
   first-event, idle-progress, and hard deadlines.

The watchdog records child status, artifact freshness, and stream completeness
independently. Exit 66 (`completed-unverified-protocol`) preserves a fresh
artifact from a successful child whose terminal stream was incomplete. The
orchestrator may use it only after validating the role shape, ingesting and
validating any finding/change evidence, and confirming the expected candidate
id per [`orchestration-evidence.md`](orchestration-evidence.md). It records the
protocol recovery in the END block. Failed verification follows the normal
fallback path.

After successful preflight, a non-zero child, timeout, network failure, stale
or missing artifact, malformed output, candidate mismatch, or unrecoverable
protocol error makes the rest of that stage native and produces a 🚨
disconnect. A Claude review that exhausts its turn cap may resume once only to
emit its verdict. Fallback is per stage; once a stage falls back, it does not
venue-thrash.

## END-block reporting

Every END block records the preflight result, orchestrating harness, and each
role's resolved model, effort, venue, fallback status, and any verified
protocol recovery. It also carries the timing and candidate-bound evidence
summaries required by [`role-timeouts.md`](role-timeouts.md) and
[`orchestration-evidence.md`](orchestration-evidence.md). Any post-preflight
difference between configured and actual venue is repeated as a 🚨 in the
user-facing summary.

## Propagation

`kickoff.yaml`, `bin/kickoff-config`, `bin/kickoff-evidence`, the finding schema,
the exact telemetry substrate, `roles`, this policy, and the timeout policy are
one universal configuration/execution bundle. `stamp` carries it. `teach`
upgrades its schema and mechanics while preserving target values, comments,
`extensions` data, ambient MCP/plugin availability, and local operational
state. `learn` may absorb general
mechanics but never donor operational state.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) owns role names, semantics, tool stances, verdicts, and convergence limits.
- [`research-authority.md`](research-authority.md) owns search/retrieval authority, allow-by-default venue resources, egress boundaries, and query budgets.
- [`role-timeouts.md`](role-timeouts.md) owns execution budgets, process-group termination, telemetry, and recalibration.
- [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md) puts validation and editing in `bin/kickoff-config`; model-choice judgment stays with the human or `roles` interpretation.
- [`human-in-the-loop.md`](human-in-the-loop.md) still governs completion and commits.
