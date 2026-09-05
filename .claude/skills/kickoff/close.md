# Kickoff — Bookkeeping, handoff and delivery

Read this resource before executing its branch. Enter through [SKILL.md](SKILL.md); its resource table defines the order. Before any failure, resume or operator-input branch, read [recovery.md](recovery.md).

### Step 9: Update status markers

For a major phase, enter only after [acceptance.md](acceptance.md) Step 8c materialized accepted close against unchanged authorities. For a child, retain the separate refusal described there; do not mutate around it. In `plan/INDEX.md`'s phase table (and only there):

1. Flip the completed phase's status cell from `🚧` to `✅`.
2. **If the closed phase was a sub-phase** (`phase-N.M.md`), go to Step 9a. Step 9a owns next-sub-phase drafting, the ripple sub-step, and (if the parent rolled up) handing off to Step 9b.
3. **Otherwise** (closed phase was a monolithic major phase with no sub-phases), go to Step 9b. Step 9b owns the major-phase ripple pass and advancing `⬅️`.

If the phase is only partially complete (the user paused mid-way), leave it `🚧` and do not advance `⬅️`.

**Never edit the per-phase file's frontmatter or body to record status.** Per-phase frontmatter is `id` / `title` / `depends_on` / `informs` plus optional `review_lane` ([`policies/review-lanes.md`](../../../policies/review-lanes.md)) only.

### Step 9a: Draft the next sub-phase (sub-phase close only)

If the just-closed phase was a sub-phase `phase-N.M.md` and the parent `phase-N.md`'s Deliverables are **not yet fully addressed** by the closed sub-phases:

1. Invoke `phase-planner` to draft `phase-N.(M+1).md` with the benefit of the closed sub-phases' outcomes. Pass it: the parent's full text, the list of closed sub-phases with their END summaries, and the parent's remaining un-addressed deliverables. The draft includes a `review_lane:` frontmatter assignment per [`policies/review-lanes.md`](../../../policies/review-lanes.md) eligibility (default `full`), and is sized per the outcome-boundary test in [preflight.md](preflight.md) Step 1a.
2. Write `phase-N.(M+1).md`. Update `plan/INDEX.md` (new row, dependency graph if needed).
3. Mark `phase-N.(M+1)` `⬅️`. Parent stays `🚧`.

If the parent's Deliverables **are** fully addressed by the closed sub-phases:

1. Mark the parent `✅`.
2. Run Step 9b (below) to ripple into the next major phase and advance `⬅️`. (Step 9.2's normal "advance to next `⏳`" is subsumed by Step 9b.)

If the closed sub-phase reveals that the parent's Deliverables list needs revision (new deliverable surfaced, an existing one no longer applies), surface this to the user explicitly in Step 10's report rather than silently rewriting the parent. The parent edit is the user's decision.

This step implements just-in-time, one-at-a-time sub-phase decomposition per [`briefs/methodology.md`](../../../briefs/methodology.md) §6 — `phase-N.(M+1)` is drafted *with* `phase-N.M`'s outcomes in hand, not in advance.

**Then run the ripple sub-step** before proceeding to Step 9c. This applies whether the parent is still `🚧` (a new sub-phase was drafted in 1–3 above) or just rolled up to `✅` (Step 9b took over). The ripple sub-step exists per [`policies/phase-ripple.md`](../../../policies/phase-ripple.md):

1. Read the closing sub-phase's `LOG.md` END block, the plan-reviewer's Observations, and the code-critic's verdict body.
2. Identify candidate ripples: pinned values, renamed paths, added brief refs, tightened Acceptance criteria, surfaced concerns addressed to a later phase by name.
3. For each candidate, walk the downstream drafted phase files — siblings (`phase-N.(M+1)`, `phase-N.(M+2)`, …, just-drafted or already drafted) plus downstream major phases (`phase-(N+1).md`, `phase-(N+2).md`, …, sketched at bootstrap). Classify each potential edit:
   - **AUTO** (mechanical, one correct shape): apply the edit now. If the edit is more than one line (e.g., reshaping an Acceptance section to incorporate a now-pinned value), invoke `phase-planner` with the downstream file and the ripple description; otherwise edit directly.
   - **DECIDE** (judgment-bearing): do *not* edit. Capture the item for the END block.
4. Prepare AUTO/DECIDE classification before accepted close at Step 8c. Resolve blocking DECIDE ripples before acceptance; apply prepared AUTO writes after accepted close and record their actual outcomes before Step 11. A newly discovered unresolved DECIDE parks completion. Note ripple's boundary: it propagates *content* into downstream `plan/` files. Durable *process* learnings are not ripples — they belong to Step 9c's lessons harvest.

If no downstream drafted phase files exist (e.g., this is the project's only phase, or all later phases are already ✅), the ripple sub-step is a no-op — note `none — no downstream sketches` in the END block.

### Step 9b: Major-phase close — ripple and advance ⬅️ (major-phase close only)

Runs when a major phase's row was just flipped to `✅` — either by Step 9.3 directly (the closed phase was a monolithic major phase) or by Step 9a's parent-rollup branch (the closed phase was the last sub-phase under its parent).

1. **Ripple pass** against the next drafted major phase (`phase-(N+1).md`) and any subsequent sketched phases. Procedure mirrors Step 9a's ripple sub-step (read END block + verdict bodies; classify each candidate AUTO/DECIDE; apply AUTO; capture DECIDE for the END block). The major-phase ripple is more likely to touch Goal and Deliverables (lower-fidelity sketches have more headroom) and Acceptance (sketched criteria need tightening once the upstream phase pins them).
2. **Advance `⬅️`.** Find the next `⏳` row in the dependency graph order (honoring parallel opportunities). Change it to `⬅️`. At most one row is `⬅️`; when no downstream phase exists, zero is the valid completed state.
3. **Sketched-phase completeness check.** If the new `⬅️` row points at a `phase-N.md` that doesn't exist as a file (only a row in INDEX.md), this is a bootstrap-completeness failure — flag in the END block. Do not auto-draft it; per [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) §8, every major phase the brief surfaces should have been sketched at bootstrap.

If no downstream major phase exists (project complete), Step 9b's ripple is a no-op and `⬅️` advances to nothing — the project is done. Surface this to the user in the report.

### Step 9c: Harvest lessons (every END or PARK)

Runs on **every** truthful terminal record, per [`policies/lessons.md`](../../../policies/lessons.md). For a major END, gather and classify lessons during close preparation before Step 8c, then file/validate them after the ripple writes and record actual outcomes before Step 11. The accepted block identifies any pending lesson writes truthfully. For PARK, it runs immediately from the evidence available at the stop; status and ripple work do not run. This is the capture stage of the improvement flywheel: the question is mandatory; "no lessons" is a permitted, recorded answer.

1. **Gather the sensor feed.** Re-read the close-out artifacts the ripple pass already collected (END-adjacent material, the plan-reviewer's and code-critic's verdict bodies) plus: every role's **Process Observations** output (planner, reviewer, coder, critic), the coder's **Failure Analysis** from any revision rounds, wall-clock observations, and any `user-actions` dispositions filed during the phase.
2. **Distill candidate lessons.** A candidate lesson is a specific, generalizable process learning — friction or ambiguity in a brief, policy, plan, skill, or tool that a future phase (or a future repo) should not re-derive. Discard one-off situational notes; keep what would change behavior next time.
3. **File or recur.** For each candidate, check `lessons/` and `lessons-archived/` for an existing entry stating the same lesson. Append an occurrence (`{date, ref}` — use the phase id) to an existing entry, or write a new `lessons/<slug>.md` with `status: candidate` and a scope classification (`local` — binds only this project; `methodology` — generalizes to the template and is an upstream candidate for `learn`). Follow the slug recipe and collision check in the policy.
4. **Validate and tally.** Run `./bin/lessons validate` (must pass — fix any schema error now), then `./bin/lessons candidates`. Carry every graduation-ready lesson (≥3 occurrences) forward to the END block as a graduation DECIDE item.
5. **Surface the telemetry recommendation.** Run `./bin/kickoff-config recommend-timeouts`. Summarize per-target output for the END block: the recommendation when a target has crossed the sample threshold, otherwise `insufficient samples (<n>/<minimum>)`. Never edit `kickoff.yaml` from this output — recalibration is a human decision per [`policies/role-timeouts.md`](../../../policies/role-timeouts.md).

**Hard boundary:** filing and occurrence-appending in `lessons/` are the *only* writes this step performs. Codifying a lesson — editing `CLAUDE.md`, `policies/`, `briefs/`, a skill, or an agent definition because of it — requires the user's explicit ratification of a surfaced DECIDE item. Never apply a graduation autonomously, and never rewrite rule documents wholesale from session memory.

### Step 10: Close the log and report

Read the validated evidence and finalized timing summaries directly to compute the block below; never substitute remembered counts or reassuring defaults when a record is absent. Run `$TELEMETRY_TOOL phase-summary --phase "$PHASE_ID"` and require every operator-input park to be closed before a completion END block. Every material count carries the exact command or deterministic procedure that produced it; a relayed number is remeasured or attributed plainly as unverified, per [`policies/verification-discipline.md`](../../../policies/verification-discipline.md).

The END block and the report that accompanies it are addressed to the operator, so both are composed in the [`plain`](../../../.claude/skills/plain/SKILL.md) register: lead with what is true now and what it means, name every parked criterion the operator still owns, and keep ids, paths, and stage mechanics available on request rather than ambient. Identifiers the operator must act on are given exactly.

Construct the complete END entry in a temporary file. For a major phase, this block is prepared and materialized at [acceptance.md](acceptance.md) Step 8c, before captured status changes. State planned close writes as pending, never as already done. After Steps 9–9c, append actual bookkeeping outcomes through `bin/log-append` before Step 11’s final tracked report write; preserve the original block. Execute the accepted close call only at Step 8c, not a second time when reading this section after bookkeeping. Materialize acceptance and append the exact prepared block at true EOF with `$EVIDENCE_TOOL close --run-dir <run> --outcome accepted --reason-code gates-green --log-block <block-file> --required-final-command "./bin/check all"`:

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
- N/A (initial implementation) | direct fix — <risk/size reason> | coder only — <risk/size reason> | full cycle — <risk/size reason>

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
- Evidence validation: `bin/kickoff-evidence validate --require-final` <OK|failed>

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

Lessons (per `policies/lessons.md`):
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

After status, ripple, lessons harvest, next-phase selection, and the END block are complete, write `$RUN_DIR/dashboard-handoff.json` using the exact schema in [`policies/execution-telemetry.md`](../../../policies/execution-telemetry.md). Ground `what_just_landed`, `see_for_yourself`, `coming_up_next`, and `recommended_steps` in accepted work, the User Demo, applied ripple, and real operator prerequisites. Never discuss commit state or place arbitrary HTML, prompts, responses, secrets, absolute paths, or private source material in the handoff.

Invoke the pinned command without `--open`:

```
$TELEMETRY_TOOL dashboard --phase "$PHASE_ID" --accepted-trace-id "$TRACE_ID" --handoff "$RUN_DIR/dashboard-handoff.json"
```

It validates and archives the sanitized handoff and regenerates the chronological offline report under `reports/execution/`. This is the final tracked close write. A render failure keeps the phase unreported and routes to the close-repair path in Step 12. When report presentation code changed, the localhost desktop/mobile, interaction, chart/table agreement, and console protocol in the telemetry policy must already have passed.

### Step 12: Prove the actual handoff tree

Run a **bare** `./bin/check all` after every tracked close write—status, ripple, lessons, END block, dashboard handoff, report, and index—is present. This is the handoff gate. It is deliberately outside the candidate-bound implementation ledger because the close writes changed the tree; its ignored full-gate receipt binds the actual tree handed to the user.

No tracked write may follow a successful handoff gate. Opening the already generated local report is read-only and may follow. If the gate fails, do not report completion. Append a truthful PARK block with the failing evidence and Lessons witness, restore the phase to `🚧` when necessary, then correct or regenerate the failing close artifact. A resumed close appends a new terminal block; it never amends, truncates, or context-patches an earlier block. Rerun the bare gate only after `bin/check-log` proves the resulting append-only log. If the failure exposes an implementation defect rather than close bookkeeping, return to Step 7's proportional correction route; the prior implementation gate is invalidated by any implementation-candidate change.

### Step 13: Deliver the accepted phase

Runs after the handoff gate is green. Parked acceptance criteria do not hold it up — they stay open for the user and are reported. Governed by [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md) and [`policies/commit-staging.md`](../../../policies/commit-staging.md).

1. **Re-read the tree.** Run `git status` and read the complete final diff. Every path must be one this phase touched. An unexpected path means a concurrent session shares this checkout — park and report it; never sweep it in.
2. **Stage explicitly and verify the staging assertions.** `git add <exact paths>`. Commit from the index without a pathspec after shared-file hunk partitioning; a commit pathspec takes whole working-tree content. **Never `git add -A` or `git add .`.** Re-read `git status --porcelain` immediately before staging. Partition any shared-file hunks, stage moved destinations rather than vanished sources, and read the staged diff before committing. If ownership cannot be established safely, park delivery.
3. **Commit and verify its file set.** Use an ordinary factual message describing the change. No agent credit, no `--no-verify`. A pre-commit hook refusal parks the commit and is reported truthfully — never retried around. Compare `git show --stat --oneline HEAD` with the intended file list before pushing.
4. **Push**, only when the current branch has exactly one unambiguous configured upstream and the update is a fast-forward. Never force. Never create an upstream, select a remote, tag, rebase, or repair history — those belong to the user.
5. **Verify.** Fetch, then prove `HEAD`, the tracking ref, and the remote tip agree and the tree is clean.

Any of the parks in the policy — unexpected path, hook refusal, missing or ambiguous upstream, rejected push, divergence, residual dirt — stops delivery, is reported, and is never worked around. An open parked criterion is not one of them. A user restriction recorded in the END block (`Delivery: restricted — …`) makes the run local-only or uncommitted; a restriction narrows delivery only and never relaxes a gate.

Commit and push change no tracked content, so they legitimately follow the handoff gate. **No later tracked write records their outcome** — the outcome is reported to the user and nowhere else.

### Step 14: Open the report and hand off

Open the already generated phase page without modifying it. A browser-open failure is presentation-only and may be retried; it changes no artifact. Then report to the user.

Report to the user, in this order:

- **🚨 Role disconnects (per [`policies/role-models.md`](../../../policies/role-models.md)):** report any configured-versus-dispatched venue difference, the failed attempt, and the explicit authority for recovery. Never infer provider identity from the requested alias or claim an automatic native downgrade succeeded. Report requested settings separately from qualified observations, with missing values `unreported`. Preflight failures abort before phase state exists.
- **What to try: the user testing protocol** for what's new or changed (Step 10a). This leads because it is what the user does next — the phase is already delivered, so the demo, not a commit instruction, is the handoff (`policies/user-demo-protocols.md`).
- **Acceptance:** what closed objectively on gate evidence, and what is parked for the user's judgment. Both halves, even when one is `None`.
- **Delivery:** the commit id and the push result — or the park and its reason, or the user's restriction verbatim.
- Which phase was completed and which is next (`⬅️`).
- Files created/modified, grouped by surface.
- Build and gate status.
- Candidate identity, finding convergence, implementation-gate identity, active command-manifest digest, venue-receipt identity, handoff-gate receipt, and any verified protocol recoveries.
- Any material wall-clock opportunity used or surfaced, and how the unchanged guarantees were preserved. Omit marginal timing noise and no-leverage observations.
- Any optional Observations the reviewers noted that the user may want to track.
- Lessons filed or recurred this phase, and any graduation DECIDE items awaiting the user's ratification (with the proposed target surface for each).

**Delivery is not acceptance.** The phase being committed and pushed settles nothing the user owes judgment on; the parked criteria stay parked, and saying otherwise in the report is the failure this whole boundary exists to prevent.
