# Policy: Acceptance Is Empirical

Every phase declares its acceptance criteria as **verifiable shell commands** or **named manual checks**. "The code compiles" is not acceptance. "The tests pass" by itself is not acceptance either; the tests must actually exercise the behavior the phase claims to deliver.

Phases that touch a user-facing surface also carry an interactive try-it-yourself protocol per [`user-demo-protocols.md`](user-demo-protocols.md) — a complement to the empirical checks here, not a substitute.

## What counts as an acceptance criterion

A criterion is acceptable when it is:

- **Executable.** A literal shell command the orchestrator can run, with a defined success condition (exit code 0, or a named substring in the output, or a JSON value at a path).
- **Observable.** A manual check named precisely enough that the human knows what to look at (e.g., "open `renders/foo/v003/foo.aiff` in QuickTime and confirm the tail decays cleanly with no clicks" — not "the audio sounds good").
- **Bounded.** The criterion either passes or fails on inspection. Open-ended ("the code is clean") is not a criterion; it is a wish.

## Examples

**Bad** — not empirical:
- "The CLI works."
- "The tests pass." *(Which tests? Covering what? Run with what command?)*
- "The schema is correct."
- "Documentation updated."

**Good** — empirical:
- `pytest -q` exits 0 with at least 8 passing tests, including `test_cli_help_lists_subcommands` and `test_validate_rejects_missing_required_field`.
- `kiln render score-bump-small` produces `renders/score-bump-small/v001/score-bump-small__v001.aiff` with exact 3.000 s duration, true peak ≤ −1 dBTP, integrated LUFS within the `small_reward` family target.
- Manual: open `renders/score-bump-small/v001/score-bump-small__v001.aiff` and confirm rumble → whoosh → soft pop → sparkle tail is recognizable as "a small reward."
- `git status` is clean after the build gate runs (no leaked generated files).
- `cat README.md | grep -c '## Quickstart'` returns 1.

## How acceptance flows through the methodology

- **Step 5 (phased plan).** When breaking the work into phases, each phase carries an Acceptance section. The criteria are drafted at planning time, not retrofitted.
- **Step 7 (orchestrator).** The orchestrator passes the Acceptance section verbatim to the planner. The planner is responsible for ensuring every criterion has a concrete satisfaction path in the implementation plan (a build-gate command, a manual check named explicitly, or a deliverable that satisfies it by construction).
- **Step 8 (acceptance check).** The orchestrator runs every executable criterion. Manual criteria are surfaced to the human in the phase's END block and in the user-facing report.
- **Step 10 (human evaluation).** The human inspects the manual criteria and either accepts the phase or asks for revisions.

## Test discipline

When acceptance leans on a test suite:

- **Name the tests.** "All of `tests/test_pipelines_load.py`" is acceptable; "the tests" is not. The phase plan can list test names; the phase acceptance lists the commands plus expected counts or specific test names that must pass.
- **Tests must exercise behavior, not type signatures.** A test that constructs a class and asserts it is not `None` is not a test. A test that calls the function and asserts on its output is.
- **Hit real boundaries when feasible.** Integration tests that hit a real database, a real file system, or a real subprocess catch failures that mocks miss. Save mocking for genuinely external dependencies (network APIs, large datasets).

## A check must be able to fail

A gate, test, or verification instrument earns trust only if it can report the
failure it claims to guard against. Most silent false results trace to a check
that structurally cannot fail in one direction.

Common false greens include:

- **A pipe masks the real status.** `cmd | tail`, `cmd | head`, and
  `cmd | grep` report the final formatter's status unless `pipefail` is
  enabled or the upstream status is captured explicitly.
- **A swallowed failure becomes a default success.** `|| true`, a
  `2>/dev/null` collapsed into an empty value, or a failed query replaced with
  `"in_progress"` turns error or absence into reassurance.
- **A proxy replaces the real assertion.** File presence does not prove a
  parser can load the file; a directory or symlink may remain after the
  dependency it names has been reaped; key-set equality does not prove byte
  equality.
- **The wrapper loses the child status.** A gate that prints `FAIL` and then
  exits zero is worse than no wrapper because it creates machine-readable
  false evidence.

False reds are corrosive too. Integrity checks must exclude volatile artifacts
such as SQLite `-wal`/`-shm` files, caches, mtimes, and nondeterministic output
ordering unless those properties are the contract. Comparisons use a fixed
baseline captured at operation start, not a moving reference such as
`origin/master` or "now."

For every new gate, state what makes it fail and demonstrate the failure.
Where practical, use mutation testing: temporarily remove or invert the guard,
prove the test fails for the intended reason, then restore it. Exception tests
name the message or state transition they expect; a bare
`pytest.raises(SomeType)` may pass because an unrelated guard raised the same
type.

The repository-owned wrapper itself is tested like product code. See
[`build-gates.md`](build-gates.md): cwd independence, locked toolchain
invocation, missing-prerequisite behavior, command ordering, and exact status
propagation are all executable contracts.

## Evidence is scoped to its environment

A result is never merely "the gate passes." It is "the gate passed here, with
these capabilities exercised." Sandboxes, missing local services, different
toolchains, and injected test doubles can all narrow what a green run proves.

- **Report the scope.** If a delegated sandbox could not reach a local service,
  say that service-backed tests skipped; do not report the bare pass count as
  host evidence.
- **Distinguish three states.** A dependency is absent, present but unusable in
  this environment, or present and working. Collapsing the middle state into
  either neighbor sends the next reader to the wrong conclusion.
- **A skip is not a pass.** Capability-gated tests skip honestly when the real
  service is absent. They never assert the behavior of the broken or missing
  capability as though it were product behavior.
- **The orchestrator owns host verification.** When acceptance depends on a
  local daemon, browser, device, credential, or network boundary, the
  orchestrator runs that check on the host. A delegated role's report is not
  evidence for it in either direction.
- **Durable dependencies live in durable locations.** Nothing a later session
  must find is installed only in an agent scratch directory. Verify durability
  with a load or run probe, not `test -e`.

Committed metadata and lockfiles define the toolchain used by the canonical
gate. A missing bootstrap executable or stale lockfile fails visibly; it never
falls back to ambient packages and calls the result equivalent.

## When acceptance can't be automated

Some phases produce output that only a human can evaluate: perceptual audio quality, visual design judgment, UX flow, the readability of a document. For those phases:

- The Acceptance section says "Manual:" and names the artifact, the tool to view it with, and the criteria to look for.
- The orchestrator surfaces the artifact's path and the criteria in the END block.
- The human approves the phase in a follow-up session, after auditing.

Never disguise a manual check as an automated one ("the AIFF file is non-empty" is not "the audio sounds right").
