# Test-suite governance policy

Every executable proof belongs to the repository's declared proof estate. The
manager, schema, reset procedure, lane integration, gates, hooks, transfer rules,
and reassessment obligation travel together. Family identities, selectors,
timings, corpora, risk judgments, dispositions, and survivors do not.

## Initial adoption

Initial adoption MUST:

1. Freeze a reproducible whole-estate baseline of parameter-collapsed families
   and expanded executable leaves, including authoritative gate and hook proofs.
2. Run a local Pareto assay and physically consolidate or delete dominated
   proofs. Retaining the estate for a later audit is forbidden.
3. Disposition every baseline proof exactly once as `retain`, `consolidate`, or
   `delete` in an append-only ledger. Each row MUST carry its contract, oracle,
   red witness, nearest overlap, replacement evidence, and standalone rationale.
4. Keep current families and leaves at or below 20% of the frozen denominators.
5. Demonstrate at least 80% recall over a frozen local historical-defect corpus
   and at least 80% kill recall over a held-out local mutant corpus.
6. Retain direct executable proof for every applicable custody, security,
   authority, concurrency, atomicity, corruption, recovery, public-contract,
   schema, deploy, and core-success risk. An inapplicable class requires a
   rationale and an activation trigger.

The historical corpus may guide selection. Selection MUST be frozen before the
holdout runs. Every case's command and mutation-patch digest MUST bind the
observed report to the exact frozen corpus, and holdout misses MUST remain
recorded. When the caps, recall floors, and direct-risk obligations cannot
coexist, work parks for the owner. The denominator never changes to make a
result pass.

## Removal and growth

Deleted and consolidated proofs MUST leave the executable estate completely.
Their dead fixtures, helpers, mutation rows, and caller wiring leave with them.
Skipping, deselecting, renaming, quarantining, or hiding a proof is not removal.
A consolidated proof names a retained executable replacement; a deleted proof
explains why it has no independent contract.

The default post-reset family and leaf budgets are zero. A new proof requires a
named active contract or risk, independent oracle, red witness, non-subsumption
account, and either a named approved positive budget or a compensating retirement.
Validation fails closed when any admission or budget evidence is absent.

After the reset, retirement is itself an append-only event. A
`proof_retirement` may target only one currently active baseline or admitted
proof, exactly once. It records `consolidate` with a named active replacement or
`delete` with no replacement, plus the same contract, oracle, red-witness,
overlap, replacement, and rationale evidence as the original reset. Replay
removes that proof and creates one budget. One later admission may consume that
budget exactly once. Reset-era dispositions cannot fund admissions appended
after the post-reset lifecycle begins. The replayed active set MUST equal the
live inventory; a shadow proof, reused retirement, or missing event refuses.

## Deterministic manager and lanes

The repository manager MUST inventory expanded pytest leaves, collapsed families,
gate members, and hook commands; validate the frozen baseline, complete ledger,
caps, budgets, direct risks, corpus, and effectiveness report; select vital and
changed lanes; execute assays; and report or reassess the current estate.

Vital and changed are iteration aids. Invalid or indeterminate selection widens
to full. `./bin/test` without lane arguments, both candidate-bound close gates,
pre-push custody, and durable receipts always use the full retained estate.
Pre-commit runs structural validation only and never claims full acceptance.

## Reassessment and transfer

Every governed sweep MUST run `./bin/test-governance reassess`. It MUST rerun the
local assay when proof code, selection, corpus, or critical-risk applicability
changed, and propose further consolidation when a proof is dominated. This is an
executable shrinkage obligation.

`learn`, `teach`, `stamp`, and bootstrap transfer this policy and procedure as an
atomic bundle. Every recipient freezes and assays its own estate. No transfer may
seed another repository's survivors, selectors, timings, corpora, risk judgments,
dispositions, or effectiveness results.
