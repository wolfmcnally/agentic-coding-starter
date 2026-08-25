---
name: plain
description: >-
  The register for addressing the operator — the human who owns this project
  and makes its calls. Governs every message written to them: decision
  requests, ratification questions, phase reports and END blocks, status
  updates, demo narration, failure reports, and the plan bodies surfaced at an
  approval gate. Lead with the consequence, carry every detail that would
  change their answer, and leave the mechanism that produced it available on
  request rather than ambient. Invoke as /plain in Claude Code or $plain in
  Codex to recompose a message that missed the register; agents follow it
  without being asked whenever the audience is the operator.
argument-hint: "[<what to recompose>]"
last-reviewed: 2026-08-25
---

# Plain — the operator register

The operator owns this project, knows what it is for, and sets its goals. When
a message to them misses, the problem is almost never that they lack context —
it is that the message was composed at the wrong **altitude**. They operate at
the level of decisions and consequences; agents operate at the level of
mechanism. This skill is the translation at that boundary.

This is a register, not a reading level. Nothing here licenses vagueness,
hedging, or withholding. Precision about consequence, cost, and risk is the
entire point; what gets dropped is the project's internal vocabulary, not its
sharpness.

## The two tests

Every message to the operator passes both before it is sent.

**1. The relevance test — what earns its place.**

> A detail belongs in the message if changing it would change the operator's
> answer. Otherwise it is provenance, and provenance goes on request.

This is the test, not "is it technical." A schema field, a version number, or a
race condition stays in when the decision turns on it. A correct, interesting,
hard-won detail that leaves the answer unchanged is what crowds the decision
out of view — and it crowds it out precisely because it was expensive to
learn.

**2. The no-context test — whether it can be read.**

> Could the operator parse every sentence without the repo, the session, or the
> transcript open?

A sentence that needs any of those open to mean something is in the wrong
register. Rewrite it as behavior in the world.

## What always stays in

Dropping these is not plain language; it is an incomplete message.

- **The consequence.** What is true now, and what it means for the goal.
- **Anything irreversible.** What cannot be undone, what it would cost to
  reverse, what the blast radius is if the call is wrong.
- **Cost the operator pays** — money, their wall-clock, their attention,
  recurring manual work a decision commits them to.
- **What is blocked on them versus what proceeds regardless.** Never make them
  work out which of five items is the one holding everything up. This is the
  acceptance boundary in [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)
  stated out loud: gates block, judgment parks, and the operator should never
  have to infer which they are looking at.
- **Bad news, in the first sentence.** Plainly, no jargon camouflage, no
  softening. "The tests are red and here is what it costs" is this register. A
  paragraph of mechanism that eventually implies failure is not.
- **An identifier the operator must act on** — a command to type, a URL to
  open, a process to kill. When acting on the answer requires the exact string,
  give it exactly, ready to use. The rule below is about identifiers used as
  *explanation*, never about ones used as *instruments*.

## What goes below the fold

Available the moment they ask; never ambient.

- File paths, commit hashes, branch names, flag names, schema fields, enum
  tokens, phase numbers, span and trace ids, candidate ids.
- Internal shorthand invented mid-work. Name things by their role ("the review
  step", "the gate that runs the tests"), not by their label.
- Tool-level narration — "I ran X, then grepped Y." Report findings, not
  process. What you did is interesting to you; what you found is what changes
  their answer.
- Internal metrics that do not map to a cost the operator carries.

Per [`policies/treatise.md`](../../../policies/treatise.md) § "Explain
decisions, not files": paths and quotes are **evidence**, never the
explanation. A message whose explanation is a filename has not explained
anything.

## Shape of a decision

When something needs the operator's call, state it in this order. This is the
same five-part form the decision dialogue in
[`sweep`](../sweep/SKILL.md) requires, generalized to every operator-facing
decision in the repo.

1. **What is true today**, as behavior — "today, every phase must X."
2. **What changes** under the proposed answer — "nothing would require X."
3. **Why it came up** — what contradicted it, superseded it, or failed.
4. **What breaks if the call is wrong**, and whether that is recoverable.
5. **The recommendation**, so they can ratify in one word or dissent in one
   sentence.

Then stop. A decision presented alongside three more decisions is not
presented; it is queued.

### Batching

- **One concept per question.** Do not fold two calls into one sentence.
- **Batch the trivial; isolate the binding.** Homogeneous low-consequence items
  get one grouped question answerable in a word. Anything that changes what
  binds future work gets its own.
- **Never drip.** If five things need answering, the operator should learn that
  from the first message, not the fifth.
- **When a structured question control is used, the explanation goes in the
  message before it.** Option labels are a few words wide; they cannot carry
  the five parts above, and a short label is exactly how a consequential call
  gets waved through.

## Shape of a report

A status report, phase END block, or completion message answers three things in
order, and the third is often "nothing":

1. **What happened**, or what is true now.
2. **What it means** for the goal.
3. **What is needed** from the operator — decisions, manual checks, custody
   actions — or explicitly nothing.

Report outcomes faithfully. If tests failed, say so with the output. If a step
was skipped, say that. When something is done and verified, say it plainly
without hedging.

## The jargon audit is mechanical, not intuitive

Do not trust a self-check here. Experts asked to audit their own short
explanations flag about four of the roughly fourteen specialist terms they
actually used — the *curse of knowledge*, named by Camerer, Loewenstein and
Weber in 1989: once a concept is internalized, the memory of not knowing it is
gone, and with it the ability to notice it needs explaining.

So run a mechanical pass instead of asking yourself whether the message is
clear:

1. List every noun and noun phrase a competent newcomer to *this project* could
   not define.
2. For each one, do exactly one of: **replace** it with ordinary words,
   **define** it inline in about six words, or **keep** it because the decision
   turns on that exact term.
3. Anything that survives as none of the three comes out.

Two supporting habits from the plain-language standards, both cheap:

- **Active voice**, so it is clear who does what. "The gate blocks the phase,"
  not "the phase is blocked."
- **Ordinary words and short sentences** — average under about twenty words.
  Long sentences are where a decision hides behind its own qualifiers.

## What this register is NOT

- **Not vagueness.** Drop the internal vocabulary; keep the sharpness. "It
  might have some issues" fails this register worse than a commit hash does.
- **Not withholding.** Full depth is one question away and should be ready the
  moment they ask. "Want the mechanism?" is always a fine closer.
- **Not for agent-to-agent traffic.** Peers get full fidelity — ids, paths,
  internal names, all of it. The register switches at the **audience**
  boundary, per message.
- **Not for direct artifact requests.** When the operator asks for a command
  line, a config value, or a file's contents, the artifact is the answer —
  verbatim, unwrapped.
- **Not a summary.** Length is not the variable being optimized. A three-page
  decision brief can be in this register; a one-line status that requires the
  transcript open is not.

## Known failure modes

- **Register drift under dense technical work.** Hours inside the mechanism
  pull the next operator-facing message down with them, without any single
  sentence being obviously wrong. The audience switch is the checkpoint: before
  writing to the operator, re-run the two tests.
- **Context compaction sheds voice before it sheds state.** A summary preserves
  what you were doing and silently drops how you were told to communicate.
  After any compaction, re-read this skill before the next message to the
  operator.
- **Questions composed in the work's own vocabulary.** If a ratification
  request enumerates fields and section numbers, the operator has to
  reverse-engineer the decision from its implementation. Compose from the
  consequence side: what changes in the world under each answer.
- **The expensive detail crowds out the decision.** The harder something was to
  find, the more it wants to lead. Lead with what it means instead, and let the
  finding follow.
- **Plainness mistaken for softness.** Bad news gets rewritten into mechanism
  because mechanism feels less blunt. It is not kinder; it is slower and it
  buries the part they need.

## On invocation

`/plain` (Claude Code) or `$plain` (Codex) is a **correction**. Recompose the
most recent message to the operator in this register, and hold the register for
the rest of the session for everything addressed to them. An optional argument
names what to recompose ("the last question", "the phase report").

Agents follow this skill without being invoked whenever the audience is the
operator — it is a convention of the repository, not a command the operator
should have to remember to type.

## Sources

External, retrieved 2026-08-25:

- ISO 24495-1:2023, *Plain language — Part 1: Governing principles and
  guidelines* (as of 2023): a communication is plain when readers can find what
  they need, understand what they find, and use it — the four principles being
  relevant, findable, understandable, actionable.
- BLUF (bottom line up front) and the active-voice requirement, US Army
  AR 25-50 (as of 2023 revision).
- Federal Plain Language Guidelines (as of 2011, rev. 1): common words, active
  voice, average sentence length under about twenty words.
- Curse of knowledge: Camerer, Loewenstein and Weber (as of 1989); the
  self-audit shortfall on specialist terms is the practical consequence.
- Answer-first structure follows the Minto pyramid: the conclusion leads, the
  supporting reasons follow.
