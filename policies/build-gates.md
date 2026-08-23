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

- `bin/setup`, `bin/test`, `bin/check`, and the full-gate receipt manager;
- any runtime entry point such as `bin/python`;
- any shared runtime resolver or dependency-chain probe used by those entry
  points;
- the runtime-version file, package manifest, and lockfile;
- behavioral tests for the entry points;
- this policy and every dependency-bearing operational caller, generated
  command, tracked hook, workflow, agent, and active instruction that calls
  repository code.

A partial transfer is stale and blocking. Copying `bin/check` without its
version pin, teaching a raw test command without `bin/test`, or changing a
lockfile without checking the wrappers is not an adoption of the contract.
`learn`, `teach`, and `stamp` assess and migrate the entire bundle atomically
while preserving the target repository's language, version policy, package
manager, and dependencies.

Adaptation may change syntax and fixtures to fit the target, but it may not
weaken coverage. Behavioral execution is the minimum test floor: source-text
assertions may supplement it, but do not replace tests that invoke the
entrypoints with controlled toolchain stubs and prove routing, ordering,
working-directory independence, child-status propagation, and fail-closed
selection.

## Ownership boundary

The host supplies only the ecosystem bootstrap manager (`uv`, `cargo`, `pnpm`,
and so on). The repository owns:

- the runtime version or accepted version range;
- dependency versions through committed metadata and a lockfile;
- setup, focused-test, and authoritative-gate command mappings;
- the set of repository tests and policy checks.

No caller assumes a versioned runtime executable such as `python3.12` is on
`PATH`. If the bootstrap manager is unavailable, an entry point reports that
exact prerequisite failure. A language profile may expose an explicit runtime
override for compatibility testing. That override is authoritative: an invalid
executable, incompatible runtime, environment-sync failure, or dependency
probe failure stops the command without falling through to the repository
default or an ambient executable.

Runtime resolution validates capability, not identity. A version string or
executable bit is insufficient: before an entry point makes a success claim,
it runs a target-adapted load/run probe through the selected locked environment
that exercises the deliverable import or startup path and its recurring test
and gate dependencies. The probe and the real command receive identical
runtime-selection arguments.

## Interface

### `bin/setup`

`./bin/setup` provisions or synchronizes the committed environment in
lock-preserving mode. It is cwd-independent, idempotent, rejects unexpected
arguments, and fails if required metadata, the runtime pin, or the lockfile is
missing or stale. After synchronization, it runs the dependency-chain probe;
`SETUP PASS` means both provisioning and the probe succeeded.

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

Every `all` run starts durable, gitignored run metadata and captures its complete
output under `.kickoff/check-all/`. Success writes a receipt bound to the exact
`bin/kickoff-tree-id` candidate, an environment fingerprint, and the log digest;
running, failed, identity-error, and candidate-drift runs retain terminal
metadata but never create a reusable receipt. A log/storage failure remains an
explicit failure and never creates a receipt. `CHECK ALL PASS` is emitted only
after the log, receipt, and terminal run metadata are durable.

The `format` mode evaluates the complete candidate working-tree state:
staged changes, unstaged changes, and nonignored untracked files. Its result
must not depend on whether the operator has staged a file, and the check never
rewrites the candidate.

### Runtime entry points

When a repository exposes a language runtime for scripts or diagnostics, the
entry point selects the same pinned, locked environment. In this starter,
`./bin/python [arguments...]` is the only supported way for methodology
callers to request the project interpreter. It never assumes `python`,
`python3`, or a minor-version binary on the host `PATH`.

The Python profile accepts `TOOLCHAIN_PYTHON=/absolute/path/to/python` for
deliberate compatibility testing. Without it, the committed `.python-version`
selects a uv-managed interpreter. With it, every wrapper uses only that
executable and fails closed if the executable or its locked dependency chain
is unusable. The
override names a base interpreter outside `project/.venv`; pointing into the
environment that uv may replace during synchronization is self-referential and
fails before uv runs.

Runtime wrappers may probe on ordinary one-shot entry. A hot loop, mutation
gate, generated multi-command workflow, or detached process resolves and
validates the underlying repository interpreter once, then reuses that exact
executable for every repeated call. It does not re-enter the wrapper for each
iteration, start a background process through an ambient executable, or depend
on a later `PATH` lookup after selection.

## Language profiles

The interface is universal; implementations are language-specific:

- Python/uv: committed `.python-version`, `pyproject.toml`, and `uv.lock`;
  `uv sync --locked --managed-python` for setup and
  `uv run --locked --managed-python` for default execution; an authoritative
  explicit interpreter is normalized by uv and uses `--python
  <resolved-path>` plus the matching managed/system preference, with the same
  selection applied to synchronization, probing, and execution;
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

## Candidate-bound focused and final gates

The planner's Build Gate Sequence has two explicit parts:

1. **Iteration and revision-close gates** — focused invocations through
   `./bin/test` or another repository-owned focused mode, plus affected
   static/structural checks. The plan states why the selection exercises the
   changed surface.
2. **Acceptance-close gates** — the phase's complete prescribed checks,
   ending with `./bin/check all`.

A raw ecosystem command is acceptable only for a narrow operation the
repository interface does not represent; it must still use committed metadata
and lock-preserving mode.

The coder runs the iteration/revision-close part as often as needed and reports
that focused evidence. The orchestrator runs the acceptance-close part once
after code-critic approval against the unchanged candidate. Evidence from a
delegated or sandboxed environment proves only that environment;
host-dependent acceptance is verified on the host.

Every gate record names the candidate identifier from
`bin/kickoff-tree-id`, its exact command, selection reason, exit status,
warning count, and optional artifact digest, per
[`orchestration-evidence.md`](orchestration-evidence.md). Verify the candidate
before and after the final sequence. A relevant candidate change invalidates
prior evidence; a gate that mutates the candidate fails. When the affected
surface is indeterminate, select a broader suite rather than defaulting to a
reassuring narrow one.

## Human wall-clock efficiency

Correctness and complete final assurance are fixed; avoidable waiting is not.
Agents remain alert when a gate or related deterministic operation materially
dominates the development critical path, especially when independent work runs
serially, invariant setup repeats, or a full suite is being used repeatedly
during iteration.

When a substantial improvement appears reasonably achievable with little risk
or effort, make one bounded execution assessment before blindly paying the
same cost again. Consider existing focused selectors, one-time preflight,
safe isolation and parallel execution of genuinely independent units, and
reuse only when complete input identity proves the result unchanged. Use an
already available safe mode. If a permanent improvement would expand the
authorized phase, surface it once as a concrete opportunity rather than
implementing the tangent.

This rule has no fixed time threshold and does not mandate optimization. Do
not spend heroic effort on marginal savings from an acceptable operation,
collect telemetry without a concrete decision it can inform, or weaken
coverage, determinism, diagnostics, failure propagation, candidate binding,
or the complete final gate. An expensive operation with no obvious safe
leverage may simply be reported and run.

## Full-gate receipt reuse

The acceptance-close gate still runs once against the approved candidate. A
receipt is a durable record of that completed gate, not permission to omit the
initial full gate or to reuse a result across candidates or environments.

The opt-in pre-push hook may reuse a receipt only when every non-deleted pushed
ref is the current `HEAD`, the working tree is clean, the current candidate and
environment fingerprint exactly match the receipt, and the receipt, terminal
run metadata, complete log path, and log digest all verify. Any absence,
malformed input, corruption, mismatch, query error, or uncertain state is an
explicit miss and runs `./bin/check all`. The lookup never falls back to a
reassuring value on error. The receipt manager writes only ignored local runtime
state; it performs no Git or other shared-state mutation.

Candidate identity and environment identity are separate bindings. The
environment fingerprint describes the runtime that actually executes the gate,
not the standalone receipt helper and not a version declaration used as its
proxy. In the Python profile, `bin/check-receipt` obtains a deterministic
descriptor through the repository-owned `bin/python` selection path. That
descriptor includes the selected implementation and actual version, resolved
executable and base-executable identities with their file digests, machine,
platform, and uv version. It does not hash `project/.venv` or an external
runtime tree. Failure to select the runtime, query any descriptor member, parse
the descriptor, or validate its schema is an explicit miss and runs the full
gate.

## Lifecycle hooks

Tracked hooks may invoke the candidate-bound receipt lookup and then
`./bin/check all` on every miss, but installation is opt-in. Hooks contain no
duplicate toolchain command list. Their installer is idempotent, reports
conflicting configuration, and requires an explicit force option to replace
it.

Opt-in needs a liveness witness, because `core.hooksPath` is local Git
configuration that does not survive a clone and can be silently repointed —
a component whose failure mode is silence needs an external witness that can
say "not running." `bin/check-hooks-installed` is that witness, and the
`check` policy lane runs it: an unset hooks path passes as the healthy
not-opted-in state (opting in is never mandated), a set-but-wrong path fails
as the silent disablement it is, and the tracked hooks themselves must exist
and stay executable in every checkout regardless of opt-in.

## Verification

Behavioral tests prove:

- invocation from outside the repository root;
- exact setup, full-test, focused-test, runtime, and gate mappings;
- pinned runtime and locked/frozen toolchain invocation;
- a real dependency-chain load/run probe before success;
- authoritative override selection, invalid-override refusal, and no fallback
  after an override or probe failure;
- clear failure when prerequisites or any bundle member is absent;
- exact child-status propagation;
- strict argument handling and stable terminal output;
- `bin/check test` delegation to `bin/test`.
- complete durable logs and terminal run metadata for every completed full-gate
  outcome, with log/storage failures explicit and never reusable;
- exact candidate/environment receipt hits, with corruption, drift, dirty-tree,
  non-`HEAD` push, and query-error paths all failing closed to a full-gate run.

The behavioral suite is the coverage floor for every supported mode and
override branch. A transfer must retain equivalent executable coverage after
target adaptation; grepping wrapper source for expected command strings is not
an adequate substitute.

Caller-policy verification inventories dependency-bearing shell workflows,
tracked hooks, generated commands, and active instructions. Repository code
uses the repository runtime. External-platform configuration literals (for
example, a cloud function's declared runtime) and language shebangs are not
operational caller instructions and remain governed by their own platform
contracts.

The policy gate runs the repository-owned caller inventory, harness-parity
check, and execution-dashboard validator. These checkers and their behavioral
tests are part of the atomic bundle: a transfer that adds a policy without its
enforcement, or a checker without its callers and fixtures, is incomplete.

After changing any bundle member or caller, run `./bin/test` for focused
wrapper coverage, run `./bin/check all`, and search for stale raw setup or test
commands that bypass the repository interface.

When a formatting gate needs a mechanical rewrite, invoke the formatter from
the same working directory and configuration boundary as `bin/check` uses.
Formatting the same paths from another directory can select different tool
configuration and still leave the authoritative check red.
