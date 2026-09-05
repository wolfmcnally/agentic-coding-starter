# Kickoff — Implementation and code review

Read this resource before executing its branch. Enter through [SKILL.md](SKILL.md); its resource table defines the order. Read [dispatch.md](dispatch.md) before every role invocation. Before any failure, resume or operator-input branch, read [recovery.md](recovery.md).

### Step 5: Implement

**Native venue** (coder unpinned, per Step 0a): delegate implementation to the `phase-coder` agent. Pass it:

- The approved plan (full text, including any explicitly optional Observations from the plan-reviewer appended as advice).
- The evidence run directory and current candidate id.
- On revision rounds, the stable finding ledger and generated code-revision packet.

**Pinned venue** (any non-`default` model, per Step 0a): run the coder in that model's implied CLI per [`policies/role-models.md`](../../../policies/role-models.md), using the **write-enabled** recipe (the coder writes — unlike every read-only reviewer role):

1. Instruct the external agent to read `.claude/agents/phase-coder.md` and adopt that role; pass the approved plan, evidence run directory, current candidate id, and any revision packet/finding ledger via temp files.
2. Invoke the registered attempt through `$WATCHER_TOOL watch`. The generated coder command is the sole external workspace-write recipe; serialization preserves the single-writer invariant, and its schema/access flags cannot drift from the routing metadata.
3. **Single-writer guarantee:** `kickoff` is sequential, so during this stage no native writer touches the tree — the pinned coder owns it exclusively (build gates run afterward, Step 7). This satisfies "serialize or isolate — never two writers on one tree" without a worktree.
4. Capture the session id (codex `--json` `thread_id`; claude stream `session_id`) — the coder resumes across code-revision and build-fix rounds. Read the report (file list, Build Status, Manual Checks) from the watcher result artifact / codex `--output-last-message`; the file writes have already landed in the tree.
5. **Recovery:** a later three-signal gate failure or timeout follows [governed recovery](../../../policies/role-models.md#governed-recovery). Preserve the failed attempt and selected model/effort; report any explicitly authorized recovery and its basis in Step 10. Do not attempt to repair the sandbox mid-run.

Wait for the coder. Write its exact report to a fresh artifact. Require the normal report shape plus exactly one `### Change Evidence` JSON block, then run:

```
./bin/kickoff-evidence capture-change --run-dir <run> --metadata-artifact <coder-artifact>
```

This binds the changed paths, declared risks, selected tests, selection reason, intentionally unchanged neighbors, rebase reasons, falsifiers, and the coder's `gate_status` to the resulting candidate. Exit 66 is recoverable only if this validation and the report-shape gate both pass. Collect the file list, focused Build Status, Finding Resolution, and Manual Checks. The coder does not run or claim the acceptance-close sequence.

For an expressly approved preparation/qualification sequence, record every focused result on the preparation return, including expected mismatches; do not loop on intentionally undelivered qualification files or dispatch final critique. Read [recovery.md](recovery.md), preserve the report and lineage, and park truthfully before fresh authority capture. The fresh run's final critique covers the complete diff from HEAD, including prepared prose. This is not a green-code exception.

**Unverified-handoff guard.** Read `gate_status` from `change.json`. When `focused` is `not-run` (the venue could not reach the toolchain) or `red`, run the approved plan's Iteration and Revision Close sequence natively, including `./bin/check format` and `./bin/check lint` when prescribed; run either missing check afterward — each command in its own block, its refusal read — and record each as a gate against the candidate. Outside the expressly approved preparation boundary above, a red result goes back to the coder as a revision attempt with the diagnostics (reason `revision`); the critic is never dispatched on code whose focused gate has not run green somewhere. When a role venue was flagged at Step 0b as unable to run the toolchain, expect this branch on every coder return.

**Delivery pre-review.** Run `./bin/check-plan-delivery --plan <approved plan artifact> --root . --deviations <coder artifact>` in its own block. `ERROR` rows — planned files, introduced identifiers, or named tests the tree does not hold and the report does not declare as deviations — go back to the coder as a revision attempt, not to the critic. `DEVIATION` rows are passed to the critic with the file list.

**Push-back.** A Finding Resolution line of the form `<id> — rejected-with-evidence: <observation>` is ingested as that transition (`--no-review-span '<coder refutation>'`) and the refutation is quoted to the critic on the next round, which accepts it or reopens with counter-evidence.

Before dispatching the coder, close `orchestration.planning` and open `orchestration.implementation`. On any later return from acceptance to implementation, close the failed acceptance stage truthfully and increment both stage attempts.

### Step 6: Review code

**Native venue** (per Step 0a): delegate code review to the `code-critic` agent. Pass it:

- The approved plan (full text).
- Any advisory Observations, clearly separated from approved requirements.
- The list of files the coder created or modified.
- The reviewed/current candidate ids, change manifest, and evidence run directory.
- On revision rounds, the prior finding ledger and generated code-revision packet.
- **Light lane only:** the lane declaration, with the instruction to additionally judge lane fit per [`policies/review-lanes.md`](../../../policies/review-lanes.md) — did the diff stay within mechanical scope?
- Any `DEVIATION` rows from the delivery pre-review, any coder refutations (`rejected-with-evidence`) with their evidence, and the native observation for any prior finding the critic marked `SUSPECTED` (run the probe it named before dispatching; attach the output verbatim).

**Delegated venue** (the non-`default` model `critic` resolved to in Step 0a): run the role in that model's implied CLI per [`policies/role-models.md`](../../../policies/role-models.md). The shipped quality preset uses same-harness critique; cross-vendor review is explicitly selectable. Add the resolved model and effort flags and preserve them on resume; a later runtime failure follows [governed recovery](../../../policies/role-models.md#governed-recovery) and is reported in Step 10.

1. Write the approved plan and the **changed-file list** to temp files, and capture `git diff --stat` (what changed and where). The external reviewer runs against a **read-only checkout** with its own Read/Grep, so hand it a map, not a payload: it pulls the specific files it wants. Inline a full diff into a temp file only when the change is small enough to read whole; for a large change the file list + `git diff --stat` *is* the handoff. **Never pre-materialize a monolithic diff and reject the venue because `git diff | wc -c` is large** — an on-disk artifact is not tokens-in-the-window; a reviewer with Read/Grep reads surgically, and delegation is discarded only on the three-signal gate below, never on a pre-computed size estimate. **Flag machine-regenerated blobs** in the file list (fixtures, snapshot JSON, lockfiles, golden files) as "spot-check structure, don't read line-by-line" — they dominate byte count but carry almost no review surface. **Redact the coder's self-assessment** — no Build Status block, no Manual Checks narrative, no "tests pass" framing. Cold artifacts review 3–4× deeper (see [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) §§1, 4).
2. Write a prompt file instructing the external agent to: read `.claude/agents/code-critic.md` and adopt that role; review the changed files against the plan using the supplied candidate ids, change manifest, evidence run directory, and revision packet/ledger when present; assume the implementer was careful but missed something; emit exactly one `## Finding Evidence` JSON block; and end with the exact verdict header.
3. Invoke the registered attempt through `$WATCHER_TOOL watch`. It generates the read-only venue command and schema-constrains the code review artifact. Preserve the session id and exact intelligence span id for finding ingestion and convergence reporting.
4. Gate on ordinary three-signal success, or handle exit 66 through Step 0c. Write the exact response to a fresh artifact, require exactly one verdict, and run `./bin/kickoff-evidence ingest-findings --run-dir <run> --kind code --candidate <current-candidate-id> --review-span-id <critic-intelligence-span-id> --artifact <critic-artifact>` against its `## Finding Evidence` block. **`--review-span-id` is required**, for the reason given in Step 4. Failure of role shape, evidence schema/transition, or candidate identity follows [governed recovery](../../../policies/role-models.md#governed-recovery). The one `error_max_turns` conclude-now rescue remains available. After ingesting the response, mark the candidate just reviewed through `bin/kickoff-evidence mark-reviewed --expected-candidate <id>`.

**If `APPROVED`**: proceed to Step 7.

**If `REVISE`**: re-run `phase-coder` with the stable finding ledger and critic narrative, instructing it to include a **Failure Analysis** — why the previous attempt produced these findings (root cause, not restatement) — in its report and as the `failure_analysis` key of its Change Evidence. Validate its new Change Evidence, then generate a `--kind code` revision packet and re-review in the same venue (resume preferred); the packet carries the failure analysis forward so the critic reviews the fix against the coder's own theory of the failure. Continue only while a blocking finding advances and no equal-or-worse finding reopens. When the change manifest requires rebasing, run a complete critique rather than a delta-only pass. Escalate on recurrence, oscillation, authority disagreement, or two rounds without reduced severity or uncertainty. The 10-cycle runaway backstop still applies.

Before dispatching another coder after any `REVISE`, apply the same failure-backed outward-spiral judgment. A critic may deepen the work inside the authorized target, but may not enlarge the target through an unsupported actor, platform, operating mode, or failure premise. Route such a premise as `blocked-owner` and park before implementation; do not ask the coder to build it merely to make review pass. After divergence, explain the disputed premise to the operator in ordinary language; finding and path counts do not substitute for the judgment.

**If any code finding is `blocked-owner`** — the critic asked an owner question (an adversary or authorization no authority names): park it to the operator exactly as Step 4 does for a plan finding, and do not dispatch the coder on it; the remaining findings proceed in the same round.

**If `REVISE` opens with `Escalate: full lane — <reason>`** (light lane only): the work exceeded mechanical scope. Run the skipped Step 4 plan review now, against the plan as-built (same venue rules), route its outcome through the normal revision loops, and finish the phase in the full lane. Record `light → full (escalated: <reason>)` for the END block. The lane escalation itself is not a stall signal and does not count toward the runaway backstop; the critic's other Required Changes do feed the convergence judgment.
