# Kickoff — Recovery, parks and follow-ups

Read this resource before executing its branch. Enter through [SKILL.md](SKILL.md); its resource table defines the order. Before resuming a stage, read its resource again when continuity is uncertain.

## Follow-up entry

A follow-up revision exists only after the affected implementation has received its initial code-critic pass. Inspect the diagnostic or user instruction and the likely change surface, then classify both risk and size per [`policies/review-lanes.md`](../../../policies/review-lanes.md):

- **Direct fix** (small and low risk): the orchestrator edits the localized code itself. Skip role resolution/preflight and Steps 3–6; validate through Steps 7–8.
- **Coder only** (low risk, but implementation delegation is useful): run Steps 0a–0c, invoke Step 5, skip Step 6, then validate through Steps 7–8.
- **Full cycle** (high risk or large/cross-cutting): run Steps 0a–0c and the normal coder → critic path in Steps 5–8. Re-run planning first only when the correction exposes a plan or architecture error.

Before any follow-up, read [preflight.md](preflight.md) for the required Step 1b evidence initialization even when live role preflight is skipped. Read [acceptance.md](acceptance.md) before validation and [close.md](close.md) before terminal bookkeeping, the handoff gate or delivery. Delegated paths additionally read [dispatch.md](dispatch.md) and [implementation.md](implementation.md); planning escalation reads [planning.md](planning.md). These loads precede the corresponding actions, not merely the final report.

For a delegated follow-up, use the concrete diagnostic or user instruction, the phase file, and the prior END block as the correction brief for Steps 5–6; do not depend on an ephemeral plan from an earlier session. If those sources do not determine the correction safely, classify it as high risk and re-run planning.

Do not turn an uncertain correction into a direct fix: uncertainty about behavior, blast radius, or validation makes it high risk. For a follow-up during an active phase, continue through the normal Steps 9–10 after validation. If the prior phase is already `✅`, skip Steps 2 and 9 and do not emit the normal Step 10 END block; preserve its status and historical END block, then append an `END (correction)` block and report the route and evidence per [`policies/log-discipline.md`](../../../policies/log-discipline.md). A concrete correction does not reopen the phase, while genuinely new scope belongs in a new phase.

Every route still initializes Step 1b evidence. For a direct fix, the orchestrator writes the same exact Change Evidence JSON object the coder would have reported and passes it to `capture-change --metadata`; direct authorship does not bypass candidate identity, risk tags, selection rationale, or final gate records.

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
