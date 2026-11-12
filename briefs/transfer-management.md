---
title: Agentic management of knowledge transfer between methodology repositories
date: 2026-11-11
status: draft
scope: Work out how a retained agent in the template repository manages releases, teaching, learning and the project registry across many receiving repositories, from what the first managed batches showed.
---

# Agentic management of knowledge transfer between methodology repositories

## Purpose and present scope

The template repository is a hub. Improvements are made or learned there, released, and taught outward to projects that use the methodology; projects in turn hold lessons and local inventions the hub should learn. Until now each transfer was a single event that a person started. This draft works out the standing arrangement instead: one retained agent in the hub that keeps track of every project's state, proposes and carries out transfers when a project can receive one, brings back what each transfer finds, and turns that into the next release.

It records procedures as they are being developed, with the operator's directions quoted and dated. It is a draft. Where practice has been tried once, it says so. The procedures of a single transfer belong to the `teach` and `learn` skills; this brief is about managing many of them.

As of 2026-11-11 the evidence is two batches on one day: four projects taught one release by four parallel workers, and three transfers of the next release that evening, two small follow-ups and one full catch-up of a project stamped before the first release. All seven were delivered. Four of the seven parked once on the way and were finished after a ruling or a diagnosed second run.

## Roles

- **The operator** owns the hub and the projects, sets direction, and keeps the decisions that change what a project is.
- **The hub primary** is a retained agent session in the template repository. It owns the hub's releases, the registry, the readiness picture, and the conduct of each transfer, whether it performs the transfer or hands it to a worker.
- **A coordinator**, where the operator uses one, relays direction, knows which projects other agents are working in, and reviews routine transfer plans within the operator's instruction.
- **A project's owner session**, when one is working, has custody of that checkout. A transfer never competes with it.
- **A transfer worker** is an agent that performs exactly one transfer into exactly one project and reports.

## The registry

A machine-wide registry lists every project that uses the methodology. It is the hub primary's working memory across sessions, and it is only useful if it is true.

Each entry records whether the project is active (real work in the last month; a housekeeping commit does not count), its layout, and its last synchronization with the template: the date, whether it was a stamp, a teach or a learn, and the template release when the project records one. A project that predates the first release says so. A project that is worked on but does not carry the methodology is listed as such, because a transfer there would be a first adoption.

The operator's direction, 2026-11-11: the file must be kept "synchronized to the state of our projects." The rule adopted is that an entry is updated in the same piece of work that changes the project's state, and that a registry disagreeing with a checkout is a defect to correct on sight. A small report command prints the registry joined with what each checkout says, including each project's newest tagged release, and lists disagreements. An applied but undelivered transfer shows up there as a disagreement, which is correct: the registry records delivered state.

## Readiness

Before proposing transfers, the hub primary takes a read-only snapshot of every active project and sorts each into one class. The classes observed so far:

| Class | What it means | What a transfer needs |
|---|---|---|
| Ready | Clean, level with its remote, no phase in progress, no agent working in it | A plan and its approval |
| Phase open | Clean, but a phase is in progress or claimed | The phase owner's word or the operator's ruling, each time |
| Actively worked | Clean at the sample, but an agent or build is running there | Wait, or the owner's word |
| Dirty | Uncommitted work | Wait; never stash or work around it |
| Held | Another party has asked that it be left alone | Wait for the hold to lift |
| No methodology | Carries none of it | An operator decision; this is adoption, not maintenance |

A snapshot is a lead, not clearance. The same checks run again immediately before the first write.

A transfer into a project with an open phase replaces the tools that phase's runs are pinned to. It can be done, by ruling, and it leaves that phase's owner a duty to re-pin before resuming, recorded where the owner will find it. A ruling covers one transfer; the next needs it again.

## The lifecycle of one managed transfer

1. **Assess, read-only.** Route check, then the ancestry report against the release being taught. Read the source at the release tag, never at its working tree: the hub may be building its next release while a batch is in flight.
2. **Plan.** A concrete plan per project: what is taken as released, what is merged, what the project keeps, what is not transferred, and the decisions that need someone else. The plan also names the records the project's own rules require of a transfer. Two projects required a scope record before implementation, the plans omitted it, and both wrote it late and said so.
3. **Approve.** See the next section.
4. **Apply.** For anything beyond a small change, build and prove the whole change in a private copy and write the project once. Each edited file is merged on the revision it actually descends from, then audited both ways.
5. **Admit proofs** with the supported commands, replaying the defects the release records.
6. **Record provenance** in the project, and confirm the route check reads it.
7. **Gate, commit, push**, reading the gate's result before anything else.
8. **Verify independently.** The hub primary checks the remote tip, the tree, the record and the commit itself, whatever the worker reported.
9. **Record** the transfer in the registry, and carry what was found back to the hub.

The operator's definition, 2026-11-11: "A successful teach is not a new release, just a commit and push."

## Approval and delegation

A transfer plan is approved before any write. Who approves has moved as the arrangement matured, and each step was an explicit direction, not an inference:

- At first the operator approved every plan.
- For a named batch, the operator let the hub primary approve its workers' plans: "If any of these background workers needs approval they can ask you for it." That covered the batch and nothing after it.
- For the standing arrangement, the operator named the hub primary "the authorized retained worker" doing transfers "to various projects opportunistically," with the coordinator helping "find active projects that are clean and ready." The coordinator then reviews routine plans within that instruction.

Some decisions stay with the operator however routine the transfer looks: a first adoption, graduating a project from the minimal form of the methodology, proceeding alongside an open phase, anything that selects a trusted external tool, and anything that tags or releases.

A delegation is read narrowly. When it is unclear whether a decision falls inside it, the hub primary says what it decided and why, so the operator can object.

## Parallelism

The operator's direction, 2026-11-11: "parallelize wherever possible without a concurrency explosion. The development computer is beefy and we're not stressing it. Wall clock time matters more than conservation of CPU, memory, or disk."

In practice: one worker per project, projects in parallel, gates included. Assessment, application and gates for separate projects share nothing, so nothing needs to wait.

This replaced a rule the hub primary had invented the same day. Two gates failed while four ran together, and it concluded that gates must run one at a time on a quiet machine and began writing that into policy. The operator asked for the rule's source and there was none. The failures were two fragile tests, since fixed in a release. The lesson kept from it: a test that fails only under load is a defect in the test, and slowing the work down hides it.

## Releases are the unit

What travels is a release, never the hub's working tree. A project records the release it holds, so "what does this project lack" is a list of releases with their named transfers.

A batch produces findings, the findings become a small release, and the release becomes a round of follow-up transfers. On the first day, teaching one release to four projects exposed three faults in the hub's own test setup; the fix shipped as the next release that evening and its follow-up transfers began at once. The cycle is the intended shape, and it means a project is often one small release behind the moment it finishes. That is normal.

## What comes back

Every transfer is also a probe of the hub. Workers are asked to report what surprised them, and the first batch returned, among others: fixtures that inherited the machine's commit signing; clocks too short for a busy machine; a dependency range that let a project resolve a version that broke parallel test isolation; a bookkeeping command that could not record a retirement while catching a project up; a proof with no recorded defect; three limits of the ancestry report; and a project's gate that depended on an external tool nobody had recorded.

The second batch returned three more that concern how a project's tests meet the arriving parallel runner. A project that gives each test worker a private cache needs each worker's cache prepared whenever any test starts tools together; the hub primary recommended leaving that out, and the first full run failed on it. A product suite in another language, especially one that launches browsers, should run through the project's own runner as a supervised family outside the worker pool from the start, with a full run recorded as proven only after both lanes pass; one project's first parallel run failed inside the pool, and one run could not say whether load, scheduling or the product was the cause. And a project catching up across many releases has no supported command to declare arriving proofs, so two workers edited the proof list by hand.

Each either becomes a change in the next release, a candidate lesson for the operator, or a candidate for a `learn` pass in the other direction. Projects also hold unharvested lessons of their own, which the transfer lists and does not act on.

## Working with workers

- **Workers are reached through the shared messaging system wherever possible.** The operator's direction, 2026-11-11: the team of agents is both the primary user of that system and its testing team, so managed transfers should exercise it. The exception in force on that date was temporary: while a fault that refused delivery to sessions whose turns had ended was being repaired, transfers ran under sub-agents of the hub session instead, and return to the messaging system once the repair lands. Faults met while using it are reported to its owner with exact evidence; that is part of the job, not a detour from it.
- **Use the messaging system's agent tools, not a side door.** Where its agent tools support an operation, they are how an agent uses it, even when the service documents an equivalent raw interface. The operator's correction, 2026-11-11: using a raw HTTP client "when it had access to its MCP tools" was a bad assumption. The hub primary had done so to trim verbose replies, and that side path is also where it drifted into reasoning from the service's internals. A tool that returns too much is a finding to report to its owner.
- **A worker's brief is complete.** It carries the plan, the rulings already made, the rules that bind, and what to report. A complete brief avoids round trips; it is not a reason to avoid them. A worker that needs a ruling asks and ends its turn, and the answer is sent to the same session.
- **A finished session can be woken.** A session that still exists is addressable after its turn ends, and an operation that needs it active revives it. The operator's correction, 2026-11-11, after the hub primary concluded otherwise: it "made a bad assumption that finished sessions could not be woken, and took as evidence the fact that it got the error we're trying to fix." A refusal to deliver is a fault to report. It is never evidence about what the system is meant to do, and it is not a reason to replace a worker that holds the context of its work.
- **Accepted is not delivered, and delivered is not done.** After sending an instruction that work depends on, read its delivery state before saying anything about progress. On the first day, instructions to four workers were accepted by the messaging system and never delivered, and progress was reported for five hours on work that had not started.
- **Report a refusal as the system gave it.** The same incident produced a confident explanation of how the messaging system behaves that had not been read anywhere and was wrong, built on the refusal itself. Why another system refused belongs to that system's owner.
- **Stale instructions are withdrawn.** Once replacement work is done, undelivered instructions to do it are dangerous: a repaired delivery path would run them. They are withdrawn through the supported operation, each checked before and after.
- **Evidence, not repair, in someone else's system.** When a transfer exposes a fault in a tool the hub does not own, the hub primary supplies exact evidence to that tool's owner and writes no source there.

## Open questions

- **Product prerequisites and the first parallel run.** One transfer was fully applied before its gate revealed it needed an external tool the operator had to choose, and two more parked on how the project's own tests behaved under the arriving runner. Assessment should find what a project's gate needs from outside its tree and how its product suite will run, before anything is applied. How, in general, is not settled.
- **A parked transfer leaves the project dirty.** Each park left a fully applied, uncommitted change in the project's working tree until a ruling came, in one case for hours. Building in a private copy until the gate has passed there would avoid that; it was done for the large transfer and not for the small ones.
- **Recording outside selections.** Gate receipts record the language runtime and nothing else a gate depended on. Whether they should is a candidate lesson.
- **Legacy layouts.** Most active projects are still on the earlier layout, and each needs a larger migration transfer. Whether to batch those, and in what order, is undecided.
- **Learning inward at the same scale.** Everything above is teaching. Projects hold dozens of unharvested lessons and several local inventions. A managed `learn` cycle has not been run.
- **How far routine approval extends.** The coordinator reviews routine plans today. What makes a plan routine is still judged case by case.
- **Following up small releases.** Whether every small release is taught at once to every project, or allowed to accumulate, is not decided.
