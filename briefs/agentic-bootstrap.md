---
title: "Standing Up a New Project From This Template"
date: 2026-08-25
status: methodology
scope: Procedure for using this repository as a master template to stand up a new project under the agentic coding methodology. Authoritative reference for the `stamp` skill.
---

# Standing Up a New Project From This Template

How to use this repository as a *master template* to bootstrap a new project that follows the same agentic coding methodology. This brief is the contract `stamp` implements; read it before customizing the skill or running the procedure by hand.

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
  LOG.md                   # Append-only activity log; kickoff writes
                           #   START/END blocks here
  lessons/                # Open candidate process lessons (.gitkeep initially)
  lessons-archived/       # Codified/rejected lesson audit trail (.gitkeep initially)
  user-actions/           # Open human-only action items (.gitkeep initially)
  user-actions-archived/  # Closed action-item audit trail (.gitkeep initially)
  .gitignore               # Editor/harness state; includes local .kickoff/
  .gitattributes           # Line-ending normalization for cross-harness mirrors
  kickoff.yaml             # Human-editable model/effort/timeout/research configuration

  bin/
    README.md              # Deterministic script operator index
    setup                  # Provision pinned, locked dependencies
    test                   # Full/focused repository test runner
    check                  # Authoritative lint/format/test/policy gates
    check-receipt          # Durable candidate-bound full-gate receipts
    <runtime>              # Optional selected runtime (for example, python)
    install-hooks          # Explicit opt-in to tracked Git hooks
    check-hooks-installed  # Opt-in-aware hook-liveness witness
    kickoff-config         # Round-trip editor, preflight, watchdog, calibration
    kickoff-tree-id        # Complete review candidate identity
    kickoff-evidence       # Authority/change/finding/packet/gate records
    execution-telemetry    # Exact stage/role/wait/gate trace and park ledger
    check-execution-dashboards # Offline report archive and renderer checks
    serve-execution-dashboard  # Local viewer for a generated report
    check-harness-parity   # Canonical-vs-mirror drift, fail-closed
    check-toolchain-callers # Every caller uses the repository runtime
    check-shell-syntax     # Shell scripts parse before they are needed
    check-plan-concreteness # kickoff's mechanical pre-review of a plan artifact
    check-plan-delivery    # kickoff's pre-critic check that the tree holds what the plan named
    review-verdicts        # Harvest review verdicts from harness traces (sweep-planning)
    lessons                # Validate/query the lessons ledger
    treatise               # Validate treatise editorial records
    check-catalogs         # Catalog, link, anchor, citation, ledger checks
    new-name               # Collision-checked ledger slug generator

  lib/
    agentic_starter/       # Shared deterministic library the bin/ scripts import
                           #   (telemetry, evidence schemas, dashboard rendering)

  reports/
    execution/             # Committed privacy-safe offline phase reports plus
                           #   index.html, index-data.js, and vendored assets/.
                           #   A fresh repo's archive holds zero phases.

  tests/
    test_toolchain_entrypoints.py # Setup/test/runtime behavioral coverage
    test_check.py          # Full-gate behavioral coverage
    test_check_receipt.py  # Durable receipt and fail-closed reuse coverage
    test_install_hooks.py  # Hook-installer behavioral coverage
    test_check_hooks_installed.py # Hook-liveness witness coverage
    test_kickoff_config.py # Universal manager/watchdog behavioral coverage
    test_kickoff_tree_id.py # Candidate identity behavioral coverage
    test_kickoff_evidence.py # Evidence/packet/gate behavioral coverage
    test_execution_telemetry.py # Trace, join, and park-ledger coverage
    test_execution_dashboard.py # Deterministic offline report coverage
    render_execution_dashboard_fixture.py # Report-rendering fixture helper
    test_mirror_parity.py  # Canonical-vs-mirror parity coverage
    test_toolchain_callers.py # Caller-policy coverage
    test_shell_syntax.py   # Shell-syntax checker coverage
    test_research_authority.py # Per-role search/retrieval boundary coverage
    test_lessons.py        # Lessons-ledger schema/query coverage
    test_treatise.py       # Editorial-record validation coverage
    test_check_catalogs.py # Document and phase-ledger coverage
    test_new_name.py       # Slug-generator coverage
    fixtures/              # Shared test fixtures (telemetry traces, config seed)

  briefs/
    BRIEF.md               # Entry-point brief, project-specific
    methodology.md         # The eleven steps (copied verbatim)
    agentic-bootstrap.md   # This brief (copied verbatim, for the next bootstrap)
    cross-agent-invocation.md  # Cross-CLI invocation BCPs (copied verbatim)
    incremental-orchestration.md # Candidate-bound incremental assurance
    deterministic-orchestration.md  # Draft: deterministic kickoff loop (copied verbatim)
    harness-self-improvement.md # Lessons capture, pruning, and propagation
    session-context-compaction.md # Managing compaction during long runs
    <topic>.md             # Project-specific topic briefs as they appear

  policies/
    README.md
    briefs-and-policies.md
    cross-harness-parity.md
    four-canonical-agents.md
    role-models.md
    role-timeouts.md
    orchestration-evidence.md
    review-lanes.md
    phase-status.md
    acceptance-empirical.md
    log-discipline.md
    lessons.md
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
      roles/SKILL.md       # Universal: edit model/effort fields for any role
                           #   (wraps bin/kickoff-config)
      sweep/SKILL.md       # Universal: audit/prune accumulated rule surfaces
      sweep-planning/SKILL.md # Universal: longitudinal review-verdict sweep over harness traces
      sweep-coding/SKILL.md # Universal: the same sweep over the coder ↔ critic loop
      demo/SKILL.md        # Universal: one-step-at-a-time demo walkthrough
      treatise/SKILL.md    # Universal: audience-specific outward explanation
      plain/SKILL.md       # Universal: the register for addressing the operator
      # stamp is NOT carried over — the new project doesn't need to stamp
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

  .agents/                 # Codex CLI native skill discovery
                           # (developers.openai.com/codex/skills)
    skills/
      kickoff              # Directory symlink → ../../.claude/skills/kickoff
      methodology          # (Codex doesn't follow file-level symlinks inside
      learn                #  a skill dir — issue #11314 — but does traverse
      teach                #  a symlinked skill directory.)
      roles
      sweep
      sweep-planning
      sweep-coding
      demo
      treatise
      plain
      # stamp is NOT mirrored here either — starter-only

  tooling/                 # ONLY when the deliverable is not Python: the
                           #   committed governance environment (runtime pin,
                           #   manifest, lockfile, no source) that runs the
                           #   universal bin/ managers and the root tests/
                           #   suite. A Python deliverable covers both from its
                           #   own dev dependency group and needs no tooling/.

  project/                 # When project-isolation is enabled (default for
                           #   single-deliverable projects), the artifact lives
                           #   here, self-contained per
                           #   policies/project-isolation.md. Otherwise the
                           #   <language-skeleton> directories live at the
                           #   repo root as siblings.
    .python-version        # (or the language's version declaration)
    pyproject.toml         # (or package.json / Cargo.toml / go.mod)
    uv.lock                # (or the selected package manager's lockfile)
    README.md              # concise, artifact-only
    <slug>/                # package directory
    tests/
```

**Status legend** used in `plan/INDEX.md` and nowhere else:

```text
⏳ Not Started    ⬅️ Next (at most one)    🚧 In Progress    ✅ Completed
```

Every phase row carries exactly one recognized status. The initial idle ledger
has exactly one `⬅️`; active and complete ledgers may have zero; more than one
is always invalid.

**The four canonical agents** — exact names matter; `kickoff` invokes them by name:

| Role            | Tools allowed                                          | Writes code |
| --------------- | ------------------------------------------------------ | ----------- |
| `phase-planner` | Read, Grep, Glob, WebSearch, WebFetch                  | No          |
| `plan-reviewer` | Read, Grep, Glob, WebSearch, WebFetch                  | No          |
| `phase-coder`   | Read, Write, Edit, Grep, Glob, Bash, WebFetch          | Yes         |
| `code-critic`   | Read, Grep, Glob, WebFetch                             | No          |

The `kickoff` skill is itself **also** an agent in spirit, but it behaves as a user-invoked workflow, not a subagent. It delegates initial implementation to the four roles above and edits `plan/INDEX.md` + `LOG.md`; for a small low-risk follow-up correction, it may edit code directly under the proportional routing rule in `policies/review-lanes.md`.

---

## 2. What to transfer verbatim, what to rewrite, what to discard

The template's contents fall into three categories.

### 2a. Transfer essentially verbatim (universal)

These files encode the methodology itself, not any particular product. Copy them; replace any "Agentic Coding Starter Template" project-name references with the new project's name. Otherwise leave the structure intact.

- `.claude/skills/kickoff/SKILL.md`
- `.claude/skills/methodology/SKILL.md`
- `.claude/skills/learn/SKILL.md` (universal cross-repo skill)
- `.claude/skills/teach/SKILL.md` (universal cross-repo skill)
- `.claude/skills/roles/SKILL.md` (universal — per-role model/effort editing; wraps `bin/kickoff-config`)
- `.claude/skills/sweep/SKILL.md` (universal rule-surface maintenance and lessons graduation)
- `.claude/skills/sweep-planning/SKILL.md` (universal longitudinal sweep of plan-review verdicts harvested from harness traces; canonical home of the shared sweep lifecycle)
- `.claude/skills/sweep-coding/SKILL.md` (the same sweep over code-review verdicts and coder failure analyses)
- `.claude/skills/demo/SKILL.md` (universal one-step-at-a-time user demonstration workflow)
- `.claude/skills/treatise/SKILL.md` (universal publication-gated long-form synthesis; governed by `policies/treatise.md`)
- `.claude/skills/plain/SKILL.md` (universal operator register; governs every message addressed to the operator)
- `.claude/settings.json` (portable harness defaults; `worktree.bgIsolation: none` disables implicit background worktrees without disabling explicit ones)
- `.claude/agents/phase-planner.md`
- `.claude/agents/plan-reviewer.md`
- `.claude/agents/phase-coder.md`
- `.claude/agents/code-critic.md`
- `.codex/agents/*.toml`
- `.agents/skills/kickoff` (directory symlink → `../../.claude/skills/kickoff`)
- `.agents/skills/methodology` (directory symlink → `../../.claude/skills/methodology`)
- `.agents/skills/learn` (directory symlink → `../../.claude/skills/learn`)
- `.agents/skills/teach` (directory symlink → `../../.claude/skills/teach`)
- `.agents/skills/roles` (directory symlink → `../../.claude/skills/roles`)
- `.agents/skills/sweep` (directory symlink → `../../.claude/skills/sweep`)
- `.agents/skills/sweep-planning` (directory symlink → `../../.claude/skills/sweep-planning`)
- `.agents/skills/sweep-coding` (directory symlink → `../../.claude/skills/sweep-coding`)
- `.agents/skills/demo` (directory symlink → `../../.claude/skills/demo`)
- `.agents/skills/treatise` (directory symlink → `../../.claude/skills/treatise`)
- `.agents/skills/plain` (directory symlink → `../../.claude/skills/plain`)
- `AGENTS.md` symlink → `CLAUDE.md`
- Every file under `policies/` (these are universal by design)
- `bin/kickoff-config` (universal Python/uv round-trip config manager, fail-closed venue preflight, execution watchdog, research-budget authority, and telemetry calibrator), plus human-editable `kickoff.yaml` seeded via `bin/kickoff-config reset all`
- `tests/test_kickoff_config.py` (universal manager/watchdog behavioral coverage; run independently of the deliverable's language)
- `bin/kickoff-tree-id` and `bin/kickoff-evidence` (universal candidate
  identity and run-evidence managers)
- `tests/test_kickoff_tree_id.py` and `tests/test_kickoff_evidence.py`
  (universal behavioral coverage for candidate/evidence mechanics)
- `bin/check-receipt` and `tests/test_check_receipt.py` (universal durable
  full-gate records and exact, fail-closed pre-push reuse)
- `bin/lessons` and `bin/check-catalogs` (universal lessons-ledger,
  document-link, and phase-ledger fitness managers)
- `tests/test_lessons.py` and `tests/test_check_catalogs.py` (universal
  behavioral coverage for those managers)
- `bin/execution-telemetry`, `bin/check-execution-dashboards`, and
  `bin/serve-execution-dashboard`, together with `lib/agentic_starter/` (the
  shared deterministic library the first two import) and `reports/execution/`
  with its `index.html`, `index-data.js`, and vendored offline `assets/`. The
  new project's archive starts empty, which the checker reports as
  `EXECUTION DASHBOARDS PASS (0 phases)`
- `tests/test_execution_telemetry.py`, `tests/test_execution_dashboard.py`,
  `tests/render_execution_dashboard_fixture.py`, and `tests/fixtures/`
  (universal behavioral coverage for telemetry and offline report rendering)
- `bin/check-harness-parity`, `bin/check-toolchain-callers`,
  `bin/check-shell-syntax`, `bin/new-name`, `bin/check-plan-concreteness`
  (which `kickoff` runs over every plan artifact before plan review, covered
  by `tests/test_check_plan_concreteness.py`), `bin/check-plan-delivery`
  (which `kickoff` runs before every code review, covered by
  `tests/test_check_plan_delivery.py`; both share
  `lib/agentic_starter/plan_artifact.py`), `bin/review-verdicts` (the
  `sweep-planning` / `sweep-coding` trace harvester, covered by
  `tests/test_review_verdicts.py`),
  and `bin/treatise` (the
  universal deterministic checkers and the ledger-slug generator), with
  `tests/test_mirror_parity.py`, `tests/test_toolchain_callers.py`,
  `tests/test_shell_syntax.py`, `tests/test_new_name.py`, and
  `tests/test_treatise.py`
- `tests/test_research_authority.py` (universal coverage for the per-role
  search/retrieval boundary)
- `.gitattributes` (line-ending normalization that keeps cross-harness mirrors
  byte-identical across platforms)
- `briefs/methodology.md`
- `briefs/agentic-bootstrap.md` (this file, so the next bootstrap is possible)
- `briefs/cross-agent-invocation.md` (the cross-CLI invocation BCPs cited by `policies/role-models.md`)
- `briefs/incremental-orchestration.md` (candidate-bound review, revision,
  verification, and protocol-recovery design)
- `briefs/deterministic-orchestration.md` (draft universal brief: decision criteria for a deterministic kickoff loop, so the derived project can act when its harnesses gain parity workflow primitives)
- `briefs/harness-self-improvement.md` (phase-scale lessons capture,
  rule-surface pruning, and cross-repo propagation)
- `briefs/session-context-compaction.md` (managing harness context compaction
  during long orchestration runs)
- The skeletal headings/structure of `plan/INDEX.md`
- The skeletal frontmatter shape for `plan/phase-*.md` (`id`, `title`, `depends_on`, `informs`, optional `review_lane` per `policies/review-lanes.md`)
- The START/END block format for `LOG.md`
- The status-marker convention (⏳ ⬅️ 🚧 ✅)

### 2b. Transfer the *shape*, rewrite the *content* (per-project)

These files have a stable shape and a project-specific body. Mirror the shape; write fresh content from the new project's brief.

- `README.md` — keep the section structure (what the project is, why, how to use, repository layout, status markers, four canonical agents, briefs-vs-policies-vs-plan, first-time setup), but every line is project-specific.
- `CLAUDE.md` — uses a two-zone structure delimited by HTML comment markers, with a **Hard rules** section above both. The `Methodology Contract` zone (between `<!-- METHODOLOGY_CONTRACT_START -->` and `<!-- METHODOLOGY_CONTRACT_END -->`) is copied verbatim — methodology briefs catalog, policies catalog, universal repo layout, phase-work protocol, status markers, reading protocol, architectural invariants, activity-log contract, universal conventions, glossary — **except for the starter-only members its catalogs name**. That zone lists what exists in *this* repository, so any entry pointing at a file the new project will not have (today: the `anonymize-log-references.md` policy bullet, and the `check-anonymization.sh` clause in the `bin/` layout bullet) comes out; left in, it is a `CLAUDE.md` reference to a missing file, which `bin/check-catalogs` fails closed on. The Hard rules section above the zones drops **Hard rule 3**, the starter-only anonymization rule, and the sentence introducing the rules is repaired to say the two survivors are universal. The `Project Context` zone (between `<!-- PROJECT_CONTEXT_START -->` and `<!-- PROJECT_CONTEXT_END -->`) is rewritten for the new project — the project's thesis, project-specific briefs list, project surfaces description, project conventions, and any project-specific skills.
- `briefs/BRIEF.md` — the entry-point brief for the new project. Pick a shape:
  - **Thesis-stub.** One short paragraph plus a pointer to `../CLAUDE.md#briefs-catalog`. Use when the project will quickly grow many topic briefs.
  - **Full single-document brief.** Opens with thesis + a catalog pointer, then continues with the long-form spec under H2 sections. Use when the project's brief is comprehensive and fits in one document.
  In both shapes the catalog itself lives in `CLAUDE.md`, not here.
- `briefs/<topic>.md` — written from the new project's spec, when the project is using the multi-file shape.
- `plan/INDEX.md` body — phase graph and table reflect the new project's phasing.
- `plan/phase-1.md` — fresh, project-specific. (Do not pre-build phases 2+. Decompose them when they become the next phase.)

### 2c. Do not transfer (template-specific)

- `.claude/skills/stamp/SKILL.md` — the new project doesn't need to stamp out more projects from itself, unless it explicitly wants to be a template too. (Note: `learn` and `teach` *are* carried over — they are universal cross-repo skills, not starter-specific.)
- `.agents/skills/stamp` — same reason. The starter-only `stamp` skill is intentionally absent from Codex's native skill discovery in derived projects.
- The starter template's own `plan/phase-1.md` (which is a placeholder for "decide what you're building") — replace it entirely with the new project's real Phase 1.
- The starter template's `example/` Python package and `tests/test_cli.py` — replace with the new project's surface, in whatever language(s) the project uses.
- `policies/anonymize-log-references.md`, `bin/check-anonymization.sh`, and `bin/anonymization-denylist.local.example` — starter-only: the rule exists because *this* template is public, not because of any methodology principle. Also drop the `bin/anonymization-denylist.local` line from the copied `.gitignore`, delete the `### check-anonymization.sh` entry from `bin/README.md`, remove its call from `bin/check`, and delete the "External / private-repo references" bullet from the copied `.claude/agents/code-critic.md`, which names both.
- `tests/test_methodology_toolchain_contract.py` — asserts on the `stamp` skill and the anonymization policy, neither of which the new project has.
- `briefs/eacp-pattern-map.md` and `briefs/methodology-treatise.md` — both are *about this repository*: one maps its structures onto a named pattern corpus, the other is its outward explanation. A derived project writes its own if it wants them.
- `LICENSE` and `.vscode/` — the new repository's licensing and editor settings belong to whoever owns it.
- This repository's `lessons/`, `lessons-archived/`, `user-actions/`, and `user-actions-archived/` entries — every ledger starts empty, with only a `.gitkeep` in each of the four so the directories survive the first commit.

If in doubt, ask: "does this file describe the methodology or a universally useful agentic capability, or does it describe the template itself?" Methodology and universal-capability files transfer; template-specific files don't.

**And prefer copying to omitting.** The list above is the whole set that stays behind; everything else under the universal surfaces travels. An unnecessary extra file in the new project is a nuisance that the next `sweep` removes. A missing one is a gate that will not start — `bin/check` fails closed on the first executable it cannot find, before it runs a single check.

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
.kickoff/
```

Do not gitignore the `.claude/` or `.codex/` *directories* themselves — the skill and agent definitions are committed source. Only runtime state is ignored.

Then create the empty directory shape:

```text
.claude/skills/kickoff/
.claude/skills/methodology/
.claude/skills/learn/
.claude/skills/teach/
.claude/skills/roles/
.claude/skills/sweep/
.claude/skills/sweep-planning/
.claude/skills/sweep-coding/
.claude/skills/demo/
.claude/skills/treatise/
.claude/skills/plain/
.claude/agents/
.codex/agents/
.agents/skills/        # (the eight skill entries here are directory symlinks
                       #  to ../../.claude/skills/<name>, created in Step 5)
briefs/
lessons/
lessons-archived/
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
     - `## Project-specific skills` — any beyond the universal eleven. Omit if none.

3. **`AGENTS.md`** — symlink to `CLAUDE.md`:
   ```bash
   ln -s CLAUDE.md AGENTS.md
   ```
   Codex and aider read `AGENTS.md`; Claude Code reads `CLAUDE.md`; the symlink keeps both honest from a single source.

4. **`LOG.md`** — create as a one-line stub:
   ```markdown
   # Activity Log
   ```
   `kickoff` will append the first START block.

5. **`README.md`** — didactic top-level for human readers. Mirror the template's section structure; write project-specific content. The README is the human's entry point; CLAUDE.md is the agent's.

### Step 5 — Port the universal harness bundle

Copy verbatim, then adapt project names and surface-specific build-gate commands:

- `.claude/skills/kickoff/SKILL.md`
- `.claude/skills/methodology/SKILL.md`
- `.claude/skills/learn/SKILL.md`
- `.claude/skills/teach/SKILL.md`
- `.claude/skills/roles/SKILL.md`
- `.claude/skills/sweep/SKILL.md`
- `.claude/skills/sweep-planning/SKILL.md`
- `.claude/skills/sweep-coding/SKILL.md`
- `.claude/skills/demo/SKILL.md`
- `.claude/skills/treatise/SKILL.md`
- `.claude/skills/plain/SKILL.md`
- `.claude/settings.json`
- `.claude/agents/phase-planner.md`
- `.claude/agents/plan-reviewer.md`
- `.claude/agents/phase-coder.md`
- `.claude/agents/code-critic.md`
- `.codex/agents/*.toml`
- `.agents/skills/{kickoff,methodology,learn,teach,roles,sweep,sweep-planning,sweep-coding,demo,treatise,plain}` (directory symlinks → `../../.claude/skills/<name>`)

Port the self-improvement machinery as the same atomic bundle:

- `briefs/harness-self-improvement.md`
- `policies/lessons.md`
- `bin/lessons` and `bin/check-catalogs`
- `tests/test_lessons.py` and `tests/test_check_catalogs.py`
- empty `lessons/` and `lessons-archived/` directories, each retained by a
  `.gitkeep`

Do not seed a new project's ledger with the template's lesson entries. Ledger
content is project state; only the schema, empty directories, capture loop, and
fitness checks transfer.

The executable transfer skills, this manual procedure, its acceptance
checklist, the methodology narrative, role-output contracts, catalogs, and
contract tests form one propagation boundary. Whenever a universal bundle
grows, update every path in the same change; leaving one path stale makes
derived repositories depend on which bootstrap procedure happened to run.

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
- `## Decomposition ledger (convention)` — the typed-note vocabulary (deferred-work notes, protocol notes, phase launch gates, insertion/renumbering records with the append-only decoder-ring rule, slice-outcome notes) copied from the template's `plan/INDEX.md`. Empty at bootstrap; it is where the plan's own history accumulates as dated, operator-attributed prose.

### Step 8 — Write Phase 1 in full; sketch Phase 2+ to general specificity

Write Phase 1 in full, then sketch every other major phase the brief surfaces. Major phases are enumerated up front — that's the project's roadmap. Only their sub-phases are JIT (drafted at parent open via the orchestrator's Step 1a). See [`methodology.md`](methodology.md) §6.

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
- **Decomposition** — if Phase 1 warrants sub-phases (multi-surface, multi-session), list the ones you can see at bootstrap; sub-phases beyond `phase-1.1` are JIT. If Phase 1 fits one session, declare "Monolithic (no sub-phase decomposition)" and skip this section.
- **Phase-level acceptance** — concrete, empirical, observable.
- **Brief refs** — links to every brief under `briefs/` that this phase implements.

Sub-phase files (`plan/phase-1.1.md`, etc.) follow the same frontmatter shape with `id: "1.1"` and `depends_on: ["1"]` (or sibling sub-phases). Bodies: Goal / Deliverables / Acceptance / Brief refs. **Only draft `phase-1.1.md` at bootstrap** if Phase 1 needs sub-phases at all; remaining sub-phases (`phase-1.2`, `phase-1.3`, …) get drafted at the close of their predecessor.

**Phase 2+ at bootstrap.** For every major phase the brief surfaces beyond Phase 1, draft a sketched `plan/phase-N.md` at lower fidelity:

- Frontmatter: same shape (`id`, `title`, `depends_on`, `informs`).
- **Goal** — one paragraph from the brief.
- **Deliverables** — a high-level list (the surfaces this phase will produce). May shift as upstream phases close and ripple their pinned decisions downstream — mechanical edits land in the same session, judgment-level ones surface as named follow-ups.
- **Acceptance** — scaffold-level criteria. Tighten at phase start via Step 1a; pinned values from upstream phases ripple in automatically.
- **Brief refs** — links to the briefs this phase implements.

**Do not draft sub-phases of Phase 2+ at bootstrap.** Sub-phase decomposition is JIT, one parent at a time. The sketched parent file is enough; its sub-phases appear when its row enters `⬅️`.

If the brief surfaces only Phase 1 (a small, single-phase project), no sketches are required. The dependency graph in `plan/INDEX.md` then contains a single node.

### Step 9 — Lay down the project's primary code surface

The template's example is Python. The new project may be Python, TypeScript, Rust, Go, Swift, Kotlin, a polyglot, or pure documentation.

**Decide first whether to adopt the `project/` convention** — isolating the
deliverable so that nothing inside it references anything above it. The
default for a single-deliverable project is opt-in: the artifact goes under
`project/` and the repository-owned toolchain wrappers select it internally.
The default for polyglot or multi-deliverable repos is opt-out: deliverable
directories live at the repo root as siblings.

Lay down (paths assume `project_isolation` enabled — prefix with `project/`; drop the prefix when disabled):

- The runtime/toolchain version declaration, package-manager file
  (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.), and
  lockfile with pinned tooling and minimum dependencies.
- A concise `README.md` for the artifact (self-contained, no `..` references).
- The package directory with empty modules.
- The test directory with one trivial test that passes (so the build gate has something to run on first kickoff).
- A `.gitignore` clause at the repo root for the language's build artifacts.

The repository owns setup, focused/full testing, runtime selection,
authoritative gates, and durable full-gate receipts as one bundle. Generate
`bin/setup`, `bin/test`, `bin/check`, and `bin/check-receipt` with the universal
interface — cwd-independent, atomic, and never inferring a runtime from the
host `PATH`; add a runtime wrapper such as `bin/python` when appropriate. Back them with the target's
version declaration, committed manifest, lockfile, and behavioral tests. A
profile that permits an explicit runtime override treats it as authoritative:
the override either passes a target-adapted dependency-chain load/run probe or
the command fails without fallback. Default and override paths apply identical
runtime selection to the probe and the real command. A mutable environment must
reject an override that points inside itself, because synchronization may
replace that interpreter while selecting it.

`bin/check` preserves `all|lint|format|test|policy` and delegates `test` to
`bin/test`. Immutable ecosystem modes include `uv --locked
--managed-python`, frozen Node installs, Cargo `--locked`, Go `-mod=readonly`,
or their equivalent. Make `kickoff`, the canonical agents, CLAUDE.md, and phase
acceptance use `./bin/test ...` for focused tests and `./bin/check all` for the
full claim; callers do not duplicate the command mappings.
Every `all` run captures a complete log and terminal metadata under the
gitignored `.kickoff/check-all/` tree. A success receipt is bound to the exact
candidate and environment fingerprint. The fingerprint is obtained through the
repository-selected runtime path and records the implementation, actual
version, resolved executable and base-executable identity and file digests,
machine, platform, and package-manager version; it never substitutes the
receipt helper's runtime or the declared version file. Candidate hashing stays
separate and does not absorb a venv or external runtime tree. The pre-push hook
reuses the receipt only for a clean current `HEAD`, and fails closed by running
the full gate on every miss, descriptor failure, or query error.

**A non-Python deliverable makes this a two-runtime contract, not a one-line
substitution.** The universal managers under `bin/` and the whole root `tests/`
suite are Python, so a TypeScript, Rust, or Go project carries a second,
committed governance environment — conventionally `tooling/`: runtime pin,
manifest, lockfile, and no source of its own. Everything above then doubles.
`bin/setup` provisions both from their lockfiles and probes both before
reporting success. `bin/test` routes by path prefix — the deliverable's path to
its own runner with the prefix stripped, `tests/...` to pytest — and refuses an
invocation that mixes the two rather than guessing. `bin/check` splits `lint`
and `format` per runtime while still emitting exactly one `CHECK <mode> PASS`
line per mode, the way the policy lane emits one after its sub-gates. Each
language gets a helper beside `bin/_python-toolchain` with the same contract —
prerequisite check, contract members, an authoritative absolute-path override
that never falls back, and a real dependency probe — and each helper takes its
own root variable, because a single `project_root` no longer says enough. Pin
the package manager in the manifest and invoke it through the launcher that
honors the pin, so no caller depends on what happens to be installed. And pin
the language version to what the *lint stack* supports rather than to the newest
release: a type-checker release its linter has not adopted yet turns the lint
gate into a load-time crash, which reads as a broken repository rather than as a
version conflict.

### Step 10 — Sanity-check the bootstrap

Before declaring the bootstrap complete, verify:

- `readlink AGENTS.md` returns `CLAUDE.md`.
- `bin/check-catalogs` accepts the initial idle ledger with exactly one `⬅️`
  and resolves every tracked internal Markdown link.
- `head -1 LOG.md` is `# Activity Log`.
- `ls .claude/agents/` lists exactly the four canonical role files.
- Each of `.claude/skills/{kickoff,methodology,learn,teach,roles,sweep,sweep-planning,sweep-coding,demo,treatise,plain}/`
  contains `SKILL.md`, and each corresponding `.agents/skills/<name>` entry
  is a directory symlink to `../../.claude/skills/<name>`.
- `bin/lessons validate`, `bin/check-catalogs`, and their behavioral tests
  pass against the empty initial ledger and Phase 1 status table.
- `bin/kickoff-config show` succeeds and `kickoff.yaml` contains valid `role_models`, `role_timeouts`, and `research_budgets` sections.
- `.claude/settings.json` sets `worktree.bgIsolation` to `none`; explicitly requested worktrees remain available.
- `bin/setup` works from outside the repository and provisions only the
  committed runtime and dependencies, then passes a real deliverable-and-tool
  dependency-chain probe.
- `bin/test` runs deliverable and universal tooling tests; a focused
  repo-relative selection runs only that selection.
- `bin/check test` delegates to `bin/test` before any live venue probe.
- A valid explicit runtime override drives setup, probing, testing, gates, and
  the runtime wrapper; an invalid or probe-failing override exits nonzero
  without trying the repository default or an ambient runtime.
- The new `CLAUDE.md` catalogs are bidirectionally complete, and every tracked
  repository-internal Markdown link resolves.
- `plan/phase-1.md`'s `Brief refs` section lists at least one brief, and each listed brief exists.
- `bin/check all` runs from outside the repository root and passes on the trivial seeded code, including the universal methodology tests.
- A successful full gate leaves a verifiable candidate/environment receipt and
  complete log; dirty, changed, corrupt, non-`HEAD`, and query-error pre-push
  cases all run the full gate.

The first `kickoff` invocation should pick up Phase 1's `⬅️` row, flip it to `🚧`, and append a START block to `LOG.md`. If any of those three actions fails, the bootstrap is incomplete — a path mismatch or a missing skill is the typical culprit.

---

## 4. Per-project adaptation axes

The bootstrap is the same shape every time. The variation is in:

| Axis                          | Examples of project-specific choices                          |
| ----------------------------- | ------------------------------------------------------------- |
| **Surfaces**                  | web + back-end + IaC; pure Python lib; mobile + API; docs     |
| **Toolchain implementation**  | repository-owned setup/test/check/runtime bundle using pinned, locked ecosystem commands |
| **Languages in play**         | Python / TS / Rust / Go / Swift / Kotlin / polyglot           |
| **Deployment story**          | AWS / Cloudflare / Vercel / app stores / static / none        |
| **Per-project invariants**    | Cost ceilings; license policy; privacy boundaries; FOSS-only  |
| **Per-project skills**        | Domain-specific workflows on top of `kickoff`                |
| **Kickoff execution config** | Human-editable `kickoff.yaml`: separate model/effort fields, target-local timeout calibration, and per-role research budgets, per the role, timeout, and research-authority policies |

When adapting, edit these files (and only these) to reflect those choices:

- `CLAUDE.md` — reflects all of them.
- `plan/INDEX.md` Cross-Cutting Concerns — duplicates the invariants from `CLAUDE.md`.
- `bin/setup`, `bin/test`, `bin/check`, `bin/check-receipt`, runtime wrapper,
  version declaration, manifest, lockfile, and their behavioral tests — one
  atomic implementation.
- `.claude/skills/kickoff/SKILL.md` and the four canonical agents — call the
  canonical focused/full mappings.
- `bin/kickoff-tree-id`, `bin/kickoff-evidence`, and
  `policies/orchestration-evidence.md` — preserve candidate-bound review,
  revision packets, implementation-final-gate evidence, and the separate
  post-bookkeeping handoff gate.

Anything else that needs to change probably indicates a bootstrap deviation that should be questioned, not normalized.

---

## 5. Common pitfalls

These bite every bootstrap; flag them before they happen.

- **Status markers in two places.** The status of a phase lives in `plan/INDEX.md`'s phase table and **nowhere else**. Per-phase frontmatter is `id / title / depends_on / informs` — no `status` field.
- **Document drift.** `CLAUDE.md`'s catalogs must be bidirectionally complete,
  and tracked internal Markdown links must resolve. Catalog membership alone
  does not prove that links inside transferred documents survived adaptation.
- **`AGENTS.md` as a real file instead of a symlink.** A duplicate file drifts. Make it a symlink and verify with `readlink`.
- **Reusing template-specific invariants.** "The example Python project must lint clean" is a template rule. Don't carry it into a project that has no Python.
- **Filling in Phase 2+ at bootstrap.** Tempting and wrong. Phase 1 reality is the input to Phase 2's design.
- **Agent name drift.** The four canonical roles must be named exactly `phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`. `kickoff` invokes them by name. A typo silently breaks the orchestrator's ability to delegate.
- **Editing `LOG.md` by hand.** History is owned by `kickoff`. If a phase pauses mid-way, `kickoff` writes the pause-reason END block; do not retroactively edit prior entries.
- **Skipping the brief.** The bootstrap assumes a brief exists. Bootstrapping into an empty `briefs/` produces scaffolding for a project nobody has decided yet — the orchestrator will plan against air.

---

## 6. Acceptance — "the new repo is ready for `kickoff`"

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
[ ] plan/INDEX.md exists with: graph block (enumerating every major phase
    the brief surfaces), status legend, phase table containing one row per
    major phase with exactly one row whose status is ⬅️ (Phase 1), cross-
    cutting concerns (mirroring CLAUDE.md), critical-files map
[ ] plan/phase-1.md exists in full, with frontmatter (id "1", depends_on []),
    Goal / Decomposition / Acceptance / Brief refs sections
[ ] plan/phase-N.md exists for every major phase N≥2 the brief surfaces,
    sketched to general specificity (frontmatter + Goal + high-level
    Deliverables + scaffold Acceptance + Brief refs). If the brief surfaces
    only Phase 1, no sketches are required.
[ ] Only the in-flight major phase has sub-phase files drafted, and only as
    many as the orchestrator's Step 1a/9a have produced so far. At bootstrap
    that's `plan/phase-1.1.md` only (when Phase 1 warrants sub-phases) — no
    `phase-1.2.md`, no `phase-2.1.md`. Subsequent sub-phases are JIT.
[ ] .claude/skills/kickoff/SKILL.md exists, adapted for this project's
    surfaces and build gates
[ ] .claude/skills/methodology/SKILL.md exists (verbatim from template)
[ ] .claude/skills/learn/SKILL.md exists (verbatim from template)
[ ] .claude/skills/teach/SKILL.md exists (verbatim from template)
[ ] .claude/skills/roles/SKILL.md exists (verbatim from template)
[ ] .claude/skills/sweep/SKILL.md exists (verbatim from template)
[ ] .claude/skills/sweep-planning/SKILL.md exists (verbatim from template)
[ ] .claude/skills/sweep-coding/SKILL.md exists (verbatim from template)
[ ] .claude/skills/demo/SKILL.md exists (verbatim from template)
[ ] .claude/skills/treatise/SKILL.md exists (verbatim from template)
[ ] .claude/skills/plain/SKILL.md exists (verbatim from template)
[ ] .claude/skills/stamp/ does NOT exist (starter-only meta-skill)
[ ] .claude/agents/{phase-planner,plan-reviewer,phase-coder,code-critic}.md
    exist, adapted for this project
[ ] .codex/agents/*.toml mirrors exist
[ ] .agents/skills/{kickoff,methodology,learn,teach,roles,sweep,sweep-planning,sweep-coding,demo,treatise,plain} exist as directory
    symlinks to ../../.claude/skills/<name> (the canonical skill directory)
[ ] .agents/skills/stamp does NOT exist (starter-only, must not propagate)
[ ] .claude/settings.json sets worktree.bgIsolation to none while explicit
    worktrees remain available
[ ] bin/kickoff-config is executable; kickoff.yaml validates all three sections; scoped updates
    preserve human comments and `extensions` data; `.kickoff/` is gitignored
[ ] bin/kickoff-tree-id and bin/kickoff-evidence are executable; candidate
    identity and run-scoped evidence behavioral tests pass
[ ] bin/lessons and bin/check-catalogs are executable; a .gitkeep exists in
    each of lessons/, lessons-archived/, user-actions/, and
    user-actions-archived/, and none of the four carries an entry copied from
    the template; ledger, document-link, and phase-lifecycle fitness tests pass
[ ] Every executable bin/check requires is present and executable:
    kickoff-tree-id, kickoff-evidence, kickoff-config, check-receipt,
    execution-telemetry, check-execution-dashboards, check-harness-parity,
    check-toolchain-callers, lessons, treatise, check-catalogs,
    check-hooks-installed, check-shell-syntax, new-name. bin/check fails closed
    on the first one missing, before any gate runs — this is the fastest way to
    catch an incomplete transfer
[ ] lib/agentic_starter/ exists (bin/execution-telemetry and
    bin/check-execution-dashboards import it); reports/execution/ carries
    index.html, index-data.js, and assets/, and
    bin/check-execution-dashboards reports 0 phases against the fresh archive
[ ] bin/check-harness-parity passes: one .agents/skills mirror per canonical
    skill, no orphans, one .codex/agents/*.toml per canonical role
[ ] policies/anonymize-log-references.md, bin/check-anonymization.sh, and
    tests/test_methodology_toolchain_contract.py do NOT exist, and no file in
    the new repo links or names them — including CLAUDE.md's Hard rules
    (rule 3 is gone) and its Policies catalog
[ ] bin/setup, bin/test, bin/check, bin/check-receipt, bin/install-hooks, and
    bin/check-hooks-installed are executable;
    the language runtime wrapper exists when applicable; .githooks/pre-push
    reuses only an exact verified receipt and otherwise calls bin/check; hook
    installation remains explicit and opt-in, with the opt-in-aware liveness
    witness in the check policy lane
[ ] Runtime version metadata, package manifest, and lockfile form a complete
    language profile; no workflow assumes a versioned runtime binary on PATH
[ ] For a non-Python deliverable: tooling/ carries a committed governance
    environment; bin/setup provisions and probes both runtimes; bin/test routes
    by path prefix and refuses an invocation spanning both suites; bin/check
    splits lint and format per runtime while still emitting one
    CHECK <mode> PASS line per mode; every language version pin sits inside the
    range its lint and type tooling support, with the constraint written down
[ ] tests/test_toolchain_entrypoints.py, tests/test_check.py,
    tests/test_check_receipt.py,
    tests/test_install_hooks.py, tests/test_check_hooks_installed.py,
    tests/test_kickoff_config.py,
    tests/test_kickoff_tree_id.py, tests/test_kickoff_evidence.py,
    tests/test_lessons.py, tests/test_check_catalogs.py,
    tests/test_treatise.py, tests/test_new_name.py, tests/test_shell_syntax.py,
    tests/test_toolchain_callers.py, tests/test_mirror_parity.py,
    tests/test_research_authority.py, tests/test_execution_telemetry.py, and
    tests/test_execution_dashboard.py pass through bin/test
[ ] Every file in policies/ from the template exists, with project-name
    references updated
[ ] No template-specific skills, briefs, or example code remain in the new
    repo (no example/, no .claude/skills/stamp/)
[ ] ./bin/check all runs from outside the repo and passes on the seeded code
[ ] First `kickoff` invocation (`/kickoff` in Claude Code; `$kickoff` in Codex)
    successfully picks up Phase 1's ⬅️ row,
    flips it to 🚧, and appends a START block to LOG.md
```

The last item is the operational test. Until it passes, the bootstrap is not done.

---

## 7. Pointers

- **The template (this repo) is itself the canonical donor.** Future versions of the bootstrap procedure should be updated *in the template first*, then propagated to derived projects' copies of `agentic-bootstrap.md` on next opportunity.
- **The methodology** is documented in [`methodology.md`](methodology.md) (sibling brief, copied verbatim into every derived project).
- **The cross-harness contract** is one canonical home per skill and role definition, with thin pointers from every other harness and a parity check that rejects a missing, copied, or orphaned mirror. Adding a third or fourth harness follows that contract rather than forking the definitions.
