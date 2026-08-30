---
title: "Rule One: From Symptom to Durable Learning"
date: 2026-08-29
status: methodology
scope: "Portable methodology for responding to wrong or unexpected outcomes through symptom recognition, causal diagnosis, containment, correction, prevention, and cross-harness persistence."
---

# Rule One: From Symptom to Durable Learning

This brief preserves the reasoning behind Rule One separately from Rule One's
operative prescriptions. It records the findings established so far, the
distinctions those findings require, and the diagnostic questions still open.
It is deliberately a living methodology brief: later rule or skill text may
cite its reasoning, while this document remains the place to refine that
reasoning without prematurely turning every hypothesis into an instruction.

Within this template, `.claude/skills/rule-one/SKILL.md` is the independent,
repo-canonical prescription. This brief is its required reasoning companion.
The pair is one portable methodology unit: `teach` offers both to another
repository, and `learn` assesses both from a peer repository, without assuming
the destination's particular lesson ledger, policies, hooks, or harness layout.
Neither member transfers alone; an already-current member is still checked for
compatibility with the one being added or revised.

## 1. The broad trigger is intentional

Rule One begins when something goes wrong or not as expected. That trigger is
broader than postmortem learning because the first response to an anomaly is
already consequential. The same initial interpretation shapes:

- what is contained;
- what is repaired;
- what is changed to prevent recurrence; and
- what account is preserved for future work.

Rule One therefore starts at first recognition, not after resolution. Its
prevention-facing maxim gives the process a forward direction, but accurate
diagnosis is necessary before containment, correction, or prevention can be
well chosen.

Unexpected favorable results belong within the same trigger. They may require
no containment or correction, but they still require diagnosis before anyone
tries to reproduce, amplify, or generalize them.

## 2. What appears is a symptom

The observable wrong or unexpected condition is best called a **symptom**, not
an event, cause, failure mechanism, or diagnosis.

The term carries an important warning: the place where a problem becomes
visible is rarely shaped like the place where an effective intervention should
act. A failing test may expose an incorrect contract, an invalid fixture, a
race, or a broken test. A wrong report may expose bad source data, faulty
conversion, independent derivations that drifted, or unsupported recall. The
symptom alone does not choose among them.

The working maxim is:

> **What went wrong is a symptom, not a diagnosis. The symptom shows where the
> problem became visible; it does not establish where the problem originated
> or where remediation should act. Never derive the remedy from the symptom's
> shape alone.**

This maxim opposes **symptom-shaped remediation**: changing the visible layer
merely because that is where the anomaly appeared. Suppressing an error,
loosening a test, adding a length cap, or rewriting an output can be useful
containment. None of those acts, by itself, establishes or repairs the cause.

## 3. Diagnosis is a causal account for action

Diagnosis connects the symptom to the conditions that produced it. The target
is not an ultimate explanation of everything, nor a ritual declaration of one
"root cause." It is an evidence-backed causal account strong enough to choose
an intervention without claiming more certainty than the evidence supports.

A useful causal account distinguishes:

- the expected condition from the observed symptom;
- the earliest relevant divergence between them;
- the decisions, assumptions, states, and environmental conditions that
  contributed to that divergence;
- which proposed causes are supported, contradicted, or still
  indistinguishable;
- which contributing conditions are actionable at the scope of the work; and
- what evidence would change the diagnosis.

Complex failures often have several necessary or contributing causes. A
singular root-cause label can hide that structure, especially when it selects
the last human action while ignoring the system conditions that made the
action dangerous. Rule One needs causal accuracy, not false singularity.

Counterfactual reasoning is one useful test of a causal claim: if the proposed
condition had been different, would the symptom probably have changed? It is
not sufficient by itself. A plausible counterfactual still needs evidence that
the condition existed and participated in the actual chain.

## 4. Map the contribution system before selecting a cause

The Harvard Negotiation Project's **contribution system** supplies a useful
diagnostic method for resisting false singularity. It replaces “Who is to
blame?” with a different question: how did the actions, omissions, assumptions,
constraints, and reactions of everyone involved combine to produce and sustain
the symptom?

The distinction is not cosmetic. Blame combines three inquiries: what caused
the outcome, whether someone violated a standard, and what judgment or
consequence should follow. Contribution isolates causal participation so the
system can be understood and changed. It does not settle, erase, or forbid a
separate inquiry into fault, responsibility, or accountability.

A contribution map considers more than the last visible action. Its candidate
contributors include:

- what each participant did or failed to do;
- how each participant reacted to the others;
- assumptions, interpretations, communication styles, and expectations;
- unspoken or conflicting ideas about roles and responsibilities;
- avoidance, delay, silence, and failures to raise a concern;
- policies, incentives, workflows, tools, and other structural conditions;
- third parties and external conditions; and
- reciprocal loops in which each response elicits or reinforces the next.

The map should include the investigator's own contribution without making it
the exclusive focus. It should also include actors and conditions outside the
immediate interaction. Contributions need not be equal, voluntary, culpable,
or equally actionable. Differences in authority, knowledge, capacity, and
freedom to act remain part of the causal account.

One practical mapping sequence is:

1. State the symptom without embedding a culprit or mechanism in its
   description.
2. Identify the participants, third parties, structures, and external
   conditions that formed the relevant system.
3. For each, list actions and omissions that may have created, prolonged,
   concealed, or intensified the symptom.
4. Trace interaction loops rather than treating every contribution as an
   independent item.
5. Probe common blind spots: avoidance until now, being difficult to approach,
   differences in background or working style, and incompatible role
   assumptions.
6. Change vantage point through role reversal and the perspective of a neutral
   observer.
7. Test the resulting causal hypotheses against chronology, direct evidence,
   plausible alternatives, and counterfactuals.
8. Identify which evidenced contributions provide leverage for containment,
   correction, or prevention.

The seventh step is essential. A contribution map broadens the field of causal
hypotheses; it does not prove them. Without evidentiary testing, “the system
contributed” can become as empty as an unsupported singular root cause.

The method also needs an ethical boundary. Causal contribution is not moral or
legal culpability, and contribution is never presumed to be evenly divided.
Mapping a harmed party's participation must not imply that they deserved the
harm or possessed the same power to prevent it. Conversely, describing a
system must not be used to dissolve an actor's genuine wrongdoing into
ambient conditions. System diagnosis and accountability are compatible but
distinct inquiries.

## 5. Containment, correction, and prevention are different responses

The three response classes answer different questions:

| Response | Question | Evidentiary need |
|---|---|---|
| **Containment** | What limits current harm or spread? | Enough diagnosis to avoid worsening the condition, destroying evidence, or blocking the eventual repair. |
| **Correction** | What restores the present system or result? | Enough diagnosis to act on the operative causal condition rather than only conceal its symptom. |
| **Prevention** | What changes future behavior or system conditions? | Enough diagnosis to identify what would materially reduce recurrence or impact. |

These responses need not occur in a strict sequence. Urgent containment may
precede a complete diagnosis. When it does, its provisional basis matters: a
good emergency containment is proportionate, reversible where possible, and
preserves the evidence and options needed for diagnosis. It does not acquire
the status of a correction merely because the symptom disappears.

Correction can also expose new evidence and revise the diagnosis. Prevention
should use the revised account rather than the first plausible story formed
under pressure.

## 6. The conceptual loop

The current model is:

1. **Recognize the symptom.** State the observed divergence without embedding
   a causal conclusion in its description.
2. **Diagnose.** Reconstruct the chronology, map the contribution system, and
   test the causal account while preserving genuine uncertainty.
3. **Contain.** Limit active harm when needed, with the provisional diagnosis
   and reversibility made explicit.
4. **Correct.** Repair the present condition at the causally appropriate
   layer.
5. **Prevent.** Derive the smallest future change justified by the causal
   account.
6. **Persist.** Place the reusable learning on a durable cross-harness surface
   at the appropriate scope and degree of permanence.
7. **Verify.** Confirm both that the response changed the intended condition
   and that the learning is actually available to future work.

The model is recursive rather than simply linear. A failed containment, an
unexpected correction result, or a recurrence is a new symptom and reopens
diagnosis. Persistence is not proof that the diagnosis was right; later
evidence may strengthen, narrow, or retire the lesson.

## 7. Persistence follows diagnosis and discernment

A false causal story becomes more dangerous when memorialized. Rule One's
persistence discipline therefore cannot compensate for weak diagnosis. The
order matters: symptom recognition and causal analysis precede abstraction;
only then can the resulting lesson be routed.

Persistence must adapt to the environment:

- repositories may provide separate provisional and permanent surfaces, such
  as a lessons ledger, instructions, policies, procedures, skills, tests, and
  executable guards;
- simpler repositories may provide only one cross-harness instruction file;
  and
- outside a repository, only a global cross-harness instruction surface may
  be available.

Harness-specific memory is not a durable methodology surface. It binds the
learning to a vendor, hides it from other harnesses and subagents, and makes
the next environment repeat the discovery.

Mechanization is likewise conditional. Once discernment establishes a stable,
mechanically detectable invariant, a guard may be the strongest persistence
or enforcement surface. Diagnosis, causal interpretation, provisional
learning, and scope selection remain judgment-bearing work. A mechanism may
carry a settled decision; it should not manufacture one from a convenient
proxy.

## 8. Three worked distinctions

### Wrong weekday

The symptom was a reset time reported with the wrong weekday even though the
relative interval was correct. Changing only the weekday would correct that
one answer. The useful diagnosis was that the calendar label and relative
interval had been derived through separate paths, allowing two individually
plausible outputs to disagree. The preventive response was therefore not
"remember which weekday it is," but to derive the weekday, date, time, zone,
and interval from the same system-resolved timestamp.

### Oversized construction plan

The symptom was a plan whose size and review growth had become unreasonable.
A line ceiling and growth stop contained further expansion. The immediate
diagnosis found that most added text duplicated gate commands already present
in authoritative verification blocks and scripts. Referencing those existing
blocks corrected the duplication mechanism. The containment did not itself
explain the growth, and the correction did not by itself settle every broader
question about why review had rewarded duplication. Those remained separate
diagnostic work.

The example also shows why a guard and a causal repair may coexist. The guard
catches recurrence at the symptom boundary; the repair changes a condition
that produced the symptom.

### WIP brief sent through the full repository gate

The symptom was a full repository gate running after a work-in-progress brief
was added, followed by a second full-gate launch after small cross-link edits.
The operator had explicitly said that the brief would be discussed and revised
before Rule One changed. No handoff, delivery, or settled candidate was pending.

Stopping the second gate and proving that its process group was gone contained
the continuing wall-clock cost. Confirming that the interrupted mutation tests
left only the intended brief paths corrected the immediate operational risk.
Neither action explained why the gate had been selected.

The relevant causal account was:

- the repository has a legitimate full-gate requirement at handoff;
- the brief was a tracked methodology artifact, but it was not at a handoff
  seam;
- verification was selected from the artifact category rather than from the
  lifecycle decision and affected risk;
- no property was named that the unrelated software, mutation, workflow, and
  shell checks could usefully falsify about the brief; and
- after the first run, candidate-invalidation momentum caused the minor
  cross-link edits to trigger another run without revisiting whether the first
  run had ever been warranted.

The existing “weakest falsifying instrument” doctrine already pointed toward
focused inventory and formatting checks. The failure was not absence of a
rule; it was failure to apply that rule when choosing the verification scope.

The candidate preventive principle is:

> **Before launching an expensive verification, name the lifecycle decision
> it informs and the defect class it can falsify. Select verification from
> those properties, not from the artifact's category. A work in progress with
> no handoff pending receives focused checks; a full gate belongs at a genuine
> integration, handoff, or delivery seam unless the changed surface itself can
> affect the whole product.**

This case is also recursive Rule One evidence. The attempt to verify that a
lesson had been persisted produced a new symptom. Applying Rule One required
diagnosing the verification decision itself rather than merely apologizing,
canceling the command, or adding a blanket “do not run gates on briefs” rule.

## 9. Failure modes already visible

- **Symptom-shaped remediation:** changing the visible output without tracing
  what produced it.
- **Containment presented as correction:** treating disappearance of the
  symptom as proof of repair.
- **Guard presented as understanding:** enforcing a boundary without learning
  why the system approached it.
- **False singularity:** naming one root cause when the evidence supports a
  chain or set of contributing conditions.
- **Blame-shaped diagnosis:** selecting the person nearest the symptom and
  treating causal participation, fault, and punishment as one question.
- **Equalized contribution:** treating membership in the same causal system as
  evidence of equal agency, influence, responsibility, or culpability.
- **Systemic exoneration:** invoking complexity or shared conditions to avoid a
  separate and warranted accountability inquiry.
- **Premature abstraction:** writing a general rule before the mechanism is
  distinguishable from alternatives.
- **Causal laundering through persistence:** treating a written lesson as more
  certain merely because it is durable.
- **Mechanized discernment:** making a proxy classify meaning, scope, or
  causation and then citing the resulting inventory as proof.
- **Vendor-bound learning:** saving the account in a harness memory that future
  harnesses cannot consult.
- **Unmemorialized intention:** saying "going forward" without changing any
  surface future work will actually encounter.
- **Lifecycle-blind verification:** selecting a check from the artifact's
  category without naming the pending decision or defect class the check can
  falsify.

## 10. Open diagnostic-method questions

The next refinement should research and compare diagnostic methods rather than
install one familiar ritual by default. Open questions include:

1. Which methods are useful for which symptom shapes: timeline and change
   analysis, contribution-system maps, causal graphs, fault trees, barrier
   analysis, Five Whys, fishbone-style factor inventories, counterfactual
   tests, or other methods?
2. How should Rule One select a method proportionate to consequence,
   uncertainty, reversibility, and available evidence?
3. What minimum causal confidence is appropriate for containment, correction,
   prevention, and permanent memorialization respectively?
4. How should the analysis distinguish a trigger, a proximate cause, a
   contributing condition, a latent system condition, and an absent safeguard?
5. What stopping rule yields an actionable diagnosis without rewarding endless
   causal excavation?
6. How should positive surprises be diagnosed so successful behavior can be
   reproduced without confusing correlation with cause?
7. How should a later recurrence update the causal account and the permanence
   of the prior lesson?
8. How should Rule One select verification proportional to the current
   lifecycle seam, so persistence verification does not itself trigger an
   unrelated full-gate ratchet?
9. How should contribution mapping represent differences in power, knowledge,
   agency, and duty without collapsing causal participation into blame or
   allowing system complexity to erase accountability?

These are research questions, not deferred implementation tasks. Their answers
belong in this brief before they are compressed into Rule One's prescriptive
surface.

## 11. Relation to adjacent methodology

[Harness Self-Improvement](harness-self-improvement.md) explains this template's
capture, provisional-ledger, graduation, and pruning architecture. This brief
sits earlier in the chain: it asks whether the account being captured is
causally sound.

[Deterministic Orchestration](deterministic-orchestration.md) separates
judgment-bearing classification from deterministic routing. This brief
generalizes that boundary to diagnosis: causal interpretation remains
judgment-bearing, while settled and detectable responses may later be
mechanized.

The resulting separation is deliberate:

- this brief owns the evolving rationale and diagnostic model;
- later prescriptive surfaces may state the concise behavior future work must
  follow; and
- repository-specific ledgers, policies, procedures, tests, and guards remain
  local adaptations rather than prerequisites of the portable methodology.

## Sources

- Operator discussion, 2026-08-29. Source of the symptom terminology, the
  broad-trigger interpretation, the requirement that diagnosis inform
  containment and correction as well as prevention, the cross-harness
  persistence constraint, the separation between this brief and Rule One's
  prescriptions, and the lifecycle-blind full-gate case.
- Douglas Stone, Bruce Patton, and Sheila Heen, *Difficult Conversations: How
  to Discuss What Matters Most*, second edition, Penguin, 2010, especially the
  chapter on abandoning blame and mapping contribution. Source text as of
  2010; retrieved 2026-08-29:
  <https://siliconflatirons.org/wp-content/uploads/2017/04/Difficult-Conversations-Chapters-1-5.pdf>.
- Sheila Heen, “Moving Through the Tunnel: A Harvard Expert's Guide to
  Difficult Conversations.” The interview directly describes the contribution
  system as the actions and omissions of all involved plus external factors,
  rejects an equal-allocation premise, and connects the map to future change.
  As of 2025-08-25; retrieved 2026-08-29:
  <https://workplaces.org/podcast-transcript/transcript-moving-through-the-tunnel-a-harvard-experts-guide-to-difficult-conversations-sheila-heen-triad-consulting-group>.
- Douglas Stone, “The Talk: Douglas Stone on 'difficult conversations.'” The
  interview explains role reversal and the observer's perspective as ways to
  expose one's own contribution and other blind spots. As of 2011-06-24;
  retrieved 2026-08-29:
  <https://economictimes.indiatimes.com/the-talk-douglas-stone-on-difficult-conversations/articleshow/8965640.cms>.
- NASA, *NPR 7120.6 Lessons Learned Process*, revalidated 2010-01-22. Historical
  precedent for treating lessons as collected, assessed, validated, documented,
  and infused through existing corrective-action systems. The displayed NASA
  page marks the directive obsolete, so it is evidence of the process model,
  not current NASA authority. Retrieved 2026-08-29:
  <https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7120_0006_&page_name=all>.
- Google, *Site Reliability Engineering Workbook*, “Postmortem Culture:
  Learning from Failure.” The chapter distinguishes impact, mitigation,
  recovery, root causes and triggers, mitigative actions, and preventive
  actions; it also treats detailed causal reconstruction and tracked action as
  central to recurrence prevention. Source publication date not stated on the
  online chapter; retrieved 2026-08-29:
  <https://sre.google/workbook/postmortem-culture/>.
- [Harness Self-Improvement](harness-self-improvement.md), as of 2026-08-29.
  The template's existing rationale for provisional capture, owner-ratified
  graduation, cross-harness persistence, and pruning.
- [Deterministic Orchestration](deterministic-orchestration.md), as of
  2026-08-29. Boundary between judgment-bearing classification and
  deterministic routing.

---

Authored 2026-08-29. Revisit after the diagnostic-method comparison and before
the next Rule One revision.
