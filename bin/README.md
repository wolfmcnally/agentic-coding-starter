# bin/ — Deterministic script reference

`bin/` is the repo's home for **deterministic executables** — the mechanistic half of the methodology. Per [`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md), work that is exact, repeatable, and judgment-free lives here as a plain script rather than in an agent: it runs identically every time, costs nothing to invoke, is unit-testable, and behaves the same under every harness (Claude Code, Codex, …).

## Convention

- **Invoke repo-relative:** `./bin/<name>`. Scripts `cd` to the repo root themselves where they need to, so they work from any working directory.
- **One concern per script.** A script does one mechanical job and exits with a meaningful status code (0 = clean/done, non-zero = findings/failure).
- **Document every script here** — what it does, when to run it, and its exit/refusal behavior — so this README is the operator-facing index for the directory. Derived projects extend this list as they add their own mechanistic scripts.
- **Reach for `bin/` deliberately.** When a phase needs a repeatable check, a mechanical sweep, a generator, or a reconciler, that is `bin/` work, not agent work. When it needs judgment, it is not. The triage rule is [`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md).

## Scripts

### `role-models` — harness-aware per-role model/venue for `/kickoff`

Reads and writes the repo-root `role-models.yaml` — a two-level `harness → role → model[@effort]` config that resolves which model, implied harness, and optional reasoning effort runs each of the four canonical roles (planner, reviewer, coder, critic), scoped by which harness is orchestrating. Backs the `/roles` skill (the parse/validate/write is the mechanical half; the skill is the thin wrapper). Validates every harness, role, model, effort, and model/effort combination against a closed vocabulary and rejects unknowns non-zero, leaving the config untouched. GPT-5.6 code names map deterministically: `sol` → `gpt-5.6-sol`, `terra` → `gpt-5.6-terra`, `luna` → `gpt-5.6-luna`; Claude pins use the same suffix grammar and additionally support `@max`. A Python script run via `uv` (PEP 723 inline `pyyaml`). Governed by [`policies/role-models.md`](../policies/role-models.md).

```bash
./bin/role-models --show                                   # config + resolved-for-this-harness view
```

```bash
./bin/role-models codex reviewer: opus, critic: opus       # set pins in a harness section
```

```bash
./bin/role-models claude reviewer: sol@medium, critic: terra@low
```

```bash
./bin/role-models codex reviewer: opus@high, critic: fable@max
```

```bash
./bin/role-models coder: opus                              # no harness token → the `default` section
```

```bash
./bin/role-models --reset                                  # restore the shipped cross-review default
```

Universal: `/stamp` and `/teach` carry it (and the cross-vendor-review default config) into every derived project — every project has the same four roles and the same default.

### `check-anonymization.sh` — pre-publish leak guard *(starter-only)*

Scans every tracked file for the two *mechanizable* leak classes — real absolute/home paths and commit-SHA-like tokens — and exits non-zero on any finding. Optionally reads a gitignored local name denylist (`bin/anonymization-denylist.local`, seeded from the committed `.example`) and greps for those private names too. Run it before any push.

```bash
./bin/check-anonymization.sh          # scan; exit 1 on findings
./bin/check-anonymization.sh --help   # usage
```

Starter-only: this script enforces [`policies/anonymize-log-references.md`](../policies/anonymize-log-references.md), which exists because *this* template repo is public. `/stamp` and `/teach` do not transfer it — a private downstream project has nothing to anonymize against itself. The `bin/` convention and the triage policy above **are** universal and do propagate.
