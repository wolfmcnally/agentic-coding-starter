---
title: "EACP Pattern Map — Which Patterns This Repo Showcases"
date: 2026-07-23
status: implemented
scope: Maps this repository's structures onto named patterns from the Encyclopedia of Agentic Coding Patterns, with file-level evidence, the patterns it deliberately declines, the antipatterns it structurally guards against, and the gaps.
---

# EACP Pattern Map

This brief answers one question: **which patterns from the [Encyclopedia of Agentic Coding Patterns](https://aipatternbook.com) does this repository actually showcase, and where does each one live?**

It exists because the template is easy to describe procedurally ("planner → reviewer → coder → critic") and hard to describe *architecturally*. The EACP gives the architectural vocabulary. Naming the patterns makes three things checkable that were previously tacit: what the repo is doing, what it is deliberately *not* doing, and what it is missing.

Every claim below cites a repo-relative path. Where the repo's implementation diverges from or extends the corpus entry, the divergence is stated rather than smoothed over.

---

## 1. Corpus snapshot and method

- **Corpus:** Encyclopedia of Agentic Coding Patterns, curator Wolf McNally, `https://aipatternbook.com`.
- **Retrieved:** 2026-07-23, via the `eacp` MCP server against an unversioned working copy (`corpus_version.commit` was `null`; there is no pinned revision to cite).
- **Extent at retrieval:** 295 articles across 14 sections; **292 carried `status: draft`**, so nearly every entry cited here is commissioned-but-unreviewed content. Treat the *names and definitions* as stable and the *prose* as provisional.
- **Retrieval caveat (measured, 2026-07-23):** the corpus's `search` tool was unreliable during this work — roughly **one call in three hard-hangs and is cut off by the CDN at exactly 30 s** (CloudFront origin-response timeout). A controlled run gave `search` 6/10 successes against 20/20 for `list_articles` and `fetch_article` on the same host and session path, isolating the fault to the semantic-retrieval half rather than the corpus or the network. The map below was therefore built from **deterministic manifest enumeration plus targeted `fetch_article` calls**, not semantic search. Consequence for this brief: coverage of the *named* corpus is complete, but a pattern whose relevance would only surface through a semantic match — rather than through its title or section — could have been missed.
- **Method:** section manifests were enumerated in full for the eight sections plausibly relevant to an agentic-methodology repo; the five highest-stakes entries (`orchestrator-workers`, `generator-evaluator`, `prompt-chaining`, `externalized-state`, `compound-engineering`, `harness-engineering`) were read in full before any claim was made about them. The remainder are matched against their canonical one-line summaries.
- **Citation form:** per the corpus's own guidance, an entry is cited as *Wolf McNally, "&lt;Title&gt;," Encyclopedia of Agentic Coding Patterns, `https://aipatternbook.com/<slug>`*.

---

## 2. The one-sentence answer

**This repository is a worked implementation of *Harness Engineering* — and the specific harness it builds is a gated prompt chain wrapped around two nested Generator-Evaluator pairs, running entirely on externalized state, with Human in the Loop as the constraint that shapes every other choice.**

Everything else in the map hangs off that sentence. The orchestration is a fixed chain, not an inventive orchestrator. The quality mechanism is role separation, not model strength. The durability mechanism is files, not memory. And the stopping condition is a human, not a score.

---

## 3. The orchestration spine

| Pattern | Where it lives | Notes |
|---|---|---|
| [Prompt Chaining](https://aipatternbook.com/prompt-chaining) | `.claude/skills/kickoff/SKILL.md` Steps 0a–10 | **This, not Orchestrator-Workers, is the correct name for `kickoff`.** The corpus's test is whether the steps are fixed in advance or invented per request. `kickoff`'s are fixed: resolve → preflight → identify → plan → plan-review → code → code-review → build → accept → log. The corpus's own worked example ("criteria before code, code before tests, tests before merge") is the same shape. |
| — its *gates* | Verdict string-match; three-signal gate; build gates (Step 7); acceptance gates (Step 8) | The corpus specifies a gate as "plain code that asks a yes-or-no question … and stops or reroutes the chain." The repo has four distinct gate classes, which is unusually rich for a chain this short. |
| [Generator-Evaluator](https://aipatternbook.com/generator-evaluator) | `policies/four-canonical-agents.md`; `.claude/agents/*.md` | **Two nested instances**, not one: `phase-planner` ↔ `plan-reviewer` on the plan artifact, and `phase-coder` ↔ `code-critic` on the code artifact. The corpus names a planner sitting upstream "often"; here it is mandatory and itself evaluated. |
| — independent context, intensified | `briefs/cross-agent-invocation.md` §§1, 4 | The corpus asks for independent context windows. This repo goes two steps further: the evaluator runs on a **different vendor's model** by default (`kickoff.yaml` `role_models`), and the handoff **redacts the implementer's self-assessment** — no Build Status block, no "tests pass" narrative — on the cited finding that cold artifacts yield ~9.4 mean review findings vs 2.4–4.0 with the implementer's framing attached. |
| [Subagent](https://aipatternbook.com/subagent) | `.claude/agents/` (canonical), `.codex/agents/` (mirror) | Four named, scoped roles with distinct tool stances. Names are load-bearing by policy. |
| [Orchestrator-Workers](https://aipatternbook.com/orchestrator-workers) | `kickoff` Step 1a; Step 9a | **Present only in the decomposition move.** The pipeline is a chain, but sub-phase decomposition genuinely invents the subtasks after inspecting the input, one at a time, with each predecessor's outcomes in hand. That is the orchestrator half; the rest is chain. |
| [Plan Mode](https://aipatternbook.com/plan-mode) / [Research, Plan, Implement](https://aipatternbook.com/research-plan-implement) | `.claude/agents/phase-planner.md` (Read/Grep/Glob/WebSearch/WebFetch, **no write tools**) | Separation of understanding from decision from execution, each producing a reviewable artifact. The planner is structurally incapable of implementing. |
| [Model Routing](https://aipatternbook.com/model-routing) | `kickoff.yaml` `role_models`; `policies/role-models.md`; `.claude/skills/roles/SKILL.md` | Harness-aware: `role_models[H][role]` → `role_models['default'][role]` → native. **The routing rationale is inverted from the corpus's.** The corpus routes to cheaper models to save budget; this repo routes to the *other vendor* to buy reviewer independence. Same mechanism, different objective. |
| [Reasoning Effort](https://aipatternbook.com/reasoning-effort) | `kickoff.yaml` `role_models.*.effort` | A separate field from `model`, deliberately — the shipped Codex-orchestrated default is `model: opus, effort: high` for both review roles. |
| [Structured Outputs](https://aipatternbook.com/structured-outputs) | `## Verdict: APPROVED` / `## Verdict: REVISE` | **Partial, and knowingly so.** This is a sentinel string parsed by exact match, not a schema. `briefs/cross-agent-invocation.md` §2 notes Codex's `--output-schema` exists; the repo doesn't use it. See §9. |
| [Checkpoint](https://aipatternbook.com/checkpoint) | Step 0b preflight; the three-signal gate; Step 7; Step 8 | Four pause-verify-proceed points. The preflight is the strongest: it aborts *before any phase state is mutated*. |
| [Verification Loop](https://aipatternbook.com/verification-loop) | Step 7's classify-and-route fix loop | Failures are classified (coder error / plan error / environment error) and routed to the role that can fix them, rather than thrown back undifferentiated. |
| [Back-Pressure (Agent)](https://aipatternbook.com/back-pressure) | `policies/role-timeouts.md`; `bin/kickoff-config watch` | Three clocks per invocation (first-event 120 s, per-role idle, per-role hard) plus a Claude-only `claude_max_turns` circuit breaker, plus the 5-cycle runaway backstop, plus `briefs/cross-agent-invocation.md` §4's "bounded calls only; never unbounded polling loops." |
| [Deep Agents](https://aipatternbook.com/deep-agents) | The composite | Explicit planning + subagent delegation + persistent memory + heavy context engineering. All four are present; the repo is a legible instance of the composite recipe. |
| [Agentic Engineering](https://aipatternbook.com/agentic-engineering) | `briefs/BRIEF.md`; `briefs/methodology.md` | "The human writes the spec and reviews while agents write almost all the code" is this repo's thesis, stated in almost those words. |

---

## 4. Durable state — the repo's center of gravity

If one cluster explains why this template exists, it is this one. `briefs/BRIEF.md` §Thesis states the design goal in the corpus's own terms without using its vocabulary: *externalize the load-bearing parts of the work so every session starts from a known state and ends by updating it.*

| Pattern | Where it lives | Notes |
|---|---|---|
| [Externalized State](https://aipatternbook.com/externalized-state) | `plan/INDEX.md` (status ledger + dependency graph), `plan/phase-*.md`, `LOG.md` | The corpus's three categories map exactly: **the plan** (`plan/phase-N.M.md`), **progress markers** (`INDEX.md`'s ⏳/⬅️/🚧/✅ table), **intermediate artifacts** (plan text, verdicts, watcher result files). |
| [Progress Log](https://aipatternbook.com/progress-log) | `LOG.md`; `policies/log-discipline.md` | Append-only, owned by `kickoff`, one START/END pair per phase. The END block is not a summary — it is a structured evidence record (files, gates, lane, venues, timings, ripples, manual checks, demo). |
| [Source of Truth](https://aipatternbook.com/source-of-truth) | `policies/phase-status.md`; `policies/cross-harness-parity.md` | Applied three times, each with an explicit "and nowhere else": phase status lives only in `plan/INDEX.md`; skills/agents live only under `.claude/` with mirrors; `project/pyproject.toml` is the sole Python tooling config. |
| [DRY](https://aipatternbook.com/dry) | `AGENTS.md` → `CLAUDE.md` symlink; `.agents/skills/<name>` → `.claude/skills/<name>` directory symlinks | Harness parity is achieved by symlink rather than by copy, so drift is impossible on the surfaces where a symlink works. `.codex/agents/*.toml` are thin pointers where it doesn't. |
| [Artifact](https://aipatternbook.com/artifact) | Every phase's END block + diff pair | `briefs/methodology.md` §"What this methodology gives up" names it: "each phase leaves a reviewable artifact pair." |
| [Pinning](https://aipatternbook.com/pinning) | `policies/phase-ripple.md`; `role_models`; `briefs/cross-agent-invocation.md` | Used at three altitudes: model/effort pins per role, "pinned decisions" propagated downstream at phase close, and BCPs pinned in a brief "so future work cites a stable position instead of re-deriving it." |
| [Task Decomposition](https://aipatternbook.com/task-decomposition) | `briefs/methodology.md` §6 | "Bounded units of work with clear acceptance criteria" is the phase definition. |
| [Task Horizon](https://aipatternbook.com/task-horizon) | `briefs/methodology.md` §6, "Bite size is capability-indexed" | The repo turns the corpus's *measurement* into a *sizing rule*: size sub-phases to the coder model's demonstrated coherence, coarsen when phases close first-cycle with green gates, split finer when revision loops stall. This is the most operationally useful reading of Task Horizon I have seen anywhere. |

---

## 5. Feedforward — controls placed before the agent acts

| Pattern | Where it lives | Notes |
|---|---|---|
| [Feedforward](https://aipatternbook.com/feedforward) | `policies/` (19 files), `briefs/`, `CLAUDE.md` | The entire `policies/` directory is a feedforward surface: rules that constrain the first attempt rather than grade the result. |
| [Instruction File](https://aipatternbook.com/instruction-file) | `CLAUDE.md` + `AGENTS.md` symlink | **Extended beyond the corpus entry.** Three structural moves the corpus doesn't describe: (a) a **Hard rules** section above both zones, placed there explicitly because "an agent reads them before doing anything irreversible" — i.e. defending against top-down readers who stop early; (b) a **two-zone split** (Project Context / Methodology Contract) with HTML comment markers so `stamp` can rewrite one zone and copy the other verbatim; (c) inlined **catalogs** of every policy so agents see the index without an extra Read. |
| [Coding Convention](https://aipatternbook.com/coding-convention) | `CLAUDE.md` §Project conventions; §Universal conventions | Written, agreed, agent-readable — including format-level ones ("one executable command per fenced code block"). |
| [Invariant](https://aipatternbook.com/invariant) | `CLAUDE.md` §Architectural invariants | Eight named invariants marked "load-bearing — do not violate," inherited by every derived project. |
| [Skill](https://aipatternbook.com/skill) | `.claude/skills/{kickoff,methodology,learn,teach,roles,stamp}/SKILL.md` | Six packaged workflows. `roles` is the interesting one: a thin intelligence wrapper over a deterministic script. |
| [Brief](https://aipatternbook.com/brief) (Intent section) | `briefs/`; `policies/briefs.md` | The corpus has a *Brief* pattern; this repo has a governed brief lifecycle with frontmatter schema and a four-value status flow. Direct hit. |
| [Spec-Driven Development](https://aipatternbook.com/spec-driven-development) | "Briefs are the contract" invariant | Phase files specify *how*; briefs specify *what*; ambiguity is fixed at the brief, not worked around. |
| [Bounded Autonomy](https://aipatternbook.com/bounded-autonomy) | `briefs/cross-agent-invocation.md` §§2–4 | Freedom calibrated to reversibility with unusual precision: reviewers get `-s read-only` / `--allowedTools "Read,Grep,Glob"`; the coder alone gets `workspace-write`; `.git` and `.claude` stay non-auto-approved even under `dontAsk`; `--yolo` / `--dangerously-bypass-approvals-and-sandbox` is refused outright with a stated reason. |
| [Approval Policy](https://aipatternbook.com/approval-policy) | `-c 'approval_policy="never"'`; `--permission-mode dontAsk` | Headless calls are pinned so they *cannot* prompt — the corpus's contract between trust and autonomy, resolved at the flag level. |
| [Greenfield and Brownfield](https://aipatternbook.com/greenfield-and-brownfield) | `policies/greenfield-until-released.md` | The corpus's advice is "naming which one, out loud, steers the agent." This repo names it as Hard Rule 2, with an explicit end condition (first stable release) and an explicit amendment procedure. |
| [Belt-and-Suspenders](https://aipatternbook.com/belt-and-suspenders) | Three-signal gate; convergence-plus-backstop; three-clocks-plus-max-turns | Three independent instances of "two checks, either sufficient alone." The revision loop is the clearest: a *judgment* check (are objections converging?) and a *counting* check (5 cycles), and either one can stop the loop. |

---

## 6. Feedback sensors — checks that run after the agent acts

| Pattern | Where it lives | Notes |
|---|---|---|
| [Feedback Sensor](https://aipatternbook.com/feedback-sensor) | Build gates; verdicts; `bin/check-anonymization.sh` | Both classes present: machine oracles (lint/format/tests/leak scan) and judgment oracles (the two critics). |
| [Acceptance Criteria](https://aipatternbook.com/acceptance-criteria) | `policies/acceptance-empirical.md` | "'It compiles' is not acceptance." Every phase lists executable commands or *named* manual checks; ambiguous criteria are treated as manual and flagged. |
| [Code Review](https://aipatternbook.com/code-review) | `.claude/agents/code-critic.md` | Runs in **every** review lane — the one thing `light` may not skip. |
| [Shift-Left Feedback](https://aipatternbook.com/shift-left-feedback) | Plan review before code exists; Step 0b preflight before phase state exists | Both are the pattern's shape: move the check as close to creation as possible. The preflight is the sharper one — it validates the *upstream infrastructure* before a single marker flips. |
| [Fail Fast and Loud](https://aipatternbook.com/fail-fast-and-loud) | Step 0b: "Any failure aborts `kickoff` immediately" | And explicitly refuses the soft landing: "Do not fall back to native, identify or decompose the phase, change `plan/INDEX.md`, append a START/END block, or invoke an agent." |
| [Silent Failure](https://aipatternbook.com/silent-failure) (guarded) | Three-signal gate; `--required-output-file` truncation | Two named guards against reassuring nulls: a missing or malformed verdict is "a failed invocation, not a lenient pass," and the watcher truncates the result path before launch so "a zero exit with no fresh artifact is a protocol error" — a revision round can never re-read a stale verdict. |
| [Architecture Fitness Function](https://aipatternbook.com/architecture-fitness-function) | `bin/check-anonymization.sh`; `tests/test_kickoff_config.py` | The leak guard is a true automated fitness function: it verifies a stated architectural decision (Hard Rule 3) and exits non-zero on drift. `tests/` covers the config manager's own invariants. **Partial** — see §9. |
| [Test](https://aipatternbook.com/test) / [Harness](https://aipatternbook.com/harness) | `project/tests/`, `tests/`; `cd project && uv run …` | The repo ships a real (if minimal) build target so the gates are never hypothetical from the first session. |
| [Metric](https://aipatternbook.com/metric) / [Agent Trace](https://aipatternbook.com/agent-trace) | `.kickoff/role-timings.jsonl`; `bin/kickoff-config recommend-timeouts` | Per-invocation telemetry (venue, model, effort, duration, first-event, longest idle, outcome) with an explicit statistical discipline: ≥30 successes per `(role, venue, model, effort)`, then `max(floor, 2 × p95)`, and **timed-out calls treated as censored cases, never used to auto-tighten.** |

---

## 7. Governance and provenance

| Pattern | Where it lives | Notes |
|---|---|---|
| [Human in the Loop](https://aipatternbook.com/human-in-the-loop) | `policies/human-in-the-loop.md`; Hard Rule 1 | Not a value statement — an enumerated list of six things the orchestrator never does, plus an explicit **waiver protocol** (explicit, scoped, logged, one-shot). The one-shot clause is the sophisticated part: "authorization stands for the scope specified," and approval never extrapolates forward. |
| [Agent Provenance](https://aipatternbook.com/agent-provenance) | `kickoff` Step 10 END block | **The strongest single match in the repo, and rare in practice.** Every END block records, per role: resolved model, effort, venue, fallback annotation, duration, first-event, longest idle, and outcome. And it goes further than the corpus asks — a role that fell back to native after a successful preflight raises a **🚨 disconnect line** stating what was configured, what actually ran, and why: *"coder configured for opus but ran native (call timed out) — output was NOT produced by opus."* That is provenance defended against its own most likely lie. |
| [Delegation Chain](https://aipatternbook.com/delegation-chain) | `KICKOFF_DELEGATION_DEPTH=1` recursion guard | Named as such in `briefs/cross-agent-invocation.md` §4: Claude's `CLAUDECODE` guard only stops claude→claude nesting, so cross-vendor chains need an explicit depth marker. A delegated role never re-delegates. |
| [Agent Registry](https://aipatternbook.com/agent-registry) | `policies/four-canonical-agents.md` | A four-row catalog with canonical file, tool stance, write capability, and job — plus rules for adding a fifth. **Partial:** no ownership field, no last-reviewed date. |
| [Runtime Governance](https://aipatternbook.com/runtime-governance) | `bin/kickoff-config watch` | Partial and mechanical rather than model-driven: the watchdog verifies the child's actual CLI/model/effort flags against its own routing metadata **before it spawns**, and refuses on mismatch. Interception on the action path, ruled allow/block. |

---

## 8. Context engineering and knowledge compounding

| Pattern | Where it lives | Notes |
|---|---|---|
| [Progressive Disclosure](https://aipatternbook.com/progressive-disclosure) | `plan/INDEX.md` §Reading protocol; `CLAUDE.md` §Reading protocol | Stated as a prohibition, which is what makes it work: **"Do **not** slurp every `phase-*.md`. `depends_on` is the contract for which predecessors actually matter."** Plus a deliberate guard against a missing `depends_on` (also read the last ✅ phase). |
| [Context Engineering](https://aipatternbook.com/context-engineering) | `kickoff` Step 6 item 1; `briefs/cross-agent-invocation.md` §4 | "Hand the reviewer a **map, not a payload**" — for a large change the handoff is the changed-file list plus `git diff --stat`, from which a reviewer with Read/Grep pulls surgically. Machine-regenerated blobs (fixtures, lockfiles, snapshots) are flagged "spot-check structure, don't read line-by-line." |
| [Context Rot](https://aipatternbook.com/context-rot) (guarded) | `kickoff` Step 4 item 2 | A recorded war story made into a rule: an unbounded "read all the sources the plan touches" mandate exhausted an external reviewer's own context and tripped a failed internal compaction *before it reached a verdict*. The fix is a **scoped reading mandate** naming the load-bearing files. |
| [Handoff](https://aipatternbook.com/handoff) | `briefs/cross-agent-invocation.md` §§1–4 | The most developed pattern instance in the repo. Session-id capture for resume (`thread_id` / `session_id`), resume-specific flag surfaces, large context via temp files, self-assessment redaction, and the explicitly named failure to avoid: computing `git diff \| wc -c`, seeing hundreds of KB, and falling back to native *without ever making the external call* — "conflating an on-disk artifact with tokens-in-the-context-window." |
| [Thread-per-Task](https://aipatternbook.com/thread-per-task) | `kickoff`: "Orchestrate a single phase per session" | One coherent unit of work, one session, one START/END pair. |
| [Compound Engineering](https://aipatternbook.com/compound-engineering) | `CLAUDE.md` invariant: **"Rules, not memory"** | The corpus asks that every closed unit of work codify its lesson onto a durable surface. This repo makes surface *selection* a hard invariant: "Agent-side memory is local to one operator, one harness, one machine; it is the wrong place for engine knowledge. If a learning surfaces in a session, capture it in the repo, not in memory." Of the corpus's five canonical surfaces, the repo uses four — instruction file, skills, subagents, tests. It does not use hooks (§9). |
| [Feedback Flywheel](https://aipatternbook.com/feedback-flywheel) | `.claude/skills/learn/SKILL.md`; `LOG.md` | Not aspirational — **instrumented and dated.** `LOG.md`'s 2026-06-14 LEARN entry records the whole loop: a donor repo's convention was observed, distilled into `policies/mechanistic-vs-intelligence.md` and a `CLAUDE.md` invariant, and the old `scripts/` directory migrated to `bin/` in the same pass. The corpus's own "three occurrences before codifying" caution is the one part not enforced. |
| [Reference Repository](https://aipatternbook.com/reference-repository) | The repo itself; `stamp` / `learn` / `teach` | The corpus describes giving an agent an exemplar repo to study. This template *is* that exemplar, plus a bidirectional transfer mechanism the corpus entry doesn't contemplate: `learn` pulls patterns in (donor read-only), `teach` pushes them out (this repo read-only), both plan-first with user approval. |
| [Garbage Collection](https://aipatternbook.com/garbage-collection) | `policies/phase-ripple.md`; `teach`'s stale-migration pass | **Partial.** Ripple is drift-*prevention* at phase close (AUTO edits land, DECIDE items surface as named follow-ups); `teach` reports "stale-in-light-of-teaching migrations." Neither is the corpus's recurring sweep over accumulated rules. Given that `compound-engineering` names garbage collection as its mandatory companion, this is the gap most worth closing. |
| [Question Generation](https://aipatternbook.com/question-generation) | `stamp`; `plan-reviewer`'s `AskUserQuestion` | `stamp` interviews only when the description leaves an answer non-obvious. The plan reviewer is the sole role permitted to escalate a product decision to the human — and when it runs in an external venue where `AskUserQuestion` is unreachable, the unresolved question becomes a `REVISE` verdict stating the question. Graceful degradation of an escalation channel. |

---

## 9. Patterns the repo deliberately declines

Naming these matters as much as naming the ones it uses. Each refusal is traceable to a stated reason.

| Declined pattern | Where the refusal is recorded | Reason |
|---|---|---|
| [Worktree Isolation](https://aipatternbook.com/worktree-isolation) | `kickoff` Step 5 item 3 | The corpus's problem — two writers on one tree — is solved by **serialization instead**: "`kickoff` is sequential, so during this stage no native writer touches the tree." The single-writer guarantee is obtained without the worktree's setup cost and cleanup risk. |
| [Parallelization](https://aipatternbook.com/parallelization) / [Agent Teams](https://aipatternbook.com/agent-teams) | `briefs/methodology.md` §"What this methodology gives up" | The methodology trades throughput for a reviewable artifact per phase. Peer coordination has no place in a chain whose stopping condition is a human. |
| [Dark Factory](https://aipatternbook.com/dark-factory) | `policies/human-in-the-loop.md`, closing line | Explicit: "Projects that need fully unattended code generation should use a different methodology. This one is wrong for that." |
| [Ralph Wiggum Loop](https://aipatternbook.com/ralph-wiggum-loop) | Convergence judgment + 5-cycle backstop | The corpus frames Ralph Wiggum as what happens when self-review has no teeth. Every loop here terminates on a *judged trend*, not on restart-until-it-looks-done. |
| [Continuous Deployment](https://aipatternbook.com/continuous-deployment) | Hard Rule 1 | The pipeline stops at a green build and a written END block. Shipping is out of scope by construction. |
| [Migration](https://aipatternbook.com/migration) / [Deprecation](https://aipatternbook.com/deprecation) / [Parallel Change](https://aipatternbook.com/parallel-change) | `policies/greenfield-until-released.md` | Suspended, not rejected — the policy has an explicit end condition. Pre-release, wrong shapes get replaced directly and every call site updated in the same phase. |

---

## 10. Antipatterns the repo structurally guards against

| Antipattern | The guard |
|---|---|
| [Approval Fatigue](https://aipatternbook.com/approval-fatigue) | Deliberately designed against: `policies/human-in-the-loop.md` — "each phase is small enough that reviewing it is fast; each END block is structured enough that the review is grep-able." One approval per phase, not per action. |
| [Vibe Coding](https://aipatternbook.com/vibe-coding) | The code critic runs in every lane and is never skippable; acceptance is empirical. |
| [Shadow Agent](https://aipatternbook.com/shadow-agent) | Every role is registered in `policies/four-canonical-agents.md`, and every non-native venue is live-preflighted before use. An unregistered agent cannot enter the loop. |
| [Tool Sprawl](https://aipatternbook.com/tool-sprawl) | Each role has a minimal, fixed tool stance — the critic gets exactly Read, Grep, Glob. |
| [Cargo Cult Programming](https://aipatternbook.com/cargo-cult-programming) | `learn` and `teach` are plan-first with explicit tiering, and the 2026-06-14 LEARN entry records what was *skipped* as out-of-scope: "only the convention and the principle generalize." |
| [Speculative Generality](https://aipatternbook.com/speculative-generality) | `briefs/methodology.md` §6: sub-phases are JIT because "pre-decomposed sub-phases lock in premature assumptions." |
| [Benchmark Mirage](https://aipatternbook.com/benchmark-mirage) | Timeout calibration refuses vendor guidance and anecdote in favor of local p95 tails from `.kickoff/` telemetry. |
| [Big Ball of Mud](https://aipatternbook.com/big-ball-of-mud) | `policies/project-isolation.md`: nothing inside `project/` references anything above it, keeping the deliverable submodule-ready. |

---

## 11. Where the repo extends the corpus

Five structures here have no corresponding EACP entry. Each is a candidate contribution back.

1. **Mechanistic-vs-Intelligence triage** (`policies/mechanistic-vs-intelligence.md`). A per-task routing rule between deterministic script and agent, with the seam-splitting corollary — "the agent decides *what*, a deterministic script does the mechanical *how*." The corpus has `tool`, `hook`, and `determinism` but no article naming the triage decision itself. This is the repo's most transferable original idea.
2. **Review Lanes** (`policies/review-lanes.md`). Risk-adaptive review *intensity* with a declared lane, an eligibility test that must pass two lists, asymmetric-safety upgrade-only orchestrator discretion, and the critic empowered to escalate `light → full` mid-phase. The corpus has no article on varying review depth by risk.
3. **Phase Ripple** (`policies/phase-ripple.md`). Propagating a closing phase's pinned decisions into downstream *drafted but unexecuted* plan files, classified AUTO (apply now) vs DECIDE (surface as a named follow-up). Adjacent to Garbage Collection but aimed forward at plans rather than backward at accumulated rules.
4. **Cross-Harness Parity** (`policies/cross-harness-parity.md`). A canonical-plus-mirror contract with a documented onboarding procedure for a third harness. `A2A` addresses agent interop at runtime; this addresses *configuration-surface* portability, which is a different problem.
5. **Fail-closed venue preflight** (`kickoff` Step 0b). One live sentinel call per unique `(CLI, model, effort, access mode)` target, in an empty temp directory, using production credential scrubs and flags — because "CLI presence, auth-status output, and credential files do not prove that precedence, entitlement, network, and the headless invocation all work together." A named pattern for *proving a delegation target is live before mutating any state* is missing from the corpus.

---

## 12. Gaps — patterns the corpus names and this repo does not show

Ordered by how actionable each one is here.

1. **[Hook](https://aipatternbook.com/hook) — absent entirely.** There are no lifecycle hooks anywhere in the repo. This is the sharpest gap, because `bin/check-anonymization.sh` is *exactly* hook-shaped: `policies/anonymize-log-references.md` says "run it before any push," which is a pre-push hook expressed as a sentence an agent must remember. `compound-engineering` names hooks as the surface for "lessons that must be enforced deterministically rather than remembered."
2. **[Architecture Fitness Function](https://aipatternbook.com/architecture-fitness-function) — under-mechanized against the repo's own law.** `briefs/BRIEF.md` §7 lists acceptance criteria that are plainly mechanizable but are not mechanized: every `briefs/` file appears in the `CLAUDE.md` catalog and vice versa (no orphans either way), the same for `policies/`, `readlink AGENTS.md` resolves, and `plan/INDEX.md` carries exactly one `⬅️`. By `policies/mechanistic-vs-intelligence.md` those are `bin/` work by definition. A `bin/check-structure.sh` would close this and gap 1 at once.
3. **[Eval](https://aipatternbook.com/eval) / [LLM-as-Judge](https://aipatternbook.com/llm-as-judge) — absent.** The repo tests its *machinery* (`tests/test_kickoff_config.py`) but never measures whether the four-role loop actually outperforms a single agent, or whether cross-vendor review outperforms same-vendor. The one quantitative claim in the repo (9.4 vs 2.4–4.0 findings) is cited from an external report, not measured locally. `briefs/BRIEF.md` §8 declares this out of scope — a defensible line, worth revisiting once telemetry accumulates.
4. **[Skill Fitness](https://aipatternbook.com/skill-fitness) — absent.** Six skills exist; none is versioned, scoped by measured lift, or subject to a retirement test.
5. **[AgentOps](https://aipatternbook.com/agentops) — seeded, not built.** `.kickoff/role-timings.jsonl` is gitignored and per-repo. There is no aggregation across repos or over time, so the recalibration discipline has nothing to feed on until a single repo accrues 30 samples per target.
6. **[Structured Outputs](https://aipatternbook.com/structured-outputs) — sentinel string, not schema.** `## Verdict: REVISE` is parsed by exact match and "any deviation … breaks orchestration." Codex's `--output-schema` is documented in `briefs/cross-agent-invocation.md` §2 but unused; Claude has no equivalent, so parity is the honest reason to stay with the sentinel. Worth an explicit note in that brief so the choice reads as decided rather than overlooked.
7. **[Codebase Map](https://aipatternbook.com/codebase-map) — partial.** `plan/INDEX.md`'s critical-files map and `CLAUDE.md`'s layout section cover the *methodology* surfaces well; nothing maps the deliverable under `project/`. This gets worse as a derived project's deliverable grows.
8. **[Agentic Pull Request](https://aipatternbook.com/agentic-pull-request) — absent by design.** Work lands in the working tree with an END block; there is no branch, no PR, no session link. Hard Rule 1 makes this deliberate, but the END block already carries most of a PR body, so the gap is smaller than it looks.
9. **[Reflexion](https://aipatternbook.com/reflexion) — absent as a mechanism.** Revision rounds pass the critic's findings forward but never ask the coder to articulate *why* the last attempt failed. `LOG.md` records outcomes, not failure analyses.
10. **[MCP](https://aipatternbook.com/mcp) / [Retrieval](https://aipatternbook.com/retrieval) — absent, appropriately.** The planner has `WebSearch`/`WebFetch`; nothing else reaches outside the repo. Nothing in the methodology needs it.

---

## 13. Sources

- Encyclopedia of Agentic Coding Patterns, Wolf McNally, `https://aipatternbook.com` — retrieved 2026-07-23 via the `eacp` MCP server (295 articles, 292 draft; no pinned corpus revision available). Individual entries cited inline.
- Read in full before citation: `orchestrator-workers`, `generator-evaluator`, `prompt-chaining`, `externalized-state`, `compound-engineering`, `harness-engineering`, plus the `intent-and-scope` section overview.
- Repo evidence: `CLAUDE.md`, `briefs/methodology.md`, `briefs/BRIEF.md`, `briefs/cross-agent-invocation.md`, `.claude/skills/kickoff/SKILL.md`, `kickoff.yaml`, `bin/README.md`, `plan/INDEX.md`, `LOG.md`, and all 19 files under `policies/`.

## 14. Related briefs

- [`methodology.md`](methodology.md) — the eleven steps this map is a pattern-level reading of.
- [`BRIEF.md`](BRIEF.md) — the product brief whose §7 acceptance criteria gap 2 above proposes mechanizing.
- [`cross-agent-invocation.md`](cross-agent-invocation.md) — the source for nearly every Handoff, Bounded Autonomy, and Back-Pressure claim.
- [`deterministic-orchestration.md`](deterministic-orchestration.md) — draft; the Prompt Chaining reading in §3 is the argument for why `kickoff`'s loop is a good candidate for deterministic encoding.
