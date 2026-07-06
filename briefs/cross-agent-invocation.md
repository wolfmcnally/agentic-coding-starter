---
title: "Cross-Agent CLI Invocation — Best Current Practices"
date: 2026-06-03
status: methodology
scope: BCPs for invoking one coding-agent CLI from inside another (Claude Code ↔ Codex CLI), and the design rationale for the per-role model/venue feature (harness-aware cross-vendor review and pinning).
---

# Cross-Agent CLI Invocation — Best Current Practices

This brief pins the researched best current practices (as of mid-2026) for invoking OpenAI's `codex` CLI from inside Claude Code and Anthropic's `claude` CLI from inside Codex, so future work cites a stable position instead of re-deriving it. It also records the design rationale for **cross-harness review** — now delivered as the shipped default of the per-role model/venue feature governed by [`policies/role-models.md`](../policies/role-models.md).

Both vendors sanction this interop: OpenAI ships an official Claude Code plugin that delegates to the local Codex CLI, and both CLIs document headless scripting modes. Every mature published pattern is **subprocess-first** — shelling out to the other CLI — rather than MCP-bridged. MCP wrappers exist but add a moving part without changing the fundamentals; for bounded, one-shot delegations the subprocess is the de-facto standard.

## 1. Why cross-harness review

- **Cross-vendor review catches more.** A model reviewing its own output misses the failure classes it generates. The strongest published experience report (Orr, May 2026) found the bigger lever is *framing*: handing the reviewer a cold artifact (raw diff + requirements, no implementer narrative) produced ~9.4 mean findings vs 2.4–4.0 when the implementer's self-assessment was included — a 3–4× difference — and critical-severity tagging roughly halved with even mild framing.
- **Review roles are read-only by construction.** Our `plan-reviewer` and `code-critic` tool stances (Read, Grep, Glob) map directly onto the external CLIs' sandboxed read-only modes. The external reviewer physically cannot contend for the working tree.
- **The verdict contract already fits.** The methodology's `## Verdict: APPROVED` / `## Verdict: REVISE` string-match contract is exactly the sentinel-string loop-control pattern the ecosystem converged on independently.
- **Instruction parity is automatic.** Codex auto-ingests `AGENTS.md` (→ `CLAUDE.md` via symlink); `claude` auto-loads `CLAUDE.md`. An external reviewer invoked from the repo root is bound by the same policies, invariants, and verdict contract as a native subagent, with no extra plumbing.

## 2. Claude Code → `codex` (headless)

Canonical invocation shape (review roles):

```
env -u OPENAI_API_KEY -u CODEX_API_KEY codex exec --json -s read-only -c 'approval_policy="never"' -C "$(pwd)" --output-last-message "$MSGFILE" "$(cat "$PROMPTFILE")" >"$EVENTS" 2>/dev/null </dev/null
```

Capture the session id for revision rounds from the first event on stdout (the human-readable mode prints it *only* to stderr, which the recipe discards — without `--json` the id is unrecoverable):

```
TID=$(grep -m1 '"thread.started"' "$EVENTS" | grep -ioE '[0-9a-f-]{36}')
```

The verdict is still read from `$MSGFILE` (the `--output-last-message` artifact populates normally under `--json`); `$EVENTS` exists only to recover the `thread_id`.

Flag-by-flag rationale:

- **`codex exec`** is the non-interactive entry point (alias `codex e`). Prompt as argument, or `-` to read stdin.
- **Redirect stdin from `/dev/null` (`</dev/null`) — mandatory for any non-interactive or backgrounded parent.** Even with the prompt passed as an argument, `codex exec` *also* reads stdin (it appends piped stdin to the prompt) and, when stdin is an open non-TTY pipe that never sees EOF, blocks on `Reading additional input from stdin...` until the wall-clock timeout kills it — discarding the whole call. A foreground interactive shell closes stdin so the bug stays hidden; a backgrounded call (a harness that detaches a long-running command) leaves stdin open and hangs deterministically. `</dev/null` gives an immediate EOF so codex proceeds. Empirically verified: a backgrounded code-review call hung on that exact stderr line and was killed at the 900 s guard; the identical recipe run in the foreground had succeeded, which is why the trap survived several rounds before being caught. The redirect is free and correct in every context, so it is unconditional.
- **Approvals must be pinned off.** Any approval prompt in a no-TTY context can block indefinitely; there are verified field reports of approval-state races freezing a session for ~10 minutes *while holding the git index lock*. A headless call must never be able to prompt. Use the **`-c 'approval_policy="never"'` config override** rather than the `-a/--ask-for-approval` flag: `exec` flag surfaces churn across versions (codex-cli 0.136.0's `exec` rejects `-a` outright — empirically verified on this template's first smoke test — while `-c` dotted-path overrides parse everywhere). When a flag-parse error occurs anyway, `codex exec --help` is the in-environment truth.
- **`-s read-only` (`--sandbox read-only`)** matches the reviewer tool stance and makes working-tree contention impossible. Use `workspace-write` only when the external agent must edit (not the case for review). `--full-auto` is deprecated; `--dangerously-bypass-approvals-and-sandbox` (`--yolo`) is for already-isolated containers only — it exposes the user's `~/.codex/auth.json` to anything in the repo.
- **`--output-last-message <file>` (`-o`) is the verdict-capture contract.** The file artifact is the robust way to capture the final agent message; gate on it. Under `--json` (which the recipe requires for session-id capture, below) stdout carries the JSONL event stream rather than the bare final message, so it is redirected to a separate `$EVENTS` file; the verdict still comes from the `-o` artifact, not from stdout. Suppress stderr noise with `2>/dev/null`.
- **`--json` is mandatory, not optional, when revision rounds may follow** (the cross-harness review case). It is the *only* way to capture the session id programmatically: the first stdout event is `{"type":"thread.started","thread_id":"<uuid>"}`. The human-readable mode prints `session id: <uuid>` to **stderr** alone — and the recipe pipes stderr to `/dev/null`, so without `--json` the id is structurally unrecoverable and every revision round is forced to spawn a fresh cold context. This was a real defect in the first cut of this recipe, reproduced deterministically. (NDJSON also carries `turn.completed` / `turn.failed` and token usage when telemetry matters; `--output-schema <schema.json>` constrains the final message to a JSON Schema when a parseable struct beats prose.)
- **`-C "$(pwd)"`** pins the working directory explicitly.
- **Pass large context via files, not inline.** Write the plan text or `git diff` output to a temp file and reference its path in the prompt. Every published skill does this.
- **Do not hardcode `-m <model>`.** Model names churn rapidly and overloaded models silently reroute; let codex use its configured default. The one exception is a *deliberate* per-role pin ([`policies/role-models.md`](../policies/role-models.md)): the `codex` pin value means codex's own default model, so it still adds **no** `-m` — pinning a role to `codex` selects the harness, not a specific model name. A project that wants a specific codex model would add `-m` and accept the churn risk knowingly.
- **Exit codes are not a documented contract** for `codex exec`. Gate success on three signals together: the `-o` artifact exists and is non-empty, it contains the expected verdict header, and the call returned within a wall-clock timeout.
- **Revision rounds: `codex exec resume <session-id> ...`** preserves the reviewer's context across rounds. **The `resume` subcommand has a different flag surface than `exec` — `-s/--sandbox` and `-C/--cd` do not exist on it** (codex-cli 0.136.0 rejects `-s` with `error: unexpected argument '-s' found`, exit 2 — empirically verified). Set the sandbox through a config override instead, and `cd` into the repo rather than passing `-C` (resume filters recorded sessions by cwd):

  ```
  ( cd "$REPO" && env -u OPENAI_API_KEY -u CODEX_API_KEY codex exec resume "$TID" --json -c 'approval_policy="never"' -c 'sandbox_mode="read-only"' --output-last-message "$MSGFILE" "$(cat "$PROMPTFILE")" >"$EVENTS" 2>/dev/null </dev/null )
  ```

  (`resume` reads stdin exactly as `exec` does, so it carries the same `</dev/null` redirect — the stdin-hang bullet above applies to both subcommands.)

  A naive resume that simply re-uses the original `exec` flags flag-parse-fails and trips the fallback, so a project that captured the id correctly but copied the `exec` flags still lands in a fresh context — the two defects compound. If no session id was captured or resume fails, fall back to a fresh call with the full updated context (correctness over efficiency).
- **Auth precedence trap (mirror of §3's).** An interactive ChatGPT-plan login persists in `~/.codex/auth.json` with token auto-refresh, and subprocess calls reuse it — but a set `OPENAI_API_KEY` silently outranks it, flipping the call to API-key billing (or a 401 on a stale key) while `codex /status` still reports the plan login (openai/codex#2341, #3367, #20099). Hence the recipe's `env -u OPENAI_API_KEY -u CODEX_API_KEY` scrub — free when no key is present, never harms the `auth.json` login. The supported hard backstop is `forced_login_method = "chatgpt"` in `~/.codex/config.toml` (`preferred_auth_method` is a user-invented knob that does nothing). For CI on API auth, pass `CODEX_API_KEY` inline to a single `codex exec` — never a job-level export beside repo-controlled code; for CI on the plan, seed a `codex login`-generated `auth.json` onto the runner and keep the env keys unset.
- **AGENTS.md ingestion.** Codex walks repo root → cwd loading `AGENTS.md` (no flag disables this as of mid-2026). For cross-harness review this is desirable — the reviewer inherits the repo's policies. To *avoid* it (scoped consultations unrelated to the repo), run with `-C` pointed at a scratch directory and pass context via temp files.

## 3. Codex → `claude` (headless)

Canonical invocation shape (review roles):

```
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u ANTHROPIC_API_KEY claude -p "$(cat "$PROMPTFILE")" --permission-mode dontAsk --allowedTools "Read,Grep,Glob" --output-format json --max-turns 50 </dev/null
```

Flag-by-flag rationale:

- **`claude -p` (`--print`)** is headless mode: run the agent loop, print, exit.
- **Redirect stdin from `/dev/null` (`</dev/null`).** Like `codex exec`, `claude -p` can treat a piped stdin as additional prompt input; with the prompt already supplied as the `-p` argument, an open non-TTY stdin from a backgrounded parent is at best useless and at worst a hang. Close it unconditionally — the same trap and the same one-token fix as the codex side (§2).
- **`--permission-mode dontAsk` is the correct headless mode — never `--dangerously-skip-permissions`.** The "dangerous" bypass still parks on a one-time *interactive* consent dialog with no pre-accept flag; with no TTY it hangs forever (anthropics/claude-code#52506). `dontAsk` is fully non-interactive: pre-approved tools run, everything else is *denied* rather than prompted, and protected paths (`.git`, `.claude`, shell rc files) are never auto-approved — exactly the posture a delegated reviewer should have.
- **`--allowedTools "Read,Grep,Glob"`** mirrors the canonical reviewer tool stance. (`AskUserQuestion` is omitted: escalation cannot reach the human through a nested CLI — an unresolved product question becomes a `REVISE` verdict stating the question, which the orchestrator surfaces.)
- **Scrub `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT` from the child environment.** Claude Code sets `CLAUDECODE=1` in every child process and a `claude` launch that sees it refuses to start — even in `-p` mode. Codex itself doesn't set it, but a claude → codex → claude chain inherits it through codex, so the bridge always scrubs.
- **`--output-format json`** returns a structured envelope: `.result` (the text), `.session_id` (for `--resume` in revision rounds), `.total_cost_usd`. `stream-json` additionally requires `--verbose`.
- **`--model <alias|id>` selects the model.** Omit it for the CLI's configured default (the review-role norm). Pass it for a deliberate per-role pin ([`policies/role-models.md`](../policies/role-models.md)): `--model opus` / `--model fable` by alias, falling back to the full ids `claude-opus-4-8` / `claude-fable-5` if an alias is unrecognized in a given CLI version.
- **`--max-turns N`** (and optionally `--max-budget-usd`) are the circuit breakers — print-mode only; use them, but calibrate as runaway guards, not review-depth budgets. A genuine code critique (role file + plan + file list + diff + sources + tests) exceeds 12 turns routinely: field use saw a 12-turn cap kill two real critiques mid-investigation in one evening (`subtype: "error_max_turns"`, `is_error: true`, `stop_reason: "tool_use"`, no verdict emitted). We use 50 — the wall-clock timeout remains the binding guard. On a max-turns death the JSON envelope still carries `session_id` and the investigation is already paid for: `claude --resume <sid> -p "Conclude your review now …"` rescues it in one cheap turn; prefer that over discarding the work into a native re-review.
- **Codex's sandbox blocks subprocess network by default.** A codex-spawned `claude` must reach the Anthropic API; `workspace-write` denies that unless `[sandbox_workspace_write] network_access = true` is set in `~/.codex/config.toml` — and on macOS, Seatbelt has been reported to silently ignore that setting in some versions (openai/codex#10390), requiring a full-access session. **Treat a network failure here as a fallback trigger; do not attempt to repair the sandbox mid-session.**
- **Auth precedence trap.** The documented credential order (code.claude.com/docs/en/authentication) ranks an env `ANTHROPIC_API_KEY` *above* `apiKeyHelper`, `CLAUDE_CODE_OAUTH_TOKEN`, and subscription OAuth — intentionally, per Anthropic's support guidance — and *set does not mean valid*. Claude Code injects a *session-scoped* `ANTHROPIC_API_KEY` into its child processes, so any chain that began in a Claude Code session carries a key that fails direct API auth — the JSON envelope comes back `is_error: true`, `api_error_status: 401`, `"Invalid API key"` — and a stale key can reach even a genuine Codex parent through its inherited environment (field-verified: a derived project's first live Codex → claude plan review failed 401 with no key in any shell rc). Under the subscription auth model an env key is never the intended credential, so the recipe scrubs it unconditionally; the scrub is provably harmless to `apiKeyHelper`, keychain OAuth, and `CLAUDE_CODE_OAUTH_TOKEN` — none of them depend on the env var. For subscription-backed automation without a browser, `claude setup-token` mints a long-lived OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`). Note `--bare` mode skips OAuth/keychain reads entirely and requires an API key; API-key-CI projects re-export the key deliberately in the child env instead of relying on inheritance.
- **CLAUDE.md auto-loading.** A `claude -p` run inside a repo loads the repo's `CLAUDE.md`, hooks, skills, and MCP servers like an interactive session would — desirable for cross-harness review (policy parity), avoidable with `--bare` when a context-free consult is wanted.

## 4. General patterns (direction-independent)

- **Redact the implementer's self-assessment** from review handoffs. Pass the raw artifact (plan text; diff or, for large changes, the changed-file list + `git diff --stat`) and the requirements, adversarially framed ("assume the implementer was careful but missed something"). Never include "all tests pass" or the coder's build-status narrative — it measurably degrades review depth (§1).
- **Hand the reviewer a map, not a payload — and never reject the venue on diff size.** The external reviewer runs against a read-only checkout with its own Read/Grep (same as the native subagent). So the handoff for a large change is the changed-file list + `git diff --stat`, from which it pulls the files it wants; inline a full diff only when it is small enough to read whole. The failure to avoid: computing `git diff | wc -c`, seeing hundreds of KB, and falling back to native *without ever making the external call* — conflating an on-disk artifact with tokens-in-the-context-window. A reviewer never loads the whole diff at once. Delegation is discarded only on the three-signal gate (missing artifact, malformed verdict, timeout/error), never on a pre-computed size estimate. Flag machine-regenerated blobs (fixtures, snapshot JSON, lockfiles) as "spot-check, don't read line-by-line" so a diff dominated by regenerated data doesn't *read* as unreviewably big. (Observed: a large, fixture-dominated diff pre-rejected on byte count with zero external calls; and, symmetrically, an unbounded "read all the sources" plan-review mandate on a big multi-file phase exhausted the external reviewer's own context and tripped a failed internal compaction before any verdict.)
- **Verdict sentinel.** Require the reviewer to end with the exact verdict header; parse by string match; treat a missing/malformed verdict as a failed invocation, not a lenient pass.
- **Bound revision rounds by convergence.** Unbounded agent-to-agent loops burn quota and don't converge; iterate only while the reviewer's objections are narrowing, and surface to the human the moment the loop stalls or diverges. A generous numeric backstop catches pathological loops regardless. (Ours: convergence judgment under a 5-cycle runaway backstop, per [`policies/four-canonical-agents.md`](../policies/four-canonical-agents.md).)
- **Recursion depth guard.** Claude's `CLAUDECODE` guard only stops claude→claude nesting. Cross-vendor chains need an explicit guard: set a depth-marker env var (ours: `KICKOFF_DELEGATION_DEPTH=1`) in the child environment and refuse external delegation when it is already set.
- **Scrub API-key env vars at every cross-CLI call site (subscription auth model).** Both CLIs rank an environment API key above their subscription OAuth, so an inherited stray key silently flips auth (and billing) or fails 401 — and the CLIs' own status displays don't reliably reveal which credential is live. `env -u <KEY>` at the call site costs nothing when no key is present and never breaks login-based auth. Do not rely on the parent's hygiene: Codex's default `shell_environment_policy` strips `*KEY*`/`*SECRET*`/`*TOKEN*` from the environment it hands its children, but Claude Code forwards the full environment *and adds* its own session `ANTHROPIC_API_KEY` — scrub at your own spawn point regardless of who launched you.
- **Reviewer is read-only; never two writers on one tree.** If an external agent must write, serialize or isolate; for review there is no reason to allow writes at all. The one write-enabled cross-harness role is a *pinned coder* ([`policies/role-models.md`](../policies/role-models.md)): it uses `-s workspace-write` (codex) / `--allowedTools "…,Write,Edit,Bash"` (claude), and the single-writer rule is satisfied by serialization — `/kickoff` runs the coder stage with no concurrent native writer, so the pinned coder owns the tree exclusively. The macOS Seatbelt `network_access` trap (§3) applies to a workspace-write child that must reach its vendor API; treat that network failure as a fallback trigger.
- **Wall-clock timeouts on every external call.** Neither CLI's exit codes are a sufficient contract; a hung subprocess must not hang the orchestrator.
- **Cost awareness.** Each external call is a full agent loop on the user's other-vendor quota. Bounded calls (capped turns, capped rounds) only; never unbounded polling loops.

## 5. How this maps onto our methodology

These BCPs are applied by the per-role model/venue feature ([`policies/role-models.md`](../policies/role-models.md)). Its shipped default is cross-vendor review: at Step 4 (plan review) and Step 6 (code critique), the read-only reviewer roles run in the *other* harness. But the same machinery routes *any* of the four roles to any harness/model — the planner and coder too (the coder write-enabled). Whatever the venue, the CLI is told to read the *same canonical role file* the native subagent uses: one role definition, many execution venues. Resolution, fallback, and reporting are prescribed by [`policies/role-models.md`](../policies/role-models.md). Orchestration and build gates are never delegated — they always run on the invoking session's model.

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

Issues and reports underpinning specific claims:

- `--dangerously-skip-permissions` hangs headless on its consent dialog — anthropics/claude-code#52506 (also #52501)
- Nested-session refusal on inherited `CLAUDECODE` — anthropics/claude-code#32618 (also #25803)
- macOS Seatbelt ignoring `network_access = true` — openai/codex#10390
- `OPENAI_API_KEY` silently shadowing ChatGPT-plan auth (billing flips / 401, `/status` misleading) — openai/codex#2341, #3367, #20099
- No flag to disable AGENTS.md ingestion — openai/codex#5983, openai/codex#10067
- Self-assessment redaction finding — Todd Orr, "What I Found When Claude Reviewed Codex's Work," May 2026
- Official OpenAI Codex plugin for Claude Code (subprocess-based) — github.com/openai/codex-plugin-cc
