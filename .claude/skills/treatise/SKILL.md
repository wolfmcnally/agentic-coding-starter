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

**Read the sidecar first.** Every treatise carries `<brief-name>.yaml` beside its
canonical brief, holding the scope, audience, register, and the operator's
standing editorial rulings (section 7). When it exists, it is binding: a later
pass may not quietly reverse a recorded ruling, and a request that conflicts with
one is a decision to surface, not to resolve silently. When it does not exist,
this pass creates it.

Then identify the topic, audience, intended venue, and requested format. Infer
only when the sidecar or the repository makes the answer unambiguous; otherwise
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

## 7. Maintain the sidecar

`<brief-name>.yaml`, beside the canonical brief, is where a treatise's intent
lives between passes. Prose carries the argument; the sidecar carries the
instructions that shaped it, which the prose cannot state about itself. Without
it, each revision re-derives the audience and register from the draft in front of
it, and the piece drifts from what the operator asked for.

Write or update it in the same pass that changes the treatise, before delivery.
Fields:

- `treatise`, `title`, `brief`, `updated` — identity and the canonical path.
- `purpose` — one or two sentences on what this treatise is for.
- `audience` — who it is written for, the range it must serve, what knowledge it
  may assume, and who it is explicitly not for.
- `register` — the form (primer, essay, white paper) and the voice constraints
  in force, including any skill the operator asked to run over it.
- `scope` — what belongs in the piece and what stays out.
- `directives` — **append-only.** One dated entry per editorial ruling the
  operator gives, in their own words where possible, with what changed in
  response. Never edit or delete a past entry; a reversal is a new entry that
  names the one it supersedes.
- `renderings` — each published format and its location.
- `external_facts` — every claim not sourced from this repository, with its
  source and retrieval date, so a later pass can re-check rather than re-trust.
- `open_questions` — anything the operator has not yet decided.

Record a ruling the moment it is given, in the pass that acts on it. A directive
reconstructed later from memory is the failure this file exists to prevent.

## 8. Deliver the repository artifact

The repaired brief, its sidecar, and any tracked rendering are ordinary repository work: once
`./bin/check all` passes against the unchanged tree, commit them by explicit
path and non-force-push to one unambiguous configured upstream
([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)).
Untracked renderings stay in the session scratchpad and are never committed.

**Committing is not publishing.** Section 6 governs anything that leaves the
repository, and no green gate opens it. Park delivery and report on an
unexpected path, an unresolved gate, a missing or ambiguous upstream, or a
divergence.
