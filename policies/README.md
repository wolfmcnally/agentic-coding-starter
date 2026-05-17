# `policies/` — Non-Negotiable Rules

This directory holds the rules every phase of work in this repo honors. A policy is **short, prescriptive, and load-bearing.** When code and a policy disagree, the policy wins. When agents and a policy disagree, the policy wins.

## How a policy differs from a brief

- A **brief** describes *what* and *why*. It is a durable design decision with context. Lives under `briefs/`.
- A **policy** prescribes *how to behave* or *what to never do*. It is a rule. Lives under `policies/`.
- A **phase file** specifies *in what order* and *with what acceptance*. Lives under `plan/`.

The full contract is in [`briefs-and-policies.md`](briefs-and-policies.md).

## When to add a policy

Add a new policy when:

- The same rule keeps getting re-explained across phases.
- A class of failures recurs that a clear rule would prevent.
- A cross-cutting invariant (touching multiple surfaces or multiple phases) needs one canonical statement instead of being duplicated.

Don't add a policy for:

- A one-off decision that belongs in a brief or a phase file.
- An ephemeral preference. Policies are durable.
- Something a code linter or formatter already enforces mechanically.

## How agents use this directory

- The planner reads the policies that touch the phase's surfaces before drafting a plan.
- The plan reviewer treats every policy as a blocking criterion: any plan that violates a policy is `REVISE`.
- The coder honors every policy while writing code.
- The code critic treats every policy as a blocking criterion: any code that violates a policy is `REVISE`.

## Catalog

The catalog of policies in this repo is in [`../CLAUDE.md`](../CLAUDE.md) under "Policies catalog." Keep that catalog and the files in this directory in sync — no orphans either way.

## Authority

Policies in this directory override:

- Briefs, when the policy and the brief disagree on a behavior. (Briefs document decisions; policies are the rules those decisions must respect.)
- Plan files, when a plan proposes work that violates a policy. The plan must change, not the policy.

Policies are themselves subordinate to:

- The methodology in [`../briefs/methodology.md`](../briefs/methodology.md), which is foundational.
- A direct instruction from the human, given in the current session, that explicitly overrides the policy for a clearly-scoped reason. (The human owns the repo; the agents serve the human's intent. But the override is one-shot — the policy survives unless the human asks for it to be amended.)
