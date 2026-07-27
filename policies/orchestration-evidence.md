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

Initialize the run through `bin/kickoff-evidence init` with the phase file,
its cited briefs, applicable policies, `plan/INDEX.md`, `CLAUDE.md`, declared
dependencies, and the immediately preceding completed phase as authorities.
Original files remain authoritative; the manifest is an index and drift
sensor, not a summary that replaces them.

## Candidate identity

`bin/kickoff-tree-id` is the sole candidate-identity implementation. It hashes
tracked content regardless of staging, tracked deletions, normalized modes,
symlink targets, and nonignored untracked files in bytewise path order.
Ignored runtime state does not enter the candidate. A clean submodule
contributes its checked-out commit; a dirty submodule fails closed. Staging
alone does not change identity.

Every change manifest, finding transition, revision packet, and gate record
names the candidate it describes. A candidate mismatch is an error, never a
warning or an assumed continuation.

## Evidence records

`bin/kickoff-evidence` owns and validates four records:

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

Exact fields are the executable schema in `bin/kickoff-evidence`; behavioral
tests are the contract floor. Agents exercise judgment to produce the facts.
The script validates and projects them mechanically.

## Findings and convergence

Plan findings use `PLAN-FNNN`; code findings use `CODE-FNNN`. An id continues
to mean the same authority and required outcome for its lifetime.

Allowed states are `open`, `addressed`, `verified`, `closed`,
`rejected-with-evidence`, `blocked-owner`, and `superseded`. Closure requires
the candidate that resolved the finding. Reopening a verified, closed, or
rejected finding is explicit and counted.

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

`bin/kickoff-evidence packet` compiles the revision packet. It includes
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
`bin/kickoff-evidence validate --require-final --required-final-command
"./bin/check all"` is the mechanical phase-close proof.

## Protocol recovery

Delegated execution records child status, artifact freshness, and terminal
stream completeness independently. Ordinary success requires all three plus
the role's exact output shape.

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

Evidence contains paths, hashes, findings, and nondisclosing gate results—not
secrets, environment dumps, credentials, ignored private data, or arbitrary
source copies. Project-specific high-assurance profiles may restrict evidence
further; they may not weaken candidate binding or the final full gate.
