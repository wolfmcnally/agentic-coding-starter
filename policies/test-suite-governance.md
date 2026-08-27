# Test-suite governance policy

Every executable proof belongs to the repository's declared proof estate. The
estate and its deterministic manager travel with the methodology; its family
contents, selectors, tiers, timings, effectiveness cases, and audit judgments do
not. A newly stamped or taught project must inventory and assay its own suite.
The design rationale is
[`test-suite-value-governance.md`](../briefs/test-suite-value-governance.md).

## Required estate

The repository MUST maintain:

1. A machine-readable manifest covering every inventoried test definition and
   each structural proof surface declared by the authoritative gate and tracked
   hooks.
2. For each proof family: a stable id, kind, selectors, source-path mappings,
   contract, risk class, oracle, tier, runner, and admission record. Fast-lane
   families additionally require a red witness and nearest-overlap account.
3. A reproducible baseline bound to the manifest and inventory digests.
4. An append-only audit ledger for any proposed consolidation or disposition.
5. Local effectiveness evidence for admitted historical defects and holdout
   mutants, kept outside routine test execution.

Every current proof is retained during initial adoption. Removing or merging a
proof is a later reviewed change and MUST trace test-to-test dependencies and
producer-to-consumer artifacts before judging redundancy.

## Deterministic manager

The repository manager MUST inventory, validate, select, and report without
model judgment. Validation fails closed on malformed schemas, duplicate ids,
missing or multiply claimed proofs, nonexistent selectors or paths, unsupported
runners, undeclared gate or hook surfaces, stale digest bindings, invalid audit
records, or incomplete effectiveness evidence.

Selection has only two safe results: a validated focused set or the complete
suite. Vital selects all families admitted to that tier. Changed selects the
union of every family matching each changed path. If the manifest is invalid, a
selected family cannot run, the comparison ref cannot be resolved, or any
changed path is unmapped, the manager MUST choose full and state why.

## Lane authority

`./bin/test` with no arguments and `./bin/check all` remain full. Repositories
may expose `./bin/test --vital`, `./bin/test --changed-from <ref>`,
`./bin/check vital`, and `./bin/check changed <ref>` only through the validated
manager selection.

Vital and changed are iteration aids. They NEVER replace either candidate-bound
phase-close gate, the handoff-tree gate, a pre-push full-gate receipt, or a phase's
explicit acceptance command. Pre-commit may run structural estate validation;
it must not imply full acceptance.

## Local effectiveness gate

Before activating a fast lane, the repository MUST admit a local set of
historical-defect and holdout-mutant cases and demonstrate that the lane detects
all of them. Each case records its class, stable id, candidate identity,
manifest and inventory digests, exact command, expected and observed result,
detecting families, output digest, and denominator. Holdouts remain outside the
routine suite. A missing case, digest mismatch, or non-detection invalidates the
fast lane and widens selection to full.

No universal numerical reduction target, duration budget, risk taxonomy, or
minimum corpus size exists. Those values are recipient-local decisions and must
be justified by the recipient's own inventory and assay.

## Evidence and reporting

Governance reports MUST be deterministic, privacy-safe, and derived from the
manifest, inventory, audit ledger, and assay records. Generated counts identify
their denominator. Historical reports are evidence, not executable authority;
the live manifest and manager decide whether a lane may run.
