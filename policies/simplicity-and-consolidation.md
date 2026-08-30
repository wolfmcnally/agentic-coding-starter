# Policy: Simplicity and Consolidation

Build the least structure that satisfies the requirement in front of you, and give each piece of knowledge one home. These are the same rule read from two directions, and one question settles both: **how many concrete, present-tense uses can you name?**

When more than one design satisfies those rules, prefer the one that leaves the next reader fewer independent concepts and exceptions to understand. Simplicity limits structure; consolidation limits repetition; conceptual economy chooses among otherwise-valid designs.

The methodology names conceptual economy as a non-negotiable in [`briefs/methodology.md`](../briefs/methodology.md#non-negotiables); this policy defines the test.

| Named uses | What the rule requires |
|---|---|
| 0 or 1 | Keep the code concrete. Write a note, not a hook. |
| 2 | Judgment call. Either answer is defensible; say which you took and why. |
| 3 or more | One home. Every other site cites it. |

Zero-or-one is where over-engineering lives. Three-or-more is where duplication lives. The bar is one count, applied in both directions, and it is answerable before any code is written.

## Why this policy exists

Agents over-build and under-consolidate in the same pass, for the same reason: both shapes are common in the corpora they learned from. A provider interface with one implementation and a rule pasted into four files are both what mature code looks like from the outside, and neither requires understanding the problem to produce.

Both failures compound, in opposite ways.

Unused generality compounds forward, because **an agent reads structure as instruction.** A one-implementation interface invites the next session to add a second implementation. An unused `mode` parameter invites a second mode rather than the parameter's deletion. The speculative seam becomes the path of least resistance for more speculative code, and by the time a human asks what the second mode is for, the answer is nothing and the shape is load-bearing in the local convention.

Duplication compounds sideways, because **a rule binds only where it is written.** A rule copied into four agent definitions governs those four agents and nothing else — not the skills, not the operator, not a derived project's own roles, not you reading the repo outside an orchestrated phase. The copies also drift: each edit lands in one of them, and nothing detects the divergence, because four files that disagree are still four files.

This policy exists because the repo hit the second failure while trying to prevent the first. The rule "a new helper module is premature unless two existing call sites already need it" was stated four separate times — in `phase-planner`, `plan-reviewer`, `phase-coder`, and `code-critic` — and nowhere as law. Four copies, no authority. This file is that authority, and those four now cite it.

## Rule 1 — Name the second case

The bar for adding an **abstraction, interface, base class, parameter, hook, plugin slot, factory, strategy object, registry, mode flag, or configuration knob** is two concrete present-tense uses in this change, or a named second case carrying an owner, a date, or a concrete difference from the first.

These fail the bar: "another backend someday," "make it extensible," "production-ready," "for future flexibility," "we'll probably need this later."

These meet it: "the CSV and JSON exporters in this phase both call it," "Phase 4.2 adds the second venue and needs the same dispatch," "the audit-log service moves to a second store next quarter, and its error model differs."

**When you cannot name the second case, write the note rather than the hook.** Notes are cheap to delete; APIs are promises. The note belongs in the phase's Open Questions, a `lessons/` entry, or the brief that would own the decision — never in a parameter whose only job is remembering the idea.

Symptoms that the bar was skipped:

- A parameter every caller passes the same way.
- An interface with exactly one implementation and no scheduled second.
- A base class that exists so a future subclass can appear someday.
- Tests that exist only to exercise machinery production code never calls.
- Removing the generalized path makes the current feature easier to read, and breaks nothing except the tests written for the generality itself.

The removal is deliberately mundane: inline the unused path, collapse the hierarchy, delete the parameter, and delete the tests that only proved the machinery existed. Do it while the feature is fresh — the best time is before anything starts depending on the shape.

## Rule 2 — One home per piece of knowledge

When the same rule, constant, contract, procedure, or explanation reaches a **third** site, stop and give it one home; the other sites cite it. Two occurrences are a coincidence worth noting. Three are a structure worth building, and by then the count is also past Rule 1's bar — consolidation is not an exception to the simplicity rule, it is the same evidence pointing the other way.

Route the consolidated home by kind, per the *Rules, not memory* invariant in `CLAUDE.md`: a universal rule to `policies/` or `CLAUDE.md`, a scoped detail to the surface's own instruction file, a per-action workflow to the owning skill, a tunable to the policy holding its tunables, a pinned decision to a brief.

This binds prose exactly as it binds code. In this repo the rule surfaces **are** the deliverable, so a policy restated across three skills is the same defect as a constant hard-coded in three modules, and it is corrected the same way. The mirror-vs-copy contract in [`cross-harness-parity.md`](cross-harness-parity.md) is Rule 2 applied to one specific surface; this is the general form.

A citation is a real pointer to a named file and section, not a paraphrase that happens to agree. A paraphrase is a fourth copy wearing a citation's clothes, and it drifts like any other copy.

## Rule 3 — Prefer conceptual economy

Among designs that fully satisfy the brief, policies, acceptance criteria, performance needs, and operational constraints, prefer the one that leaves the next reader fewer independent concepts, states, branches, representations, authorities, and exceptional rules to understand. This is conceptual economy.

Do not measure it by lines of code, file count, or abstraction count. Those proxies can invert the result: compressed code may hide complexity, while one well-chosen abstraction may eliminate several concepts. Count what the reader must understand, not what the repository happens to contain.

A new concept earns its place when it represents a real distinction in the problem or removes more accidental complexity than it introduces. One behavior should have one obvious path, one piece of state should have one authority, and the common case should not travel through machinery built only for hypothetical variation.

When two designs are materially equivalent in correctness and capability, choose the one expressible with fewer rules and exceptions. If the more elaborate design wins, name the concrete requirement that makes the simpler design insufficient.

A conceptual-economy finding must be comparative. Name the unnecessary concept or exception, describe a simpler in-scope design, and show that the alternative preserves the applicable requirements and invariants. “This feels over-engineered” and “this is inelegant” are not findings.

## What this policy does not license

**It is not anti-design.** Public APIs, on-disk data formats, migration paths, and security boundaries are expensive to change after release, and treating them as requirements rather than guesses is correct. The difference is evidence: write the constraint down, name who depends on it, and test the compatibility promise. The antipattern begins when the only evidence is anxiety about a future nobody has committed to.

**It is not a license to under-build.** A change implemented as a special case layered onto shared infrastructure is a signal that the fix is at the wrong depth, not that it is admirably small. When the honest correction is to generalize the underlying mechanism, generalizing it *is* the least structure that satisfies the requirement — and the special case is the speculative option, because it commits the next reader to a branch that should not exist. Rule 1 asks for the smallest shape that solves the real problem, not the smallest diff.

**It is not a mandate to refactor outside the phase.** Duplication you notice in code the phase does not touch is a tangent: record it once and defer it, per the *Monotonic progress* invariant. The third occurrence forces consolidation when your change is what creates it.

**It does not relax [`greenfield-until-released.md`](greenfield-until-released.md).** Replacing a wrong shape directly is not "adding structure," and keeping a compat path is not "avoiding an abstraction."

## Verification

This policy is deliberately enforced by review rather than by script. Its load-bearing symptoms — a parameter every caller passes identically, an abstraction whose second case was never named, a third copy of a rule that reads differently from the first two — are judgments about intent and evidence, not string matches, and per [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md) that routes them to intelligence. A grep here would report the shapes it can see and stay silent on every instance that matters, which is the vacuous-green failure [`acceptance-empirical.md`](acceptance-empirical.md) rejects.

The enforcement points are therefore:

- The **planner** does not plan structure whose second case it cannot name and, among phase-compliant designs, chooses the one with fewer independent concepts and exceptions unless a concrete requirement defeats it.
- The **plan reviewer** blocks unrequested structure and accidental complexity only with a simpler in-scope alternative that preserves the requirements and invariants.
- The **coder** honors the second-case bar while writing, then takes both the removal pass and the indirection pass before reporting.
- The **code critic** blocks on speculative structure, third copies, or accidental complexity, naming both the concrete comprehension cost and the smaller equivalent design.

One mechanical check does apply, because it is exact: `bin/check-catalogs` enforces that a policy has one cataloged home and that every citation of it resolves. That guards Rule 2's *pointer* discipline, not its judgment.
