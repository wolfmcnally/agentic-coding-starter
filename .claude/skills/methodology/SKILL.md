---
name: methodology
description: >-
  The eleven-step agentic coding methodology this repo implements: vague
  ideas → insights → brief → architecture → repo policies → phased plan →
  sub-phase decomposition → orchestrated planner/reviewer/coder/critic loops
  → acceptance → log → human evaluation → stay agile. Invoke when scoping a
  new project, setting up a repo's planning structure, breaking a large
  initiative into phases, or when you need a reminder of the steps without
  reading the full brief.
---

# The Agentic Coding Methodology

A methodology for writing software with AI coding agents in a way that scales beyond ad-hoc prompting. Each step involves conversing with or using LLMs. Apply it when scoping or structuring a coding project — not when answering one-off coding questions.

The authoritative source is [`briefs/methodology.md`](../../../briefs/methodology.md). This skill is a slash-command-accessible restatement.

## The eleven steps

1. **Vague ideas → insights.** Turn vague ideas into insights, including competitive analysis. What problem are you actually solving? Who has already tried? What do you need to learn before committing?

2. **Insights → brief.** Turn the insights into a brief: *what* to build. The brief lives under `briefs/`.

3. **Brief → architecture document.** Decide *how*. Research Best Current Practices (BCPs) for each technical aspect: libraries, protocols, data formats, platform conventions. Lives under `briefs/` or `ARCHITECTURE.md`.

4. **Repo-level policies.** Codify standards and practices. Lives under `policies/`. Every phase honors every policy.

5. **Brief + architecture → phased plan.** Break the work down by phase. Each phase is independently testable and has a clearly defined goal and acceptance criteria. Lives under `plan/`; the spine is `plan/INDEX.md`.

6. **Sub-phase breakdown at phase start.** At the start of every major phase, break it down into sub-phases. Resist decomposing future major phases at bootstrap.

7. **Orchestrator-driven sub-phase execution.** Use a high-level orchestrator skill (`/kickoff`) that does **no coding itself**. It:
   - determines the current phase,
   - invokes a **planner agent**,
   - hands the plan to a **plan reviewer**,
   - hands the approved plan to a **coding agent**,
   - hands the result to a **code critic**,
   - on any critic's complaint, sends the work back to the relevant agent for revision (bounded loops).

8. **Acceptance check.** The orchestrator runs the tests and gates. Failures are classified (coder error, plan error, environment error) and routed back through the appropriate revision loop, with a cap before surfacing to the human.

9. **Append-only phase log.** `LOG.md` opens and closes work on every phase. Closing requires recording evidence of what happened and why the success criteria were met.

10. **Human evaluation.** The human evaluates each sub-phase. The orchestrator does not decide done.

11. **Stay agile.** Add new phases, or break existing phases into more sub-phases, as the problem and solution space become clearer.

## How to apply this methodology

- If you have only a vague idea, push to step 1.
- If a brief exists but no architecture, do step 3 and research BCPs.
- If architecture exists but no phase plan, do step 5.
- If a phase exists but no sub-phases, do step 6.
- If a sub-phase is being executed, follow step 7's orchestrator pattern (`/kickoff`).
- Whenever a phase opens or closes, write to the append-only log (step 9) with explicit evidence.

## The four canonical agents

The orchestrator delegates to four specialist roles. Their names are load-bearing:

| Role | Reads | Writes code | Job |
|---|---|---|---|
| `phase-planner` | Briefs, plan, repo | No | Turn one phase into a file-level implementation plan |
| `plan-reviewer` | Briefs, plan, repo, plan output | No | Approve the plan or send it back for revision |
| `phase-coder` | Briefs, plan, repo, approved plan | Yes | Implement the approved plan and run build gates |
| `code-critic` | Briefs, plan, repo, code diff | No | Approve the code or send it back for revision |

## Non-negotiables

- **Every completed phase is incremental and testable.**
- **The human decides when work is "done."**
- **The orchestrator never writes code itself.**
- **Closing a phase requires recorded evidence.**
- **Phases and sub-phases are mutable.**

## Source

This skill restates [`briefs/methodology.md`](../../../briefs/methodology.md). If that brief changes, update this skill.
