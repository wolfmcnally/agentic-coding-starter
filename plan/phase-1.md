---
id: "1"
title: "Adopt the template for your project"
depends_on: []
informs: []
---

# Phase 1 — Adopt the template for your project

**Goal**: turn this template into a real project that has a brief, a phased plan, and a first slice of code worth `/kickoff`'ing again. After this phase lands, the repo no longer looks like the template — it looks like *your* project, with its own name, its own brief, its own Phase 2.

This phase is a placeholder. It exists so the first `/kickoff` invocation has a row to pick up, and so a human exploring the template can experience the whole orchestrator cycle end-to-end against a small, real piece of work.

You have two options for this phase:

## Option A — You're using this repo as a template for a new project

The right tool is the `/stamp` skill, not `/kickoff`. Type:

```
/stamp ~/path/to/new-project "one-line description of what to build"
```

`/stamp` will create the new directory, transfer the template's structural files, customize them for your project, and leave you with a project ready to `/kickoff` from a real Phase 1. You can return here to this repo afterward and either close out Phase 1 (`✅ Completed` — "adoption happened via /stamp") or leave it `⬅️ Next` for the next user.

## Option B — You're using this repo directly to build something here

Replace Phase 1's content with the real first phase of your real project. Concretely:

1. **Edit [`../briefs/BRIEF.md`](../briefs/BRIEF.md)** to describe your project, not the template. The template's BRIEF.md is itself an example of a thesis-stub-style entry-point brief; rewrite the H1, the thesis paragraph, sections 1–8 to describe what you're actually building.
2. **Decide Phase 1's real goal** for your project. Some examples:
   - For a CLI tool: "stand up the package skeleton, the CLI entry point, and one subcommand end-to-end."
   - For a web app: "stand up the dev server, the routing layer, and one read-only page."
   - For a library: "land the public API surface (types + signatures only) plus one fully-implemented function with tests."
3. **Rewrite this file (`plan/phase-1.md`)** with the real goal, deliverables, and acceptance criteria. Use the structure below (Goal / Decomposition / Deliverables / Acceptance / Brief refs) as a template.
4. **Update [`INDEX.md`](INDEX.md)**'s phase table title and dependency graph to match.
5. **Run `/kickoff`** to start the real Phase 1.

## Decomposition

This phase is small enough that it does not need sub-phases. If you discover it should be split (e.g., "Phase 1.1: rewrite BRIEF.md" and "Phase 1.2: rewrite phase-1.md"), feel free to split — that is the methodology working as designed (step 11, "stay agile").

## Deliverables

For Option A:

- A new project directory at the location given to `/stamp`, satisfying every checkbox in [`../briefs/agentic-bootstrap.md` §6 "Acceptance"](../briefs/agentic-bootstrap.md).

For Option B:

- `../briefs/BRIEF.md` rewritten to describe the user's real project.
- `../plan/phase-1.md` (this file) rewritten with a real Phase 1 of the user's project.
- `../plan/INDEX.md`'s phase table title and dependency graph updated to match.
- Any briefs the new project's Phase 1 references exist under `briefs/` (write the briefs first; the orchestrator should not be planning against nothing).
- Optionally: the template-specific `example/` Python package replaced with the user's real surface skeleton, in whatever language is correct for the project.

## Acceptance

For Option A:

- `ls ~/path/to/new-project/` (or the named directory) returns a populated project that passes every check in the bootstrap acceptance list ([`../briefs/agentic-bootstrap.md` §6](../briefs/agentic-bootstrap.md)).
- Manual check: a `cd` into the new project and `/kickoff` picks up its real Phase 1 (not this placeholder).

For Option B:

- `head -1 ../briefs/BRIEF.md` shows the user's project title, not "Agentic Coding Starter Template".
- `head -3 plan/phase-1.md` shows the user's real Phase 1 title in the frontmatter.
- The example Python project's gates still pass (`cd project && uv run ruff check example tests && uv run ruff format --check example tests && uv run pytest -q`), unless the user has replaced it with a different surface — in which case the new surface's gates pass.
- `/kickoff phase 1` invoked after the rewrite picks up the user's real Phase 1 and walks through plan → plan-review → code → code-review → build for it.

## Brief refs

- [`../briefs/BRIEF.md`](../briefs/BRIEF.md) — overall product brief for this template (will be rewritten in Option B).
- [`../briefs/methodology.md`](../briefs/methodology.md) — the eleven-step methodology this phase ultimately serves.
- [`../briefs/agentic-bootstrap.md`](../briefs/agentic-bootstrap.md) — required reading for Option A; describes what `/stamp` does.

## Out of scope

- Sub-phases of Phase 2 and beyond. Per [`../briefs/methodology.md`](../briefs/methodology.md) §6, major phases the brief surfaces *are* enumerated at bootstrap (sketched to general specificity); only their sub-phases are JIT, drafted at parent open via `/kickoff` Step 1a. Sketched Phase 2+ files belong in the project that emerges from Phase 1, not in this placeholder.
- Customizing every brief/policy file individually for the new project. The template's policies are universal by design; they don't need rewriting. The briefs that need rewriting are `BRIEF.md` (always) and any topic-specific briefs the new project introduces.
