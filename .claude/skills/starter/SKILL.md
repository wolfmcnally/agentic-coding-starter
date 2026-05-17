---
name: starter
description: >-
  Stamp out a new project at <directory>, using this repository as the
  master template. Asks a small number of configuration questions only when
  the optional <description> doesn't make the answers obvious. Adapts
  CLAUDE.md, README.md, briefs/BRIEF.md, the kickoff skill's build gates,
  and the four canonical agents for the new project's name and primary
  language. Invoke as /starter <directory> [<description>].
argument-hint: "<directory> [<description>]"
---

# /starter — Bootstrap a new agentic-coding project

Use **this** repository as a master template to stand up a new project at `<directory>`. The new project ends up with everything needed to immediately `/kickoff` its first phase: a brief, a phased plan, policies, the four canonical agents, the kickoff skill, the methodology skill, harness mirrors, and a minimal code surface in the project's primary language.

The authoritative contract this skill implements is [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md). Read that brief before deviating from this skill.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

The arguments are a positional `<directory>` followed by an optional `<description>`. Both may contain spaces; the description is everything after the first whitespace-separated token unless the directory itself is quoted.

- `<directory>` — the destination path. May be absolute (`~/projects/foo`, `/Users/me/foo`) or relative to the current working directory. Tilde is expanded.
- `<description>` (optional) — a one-line description of what the new project is for. When provided and informative, it answers most of the configuration questions automatically.

If `<directory>` is missing, refuse with: `Usage: /starter <directory> [<description>]` and exit.

## Pre-flight checks

Before changing anything, verify:

1. **Source repo invariants.** This repo (the template) is itself in a healthy state. Specifically:
   - `readlink AGENTS.md` returns `CLAUDE.md`.
   - `.claude/agents/` contains exactly `phase-planner.md`, `plan-reviewer.md`, `phase-coder.md`, `code-critic.md`.
   - `.claude/skills/kickoff/SKILL.md` and `.claude/skills/methodology/SKILL.md` exist.
   - `.codex/agents/*.toml` has one TOML file per canonical agent.
   - `briefs/BRIEF.md`, `briefs/methodology.md`, `briefs/agentic-bootstrap.md` exist.
   - `plan/INDEX.md` and `plan/phase-1.md` exist.
   - Every file under `policies/` is non-empty.
   If any check fails, refuse with a specific error naming the missing file and exit.

2. **Destination directory.** Expand `~` and resolve to an absolute path. Then:
   - If the path exists and is non-empty, refuse with: `Refusing to bootstrap into a non-empty directory: <path>`. Surface the contents so the user can decide.
   - If the path exists and is empty, proceed.
   - If the path does not exist, `mkdir -p` it (with the user's tacit consent — they named the directory).

3. **Parent directory writable.** Check the parent of the destination is writable. If not, refuse.

## Gather configuration

The skill needs five pieces of information to customize the new project:

| Key | Purpose | Default behavior when unspecified |
|---|---|---|
| `project_name` | Brand name; appears in README, CLAUDE.md, BRIEF.md | Derive from the final path segment (camel-case it: `my-tool` → `MyTool`) |
| `project_slug` | Lowercase-kebab; appears in package names, directory names | The final path segment |
| `description` | One-line thesis | The `<description>` argument, or "(to be written)" |
| `primary_language` | Drives the example surface and the build gate commands | Inferred from description heuristics; defaults to `python` |
| `surfaces` | List of repo surfaces (e.g., `cli`, `library`, `web`, `service`) | Inferred; defaults to `[cli]` |

**Inference heuristics** (apply only when `<description>` is informative):

- Description mentions "CLI", "command-line", "terminal tool" → `surfaces: [cli]`.
- Description mentions "web app", "frontend", "React", "Vue" → `surfaces: [web]`, `primary_language: typescript`.
- Description mentions "API", "server", "service", "backend" → `surfaces: [service]`.
- Description mentions "library", "SDK", "package" → `surfaces: [library]`.
- Description mentions "Rust", "Cargo" → `primary_language: rust`.
- Description mentions "Go" → `primary_language: go`.
- Description mentions "Python", "Django", "Flask", "pandas", "numpy" → `primary_language: python`.
- Description mentions "TypeScript", "JavaScript", "Node" → `primary_language: typescript`.
- Description mentions "Swift", "iOS" → `primary_language: swift`.
- Description mentions "Kotlin", "Android" → `primary_language: kotlin`.

**Ask the user only the questions inference can't answer.** Use `AskUserQuestion` with up to four questions per round. Common patterns:

- If `<description>` is empty or vague: ask for a one-line description first.
- If language can't be inferred: ask for primary language with the common choices.
- If the project name should differ from the kebab-cased slug: ask explicitly.

**Do not** ask configuration questions when the description is straightforward. "Build a Rust CLI that prints the current weather" needs no further questions — `project_name` from directory, `primary_language: rust`, `surfaces: [cli]`, done.

## Bootstrap procedure

Follow [`briefs/agentic-bootstrap.md` §3](../../../briefs/agentic-bootstrap.md) step by step. The condensed procedure:

### Step 1 — Lay down the directory skeleton

`mkdir -p` under the destination:

```
<dest>/
  briefs/
  policies/
  plan/
  .claude/skills/kickoff/
  .claude/skills/methodology/
  .claude/agents/
  .codex/agents/
  .codex/prompts/
```

Plus the language-specific directories:

- Python: `<slug>/`, `tests/`
- TypeScript: `src/`, `tests/`
- Rust: `src/`, `tests/`
- Go: `cmd/<slug>/`, `internal/`
- Other: appropriate convention

### Step 2 — Copy verbatim, adapt names

Copy these files **from this template** into the new project, then run a name substitution pass (replacing `Agentic Coding Starter Template`, `agentic-coding-starter-template`, and `starter` with `<project_name>`, `<project_slug>`, and a project-appropriate handle):

- `.claude/skills/kickoff/SKILL.md`
- `.claude/skills/methodology/SKILL.md`
- `.claude/agents/phase-planner.md`
- `.claude/agents/plan-reviewer.md`
- `.claude/agents/phase-coder.md`
- `.claude/agents/code-critic.md`
- `.codex/agents/phase-planner.toml`
- `.codex/agents/plan-reviewer.toml`
- `.codex/agents/phase-coder.toml`
- `.codex/agents/code-critic.toml`
- `.codex/prompts/kickoff.md`
- Every file under `policies/`
- `briefs/methodology.md` (verbatim — methodology is universal)
- `briefs/agentic-bootstrap.md` (verbatim — so the next bootstrap from this project is possible)

**Do not** copy `.claude/skills/starter/` (this skill itself) or `.codex/prompts/starter.md`. The new project doesn't need to stamp out more projects unless it explicitly wants to be a template too.

### Step 3 — Write the project-specific files

Author these afresh, using the gathered configuration:

- **`<dest>/README.md`** — didactic top-level for human readers. Mirror the template's section structure (what this is, why, how to use, repository layout, status markers, four canonical agents, briefs-vs-policies-vs-plan, first-time setup). Every line is `<project_name>`-specific.

- **`<dest>/CLAUDE.md`** — top-level agent guidance. Sections, in order:
  - `# CLAUDE.md` preamble.
  - `## This Repo is <project_name>` — canonical spelling, one-sentence thesis (from `description`), pointer to `briefs/BRIEF.md`.
  - `## Briefs catalog` — bulleted index of every file under `briefs/`.
  - `## Policies catalog` — bulleted index of every file under `policies/`.
  - `## Repo layout` — one-line description per top-level directory.
  - `## Phase work and the kickoff skill` — copy from this template's `CLAUDE.md`, adapted.
  - `## Architectural invariants` — copy the template's universals, plus any project-specific invariants the description implies (e.g., "no proprietary dependencies in the runtime path" for a FOSS project).
  - `## Activity log (LOG.md)` — short pointer.
  - `## Conventions` — language, tooling, file shapes.
  - `## Glossary` — domain terms from the description.

- **`<dest>/AGENTS.md`** — symlink to `CLAUDE.md`. Create with `ln -s CLAUDE.md AGENTS.md` in the destination.

- **`<dest>/LOG.md`** — one-line stub:
  ```markdown
  # Activity Log

  This log is **append-only** and owned by `/kickoff`. Do not hand-edit historical entries.
  ```

- **`<dest>/briefs/BRIEF.md`** — entry-point brief for the new project. Use the thesis-stub shape: H1, italic tagline, `## Thesis` paragraph from `description`, `## Catalog` pointer to `../CLAUDE.md#briefs-catalog`. Mark `status: draft` in frontmatter so the user knows it needs to be fleshed out.

- **`<dest>/plan/INDEX.md`** — copy this template's `plan/INDEX.md` structure, adapted: project name in the H1, a single Phase 1 in the dependency graph, a single `⬅️` row in the phase table.

- **`<dest>/plan/phase-1.md`** — a real first phase for the new project. Use the description plus inferred surfaces to draft a plausible Goal, Deliverables, and Acceptance. Mark Open Questions where the description is genuinely insufficient. Phase 1 should aim to deliver the project's "first slice end-to-end" — for a CLI, that's `<name> --help` plus one working subcommand; for a web app, that's the dev server plus one read-only page; for a library, that's the public API surface plus one working function. **Do not pre-build Phase 2.** The methodology says decompose at start-time.

### Step 4 — Lay down the primary code surface

Write a minimal-but-runnable code skeleton in the project's primary language. The intent is that the project's build gates can be run successfully on first clone — Phase 1 then fleshes out the real behavior.

**Python:**
- `pyproject.toml` with `[project]` metadata, `[tool.ruff]`, `[tool.pytest.ini_options]`, dev deps `ruff`, `pytest`.
- `<slug>/__init__.py` with version export.
- `<slug>/cli.py` with an argparse entry point that responds to `--help` and a stub subcommand.
- `tests/test_cli.py` with one passing test (e.g., asserts `--help` exits 0).
- `.gitignore` with Python plus agentic runtime-state entries.

**TypeScript / Node:**
- `package.json` with `scripts: { lint, test, typecheck }`.
- `tsconfig.json`.
- `src/index.ts` exporting a stub function.
- `tests/index.test.ts` with one passing test.
- ESLint and Prettier config files.
- `.gitignore` with Node plus agentic runtime-state entries.

**Rust:**
- `Cargo.toml` with `[package]` and one binary or one library entry.
- `src/main.rs` (binary) or `src/lib.rs` (library) with a `--help`-handling entry point or a stub function.
- `tests/smoke.rs` with one passing test.
- `.gitignore` with `target/` plus agentic runtime-state entries.

**Go:**
- `go.mod` with the module path.
- `cmd/<slug>/main.go` with a stub flag-parsing main.
- `internal/<slug>/<slug>.go` with a stub exported function.
- `internal/<slug>/<slug>_test.go` with one passing test.
- `.gitignore` with Go plus agentic runtime-state entries.

**Other languages:** apply the same pattern — package metadata, one source file with a stub entry, one passing test.

### Step 5 — Customize the kickoff skill's build gates

Open `<dest>/.claude/skills/kickoff/SKILL.md` and replace the **Final build gate** example commands with the project's actual gates. The template's defaults reference the Python `example/` package; adapt to the project's primary language.

### Step 6 — Initialize git

In the destination directory:

```
git init
git add .
```

Do *not* run `git commit`. The user owns the first commit ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)).

### Step 7 — Sanity-check

Run the bootstrap acceptance check from [`briefs/agentic-bootstrap.md` §6](../../../briefs/agentic-bootstrap.md), against the destination. Specifically:

- `readlink <dest>/AGENTS.md` returns `CLAUDE.md`.
- `grep -E '^\| \[Phase ' <dest>/plan/INDEX.md` returns at least one row with `⬅️`.
- `head -1 <dest>/LOG.md` is `# Activity Log`.
- `ls <dest>/.claude/agents/` lists exactly the four canonical role files.
- `ls <dest>/.claude/skills/kickoff/` contains `SKILL.md`.
- `ls <dest>/.claude/skills/methodology/` contains `SKILL.md`.
- `ls <dest>/.claude/skills/starter/` does **not** exist (we did not transfer it).
- The new `CLAUDE.md`'s catalogs reference every file in `briefs/` and `policies/`.
- The project's primary build gate runs clean on the seeded code.

Run the language-specific gate to confirm. For example, for Python:

```
cd <dest>
uv sync   # if uv is used
uv run ruff check <slug> tests
uv run ruff format --check <slug> tests
uv run pytest -q
```

If any step fails, surface the failure and let the user fix it before declaring the bootstrap complete.

## Report

When the bootstrap finishes cleanly, report to the user:

- The destination path.
- The project name, slug, primary language, and inferred surfaces.
- The path to the new project's `BRIEF.md` (which the user should flesh out next) and `plan/phase-1.md` (which the user should review before `/kickoff`'ing).
- The recommended next steps:
  1. `cd <dest>`
  2. Read and edit `briefs/BRIEF.md` until it accurately describes the project.
  3. Read and edit `plan/phase-1.md` if the inferred Phase 1 isn't what you want.
  4. Run `/kickoff` to start Phase 1.

**Do not auto-commit** in the new project. The user owns the first commit.

## Rules

- The destination repo's content is the user's. Never mirror Wolf McNally, his projects, his email, or any third-party PII. The starter skill itself ships in a distributable repo; the new repo is even more so.
- Ask only the questions inference cannot answer. A clear description shortens the bootstrap to seconds.
- When in doubt about a name, file path, or convention, prefer this template's choice — that's why it exists.
- Surface every assumption you made (inferred language, inferred surfaces, derived project name) in the final report so the user can correct anything before kickoff.
