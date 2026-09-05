---
name: kickoff
description: >-
  Orchestrate a single phase of plan/ end-to-end: pick up the next phase,
  plan, review plan, implement, review code, build/test, update status
  markers in plan/INDEX.md, and log; route later test- or user-driven
  corrections by risk and size. Language- and surface-agnostic; the project's
  CLAUDE.md and phase file declare which build gates to run.
  Invoke as /kickoff in Claude Code or $kickoff in Codex (picks up the ⬅️
  phase); append "phase N" to target a specific phase.
last-reviewed: 2026-09-04
---

# Kickoff: Single-Phase Session

Orchestrate one independently acceptable phase under `plan/`: plan → independent plan review → implementation → independent code critique → candidate gate → accepted evidence close → bookkeeping → handoff gate → delivery. This is the entry point; the adjacent resources carry the execution procedure. Read `CLAUDE.md`, the phase and its named authorities. The invoking session owns orchestration, logs, telemetry and both close gates; the coder owns initial implementation. Do not proceed to another phase without authorization.

## Parse arguments

Before selecting work, apply [methodology routing](../../../policies/review-lanes.md#methodology-improvements-direct-implementation-by-default): approved methodology improvements default to direct implementation outside this skill unless the operator explicitly requests this workflow.

Raw arguments: `$ARGUMENTS`

- Empty: select the single `⬅️` row in `plan/INDEX.md`.
- `phase N` or `phase N.M`: select that explicit phase. Resuming a `🚧` row requires explicit selection; do not infer it from an absent arrow.
- `one-shot`: invocation-only request under [review-lanes.md](../../../policies/review-lanes.md); check eligibility before skipping planning. Never select it autonomously or declare it in frontmatter.
- Concrete feedback or a build/test failure after initial critique: use the follow-up route in [recovery.md](recovery.md).
- Other text: match a phase row; unresolved ambiguity goes to the operator through recovery's input-park procedure.

Inspect the current branch, authoritative phase table and relevant recent log directly. Report missing files, command failures and invalid ledgers explicitly; never default a failed status probe to a benign state.

## Required resources and order

**Read each directly linked resource before executing its stage or branch.** This applies to every initial, follow-up, escalation, recovery and resumed path. Discovery and links are not evidence that a resource was loaded. A missing or unreadable resource stops that branch; do not reconstruct it from memory.

| Execution condition | Direct resource | Load requirement |
|---|---|---|
| Initial or delegated work; phase/lane selection, startup, fresh capture | [preflight.md](preflight.md) | Read before preflight or phase entry; Steps 0a–2. |
| Any role invocation, retry, resume or native dispatch | [dispatch.md](dispatch.md) | Read before dispatch; use generated contracts and registrations. |
| Planning or independent plan review, including escalation | [planning.md](planning.md) | Read before Steps 3–4. |
| Coder, critic, build-fix or delegated correction | [implementation.md](implementation.md) | Read before Steps 5–6. |
| Any executable acceptance or accepted evidence close | [acceptance.md](acceptance.md) | Read before Steps 7–8c. |
| Close preparation, status/ripple/lessons, reports, handoff or delivery | [close.md](close.md) | Read before preparing the END block or Steps 9–14. |
| Follow-up classification, failure, operator wait, park or resume | [recovery.md](recovery.md) | Read before entering any recovery or follow-up branch. |

Full initial lane: preflight → dispatch + planning → dispatch + implementation → acceptance → close. `light` skips plan review only; `one-shot` skips planning only when explicitly invoked and eligible. Every initial implementation receives independent code critique. Review lane and evidence lane are separate; neither can waive the mandatory seal or either full close gate. Follow-ups load recovery first, then every resource their selected route uses. Before escalating or returning to an earlier stage, load that stage's resource.

## Essential controls

- Resolve per-role venue/model/effort from `kickoff.yaml`; live preflight precedes phase mutation. Freeze runtime selection with the run. No silent substitution or permission changes. Retain configured timeouts, self-resume limits and recursion guard. [Role authority](../../../policies/role-models.md) governs admissible recovery.
- Keep coherent outcomes intact. Decompose only at an authorized consequential decision, independently accepted prerequisite, deployment/migration/human seam or demonstrated coherence limit. Surface count and missing child files are not boundaries. Planning settles consequential interfaces; ordinary implementation choices and approved deletions belong to the coder.
- Mark major work `🚧` before whole-file authority capture. Approved governing-prose preparation ends in a truthful park; a fresh run captures final authority before real remaining qualification work. Later authority changes require a new park/rebind. Never edit hashes or normalize unrelated ledgers.
- Use fresh opaque run directories and the pinned tools after initialization. Shared checkout work is sequential with one implementation writer. No worktrees by default. Each role attempt is immutable, generated and trace-bound; read each refusal before continuing.
- First reviews discover broadly and batch source-backed blockers. Optional advice is not an unresolved finding. Preserve stable finding IDs, evidence and causal revisions; rebase when authority, scope, risk or continuity changes. Exact verdict headers and structured evidence shapes remain mandatory.
- Preserve the 600-line ceiling, greater-than-one-third growth refusal, second-growth stop, stalled/oscillating review stops and ten-cycle backstop. Remove repetition before proposing a split; unsupported new premises go to the operator. See [four-canonical-agents.md](../../../policies/four-canonical-agents.md).
- Focused checks precede critique. An unavailable coder toolchain means `not-run`; the orchestrator runs the exact focused sequence. Approved preparation mismatches stay explicitly unresolved until fresh qualification; they never establish a green phase.
- After final critique, command zero and the complete implementation-candidate sequence end with `./bin/check all` against unchanged bytes. Validate and finalize evidence; materialize accepted **major-phase** close before captured status changes. Retain the separate unresolved child-close refusal.
- Complete status, ripple, lessons, END/report writes, then run a second **bare `./bin/check all`** on the handoff tree. No tracked write follows success. Every gate remains independent and full; [orchestration-evidence.md](../../../policies/orchestration-evidence.md) governs identities and custody.
- Only gate-proved work is committed and fast-forward-pushed by the orchestrator, using explicit paths and live staged-diff verification. User restrictions persist for their named scope. Destructive git operations, ambiguous ownership/upstream, refused hooks, divergence and residual dirt retain their hard stops. Delivery never claims manual or subjective acceptance.
- Every terminal outcome is truthful and append-only, with a Lessons witness, preserved evidence and exact timing where measured. Every unrun User Demo stays parked for the operator. End with the actual outcome, never a promise to dispatch later.

## Canonical source

Edit `.claude/skills/kickoff/`; `.agents/skills/kickoff` is its directory symlink. Resources retain the same root-relative link depth as this entry. Transfer the whole directory and inspect every branch, not only `SKILL.md`. Root/entry UTF-8 budgets and structural delivery are governed by [cross-harness-parity.md](../../../policies/cross-harness-parity.md#instruction-delivery). They do not prove live injection, adherence or model performance.
