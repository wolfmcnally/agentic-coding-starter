# Policy: Review Lanes — Risk-Adaptive Review Intensity

Every phase pays for the review it needs, not the review some other phase needed. The four-role loop ([`four-canonical-agents.md`](four-canonical-agents.md)) is the default and the right shape for any phase that makes decisions; for purely mechanical phases, a first-cycle `APPROVED` with zero findings is review that found nothing — pure cost. This policy lets a phase declare that up front, with the code critic as the backstop.

## The two lanes

| Lane | Pipeline | When |
|---|---|---|
| `full` (default) | planner → plan-reviewer → coder → code-critic | Any phase that decides anything. When in doubt, this. |
| `light` | planner → coder → code-critic | Mechanical phases only (eligibility below). Plan review (kickoff Step 4) is skipped. |

There is no lane with zero review. The **code critic runs in every lane** — that is non-negotiable. The planner also runs in every lane: a file-level plan is cheap and the coder needs it; `light` removes only the plan-review stage.

## Declaration

The lane is declared in the phase file's YAML frontmatter:

```yaml
review_lane: light
```

Absent, or `review_lane: full`, means the full lane. The field is set by whoever drafts the phase file — the bootstrap sketch, the JIT sub-phase decomposition (kickoff Step 1a), or the human — and the human may change it any time before the phase starts.

The orchestrator:

- **Reports the lane** in the opening report and records it in the END block, so the human always sees which intensity a phase ran at.
- **May upgrade** a declared `light` to `full` when the phase's actual deliverables look non-mechanical — noting the upgrade and why. Safety is asymmetric: an unnecessary full lane costs minutes; a wrongly light lane can cost a defect.
- **Never downgrades** `full` to `light` on its own. Skipping review is a human-visible declaration, not an orchestrator optimization.

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

## The critic guards the lane

In the light lane, the code critic receives the lane declaration along with its usual inputs, and gains one additional duty: **judge lane fit** — did the diff actually stay within the mechanical scope above?

If it did not, the critic's verdict is `REVISE` and the first Required Change is:

```
Escalate: full lane — <one-line reason>
```

On escalation, the orchestrator runs the skipped plan review retroactively against the plan as-built (same venue rules as kickoff Step 4), routes its outcome through the normal revision loops, and the phase finishes in the full lane. The END block records `light → full (escalated: <reason>)`.

## Why this is capability-indexed

The stronger the coder model, the larger the fraction of mechanical phases whose reviews approve first-cycle with nothing to say — and the more the uniform four-role loop overpays. Lanes recover that cost exactly where risk is low, while the phases that benefit from review — the ones making decisions — keep the full loop. As coder capability grows, expect more phases to qualify for `light`, not weaker review on the phases that stay `full`. See also [`briefs/methodology.md`](../briefs/methodology.md) §6 on capability-indexed phase sizing — the same calibration, applied to bite size instead of review depth.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) — the roles, tool stances, verdict headers, and cycle caps are unchanged. `light` skips one *invocation* of `plan-reviewer`; it changes nothing about the role.
- [`cross-harness-review.md`](cross-harness-review.md) — lane and venue are orthogonal. In the light lane, the code critique (the only review that runs) still executes in the resolved venue — and venue diversity matters *more* there, since it is the sole independent check.
- [`phase-status.md`](phase-status.md) — `review_lane` is a phase property, not a status. It lives in per-phase frontmatter; status still lives only in `plan/INDEX.md`.
- [`human-in-the-loop.md`](human-in-the-loop.md) — unchanged. The lane is named in the opening report and END block precisely so the human can veto a `light` declaration before or after the fact.
