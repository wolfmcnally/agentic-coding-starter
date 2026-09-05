# bin/ — Deterministic script reference

`bin/` is the repo's home for **deterministic executables** — the mechanistic half of the methodology. Per [`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md), work that is exact, repeatable, and judgment-free lives here as a plain script rather than in an agent: it runs identically every time, costs nothing to invoke, is unit-testable, and behaves the same under every harness (Claude Code, Codex, …).

## Convention

- **Invoke repo-relative:** `./bin/<name>`. Shell entry points resolve their own
  symlink chains before deriving the repository root, then `cd` there where
  needed, so they work from any working directory and through single-hop or
  chained launch symlinks.
- **One concern per script.** A script does one mechanical job and exits with a meaningful status code (0 = clean/done, non-zero = findings/failure).
- **Document every script here** — what it does, when to run it, and its exit/refusal behavior — so this README is the operator-facing index for the directory. Derived projects extend this list as they add their own mechanistic scripts.
- **Reach for `bin/` deliberately.** When a phase needs a repeatable check, a mechanical sweep, a generator, or a reconciler, that is `bin/` work, not agent work. When it needs judgment, it is not. The triage rule is [`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md).

## Scripts

### `check-candidate-partition` — validate declared paths

`./bin/check-candidate-partition` validates the live declaration and every tracked path. `./bin/check-candidate-partition --staged` validates indexed declaration bytes against the complete index. Missing, malformed, or incomplete classification exits nonzero; a valid declaration reports its digest and tracked-path count. The declaration format and review boundary are owned by [orchestration evidence](../policies/orchestration-evidence.md). The checker runs in the policy gate and opt-in commit hook; it does not install hooks or mutate Git configuration.

### `setup` — provision the pinned, locked environment

Validates the `uv` prerequisite and the complete Python profile, then
synchronizes the selected interpreter and exact locked dependencies. Before
reporting success it imports the example package and pytest and runs
`ruff --version` inside that environment. It works from any current directory
and refuses a stale or missing lockfile.

```bash
./bin/setup
```

### `test` — full or focused repository tests

With no arguments, runs the deliverable tests and root methodology tests.
Arguments are forwarded to pytest from the repository root, so focused paths
are stable from any caller directory.

```bash
./bin/test
./bin/test tests/test_check.py -q
./bin/test --vital
./bin/test --changed-from HEAD~1
```

The governed lanes use the recipient-local `tests/proof-estate.yaml`. Vital
runs every locally admitted fast family; changed runs the union of every family
mapped to the live diff. Invalid governance, an unresolved ref, or an unmapped
path widens to the full suite. Both phase-close gates remain `bin/check all`.

### `python` — repository-selected Python

Runs Python from the same managed, locked environment as setup and the gates.
Use it for one-off scripts and diagnostics instead of assuming a host
`python3.x` executable. The shared dependency-chain probe runs before the
requested command.

```bash
./bin/python --version
./bin/python -c 'print("hello")'
```

The managed interpreter from `project/.python-version` is the default. To test
one specific interpreter deliberately, set an executable absolute path:

```bash
TOOLCHAIN_PYTHON=/absolute/path/to/python ./bin/check all
```

That override is authoritative. An invalid path, incompatible interpreter, or
failed dependency probe stops the command; no managed or ambient fallback is
tried. Select a base interpreter outside `project/.venv`; an interpreter inside
the environment uv manages is rejected before synchronization can replace it.

### `_python-toolchain` — shared runtime resolver and probe

Source-only helper used by `setup`, `test`, `check`, and `python`. It validates
the Python bundle, resolves the managed default or authoritative override, and
runs the real project-and-tool dependency probe with the same selection
arguments used by the eventual command. It is part of the atomic toolchain
contract and is not invoked directly.

### `check` — authoritative repository build gate

The single authoritative entry point for automated repository checks. It
resolves the repo root from its own location, validates the complete toolchain
bundle, probes the selected locked environment, then runs the selected named
mode with the identical runtime selection.
Its `test` mode delegates to `bin/test`. `all` runs lint, format verification,
tests, and deterministic policy checks in order. Child failures retain their
exact status and emit a terminal `CHECK <name> FAIL`; success ends with
`CHECK ALL PASS`. Every `all` run also captures a complete durable log and
terminal run metadata under `.kickoff/check-all/`; success stores a receipt
bound to the exact candidate, environment fingerprint, and log digest.

```bash
./bin/check
```

```bash
./bin/check test
```

```bash
./bin/check vital
./bin/check changed HEAD~1
```

Universal contract: [`policies/build-gates.md`](../policies/build-gates.md).
`stamp`, `learn`, and `teach` preserve the atomic interface while adapting its
implementation to the destination's language, runtime policy, metadata, and
lockfile. Behavioral coverage lives in
`tests/test_toolchain_entrypoints.py`, `tests/test_check.py`, and
`tests/test_check_receipt.py`.

### `test-governance` — proof-estate reset, assay, and safe selection

Inventories collapsed families, expanded leaves, gate members, and hook
commands. It validates the frozen reset, complete disposition/admission ledger,
20% ceilings, 80% effectiveness floors, digest-bound corpus patches, direct
critical risks, and zero-growth budget; runs the local mutation assay; selects
vital/changed lanes; and reports or reassesses the estate. It runs through the
repository-selected environment.

```bash
./bin/test-governance inventory
./bin/test-governance validate
./bin/test-governance select --tier vital --format lines
./bin/test-governance select --changed-from HEAD~1 --format lines
./bin/test-governance report
./bin/test-governance assay --class historical_defect
./bin/test-governance assay --class holdout_mutant
./bin/test-governance reassess
```

Universal contract:
[`policies/test-suite-governance.md`](../policies/test-suite-governance.md).
Behavioral coverage lives in `tests/test_test_governance.py` and
`tests/test_pre_commit.py`; the manifest and reports are recipient-local state.

Post-reset evolution is replayed from the append-only audit ledger. A
`proof_retirement` removes one currently active proof and creates one budget;
one later `proof_admission` may consume that budget exactly once. Reset-era
retirements cannot fund proofs appended after the post-reset lifecycle begins.

### `kickoff-command-zero` — cheap ordered acceptance preflight

Validates the active immutable command manifest, real-read venue receipt, and
stage topology; runs every manifest-declared selector dry-run; then checks
format and log policy. It stops on the first failure.

```bash
./bin/kickoff-command-zero --run-dir "$RUN_DIR"
```

### `check-log` and bounded log repair tools

`check-log` composes the exact committed-prefix and effective-chronology
validators. `log-append` is the true-EOF writer. `log-relocate` moves one
uncommitted block only by unique content digest. `normalize-final-newline` is
closed to the three admitted bookkeeping files.

```bash
./bin/check-log
./bin/check-log --staged
./bin/log-relocate --block <sha256> --after <sha256> --dry-run
./bin/normalize-final-newline --path plan/INDEX.md --check
```

### `check-receipt` — durable full-gate record and exact reuse

Internal manager used by `bin/check all` and the pre-push hook. It identifies
the complete candidate through `kickoff-tree-id`, records running and terminal
metadata plus the full gate log, and writes a reusable success receipt only
after the candidate, environment, and durable artifacts verify. Its environment
descriptor comes through `bin/python`, so the implementation, actual version,
resolved executable and base-executable identities and digests, platform, and
uv version describe the runtime that ran the gate rather than the standalone
receipt helper. Candidate and environment identities remain separate; no venv
or external runtime tree is added to the candidate hash. Pre-push reuse
additionally requires a clean tree and every non-deleted pushed ref to equal
`HEAD`; any miss, malformed record, descriptor failure, corruption, or query
failure runs the full gate. It is normally not invoked directly.

Universal contract: [`policies/build-gates.md`](../policies/build-gates.md).
Behavioral coverage lives in `tests/test_check_receipt.py`.

### `install-hooks` — opt in to tracked Git hooks

Configures only the current checkout's `core.hooksPath` to `.githooks`. The
pre-commit hook runs the fast harness-parity and toolchain-caller checks; the
pre-push hook reuses a verified exact full-gate receipt or runs
`./bin/check all` on any miss. Installation is explicit and idempotent.
A different existing hooks path is preserved and reported; only `--force`
replaces it. `--dry-run` reports the proposed change without writing Git
configuration.

```bash
./bin/install-hooks --dry-run
```

```bash
./bin/install-hooks
```

Universal contract: [`policies/build-gates.md`](../policies/build-gates.md).
Behavioral coverage lives in `tests/test_install_hooks.py`.

### `check-hooks-installed` — opt-in-aware hook-liveness witness

`core.hooksPath` is local Git configuration that does not survive a clone and
can be silently repointed, disabling the tracked hooks with no error anywhere.
This witness makes that state visible: an unset path passes as the healthy
not-opted-in state (with a pointer to `./bin/install-hooks`), a set-but-wrong
path fails as silent disablement, and `.githooks/pre-commit` / `pre-push`
must exist and stay executable regardless of opt-in. Runs inside the `check`
policy lane.

```bash
./bin/check-hooks-installed
```

Behavioral coverage lives in `tests/test_check_hooks_installed.py`.

### `kickoff-config` — human-editable `kickoff` configuration and enforcement

Validates and safely edits repo-root `kickoff.yaml`, whose `role_models`,
`role_timeouts`, `research_budgets`, and `run_budgets` sections hold separate
model/effort fields, execution budgets, per-role originating-search budgets,
and the per-phase self-resume budget. Round-trip YAML
handling preserves human comments and extension data. The manager also owns
fail-closed real-read venue preflight and its config-bound receipt, generated cross-harness commands, strict
review-output schemas, immutable role-attempt registration, progress-aware
supervision, fresh-artifact enforcement, exact execution spans, and
evidence-based timeout recommendations. A Python script run via `uv` with
PEP 723 `ruamel.yaml`. Governed by
[`policies/role-models.md`](../policies/role-models.md),
[`policies/role-timeouts.md`](../policies/role-timeouts.md),
[`policies/research-authority.md`](../policies/research-authority.md),
[`policies/execution-telemetry.md`](../policies/execution-telemetry.md), and
[`policies/fail-closed-resume.md`](../policies/fail-closed-resume.md).

```bash
./bin/kickoff-config show
```

```bash
./bin/kickoff-config set-models codex reviewer.model=opus reviewer.effort=high critic.model=opus critic.effort=high
```

```bash
./bin/kickoff-config reset models
```

```bash
./bin/kickoff-config show budgets
```

```bash
./bin/kickoff-config set-budgets self_resume=3
```

```bash
./bin/kickoff-config preflight --receipt "$RUN_DIR/role-preflight.json"
./bin/kickoff-config verify-preflight-receipt --receipt "$RUN_DIR/role-preflight.json"
```

```bash
./bin/kickoff-config render-command --role reviewer --venue codex --model sol --effort high --prompt-file /absolute/run/reviewer.prompt --required-output-file /absolute/run/reviewer.result
```

```bash
./bin/kickoff-config recommend-timeouts
```

Behavioral coverage lives in `tests/test_kickoff_config.py`; `./bin/check all`
lints and format-checks the manager and runs its tests alongside the canonical
gate/hook tests and isolated example package tests.

The watcher records child-process status, fresh artifact status, and terminal
event-stream completeness independently. Ordinary success requires all three.
Exit 66 preserves a fresh artifact from a successful child whose stream was
incomplete so `kickoff` can explicitly validate its role shape, evidence, and
candidate before accepting it; exit 65 remains an unrecoverable protocol
failure.

Universal: `stamp` and `teach` carry the manager, policies, tests, and seed config. Target values, comments, `extensions` data, and raw `.kickoff/` telemetry stay target-owned.

### `kickoff-tree-id` — complete review candidate identity

Hashes the complete reviewable Git working tree: tracked content whether
staged or unstaged, deletions, normalized executable modes, symlink targets,
and nonignored untracked files. Ignored runtime state is excluded, and staging
alone does not change the identity. With `--json`, emits the ordered
path/mode/content-hash manifest without source contents. Escaping symlinks and
unsupported entry types fail closed. A clean submodule contributes its checked
out commit; a dirty submodule fails closed because one superproject hash
cannot safely summarize its unresolved candidate.

```bash
./bin/kickoff-tree-id
```

```bash
./bin/kickoff-tree-id --json
```

Governed by
[`policies/orchestration-evidence.md`](../policies/orchestration-evidence.md);
behavioral coverage lives in `tests/test_kickoff_tree_id.py`.

### `kickoff-evidence` — run-scoped review and gate evidence

Initializes and validates the authority, change, finding, packet, role-attempt,
trace-binding, candidate-lineage, timing-summary, and gate records for one
`kickoff` run. It extracts exact JSON evidence blocks from role artifacts,
enforces stable finding identity and state transitions, detects authority/risk
rebases, compiles deterministic revision packets, and rejects stale or
unjoined evidence. `ingest-findings` requires `--review-span-id` (convergence
metrics attach to the review pass's own intelligence span, and a finalized
trace cannot be repaired retroactively); a non-review ingest passes
`--no-review-span '<reason>'`, which records the owned omission in the run's
`review-metrics-omitted.jsonl`. `run-gate` checks artifact-path preconditions
before the gated command runs and records an artifact absent afterward with no
digest plus a loud warning rather than stranding the closed gate span. Run
`--help` or a subcommand's `--help` for the full schema-driven interface.
`validate --level integrity` proves only the facts actually recorded;
`validate --level acceptance` adds every required success event. `status`
reports missing acceptance roles and allowed next actions. `close` materializes
one idempotent accepted, parked, or failed terminal record and appends its exact
log block once; parked and failed closes require a validated failure signature.

```bash
./bin/kickoff-evidence --help
```

```bash
./bin/kickoff-evidence validate --run-dir /absolute/run/directory --level acceptance
```

Governed by
[`policies/orchestration-evidence.md`](../policies/orchestration-evidence.md);
behavioral coverage lives in `tests/test_kickoff_evidence.py`.

### `execution-telemetry` — exact shared execution trace

Records append-only stage, role, wait, tool, and gate spans in one trace;
records phase-level operator-input parks in a separate append-only ledger;
reconciles interrupted spools; computes union-based makespan, concurrency, and
park totals; and projects a privacy-safe phase handoff. Same-boot parks are
monotonic and exact, cross-boot parks are visibly non-exact, and any open park
fails close. The handoff is the only input to the committed HTML report.

```bash
./bin/execution-telemetry --help
```

Governed by
[`policies/execution-telemetry.md`](../policies/execution-telemetry.md);
behavioral coverage lives in `tests/test_execution_telemetry.py`.

### `check-execution-dashboards` — validate committed reports

Regenerates and validates every committed phase report and its aggregate index,
rejecting stale output, unsafe paths, network dependencies, and unsanitized
runtime data. An empty archive is valid before the first completed phase.

```bash
./bin/check-execution-dashboards
```

### `serve-execution-dashboard` — local report server

Serves `reports/execution/` on loopback for browser review. `kickoff` uses its
`--open` mode as the final end-of-phase handoff after the report has passed
validation.

```bash
./bin/serve-execution-dashboard --open
```

### `lessons` — lessons-ledger validation and queries

Validates every file in `lessons/` and `lessons-archived/` against the ledger
schema (closed key set, enums, slug uniqueness across both directories,
well-formed occurrences) and answers the two mechanical queries the harvest
and sweep loops need: filtered listings and graduation-ready candidates
(three or more occurrences, still open). Queries fail closed on an invalid
ledger. Filing, occurrence-appending, and graduation remain judgment work
outside this tool.

```bash
./bin/lessons validate
```

```bash
./bin/lessons list --scope methodology --status candidate
```

```bash
./bin/lessons candidates
```

Governed by [`policies/lessons.md`](../policies/lessons.md); behavioral
coverage lives in `tests/test_lessons.py`.

### `treatise` — editorial-record validation

Validates every brief whose frontmatter carries a `treatise:` mapping: the
required keys, the field shapes, and ISO dates on directives, renderings, and
external facts. A leftover `briefs/<name>.yaml` sidecar beside its brief fails,
because the record has one home. The checks are about shape; the history of the
`directives` log lives in version control.

```
./bin/treatise validate
```

```
./bin/treatise show
```

`validate` is the default subcommand. Exit 0 when every treatise validates, 1 on
a violation, 2 when `briefs/` cannot be read.

Governed by [`policies/treatise.md`](../policies/treatise.md); behavioral
coverage in `tests/test_treatise.py`.

### `check-harness-parity` — canonical/mirror consistency

Verifies the top-level instruction symlink, skill-directory symlinks, and thin
Codex agent pointers against their canonical Claude definitions.

```bash
./bin/check-harness-parity
```

### `check-toolchain-callers` — repository runtime boundary

Inventories active scripts, hooks, workflows, and instructions and rejects
raw dependency-bearing runtime or test commands that bypass repository-owned
entry points.

```bash
./bin/check-toolchain-callers
```

### `check-catalogs` — document and phase-ledger fitness functions

Verifies the durable-document catalogs stay closed under sync: every
`policies/*.md` and `briefs/*.md` file is indexed in `CLAUDE.md` and every
indexed entry resolves to a file (no orphans either way). It also validates
current-candidate repository-internal Markdown links — both tracked and
nonignored untracked files, path *and* the
`#fragment`, resolved against the target document's own headings, so a link
cannot be green and dead at once; a fragment into a non-Markdown target has no
derivable anchor set and is skipped rather than guessed at. It enforces the
one-way citation direction from
[`policies/briefs-and-policies.md`](../policies/briefs-and-policies.md): a file
under `briefs/` may not link into `policies/` or `plan/`, because the thinking
predates the rule derived from it. It enforces the `docs/` contract from
[`policies/docs.md`](../policies/docs.md): whenever `docs/` holds anything
beyond its README, `docs/README.md` must exist and link every top-level entry,
and no file under `docs/` other than that catalog may link outside `docs/`,
because pinned third-party material never references the project. And it
validates the complete phase lifecycle:
each phase-table row has one recognized status, at most one row is `⬅️`, idle
incomplete work has exactly one next row, and active or complete work may have
none. Link scanning exempts fenced code blocks *and* inline code spans — a
link quoted inside backticks is a quoted edit target, not a live link. It also
enforces [`policies/phase-status.md`](../policies/phase-status.md) over
per-phase files: a `status:` frontmatter field or a `Status: ✅`-shaped
declaration line in any `plan/phase-*.md` fails; narrative emoji mentions in
prose stay fine. `--closing-phase <id>` additionally refuses a completed child
that neither completes its parent nor leaves that parent in progress with
another drafted incomplete direct child.

```bash
./bin/check-catalogs
```

Behavioral coverage lives in `tests/test_check_catalogs.py`.

### `check-plan-concreteness` — mechanical pre-review of a plan artifact

Runs between plan capture and plan review inside `kickoff` (Step 3), over the
planner's artifact rather than the repository, so the reviewer's round is not
spent on what a script can refuse. It fails closed on the four defect shapes
that a month of plan-review rejections across three projects showed to be the
most frequent and the most mechanical: a backticked identifier that occurs
nowhere in the tree and is not declared in the plan's `## Definitions Read`
table (a name the planner never read — `Mode.FAST` for a member that
is `FAST_PATH`); a `Definitions Read` row whose file or line does not
define what it claims; a cited path that does not exist and is not a declared
new file; a command that cannot run as written — absent repository script,
a `--flag` no argparse definition in that script spells, a `<placeholder>`
token, or a 64-hex candidate id pinned before the implementation that will
change it; and a lookup deferred to the coder (`or equivalent`, `TBD`, "verify
before coding"). Shell pass-through wrappers such as `bin/test` are not
flag-checked, since their arguments reach another program. Exit 0 prints
`PLAN CONCRETENESS PASS`; exit 1 prints one `ERROR\t<check>\t<line>\t<message>`
row per refusal; exit 2 is a usage or I/O error. The plan may live anywhere;
`--root` names the repository it describes. Revision runs repeat
`--prior-plan <artifact>` in chronological order; the checker stops a plan
over 600 lines, growth greater than one third in one round, or the second
growth event in the artifact history.

```bash
./bin/check-plan-concreteness --plan /absolute/path/to/plan.md --root .
```

Behavioral coverage lives in `tests/test_check_plan_concreteness.py`.

### `check-plan-delivery` — did the tree receive what the plan named

Mechanistic post-implementation check `kickoff` runs after `capture-change`
and before the code critic is dispatched (Step 5). About one code finding in
seven over a month was the critic discovering an item the approved plan named
and the coder never wrote; a script reads the plan's own inventory against the
tree instead. Every `### New Files` path must exist; every identifier the
plan's `## Definitions Read` table declares `introduced` must occur in the
tree; every backticked `test_*` node and `path::member` cited under Testing
Strategy, Build Gate Sequence, or Acceptance must exist. An item that is
missing but named under the coder report's `### Notes` or `### Files to
Delete` (`--deviations <report>`) is reported as `DEVIATION` rather than
`ERROR`, so a declared narrowing reaches the critic without failing the
check. Shares its parser with `check-plan-concreteness` through
`lib/agentic_starter/plan_artifact.py`, so the two cannot disagree about what
a plan says. Exit 0 prints `PLAN DELIVERY PASS`; exit 1 prints one
`ERROR\t<check>\t<line>\t<message>` row per missing item; exit 2 is a
usage or I/O error.

```bash
./bin/check-plan-delivery --plan /absolute/path/to/approved-plan.md --root . --deviations /absolute/path/to/coder-report.md
```

Behavioral coverage lives in `tests/test_check_plan_delivery.py`.

### `review-verdicts` — harvest review verdicts from harness traces

The mechanistic half of the `sweep-planning` skill. Walks the machine's Claude
Code (`~/.claude/projects/`) and Codex (`~/.codex/sessions/`) session
transcripts for the last `--since-days` (default 31), extracts every
`## Verdict: APPROVED|REVISE` block with the `## Finding Evidence` batch that
precedes it, drops the template echoes that outnumber real verdicts (a header
inside a quoted persona file, a grep hit, a line-numbered read), and
deduplicates cross-harness copies of one review by normalized text. Prints
verdicts by project, harness, kind, and week; findings by severity,
classification, and state; and the **re-aimed ids** — finding ids that carried
more than one distinct evidence text while they stayed actionable, each of
which is a review round the ledger cannot explain. `--kind plan|code|all`
selects the review loop, `--project <basename>` (repeatable) narrows to one
repository, `--json <path>` writes the complete dataset for the skill's
judgment half; verdicts with no finding ids (pre-evidence-plane narratives)
are reported as unclassified and carried in the JSON. Reads the trace roots
only; never writes under `~/.claude` or `~/.codex`. Exit 2 when neither root
exists.

```bash
./bin/review-verdicts --since-days 31 --kind plan --json "$SCRATCH/verdicts.json"
```

Behavioral coverage lives in `tests/test_review_verdicts.py`.

### `check-shell-syntax` — shell-script parse gate

Runs `bash -n` over every shell script (selected by shebang) under `bin/` and
`.githooks/`, so a parse error in a gate or hook script is caught by the gate
rather than surfacing the next time that script runs — possibly inside the
failure path it guards. Exit 0 clean; exit 1 with one `ERROR:` line per
failing file. Part of `./bin/check policy` as `policy-shell-syntax`.

```bash
./bin/check-shell-syntax
```

Behavioral coverage lives in `tests/test_shell_syntax.py`.

### `new-name` — ledger slug generator

Prints one random, memorable, hyphenated slug (default two words) for naming
`lessons/` and `user-actions/` files. Filters connective filler tokens and
refuses candidates that collide with any existing basename across all four
ledger directories (`lessons/`, `lessons-archived/`, `user-actions/`,
`user-actions-archived/`). Exit 2 on a word count below 2; exit 1 if no
acceptable slug is found within the attempt budget.

```bash
./bin/new-name        # two words (the ledger convention)
./bin/new-name 3      # three words
```

Behavioral coverage lives in `tests/test_new_name.py`.

### `check-anonymization.sh` — pre-publish leak guard *(starter-only)*

Scans every tracked file for the two *mechanizable* leak classes — real absolute/home paths and commit-SHA-like tokens — and exits non-zero on any finding. Optionally reads a gitignored local name denylist (`bin/anonymization-denylist.local`, seeded from the committed `.example`) and greps for those private names too. Run it before any push.

```bash
./bin/check-anonymization.sh          # scan; exit 1 on findings
./bin/check-anonymization.sh --help   # usage
```

Starter-only: this script enforces [`policies/anonymize-log-references.md`](../policies/anonymize-log-references.md), which exists because *this* template repo is public. `stamp` and `teach` do not transfer it — a private downstream project has nothing to anonymize against itself. The `bin/` convention and the triage policy above **are** universal and do propagate.
