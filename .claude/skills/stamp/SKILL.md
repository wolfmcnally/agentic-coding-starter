---
name: stamp
description: >-
  Stamp out a new project at <directory>, using this repository as the
  master template. Asks a small number of configuration questions only when
  the optional <description> doesn't make the answers obvious. Adapts
  CLAUDE.md, README.md, briefs/BRIEF.md, the atomic setup/test/check
  toolchain contract, the kickoff skill, and the four canonical agents for
  the new project's name and primary language. Invoke as /stamp <directory>
  [<description>] in Claude Code or $stamp <directory> [<description>] in Codex.
argument-hint: "<directory> [<description>]"
last-reviewed: 2026-08-25
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
   - Each universal skill in `{kickoff, methodology, learn, teach, roles, sweep, demo, treatise, plain}` has a `.claude/skills/<name>/SKILL.md`.
   - `.claude/settings.json` exists and sets `worktree.bgIsolation` to `none`.
   - `bin/kickoff-config` exists and is executable.
   - `bin/kickoff-tree-id` and `bin/kickoff-evidence` exist and are executable.
   - `bin/setup`, `bin/test`, `bin/check`, and `bin/check-receipt` exist and are
     executable; `tests/test_check_receipt.py` exists; the Python profile also
     has executable `bin/python`.
   - `kickoff.yaml` exists and `./bin/kickoff-config show` validates role models, role timeouts, and research budgets.
   - `.codex/agents/*.toml` has one TOML file per canonical agent.
   - `briefs/BRIEF.md`, `briefs/methodology.md`,
     `briefs/agentic-bootstrap.md`, and
     `briefs/incremental-orchestration.md` exist.
   - `plan/INDEX.md` and `plan/phase-1.md` exist.
   - Every file under `policies/` is non-empty.
   If any check fails, refuse with a specific error naming the missing file and exit.

2. **Destination directory.** Expand `~` and resolve to an absolute path. Then:
   - If the path does not exist, `mkdir -p` it (with the user's tacit consent — they named the directory).
   - If the path exists and is empty, proceed.
   - If the path exists and holds nothing but a **seed brief** (defined below), adopt it and proceed.
   - Otherwise refuse with: `Refusing to bootstrap into a non-empty directory: <path>`, naming the specific entries that disqualified it so the user can move them aside and retry.

3. **Parent directory writable.** Check the parent of the destination is writable. If not, refuse.

## Seed briefs — stamping onto a brief the user already wrote

The best input to a bootstrap is a real brief. Writing one first and then stamping
onto it is the intended workflow, not an edge case: [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md)
opens by assuming a brief exists, and Step 3's phase sketches are only as good as
the brief they enumerate. A one-line description yields one phase; a real brief
yields the project's actual shape.

**What counts as a seed.** The destination may contain, and *only* contain:

- `.git/` — the user initialized a repository first.
- `briefs/`, containing only `.md` files.
- `.md` files at the top level.
- `.gitignore`.

Anything else — a source directory, a `package.json`, a stray archive, a nested
project — disqualifies the destination. Refuse and name what tripped it. This
strictness is deliberate: the stamp writes a whole repository into that path, and
a destination holding unrelated work is a destination the user did not mean.

**Adopting the seed.**

1. **Place the briefs.** Top-level `.md` files move into `briefs/`, except
   `README.md`, which stays where it is and is **not** overwritten by Step 3 —
   the user wrote it, so keep it and adapt around it. Report every move. **When
   `.git/` is part of the seed, move with `git mv`**, or stage the rename
   immediately: a plain `mv` leaves the old path in the index, and
   `bin/check-catalogs` reads tracked paths, so it then reports a broken link to
   a file that no longer exists — a failure whose message points at the brief
   rather than at the move that caused it.
2. **Pick the entry point.** `briefs/BRIEF.md` if it exists; otherwise, if
   exactly one brief is present, that file is the entry point and keeps its own
   name — never rename a file the user wrote. If several briefs are present and
   none is `BRIEF.md`, ask which is the entry point.
3. **Repair frontmatter, never the body.** A hand-written brief usually lacks the
   `title` / `date` / `status` / `scope` frontmatter [`policies/briefs.md`](../../../policies/briefs.md)
   requires. Add what is missing, deriving `title` from the H1 and `date` from
   today. Do not touch a single byte below the frontmatter: the brief is the
   user's contract, and the stamp is not authorized to edit it.
4. **Read the configuration out of the brief.** It answers the questions in
   *Gather configuration* far better than a one-line description can —
   `project_name`, `description`, `primary_language`, `surfaces`, and
   `dependencies` are usually all stated or clearly implied. Ask the user only
   what the brief genuinely leaves open.
5. **Let an explicit `<description>` argument win.** If the argument and the
   brief disagree, the argument is the more recent statement of intent — use it,
   and say plainly in the report which brief statement it overrode, so the user
   can correct whichever one is wrong.
6. **Enumerate the real phases.** Draft `plan/phase-1.md` in full and a sketch for
   every major phase the brief surfaces, per Step 3. This is the payoff for
   seeding a brief; do not fall back to a single placeholder phase when the brief
   plainly describes more.

**Where the adopted brief changes later steps.** Step 3 does not author
`briefs/BRIEF.md` over an adopted entry-point brief, and does not overwrite an
adopted `README.md`. Step 6 skips `git init` when `.git/` already exists. Step 7
verifies that every adopted brief's body is byte-identical to what the user
wrote.

## Gather configuration

The skill needs a small set of facts to customize the new project. When a seed brief was adopted, read them out of the brief first and ask only about what it leaves open:

| Key | Purpose | Default behavior when unspecified |
|---|---|---|
| `project_name` | Brand name; appears in README, CLAUDE.md, BRIEF.md | Derive from the final path segment (camel-case it: `my-tool` → `MyTool`) |
| `project_slug` | Lowercase-kebab; appears in package names, directory names | The final path segment |
| `description` | One-line thesis | The `<description>` argument, or "(to be written)" |
| `primary_language` | Drives the deliverable's code skeleton and build gate commands | Inferred from description heuristics; defaults to `python` |
| `surfaces` | List of repo surfaces: `cli`, `library`, `web`, `service`, `desktop`, `tui` | Inferred; defaults to `[cli]` |
| `dependencies` | Runtime and dev packages the brief or description names explicitly | None beyond the language profile's own minimum |
| `project_isolation` | Whether to adopt the `project/` subdirectory convention per [`policies/project-isolation.md`](../../../policies/project-isolation.md) | Default *opt-in* for single-deliverable projects (`cli`, `library`, `service`, `book`); default *opt-out* for polyglot or multi-deliverable repos (`surfaces` length > 1 with siblings like `web`+`service`) |

**Inference heuristics** (apply only when `<description>` is informative):

- Description mentions "CLI", "command-line", "terminal tool" → `surfaces: [cli]`.
- Description mentions "web app", "frontend", "React", "Vue", "single-page", "PWA" → `surfaces: [web]`, `primary_language: typescript`.
- Description mentions "game", "canvas", "Canvas2D", "WebGL", "sprite", "game loop", "browser app" → `surfaces: [web]`. A browser-delivered game is a `web` surface: it needs a host page, a bundler, and a dev server, none of which a library or CLI skeleton provides.
- Description mentions "desktop app", "Electron", "Tauri", "menu bar app", "macOS app", "Windows app" → `surfaces: [desktop]`.
- Description mentions "TUI", "terminal UI", "full-screen terminal", "ncurses", "ratatui", "textual" → `surfaces: [tui]`. A TUI still ships as a terminal binary, so it uses the `cli` layout with a screen-driving dependency and a headless-safe test.
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

**Named dependencies are part of the declared architecture.** When the brief or
the description names a package — a rendering library, a validation library, a
test runner, a specific framework — it goes into the destination's manifest and
lockfile at stamp time, pinned by the language's normal mechanism, even when the
seed code does not import it yet. The brief is the contract; a dependency it
names is a decision already made, and discovering at Phase 1 that the stamp
silently dropped it is worse than a manifest entry that waits one phase for its
first call site. **Do not invent dependencies nobody named** — a stamp that
guesses a framework has made an architectural decision that was not its to make.
Surface every dependency you recorded in the final report so the user can strike
any that were misread.

**Do not** ask configuration questions when the description is straightforward. "Build a Rust CLI that prints the current weather" needs no further questions — `project_name` from directory, `primary_language: rust`, `surfaces: [cli]`, done. "A TypeScript Canvas2D game" needs none either — `primary_language: typescript`, `surfaces: [web]`, and the browser-app skeleton in Step 4.

## Bootstrap procedure

Follow [`briefs/agentic-bootstrap.md` §3](../../../briefs/agentic-bootstrap.md) step by step. The condensed procedure:

### Step 1 — Lay down the directory skeleton

`mkdir -p` under the destination:

```
<dest>/
  briefs/
  policies/
  plan/
  bin/
  lib/
  tests/
  reports/
  .githooks/
  .claude/skills/kickoff/
  .claude/skills/methodology/
  .claude/skills/learn/
  .claude/skills/teach/
  .claude/skills/roles/
  .claude/skills/sweep/
  .claude/skills/demo/
  .claude/skills/treatise/
  .claude/skills/plain/
  .claude/agents/
  .codex/agents/
  .agents/skills/         # (kickoff, methodology, learn, teach, roles, sweep,
                          #  demo, treatise, plain
                          #  added as directory symlinks in Step 2)
  lessons/                # (empty ledger — .gitkeep only; policies/lessons.md)
  lessons-archived/       # (empty — .gitkeep only)
  user-actions/           # (empty — .gitkeep only; policies/user-actions.md)
  user-actions-archived/  # (empty — .gitkeep only)
```

All four ledger directories get a `.gitkeep`; an empty directory does not survive
`git add`, and a ledger that vanishes at the first commit is a ledger the next
session will not find.

Plus the language-specific deliverable directories. When `project_isolation` is enabled (the default for single-deliverable projects), the deliverable goes under `project/`:

- Python: `project/<slug>/`, `project/tests/`
- TypeScript: `project/src/`, `project/tests/`
- Rust: `project/src/`, `project/tests/`
- Go: `project/cmd/<slug>/`, `project/internal/`
- Other: appropriate convention, all under `project/`

When `project_isolation` is disabled (polyglot or multi-deliverable repos), the deliverable directories live at the repo root as siblings, with no `project/` wrapper:

- Polyglot example: `web/`, `lambda/<svc>/`, `cdk/`, etc. as top-level siblings.

### Step 2 — Copy verbatim, adapt names

**The copy rule is a denylist, not an allowlist.** Copy *everything* under the
universal surfaces below into the new project, leave behind only the starter-only
entries named in the table, then run a name substitution pass (replacing
`Agentic Coding Starter Template`, `agentic-coding-starter-template`, and
`starter` with `<project_name>`, `<project_slug>`, and a project-appropriate
handle).

The direction matters. An allowlist of files to copy goes stale silently: every
universal script, skill, or test added to the template after the list was written
is invisible to it, and the omission surfaces downstream as a stamped project
whose own gate refuses to start — `bin/check` fails closed on the first missing
executable. A denylist fails the other way: a forgotten entry copies one harmless
extra file, which the adaptation pass or the next `sweep` catches.

**Universal surfaces — copy the whole directory:**

- `.claude/skills/` — every skill directory, each with its `SKILL.md`
- `.claude/agents/` and `.codex/agents/` — the four canonical roles and their mirrors
- `.claude/settings.json`
- `policies/`
- `briefs/`
- `bin/`, including `bin/README.md` and its convention preamble
- `lib/` — the shared deterministic library the universal `bin/` scripts import
- `tests/`, including `tests/fixtures/`
- `reports/execution/`, including its vendored `assets/`
- `.githooks/`
- `.gitignore`, `.gitattributes`, `kickoff.yaml`

**Starter-only — leave behind:**

| Entry | Why it does not propagate |
|---|---|
| `.claude/skills/stamp/` and `.agents/skills/stamp` | this skill itself; a derived project stamps out more projects only if it deliberately becomes a template too |
| `policies/anonymize-log-references.md` | starter-only: the rule exists because *this* template is public, not because of any methodology principle |
| `bin/check-anonymization.sh` and `bin/anonymization-denylist.local.example` | that policy's enforcement (also drop the `bin/anonymization-denylist.local` line from the copied `.gitignore`) |
| `tests/test_methodology_toolchain_contract.py` | asserts on `stamp` and the anonymization policy, neither of which the destination has |
| `briefs/BRIEF.md`, `briefs/eacp-pattern-map.md`, `briefs/methodology-treatise.md` | about *this* repository; `BRIEF.md` is authored fresh in Step 3 |
| `LICENSE` and `.vscode/` | the operator's choices, not the template's |
| `plan/`, `LOG.md`, `README.md`, `CLAUDE.md`, `project/` | authored or adapted fresh in Steps 3–5 |
| the *contents* of `lessons/`, `lessons-archived/`, `user-actions/`, `user-actions-archived/` | every ledger starts **empty** — a `.gitkeep` in each of the four, never Starter's own entries |

Everything else under those surfaces is universal by construction. When in doubt,
copy it: an extra file downstream is a nuisance, a missing one is a broken gate.

**Load-bearing members — a floor, not a ceiling.** The denylist above is the
authority for what to copy; this list names members whose absence is known to
break the destination, so a copy that omits any of them is wrong regardless of how
the copy was performed. It is not exhaustive and does not need to be.

- Every universal skill: `.claude/skills/kickoff/SKILL.md`,
  `.claude/skills/methodology/SKILL.md`, `.claude/skills/learn/SKILL.md`,
  `.claude/skills/teach/SKILL.md`, `.claude/skills/roles/SKILL.md`,
  `.claude/skills/sweep/SKILL.md`, `.claude/skills/demo/SKILL.md`,
  `.claude/skills/treatise/SKILL.md`, `.claude/skills/plain/SKILL.md`
- `.claude/settings.json` (an explicitly requested worktree stays available; only
  implicit background worktree isolation is disabled)
- The four canonical agents and their Codex mirrors:
  `.claude/agents/phase-planner.md`, `.claude/agents/plan-reviewer.md`,
  `.claude/agents/phase-coder.md`, `.claude/agents/code-critic.md`;
  `.codex/agents/phase-planner.toml`, `.codex/agents/plan-reviewer.toml`,
  `.codex/agents/phase-coder.toml`, `.codex/agents/code-critic.toml`
- Every file under `policies/` except the starter-only entry above
- `briefs/methodology.md` (methodology is universal),
  `briefs/agentic-bootstrap.md` (so the next bootstrap from this project is
  possible), `briefs/cross-agent-invocation.md` (the cross-CLI invocation BCPs
  that `policies/role-models.md` cites),
  `briefs/incremental-orchestration.md` (candidate-bound review, revision,
  verification, and protocol-recovery design),
  `briefs/deterministic-orchestration.md` (draft: decision criteria for a
  deterministic kickoff loop once every supported harness has a parity workflow
  primitive), `briefs/harness-self-improvement.md` (the two-tier improvement
  flywheel the lessons ledger, `sweep`, and the transfer skills implement), and
  `briefs/session-context-compaction.md` (managing harness compaction during long
  orchestration runs)
- `.githooks/pre-push` (optional hook; it reuses only an exact verified full-gate
  receipt and otherwise delegates to the canonical gate; inert until explicitly
  installed)
- The toolchain entry points `bin/setup`, `bin/test`, `bin/check`, and
  `bin/check-receipt` (adapted together in Step 5), plus `bin/install-hooks` and
  `bin/check-hooks-installed` (verbatim)
- `bin/_python-toolchain` and `bin/python` for a Python target (adapted in Step 5;
  omit both when Python is not a deliverable runtime)
- The universal managers and checkers, all of which `bin/check` requires present
  before it will run a single gate: `bin/kickoff-config`, `bin/kickoff-tree-id`,
  `bin/kickoff-evidence`, `bin/check-receipt`, `bin/execution-telemetry`,
  `bin/check-execution-dashboards`, `bin/check-harness-parity`,
  `bin/check-toolchain-callers`, `bin/lessons`, `bin/treatise`,
  `bin/check-catalogs`, `bin/check-hooks-installed`, `bin/check-shell-syntax`,
  `bin/new-name`; plus the operator convenience `bin/serve-execution-dashboard`
- `lib/agentic_starter/` — `bin/execution-telemetry` and
  `bin/check-execution-dashboards` import it; without it both fail at startup and
  take the whole gate with them
- `reports/execution/` with `index.html`, `index-data.js`, and `assets/` —
  `bin/check-execution-dashboards` reads the archive and validates the vendored
  offline renderer. A fresh destination's archive holds zero phases, which the
  checker reports as `EXECUTION DASHBOARDS PASS (0 phases)`
- `tests/test_toolchain_entrypoints.py` and `tests/test_check.py` (adapted with
  the toolchain in Step 5), plus verbatim `tests/test_check_receipt.py`,
  `tests/test_install_hooks.py`, `tests/test_check_hooks_installed.py`,
  `tests/test_kickoff_config.py`, `tests/test_kickoff_tree_id.py`,
  `tests/test_kickoff_evidence.py`, `tests/test_lessons.py`,
  `tests/test_check_catalogs.py`, `tests/test_treatise.py`,
  `tests/test_new_name.py`, `tests/test_shell_syntax.py`,
  `tests/test_toolchain_callers.py`, `tests/test_mirror_parity.py`,
  `tests/test_research_authority.py`, `tests/test_execution_telemetry.py`,
  `tests/test_execution_dashboard.py`,
  `tests/render_execution_dashboard_fixture.py`, and `tests/fixtures/`
- `.gitattributes` — the line-ending normalization that keeps cross-harness
  mirrors byte-identical across platforms

The candidate-identity and orchestration-evidence contract
(`bin/kickoff-tree-id`, `bin/kickoff-evidence`, `tests/test_kickoff_tree_id.py`,
`tests/test_kickoff_evidence.py`, governed by
`policies/orchestration-evidence.md` and designed in
`briefs/incremental-orchestration.md`) is atomic: transfer every member or none.
So is the self-improvement bundle (`.claude/skills/sweep/SKILL.md`,
`briefs/harness-self-improvement.md`, `policies/lessons.md`, `bin/lessons`,
`bin/check-catalogs`, `tests/test_lessons.py`, `tests/test_check_catalogs.py`,
and the empty `lessons/` + `lessons-archived` ledger).

The denylist, this floor, the manual bootstrap brief, `teach`'s atomic transfer
list, acceptance checklists, role contracts, and methodology narrative are one
propagation boundary. Whenever the universal bundle grows, reconcile every member
in the same change; a current executable path does not excuse a stale manual path.

Then create the `.agents/skills/` **directory symlinks** for Codex CLI's native skill discovery. Each is a relative symlink whose target is the canonical skill *directory* (not the SKILL.md file inside it — Codex doesn't follow file-level symlinks inside a skill dir per [openai/codex#11314](https://github.com/openai/codex/issues/11314), but does traverse a symlinked skill directory):

```
cd <dest>
mkdir -p .agents/skills
ln -s ../../.claude/skills/kickoff     .agents/skills/kickoff
ln -s ../../.claude/skills/methodology .agents/skills/methodology
ln -s ../../.claude/skills/learn       .agents/skills/learn
ln -s ../../.claude/skills/teach       .agents/skills/teach
ln -s ../../.claude/skills/roles       .agents/skills/roles
ln -s ../../.claude/skills/sweep       .agents/skills/sweep
ln -s ../../.claude/skills/demo        .agents/skills/demo
ln -s ../../.claude/skills/treatise    .agents/skills/treatise
ln -s ../../.claude/skills/plain       .agents/skills/plain
```

There is one mirror per canonical skill directory, and `bin/check-harness-parity`
fails closed on a missing mirror, an orphan mirror, or a wrong target — so a skill
copied without its symlink breaks the destination's gate just as surely as a skill
never copied at all.

Verify each `readlink <dest>/.agents/skills/<name>` returns the expected target and `test -L <dest>/.agents/skills/<name> && test -d <dest>/.agents/skills/<name>` passes before moving on.

The nine universal skills are all carried over, including cross-repo `learn` and
`teach`, interactive `demo`, publication-gated `treatise`, and the operator
register `plain`.

Seed both config sections by running `<dest>/bin/kickoff-config reset all`; this
preserves data under `extensions` if the destination already has it. The managers
run via `uv`, so the destination needs `uv` on PATH, and `kickoff-config` declares
its PEP 723 `ruamel.yaml` dependency. Keep every universal script entry in
`bin/README.md`; delete the starter-specific anonymization section **and every
other reference to it in that file** — the section heading, the usage block, and
the trailing paragraph that links `policies/anonymize-log-references.md` are
separate hits, and leaving the last one produces a broken link that
`bin/check-catalogs` fails on. Remove the anonymization call from the copied
`bin/check` as well.

Because the anonymization policy and its script are starter-only but `code-critic.md` is copied verbatim (above), the adaptation pass must **delete the "External / private-repo references" bullet** from the destination's `.claude/agents/code-critic.md` — it references `bin/check-anonymization.sh` and `policies/anonymize-log-references.md`, neither of which the new project will have.


### Step 3 — Write the project-specific files

Author these afresh, using the gathered configuration:

- **`<dest>/README.md`** — didactic top-level for human readers. Mirror the template's section structure (what this is, why, how to use, repository layout, status markers, four canonical agents, briefs-vs-policies-vs-plan, first-time setup). Every line is `<project_name>`-specific. **If the seed carried a `README.md`, keep it**: append the repository-layout and getting-started sections beneath what the user wrote rather than replacing their words.

- **`<dest>/CLAUDE.md`** — top-level agent guidance. The template's `CLAUDE.md` has two clearly-marked zones (HTML comments delimit them), plus a **Hard rules** section above both. The job:
  - **Copy the file as a whole.**
  - **Above both zones — the Hard rules section**: delete **Hard rule 3**, the starter-only anonymization rule. Its own text says it does not propagate, and it links `policies/anonymize-log-references.md`, which the destination will not have — a link `bin/check-catalogs` will report as a missing target. Then repair the sentence that introduces the rules: "Rules 1 and 2 are universal … Rule 3 is **starter-only** …" becomes a statement that both remaining rules are universal. Leave rules 1 and 2, and the restriction/waiver paragraph beneath them, untouched.
  - **Inside the `<!-- METHODOLOGY_CONTRACT_START --> ... <!-- METHODOLOGY_CONTRACT_END -->` markers**: verbatim *except* for the starter-only members it names. This is the universal methodology content and every derived project gets the same text, but the zone also carries the catalog of what exists in *this* repo, and two of those entries do not travel:
    - Delete the `anonymize-log-references.md` bullet from the **Policies catalog**. Left in place, it is a `CLAUDE.md` reference to a file the destination does not have, and `bin/check-catalogs` fails closed on it.
    - Drop the trailing `check-anonymization.sh` clause from the `bin/` bullet in **Universal repo layout**, and repair the sentence so it still reads as one list.
    - Nothing else in the zone changes. If a future starter-only surface is added to the template, it gets an entry in Step 2's denylist *and* a line here.
  - **Inside the `<!-- PROJECT_CONTEXT_START --> ... <!-- PROJECT_CONTEXT_END -->` markers**: rewrite from scratch for the new project. Sections to author:
    - `# Project Context` header (unchanged).
    - `## This Repo is <project_name>` — canonical spelling, one-sentence thesis (from `description`), pointer to `briefs/BRIEF.md`.
    - `## Project briefs` — list of `briefs/*.md` files specific to this project (initially just `BRIEF.md`).
    - `## Project surfaces` — describe the deliverable (path, what language, what the example or seed code is). When `project_isolation` is on, the surface is `project/`; when off, name the sibling deliverable directories.
    - `## Project conventions` — language, tooling, build-gate command shape for this project.
    - `## Model & review venue` — describe `kickoff.yaml` as the human-editable source for separate model/effort fields and execution budgets; `roles` is an optional validated editor; the shipped default gives cross-vendor review. Governed by the two role policies.
    - `## Project-specific skills` — if the new project carries any skills beyond the universal nine (kickoff, methodology, learn, teach, roles, sweep, demo, treatise, plain), list them here. For most fresh projects, this section is empty (or omitted).
  - Preserve the introductory paragraph that explains the two-zone contract; it is informational and lives outside both markers. Adjust only its `stamp`-specific wording: the destination is not a template, so the zones are described as written-for-this-project and carried-from-the-template rather than as things `stamp` does.

- **`<dest>/AGENTS.md`** — symlink to `CLAUDE.md`. Create with `ln -s CLAUDE.md AGENTS.md` in the destination.

- **`<dest>/LOG.md`** — one-line stub:
  ```markdown
  # Activity Log

  This log is **append-only** and owned by `kickoff`. Do not hand-edit historical entries.
  ```

- **`<dest>/briefs/BRIEF.md`** — entry-point brief for the new project. Use the thesis-stub shape: H1, italic tagline, `## Thesis` paragraph from `description`, `## Catalog` pointer to `../CLAUDE.md#briefs-catalog`. Mark `status: draft` in frontmatter so the user knows it needs to be fleshed out.

  **Skip this entirely when a seed brief was adopted.** The adopted entry-point brief *is* the brief; writing a stub over it would destroy the best input the bootstrap had. Catalog it — and every other adopted brief — in `CLAUDE.md`'s Project briefs section under whatever names the user gave them, with a one-line summary drawn from each brief's own opening. Leave the bodies untouched.

- **`<dest>/plan/INDEX.md`** — copy this template's `plan/INDEX.md` structure, adapted: project name in the H1; the dependency graph enumerates every major phase the brief surfaces (Phase 1 + sketched Phases 2+); the phase table has one row per major phase, with Phase 1 as `⬅️` and the rest as `⏳`. See [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) §8.

- **`<dest>/plan/phase-1.md`** — a real first phase for the new project, drafted **in full**. Use the description plus inferred surfaces to draft Goal, Deliverables, and Acceptance. Mark Open Questions where the description is genuinely insufficient. Phase 1 should aim to deliver the project's "first slice end-to-end" — for a CLI, `<name> --help` plus one working subcommand; for a web app, the dev server plus one read-only page; for a library, the public API surface plus one working function.

- **`<dest>/plan/phase-2.md`, `<dest>/plan/phase-3.md`, …** — sketched major phases at lower fidelity. When a seed brief was adopted, this is where it pays off: enumerate one sketch per major phase the brief actually surfaces, rather than settling for a single placeholder. For each major phase the brief surfaces beyond Phase 1, draft a `phase-N.md` with frontmatter (`id`, `title`, `depends_on`, `informs`, plus `review_lane: light` only when the phase is mechanical per `policies/review-lanes.md` — omit otherwise) + one-paragraph Goal + high-level Deliverables list + scaffold Acceptance + Brief refs. These sketches will be tightened by ripple at each upstream phase's close (per [`policies/phase-ripple.md`](../../../policies/phase-ripple.md)) and elaborated when their row enters `⬅️` (per the kickoff Step 1a/9a/9b machinery). If the brief surfaces only a single phase, skip the sketches.

- **Do NOT draft any sub-phase files at bootstrap** — no `phase-1.1.md`, no `phase-2.1.md`, none. Sub-phase decomposition is JIT, owned by `kickoff` Step 1a at each major phase's open. The bootstrap leaves sub-phase shape to the orchestrator with each predecessor's outcomes in hand.

### Step 4 — Lay down the primary code surface

Write a minimal-but-runnable code skeleton in the project's primary language. The intent is that the project's build gates can be run successfully on first clone — Phase 1 then fleshes out the real behavior.

**Path convention.** All paths below are written assuming `project_isolation` is enabled (the default for single-deliverable projects). Prefix every path with `project/` when laying files down. If `project_isolation` is disabled, drop the `project/` prefix and lay files at the repo root.

**Python (paths inside `project/`):**
- `.python-version` selecting the repository's default managed interpreter.
- `pyproject.toml` with `[project]` metadata, `[tool.uv]` managed-interpreter
  policy, `[tool.ruff]`, `[tool.pytest.ini_options]`, and committed dev
  dependencies `ruff`, `pytest`.
- `uv.lock`, generated from that manifest and interpreter policy.
- A concise `README.md` for the artifact (the repo's didactic README is at the root).
- `<slug>/__init__.py` with version export.
- `<slug>/cli.py` with an argparse entry point that responds to `--help` and a stub subcommand.
- `tests/test_cli.py` with one passing test (e.g., asserts `--help` exits 0).
- `.gitignore` listing Python build artifacts (`__pycache__/`, `*.py[cod]`, `*.egg-info/`, `build/`, `dist/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.coverage`).

**TypeScript / Node — library, CLI, or service (paths inside `project/`):**
- `package.json` with `scripts: { lint, test, typecheck }`, the package manager
  and its version pinned via `packageManager`, plus every named dependency.
- The package manager's lockfile, generated from that manifest.
- `tsconfig.json`.
- Concise `README.md`.
- `src/index.ts` exporting a stub function (for a CLI, `src/cli.ts` with an
  argument parser and one subcommand; for a service, `src/server.ts` with one
  route).
- `tests/index.test.ts` with one passing test.
- ESLint and Prettier config files.
- `.gitignore` listing Node build artifacts (`node_modules/`, `dist/`, `build/`, `coverage/`).

**TypeScript — browser app, including a Canvas2D or WebGL game (`surfaces: [web]`,
paths inside `project/`):** everything in the Node profile above, and then the
parts a browser-delivered app needs and a library skeleton does not:
- `index.html` — the host page, with a single mount point (`<canvas>` for a
  canvas game, `<div id="app">` otherwise). Without a page there is nothing to
  run, and a stamped "web" project that cannot be opened in a browser has failed
  at its one job.
- A bundler with a dev server, wired to `scripts: { dev, build, preview }`. Vite
  is the default choice unless the brief names another; record the choice in the
  brief's conventions so Phase 1 does not relitigate it.
- `src/main.ts` — the entry point the page loads. For a canvas surface it
  acquires the drawing context, runs one frame of a `requestAnimationFrame`
  loop, and draws something visible. "Something visible" is the point: the first
  `./bin/check all` should be followed by a dev server the user can look at.
- `src/<slug>.ts` — the first real module (for a game, the update/draw step),
  kept free of DOM access so it is testable headlessly.
- `tests/<slug>.test.ts` — tests that module directly. **Do not** make the seed
  test depend on a real browser: a gate that needs a display is a gate that fails
  in CI and on a headless machine. Keep browser-dependent verification in the
  phase's `User Demo:` protocol, where a human runs it, per
  [`policies/user-demo-protocols.md`](../../../policies/user-demo-protocols.md).
- `.gitignore` additions for the bundler's output and cache.

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

**Desktop app (`surfaces: [desktop]`):** the language's normal application
layout plus whatever the named framework requires, with the same rule as the
browser profile — the business logic lives in a module with no window or
platform-API access, so the seed test runs headlessly, and the window itself is
verified through the phase's `User Demo:` protocol.

**TUI (`surfaces: [tui]`):** the `cli` layout, plus the screen-driving
dependency the brief names, plus the same separation — render state is computed
by a pure function the test can call, and the terminal rendering itself is a
manual check.

**Other languages:** apply the same pattern — package metadata, one source file with a stub entry, one passing test, a concise README, the language's `.gitignore` inside `project/`.

**Every named dependency lands in the manifest and the lockfile**, whatever the
language and surface. Generate the lockfile from the finished manifest rather
than hand-writing it, and never add a package nobody asked for.

The artifact's `README.md` is short and self-contained (no `..` references) per [`policies/project-isolation.md`](../../../policies/project-isolation.md). The deliverable's `.gitignore` lives inside `project/` so submodule extraction carries it. The repo's top-level `.gitignore` lists only editor/OS files and agentic harness runtime state, including `.kickoff/` local timing telemetry. The repo's didactic top-level `README.md` describes the methodology and points at `project/` for the artifact.

When `project_isolation` is disabled (polyglot), there is no `project/.gitignore`; all language entries live at the repo root in a single combined `.gitignore`.

### Step 5 — Generate the repository-owned toolchain contract

Adapt the complete atomic bundle defined by `policies/build-gates.md`:

- `<dest>/bin/setup` provisions the committed environment in immutable mode;
- `<dest>/bin/test` runs all tests with no arguments and forwards focused
  arguments with paths rooted at `<dest>`;
- `<dest>/bin/check` preserves `all|lint|format|test|policy`, delegates `test`
  to `bin/test`, and runs every authoritative gate;
- `<dest>/bin/check-receipt` records every full-gate run under the gitignored
  `.kickoff/check-all/` tree and creates a reusable success receipt only after
  the exact candidate, environment fingerprint, complete log, and terminal
  metadata verify; for a Python target, it obtains the fingerprint through the
  repository-selected runtime path, `<dest>/bin/python`, with the selected
  implementation, actual version, resolved executable and base-executable
  identities and file digests, machine, platform, and uv version—not the
  receipt helper's runtime or a version-file proxy; candidate hashing stays
  separate from the venv and external runtime tree;
- a Python target gets `<dest>/bin/_python-toolchain` plus
  `<dest>/bin/python`; the shared helper selects the managed default or a
  fail-closed authoritative override and runs a target-adapted real dependency
  probe before the wrappers proceed;
- the runtime pin, manifest, lockfile, behavioral tests, hook, docs, `kickoff`,
  and four canonical agents all agree with those entry points.
- every dependency-bearing operational caller, generated command, tracked
  hook, and active instruction uses the destination's repository runtime;
- format checking covers staged, unstaged, and nonignored untracked candidate
  files without rewriting them;
- hot loops, mutation gates, generated multi-command workflows, and detached
  processes resolve the underlying repository interpreter once and reuse it.

Preserve cwd independence, strict argument handling, fail-closed prerequisite,
bundle-member, and authoritative-override checks, exact child-status
propagation, and stable PASS/FAIL lines. Apply identical runtime-selection
arguments to synchronization, probing, and execution, and reject an override
inside an environment the package manager may replace. Replace Starter's
package names, dependency probe, and policy-only anonymization call with the
target's real surfaces.

Use the target's committed language profile:

| Language | Setup / test / gate implementation |
|---|---|
| Python | `.python-version` + `pyproject.toml` + `uv.lock`; managed default plus an authoritative absolute-path compatibility override; locked sync/run; a real deliverable-and-tool load/run probe; recurring tools in the dev dependency group |
| TypeScript / Node | package-manager/version metadata plus the selected lockfile; frozen/immutable setup; package scripts behind `bin/test` and `bin/check` |
| Rust | declared/pinned toolchain when applicable; dependency fetch/build/test with Cargo `--locked` |
| Go | declared Go version; dependency and test commands with module reads `-mod=readonly` |

When `project_isolation` is enabled, each language gate runs from
`<dest>/project`; otherwise it runs from `<dest>`. The `policy` mode must check
at least the universal instruction/config invariants (`AGENTS.md` resolves to
`CLAUDE.md`; `bin/kickoff-config show` succeeds) and any target-specific
deterministic policy gates. It must not be an unconditional pass.

### The non-Python profile is a two-runtime contract

For a Python deliverable, its committed dev dependency group and lockfile cover
both the deliverable and the root methodology tests, and everything below is
moot. For **any other language** the repository has two runtimes, and treating
that as a footnote is how a stamp produces a project whose gate cannot start.
The shape, proved by stamping a TypeScript browser game end to end:

- **A committed governance environment**, conventionally `<dest>/tooling/`:
  runtime pin, manifest, and lockfile, no source of its own. It exists to run
  the universal managers under `bin/` and the root `tests/` suite, both of which
  are Python. Do not reach for an unpinned `uv run --with pytest` escape hatch
  merely because the deliverable is Node, Rust, or Go.
- **A per-language helper beside `bin/_python-toolchain`** — `bin/_node-toolchain`
  and so on — with the same contract: prerequisite check, contract-member check,
  an authoritative absolute-path override (`TOOLCHAIN_NODE` alongside
  `TOOLCHAIN_PYTHON`) that never falls back, and a real dependency-chain probe.
  Each helper takes its own root variable (`node_project_root`,
  `python_project_root`); the single `project_root` of the Python profile no
  longer says enough.
- **The package manager comes from the manifest, not from `PATH`.** Pin it in
  the manifest's own field (`packageManager` for Node) and invoke it through the
  launcher that honors that pin (`corepack`), so no caller depends on whichever
  version happens to be installed.
- **`bin/setup` provisions both**, from committed lockfiles, and probes both
  before reporting success.
- **`bin/test` routes by path prefix.** With no arguments it runs both suites.
  With arguments, the leading path selects the runner — `project/...` to the
  deliverable's runner with the prefix stripped, `tests/...` to pytest — and an
  invocation mixing both is an error, not a guess. A focused run that silently
  reaches the wrong suite is worse than one that refuses.
- **`bin/check` splits `lint` and `format` per runtime** and keeps `test`
  delegating to `bin/test`. **A split gate still owes exactly one summary line
  per mode**: emit `CHECK lint PASS` after the sub-gates the way `run_policy`
  emits `CHECK policy PASS`, or `./bin/check lint` stops reporting the stable
  line every caller and test reads.
- **Pin the deliverable's language version to what its *lint stack* supports,
  not to the newest release.** Observed 2026-08-25: the newest TypeScript was
  7.0, `typescript-eslint` declared a peer range of `>=4.8.4 <6.1.0`, and the
  combination made `eslint` abort at load time rather than report a finding — a
  broken gate that looks like a broken repo. Check the peer ranges of the lint
  and type tooling before choosing the pin, and record the constraint in the
  destination's conventions so the next person to bump it knows what it is
  waiting on.

**One shell trap, because it bit during that run and fails silently.** Capturing
a child's status with `if ! command; then command_exit=$?` yields **0**: after an
`if` whose condition failed and which has no `else`, `$?` is the status of the
`if` statement, not of the command. Every failure then propagates as success, or
as a diagnostic reading `(exit 0)`. Use the shape the existing entry points
already use — `if command; then :; else command_exit=$?; ...; fi` — and prove it
with a test that injects a specific nonzero code and asserts that exact code
comes back.

Adapt `<dest>/tests/test_toolchain_entrypoints.py` and
`<dest>/tests/test_check.py` in the same step, and carry
`<dest>/tests/test_check_receipt.py`, so their controlled fixtures expect
the target's exact setup, dependency probe, full/focused test, runtime, and
locked-gate commands. Prove valid override selection, invalid override refusal,
unsupported and self-referential override refusal, probe-failure status
propagation, exact gate ordering/delegation, cwd independence, child-status
propagation, and no fallback. These tests must execute the entrypoints with
controlled stubs; source-text assertions alone do not meet the behavioral
coverage floor. Prove format failures in staged, unstaged, and nonignored
untracked candidates. Prove a Python receipt records the runtime selected by
`bin/python`, not the receipt helper; changing the selected managed runtime or
the interpreter behind a stable `TOOLCHAIN_PYTHON` path invalidates the old
receipt while candidate content remains unchanged. Prove descriptor selection,
probe, query, parse, and schema failures run the authoritative full gate. Prove
pre-push reuse only for a clean current `HEAD` with an exact
candidate/environment receipt and intact log/run digests; every miss,
corruption, or query error must run the full gate.

`<dest>/tests/test_check.py` needs one adaptation beyond the command strings, and
it is easy to miss because it is about a gate the destination does not have.
Starter's `check-anonymization.sh` is the **last** policy gate, so the test uses
it three ways: as the failure-injection stub honoring `CHECK_POLICY_FAIL_CODE`,
as the trailing `policy cwd=…` entry in two ordered call lists, and as the
subject of `CHECK policy-anonymization FAIL`. All three must move onto the
destination's own last policy gate — `check-shell-syntax` for a repo carrying
the standard set — so the test still proves what it exists to prove: that a
policy failure cannot be masked by a later policy gate's output. Moving the stub
without moving the ordered lists leaves the test passing for the wrong reason.

Also adapt the dependency probe string in
`<dest>/bin/_python-toolchain`, which imports Starter's example package by name,
and the `ruff check` / `ruff format --check` target lists in `<dest>/bin/check`,
which name it as a directory. Both appear again inside the two toolchain tests;
the four must agree exactly or the ordered-call assertions fail.

Then change the **Final build gate** examples in `kickoff`, the four canonical
agents, `CLAUDE.md`, the brief, and Phase 1 to use `./bin/test ...` for focused
tests and `./bin/check all` for the authoritative suite. No copied raw
full-suite list may remain.

### Step 6 — Initialize git

In the destination directory:

```
git init
```

```
git add .
```

Skip `git init` when the seed already carried a `.git/` directory; stage and
commit onto the existing repository instead.

Then make the new repo's initial commit ([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)) — an ordinary factual message such as `Stamp project scaffold from the agentic starter template`, with no agent credit. Do **not** push: a freshly initialized repo has no configured upstream, and selecting or creating a remote belongs to the user. If `git init` fails, or the destination was already a repo with content the stamp did not write, leave the tree staged and report it instead of committing.

### Step 7 — Sanity-check

Run the bootstrap acceptance check from [`briefs/agentic-bootstrap.md` §6](../../../briefs/agentic-bootstrap.md), against the destination. Specifically:

- `readlink <dest>/AGENTS.md` returns `CLAUDE.md`.
- `grep -E '^\| \[Phase ' <dest>/plan/INDEX.md` returns at least one row with `⬅️`.
- `head -1 <dest>/LOG.md` is `# Activity Log`.
- `ls <dest>/.claude/agents/` lists exactly the four canonical role files.
- `ls <dest>/.claude/skills/kickoff/` contains `SKILL.md`.
- `ls <dest>/.claude/skills/methodology/` contains `SKILL.md`.
- `ls <dest>/.claude/skills/stamp/` does **not** exist (we did not transfer it).
- For each name in {kickoff, methodology, learn, teach, roles, sweep, demo, treatise, plain}: `readlink <dest>/.agents/skills/<name>` returns `../../.claude/skills/<name>`, `test -L <dest>/.agents/skills/<name>` and `test -d <dest>/.agents/skills/<name>` both pass, and `<dest>/.agents/skills/<name>/SKILL.md` is reachable through the directory symlink.
- `<dest>/.claude/settings.json` sets `worktree.bgIsolation` to `none`; an explicitly requested worktree remains available.
- `<dest>/bin/kickoff-config show` runs; `<dest>/bin/README.md` retains its universal entry but **not** the `### check-anonymization.sh` entry.
- `<dest>/bin/kickoff-tree-id` and `<dest>/bin/kickoff-evidence` are
  executable; their behavioral tests pass.
- `<dest>/bin/check-receipt` is executable and
  `<dest>/tests/test_check_receipt.py` passes; successful full gates retain a
  complete durable log and exact candidate/environment receipt; Python
  receipts identify the runtime selected by `<dest>/bin/python`, including its
  executable and base-executable identities, while dirty, changed-runtime,
  corrupt, non-`HEAD`, descriptor-error, and query-error pushes fail closed to
  the full gate.
- `<dest>/bin/lessons validate` and `<dest>/bin/check-catalogs` are executable
  and pass against the fresh destination (empty ledger, synced catalogs, one
  `⬅️`); a `.gitkeep` exists in each of `lessons/`, `lessons-archived/`,
  `user-actions/`, and `user-actions-archived/`, and no Starter ledger entries
  were copied into any of the four.
- Every executable `<dest>/bin/check` requires before it runs a gate is present
  and executable: `kickoff-tree-id`, `kickoff-evidence`, `kickoff-config`,
  `check-receipt`, `execution-telemetry`, `check-execution-dashboards`,
  `check-harness-parity`, `check-toolchain-callers`, `lessons`, `treatise`,
  `check-catalogs`, `check-hooks-installed`, `check-shell-syntax`, `new-name`.
  This is the fastest way to catch an incomplete copy: `bin/check` fails closed
  on the first one missing, before any gate runs.
- `<dest>/lib/agentic_starter/` exists and
  `<dest>/bin/execution-telemetry --help` runs; `<dest>/reports/execution/`
  carries `index.html`, `index-data.js`, and `assets/`, and
  `<dest>/bin/check-execution-dashboards` reports
  `EXECUTION DASHBOARDS PASS (0 phases)` against the fresh archive.
- `<dest>/bin/check-harness-parity` passes: one `.agents/skills/` mirror per
  canonical skill, no orphans, and one `.codex/agents/*.toml` per canonical role.
- `<dest>/.agents/skills/stamp` does **not** exist (starter-only, must not propagate).
- `<dest>/policies/anonymize-log-references.md`,
  `<dest>/bin/check-anonymization.sh`, and
  `<dest>/tests/test_methodology_toolchain_contract.py` do **not** exist, and no
  file in the destination links or names any of them — including the `CLAUDE.md`
  Hard rules section (rule 3 is gone) and the Policies catalog inside the
  Methodology Contract zone.
- The new `CLAUDE.md`'s catalogs reference every file in `briefs/` and `policies/`.
- When a seed brief was adopted: every adopted brief's body below its frontmatter
  is **byte-identical** to what the user wrote, an adopted `README.md` still
  contains the user's own text, and `plan/` carries one sketch per major phase
  the brief surfaces rather than a lone placeholder. Diff the bodies; do not
  eyeball them.
- When `surfaces` includes `web`: `<dest>/project/index.html` exists and names
  the mount point `src/main.ts` acquires, the dev/build scripts run, and the seed
  test suite passes **without a browser or a display** — a gate that needs a
  screen is a broken gate. Prove the page actually serves rather than merely
  builds: run the preview server and fetch `/`, confirming the mount point and
  the bundled entry script both appear in the response.
- Every language-version pin the lint or type tooling constrains is inside that
  tooling's supported range, and the constraint is written down in the
  destination's conventions rather than left to be rediscovered.
- Every dependency named in the brief or the description appears in the
  destination's manifest and in its lockfile, and no dependency appears that
  nobody named.
- `<dest>/kickoff.yaml` exists; `show` prints the seeded cross-vendor model routing, portable timeout values, and per-role research budgets; a scoped model edit preserves timeout/research comments and values; `<dest>/.gitignore` includes `.kickoff/`; the role, timeout, and research-authority policies plus invocation brief exist.
- `<dest>/bin/setup` succeeds from outside `<dest>` and provisions only the
  committed runtime/dependencies, then passes the target-adapted dependency
  probe.
- `<dest>/bin/test` runs `tests/test_toolchain_entrypoints.py`,
  `tests/test_check.py`, `tests/test_check_receipt.py`, `tests/test_install_hooks.py`,
  `tests/test_kickoff_config.py`, `tests/test_kickoff_tree_id.py`,
  `tests/test_kickoff_evidence.py`, `tests/test_lessons.py`,
  `tests/test_check_catalogs.py`, `tests/test_treatise.py`,
  `tests/test_new_name.py`, `tests/test_shell_syntax.py`,
  `tests/test_toolchain_callers.py`, `tests/test_mirror_parity.py`,
  `tests/test_research_authority.py`, `tests/test_execution_telemetry.py`,
  `tests/test_execution_dashboard.py`, and the deliverable tests through
  committed locked environments; a focused repo-relative test argument runs
  only that selection.
- `<dest>/bin/check test` delegates to `<dest>/bin/test`.
- `<dest>/bin/check all` runs from outside `<dest>` and passes on the seeded code.
- A valid explicit runtime override drives every Python entry point; an invalid
  or probe-failing override exits nonzero without fallback.
- Staged, unstaged, and nonignored untracked format failures are each rejected
  without rewriting the candidate.
- A hot loop, mutation gate, generated multi-command workflow, or detached
  process resolves its underlying repository interpreter once and reuses it.

Run the repository-owned gate to confirm:

```
<dest>/bin/check all
```

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

**The scaffold is committed; the remote is not chosen.** The new project starts with one initial commit and no upstream — the user decides where it lives.

## Rules

- The destination repo's content is the user's. Never carry over the template author's personal identity, the identity of whoever ran this stamp, their other projects, their email, or any third-party PII. The stamp skill itself ships in a distributable repo; the new repo is even more so.
- Ask only the questions inference cannot answer. A clear description shortens the bootstrap to seconds.
- When in doubt about a name, file path, or convention, prefer this template's choice — that's why it exists.
- Surface every assumption you made (inferred language, inferred surfaces, derived project name) in the final report so the user can correct anything before kickoff.
