---
title: "Structure as the Substrate: How This Template Makes Agentic Coding Reviewable"
date: 2026-08-24
status: implemented
scope: Canonical outward explanation of this repository — its thesis, governing principles, architecture, workflows, and skills — for practitioners and engineering leads evaluating or adopting the methodology. Source of truth for every derivative rendering.
---

# Structure as the Substrate

**Author and maintainer: Wolf McNally.**

*Audience: practitioners and engineering leads who already use coding agents seriously, and who have noticed that the failures are not about model capability. Companion to [`BRIEF.md`](BRIEF.md) (what the template is) and [`methodology.md`](methodology.md) (the eleven steps). This brief is the canonical explanation; rendered formats derive from it and corrections land here first, per [`../policies/treatise.md`](../policies/treatise.md).*

---

## 1. Thesis

Agentic coding fails for structural reasons, not cognitive ones. A capable model produces a plan nobody reviewed, code nobody checked, and a workspace whose state cannot be reconstructed from its files — not because it reasoned badly, but because nothing in the environment required otherwise.

This repository's claim is narrow and testable: **put the load-bearing state outside the session — the brief (*what*), the architecture (*how*), the plan (*in what order*), the log (*what actually happened*), the policies (*what is off-limits*), and the lessons ledger (*what this keeps re-teaching us*) — and the quality problem changes shape.** It stops being a prompting problem and becomes an engineering problem: reviewable, testable, and improvable by ordinary means.

Everything else here is consequence. The four agent roles, the phase ledger, the candidate-bound evidence, the two close gates, the deterministic scripts, the improvement flywheel — each exists because externalized state made a specific failure mode visible and fixable.

## 2. The problem, stated precisely

Three failures recur in unstructured agentic work, and they compound:

**State lives in the conversation.** The next session — or the same session after a context compaction — cannot recover what was decided, why, or what was already tried. Re-explaining is not merely expensive; it silently re-litigates settled decisions.

**Verification is self-referential.** The agent that wrote the plan assesses the plan. The agent that wrote the code reports the code works. Nothing structurally independent contradicts it, and a confident wrong answer is indistinguishable from a correct one at the point of delivery.

**Nothing accumulates.** The same mistake is made and corrected weekly. Any learning that does survive lives in one operator's memory, one harness's memory store, or one machine — none of which binds the next session.

The methodology addresses each: externalized state for the first, role separation plus candidate-bound evidence for the second, and a lessons ledger with human-ratified graduation for the third.

## 3. Governing principles

Six principles generate nearly every rule in the repository.

### Rules, not memory

Anything that should bind future sessions belongs in the repository, routed by kind: a universal rule to `policies/` or `CLAUDE.md`; a per-action workflow to the owning skill; a tunable to the policy that holds its tunables; longitudinal context or a pinned decision to a brief. Agent-side memory is local to one operator, one harness, one machine — the wrong place for engine knowledge. When a harness offers to remember something, the answer is to write a repo rule instead.

The corollary matters as much: when a learning is real but its surface is unknown, or it has been seen only once and codifying now would lock in a rule its variations have not tested, it goes to `lessons/` — the holding pen between noticing and knowing.

### Briefs describe, policies prescribe, the plan sequences

Three document classes with disjoint jobs ([`../policies/briefs-and-policies.md`](../policies/briefs-and-policies.md)). A brief explains what and why and stays authoritative for cross-session reasoning. A policy is a short prescriptive rule every phase honors — a policy violation blocks acceptance. The plan orders the work. When the plan and a brief disagree, the plan wins; when two briefs disagree, the briefs get fixed.

The discipline this enforces is against the most common documentation failure in agentic repos: a single swelling instruction file that means everything and binds nothing.

### Two kinds of work, triaged consciously

Half the work in any real engine is mechanical — exact, repeatable, judgment-free — and belongs in deterministic code, not in a model ([`../policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md)). Reconcilers, parity audits, leak scans, index generators, format checks: a script does these cheaper, exactly, idempotently, unit-testably, and byte-identically across harnesses. A model asked to do them will sometimes get them subtly wrong.

The inverse error is equally real: a brittle script faking judgment with keyword heuristics fails silently and confidently, which is worse than an agent. Mixed tasks split at the seam — **the agent decides *what*, a deterministic script does the mechanical *how*.**

### Assurance is candidate-bound

A green result proves only the exact working tree it exercised. So review, findings, revision packets, and gates all name the specific complete candidate they describe — tracked content, deletions, modes, symlink targets, and non-ignored untracked files, hashed by `bin/kickoff-tree-id` ([`../policies/orchestration-evidence.md`](../policies/orchestration-evidence.md)). A relevant change to the tree invalidates prior evidence rather than quietly inheriting it.

This is the structural answer to "the tests passed" meaning nothing. It also produces one of the repository's stranger-looking rules — verification captures go to a scratch path, never a bare filename — because a stray screenshot in the tree moves the candidate id that a phase's whole evidence chain is bound to.

### A check must be able to fail

An instrument earns trust only if it can report the failure it claims to guard against ([`../policies/acceptance-empirical.md`](../policies/acceptance-empirical.md)). The policy enumerates the ways instruments lose that property: a pipe that masks the real exit status; a swallowed failure defaulting to success; a proxy standing in for the real assertion; a wrapper that prints FAIL and exits zero. Then the subtler three — a check that passes on an empty result, a survey reporting perfect uniformity, and their unifying form: **the instrument could return only one answer, so its answer carried no information.**

### Lessons compound, and rules are curated

Every phase close asks what generalizable process lesson was learned; "none" is a permitted recorded answer, but the question is mandatory. Lessons file as discrete addressable entries with provenance and occurrence counters. **Graduation into a rule is the human's act, never the agent's**, and needs three occurrences or explicit approval ([`../policies/lessons.md`](../policies/lessons.md)).

Three is the stabilization threshold: a lesson codified on first sight tends to be wrong in ways its variations would have revealed. And the naive alternative — "agent, update the instruction file with what you learned" — degrades under iteration, each rewrite shortening and blanding the document until accumulated knowledge collapses into generic filler. The ledger grows; the rules are curated.

## 4. Architecture

The repository is a harness: skills, agent definitions, policies, briefs, and deterministic scripts wrapped around whichever coding-agent CLI hosts the session.

**Externalized state** lives in five surfaces. `briefs/` is the durable design library. `policies/` is the law — 28 files, each a rule every phase honors. `plan/` holds the phase ledger, with `plan/INDEX.md` as the single source of truth for phase status; per-phase frontmatter never carries a `status` field, because two places to look is one place to be wrong. `LOG.md` is the append-only record, owned by the orchestrator, never hand-edited. `lessons/` and its archive hold candidate process lessons and the permanent trail linking every rule to the incidents that earned it.

**The mechanistic half** lives in `bin/` — 20 executables that own everything exact: the atomic toolchain contract (`setup`, `test`, `check`, `python`), candidate identity (`kickoff-tree-id`), the evidence manager (`kickoff-evidence`), configuration with validation and preflight (`kickoff-config`), execution telemetry, durable full-gate receipts, and the deterministic checkers for catalog drift, harness parity, caller policy, shell syntax, and external-reference leaks. These are tested like product code: 18 test modules, 572 assertions as of 2026-08-24.

**The intelligence half** lives in `.claude/skills/` (9 skills) and `.claude/agents/` (the four canonical roles). Harness-specific surfaces — `.codex/agents/*.toml`, `.agents/skills/`, `AGENTS.md` — are thin pointers to the canonical files, and `bin/check-harness-parity` rejects missing, copied, or orphaned mirrors. One home per fact; mirrors that drift fail the gate.

**Isolation.** When a repo has one primary deliverable it lives under `project/`, referencing nothing above it, which keeps it submodule-ready and keeps methodology machinery out of the shipped artifact.

## 5. The workflow

`kickoff` orchestrates one phase end-to-end, delegating to four specialists whose names are load-bearing because the orchestrator invokes them by name.

| Role | Writes code | Job |
|---|---|---|
| `phase-planner` | No | Turn one phase into a file-level implementation plan |
| `plan-reviewer` | No | Approve the plan or send it back |
| `phase-coder` | Yes | Implement the approved plan; run focused and revision-close gates |
| `code-critic` | No | Approve the code or send it back |

The orchestrator is the fifth participant: it owns authority, change, finding, and gate evidence, handles verdicts and both close gates, runs the lessons harvest, writes `LOG.md`, and may write code only for a small low-risk follow-up whose shape is already determined.

**Revision loops are convergence-bounded.** Iterate while converging; escalate on stall; a 10-cycle backstop catches runaway iteration. An explicit extension is a *convergence lease* — continue while each cycle strictly shrinks the open-finding set, nothing closed reopens at equal-or-worse severity, no new defect class appears, and the touched surface stays within named bounds. Counts measure effort, not health; a count-scoped grant expires mid-convergence and pages the operator to re-authorize work that never stopped working.

**Ceremony is proportional.** A phase declares a review lane — `full` (all four roles), `light` (mechanical work; plan review skipped, the code critic still runs and can escalate back), or the invocation-only `one-shot` — on an orthogonal axis from the evidence lane, which scales candidate-bound apparatus. Both fail closed over authority surfaces, irreversible state, and deploy seams ([`../policies/review-lanes.md`](../policies/review-lanes.md)).

**Closing has two gates.** The implementation-candidate gate runs the complete prescribed sequence against the unchanged approved candidate. Then status, ripple, lessons, the END block, and the report all land — and because those are tracked writes, they move the tree. So a second bare `./bin/check all` proves the *actual handoff tree*, and no tracked write may follow it. A gate that certified a tree nobody will ever have is not a gate.

**Then the phase delivers itself**, and this is the design's most consequential recent decision (§6).

## 6. Consequential decisions

The interesting content of any methodology is where it chose against the obvious alternative.

### The acceptance boundary is typed, and delivery is decoupled from it

The template originally required the human to commit every phase. As of 2026-08-24 it does not. The rule now distinguishes two kinds of acceptance criterion ([`../policies/human-in-the-loop.md`](../policies/human-in-the-loop.md)):

- **Objective** — executable, independently reviewed by a role the implementer does not control, proved by a complete gate against the exact candidate, and recorded. These close autonomously.
- **Subjective and owner-only** — named manual checks, perceptual and UX judgment, product decisions, custody (credentials, billing, anything behind a console), and an unrun `User Demo:` protocol. These *always* park. No amount of green closes them.

The orchestrator then commits and fast-forward-pushes: explicit paths only (never `git add -A`, since the checkout may be shared with a concurrent session), no agent credit, never `--no-verify`, one unambiguous upstream, no force. The destructive surface — tags, resets, rebases, branch deletion, remote selection, history rewrite — stays with the human, always.

Two properties make this safe rather than reckless. First, **delivery is not acceptance and does not wait on it**: a phase with parked criteria still delivers, and those criteria stay open afterward exactly as they were. Second, **what blocks a phase is an unresolved gate, not an open judgment.** Conflating the two is what made the old posture expensive — it charged the reviewer's attention for a `git commit` they had no basis to refuse, at exactly the moment the demo needed that attention.

The compensating control is that the human's gate moved rather than disappearing: it now sits at the seam, on the END block's acceptance split and the demo protocol, and the code critic blocks on a *mistyped* criterion — a subjective criterion labeled objective is the one defect that would let a phase claim evidence that does not exist.

The honest cost: a phase can be delivered and later judged wrong, and the correction is a follow-up commit rather than an unpushed diff. That trade was made deliberately.

### Sub-phases are decomposed just-in-time

Major phases are drafted up front at general specificity, so the roadmap is visible from bootstrap. Sub-phases are decomposed **one at a time**, each drafted at the close of its predecessor with that predecessor's outcomes in hand. Pre-decomposing locks in premature assumptions and resists the very revisions that doing the work reveals.

Bite size is capability-indexed, not calendar-indexed: a model class that routinely closes phases of the current size on first-cycle approval can take bigger bites. Per-phase ceremony is a fixed cost, and over-fine decomposition under a strong coder pays it more often than the work needs.

### Autonomous self-modification was declined

The fully closed improvement loop — agent mines weaknesses, edits its own rules, validates, merges — was considered and rejected. It contradicts the human-in-the-loop boundary and imports the literature's own top risks: reward hacking and evaluator contamination. **Humans move up the stack, not out of the loop**; the human is the Curator, and that is a design choice rather than a maturity gap. Correspondingly, `./bin/check all` never bends to a lesson.

### Ceremony grows only against incidents, and every review prunes

Fail-closed pressure ratchets: every defect adds rigor, and nothing subtracts. Left alone, a methodology accretes binding steps until the ceremony costs more than the failures it prevents. So a new binding rule enters only with its motivating incident cited inline, every binding step must name the park it prevents, and every review pass treats steps whose failure families are structurally dead as deletion candidates. The worked form is a **ceremony audit** — walk a protocol step by step under that test and delete or demote the rest. A donor repo's first such audit deleted or demoted four binding steps, including a per-fix reseal duty that had cost roughly twenty-seven whole-repository reseal cycles in a single phase, each invalidated by the next one-line fix.

The same anti-ratchet logic applies to instruments: when a design change eliminates a defect class, retire its instrument rather than perfecting it.

### Greenfield until released

No backward-compatibility shims, legacy aliases, schema migrations, or transitional code paths until the project ships a stable external release. A wrong shape gets replaced directly, with every call site, fixture, test, sample, brief, and doc updated in the same phase. The rule ends by explicit amendment, not by drift.

### One canonical home, thin mirrors

Skills and agent definitions have exactly one canonical source, with harness-specific pointers generated around it, enforced mechanically. The alternative — maintaining parallel prose per harness — fails the way all duplicated documentation fails, except that here the duplicates are executable instructions and the drift is invisible until an agent behaves differently under one CLI than another.

## 7. The improvement flywheel

The repository improves at two scales, and owns both.

**Inner tier, within a repo.** Each role emits Process Observations — friction or ambiguity in briefs, policies, plans, or tooling — and the coder states *why* a previous attempt failed on revision rounds. `kickoff` harvests these at every close into `lessons/`. `bin/lessons` validates and tallies; `bin/lessons candidates` lists graduation-ready entries. `sweep` runs the pruning half over policies, briefs, skills, catalogs, and the ledger.

**Outer tier, between repos.** The starter is a hub. `stamp` ships the machinery into new projects; `teach` retrofits it onto existing ones; `learn` harvests back — both a spoke's `scope: methodology` lessons and the new defects exposed while applying a donor bundle, because applying a pattern is empirical evidence about that pattern's contract.

The seam between tiers is the lesson's `scope` field: `local` stays home, `methodology` is a standing export. This is the answer to the portability problem — knowledge is repo-local by default, and the hub-and-spoke channel is what makes phase-scale learning compound across a family of projects. The return path earns its cost precisely because of where defects surface first: a spoke exercises the machinery at a scale the template never does.

Two disciplines keep the transfer honest. **Direction of advance is established per item, never per repo** — a donor being "ahead" overall proves nothing about any single file or fix, and before importing a remedy, its defect must be shown to reproduce in the destination. **Anonymization runs at write time**, not as a cleanup pass, because this repository is public.

## 8. What this gives up

Stated as the methodology states it about itself.

- **Speed of a single throwaway iteration.** A one-line prompt beats a brief, a plan, and a phase. Use ad-hoc for one-off scripts; use this for what will exist next month.
- **Unbounded autonomy.** Objectively accepted phases deliver themselves unattended, but the loop still parks at every designed manual, subjective, product, custody, destructive, or owner-only gate. Silence never becomes judgment. If the goal is code generation with no human judgment at all, this is the wrong tool.
- **Flexibility within a session.** The orchestrator follows the plan. Wander before `kickoff` starts or between phases, not mid-orchestration.
- **Overhead on small things.** Single-file scripts and throwaway prototypes are not worth the structure.

One limit is internal rather than a trade: the orchestration runtime doctrine — sixteen fail-closed rules distilled from a production day in a derived repo where one orchestration halted nine times, each halt diagnosed and compiled into a standing rule — is **doctrine, not yet mechanics**. Self-resume budgets are mechanized; delta-merge tooling and instrument-qualification harnesses are not. Until they land, the `kickoff` prose loop and the human relay carry those rules. The brief says so in its own text rather than leaving a reader to discover it.

## 9. Verifying the claims

Every claim above is checkable from a clone. Counts are as of 2026-08-24, each reproducible by the command beside it.

| Claim | Verification |
|---|---|
| The full gate is green and warning-free | `./bin/check all` — 12 lanes, 572 tests |
| Policies bind and are cataloged | `ls policies/*.md` (28); `./bin/check-catalogs` |
| Briefs are indexed and links resolve | `ls briefs/*.md` (9); `./bin/check-catalogs` |
| The mechanistic half is real and tested | `find bin -maxdepth 1 -type f -perm -u+x` (20); `ls tests/test_*.py` (18) |
| Mirrors never drift from canonical | `./bin/check-harness-parity` |
| The ledger is valid and tallied | `./bin/lessons validate`; `./bin/lessons candidates` |
| No external-repo identifiers leak | `./bin/check-anonymization.sh` |
| Candidate identity is deterministic | `./bin/kickoff-tree-id` twice, unchanged tree |
| Phase history is auditable | `LOG.md` START/END pairs; `git log` |

The strongest verification is not a command: read one phase's END block, then read the commit it delivered. The methodology's whole proposition is that those two artifacts, together, tell the next reader what is true.

## 10. Authority map

This brief derives from, and must stay consistent with:

- [`BRIEF.md`](BRIEF.md) — what the template is, who it is for, the two operating modes, acceptance criteria.
- [`methodology.md`](methodology.md) — the eleven steps, the four roles, the runtime doctrine, the run-lifecycle vocabulary.
- [`harness-self-improvement.md`](harness-self-improvement.md) — the two-tier flywheel, its grounding, and what was declined.
- [`incremental-orchestration.md`](incremental-orchestration.md) — the implemented evidence plane.
- [`eacp-pattern-map.md`](eacp-pattern-map.md) — this repository mapped onto named patterns from the Encyclopedia of Agentic Coding Patterns, with the patterns deliberately declined and the antipatterns structurally guarded against.
- `policies/` — every prescriptive claim above; the file is named inline where the claim is made.

Corrections land here and in the owning source, then regenerate outward. A derivative rendering that disagrees with this brief is stale, not authoritative.
