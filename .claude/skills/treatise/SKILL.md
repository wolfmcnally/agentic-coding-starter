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

Identify the topic, audience, intended venue, and requested format. Infer only
when the repository makes the answer unambiguous; otherwise ask for the single
decision that materially changes the artifact.

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

## 7. Deliver the repository artifact

The repaired brief and any tracked rendering are ordinary repository work: once
`./bin/check all` passes against the unchanged tree, commit them by explicit
path and non-force-push to one unambiguous configured upstream
([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)).
Untracked renderings stay in the session scratchpad and are never committed.

**Committing is not publishing.** Section 6 governs anything that leaves the
repository, and no green gate opens it. Park delivery and report on an
unexpected path, an unresolved gate, a missing or ambiguous upstream, or a
divergence.
