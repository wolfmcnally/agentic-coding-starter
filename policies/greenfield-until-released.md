# Policy: Greenfield Until Released

A project is **greenfield** by default until it ships a first stable, externally-consumed release — and explicitly amends this policy. Until then, agents must not write code or schemas that exist solely to preserve compatibility with earlier internal shapes. Breaking changes are not just permitted; they are the *expected* response to learning that an earlier shape was wrong.

## Why this policy exists

Backward-compatibility burden has a cost that compounds:

- Every legacy alias / deprecated field / migration path is a permanent slice of the surface area.
- Every shim is code that has to be maintained, tested, and reasoned about.
- Agents are particularly prone to adding compatibility scaffolding "to be safe." That scaffolding is dead weight in a greenfield project where no external user depends on the prior shape.

Greenfield projects move faster when the agent is allowed — required, even — to replace wrong shapes directly. The cost of a rename is a find-and-replace; the cost of carrying a legacy name forever is paid every session.

## The rule

**Until this policy is explicitly amended, do not add:**

- Backward-compatibility shims (`old_api()` that forwards to `new_api()`).
- Legacy aliases (`PipelineV1` → `Pipeline`).
- Schema migrations to read older on-disk formats.
- "Transitional" code paths that handle both old and new field names.
- `@deprecated` markers on still-supported surfaces (the surface is either current or removed; "deprecated" implies a transition period that this policy denies).
- Configuration knobs whose only purpose is to opt back into older behavior.
- Conditionals like `if version < 2: old_path else: new_path` when no version-2 consumer exists.
- Tests of "old format" or "v1 compatibility" when no v1 consumer survives.

**Instead, when an earlier shape turns out wrong:**

1. Pick the new shape.
2. Replace the old shape directly — rename, refactor, change the schema.
3. Update *every* call site, fixture, test, sample data file, and reference in briefs/plan/docs to the new contract.
4. Delete the old shape's code, tests, and documentation.
5. Note the change in the phase's END block (the LOG entry is the audit trail of breaking changes).

## What this policy does *not* cover

This policy is about *internal* compatibility burden — the project carrying its own past forward. It does not relax rigor in any other direction. Things still required:

- **Quality.** Code is still well-typed, well-tested, and idiomatic.
- **Acceptance gates.** Every phase still satisfies its [empirical acceptance criteria](acceptance-empirical.md).
- **External API contracts.** When the project *consumes* an external API (a third-party service, a vendor SDK, an OS API), normal fault-tolerance applies — handle the API's documented error modes, retry where appropriate, validate inputs at the boundary. The external API is not under this policy's scope; only the project's own surface area is.
- **Robustness at runtime.** A function that takes a string still validates the string. A parser still handles malformed input cleanly. "Greenfield" doesn't mean "fragile" — it means "no compatibility cruft."
- **Data the user has invested time in.** If the project has accumulated files the human created by hand (pipeline recipes, hand-authored content, captured logs), an in-flight breaking change should include a migration *of those files* as part of the phase, even though the code stops supporting the old shape afterward. The point is to keep the user's investment alive, not to keep two code paths alive.

## How this policy ends

The policy ends when one of these is true:

- The project ships a v1.0 release intended for external consumers, and amends this policy file to declare the post-v1 backward-compatibility regime (typically semver-based deprecation windows).
- The project becomes a dependency of another project (anything outside this repo starts importing or invoking its surfaces).
- The human explicitly amends the policy for a specific surface.

Until one of those triggers fires, every phase honors the greenfield rule.

## Per-phase waiver

The human may grant a phase-specific waiver of this policy. For example: "This phase changes the recipe schema; keep a one-week migration window so I can re-render existing pipelines before the old format is dropped." Waivers are:

- **Explicit.** Stated in the current session, not inferred from context.
- **Scoped.** Apply to a named surface for a named duration.
- **Logged.** The phase's END block records the waiver (e.g., `Waiver: recipe-schema v1 reader retained until 2026-06-01`).
- **One-shot.** Do not amend the policy as a whole. The next phase reverts to greenfield discipline unless the human grants another waiver.

## Verification

A clean state satisfies:

```bash
# No common "compat shim" markers in the deliverable
grep -RIn -E '(deprecated|legacy|backward.compat|_v1\b|_old\b|fixme.*migration)' \
  --include='*.py' --include='*.ts' --include='*.rs' --include='*.go' \
  --include='*.toml' --include='*.json' --include='*.yaml' --include='*.yml' \
  project/ 2>/dev/null && echo "REVIEW: possible compat cruft" || echo "no compat markers"

# No version-conditional branches in code without an explicit waiver in LOG.md
grep -RIn -E 'if .*[Vv]ersion *[<=>]|if .*format *==.*[\"\x27]v?1' \
  --include='*.py' --include='*.ts' --include='*.rs' --include='*.go' \
  project/ 2>/dev/null
```

These greps are heuristics, not proofs. The real verification is review during the `code-critic` pass: any compat-shaped code is flagged unless the phase's END block carries an explicit waiver line.
