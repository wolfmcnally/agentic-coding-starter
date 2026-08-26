---
title: "Cross-Agent CLI Invocation — Best Current Practices"
date: 2026-08-23
status: methodology
scope: BCPs for invoking one coding-agent CLI from inside another (Claude Code ↔ Codex CLI), and the design rationale for the per-role model/venue feature (harness-aware cross-vendor review and pinning).
---

# Cross-Agent CLI Invocation — Best Current Practices

This brief pins the researched best current practices (as of mid-2026) for invoking OpenAI's `codex` CLI from inside Claude Code and Anthropic's `claude` CLI from inside Codex, so future work cites a stable position instead of re-deriving it. It also records the design rationale for **cross-harness review** — now delivered as the shipped default of the per-role model/venue feature, which pins a separate model and effort per canonical role, scoped by which harness is orchestrating.

Both vendors sanction this interop: OpenAI ships an official Claude Code plugin that delegates to the local Codex CLI, and both CLIs document headless scripting modes. Every mature published pattern is **subprocess-first** — shelling out to the other CLI — rather than MCP-bridged. MCP wrappers exist but add a moving part without changing the fundamentals; for bounded, one-shot delegations the subprocess is the de-facto standard.

Research authority remains role-based across either transport. Planner and
reviewer may originate search and retrieve. Coder and critic may retrieve only
plan- or brief-identified resources plus same-host structural neighbors; they
may not originate discovery. `bin/kickoff-config` renders that authority and
the resolved `kickoff.yaml` query budget into every prompt. Installed MCP
servers and plugins remain available by default, but no named server is
assumed to exist. External research is GET-only and carries no repository or
candidate content outbound.

## 1. Why cross-harness review

- **Cross-vendor review catches more.** A model reviewing its own output misses the failure classes it generates. The strongest published experience report (Orr, May 2026) found the bigger lever is *framing*: handing the reviewer a cold artifact (raw diff + requirements, no implementer narrative) produced ~9.4 mean findings vs 2.4–4.0 when the implementer's self-assessment was included — a 3–4× difference — and critical-severity tagging roughly halved with even mild framing.
- **Review roles are read-only by construction.** Our `plan-reviewer` stance adds WebSearch/WebFetch and `code-critic` adds WebFetch to Read/Grep/Glob, but neither receives a repository write tool. That maps directly onto the external CLIs' sandboxed read-only modes: the external reviewer physically cannot contend for the working tree.
- **The verdict contract already fits.** The methodology's `## Verdict: APPROVED` / `## Verdict: REVISE` string-match contract is exactly the sentinel-string loop-control pattern the ecosystem converged on independently.
- **Instruction parity is automatic.** Codex auto-ingests `AGENTS.md` (→ `CLAUDE.md` via symlink); `claude` auto-loads `CLAUDE.md`. An external reviewer invoked from the repo root is bound by the same policies, invariants, and verdict contract as a native subagent, with no extra plumbing.

## 2. Claude Code → `codex` (headless)

Canonical generated invocation (review roles):

```
./bin/kickoff-config render-command --role reviewer --venue "$VENUE" --model "$MODEL" --effort "$EFFORT" --prompt-file "$PROMPTFILE" --required-output-file "$MSGFILE"
```

The manager resolves the venue, model, effort, auth scrubs, access mode,
artifact paths, output schema, telemetry registration, and watcher command.
The rendered command is authoritative; callers do not reconstruct it from the
flag rationale below.

Capture the session id for revision rounds from the first event on stdout (the human-readable mode prints it *only* to stderr, which the recipe discards — without `--json` the id is unrecoverable):

```
TID=$(grep -m1 '"thread.started"' "$EVENTS" | grep -ioE '[0-9a-f-]{36}')
```

The verdict is still read from `$MSGFILE` (the `--output-last-message` artifact populates normally under `--json`); `$EVENTS` exists only to recover the `thread_id`.

Flag-by-flag rationale:

- **`codex exec`** is the non-interactive entry point (alias `codex e`). Prompt as argument, or `-` to read stdin.
- **Close stdin — mandatory for any non-interactive or backgrounded parent.** Even with the prompt passed as an argument, `codex exec` *also* reads stdin (it appends piped stdin to the prompt) and, when stdin is an open non-TTY pipe that never sees EOF, blocks on `Reading additional input from stdin...` until a guard kills it. `bin/kickoff-config watch` supplies `DEVNULL`; direct diagnostic invocations must use `</dev/null` explicitly.
- **Approvals must be pinned off.** Any approval prompt in a no-TTY context can block indefinitely; there are verified field reports of approval-state races freezing a session for ~10 minutes *while holding the git index lock*. A headless call must never be able to prompt. Use the **`-c 'approval_policy="never"'` config override** rather than the `-a/--ask-for-approval` flag: `exec` flag surfaces churn across versions (codex-cli 0.136.0's `exec` rejects `-a` outright — empirically verified on this template's first smoke test — while `-c` dotted-path overrides parse everywhere). When a flag-parse error occurs anyway, `codex exec --help` is the in-environment truth.
- **`-s read-only` (`--sandbox read-only`)** matches the reviewer tool stance and makes working-tree contention impossible. Use `workspace-write` only when the external agent must edit (not the case for review). `--full-auto` is deprecated; `--dangerously-bypass-approvals-and-sandbox` (`--yolo`) is for already-isolated containers only — it exposes the user's `~/.codex/auth.json` to anything in the repo.
- **`--output-last-message <file>` (`-o`) is the verdict-capture contract.** The file artifact is the robust way to capture the final agent message; gate on it. Under `--json` (which the recipe requires for session-id capture, below) stdout carries the JSONL event stream rather than the bare final message, so it is redirected to a separate `$EVENTS` file; the verdict still comes from the `-o` artifact, not from stdout. Suppress stderr noise with `2>/dev/null`.
- **The watchdog makes artifacts fresh.** `--required-output-file "$MSGFILE"` truncates the path before launch and requires the child to repopulate it. A zero exit with no fresh artifact is a protocol error, so a revision round can never reuse an earlier verdict.
- **`--json` is mandatory, not optional, when revision rounds may follow** (the cross-harness review case). It is the *only* way to capture the session id programmatically: the first stdout event is `{"type":"thread.started","thread_id":"<uuid>"}`. The human-readable mode prints `session id: <uuid>` to **stderr** alone — and the recipe pipes stderr to `/dev/null`, so without `--json` the id is structurally unrecoverable and every revision round is forced to spawn a fresh cold context. This was a real defect in the first cut of this recipe, reproduced deterministically. (NDJSON also carries `turn.completed` / `turn.failed` and token usage when telemetry matters; `--output-schema <schema.json>` constrains the final message to a JSON Schema when a parseable struct beats prose.)
- **`-C "$(pwd)"`** pins the working directory explicitly.
- **`-c 'web_search="live"'` exposes retrieval/search capability; the prompt
  supplies authority.** Codex's transport switch cannot distinguish originating
  discovery from retrieval, so every role gets the capability and the rendered
  role directive enforces the matrix. Do not disable all MCP servers or
  plugins as a substitute for role authority.
- **Pass large context via files, not inline.** Write the plan text or `git diff` output to a temp file and reference its path in the prompt. Every published skill does this.
- **Do not hardcode `-m <model>` except through the deliberate pin resolver.**
  Model names churn rapidly and overloaded models silently reroute; a bare
  `codex` pin therefore uses the configured default and adds no `-m`. The
  closed `roles` vocabulary owns the explicit exception: `sol`, `terra`, and
  `luna` map deterministically to `--model gpt-5.6-sol`,
  `--model gpt-5.6-terra`, and `--model gpt-5.6-luna`. The user-facing code
  name stays stable inside this methodology; `bin/kickoff-config` owns the current
  versioned CLI slug. A separate `effort` field set to `low|medium|high|xhigh` adds
  `-c 'model_reasoning_effort="<effort>"'`. Preserve both overrides on every
  resume call so a role never changes model or effort mid-stage. In the recipe,
  `MODEL_ARGS` is empty for bare `codex` or `(--model gpt-5.6-<name>)` for an
  explicit pin; `EFFORT_ARGS` is empty or
  `(-c 'model_reasoning_effort="<effort>"')`. The watchdog verifies that these
  actual CLI flags match its `--model` / `--effort` metadata before it spawns.
- **Exit codes are not the whole contract** for `codex exec`. Ordinary success
  requires a successful child, a fresh `-o` artifact with the expected role
  shape, a terminal `turn.completed` event, and execution inside the budget.
  The watchdog records those signals separately. A successful child plus a
  fresh artifact but no terminal event returns 66; the artifact is usable only
  after explicit role-shape, evidence, and candidate verification.
- **Revision rounds: `codex exec resume <session-id> ...`** preserves the reviewer's context across rounds. **The `resume` subcommand has a different flag surface than `exec` — `-s/--sandbox` and `-C/--cd` do not exist on it** (codex-cli 0.136.0 rejects `-s` with `error: unexpected argument '-s' found`, exit 2 — empirically verified). Set the sandbox through a config override instead, and `cd` into the repo rather than passing `-C` (resume filters recorded sessions by cwd). `--model` and `-c model_reasoning_effort=...` are accepted on resume (re-verified with codex-cli 0.144.0) and must be repeated for an explicit pin:

  ```
  ./bin/kickoff-config render-command --role reviewer --venue codex --model "$MODEL" --effort "$EFFORT" --prompt-file "$PROMPTFILE" --required-output-file "$MSGFILE" --resume-session "$TID"
  ```

  For example, a resumed role with `model: sol` and `effort: medium` adds
  `--model gpt-5.6-sol -c 'model_reasoning_effort="medium"'` to that command.

  (`resume` reads stdin exactly as `exec` does, so it carries the same `</dev/null` redirect — the stdin-hang bullet above applies to both subcommands.)

  A naive resume that simply re-uses the original `exec` flags flag-parse-fails and trips the fallback, so a project that captured the id correctly but copied the `exec` flags still lands in a fresh context — the two defects compound. If no session id was captured or resume fails, fall back to a fresh call with the full updated context (correctness over efficiency).
- **Auth precedence trap (mirror of §3's).** An interactive ChatGPT-plan login persists in `~/.codex/auth.json` with token auto-refresh, and subprocess calls reuse it — but a set `OPENAI_API_KEY` silently outranks it, flipping the call to API-key billing (or a 401 on a stale key) while `codex /status` still reports the plan login (openai/codex#2341, #3367, #20099). Hence the recipe's `env -u OPENAI_API_KEY -u CODEX_API_KEY` scrub — free when no key is present, never harms the `auth.json` login. The supported hard backstop is `forced_login_method = "chatgpt"` in `~/.codex/config.toml` (`preferred_auth_method` is a user-invented knob that does nothing). For CI on API auth, pass `CODEX_API_KEY` inline to a single `codex exec` — never a job-level export beside repo-controlled code; for CI on the plan, seed a `codex login`-generated `auth.json` onto the runner and keep the env keys unset.
- **AGENTS.md ingestion.** Codex walks repo root → cwd loading `AGENTS.md` (no flag disables this as of mid-2026). For cross-harness review this is desirable — the reviewer inherits the repo's policies. To *avoid* it (scoped consultations unrelated to the repo), run with `-C` pointed at a scratch directory and pass context via temp files.

## 3. Codex → `claude` (headless)

Canonical generated invocation (review roles):

```
./bin/kickoff-config render-command --role reviewer --venue claude --model "$MODEL" --effort "$EFFORT" --prompt-file "$PROMPTFILE" --result-file "$MSGFILE"
```

As in the Codex direction, the generated command is the executable contract;
the bullets below explain its choices rather than defining a second copy.

Flag-by-flag rationale:

- **`claude -p` (`--print`)** is headless mode: run the agent loop, print, exit.
- **Close stdin.** Like `codex exec`, `claude -p` can treat piped stdin as additional prompt input. The watchdog supplies `DEVNULL`; direct diagnostic invocations use `</dev/null`.
- **`--permission-mode dontAsk` is the correct headless mode — never `--dangerously-skip-permissions`.** The "dangerous" bypass still parks on a one-time *interactive* consent dialog with no pre-accept flag; with no TTY it hangs forever (anthropics/claude-code#52506). `dontAsk` is fully non-interactive: pre-approved tools run, everything else is *denied* rather than prompted, and protected paths (`.git`, `.claude`, shell rc files) are never auto-approved — exactly the posture a delegated reviewer should have.
- **`--allowedTools` mirrors the canonical role stance.** Planner/reviewer get
  `Read,Grep,Glob,WebFetch,WebSearch`; coder gets
  `Read,Grep,Glob,Write,Edit,Bash,WebFetch`; critic gets
  `Read,Grep,Glob,WebFetch`. (`AskUserQuestion` is omitted: escalation cannot
  reach the human through a nested CLI — an unresolved product question
  becomes a verdict/advisory the orchestrator surfaces.)
- **Scrub `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT` from the child environment.** Claude Code sets `CLAUDECODE=1` in every child process and a `claude` launch that sees it refuses to start — even in `-p` mode. Codex itself doesn't set it, but a claude → codex → claude chain inherits it through codex, so the bridge always scrubs.
- **`--output-format stream-json --verbose` is required for progress-aware
  supervision.** It exposes startup and ongoing events so first-event and idle
  guards measure real activity. `bin/kickoff-config` truncates the result path,
  preserves the stream for `session_id`, and requires a fresh final `result`
  event for ordinary success. If the child succeeds and its last assistant
  message is fresh but the final event is absent, the watcher preserves that
  message and returns 66 for explicit role-shape, evidence, and candidate
  verification. A one-shot `json` envelope is acceptable for preflight only;
  it cannot support an idle watchdog during production work.
- **`--model <alias|id>` selects the model.** Omit it for the CLI's configured default (the review-role norm). Pass it for a deliberate per-role pin: `--model opus` / `--model fable` by alias, falling back to the full ids `claude-opus-4-8` / `claude-fable-5` if an alias is unrecognized in a given CLI version.
- **`--effort <level>` selects Claude Code reasoning effort.** The headless CLI
  accepts `low`, `medium`, `high`, `xhigh`, and `max` on fresh and resumed
  sessions (re-verified with Claude Code 2.1.205). A separate `roles` effort
  field such as `high`, `max`, or `medium` adds this flag; omission preserves
  the configured/default effort. Repeat `--effort` together with `--model` on
  every `--resume` call so the role cannot drift mid-stage. `MODEL_ARGS` is
  empty for bare `claude` or `(--model <alias>)`; `EFFORT_ARGS` is empty or
  `(--effort <level>)`. The watchdog rejects a mismatch between those actual
  flags and its routing metadata before launch.
- **`--max-turns N`** (and optionally `--max-budget-usd`) are Claude print-mode circuit breakers — use them as runaway guards, not review-depth budgets. `role_timeouts.<role>.claude_max_turns` supplies 50 for planner/reviewer/critic and 200 for coder. Codex and native roles expose no equivalent per-invocation turn flag, so their enforceable guards are first-event, idle, and hard time. On `error_max_turns`, preserve the streamed `session_id` and allow one concise “conclude now” resume before fallback.
- **Codex's sandbox blocks subprocess network by default.** A codex-spawned `claude` must reach the Anthropic API; `workspace-write` denies that unless `[sandbox_workspace_write] network_access = true` is set in `~/.codex/config.toml` — and on macOS, Seatbelt has been reported to silently ignore that setting in some versions (openai/codex#10390), requiring a full-access session. **Treat a network failure here as a fallback trigger; do not attempt to repair the sandbox mid-session.**
- **Auth precedence trap.** The documented credential order (code.claude.com/docs/en/authentication) ranks an env `ANTHROPIC_API_KEY` *above* `apiKeyHelper`, `CLAUDE_CODE_OAUTH_TOKEN`, and subscription OAuth — intentionally, per Anthropic's support guidance — and *set does not mean valid*. Claude Code injects a *session-scoped* `ANTHROPIC_API_KEY` into its child processes, so any chain that began in a Claude Code session can carry a key that fails direct API auth with a structured 401 `Invalid API key` error; a stale key can also reach a genuine Codex parent through its inherited environment. Under the subscription auth model an env key is never the intended credential, so the recipe scrubs it unconditionally; the scrub is harmless to `apiKeyHelper`, keychain OAuth, and `CLAUDE_CODE_OAUTH_TOKEN`. For subscription-backed automation without a browser, `claude setup-token` mints a long-lived OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`). Note `--bare` mode skips OAuth/keychain reads entirely and requires an API key; API-key-CI projects re-export the key deliberately in the child env instead of relying on inheritance.
- **CLAUDE.md auto-loading.** A `claude -p` run inside a repo loads the repo's `CLAUDE.md`, hooks, skills, and MCP servers like an interactive session would — desirable for cross-harness review (policy parity), avoidable with `--bare` when a context-free consult is wanted.

## 4. General patterns (direction-independent)

- **Live-preflight every non-native target before mutating phase state.** Resolve the phase's external roles first, group them by unique `(CLI, model, effort, access mode)`, and make one minimal sentinel call per group using the production auth scrubs, flags, stdin closure, and read-only/write-enabled posture. Run the probe in an empty temporary working directory: upstream readiness does not need repository context, and the check should neither ingest that token load nor risk touching the tree. Codex therefore needs `--skip-git-repo-check` on this probe alone; the production checkout invocation does not. Require the exact sentinel and a bounded return. CLI presence, auth-status output, and credential files do not prove that precedence, entitlement, network, and the headless invocation all work together. Any preflight failure is an upstream prerequisite failure: abort before status/log mutation rather than silently weakening the configured role topology. `kickoff` encodes this mechanically as `./bin/kickoff-config preflight`.
- **Redact the implementer's self-assessment** from review handoffs. Pass the raw artifact (plan text; diff or, for large changes, the changed-file list + `git diff --stat`) and the requirements, adversarially framed ("assume the implementer was careful but missed something"). Never include "all tests pass" or the coder's build-status narrative — it measurably degrades review depth (§1).
- **After the first full pass, send a candidate-bound revision packet.** The
  packet carries unresolved stable findings, reviewed/current candidate ids,
  causal path/hash changes, authority drift, mapped verification, prior gates,
  and explicit omissions. Original files remain readable. Rebase to a complete
  review when authority, scope, risk class, or trustworthy continuity changes;
  do not make a resumed reviewer reconstruct state from the transcript.
- **Hand the reviewer a map, not a payload — and never reject the venue on diff size.** The external reviewer runs against a read-only checkout with its own Read/Grep (same as the native subagent). So the handoff for a large change is the changed-file list + `git diff --stat`, from which it pulls the files it wants; inline a full diff only when it is small enough to read whole. The failure to avoid: computing `git diff | wc -c`, seeing hundreds of KB, and falling back to native *without ever making the external call* — conflating an on-disk artifact with tokens-in-the-context-window. A reviewer never loads the whole diff at once. Delegation is discarded only on the three-signal gate (missing artifact, malformed verdict, timeout/error), never on a pre-computed size estimate. Flag machine-regenerated blobs (fixtures, snapshot JSON, lockfiles) as "spot-check, don't read line-by-line" so a diff dominated by regenerated data doesn't *read* as unreviewably big. (Observed: a large, fixture-dominated diff pre-rejected on byte count with zero external calls; and, symmetrically, an unbounded "read all the sources" plan-review mandate on a big multi-file phase exhausted the external reviewer's own context and tripped a failed internal compaction before any verdict.)
- **Generate each round's invocation from explicit parameters — never derive it from the previous round's.** Deriving round N's launcher from round N−1 by search-replacing a token silently no-ops when the token doesn't match, and the new round is handed the *previous* round's prompt. The symptom mimics model misbehavior exactly (a reviewer re-raising already-fixed findings; a coder reporting "already done") and gets misdiagnosed as drift or a stale cache. Assert the prompt file exists before spawning; when a delegated agent's output contradicts what you believe you sent it, suspect the plumbing before the model.
- **Verdict sentinel.** Require the reviewer to end with the exact verdict header; parse by string match; treat a missing/malformed verdict as a failed invocation, not a lenient pass.
- **Bound revision rounds by convergence.** Unbounded agent-to-agent loops burn quota and don't converge; iterate only while the reviewer's objections are narrowing, and surface to the human the moment the loop stalls or diverges. A generous numeric backstop catches pathological loops regardless. (Ours: convergence judgment under a 10-cycle runaway backstop.)
- **Recursion depth guard.** Claude's `CLAUDECODE` guard only stops claude→claude nesting. Cross-vendor chains need an explicit guard: set a depth-marker env var (ours: `KICKOFF_DELEGATION_DEPTH=1`) in the child environment and refuse external delegation when it is already set.
- **Scrub API-key env vars at every cross-CLI call site (subscription auth model).** Both CLIs rank an environment API key above their subscription OAuth, so an inherited stray key silently flips auth (and billing) or fails 401 — and the CLIs' own status displays don't reliably reveal which credential is live. `env -u <KEY>` at the call site costs nothing when no key is present and never breaks login-based auth. Do not rely on the parent's hygiene: Codex's default `shell_environment_policy` strips `*KEY*`/`*SECRET*`/`*TOKEN*` from the environment it hands its children, but Claude Code forwards the full environment *and adds* its own session `ANTHROPIC_API_KEY` — scrub at your own spawn point regardless of who launched you.
- **Reviewer is read-only; never two writers on one tree.** If an external agent must write, serialize or isolate; for review there is no reason to allow writes at all. The one write-enabled cross-harness role is a *pinned coder*: it uses `-s workspace-write` (codex) / `--allowedTools "…,Write,Edit,Bash,WebFetch"` (claude), and the single-writer rule is satisfied by serialization — `kickoff` runs the coder stage with no concurrent native writer, so the pinned coder owns the tree exclusively. The macOS Seatbelt `network_access` trap (§3) applies to a workspace-write child that must reach its vendor API; treat that network failure as a fallback trigger.
- **Three clocks on every role call.** Require a first structured event, reset an idle watchdog only on real subprocess progress, and enforce an absolute hard deadline regardless of activity. Kill the process group, preserve artifacts/session ids, and record which clock fired. `bin/kickoff-config watch` implements this for external CLIs; native subagents use the same role budgets through their harness. Every dispatch uses an execution surface that remains observable for the full configured budget: a durable foreground session when the harness provides one, otherwise its tracked background mechanism.
- **Calibrate from tails, not anecdotes.** Vendors publish qualitative latency guidance, not stable planner/reviewer/coder/critic wall-time distributions; task scope, repository size, tools, model, and effort dominate. Keep portable seed floors, collect local successful durations and longest progress gaps, and after at least 30 successes per `(role, venue, model, effort)` recommend `max(floor, 2 × p95)`. Treat timed-out calls as censored cases and never auto-tighten from them.
- **Cost awareness.** Each external call is a full agent loop on the user's other-vendor quota. Bounded calls (capped turns, capped rounds) only; never unbounded polling loops.

## 5. How this maps onto our methodology

These BCPs are applied by the per-role model/venue feature and the per-role execution budgets. Their separate model and effort fields plus first-event, idle-progress, and hard-deadline budgets live together in human-editable `kickoff.yaml`. Its shipped default is cross-vendor review: at Step 4 (plan review) and Step 6 (code critique), the read-only reviewer roles run in the *other* harness. Before phase state begins, `./bin/kickoff-config preflight` live-validates every non-native target. Production external calls run through `watch`, which generates and supervises the child command from resolved metadata; `render-command` exposes the same generated argv for inspection. Calls read the same canonical role file as native subagents, stream progress into the shared exact execution trace, and register immutable evidence. Orchestration and build gates are never delegated.

## 6. Sources

Authoritative documentation:

- Codex non-interactive mode — developers.openai.com/codex/noninteractive
- Codex CLI reference — developers.openai.com/codex/cli/reference
- Codex sandboxing & approvals — developers.openai.com/codex/concepts/sandboxing, developers.openai.com/codex/agent-approvals-security
- Codex auth — developers.openai.com/codex/auth (CI variants: …/codex/auth/ci-cd-auth)
- Codex config (`forced_login_method`, `shell_environment_policy` default credential filter) — developers.openai.com/codex/config-reference, …/codex/config-advanced
- Codex AGENTS.md discovery — developers.openai.com/codex/guides/agents-md
- Claude Code headless mode — code.claude.com/docs/en/headless
- Claude Code credential precedence — code.claude.com/docs/en/authentication; env key over subscription is intentional — support.claude.com/en/articles/12304248
- Claude Code CLI reference — code.claude.com/docs/en/cli-reference
- Claude Code permission modes — code.claude.com/docs/en/permission-modes
- OpenAI Codex model selection and effort/latency tradeoffs — developers.openai.com/codex/models
- OpenAI long-running/background response guidance — platform.openai.com/docs/guides/background
- Anthropic model comparison and effort controls — docs.anthropic.com/en/docs/about-claude/models/overview; platform.claude.com/docs/en/build-with-claude/effort
- METR time-horizon methodology (human-equivalent task difficulty, not agent runtime) — metr.org/time-horizons
- Tail-based timeout practice — aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter; sre.google/sre-book/addressing-cascading-failures/

Issues and reports underpinning specific claims:

- `--dangerously-skip-permissions` hangs headless on its consent dialog — anthropics/claude-code#52506 (also #52501)
- Nested-session refusal on inherited `CLAUDECODE` — anthropics/claude-code#32618 (also #25803)
- macOS Seatbelt ignoring `network_access = true` — openai/codex#10390
- `OPENAI_API_KEY` silently shadowing ChatGPT-plan auth (billing flips / 401, `/status` misleading) — openai/codex#2341, #3367, #20099
- No flag to disable AGENTS.md ingestion — openai/codex#5983, openai/codex#10067
- Self-assessment redaction finding — Todd Orr, "What I Found When Claude Reviewed Codex's Work," May 2026
- Official OpenAI Codex plugin for Claude Code (subprocess-based) — github.com/openai/codex-plugin-cc
