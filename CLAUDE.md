# CLAUDE.md

`AGENTS.md` points here. `stamp` rewrites Project Context and copies Methodology Contract except starter-only entries. Hard rules govern both.

## Hard rules — read these before any action


These rules govern every action in this repo. They are placed above both zones so an agent reads them before doing anything irreversible. The full policy text for each is in `policies/`; consult that before bending the rule. Rules 1 and 2 are universal (apply to this template and to every project `stamp` derives from it). Rule 3 is **starter-only** — it does not propagate to derived projects.

1. **Deliver gate-proved work; the user owns judgment and the destructive git surface.** Once a phase closes with every gate green, the orchestrator commits and fast-forward-pushes it — staging only its explicit paths (never `git add -A` or `git add .`, since this checkout may be shared), re-verifying the live tree and staged diff, and checking the resulting commit against the intended file list, with no agent credit and never `--no-verify`. Everything else stays the user's: `git tag`, `git reset --hard`, `git branch -D`, `git rebase`, `git checkout --`, `git clean -fd`, force-pushing, creating or selecting a remote, and any history rewrite. An unexpected path in `git status`, a shared file whose hunks cannot be attributed safely, a hook refusal, a missing or ambiguous upstream, a rejected push, divergence, or residual dirt **parks delivery** — report it and wait; never work around it. **Delivery is not acceptance.** Manual, perceptual, product, and custody criteria — and the phase's `User Demo:` protocol — stay open for the user *after* the work is delivered, and the orchestrator never claims them. What does block a phase from closing at all is an unresolved *gate*: a failed build gate, an unmet executable criterion, an open `DECIDE` ripple. Full policies: [`policies/human-in-the-loop.md`](policies/human-in-the-loop.md) and [`policies/commit-staging.md`](policies/commit-staging.md).

2. **Greenfield until released: no backward-compatibility code.** Do not write legacy aliases, `@deprecated` markers, schema migrations to read older formats, transitional code paths, version-conditional branches, or "compat" shims of any kind. When an earlier shape turns out wrong, replace it directly and update every call site, fixture, test, sample data file, brief, plan, and doc in the same phase. This rule ends only when the project ships a stable external release and explicitly amends the policy. Full policy: [`policies/greenfield-until-released.md`](policies/greenfield-until-released.md).

3. **Anonymize external-repo references in committed files. (Starter-only.)** This repo will be public. Every committed file that documents or references a cross-repo operation — a `LOG.md` entry from `learn` or `teach`, an archived `user-actions-archived/` disposition, a policy example, a brief — must anonymize external project names, commit SHAs, daemon / CLI / MCP-tool names unique to the external repo, internal repo paths beyond what is structurally identical to this template, and proprietary identifiers, *before the file is written*. Use `Donor A` / `Donor B` / … to distinguish multiple donors; use `the donor` / `the target` when there is one and no ambiguity. Do not commit unanonymized content with the intent to fix later — once pushed, the data is leaked even after a later rewrite (SHA still resolves on forks and caches). Run `bin/check-anonymization.sh` before any push; it deterministically catches real paths and commit SHAs across the whole tree. This rule is starter-only because the asymmetry is driven by this repo's publicness, not by any methodology principle; derived projects' files are their own business. Full policy: [`policies/anonymize-log-references.md`](policies/anonymize-log-references.md).

If the user explicitly restricts or waives one of these rules for a named scope ("keep Phase 1.1 local — don't push it"; "keep the v1 reader for one week so I can re-render"), record it verbatim in the phase's END block. Restrictions and waivers are one-shot; the next phase reverts to the default. A restriction narrows delivery only — it never relaxes a gate and never closes a parked criterion.

<!-- PROJECT_CONTEXT_START -->

# Project Context

## This Repo is the Agentic Coding Starter Template

Master template for independently reviewed, evidence-bound development. `kickoff` selects work from `plan/INDEX.md`.

## Project briefs

- [Template thesis and acceptance](briefs/BRIEF.md)
- [Canonical public explanation](briefs/methodology-treatise.md)
- [Patterns and repository evidence](briefs/eacp-pattern-map.md)
- [Approved workflow upgrade](briefs/astra-era-development.md)

## Project surfaces

`project/`: isolated Python example, source, tests, runtime pin, metadata and lockfile; no parent references.

## Project conventions

Python 3.11+; `project/.python-version` pins managed 3.11. `uv`, `project/pyproject.toml` and `project/uv.lock` own tooling/dependencies; `tool.uv.python-preference = "only-managed"`. Type public functions; prefer stdlib.

Use `./bin/setup`, `./bin/test [args...]`, `./bin/check all`, `./bin/python`. Real-dependency probes fail closed. `TOOLCHAIN_PYTHON` is an authoritative absolute-path test override; no PATH inference or fallback.

## Model & review venue

`kickoff.yaml`: model/effort pins, timeouts, research budgets. `roles` edits pins or expands presets. Default: quality/same-harness; cross-vendor review is explicit. Live preflight precedes mutation.

## Project-specific skills

See also [universal skills](#universal-skills).

- [stamp](.claude/skills/stamp/SKILL.md)

<!-- PROJECT_CONTEXT_END -->

<!-- METHODOLOGY_CONTRACT_START -->

# Methodology Contract

## Methodology briefs

- [Eleven steps, doctrine and glossary](briefs/methodology.md)
- [Diagnosis and durable learning](briefs/rule-one-diagnostic-learning.md)
- [Portable bootstrap procedure](briefs/agentic-bootstrap.md)
- [Cross-CLI invocation contracts](briefs/cross-agent-invocation.md)
- [Candidate-bound incremental assurance](briefs/incremental-orchestration.md)
- [Command authority and custody](briefs/deterministic-orchestration-control-plane.md)
- [Draft deterministic workflow design](briefs/deterministic-orchestration.md)
- [Lessons and maintenance flywheel](briefs/harness-self-improvement.md)
- [Dated loading and continuity guidance](briefs/session-context-compaction.md)
- [Proof-estate design](briefs/test-suite-value-governance.md)
- [Minimal methodology scaffold](briefs/mini-method.md)

## Policies catalog

Every applicable policy binds.

- [Policy catalog](policies/README.md)
- [Brief lifecycle](policies/briefs.md)
- [Authority direction](policies/briefs-and-policies.md)
- [Reference pins](policies/docs.md)
- [Mirrors and loading](policies/cross-harness-parity.md)
- [Roles and convergence](policies/four-canonical-agents.md)
- [Role routing](policies/role-models.md)
- [Role deadlines](policies/role-timeouts.md)
- [Research authority](policies/research-authority.md)
- [Evidence and close](policies/orchestration-evidence.md)
- [Command custody](policies/orchestration-control-plane.md)
- [Timing and reports](policies/execution-telemetry.md)
- [Scripts versus judgment](policies/mechanistic-vs-intelligence.md)
- [Staging](policies/commit-staging.md)
- [Build gates](policies/build-gates.md)
- [Test governance](policies/test-suite-governance.md)
- [Park/resume](policies/fail-closed-resume.md)
- [Review lanes](policies/review-lanes.md)
- [Phase state](policies/phase-status.md)
- [Ripple](policies/phase-ripple.md)
- [Acceptance](policies/acceptance-empirical.md)
- [User demos](policies/user-demo-protocols.md)
- [Treatise](policies/treatise.md)
- [Verification](policies/verification-discipline.md)
- [Log](policies/log-discipline.md)
- [User actions](policies/user-actions.md)
- [Lessons](policies/lessons.md)
- [Human judgment](policies/human-in-the-loop.md)
- [Paths](policies/repo-relative-paths.md)
- [Isolation](policies/project-isolation.md)
- [Simplicity](policies/simplicity-and-consolidation.md)
- [Greenfield](policies/greenfield-until-released.md)
- [Anonymization](policies/anonymize-log-references.md)

## Universal repo layout

[docs catalog](docs/README.md): third-party pins; [bin catalog](bin/README.md): executables. `lib/agentic_starter/`: shared machinery; `tests/`: independent proofs. `.githooks/`: opt-in via `bin/install-hooks`, witnessed by `bin/check-hooks-installed`. `reports/execution/`: sanitized reports; `reports/test-governance/`: recipient-local proofs. `LOG.md`: history; `user-actions/` and `lessons/`: per-file queues with archive directories.

### Universal skills

- [kickoff](.claude/skills/kickoff/SKILL.md)
- [methodology](.claude/skills/methodology/SKILL.md)
- [rule-one](.claude/skills/rule-one/SKILL.md)
- [learn](.claude/skills/learn/SKILL.md)
- [teach](.claude/skills/teach/SKILL.md)
- [roles](.claude/skills/roles/SKILL.md)
- [sweep](.claude/skills/sweep/SKILL.md)
- [sweep-planning](.claude/skills/sweep-planning/SKILL.md)
- [sweep-coding](.claude/skills/sweep-coding/SKILL.md)
- [demo](.claude/skills/demo/SKILL.md)
- [treatise](.claude/skills/treatise/SKILL.md)
- [plain](.claude/skills/plain/SKILL.md)
- [ask](.claude/skills/ask/SKILL.md)

### Canonical roles and mirrors

- [phase-planner](.claude/agents/phase-planner.md)
- [plan-reviewer](.claude/agents/plan-reviewer.md)
- [phase-coder](.claude/agents/phase-coder.md)
- [code-critic](.claude/agents/code-critic.md)

`.claude/` is canonical. `.agents/skills/<name>` → `../../.claude/skills/<name>` exposes all resources. `.codex/agents/<role>.toml` is a thin canonical pointer with matching description. Edit canonical sources. Product phases use `kickoff`; methodology follows the routing rule below.

## Phase work and the `kickoff` skill

Invoke `/kickoff` (Claude Code) or `$kickoff` (Codex). Read the [kickoff](.claude/skills/kickoff/SKILL.md) and each linked resource before its branch, including follow-ups/recovery; links do not prove reads. Limits: root 16384 UTF-8 bytes; entry 8192. Preserve obligations and catalogs; move explanation to its owner.

### Status markers

Only [plan/INDEX.md](plan/INDEX.md) holds status: ⏳ not started, ⬅️ next, 🚧 in progress, ✅ completed. One marker per row; idle incomplete work has one arrow, active/complete work may have none; never multiple arrows. Explicitly select active work to resume. `kickoff` owns transitions; no per-phase `status`.

### Reading protocol for phase work

1. Read `plan/INDEX.md` for dependencies and cross-cutting concerns.
2. Read the parent phase if targeting a child, then the target phase.
3. Read every Brief ref and every pinned document on which it depends.
4. Read every `depends_on` file and the immediately preceding completed phase.
5. Read applicable policies, root invariants and the stage resource. Read only required phase files.

### Architectural invariants (load-bearing — do not violate)

Rationale: [methodology](briefs/methodology.md#operating-invariants-and-vocabulary).

- **Rules, not memory; Rule One.** Keep durable cross-harness knowledge in its owning repo authority. Diagnose failures, corrections, surprises and discarded work; separate containment, correction and prevention. File unsettled learning in `lessons/` and harvest every END/PARK, including `none`; only the human graduates rules.
- **Monotonic progress.** Hold authorized scope fixed; defer tangents once. Stop unsupported expansion. Dispatch authorized unblocked work or state the hold; inspect any command refusal before continuing.
- **Evidence over proxies.** Name the authoritative property, proxy, innocent triggers and sign-inversion risk. Read cited identifiers at their definitions; grep is a lead. Recheck affected callers, fixtures, tests and independent inventories.
- **Concrete uses; one home.** No speculative abstraction without a second present use. Consolidate at three copies; prefer fewer concepts. Use scripts for deterministic work and intelligence for contextual judgment.
- **Authority direction.** Policies prevail; plans refine and outrank briefs. Fix ambiguity at its owner; briefs never cite policies or plans.
- **Coherent outcomes.** Multiple surfaces and absent children do not require splitting. Split only at consequential decisions, independently accepted prerequisites, deployment/migration/human seams or demonstrated coherence limits. Ordinary internals belong to the coder; consequential scope stays approved. Never merge completed phases.
- **Empirical acceptance and independent review.** Name falsifying checks and manual criteria. Discover broadly, batch evidenced blockers, separate optional advice, preserve stable findings; rebase on changed authority, scope, risk or lost continuity. Preserve the role policy’s 600-line/growth/stall/ten-cycle limits.
- **Candidate-bound assurance.** Product identity binds review; full-tree identity binds gate non-mutation and delivery. Declared-authority and reviewed-bookkeeping checks remain independent. Unknown tracked classifications refuse; unknown nonignored untracked paths and `candidate-partition.yaml` itself stay active.
- **Two full gates.** Focused iteration precedes critique. The orchestrator runs the full implementation-candidate sequence ending in `./bin/check all`; accepted major close precedes captured status mutation. After all bookkeeping, run the second bare full handoff gate; no tracked write follows success. Preserve the separate child-close refusal; waive no guard.
- **Execution truth.** One append-only trace, exact joins and overlap-safe unions; separately report operator-input parks. Missing measurement is unknown, never zero. Finalize evidence before sanitized offline reports.
- **Safe acceleration.** Use substantial, obvious low-risk time savings within scope, preserving correctness, coverage, determinism, independent review and both gates. No optimization tangents.
- **Atomic toolchain.** Runtime, metadata, lockfile, setup, focused/full tests, receipts, proofs and callers move together. Use repository wrappers; bad overrides and failed probes never fall back. Keep scratch captures outside the reviewable tree or explicitly ignored.
- **Methodology routing.** Approved improvements, including here: implement directly, independently review, run required checks. Full phase roles require operator direction. Read [review lanes](policies/review-lanes.md).
- **Portable parity.** Canonical sources and thin mirrors; repo-relative committed paths; isolated deliverable. Greenfield replacement and delivery/human-judgment boundaries follow the hard rules.

### Activity log (`LOG.md`)

Owning skills append via the deterministic writer at true EOF; preserve bytes and chronology. Parks stay `🚧`; terminal records carry Lessons, evidence, remaining work and truthful outcomes.

### User actions (`user-actions/`)

Glob `user-actions/*.md` at session start; read frontmatter and surface dependencies before work. File human-only actions before ending; use `bin/new-name`, record dependencies/deferral and archive closed entries. Agents close only personally completed actions; GUI, console, pricing and billing checkoff stays human-only.

### Lessons (`lessons/`)

Read both lesson directories before filing/recurring; one row per observation. Run `./bin/lessons validate` and `./bin/lessons candidates`. Human ratification owns graduation/rejection. Harvest process observations and failure analysis at each close/park.

## Universal conventions

Never hard-wrap Markdown prose: one physical line per paragraph, including list-item prose. Preserve syntax-required breaks. Give one executable command per copyable shell fence. Use bare skill names in neutral prose and both harness invocation forms when showing commands. Follow `plain` for operator messages; peers retain full technical fidelity. Use User/operator/owner and they/them in durable role language; authorship credit is separate.

Agent decisions use kickoff’s input-park/`blocked-owner` route; unattended decisions park in artifacts. Only the operator invokes `ask`. Record rulings at their authority and human work in `user-actions/`.

## Glossary

Use the canonical [glossary](briefs/methodology.md#glossary); flag terminology mismatches.

<!-- METHODOLOGY_CONTRACT_END -->
