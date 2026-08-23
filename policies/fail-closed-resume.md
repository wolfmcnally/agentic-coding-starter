# Policy: Fail-Closed Park and Diagnosed Resume

This policy mechanizes the runtime doctrine's park/resume rules
([`../briefs/methodology.md`](../briefs/methodology.md) § Orchestration
runtime doctrine). A fail-closed park preserves the truth of an evidentiary
run. A diagnosed resume may begin a new run without weakening that record, but
only within explicit authority, novelty, integrity, and budget bounds.

## Fail closed first

When a run meets a parking condition, finish it exactly as if no resume were
possible:

- stop further role dispatches and state-changing execution;
- write the ordinary append-only park and `END` records without changing their
  form, severity, or terminal outcome;
- close the run's open telemetry spans with the truthful failure outcome and
  finalize the trace;
- preserve watcher-owned artifacts and the failed run directory byte-for-byte;
- prove the repository candidate was restored, or record the exact candidate
  lineage when restoration is neither required nor truthful;
- prove every process the run started has ended and every resource it held is
  released.

Permission to resume changes only whether the orchestrator waits for another
operator message. It never turns a failed run into success, edits its
evidence, or allows work to continue inside it.

## Failure signatures and novelty

Every park records a **failure signature**: the failed operation, execution
boundary, exact terminal condition, causal generator, and affected contract.
The phase keeps an append-only signature ledger across its traces at
`.kickoff/failure-signatures.jsonl` — gitignored local runtime state, one JSON
object per park carrying the phase id, trace id, the five signature parts, the
novelty verdict, and the remaining budget. It spans evidence runs because a
signature's recurrence is a fact about the phase, not about any one trace.

A signature is **novel** only when it does not match an earlier signature in
the phase at the level of causal generator. Cosmetic differences in filenames,
ports, candidate ids, role attempts, symptoms, or line numbers do not make the
same generator novel.

A recurring signature always returns to the operator. It may not consume a
self-resume budget, be renamed to appear novel, or be routed to another venue.

## Diagnosed self-resume

A fresh corrective trace may open without another operator relay only when all
of these are true:

1. the current phase grants a positive self-resume budget and at least one
   unit remains;
2. the failure signature is novel for the phase;
3. the causal correction is complete and recorded, not merely a symptom-level
   workaround;
4. the next action remains inside the already authorized plan substance,
   implementation write set, external-state boundary, and operator-decision
   boundary;
5. prior evidence is read-only;
6. candidate restoration or explicit candidate lineage is proved;
7. every relevant process is terminated and every held resource is proved
   released.

Opening the corrective trace consumes one budget unit. Record the decision,
the matched novelty proof, and the remaining budget in the append-only log.
The budget is **per phase, between operator contacts**: any operator relay
restores it to its configured value. The configured value lives in
[`../kickoff.yaml`](../kickoff.yaml)'s `run_budgets.self_resume` key, managed
by `bin/kickoff-config` (`show budgets` / `set-budgets self_resume=N`); the
shipped default is **3** — the doctrine's "small budget between operator
contacts". An absent section means the shipped default; `0` is an explicit
valid pin meaning every park waits for the operator. A phase file may narrow
the budget for its own run; it may not widen it above the configured value.

No self-resume authority reaches across a conflicting narrower bound. A named
single-attempt limit, required operator relay, plan-substance decision,
write-set expansion, designed human checkpoint, deploy or close gate,
financial action, or external-state action wins over the general authority in
this policy.

## Prelaunch correction is not a resume

A dispatcher or watcher rejection before child launch consumes neither a role
dispatch nor provider budget. When the invocation defect is fully determined,
the orchestrator may correct it and relaunch at most once for that registered
dispatch, recording the correction in the trace.

A provider or usage-cap failure, timeout, protocol failure, post-launch
nonzero exit without an admissible artifact, or other post-launch failure is a
park unless a more specific authorized recovery rule applies (exit 66 protocol
recovery per [`role-models.md`](role-models.md) is one). Never retry one of
those by silently changing venue, model, role, or evidence contract.

## Mechanistic substitution

Deterministic transforms belong to the orchestrator. When a role task reduces
to exact substitution, splicing, hashing, schema projection, or another
repeatable transform, the orchestrator may perform it mechanically when the
phase authority permits. The evidence must include:

- the complete source identity;
- the declared transformation;
- the complete result identity;
- a byte-level boundary proof showing every undeclared region unchanged;
- an independent model-role review of the result.

Substitution does not authorize new judgment. If the transform requires a
product, architecture, policy, acceptance, or write-set decision, route that
decision to the normal intelligence role or operator.

Large plan revisions are delta-native: a role emits bounded replacement
clauses, the orchestrator merges them deterministically, and the reviewer
reviews both result and containment proof. A role must not be required to
round-trip a document expected to exceed its single-message artifact ceiling.

## Sealing cadence

Sealing is a **close-time act, not a per-fix act**. A plan, acceptance recipe,
or protocol step must not require a whole-repository reseal — manifest
re-derivation, snapshot, binding-chain replay — after each correction inside a
convergence loop. Corrections run the smallest falsifying check and the
affected revision-close gates; the implementation seal is the complete
candidate-bound validation against the unchanged final candidate at close
([`orchestration-evidence.md`](orchestration-evidence.md) § Candidate-bound
verification), which already invalidates itself if any later implementation
change lands. Tracked close writes then receive the separate bare handoff gate.

Motivating incident (cited per the doctrine's growth rule): a donor project
ran roughly twenty-seven whole-repository reseal cycles in one phase — each a
full preparation → inventory → snapshot → binding replay invalidated by the
next one-line fix — judged pure per-fix ceremony in the phase's own closing
verdict, while the single sealed close carried all the evidentiary weight.
The park this rule prevents is the slow one: a convergence loop whose
per-iteration cost is dominated by re-proving state no decision consumes.

When a role artifact fails ingestion solely on schema or contract shape and
candidate equality proves the underlying work intact, one artifact-only
re-emission is permitted per role attempt when phase authority allows it. The
new prompt embeds the exact live schema, closed vocabularies, and allowed
state transitions rendered from their executable source. The role performs no
implementation work; candidate identity is measured immediately before launch
and after artifact retrieval but before ingestion, and any drift disqualifies
the artifact and parks. Watcher-owned output is never pre-created, edited,
moved, or overwritten by the orchestrator.

## Off-trace diagnosis and instrument qualification

After an evidence failure, diagnosis may proceed read-only or in a fresh
qualification directory outside an evidentiary trace. Classify the failure as
product, instrument, or environment before selecting a correction.

An instrument repair is admissible only after qualification reaches every
affected branch and proves: representative positive admission; a deliberately
wrong probe fails for the intended reason; every declared falsification
control is capable of succeeding under the specified comparator and fixture;
aim or measurement-location evidence for every measurement-consuming
artifact; exact restoration of any mutation; and fail-closed teardown. A
falsification family that cannot fail is invalid; a specified control that
cannot succeed is equally invalid — it tests contradiction, not instrument
fitness. Plan review checks both sides at specification time.

Freeze qualified executor files under a SHA-256 manifest and make them
read-only. A formal run consumes byte-identical copies and varies only
declared data arguments; orchestration code is not authored inside the formal
trace.

## Operator checkpoints and supervision

Designed operator checkpoints are successful stopping points, not blockers or
incomplete work. Keep the required system live only for the requested
observation, present one concrete check at a time when the protocol calls for
back-and-forth work, and never infer acceptance.

Out-of-band supervision is a correction channel. Supervisor evidence is
ingested read-only, its causal claims are independently reconciled with the
trace, and any correction is appended rather than used to rewrite historical
records. Supervision may diagnose and recommend; it does not silently grant
plan-substance, external-state, deploy, or close authority.

## Required park and resume record

The append-only record includes:

- trace and candidate identities;
- exact failure signature and causal correction;
- product/instrument/environment classification where applicable;
- evidence preservation and candidate-lineage proof;
- process and resource teardown proof where applicable;
- whether the signature is novel or recurring;
- the controlling authority and any narrower bound;
- self-resume decision and remaining budget;
- the exact work still pending.

The record is evidence, not narration to be cleaned up later. Corrections are
new append-only entries. Historical artifacts and earlier log text remain
untouched.

## Relationship to other policies

- [`orchestration-evidence.md`](orchestration-evidence.md) owns candidate
  identity, finding ledgers, gates, and the final-candidate seal this policy's
  sealing cadence defers to.
- [`role-models.md`](role-models.md) owns venue routing, preflight, the
  generated dispatch command, and the exit-66 protocol exception.
- [`execution-telemetry.md`](execution-telemetry.md) owns the trace whose
  truthful finalization a park must complete.
- [`human-in-the-loop.md`](human-in-the-loop.md) is a standing narrower bound:
  no self-resume authority ever reaches a commit, push, or acceptance the
  human owns.
