---
title: "Multi-Operator Collaboration"
date: 2026-10-29
status: draft
scope: How several operators could share one methodology project without serializing on a single writer — conflict-free repository layout over git, collision-free phase identity, and what still needs coordination.
---

# Multi-Operator Collaboration

The methodology as it stands assumes one operator directing agents against one checkout, with one line of delivery to the default branch. This brief works out what changes when several people collaborate on the same derived project, each running their own sessions. The operational migration design and isolated tools below are commissioned work; the proposed live structure is not adopted. Existing project authority remains in force until a separately qualified cutover replaces all affected readers and writers atomically.

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

The core structure is **a grow-only set of immutable event files, with everything else derived from it**. Independent additions under disjoint flat file names remove the usual append conflict; file/directory collisions, divergent metadata and semantic invariants can still conflict. Two branches that add the *same* path with different content produce an add/add conflict that git always reports (verified 2026-10-26), so an identity collision is surfaced rather than silently resolved.

- **Activity log.** One file per entry, ordered by timestamp with a unique id as tiebreak rather than by position. The single log file becomes a generated view. Chronology checks then apply per writer: wall clocks on different machines disagree, so a global position-order check becomes a check that each writer's own entries are monotonic, or entries carry a hybrid logical clock.
- **Phase status.** One event file per transition ("phase X claimed by owner Y", "phase X completed"). Status is a predecessor-bound fold over those events, and the index becomes discovery/context with an uncommitted status projection. Competing successors are reported as a fork; taking the furthest state would hide contradictory claims, withdrawn selections or incomplete acceptance.
- **User actions and lessons.** Unchanged; archiving an entry already acts as its removal marker.
- **Prose stays prose.** Phase bodies, briefs and policies keep git's ordinary three-way merge with a human resolving conflicts. A character-level CRDT merge of two people's edits to the same acceptance criteria converges, but to text that may no longer say anything coherent. Only metadata is made conflict-free.

The index retains hand-written context. For the implemented rehearsal format, status and combined log views are generated under ignored `.collaboration-views/`; they are never the shared source of truth or committed merge inputs. Validation detects stale views with a read-only check. No custom merge driver or global Git configuration is needed.

## 4. Phase identity separated from execution order

Today a phase's number is both its name and its position. Under concurrency those have to be separated.

```yaml
---
id: amber-river-heron          # permanent; what dependencies, log entries and commits cite
title: "Add export API"
order: "3/2"             # exact rational sort key; controls display/order only
parent: null             # a child names its parent instead of being numbered "3.1"
depends_on: [quiet-forest-falcon]
---
```

The file is `plan/phases/amber-river-heron.md`. Ownership has one home in phase events; it is not duplicated in frontmatter. The generated index may still show "#3 amber-river-heron" so people have a short handle; that number is display only and is never cited.

**Identity options weighed:**

- **Random memorable slug (preferred).** The same generator the ledgers already use. Slugs are short, speakable, and readable aloud by speech synthesis. The generator's uniqueness check sees only the local checkout, so across branches uniqueness is probabilistic — but a collision surfaces as the add/add conflict above. Three-word slugs make it rare enough to ignore.
- **Owner-qualified counter** (`alice-7`). Locally allocated without a shared counter, but bakes a person into a permanent name that reads wrong after a handoff.
- **ULID or UUID.** Probabilistically unique, and time-sortable for ULID, but opaque: nobody can say or remember one, and long identifiers are noise in spoken output.
- **Central allocator.** Hands out 1, 2, 3 under a lease. This reintroduces exactly the coordination the change exists to remove.

**Order** in the rehearsal uses exact rational strings and sorts by `(rational value, permanent id)`. Between `1` and `2`, use `3/2`; no float rounding or rename is involved. This is a small stdlib-based dense ordering choice, not an implementation of a vendor's fractional-string algorithm. Equal keys have a deterministic id tiebreak, but dependency checks use that same total order and may reject the result. A reorder edits one phase's order key and validates the complete graph; it does not renumber identities.

**Children** get their own slug and a `parent:` field. A counter scoped to the parent would still collide when two people add children to the same phase.

Identity becomes permanent and order becomes freely editable — the inverse of the pre-migration arrangement, where order is fixed by the name and the name changes on reorder.

## 5. What conflict-free layout does not provide

A CRDT guarantees that replicas converge. It does not guarantee that the converged state is valid.

- **Exclusive claims are coordination, not convergence.** Two operators both starting the same phase merge cleanly into a wrong state. Taking a phase needs a lease — a short-lived lock from a service all operators can reach, or a claim that a central branch accepts first-come — not a merge rule. Once the claim is settled, the resulting event file merges conflict-free like any other.
- **Project-wide invariants need a post-merge check.** No dependency cycles; no phase started before its dependencies complete; no phase sorted ahead of something it depends on; at most one active owner per phase; no duplicate ids. Each of these is checkable after every merge and, when violated, is surfaced to a human — the layout analogue of a multi-value register that keeps both conflicting values for review instead of silently picking one.
- **Code still conflicts.** Making the plan and the log conflict-free removes the bookkeeping merges, not the product ones.

## 6. Delivery

Fast-forward push to one default branch serializes every operator behind every other. Two directions are open, and the choice is the operator's:

- **Branches and pull requests.** Each operator delivers to a branch; integration happens through review. This matches ordinary multi-person practice and keeps the human in charge of every merge, at the cost of a second integration step after the phase gate.
- **Narrow rebase authority for agents.** Once project-record files cannot conflict, rebasing a delivery whose only divergence is in those files becomes mechanical. Granting agents rebase authority for that case alone — with the full gate rerun on the rebased tree and any product-file divergence still parking for the human — would keep linear delivery without serializing operators.

## 7. Research outcome and operational handoff

The isolated implementation separates stable phase identity from order, reconstructs historical log bytes without assigning invented authorship, and represents concurrent ownership successors as conflicts rather than silently choosing a winner. Its maintenance commands exercise the proposed new records. The rehearsal supports these structural claims; it is not evidence that live execution, acceptance, session loading or multi-operator delivery has been adopted. Active consumed review history still has identity-continuity consequences, and existing shared workflow callers need a coherent eventual cutover.

The single authoritative [migration runbook](../policies/multi-operator-migration.md#0-unified-migration-runbook) owns preflight, conversion, retirement, constitutional requirements, Teach/Learn entrypoints, acceptance and Git rollback. This operator-directed procedural handoff is navigation to the adopted operational rule, not evidence for the research above. No procedure is duplicated here. Actual adoption and session-loading evidence belong to the receiving owner’s scoped delivery record, separately from these research claims.

## Sources

- Evan Wallace, [Realtime editing of ordered sequences](https://www.figma.com/blog/realtime-editing-of-ordered-sequences/). As of 2017-03-06; retrieved 2026-10-29 UTC. Supports the distinction between list identity, order and coordination. The implementation here uses Python exact rationals rather than that article's fractional-string implementation. External text is not redistributed; site republication terms were not established.
- [Git log documentation](https://git-scm.com/docs/git-log), edition2.56.0. As of 2026-09-28; retrieved 2026-10-29 UTC. Git history and rename-aware inspection support provenance; a content rewrite is not made harmless by calling it a rename. The migration itself invokes only read-only `rev-parse` and `archive`; it has no rollback Git mutator.
- Current Starter source, observed 2026-10-29 UTC: one numbered adoption placeholder, the actual append-only historical log, root wrappers and the recorded caller inventory. These are the rehearsal inputs and enforcement evidence, rather than assumptions that all derived projects have the same shape. No third-party code or document body is copied into the implementation.

- [Claude Code stable release 2.1.290](https://github.com/anthropics/claude-code/releases/tag/v2.1.290), as of 2026-10-05; retrieved 2026-10-29 UTC. Selected fixed-release minimum for AGENTS-primary migration. [Native AGENTS loading rules](https://code.claude.com/docs/en/memory#agentsmd), retrieved 2026-10-29 UTC; a living configuration reference, not proof that a particular session loaded its instructions.


## Existing-product transfer boundary

As of 2026-11-07, capability learning, canonical-history conversion and first methodology retrofit have different evidence inputs. Existing numbered prose plans are historical documents, not lifecycle events. An isolated retrofit can retain their exact preimages while starting prospective records without importing accepted work. The committed source and explicit receiving constitution bind that rehearsal; its success does not establish live custody, complete caller adoption or runtime loading. Teach from the source and learn from the receiver describe the same transformation in both directions, with the source read-only and one concrete receiving-plan approval. Non-template capability sources need evidence for their selected capability rather than unrelated lifecycle scaffolding.
