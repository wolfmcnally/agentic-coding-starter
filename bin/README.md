# bin/ — Deterministic script reference

`bin/` is the repo's home for **deterministic executables** — the mechanistic half of the methodology. Per [`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md), work that is exact, repeatable, and judgment-free lives here as a plain script rather than in an agent: it runs identically every time, costs nothing to invoke, is unit-testable, and behaves the same under every harness (Claude Code, Codex, …).

## Convention

- **Invoke repo-relative:** `./bin/<name>`. Scripts `cd` to the repo root themselves where they need to, so they work from any working directory.
- **One concern per script.** A script does one mechanical job and exits with a meaningful status code (0 = clean/done, non-zero = findings/failure).
- **Document every script here** — what it does, when to run it, and its exit/refusal behavior — so this README is the operator-facing index for the directory. Derived projects extend this list as they add their own mechanistic scripts.
- **Reach for `bin/` deliberately.** When a phase needs a repeatable check, a mechanical sweep, a generator, or a reconciler, that is `bin/` work, not agent work. When it needs judgment, it is not. The triage rule is [`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md).

## Scripts

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
```

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

Universal contract: [`policies/build-gates.md`](../policies/build-gates.md).
`stamp`, `learn`, and `teach` preserve the atomic interface while adapting its
implementation to the destination's language, runtime policy, metadata, and
lockfile. Behavioral coverage lives in
`tests/test_toolchain_entrypoints.py`, `tests/test_check.py`, and
`tests/test_check_receipt.py`.

### `check-receipt` — durable full-gate record and exact reuse

Internal manager used by `bin/check all` and the pre-push hook. It identifies
the complete candidate through `kickoff-tree-id`, records running and terminal
metadata plus the full gate log, and writes a reusable success receipt only
after the candidate, environment, and durable artifacts verify. Pre-push reuse
additionally requires a clean tree and every non-deleted pushed ref to equal
`HEAD`; any miss, malformed record, corruption, or query failure runs the full
gate. It is normally not invoked directly.

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
`role_timeouts`, and `run_budgets` sections hold separate model/effort fields,
execution budgets, and the per-phase self-resume budget. Round-trip YAML
handling preserves human comments and extension data. The manager also owns
fail-closed venue preflight, generated cross-harness commands, strict
review-output schemas, immutable role-attempt registration, progress-aware
supervision, fresh-artifact enforcement, exact execution spans, and
evidence-based timeout recommendations. A Python script run via `uv` with
PEP 723 `ruamel.yaml`. Governed by
[`policies/role-models.md`](../policies/role-models.md),
[`policies/role-timeouts.md`](../policies/role-timeouts.md),
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
./bin/kickoff-config preflight
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

```bash
./bin/kickoff-evidence --help
```

```bash
./bin/kickoff-evidence validate --run-dir /absolute/run/directory --require-final
```

Governed by
[`policies/orchestration-evidence.md`](../policies/orchestration-evidence.md);
behavioral coverage lives in `tests/test_kickoff_evidence.py`.

### `execution-telemetry` — exact shared execution trace

Records append-only stage, role, wait, tool, and gate spans in one trace;
reconciles interrupted spools; computes union-based makespan and concurrency;
and projects a privacy-safe phase handoff. The handoff is the only input to the
committed HTML report.

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
tracked repository-internal Markdown links and the complete phase lifecycle:
each phase-table row has one recognized status, at most one row is `⬅️`, idle
incomplete work has exactly one next row, and active or complete work may have
none. Link scanning exempts fenced code blocks *and* inline code spans — a
link quoted inside backticks is a quoted edit target, not a live link. It also
enforces [`policies/phase-status.md`](../policies/phase-status.md) over
per-phase files: a `status:` frontmatter field or a `Status: ✅`-shaped
declaration line in any `plan/phase-*.md` fails; narrative emoji mentions in
prose stay fine.

```bash
./bin/check-catalogs
```

Behavioral coverage lives in `tests/test_check_catalogs.py`.

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
