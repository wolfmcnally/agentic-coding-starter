---
title: Mini-method — a minimal CLAUDE.md for small projects
date: 2026-09-01
status: methodology
scope: A verbatim, copy-pasteable CLAUDE.md that idempotently provisions the smallest useful project shape — git repo, .gitignore, briefs/, policies/, docs/, bin/ — and graduates to the full methodology through teach.
---

# Mini-method — a minimal CLAUDE.md for small projects

## Purpose

The full methodology is proportionate to phased, gate-proved software: it earns its ceremony on projects with a plan ledger, four review roles, candidate-bound evidence, and an authoritative build gate. A notebook of experiments, a small tool, a research folder, or a knowledge base needs none of that machinery — but it still benefits from the *shape*: a git repository, an ignore file, one place for thinking, one for rules, one for pinned third-party material, one for deterministic scripts, and a single instruction file that tells any agent how the directory is organized and how to behave. Mini-method is that subset, packaged as one `CLAUDE.md` an agent can execute.

This is not the light review lane. The light lane is a review-depth setting *inside* the full methodology; mini-method is a smaller method — no `plan/`, no `LOG.md`, no roles, no gates — for projects that have not yet earned them.

## What it provides

| Surface | Role in mini-method | At graduation to the full methodology |
|---|---|---|
| git repository | `git init -b master`; no remote is ever created | Unchanged; delivery machinery starts using the remote the operator configures |
| `.gitignore` | Editor, OS, and harness runtime state | Extended with the full method's runtime entries (`.kickoff/` and friends) |
| `CLAUDE.md` | The whole method: layout, setup protocol, rule set | Replaced by the two-zone form; the Project paragraph carries into Project Context |
| `briefs/` | Durable thinking, indexed by `briefs/README.md` | Carries over unchanged; the catalog moves into `CLAUDE.md` |
| `policies/` | Binding rules, indexed by `policies/README.md` | Carries over unchanged; the catalog moves into `CLAUDE.md`; the universal policy set is added |
| `docs/` | Pinned third-party material, cataloged in `docs/README.md` | Carries over unchanged — the full method keeps the same catalog file |
| `bin/` | Deterministic scripts, indexed by `bin/README.md` | Carries over unchanged; the toolchain contract and checkers are added |
| — | Absent by design: `plan/`, `LOG.md`, ledgers, roles, skills, gates | Added by `teach` |

The catalogs live in per-directory `README.md` files, not in `CLAUDE.md`, so the fenced block below is verbatim for every project and never needs editing as the project grows: the project's own content accumulates in the directories and their READMEs, and the one file that came from this brief stays byte-identical to its source.

## Two ways to use it

**Copy the block.** Copy the fenced block below into `<dir>/CLAUDE.md` and open the directory in a coding harness. The first agent to read the file finds the layout incomplete and runs the Setup section; every step is idempotent, so a half-finished or already-complete directory is handled by the same protocol.

**Ask an agent in this repository.** Say "set up `<dir>` with mini-method". The agent extracts the fenced block from this brief *verbatim* — for example, the lines strictly between the `` ````markdown `` fence markers below — writes it to `<dir>/CLAUDE.md`, then follows that file's own Setup section exactly as the target's agent would, and reports what it created and what was already present. The written block must be byte-identical to the block here; the agent adds nothing and localizes nothing.

There is deliberately no `bin/` script for this. The protocol has to work for a stranger who copied the block and has no access to this repository, so the block itself must remain the complete implementation — a parallel script would be a second home for the same procedure and the two would drift (`policies/simplicity-and-consolidation.md`'s one-home rule, applied to a procedure).

## The CLAUDE.md

The block is the artifact; the prose around it is commentary. Corrections land in the block first, and the sections after it are updated to match.

````markdown
# CLAUDE.md

Guidance for coding agents working in this repository. This project uses the **mini-method**: a minimal layout and a short rule set. It can be upgraded to the full agentic-coding methodology later; see "Graduating" at the end.

## Setup — idempotent; run whenever the layout below is incomplete

An agent that reads this file in a directory that does not yet match the layout brings it up to the layout, creating only what is missing and touching nothing that exists. Every step is safe to repeat.

1. **Git.** If `git rev-parse --is-inside-work-tree` fails, run `git init -b master`. Never create a remote, never change an existing one, never push. An existing remote is left exactly as found.
2. **`.gitignore`.** Create it if absent with these lines; if present, append only the lines that are missing and never remove or reorder any: `.DS_Store`, `.idea/`, `.vscode/`, `*.swp`, `*.swo`, `.claude/settings.local.json`, `.claude/projects/`, `.codex/cache/`, `__pycache__/`, `.pytest_cache/`, `node_modules/`, `.venv/`. Language build output is the project's own addition.
3. **Directories.** `mkdir -p briefs policies docs bin`. Give each directory a `README.md` if it has none, stating in a sentence what belongs there (per Layout below) and holding the directory's catalog. Never overwrite an existing README.
4. **Project paragraph.** If the "Project" section below still holds the angle-bracket placeholder, replace it with one paragraph drawn from the operator's description or an existing top-level `README.md`. If neither exists, leave the placeholder and say so in the report.
5. **Commit.** Stage only the paths this setup created or appended to — never `git add -A` or `git add .` — and commit as `Set up mini-method layout`. Do not push. Then report what was created and what was already present.

## Project

<Not yet described. Replace this paragraph with what the project is, who it is for, and what done looks like.>

## Layout

- `briefs/` — durable thinking: what was intended, what was researched, what was decided and why. One Markdown file per topic; each opens with a title, a date, and a one-line scope. `briefs/README.md` lists every brief with one line each.
- `policies/` — rules every piece of work honors. Short and prescriptive. A brief describes; a policy binds; when they disagree, the policy wins until it is amended. `policies/README.md` lists every policy with one line each.
- `docs/` — third-party material this project depends on, pinned verbatim: vendor documentation, specifications, license texts. Nothing here is written by the project, and nothing here links to anything else in the repository. `docs/README.md` is the catalog: one row per entry with the source URL, the source's own date or version (`As of`), the fetch date (`Retrieved`), and the license or terms that permit keeping a copy.
- `bin/` — deterministic scripts: one concern per script, invoked as `./bin/<name>`, exit 0 on success and non-zero on findings or failure. `bin/README.md` documents every script: what it does, when to run it, how it fails.

Citations run one way: policies and briefs may cite docs; a policy may cite the brief that motivated it; a doc cites nothing. When a directory gains or loses a file, its README changes in the same commit.

## Rules

- **Rules, not memory.** Anything that should bind a future session — any agent, any harness, any operator — is written into this repository, not into a harness's memory. A rule goes in `policies/`; reasoning goes in `briefs/`; a repeatable procedure becomes a script in `bin/`.
- **Script the mechanical, reason about the rest.** A task that is exact and repeatable belongs in `bin/`; a task that needs judgment belongs to the agent. Do not spend a model on what a script does better, and do not script what needs judgment.
- **Repo-relative paths only** in committed files. Never an absolute path into someone's home directory.
- **Never hard-wrap Markdown prose.** One paragraph is one physical line; line breaks only where Markdown syntax requires them.
- **Date external facts.** A claim about the outside world carries the date it was true (`As of YYYY-MM-DD`) and, when fetched, the date it was fetched (`Retrieved YYYY-MM-DD`). These are different dates; a fresh retrieval of an old document is still an old document.
- **Verify names before citing them.** A function, flag, config key, command, or file is named only after reading it from whatever defines it. An identifier that merely looks conventional is unverified; say so.
- **Commit discipline.** Stage explicit paths, never `git add -A` or `git add .`. Write plain factual commit messages with no agent credit. Never rewrite history, force-push, reset, or delete branches on your own initiative; push only when the operator asks.
- **The operator decides.** The person running this checkout is the operator, referred to with they/them pronouns and never by name in a committed file. Subjective judgments, destructive actions, and anything outward-facing are theirs to approve.

## Graduating

When this project needs phased work, review gates, and an activity log, it is time for the full methodology. From a checkout of the agentic-coding starter template, run `/teach <this directory>` in Claude Code or `$teach <this directory>` in Codex. It keeps `briefs/`, `policies/`, `docs/`, and `bin/` as they are, moves the directory catalogs into this file, and adds the plan ledger, log, roles, skills, and gates. Commit or stash first — the upgrade requires a clean working tree.

<!-- mini-method: agentic-coding-starter -->
````

## Graduating

The trailing HTML comment in the block is the marker the `teach` skill recognizes: a target whose `CLAUDE.md` carries it is classified as a *mini-method graduation* rather than a divergent or partially stamped project. The four directories transfer as they stand; the `briefs/README.md` and `policies/README.md` catalogs fold into the new `CLAUDE.md`'s catalogs, while `docs/README.md` and `bin/README.md` remain the catalog files the full methodology also uses; the mini `CLAUDE.md` is replaced wholesale by the two-zone form, with its Project paragraph carried into the Project Context zone; and the absence of `plan/`, `LOG.md`, ledgers, roles, and gates is absent-by-design, not drift.

Two preconditions belong to the operator: the working tree must be clean (the `teach` preflight refuses otherwise), and any `README.md` the operator wrote is preserved — the upgrade adds surfaces, it does not rewrite prose. And one non-path to note: `stamp` will *refuse* a mini-method directory, because its destination gate tolerates only seed briefs; `teach` is the upgrade path.

## Design notes

- **Per-directory catalogs.** The block must be verbatim for every project or it stops being copy-pasteable and starts being a template with holes. Moving the catalogs into the directory READMEs is what makes that possible: the one file sourced from this brief never changes, and everything project-specific accumulates beside it. Graduation reverses this for `briefs/` and `policies/` because the full method's catalogs live in `CLAUDE.md`.
- **Commit, never push.** Setup ends in one atomic, visible commit of exactly what it created, so the scaffold has a clean provenance line in history. Remotes, pushes, and hosting are the operator's: "no remote unless it already has one" means `git init` only — never creating a hosted repository on the operator's behalf.
- **`master`.** The default branch is `master`, matching every repository in this methodology's lineage.
- **No `plan/`, no `LOG.md`.** A small project's history is its commit log, and its next action fits in the operator's head. The moment those stop being true — work needs phases, or "what happened while I was away" needs an answer better than `git log` — is precisely the graduation signal, so the surfaces arrive with the machinery that writes them.
- **Rules left out, deliberately.** Greenfield-until-released presumes a release boundary; review lanes presume roles; the evidence plane presumes candidates and gates. Each would be a rule wired to nothing here. The eight rules kept are the ones that bind any repository with agents in it, whatever its size.
