# Policy: Repository-Owned Build Gates

Every methodology-following repository owns one canonical entry point for its
authoritative automated checks:

```bash
./bin/check
```

The repository—not an agent prompt, a shell history, an IDE task, or a
machine-global environment—defines what that command runs. Phase plans may add
focused checks for the surface they change, but the final full-suite claim
always goes through the repository entry point.

## Why the entry point belongs in the repository

Raw lint, format, type, and test commands tend to be copied into `CLAUDE.md`,
skills, agent definitions, phase files, and CI. Those copies drift as soon as a
package moves, a test root is added, or an option changes. A checked-in
executable gives every caller the same answer and makes the gate itself
testable.

The canonical entry point:

- resolves the repository root from its own location, so it works from any
  current directory;
- invokes the toolchain and lockfile declared by the repository;
- fails closed when the toolchain, metadata, or lockfile is missing or stale;
- preserves the failing command's non-zero exit status;
- emits an unambiguous terminal result for every gate it runs;
- emits a terminal result for the public composite mode as well as each child
  gate, so callers never infer aggregate success from the last child alone;
- never hides a failure behind a formatter, pipe, fallback, or reassuring
  default;
- performs no commit, push, deploy, or other shared-state mutation.

## Interface

`./bin/check` with no arguments is identical to `./bin/check all`.

The universal named modes are:

- `all` — every authoritative repository gate, in deterministic order;
- `lint` — static lint checks;
- `format` — formatting checks without rewriting files;
- `test` — the automated test suite;
- `policy` — deterministic repository-policy checks that are not language
  lint or tests.

A project may add named focused modes, but it does not remove or weaken
`all`. Unknown modes and extra arguments are usage errors, not aliases for a
partial run.

Each mode exits:

- `0` only when every selected gate passed;
- the selected gate's non-zero status when a gate failed;
- `2` for invalid invocation.

## Toolchain ownership

The gate uses the project's committed metadata and lockfiles:

- Python/uv: `uv run --locked`;
- Node: the package manager selected by the committed lockfile, with immutable
  install/frozen-lockfile behavior in setup or CI;
- Rust: Cargo commands with `--locked`;
- Go: module reads with `-mod=readonly`;
- other ecosystems: their equivalent lock-preserving mode.

An ambient executable may bootstrap the committed environment (`uv`, `cargo`,
`pnpm`, and so on), but it may not silently choose dependency versions or a
different project environment. If the bootstrap executable is unavailable,
the gate reports that exact prerequisite failure.

An explicit tool override, when a project offers one, is authoritative: an
invalid override fails rather than falling through to a different executable.

## Focused gates and phase plans

The planner's Build Gate Sequence begins with any narrow checks useful for fast
feedback, then ends with `./bin/check all`. A focused command is not a
substitute for the full repository gate unless the phase explicitly documents
why the untouched surfaces cannot be affected and the governing policy permits
that narrower claim.

The coder may run focused checks repeatedly while implementing. The
orchestrator independently runs the final sequence after code review. Gate
output from a delegated or sandboxed environment is evidence only for that
environment; host-dependent acceptance is verified by the orchestrator on the
host.

## Lifecycle hooks

Tracked hooks may call `./bin/check all`, but hook installation is opt-in.
Cloning or stamping a repository must not silently rewrite a user's Git
configuration. A repository-provided installer must be idempotent, must report
an existing conflicting hook configuration, and must require an explicit force
option before replacing it.

Hooks are an additional enforcement seam, not a second definition of the
gates. They call the canonical entry point and contain no duplicate toolchain
command list.

## Verification

The gate wrapper itself has behavioral tests proving:

- invocation from outside the repository root;
- deterministic mode-to-command mapping and ordering;
- locked/frozen toolchain invocation;
- clear failure when prerequisites or lockfiles are absent;
- exact non-zero status propagation;
- rejection of invalid modes and extra arguments;
- stable PASS/FAIL terminal output.

After changing the gate or its callers, run `./bin/check all` and search the
repository for stale copies of the superseded full-suite command.
