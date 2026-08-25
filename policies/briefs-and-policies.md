# Policy: Briefs, Policies, and the Plan

The three top-level documentation directories in this repo (`briefs/`, `policies/`, `plan/`) look similar at a glance. The distinction is load-bearing — confusing them produces drift between intent, rule, and execution.

This policy covers the contract *between* the three directories. The brief-file lifecycle within `briefs/` itself (frontmatter schema, `draft` / `methodology` / `implemented` / `historical` status flow, when to write one, when to retire one) is governed by the companion policy [`briefs.md`](briefs.md).

## The three directories

- **`briefs/`** — durable *thinking*. What you intended to build as of some date, research into whatever questions the work raised, positions taken, options weighed. **A brief is not a decision record.** Much of what a brief contains is never pinned down, and a brief that turns out to be wrong is marked `historical` rather than treated as a broken promise.
- **`policies/`** — durable *decisions*. What every phase must do, must never do, or must produce. A policy is a rule, and `policies/` is where this project records what it actually settled on.
- **`plan/`** — sequenced *intent*. Which phases happen in which order, what each phase delivers, what acceptance criteria it must satisfy. A phase file is a unit of work.

## The contract

1. **Briefs inform, and the citation runs one way only.** A policy or a plan file may cite a brief as supporting material, because a decision should be able to show the thinking behind it. **A brief never cites a policy or a plan file.** The thinking predates the rule derived from it; a brief that cites a policy inverts that order, and afterward neither document can be read on its own. When a brief needs to mention a constraint, it states the constraint in its own words rather than pointing at the file that binds it.
2. **Policies bind.** Every phase honors every policy that applies to its surfaces. A policy violation blocks acceptance, full stop.
3. **The plan sequences.** Phase files specify *how* to realize the briefs' designs and *when* in the project's life that work happens.
4. **When a policy and a brief conflict, the policy wins.** A brief records thinking that was current when it was written; a policy is what the project decided. Rewrite the brief if its thinking has been superseded, mark it `historical` if it has been abandoned, or change the policy if the decision itself was wrong.
5. **When a plan and a brief conflict, the plan wins.** The plan is the refinement — it knows what the brief did not when the brief was written. Update the brief to record the refinement.

## How to tell which directory something belongs in

Ask three questions:

- *Will future phases need this as context?* → `briefs/`
- *Will every future phase need to obey this?* → `policies/`
- *Does this describe a specific unit of work?* → `plan/`

If the answer is "all three," the content is in three different shapes and probably belongs in all three: a brief that works through the reasoning, a policy that prescribes the rule the reasoning produced, and a phase that does the work.

## Common drift modes

- **Policy disguised as brief.** A brief that contains imperative sentences like "every phase must…" is actually a policy. Move the rule to `policies/`; keep the thinking in the brief.
- **Brief citing downward.** A brief that links to a policy or a phase file has inverted the citation direction (contract item 1). State the constraint in the brief's own words, and let the policy carry the link back.
- **Plan disguised as policy.** A policy that names specific files or phases is actually a phase file. Move the work to `plan/`; if there's a general rule behind the specific work, abstract it into a real policy.
- **Brief disguised as plan.** A phase file that documents *why* a decision was made rather than *how* to execute it should split: extract the why into a brief, leave the how in the phase.

## Catalogs

`CLAUDE.md` carries:

- **Briefs catalog** — every file in `briefs/`.
- **Policies catalog** — every file in `policies/`.

Both catalogs must list every file in their respective directories, and every file in those directories must be in its catalog. Orphans on either side cause agents to read past content or miss it entirely.

## Authority

Within this repo:

- Methodology (in `briefs/methodology.md`) is foundational and shapes everything downstream.
- Policies bind every phase.
- Briefs inform every phase and policy that cites them, and cite neither in return.
- The plan sequences the work.

When the human explicitly overrides a policy in-session for a clearly-scoped reason, the override is one-shot. Update the policy if the override should be permanent.
