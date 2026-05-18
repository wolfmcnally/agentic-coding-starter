# CLAUDE.md

This file provides guidance to coding agents (Claude Code, Codex CLI, and others that read top-level instruction files) when working in this repository.

This file has two zones. **Project Context** is everything specific to *this* repo — the project's thesis, the deliverable's surface, the language conventions, the project-specific briefs and skills. `/starter` rewrites this zone when stamping out a new project. **Methodology Contract** is everything universal to the agentic methodology — methodology briefs, every policy, the phase-work protocol, universal conventions, the glossary. `/starter` copies this zone verbatim. The two zones are demarcated by HTML comment markers; both humans and `/starter` use the markers to find the boundary. Above both zones is a small **Hard rules** section that governs every action regardless of zone — these are too consequential to risk an agent missing them by reading top-down and stopping early.

## Hard rules — read these before any action

These rules govern every action in this repo. They are placed above both zones so an agent reads them before doing anything irreversible. The full policy text for each is in `policies/`; consult that before bending the rule. Rules 1 and 2 are universal (apply to this template and to every project `/starter` derives from it). Rule 3 is **starter-only** — it does not propagate to derived projects.

1. **The user initiates all commits and other destructive git operations.** Do not run `git commit`, `git push`, `git tag`, `git reset --hard`, `git branch -D`, `git rebase`, `git checkout --`, `git clean -fd`, or anything that rewrites history or affects shared state — unless the user *explicitly* asks in the current session. Approval from a prior session does not carry forward. When phase work is ready, report it (file list, build-gate status, manual checks) and wait. Full policy: [`policies/human-in-the-loop.md`](policies/human-in-the-loop.md).

2. **Greenfield until released: no backward-compatibility code.** Do not write legacy aliases, `@deprecated` markers, schema migrations to read older formats, transitional code paths, version-conditional branches, or "compat" shims of any kind. When an earlier shape turns out wrong, replace it directly and update every call site, fixture, test, sample data file, brief, plan, and doc in the same phase. This rule ends only when the project ships a stable external release and explicitly amends the policy. Full policy: [`policies/greenfield-until-released.md`](policies/greenfield-until-released.md).

3. **Anonymize external-repo references in `LOG.md`. (Starter-only.)** This repo will be public. Every `LOG.md` entry that documents a cross-repo operation — `/learn` from a donor, `/teach` to a target, or any other skill that brings external-repo context into the log — must anonymize external project names, commit SHAs, daemon / CLI / MCP-tool names unique to the external repo, internal repo paths beyond what is structurally identical to this template, and proprietary identifiers, *before the entry is written*. Use `Donor A` / `Donor B` / … to distinguish multiple donors; use `the donor` / `the target` when there is one and no ambiguity. Do not commit unanonymized entries with the intent to fix later — once pushed, the data is leaked even after a later rewrite (SHA still resolves on forks and caches). This rule is starter-only because the asymmetry is driven by this repo's publicness, not by any methodology principle; derived projects' `LOG.md` files are their own business. Full policy: [`policies/anonymize-log-references.md`](policies/anonymize-log-references.md).

If the user explicitly waives one of these rules for a named scope ("go ahead and commit Phase 1.1 since it's just scaffolding"; "keep the v1 reader for one week so I can re-render"), record the waiver verbatim in the phase's END block. Waivers are one-shot; the next phase reverts to the default.

<!-- PROJECT_CONTEXT_START -->

# Project Context

## This Repo is the Agentic Coding Starter Template

A *master template* for projects built with AI coding agents under a structured planner → reviewer → coder → critic methodology. The entry-point brief is [`briefs/BRIEF.md`](briefs/BRIEF.md).

This repo is also a working project in its own right. Open it in any agent host and `/kickoff` will pick up Phase 1 from `plan/INDEX.md`.

## Project briefs

In addition to the universal methodology briefs (see Methodology Contract below):

- [`BRIEF.md`](briefs/BRIEF.md) — entry-point brief for *this* repo: thesis, what the template provides, when to use it, the two operating modes (template-stamp vs. self-build), and acceptance criteria.

## Project surfaces

- `project/` — the deliverable: package metadata, source, tests, lockfile. Self-contained per [`policies/project-isolation.md`](policies/project-isolation.md) — nothing inside `project/` references anything above it. Currently holds a minimal Python example (`project/example/`, `project/tests/`, `project/pyproject.toml`) so the build gates have a real target from the first session.

## Project conventions

- **Python 3.11+** for the example package and any Python the template ships. Type hints on all new public functions; idiomatic stdlib where the difference is small.
- **`uv` with `pyproject.toml`** is the recommended Python package manager. The example project's gates assume `uv run ...`.
- **Build gates run from inside `project/`** as `cd project && uv run <cmd>`. (See universal conventions for the rationale.)
- **`project/pyproject.toml` is the single source of truth** for Python tooling configuration (ruff, pytest, mypy if used) in this repo.

## Project-specific skills

In addition to the universal `/kickoff`, `/methodology`, `/learn`, and `/teach` skills (carried into every derived project):

- **`/starter`** — starter-template-only bootstrapping skill. Stamps out a new project from this repo. Not carried into derived projects. Source: `.claude/skills/starter/SKILL.md`; Codex wrapper: `.codex/prompts/starter.md`.

<!-- PROJECT_CONTEXT_END -->

<!-- METHODOLOGY_CONTRACT_START -->

# Methodology Contract

## Methodology briefs

- [`methodology.md`](briefs/methodology.md) — the eleven-step pipeline: vague ideas → insights → brief → architecture → policies → phased plan → sub-phase decomposition → orchestrator-driven execution → acceptance → log → human evaluation → stay agile.
- [`agentic-bootstrap.md`](briefs/agentic-bootstrap.md) — procedure for standing up a new project from this template: anatomy of the structure, what to transfer verbatim vs. rewrite vs. discard, step-by-step procedure, sanity-check protocol.

## Policies catalog

Every file under `policies/`, indexed so agents see the catalog without an extra Read. A policy is a non-negotiable rule every phase honors.

- [`README.md`](policies/README.md) — what `policies/` is and how it differs from `briefs/`.
- [`briefs-and-policies.md`](policies/briefs-and-policies.md) — the contract: briefs describe, policies prescribe, plan sequences.
- [`cross-harness-parity.md`](policies/cross-harness-parity.md) — keep Claude Code, Codex CLI, and any other supported harness in lockstep; canonical files vs. mirrors; onboarding a new harness.
- [`four-canonical-agents.md`](policies/four-canonical-agents.md) — the four roles `/kickoff` invokes by name; their tool stances; their verdict headers.
- [`phase-status.md`](policies/phase-status.md) — status markers live only in `plan/INDEX.md`; no `status:` field in per-phase frontmatter; `/kickoff` owns transitions.
- [`phase-ripple.md`](policies/phase-ripple.md) — at phase close, pinned decisions from the closing phase propagate into downstream drafted phase files. AUTO ripples (mechanical) land in the same session; DECIDE ripples (judgment) surface as named follow-ups in the END block.
- [`acceptance-empirical.md`](policies/acceptance-empirical.md) — every phase's Acceptance section lists verifiable shell commands or named manual checks. "It compiles" is not acceptance.
- [`user-demo-protocols.md`](policies/user-demo-protocols.md) — when a phase touches a user-facing surface, Acceptance carries an interactive try-it-yourself protocol (entry point, suggested inputs, what to look for, variations). When there's nothing meaningful to demo, declare `User Demo: N/A` with a one-line reason instead. Silence is blocking; contrived demos are blocking.
- [`log-discipline.md`](policies/log-discipline.md) — `LOG.md` is append-only and owned by `/kickoff`. Never hand-edit historical entries.
- [`user-blockers.md`](policies/user-blockers.md) — `user-blockers.md` at the repo root is the live queue of human-only action items; stable two-word slug per item; closure in place. Read at session start; surface relevant items before doing dependent work.
- [`human-in-the-loop.md`](policies/human-in-the-loop.md) — the human decides when work is done. The orchestrator never auto-commits, never advances past unresolved gates, never claims subjective acceptance the human owes.
- [`repo-relative-paths.md`](policies/repo-relative-paths.md) — no absolute `/Users/...` paths in committed files. Bash commands may use absolute paths.
- [`project-isolation.md`](policies/project-isolation.md) — when the repo has one primary deliverable, isolate it under `project/`; nothing in there references anything above it. Makes the deliverable submodule-ready.
- [`greenfield-until-released.md`](policies/greenfield-until-released.md) — a project is greenfield by default until first stable release. No backward-compatibility shims, legacy aliases, schema migrations, or transitional code paths. Replace old shapes directly.
- [`anonymize-log-references.md`](policies/anonymize-log-references.md) — **starter-only** (not inherited by derived projects). Every `LOG.md` entry that documents a cross-repo operation must anonymize external project names, commit SHAs, and proprietary identifiers, because this repo will be public.

## Universal repo layout

- `briefs/` — durable design library. See "Methodology briefs" above for the universal briefs, and "Project briefs" in Project Context for this repo's specifics.
- `policies/` — non-negotiable rules. Full catalog above.
- `plan/` — phased execution plan. Entry point [`plan/INDEX.md`](plan/INDEX.md) (dependency graph, status table, cross-cutting concerns, critical-files map). Each `plan/phase-*.md` holds Goal / Deliverables / Acceptance / brief refs. **When `plan/` and a brief disagree, `plan/` wins.**
- `LOG.md` — append-only activity log. `/kickoff` writes START on phase entry and END on phase completion. Do not hand-edit historical entries.
- `user-blockers.md` — live queue of human-only action items, parallel to `LOG.md`. Mutable by design; closed items stay strikethrough'd in place as an audit trail. Governed by [`policies/user-blockers.md`](policies/user-blockers.md).
- `.claude/skills/` — slash-command surface for Claude Code.
  - `kickoff/SKILL.md` orchestrates one phase end-to-end.
  - `methodology/SKILL.md` exposes the eleven steps as a slash command.
  - `learn/SKILL.md` — explores another repo for patterns worth absorbing INTO this one, produces a plan, applies on approval.
  - `teach/SKILL.md` — applies patterns FROM this repo to another repo, produces a plan, applies on approval.
  - (Project-specific skills live here too; see Project Context.)
- `.claude/agents/` — canonical role definitions invoked by `/kickoff`: `phase-planner.md`, `plan-reviewer.md`, `phase-coder.md`, `code-critic.md`. These are the four roles in the methodology's planner → reviewer → coder → critic loop; do not invoke them by hand for full-phase work unless deliberately bypassing orchestration.
- `.codex/agents/` — Codex CLI mirrors of the four canonical roles (TOML).
- `.codex/prompts/` — Codex slash-command entry points for the universal skills (and any project-specific skills the project chooses to expose). Each entry is a symlink to the canonical `.claude/skills/<name>/SKILL.md`.
- `.agents/skills/` — Codex CLI's native project-skill discovery path ([developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)). Each `<name>` is a **directory** symlink to the canonical `.claude/skills/<name>` directory (Codex doesn't follow file-level symlinks inside a skill dir per [#11314](https://github.com/openai/codex/issues/11314), but does traverse a symlinked skill directory). The starter-only `/starter` skill is intentionally excluded so it does not propagate to derived projects.
- `AGENTS.md` — symlink → `CLAUDE.md`, so Codex/aider read the same source of truth.

The deliverable's directory (whatever the project calls it — `project/` when project-isolation is enabled, or sibling deliverable directories at the repo root when not) is described in Project Context.

## Phase work and the `kickoff` skill

Work proceeds phase by phase under [`plan/`](plan/INDEX.md). `/kickoff` orchestrates one phase per session through plan → plan-review → code → code-review → build. Canonical role definitions live in `.claude/agents/*.md` (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`); don't invoke them by hand for full-phase work unless deliberately bypassing the orchestration.

### Status markers

Phase statuses live **only** in [`plan/INDEX.md`](plan/INDEX.md)'s phase table:

- ⏳ Not Started
- ⬅️ Next (only one at a time)
- 🚧 In Progress
- ✅ Completed

`/kickoff` flips `⬅️` → `🚧` on start, `🚧` → `✅` on completion, and advances `⬅️` per the dependency graph at the top of `plan/INDEX.md`.

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

- **Rules, not memory.** Anything that should bind future sessions — across harnesses (Claude Code, Codex, and others), across operators, across machines — belongs in this repo: in `CLAUDE.md`, in `briefs/`, in `policies/`, or in a `.claude/skills/<name>/SKILL.md`. Agent-side memory is local to one operator, one harness, one machine; it is the wrong place for engine knowledge. If a learning surfaces in a session, capture it in the repo, not in memory.
- **Briefs are the contract.** Every phase points at files under `briefs/`. Phase files specify *how*, not *what*. Fix ambiguous briefs at the source. When `plan/` and a brief disagree, `plan/` wins.
- **Policies are the law.** Every phase honors every file under `policies/`. A policy violation blocks acceptance.
- **Status lives in one place.** `plan/INDEX.md`'s phase table is the single source of truth for which phase is `⬅️ / 🚧 / ✅`. Per-phase frontmatter never carries `status`.
- **Acceptance is empirical.** Every phase's Acceptance section lists shell commands with verifiable results, named manual checks, or analyzer outputs that pass a quality gate. "The code compiles" is not acceptance.
- **Repo-relative paths only** in any file committed to this repo. Bash invocations may use absolute paths.
- **Cross-harness parity.** Skills and agent definitions have one canonical home (`.claude/` / repo-root `CLAUDE.md`) and harness-specific mirrors (`.codex/`, `.agents/`, `AGENTS.md`). Edit the canonical; refresh the mirror in the same commit.
- **Human decides done.** `/kickoff` never auto-commits. The human reviews each phase's END block and either accepts the work, asks for revisions, or commits.
- **Greenfield until released.** No backward-compatibility shims, legacy aliases, or migration code paths are added unless the policy is explicitly amended. Wrong shapes get replaced directly. See [`policies/greenfield-until-released.md`](policies/greenfield-until-released.md).

### Activity log (`LOG.md`)

`/kickoff` appends a START block on `🚧` and an END block on `✅`. Format owned by `/kickoff`. Do not hand-edit historical entries. If a phase pauses mid-way, leave it at `🚧` and note the pause reason in an END block.

### User blockers (`user-blockers.md`)

[`user-blockers.md`](user-blockers.md) at the repo root is the live queue of action items only the human can perform — deploys, console / dashboard / GUI checks, manual reconciliations, third-party logins, pricing decisions, signups, anything outside an agent's reach. Every agent must:

1. **Read `user-blockers.md` at session start.** Surface any pending item that affects the current task before doing dependent work. If a task depends on an unchecked blocker, flag and wait — don't proceed silently.
2. **File new items as they arise.** Any time a session hits a human-only wall, write a new entry before the session ends.
3. **Tag every new item with a unique two-word slug** for stable conversational reference (`close out warping-butterfly`). Recipe: `uv run --with coolname python -c "from coolname import generate_slug; print(generate_slug(2))"`. Grep live + closed sets to confirm uniqueness; never reuse.
4. **Sort by dependency within each section.** Unblockers above unblocked.
5. **Date-defer items that can't run yet** under a `## YYYY-MM-DD` heading. Always absolute dates; convert relative ("Thursday") at write time.
6. **Close in place.** Strikethrough the title and append `✅ DONE` / `✅ CLOSED` / `✅ SUPERSEDED`, plus a `**Disposition:**` line when the resolution is non-obvious. Closed items stay in the file as a permanent audit trail.

Checkoff discipline: an agent may check a box only when *it personally* did the underlying action (e.g., ran a smoke script clean, read CloudWatch logs directly). Console / dashboard / GUI / pricing / billing verification is **human-only checkoff**. Full contract: [`policies/user-blockers.md`](policies/user-blockers.md).

## Universal conventions

- **Repo-relative paths only** in committed files (also load-bearing per the invariants).
- **One executable command per fenced code block** when a code block is meant to be copy-pasted into a shell, so the user can copy individual commands one at a time without breaking on multi-line clipboards.
- **Build gates use the `cd <deliverable> && <command>` shape** when project-isolation is enabled. Uniform across language ecosystems — uv, npm, cargo, go all work the same way. Specific commands per language live in Project Context.

## Glossary

Terms used consistently across briefs, skills, policies, and code. Mismatched usage is a bug — flag or fix.

- **Brief.** A document under `briefs/` describing *what* to build, *why*, and *what was decided*. Briefs inform phases; phases reference briefs.
- **Policy.** A short, prescriptive rule under `policies/` that every phase honors. Policies are the law of the repo.
- **Phase.** One unit of phased work. A phase file (`plan/phase-N.md`) holds Goal, Deliverables, Acceptance, and Brief refs. Status lives in `plan/INDEX.md`.
- **Sub-phase.** A child of a major phase (`plan/phase-N.M.md`), produced by decomposing the parent at the moment the parent becomes the next phase to work.
- **`/kickoff`.** The orchestrator skill. Runs one phase end-to-end through planner → reviewer → coder → critic. Writes START/END to `LOG.md`. Does not write code itself.
- **`/learn`.** Universal cross-repo skill. Explores a donor repo and proposes which of its patterns to absorb into the current repo. Plan-first; user approves; then applies. The donor stays read-only.
- **`/teach`.** Universal cross-repo skill. Inverse of `/learn`. Proposes which of the current repo's patterns to apply to a target repo. Plan-first; user approves; then applies to the target. The current repo stays read-only during teaching.
- **The four canonical agents.** `phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`. Their names are load-bearing — `/kickoff` invokes them by name. Their definitions live in `.claude/agents/` (canonical) and `.codex/agents/` (mirror).
- **Build gate.** A shell command (or sequence) the orchestrator runs after the coder finishes, to confirm the code still builds, lints, types, and tests clean.
- **Acceptance.** The empirical criteria the phase declares for being "done." May include shell-command checks and named manual checks. The human signs off.
- **START / END block.** The two entries `/kickoff` appends to `LOG.md` per phase — one when the phase is taken up (`🚧`) and one when it is closed (`✅` or paused).

<!-- METHODOLOGY_CONTRACT_END -->
