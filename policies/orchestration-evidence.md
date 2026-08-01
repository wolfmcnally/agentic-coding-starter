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

## Candidate identity

`./bin/python bin/kickoff-tree-id` is the sole candidate-identity implementation. It hashes
tracked content regardless of staging, tracked deletions, normalized modes,
symlink targets, and nonignored untracked files in bytewise path order.
Ignored runtime state, standalone book checkouts, `.gates/`, and nested engine repositories do not enter the engine candidate. A clean submodule
contributes its checked-out commit; a dirty submodule fails closed. Staging
alone does not change identity.

Every change manifest, finding transition, revision packet, and gate record
names the candidate it describes. A candidate mismatch is an error, never a
warning or an assumed continuation.

**The candidate is recomputed, never cached.** A run's tree identity changes for
reasons that have nothing to do with the code under review: `plan/INDEX.md` and
the top-level `LOG.md` are tracked files, so the marker flip and the START block
both move it before any role is dispatched. `kickoff-evidence current-candidate`
recomputes it and records it in the run's **lineage**, and that recomputed id is
what roles receive. The lineage is the run's own history — seeded at `init` and
extended wherever the tool observes a candidate — not a list anyone maintains.

A **new** finding's `introduced_in` may name any candidate in that lineage, not
only the current head. A reviewer that stamps the id it was given is telling the
truth; rejecting it discards correct work over the orchestrator's bookkeeping,
which is exactly what happened to a seven-finding plan review. The set stays
closed: an id the run never observed is still refused, because a finding bound
to a tree nobody saw is bound to nothing. A `resolved_in` still requires the
current candidate — resolution is a claim about the tree as it stands now.

## Evidence records

`./bin/python bin/kickoff-evidence` owns and validates four records:

- **Authority manifest:** repository-relative path, content hash, optional
  locator, and priority.
- **Change manifest:** reviewed/current candidate ids; added, modified,
  mode-changed, and deleted paths; risk tags; selected tests and selection
  reason; intentionally unchanged neighbors; authority drift; review-rebase
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
neither open severity nor uncertainty. The five-cycle cap remains a hard
runaway backstop.

## Revision packets and rebasing

`./bin/python bin/kickoff-evidence packet` compiles the revision packet. It includes
unresolved findings, reviewed/current candidate ids, causal path/hash changes,
authority drift, risk/test-selection facts, gate evidence, and explicit
omission rules. Closed, rejected, superseded, unchanged-authority, and
unchanged-candidate details may be omitted because their source hashes remain
recorded and original files remain readable.

Rebase to a complete review when authority or scope changes, a new risk class
appears, a public API or persisted format changes, security/concurrency/
irreversible-state boundaries change, the revision disperses beyond the
reviewed surface, an acceptance claim is invalidated outside the prior delta,
or trustworthy continuity is lost. When impact is indeterminate, rebase.

## Candidate-bound verification

Use three levels:

1. focused, smallest falsifying behavioral test or proof during editing;
2. affected suites and static/structural checks at revision close;
3. the complete phase-prescribed sequence and `./bin/check all` once after
   code-critic approval, against the unchanged approved candidate.

Record every executed gate and its selection reason. Focused selection may be
agent-judged or supplied by a project-specific dependency tool, but uncertain
impact fails closed to broader verification. A relevant candidate change
invalidates prior gate evidence. Verify candidate identity before and after
the final sequence; mutation by a read-only gate fails the phase.
`./bin/python bin/kickoff-evidence validate --require-final --required-final-command
"./bin/check all"` is the mechanical acceptance proof and must run immediately
after the final gate, before status and append-only log bookkeeping change the
working tree. It also refuses phase close while a finding remains `open`,
`addressed`, or `blocked-owner`. Close-out bookkeeping may follow; it does not
retroactively change the accepted implementation candidate.

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
that refusal is deliberate: the dispatch record is immutable, so a span-less row
makes the whole run unvalidatable and cannot be repaired afterwards — creating
the span late only moves the error to "dispatch and intelligence span ids do not
agree". Correctness is required at write time, not forgiven at read time.

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

Evidence contains engine-relative paths, hashes, findings, and nondisclosing gate results—not
secrets, environment dumps, credentials, ignored private data, or arbitrary
source copies. Project-specific high-assurance profiles may restrict evidence
further; they may not weaken candidate binding or the final full gate.

## Trace-bound execution

Schema-3 runs bind `run.json` to one open kickoff trace/root, the initial open
`orchestration.setup` span, review lane, follow-up route, mechanically derived
initial role set, and required orchestration-stage set. Every dispatch is
preceded by an immutable `register-role-attempt` row and atomic handoff.
Validation joins registrations one-to-one with closed intelligence/wait spans,
rejecting omissions, duplicates, metadata drift, gaps, and unregistered spans.

Sequential reconciliation spans measure setup, planning, implementation,
acceptance, and close preparation. Final timing validation requires the
route-appropriate successful stages, contiguous attempts, no stage overlap,
and close preparation last. Accepted review dispatches must carry the
candidate-bound convergence integers produced by `ingest-findings`.

Managed gates use `run-gate`; `record-gate` is nonfinal imported evidence only.
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
