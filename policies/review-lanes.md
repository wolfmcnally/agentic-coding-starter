# Policy: Review Lanes and Proportional Follow-ups

Every phase pays for the review it needs, not the review some other phase needed. The four-role loop ([`four-canonical-agents.md`](four-canonical-agents.md)) is the default initial pipeline and the right shape for any phase that makes decisions; for purely mechanical phases, a first-cycle `APPROVED` with zero findings is review that found nothing — pure cost. This policy adapts both the initial lane and later correction route, with empirical validation as the backstop.

## The three initial lanes

| Lane | Pipeline | When |
|---|---|---|
| `full` (default) | planner → plan-reviewer → coder → code-critic | Any initial phase implementation that decides anything. When in doubt, this. |
| `light` | planner → coder → code-critic | Mechanical initial implementations only (eligibility below). Plan review (kickoff Step 4) is skipped. |
| `one-shot` | coder → code-critic | Invocation-only (§ The one-shot lane). Well-specified, isolated phases; the phase file is the binding contract and the human's invocation substitutes for plan review. Kickoff Steps 3–4 are skipped. |

There is no **initial implementation** lane with zero review. The code critic runs on the initial implementation in every lane, including `one-shot`. The planner runs in both planner-bearing lanes, because a file-level plan is cheap and the coder needs it; `light` removes only the initial plan-review stage. In `one-shot`, the phase file itself must already carry what a plan would have supplied — which is exactly what its eligibility bar tests. Later test- or user-driven corrections follow the proportional routing rule below and do not automatically repeat the coder → critic cycle.

## Declaration

The lane is declared in the phase file's YAML frontmatter:

```yaml
review_lane: light
```

Absent, or `review_lane: full`, means the full lane. The field is set by whoever drafts the phase file — the bootstrap sketch, the JIT sub-phase decomposition (kickoff Step 1a), or the human — and the human may change it any time before the phase starts.

**`one-shot` is invocation-only.** Frontmatter may declare `full` or `light`, never `one-shot`: the frontmatter drafter can be an agent, and skipping the planner is a decision only the human's own hand may make. The lane activates solely through the `one-shot` token on the `kickoff` invocation line, which takes precedence over the phase file's declared lane for that cycle. The orchestrator never selects it. A frontmatter `review_lane: one-shot` is invalid — the orchestrator refuses it and asks.

The orchestrator:

- **Reports the lane** in the opening report and records it in the END block, so the human always sees which intensity a phase ran at.
- **May upgrade** a declared `light` to `full` when the phase's actual deliverables look non-mechanical, and may refuse a `one-shot` invocation into the phase file's declared lane when eligibility fails — noting the upgrade or refusal and why. Safety is asymmetric: an unnecessary full lane costs minutes; a wrongly light lane can cost a defect.
- **Never downgrades** on its own — not `full` to `light`, and never into `one-shot` at all. Skipping review is a human-visible declaration, not an orchestrator optimization; a human's `one-shot` invocation is such a declaration, which is why honoring it is not a downgrade.

## Eligibility for `light`

A phase qualifies only when **both** lists hold.

The work is mechanical — every deliverable is one of:

- documentation-only changes (briefs, policies, READMEs, catalogs, comments);
- renames, path moves, and the call-site updates they force;
- catalog/index/cross-reference updates;
- cross-harness mirror or parity refreshes;
- applying an already-classified batch of AUTO ripples;
- dependency bumps that pass the existing gates unchanged;
- configuration plumbing that follows an established in-repo pattern.

And **none** of the following appear anywhere in the phase:

- new or changed public API surface;
- schema, data-format, or persisted-state changes;
- concurrency, locking, or ordering logic;
- security-sensitive surface (auth, credentials, input parsing, sandboxing);
- a new architectural decision, however small it looks;
- user-visible behavior changes beyond wording.

When a phase is borderline, it is not eligible. `light` is an optimization, never a requirement.

## The one-shot lane

The one-shot lane runs a well-specified, isolated phase directly from its phase file: coder → orchestrator vet → code-critic → the normal acceptance close. It exists for work whose decisions are already made — by the phase file, or by a human-approved plan the phase file embodies — where the four-role loop's remaining value is the independent code review, which the lane keeps. It is the in-`kickoff` sibling of the doctrine's goal-armed one-shot ([`../briefs/methodology.md`](../briefs/methodology.md) § Orchestration runtime doctrine): the doctrine form runs a standalone task outside the phase loop; this lane runs a phase inside it.

**Eligibility** — checked by the orchestrator at kickoff Step 0; a failed check refuses the lane (with a stated reason) and runs the phase file's declared lane instead. This bar is deliberately *not* the `light` mechanical list — a one-shot may create new surface; its bar is specification quality and isolation:

- **Binding-spec bar.** The phase file names its deliverables concretely, carries empirical acceptance criteria, and states its verification steps. A phase file that would leave the coder inventing scope is not a spec.
- **Isolation.** The write surface is bounded and does not rewire existing authority surfaces mid-flight. New, self-contained machinery qualifies; cross-cutting edits to live contracts do not.

**Evidence.** The lane's mechanically derived initial role set is `role.implement` + `role.code-review` (no planner attempt, no `orchestration.planning` stage — `bin/kickoff-evidence` derives both from the lane). Everything else is unchanged: candidate binding, finding ledger, gate records, the complete final gate against the unchanged candidate.

### One-shot escalation

Four triggers end a one-shot attempt: a fail-closed park, a write-set widening, a second gate failure, or the critic's `Escalate: full lane` verdict. Escalation cannot continue inside the same evidence run — a late planning stage would violate stage-order validation — so the orchestrator finalizes the one-shot run truthfully (paused, with its stages closed as they actually ended), re-inits a fresh full-lane evidence run, and carries the open findings forward in the revision packet. The planner then produces the plan as-built, plan review runs against it, and the phase finishes in the full lane. The END block records `one-shot → full (escalated: <reason>)`.

## The evidence lane — a parallel axis

`review_lane` chooses which roles run; **`evidence_lane`** chooses how much candidate-bound evidence ceremony binds them. The axes are orthogonal, declared side by side in the phase file's frontmatter:

```yaml
review_lane: full      # which roles run
evidence_lane: light   # how much ceremony binds them; absent or `full` = full
```

| Lane | Apparatus | When |
|---|---|---|
| `full` (default) | The complete candidate-bound apparatus: role registration, span joins, stage envelopes, per-record candidate binding, review convergence metrics, the final gate ([`orchestration-evidence.md`](orchestration-evidence.md)). | Any phase touching an authority surface, irreversible or external state, or a deploy seam. When in doubt, this. |
| `light` | Structural tests, the human gate, and the seal at close. The run directory, authority manifest, finding ledger, and gate ledger remain the durable record; role registration, span joins, and stage envelopes become *validated-if-present, never required* — the lane is recorded in the immutable run metadata and the END block, never silently. **The seal at close is unchanged and mandatory:** `validate --require-final` still demands terminal findings and the final candidate-bound `./bin/check all` gate row with equal before/after/current candidates. | Presentation-scale phases and self-contained new machinery. |

**Eligibility for `light` — fail-closed triggers.** A phase is ineligible when any deliverable touches:

- **authority surfaces** — `policies/`, schemas, agent definitions, skills, the evidence/gate tooling, `CLAUDE.md`;
- **irreversible or external state** — deploys, cloud resources, data migrations, published URLs;
- **deploy seams** — anything a deploy pipeline consumes.

Borderline is ineligible, exactly as for review-lane `light`. Safety is asymmetric in the same direction: an unnecessary full apparatus costs minutes of ceremony; a wrongly light one can lose the evidence that would have caught a defect on a surface that mattered.

**Enforcement.** `bin/kickoff-evidence init` requires `--evidence-lane` and derives the run's requirements from both lanes; validation is lane-aware end to end. The orchestrator reads the declaration at kickoff Step 0, **may upgrade** `light` → `full` (never downgrades), refuses a `light` declaration whose deliverables hit a trigger, and reports the lane in the opening report and END block. **Plan review checks the declared lane against the plan's actual blast radius**: a `light` declaration over an authority, irreversible-state, or deploy surface is a blocking finding.

Motivating incident (cited per the doctrine's growth rule): in a donor project, a presentation-scale phase ran the complete apparatus and closed at twelve parks, roughly ten operator relays, and about forty-four hours — with much of that cost in ceremony the phase's blast radius never needed. The lane exists so the apparatus concentrates where authority, irreversibility, or deploy make it load-bearing.

## The critic guards the lane

In the light and one-shot lanes, the code critic receives the lane declaration along with its usual inputs, and gains one additional duty: **judge lane fit** — did the diff actually stay within the lane's scope (the mechanical list for `light`; the phase file's bounded write surface for `one-shot`)?

If it did not, the critic's verdict is `REVISE` and the first Required Change is:

```
Escalate: full lane — <one-line reason>
```

On escalation from `light`, the orchestrator runs the skipped plan review retroactively against the plan as-built (same venue rules as kickoff Step 4), routes its outcome through the normal revision loops, and the phase finishes in the full lane. The END block records `light → full (escalated: <reason>)`. Escalation from `one-shot` follows § One-shot escalation (there is no plan artifact to review retroactively — the planner runs late, in a fresh evidence run).

## Follow-up revisions are proportional

After the initial implementation has passed code review, a correction prompted by a build/test/acceptance failure or by concrete user feedback is a **follow-up revision**. Before changing code, the orchestrator classifies both its **risk** and its **size**. The initial phase lane does not force the follow-up route.

A full coder → critic cycle is required when **either** dimension is high:

- **High risk:** the correction touches a public API, schema or persisted state, concurrency or ordering, security-sensitive behavior, an architectural boundary, or ambiguous product behavior; weak or missing test coverage also makes the correction high risk.
- **Large or cross-cutting:** the correction spans multiple subsystems or user-visible surfaces, forces a broad call-site update, or produces a diff too large to inspect confidently as one focused change.

Risk tags are recorded in the candidate-bound change manifest governed by
[`orchestration-evidence.md`](orchestration-evidence.md). A revision that adds
a risk tag not present in the reviewed snapshot rebases to a complete review;
it is not eligible for a delta-only pass. Authority or scope drift, lost
review continuity, or indeterminate impact has the same fail-closed result.

When neither condition holds, use the least ceremony that safely completes the correction:

1. **Direct fix** — for a small, localized correction whose intended shape is already determined by a diagnostic or explicit user instruction. The orchestrator may edit the code itself.
2. **Coder only** — for a low-risk correction that benefits from implementation delegation but is not large or cross-cutting. Invoke `phase-coder`; do not invoke `code-critic` merely because a coder ran.
3. **Full cycle** — for any high-risk or large/cross-cutting correction. Invoke `phase-coder`, then `code-critic`, using the normal revision loop.

Validation is never proportionalized away. Every route reruns the failing
check first, then the focused tests and affected revision-close gates. After
code-critic approval, the orchestrator runs the complete acceptance-close
sequence and `./bin/check all` once against the unchanged candidate. If a
direct or coder-only correction grows beyond its classification, exposes an
architectural question, or lacks convincing validation, upgrade it immediately
to the full cycle.

The orchestrator reports the selected route, the risk/size reason, files changed, and validation evidence. This is a routing decision, not a new `review_lane:` value and not permission to skip the initial code review.

## Why this is capability-indexed

The stronger the coder model, the larger the fraction of mechanical phases whose initial reviews approve first-cycle with nothing to say — and the more the uniform four-role loop overpays. Lanes recover that cost at phase scale; proportional follow-up routing recovers it at correction scale. Work that makes decisions or carries significant blast radius still gets independent review. See also [`briefs/methodology.md`](../briefs/methodology.md) §6 on capability-indexed phase sizing — the same calibration, applied to bite size instead of review depth.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) — the roles, tool stances, verdict headers, and cycle caps are unchanged. `light` skips one initial *invocation* of `plan-reviewer`; `one-shot` skips the initial invocations of `phase-planner` and `plan-reviewer`; follow-up routing may omit role invocations without changing the roles themselves.
- [`role-models.md`](role-models.md) — lane and venue are orthogonal. In the light and one-shot lanes, the initial code critique (the only initial review that runs) still executes in the resolved venue — and venue diversity matters *more* there, since it is the sole independent check. The one-shot implementer resolves through the `coder` pin; there is no separate config role.
- [`phase-status.md`](phase-status.md) — `review_lane` and `evidence_lane` are phase properties, not statuses. They live in per-phase frontmatter; status still lives only in `plan/INDEX.md`.
- [`human-in-the-loop.md`](human-in-the-loop.md) — the human may request a concrete correction after a phase closes without reopening its historical status; new scope still requires a new phase.
