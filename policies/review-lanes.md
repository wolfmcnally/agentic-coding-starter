# Policy: Review Lanes and Proportional Follow-ups

Review intensity follows authorized scope and risk. Approved methodology improvements use direct implementation below; other phase work defaults to the four-role loop ([four-canonical-agents.md](four-canonical-agents.md)), with an explicit light lane for mechanical phases. First-cycle approval records that review’s outcome, not proof of wasted effort, model capability or permission to skip future review. Both full close gates remain unchanged.

## Methodology improvements: direct implementation by default

Operator-ratified 2026-09-05. After the operator approves the intended methodology change, the invoking agent implements the complete coherent change directly, then obtains one independent review of the complete change and runs the required checks. Do not create phases, delegate planning or implementation, or repeat plan review merely because the work improves methodology. This applies in the starter template as well as derived projects, including methodology instructions, policies, skills, role definitions, orchestration code and their tests. Product work remains governed by the project's phase workflow; labeling a product change “methodology” does not change its route.

This is a default outside `kickoff`, not its invocation-only `one-shot` lane or a new lane value. Explicit operator requests for `kickoff`, phase roles or a different review process override it for their named scope. An already approved improvement plan supplies scope; unresolved consequential decisions still go to the operator. File count, authority edits and the fact that methodology is this template's product do not themselves require the four-role loop. The observed failure was repeated planning and authority recapture while changing the workflow's own instructions; approval of improvements must not silently become approval of that overhead.

Independent review uses a separate context and examines the complete implementation against the approved outcome and applicable rules. The invoking agent runs focused checks first, addresses all required findings directly and obtains review of those corrections as needed. “One independent review” means one initial comprehensive pass, not permission to ship unresolved findings or forbid necessary verification of a fix. Reopen planning only for a consequential scope or design decision; do not regenerate an unchanged plan to carry a correction.

Preserve both full gates: after independent approval, run the required implementation-candidate sequence ending in `./bin/check all`; after all log, status, lesson and report writes, run the second bare `./bin/check all`, with no tracked write afterward. Record the approved scope, actual changed paths, independent verdict and resolutions, exact reviewed candidate, gate commands/results and remaining human criteria. Existing hard rules, delivery authority, test governance and human acceptance remain binding. Do not fabricate phase-role attempts, command receipts or an accepted `kickoff` run for direct work. When changing routes during an existing run, close that run truthfully, preserve its artifacts and completed work, and verify the complete resulting change under the newly approved route.

Kickoff locations: [preflight](../.claude/skills/kickoff/preflight.md) owns Steps 0–2 and lane selection; [planning](../.claude/skills/kickoff/planning.md) owns Steps 3–4; [implementation](../.claude/skills/kickoff/implementation.md) owns Steps 5–6; [recovery](../.claude/skills/kickoff/recovery.md) owns follow-ups and escalation; [acceptance](../.claude/skills/kickoff/acceptance.md) and [close](../.claude/skills/kickoff/close.md) retain the two-gate close. Read each resource before its branch.

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

The one-shot lane runs a well-specified, isolated phase directly from its phase file: coder → orchestrator vet → code-critic → the normal two-gate close. It exists for work whose decisions are already made — by the phase file, or by a human-approved plan the phase file embodies — where the four-role loop's remaining value is the independent code review, which the lane keeps. It is the in-`kickoff` sibling of the doctrine's goal-armed one-shot ([`../briefs/methodology.md`](../briefs/methodology.md) § Orchestration runtime doctrine): the doctrine form runs a standalone task outside the phase loop; this lane runs a phase inside it.

**Eligibility** — checked by the orchestrator at kickoff Step 0; a failed check refuses the lane (with a stated reason) and runs the phase file's declared lane instead. This bar is deliberately *not* the `light` mechanical list — a one-shot may create new surface; its bar is specification quality and isolation:

- **Binding-spec bar.** The phase file names its deliverables concretely, carries empirical acceptance criteria, and states its verification steps. A phase file that would leave the coder inventing scope is not a spec.
- **Isolation.** The write surface is bounded and does not rewire existing authority surfaces mid-flight. New, self-contained machinery qualifies; cross-cutting edits to live contracts do not.

**Evidence.** The lane's mechanically derived initial role set is `role.implement` + `role.code-review` (no planner attempt, no `orchestration.planning` stage — `bin/kickoff-evidence` derives both from the lane). Everything else is unchanged: candidate binding, finding ledger, implementation-gate records, and the post-bookkeeping handoff gate.

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
| `full` (default) | The complete candidate-bound apparatus: role registration, span joins, stage envelopes, per-record candidate binding, review convergence metrics, and the implementation gate ([`orchestration-evidence.md`](orchestration-evidence.md)); the handoff gate follows tracked close writes. | Any phase touching an authority surface, irreversible or external state, or a deploy seam. When in doubt, this. |
| `light` | Structural tests, the human gate, and the seal at close. The run directory, authority manifest, finding ledger, and gate ledger remain the durable record; role registration, span joins, and stage envelopes become *validated-if-present, never required* — the lane is recorded in the immutable run metadata and the END block, never silently. **The implementation seal is unchanged and mandatory:** `validate --level acceptance` still demands terminal findings and the final candidate-bound `./bin/check all` gate row with unchanged full-tree identity during the gate and a current matching product candidate. The bare handoff gate is also unchanged. | Presentation-scale phases and self-contained new machinery. |

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

Risk tags are recorded in the candidate-bound change manifest governed by [`orchestration-evidence.md`](orchestration-evidence.md). A revision that adds a risk tag not present in the reviewed snapshot rebases to a complete review; it is not eligible for a delta-only pass. Authority or scope drift, lost review continuity, or indeterminate impact has the same fail-closed result.

When neither condition holds, use the least ceremony that safely completes the correction:

1. **Direct fix** — for a small, localized correction whose intended shape is already determined by a diagnostic or explicit user instruction. The orchestrator may edit the code itself.
2. **Coder only** — for a low-risk correction that benefits from implementation delegation but is not large or cross-cutting. Invoke `phase-coder`; do not invoke `code-critic` merely because a coder ran.
3. **Full cycle** — for any high-risk or large/cross-cutting correction. Invoke `phase-coder`, then `code-critic`, using the normal revision loop.

Validation is never proportionalized away. Every route reruns the failing check first, then the focused tests and affected revision-close gates. After code-critic approval, the orchestrator runs the complete implementation-candidate sequence against the unchanged candidate, then the bare handoff gate after tracked close writes. If a direct or coder-only correction grows beyond its classification, exposes an architectural question, or lacks convincing validation, upgrade it immediately to the full cycle.

The orchestrator reports the selected route, the risk/size reason, files changed, and validation evidence. This is a routing decision, not a new `review_lane:` value and not permission to skip the initial code review.

## Scope and risk determine the lane

Lane eligibility and follow-up classification use the work’s actual decisions, boundaries and affected behavior. They do not follow model reputation or a count of first-cycle approvals. A coherent phase may span multiple surfaces while still requiring full independent review; smaller phases do not waive either full gate. Outcome-based phase sizing is described in [methodology](../briefs/methodology.md) §6.

## Containment-claim review checklist

Whenever the work under review asserts an **isolation, containment, or firewall property** — a sweep can't reach X, a lane is self-contained, a surface is withheld — the critic reads the claim against this five-entry catalogue and, for each claim, asks which entry it is most likely to be. Every entry was observed surviving at least one real review in the donor project before being caught; several arrived through locally-correct work. (Graduated there from a three-occurrence lesson, owner-ratified 2026-08-17.)

1. **A fix aimed at availability silently spends isolation.** The fix's success criterion (it runs) and the property's (it contains) are different criteria — check both are being watched.
2. **It holds at the level it was checked.** The assertion tests the mechanism the author was thinking about, not the path the runtime takes (an env var asserted absent while a symlink reaches the same store). The repo's own policy prose is a review input here.
3. **It holds at the scale it was checked.** Controls that pass only at fixture size; wall time is a first-class gate result — a pass count over unbounded runtime is a verification that can only say "good."
4. **It holds at the top level and fails one level down.** State containment transitively (*no path reachable from the lane resolves outside it*) — that phrasing admits a test; "the directory is lane-owned" does not.
5. **A reordering turns a real control vacuous.** A control that names a guard must match *that guard's refusal*, not any refusal — `pytest.raises(SomeError)` without a message predicate is a control waiting to be reassigned by a correct refactor.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) — the roles, tool stances, verdict headers, and cycle caps are unchanged. `light` skips one initial *invocation* of `plan-reviewer`; `one-shot` skips the initial invocations of `phase-planner` and `plan-reviewer`; follow-up routing may omit role invocations without changing the roles themselves.
- [`role-models.md`](role-models.md) — lane and venue are orthogonal. In the light and one-shot lanes, the initial code critique (the only initial review that runs) still executes in the resolved venue with a separate review context. Cross-vendor selection is explicit; its incremental value is not presumed from the lane. The one-shot implementer resolves through the `coder` pin; there is no separate config role.
- [`phase-status.md`](phase-status.md) — `review_lane` and `evidence_lane` are phase properties, not statuses. They live in per-phase frontmatter; status still lives only in `plan/INDEX.md`.
- [`human-in-the-loop.md`](human-in-the-loop.md) — the human may request a concrete correction after a phase closes without reopening its historical status; new scope still requires a new phase.
