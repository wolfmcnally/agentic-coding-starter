# Policy: Acceptance Is Empirical

Every phase declares its acceptance criteria as **verifiable shell commands** or **named manual checks**. "The code compiles" is not acceptance. "The tests pass" by itself is not acceptance either; the tests must actually exercise the behavior the phase claims to deliver.

Phases that touch a user-facing surface also carry an interactive try-it-yourself protocol per [`user-demo-protocols.md`](user-demo-protocols.md) — a complement to the empirical checks here, not a substitute.

The evidentiary discipline around those checks—reading grep matches before
calling them findings, naming blind spots, rejecting blacklist-as-proof, and
testing sign-inverting proxies—is governed by
[`verification-discipline.md`](verification-discipline.md).

## A test carries its falsifier

Every new or materially changed test names the one-line mutation of the code
under test that would turn it red — the coder records the pair in Change
Evidence (`falsifiers`), the critic judges whether the mutation really reds
the test. A test with no nameable falsifier is scoring a stand-in for the
property: the implementation's own output, a constant lifted from the code, a
count preserved by any write. It is rewritten or deleted, never shipped as
coverage. (A month of code reviews across three derived projects put this
shape first among all findings.)

## What counts as an acceptance criterion

A criterion is acceptable when it is:

- **Executable.** A literal shell command the orchestrator can run, with a defined success condition (exit code 0, or a named substring in the output, or a JSON value at a path).
- **Observable.** A manual check named precisely enough that the human knows what to look at (e.g., "open `out/notify.aiff` in an audio player and confirm the tail decays cleanly with no clicks" — not "the audio sounds good").
- **Bounded.** The criterion either passes or fails on inspection. Open-ended ("the code is clean") is not a criterion; it is a wish.

## Examples

**Bad** — not empirical:
- "The CLI works."
- "The tests pass." *(Which tests? Covering what? Run with what command?)*
- "The schema is correct."
- "Documentation updated."

**Good** — empirical:
- `pytest -q` exits 0 with at least 8 passing tests, including `test_cli_help_lists_subcommands` and `test_validate_rejects_missing_required_field`.
- `toneforge render chime-short` produces `out/chime-short.aiff` with exact 3.000 s duration, true peak ≤ −1 dBTP, and integrated LUFS within the loudness target the recipe declares.
- Manual: open `out/chime-short.aiff` and confirm the rise → strike → decay sequence is recognizable as a short confirmation chime.
- `git status` is clean after the build gate runs (no leaked generated files).
- `cat README.md | grep -c '## Quickstart'` returns 1.

## How acceptance flows through the methodology

- **Step 5 (phased plan).** When breaking the work into phases, each phase carries an Acceptance section. The criteria are drafted at planning time, not retrofitted.
- **Step 7 (orchestrator).** The orchestrator passes the Acceptance section verbatim to the planner. The planner is responsible for ensuring every criterion has a concrete satisfaction path in the implementation plan (a build-gate command, a manual check named explicitly, or a deliverable that satisfies it by construction).
- **Step 8 (acceptance check).** The orchestrator runs every executable criterion. Manual criteria are surfaced to the human in the phase's END block and in the user-facing report.
- **Step 10 (human evaluation).** The human inspects the manual criteria and either accepts the phase or asks for revisions.

Which criteria the orchestrator may close on its own, and which always park for
the human, is the acceptance boundary in
[`human-in-the-loop.md`](human-in-the-loop.md). An executable criterion that was
independently reviewed and proved by a complete gate against the exact candidate
is objective and closes autonomously; a manual, perceptual, product, custody, or
owner-only criterion parks no matter how green the gate is.

## Acceptance evidence is candidate-bound

A green result proves only the exact reviewable working tree it exercised. Every
implementation-gate command is recorded with the candidate id from
`bin/kickoff-tree-id`. A relevant candidate change invalidates the result;
staging alone does not. The complete phase-prescribed sequence ends with
`./bin/check all` once after code-critic approval, and the candidate id must be
unchanged before and after the sequence. After tracked close bookkeeping changes
the tree, a second bare `./bin/check all` proves the actual handoff candidate; no
tracked write follows that gate.

During editing and revision, run the smallest falsifying test first and then the
affected suites. That focused evidence narrows defects efficiently but does not
replace final acceptance. See
[`orchestration-evidence.md`](orchestration-evidence.md).

## Test discipline

When acceptance leans on a test suite:

- **Name the tests.** "All of `tests/test_pipelines_load.py`" is acceptable; "the tests" is not. The phase plan can list test names; the phase acceptance lists the commands plus expected counts or specific test names that must pass.
- **Tests must exercise behavior, not type signatures.** A test that constructs a class and asserts it is not `None` is not a test. A test that calls the function and asserts on its output is.
- **Hit real boundaries when feasible.** Integration tests that hit a real database, a real file system, or a real subprocess catch failures that mocks miss. Save mocking for genuinely external dependencies (network APIs, large datasets).

## Baseline-dependent criteria

Some criteria compare against a **prior** state rather than an absolute one:
"byte-identical before and after", "the untouched surfaces' output does not
change", "unchanged across the edit". These are the idiom for a *no-op*
assertion, and they stay — a byte-diff is the weakest sufficient falsifier for
"this surface must not change". A surface that is *expected* to change is
asserted structurally instead; a byte-diff there is the wrong instrument and
only generates noise.

**The baseline is a commit, not a pile of artifacts.** A phase carrying any
such criterion records its baseline as a commit id in the START block at phase
start ([`log-discipline.md`](log-discipline.md) § START block format), naming
the criteria that depend on it. That line is the whole obligation: it is
cheap, it is visible from the first minute, and it converts an implicit
"before" into a stated one.

**Artifacts are derived lazily, never captured eagerly.** At acceptance, and
only if the comparison is actually wanted, rebuild the baseline from a clean
copy at the recorded commit and diff. Eager capture pays a build cost on every
phase to serve the few that need it, and stores bytes that were derivable all
along. Build determinism is the precondition for that rebuild; if a rebuild
ever produces a spurious diff, that is a finding about the surface — a
non-deterministic build is a defect worth its own work — not a reason to start
capturing eagerly.

**An unrecorded baseline is a protocol failure, not an unmet criterion.** The
commit is recoverable from the log and the phase's own history, so the rebuild
path always exists. "Unmet, substituted with a structural check" is never the
honest terminal answer to a baseline-dependent criterion.

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

**A check that passes on an empty result** (vacuous green) is the third mode,
and the hardest to see: the instrument ran, found nothing, and reported
satisfaction. An empty result set indicts the instrument before it establishes
absence. `assert every_x_is_valid(xs)` and `assert not any_bad(xs)` both pass
when `xs` is empty — and `xs` goes empty for reasons that have nothing to do
with the property: a query whose subject moved, a probe reading transient state
that a successful run legitimately drained, a path that resolved to the wrong
root, a filter that over-matched.

- **Assert positive cardinality first.** A probe over a known population states
  the population size it expects (`assert len(pairs) == 4`) before asserting
  anything about the members. Then an empty read fails loudly as itself rather
  than silently as success.
- **Prefer durable state over transient state as a probe's subject.** A check
  built on a workspace, queue, or pending set that completion drains cannot
  outlive the completion it was guarding — it passes before the run and fails,
  or worse passes vacuously, after. Read the folded/committed record instead.
- **Treat a newly-empty result as an instrument fault until proven otherwise.**
  The first question is "did I lose my subject?", not "is the subject clean?"

**A survey that reports perfect uniformity** (vacuous *finding*) is the fourth
mode, and it is the most dangerous because it does not read as an absence at
all — it reads as a result you can build on. A probe over a real population
that comes back completely uniform is more often measuring a field that cannot
vary than discovering that the population is uniform.

- **Worked case (a derived project's format survey).** A survey over 134 legacy
  documents reported one version constant on all 134, and that uniformity was
  taken as a strong population finding. The probed field was a compatibility
  constant; the field that carries the version was one the probe never read.
  The real distribution was 128/6 across two versions. A phase file, an
  implementation plan, a review requirement, and a parser validity check were
  all built on the constant before the corpus refuted it — and the first
  correction would have shipped a converter with 0% recall.
- **Real corpora are messy.** Near-perfect uniformity across a population
  assembled by many tools over many years is itself the trigger to ask what the
  instrument is reading, not a finding to act on.
- **Prove the instrument can produce a different answer.** Not merely "can it
  find something" (the mutation test below), but "can it return anything other
  than what it just returned." Run it against a deliberately different input
  and confirm the output changes.

**The unifying rule.** Zero results, all-positive results, empty results, and
uniform results are one defect wearing four faces: **the instrument could
return only one answer, so its answer carried no information.** Before
believing any instrument, establish that its output space has more than one
reachable member.

For every new gate, state what makes it fail and demonstrate the failure.
Where practical, use mutation testing: temporarily remove or invert the guard,
prove the test fails for the intended reason, then restore it. Exception tests
name the message or state transition they expect; a bare
`pytest.raises(SomeType)` may pass because an unrelated guard raised the same
type.

## One truth, one fold

A closure question — "is this batch done", "did this wave converge", "are all
inputs terminal" — has exactly **one** authoritative fold, and every other
instrument reports that fold rather than re-deriving the answer at its own
scope.

Secondary instruments that re-derive a closure claim will disagree with it, and
the disagreement is an artifact of scope rather than a finding. In the donor
incident, a batch-scoped audit asked whether a *wave* had closed and answered
`all_inputs_terminal: false` because two of its inputs reached terminal state
in sibling batches of the same wave; a wave-closure-scoped counter was required
to equal a batch-scoped container count, which could only ever produce false
mismatches. In one phase, four instruments answered one question at four scopes
and two orchestrator misclassifications rode on the disagreements.

The rule, therefore:

- **Name the authoritative fold** for any closure claim, and make every other
  surface read it. A second implementation of the same question is a second
  answer, not a cross-check.
- A genuine cross-check compares an instrument against the **authoritative
  fold**, never against another instrument's independent re-derivation.
- When two instruments disagree about closure, **establish which scopes they
  are folding over before treating either as a defect.** Different scopes
  answering differently is the expected behaviour of a system that has more
  than one scope, not evidence that something is broken.
- A claim of the form "X is complete" must state the scope it is complete
  *over*. An unscoped closure claim cannot be verified, because no instrument
  can tell whether it agrees with it.

The repository-owned toolchain wrappers are tested like product code. See
[`build-gates.md`](build-gates.md): cwd independence, runtime selection,
locked setup, authoritative-override refusal without fallback, a real
project-and-tool dependency-chain probe, full/focused test routing,
missing-bundle behavior, command ordering, delegation, and exact status
propagation are executable contracts.

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
falls back to ambient packages and calls the result equivalent. When a human
explicitly overrides the runtime for compatibility testing, the override is
the only candidate: validate it with the repository's load/run probe and fail
if it cannot exercise the real dependency chain.

### Cross-tree defect reports are leads, not findings

A defect report arriving from another tree — a sibling checkout, a donor repo
under `learn`, a peer session working a different worktree — transfers its
**artifact** cheaply and its **mechanism** not at all. The symptom, the file
path, and the proposed fix all copy across intact and cost nothing to believe.
Whether the same cause is present here does not copy at all. So an inbound
finding is a **lead, not a finding**, until its mechanism is re-derived in the
tree where it is asserted:

- **Re-derive the mechanism locally before acting on the fix.** In the donor's
  worked case, a shebang defect whose artifact matched exactly had no local
  mechanism, and the proposed fix would have broken a pinned-tool bundle.
  Matching the symptom is not confirming the cause.
- **Treat a divergence as the finding, not as noise.** A guard reported dead in
  a sibling's frozen tree was alive here; the divergence was the whole answer,
  and reconciling it to the sibling's verdict would have destroyed the
  information.
- **Read relayed arguments and commands whole.** A relayed invocation was
  misattributed because its `-C` argument was read in part rather than entire.
- **Say which tree a claim was verified in.** A verdict is scoped to the tree
  that produced it, and a report that omits its tree cannot be checked against
  another one.

This is the cross-tree instance of the general rule above that evidence is
scoped to the environment that produced it; the `learn` skill's
direction-verification rule is its donor-remedy special case.

## When acceptance can't be automated

Some phases produce output that only a human can evaluate: perceptual audio quality, visual design judgment, UX flow, the readability of a document. For those phases:

- The Acceptance section says "Manual:" and names the artifact, the tool to view it with, and the criteria to look for.
- The orchestrator surfaces the artifact's path and the criteria in the END block.
- The human approves the phase in a follow-up session, after auditing.

Never disguise a manual check as an automated one ("the AIFF file is non-empty" is not "the audio sounds right").
