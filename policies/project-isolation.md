# Policy: Project Isolation (`project/` convention)

When a repo has a **single primary deliverable** — one CLI, one library, one service, one document — that deliverable lives under `project/`. Nothing inside `project/` references anything outside it. The rest of the repo (briefs, policies, plan, LOG, agent definitions, scaffolding skills) is project *governance metadata* that surrounds and builds the project but is not itself part of the deliverable.

This makes the deliverable **submodule-ready**: once it's ready to be reused, `project/` can be extracted into its own repository and added back as a Git submodule. The scaffolding continues to operate on it normally, and the deliverable becomes independently consumable.

## When this policy applies

Applies to repos with **one primary deliverable**:

- Single-language CLI, library, or service
- A book, document, research artifact, or report
- A model, a dataset pipeline, a single web app, a single mobile app

Does **not** apply to repos with multiple co-equal deliverables:

- Polyglot mono-repos (`web/` + `lambda/` + `cdk/` as siblings)
- Multi-language SDKs (`python-sdk/` + `js-sdk/` + `rust-sdk/`)
- Catalogs (`books/` containing many books)

For multi-deliverable repos, treat each top-level sibling like a `project/` for the boundary rule below: nothing in `web/` references `lambda/`, etc. The convention generalizes; the literal directory name doesn't.

## What goes inside `project/`

Everything that is *the deliverable*:

- The package metadata file (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, …)
- The runtime/toolchain version declaration (`.python-version`,
  `rust-toolchain.toml`, `packageManager`, declared Go version, …)
- The lockfile (`uv.lock`, `package-lock.json`, `Cargo.lock`, `go.sum`)
- Source code (the package directory)
- Tests (the test directory)
- Build outputs (gitignored)
- The artifact's own configuration (`tsconfig.json`, `ruff.toml` if separate, etc.)
- The deliverable's own `.gitignore` listing the language's build artifacts, virtual envs, tool caches. When `project/` is extracted as a submodule it carries these ignores with it.
- An optional `README.md` for the artifact — usually concise; the repo's top-level `README.md` is the didactic one

## What stays at the repo root

Project *governance metadata* — the scaffolding that builds and supervises the project:

- `briefs/` — design library
- `policies/` — rules every phase honors (including this one)
- `plan/` — phased execution plan
- `LOG.md` — append-only activity log
- `CLAUDE.md` / `AGENTS.md` — top-level agent guidance
- `.claude/` / `.codex/` — agent definitions, skills, harness mirrors
- `README.md` — didactic top-level for human readers
- `.gitignore` — editor/OS files and agentic harness runtime state only. The deliverable's language-specific build-artifact ignores live in `project/.gitignore`.

These are *about* the project but not *part* of it. The plan describes the work; the work happens under `project/`. The LOG records what was done; the doing happened under `project/`.

## The boundary rule

The single load-bearing rule of this policy:

> **Nothing inside `project/` references anything outside `project/`.**

Concrete consequences:

- No source file under `project/` imports from `../briefs/`, `../policies/`, or `../plan/`.
- No `pyproject.toml` (or analogous) field names a path outside `project/`.
- No test fixture loads data from `../*`.
- No `README.md` inside `project/` links to `../briefs/` or `../policies/`.
- No script inside `project/` `cd`s up the tree.

Cross-boundary references in the *other* direction (root referencing `project/`) are fine and expected:

- `CLAUDE.md` says "the project lives under `project/`".
- `plan/phase-1.md` says "modify `project/example/cli.py`".
- Root `bin/setup`, `bin/test`, `bin/check`, and any runtime wrapper select
  `project/` and invoke its native toolchain.

## Toolchain entry points from the root

The repository owns one atomic interface:

```bash
./bin/setup
./bin/test [focused arguments...]
./bin/check all
```

The wrappers resolve the repository root from their own location, select the
deliverable's runtime declaration, manifest, and lockfile, and invoke its
native toolchain. They may use `cd project` or an ecosystem's explicit project
selector; callers do not depend on that implementation detail.

The root wrapper is preferred because:

- every human, agent, hook, and CI job calls the same checked-in mappings;
- the command works from any current directory;
- setup, runtime selection, lock enforcement, gate ordering, and failure
  reporting remain synchronized;
- root methodology tests and deliverable tests cannot drift into separate
  undocumented command lists.

Focused repository tests use `./bin/test <repo-relative selection>`. A
developer working on the independently extracted `project/` may use the
artifact's documented native commands; the parent repository's wrappers are
governance metadata and intentionally stay outside the deliverable.

Root-level methodology machinery is a separate surface, not part of the
isolated deliverable. In this starter, root `tests/` exercises the atomic
toolchain wrappers, `bin/install-hooks`, and `bin/kickoff-config`; `bin/test`
runs those tests alongside `project/tests/`. Derived projects carry the
universal machinery tests and adapt the complete contract during `stamp`.

## Extracting `project/` as a submodule

When the artifact is ready to be reused outside this repo:

1. `cd project`
2. `git init` (if not already a repo)
3. `git add . && git commit -m "initial: extracted from <parent-repo>"`
4. Push to a new remote.
5. In the parent repo: `git rm -rf project` (or back it up first), then `git submodule add <new-remote> project`.
6. Commit the submodule pointer.

After step 6, the parent repo's `project/` is a submodule. The scaffolding continues to operate on it — agents Read and Write project files normally — and the deliverable is now independently consumable by other repos.

## Verification

A clean state satisfies:

```bash
# No file inside project/ references parent-tree governance paths
grep -RIn '\.\./\(briefs\|policies\|plan\|LOG\|CLAUDE\|AGENTS\|README\)' \
  --include='*.py' --include='*.toml' --include='*.md' --include='*.yaml' --include='*.yml' \
  project/ 2>/dev/null && echo "BOUNDARY VIOLATION" || echo "boundary OK"

# project/ has its own metadata file
ls project/pyproject.toml project/package.json project/Cargo.toml project/go.mod 2>/dev/null | head -1 \
  || echo "no metadata file in project/"

# The repository-owned full gate passes
./bin/check all
```

## When to opt out

A project may decline this policy at `stamp` time when:

- The project is intrinsically polyglot or multi-deliverable.
- The project's tooling deeply assumes the deliverable lives at the repo root (rare but real for some IDE workspaces and CI templates).
- The repo *is* the deliverable as a whole — e.g., a documentation repo where `src/` and `theme/` at the root are both load-bearing.

In those cases, the deliverable lives at the repo root, scaffolding lives at the repo root alongside it, and this policy is replaced by the softer rule: *"deliverable directories don't reference each other's internals."*

`stamp` asks about this at bootstrap. The default for single-language CLI/library/service projects is *opt in*. The default for polyglot or web+infra projects is *opt out*.
