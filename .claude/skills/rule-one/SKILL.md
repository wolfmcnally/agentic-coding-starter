---
name: rule-one
description: >-
  Rule One turns corrections, failures, surprises, repeated work, and discarded
  effort into accurate, durable cross-harness learning. It treats the observed
  problem as a symptom, diagnoses before deriving remediation, and persists any
  reusable lesson. Use when an approach is corrected, a command or test fails
  unexpectedly, results contradict assumptions, work gets thrown away, context
  keeps being re-explained, or an insight is worth preserving for future work.
---

# Rule One: Continuous Self-Improvement

> When things go wrong or not as expected, ask yourself:
> **"What can I remember to do differently next time so this doesn't happen again?"**
> Act on that.

> **What went wrong is a symptom, not a diagnosis.** The symptom shows where
> the problem became visible; it does not establish where the problem
> originated or where remediation should act.

Rule One operates in any environment. It depends on discernment, not a
particular repository layout, tool, or harness memory system.

**A lesson is not learned until it has been written to a durable,
cross-harness surface.** An intention such as "I'll remember" or "going
forward" is not a completed lesson.

## When to trigger Rule One

Use Rule One when any of these occur:

- **Correction**: The user rejects or redirects an approach.
- **Failure**: A command, test, build, deployment, or workflow fails
  unexpectedly.
- **Surprise**: Results differ from a prediction or assumption, favorably or
  unfavorably.
- **Repeated work**: The same context must be explained again.
- **Wasted effort**: Work is discarded because the approach was wrong.
- **Hard-won insight**: Effort reveals something non-obvious and reusable.

A one-time instruction with no plausible recurrence is context, not a lesson.
Do not invent a general rule merely to complete the process.

## The response and learning cycle

### 1. Recognize the symptom

Pause and state the expected condition and the observed divergence without
embedding a culprit or causal mechanism in the description. Do not silently
make the symptom disappear and move on.

If active harm may continue while diagnosis proceeds, contain it first with a
proportionate and preferably reversible action. Preserve the evidence and
options needed for diagnosis, and identify the containment as provisional.

### 2. Diagnose proportionately

Build an evidence-backed causal account sufficient to choose a response:

- locate the earliest relevant divergence, not only the final visible action;
- distinguish observation from inference;
- identify which proposed causes are supported, contradicted, or still
  indistinguishable;
- test important claims against chronology, direct evidence, plausible
  alternatives, and counterfactuals; and
- state what further evidence would change the diagnosis.

When several actions, people, tools, or conditions interacted, map the
**contribution system**. Ask how actions, omissions, reactions, assumptions,
role expectations, workflows, incentives, tools, third parties, external
conditions, and reinforcing loops helped produce or sustain the symptom.
Include your own contribution without making it the exclusive focus.

Contribution is causal participation, not moral or legal culpability. Do not
presume equal contribution, agency, influence, responsibility, or freedom to
act. A system account must neither blame a harmed party for the harm nor erase
genuine individual accountability. Treat every proposed contribution as a
hypothesis until the evidence supports it.

A simple symptom may have a simple cause. Stop when the causal account is
strong enough to choose the response and unresolved alternatives would not
change it. Investigate further when the uncertainty would change safety, the
correction, the preventive action, or the permanence of the lesson.

### 3. Respond at the causally appropriate layer

Distinguish three possible responses:

- **Containment** limits current harm or spread. It may precede a complete
  diagnosis, but disappearance of the symptom does not prove correction.
- **Correction** restores the present condition by acting on the operative
  causal conditions rather than merely concealing the symptom.
- **Prevention** changes future behavior or system conditions to reduce the
  likelihood or impact of recurrence.

Use only the responses the situation needs. A favorable surprise may require
diagnosis and learning without containment or correction. A failed response or
recurrence is a new symptom and reopens diagnosis.

### 4. Distill the lesson

Determine whether the causal account reveals a reusable change in future
behavior. If it does, state the smallest principle that would prevent the same
class of failure without overreaching beyond the evidence.

If it does not, say why. A one-time condition or unresolved hypothesis may be
worth recording as context without becoming a rule. Pretending that every
surprise deserves a permanent prescription creates noise.

**Too specific:** "Port 5432 is used by local Postgres."

**Reusable:** "Before binding a local port, check whether it is already in
use."

**Not a rule:** "The test failed."

**Actionable:** "When an API shape is undocumented, inspect the actual
response before writing assertions."

### 5. Persist or strengthen

Read the environment's own instructions before choosing a destination. Search
for an existing rule that covers the behavior, then use the narrowest existing
surface that is durable, cross-harness, and authoritative for the lesson's
scope. Do not invent a repository structure that the environment has not
adopted.

Common surface classes include:

- a global instruction file for behavior that applies across environments;
- a project instruction, policy, procedure, or skill for established local
  rules;
- a project-provided lessons, incident, or decision ledger for provisional
  learning;
- a test, lint rule, hook, or executable guard when the settled requirement is
  genuinely mechanically detectable.

Some environments provide several permanent and provisional surfaces; others
provide only one instruction file. Adapt to what exists. Outside a repository,
use the available global cross-harness instruction surface.

Do not use harness-specific memory as the durable home for a lesson. It is not
portable to other harnesses, agents, operators, or machines. If no writable
cross-harness surface is available, report that persistence is blocked and
name the required destination; do not claim the lesson was learned.

Then do one of the following:

- add the lesson at the appropriate permanent or provisional scope;
- strengthen an existing entry when its wording failed to prevent the problem;
- when an adequate rule already exists, identify it and correct the failure to
  load or follow it rather than adding a duplicate.

Lead with the future action, include enough reason to prevent blind
application, and preserve the terminology and conventions of the destination.

Before creating a test, hook, lint rule, mutation row, or guard, name the active requirement, how correctness is judged, and the nearest existing enforcement. When the same requirement is proved in the same way, strengthen the existing proof or proof family instead of creating another. Similarity alone does not justify consolidation: preserve independent evidence for distinct failures. Read the local proof inventory, admission criteria, and budget before authoring; a new incident does not by itself establish a new proof family.

Mechanization follows discernment. Use a guard when the environment supports
one and a settled requirement is mechanically recognizable. A guard can
enforce a decision or contain a symptom; it does not establish the diagnosis.
Do not force judgment, context, causation, or a provisional hypothesis into a
mechanical check merely because a tool is available.

### 6. Verify and report

Verify two different outcomes when they apply:

- **Response verification:** confirm that containment, correction, or
  prevention changed the intended condition without creating a worse one.
- **Persistence verification:** re-read the persisted artifact and confirm
  that it contains the intended learning, at the intended scope, on a surface
  future harnesses will actually load or consult.

Choose verification from the lifecycle decision it informs and the defect
class it can falsify, not merely from the artifact category. Use the least
expensive instrument capable of falsifying the relevant claim. Expensive or
integration-wide checks belong at the seams where the environment requires
them or where the changed property can affect the wider system.

Before replying, reach one honest outcome:

- **Persisted:** name what was added or strengthened and where.
- **Already covered:** cite the existing rule and state how the failure to load
  or follow it was corrected.
- **No reusable lesson:** explain why the event should remain context only.
- **Persistence blocked:** name the unavailable or unauthorized destination
  and do not claim completion.

Also report any containment or correction still provisional or unverified.
Then continue the original task. "I'll remember" is never a terminal outcome.

## Persistence hygiene

- Prefer one well-scoped rule over several overlapping ones.
- Distinguish provisional evidence from a settled requirement.
- Resolve conflicts instead of appending another instruction.
- Retire or revise stale rules through the environment's existing governance.
- Test the wording against a fresh session: would it change the relevant
  decision without requiring hidden context?
