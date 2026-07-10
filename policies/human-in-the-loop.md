# Policy: Human In The Loop

The methodology assumes a human reviews each phase before the next begins. This policy is the operational consequence of that assumption.

## What the orchestrator never does

- **Never auto-commits.** `kickoff` finishes a phase by writing an END block and reporting to the human. Commits are the human's job.
- **Never advances past unresolved gates.** If a build gate fails after the bounded fix loop, `kickoff` surfaces the failure to the human; it does not silently downgrade the failure to a warning and proceed.
- **Never claims subjective acceptance.** If a phase has a manual acceptance criterion (audition the audio, eyeball the design, review the writing), the orchestrator surfaces the criterion in the END block. It does not say "I listened and it sounds great" — it cannot.
- **Never adds work the plan doesn't authorize.** Drift is contained to the plan that was actually approved. If the coder thinks something extra should land, the coder reports it as a Note for the human to consider.
- **Never edits closed phases.** A phase whose status is `✅` is closed. Changes belong in a new phase that supersedes or extends the old one.
- **Never modifies `policies/` or top-level `CLAUDE.md` without explicit instruction.** Those are the rules of the road; the orchestrator and the four canonical agents serve those rules, they do not amend them.

## What the human does

- **Decides "done."** The human reads each phase's END block, optionally audits the diff and the artifacts, and either:
  - Accepts the phase (commits the work, or asks the orchestrator to advance to the next phase).
  - Asks for revisions (calls `kickoff` again with feedback, or invokes a specific agent directly).
  - Rejects the phase wholesale (resets `plan/INDEX.md`, writes a follow-up END block documenting the rejection, refactors the plan).
- **Authors and amends briefs.** Briefs document the human's intent. Agents may propose changes (in their reports), but the human is the editor of record for `briefs/`.
- **Authors and amends policies.** Policies are the rules the human chooses to live by. Agents propose policies; humans approve them.
- **Commits.** Git history is the human's record. The orchestrator does not write commits — and especially does not write commit messages claiming credit for an agent.
- **Decides when to break a phase, merge phases, or abandon a phase.** Methodology step 11 ("stay agile") belongs to the human, not the orchestrator.

## Why this is non-negotiable

The methodology's value proposition is that the human's judgment is in the loop *cheaply*. Each phase is small enough that reviewing it is fast; each END block is structured enough that the review is grep-able. Removing the human review removes the value proposition.

Projects that need fully unattended code generation should use a different methodology. This one is wrong for that.

## "Authorization stands for the scope specified"

When the human approves a phase, the approval is for *that phase*. The orchestrator does not extrapolate ("the human approved Phase 2.3, so they probably want me to also do Phase 2.4") — it stops, writes the END block, and waits. The next phase requires the next `kickoff` invocation.

Similarly, when the human asks `kickoff` to "run all the remaining phases," that is a one-shot escalation, not a permanent policy change. The next session starts back at single-phase orchestration.

## When the human is asleep

If the human is unavailable (overnight, on vacation), `kickoff` does not silently proceed. It either:

- Reports as far as it can take a single phase (planner approved, coder approved, build gate green, END block written) and waits.
- Or, if explicitly authorized for a multi-phase run, runs to the end of the authorized scope, writes one END block per phase, and waits at the next phase boundary.

The orchestrator does not interpret silence as approval.

## Exception clause

The human may grant a phase-specific waiver of any rule in this policy. For example: "Go ahead and auto-commit Phase 1.1 since it's just scaffolding." Waivers are:

- **Explicit.** Stated in the current session, not inferred.
- **Scoped.** Apply to a named phase or a named action.
- **Logged.** The orchestrator records the waiver in the END block ("Pre-authorized: auto-commit by user").
- **One-shot.** They do not amend the policy. The next phase reverts to the policy's defaults unless the human grants another waiver.
