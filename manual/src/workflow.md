# Run a Phase

Use a phase to deliver one coherent outcome with explicit acceptance criteria. A phase may touch several files or surfaces. Split it when a consequential decision, independently accepted prerequisite, deployment seam, or human judgment separates the outcomes.

## Select and load the work

`plan/INDEX.md` is the sole status ledger. Its markers mean: ⏳ not started, ⬅️ next, 🚧 in progress, and ✅ completed. `kickoff` owns transitions. To resume active work, name that phase explicitly.

Invoke `kickoff` with no argument to select the next phase, or name a phase. In Claude Code:

```text
/kickoff phase 2
```

In Codex:

```text
$kickoff phase 2
```

The agent reads the index, target and parent when needed, cited briefs and pinned references, dependencies, preceding completed phase, applicable policies, and the execution resource for the current stage.

## Plan, implement, and review

An eligible primary owns product planning, coding, and acceptance decisions. Independent advisers inspect the plan and implementation, preferably through a permitted different provider. A single-provider setup uses a fresh same-provider instance. Advisers supply evidence and severity; the primary resolves findings and records consequential dispositions.

Constrained primaries use delegated planner/coder roles and approval-gated reviewer/critic loops. The configured mode determines authority; a review lane determines which stages run. Ordinary product work defaults to the full lane. An explicit user invocation is required for the product one-shot lane.

Methodology improvements follow a different standing route: the primary assesses, implements, self-checks, validates, commits, and fast-forward-pushes authorized work. Independent role loops are not invoked. `teach` and `learn` still require the operator to approve their concrete transfer plan before recipient writes.

## Prove and deliver the candidate

Use focused tests during implementation. The implementation-candidate sequence ends with changed-path test selection. After every tracked close write, run the full handoff gate on the exact tree being delivered. No tracked write follows a successful handoff gate.

```sh
./bin/test --changed-from '@{upstream}'
```

```sh
./bin/check all
```

Candidate identity binds product review. Full-tree identity binds the handoff gate and delivery. A changed candidate invalidates evidence that depended on its previous bytes. Unknown classifications or failed queries refuse; they never become a reassuring default.

When every executable gate passes, delivery stages explicit attributable paths, commits with hooks enabled, verifies the resulting commit and clean tree, and fast-forward-pushes to the existing upstream. Unexpected changes, divergence, ambiguous upstream, or unresolved hook refusal park delivery.

```admonish note title="Delivery and acceptance are separate"
Passing checks proves the executable criteria that were actually run. It does not prove the product feels right, that a visual result is acceptable, or that a human demo has been completed. Those criteria remain the operator's.
```

## Close or park truthfully

Record remaining work, evidence, lessons, and outcomes through the deterministic activity-log writer. Failed gates keep the phase open. Human-only actions belong in the action queue. A park says what blocks progress and what evidence or decision will unblock it.

## Finish resource cleanup

After integration, account for temporary worktrees, temporary branches and generated outputs created for the work. Retire them after ownership is released, commands have ended, and required evidence survives in its canonical durable home. Otherwise retain each for a named current purpose or report the exact blocker. Useful incremental build directories, dependency caches and environments may stay; cleanup should not force an unnecessary rebuild or create redundant archives.

Routine cleanup uses nonforced commands on verified integrated, scope-owned resources. Active work, unique unmerged history, uncertain custody and required evidence are preserved. A dirty flag alone does not settle whether anything unique remains. Record actual outcomes privately, then use the live evidence manager's `verify-completion` command to check the disposition record and read back resource state. The repository’s human-in-the-loop policy defines its record format and permission boundaries. Source delivery and completed cleanup are separate claims; a queued cleanup request is neither execution nor completion.
