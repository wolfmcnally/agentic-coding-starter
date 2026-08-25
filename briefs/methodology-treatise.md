---
title: "The Project Remembers"
date: 2026-08-25
status: implemented
scope: Canonical primer on this repository for a general audience, from working engineers to readers who have never written code. Explains what the repository is for and how its parts work. Source of truth for every derivative rendering.

# Editorial record, managed by the `treatise` skill under policies/treatise.md.
# The presence of this block is what marks the brief as a treatise.
# `directives` is append-only: a reversal is a new dated entry, never an edit.
treatise:
  updated: 2026-08-25

  purpose: >-
    Explain what this repository is for and how its parts work, to a reader who
    has not seen it. Canonical outward explanation; every rendered format
    derives from this brief, and corrections land here first.

  audience:
    primary: >-
      Anyone evaluating or curious about the repository, whether or not they
      write software.
    range: >-
      Experienced engineers through readers who have never coded. Both ends
      must be able to finish the piece.
    may_assume: >-
      That the reader has heard of AI coding assistants and knows software is
      built in steps. Nothing further.
    must_not_assume: >-
      Git vocabulary, test-suite vocabulary, agent-harness vocabulary, or any
      familiarity with this repository's own file layout and terms.
    not_written_for: >-
      Contributors needing implementation detail; they are served by the
      policies and the eleven-step brief, which this piece links.

  register:
    form: primer
    flow: magazine article
    voice_skills: [humanizer, minto]
    constraints:
      - No self-congratulation. Praising the design reads as slop.
      - Present tense. What the repository does, never where it has been.
      - Explain each term in plain words at first use.
      - Paths and commands stay out of the argument.
      - Sentence-case headings. Straight quotes. No emoji.

  coverage:
    includes:
      - The repository's purpose as an opinionated, evolving practice collection.
      - The claim that the project, rather than the conversation, holds the state.
      - The three failures the method answers, and one answer per failure.
      - The four roles, the two-run close, and the acceptance boundary.
      - The lessons ledger and the hub-and-spoke transfer between projects.
      - The honest costs, including where enforcement is written rather than mechanized.
      - Where to find the repository and the two ways to start using it.
    excludes:
      - A directory tour or a file inventory.
      - Change history of the methodology itself.
      - Implementation detail the policies already own.
      - Any claim not traceable to this repository or a dated external source.

  directives:
    - date: 2026-08-24
      ruling: >-
        "on the subject of this repo: the methodology, its architecture, its
        workflows, skills, etc. You can credit me as author and maintainer.
        Markdown brief as always then publish as an artifact for my review."
      effect: Established the treatise, this brief, and the private artifact rendering.
    - date: 2026-08-24
      ruling: '"It is dense. It needs to have a better, magazine-article like flow."'
      effect: Replaced numbered sections with an article; fewer sections, more air.
    - date: 2026-08-24
      ruling: >-
        "It is too technical. The audience ranges from experienced engineers to
        people who have never coded."
      effect: Removed repository vocabulary from the argument; glossed every term at first use.
    - date: 2026-08-24
      ruling: '"It has many AI tells. It should be run through /humanizer."'
      effect: Voice pass applied and mechanically checked; recorded as standing, not one-time.
    - date: 2026-08-24
      ruling: '"It should probably follow the /minto flow."'
      effect: Restructured answer-first, three arguments, one concrete each; standing.
    - date: 2026-08-24
      ruling: '"self-congratulatory statements read as slop."'
      effect: Cut every line praising the design's own cleverness; standing constraint.
    - date: 2026-08-24
      ruling: >-
        "this is not a history, it is a primer; explain what the repo does, not
        where it's been."
      effect: Removed all before-and-after narration; form fixed as primer, tense as present.
    - date: 2026-08-24
      ruling: >-
        "It should introduce me as the creator of https://aipatternbook.com and
        https://bartleyeditions.com."
      effect: Byline expanded, both sites visited so the description is sourced.
    - date: 2026-08-24
      ruling: >-
        "it should state what the overall purpose of the repo is: to collect in
        one place an evolving yet opinionated set of best practices for agentic
        software construction."
      effect: Purpose moved to the opening section; the two adjectives earned in their own paragraph.
    - date: 2026-08-24
      ruling: >-
        "The treatise describes a repo so you should probably tell people where
        to find it and how to get started with it."
      effect: Added the getting-started section, sourced from README.md.
    - date: 2026-08-25
      ruling: >-
        "I forgot that we can actually put the sidecar in as YAML front matter
        directly in the markdown... It would obviate the need for another file
        and more closely couple this metadata."
      effect: >-
        Editorial record folded into this frontmatter; the separate
        methodology-treatise.yaml deleted. Presence of the `treatise` block is
        now the marker, so no separate flag can contradict it.

  renderings:
    - format: artifact
      url: https://claude.ai/code/artifact/d1bf77fe-e6d5-46a3-8599-c5e00ff69de4
      visibility: private
      published: 2026-08-24

  external_facts:
    - claim: >-
        Bartley Editions publishes living reference works curated by human
        experts and kept current by the Bartley engine, in place of a publishing
        house and a decades-long production cycle.
      source: https://bartleyeditions.com
      retrieved: 2026-08-24
    - claim: >-
        The Encyclopedia of Agentic Coding Patterns is a compendium of tested
        patterns for building software with AI agents, roughly 308 entries
        across patterns, antipatterns, and concepts.
      source: https://aipatternbook.com
      retrieved: 2026-08-24
      volatility: >-
        The entry count moves; briefs/eacp-pattern-map.md recorded 295 articles
        on 2026-07-23. Re-check before republishing.
    - claim: The repository is public at github.com/wolfmcnally/agentic-coding-starter.
      source: git remote of this checkout
      retrieved: 2026-08-24

  open_questions:
    - >-
      Whether the artifact should ever be shared beyond the operator's own
      account. Separate publication decision under policies/treatise.md.
---

# The Project Remembers

*A primer on what this repository is for and how it works.*

**Wolf McNally** created Bartley Editions ([bartleyeditions.com](https://bartleyeditions.com)), which publishes living reference works: books kept current by an agent, the Bartley engine, under human curators, in place of a publishing house and a decades-long production cycle. One of those works is the Encyclopedia of Agentic Coding Patterns ([aipatternbook.com](https://aipatternbook.com)), a compendium of tested patterns for building software with AI agents, running to roughly 308 entries across patterns, antipatterns, and concepts (retrieved 2026-08-24). The two fit together: the engine is an agent that writes books, and the Encyclopedia is a book about directing agents.

He is the author and maintainer of this repository.

*Companion to [`BRIEF.md`](BRIEF.md), which describes the template's surface, and [`methodology.md`](methodology.md), which states the eleven steps. This brief is the canonical explanation; rendered formats derive from it, and corrections land here first, per [`../policies/treatise.md`](../policies/treatise.md).*

---

## What this is for

This repository collects, in one place, an evolving and deliberately opinionated set of best practices for building software with AI agents.

It is a working template. You copy it to start a project, and the practices arrive with it as files: rules the agent must respect, a plan it must follow, records it must keep. The opinions are not advice sitting in a document somewhere. They are the shape of the project itself.

Opinionated, because a set of practices that accommodates every preference decides nothing. Evolving, because the practices change as the work teaches, and the repository has machinery for that change, described further down.

## The claim underneath it

An AI coding agent will write you a plausible plan, a plausible implementation, and a plausible report saying it all worked. Whether any of that is true has less to do with the model than with what the project around it writes down.

So:

**An AI agent becomes reliable when the project holds the memory, the rules, and the evidence, so that every session starts from a written record and ends by updating it.**

Everything in the repository follows from that. The separated roles, the phase ledger, the two rounds of testing at the end of every phase, the small deterministic scripts, the file where mistakes accumulate: each one moves some piece of state out of the conversation and into a file, where it can be read, checked, and corrected.

## Three problems

Working with a coding agent surfaces the same three problems.

**Forgetting.** A session ends, or its memory fills up and gets compressed, and everything decided along the way goes with it. The next session has to be told again, and it will re-open questions that were settled last week, because nothing in front of it says they were settled.

**Circular grading.** The agent that wrote the plan is the one asked whether the plan is good. The agent that wrote the code reports that the code works. Nothing independent disagrees, and a confident wrong answer looks exactly like a correct one until somebody runs it.

**No accumulation.** The same mistake gets made and corrected on a two-week cycle. A lesson that does survive lives in one person's head, or in one tool's private memory on one laptop, neither of which reaches the next session.

Three problems, three answers. Write the state down. Have something other than the author do the checking. Collect the mistakes on purpose.

## Writing survives what talking loses

Every project built this way keeps a small set of files that outlive any conversation. A brief says what is being built and why. An architecture document says how. A plan breaks the work into phases and puts them in order. A log records what happened. A policies folder holds the rules every phase respects. This is the paperwork a careful team keeps anyway. What differs here is that the agent must read it before acting and update it before finishing.

Two rules keep the paperwork from rotting.

**A fact lives in exactly one place.** Whether a phase is finished, in progress, or next up is recorded in one file and nowhere else. Individual phase documents are forbidden from carrying their own status. Two places to look is one place to be wrong, and a project whose files disagree about what is done is worse off than one that wrote nothing down.

**The log only ever grows.** Each phase opens with an entry saying what is being attempted and closes with one recording what happened, what was checked, and what remains open. Old entries are never edited. A correction to something written last month is a new entry, so the record of the mistake survives next to the fix.

The effect: a new session reads the ledger and the last entry, then picks up. Nobody re-explains the project. When a long session runs out of room and its memory gets compressed, the compression takes the conversation and leaves the files, which is where the state was.

## Nothing is accepted on its author's word

Work on a phase passes through four specialists, each with a narrow job. A planner turns the phase into a file-by-file plan and writes no code. A plan reviewer approves that plan or sends it back. A coder implements the approved plan. A code critic reads the result and approves it or sends it back. A fifth participant, the orchestrator, moves work between them, keeps the records, and runs the tests.

| Role | Writes code | Job |
|---|---|---|
| Planner | No | Turn one phase into a file-by-file plan |
| Plan reviewer | No | Approve the plan or send it back |
| Coder | Yes | Implement the approved plan |
| Code critic | No | Approve the result or send it back |

No role reviews its own output. Round-trips between them are bounded: the loop continues while each pass shrinks the list of open problems, and stops for a human when the same complaint keeps returning, which means the fix is not reaching whatever generates the problem.

Every test result is stamped with a fingerprint of the exact version of the project it ran against. Change any relevant file and the old result stops counting, because it was evidence about a version that no longer exists.

This is why a phase ends with the full test suite running **twice**. The first run proves the code the critic approved. Then the orchestrator writes the closing paperwork: flip the status, append the log entry, file the lessons, generate the report. Those writes change the project. So the suite runs again against the version actually being handed over, and after that, nothing may be written at all.

> A test run that certified a version nobody will ever have is not a test run.

The same requirement applies to checks in general: a check earns trust only when it is able to report the failure it claims to guard against. The rules name the ways a check loses that ability. A pipe that hides the real error code. A failure swallowed and replaced by a default that reads as fine. A stand-in measurement that was never the thing anyone cared about. A check that passes because it found nothing at all. A survey that reports perfect uniformity because it was reading a field that cannot vary. In each case the instrument could only ever return one answer, so its answer carried no information.

### The line between what a machine can prove and what a person must judge

If the checking is this thorough, what is the human for?

Every acceptance criterion sorts into two kinds.

**Closes on evidence.** It can be run as a command, it was reviewed by someone other than its author, the full suite proved it against that exact version, and the result was recorded rather than asserted.

**Waits for a person.** Does this feel right to use. Is this the right feature at all. Does the audio sound clean, does the page look wrong. Anything needing a password or a credit card. And the phase's hands-on demo, until someone has actually tried it. The agent is forbidden from claiming any of these.

Criteria of the first kind close on the machinery's own evidence, and the orchestrator then delivers the phase itself, under tight constraints. It stages only the files the phase touched, never a blanket "add everything," because another session may be working in the same folder. It writes an ordinary factual message with no credit to any agent. It never bypasses the safety checks. It publishes only when there is exactly one unambiguous destination and the update is a clean fast-forward. Everything destructive stays with the person: no force, no rewriting history, no deleting branches, no choosing where the code goes.

Two properties bound that authority.

**Delivery does not mean acceptance, and it does not wait for it.** A phase whose checks are green gets delivered while its subjective criteria are still open, and those criteria stay open afterward exactly as they were. If the work turns out to be wrong, the correction is an ordinary follow-up, and nothing about having published it makes reversing it harder.

**What stops a phase is a failed check, never an open judgment.** A failed test, an unmet command-line criterion, or an unresolved decision blocks the phase. A pending human judgment does not.

The human's attention goes to the seam between phases: the closing entry and the hands-on demo. And the code critic blocks on a criterion filed under the wrong kind, since a judgment call dressed as an automated check would let a phase claim proof it does not have.

The trade is real in one direction: a phase can be delivered and then judged wrong, and the fix is a follow-up rather than an unpublished draft.

## Mistakes are collected, and a person decides which become rules

Every phase ends with a required question: what did this teach us that will apply again? "Nothing" is an acceptable answer. Skipping the question is not. Whatever comes back is filed as its own small document with a date, a description, and a count of how many times this has now happened.

A third occurrence does not make it a rule. A person promotes it, one at a time, onto a named surface: a policy, a brief, a role definition, a script, a test. The threshold exists because a lesson written into law on first sight is usually wrong in ways its next two occurrences would reveal. The human ratification exists because the obvious alternative, letting the agent rewrite its own instruction file with what it learned, degrades the document: each rewrite shortens it and sands off some of what made it specific, until a page of hard-won detail reads as generic advice that binds nothing.

Keeping the raw entries separate from the curated rules avoids that. The pile of entries grows. The rules are edited by hand, one at a time, and each traces back to the incidents that earned it.

The same structure runs between projects. This repository is a hub. One command stamps out a new project from it. Another pushes improvements to a project stamped from an older version. A third harvests back what those projects learned, along with any new defect exposed by the act of transferring, since applying a pattern somewhere new is a test of that pattern. The harvest direction carries weight for a specific reason: a working project exercises this machinery at a scale the template never does, so that is where defects surface first.

Two disciplines govern that traffic. A project being further ahead in general proves nothing about any particular file, so direction is established one item at a time. And before importing a fix, the problem it fixes has to be shown to exist here, since a repair for a defect the destination solved differently is a regression wearing the shape of an improvement.

## What it costs

It loses to a one-line prompt on anything small. Writing a brief, a plan, and a phase to change a script that gets thrown away next week is silly. Use the quick thing for the quick thing.

It gives up unattended autonomy at the end. Work that can be proved gets delivered without asking, but the process stops wherever a judgment is required, and silence from an absent human is never read as approval. A project that wants no human judgment anywhere wants a different method.

It gives up wandering mid-flight. Once a phase starts, the orchestrator follows the plan. Explore before it starts, or between phases.

And the enforcement is uneven in one area. Sixteen rules govern what happens when a long automated run hits trouble: when it may recover on its own, when it must stop and wait, how it proves its instruments before trusting them. Some of those rules are enforced by machinery. The rest are written guidance that the orchestrator and the human carry between them. The repository says which is which rather than leaving a reader to find out.

## Where to find it, and how to start

The repository is at [github.com/wolfmcnally/agentic-coding-starter](https://github.com/wolfmcnally/agentic-coding-starter). It works with Claude Code, with Codex CLI, and with any agent host that reads project instructions and agent definitions from the usual places. Clone it, then pick one of two ways in.

**Start a new project from it.** From inside the clone, invoke the `stamp` skill with a destination and a one-line description of what you want to build: `/stamp ~/path/to/new-project "..."` in Claude Code, `$stamp ~/path/to/new-project "..."` in Codex. It copies the structure, adapts the names and build commands, asks only what the description leaves open, and hands back a project ready to work on.

**Or work in the template itself.** Invoke `kickoff` (`/kickoff`, or `$kickoff`) and it picks up the first phase of the template's own plan and walks the entire loop, writing its records as it goes. This is the way to watch the method run before adopting it.

The host needs `uv` and nothing else. `./bin/setup` provisions the pinned environment, `./bin/test` runs the tests, and `./bin/check all` runs everything the method claims to run.

## Checking any of this

None of the above has to be taken on faith. From a copy of the project, one command runs every check the method claims to run: twelve categories, 572 tests, all passing as of 24 August 2026. Other commands verify that the rules are indexed, that no duplicated instruction file has drifted from its original, that the lessons ledger is well formed, and that no private path or outside project name has leaked into a public repository.

One check needs no command. Read a phase's closing entry, then read the change it delivered. The two should agree.

## Where this comes from

This brief derives from, and must stay consistent with:

- [`BRIEF.md`](BRIEF.md), the entry-point brief: what the template is, who it is for, the two ways it gets used, and what counts as done.
- [`methodology.md`](methodology.md), the eleven steps, the four roles, the runtime doctrine, and the vocabulary for how runs end.
- [`harness-self-improvement.md`](harness-self-improvement.md), the two-tier improvement loop, its grounding, and what was deliberately declined.
- [`incremental-orchestration.md`](incremental-orchestration.md), the evidence machinery as implemented.
- [`eacp-pattern-map.md`](eacp-pattern-map.md), this repository mapped onto named patterns from the Encyclopedia of Agentic Coding Patterns, including the patterns it declines and the failure modes it guards against.
- The `policies/` folder, which owns every prescriptive claim above.

Corrections land here and in the owning source, then regenerate outward. A rendered version that disagrees with this brief is out of date, not authoritative.
