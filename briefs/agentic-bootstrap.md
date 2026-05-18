---
title: "Standing Up a New Project From This Template"
date: 2026-05-17
status: methodology
scope: Procedure for using this repository as a master template to stand up a new project under the agentic coding methodology. Authoritative reference for the `/starter` skill.
---

# Standing Up a New Project From This Template

How to use this repository as a *master template* to bootstrap a new project that follows the same agentic coding methodology. This brief is the contract `/starter` implements; read it before customizing the skill or running the procedure by hand.

This brief assumes you already have (or are about to write) a high-level brief for the new project. If you don't yet have one, do the methodology's steps 1–3 first ([`methodology.md`](methodology.md)) — turn the idea into insights, write a brief, decide an architecture.

---

## 1. What gets transferred

A project derived from this template contains the following **portable structure**. Names and paths are load-bearing — don't rename them.

```text
<new-repo>/
  README.md                # Didactic top-level for human readers
  CLAUDE.md                # Top-level agent guidance, briefs + policies catalogs,
                           #   invariants, glossary, conventions
  AGENTS.md                # Symlink → CLAUDE.md (for Codex/aider/OpenHands)
  LOG.md                   # Append-only activity log; /kickoff writes
                           #   START/END blocks here

  briefs/
    BRIEF.md               # Entry-point brief, project-specific
    methodology.md         # The eleven steps (copied verbatim)
    agentic-bootstrap.md   # This brief (copied verbatim, for the next bootstrap)
    <topic>.md             # Project-specific topic briefs as they appear

  policies/
    README.md
    briefs-and-policies.md
    cross-harness-parity.md
    four-canonical-agents.md
    phase-status.md
    acceptance-empirical.md
    log-discipline.md
    human-in-the-loop.md
    repo-relative-paths.md
    <project-specific>.md  # Add per-project as they appear

  plan/
    INDEX.md               # Phase graph + table + cross-cutting + critical files
    phase-1.md             # First phase (the rest grow as the project does)

  .claude/
    skills/
      kickoff/SKILL.md     # Phase orchestrator
      methodology/SKILL.md # Self-contained methodology reference
      learn/SKILL.md       # Universal cross-repo skill: absorb patterns into
                           #   THIS repo from another
      teach/SKILL.md       # Universal cross-repo skill: apply THIS repo's
                           #   patterns to another
      # /starter is NOT carried over — the new project doesn't need to stamp
      # out more projects from itself by default
    agents/
      phase-planner.md
      plan-reviewer.md
      phase-coder.md
      code-critic.md

  .codex/
    agents/
      phase-planner.toml
      plan-reviewer.toml
      phase-coder.toml
      code-critic.toml
    prompts/
      kickoff.md           # Symlink → ../../.claude/skills/kickoff/SKILL.md
      methodology.md
      learn.md
      teach.md

  .agents/                 # Codex CLI native skill discovery
                           # (developers.openai.com/codex/skills)
    skills/
      kickoff              # Directory symlink → ../../.claude/skills/kickoff
      methodology          # (Codex doesn't follow file-level symlinks inside
      learn                #  a skill dir — issue #11314 — but does traverse
      teach                #  a symlinked skill directory.)
      # /starter is NOT mirrored here either — starter-only

  project/                 # When project-isolation is enabled (default for
                           #   single-deliverable projects), the artifact lives
                           #   here, self-contained per
                           #   policies/project-isolation.md. Otherwise the
                           #   <language-skeleton> directories live at the
                           #   repo root as siblings.
    pyproject.toml         # (or package.json / Cargo.toml / go.mod)
    README.md              # concise, artifact-only
    <slug>/                # package directory
    tests/
```

**Status legend** used in `plan/INDEX.md` and nowhere else:

```text
⏳ Not Started    ⬅️ Next (only one)    🚧 In Progress    ✅ Completed
```

**The four canonical agents** — exact names matter; `/kickoff` invokes them by name:

| Role            | Tools allowed                                          | Writes code |
| --------------- | ------------------------------------------------------ | ----------- |
| `phase-planner` | Read, Grep, Glob, WebSearch, WebFetch                  | No          |
| `plan-reviewer` | Read, Grep, Glob, AskUserQuestion                      | No          |
| `phase-coder`   | Read, Write, Edit, Grep, Glob, Bash                    | Yes         |
| `code-critic`   | Read, Grep, Glob                                       | No          |

The `/kickoff` skill is itself **also** an agent in spirit, but it behaves as a slash-command-invoked workflow, not a subagent. It does no coding — it only orchestrates the four roles above and edits `plan/INDEX.md` + `LOG.md`.

---

## 2. What to transfer verbatim, what to rewrite, what to discard

The template's contents fall into three categories.

### 2a. Transfer essentially verbatim (universal)

These files encode the methodology itself, not any particular product. Copy them; replace any "Agentic Coding Starter Template" project-name references with the new project's name. Otherwise leave the structure intact.

- `.claude/skills/kickoff/SKILL.md`
- `.claude/skills/methodology/SKILL.md`
- `.claude/skills/learn/SKILL.md` (universal cross-repo skill)
- `.claude/skills/teach/SKILL.md` (universal cross-repo skill)
- `.claude/agents/phase-planner.md`
- `.claude/agents/plan-reviewer.md`
- `.claude/agents/phase-coder.md`
- `.claude/agents/code-critic.md`
- `.codex/agents/*.toml`
- `.codex/prompts/kickoff.md` (symlink → `../../.claude/skills/kickoff/SKILL.md`)
- `.codex/prompts/methodology.md` (symlink)
- `.codex/prompts/learn.md` (symlink)
- `.codex/prompts/teach.md` (symlink)
- `.agents/skills/kickoff` (directory symlink → `../../.claude/skills/kickoff`)
- `.agents/skills/methodology` (directory symlink → `../../.claude/skills/methodology`)
- `.agents/skills/learn` (directory symlink → `../../.claude/skills/learn`)
- `.agents/skills/teach` (directory symlink → `../../.claude/skills/teach`)
- `AGENTS.md` symlink → `CLAUDE.md`
- Every file under `policies/` (these are universal by design)
- `briefs/methodology.md`
- `briefs/agentic-bootstrap.md` (this file, so the next bootstrap is possible)
- The skeletal headings/structure of `plan/INDEX.md`
- The skeletal frontmatter shape for `plan/phase-*.md` (`id`, `title`, `depends_on`, `informs`)
- The START/END block format for `LOG.md`
- The status-marker convention (⏳ ⬅️ 🚧 ✅)

### 2b. Transfer the *shape*, rewrite the *content* (per-project)

These files have a stable shape and a project-specific body. Mirror the shape; write fresh content from the new project's brief.

- `README.md` — keep the section structure (what the project is, why, how to use, repository layout, status markers, four canonical agents, briefs-vs-policies-vs-plan, first-time setup), but every line is project-specific.
- `CLAUDE.md` — uses a two-zone structure delimited by HTML comment markers. The `Methodology Contract` zone (between `<!-- METHODOLOGY_CONTRACT_START -->` and `<!-- METHODOLOGY_CONTRACT_END -->`) is copied verbatim — methodology briefs catalog, policies catalog, universal repo layout, phase-work protocol, status markers, reading protocol, architectural invariants, activity-log contract, universal conventions, glossary. The `Project Context` zone (between `<!-- PROJECT_CONTEXT_START -->` and `<!-- PROJECT_CONTEXT_END -->`) is rewritten for the new project — the project's thesis, project-specific briefs list, project surfaces description, project conventions, and any project-specific skills.
- `briefs/BRIEF.md` — the entry-point brief for the new project. Pick a shape:
  - **Thesis-stub.** One short paragraph plus a pointer to `../CLAUDE.md#briefs-catalog`. Use when the project will quickly grow many topic briefs.
  - **Full single-document brief.** Opens with thesis + a catalog pointer, then continues with the long-form spec under H2 sections. Use when the project's brief is comprehensive and fits in one document.
  In both shapes the catalog itself lives in `CLAUDE.md`, not here.
- `briefs/<topic>.md` — written from the new project's spec, when the project is using the multi-file shape.
- `plan/INDEX.md` body — phase graph and table reflect the new project's phasing.
- `plan/phase-1.md` — fresh, project-specific. (Do not pre-build phases 2+. Decompose them when they become the next phase.)

### 2c. Do not transfer (template-specific)

- `.claude/skills/starter/SKILL.md` — the new project doesn't need to stamp out more projects from itself, unless it explicitly wants to be a template too. (Note: `/learn` and `/teach` *are* carried over — they are universal cross-repo skills, not starter-specific.)
- `.codex/prompts/starter.md` — same reason.
- `.agents/skills/starter` — same reason. The starter-only `/starter` skill is intentionally absent from Codex's native skill discovery in derived projects.
- The starter template's own `plan/phase-1.md` (which is a placeholder for "decide what you're building") — replace it entirely with the new project's real Phase 1.
- The starter template's `example/` Python package and `tests/test_cli.py` — replace with the new project's surface, in whatever language(s) the project uses.

If in doubt, ask: "does this file describe the methodology or a universally useful agentic capability, or does it describe the template itself?" Methodology and universal-capability files transfer; template-specific files don't.

---

## 3. The bootstrap procedure

The procedure assumes a directory has been named (or will be created) and a one-line description of the new project exists. If both are unavailable, ask the human before proceeding.

Bootstrap order matters: each step assumes the previous one's outputs.

### Step 1 — Confirm the project's identity and one-line thesis

Before touching files, write down (in conversation, not a file):

- **The canonical project name.** Camel-case, capitalization rules, ASCII symbol if different from the brand. Treat this as a placeholder until Step 2 vets it; failures send you back here to reconsider.
- **A one-sentence thesis.** "A daily palindromic-sentence word game"; "a recipe-first audio asset compiler"; "a small CLI that fetches the time from an NTP server."
- **The primary surfaces** the project will have (web front-end + back-end + IaC; pure Python CLI + library; mobile app + API; pure documentation; etc.).

These three pieces drive the rest of the bootstrap. Anchor them in `CLAUDE.md` first thing in Step 4.

### Step 2 — Brand-check the project name (when commercially relevant)

For personal projects, prototypes, or internal tools, skip to Step 3. For projects that may grow public, the name in the brief is a *placeholder* until this check passes.

Check, in this order:

1. **Domain availability.** `<name>.com` first; project-relevant TLDs second (`.io`, `.dev`, `.app`, plus one domain-relevant one such as `.audio` for an audio tool). For compound names, also check bare-noun and word-swap variants.
2. **Software-ecosystem collisions.** Search PyPI, npm, crates.io, GitHub (sort by stars), Homebrew, Linux distros, for the name and near-variants. A tool with the same name in an unrelated space is usually tolerable; a tool with the same name in an *adjacent* space is a hard collision.
3. **Trademark / commercial signals** (when commercial intent exists). USPTO TESS or EUIPO lookup. Skip for purely personal projects.
4. **In-context web search.** Query the name with adjacent-space keywords to surface social-media handles, blog properties, indie projects living below the bare-name search.

Pass criteria (all must hold): no active product or site in adjacent space; no popular GitHub repo using the same name; no package on the ecosystems your project will publish to; no trademark in adjacent space if commercial intent.

Failure protocol: stop. Propose 5–10 alternatives with collision summaries. Once the human picks, update the brief's title and any in-line references to the placeholder name before any file is committed under that name. Renaming pre-commit is cheap; renaming a working project is expensive.

### Step 3 — Initialize git and lay down the directory skeleton

`git init` first if the directory is not already a git repo. The methodology relies on `git status` and `git log` for several invariants (the orchestrator's "files touched" detection, blame-aware reads, the build-gate's surface inference); without a git repo those quietly fall back to broken behavior.

Then write `.gitignore` from a language-appropriate template plus the methodology's own entries:

```gitignore
# Agentic system runtime state
.claude/scheduled_tasks.lock
.claude/settings.local.json
.claude/projects/
.codex/cache/
```

Do not gitignore the `.claude/` or `.codex/` *directories* themselves — the skill and agent definitions are committed source. Only runtime state is ignored.

Then create the empty directory shape:

```text
.claude/skills/kickoff/
.claude/skills/methodology/
.claude/agents/
.codex/agents/
.codex/prompts/
.agents/skills/        # (the four skill entries here are directory symlinks
                       #  to ../../.claude/skills/<name>, created in Step 5)
briefs/
policies/
plan/
```

Plus directories for the project's primary language skeleton (e.g., `src/`, `tests/`, `web/`, etc.).

### Step 4 — Author the top-level files

In this exact order (each feeds the next):

1. **`briefs/BRIEF.md`** — the entry-point brief. Pick the thesis-stub or full-single-document shape from §2b. In both shapes, the catalog itself lives in `CLAUDE.md`, not here.

2. **`CLAUDE.md`** — top-level guidance. The template's `CLAUDE.md` ships with a two-zone structure. Bootstrap consists of:
   - Copying the template's `CLAUDE.md` as a whole, including the introductory paragraph that documents the two-zone contract.
   - Leaving the **Methodology Contract** zone (between `<!-- METHODOLOGY_CONTRACT_START -->` and `<!-- METHODOLOGY_CONTRACT_END -->`) verbatim. This contains: methodology briefs list, full policies catalog, universal repo layout, phase work + kickoff skill section, status markers, reading protocol, architectural invariants, activity log contract, universal conventions, glossary.
   - Rewriting the **Project Context** zone (between `<!-- PROJECT_CONTEXT_START -->` and `<!-- PROJECT_CONTEXT_END -->`) for the new project. The Project Context zone uses these sections:
     - `# Project Context` header
     - `## This Repo is <Project>` — canonical spelling, one-sentence thesis, pointer to `briefs/BRIEF.md`.
     - `## Project briefs` — `briefs/` entries specific to this project (initially `BRIEF.md` only).
     - `## Project surfaces` — the deliverable (location, language, seed code description).
     - `## Project conventions` — language, tooling, build-gate command shape.
     - `## Project-specific skills` — any beyond the universal four. Omit if none.

3. **`AGENTS.md`** — symlink to `CLAUDE.md`:
   ```bash
   ln -s CLAUDE.md AGENTS.md
   ```
   Codex and aider read `AGENTS.md`; Claude Code reads `CLAUDE.md`; the symlink keeps both honest from a single source.

4. **`LOG.md`** — create as a one-line stub:
   ```markdown
   # Activity Log
   ```
   `/kickoff` will append the first START block.

5. **`README.md`** — didactic top-level for human readers. Mirror the template's section structure; write project-specific content. The README is the human's entry point; CLAUDE.md is the agent's.

### Step 5 — Port the orchestrator, the four canonical agents, the methodology skill

Copy verbatim, then adapt project names and surface-specific build-gate commands:

- `.claude/skills/kickoff/SKILL.md`
- `.claude/skills/methodology/SKILL.md`
- `.claude/skills/learn/SKILL.md`
- `.claude/skills/teach/SKILL.md`
- `.claude/agents/phase-planner.md`
- `.claude/agents/plan-reviewer.md`
- `.claude/agents/phase-coder.md`
- `.claude/agents/code-critic.md`
- `.codex/agents/*.toml`
- `.codex/prompts/{kickoff,methodology,learn,teach}.md` (file symlinks → `../../.claude/skills/<name>/SKILL.md`)
- `.agents/skills/{kickoff,methodology,learn,teach}` (directory symlinks → `../../.claude/skills/<name>`)

Adaptations to make in each:

- Replace `Agentic Coding Starter Template` (and any short-name like `Starter`) with the new project name throughout.
- Replace the template's example surface paths (`example/`, `tests/`) in build-gate command lists with the new project's surfaces. The template's polyglot pattern (lint command + format command + test command) is a template — keep the surfaces that apply, drop the rest, add new ones (e.g., a Rust package, a TypeScript front-end, IaC) as the project requires.
- Replace template-specific brief references with the new project's analogues, or remove them if no analogue exists.
- Keep the **structural elements verbatim**: step numbering, agent invocation order, status-marker semantics, verdict headers (`## Verdict: APPROVED` / `## Verdict: REVISE`), output schemas. These are the contract between the four roles; changing them silently breaks orchestration.

### Step 6 — Port every file under `policies/`

Policies are universal by design. Copy them verbatim; replace any `Agentic Coding Starter Template` references with the new project name. Add new policy files only when the new project genuinely needs a rule the template doesn't have.

### Step 7 — Stand up `plan/INDEX.md`

The spine. Lay it down before any phase files exist:

- `# Phased Execution Plan — <Project>` heading.
- One-paragraph statement of what `plan/` covers and what it doesn't.
- `## Reading protocol` — copy from template, lightly adapted.
- `## Phase Dependency Graph` — a Mermaid `graph TD` block. At bootstrap, this contains a single Phase 1 node. It grows as phases are decomposed.
- `## Phase Table` — the canonical status ledger. Columns: `Phase | Title | Status`. Initially:

  ```markdown
  | [Phase 1](phase-1.md) | <First-phase title> | ⬅️ |
  ```

  Status markers live only here.
- `## Cross-Cutting Concerns` — the project's invariants, mirrored from `CLAUDE.md`'s "Architectural invariants" section. Keep the two lists in sync.
- `## Critical-Files Map` — table of "concern → location." Initially sparse; populated as the project takes shape.

### Step 8 — Write Phase 1 (and only Phase 1)

Resist planning everything up front. The template ships a placeholder Phase 1 because *it* doesn't know what the user's project is yet; a derived project replaces that placeholder with a real first phase.

`plan/phase-1.md` frontmatter:

```yaml
---
id: "1"
title: "<First-phase title>"
depends_on: []
informs: []        # filled in as later phases are added
---
```

Body sections, in order:

- **Goal** — one paragraph. What the user can do or observe at the end of Phase 1 that they cannot do now.
- **Decomposition** — the sub-phases this parent will break into. At bootstrap you may not know all of them; list the ones you do, and note that more will be added.
- **Phase-level acceptance** — concrete, empirical, observable.
- **Brief refs** — links to every brief under `briefs/` that this phase implements.

Sub-phase files (`plan/phase-1.1.md`, etc.) follow the same frontmatter shape with `id: "1.1"` and `depends_on: ["1"]` (or sibling sub-phases). Bodies: Goal / Deliverables / Acceptance / Brief refs.

**Do not** create `phase-2.md` and beyond at bootstrap. Methodology step 11 is "stay agile"; phases get added once Phase 1's reality informs their shape.

### Step 9 — Lay down the project's primary code surface

The template's example is Python. The new project may be Python, TypeScript, Rust, Go, Swift, Kotlin, a polyglot, or pure documentation.

**Decide first whether to adopt the `project/` convention** ([`../policies/project-isolation.md`](../policies/project-isolation.md)). The default for a single-deliverable project is opt-in: the artifact goes under `project/` and the build gates run as `cd project && <commands>`. The default for polyglot or multi-deliverable repos is opt-out: deliverable directories live at the repo root as siblings.

Lay down (paths assume `project_isolation` enabled — prefix with `project/`; drop the prefix when disabled):

- The package-manager file (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.) with pinned tooling and minimum dependencies.
- A concise `README.md` for the artifact (self-contained, no `..` references).
- The package directory with empty modules.
- The test directory with one trivial test that passes (so the build gate has something to run on first kickoff).
- A `.gitignore` clause at the repo root for the language's build artifacts.

Build gates the orchestrator should run are whatever the language ecosystem provides: lint (e.g., `ruff check` / `eslint` / `cargo clippy`), format check (e.g., `ruff format --check` / `prettier --check` / `cargo fmt --check`), test (e.g., `pytest -q` / `npm test` / `cargo test`).

Adapt the `kickoff` skill's "Final build gate" section to call these commands for the surfaces this project actually has. Use the `cd project && <cmd>` shape when `project_isolation` is enabled.

### Step 10 — Sanity-check the bootstrap

Before declaring the bootstrap complete, verify:

- `readlink AGENTS.md` returns `CLAUDE.md`.
- `grep -E '^\| \[Phase ' plan/INDEX.md` returns at least one row, exactly one of which is `⬅️`.
- `head -1 LOG.md` is `# Activity Log`.
- `ls .claude/agents/` lists exactly the four canonical role files.
- `ls .claude/skills/kickoff/` contains `SKILL.md`.
- `ls .claude/skills/methodology/` contains `SKILL.md`.
- The new `CLAUDE.md`'s "Briefs catalog" section lists every file in `briefs/`, and every file in `briefs/` is referenced from the catalog (no orphans either way).
- The new `CLAUDE.md`'s "Policies catalog" section lists every file in `policies/`, and every file in `policies/` is referenced from the catalog (no orphans either way).
- `plan/phase-1.md`'s `Brief refs` section lists at least one brief, and each listed brief exists.
- The project's primary build gate runs clean on the trivial seeded code (e.g., `pytest -q` exits 0 with at least one passing test).

The first `/kickoff` invocation should pick up Phase 1's `⬅️` row, flip it to `🚧`, and append a START block to `LOG.md`. If any of those three actions fails, the bootstrap is incomplete — a path mismatch or a missing skill is the typical culprit.

---

## 4. Per-project adaptation axes

The bootstrap is the same shape every time. The variation is in:

| Axis                          | Examples of project-specific choices                          |
| ----------------------------- | ------------------------------------------------------------- |
| **Surfaces**                  | web + back-end + IaC; pure Python lib; mobile + API; docs     |
| **Build gate commands**       | `pytest`, `npm test`, `cargo test`, `go test`, etc.           |
| **Languages in play**         | Python / TS / Rust / Go / Swift / Kotlin / polyglot           |
| **Deployment story**          | AWS / Cloudflare / Vercel / app stores / static / none        |
| **Per-project invariants**    | Cost ceilings; license policy; privacy boundaries; FOSS-only  |
| **Per-project skills**        | Domain-specific workflows on top of `/kickoff`                |

When adapting, edit these files (and only these) to reflect those choices:

- `CLAUDE.md` — reflects all of them.
- `plan/INDEX.md` Cross-Cutting Concerns — duplicates the invariants from `CLAUDE.md`.
- `.claude/skills/kickoff/SKILL.md` Final build gate section — the surface → command mapping.
- `.claude/agents/phase-planner.md` and `phase-coder.md` — the surface list and build-gate templates inside.

Anything else that needs to change probably indicates a bootstrap deviation that should be questioned, not normalized.

---

## 5. Common pitfalls

These bite every bootstrap; flag them before they happen.

- **Status markers in two places.** The status of a phase lives in `plan/INDEX.md`'s phase table and **nowhere else**. Per-phase frontmatter is `id / title / depends_on / informs` — no `status` field.
- **Catalog drift.** `CLAUDE.md`'s "Briefs catalog" and "Policies catalog" must list every file in their respective directories, and every file in those directories must be listed. Orphans on either side cause agents to read past the file or miss it entirely.
- **`AGENTS.md` as a real file instead of a symlink.** A duplicate file drifts. Make it a symlink and verify with `readlink`.
- **Reusing template-specific invariants.** "The example Python project must lint clean" is a template rule. Don't carry it into a project that has no Python.
- **Filling in Phase 2+ at bootstrap.** Tempting and wrong. Phase 1 reality is the input to Phase 2's design.
- **Agent name drift.** The four canonical roles must be named exactly `phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`. `/kickoff` invokes them by name. A typo silently breaks the orchestrator's ability to delegate.
- **Editing `LOG.md` by hand.** History is owned by `/kickoff`. If a phase pauses mid-way, `/kickoff` writes the pause-reason END block; do not retroactively edit prior entries.
- **Skipping the brief.** The bootstrap assumes a brief exists. Bootstrapping into an empty `briefs/` produces scaffolding for a project nobody has decided yet — the orchestrator will plan against air.

---

## 6. Acceptance — "the new repo is ready to `/kickoff`"

Bootstrap is complete when **all** of the following hold:

```text
[ ] Project name confirmed; brand check passed (if commercially relevant)
[ ] `git rev-parse --is-inside-work-tree` returns true
[ ] `.gitignore` exists with language-appropriate entries plus the agentic
    runtime-state ignores
[ ] briefs/BRIEF.md exists in one of the two valid shapes (thesis-stub or
    full-spec-with-thesis-preamble) and references the catalog in CLAUDE.md
[ ] CLAUDE.md exists with all required sections (§3.4 above)
[ ] AGENTS.md is a symlink to CLAUDE.md
[ ] LOG.md exists and contains only `# Activity Log` and the contract paragraph
[ ] plan/INDEX.md exists with: graph block, status legend, phase table
    containing exactly one row whose status is ⬅️, cross-cutting concerns
    (mirroring CLAUDE.md), critical-files map
[ ] plan/phase-1.md exists, with frontmatter (id "1", depends_on []),
    Goal / Decomposition / Acceptance / Brief refs sections
[ ] All known plan/phase-1.<M>.md sub-phases of the current major phase exist
    (per methodology step 6: "Sub-phase breakdown at phase start"). Future
    major phases (2+) are NOT decomposed yet.
[ ] .claude/skills/kickoff/SKILL.md exists, adapted for this project's
    surfaces and build gates
[ ] .claude/skills/methodology/SKILL.md exists (verbatim from template)
[ ] .claude/skills/learn/SKILL.md exists (verbatim from template)
[ ] .claude/skills/teach/SKILL.md exists (verbatim from template)
[ ] .claude/skills/starter/ does NOT exist (starter-only meta-skill)
[ ] .claude/agents/{phase-planner,plan-reviewer,phase-coder,code-critic}.md
    exist, adapted for this project
[ ] .codex/agents/*.toml mirrors exist
[ ] .codex/prompts/{kickoff,methodology,learn,teach}.md exist (file symlinks)
[ ] .agents/skills/{kickoff,methodology,learn,teach} exist as directory
    symlinks to ../../.claude/skills/<name> (the canonical skill directory)
[ ] .agents/skills/starter does NOT exist (starter-only, must not propagate)
[ ] Every file in policies/ from the template exists, with project-name
    references updated
[ ] No template-specific skills, briefs, or example code remain in the new
    repo (no example/, no .claude/skills/starter/)
[ ] The project's primary build gate runs clean on the seeded code
[ ] First `/kickoff` invocation successfully picks up Phase 1's ⬅️ row,
    flips it to 🚧, and appends a START block to LOG.md
```

The last item is the operational test. Until it passes, the bootstrap is not done.

---

## 7. Pointers

- **The template (this repo) is itself the canonical donor.** Future versions of the bootstrap procedure should be updated *in the template first*, then propagated to derived projects' copies of `agentic-bootstrap.md` on next opportunity.
- **The methodology** is documented in [`methodology.md`](methodology.md) (sibling brief, copied verbatim into every derived project).
- **The cross-harness contract** is in [`../policies/cross-harness-parity.md`](../policies/cross-harness-parity.md). Adding a third or fourth harness is governed by that policy.
