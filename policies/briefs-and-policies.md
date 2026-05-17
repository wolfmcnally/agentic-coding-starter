# Policy: Briefs, Policies, and the Plan

The three top-level documentation directories in this repo (`briefs/`, `policies/`, `plan/`) look similar at a glance. The distinction is load-bearing — confusing them produces drift between intent, rule, and execution.

## The three directories

- **`briefs/`** — durable *descriptions*. What you're building, why, how, what was decided, what was rejected. A brief is a piece of design memory.
- **`policies/`** — durable *prescriptions*. What every phase must do, must never do, or must produce. A policy is a rule.
- **`plan/`** — sequenced *intent*. Which phases happen in which order, what each phase delivers, what acceptance criteria it must satisfy. A phase file is a unit of work.

## The contract

1. **Briefs inform.** Plan files and policies cite briefs. Briefs do not cite plan files or policies (since they predate them in the project's lifecycle).
2. **Policies bind.** Every phase honors every policy that applies to its surfaces. A policy violation blocks acceptance, full stop.
3. **The plan sequences.** Phase files specify *how* to realize the briefs' designs and *when* in the project's life that work happens.
4. **When a policy and a brief conflict, the policy wins.** Briefs document past decisions; policies are the present-day rules those decisions must respect. Update the brief to acknowledge the constraint, or update the policy if it has become wrong.
5. **When a plan and a brief conflict, the plan wins.** The plan is the refinement — it knows what the brief did not when the brief was written. Update the brief to record the refinement.

## How to tell which directory something belongs in

Ask three questions:

- *Will future phases need this as context?* → `briefs/`
- *Will every future phase need to obey this?* → `policies/`
- *Does this describe a specific unit of work?* → `plan/`

If the answer is "all three," the content is in three different shapes and probably belongs in all three: a brief that describes the underlying decision, a policy that prescribes the resulting rule, and a phase that does the work.

## Common drift modes

- **Policy disguised as brief.** A brief that contains imperative sentences like "every phase must…" is actually a policy. Move the rule to `policies/`; keep the design discussion in the brief.
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
- Briefs inform every phase that cites them.
- The plan sequences the work.

When the human explicitly overrides a policy in-session for a clearly-scoped reason, the override is one-shot. Update the policy if the override should be permanent.
