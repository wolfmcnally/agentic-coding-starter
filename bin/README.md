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
`CHECK ALL PASS`.

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
`tests/test_toolchain_entrypoints.py` and `tests/test_check.py`.

### `install-hooks` — opt in to tracked Git hooks

Configures only the current checkout's `core.hooksPath` to `.githooks`, whose
pre-push hook calls `./bin/check all`. Installation is explicit and
idempotent. A different existing hooks path is preserved and reported; only
`--force` replaces it. `--dry-run` reports the proposed change without writing
Git configuration.

```bash
./bin/install-hooks --dry-run
```

```bash
./bin/install-hooks
```

Universal contract: [`policies/build-gates.md`](../policies/build-gates.md).
Behavioral coverage lives in `tests/test_install_hooks.py`.

### `kickoff-config` — human-editable `kickoff` configuration and enforcement

Validates and safely edits repo-root `kickoff.yaml`, whose `role_models` and `role_timeouts` sections hold separate model/effort fields and execution budgets. Round-trip YAML handling preserves human comments, ordering, quoting, and data under `extensions`; strict known sections reject typos; scoped resets never overwrite the other section; every write validates first and atomically replaces the file. The same manager performs fail-closed live venue preflight, routing-verified and progress-aware subprocess supervision, fresh-artifact enforcement, gitignored telemetry, and evidence-based timeout recommendations. A Python script run via `uv` with PEP 723 `ruamel.yaml`. Governed by [`policies/role-models.md`](../policies/role-models.md) and [`policies/role-timeouts.md`](../policies/role-timeouts.md).

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
./bin/kickoff-config preflight
```

```bash
./bin/kickoff-config watch --role reviewer --venue claude --model opus --effort high --phase 2 --stdout-file /tmp/reviewer.events.jsonl --stderr-file /tmp/reviewer.stderr --result-file /tmp/reviewer.result -- claude --model opus --effort high <production flags>
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

Initializes and validates the authority, change, finding, packet, and gate
records for one `kickoff` run. It extracts exact JSON evidence blocks from role
artifacts, enforces stable finding identity and state transitions, detects
authority/risk rebases, compiles deterministic plan/code revision packets, and
rejects gate records for stale candidates. Run `--help` or a subcommand's
`--help` for the full schema-driven interface.

```bash
./bin/kickoff-evidence --help
```

```bash
./bin/kickoff-evidence validate --run-dir /absolute/run/directory --require-final
```

Governed by
[`policies/orchestration-evidence.md`](../policies/orchestration-evidence.md);
behavioral coverage lives in `tests/test_kickoff_evidence.py`.

### `check-anonymization.sh` — pre-publish leak guard *(starter-only)*

Scans every tracked file for the two *mechanizable* leak classes — real absolute/home paths and commit-SHA-like tokens — and exits non-zero on any finding. Optionally reads a gitignored local name denylist (`bin/anonymization-denylist.local`, seeded from the committed `.example`) and greps for those private names too. Run it before any push.

```bash
./bin/check-anonymization.sh          # scan; exit 1 on findings
./bin/check-anonymization.sh --help   # usage
```

Starter-only: this script enforces [`policies/anonymize-log-references.md`](../policies/anonymize-log-references.md), which exists because *this* template repo is public. `stamp` and `teach` do not transfer it — a private downstream project has nothing to anonymize against itself. The `bin/` convention and the triage policy above **are** universal and do propagate.
