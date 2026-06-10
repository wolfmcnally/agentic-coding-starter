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

The roles, names, tool stances, and verdict headers above are fixed. The **execution venue** of the two reviewer roles is not: when cross-harness review is enabled ([`cross-harness-review.md`](cross-harness-review.md)), `/kickoff` may run `plan-reviewer` and `code-critic` in the *other* harness's CLI (`codex` from Claude Code, `claude` from Codex). The external venue reads the same canonical `.claude/agents/<role>.md` file, honors the same tool stance, and emits the same verdict headers — only where the role executes changes. `phase-planner` and `phase-coder` always run in the invoking harness. Do not assume the reviewers run as in-harness subagents when reasoning about orchestration.

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

`/kickoff` enforces a bound on revision cycles:

- **Plan review**: up to 2 revision cycles (planner → reviewer → planner → reviewer → planner). Beyond that, surface to the human.
- **Code review**: up to 2 revision cycles. Beyond that, surface to the human.
- **Build-gate failure**: up to 3 fix cycles. Beyond that, surface to the human.

These bounds are deliberate. The methodology assumes a human in the loop ([`human-in-the-loop.md`](human-in-the-loop.md)); when the agents can't converge in a small number of attempts, the right answer is to ask the human, not to keep iterating.

## Adding a fifth agent

This policy does not forbid project-specific agents — a project may add a `database-migration-reviewer` or an `audio-perceptual-judge` agent as needed. But:

- The fifth agent must not replace one of the four canonical roles.
- `/kickoff` does not invoke it automatically. Either the fifth agent is called from a different skill, or `/kickoff` is customized for the project to call it at a specific point in the cycle.
- Its name should be unambiguous (e.g., `migration-reviewer`, not `reviewer`).
