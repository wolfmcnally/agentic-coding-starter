---
title: "The Agentic Coding Methodology — Eleven Steps"
date: 2026-08-24
status: methodology
scope: The canonical statement of the methodology this template implements. Authoritative reference for every skill, agent, and policy in the repo.
---

# The Agentic Coding Methodology

A methodology for writing software with AI coding agents in a way that scales beyond ad-hoc prompting. Each step involves conversing with or using LLMs. Apply it when scoping or structuring a coding project — not when answering one-off coding questions.

## The eleven steps

1. **Vague ideas → insights.** Turn vague ideas into insights, including competitive analysis. What problem are you actually solving? Who has already tried to solve it, and how? What do you need to learn before committing to a direction?

2. **Insights → brief.** Turn the insights into a brief: *what* to build. A brief is a durable document — it describes the product, the user, the goal, the constraints, the success criteria. It lives under `briefs/`.

3. **Brief → architecture document.** Decide *how*. This probably involves the LLM researching Best Current Practices (BCPs) for each technical aspect: which libraries, which protocols, which data formats, which platform conventions. The architecture document lives under `briefs/` too (or `ARCHITECTURE.md` at the root for very large efforts).

4. **Repo-level policies.** Put policies in place that enforce standards and practices. Examples: each completed phase must be incremental and testable; the repo tracks which phases are complete, in progress, up next, or yet to start; **objective acceptance is independently reviewed and gate-proved, while the human owns subjective and owner-only judgment** — gate-proved work is then committed and fast-forward-pushed by default, which is delivery rather than acceptance. Policies live under `policies/`. Every phase honors every policy.

5. **Brief + architecture → phased plan.** Break the work down by phase. Each phase is independently testable, mostly independently deliverable, and has a clearly defined goal and acceptance criteria. Phases live under `plan/`; the spine is `plan/INDEX.md`. Major phases are written *after* the brief (step 2) and architecture (step 3) exist — without those, the phase plan is speculation. If you find yourself wanting to plan phases before there's a primary brief, go back to step 2.

6. **Major phases up front, sub-phases just-in-time, ripple at every close.** Two scales, two rules:

   - **Major phases are drafted up front** to *general specificity* from the brief and architecture. Same shape as a full phase file (frontmatter + Goal + Deliverables + Acceptance + brief refs), at lower fidelity than the in-flight phase. The dependency graph in `plan/INDEX.md` enumerates them from the start. Some major phases stay monolithic — small phases that fit one session never need sub-phase decomposition.
   - **Sub-phases are JIT, one at a time.** At the start of a major phase, decompose only `phase-N.1` in full. Subsequent sub-phases (`phase-N.2`, `phase-N.3`, …) get drafted at *close* of the previous one, with the benefit of its outcomes. Pre-decomposed sub-phases lock in premature assumptions and resist the very revisions that doing the work earlier reveals.
   - **Bite size is capability-indexed.** Size sub-phases to the executing coder model's demonstrated coherence, not to a fixed calendar. Acceptance criteria, not session length, define a bite. The signal to coarsen: a model class that routinely closes phases of the current size with first-cycle approvals and green gates can safely take bigger bites — fewer, larger sub-phases, more major phases left monolithic. The signal to split finer: revision loops stalling instead of converging, build-gate fix cycles recurring. Per-phase ceremony (planning, review, logging) is a fixed cost; over-fine decomposition under a strong coder pays that cost more often than the work needs.
   - **Ripple propagation at every phase close.** When a phase (sub or major) closes, pinned decisions and surfaced concerns from its END block — plan-reviewer Observations, code-critic findings, deliberate scope changes — are propagated into downstream drafted phase files. Mechanical edits (renaming a path the closing phase pinned; adding a brief ref it introduced; tightening an Acceptance criterion to a now-pinned value) land automatically (AUTO). Judgment-level changes (a downstream Goal needs revision; a Deliverable becomes obsolete; the dependency graph shifts) surface to the user as named follow-ups (DECIDE). The orchestrator executes that classification at each phase close, and a DECIDE item left unresolved is an open gate, not a note.

   Net effect: the major-phase roadmap is visible at bootstrap; the orchestrator works one sub-phase at a time with each predecessor's outcomes baked in; the downstream sketches stay fresh as work proceeds rather than diverging from reality.

7. **Orchestrator-driven sub-phase execution.** Use a high-level orchestrator skill (`kickoff`) that delegates the initial implementation and owns candidate-bound evidence. It:
   - determines the current phase,
   - invokes a **planning agent** to turn the current sub-phase into a file-level plan,
   - hands the plan to a **plan-reviewer agent**,
   - hands the (possibly revised) plan to a **coding agent**,
   - hands the result to a **code-critic agent**,
   - on any critic's complaint, assigns stable finding ids and sends the work
     back to the relevant agent with a deterministic revision packet;
   - binds review and gate records to the exact candidate tree.

   *One step, a lot happening. Each of those four roles is a specialist with its own tool stance, reading protocol, and verdict format.*

   Review intensity is risk-adaptive: a phase may declare a **review lane** in its frontmatter. The default `full` lane runs all four roles; a `light` lane — mechanical phases only — skips initial plan review while keeping the initial code critic, who also guards the lane and escalates back to `full` when the work exceeded mechanical scope.

8. **Acceptance check.** During convergence, the coder runs the smallest
   falsifying tests and affected revision-close gates. After code-critic
   approval, the orchestrator runs the complete phase-prescribed sequence and
   `./bin/check all` once against the unchanged candidate. A failure or
   concrete user correction is routed proportionally: the orchestrator may
   apply a small low-risk fix directly, use the coder alone for a low-risk
   delegated fix, or repeat the coder → critic cycle when risk is high or the
   change is large/cross-cutting. A failed lightweight attempt upgrades to the
   full cycle; every relevant change invalidates prior gate evidence.

9. **Append-only phase log and lessons harvest.** Use an append-only log (`LOG.md`) to **open, park, and close** work on every phase. Every block is appended at true EOF; committed bytes are an exact prefix, and chronology corrections are later authenticated records rather than historical edits. END and PARK both harvest every role's Process Observations, revision failure analyses, wall-clock observations, and relevant dispositions into the `lessons/` ledger — filing a new scope-classified lesson or appending an occurrence to an existing one. `None` is valid; skipping the question is not. After the handoff gate, the orchestrator ordinarily commits and fast-forward-pushes the accepted tree; the terminal block remains the human's compact audit surface, read at the seam rather than before the commit.

10. **Human evaluation where judgment is required.** Objective criteria — executable, independently reviewed, proved by a complete gate against the exact candidate — close autonomously, and the phase is delivered. Every named manual, subjective, product, custody, or owner-only criterion still parks for the human, who evaluates the sub-phase at the seam (the END block and the demo protocol) and re-invokes the orchestrator to refine or fix anything found. This is where the human exercises engineering, UX, and product judgment. **The orchestrator never fabricates that acceptance, and delivery never substitutes for it.**

11. **Stay agile.** Add new phases, or break existing phases into more sub-phases, as the problem and solution space become clearer. The phase plan is mutable. Phases that turn out to be wrong are split, merged, or rewritten.

## How to apply this methodology

When you're starting or scoping a coding project, work through these steps in order — don't jump to coding. Concretely:

- If you have only a vague idea, push to step 1: surface insights and do competitive analysis before committing to a brief.
- If a brief exists but no architecture, do step 3 and research BCPs.
- If architecture exists but no phase plan, do step 5.
- If a phase exists but no sub-phases, do step 6.
- If a sub-phase is being executed, follow step 7's orchestrator pattern (planner → planning critic → coder → coding critic, with revision loops).
- Whenever a phase opens or closes, write to the append-only log (step 9) with explicit evidence; at close, also run the mandatory lessons harvest and surface graduation-ready candidates for human ratification.

## The four canonical agents

The methodology's orchestrator delegates to four specialist roles. Their names are load-bearing — the orchestrator invokes them by name, each with a fixed tool stance and a verdict emitted under an exact `## Verdict:` header that the orchestrator matches by string.

| Role | Reads | Writes code | Job |
|---|---|---|---|
| `phase-planner` | Briefs, plan, repo | No | Turn one phase into a file-level implementation plan |
| `plan-reviewer` | Briefs, plan, repo, plan output | No | Approve the plan or send it back for revision |
| `phase-coder` | Briefs, plan, repo, approved plan | Yes | Implement the approved plan and run focused/revision-close gates |
| `code-critic` | Briefs, plan, repo, code diff | No | Approve the code or send it back for revision |

The orchestrator (`kickoff`) is the fifth participant. It delegates initial
implementation; owns authority, change, finding, and gate evidence; handles
verdicts, the implementation-candidate and handoff gates, the lessons harvest,
and `LOG.md`; and may write code only for a small,
low-risk follow-up correction whose intended shape is already determined.

## Non-negotiables

- **Every completed phase is incremental and testable** (step 4).
- **Every initial phase implementation passes the code critic**, whichever review lane it declares; repeat review on follow-ups is risk- and size-based (steps 7–8).
- **The human owns subjective and owner-only acceptance; objective acceptance is independently reviewed and gate-proved** (steps 4, 8, 10).
- **The orchestrator writes code only for eligible small, low-risk follow-up corrections** (step 8).
- **Closing a phase requires recorded evidence and a lessons-harvest answer**, not just a green test run (step 9).
- **Research authority follows the role across harnesses.** Planner and
  reviewer may originate search and retrieve; coder and critic retrieve only
  plan- or brief-identified sources and same-host structural neighbors. The
  ambient resource set is allow-by-default, but no named MCP server or plugin
  is presumed available.
- **Closing has two gates.** The complete candidate-bound sequence runs before
  evidence finalization and tracked bookkeeping; a second bare full gate runs
  on the resulting handoff tree, after which no tracked write is permitted.
- **Phases and sub-phases are mutable**; refactor the plan as understanding grows (step 11).

## Orchestration runtime doctrine

Hard-won rules for step 7 when the loop runs fail-closed and unattended. Distilled from a production day in a derived repo in which one orchestration halted nine times: each halt was diagnosed, cured, and compiled into a standing rule; these are the rules.

- **Fail-closed park, diagnosed self-resume.** Any first-encountered defect halts the run and writes an honest park record. A halt whose cause is *novel* for the phase, fully diagnosed with a recorded causal correction, and whose integrity proofs pass (candidate restoration or explicit lineage, prior evidence read-only, governed resources released) may self-resume without waiting for the human — against a small budget (three self-resumes between human contacts is a working default). A *recurring* cause class always stops for the human: recurrence means a generator the cure didn't reach. The budget is a configured number in `kickoff.yaml`'s `run_budgets.self_resume` key, and any operator relay restores it.
- **Executable authority precedes expensive acceptance.** Every full-evidence run carries an immutable content-addressed command manifest, a configuration-bound venue receipt proved by a real read of unpredictable local bytes, and separate product/full-tree identities. Command zero validates that topology, selector dry-runs, formatting, and append-only log custody in fixed cheap order before a full gate begins. One novel bookkeeping failure may receive one atomic deterministic repair only when the complete bytes are derivable and product identity remains unchanged; ambiguity, recurrence, or a second attempt parks.
- **Never round-trip deterministic work through a model.** Bookkeeping rebases, identifier substitutions, and small revisions to large documents are orchestrator-performed, byte-diff-proven transforms; the displaced model role reviews the result instead of producing it.
- **No artifact larger than one model response travels a single-message channel.** Large documents are revised by delta plus deterministic merge. A model asked to re-emit a big document verbatim will summarize it or paginate it, and either way the artifact is wrong.
- **Qualify every measuring instrument outside the evidentiary run** before it gates anything: exercise every branch, prove aim (the probe demonstrably measures the intended target), and prove falsifiability (a deliberately wrong probe must fail). An assertion that can only pass is not evidence — a mis-aimed probe can emit green forever.
- **Embed every contract verbatim in the dispatch prompt**, rendered from the enforcing source — never trusted to model memory, never inferred from prose in an upstream document. This includes closed vocabularies, artifact schemas, and output-shape requirements.
- **Designed human checkpoints are satisfying stops**, enumerated in advance so continuation machinery never bulldozes holds that exist for the human. Every other stop is classified before it is cured — legitimate park, defect, contract mismatch, or model behavior — because each class takes a different fix, and retrying a generator-class cause can never converge.
- **Run an out-of-band supervisor** for long orchestrations: a second session with no write access to the worker's context that reads its trace, verifies every load-bearing claim against ground truth, and drafts steering the human ratifies and relays. The supervisor's real job is compiling incidents into standing rules so each failure class dies after its first appearance.
- **Choose the weakest instrument that can falsify the defect class under test** — and when a design change eliminates a defect class, retire its instrument instead of perfecting it. Fail-closed pressure ratchets instruments (every defect adds rigor; nothing subtracts), so every instrument repair first re-asks whether the measured property still needs measuring. (Observed in a derived repo: a pixel-analysis rig built for a paint-level rendering defect survived the geometry redesign that made the defect impossible, then consumed revision cycles perfecting arithmetic a bounding-box ratio had made unnecessary.) Altitude also has a time axis: before any instrument repair or new machinery, check the project's briefs, plan ledger, and pinned decisions for a scheduled change that obsoletes the repaired surface — a reset, migration, rewrite, or retirement. A fix for data or code the roadmap already deletes is the ratchet in a new coat, and the operator's half-memory of such a plan ("didn't we write a brief on this?") is a signal to go read it, not to reason from the recollection. (Observed: a validator exception proposed for one legacy ledger row in a store the project's own plan had already scheduled for reset.)
- **Every falsification control must itself be provably satisfiable.** Instrument validity has two sides: a deliberately wrong probe must fail for its intended reason, and the specified control must be mathematically capable of succeeding under the declared comparator and fixture. Plan review checks satisfiability at specification time — an unsatisfiable control is the mirror image of an assertion that can only pass.
- **A machine check fully shadowed by a designed human gate defaults to advisory.** Binding machine checks guard decisions no human gate in the same flow will see; a check whose failure the human reviewer would catch anyway earns recording rights, not parking rights.
- **Structure every ratification artifact orientation-first.** Human approval gates degrade under density as well as volume — a single dense technical artifact defeats an attentive ratifier when the decidable facts are buried ("approval snow blindness," the density-side cousin of approval fatigue). Every artifact seeking ratification opens with plain-language beats (where we are, what happened, what approval authorizes — a couple of sentences each), keeps the decision payload in a fixed predictable position, and makes the producer own legibility. The receiver restating the ask before approving (read-back) is the strongest known forcing function.
- **Preflight the environment before staking an unattended run on it.** A fail-closed probe ladder — repository baseline, committer identity, toolchain launch, temp and platform capabilities (file clones, database journaling, sniffing backends), permission-escalation mechanics, and the authoritative gate as a pre-work baseline — runs *before* the tasking prompt, with every probe read-only or self-cleaning and a printed PASS/FAIL table. Environment barriers come in layers, and each probing round surfaces exactly one (observed: three distinct sandbox boundaries in three successive rounds — a direct write denial, a cache-initialization denial, and a platform-API panic). Fixes land as durable configuration, never session memory, and the green baseline doubles as the classifier for every later failure: after a green baseline, every failure is the run's own.
- **A well-specified isolated task may run as a goal-armed one-shot** instead of the full four-role loop: a complete binding spec that already passed operator review (which substitutes for plan review), a new-files-only write set with a park on any widening, designed parks enumerated as satisfying stops, a durable goal whose compact objective carries the outcome, the printed proof, and the park-satisfying clause, authoritative gates as the external verifier, and independent verification against the recorded baseline before push. Goal durability is harness-specific: one harness lets the agent arm its own goal from the tasking prompt and persists it as database state across compaction; another's goal is context-fragile and silently cleared by compaction — know which you have before trusting continuation to it. Role machinery at this scale is ceremony; an observed cost profile of roughly 2:1 environment-proving to implementation was worth every minute.
- **Authoritative gates run in the native execution context.** Sandboxed gate output can contain phantom failures — and therefore phantom evidence in either direction. Classify sandbox-vs-real with one native baseline run before work begins; a gate that could not run is "not run," never "passed"; route gate and commit commands through the proven native or escalated mechanism; and never cite in-sandbox gate output as evidence. (Observed twice in one day: a coder's hundred-plus in-sandbox test failures that were all phantoms save one real regression, and a preflight's in-sandbox gate failing while the native run of the same gate was green.)
- **Scope loop-extension grants by convergence, not counts.** The runaway
  backstop's default count stands for ungoverned loops, but an explicit
  extension grant is a *convergence lease*: continue while each cycle
  strictly shrinks the open-finding set, nothing closed reopens at
  equal-or-worse severity, no new defect class appears, and the touched
  surface stays within named bounds — park on first violation, any guard
  trip, or an operator-only hard ceiling. Counts measure effort, not
  health; count-scoped grants expire mid-convergence and page the operator
  to re-authorize work that never stopped working. An out-of-band
  supervisor may judge the lease's invariants and, below the ceiling,
  decides whether another cycle is worth the effort (operator directive in
  a derived project, 2026-08-13 — the ceiling, raised 5 → 10 the same day,
  is a circuit breaker against runaway iteration, not a work quota); a
  *tripped* backstop and the ceiling itself remain operator-only.
  (Observed 2026-08-11 in the same project: three count-scoped
  micro-grants in one day on a strictly-converging loop, each an operator
  round-trip during their absence; two of the phase's three parks and three
  relays traced to count expiry rather than any defect.) Mechanized in
  `policies/four-canonical-agents.md § Convergence-lease grants`.
- **Stop an outward spiral at its premise.** A defensive requirement,
  refusal, guard, compatibility behavior, or mandatory proof joins the target
  only when it is backed by an observed failure, an explicit operator
  decision, or the contract of an actually targeted platform and operating
  mode. On every revision, the reviewer asks what failure justifies the
  change, whether it stays inside the authorized actors and environments, and
  whether it moves the fixed target closer or moves the target outward. An
  unsupported premise becomes an owner question before another implementation
  pass; counts may describe divergence but do not decide it. (Observed in a
  derived project: a single-writer macOS preview repair widened into Windows
  compatibility and arbitrary concurrent-filesystem mutation defenses, even
  though deployment was a static read-only Linux artifact. Repeated reviews
  added machinery and new blocking classes until the operator removed the
  invented premises.) This is a judgment protocol, not a semantic detector:
  the reviewer explains the failure basis, operating envelope, and direction
  of travel in the verdict, and an unsupported premise parks for the operator.
- **Doctrine and ceremony grow only against incidents, and every review prunes.** A new binding rule or protocol step enters only with its motivating incident cited inline; foresight proposals remain candidates (the `lessons/` ledger is the holding pen), never rules. Every binding step names the park it prevents. Every review pass — plan review, code review, `sweep` — treats steps whose failure families are structurally dead as deletion candidates, because fail-closed pressure ratchets ceremony (every defect adds rigor; nothing subtracts) and only deliberate pruning reverses it. This generalizes the instrument-retirement rule above from measuring instruments to every binding step of the protocol itself. The worked form is a **ceremony audit**: walk every binding step of an orchestration protocol, require each to name the park it prevents or cite its motivating incident, and delete or demote the rest. (Observed in a donor repo: a full audit under this rule deleted or demoted four binding steps, including a strictness family whose every production firing was a comparator false positive and a per-fix reseal duty — roughly twenty-seven whole-repository reseal cycles in one phase, each invalidated by the next one-line fix — judged pure ceremony in the phase's own closing verdict.)

## Run-lifecycle vocabulary

Four words with exact meanings, evolved in fail-closed orchestration practice. The field has partial equivalents for one of them and none for the rest; teach them as a set:

- **Finalized** — a run's lifecycle is closed with its outcome recorded, *failure included*. A failed run still gets a truthful terminal record.
- **Sealed** — an artifact passed its acceptance gate and is closed as evidence: digest-bound, immutable, and cited by later stages instead of re-derived (the coder implements against the sealed plan; the after-capture compares against the sealed baseline). This is working shorthand for what the software supply-chain world formalizes as **attestation** — a subject bound by cryptographic digest to a predicate about what it passed. Git commits are the sealing substrate every engineer already trusts: a commit seals *what* existed; a seal adds *why you may rely on it* (commits-plus-verdicts). Runs additionally need working-state seals — a deterministic tree hash covering uncommitted and untracked-unignored work (`bin/kickoff-tree-id` here) — for the interval before the phase-close commit seals everything durably. Seal at every trust boundary: run open, before and after each role dispatch, evidence acceptance, restoration proofs, run close. Keep the sealer cheap enough that ubiquity costs nothing — a flat SHA-256 manifest over a few thousand files runs in a fraction of a second, so hundreds of daily invocations cost about a minute.
- **Frozen** — tooling (not evidence) made byte-identical and read-only under a recorded manifest, so later runs provably execute the qualified instrument rather than a drifted copy.
- **Parked** — the run-level stop discipline defined in the doctrine above: a deliberate, orderly stop with a written causal account, nothing disturbed, a clean proven scene, and explicit resume conditions. Distinct from the field's *interrupt/pause* (designed suspension awaiting input), *checkpoint* (the state snapshot that makes resuming cheap — machinery, not discipline), and *halt* (ending execution with no promises at all).

**Enforcement status:** these are doctrine, not yet mechanics. Self-resume budgets in `kickoff`, delta-merge tooling, and instrument-qualification harnesses are not yet mechanized in this template; until they land, the `kickoff` prose loop and the human relay carry these rules.

## What this methodology gives up

Honest accounting of the cost.

- **Speed of a single throwaway iteration.** A one-line ad-hoc prompt is faster than spinning up a brief, a plan, and a phase. Use ad-hoc for one-off scripts; use this methodology for projects that will exist next month.
- **Unbounded autonomy.** Objectively accepted phases deliver themselves — committed and fast-forward-pushed unattended — but the methodology still parks at every designed manual, subjective, product, custody, destructive, or owner-only gate, and silence never becomes judgment. If your goal is code generation with no human gates at all, this is still the wrong tool.
- **Flexibility within a session.** The orchestrator follows the plan. If you want to wander, do it before `kickoff` starts or in between phases — not mid-orchestration.

What you get in exchange: each phase leaves a reviewable artifact pair (END block + commit diff), the next session resumes from a known state without re-explaining anything, and the structural surface (briefs, policies, plan, log) tells the next human contributor — or the next session of you — what's true about the project.

## Related skills

- **`kickoff`** — runs steps 7–9 for one sub-phase, end-to-end.
- **`stamp`** — runs the bootstrap procedure described in [`agentic-bootstrap.md`](agentic-bootstrap.md) to stand up a new repo under this methodology.
- **`methodology`** — re-states this brief as a skill, invoked as `/methodology` in Claude Code or `$methodology` in Codex, for sessions that need a reminder without reading the whole file.
- **`learn` / `teach`** — move ratified methodology patterns and scope-classified lessons between the starter hub and project repos under explicit user approval.
- **`sweep`** — audits policies, briefs, skills, agents, catalogs, and the lessons ledger; proposes pruning and graduation decisions for human ratification.
