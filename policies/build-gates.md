# Policy: Repository-Owned Toolchain Contract

Every methodology-following repository owns one canonical, atomic interface
for provisioning and verifying itself:

```bash
./bin/setup
./bin/test [focused test arguments...]
./bin/check [all|lint|format|test|policy]
```

A language profile may add a repository-selected runtime entry point such as
`./bin/python`. The repository—not an agent prompt, shell history, IDE task, or
machine-global environment—defines what these commands mean.

## Atomic bundle

The contract is one unit:

- `bin/setup`, `bin/test`, and `bin/check`;
- any runtime entry point such as `bin/python`;
- the runtime-version file, package manifest, and lockfile;
- behavioral tests for the entry points;
- this policy and every workflow, agent, hook, and document that calls them.

A partial transfer is stale and blocking. Copying `bin/check` without its
version pin, teaching a raw test command without `bin/test`, or changing a
lockfile without checking the wrappers is not an adoption of the contract.
`learn`, `teach`, and `stamp` assess and migrate the entire bundle atomically
while preserving the target repository's language, version policy, package
manager, and dependencies.

## Ownership boundary

The host supplies only the ecosystem bootstrap manager (`uv`, `cargo`, `pnpm`,
and so on). The repository owns:

- the runtime version or accepted version range;
- dependency versions through committed metadata and a lockfile;
- setup, focused-test, and authoritative-gate command mappings;
- the set of repository tests and policy checks.

No caller assumes a versioned runtime executable such as `python3.12` is on
`PATH`. If the bootstrap manager is unavailable, an entry point reports that
exact prerequisite failure. An invalid explicit tool override fails rather
than falling through to an ambient executable.

## Interface

### `bin/setup`

`./bin/setup` provisions or synchronizes the committed environment in
lock-preserving mode. It is cwd-independent, idempotent, rejects unexpected
arguments, and fails if required metadata, the runtime pin, or the lockfile is
missing or stale.

### `bin/test`

`./bin/test` with no arguments runs every repository test, including
methodology/tooling tests outside the deliverable. Arguments are forwarded to
the underlying test runner for focused iteration, with paths interpreted
relative to the repository root. It uses the same locked environment as the
full gate and preserves the test runner's exit status.

### `bin/check`

`./bin/check` with no arguments is identical to `./bin/check all`. Universal
named modes are:

- `all` — every authoritative repository gate, in deterministic order;
- `lint` — static lint checks;
- `format` — formatting checks without rewriting files;
- `test` — delegates to `./bin/test`;
- `policy` — deterministic repository-policy checks that are not language
  lint or tests.

A project may add named modes but does not remove or weaken `all`. Unknown
modes and extra arguments are usage errors. Every entry point preserves child
failures, emits unambiguous terminal results where applicable, hides no failure
behind a pipe or fallback, and performs no commit, push, deploy, or other
shared-state mutation.

### Runtime entry points

When a repository exposes a language runtime for scripts or diagnostics, the
entry point selects the same pinned, locked environment. In this starter,
`./bin/python [arguments...]` is the only supported way for methodology
callers to request the project interpreter. It never assumes `python`,
`python3`, or a minor-version binary on the host `PATH`.

## Language profiles

The interface is universal; implementations are language-specific:

- Python/uv: committed `.python-version`, `pyproject.toml`, and `uv.lock`;
  `uv sync --locked --managed-python` for setup and
  `uv run --locked --managed-python` for execution;
- Node: the package manager selected by the committed lockfile, with
  immutable/frozen dependency setup and package scripts behind the wrappers;
- Rust: the pinned toolchain when applicable and Cargo commands with
  `--locked`;
- Go: the declared Go version and module reads with `-mod=readonly`;
- other ecosystems: their equivalent version selection and lock-preserving
  modes.

Recurring tools belong in committed development dependencies. Do not use
ephemeral dependency injection such as an unpinned `uv run --with ...` for a
repository-owned gate.

## Focused gates and phase plans

The planner's Build Gate Sequence starts with focused invocations through
`./bin/test` or another repository-owned focused mode, then ends with
`./bin/check all`. A raw ecosystem command is acceptable only for a narrow
operation the repository interface does not represent; it must still use
committed metadata and lock-preserving mode.

The coder may run focused checks repeatedly. The orchestrator independently
runs the final sequence after review. Evidence from a delegated or sandboxed
environment proves only that environment; host-dependent acceptance is
verified on the host.

## Lifecycle hooks

Tracked hooks may call `./bin/check all`, but installation is opt-in. Hooks
contain no duplicate toolchain command list. Their installer is idempotent,
reports conflicting configuration, and requires an explicit force option to
replace it.

## Verification

Behavioral tests prove:

- invocation from outside the repository root;
- exact setup, full-test, focused-test, runtime, and gate mappings;
- pinned runtime and locked/frozen toolchain invocation;
- clear failure when prerequisites or any bundle member is absent;
- exact child-status propagation;
- strict argument handling and stable terminal output;
- `bin/check test` delegation to `bin/test`.

After changing any bundle member or caller, run `./bin/test` for focused
wrapper coverage, run `./bin/check all`, and search for stale raw setup or test
commands that bypass the repository interface.
