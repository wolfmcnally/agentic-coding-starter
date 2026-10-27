---
title: "Multi-Operator Collaboration"
date: 2026-10-26
status: draft
scope: How several operators could share one methodology project without serializing on a single writer — conflict-free repository layout over git, collision-free phase identity, and what still needs coordination.
---

# Multi-Operator Collaboration

The methodology as it stands assumes one operator directing agents against one checkout, with one line of delivery to the default branch. This brief works out what changes when several people collaborate on the same derived project, each running their own sessions. It is thinking, not a decision: nothing here is adopted until a policy and a phase say so.

## 1. Where the methodology assumes a single writer

- **Phase status.** The plan index is the only home of status, and it allows at most one "next" marker across the whole project. Two operators cannot each have their own next phase, and every status transition is an edit to the same table.
- **Phase numbering.** Unstarted phase numbers follow execution order, and inserting a phase renumbers everything after it. Two people inserting phases concurrently both renumber the same files.
- **The activity log.** Every writer appends at the end of one file, and the log's chronology is checked by position. Two branches that each append an entry conflict on every merge.
- **Delivery.** Gate-proved work is fast-forward pushed to the default branch, and a rejected push or divergence parks delivery for the human, who alone may rebase. With several writers, every push race parks.
- **Already safe.** The lessons and user-action ledgers are one file per entry with generated slug names. Two branches adding different entries merge cleanly, so these already behave the way the rest of this brief proposes.

## 2. Per-operator plan directories are the wrong split

The first idea considered was to give each operator a private plan directory (`plan-<username>/`) and share everything else. It fixes the status and numbering collisions, but at a worse cost:

- **The dependency graph fractures.** Phases depend on each other across people. Dependency ids would need operator qualification, and no single place would show the whole sequence.
- **Ripple goes blind.** When a completed phase changes, the change is propagated to the phases that depend on it. That propagation cannot see across private plans.
- **Conflict moves somewhere worse.** Two operators' plans colliding in the shared index is a cheap, visible textual conflict. Two private plans touching the same code collide only at integration, where the conflict is semantic and expensive.
- **The index's project-wide sections** — cross-cutting concerns and the critical-files map — would either be duplicated and drift, or stay shared and keep the hotspot.
- **People are the wrong axis.** A plan describes the product. Operators hand work off, pair, and leave; if ownership is a directory, a handoff is a file move that breaks links and history. Ownership is an attribute of a phase.

If a project genuinely has independent tracks, splitting the plan by **workstream** (`plan/<track>/`) under one shared index is defensible. Splitting by person is not.

## 3. Conflict-freedom by layout, with git as the merge layer

Several of these artifacts want the property of a conflict-free replicated data type (CRDT): concurrent edits always merge to the same result without human help. The position here is to get that property from **how files are laid out**, not from a CRDT library such as Automerge or Yjs. Git already replicates state between operators; a library would replace readable Markdown with an opaque binary document that agents and reviewers cannot read directly.

The core structure is **a grow-only set of immutable event files, with everything else derived from it**. Two branches that each add *different* new files always merge cleanly. Two branches that add the *same* path with different content produce an add/add conflict that git always reports (verified 2026-10-26), so an identity collision is surfaced rather than silently resolved.

- **Activity log.** One file per entry, ordered by timestamp with a unique id as tiebreak rather than by position. The single log file becomes a generated view. Chronology checks then apply per writer: wall clocks on different machines disagree, so a global position-order check becomes a check that each writer's own entries are monotonic, or entries carry a hybrid logical clock.
- **Phase status.** One event file per transition ("phase X claimed by owner Y", "phase X completed"). Status is a fold over those events, and the index's status column becomes a projection. The status sequence not started → next → in progress → completed is naturally monotonic, so concurrent events resolve by taking the furthest state — with the exceptions in § 5.
- **User actions and lessons.** Unchanged; archiving an entry already acts as its removal marker.
- **Prose stays prose.** Phase bodies, briefs and policies keep git's ordinary three-way merge with a human resolving conflicts. A character-level CRDT merge of two people's edits to the same acceptance criteria converges, but to text that may no longer say anything coherent. Only metadata is made conflict-free.

The index keeps its hand-written sections (cross-cutting concerns, critical files) and gains a generated table. Whether the generated part is committed and regenerated by a check, or produced on demand and never committed, is an open choice; committing it brings back a merge hotspot unless a merge driver regenerates it.

## 4. Phase identity separated from execution order

Today a phase's number is both its name and its position. Under concurrency those have to be separated.

```yaml
---
id: amber-heron          # permanent; what dependencies, log entries and commits cite
title: "Add export API"
order: "m"               # fractional sort key; controls execution order only
parent: null             # a child names its parent instead of being numbered "3.1"
owner: alice
depends_on: [quiet-falcon]
---
```

The file is `plan/amber-heron.md`. The generated index may still show "#3 amber-heron" so people have a short handle; that number is display only and is never cited.

**Identity options weighed:**

- **Random memorable slug (preferred).** The same generator the ledgers already use. Slugs are short, speakable, and readable aloud by speech synthesis. The generator's uniqueness check sees only the local checkout, so across branches uniqueness is probabilistic — but a collision surfaces as the add/add conflict above. Three-word slugs make it rare enough to ignore.
- **Owner-qualified counter** (`alice-7`). Guaranteed unique without coordination, but bakes a person into a permanent name that reads wrong after a handoff.
- **ULID or UUID.** Guaranteed unique and time-sortable, but opaque: nobody can say or remember one, and long identifiers are noise in spoken output.
- **Central allocator.** Hands out 1, 2, 3 under a lease. This reintroduces exactly the coordination the change exists to remove.

**Order** uses fractional indexing, the standard CRDT technique for user-ordered lists: to place a phase between keys `m` and `n`, give it `mm`. No other file changes, so phase renumbering disappears as an operation. Two people inserting at the same point get distinct keys, or equal keys that the id tiebreak settles; either way the result is a valid order that someone may later adjust, never a conflict.

**Children** get their own slug and a `parent:` field. A counter scoped to the parent would still collide when two people add children to the same phase.

Identity becomes permanent and order becomes freely editable — the inverse of the current arrangement, where order is fixed by the name and the name changes on reorder.

## 5. What conflict-free layout does not provide

A CRDT guarantees that replicas converge. It does not guarantee that the converged state is valid.

- **Exclusive claims are coordination, not convergence.** Two operators both starting the same phase merge cleanly into a wrong state. Taking a phase needs a lease — a short-lived lock from a service all operators can reach, or a claim that a central branch accepts first-come — not a merge rule. Once the claim is settled, the resulting event file merges conflict-free like any other.
- **Project-wide invariants need a post-merge check.** No dependency cycles; no phase started before its dependencies complete; no phase sorted ahead of something it depends on; at most one active owner per phase; no duplicate ids. Each of these is checkable after every merge and, when violated, is surfaced to a human — the layout analogue of a multi-value register that keeps both conflicting values for review instead of silently picking one.
- **Code still conflicts.** Making the plan and the log conflict-free removes the bookkeeping merges, not the product ones.

## 6. Delivery

Fast-forward push to one default branch serializes every operator behind every other. Two directions are open, and the choice is the operator's:

- **Branches and pull requests.** Each operator delivers to a branch; integration happens through review. This matches ordinary multi-person practice and keeps the human in charge of every merge, at the cost of a second integration step after the phase gate.
- **Narrow rebase authority for agents.** Once project-record files cannot conflict, rebasing a delivery whose only divergence is in those files becomes mechanical. Granting agents rebase authority for that case alone — with the full gate rerun on the rebased tree and any product-file divergence still parking for the human — would keep linear delivery without serializing operators.

## 7. Open questions

- Whether the generated index and log views are committed, and if so how they merge.
- Which lease mechanism a derived project can rely on without assuming any particular service.
- How per-operator "next" selection interacts with the dependency graph when one operator's next phase waits on another's.
- How execution traces and evidence storage, which are currently per-checkout, identify the operator who produced them.
- Adoption follows the no-backward-compatibility rule: the change replaces numbered phases, the single log file and positional chronology outright, with every tool, check and fixture updated in the same phase.

## Sources

Cited from prior knowledge; not retrieved this session.

- Shapiro, Preguiça, Baquero, Zawirski, "Conflict-free Replicated Data Types", SSS 2011 — convergence guarantees, grow-only sets, multi-value registers.
- Kulkarni, Demirbas, et al., "Logical Physical Clocks and Consistent Snapshots in Globally Distributed Databases", 2014 — hybrid logical clocks.
- Evan Wallace, "Realtime Editing of Ordered Sequences", Figma engineering blog, 2017 — fractional indexing for user-ordered lists.
- ULID specification (github.com/ulid/spec) — sortable unique identifiers.
