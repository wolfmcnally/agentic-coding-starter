# Policy: Acceptance Is Empirical

Every phase declares its acceptance criteria as **verifiable shell commands** or **named manual checks**. "The code compiles" is not acceptance. "The tests pass" by itself is not acceptance either; the tests must actually exercise the behavior the phase claims to deliver.

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

## When acceptance can't be automated

Some phases produce output that only a human can evaluate: perceptual audio quality, visual design judgment, UX flow, the readability of a document. For those phases:

- The Acceptance section says "Manual:" and names the artifact, the tool to view it with, and the criteria to look for.
- The orchestrator surfaces the artifact's path and the criteria in the END block.
- The human approves the phase in a follow-up session, after auditing.

Never disguise a manual check as an automated one ("the AIFF file is non-empty" is not "the audio sounds right").
