# Policy: Per-Role Model Pinning

Each of the four canonical roles ([`four-canonical-agents.md`](four-canonical-agents.md)) — planner, reviewer, coder, critic — may be **pinned to a specific model/harness**. When a role is pinned, `/kickoff` always invokes that harness's CLI with that model for the role, using the cross-harness invocation recipes ([`cross-harness-review.md`](cross-harness-review.md), [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md)). When a role is unpinned it keeps the current behavior. **Orchestration and build gates — the `/kickoff` main loop itself — always run on the current session's model and are never pinnable.**

This generalizes cross-harness review. That policy makes the *venue* of the two reviewer roles configurable; this policy makes the *(harness, model)* of *all four* roles configurable, and is the mechanism the cross-harness-review policy anticipated when it noted that "projects that pin models per role should route the reviewer roles to a different model family from the coder."

## Why pin at all

Review decorrelation ([`cross-harness-review.md`](cross-harness-review.md)) is one reason: a critic on a different model family from the coder catches failure classes a same-family critic shares blind spots on. But pinning is broader — a project may want a cheaper/faster model for mechanical planning, the strongest available model for implementation, or a specific vendor for a role for any reason. The template does not prescribe *which* pins are wise; it provides the mechanism and the safe defaults.

## The config file

Pins live in a dedicated file **`role-models.yaml` at the repo root**, owned by `bin/role-models` and set through the `/roles` skill. It is a small YAML mapping — one `role: model` entry per line, `#` comments:

```
planner: fable
reviewer: codex
coder: opus
critic: fable
```

- **Roles:** `planner` → `phase-planner`, `reviewer` → `plan-reviewer`, `coder` → `phase-coder`, `critic` → `code-critic`.
- **Models (current vocabulary):**
  - `default` — native: the current `/kickoff` session's model. The unpinned default for every role.
  - `opus`, `fable` — Claude Code harness (`claude --model opus` / `claude --model fable`; fall back to the full ids `claude-opus-4-8` / `claude-fable-5` if an alias is unrecognized).
  - `codex` — Codex harness (`codex` with **no** `-m` flag — its configured default, i.e. "the most recent codex").

A missing file, a missing line, or `default` all mean unpinned. The file is a
dedicated machine-owned surface deliberately — *not* a token in `CLAUDE.md`
Project Context like `cross-harness-review:` — because a script rewrites it
repeatedly and it must not disturb the human-authored prose zone `/stamp`
rewrites. The vocabulary is closed: `bin/role-models` rejects any role or model
outside the sets above non-zero and leaves the file unchanged.

Extending the vocabulary (a new supported model) is a deliberate edit to
`bin/role-models`' `MODELS` list, this policy's model table, and the `/roles`
skill's vocabulary — kept in lockstep in one commit.

## Mechanistic/intelligence seam

Per [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md), the parse-validate-write is **mechanistic** and lives in `bin/role-models` (deterministic, idempotent, harness-portable, testable). The `/roles` skill is the thin intelligence wrapper: it resolves a possibly-vague request ("put the coder on the big model") into concrete `role: model` pairs, then shells out to the script. No model does the writing.

## Resolution (kickoff Step 0a)

Resolved **once per session**, before phase work, per role. This subsumes the review-venue resolution in [`cross-harness-review.md`](cross-harness-review.md):

1. **Recursion guard.** If `KICKOFF_DELEGATION_DEPTH` is set, this session is *itself* a delegated role invoked by an outer `/kickoff`; **every role runs native** and no further delegation happens. Skip the rest.
2. **Read `role-models.yaml`.** For each role:
   - **Pinned** (`opus` / `fable` / `codex`) → the role runs on that harness/model via the CLI recipe. A pin on `reviewer` or `critic` **overrides** the `cross-harness-review:` token for that role.
   - **Unset / `default`** → current behavior: `planner` and `coder` run **native** (in-harness subagents on the session model); `reviewer` and `critic` follow the `cross-harness-review:` token + harness detection + PATH resolution.
3. **CLI availability.** A pinned role whose target harness CLI is not on PATH resolves to **native**, and the role is flagged for 🚨 disconnect surfacing (§ Fallback) — the pin was requested but could not be honored.

Resolution deliberately does **not** try to detect "the pin equals the session model" and skip the CLI. A pinned role *always* goes through the CLI recipe — uniform, deterministic, and free of fragile session-model probing. The cost of an occasional redundant subprocess is accepted in exchange for a resolution rule with no special cases.

## Invocation, resume, and the write-enabled coder

Pinned **read-only** roles (planner, reviewer, critic) use the read-only recipes from [`cross-harness-review.md`](cross-harness-review.md) with the model flag added (`claude --model <m>` / `codex` with no `-m`) and `--allowedTools` mirroring the role's tool stance (planner keeps `WebSearch,WebFetch`; reviewer/critic keep `Read,Grep,Glob`).

The pinned **coder** writes, so it uses a **write-enabled** variant:

- **claude coder:** `--allowedTools "Read,Grep,Glob,Write,Edit,Bash"`, a higher `--max-turns` (an implementation loop, not a review), `--model <m>`, otherwise the same `--permission-mode dontAsk`, env scrubs, and `</dev/null` redirect. Protected paths (`.git`, `.claude`) stay non-auto-approved under `dontAsk`; the coder writes under the deliverable directory.
- **codex coder:** `-s workspace-write` on the initial call / `-c 'sandbox_mode="workspace-write"'` on resume, `approval_policy="never"`, no `-m`, the same scrubs and `</dev/null`. **Never** `--yolo` / `danger-full-access`.

**Single-writer guarantee.** `/kickoff` is sequential; during the coder's stage the orchestrator runs no concurrent native writer, so the pinned coder owns the tree exclusively (build gates run afterward, in the orchestrator). This satisfies the "serialize or isolate — never two writers on one tree" rule in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md) §4 without a worktree.

**Session resume across a phase.** A pinned role invoked more than once in a phase — the planner across plan-revision rounds, the coder across code-revision and build-fix rounds — **resumes the same session** so its prior context stays live, exactly as the reviewer roles already do: capture the session id (codex `thread_id` via `--json`; claude `.session_id`), thread the latest id forward, re-capture each round, and honor the codex `resume` flag-surface trap (`-s`/`-C` rejected → `-c 'sandbox_mode=…'` + `cd`). Details in [`cross-harness-review.md`](cross-harness-review.md) "Revision cycles across harnesses".

**Recursion guard.** Every delegated child — read-only or write-enabled — runs with `KICKOFF_DELEGATION_DEPTH=1` in its environment, so a delegated role that itself reads this config never re-delegates (step 1 above). The guard is shared with cross-harness review ([`cross-harness-review.md`](cross-harness-review.md)); it is named for delegation generally because it guards every delegated role, not just review.

## Fallback and 🚨 disconnect surfacing

A pinned role falls back to **native (the session model)** — and the phase proceeds — on any of: the target CLI absent at Step 0a; the three-signal gate failing (empty artifact, malformed/absent expected output, or wall-clock timeout); or a sandbox network failure (the macOS Seatbelt `workspace-write` network trap — treat as a fallback trigger, never repair the sandbox mid-run). Fallback is never a phase failure.

Because a fallback means **what ran ≠ what was pinned**, the disconnect must be made loud, not buried:

- **`LOG.md` END block** records each role's resolved model/venue plus `[fallback: <reason>]`.
- **The user-facing `/kickoff` summary** carries a 🚨 line per disconnect, e.g. `🚨 coder pinned to opus but ran native (codex CLI not on PATH) — output was NOT produced by opus`. A clean run (every pinned role ran on its pin) shows no 🚨.

The human must be able to see, at a glance, when a pin they set did not take effect.

## Propagation

`/roles`, `bin/role-models`, this policy, and a default (all-`default`) `role-models.yaml` are **universal** — `/stamp` carries them into every derived project, and `/teach` can port them. Every project has the same four roles and may want to pin them. The *values* are per-project state (seeded all-`default`, like the `cross-harness-review:` token is seeded `enabled`); the *machinery* is methodology.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) owns the roles, names, tool stances, and verdict headers; this policy pins their model/harness without changing any of that.
- [`cross-harness-review.md`](cross-harness-review.md) owns the invocation recipes, the fallback state machine, and the reviewer-venue default; a role pin overrides its token for that role, and its recipes are reused (plus a model flag) for every pinned role.
- [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md) governs the script/skill seam.
- [`human-in-the-loop.md`](human-in-the-loop.md) is unaffected: no pinned model may commit, advance gates, or claim subjective acceptance. The human decides done, whichever model ran.
