---
name: treatise
description: >-
  Produce an audience-specific outward explanation of a repository's principles
  and decisions from live briefs, policies, plans, and code evidence. Writes or
  repairs the canonical brief first, then renders requested formats. Use when a
  user asks for a treatise, white paper, architecture explainer, or durable
  public-facing account of why a project works the way it does.
argument-hint: "<topic> [for <audience>] [as <format>]"
last-reviewed: 2026-08-23
---

# Treatise — Explain a repository outward

Read [`policies/treatise.md`](../../../policies/treatise.md) in full before
classifying or writing the artifact.

## 1. Resolve the request

**Read the editorial record first.** A treatise is a brief whose frontmatter
carries a `treatise:` mapping holding the purpose, audience, register, coverage,
and the operator's standing rulings (section 7). When it exists, it is binding:
a later pass may not quietly reverse a recorded ruling, and a request that
conflicts with one is a decision to surface, not to resolve silently. When it
does not exist, this pass creates it.

Then identify the topic, audience, intended venue, and requested format. Infer
only when the record or the repository makes the answer unambiguous; otherwise
ask for the single decision that materially changes the artifact.

## 2. Build a claim map

Read the owning briefs and policies first, then the relevant plan and code
evidence. For every material claim, record its canonical authority and any
verification evidence. Research externally only within
[`policies/research-authority.md`](../../../policies/research-authority.md), and
date volatile facts.

## 3. Repair authority first

If the repository has no canonical explanation, create or revise the smallest
owning brief before producing a derivative. Keep project principles and pinned
decisions in the brief; keep non-negotiable behavior in policy.

## 4. Draft for the audience

Lead with the thesis. Explain principles, consequential decisions, tradeoffs,
limits, and verification. Use file paths as evidence rather than organizing the
piece as a file inventory. Elide protected information while composing.

## 5. Render and verify

Use the appropriate document, presentation, site, or other artifact workflow
when the requested format requires it. Verify layout as well as content, and
confirm every claim still maps to its authority after rendering.

## 6. Publication gate

An internal canonical brief may be written under ordinary repository authority.
Do not publish externally without explicit user authority and a governing
disclosure or release policy for the receiving venue. When either is absent,
deliver the internal artifact and name the blocked publication action.

## 7. Maintain the editorial record

The `treatise:` block in the brief's own frontmatter is where a treatise's intent
lives between passes. Prose carries the argument; the block carries the
instructions that shaped it, which the prose cannot state about itself. Without
it, each revision re-derives the audience and register from the draft in front of
it, and the piece drifts from what the operator asked for.

It lives in the frontmatter rather than a sidecar file so it cannot be renamed,
orphaned, or forgotten apart from the document it describes, and so its presence
is itself the marker that the brief is a treatise. Markdown renderers hide
frontmatter, so the record costs the reader nothing.

Write or update it in the same pass that changes the treatise, before delivery.
Keys under `treatise:`:

- `updated` — ISO date of this pass.
- `purpose` — one or two sentences on what this treatise is for.
- `audience` — `primary` and `range` are required; add `may_assume`,
  `must_not_assume`, and `not_written_for` when they carry a real constraint.
- `register` — the `form` (primer, essay, white paper), the flow, any voice
  skills standing over the piece, and the constraints in force.
- `coverage` — `includes` and `excludes`: what belongs in the piece and what
  stays out.
- `directives` — the provenance log. One dated entry per editorial ruling the
  operator gives, quoting their words where possible, with a one-line `effect`
  naming what changed. Record a reversal as a new entry naming the one it
  supersedes; removing a past entry is a deliberate act rather than a tidy-up,
  and version history holds every earlier state of the log either way.
- `renderings` — each published format, where it lives, and when.
- `external_facts` — every claim not sourced from this repository, with its
  source and retrieval date, so a later pass can re-check rather than re-trust.
  Note volatility where a figure is known to move.
- `open_questions` — anything the operator has not yet decided.

Record a ruling the moment it is given, in the pass that acts on it. A directive
reconstructed later from memory is the failure this record exists to prevent.

Run `./bin/treatise validate` before delivery. It enforces the schema, the
required fields, and the ISO dates, and it runs again inside `./bin/check all`.

## 8. Deliver the repository artifact

The repaired brief, its editorial record, and any tracked rendering are ordinary repository work: once
`./bin/check all` passes against the unchanged tree, commit them by explicit
path and non-force-push to one unambiguous configured upstream
([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)).
Untracked renderings stay in the session scratchpad and are never committed.

**Committing is not publishing.** Section 6 governs anything that leaves the
repository, and no green gate opens it. Park delivery and report on an
unexpected path, an unresolved gate, a missing or ambiguous upstream, or a
divergence.
