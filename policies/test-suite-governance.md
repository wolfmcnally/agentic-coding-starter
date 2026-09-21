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
4. Keep current families and leaves at or below the declared `max_families_ratio`
   and `max_leaves_ratio` of the frozen denominators.
5. Demonstrate at least the declared recall over a frozen local historical-defect
   corpus and at least the declared kill recall over a held-out local mutant
   corpus, each holding at least its declared case floor.
6. Retain direct executable proof for every applicable custody, security,
   authority, concurrency, atomicity, corruption, recovery, public-contract,
   schema, deploy, and core-success risk. An inapplicable class requires a
   rationale and an activation trigger.

**The ceilings and case floors are recipient-declared; the floors on effectiveness are not.** `reset_limits` carries `max_families_ratio`, `max_leaves_ratio`, `min_historical_cases`, and `min_mutant_cases` alongside the recall minimums, and a repository declares the values its own history can support. This template declares 0.2 ratios and twelve cases per class because it reset an overgrown estate and has the defect history to prove the result. A freshly stamped recipient declares ratios of 1.0 and an empty-but-frozen corpus, because its baseline *is* the template's post-reset estate: a compliant 20% reset would discard four fifths of the universal machinery's direct proofs, and it has no defect history to recall. `reassess` widens the declaration as phase history accrues — each ratified lesson and closed defect is a case the recipient can freeze, and the floors rise with them.

What never moves: the recall minimums over whatever corpus exists, direct proof for every applicable critical risk, the zero-net-growth budget, frozen selection before holdout execution, and digest binding. A class with no declared floor and no cases is reported as **unmeasured** — never as zero, never as passing — and the report names it, so an empty corpus cannot be read as a clean one.

The historical corpus may guide selection. Selection MUST be frozen before the
holdout runs. Every case's command and mutation-patch digest MUST bind the
observed report to the exact frozen corpus, and holdout misses MUST remain
recorded. When the caps, recall floors, and direct-risk obligations cannot
coexist, work parks for the owner. The denominator never changes to make a
result pass.

## Removal and growth

Deleted and consolidated proofs MUST leave the executable estate completely.
Their dead fixtures, helpers, and caller wiring leave with them.
Skipping, deselecting, renaming, quarantining, or hiding a proof is not removal.
A consolidated proof names a retained executable replacement; a deleted proof
explains why it has no independent contract.

The default post-reset family and leaf budgets are zero. A new proof requires a
named active contract or risk, independent oracle, red witness, non-subsumption
account, and either a named approved positive budget or a compensating retirement.
Validation fails closed when any admission or budget evidence is absent.

A **red witness is recorded at construction, not re-run at close.** A mutant exists to vet a proof while that proof is being written: apply the intended defect, watch the named case fail at the assertion that encodes the guarantee, restore the code byte-exactly, and watch it pass. The mutant is then discarded. What the estate retains is the named defect in the family's `mutation_evidence`; the close record that admitted the proof carries the command, the failing node and the clean result after restoration. A name in that list is a claim that the mutation was applied, observed red at the named assertion, and restored — never a plan to try it. No mutation patch or standing mutation battery is committed, and no close gate runs one.

What this gives up is worth stating: a committed mutant re-proves on every run that its bound case still catches its fault, which guards against a proof being weakened later. That standing guarantee is traded for a gate that fails only for reasons of correctness, since a patch anchored on source lines breaks whenever the guarded function is edited. A reviewer who suspects a proof has been weakened re-applies the recorded defect.

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
