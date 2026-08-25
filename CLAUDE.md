# CLAUDE.md

This file provides guidance to coding agents (Claude Code, Codex CLI, and others that read top-level instruction files) when working in this repository.

This file has two zones. **Project Context** is everything specific to *this* repo — the project's thesis, the deliverable's surface, the language conventions, the project-specific briefs and skills. `stamp` rewrites this zone when stamping out a new project. **Methodology Contract** is everything universal to the agentic methodology — methodology briefs, every policy, the phase-work protocol, universal conventions, the glossary. `stamp` copies this zone verbatim. The two zones are demarcated by HTML comment markers; both humans and `stamp` use the markers to find the boundary. Above both zones is a small **Hard rules** section that governs every action regardless of zone — these are too consequential to risk an agent missing them by reading top-down and stopping early.

## Hard rules — read these before any action

These rules govern every action in this repo. They are placed above both zones so an agent reads them before doing anything irreversible. The full policy text for each is in `policies/`; consult that before bending the rule. Rules 1 and 2 are universal (apply to this template and to every project `stamp` derives from it). Rule 3 is **starter-only** — it does not propagate to derived projects.

1. **Deliver gate-proved work; the user owns judgment and the destructive git surface.** Once a phase closes with every gate green, the orchestrator commits and fast-forward-pushes it — staging only its explicit paths (never `git add -A` or `git add .`, since this checkout may be shared), with no agent credit and never `--no-verify`. Everything else stays the user's: `git tag`, `git reset --hard`, `git branch -D`, `git rebase`, `git checkout --`, `git clean -fd`, force-pushing, creating or selecting a remote, and any history rewrite. An unexpected path in `git status`, a hook refusal, a missing or ambiguous upstream, a rejected push, divergence, or residual dirt **parks delivery** — report it and wait; never work around it. **Delivery is not acceptance.** Manual, perceptual, product, and custody criteria — and the phase's `User Demo:` protocol — stay open for the user *after* the work is delivered, and the orchestrator never claims them. What does block a phase from closing at all is an unresolved *gate*: a failed build gate, an unmet executable criterion, an open `DECIDE` ripple. Full policy: [`policies/human-in-the-loop.md`](policies/human-in-the-loop.md).

2. **Greenfield until released: no backward-compatibility code.** Do not write legacy aliases, `@deprecated` markers, schema migrations to read older formats, transitional code paths, version-conditional branches, or "compat" shims of any kind. When an earlier shape turns out wrong, replace it directly and update every call site, fixture, test, sample data file, brief, plan, and doc in the same phase. This rule ends only when the project ships a stable external release and explicitly amends the policy. Full policy: [`policies/greenfield-until-released.md`](policies/greenfield-until-released.md).

3. **Anonymize external-repo references in committed files. (Starter-only.)** This repo will be public. Every committed file that documents or references a cross-repo operation — a `LOG.md` entry from `learn` or `teach`, an archived `user-actions-archived/` disposition, a policy example, a brief — must anonymize external project names, commit SHAs, daemon / CLI / MCP-tool names unique to the external repo, internal repo paths beyond what is structurally identical to this template, and proprietary identifiers, *before the file is written*. Use `Donor A` / `Donor B` / … to distinguish multiple donors; use `the donor` / `the target` when there is one and no ambiguity. Do not commit unanonymized content with the intent to fix later — once pushed, the data is leaked even after a later rewrite (SHA still resolves on forks and caches). Run `bin/check-anonymization.sh` before any push; it deterministically catches real paths and commit SHAs across the whole tree. This rule is starter-only because the asymmetry is driven by this repo's publicness, not by any methodology principle; derived projects' files are their own business. Full policy: [`policies/anonymize-log-references.md`](policies/anonymize-log-references.md).

If the user explicitly restricts or waives one of these rules for a named scope ("keep Phase 1.1 local — don't push it"; "keep the v1 reader for one week so I can re-render"), record it verbatim in the phase's END block. Restrictions and waivers are one-shot; the next phase reverts to the default. A restriction narrows delivery only — it never relaxes a gate and never closes a parked criterion.

<!-- PROJECT_CONTEXT_START -->

# Project Context

## This Repo is the Agentic Coding Starter Template

A *master template* for projects built with AI coding agents under a structured planner → reviewer → coder → critic methodology. The entry-point brief is [`briefs/BRIEF.md`](briefs/BRIEF.md).

This repo is also a working project in its own right. Open it in either supported harness and invoke the `kickoff` skill (`/kickoff` in Claude Code; `$kickoff` in Codex) to pick up Phase 1 from `plan/INDEX.md`.

## Project briefs

In addition to the universal methodology briefs (see Methodology Contract below):

- [`BRIEF.md`](briefs/BRIEF.md) — entry-point brief for *this* repo: thesis, what the template provides, when to use it, the two operating modes (template-stamp vs. self-build), and acceptance criteria.
- [`methodology-treatise.md`](briefs/methodology-treatise.md) — "Wolf's Agentic Coding Starter Kit": the canonical introduction to this repository for a general audience, from working engineers to readers who have never written code. Argues that an agent becomes reliable when the project holds the memory, the rules, and the evidence, and supports it with the ledger and append-only log, the four separated roles and the two-gate close (including the typed acceptance boundary and autonomous delivery), and the lessons ledger with human-only graduation. Carries the honest costs and the internal limits. Source of truth for every derivative rendering; corrections land here first per [`policies/treatise.md`](policies/treatise.md).
- [`eacp-pattern-map.md`](briefs/eacp-pattern-map.md) — maps this repo's structures onto named patterns from the Encyclopedia of Agentic Coding Patterns, with file-level evidence: the orchestration spine, durable state, feedforward controls, feedback sensors, governance and provenance; plus the patterns deliberately declined, the antipatterns structurally guarded against, where the repo extends the corpus, and the gaps.

## Project surfaces

- `project/` — the deliverable: runtime pin, package metadata, source, tests,
  and lockfile. Self-contained per
  [`policies/project-isolation.md`](policies/project-isolation.md) — nothing
  inside `project/` references anything above it. Currently holds a minimal
  Python example so the toolchain contract has a real target from the first
  session.

## Project conventions

- **Python 3.11+** is the supported range; `project/.python-version` selects
  Python 3.11 as Starter's reproducible managed default. Type hints on all new
  public functions; idiomatic stdlib where the difference is small.
- **`uv` with `.python-version`, `pyproject.toml`, and `uv.lock`** owns the
  example environment. `tool.uv.python-preference = "only-managed"` prevents
  an ambient system interpreter from silently winning.
- **The repository-owned toolchain contract is atomic.** `./bin/setup`
  provisions the locked environment, `./bin/test [args...]` runs full or
  focused tests, `./bin/check all` is the authoritative suite, and
  `./bin/python` selects the project interpreter. Callers never assume
  `python3.12` or another versioned binary is on `PATH`. Each wrapper uses the
  shared real-dependency probe; `TOOLCHAIN_PYTHON=/absolute/path/to/python` is
  an authoritative compatibility-test override and never falls back.
- **`project/pyproject.toml` is the single source of truth** for Python tooling configuration (ruff, pytest, mypy if used) in this repo.

## Model & review venue

Which model runs each `kickoff` role is set under `role_models` in human-editable `kickoff.yaml` (directly or via `roles`), scoped by which harness orchestrates. Model and effort are separate fields; the model implies its CLI. The shipped default routes reviewer + critic to the other harness (`codex` from Claude Code; `model: opus`, `effort: high` from Codex) and leaves planner + coder native. Before phase state begins, `kickoff` live-validates every non-native target and aborts on any upstream failure. Governed by [`policies/role-models.md`](policies/role-models.md); invocation recipes in [`briefs/cross-agent-invocation.md`](briefs/cross-agent-invocation.md).

## Project-specific skills

In addition to the universal `kickoff`, `methodology`, `learn`, `teach`, `roles`, and `sweep` skills (carried into every derived project):

- **`stamp`** — starter-template-only bootstrapping skill. Stamps out a new project from this repo. Registered for Codex in this template repo only; not carried into derived projects. Source: `.claude/skills/stamp/SKILL.md`; Codex native skill: `.agents/skills/stamp`.

<!-- PROJECT_CONTEXT_END -->

<!-- METHODOLOGY_CONTRACT_START -->

# Methodology Contract

## Methodology briefs

- [`methodology.md`](briefs/methodology.md) — the eleven-step pipeline: vague ideas → insights → brief → architecture → policies → phased plan → sub-phase decomposition → orchestrator-driven execution → acceptance → log → human evaluation → stay agile. Includes the orchestration runtime doctrine — sixteen fail-closed rules for unattended stretches (diagnosed self-resume, deterministic substitution, the single-message artifact ceiling, instrument qualification and altitude with its time axis, falsification-control satisfiability, advisory-when-human-shadowed, orientation-first ratification artifacts, contract embedding, designed stops, out-of-band supervision, the environment preflight ladder, the goal-armed one-shot lane, native-context gates, convergence-lease loop extensions, incident-gated ceremony growth with pruning on every review) — and the run-lifecycle vocabulary (finalized / sealed / frozen / parked, with sealed as working shorthand for attestation). Doctrine now, mechanics deferred (self-resume budgets excepted — see `policies/fail-closed-resume.md`).
- [`agentic-bootstrap.md`](briefs/agentic-bootstrap.md) — procedure for standing up a new project from this template: anatomy of the structure, what to transfer verbatim vs. rewrite vs. discard, step-by-step procedure, sanity-check protocol.
- [`cross-agent-invocation.md`](briefs/cross-agent-invocation.md) — best current practices for invoking one coding-agent CLI from inside another (Claude Code ↔ Codex): headless flags, sandbox/permission posture, capture contracts, failure modes; rationale for cross-harness review.
- [`incremental-orchestration.md`](briefs/incremental-orchestration.md) — implemented evidence plane for candidate-bound review, delta revision packets, focused iteration checks, separate implementation-candidate and post-bookkeeping handoff gates, recoverable incomplete event streams, and effectiveness-preserving attention to human wall-clock cost.
- [`deterministic-orchestration.md`](briefs/deterministic-orchestration.md) — **draft.** Design and decision criteria for encoding `kickoff`'s delegate → verdict → route-back loop as a deterministic workflow program. Deferred until every supported harness ships a parity workflow primitive; the prose loop in `kickoff/SKILL.md` remains canonical until then.
- [`harness-self-improvement.md`](briefs/harness-self-improvement.md) — the two-tier improvement flywheel: phase-scale lessons capture (roles emit Process Observations; `kickoff` harvests into the `lessons/` ledger; recurring lessons graduate under human ratification), the `sweep` maintenance pass, and repo-scale propagation (`stamp` ships the machinery, `teach` retrofits it, `learn` harvests `scope: methodology` lessons back). Records the declined patterns and the deferred contract-versioning DECIDE.
- [`session-context-compaction.md`](briefs/session-context-compaction.md) — managing harness context compaction during long orchestration runs: verified harness facts (the model can neither invoke `/compact` nor see its own fill level), why mid-arc compaction severs evidence bindings, measured per-arc token economics, the safe-boundary pause protocol (a capacity pause must show its arithmetic), and an unimplemented hook-based automation option.

## Policies catalog

Every file under `policies/`, indexed so agents see the catalog without an extra Read. A policy is a non-negotiable rule every phase honors.

- [`README.md`](policies/README.md) — what `policies/` is and how it differs from `briefs/`.
- [`briefs.md`](policies/briefs.md) — the brief-file lifecycle: frontmatter schema (`title`, `date`, `status`, `scope`), four-value status flow (`draft` / `methodology` / `implemented` / `historical`), filename conventions, when to write one, when to retire one.
- [`briefs-and-policies.md`](policies/briefs-and-policies.md) — the contract: briefs describe, policies prescribe, plan sequences.
- [`cross-harness-parity.md`](policies/cross-harness-parity.md) — keep Claude Code, Codex CLI, and any other supported harness in lockstep; canonical files vs. mirrors; onboarding a new harness.
- [`four-canonical-agents.md`](policies/four-canonical-agents.md) — the four roles `kickoff` invokes by name; their tool stances; their verdict headers; convergence-bounded revision loops (iterate while converging, escalate on stall, 10-cycle runaway backstop, convergence-lease extension grants).
- [`role-models.md`](policies/role-models.md) — harness-aware per-role model/venue in `kickoff.yaml`, with separate model and effort fields. Direct edits and `roles` are both supported; `bin/kickoff-config` preserves comments and `extensions` data, preflights every non-native target before phase mutation, and owns runtime fallback/reporting mechanics.
- [`role-timeouts.md`](policies/role-timeouts.md) — first-event, idle-progress, and hard deadlines under `kickoff.yaml`'s `role_timeouts`. The unified manager enforces external calls, records gitignored telemetry, and recommends evidence-based recalibration without rewriting values automatically.
- [`research-authority.md`](policies/research-authority.md) — role-based search and retrieval authority: planner/reviewer may search and retrieve; coder/critic retrieve plan- or brief-identified sources plus same-host structural neighbors; external research is GET-only; installed MCP servers and plugins are allow-by-default without assuming any named resource exists.
- [`orchestration-evidence.md`](policies/orchestration-evidence.md) — binds review, revision, findings, and gates to exact candidate identities; requires fresh run-scoped evidence, delta packets with fail-closed rebasing, a focused-to-final verification ladder, and explicit protocol recovery. Also the fail-closed recoveries: the unconditional unmeasured-review-pass latch that surfaces a missing convergence measurement while a re-ingest still costs one command; the derived-metrics overlay for a review pass whose batch was structurally refused, recomputed by `validate` from the ingest journal and stored artifacts; and candidate-drift classification for a tree that moves under an in-flight dispatch — an append-then-amend dispatch lifecycle whose open/return candidate pair brackets the child, a write-once candidate manifest store, and a fail-closed three-check acceptance (declared partition ∧ reviewed surface ∧ declared authority) re-derived at every `validate`.
- [`execution-telemetry.md`](policies/execution-telemetry.md) — requires one exact shared execution trace for stages, roles, waits, tools, and gates plus a separate operator-input park ledger; defines union-based timing metrics, exact same-boot and visibly non-exact cross-boot park durations, fail-closed joins/recovery, privacy projection, and deterministic offline end-of-phase HTML reports.
- [`mechanistic-vs-intelligence.md`](policies/mechanistic-vs-intelligence.md) — the triage rule: route each repeatable task to a deterministic script in `bin/` (consistency, determinism, repeatability) or to intelligence (synthesis, judgment, generativity). Don't burn a model on what a script does better, or script what needs judgment; split mixed tasks at the seam, and stay alert to conspicuous low-effort wall-clock improvements in expensive mechanics.
- [`build-gates.md`](policies/build-gates.md) — every repo owns an atomic,
  cwd-independent setup/test/check contract backed by its runtime pin,
  committed metadata, lockfile, behavioral tests, callers, and durable
  candidate-bound full-gate receipts; language values remain repo-specific,
  failures stay visible, receipt misses fail closed, and hook installation is
  opt-in.
- [`fail-closed-resume.md`](policies/fail-closed-resume.md) — mechanizes the doctrine's park/resume rules: fail closed first, five-part failure signatures with an append-only novelty ledger, the seven-condition diagnosed self-resume against `kickoff.yaml`'s `run_budgets.self_resume` budget, prelaunch-correction-is-not-a-resume, mechanistic substitution, sealing as a close-time act, instrument qualification, and the required park/resume record.
- [`review-lanes.md`](policies/review-lanes.md) — risk-adaptive review intensity and proportional follow-up routing. A phase declares `review_lane: full` (default; all four roles) or `light` (mechanical initial work; plan review skipped); the invocation-only `one-shot` lane (coder → critic) runs well-specified isolated phases at the human's explicit token. The orthogonal `evidence_lane: full|light` axis scales candidate-bound ceremony, fail-closed against authority/irreversible/deploy triggers, with the close seal always mandatory. Every initial implementation gets a code critic; later test- or user-driven corrections use direct, coder-only, or full-cycle routing according to risk and size.
- [`phase-status.md`](policies/phase-status.md) — status markers live only in `plan/INDEX.md`; no `status:` field in per-phase frontmatter; `kickoff` owns transitions.
- [`phase-ripple.md`](policies/phase-ripple.md) — at phase close, pinned decisions from the closing phase propagate into downstream drafted phase files. AUTO ripples (mechanical) land in the same session; DECIDE ripples (judgment) surface as named follow-ups in the END block.
- [`acceptance-empirical.md`](policies/acceptance-empirical.md) — every phase's Acceptance section lists verifiable shell commands or named manual checks. "It compiles" is not acceptance.
- [`user-demo-protocols.md`](policies/user-demo-protocols.md) — when a phase touches a user-facing surface, Acceptance carries an interactive try-it-yourself protocol (entry point, suggested inputs, what to look for, variations). When there's nothing meaningful to demo, declare `User Demo: N/A` with a one-line reason instead. Silence is blocking; contrived demos are blocking.
- [`treatise.md`](policies/treatise.md) — requires outward explanations to derive from canonical briefs/policies, lead with decisions rather than file inventories, preserve claim provenance and audience-specific disclosure, and stop at the two-part external publication gate. A treatise records its editorial intent in a `treatise:` frontmatter block on its own brief — purpose, audience, register, coverage, a dated log of operator directives, renderings, and external facts with retrieval dates — validated by `bin/treatise`.
- [`verification-discipline.md`](policies/verification-discipline.md) — requires verification to name blind spots, treat grep as a lead rather than a finding, avoid blacklist-as-closed-world claims, test proxies for sign inversion, and make material counts reproducible.
- [`log-discipline.md`](policies/log-discipline.md) — `LOG.md` is append-only and owned by `kickoff`. Never hand-edit historical entries.
- [`user-actions.md`](policies/user-actions.md) — `user-actions/` at the repo root is the live queue of human-only action items, one file per action (`<slug>.md`, YAML frontmatter); closed actions move to `user-actions-archived/`; no index. Glob at session start; surface relevant items before doing dependent work.
- [`lessons.md`](policies/lessons.md) — `lessons/` at the repo root is the ledger of candidate process lessons, one file per lesson (`<slug>.md`, YAML frontmatter, `scope: local | methodology`); graduated/rejected lessons move to `lessons-archived/`. Agents file and recur lessons; only the human graduates one into a policy, brief, skill, script, test, or invariant — at three occurrences or explicit approval. One occurrence row per observation (batched rows silently suppress the graduation trigger); rhyming diagnoses may be named as a family without merging. `bin/lessons` validates and tallies.
- [`human-in-the-loop.md`](policies/human-in-the-loop.md) — where the human's judgment binds. Objective criteria (executable, independently reviewed, gate-proved, candidate-bound) close autonomously and the phase is delivered; subjective, manual, product, custody, and owner-only criteria always park. The orchestrator never advances past unresolved gates, never claims subjective acceptance the human owes, and never touches the destructive git surface.
- [`repo-relative-paths.md`](policies/repo-relative-paths.md) — no absolute `/Users/...` paths in committed files. Bash commands may use absolute paths.
- [`project-isolation.md`](policies/project-isolation.md) — when the repo has one primary deliverable, isolate it under `project/`; nothing in there references anything above it. Makes the deliverable submodule-ready.
- [`greenfield-until-released.md`](policies/greenfield-until-released.md) — a project is greenfield by default until first stable release. No backward-compatibility shims, legacy aliases, schema migrations, or transitional code paths. Replace old shapes directly.
- [`anonymize-log-references.md`](policies/anonymize-log-references.md) — **starter-only** (not inherited by derived projects). Every committed file (not just `LOG.md`) that references a cross-repo operation must anonymize external project names, commit SHAs, and proprietary identifiers, because this repo will be public. Enforced mechanically by `bin/check-anonymization.sh`.

## Universal repo layout

- `briefs/` — durable design library. Each brief is markdown with YAML frontmatter (`title`, `date`, `status`, `scope`); brief-file lifecycle is governed by [`policies/briefs.md`](policies/briefs.md). See "Methodology briefs" above for the universal briefs, and "Project briefs" in Project Context for this repo's specifics.
- `policies/` — non-negotiable rules. Full catalog above.
- `bin/` — the repo's deterministic executables: the mechanistic half of the
  methodology. [`bin/README.md`](bin/README.md) is the operator index. This
  repo ships the atomic `setup`/`test`/`check`/`python` toolchain interface,
  opt-in `install-hooks` with its `check-hooks-installed` liveness witness;
  universal `kickoff-config`, `kickoff-tree-id`, `check-receipt`,
  `kickoff-evidence`, `execution-telemetry`, `lessons`, and `treatise` managers; the
  `new-name` ledger-slug generator; deterministic dashboard, harness-parity,
  caller-policy, shell-syntax, and catalog (`check-catalogs`) checkers; and
  the starter-only `check-anonymization.sh` leak guard.
- `lib/agentic_starter/` — shared deterministic implementation for exact execution telemetry, evidence schemas, and offline dashboard generation.
- `reports/execution/` — committed, privacy-safe, offline phase reports and aggregate index generated from sanitized telemetry handoffs.
- `tests/` — tests for universal methodology machinery outside the isolated deliverable: gate/hook contracts, orchestration evidence, execution telemetry and reports, candidate identity, and `kickoff-config`. These are carried into derived projects and run in addition to the deliverable's own gates.
- `.githooks/` — tracked optional lifecycle hooks. `bin/install-hooks` opts a checkout in; cloning or stamping never changes Git configuration silently; `bin/check-hooks-installed` is the opt-in-aware liveness witness (a set-but-wrong hooks path fails; an unset one passes as not opted in).
- `plan/` — phased execution plan. Entry point [`plan/INDEX.md`](plan/INDEX.md) (dependency graph, status table, cross-cutting concerns, critical-files map). Each `plan/phase-*.md` holds Goal / Deliverables / Acceptance / brief refs. **When `plan/` and a brief disagree, `plan/` wins.**
- `LOG.md` — append-only activity log. `kickoff` writes START on phase entry and END on phase completion. Do not hand-edit historical entries.
- `user-actions/` — live queue of human-only action items, parallel to `LOG.md`. One file per action (`<slug>.md`, YAML frontmatter); closed actions move to `user-actions-archived/` as an audit trail. Governed by [`policies/user-actions.md`](policies/user-actions.md).
- `lessons/` — ledger of candidate process lessons, parallel to `user-actions/`. One file per lesson (`<slug>.md`, YAML frontmatter, scope-classified); graduated/rejected lessons move to `lessons-archived/` as the audit trail linking rules to the incidents that earned them. Governed by [`policies/lessons.md`](policies/lessons.md).
- `.claude/skills/` — canonical skill source and Claude Code's slash-command surface.
  - `kickoff/SKILL.md` orchestrates one phase end-to-end.
  - `methodology/SKILL.md` exposes the eleven steps as a skill.
  - `learn/SKILL.md` — explores another repo for patterns worth absorbing INTO this one, produces a plan, applies on approval.
  - `teach/SKILL.md` — applies patterns FROM this repo to another repo, produces a plan, applies on approval.
  - `roles/SKILL.md` — edits separate model/effort fields for any canonical role (thin wrapper over `bin/kickoff-config`); governed by [`policies/role-models.md`](policies/role-models.md).
  - `sweep/SKILL.md` — recurring, user-gated maintenance pass over the rule surfaces: stale or contradictory policies, skills past review cadence, brief status transitions, aging ledger candidates, catalog drift. Judgment calls are settled with the user in conversation before the plan is composed. In a template repo it additionally audits the methodology corpus itself.
  - `demo/SKILL.md` — walks the user through an approved demo protocol one visible action at a time, answering questions without advancing.
  - `treatise/SKILL.md` — builds an audience-specific outward explanation from canonical authority, maintains the brief's editorial record, and enforces the publication gate.
  - (Project-specific skills live here too; see Project Context.)
- `.claude/agents/` — canonical role definitions invoked by `kickoff`: `phase-planner.md`, `plan-reviewer.md`, `phase-coder.md`, `code-critic.md`. These are the four roles in the methodology's planner → reviewer → coder → critic loop; do not invoke them by hand for full-phase work unless deliberately bypassing orchestration.
- `.codex/agents/` — Codex CLI mirrors of the four canonical roles (TOML).
- `.agents/skills/` — Codex CLI's native project-skill discovery path ([developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)). Each `<name>` is a **directory** symlink to the canonical `.claude/skills/<name>` directory (Codex doesn't follow file-level symlinks inside a skill dir per [#11314](https://github.com/openai/codex/issues/11314), but does traverse a symlinked skill directory). Template-only skills such as `stamp` are registered here only in repos that are themselves templates; ordinary derived projects omit them so template-bootstrapping commands do not propagate.
- `AGENTS.md` — symlink → `CLAUDE.md`, so Codex/aider read the same source of truth.

The deliverable's directory (whatever the project calls it — `project/` when project-isolation is enabled, or sibling deliverable directories at the repo root when not) is described in Project Context.

## Phase work and the `kickoff` skill

Work proceeds phase by phase under [`plan/`](plan/INDEX.md). `kickoff` orchestrates an initial implementation through plan → plan-review → code → code-review → acceptance (plan review is skipped for phases declaring the `light` review lane — [`policies/review-lanes.md`](policies/review-lanes.md); the initial code critic runs in every lane). First reviews are complete; later rounds use candidate-bound finding ledgers and causal revision packets, widening back to a complete pass when authority, risk, scope, or continuity changes. Iteration uses focused checks. Close runs the complete sequence and `./bin/check all` against the unchanged approved candidate, finalizes evidence and tracked bookkeeping, then runs a second bare `./bin/check all` against the actual handoff tree; no tracked write follows that handoff gate. One shared exact trace covers stage, role, wait, tool, and gate activity, while operator-input parks live in a separate phase ledger and report every interval plus their overlap-safe total. Phase close validates its joins, writes timing metrics into the END block, and generates a privacy-safe offline HTML report. Later test- or user-driven corrections are routed proportionally by risk and size. Canonical role definitions live in `.claude/agents/*.md` (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`); don't invoke them by hand for full-phase work unless deliberately bypassing the orchestration.

### Status markers

Phase statuses live **only** in [`plan/INDEX.md`](plan/INDEX.md)'s phase table:

- ⏳ Not Started
- ⬅️ Next (at most one; required while idle and incomplete)
- 🚧 In Progress
- ✅ Completed

`kickoff` flips `⬅️` → `🚧` on start, `🚧` → `✅` on completion, and advances `⬅️` per the dependency graph at the top of `plan/INDEX.md`.
Every phase row carries exactly one recognized status. Active and complete
projects may have zero `⬅️` rows; more than one is always invalid.

### Reading protocol for phase work

1. Read [`plan/INDEX.md`](plan/INDEX.md) — cross-cutting concerns apply to every phase.
2. Read the parent `plan/phase-N.md` to understand the larger context (if a sub-phase is targeted).
3. Read the target `plan/phase-N.M.md` (or `plan/phase-N.md` when no sub-phase has been split out).
4. Read every brief listed under "Brief refs". Briefs are the source of truth for *what* to build; the phase file specifies *how*.
5. Read every file in the target's frontmatter `depends_on`.
6. As a guard against missing `depends_on`, also read the immediately preceding completed phase (last `✅` row before the target).
7. Do **not** slurp every `phase-*.md`. `depends_on` is the contract for which predecessors actually matter.

### Architectural invariants (load-bearing — do not violate)

These are the universals every project derived from this template inherits. The project may add more invariants of its own; it may not silently drop these.

- **Rules, not memory.** Anything that should bind future sessions — across harnesses (Claude Code, Codex, and others), across operators, across machines — belongs in this repo. Route by kind: a universal rule → `policies/` or `CLAUDE.md`; a scoped project detail → the surface's own instruction file; a per-action workflow → the owning skill; a tunable parameter → the policy that holds its tunables; longitudinal context or a pinned decision → a brief. Agent-side memory is local to one operator, one harness, one machine; it is the wrong place for engine knowledge — if a harness offers to save something to its memory, save it as a repo rule instead. When a learning is real but its surface is unknown — or it has been seen only once, and codifying now would lock in a rule its variations have not tested — file it in `lessons/`: the holding pen between noticing and knowing.
- **Lessons compound.** Every phase close asks what generalizable process lesson was learned and routes the answer — scope-classified `local` or `methodology` — into the `lessons/` ledger; "none" is a permitted, recorded answer, but the question is mandatory. Graduation of a recurring lesson into a durable surface is human-ratified, never agent-applied; the ledger is swept and pruned, not only grown. See [`policies/lessons.md`](policies/lessons.md).
- **Monotonic progress — spiral in, never out.** Hold the authorized objective, scope, and completion criteria fixed unless the user explicitly changes them. Every action must serve that objective by either advancing a completion criterion or reducing uncertainty that directly blocks one; prerequisite work remains in scope only while that causal link is explicit. Record each material tangent once in the appropriate backlog or decision surface, then defer it. Do not investigate, design, implement, or promote it into a new phase or loop without explicit user authorization, and never move the finish line to justify opportunistic improvement. If successive iterations no longer materially shrink the remaining work or blocking uncertainty, stop and escalate.
- **A turn ends by dispatching or by stating a hold — never on a promise.** A session holding authorized, unblocked work does not end a turn describing what it is about to do: it either dispatches the next step or states an explicit hold and why. "Next: Phase N", "opening step 2 now", "I'll pick up the follow-up" are all the same defect — the work then sits idle until something external notices. Corollary on chaining: **a command whose refusal must be read gets its own block.** Never chain a validating command into a compound block that continues past its failure — `a && b`, `a; b`, or a block ending in a backgrounded dispatch. (Donor incidents: a failed close-out validation chained into a persist stamped a permanent false record; an ingest refusal chained behind a backgrounded dispatch was never read, leaving four review passes unmeasured — the incident behind the evidence plane's unmeasured-pass latch. Both rules graduated from a seven-occurrence donor lesson whose thesis is that a rule wired to nothing is a comment.)
- **Route on the authoritative property, not a convenient stand-in.** Before shipping any dispatch, classification, or selection decision, name two things: what the code actually reads, and what actually determines the answer. If they differ, say why the stand-in is safe here — and if you cannot, read the real thing. (Donor worked case, graduated at three same-day occurrences: an extraction backend chose its engine on `path.suffix`, so valid PDFs whose archive members carried no extension were handed to a tool that cannot read PDF input and failed "for" a reason that was never the reason. A convenient property is convenient precisely because it is cheap to read, which is unrelated to whether it is true.)
- **Briefs are the contract.** Every phase points at files under `briefs/`. Phase files specify *how*, not *what*. Fix ambiguous briefs at the source. When `plan/` and a brief disagree, `plan/` wins; when two briefs disagree, fix the briefs.
- **Policies are the law.** Every phase honors every file under `policies/`. A policy violation blocks acceptance.
- **Status lives in one place.** `plan/INDEX.md`'s phase table is the single source of truth for which phase is `⬅️ / 🚧 / ✅`. Per-phase frontmatter never carries `status`.
- **Acceptance is empirical.** Every phase's Acceptance section lists shell commands with verifiable results, named manual checks, or analyzer outputs that pass a quality gate. "The code compiles" is not acceptance.
- **Assurance is candidate-bound.** Review, findings, revision packets, and
  gates name the exact complete working-tree candidate they describe. Run the
  smallest falsifying checks while work converges, then the complete
  phase-prescribed sequence and authoritative full gate once against the
  unchanged approved candidate. See
  [`policies/orchestration-evidence.md`](policies/orchestration-evidence.md).
- **Execution truth is trace-bound.** Stage, role, wait, tool, and gate timing
  comes from one append-only trace joined fail-closed to evidence. Makespan is
  a union of active intervals rather than a sum that double-counts overlap.
  Operator-input parks are a separate phase-level ledger: every interval and
  the union total are reported, same-boot duration is exact, and cross-boot
  calendar duration is visibly non-exact. Every completed phase ends with a
  sanitized, deterministic, offline HTML report. See
  [`policies/execution-telemetry.md`](policies/execution-telemetry.md).
- **Mechanistic vs. intelligence.** Triage every repeatable task. Deterministic, exact, repeatable work is a script under `bin/`; synthesis, judgment, and generative work is an agent. Don't burn a model on what a script does better (cheaper, exact, harness-portable, testable), and don't script what needs judgment. Split mixed tasks at the seam — the agent decides *what*, a deterministic script does the mechanical *how*. See [`policies/mechanistic-vs-intelligence.md`](policies/mechanistic-vs-intelligence.md).
- **Human wall-clock efficiency.** Treat the operator's elapsed wait as a first-class development cost. Stay alert when gates, builds, indexing, generation, migrations, repeated setup, or other operations materially dominate the work and a substantial, low-risk reduction appears available. Prefer conspicuous gains—safe parallel execution of genuinely independent work, one-time invariant setup, focused iteration, or reuse with complete input identity—over heroic micro-optimization. Never trade away correctness, coverage, determinism, review independence, or either close gate, and never expand the active phase merely to chase speed.
- **Repository-owned toolchain contract.** Setup, focused/full testing,
  durable candidate-bound full-gate receipts, runtime selection, metadata,
  locking, behavioral tests, and callers are one atomic bundle. Use
  `./bin/setup`, `./bin/test`, and `./bin/check all`;
  language profiles may add a runtime wrapper such as `./bin/python`. See
  [`policies/build-gates.md`](policies/build-gates.md).
- **Repo-relative paths only** in any file committed to this repo. Bash invocations may use absolute paths.
- **Verification captures go to a scratch path, never a bare filename.** Screenshots, traces, probe output, and other verification artifacts are written to the session scratch directory or an explicitly gitignored path — never a bare filename resolved against the repo root. The load-bearing reason: `bin/kickoff-tree-id` hashes nonignored untracked files, so a stray capture landing in the tree moves the candidate id that the phase's plan, review, and gate evidence are bound to.
- **`plan/` governs the product; methodology changes are operator-routed.** In a derived project, the plan ledger and the `kickoff` lifecycle govern the *deliverable*. Changes to the methodology machinery itself — the skills, canonical agents, orchestration policies, doctrine briefs, parity tooling — are not plan-routed: they run as operator-directed plan-mode → approve → implement cycles recorded by their commits, and are tracked in the plan ledger only as dated notes when they must be remembered. (In this template repo the deliverable *is* the methodology, so its plan legitimately carries methodology work; the rule binds the projects `stamp` derives.)
- **Cross-harness parity.** Skills and agent definitions have one canonical home (`.claude/` / repo-root `CLAUDE.md`) and thin harness-specific pointers (`.codex/`, `.agents/`, `AGENTS.md`). Edit the canonical; `bin/check-harness-parity` rejects missing, copied, or orphaned mirrors.
- **Autonomous delivery, human judgment.** `kickoff` commits and fast-forward-pushes work whose gates are all green; it never advances past an unresolved gate, never claims subjective acceptance, and never performs a destructive git operation. The human's gate is the seam: the END block and the `User Demo:` protocol, where they accept the phase, ask for revisions, or reject it. See [`policies/human-in-the-loop.md`](policies/human-in-the-loop.md).
- **Greenfield until released.** No backward-compatibility shims, legacy aliases, or migration code paths are added unless the policy is explicitly amended. Wrong shapes get replaced directly. See [`policies/greenfield-until-released.md`](policies/greenfield-until-released.md).

### Activity log (`LOG.md`)

`kickoff` appends a START block on `🚧` and an END block on `✅`. Format owned by `kickoff`. Do not hand-edit historical entries. If a phase pauses mid-way, leave it at `🚧` and note the pause reason in an END block.

### User actions (`user-actions/`)

The [`user-actions/`](user-actions/) directory at the repo root is the live queue of action items only the human can perform — deploys, console / dashboard / GUI checks, manual reconciliations, third-party logins, pricing decisions, signups, anything outside an agent's reach. **One file per action**, named `<slug>.md`, with all metadata in YAML frontmatter; closed actions move to `user-actions-archived/`. There is deliberately **no index file** — a central list would be a contention point for concurrent agents, which is the whole reason for going per-file. Every agent must:

1. **Glob `user-actions/*.md` at session start.** Read frontmatter; surface any open action that affects the current task before doing dependent work. If a task depends on an open action, flag and wait — don't proceed silently.
2. **File new actions as they arise.** Any time a session hits a human-only wall, write a new `user-actions/<slug>.md` file before the session ends.
3. **Name each file with a unique two-word slug** — the filename *is* the slug (`warping-butterfly.md`), for stable conversational reference (`close out warping-butterfly`). Recipe: `./bin/new-name` (filler-filtered, collision-checked against all four ledger directories); never reuse a basename.
4. **Express dependencies in frontmatter** (`blocks:`), not in a shared ordering — files are self-contained.
5. **Defer with frontmatter**, not section headings: `status: deferred` plus `needed_at:` (`now` | `"Phase 3"` | an absolute date). Convert relative dates ("Thursday") at write time.
6. **Close by moving to the archive.** Set `status: done | closed | superseded` + a `closed:` date, add a `## Disposition` section when the resolution is non-obvious, and move the file to `user-actions-archived/`. The disposition also answers whether the resolution reveals a recurring learning — if so, file or recur a `lessons/<slug>.md` entry before archiving. Archived files stay on disk as a permanent audit trail.

Checkoff discipline: an agent may close an action only when *it personally* did the underlying action (e.g., ran a smoke script clean, read CloudWatch logs directly). Console / dashboard / GUI / pricing / billing verification is **human-only checkoff**. Full contract: [`policies/user-actions.md`](policies/user-actions.md).

### Lessons (`lessons/`)

[`lessons/`](lessons/) at the repo root is the ledger of candidate **process** lessons — what work in this repo keeps re-teaching us. It is the sibling of `user-actions/` (human-only *work*) and `LOG.md` (phase *history*): this directory holds durable *learnings* that have not yet earned a rule. One Markdown file per lesson, all metadata in YAML frontmatter, a two-word slug for a filename, no index file. Closed lessons move to `lessons-archived/` as the permanent trail linking every rule back to the incidents that earned it.

The mechanics an agent needs:

1. **`kickoff` Step 9c harvests at every phase close.** The sensor feed is each role's Process Observations, the coder's Failure Analysis from any revision round, verdict bodies, wall-clock observations, and `user-actions` dispositions. "No lessons this phase" is a valid recorded answer; omitting the `Lessons:` END-block field is not.
2. **File or recur, never duplicate.** Check both directories first. If an entry already states the lesson, append an occurrence (`{date, ref}`) instead of filing a second file.
3. **Classify the scope.** `local` binds only this project; `methodology` generalizes to the methodology itself and is a standing export upstream.
4. **Filing and recurring are the only writes an agent performs.** Graduation — editing `policies/`, `briefs/`, `CLAUDE.md`, a skill, or an agent definition because of a lesson — is the human's ratified act. Surface it as a DECIDE item and stop.
5. **Validate mechanically**: `./bin/lessons validate` (schema, enums, slug uniqueness) and `./bin/lessons candidates` (graduation-ready: three or more occurrences, still open). Both run inside `./bin/check all`.

Full contract: [`policies/lessons.md`](policies/lessons.md); design rationale: [`briefs/harness-self-improvement.md`](briefs/harness-self-improvement.md). The `sweep` skill (`/sweep` in Claude Code; `$sweep` in Codex) runs the pruning half over policies, briefs, skills, catalogs, and the ledger.

## Universal conventions

- **Repo-relative paths only** in committed files (also load-bearing per the invariants).
- **Harness-specific skill invocation.** In harness-neutral prose, name a skill without a command prefix (for example, "the `kickoff` skill"). When showing an invocation, always give both forms: `/kickoff` for Claude Code and `$kickoff` for Codex. Never present Claude Code's `/name` syntax as universal.
- **One executable command per fenced code block** when a code block is meant to be copy-pasted into a shell, so the user can copy individual commands one at a time without breaking on multi-line clipboards.
- **Toolchain commands belong to the repository.** Use `./bin/setup` for
  provisioning, `./bin/test` for full or focused tests, and `./bin/check` for
  the authoritative suite. The wrappers select the isolated deliverable's
  pinned, locked environment; do not infer a runtime from host `PATH`.

## Glossary

Terms used consistently across briefs, skills, policies, and code. Mismatched usage is a bug — flag or fix.

- **Brief.** A document under `briefs/` describing *what* to build, *why*, and *what was decided*. Briefs inform phases; phases reference briefs.
- **Policy.** A short, prescriptive rule under `policies/` that every phase honors. Policies are the law of the repo.
- **Phase.** One unit of phased work. A phase file (`plan/phase-N.md`) holds Goal, Deliverables, Acceptance, and Brief refs. Status lives in `plan/INDEX.md`.
- **Sub-phase.** A child of a major phase (`plan/phase-N.M.md`), produced by decomposing the parent at the moment the parent becomes the next phase to work.
- **`kickoff`.** The orchestrator skill. Invoke it as `/kickoff` in Claude Code or `$kickoff` in Codex. Runs an initial phase implementation through planner → reviewer → coder → critic, retains candidate-bound evidence across revision rounds, closes through separate implementation-candidate and handoff gates, records exact execution and operator-park timing, generates the end-of-phase HTML report, then routes later corrections in proportion to risk and size. Writes START/END blocks to `LOG.md`; it may write code only for an eligible small, low-risk follow-up fix.
- **`learn`.** Universal cross-repo skill. Invoke it as `/learn` in Claude Code or `$learn` in Codex. Explores a donor repo and proposes which of its patterns to absorb into the current repo. Plan-first; user approves; then applies. The donor stays read-only.
- **`teach`.** Universal cross-repo skill. Invoke it as `/teach` in Claude Code or `$teach` in Codex. Inverse of `learn`. Proposes which of the current repo's patterns to apply to a target repo. Plan-first; user approves; then applies to the target. The current repo stays read-only during teaching.
- **`sweep`.** Universal maintenance skill. Invoke it as `/sweep` in Claude Code or `$sweep` in Codex. Audits the accumulated rule surfaces — policies, briefs, skills, the lessons ledger, catalogs — for staleness, contradiction, and drift, settles every judgment call with the user before composing the plan, and proposes retirements and graduations as one complete plan the user ratifies. The pruning half of the improvement flywheel; governed by `policies/lessons.md` and `briefs/harness-self-improvement.md`.
- **`demo`.** Universal interactive-evaluation skill. Invoke it as `/demo` in Claude Code or `$demo` in Codex. Runs an already approved `User Demo:` protocol one visible action per turn and preserves the resume point without repairing the product mid-demo.
- **`treatise`.** Universal outward-explanation skill. Invoke it as `/treatise` in Claude Code or `$treatise` in Codex. Repairs the canonical brief first, renders for a named audience, and requires explicit authority plus a governing disclosure policy before external publication.
- **Research authority.** The per-role search/retrieval boundary in `policies/research-authority.md` and `kickoff.yaml`: planner/reviewer search and retrieve; coder/critic retrieve approved authorities and same-host structural neighbors; installed resources are allow-by-default but never presumed present.
- **Operator-input park.** A phase-level interval during which progress is waiting on a human decision or action. It is measured outside execution traces, reports every span plus an overlap-safe total, and fails closed while any interval remains open.
- **Lessons ledger.** The `lessons/` + `lessons-archived/` directories: one file per candidate process lesson with scope, provenance, and occurrence history. Validated and tallied by `bin/lessons`; graduation is human-only. Governed by `policies/lessons.md`.
- **Editorial record.** The `treatise:` mapping in a treatise brief's frontmatter. `audience`, `register`, and `coverage` are current state; `directives` is the dated provenance log of the operator's rulings; `renderings` and `external_facts` carry locations and retrieval dates. Its presence marks the brief as a treatise; `bin/treatise` validates its shape. Governed by `policies/treatise.md`.
- **Process observations.** The structured output field each canonical role emits for friction or ambiguity in briefs, policies, plans, or tooling — the raw sensor feed `kickoff`'s lessons harvest distills at phase close. "None" is a valid value.
- **The four canonical agents.** `phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`. Their names are load-bearing — `kickoff` invokes them by name. Their definitions live in `.claude/agents/` (canonical) and `.codex/agents/` (mirror).
- **Repository-owned toolchain contract.** The atomic setup, focused/full test,
  runtime-selection, full-gate, durable receipt, metadata, lockfile, tests, and caller bundle.
  The authoritative full sequence is `./bin/check all`; focused tests use
  `./bin/test`.
- **Full-gate receipt.** The gitignored durable log, terminal run metadata, and
  success record managed by `bin/check-receipt`, bound to one exact candidate
  and environment. The environment fingerprint comes through the
  repository-selected runtime and includes its actual executable and
  base-executable identity; it is not inferred from the receipt helper or a
  version file. The opt-in pre-push hook reuses it only for the clean current
  `HEAD`; every miss or error runs the authoritative full gate.
- **Candidate id.** The SHA-256 identity emitted by `bin/kickoff-tree-id` for
  the complete reviewable working tree: tracked content, deletions, modes,
  symlink targets, and nonignored untracked files. Staging alone does not
  change it.
- **Orchestration evidence.** Run-scoped authority, change, finding, packet,
  and gate records managed by `bin/kickoff-evidence`. These records index
  authoritative sources and bind later review to exact candidates; they do
  not replace the underlying plan, briefs, policies, or repository files.
- **Revision packet.** A deterministic projection for a later review round:
  unresolved stable findings, the causal candidate or plan delta, authority
  drift, risk and test-selection facts, prior gates, and disclosed omissions.
- **Mechanistic vs. intelligence triage.** The decision, made per repeatable task, between a deterministic script (mechanistic — consistency, determinism, repeatability) and an agent (intelligence — synthesis, judgment, generativity). Mechanistic code lives in `bin/`. Governed by `policies/mechanistic-vs-intelligence.md`.
- **`bin/`.** The repo's home for deterministic executables — the mechanistic half of the methodology. Indexed by `bin/README.md`; one concern per script.
- **Role-model pinning / cross-harness invocation.** `kickoff.yaml`'s `role_models` section selects separate model and effort fields per role and orchestrating harness. The model implies its CLI. `roles` is an optional validated editor; direct edits are supported. `bin/kickoff-config` resolves and fail-closed preflights non-native targets. Governed by `policies/role-models.md`.
- **Role execution budget.** `kickoff.yaml`'s `role_timeouts` section defines first-event, idle-progress, and hard deadlines per invocation. `bin/kickoff-config` enforces external calls and writes gitignored telemetry for evidence-based recalibration. Governed by `policies/role-timeouts.md`.
- **Self-resume budget.** `kickoff.yaml`'s `run_budgets.self_resume` key (shipped default 3; `0` pins every park to the human): how many diagnosed, novel-signature self-resumes a phase may take between operator contacts. Any operator relay restores it. Governed by `policies/fail-closed-resume.md`.
- **Review lane.** A phase's declared initial review intensity: `full` (default — all four roles), `light` (mechanical phases only — plan review skipped; the initial code critic still runs, guards the lane, and can escalate back to full), or the invocation-only `one-shot` (coder → critic for well-specified isolated phases; never declarable in frontmatter). Declared as optional `review_lane:` frontmatter in the phase file. Governed by `policies/review-lanes.md`.
- **Evidence lane.** The orthogonal axis to the review lane: `evidence_lane: full` (default — the complete candidate-bound apparatus) or `light` (role registration, span joins, and stage envelopes validated-if-present; the close seal stays mandatory). Fail-closed ineligible over authority surfaces, irreversible or external state, and deploy seams. Governed by `policies/review-lanes.md`.
- **Follow-up route.** The correction path selected after initial code review: `direct fix` for a small low-risk edit, `coder only` for low-risk delegated implementation, or `full cycle` when risk is high or the change is large/cross-cutting. Every route includes empirical validation. Governed by `policies/review-lanes.md`.
- **Acceptance.** The empirical criteria the phase declares for being "done." May include shell-command checks and named manual checks. The human signs off.
- **START / END block.** The two entries `kickoff` appends to `LOG.md` per phase — one when the phase is taken up (`🚧`) and one when it is closed (`✅` or paused).

<!-- METHODOLOGY_CONTRACT_END -->
