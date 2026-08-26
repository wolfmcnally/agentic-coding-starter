# Policy: The Four Canonical Agents

The methodology's orchestrator (`kickoff`) delegates one phase of work to four specialist agents. Their names are load-bearing: `kickoff` invokes them by name. A typo silently breaks the orchestration.

## The four roles

| Role            | Canonical file                                        | Tools allowed                                     | Writes code |
| --------------- | ----------------------------------------------------- | ------------------------------------------------- | ----------- |
| `phase-planner` | `.claude/agents/phase-planner.md`                     | Read, Grep, Glob, WebSearch, WebFetch             | No          |
| `plan-reviewer` | `.claude/agents/plan-reviewer.md`                     | Read, Grep, Glob, WebSearch, WebFetch, AskUserQuestion | No      |
| `phase-coder`   | `.claude/agents/phase-coder.md`                       | Read, Write, Edit, Grep, Glob, Bash, WebFetch     | Yes         |
| `code-critic`   | `.claude/agents/code-critic.md`                       | Read, Grep, Glob, WebFetch                        | No          |

The Codex mirrors live at `.codex/agents/<role>.toml`. See [`cross-harness-parity.md`](cross-harness-parity.md) for the parity contract.

## Execution venue

The roles, names, tool stances, and verdict headers above are fixed. The **execution venue** — which model and implied harness runs a role — is not, and is governed by [`role-models.md`](role-models.md): `kickoff.yaml`'s harness-aware `role_models` section (edited directly or via `roles`) resolves any role to separate model and optional effort fields, scoped by which harness orchestrates. A role resolving to a CLI runs there while reading the same canonical role file and honoring the same contract; only where it executes changes. The shipped default runs `plan-reviewer` + `code-critic` in the other harness; planner and coder can be routed too.

Each invocation or revision round is also bounded by the role-specific first-event, idle-progress, and hard-deadline values in [`role-timeouts.md`](role-timeouts.md). Claude CLI roles additionally use its configured turn circuit breaker; Codex and native roles expose no equivalent flag. Those guards limit one run; the convergence rules below limit the number of runs.

Research is a second role-bound axis governed by
[`research-authority.md`](research-authority.md). Planner and reviewer may
originate search and retrieval; coder and critic may retrieve approved
authorities but may not originate discovery. Installed MCP servers and plugins
are available by default unless a project or phase explicitly narrows them.

So do **not** assume any role runs as an in-harness subagent on the session model when reasoning about orchestration — check the resolved venue. The one invariant: **orchestration and build gates always run on the invoking session's model** and are never pinnable.

Every lane closes with two orchestrator-owned gates. The
**implementation-candidate gate** follows code-critic approval and binds the
unchanged reviewed implementation. The bare **handoff gate** follows every
tracked status, ripple, lesson, END, and report write; no tracked write follows
it. Delivery — the ordinary commit and non-force push of gate-proved work
([`human-in-the-loop.md`](human-in-the-loop.md)) — is likewise
orchestrator-only: it happens after the handoff gate, and no delegated role
ever commits or pushes.

## Execution cadence: review lanes

Whether *both* reviewer roles run on a phase's initial implementation is governed by [`review-lanes.md`](review-lanes.md). The default `full` lane runs all four roles; a `light` lane (mechanical phases only, declared in the phase file's frontmatter) skips the initial `plan-reviewer` invocation and gives `code-critic` one additional duty — judging whether the work actually stayed mechanical, with an `Escalate: full lane — <reason>` Required Change when it did not. The code critic runs on every initial implementation. Later test- or user-driven corrections may use a direct-fix or coder-only route when both risk and change size are low; this omits an invocation, not a role from the canonical set.

## What each role does

- **`phase-planner`** — Reads the phase file, the briefs it references, the policies, and the existing repo, and produces a concrete file-level implementation plan. Does not write code. Output: a markdown plan with named files, named types/functions, an Implementation Order, a Build Gate Sequence, Open Questions, and Process Observations.

- **`plan-reviewer`** — Reads the same authorities plus the planner's output and may independently research uncertain or volatile claims. Issues a single verdict (`APPROVED` or `REVISE`) at the top of its response and records Process Observations separately from phase findings. May call `AskUserQuestion` to escalate decisions only the human can make.

- **`phase-coder`** — Reads the approved plan and implements it. May retrieve resources the plan or briefs identify, but does not originate research. Runs the build gates. Reports files created/modified, the build-status block, Process Observations, and — on revision rounds — root-cause Failure Analysis in both its human report and Change Evidence.

- **`code-critic`** — Reads the approved plan, the briefs and policies it cites, and the code diff. May retrieve those authorities and their same-host structural neighbors, but does not originate research. Issues a single verdict (`APPROVED` or `REVISE`) and records Process Observations separately from code findings. Does not rewrite the implementation; only reviews it.

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

`kickoff` parses the verdict by matching the first occurrence of one of those two strings. Any deviation — different casing, a missing colon, a wrapped section — breaks orchestration.

## Revision loops

The first review batches every blocking finding. Plan-review findings receive
stable `PLAN-FNNN` ids; code-review findings receive `CODE-FNNN` ids. Their
states and candidate identities live in the finding ledger governed by
[`orchestration-evidence.md`](orchestration-evidence.md).

`kickoff` keeps iterating a review or fix loop only while it is **converging on
approval**, and escalates to the human the moment it stalls or diverges. After
each cycle the orchestrator evaluates exact finding transitions rather than
reconstructing continuity from prose:

- **Converging — continue.** At least one blocking finding advances from
  `open` toward `closed`, open severity or uncertainty falls, and no closed
  finding reopens at equal or greater severity.
- **Stalled or diverging — escalate.** A finding returns to `open`, a fix
  creates an equal-or-higher-severity regression, the loop oscillates, a
  finding rests on unresolved product/architecture authority, or two
  consecutive rounds reduce neither open severity nor uncertainty. Surface
  the ledger history and sticking point to the human.

After the first full pass, a revision reviewer receives the prior ledger, the
candidate-bound revision packet, mapped verification, and the new candidate
id. It resolves prior findings first and then checks the causal change surface.
New findings are classified `introduced-by-revision`,
`newly-exposed-by-resolution`, or `missed-in-full-pass`. A prior finding that
remains actionable keeps the evidence it was opened with; a reviewer that sees
a further defect once the stated one is repaired opens a new id under one of
those three classifications rather than re-aiming the old one, and
`bin/kickoff-evidence` refuses the substitution. (Observed across three
projects in one month: a stable id carrying a different objection in each of
four rounds, every round classified `initial`, so the ledger showed one
persistent finding where there were four consecutive misses.) A finding that
rests on a decision only the operator can make — a product, architecture,
authorization, or custody call — enters the ledger as `blocked-owner` and
routes to the operator; sending it back to the planner as `REVISE` loops until
someone notices.

The code loop adds four rules of the same kind, each from the month's
code-review record:

- **The threat model is an authority, not a reviewer's imagination.** A
  critic may require the code to withstand only the actors, failures, and
  capabilities a phase file, brief, or policy names. A defense against
  anything else — the repository's own code forging its evidence, a same-user
  process ignoring the protocol lock — is an owner question recorded as
  `blocked-owner`, never `blocking`. (Five blocking findings of this shape
  survived attempts up to nine in one derived project before the owner
  amended the threat model and all five were superseded.)
- **A non-finding is not a finding.** "None required", "optional", and
  "outside this phase" belong in Process Observations or a follow-up note;
  the batch carries only findings with a required change.
- **The coder may refuse with evidence.** A finding the coder can refute
  returns as `rejected-with-evidence` with the refuting observation; the
  critic accepts it or reopens with counter-evidence. In 328 findings over a
  month the transition was used zero times while coders implemented
  non-requirements to make findings go away.
- **No unverified handoff.** The coder's Change Evidence states whether the
  plan's focused sequence ran (`gate_status`); when it did not, the
  orchestrator runs it natively before the critic is dispatched. Code whose
  focused gate never ran anywhere is not reviewed. Authority/scope drift,
a new risk class, public API or persisted-state changes, security, concurrency,
irreversible-state boundaries, broad change dispersion, an invalidated
acceptance claim, or lost trustworthy continuity rebases to a complete review.

The same judgment governs the full review loops:

- **Plan review** (planner → reviewer): continue while the reviewer's objections are narrowing; escalate when they stall.
- **Code review** (coder → critic): continue while findings shrink in count and severity; escalate on recurrence or whack-a-mole.
- **Full-cycle build-gate failure** (coder → critic → gate): converging means each fix knocks down failures and review findings; stalled means the same failure recurs or each fix trades one break for another.

Low-risk, bounded follow-up corrections do not enter a review loop by default. They get one direct-fix or coder-only attempt with focused and touched-surface validation. A failed attempt upgrades to the full loop above; see [`review-lanes.md`](review-lanes.md).

**Runaway backstop.** Independent of the convergence read, no single loop runs past **10 cycles** without surfacing to the human. This is a circuit breaker against runaway iteration, not a work quota — the same philosophy as the `--max-turns` cap in [`role-timeouts.md`](role-timeouts.md): a healthy converging loop almost never reaches it, and a loop that does has by definition failed to converge. When the backstop trips, escalate exactly as for a stall. (Raised from 5 by operator directive in a derived project, 2026-08-13: a loop should stop only when it is not converging in a way that seems reasonable and tractable and root-cause attempts are not yielding breakthroughs — that judgment call belongs to the supervising authority below the ceiling; the ceiling exists solely to stop runaway iteration. Motivating case: the 5-cycle trip landed one cycle before the genuine root cause, though the trip also forced the register change that found it.)

**Convergence-lease grants.** When the operator extends a loop beyond its defaults, the extension is scoped by convergence invariants, not cycle counts. Counts measure effort spent, not whether the loop is still healthy, so count-scoped grants expire mid-convergence and page the operator to re-authorize work that never stopped working. A lease reads: *continue while every cycle strictly shrinks the open-finding set, no closed finding reopens at equal or worse severity, no new defect class appears, and touched paths stay inside a named surface; park immediately on any violation, any guard trip, or at a hard ceiling.* An out-of-band supervisor may judge the lease's convergence invariants, and below the hard ceiling the supervisor's discretion decides whether another cycle is worth the effort — the criteria are convergence tractability and whether root-cause attempts are yielding breakthroughs, not counts; the hard ceiling and any *tripped* runaway backstop remain operator-only to reset. (Motivating incidents, 2026-08-11, in the same derived project: three count-scoped micro-grants in one day — a backstop reset, a scoped completion grant, and a "+2 cycles if necessary" — each an operator round-trip during their absence, all while the finding trajectory was strictly shrinking; two of the phase's three parks and three relays traced to count expiry rather than to any defect.)

These bounds are deliberate. The methodology assumes a human in the loop ([`human-in-the-loop.md`](human-in-the-loop.md)); the goal is to spend revision cycles only while they are buying convergence, and to hand a genuinely stuck decision to the human rather than grind identical objections — or burn the whole backstop — against a wall.

## Adding a fifth agent

This policy does not forbid project-specific agents — a project may add a `database-migration-reviewer` or an `audio-perceptual-judge` agent as needed. But:

- The fifth agent must not replace one of the four canonical roles.
- `kickoff` does not invoke it automatically. Either the fifth agent is called from a different skill, or `kickoff` is customized for the project to call it at a specific point in the cycle.
- Its name should be unambiguous (e.g., `migration-reviewer`, not `reviewer`).
