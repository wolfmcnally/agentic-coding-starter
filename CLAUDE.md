# CLAUDE.md

This file provides guidance to coding agents (Claude Code, Codex CLI, and others that read top-level instruction files) when working in this repository.

## This Repo is the Agentic Coding Starter Template

A *master template* for projects built with AI coding agents under a structured planner → reviewer → coder → critic methodology. The entry-point brief is [`briefs/BRIEF.md`](briefs/BRIEF.md); the methodology itself is [`briefs/methodology.md`](briefs/methodology.md); the bootstrap procedure is [`briefs/agentic-bootstrap.md`](briefs/agentic-bootstrap.md).

This repo is also a working project in its own right. Open it in any agent host and `/kickoff` will pick up Phase 1 from `plan/INDEX.md`.

## Briefs catalog

Every file under `briefs/`, indexed so agents see the catalog without an extra Read.

- [`BRIEF.md`](briefs/BRIEF.md) — entry-point brief for *this* repo: thesis, what the template provides, when to use it, the two operating modes (template-stamp vs. self-build), and acceptance criteria.
- [`methodology.md`](briefs/methodology.md) — the eleven-step pipeline: vague ideas → insights → brief → architecture → policies → phased plan → sub-phase decomposition → orchestrator-driven execution → acceptance → log → human evaluation → stay agile.
- [`agentic-bootstrap.md`](briefs/agentic-bootstrap.md) — procedure for standing up a new project from this template: anatomy of the structure, what to transfer verbatim vs. rewrite vs. discard, step-by-step procedure, sanity-check protocol.

## Policies catalog

Every file under `policies/`, indexed so agents see the catalog without an extra Read. A policy is a non-negotiable rule every phase honors.

- [`README.md`](policies/README.md) — what `policies/` is and how it differs from `briefs/`.
- [`briefs-and-policies.md`](policies/briefs-and-policies.md) — the contract: briefs describe, policies prescribe, plan sequences.
- [`cross-harness-parity.md`](policies/cross-harness-parity.md) — keep Claude Code, Codex CLI, and any other supported harness in lockstep; canonical files vs. mirrors; onboarding a new harness.
- [`four-canonical-agents.md`](policies/four-canonical-agents.md) — the four roles `/kickoff` invokes by name; their tool stances; their verdict headers.
- [`phase-status.md`](policies/phase-status.md) — status markers live only in `plan/INDEX.md`; no `status:` field in per-phase frontmatter; `/kickoff` owns transitions.
- [`acceptance-empirical.md`](policies/acceptance-empirical.md) — every phase's Acceptance section lists verifiable shell commands or named manual checks. "It compiles" is not acceptance.
- [`log-discipline.md`](policies/log-discipline.md) — `LOG.md` is append-only and owned by `/kickoff`. Never hand-edit historical entries.
- [`human-in-the-loop.md`](policies/human-in-the-loop.md) — the human decides when work is done. The orchestrator never auto-commits, never advances past unresolved gates, never claims subjective acceptance the human owes.
- [`repo-relative-paths.md`](policies/repo-relative-paths.md) — no absolute `/Users/...` paths in committed files. Bash commands may use absolute paths.
- [`project-isolation.md`](policies/project-isolation.md) — when the repo has one primary deliverable, isolate it under `project/`; nothing in there references anything above it. Makes the deliverable submodule-ready.

## Repo layout

- `briefs/` — durable design library. Entry point [`briefs/BRIEF.md`](briefs/BRIEF.md); full catalog above.
- `policies/` — non-negotiable rules. Full catalog above.
- `plan/` — phased execution plan. Entry point [`plan/INDEX.md`](plan/INDEX.md) (dependency graph, status table, cross-cutting concerns, critical-files map). Each `plan/phase-*.md` holds Goal / Deliverables / Acceptance / brief refs. **When `plan/` and a brief disagree, `plan/` wins.**
- `LOG.md` — append-only activity log. `/kickoff` writes START on phase entry and END on phase completion. Do not hand-edit historical entries.
- `project/` — the deliverable: package metadata, source, tests, lockfile. Self-contained per [`policies/project-isolation.md`](policies/project-isolation.md) — nothing inside `project/` references anything above it. Currently holds a minimal Python example (`project/example/`, `project/tests/`, `project/pyproject.toml`) so the build gates have a real target from the first session. Build gates run as `cd project && uv run ...` from the repo root.
- `.claude/skills/` — slash-command surface for Claude Code.
  - `kickoff/SKILL.md` orchestrates one phase end-to-end.
  - `methodology/SKILL.md` exposes the eleven steps as a slash command.
  - `learn/SKILL.md` — explores another repo for patterns worth absorbing INTO this one, produces a plan, applies on approval. Universal — `/starter` carries it into every derived project.
  - `teach/SKILL.md` — applies patterns FROM this repo to another repo, produces a plan, applies on approval. Universal — `/starter` carries it into every derived project.
  - `starter/SKILL.md` — starter-only meta-skill. Stamps out a new project from this template. Not carried into derived projects.
- `.claude/agents/` — canonical role definitions invoked by `/kickoff`: `phase-planner.md`, `plan-reviewer.md`, `phase-coder.md`, `code-critic.md`. These are the four roles in the methodology's planner → reviewer → coder → critic loop; do not invoke them by hand for full-phase work unless deliberately bypassing orchestration.
- `.codex/agents/` — Codex CLI mirrors of the four canonical roles (TOML).
- `.codex/prompts/` — Codex slash-command entry points for `/kickoff` and `/starter`.
- `AGENTS.md` — symlink → `CLAUDE.md`, so Codex/aider read the same source of truth.

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

- **Briefs are the contract.** Every phase points at files under `briefs/`. Phase files specify *how*, not *what*. Fix ambiguous briefs at the source. When `plan/` and a brief disagree, `plan/` wins.
- **Policies are the law.** Every phase honors every file under `policies/`. A policy violation blocks acceptance.
- **Status lives in one place.** `plan/INDEX.md`'s phase table is the single source of truth for which phase is `⬅️ / 🚧 / ✅`. Per-phase frontmatter never carries `status`.
- **Acceptance is empirical.** Every phase's Acceptance section lists shell commands with verifiable results, named manual checks, or analyzer outputs that pass a quality gate. "The code compiles" is not acceptance.
- **Repo-relative paths only** in any file committed to this repo. Bash invocations may use absolute paths.
- **Cross-harness parity.** Skills and agent definitions have one canonical home (`.claude/` / repo-root `CLAUDE.md`) and harness-specific mirrors (`.codex/`, `AGENTS.md`). Edit the canonical; refresh the mirror in the same commit.
- **Human decides done.** `/kickoff` never auto-commits. The human reviews each phase's END block and either accepts the work, asks for revisions, or commits.

### Activity log (`LOG.md`)

`/kickoff` appends a START block on `🚧` and an END block on `✅`. Format owned by `/kickoff`. Do not hand-edit historical entries. If a phase pauses mid-way, leave it at `🚧` and note the pause reason in an END block.

## Conventions

- **Python 3.11+** for the example package and any Python the template ships. Type hints on all new public functions; idiomatic stdlib where the difference is small.
- **`uv` with `pyproject.toml`** is the recommended Python package manager. The example project's gates assume `uv run ...`. Projects derived from this template may switch.
- **Build gates run from inside `project/`.** Per [`policies/project-isolation.md`](policies/project-isolation.md), invoke as `cd project && uv run <cmd>` from the repo root. This shape is uniform across language ecosystems.
- **Repo-relative paths only** in committed files (also load-bearing per the invariants).
- **One executable command per fenced code block** when a code block is meant to be copy-pasted into a shell, so the user can copy individual commands one at a time without breaking on multi-line clipboards.
- **`project/pyproject.toml` is the single source of truth** for Python tooling configuration (ruff, pytest, mypy if used) in this repo. A project that opts out of the `project/` convention puts it at the repo root.

## Glossary

Terms used consistently across briefs, skills, policies, and code. Mismatched usage is a bug — flag or fix.

- **Brief.** A document under `briefs/` describing *what* to build, *why*, and *what was decided*. Briefs inform phases; phases reference briefs.
- **Policy.** A short, prescriptive rule under `policies/` that every phase honors. Policies are the law of the repo.
- **Phase.** One unit of phased work. A phase file (`plan/phase-N.md`) holds Goal, Deliverables, Acceptance, and Brief refs. Status lives in `plan/INDEX.md`.
- **Sub-phase.** A child of a major phase (`plan/phase-N.M.md`), produced by decomposing the parent at the moment the parent becomes the next phase to work.
- **`/kickoff`.** The orchestrator skill. Runs one phase end-to-end through planner → reviewer → coder → critic. Writes START/END to `LOG.md`. Does not write code itself.
- **`/starter`.** The starter-template-only bootstrapping skill. Stamps out a new project in a different directory using *this* repo as the master template.
- **`/learn`.** Universal cross-repo skill. Explores a donor repo and proposes which of its patterns to absorb into the current repo. Plan-first; user approves; then applies. The donor stays read-only.
- **`/teach`.** Universal cross-repo skill. Inverse of `/learn`. Proposes which of the current repo's patterns to apply to a target repo. Plan-first; user approves; then applies to the target. The current repo stays read-only during teaching.
- **The four canonical agents.** `phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`. Their names are load-bearing — `/kickoff` invokes them by name. Their definitions live in `.claude/agents/` (canonical) and `.codex/agents/` (mirror).
- **Build gate.** A shell command (or sequence) the orchestrator runs after the coder finishes, to confirm the code still builds, lints, types, and tests clean.
- **Acceptance.** The empirical criteria the phase declares for being "done." May include shell-command checks and named manual checks. The human signs off.
- **START / END block.** The two entries `/kickoff` appends to `LOG.md` per phase — one when the phase is taken up (`🚧`) and one when it is closed (`✅` or paused).
