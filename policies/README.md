# `policies/` — Non-Negotiable Rules

This directory holds the rules every phase of work in this repo honors. A policy is **short, prescriptive, and load-bearing.** When code and a policy disagree, the policy wins. When agents and a policy disagree, the policy wins.

## How a policy differs from a brief

- A **brief** describes *what* and *why*. It is a durable design decision with context. Lives under `briefs/`.
- A **policy** prescribes *how to behave* or *what to never do*. It is a rule. Lives under `policies/`.
- A **phase file** specifies *in what order* and *with what acceptance*. Lives under `plan/`.
- A **pinned document** is third-party text the project depends on, kept verbatim. It is none of the above and is cited by all of them. Lives under `docs/` ([`docs.md`](docs.md)).

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
- Research, surveys, or methodology investigations. Those are briefs — a brief *informs* a policy; the policy is the rule extracted from it.
- Logs of what happened. Those are commits and `LOG.md`.
- Active execution queues. Live queues are directories at the repo root (`user-actions/`, `lessons/`), not policy bodies. A policy may *govern* a queue's format and lifecycle; the queue itself does not live under `policies/`.
- Identity / framing material that every agent needs every turn. That stays in `CLAUDE.md`.

## How a policy evolves

- **Add** a policy when a rule starts being cited or implicitly assumed in more than one place. Don't pre-write speculative policies.
- **Revise** in place when the rule changes; bump no version metadata, just edit. Git is the audit trail.
- **Supersede** by replacing the file's contents and noting the prior shape inline if the prior shape will be referenced. Don't keep dead policies around just for history.
- **Cite the brief** that motivated the policy when the brief's argument is the load-bearing justification. The policy is the rule; the brief is why.

## How agents use this directory

- The planner reads the policies that touch the phase's surfaces before drafting a plan.
- The plan reviewer treats every policy as a blocking criterion: any plan that violates a policy is `REVISE`.
- The coder honors every policy while writing code.
- The code critic treats every policy as a blocking criterion: any code that violates a policy is `REVISE`.

## Catalog

The catalog of policies in this repo is in [`../CLAUDE.md`](../CLAUDE.md) under "Policies catalog." Keep that catalog and the files in this directory in sync — no orphans either way.

## Authority and precedence

When two rules conflict:

1. The human's global instructions override everything in this repo.
2. The repo's `CLAUDE.md` (Hard rules and architectural invariants) overrides individual policy files.
3. Policy files override briefs (briefs inform, policies bind) and plan files (a plan that proposes work violating a policy must change — the plan, not the policy).
4. `plan/` files override briefs (the plan is the refinement — it knows what the brief did not; update the brief to record the refinement).
5. A more-specific policy overrides a more-general one.

If an apparent conflict can't be resolved by precedence, surface it. Don't paper it over.

Policies are themselves subordinate to:

- The methodology in [`../briefs/methodology.md`](../briefs/methodology.md), which is foundational.
- A direct instruction from the human, given in the current session, that explicitly overrides the policy for a clearly-scoped reason. (The human owns the repo; the agents serve the human's intent. But the override is one-shot — the policy survives unless the human asks for it to be amended.)
