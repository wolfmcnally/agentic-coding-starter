---
name: stamp
description: >-
  Stamp out a new project at <directory>, using this repository as the
  master template. Asks a small number of configuration questions only when
  the optional <description> doesn't make the answers obvious. Adapts
  CLAUDE.md, README.md, briefs/BRIEF.md, the kickoff skill's build gates,
  and the four canonical agents for the new project's name and primary
  language. Invoke as /stamp <directory> [<description>] in Claude Code or
  $stamp <directory> [<description>] in Codex.
argument-hint: "<directory> [<description>]"
---

# Stamp — Bootstrap a new agentic-coding project

Use **this** repository as a master template to stand up a new project at `<directory>`. The new project ends up with everything needed to immediately invoke its `kickoff` skill (`/kickoff` in Claude Code; `$kickoff` in Codex): a brief, a phased plan, policies, the four canonical agents, the kickoff skill, the methodology skill, harness mirrors, and a minimal code surface in the project's primary language.

The authoritative contract this skill implements is [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md). Read that brief before deviating from this skill.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

The arguments are a positional `<directory>` followed by an optional `<description>`. Both may contain spaces; the description is everything after the first whitespace-separated token unless the directory itself is quoted.

- `<directory>` — the destination path. May be absolute (`~/projects/foo`, `/Users/me/foo`) or relative to the current working directory. Tilde is expanded.
- `<description>` (optional) — a one-line description of what the new project is for. When provided and informative, it answers most of the configuration questions automatically.

If `<directory>` is missing, refuse with: `Usage: /stamp <directory> [<description>] (Claude Code) or $stamp <directory> [<description>] (Codex)` and exit.

## Pre-flight checks

Before changing anything, verify:

1. **Source repo invariants.** This repo (the template) is itself in a healthy state. Specifically:
   - `readlink AGENTS.md` returns `CLAUDE.md`.
   - `.claude/agents/` contains exactly `phase-planner.md`, `plan-reviewer.md`, `phase-coder.md`, `code-critic.md`.
   - `.claude/skills/kickoff/SKILL.md`, `.claude/skills/methodology/SKILL.md`, and `.claude/skills/roles/SKILL.md` exist.
   - `bin/kickoff-config` exists and is executable.
   - `kickoff.yaml` exists and `./bin/kickoff-config show` validates both sections.
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
| `primary_language` | Drives the deliverable's code skeleton and build gate commands | Inferred from description heuristics; defaults to `python` |
| `surfaces` | List of repo surfaces (e.g., `cli`, `library`, `web`, `service`) | Inferred; defaults to `[cli]` |
| `project_isolation` | Whether to adopt the `project/` subdirectory convention per [`policies/project-isolation.md`](../../../policies/project-isolation.md) | Default *opt-in* for single-deliverable projects (`cli`, `library`, `service`, `book`); default *opt-out* for polyglot or multi-deliverable repos (`surfaces` length > 1 with siblings like `web`+`service`) |

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
  .claude/skills/learn/
  .claude/skills/teach/
  .claude/skills/roles/
  .claude/agents/
  .codex/agents/
  .agents/skills/         # (kickoff, methodology, learn, teach, roles added
                          #  as directory symlinks in Step 2)
```

Plus the language-specific deliverable directories. When `project_isolation` is enabled (the default for single-deliverable projects), the deliverable goes under `project/`:

- Python: `project/<slug>/`, `project/tests/`
- TypeScript: `project/src/`, `project/tests/`
- Rust: `project/src/`, `project/tests/`
- Go: `project/cmd/<slug>/`, `project/internal/`
- Other: appropriate convention, all under `project/`

When `project_isolation` is disabled (polyglot or multi-deliverable repos), the deliverable directories live at the repo root as siblings, with no `project/` wrapper:

- Polyglot example: `web/`, `lambda/<svc>/`, `cdk/`, etc. as top-level siblings.

### Step 2 — Copy verbatim, adapt names

Copy these files **from this template** into the new project, then run a name substitution pass (replacing `Agentic Coding Starter Template`, `agentic-coding-starter-template`, and `starter` with `<project_name>`, `<project_slug>`, and a project-appropriate handle):

- `.claude/skills/kickoff/SKILL.md`
- `.claude/skills/methodology/SKILL.md`
- `.claude/skills/learn/SKILL.md`
- `.claude/skills/teach/SKILL.md`
- `.claude/skills/roles/SKILL.md`
- `.claude/agents/phase-planner.md`
- `.claude/agents/plan-reviewer.md`
- `.claude/agents/phase-coder.md`
- `.claude/agents/code-critic.md`
- `.codex/agents/phase-planner.toml`
- `.codex/agents/plan-reviewer.toml`
- `.codex/agents/phase-coder.toml`
- `.codex/agents/code-critic.toml`
- Every file under `policies/` **except** any policy explicitly marked starter-only (currently `policies/anonymize-log-references.md` — the public-repo LOG anonymization rule; the asymmetry is driven by this template's publicness, not by methodology).
- `briefs/methodology.md` (verbatim — methodology is universal)
- `briefs/agentic-bootstrap.md` (verbatim — so the next bootstrap from this project is possible)
- `briefs/cross-agent-invocation.md` (verbatim — the cross-CLI invocation BCPs that `policies/role-models.md` cites are universal)
- `briefs/deterministic-orchestration.md` (verbatim — universal draft brief: decision criteria for a deterministic kickoff loop once every supported harness has a parity workflow primitive)
- `tests/test_kickoff_config.py` (verbatim — universal behavioral coverage for the manager/watchdog contract)

Then create the `.agents/skills/` **directory symlinks** for Codex CLI's native skill discovery. Each is a relative symlink whose target is the canonical skill *directory* (not the SKILL.md file inside it — Codex doesn't follow file-level symlinks inside a skill dir per [openai/codex#11314](https://github.com/openai/codex/issues/11314), but does traverse a symlinked skill directory):

```
cd <dest>
mkdir -p .agents/skills
ln -s ../../.claude/skills/kickoff     .agents/skills/kickoff
ln -s ../../.claude/skills/methodology .agents/skills/methodology
ln -s ../../.claude/skills/learn       .agents/skills/learn
ln -s ../../.claude/skills/teach       .agents/skills/teach
ln -s ../../.claude/skills/roles       .agents/skills/roles
```

Verify each `readlink <dest>/.agents/skills/<name>` returns the expected target and `test -L <dest>/.agents/skills/<name> && test -d <dest>/.agents/skills/<name>` passes before moving on.

**Do not** copy `.claude/skills/stamp/` (this skill itself), create `.agents/skills/stamp` in the destination, or copy `policies/anonymize-log-references.md`, `bin/check-anonymization.sh`, or `bin/anonymization-denylist.local.example` (and drop the `bin/anonymization-denylist.local` line from the copied `.gitignore`). The new project doesn't need to stamp out more projects unless it explicitly wants to be a template too, and the anonymization rule (and its enforcement script) doesn't apply to private downstream projects. The `learn` and `teach` skills *are* carried over — they are universal cross-repo skills that benefit every methodology-following project.

The `bin/` directory, its `bin/README.md` convention preamble, and `policies/mechanistic-vs-intelligence.md` **are** carried over. The universal `bin/kickoff-config` manager and human-editable `kickoff.yaml` carry over too. Seed both config sections by running `<dest>/bin/kickoff-config reset all`; this preserves data under `extensions` if the destination already has it. The manager runs via `uv` with PEP 723 `ruamel.yaml`, so the destination needs `uv` on PATH. Keep its script entry in `bin/README.md`; delete only the starter-only anonymization entry.

Because the anonymization policy and its script are starter-only but `code-critic.md` is copied verbatim (above), the adaptation pass must **delete the "External / private-repo references" bullet** from the destination's `.claude/agents/code-critic.md` — it references `bin/check-anonymization.sh` and `policies/anonymize-log-references.md`, neither of which the new project will have.

### Step 3 — Write the project-specific files

Author these afresh, using the gathered configuration:

- **`<dest>/README.md`** — didactic top-level for human readers. Mirror the template's section structure (what this is, why, how to use, repository layout, status markers, four canonical agents, briefs-vs-policies-vs-plan, first-time setup). Every line is `<project_name>`-specific.

- **`<dest>/CLAUDE.md`** — top-level agent guidance. The template's `CLAUDE.md` has two clearly-marked zones (HTML comments delimit them). The job:
  - **Copy the file as a whole.**
  - **Inside the `<!-- METHODOLOGY_CONTRACT_START --> ... <!-- METHODOLOGY_CONTRACT_END -->` markers**: leave verbatim. This is the universal methodology content; every derived project gets the same text.
  - **Inside the `<!-- PROJECT_CONTEXT_START --> ... <!-- PROJECT_CONTEXT_END -->` markers**: rewrite from scratch for the new project. Sections to author:
    - `# Project Context` header (unchanged).
    - `## This Repo is <project_name>` — canonical spelling, one-sentence thesis (from `description`), pointer to `briefs/BRIEF.md`.
    - `## Project briefs` — list of `briefs/*.md` files specific to this project (initially just `BRIEF.md`).
    - `## Project surfaces` — describe the deliverable (path, what language, what the example or seed code is). When `project_isolation` is on, the surface is `project/`; when off, name the sibling deliverable directories.
    - `## Project conventions` — language, tooling, build-gate command shape for this project.
    - `## Model & review venue` — describe `kickoff.yaml` as the human-editable source for separate model/effort fields and execution budgets; `roles` is an optional validated editor; the shipped default gives cross-vendor review. Governed by the two role policies.
    - `## Project-specific skills` — if the new project carries any skills beyond the universal five (kickoff, methodology, learn, teach, roles), list them here. For most fresh projects, this section is empty (or omitted).
  - Preserve the introductory paragraph that explains the two-zone contract; it is informational and lives outside both markers.

- **`<dest>/AGENTS.md`** — symlink to `CLAUDE.md`. Create with `ln -s CLAUDE.md AGENTS.md` in the destination.

- **`<dest>/LOG.md`** — one-line stub:
  ```markdown
  # Activity Log

  This log is **append-only** and owned by `kickoff`. Do not hand-edit historical entries.
  ```

- **`<dest>/briefs/BRIEF.md`** — entry-point brief for the new project. Use the thesis-stub shape: H1, italic tagline, `## Thesis` paragraph from `description`, `## Catalog` pointer to `../CLAUDE.md#briefs-catalog`. Mark `status: draft` in frontmatter so the user knows it needs to be fleshed out.

- **`<dest>/plan/INDEX.md`** — copy this template's `plan/INDEX.md` structure, adapted: project name in the H1; the dependency graph enumerates every major phase the brief surfaces (Phase 1 + sketched Phases 2+); the phase table has one row per major phase, with Phase 1 as `⬅️` and the rest as `⏳`. See [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) §8.

- **`<dest>/plan/phase-1.md`** — a real first phase for the new project, drafted **in full**. Use the description plus inferred surfaces to draft Goal, Deliverables, and Acceptance. Mark Open Questions where the description is genuinely insufficient. Phase 1 should aim to deliver the project's "first slice end-to-end" — for a CLI, `<name> --help` plus one working subcommand; for a web app, the dev server plus one read-only page; for a library, the public API surface plus one working function.

- **`<dest>/plan/phase-2.md`, `<dest>/plan/phase-3.md`, …** — sketched major phases at lower fidelity. For each major phase the brief surfaces beyond Phase 1, draft a `phase-N.md` with frontmatter (`id`, `title`, `depends_on`, `informs`, plus `review_lane: light` only when the phase is mechanical per `policies/review-lanes.md` — omit otherwise) + one-paragraph Goal + high-level Deliverables list + scaffold Acceptance + Brief refs. These sketches will be tightened by ripple at each upstream phase's close (per [`policies/phase-ripple.md`](../../../policies/phase-ripple.md)) and elaborated when their row enters `⬅️` (per the kickoff Step 1a/9a/9b machinery). If the brief surfaces only a single phase, skip the sketches.

- **Do NOT draft any sub-phase files at bootstrap** — no `phase-1.1.md`, no `phase-2.1.md`, none. Sub-phase decomposition is JIT, owned by `kickoff` Step 1a at each major phase's open. The bootstrap leaves sub-phase shape to the orchestrator with each predecessor's outcomes in hand.

### Step 4 — Lay down the primary code surface

Write a minimal-but-runnable code skeleton in the project's primary language. The intent is that the project's build gates can be run successfully on first clone — Phase 1 then fleshes out the real behavior.

**Path convention.** All paths below are written assuming `project_isolation` is enabled (the default for single-deliverable projects). Prefix every path with `project/` when laying files down. If `project_isolation` is disabled, drop the `project/` prefix and lay files at the repo root.

**Python (paths inside `project/`):**
- `pyproject.toml` with `[project]` metadata, `[tool.ruff]`, `[tool.pytest.ini_options]`, dev deps `ruff`, `pytest`.
- A concise `README.md` for the artifact (the repo's didactic README is at the root).
- `<slug>/__init__.py` with version export.
- `<slug>/cli.py` with an argparse entry point that responds to `--help` and a stub subcommand.
- `tests/test_cli.py` with one passing test (e.g., asserts `--help` exits 0).
- `.gitignore` listing Python build artifacts (`__pycache__/`, `*.py[cod]`, `*.egg-info/`, `build/`, `dist/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.coverage`).

**TypeScript / Node (paths inside `project/`):**
- `package.json` with `scripts: { lint, test, typecheck }`.
- `tsconfig.json`.
- Concise `README.md`.
- `src/index.ts` exporting a stub function.
- `tests/index.test.ts` with one passing test.
- ESLint and Prettier config files.
- `.gitignore` listing Node build artifacts (`node_modules/`, `dist/`, `build/`, `coverage/`).

**Rust (paths inside `project/`):**
- `Cargo.toml` with `[package]` and one binary or one library entry.
- Concise `README.md`.
- `src/main.rs` (binary) or `src/lib.rs` (library) with a `--help`-handling entry point or a stub function.
- `tests/smoke.rs` with one passing test.
- `.gitignore` listing `target/`.

**Go (paths inside `project/`):**
- `go.mod` with the module path.
- Concise `README.md`.
- `cmd/<slug>/main.go` with a stub flag-parsing main.
- `internal/<slug>/<slug>.go` with a stub exported function.
- `internal/<slug>/<slug>_test.go` with one passing test.
- `.gitignore` listing Go build artifacts.

**Other languages:** apply the same pattern — package metadata, one source file with a stub entry, one passing test, a concise README, the language's `.gitignore` inside `project/`.

The artifact's `README.md` is short and self-contained (no `..` references) per [`policies/project-isolation.md`](../../../policies/project-isolation.md). The deliverable's `.gitignore` lives inside `project/` so submodule extraction carries it. The repo's top-level `.gitignore` lists only editor/OS files and agentic harness runtime state, including `.kickoff/` local timing telemetry. The repo's didactic top-level `README.md` describes the methodology and points at `project/` for the artifact.

When `project_isolation` is disabled (polyglot), there is no `project/.gitignore`; all language entries live at the repo root in a single combined `.gitignore`.

### Step 5 — Customize the kickoff skill's build gates

Open `<dest>/.claude/skills/kickoff/SKILL.md` and replace the **Final build gate** example commands with the project's actual gates. The template's defaults reference the Python `project/example/` package; adapt to the project's primary language. Keep the `cd project && ...` prefix when `project_isolation` is enabled; drop it otherwise.

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
- `ls <dest>/.claude/skills/stamp/` does **not** exist (we did not transfer it).
- For each name in {kickoff, methodology, learn, teach, roles}: `readlink <dest>/.agents/skills/<name>` returns `../../.claude/skills/<name>`, `test -L <dest>/.agents/skills/<name>` and `test -d <dest>/.agents/skills/<name>` both pass, and `<dest>/.agents/skills/<name>/SKILL.md` is reachable through the directory symlink.
- `<dest>/bin/kickoff-config show` runs; `<dest>/bin/README.md` retains its universal entry but **not** the `### check-anonymization.sh` entry.
- `<dest>/.agents/skills/stamp` does **not** exist (starter-only, must not propagate).
- The new `CLAUDE.md`'s catalogs reference every file in `briefs/` and `policies/`.
- `<dest>kickoff.yaml` exists; `show` prints the seeded cross-vendor model routing and portable timeout values; a scoped model edit preserves timeout comments/values; `<dest>/.gitignore` includes `.kickoff/`; the two role policies and invocation brief exist.
- `cd <dest> && uv run --with pytest pytest -q tests/test_kickoff_config.py` passes independently of the deliverable's language/toolchain.
- The project's primary build gate runs clean on the seeded code.

Run the language-specific gate to confirm. For example, for Python with `project_isolation` enabled:

```
cd <dest>/project && uv sync && uv run ruff check <slug> tests && uv run ruff format --check <slug> tests && uv run pytest -q
```

When `project_isolation` is disabled, drop the `/project` segment.

If any step fails, surface the failure and let the user fix it before declaring the bootstrap complete.

## Report

When the bootstrap finishes cleanly, report to the user:

- The destination path.
- The project name, slug, primary language, and inferred surfaces.
- That human-editable `kickoff.yaml` was seeded with cross-vendor model routing and portable role budgets; model and effort are separate fields; `roles` edits model fields; local telemetry stays under `.kickoff/`; and `bin/kickoff-config recommend-timeouts` proposes target-local recalibration.
- The path to the new project's `BRIEF.md` (which the user should flesh out next) and `plan/phase-1.md` (which the user should review before `kickoff`'ing).
- The recommended next steps:
  1. `cd <dest>`
  2. Read and edit `briefs/BRIEF.md` until it accurately describes the project.
  3. Read and edit `plan/phase-1.md` if the inferred Phase 1 isn't what you want.
  4. Run `/kickoff` in Claude Code or `$kickoff` in Codex to start Phase 1.

**Do not auto-commit** in the new project. The user owns the first commit.

## Rules

- The destination repo's content is the user's. Never mirror Wolf McNally, his projects, his email, or any third-party PII. The stamp skill itself ships in a distributable repo; the new repo is even more so.
- Ask only the questions inference cannot answer. A clear description shortens the bootstrap to seconds.
- When in doubt about a name, file path, or convention, prefer this template's choice — that's why it exists.
- Surface every assumption you made (inferred language, inferred surfaces, derived project name) in the final report so the user can correct anything before kickoff.
