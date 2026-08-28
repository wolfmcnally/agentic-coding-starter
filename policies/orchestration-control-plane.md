# Policy: Orchestration Control Plane

Every governed run establishes deterministic executable authority before an
expensive acceptance command may start.

## Immutable command manifest

1. A full-evidence run activates a validated command manifest before any
   managed gate.
2. Manifest bytes are stored content-addressed by SHA-256 and never rewritten.
3. Activation is append-only. A successor must name the current digest in
   `supersedes`; the first activation must not name one.
4. Each command row contains exactly `operation`, positive `attempt`, boolean
   `final`, and a nonempty NUL-free argv array.
5. Every managed gate must match one active row exactly before execution.
6. A final successful gate and final validation must bind the active manifest.
7. Imported non-final evidence may record no manifest, but it never substitutes
   for a managed final gate.

## Command zero

Command zero runs before expensive acceptance and stops on the first refusal:

1. validate the active manifest, venue receipt, and stage topology;
2. execute each manifest-declared side-effect-free selector dry-run;
3. run format validation;
4. prove `LOG.md` extends committed bytes exactly; and
5. prove effective log chronology.

Selector checks must be non-mutating and must enumerate against the
authoritative local inventory rather than a hand-maintained approximation.

## Venue receipt

Preflight must require each non-native target to read unpredictable local bytes
and return their exact SHA-256. The receipt records the routing-configuration
digest, harness, resolved target descriptors, and shared probe digest. An
all-native run records the same schema with no targets. A stale, missing,
malformed, or incomplete receipt refuses initialization or final acceptance.

A model echoing a known sentinel is not a qualified venue. The independent
write-enabled coder toolchain probe remains mandatory and may still route
focused verification back to the orchestrator when the venue cannot run it.

## Candidate identities

The evidence plane records both identities:

- **product candidate** — excludes only the inert vocabulary in
  `policies/orchestration-evidence.md`;
- **full-tree candidate** — includes the entire tracked and
  nonignored-untracked repository.

Product identity may establish that a bounded bookkeeping repair did not alter
the implementation. Full-tree identity remains authoritative for review
handoff, final gates, delivery, and commit custody. Reviewed-surface and
declared-authority drift checks remain separate and mandatory.

## Log construction and custody

`LOG.md` is written only by `bin/log-append` or an explicitly admitted bounded
repair tool. The candidate and staged blobs must begin with the exact committed
bytes. Semantic validity never excuses a byte rewrite.

A later chronology correction may change only the effective anchor. It binds
one unique earlier block by content digest, repeats its recorded anchor, moves
strictly forward, and is itself no later than the correction record. Existing
blocks are never edited.

Every newly appended END or PARK block contains a literal `Lessons:` line.
`bin/check-log` is the one composed gate used by `bin/check`, command zero, and
the staged pre-commit hook.

## One bounded repair

After the first novel bookkeeping failure, one deterministic repair is allowed
only when all of these hold:

- the replacement is fully derivable without judgment;
- the complete candidate validates in memory;
- implementation/product identity is unchanged;
- one atomic replacement writes the candidate;
- post-write bytes exactly equal the validated bytes; and
- the repair and proof are recorded.

Relocation requires unique authenticated block identities and may touch only an
uncommitted suffix. Final-newline repair is closed to `LOG.md`,
`EXECUTION_LOG.jsonl`, and `plan/INDEX.md`.

Ambiguity, contextual patching, a recurring signature, a second attempt, a
substantive edit, an identity change, or failed verification parks for the
operator. The orchestrator never widens the repair set to avoid a park.

## Transfer

This policy, its brief, managers, evidence schema, kickoff instructions, hook
wiring, behavioral proofs, catalogs, and proof-estate admissions transfer as
one atomic capability. A recipient inventories its own commands, inert paths,
selectors, venues, and proofs; no donor command list or local judgment is
copied as authority.
