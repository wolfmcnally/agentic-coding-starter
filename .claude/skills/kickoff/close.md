# Kickoff — Bookkeeping, handoff and delivery

## Authority-mode interpretation

Read the frozen workflow mode. Product primary mode dispatches only independent advisory reviewers, retains planning/coding on the invoking instance, and accepts through a current primary decision plus required checks. A reviewer verdict or remaining suggestion cannot block it. Second review/critique requires recorded cause; two passes per stage is the default maximum across continuations, subject only to the explicit single-use User exception in [orchestration-evidence.md](../../../policies/orchestration-evidence.md#single-use-owner-exception). Candidate changes require truthful delta assessment and fresh tests, not mandatory additional advice. Delegated product mode retains the approval/revision procedures below. Methodology work follows the separate primary one-shot route with no delegated role or independent review and with commit/push authority after required checks.


Inter-phase corrections use the append-only `END (correction)` format in [`policies/log-discipline.md`](../../../policies/log-discipline.md#follow-up-correction-format), recording the phase recommendation and operator ruling without formal reviews or fabricated phase evidence. Preserve completed status/history; the normal phase status, acceptance-close and END machinery below applies only to actual phase/sub-phase work. Validation and the final full handoff gate still apply to both routes.

Read this resource before executing its branch. Enter through [SKILL.md](SKILL.md); its resource table defines the order. Before any failure, resume or operator-input branch, read [recovery.md](recovery.md).

### Step 9: Verify the accepted phase event

Accepted close binds the proposed JSON completion to the real run and its captured owner/claim, retains qualification bytes and appends the terminal log entry. It then publishes completion events; verify with the same close invocation plus `--verify-handoff` before other bookkeeping. Never edit `plan/INDEX.md`, phase frontmatter or an earlier event to reflect status. A failed publication stays visible and is retried only against the exact original close request. A park leaves the phase in progress.

### Step 9a: Complete children and independently accepted parents

Prepare the real successor and relevant authorities before final review. A child completes under its own acceptance; an actual incomplete sibling or a truthful parent-continuation reason permits the parent to remain active. Parent completion additionally needs `--parent-run` with separately accepted current parent implementation and its exact ancestor chain. Parents cannot complete over incomplete children. Accepted parent implementation may remain without a completion event until its children finish. See [phase-status.md](../../../policies/phase-status.md).

### Shared ripple procedure (child and major close)

Before acceptance, read the prepared END block, reviewer and critic verdicts, and affected downstream phase files. Identify every pinned name, path, value and decision; classify each propagation as AUTO or DECIDE under [phase-ripple.md](../../../policies/phase-ripple.md). Resolve every DECIDE gate before accepted close. After the recorded ledger transition is verified, apply the prepared AUTO edits to incomplete downstream phases and append actual outcomes before the final handoff gate. A non-final child runs this procedure against its drafted successor and affected later phases; parent completion runs it against subsequent major phases. Never edit the completed phase or claim a planned edit already happened.

### Step 9b: Ripple and select the next real work

Perform the prepared AUTO ripple against incomplete downstream definitions after verified accepted close. Consequential new scope still goes to the operator. Select a dependency-ready phase by rational order and permanent id under the current owner's queue, append a predecessor-bound `next` event and render the local view. Do not overwrite another operator's selection or infer custody from selection. No next selection is required while work remains active; explicit resume is valid. Missing selected definitions are a bootstrap defect, never a reason to fabricate work at close.

### Step 10: Close the log and report

Read the validated evidence and finalized timing summaries directly to compute the block below; never substitute remembered counts or reassuring defaults when a record is absent. Run `$TELEMETRY_TOOL phase-summary --phase "$PHASE_ID"` and require every operator-input park to be closed before a completion END block. Every material count carries the exact command or deterministic procedure that produced it; a relayed number is remeasured or attributed plainly as unverified, per [`policies/verification-discipline.md`](../../../policies/verification-discipline.md).

Gate executions are the rows in `gates.jsonl`; diagnostic reviews and their corrections in `gate-reviews.jsonl` are observations of those executions, never additional runs. Use the validated latest diagnostic review for each managed gate. Render execution identifiers with the canonical plain-text `Execution trace: <id>` field from `policies/log-discipline.md`; decorative formatting must not turn an identifier into a misleading commit reference.

The END block and the report that accompanies it are addressed to the operator, so both are composed in the [`plain`](../../../.claude/skills/plain/SKILL.md) register: lead with what is true now and what it means, name every parked criterion the operator still owns, and keep ids, paths, and stage mechanics available on request rather than ambient. Identifiers the operator must act on are given exactly.

Compose the complete END entry in the durable run directory with `./bin/multioperator compose-terminal --content <content.json> --output <fresh-block.md>` using the explicit substantive fields and lessons contract in [log discipline](../../../policies/log-discipline.md#follow-up-correction-format); do not hand-copy the illustrative layout below. For a major phase, this block is prepared and materialized at [acceptance.md](acceptance.md) Step 8c, before captured status changes. State planned close writes as pending, never as already done. After Steps 9–9c, append actual bookkeeping outcomes through `bin/multioperator append-terminal` before Step 11’s final tracked report write; preserve the original block. Execute the accepted close call only at Step 8c, not a second time when reading this section after bookkeeping. Materialize acceptance and append the exact prepared body as an immutable attributed entry with `$EVIDENCE_TOOL close --run-dir <run> --outcome accepted --reason-code gates-green --log-block <block-file> --required-final-command "./bin/test --changed-from '@{upstream}'"`:

```
## <YYYY-MM-DD HH:MM> — END
<Phase heading>

Files changed:
- <path> — <brief>
- ...

Build status:
- <gate 1>: OK | N/A | failed (<short reason>)
- <gate 2>: OK | N/A | failed (<short reason>)
- Handoff gate: runs after this tracked END block; completion is contingent on
  the ignored receipt from the final bare `./bin/check all`
- ...

Review lane (per `policies/review-lanes.md`):
- full | light | one-shot | light → full (escalated: <reason>) | light → full (orchestrator upgrade: <reason>) | one-shot → full (escalated: <reason>) | one-shot refused (<reason>) → <declared lane>

Evidence lane (per `policies/review-lanes.md`):
- full | light | light → full (orchestrator upgrade: <reason>) | light refused (<trigger>) → full

Follow-up route (per `policies/review-lanes.md`):
- N/A (initial implementation) | inserted phase/sub-phase with formal planning/reviews — <risk/size reason>
- Phase recommendation and operator ruling: <inserted sub-phase recommendation and attributable choice, or existing authority for a small low-risk correction>

Role model/venue (per `policies/role-models.md`) — orchestrated by <claude|codex>:
- Preflight: OK (<validated targets>) | N/A (every role native)
- Planner: requested model=<model> effort=<effort|default> venue=<native|claude|codex> <annotate any authorized recovery with its reason and authority>
- Reviewer (plan review): requested model=<model> effort=<effort|default> venue=<native|claude|codex> | skipped (light lane) <same annotations>
- Coder: requested model=<model> effort=<effort|default> venue=<native|claude|codex> <same annotations>
- Critic (code review): requested model=<model> effort=<effort|default> venue=<native|claude|codex> <same annotations>
<Annotate any exit-66 artifact accepted after explicit validation as
"[protocol recovered: terminal stream incomplete]"; this is not a fallback.>

For each role separately: harness_version=<observed|unreported>, observed_model=<observed|unreported>, observed_effort=<observed|unreported>; observation_errors=<diagnostics|none>. Never copy requested settings into observed fields. Follow `policies/role-models.md` for qualified observation sources.

Role timing (per `policies/role-timeouts.md`):
- Planner: <duration>; first event <duration|unavailable>; longest idle <duration|unavailable>; <success|error|timeout(type)>
- Reviewer (plan review): <same> | skipped (light lane)
- Coder: <same>
- Critic (code review): <same>

Execution timing (per `policies/execution-telemetry.md`):
- Active makespan: <exact duration>; calendar window: <exact duration>
- Summed measured work: <duration>; peak concurrency: <n>
- Exclusive work: Planning=<duration>; Plan Review=<duration>; Implementation=<duration>; Code Review=<duration>; Automated Checks=<duration>; Reconciliation=<duration>
- Failed work: <duration>; retry work: <duration>
- Orchestration / Unmeasured: <duration>; largest measured gaps: <summary|none>
- Awaiting user input:
  - <opened UTC> → <closed UTC|open>: <duration|unavailable> (<reason>; exact monotonic | non-exact calendar cross-boot | unavailable)
  - Total: <union duration|unavailable> (<exact monotonic union | non-exact calendar union | incomplete>)
- Timing validation: exact monotonic nanoseconds, overlap-safe unions, trace joins <OK|failed>

Candidate-bound evidence (per `policies/orchestration-evidence.md`):
- Candidate: initial=<id> approved=<id> final=<id>
- Revision packets: <count>; <total bytes>; source hashes recorded
- Findings: open=<n> addressed=<n> verified=<n> closed=<n> blocked=<n>; reopened=<n>; missed-in-full-pass=<n>
- Gates: focused=<n> implementation-final=<n>; all recorded against approved implementation candidate=<yes|no>
- Evidence validation: `$EVIDENCE_TOOL validate --run-dir <run> --level acceptance --required-final-command "./bin/test --changed-from '@{upstream}'"` <OK|failed>

Wall-clock observations:
- <material operation; substantial safe improvement used or surfaced; why guarantees were preserved> | None

Acceptance (per `policies/human-in-the-loop.md`):
- Objective (independently reviewed, gate-proved, candidate-bound): <named criteria> | None
- Parked for the user: <named manual, perceptual, product, or custody criteria, and the `User Demo:` protocol when unrun> | None

Delivery:
- default — commit + fast-forward push after the handoff gate | restricted: <user's words, verbatim> | parked: <reason>

Ripple (per `policies/phase-ripple.md`):
- AUTO: <downstream phase file> — <pinned change; applied or pending, truthfully> | None
- DECIDE: <downstream phase file> — <one-line: candidate ripple, why it needs human judgment> | None
<If no downstream drafted phase files exist, state "none — no downstream sketches".>

Lessons:
- filed or pending: <slug> — <one-line lesson, scope, actual state> | none
- occurrences added or pending: <slug> (<measured current n> total) — <ref, actual state> | none
- graduation DECIDE: <slug> → <proposed_surface> — <one-line why it is ready> | none
- recalibration: <role/venue target — recommended hard/idle values> | insufficient samples (<n>/<minimum>)

User demo (per `policies/user-demo-protocols.md`):
<If the approved plan carried a `User Demo:` block, paste it verbatim here, with the entry-point command on its own line so the user can copy it directly. If the plan declared `User Demo: N/A — <reason>`, restate that line.>

Remaining:
- <anything significant left incomplete, or "None">
```

### Step 10a: User testing protocol

Every phase that ships user-observable behavior — a running service, a CLI tool, a new tool surface, a new artifact landing where the user can see it — produces a structured **test protocol** appended to the user-facing report (Step 11). The protocol is the bridge between "the orchestrator says this is done" and "the user has satisfied themselves it works." It is the deeper sibling of the `User Demo:` block from [`policies/user-demo-protocols.md`](../../../policies/user-demo-protocols.md): the policy declares *what* to demo at plan time; this step ships the structured testing layout at close time. It is not optional except for purely internal phases (e.g., a refactor that ships nothing externally observable; flag the exception explicitly in the END block under `Remaining` if so).

Format. The protocol has up to seven sections; omit any that don't apply:

```
# <Phase id> — <Phase title> · Test Protocol

**Surfaces introduced.** One-line inventory the user can paste into their shell or open directly.

## 1. Hot-state checks (run now, no setup)
Two-to-five short shell commands the user can run immediately to confirm the deployed state. Each line: a `bash` block plus the expected output.

## 2. Daemon / service / console checks (manual)
What to inspect via process listings, service status commands, log directories, or a GUI. Anything the orchestrator cannot script.

## 3. End-to-end behaviour (if a new behaviour ships)
The full happy path the user should walk through — invoking the new command, opening the produced artifact, exercising the new surface end to end. Name every observable side-effect.

## 4. Acceptance items not covered by automated smokes
Phase-file Acceptance entries that require manual verification. Quote the entry and provide the verification recipe.

## 5. Destructive / maintenance-window checks (optional)
Anything that requires a temporary-state change to verify (e.g., "stop the service, edit a file, restart, verify catch-up"). Mark clearly as "DO NOT RUN CASUALLY" and document the restore procedure.

## 6. Future-phase deferrals
Acceptance items the phase claims partial credit for but that genuinely belong to a future phase. Name which phase will close them out.

## 7. Summary
A two-to-three-line wrap: which automated checks PASS, which manual checks remain, what the user should do next.
```

Style notes:
- Use real values from the running system (file paths, session ids, service names) rather than `<placeholders>` the user has to fill in.
- Every shell command is copy-pasteable and self-contained.
- When a check is racey or eventually consistent, say so and provide the deterministic alternative.
- When the protocol leans on a brief or policy, name it — e.g., "verifies the append-only invariant from `policies/log-discipline.md`."

Where to put it: inline at the end of the user-facing report. Long protocols (~> 50 lines) may also be appended to `LOG.md` under the END block as a `### Test protocol` subsection so future planners can find it without scrolling the conversation.

When to skip: mandatory unless the phase is a pure internal refactor with no user-observable surface, or introduces only invariants enforced by automated gates. In either case, state explicitly in the END block under `Remaining`: `Test protocol: skipped (reason: …)`.

### Step 11: Generate the tracked phase report

After status, ripple, lessons harvest, next-phase selection, and the END block are complete, write `$RUN_DIR/dashboard-handoff.json` using the exact schema in [`policies/execution-telemetry.md`](../../../policies/execution-telemetry.md). Set `project` to the project's name as its README titles it. Ground `what_just_landed`, `see_for_yourself`, `coming_up_next`, and `recommended_steps` in accepted work, the User Demo, applied ripple, and real operator prerequisites. Never discuss commit state or place arbitrary HTML, prompts, responses, secrets, absolute paths, or private source material in the handoff.

Invoke the pinned command without `--open`:

```
$TELEMETRY_TOOL dashboard --phase "$PHASE_ID" --accepted-trace-id "$TRACE_ID" --handoff "$RUN_DIR/dashboard-handoff.json"
```

It validates and archives the sanitized handoff and regenerates the chronological offline report under `reports/execution/`. This is the final tracked close write. If a later bookkeeping write to the trace ledger leaves an archived file stale, `./bin/check-execution-dashboards --regenerate` rewrites it from tracked inputs; run that before the handoff gate rather than discovering it there. A render failure keeps the phase unreported and routes to the close-repair path in Step 12. When report presentation code changed, the localhost desktop/mobile, interaction, chart/table agreement, and console protocol in the telemetry policy must already have passed.

### Step 12: Prove the actual handoff tree

Run a **bare** `./bin/check all` after every tracked close write—status, ripple, lessons, END block, dashboard handoff, report, and index—is present. This is the handoff gate and the phase's one full run; its receipt qualifies the push. It is deliberately outside the candidate-bound implementation ledger because the close writes changed the tree; its ignored full-gate receipt binds the actual tree handed to the user.

No tracked write may follow a successful handoff gate. Opening the already generated local report is read-only and may follow. If the gate fails, do not report completion. Append a truthful PARK block with the failing evidence and Lessons witness, preserve the accepted completion and report the later delivery failure separately, then correct or regenerate the failing close artifact. A resumed close appends a new terminal block; it never amends, truncates, or context-patches an earlier block. Rerun the bare gate only after `bin/multioperator validate --root .` proves the resulting append-only log. If the failure exposes an implementation defect rather than close bookkeeping, return to the correction-routing rule: recommend an inserted sub-phase when risk or size warrants it and honor the operator's phase versus inter-phase ruling. The prior implementation gate is invalidated by any implementation-candidate change.

### Step 13: Deliver the accepted phase

Runs after the handoff gate is green. Parked acceptance criteria do not hold it up — they stay open for the user and are reported. Governed by [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md) and [`policies/commit-staging.md`](../../../policies/commit-staging.md).

1. **Re-read the tree.** Run `git status` and read the complete final diff. Every path must be one this phase touched. An unexpected path means a concurrent session shares this checkout — park and report it; never sweep it in.
2. **Stage explicitly and verify the staging assertions.** `git add <exact paths>`. Commit from the index without a pathspec after shared-file hunk partitioning; a commit pathspec takes whole working-tree content. **Never `git add -A` or `git add .`.** Re-read `git status --porcelain` immediately before staging. Partition any shared-file hunks, stage moved destinations rather than vanished sources, and read the staged diff before committing. If ownership cannot be established safely, park delivery.
3. **Commit and verify its file set.** Use an ordinary factual message describing the change. No agent credit, no `--no-verify`. A pre-commit hook refusal whose cause or safe correction is unresolved parks the commit and is reported truthfully — never retried around. A diagnosed, agent-owned refusal is corrected and requalified under [`human-in-the-loop.md`](../../../policies/human-in-the-loop.md) § Correcting a diagnosed hook refusal. Compare `git show --stat --oneline HEAD` with the intended file list before pushing.
4. **Push**, only when the current branch has exactly one unambiguous configured upstream and the update is a fast-forward. Never force. Never create an upstream, select a remote, tag, rebase, or repair history — those belong to the user.
5. **Verify.** Fetch, then prove `HEAD`, the tracking ref, and the remote tip agree and the tree is clean.

Any of the parks in the policy — unexpected path, unresolved hook refusal, missing or ambiguous upstream, rejected push, divergence, residual dirt — stops delivery, is reported, and is never worked around. An open parked criterion is not one of them. A user restriction recorded in the END block (`Delivery: restricted — …`) makes the run local-only or uncommitted; a restriction narrows delivery only and never relaxes a gate.

Commit and push change no tracked content, so they legitimately follow the handoff gate. **No later tracked write records their outcome** — the outcome is reported to the user and nowhere else.

### Step 14: Open the report and hand off

Before reporting delivery completion, perform the resource disposition procedure in [human-in-the-loop.md](../../../policies/human-in-the-loop.md#delivery-resource-disposition). Inventory scope-created temporary worktrees, temporary branches and generated outputs, including none explicitly. Retire only after verified integration, released ownership, preserved required evidence and terminal commands; otherwise retain for a named current purpose or report an exact blocker. Useful incremental build directories, dependency caches and environments may remain. Use the live `bin/kickoff-evidence verify-completion` against the durable disposition record after actual readback; never alter closed pinned tools or accepted evidence. This applies to inter-phase and methodology delivery too and creates no new phase run. A blocked cleanup is reported separately from successful source delivery; it cannot be called completed cleanup. Preserve the record and command output outside the reviewable tree, so post-delivery readback changes no gate-qualified tracked bytes.

Open the already generated phase page without modifying it. A browser-open failure is presentation-only and may be retried; it changes no artifact. Then report to the user.

Report to the user, in this order:

- **🚨 Role disconnects (per [`policies/role-models.md`](../../../policies/role-models.md)):** report any configured-versus-dispatched venue difference, the failed attempt, and the explicit authority for recovery. Never infer provider identity from the requested alias or claim an automatic native downgrade succeeded. Report requested settings separately from qualified observations, with missing values `unreported`. Preflight failures abort before phase state exists.
- **What to try: the user testing protocol** for what's new or changed (Step 10a). This leads because it is what the user does next — the phase is already delivered, so the demo, not a commit instruction, is the handoff (`policies/user-demo-protocols.md`).
- **Acceptance:** what closed objectively on gate evidence, and what is parked for the user's judgment. Both halves, even when one is `None`.
- **Delivery:** the commit id and the push result — or the park and its reason, or the user's restriction verbatim.
- Which phase was completed and which phase is selected next for this operator.
- Files created/modified, grouped by surface.
- Build and gate status.
- Resource disposition: retired / retained with named current purposes / blocked with exact reasons; durable record and actual readback. Source delivery and cleanup completion are separate claims.
- Candidate identity, finding convergence, implementation-gate identity, active command-manifest digest, venue-receipt identity, handoff-gate receipt, and any verified protocol recoveries.
- Any material wall-clock opportunity used or surfaced, and how the unchanged guarantees were preserved. Omit marginal timing noise and no-leverage observations.
- Any optional Observations the reviewers noted that the user may want to track.
- Lessons filed or recurred this phase, and any graduation DECIDE items awaiting the user's ratification (with the proposed target surface for each).

**Delivery is not acceptance.** The phase being committed and pushed settles nothing the user owes judgment on; the parked criteria stay parked, and saying otherwise in the report is the failure this whole boundary exists to prevent.
