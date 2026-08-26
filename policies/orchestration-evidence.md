# Policy: Candidate-Bound Orchestration Evidence

`kickoff` preserves independent review while making later rounds incremental.
Every material review, revision, and gate is bound to exact run-scoped
evidence. Narrative continuity or a remembered green result is not evidence.

## Run isolation

After the target phase or sub-phase is resolved and before its first
implementation role invocation, allocate a new opaque run directory with
`mktemp -d`; never reuse a predictable path from an earlier or interrupted
run. A just-in-time decomposition call belongs to the parent-resolution
pre-run and does not share evidence with the child run it creates. Evidence is
local runtime state and stays under a gitignored location or the run-scoped
temporary directory. It is not committed.

Initialize the run through `./bin/python bin/kickoff-evidence init` with the phase file,
its cited briefs, applicable policies, `plan/INDEX.md`, `CLAUDE.md`, declared
dependencies, and the immediately preceding completed phase as authorities.
Original files remain authoritative; the manifest is an index and drift
sensor, not a summary that replaces them.

`init` requires both lane declarations (`--review-lane full|light|one-shot`,
`--evidence-lane full|light` — [`review-lanes.md`](review-lanes.md)) and
derives the run's required role operations and orchestration stages from them:
`one-shot` drops the planner attempt and the planning stage mechanically. Both
lanes are recorded immutably in the run metadata. In the `light` evidence
lane, role registration, span joins, and stage envelopes are validated when
present but their absence does not fail validation — the recorded lane is the
auditable declaration of that demotion. Everything else in this policy is
lane-independent, and the final candidate-bound gate under
`validate --require-final` is mandatory in every lane.

## Candidate identity

`./bin/python bin/kickoff-tree-id` is the sole candidate-identity implementation. It hashes
tracked content regardless of staging, tracked deletions, normalized modes,
symlink targets, and nonignored untracked files in bytewise path order.
Ignored runtime state, `.gates/`, and nested repositories do not enter the
candidate. A clean submodule
contributes its checked-out commit; a dirty submodule fails closed. Staging
alone does not change identity.

Every change manifest, finding transition, revision packet, and gate record
names the candidate it describes. A candidate mismatch is an error, never a
warning or an assumed continuation.

**The candidate is recomputed, never cached.** A run's tree identity changes for
reasons that have nothing to do with the code under review: `plan/INDEX.md` and
the top-level `LOG*.md` logs are tracked files, so the marker flip and the START
block both move it before any role is dispatched. The phase-close harvest and
the user-action lifecycle move it the same way and for the same kind of reason,
through `lessons/`, `lessons-archived/`, `user-actions/`, and
`user-actions-archived/`. Those six surfaces are the orchestrator's own
bookkeeping candidate-movers, and they are the whole of it.
`kickoff-evidence current-candidate`
recomputes it and records it in the run's **lineage**, and that recomputed id is
what roles receive. The lineage is the run's own history — seeded at `init` and
extended wherever the tool observes a candidate — not a list anyone maintains.

A **new** finding's `introduced_in` may name any candidate in that lineage, not
only the current head. A reviewer that stamps the id it was given is telling the
truth; rejecting it discards correct work over the orchestrator's bookkeeping,
which is exactly what happened to a seven-finding plan review. The set stays
closed: an id the run never observed is still refused, because a finding bound
to a tree nobody saw is bound to nothing. A `resolved_in` still requires the
current candidate — resolution is a claim about the tree as it stands now — with
one recorded exception, under *Candidate drift under an in-flight dispatch*
below.

## Evidence records

`./bin/python bin/kickoff-evidence` owns and validates four records:

- **Authority manifest:** repository-relative path, content hash, optional
  locator, and priority.
- **Change manifest:** reviewed/current candidate ids; added, modified,
  mode-changed, and deleted paths; risk tags; selected tests and selection
  reason; falsifiers (the mutation that reds each new test); the coder's
  focused gate status; intentionally unchanged neighbors; authority drift; review-rebase
  reasons.
- **Finding ledger:** stable id, severity, authority, evidence, affected
  paths, required outcome, introduction/resolution candidates, state,
  classification, and disposition.
- **Gate ledger:** command, candidate id, selection reason, exit status,
  warning count, final-gate flag, and optional artifact digest.

Exact fields are the executable schema in `./bin/python bin/kickoff-evidence`; behavioral
tests are the contract floor. Agents exercise judgment to produce the facts.
The script validates and projects them mechanically.

## Findings and convergence

Plan findings use `PLAN-FNNN`; code findings use `CODE-FNNN`. An id continues
to mean the same authority and required outcome for its lifetime.

Allowed states are `open`, `addressed`, `verified`, `closed`,
`rejected-with-evidence`, `blocked-owner`, and `superseded`. Closure requires
the candidate that resolved the finding. Reopening a verified, closed, or
rejected finding is explicit and counted.

`addressed → rejected-with-evidence` is legal: it is the reviewer accepting an
implementer's counter-argument, which is a different outcome from the reviewer
rejecting a finding on first look. Without that edge a finding answered by
evidence rather than by a change had no truthful terminal state and had to be
walked backwards through `open` to reach one.

The first review batches every blocker found. Revision review resolves the
existing ledger first, then examines the causal change surface. A new finding
is classified `introduced-by-revision`, `newly-exposed-by-resolution`, or
`missed-in-full-pass`; an initial finding is classified `initial`.

Continue a loop only while at least one blocking finding advances and no
closed finding reopens at equal or greater severity. Escalate on recurrence,
oscillation, authority disagreement, or two consecutive rounds that reduce
neither open severity nor uncertainty. The ten-cycle cap remains a hard
runaway backstop; below it, continuation is the supervising authority's
judgment call
([`four-canonical-agents.md § Runaway backstop`](four-canonical-agents.md)).

## Revision packets and rebasing

`./bin/python bin/kickoff-evidence packet` compiles the revision packet. It includes
unresolved findings, reviewed/current candidate ids, causal path/hash changes,
authority drift, risk/test-selection facts, the coder's failure analysis, gate
evidence, and explicit omission rules. Closed, rejected, superseded,
unchanged-authority, and unchanged-candidate details may be omitted because
their source hashes remain recorded and original files remain readable.

The failure analysis is the reflexion contract: on every revision round the
coder's Change Evidence must state *why* the previous attempt produced the
findings being fixed — root cause, not restatement — and `capture-change`
rejects a revision capture that omits it. The packet carries the analysis
forward so the next review judges the fix against the coder's own theory of
the failure, and the phase-close lessons harvest ([`lessons.md`](lessons.md))
reads it as sensor input.

Rebase to a complete review when authority or scope changes, a new risk class
appears, a public API or persisted format changes, security/concurrency/
irreversible-state boundaries change, the revision disperses beyond the
reviewed surface, an acceptance claim is invalidated outside the prior delta,
or trustworthy continuity is lost. When impact is indeterminate, rebase.

## Candidate-bound verification

Use four levels:

1. focused, smallest falsifying behavioral test or proof during editing;
2. affected suites and static/structural checks at revision close;
3. the complete phase-prescribed sequence and `./bin/check all` after
   code-critic approval, against the unchanged approved implementation
   candidate;
4. a bare `./bin/check all` after every tracked close write, against the actual
   handoff tree.

**Rehearse before an expensive or irreversible acceptance step.** When a phase's
acceptance includes a long or externally-irreversible run — a live data
migration, a deploy, a bulk external operation — the complete gate and the
affected consumer probes run *first*, as recorded **non-final** rows, before
that run begins:

1. `./bin/check all` green, so cheap failures surface in minutes rather than
   after hours of irreversible work;
2. every identity the change touched resolved through its **production
   consumer**, not merely inspected in place — a data repair that satisfies
   file-and-ledger inspection can still fail the first thing that consumes it,
   and neither a coder forbidden from the live run nor a read-only critic can
   see that.

The implementation-candidate contract is unchanged: its `./bin/check all`
runs last against the unchanged approved candidate, and rehearsal rows are
explicitly non-final. After close bookkeeping changes the tree, the separate
handoff gate proves that actual tree. Only the discovery of cheap failures
moves earlier.

Record every candidate-bound implementation gate and its selection reason. Focused selection may be
agent-judged or supplied by a project-specific dependency tool, but uncertain
impact fails closed to broader verification. A relevant candidate change
invalidates prior gate evidence. Verify candidate identity before and after
the implementation sequence; mutation by a read-only gate fails the phase.
`./bin/python bin/kickoff-evidence validate --require-final --required-final-command
"./bin/check all"` is the mechanical implementation acceptance proof and must
run immediately after the implementation gate, before status and append-only
log bookkeeping change the working tree. It also refuses close bookkeeping
while a finding remains `open`,
`addressed`, or `blocked-owner`. Close-out bookkeeping may follow; it does not
retroactively change the accepted implementation candidate, but the bare
handoff gate must pass before completion is reported. Its ignored full-gate
receipt binds the post-bookkeeping tree. No tracked write may follow a
successful handoff gate.

The ordinary commit and non-force push of gate-proved work
([`human-in-the-loop.md`](human-in-the-loop.md)) are close-out bookkeeping in
exactly that sense: they run only after the successful `--require-final`
validation and the handoff gate, they change no tracked content, and they
therefore leave the accepted candidate identity intact. An operator restriction
may suppress either action; neither may be used to repair a failed gate.

## The registration file is not the ledger

`register-role-attempt` does two writes: it appends the record to the run's
append-only `role-attempts.jsonl`, and it writes that same record, alone, to the
path given as `--output`. **`--output` is the registration file** — the one a
dispatch passes as `--telemetry-role-registration`, and the one the watcher
cross-checks for uniqueness against the ledger. The ledger itself is never a
registration: `bin/kickoff-config watch` refuses it by name. It has to, because a
ledger holding exactly one record is also a valid JSON object and would parse,
so the same argument would work for the first role registered and die on the
second — an order-dependent trap that teaches the wrong contract and fails at the
worst moment. Give each attempt its own `--output` path.

## Every registered attempt has an intelligence span, rejections included

An attempt the watcher refuses before launch still consumed a registration, so
validation still demands exactly one closed `intelligence` span for it. A
rejected dispatch opens that span and closes it **error 127 at rejection time**,
records `--idle-telemetry not-dispatched`, and creates **no** wait span.
`record-role-dispatch` refuses a dispatch that names no intelligence span, and
that refusal is deliberate: terminal amendments are append-only, so a
span-less terminal row makes the whole run unvalidatable and cannot be repaired
afterwards — creating the span late only moves the error to "dispatch and
intelligence span ids do not agree". Correctness is required at write time, not
forgiven at read time.

## Native span recipes and declared telemetry gaps

A delegated dispatch has its `intelligence` and `wait` spans built by
`bin/kickoff-config watch`. A native dispatch does not, and validation joins
both spans against the registration field by field — so an orchestrator that
hand-builds the pair and omits one `--model` produces a join that can never
close, because a span is immutable once finished. `register-role-attempt`
therefore writes `<handoff>.span-recipe.json` for every native attempt and
prints its path; `span-recipe` re-emits it, substituting the intelligence span
id into the wait argv. Do not hand-assemble either command.

When a wait-span join is nonetheless broken, the run may **own the defect in
writing** with `record-telemetry-incomplete`, naming the exact span, the exact
missing fields, and the cause. Validation then reports that attempt as
telemetry-incomplete — in `timing-summary`'s markdown section and its
`telemetry_incomplete` projection array — instead of refusing outright. The
declaration is not a bypass:

- a wait span that is **absent** still fails, because degradation covers a
  malformed span, never a missing one;
- the declaration must name the span the trace actually carries;
- every excused field must really be defective, and every defective field must
  really be excused — a record that excuses a correct field, or omits a broken
  one, fails;
- a declaration for an unregistered attempt fails.

The reasoning is that a validator which can only refuse converts one honest
orchestrator slip into a phase that can never close, which pressures the next
operator toward fabricating a passing record. A typed, bounded degradation
keeps the record honest and the contract satisfiable at once. Attempts closed
this way are measured, not omitted: their intelligence spans and durations stay
exact.

`repin-tools` re-pins a run's bundle to the current tree and prints both
manifest digests. It exists for the case the snapshot cannot serve — a repair
the active run itself needs — and is deliberately explicit rather than silent.

## An unmeasured review pass is caught while it can still be repaired

`validate` refuses, unconditionally in the full evidence lane and not only
under `--require-final`, whenever an accepted review dispatch closed
successfully and its intelligence span carries no convergence integers. It
names each `operation#attempt` with its span id.

The check has to run there because the repair only exists there. Re-ingesting
the pass's findings with `--review-span-id` attaches the metrics to a live
span; once the trace finalizes the span is immutable and that route is gone.
Checking only at `timing-summary` meant a run passed validation all night with
unmeasured passes and discovered the gap after finalization, when the only
remaining "repair" would re-ingest earlier artifacts, drive `verified → open`,
and reopen resolved findings to satisfy a validator. The check runs on the
run's **runtime** spans, not a finalized bundle, precisely so it works on an
open trace.

Four of the five incidents recorded upstream were not uningestable batches at
all: the ingest was chained into a command block ending in a backgrounded
dispatch, so its refusal was never read. The batches were repairable at the
time and nothing looked. This latch is what looks.

## Derived convergence metrics for a refused batch

A review pass that genuinely succeeded and whose batch was then **structurally
refused** closes with a successful span and no metrics, and the latch above
cannot help once the trace is closed. `attach-derived-metrics` is the
sanctioned recovery. It is an **overlay** — the record lives in
`derived-metrics.jsonl` and `validate` reads it when the span has none — never
a span attach. Two reasons: a finalized span cannot be written at all, which is
exactly where the gap bites; and a derived number written onto a span whose
ingest never produced it would be indistinguishable from a measured one.

Every ingest, accepted or refused, appends one row to the run's append-only
`ingest-log.jsonl`, carrying the artifact digest, the reported finding count,
the namespace-restricted `{id: state}` ledger captured **before** any mutation,
and — on a refusal — the typed refusal codes. That recorded base is what makes
the merge replayable after `findings.json` has been rewritten wholesale. Only
refusals about the batch's own content are journaled; a bad run directory,
inconsistent flags, a candidate mismatch, or an unreadable artifact is an
orchestrator error, not a defect in a review pass. On the accepted path the row
is appended after the ledger is written, so the journal can never claim a merge
that did not land.

The derivation declares a **refusal class** — the machine-checkable fact of
which rule fired — from a closed set:

- `finding-id-format`
- `resolved-in-not-current-candidate`
- `immutable-field-restated`

It supplies no integers. There is no `--findings-reported` and no
`--actionable-findings`: operator-supplied numbers are what make a record an
assertion instead of a measurement. The tool computes both from the refused
artifact and the journal row's recorded base, and `validate` **recomputes and
compares** them on every run. That recomputation is the analogue of "every
excused field must really be defective" above; without it this would be a
write-only ledger with no reader that could ever contradict it.

One operator input does reach a recorded integer, and it is named here rather
than left implicit: **`--id-map`**, on the `finding-id-format` class alone. The
bijection must be total over the malformed ids, injective, in-namespace, and
free of collisions *within the batch* — but a target may legally land on an
existing ledger entry, because `open → open` is an allowed transition. Mapping
a malformed id onto an existing `open` finding therefore merges two actionable
entries and lowers `actionable_findings` by one, in the flattering direction.
This grants no power the ordinary ingest path lacks — a reviewer can emit that
same id directly — and `--corroborating-artifact` removes the discretion
entirely, because the identity check then pins every id to a batch that was
measured natively.

The record is not a bypass:

- the declared class must match a **recorded** refusal — of that exact artifact,
  named against that exact review span — with **exactly** that class's codes;
  extra codes refuse, because a batch that also carried a substance defect was
  never a measurable review pass, and an ingest that was never attempted proves
  nothing at all;
- the span must be the pass's own successful review intelligence span and must
  **not** already carry metrics; a pass whose ingest landed has nothing to
  derive;
- both integers must **recompute** from artifacts still present at their
  recorded digests, replaying the four rules the recorded base can answer —
  namespace prefix, `introduced_in` lineage, `resolved_in` currency, and the
  allowed state transitions — with only the declared class's own rule
  suppressed. The immutable-field check, the evidence-substitution check,
  the placeholder-evidence check (`carried forward unchanged` / `text not
  supplied` is not evidence), and the suspected-not-blocking check (a
  read-only reviewer's unexecuted claim, marked `SUSPECTED`, is capped below
  `blocking`)
  (a finding that stays actionable keeps its `evidence`; a new objection is a
  new id) are not among them and cannot be: the recorded base is
  `{id: state}`, not the prior fields they would compare against. Nothing recorded is wrong for want of it, because that rule is
  either the suppressed one or provably never fired, but the replay is those
  four rules and the policy says so rather than claiming all of them;
- an optional corroborating artifact must itself have been ingested with
  metrics attached to its own review span (no chaining), may support exactly
  one derivation (no fan-out), and must be identical to the refused artifact in
  severity, state, classification, authority, evidence, required outcome,
  disposition, affected paths, batch verdict, and cardinality — the only
  permitted delta is the one the declared class names, and that delta must
  really be present.

The verb enforces every one of those checks itself, including the ones its
reader would apply later — the dispatch for `(operation, attempt)` must exist,
be accepted, name the declared span, and that span must be successful and
unmeasured. **A verb that appends to an append-only evidence ledger enforces
every check its reader will apply, because the reader's refusal has no undo:** a
record accepted at write time with a wrong attempt would refuse every later
`validate` and `timing-summary` permanently, and the only recovery would be
hand-editing an append-only ledger.

For the same reason, deriving and then **honestly re-ingesting** the same pass
is not an error. Once the span carries its own measurement, the real numbers
win, the derived record is reported as **superseded** rather than orphaned, and
the run still closes. The operator who did the more honest thing must never be
the one who gets blocked.

A superseded record is not recomputed — supersession entails both that the span
carries metrics and that an accepted ingest named it, so the full check would
refuse twice over conditions that have stopped mattering. But it is not
unverified either, because it goes on **publishing** its refusal class, its
cause, and its corroboration state in `timing-summary`. Two checks therefore
survive supersession: the pinned journal row must still resolve uniquely, and
both recorded artifacts must still be present at their recorded digests. After
supersession nothing else in the run references those artifacts, so they are
the first thing a cleanup removes — and without this floor that removal would
be silent while the entry kept being published. **Whenever a record's
verification is relaxed, ask immediately what is still being published on the
strength of it.**

Two deliberate divergences from the `record-telemetry-incomplete` precedent,
stated so neither reads as an oversight:

1. **The ingest journal has no duplicate-key refusal.** Re-ingesting a refused
   batch is the normal recovery, so repeated rows for one artifact are the
   expected shape. `derived-metrics.jsonl` does refuse a duplicate
   `(operation, attempt)`, as the telemetry ledger does.
2. **The record is an overlay, not an attach.** The telemetry declaration
   annotates a span that exists and is malformed; this one supplies a value the
   span will never hold, and keeps it visibly derived. `timing-summary` prints
   it in its own `#### Derived review convergence metrics` section and carries
   it in a `derived_review_metrics` projection array, stating that the integers
   were recomputed from artifacts on disk rather than produced by an ingest.

## Candidate drift under an in-flight dispatch

`kickoff-tree-id` hashes nonignored untracked files, so **any** write by **any**
session moves the candidate. A role dispatched against candidate A returns
findings honestly stamped A, `ingest-findings` binds to the current candidate B,
and the whole batch is refused. A shared working tree is stricter for
tree-hashed evidence than for staging: one stray write invalidates an entire
review.

**The freeze convention.** While a role dispatch is in flight, the repository
tree belongs to one writer. Announce dispatch-open and dispatch-return; queue
other sessions' writes for the gaps, or hand them to the active writer to land
at a candidate boundary. "Harmless" is not a property of an edit — it is a
property of the timing. Gitignored runtime state is structurally invisible to
the candidate: the freeze covers nonignored paths only.

**The convention is now observed rather than merely stated.** Every folded
dispatch carries both the candidate it opened against and the candidate it
returned at, and **the pair brackets the child's run**: a dispatch whose two
candidates differ moved under the role, and — this is the half worth stating,
because it is the one an operator will rely on — a dispatch whose two
candidates are equal really did not move.

That converse is a property of *when* each observation is taken, not of whether
both are recorded, and it is easy to ship a version where only the second is
true. The open side is captured **by whoever is closest to the child**: for an
external role — which under the shipped pins is every reviewer role —
`kickoff-config watch` calls the run's pinned `current-candidate` immediately
before it spawns the child, later and therefore truer than any id the
orchestrator could hand down. The watcher appends that opening before spawning
the child. The return side is recomputed by the terminal `record-role-dispatch`
amendment **after the child has terminated**. Writing both observations at open
would carry two dispatch-open candidates, and then a concurrent write during
the role's run — the case this whole mechanism exists for — would leave them
equal and earn a "did not move the candidate" refusal that is simply false.

A native dispatch has no watcher, so there the orchestrator passes
`--dispatch-candidate` itself, naming a candidate that must already be in the
run's lineage, appends `--state opened` before launch, and appends the terminal
amendment once the role has returned. A dispatch that records no open candidate
is not refused, but no drift recovery is available for it: the recovery below
needs both sides, and an unrecorded one is not reconstructible afterwards. A
failed candidate capture is recorded as a telemetry incompleteness rather than
killing the dispatch, and costs exactly that recovery; failure to append the
opening itself refuses launch.

**The manifest store.** Only two manifests were ever persisted per run
(`candidate.json`, `reviewed-candidate.json`), both overwritten in place, and
`lineage.jsonl` carries ids only — so at the moment a batch was refused, the
manifest the role had been dispatched against was already gone and the drift was
unclassifiable. Every candidate the tool observes is therefore also written to
`<run>/candidates/<candidate_id>.json`, content-addressed and **write-once**: a
manifest whose name is its own digest cannot legitimately change. A
classification whose manifests are not both present in that store **refuses**;
it never assumes disjointness.

**The repair is not falsification.** Rewriting `resolved_in` to the ingesting
candidate records that a reviewer verified a tree it never saw, and
hand-reconstructing the reviewed tree has been tried upstream and failed to
reproduce the candidate byte-exactly. The sound recoveries are to re-run the
review against the current candidate, or to accept the mismatch **only** with a
recorded, proven-disjoint drift classification.

### Three independent acceptance checks

`accept-candidate-drift` classifies the paths that changed between a dispatch's
two candidates, recomputed from the two stored manifests. Acceptance requires
**all three** of the following, and each is independently capable of refusing a
drift the other two accept:

1. **Partition** — every drifted path lies in the declared inert set below.
2. **Reviewed surface** — no drifted path appears in `change.json`'s
   `changed_files`, nor in any ledger finding's `affected_paths`.
3. **Authority** — no drifted path is a declared authority in `authority.json`.

The third is not implied by the first: `plan/` splits. `plan/INDEX.md` is inert
bookkeeping and sits in the partition, while `plan/phase-N.md` is the review's
own specification — and `plan/INDEX.md` is itself routinely a *declared
authority*, so the authority check is what stops an inert-partition path from
being waved through when the review was bound to its content.

Any check failing, **or any path the classifier cannot place**, fails closed. A
false refusal costs one re-review; a false accept records a review of a tree
nobody read.

### The partition vocabulary

A path partition is a stand-in for "could this drift have changed what the
review means." Its dangerous direction is the false accept — a path in the inert
set that actually mattered — which is precisely why checks 2 and 3 exist and are
independent. The vocabulary is deliberately tiny: only the surfaces this
document already names as the orchestrator's own bookkeeping candidate-movers.
Everything unlisted fails closed. This block is the single source of truth and
is parsed by `bin/kickoff-evidence`; it is not restated in code.

```yaml
# kickoff-evidence drift partitions
inert:
  - LOG*.md
  - plan/INDEX.md
  - lessons/
  - lessons-archived/
  - user-actions/
  - user-actions-archived/
```

An entry ending in `/` is a directory prefix; any other entry is a single
path matched component by component, so `*` never crosses a `/` and `LOG*.md`
names only root-level logs, never a nested file with the same basename. The
list is read from this file at classification time and again at every
`validate`, so a record is never accepted on a vocabulary that has since been
withdrawn.

### The record

`accept-candidate-drift` appends to the run's append-only
`<run>/candidate-drift.jsonl`: the dispatch it describes, both candidate ids,
the exact drifted paths, and a mandatory nonempty `cause`. Neither candidate nor
the path list is an operator input — all three are read from the dispatch row and
recomputed from the stored manifests, which is what makes the record a
measurement rather than an assertion. A duplicate `(operation, attempt)`
refuses, as the telemetry ledger does.

The verb enforces every check its reader will apply, because the reader's
refusal has no undo: the dispatch must exist, be accepted, name both candidates,
and the two must actually differ. `validate` then **re-derives** the drifted-path
set from the two stored manifests and re-runs all three checks on every run;
a record whose paths no longer recompute, or whose classification no longer
holds, refuses. Accepted drift is published in both `timing-summary` formats —
markdown section and a `candidate_drift` projection array — because a run that
accepted a review of a tree the ingest did not hold must say so where anyone
reading its close will see it.

### What the drift record does *not* relax

- **`resolved_in` only.** With an accepted record for the review pass's own
  dispatch, and only when the record's return candidate is the candidate the
  ingest binds to, a finding's `resolved_in` may name that dispatch's open
  candidate. An ingest with `--no-review-span` has no dispatch to bind to and
  gets no relaxation.
- **Gate rows and the final seal are untouched.** `validate --require-final`
  still demands the final candidate-bound gate row with equal
  before/after/current candidates. A gate whose candidates differ has measured a
  tree other than the one being accepted, and that is lane- and drift-independent.
- **`introduced_in`** is already relaxed to the run's lineage and needs nothing.
- **The batch-level candidate mismatch in `ingest-findings`** stays an
  orchestrator error, not a content refusal — an ingest bound to the wrong
  candidate is a bad invocation, not a defect in a review pass.

## Protocol recovery

Delegated execution uses a three-signal result: child status, artifact
freshness, and terminal stream completeness are recorded independently.
Ordinary success requires all three plus the role's exact output shape.

Exit 66 (`completed-unverified-protocol`) means only that a successful child
left a fresh artifact while its terminal stream was incomplete. Before using
that artifact, the orchestrator must validate its verdict/report shape, ingest
and validate its evidence block when the role produces findings, and confirm
the expected candidate id. If any check fails, use the normal stage fallback.
Exit 65, a timeout, a nonzero child, a stale artifact, or an invalid artifact
is never recoverable success.

## Measurement and privacy

Record direct facts already carried by the evidence: packet bytes and hashes,
changed-path count, finding counts/states/reopenings/classifications, gate
results, candidate ids, and protocol signals. Record unavailable data as
`unknown`; never infer a reassuring category.

For every accepted Plan Review and Code Review dispatch, finding ingestion
attaches two exact nonnegative integers to that review's intelligence span:
the number of Finding Evidence entries reported on the pass, and the number of
that namespace's actionable findings remaining after reconciliation. An empty
approved evidence block is measured zero, not omitted. These per-pass values
are the durable convergence series; cumulative ledger size is not a substitute.

**`actionable_findings` counts the whole merged ledger, namespace-filtered —
never the batch alone.** After the batch is merged, it is every finding whose id
carries that review namespace and whose state is `open`, `addressed`, or
`blocked-owner`, including entries the batch never mentioned. A rule that
counted only the batch's own non-merging findings gives the same answer whenever
the pre-existing actionable set happens to be empty, and a different one
otherwise; the coincidence is what makes the error survive a spot check. Any
recomputation of this number — by hand, or by `attach-derived-metrics` — must
reproduce the whole-ledger expression, base term included.

Evidence contains repository-relative paths, hashes, findings, and nondisclosing gate results—not
secrets, environment dumps, credentials, ignored private data, or arbitrary
source copies. Project-specific high-assurance profiles may restrict evidence
further; they may not weaken candidate binding or either close gate.

## Trace-bound execution

Schema-3 runs bind `run.json` to one open kickoff trace/root, the initial open
`orchestration.setup` span, review lane, follow-up route, mechanically derived
initial role set, and required orchestration-stage set. Every dispatch is
preceded by an immutable `register-role-attempt` row and atomic handoff.
Validation joins registrations one-to-one with closed intelligence/wait spans,
rejecting omissions, duplicates, metadata drift, gaps, and unregistered spans.

`role-dispatch.jsonl` uses an append-then-amend lifecycle. Immediately before
launch, the watcher appends a `state: opened` row naming the registered attempt,
its intelligence span when available, and the dispatch-open candidate when
capture succeeded. After the child terminates, it appends an accepted or
rejected terminal amendment with the return candidate and completed span
topology. Readers fold the pair. An opening with no amendment is an interrupted
dispatch and makes the run incomplete; it is evidence that work began, not a
malformed row to discard. This opening is the layer that survives an externally
killed watcher.

Teardown hardening is a separate in-process layer. A `PermissionError` from
either the SIGTERM or SIGKILL process-group call, or another cleanup exception,
becomes a diagnostic and cannot prevent span bookkeeping or the terminal
amendment. It does nothing when the watcher itself is externally killed; the
pre-launch opening is what covers that case. Failing to kill is recoverable
through timeout bookkeeping; failing to record is not.

A terminal `record-role-dispatch` with no opening refuses because an external
watcher death would otherwise disappear from the ledger and make an incomplete
trace appear complete. A legitimate recovery must pass
`--no-open-row '<reason>'`; the tool appends that reason to the separate
`dispatch-open-omitted.jsonl` audit artifact, and validation requires the
terminal row and omission record to correspond one-to-one. The opt-out is an
audited exception, not a silent compatibility path.

Sequential reconciliation spans measure setup, planning, implementation,
acceptance, and close preparation. Final timing validation requires the
route-appropriate successful stages, contiguous attempts, no stage overlap,
and close preparation last. Accepted review dispatches must carry the
candidate-bound convergence integers produced by `ingest-findings`. Those
integers attach to the review pass's own intelligence span, so `ingest-findings`
requires `--review-span-id` and refuses without it: a span is immutable once its
trace is finalized, which makes an omission unrepairable after the fact rather
than merely untidy. An ingest that is not a review pass — an orchestrator-authored
state transition with no dispatched span — uses `--no-review-span '<reason>'`,
which records the omission in `review-metrics-omitted.jsonl` rather than leaving
it silent.

Managed gates use `run-gate`; `record-gate` is nonfinal imported evidence only.
Both verbs take exact positional argv after `--` and derive the display command
with `shlex.join`, so a writer cannot emit the noncanonical command/argv pair
that its validator refuses. Historical imported rows with the old whole-command
single-element argv remain readable; validation refuses each by its exact
`gates.jsonl` line, recorded command, argv, and canonical display.
Final eligibility requires a complete matching span, exact argv, and equal
before/after/current candidates. Acceptance validates while the root is open;
finalization and `timing-summary` precede completion bookkeeping.

Initialization also creates an immutable run-scoped tool bundle containing the
exact evidence binary, candidate tree identifier, telemetry CLI, and telemetry
library plus the external watcher and its `kickoff.yaml`, all covered by one
hash manifest. Every later operation in that run uses those
pinned executables; the evidence binary rejects access through a mutable live
copy. A phase may therefore change its own construction machinery without
stranding the active run. The bundle is a same-run snapshot and never a
historical schema reader or migration shim.
