# Policy: Per-Role Model Pinning (harness-aware)

Each canonical `kickoff` role may select a model and optional reasoning effort, scoped by which harness is orchestrating. The model determines the delegated CLI; `{model: default}` runs natively. Orchestration and build gates always stay on the current session model.

## Independent review and portable presets

Every review runs in a separate role context with the canonical review contract. Same-harness review preserves that independence. Cross-vendor review is an explicit option whose incremental value should be measured; model strength alone does not establish decorrelation or better defect detection. Review lane and model/venue selection are orthogonal.

`bin/kickoff-config apply-preset quality|balanced|economy [--review same-harness|cross-vendor]` expands the selected preset into ordinary `role_models` pins for both concrete harness sections. Omitted review mode means `same-harness`. There is no persisted preset selector or runtime router. Applying a preset replaces all concrete role selections, preserves the base `default` layer and other configuration/comments, validates the complete document, and writes atomically. It makes no model call and requires no preflight.

| Preset | Orchestrating harness | Planner | Reviewer | Coder | Critic |
|---|---|---|---|---|---|
| quality | codex | astra | astra | astra | astra |
| quality | claude | fable | fable | fable | fable |
| balanced | codex | astra | astra | sol | astra |
| balanced | claude | fable | fable | opus | fable |
| economy | codex | sol | sol | sol | sol |
| economy | claude | opus | opus | opus | opus |

All preset pins use `high` effort. Quality/same-harness is the shipped, reset and stamp default. Cross-vendor changes reviewer and critic only: quality/balanced use Fable from Codex and Astra from Claude; economy uses Opus from Codex and Sol from Claude. These are operator-approved starting points, not measured rankings. A missing required CLI or model entitlement fails preflight; select an available preset or explicit pins through the manager, `roles`, or direct editing before restarting.

## Human-editable configuration

Model routing lives under `role_models` in the repo-root [`kickoff.yaml`](../kickoff.yaml). The file is deliberately human-editable. Model and effort are separate fields:

```yaml
role_models:
  default:
    planner: {model: default}
    reviewer: {model: default}
    coder: {model: default}
    critic: {model: default}
  claude:
    planner: {model: fable, effort: high}
    reviewer: {model: fable, effort: high}
    coder: {model: fable, effort: high}
    critic: {model: fable, effort: high}
  codex:
    planner: {model: astra, effort: high}
    reviewer: {model: astra, effort: high}
    coder: {model: astra, effort: high}
    critic: {model: astra, effort: high}
```

Harness sections `claude` and `codex` override the base `default` layer. Roles `planner`, `reviewer`, `coder`, and `critic` map to the four canonical agent definitions. A non-default model always uses its implied CLI, including when its vendor matches the orchestrator.

| Selector | Venue / explicit model | Supported explicit effort |
|---|---|---|
| default | Native session | None |
| claude | Claude CLI configured model | low, medium, high, xhigh, max |
| codex | Codex CLI configured model | low, medium, high, xhigh |
| opus, fable | Claude CLI / corresponding alias | low, medium, high, xhigh, max |
| astra | Codex CLI / gpt-6-astra | low, medium, high, xhigh, max |
| sol, terra, luna | Codex CLI / gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna | low, medium, high, xhigh, max |

Effort is a separate optional field; omission retains the selected CLI/model's configured effort. The table is a supported subset, not a claim that other settings cannot exist. `ultra` is not enabled. Invalid model/venue or model/effort combinations fail before write or spawn. Capability metadata is not live entitlement; recipient-local preflight remains decisive for execution.

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
- `apply-preset` expands a named preset into both concrete harness sections;
- `reset models` resets only model routing;
- `preflight --receipt <path>` validates live external venues and writes a config-bound receipt;
- `verify-preflight-receipt` revalidates that receipt against current routing.

It uses round-trip YAML parsing, preserves comments, ordering, quoting, and data under `extensions`, and atomically replaces the file only after full validation. `roles` is its thin natural-language wrapper. Direct human edits are equally supported and take effect after `show models` validates them.

## Resolution (kickoff Step 0a)

Resolve once per evidence run and retain its frozen tool/config bundle through all rounds, including when implementation edits the live configuration. New settings apply to the next run. `CLAUDECODE=1` means Claude orchestrates; otherwise Codex does.

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

## Governed recovery

Preserve failed artifacts and dispatch evidence, classify the failure, and park unless an existing explicitly authorized recovery preserves the selected model, effort, and required authority. Native dispatch is admissible only when the harness can explicitly honor those same selections; otherwise that route is unavailable. Never inherit an agent-wrapper model pin, silently downgrade, change effort, or switch providers to make a failed call appear successful. Terminal policy refusals do not authorize automatic retries or provider switching. Do not identify refusals by matching words in prose; structured terminal errors remain failures even when a text artifact exists. Alias string equality and auxiliary usage-model maps cannot prove a provider substitution.

Existing bounded verdict-only and incomplete-stream recoveries retain their own conditions and budgets. This rule grants no additional retry authority. Report the failed request, any authorized recovery and its basis, and the actual dispatch venue.

## Mandatory live preflight (kickoff Step 0b)

Before phase identification, decomposition, status mutation, log writes, or agent invocation, `kickoff` runs:

```bash
./bin/kickoff-config preflight --receipt "$RUN_DIR/role-preflight.json"
```

The manager probes every non-native role target with its resolved `(CLI, model,
effort, access mode, research capability)`. It writes unpredictable ASCII text to an isolated local file and requires the venue to read and return that exact text beside `KICKOFF_PREFLIGHT_OK`. The text is absent from the prompt; echoing a prompt sentinel is insufficient. The manager validates the response and computes the SHA-256 of the file bytes for the receipt, so read-only roles need no hashing tool or shell permission.
The receipt binds the configuration digest, harness, resolved targets, and
shared probe digest. All-native routing writes the same schema with no targets.
Production credential scrubs, model/effort and research flags, stdin closure,
approval posture, and read-only/write-enabled access still apply.

Preflight is fail-closed. A missing CLI, unusable authentication, unavailable model, network or sandbox error, flag incompatibility, timeout, malformed response, wrong challenge response, stale configuration, or incomplete target set aborts `kickoff` before phase state exists. There is no native fallback for an upstream prerequisite failure.

## Invocation and resume

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
protocol recovery in the END block. Failed verification follows [Governed recovery](#governed-recovery).

After successful preflight, a non-zero child, timeout, network failure, stale or missing artifact, malformed output, candidate mismatch, or unrecoverable protocol error remains a failed attempt under [Governed recovery](#governed-recovery). A Claude review that exhausts its turn cap after completing investigation may resume once only to emit its verdict under the existing timeout policy.

## END-block reporting

Every END block records preflight, orchestrating harness, and each role's requested model, effort and venue separately from provider observations. The watcher's existing `model` and `effort` fields mean requested values. Optional local diagnostic fields are `harness_version`, `observed_model`, `observed_effort`, and `observation_errors`; they do not change required trace, registration or receipt schemas. Null observations render as `unreported`, never as the request copied into an observation.

The selected CLI's bounded, scrubbed `--version` operation supplies a version observation when available; failure records null and a diagnostic without changing routing. Qualified Claude `system`/`init` metadata may supply its top-level `model` and `claude_code_version`; conflicting primary values remain null with an observation error. Effort for both venues and Codex primary model remain unreported until a primary source field is qualified. Do not infer identity from assistant prose, requested argv, or auxiliary usage-model maps.

Record authorized recovery and verified protocol recovery separately, retaining failed evidence. Any configured-versus-dispatched venue difference is repeated with a 🚨 and its authority in the user-facing summary. Timing and candidate-bound summaries remain required by [`role-timeouts.md`](role-timeouts.md) and [`orchestration-evidence.md`](orchestration-evidence.md).

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
- [`human-in-the-loop.md`](human-in-the-loop.md) still governs completion and delivery: a delegated venue may not commit, push, advance a gate, or claim subjective acceptance, whichever vendor reviewed. Only the orchestrator delivers, and only after the phase closes with every gate green.
