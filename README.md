# Agentic Coding Starter Template

A repository template for building software with AI coding agents under a structured, multi-agent methodology. It encodes a workflow that turns a vague idea into shippable software through a planner → reviewer → coder → critic loop, with humans deciding what "done" means.

This template is harness-agnostic. It works with [Claude Code](https://claude.com/claude-code), with [Codex CLI](https://github.com/openai/codex), and with any other agent host that reads project-level instructions and agent definitions from `.claude/`, `.codex/`, `.agents/`, or `AGENTS.md`. The same files drive both — never edit a harness-specific mirror by hand.

---

## What this is

A starter template — a *master template* — for projects that use agent-driven development. Clone it, run `/starter` to spin up a new project from it, or open it directly and run `/kickoff` to start building.

The template ships with:

- A **methodology** (eleven-step pipeline, see [`briefs/methodology.md`](briefs/methodology.md)) that takes you from idea to shipped code.
- A **`/kickoff` skill** that orchestrates one phase of work end-to-end: plan → plan-review → code → code-review → build → log.
- Four **canonical agent roles** (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`) defined once and mirrored to every supported harness.
- A **`/starter` skill** (starter-template-only) for stamping out new repos from this one.
- **`/learn` and `/teach` skills** (universal — carried into every derived project) for moving patterns *between* methodology-following repos. `/learn` absorbs patterns from another repo into the current one; `/teach` sends patterns from the current repo out to a target. Both are plan-first: the user approves before any file changes.
- A **`plan/` ledger** (status table, dependency graph, cross-cutting concerns) where work is tracked phase by phase.
- A **`briefs/` library** for durable design decisions and methodology notes.
- A **`policies/` library** for the rules every phase must respect.
- A **`LOG.md`** activity log written by `/kickoff` on phase open and close.
- A minimal Python example project so the build gates have something real to chew on.

---

## Why this exists

Coding with agents is high-leverage but easy to do badly. Without structure, you get:

- Agents that re-derive the same decisions every session.
- Plans nobody reviewed and code nobody checked.
- "Done" that means "the agent stopped talking" rather than "the human accepted the work."
- A directory whose state is impossible to reconstruct from its files.

This template solves those problems by externalizing the parts of the work that *must* persist across sessions: the brief (what), the architecture (how), the plan (in what order), the log (what actually happened), and the policies (what's off-limits). Each session starts from those artifacts and ends by updating them.

The result is a workflow where each phase is incremental, testable, and reviewed by a human before the next one begins.

---

## How to use this template

There are two ways to start.

### Option A — Stamp out a new project (recommended)

From inside this repo, in your agent host of choice:

```
/starter ~/path/to/new-project "one-line description of what to build"
```

The `/starter` skill copies this repo's structural files into the new directory, asks a few configuration questions (project name, primary language, build commands) when the description doesn't make them obvious, and leaves you with a ready-to-`/kickoff` project.

### Option B — Use this repo directly

If you're trying it out or learning the workflow, just open this repo in your agent host and type:

```
/kickoff
```

The first kickoff will pick up Phase 1 (currently a placeholder for "decide what you're building"), walk you through the planner → reviewer → coder → critic loop, and write a START/END pair to `LOG.md`. Edit the brief, edit the plan, run kickoff again. The example Python project under `example/` exists so build gates have something to lint and test from the very first run.

---

## The eleven-step methodology

The full version lives in [`briefs/methodology.md`](briefs/methodology.md). The short version:

1. **Vague ideas → insights.** Surface what's actually being asked for. Do competitive analysis.
2. **Insights → brief.** Write down *what* you're building. Lives under `briefs/`.
3. **Brief → architecture.** Research Best Current Practices. Decide *how*.
4. **Repo-level policies.** Codify the non-negotiables. Lives under `policies/`.
5. **Brief + architecture → phased plan.** Break the work into incremental, testable phases.
6. **Sub-phase breakdown at phase start.** Decompose each major phase only when you start it.
7. **Orchestrator-driven sub-phase execution.** `/kickoff` runs planner → reviewer → coder → critic, with bounded revision loops. It never writes code itself.
8. **Acceptance check.** The orchestrator runs the tests and gates the phase declares.
9. **Append-only phase log.** `LOG.md` records open and close with evidence.
10. **Human evaluation.** *You* decide whether each sub-phase is done. The agent does not.
11. **Stay agile.** Add or split phases as the problem gets clearer.

---

## Repository layout

```
.
├── README.md                       ← this file
├── CLAUDE.md                       ← top-level guidance for agents
├── AGENTS.md                       ← symlink → CLAUDE.md (for Codex/aider)
├── LOG.md                          ← append-only activity log
├── project/                        ← the deliverable (self-contained per
│   │                                  policies/project-isolation.md)
│   ├── pyproject.toml              ←   package metadata
│   ├── uv.lock
│   ├── example/                    ←   source code
│   │   ├── __init__.py
│   │   └── cli.py
│   ├── tests/                      ←   pytest suite
│   │   └── test_cli.py
│   └── README.md                   ←   the artifact's own quickstart
├── briefs/                         ← durable design + methodology library
│   ├── BRIEF.md                    ←   entry-point brief for *this* repo
│   ├── methodology.md              ←   the eleven-step methodology
│   └── agentic-bootstrap.md        ←   how to stand up a new project
├── policies/                       ← non-negotiable rules every phase honors
│   ├── README.md
│   ├── briefs-and-policies.md
│   ├── cross-harness-parity.md
│   ├── phase-status.md
│   ├── acceptance-empirical.md
│   ├── repo-relative-paths.md
│   ├── log-discipline.md
│   ├── human-in-the-loop.md
│   ├── four-canonical-agents.md
│   ├── project-isolation.md        ← isolate deliverable under project/
│   └── greenfield-until-released.md ← no backward-compat shims pre-release
├── plan/                           ← phased execution plan
│   ├── INDEX.md                    ←   phase ledger (status lives ONLY here)
│   └── phase-1.md                  ←   first phase (a stub you replace)
├── .claude/                        ← Claude Code agent definitions
│   ├── skills/
│   │   ├── kickoff/SKILL.md        ←   phase orchestrator
│   │   ├── methodology/SKILL.md    ←   the eleven steps (self-contained)
│   │   ├── learn/SKILL.md          ←   absorb patterns FROM another repo (universal)
│   │   ├── teach/SKILL.md          ←   send patterns TO another repo (universal)
│   │   └── starter/SKILL.md        ←   new-project bootstrapper (starter-only)
│   └── agents/
│       ├── phase-planner.md
│       ├── plan-reviewer.md
│       ├── phase-coder.md
│       └── code-critic.md
├── .codex/                         ← Codex CLI slash-command + agent mirrors
│   ├── agents/
│   │   ├── phase-planner.toml
│   │   ├── plan-reviewer.toml
│   │   ├── phase-coder.toml
│   │   └── code-critic.toml
│   └── prompts/
│       ├── kickoff.md              ← Codex slash-command entry point (symlink → .claude/skills/<name>/SKILL.md)
│       ├── methodology.md
│       ├── learn.md
│       ├── teach.md
│       └── starter.md
└── .agents/                        ← Codex CLI's native project-skill discovery
    └── skills/                     ←   (developers.openai.com/codex/skills)
        ├── kickoff                 ←   each is a directory symlink → ../../.claude/skills/<name>
        ├── methodology             ←     (directory-level because Codex doesn't follow
        ├── learn                   ←      file-level symlinks inside skill dirs — issue #11314)
        └── teach                   ←   /starter is intentionally absent
```

---

## Status markers

Phase status lives in **`plan/INDEX.md`** and nowhere else. The legend is:

- ⏳ Not Started
- ⬅️ Next — exactly one phase carries this marker at any time
- 🚧 In Progress
- ✅ Completed

`/kickoff` flips `⬅️` → `🚧` on start, `🚧` → `✅` on completion, and advances the next `⏳` row to `⬅️`. Status does not live in per-phase frontmatter; `id`, `title`, `depends_on`, and `informs` are the only frontmatter fields.

---

## The four canonical agents

Every phase passes through four roles. Their names are load-bearing — `/kickoff` calls them by name.

| Role | Tools | Writes code | Job |
|---|---|---|---|
| `phase-planner` | Read, Grep, Glob, WebSearch, WebFetch | No | Turn one phase into a concrete, file-level plan |
| `plan-reviewer` | Read, Grep, Glob, AskUserQuestion | No | Approve the plan or send it back for revision |
| `phase-coder` | Read, Write, Edit, Grep, Glob, Bash | Yes | Implement the approved plan |
| `code-critic` | Read, Grep, Glob | No | Approve the code or send it back for revision |

`/kickoff` itself does *not* write code. Its job is to delegate, watch verdicts, run build gates, and write `LOG.md`.

---

## Briefs vs. policies vs. plan

These three directories look similar at a glance. The distinction is load-bearing.

- **`briefs/`** — *what* you're building and why. Durable design decisions, methodology, research notes, glossaries. A brief informs every phase that references it.
- **`policies/`** — non-negotiable *rules* every phase honors. Cross-cutting invariants ("repo-relative paths only", "tests must hit a real database", "every phase produces a START/END log entry"). Policies are short and prescriptive.
- **`plan/`** — *in what order* you're building it. Phase files, dependency graph, status ledger.

When the plan and a brief disagree, the plan wins — it is the refinement. When code and a policy disagree, the policy wins — it is the law.

See [`policies/briefs-and-policies.md`](policies/briefs-and-policies.md) for the full contract.

---

## Cross-harness parity

The same workflow runs in Claude Code, Codex CLI, and other agent hosts. The contract:

- **Canonical sources** live under `.claude/` (skills, agents) and at the repo root (`CLAUDE.md`).
- **Harness mirrors** are either symlinks (`AGENTS.md` → `CLAUDE.md`; `.codex/prompts/<name>.md` → `.claude/skills/<name>/SKILL.md` as a *file* symlink; `.agents/skills/<name>` → `.claude/skills/<name>` as a *directory* symlink) or thin wrapper files (`.codex/agents/*.toml`) that point at the canonical content.
- **`.codex/prompts/`** feeds Codex's slash-command surface; **`.agents/skills/`** feeds Codex's native skill loader ([documented contract](https://developers.openai.com/codex/skills)). Both mirror the same canonical skill content. The `.agents/skills/` mirror uses *directory* symlinks because Codex doesn't follow file-level symlinks inside a skill directory ([openai/codex#11314](https://github.com/openai/codex/issues/11314)), but does traverse a symlinked skill directory.
- **Never edit a mirror by hand.** Update the canonical file; refresh the mirror.

See [`policies/cross-harness-parity.md`](policies/cross-harness-parity.md) for the rules and the onboarding procedure for adding a third harness.

---

## Cross-repo knowledge transfer: `/learn` and `/teach`

Once you have more than one methodology-following project, patterns evolve in one and stop in another. Two universal skills handle the round trip:

- **`/learn <donor-dir> [<desc>]`** — Run from inside *this* repo. Explores `<donor-dir>` for patterns (skills, policies, briefs, agent refinements, build-gate idioms, even domain specializations) and proposes which to absorb. The donor stays read-only. You get a plan ranked by generality (methodology-level first, language specializations later, domain specializations last). Nothing is written here until you approve.
- **`/teach <target-dir> [<desc>]`** — The inverse. Run from inside *this* repo. Proposes which of *this* repo's patterns to apply to `<target-dir>` — useful for upgrading a previously-stamped project that has fallen behind, or retrofitting an existing project with the methodology. This repo stays read-only. The target's custom skills, agents, briefs, and active phase work are preserved by default.

Both skills are carried into every project `/starter` stamps out, so any methodology-following project can `/learn` from any other and `/teach` to any other.

The `<desc>` argument narrows intent. Omit it for a broad assessment that defaults to general-purpose improvements; supply it to focus on a specific surface ("focus on the testing setup", "Unity specialization", "just the policies").

## First-time setup

1. Pick a harness:
   - **Claude Code**: `claude` in this directory.
   - **Codex CLI**: `codex` in this directory.
2. Read [`briefs/BRIEF.md`](briefs/BRIEF.md), [`briefs/methodology.md`](briefs/methodology.md), and [`plan/INDEX.md`](plan/INDEX.md) to ground yourself in what this repo expects.
3. Either:
   - Use this repo directly: type `/kickoff` and let the orchestrator drive the placeholder Phase 1.
   - Stamp out a new project: type `/starter ~/path/to/new-project "what you want to build"`.

---

## License

The contents of this template are released under the terms in `LICENSE` (provide your own; this template makes no claim on what you build with it).
