---
title: "The Project Remembers"
date: 2026-08-24
status: implemented
scope: Canonical outward explanation of this repository for a general audience, from working engineers to readers who have never written code. Source of truth for every derivative rendering.
---

# The Project Remembers

**Author and maintainer: Wolf McNally.**

*Companion to [`BRIEF.md`](BRIEF.md), which describes what the template is, and [`methodology.md`](methodology.md), which states the eleven steps. This brief is the canonical explanation; rendered formats derive from it, and corrections land here first, per [`../policies/treatise.md`](../policies/treatise.md).*

---

An AI coding agent will write you a plausible plan, a plausible implementation, and a plausible report saying it all worked. Whether any of that is true has less to do with the model than with what the project around it writes down.

That is the claim this repository makes, and it is narrow enough to check: **an AI agent becomes reliable when the project holds the memory, the rules, and the evidence, so that every session starts from a written record and ends by updating it.**

Everything else here follows from that. The specialist roles, the phase ledger, the two rounds of testing at the end of every phase, the small deterministic scripts, the file where mistakes accumulate: each one exists because moving state out of the conversation made a specific failure visible, and a visible failure can be fixed.

## What goes wrong

Anyone who has worked with a coding agent for more than an afternoon has seen the same three things.

The first is forgetting. A session ends, or its memory fills up and gets compressed, and everything decided along the way goes with it. The next session has to be told again. Worse, it will happily re-open questions that were settled last week, because nothing in front of it says they were settled.

The second is a kind of circular grading. The agent that wrote the plan is the one asked whether the plan is good. The agent that wrote the code reports that the code works. Nothing independent ever disagrees, and a confident wrong answer looks exactly like a correct one right up until someone runs it.

The third is that none of it accumulates. The same mistake gets made and corrected on a two-week cycle. When a lesson does survive, it survives in one person's head, or in one tool's private memory on one laptop, none of which reaches the next session.

Three problems, three answers. Write the state down. Have something other than the author do the checking. Collect the mistakes on purpose.

## Writing survives what talking loses

The first answer is the least clever and does the most work.

Every project built this way keeps a small set of files that outlive any conversation. A brief says what is being built and why. An architecture document says how. A plan breaks the work into phases and puts them in order. A log records what actually happened. A policies folder holds the rules that every phase has to respect. None of this is exotic; it is the paperwork a careful team would keep anyway. The difference is that here the agent is required to read it before acting and to update it before finishing.

Two details make the difference between paperwork that helps and paperwork that rots.

**A fact lives in exactly one place.** Whether a phase is finished, in progress, or next up is recorded in one file and nowhere else. Individual phase documents are forbidden from carrying their own status field. Two places to look is one place to be wrong, and a project where two files disagree about what is done is worse off than one that never wrote it down.

**The log only ever grows.** Each phase opens with an entry saying what is being attempted and closes with an entry recording what happened, what was checked, and what remains open. Old entries are never edited. If something recorded last month turns out to be wrong, the correction is a new entry, so the record of the mistake survives alongside the fix.

The practical effect is undramatic and worth a lot: a new session reads the ledger and the last entry, and picks up. Nobody re-explains the project. When a long session runs out of room and its memory gets compressed, the compression takes the conversation and leaves the files, which are where the real state was.

## Nothing is accepted on its author's word

The second answer is where the design gets opinionated.

Work on a phase passes through four specialists, each with a narrow job. A planner turns the phase into a file-by-file plan and writes no code. A plan reviewer approves that plan or sends it back. A coder implements the approved plan. A code critic reads the result and approves it or sends it back. A fifth participant, the orchestrator, moves the work between them, keeps the records, and runs the tests.

The separation is the point. Reviewing your own homework produces a grade, not a check.

| Role | Writes code | Job |
|---|---|---|
| Planner | No | Turn one phase into a file-by-file plan |
| Plan reviewer | No | Approve the plan or send it back |
| Coder | Yes | Implement the approved plan |
| Code critic | No | Approve the result or send it back |

Round-trips between these roles are bounded. The loop continues while each pass is genuinely shrinking the list of open problems, and it stops for a human when the same complaint keeps coming back, which means the fix is not reaching whatever is generating the problem.

Then comes the part that sounds like a technicality and is the sharpest idea in the repository.

Every test result here is stamped with a fingerprint of the exact version of the project it ran against. Change any relevant file and the old result stops counting, because it was evidence about a version that no longer exists. This is why a phase ends with the full test suite running **twice**. The first run proves the code the critic approved. Then the orchestrator writes the closing paperwork: flip the status, append the log entry, file the lessons, generate the report. Those writes change the project. So the suite runs a second time against the version that is actually being handed over, and after that, nothing may be written at all.

A test run that certified a version nobody will ever have is not a test run.

That same insistence on knowing what a check actually proves shows up as a rule about instruments in general: a check earns trust only when it is able to report the failure it claims to guard against. The policies file spends a long section on the ways checks quietly lose that ability. A pipe that hides the real error code. A failure swallowed and replaced with a default that reads as fine. A stand-in measurement that was never the thing anyone cared about. And the subtle ones: a check that passes because it found nothing at all, or a survey that reports perfect uniformity because it was reading a field that cannot vary. All of these are one defect wearing different clothes. The instrument could only ever return one answer, so its answer carried no information.

### The line between what a machine can prove and what a person must judge

Given all that machinery, an obvious question follows: if the checking is this thorough, what is the human still for?

The repository answers by sorting every acceptance criterion into two kinds.

A criterion is **objective** when it can be run as a command, was reviewed by someone other than its author, was proved by the full test suite against that exact version, and was recorded rather than asserted. Those close on the machinery's own evidence.

A criterion is **subjective or owner-only** when no amount of green output can settle it. Does this feel right to use. Is this the right feature at all. Does the audio sound clean, does the page look wrong, is this copy any good. Anything requiring a password, a credit card, or a login the agent does not have. And the phase's own hands-on demo, until a person has actually sat down and tried it. Those always wait for the human, and the agent is forbidden from claiming them.

Until recently the human also had to make every commit by hand, which is to say: approve, in a formal sense, work they had no grounds to refuse. The test suite was green, the review was independent, the evidence named the version. As of 2026-08-24 the orchestrator does that step itself, under tight constraints. It stages only the files the phase touched, never a blanket "add everything," because another session may be working in the same folder. It writes an ordinary factual message with no credit to any agent. It never bypasses the safety hooks. It publishes only when there is exactly one unambiguous destination and the update is a clean fast-forward. Everything destructive stays with the person: no force, no rewriting history, no deleting branches, no choosing where the code goes.

Two properties keep that from being reckless.

Delivery does not mean acceptance, and it does not wait for it. A phase whose gates are green gets delivered even when its subjective criteria are still open, and those criteria stay open afterward exactly as they were. Being published is not the same as being liked. If the work turns out to be wrong, the correction is an ordinary follow-up, and nothing about having published it makes reversing it harder.

And what stops a phase is a failed check, never an open judgment. Confusing the two is exactly what made the old arrangement expensive: it spent the reviewer's attention on a bookkeeping step at precisely the moment the actual review needed that attention.

The compensating control is that the human's job moved rather than disappearing. It now sits at the seam between phases, on the closing entry and the hands-on demo. And the code critic has a new blocking duty: catch a criterion that has been filed under the wrong kind. A judgment call dressed up as an automated check is the one defect that would let a phase claim proof that does not exist.

The honest cost of the trade: a phase can be delivered and then judged wrong, and the fix is a follow-up rather than an unpublished draft. That was chosen deliberately.

## Mistakes are collected, and a person decides which become rules

The third answer is the one most projects skip.

Every phase ends with a required question: what did this teach us that will apply again? "Nothing" is an acceptable answer. Skipping the question is not. Whatever comes back gets filed as its own small document with a date, a description, and a count of how many times this has now happened.

Nothing becomes a rule on the third occurrence by itself. A person promotes it, one at a time, onto a named surface: a policy, a brief, a role definition, a script, a test. The threshold exists because a lesson written into law the first time it happens is usually wrong in ways its next two occurrences would have revealed. The human ratification exists because the alternative has a known failure mode.

That alternative is the obvious one: tell the agent to update its own instruction file with what it learned. Try it for a few months and watch the document. Each rewrite shortens it a little and sands off a little of what made it specific, until a page of hard-won detail has degraded into generic advice that no longer binds anything. Keeping the raw entries separate from the curated rules avoids that. The pile of entries grows. The rules are edited by hand, deliberately, one at a time, and each one can be traced back to the incidents that earned it.

The same logic runs between projects. This repository is a hub. One command stamps a new project from it. Another pushes improvements out to a project that was stamped from an older version. A third harvests back what those projects learned, along with any new defect exposed by the act of transferring, because applying a pattern somewhere new is a real test of that pattern. The return path matters most, and for a specific reason: a working project exercises this machinery at a scale the template itself never does, so that is where the interesting defects surface first.

Two disciplines keep that traffic honest. A project being further ahead in general proves nothing about any particular file, so direction is established one item at a time. And before importing somebody's fix, the problem it fixes has to be shown to exist here, because a repair for a defect the destination solved differently is a regression wearing the shape of an improvement.

## What it costs

An honest accounting, since the structure is not free.

It loses to a one-line prompt on anything small. Writing a brief, a plan, and a phase to change a script that will be thrown away next week is silly. Use the quick thing for the quick thing.

It gives up unattended autonomy at the end. Work that can be proved gets delivered without asking, but the process still stops at every point where a judgment is genuinely required, and silence from an absent human is never read as approval. A project that wants no human judgment anywhere wants a different method.

It gives up wandering mid-flight. Once a phase starts, the orchestrator follows the plan. Explore before it starts, or between phases.

There is also a limit inside the method rather than a trade against it. A set of sixteen rules governs what happens when a long automated run hits trouble, distilled from a single production day in a real project where one run stopped nine times, and each stop was diagnosed and turned into a standing rule. Most of those rules are still written guidance rather than enforced machinery. Some of the enforcement exists; some does not. The document says so in its own text rather than leaving a reader to discover it, which is the same discipline it asks of everything else.

## Checking any of this

None of the above has to be taken on faith. From a copy of the project, one command runs every check the method claims to run: twelve categories, 572 tests, which passed on 2026-08-24. Other commands verify that the rules are indexed, that no duplicated instruction file has drifted from its original, that the lessons ledger is well formed, and that no private path or external project name has leaked into a public repository. Counts in this document come from those commands, and a reader who wants to reproduce them can find each one in the table at the end of the eleven-step brief.

The verification that matters most needs no command at all. Read one phase's closing entry, then read the change it delivered. Those two documents should agree, and if they do not, that is visible to anyone who looks.

## Where this comes from

This brief derives from, and must stay consistent with:

- [`BRIEF.md`](BRIEF.md), the entry-point brief: what the template is, who it is for, the two ways it gets used, and what counts as done.
- [`methodology.md`](methodology.md), the eleven steps, the four roles, the runtime doctrine, and the vocabulary for how runs end.
- [`harness-self-improvement.md`](harness-self-improvement.md), the two-tier improvement loop, its grounding in the literature, and what was deliberately declined.
- [`incremental-orchestration.md`](incremental-orchestration.md), the evidence machinery as implemented.
- [`eacp-pattern-map.md`](eacp-pattern-map.md), this repository mapped onto named patterns from the Encyclopedia of Agentic Coding Patterns, including the patterns it declines and the failure modes it guards against.
- The `policies/` folder, which owns every prescriptive claim above.

Corrections land here and in the owning source, then regenerate outward. A rendered version that disagrees with this brief is out of date, not authoritative.
