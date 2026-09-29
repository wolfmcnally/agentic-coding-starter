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
3. Disposition every baseline proof exactly once as `retain`, `repair`, `consolidate`, or `delete` in an append-only ledger. `repair` keeps the contract active and records that its assertion was corrected, for a proof whose contract is real but whose assertion could not fail. Each row MUST carry its contract, oracle, red witness, nearest overlap, replacement evidence, and standalone rationale.
4. Declare a size for every pytest family and a test-lane time budget, and bring the retained estate within both on the reference machine (see [Time budget](#time-budget)).
5. Demonstrate at least the declared recall over a frozen local historical-defect
   corpus and at least the declared kill recall over a held-out local mutant
   corpus, each holding at least its declared case floor.
6. Retain direct executable proof for every applicable custody, security,
   authority, concurrency, atomicity, corruption, recovery, public-contract,
   schema, deploy, and core-success risk. An inapplicable class requires a
   rationale and an activation trigger.

**The case floors and the time budget are recipient-declared; the floors on effectiveness are not.** `effectiveness_floors` carries `min_historical_cases` and `min_mutant_cases` alongside the recall minimums, and a repository declares the values its own history can support. This template declares twelve cases per class because it reset an overgrown estate and has the defect history to prove the result. A freshly stamped recipient declares an empty-but-frozen corpus, because it has no defect history to recall, and a null reference machine until someone on its own hardware records one. `reassess` widens the declaration as phase history accrues — each ratified lesson and closed defect is a case the recipient can freeze, and the floors rise with them.

What never moves: the recall minimums over whatever corpus exists, direct proof for every applicable critical risk, the size ceilings on whatever machine runs the suite, frozen selection before holdout execution, and digest binding. A class with no declared floor and no cases is reported as **unmeasured** — never as zero, never as passing — and the report names it, so an empty corpus cannot be read as a clean one.

The historical corpus may guide selection. Selection MUST be frozen before the
holdout runs. Every case's command and mutation-patch digest MUST bind the
observed report to the exact frozen corpus, and holdout misses MUST remain
recorded. When the size ceilings, time budget, recall floors, and direct-risk obligations cannot
coexist, work parks for the owner. The denominator never changes to make a
result pass.

## Judging a proof

These criteria are the one home for proof-value judgment. Authoring, critique, reset, and reassessment apply them; persona and skill text cites this section rather than restating it.

**Admission.** Before a proof is written, answer four questions; a missing answer means it is not written yet:

1. What observable behavior, invariant, or independent contract does it protect?
2. What credible regression makes it fail?
3. Why does existing coverage not already catch that failure? Each contract has one primary proof at its strongest boundary. Another layer needs its own distinct risk the primary cannot reach. Extending a table case or shared fixture is preferred over a near-duplicate proof.
4. Does it need a production seam (an export, flag, wrapper, parameter, or injection hook) that no production caller needs? If so, the proof moves to the real boundary and the seam is not added.

A proof that would break under behavior-preserving refactoring asserts the implementation, not the behavior, and is rewritten at the owning boundary before it lands. A regression proof must fail on the pre-fix code for the intended reason; one regression at the owning boundary covers the bug, not one per layer it crosses.

**Junk patterns.** A new proof matching one fails admission unless the retention bar names the contract it independently guards, and reassessment hunts existing proofs for them:

- assertion-free coverage probes, and assertions that cannot fail on any reachable input;
- self-comparisons and identity copiers;
- copied fixtures, inventories, manifests, or export lists;
- exact source, import, or string greps;
- private predicate or call-shape tests duplicated at a real boundary;
- duplicate invocations of one contract, including replays of a shared helper through each of its callers;
- proofs whose only purpose is preserving test-only exports, globals, or wrappers, and dead production code whose only callers are tests;
- expected values produced by the helper or renderer under test;
- mocks that implement the asserted behavior, or one identical mock standing in for different interfaces;
- fixtures that supply the receipt, ordering, or callback the code under test should produce, or persistence asserted against a store the path never writes;
- capability proofs that restate a declared flag instead of exercising what the flag promises;
- negative controls that pass for an unrelated reason, such as a refusal from a different guard or a rejection the production path never reaches;
- fault-injection and timing proofs that never show the fault or window was reached, such as a fake that raises without first asserting the state the real function would see, or a kill that can land between writes; each asserts the precondition and is shown red against a deliberately broken implementation;
- names or fixtures that promise more than the assertions check.

**Retention bar.** Resemblance to the implementation is a proxy, and it can invert: the proofs that guard exact bytes, keys, paths, and wire formats look most like the code they protect. A proof is retained when it independently enforces a public interface, protocol, configuration, storage format, security, platform, default, generated artifact, release, or architecture contract; when call order is observable behavior; when it is a regression with a credible failure mode; or when source inspection is the cheapest independent guard, failing when the contract changes and surviving an identifier-only rename. Static or slow is not a removal reason. A retained proof that fails on the baseline is a suspected product defect: reproduce it and repair its owner rather than removing the proof.

## Removal and growth

Deleted and consolidated proofs MUST leave the executable estate completely.
Their dead fixtures, helpers, and caller wiring leave with them.
Skipping, deselecting, renaming, quarantining, or hiding a proof is not removal.
A consolidated proof names a retained executable replacement; a deleted proof
explains why it has no independent contract.

**Every retirement batch passes a preservation review before it lands**, at reset and afterward, whether a phase, a sweep, or a reassessment proposes it. A reviewer who did not choose the retirements compares the removed coverage against the proofs that remain and names each contract that lost its only proof, and each new or carried assertion that cannot fail. Every restored contract gets one deliberate mutation of its production owner, observed red in the keeper and restored byte-exactly, recorded like any other red witness. The review completes when every reported gap is restored or rejected with source evidence. The recall floors are statistical and measure nothing until a corpus exists; this review is the per-contract guard that holds from the first batch.

A new proof requires a named active contract or risk, independent oracle, red witness, and non-subsumption account, recorded as a `proof_admission`, and a declared size for its family. There is no count budget: what an agent may add is limited by the [admission questions](#judging-a-proof) and by the [time budget](#time-budget), not by how many proofs already exist. Validation fails closed when any admission evidence is absent.

A **red witness is recorded at construction, not re-run at close.** A mutant exists to vet a proof while that proof is being written: apply the intended defect, watch the named case fail at the assertion that encodes the guarantee, restore the code byte-exactly, and watch it pass. The mutant is then discarded. What the estate retains is the named defect in the family's `mutation_evidence`; the close record that admitted the proof carries the command, the failing node and the clean result after restoration. A name in that list is a claim that the mutation was applied, observed red at the named assertion, and restored — never a plan to try it. No red-witness patch is committed, and no close gate runs one.

What this gives up is worth stating: a committed mutant re-proves on every run that its bound case still catches its fault, which guards against a proof being weakened later. That standing guarantee is traded for a gate that fails only for reasons of correctness, since a patch anchored on source lines breaks whenever the guarded function is edited. A reviewer who suspects a proof has been weakened re-applies the recorded defect.

**The effectiveness corpus is the one committed set of patches, and it is a dated measurement, not a standing battery.** Its historical-defect and held-out patches are anchored on source lines for the same reason red witnesses are, so edits strand them between measurements, and nothing gates on that. `assay` runs at adoption and at every governed sweep and stamps each observation with its date; validation reports recall with the date of the oldest observation (`recall_as_of`), never as a live property. The sweep's assay refuses a patch that no longer applies; the sweep re-anchors it to the same defect, or retires the case with its rationale, and measures again. (Operator ruling, 2026-09-29.) A check added to code the corpus mutates must be shown not to fire merely because a planted defect is present in the assay copy; otherwise the check itself becomes the detector and recall rises with no proof behind it.

After the reset, retirement and repair are append-only events. A `proof_repair` targets one currently active proof, self-binds, carries the same evidence as a disposition, and leaves the active set unchanged; a proof may be repaired more than once.

A `proof_retirement` may target only one currently active baseline or admitted
proof, exactly once. It records `consolidate` with a named active replacement or
`delete` with no replacement, plus the same contract, oracle, red-witness,
overlap, replacement, and rationale evidence as the original reset. Replay
removes that proof. Renaming a proof is an admission of the new name followed by
a consolidating retirement of the old one. The replayed active set MUST equal
the live inventory; a shadow proof, repeated retirement, or missing event
refuses.

## Time budget

The cost an estate imposes is the time it takes to run, and a count of proofs is a poor stand-in for it: one subprocess-heavy proof can outweigh a hundred pure ones, and a count cap rewards folding new contracts into existing proofs whose names then stop describing them. Time is governed directly, with each check shaped to survive the noise in wall-clock measurement.

- **Size classes bound each proof.** Every pytest family declares `size: small | medium | large`, and `size_ceilings_seconds` gives each class a per-leaf ceiling roughly an order of magnitude above the last. A family takes the smallest class whose ceiling is at least twice its slowest leaf's measured time, so ordinary noise cannot cross a ceiling. A leaf over its family's ceiling fails, on any machine, from a single run. A `large` family names in its admission why the contract cannot be proved more cheaply.
- **A lane budget bounds the whole.** `time_budget` declares `test_lane_seconds`, a `tolerance`, and a `reference_machine` fingerprint. The budget is judged only on the machine that set it; anywhere else it reports **unmeasured**, never within or over. A single run over the budget plus tolerance is an **advisory**; only the median of three runs over it (`./bin/test-governance timing --samples 3`) confirms an **over** and fails.
- **Every full run is measured.** `./bin/test` without arguments records per-leaf times, and the full gate's `policy-test-time` member judges that record. A record that does not cover exactly the current pytest estate is stale and reports unmeasured.
- **An overrun parks for the owner.** A confirmed overrun is resolved by making proofs cheaper, retiring dominated proofs through the preservation review, or the owner raising the budget. The budget is never raised, the tolerance widened, or a family's size moved up to make a gate pass without the owner's ruling, recorded in the phase or the ledger.

Instruction counting is a steadier measure of CPU-bound work, but it does not see the subprocess, filesystem and waiting time that dominate an agentic repository's proofs, so it is not the governed measure here.

## Deterministic manager and lanes

The repository manager MUST inventory expanded pytest leaves, collapsed families,
gate members, and hook commands; validate the frozen baseline, complete ledger,
sizes, time-budget declaration, direct risks, corpus, and dated effectiveness
report; judge recorded timings; select vital and
changed lanes; execute assays; and report or reassess the current estate.

The changed-path selection is the local commit gate and the implementation-candidate gate (`policies/build-gates.md`). Invalid or indeterminate selection widens to full. `./bin/test` without lane arguments, the handoff gate, pre-push custody, and durable receipts always use the full retained estate. Pre-commit runs structural validation only and never claims full acceptance.

## Reassessment and transfer

Every governed sweep MUST run `./bin/test-governance reassess` and rerun the local
assay, re-anchoring or retiring any case whose patch no longer applies, and
propose further consolidation when a proof is dominated. It runs
`./bin/test-governance timing --samples 3` on the reference machine when one is
available and reports the slowest proofs and any family whose measured time no
longer fits its size. This is an executable shrinkage obligation.

The same sweep reads the proofs whose code changed since the previous sweep against the [junk patterns](#judging-a-proof), and makes a layer pass over each contract with more than one proof: it names the keeper at the strongest boundary, preferring a real boundary with a fake dependency over a mocked collaborator, and proposes the other layers for consolidation unless each names a distinct risk. Findings are proposals in the sweep's decision queue; each batch the operator ratifies passes the preservation review before it lands.

`learn`, `teach`, `stamp`, and bootstrap transfer this policy and procedure as an
atomic bundle. Every recipient freezes and assays its own estate. No transfer may
seed another repository's survivors, selectors, timings, corpora, risk judgments,
dispositions, or effectiveness results.
