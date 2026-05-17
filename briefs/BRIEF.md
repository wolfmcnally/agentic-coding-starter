---
title: "Agentic Coding Starter Template — Product Brief"
date: 2026-05-17
status: methodology
scope: Entry-point brief for this repository. Describes what the starter template is, who it's for, the two operating modes, and acceptance criteria.
---

# Agentic Coding Starter Template — Product Brief

A repository template for building software with AI coding agents under a structured planner → reviewer → coder → critic methodology. It is harness-agnostic: the same canonical files drive Claude Code, Codex CLI, and any other agent host that reads project-level instructions and agent definitions.

## Thesis

Coding with AI agents is high-leverage but easy to do badly. Without structure, you get plans nobody reviewed, code nobody checked, and a workspace whose state is impossible to reconstruct from its files. This template externalizes the load-bearing parts of the work — the brief (what), the architecture (how), the plan (in what order), the log (what actually happened), and the policies (what's off-limits) — so every session starts from a known state and ends by updating it.

The result is a workflow where each phase is incremental, testable, and reviewed by a human before the next one begins.

## Catalog

See [`CLAUDE.md` — Briefs catalog](../CLAUDE.md#briefs-catalog) for the index of sibling briefs.

---

## 1. What the template provides

- **A methodology.** An eleven-step pipeline from vague idea to shipped code. Authoritative source: [`methodology.md`](methodology.md).
- **A `/kickoff` skill.** A phase orchestrator that delegates to four specialist agents and writes `LOG.md`. Authoritative source: `.claude/skills/kickoff/SKILL.md`.
- **Four canonical agent roles.** `phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`. Names are load-bearing; `/kickoff` invokes them by name. Defined under `.claude/agents/` and mirrored to `.codex/agents/`.
- **A `/starter` skill.** Stamps out a new project from this template into a different directory, with light configuration.
- **A `plan/` ledger.** Phase table, dependency graph, cross-cutting concerns, critical-files map. Status lives only here.
- **A `briefs/` library.** Durable design decisions and methodology notes.
- **A `policies/` library.** The non-negotiable rules every phase respects.
- **A `LOG.md`.** Append-only activity log, owned by `/kickoff`.
- **A minimal example project.** A tiny Python package under `project/example/` so build gates have a real target to lint and test against from the first session. The deliverable lives under `project/` per [`../policies/project-isolation.md`](../policies/project-isolation.md), making it submodule-ready once the project is real.

## 2. Two operating modes

This repository supports two usage modes.

### Mode A — Master template

The dominant intended use. From an agent host inside this repo, run:

```
/starter ~/path/to/new-project "one-line description of what to build"
```

The `/starter` skill creates the directory, copies the structural files, customizes the project name, briefs catalog, and build gates for the new project, and asks a small number of configuration questions only when the description doesn't make the answers obvious.

The new project comes up ready to `/kickoff`. The old template repo is unchanged.

### Mode B — Self-build

A secondary mode used to validate that the template actually works, and to give human readers a fully working example. If a user opens *this* repo in an agent host and types `/kickoff`, the orchestrator picks up Phase 1 from [`../plan/INDEX.md`](../plan/INDEX.md) and walks through the full plan → review → code → review → build → log cycle against the example Python project.

In Mode B, the example project under `project/example/` is the build target. In Mode A, the example may be deleted or replaced as soon as the new project's real surface lands.

## 3. Who this is for

- People who want to use coding agents seriously but find ad-hoc prompting unreliable.
- Teams that need agent-driven work to leave a reviewable audit trail per phase.
- Individual builders standing up many small projects who want a repeatable scaffold.
- Anyone willing to let a human decide what "done" means — the methodology assumes a human in the loop and is the wrong tool for fully autonomous code generation.

## 4. Who this is *not* for

- Single-file scripts. The overhead is not worth it.
- Throwaway prototypes where the goal is to learn whether an idea works, not to build it well. (Use the methodology *before* a throwaway prototype, to decide if the prototype is the right next step.)
- Teams that want the agent to commit autonomously. The template's load-bearing assumption — that a human accepts each phase — is non-negotiable. See [`../policies/human-in-the-loop.md`](../policies/human-in-the-loop.md).

## 5. Anti-goals

This template deliberately does *not*:

- **Prescribe a language stack.** The example is Python because Python is broadly familiar, but the methodology is language-agnostic. The `/starter` skill asks about the primary language and adapts build gates.
- **Prescribe a specific agent host.** Claude Code and Codex CLI are first-class. The cross-harness parity policy ([`../policies/cross-harness-parity.md`](../policies/cross-harness-parity.md)) describes how to add a third.
- **Auto-commit.** The orchestrator reports each phase's status; the human commits. The human owns the git history.
- **Manage secrets, deployments, or infrastructure.** Those belong in project-specific briefs and policies once a project graduates beyond the template.

## 6. Architectural invariants

These are the rules the template assumes about itself. A project derived from this template inherits them and may add more.

- **Briefs are the contract.** Every phase points at one or more briefs. Phase files specify *how*; briefs specify *what*. Fix ambiguous briefs at the source.
- **Policies are the law.** Every phase honors every policy. A policy violation blocks acceptance.
- **Status lives in one place.** `plan/INDEX.md`'s phase table is the single source of truth for phase status.
- **Acceptance is empirical.** Verifiable shell commands and named manual checks — not "the code compiles."
- **Repo-relative paths only** in committed files.
- **Cross-harness parity.** Canonical files have one home; mirrors are symlinks or thin wrappers.
- **Human decides done.** The orchestrator never auto-commits and never claims subjective acceptance.

## 7. Acceptance for *this template*

The template is acceptable when:

- A user clones this repo, opens it in Claude Code (or Codex CLI), and types `/kickoff` — and the orchestrator picks up Phase 1, walks through plan → plan-review → code → code-review → build → log, and produces a START/END pair in `LOG.md` with a non-empty Files changed section.
- A user types `/starter ~/some-new-dir "build a small CLI that fetches the time from an NTP server"` — and ends up with a populated new directory that itself satisfies the bullet above, with project-specific naming everywhere references appear.
- The example Python project under `project/example/` exists and passes its build gates from inside `project/` (`cd project && uv run ruff check example tests && uv run ruff format --check example tests && uv run pytest -q`) on first clone.
- No file in this repo references Wolf McNally, his email, his other projects, or any third-party PII. The template is distributable.
- Every file under `briefs/` is listed in `CLAUDE.md`'s Briefs catalog, and every file in the catalog exists. No orphans either way.
- Every file under `policies/` is listed in `CLAUDE.md`'s Policies catalog, and every file in the catalog exists. No orphans either way.
- `AGENTS.md` is a symlink to `CLAUDE.md` (verifiable with `readlink AGENTS.md`).
- `plan/INDEX.md` carries exactly one `⬅️` row at any time.

## 8. Out of scope

- Full multi-phase plan for *this* repo. The methodology says decompose major phases at start-time, not bootstrap-time. Phase 1 of this repo is "Acquire a real project" — i.e., either run `/starter` to spin out a new project, or replace Phase 1 with whatever real work the user wants to do here.
- A graphical UI, a web dashboard, or any presentation layer. The template is text files.
- A test harness that proves agentic loops produce correct code. That's a research project; this is a scaffolding.
