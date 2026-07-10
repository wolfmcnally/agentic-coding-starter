# Policy: The Four Canonical Agents

The methodology's orchestrator (`/kickoff`) delegates one phase of work to four specialist agents. Their names are load-bearing: `/kickoff` invokes them by name. A typo silently breaks the orchestration.

## The four roles

| Role            | Canonical file                                        | Tools allowed                                     | Writes code |
| --------------- | ----------------------------------------------------- | ------------------------------------------------- | ----------- |
| `phase-planner` | `.claude/agents/phase-planner.md`                     | Read, Grep, Glob, WebSearch, WebFetch             | No          |
| `plan-reviewer` | `.claude/agents/plan-reviewer.md`                     | Read, Grep, Glob, AskUserQuestion                 | No          |
| `phase-coder`   | `.claude/agents/phase-coder.md`                       | Read, Write, Edit, Grep, Glob, Bash               | Yes         |
| `code-critic`   | `.claude/agents/code-critic.md`                       | Read, Grep, Glob                                  | No          |

The Codex mirrors live at `.codex/agents/<role>.toml`. See [`cross-harness-parity.md`](cross-harness-parity.md) for the parity contract.

## Execution venue

The roles, names, tool stances, and verdict headers above are fixed. The **execution venue** — which model and implied harness runs a role — is not, and is governed by [`role-models.md`](role-models.md): `kickoff.yaml`'s harness-aware `role_models` section (edited directly or via `/roles`) resolves any role to separate model and optional effort fields, scoped by which harness orchestrates. A role resolving to a CLI runs there while reading the same canonical role file and honoring the same contract; only where it executes changes. The shipped default runs `plan-reviewer` + `code-critic` in the other harness; planner and coder can be routed too.

Each invocation or revision round is also bounded by the role-specific first-event, idle-progress, and hard-deadline values in [`role-timeouts.md`](role-timeouts.md). Claude CLI roles additionally use its configured turn circuit breaker; Codex and native roles expose no equivalent flag. Those guards limit one run; the convergence rules below limit the number of runs.

So do **not** assume any role runs as an in-harness subagent on the session model when reasoning about orchestration — check the resolved venue. The one invariant: **orchestration and build gates always run on the invoking session's model** and are never pinnable.

## Execution cadence: review lanes

Whether *both* reviewer roles run on a given phase is governed by [`review-lanes.md`](review-lanes.md). The default `full` lane runs all four roles; a `light` lane (mechanical phases only, declared in the phase file's frontmatter) skips the `plan-reviewer` invocation and gives `code-critic` one additional duty — judging whether the work actually stayed mechanical, with an `Escalate: full lane — <reason>` Required Change when it did not. The role definitions, tool stances, and verdict headers are identical in both lanes. The code critic is never skipped in any lane.

## What each role does

- **`phase-planner`** — Reads the phase file, the briefs it references, the policies, and the existing repo, and produces a concrete file-level implementation plan. Does not write code. Output: a markdown plan with named files, named types/functions, an Implementation Order, a Build Gate Sequence, and an Open Questions section.

- **`plan-reviewer`** — Reads the same authorities plus the planner's output. Issues a single verdict (`APPROVED` or `REVISE`) at the top of its response. May call `AskUserQuestion` to escalate decisions only the human can make.

- **`phase-coder`** — Reads the approved plan and implements it. Runs the build gates. Reports files created/modified and the build-status block.

- **`code-critic`** — Reads the approved plan, the briefs and policies it cites, and the code diff. Issues a single verdict (`APPROVED` or `REVISE`). Does not rewrite the implementation; only reviews it.

## Verdict headers

Both reviewers (`plan-reviewer` and `code-critic`) end with a verdict block whose first line is exactly one of:

```markdown
## Verdict: APPROVED
```

or

```markdown
## Verdict: REVISE
```

Followed in the `REVISE` case by a `### Required Changes` section listing specific, actionable changes.

`/kickoff` parses the verdict by matching the first occurrence of one of those two strings. Any deviation — different casing, a missing colon, a wrapped section — breaks orchestration.

## Revision loops

`/kickoff` keeps iterating a review or fix loop only while it is **converging on approval**, and escalates to the human the moment it stalls or diverges — rather than counting to a fixed cap. After each cycle the orchestrator compares the new verdict against the prior one and judges the trend:

- **Converging — continue.** The set of Required Changes is shrinking, their severity is trending down (blocking → minor → nit), each round resolves prior findings without raising equal-or-worse new ones, and the reviewer's verdict is moving toward approval.
- **Stalled or diverging — escalate.** The same finding recurs across rounds (the fix didn't take, or the reviewer keeps re-raising it); new findings of equal or greater severity keep appearing (whack-a-mole); the loop oscillates (fixing A re-breaks B); or a finding rests on a product or architecture disagreement the agents cannot resolve among themselves. Surface the cycle history and the sticking point to the human.

The same judgment governs all three loops:

- **Plan review** (planner → reviewer): continue while the reviewer's objections are narrowing; escalate when they stall.
- **Code review** (coder → critic): continue while findings shrink in count and severity; escalate on recurrence or whack-a-mole.
- **Build-gate failure** (coder → gate): converging means each fix knocks down failures and the error surface shrinks; stalled means the same failure recurs or each fix trades one break for another.

**Runaway backstop.** Independent of the convergence read, no single loop runs past **5 cycles** without surfacing to the human. This is a runaway guard, not a budget — the same philosophy as the `--max-turns` cap in [`role-timeouts.md`](role-timeouts.md): a healthy converging loop almost never reaches it, and a loop that does has by definition failed to converge. When the backstop trips, escalate exactly as for a stall.

These bounds are deliberate. The methodology assumes a human in the loop ([`human-in-the-loop.md`](human-in-the-loop.md)); the goal is to spend revision cycles only while they are buying convergence, and to hand a genuinely stuck decision to the human rather than grind identical objections — or burn the whole backstop — against a wall.

## Adding a fifth agent

This policy does not forbid project-specific agents — a project may add a `database-migration-reviewer` or an `audio-perceptual-judge` agent as needed. But:

- The fifth agent must not replace one of the four canonical roles.
- `/kickoff` does not invoke it automatically. Either the fifth agent is called from a different skill, or `/kickoff` is customized for the project to call it at a specific point in the cycle.
- Its name should be unambiguous (e.g., `migration-reviewer`, not `reviewer`).
