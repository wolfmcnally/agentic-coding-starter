# Kickoff — Recovery, parks and follow-ups

## Authority-mode interpretation

Read the frozen workflow mode. Product primary mode dispatches only independent advisory reviewers, retains planning/coding on the invoking instance, and accepts through a current primary decision plus required checks. A reviewer verdict or remaining suggestion cannot block it. Second review/critique requires recorded cause; two passes per stage is the default maximum across continuations, subject only to the explicit single-use User exception in [orchestration-evidence.md](../../../policies/orchestration-evidence.md#single-use-owner-exception). Candidate changes require truthful delta assessment and fresh tests, not mandatory additional advice. Delegated product mode retains the approval/revision procedures below. Methodology work follows the separate primary one-shot route with no delegated role or independent review and with commit/push authority after required checks.


Read this resource before executing its branch. Enter through [SKILL.md](SKILL.md); its resource table defines the order. Before resuming a stage, read its resource again when continuity is uncertain.

## Follow-up entry

Inspect the diagnostic or user instruction, likely write set and validation needs before implementing a correction. Follow [`policies/review-lanes.md`](../../../policies/review-lanes.md): for high-risk or large/cross-cutting work, **recommend an inserted phase**, normally an additional sub-phase of the current phase; a new major top-level phase is rare. Uncertain behavior, blast radius or weak proof belongs in that recommendation, not an unsupported low-risk classification.

Honor the operator's ruling. A chosen phase/sub-phase enters the ordinary phase lifecycle with formal planning and reviews; read [preflight.md](preflight.md), [planning.md](planning.md), [dispatch.md](dispatch.md), [implementation.md](implementation.md), [acceptance.md](acceptance.md) and [close.md](close.md) before their respective actions. Insert it through the existing phase-ledger procedure, preserving completed history and real review accounting. An approved preparation/qualification continuation instead uses [Planned continuation](#planned-continuation) below; it is not an inter-phase correction.

If the operator chooses **inter-phase implementation without formal review**, use the concrete instruction and preserved earlier records as the bounded correction brief and proceed without Steps 0a–0c or formal planner/reviewer/critic stages. Do not initialize a fictitious phase evidence run to force those stages back in. Small low-risk corrections may proceed directly under existing authority. Read [acceptance.md](acceptance.md) before validation and [close.md](close.md) before terminal bookkeeping, the handoff gate or delivery. Also read [`policies/log-discipline.md`](../../../policies/log-discipline.md) for the correction record; the resources' phase-only role/acceptance machinery does not apply to this route.

Every inter-phase correction still reruns the failing check, focused/touched-surface tests, the changed-path selection and the final bare full handoff gate after bookkeeping. Record the phase recommendation and attributable inter-phase ruling where applicable, scope, risk/size assessment, exact validation and remaining limitations. Preserve prior phase status, START/END records, reports, refusals and budgets; append an `END (correction)` record instead of reopening a completed phase or inventing a review. No new permission, worker or review allowance follows from the route.

Failure, recurrence, growth or a consequential scope/design change requires fresh diagnosis and a renewed recommendation with concrete evidence, not automatic review escalation contrary to the operator's ruling. Safety/permission constraints and unresolved executable failures remain binding. For a correction that remains inside an actual phase lifecycle, initialize the required candidate-bound evidence and capture truthful Change Evidence; only that phase route uses Step 1b and the corresponding formal phase procedures.

## Planned continuation

Apply [the approved-plan continuation rule](../../../policies/review-lanes.md#continue-an-approved-plan-after-preparation) before restarting an expressly approved preparation/qualification sequence. Verify the preserved approved plan, approval, authority diff and candidate lineage; identify completed work, real remaining work, focused results and every unresolved finding. If the policy's eligibility conditions fail, use fresh planning and independent plan review rather than this branch.

After the truthful preparation park and final authority edits, read [preflight.md](preflight.md) and initialize a fresh run with `--follow-up-route full-cycle`, retaining the resolved review and evidence lanes. This existing route derives coder and critic attempts without a new planning stage. Put the preserved plan and hash, approval and the verified continuation evidence in the continuation brief; do not invent fresh planning or review records. Read [dispatch.md](dispatch.md) and [implementation.md](implementation.md), then run Steps 5–8 using that brief. Tell the critic to check continuation eligibility and review the entire diff from HEAD against the preserved plan and current authorities. Ineligible continuation requires a truthful park and fresh planning/review; do not insert a late planning stage into this run.

Before dispatching the continuation coder, append `START (resumed)` through preflight Step 2, naming the preserved preparation and plan. Close `orchestration.setup` successfully, recompute the candidate through `$EVIDENCE_TOOL current-candidate`, and open `orchestration.implementation` directly; do not open or close an omitted planning stage. This remains the same incomplete phase: preserve its in-progress marker and close through [acceptance.md](acceptance.md) and [close.md](close.md), including Steps 9–10 and the normal END block. Record the preparation and continuation relationship, actual roles and preserved approval; never report preparation as acceptance or use the historical-phase correction format.

### Operator-input parks (applies throughout)

Phase-level time awaiting required user input is not a role `wait` span and may cross trace finalization or a machine reboot. Immediately before stopping for an approval, decision, manual check, environment action, acceptance judgment, or other required input, run:

```
$TELEMETRY_TOOL park-open --phase "$PHASE_ID" --reason <stable-reason-code>
```

Use only the enumerated reason codes shown by the CLI; never record the question, response, prompt, repository content, or private data. Preserve the returned park id. On the continuation that receives an answer satisfying the wait, close it **before resuming phase work**:

```
$TELEMETRY_TOOL park-close --phase "$PHASE_ID" --park-id <park-id>
```

Repeated open/close calls are idempotent for the same identity; a conflicting, missing, or multiply-open park fails closed. `phase-summary` reports each interval and its union total. Same-boot intervals use exact monotonic time; cross-boot intervals use visibly non-exact UTC calendar duration. Never turn an open, malformed, or unknowable interval into zero.

When the run must terminate in a truthful PARK rather than merely keep the turn open, harvest the available sensor feed immediately using Step 9c's file-or-recur rules, validate the ledger, and append a PARK block through `bin/log-append`. The block names the reason, preserved evidence, resume condition, and a literal `Lessons:` section. Do not postpone a failed attempt's learning until a future END.

## Native execution limits

Absent named subagents does not authorize substituting the orchestrator for a selected model or reviewing its own work in the same context. Follow [governed recovery](../../../policies/role-models.md#governed-recovery); retain canonical role procedures, tool stances and verdict formats in any admissible venue.

- Fail-closed park and diagnosed resume ([`policies/fail-closed-resume.md`](../../../policies/fail-closed-resume.md)): any first-encountered defect finishes the run truthfully — dispatches stopped, spans closed with the failure outcome, artifacts preserved, candidate restoration or lineage proved — and records a five-part failure signature in the phase's append-only `.kickoff/failure-signatures.jsonl` ledger. A **novel**, fully diagnosed signature with a recorded causal correction may open a fresh corrective trace against the phase's self-resume budget (`kickoff.yaml` `run_budgets.self_resume`, shipped default 3, restored by any operator relay; `0` pins every park to the operator). A **recurring** signature always stops for the operator. Prelaunch dispatcher rejections are corrected-and-relaunched at most once without consuming budget. Sealing is a close-time act: never re-run whole-repository sealing per fix inside a convergence loop.

- `ingest-findings` **requires `--review-span-id`** and refuses without it. The convergence integers attach to the review pass's own intelligence span, and a span is immutable once the trace is finalized — so an omitted flag makes `timing-summary` refuse for the entire run and cannot be repaired afterward. Preserve each reviewer's and critic's intelligence span id when you dispatch it. For an ingest that is genuinely **not** a review pass — most commonly the orchestrator recording an `open → addressed` transition after a *plan* revision, since `phase-planner` emits a revised plan rather than a `## Finding Evidence` block — pass `--no-review-span '<reason>'`, which records the omission in `review-metrics-omitted.jsonl` instead of hiding it.

## Context continuity

Before a capacity pause or compaction continuation, read [the context brief](../../../briefs/session-context-compaction.md). Use measured session capacity and comparable arc evidence; unknown capacity is unknown. Externalize exact plan/candidate/findings and actual run state at a safe boundary, then re-read active instructions and the next stage resource on continuation. Lost trustworthy continuity requires complete review; authority drift requires a truthful park and fresh capture. Do not add hooks, change permissions or infer CLI capacity from an API setting.

For a fresh primary-mode continuation run, use `kickoff-evidence carry-advice --run-dir <new-run> --source-run <prior-run>` after initialization. It preserves original report/candidate/dispatch provenance and the phase-wide pass allowance. Record a fresh primary decision about the final delta; an old decision is not acceptance of new bytes. Keep prior evidence available. A failed second advisory invocation does not authorize a third under another run directory.

Primary review attempt continuity may use verified carried predecessors from the same work item; their original registrations, accepted dispatches, reports and earlier phase-bound launch claims remain in their originating runs. Local span joins never borrow inherited spans. Missing or mismatched predecessor evidence refuses. If a qualified tooling repair is needed by a prior source exporter, archive its exact old bundle, run metadata and refusal, then use supported `repin-tools` under that run owner's custody for the source and target. Repairing only the target leaves its subprocess calling the source's old pinned exporter. Preserve historical reports, traces and budgets, then carry and record a fresh final-delta decision; never renumber old attempts or launch replacement advice to escape a validator defect.

## Cross-boot interruption and lost evidence

Preserve the old run and spool byte-for-byte. `finish` and same-boot `recover` must continue to refuse a changed clock domain. After current process/resource custody and candidate lineage have been verified independently, start a fresh same-phase successor trace in the current boot. Use the qualified live telemetry command `interrupt --trace-id <old> --successor-trace-id <new> --custody-evidence <durable-json>` before successor implementation. The custody object contains nonempty `source`, `reference` and `candidate_lineage` strings plus literal `processes_quiescent: true` and `resources_released: true`; a caller's assertion does not perform the checks or grant authority. Keep it private. The command preserves its bytes in the successor spool and records a separate conflict-checked observation next to the old spool. Old completion, exit and duration remain unknown; the old root/children remain open and cannot supply acceptance. Do not force ordinary old-run close or repin historical tools to manufacture finalization.

Initialize fresh durable evidence with current approved authorities and the unchanged phase budget. Carry only complete eligible original advice through its original pinned exporter. Missing source metadata or joins remain an explicit lost-source-run hold even when raw plan/report bytes have been recovered. Preserve those bytes as observations and the consumed allowance as consumed; do not reconstruct a run from a summary, reset counts or launch unauthorized replacement advice. Rerun missing test/qualification proof on the successor where authorized. A cross-boot observation does not settle a permission, process-custody question or independent review requirement.
