---
title: "EACP Pattern Map — Which Patterns This Repo Showcases"
date: 2026-08-23
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
| — its *gates* | Verdict string-match; three-signal gate; candidate identity; evidence validation; implementation-candidate close; handoff close | The corpus specifies a gate as "plain code that asks a yes-or-no question … and stops or reroutes the chain." The repo separates transport completion, role shape/evidence, exact candidate identity, the complete candidate suite, and the post-bookkeeping suite on the delivered tree. |
| [Generator-Evaluator](https://aipatternbook.com/generator-evaluator) | `policies/four-canonical-agents.md`; `.claude/agents/*.md` | **Two nested instances**, not one: `phase-planner` ↔ `plan-reviewer` on the plan artifact, and `phase-coder` ↔ `code-critic` on the code artifact. The corpus names a planner sitting upstream "often"; here it is mandatory and itself evaluated. |
| — independent context, intensified | `briefs/cross-agent-invocation.md` §§1, 4 | The corpus asks for independent context windows. This repo goes two steps further: the evaluator runs on a **different vendor's model** by default (`kickoff.yaml` `role_models`), and the handoff **redacts the implementer's self-assessment** — no Build Status block, no "tests pass" narrative — on the cited finding that cold artifacts yield ~9.4 mean review findings vs 2.4–4.0 with the implementer's framing attached. |
| [Subagent](https://aipatternbook.com/subagent) | `.claude/agents/` (canonical), `.codex/agents/` (mirror) | Four named, scoped roles with distinct tool stances. Names are load-bearing by policy. |
| [Orchestrator-Workers](https://aipatternbook.com/orchestrator-workers) | `kickoff` Step 1a; Step 9a | **Present only in the decomposition move.** The pipeline is a chain, but sub-phase decomposition genuinely invents the subtasks after inspecting the input, one at a time, with each predecessor's outcomes in hand. That is the orchestrator half; the rest is chain. |
| [Plan Mode](https://aipatternbook.com/plan-mode) / [Research, Plan, Implement](https://aipatternbook.com/research-plan-implement) | `.claude/agents/phase-planner.md` (Read/Grep/Glob/WebSearch/WebFetch, **no write tools**) | Separation of understanding from decision from execution, each producing a reviewable artifact. The planner is structurally incapable of implementing. |
| [Model Routing](https://aipatternbook.com/model-routing) | `kickoff.yaml` `role_models`; `policies/role-models.md`; `.claude/skills/roles/SKILL.md` | Harness-aware: `role_models[H][role]` → `role_models['default'][role]` → native. **The routing rationale is inverted from the corpus's.** The corpus routes to cheaper models to save budget; this repo routes to the *other vendor* to buy reviewer independence. Same mechanism, different objective. |
| [Reasoning Effort](https://aipatternbook.com/reasoning-effort) | `kickoff.yaml` `role_models.*.effort` | A separate field from `model`, deliberately — the shipped Codex-orchestrated default is `model: opus, effort: high` for both review roles. |
| [Structured Outputs](https://aipatternbook.com/structured-outputs) | `## Verdict:` sentinel; `## Finding Evidence` / `### Change Evidence` JSON | **Partial, and knowingly so.** Findings and change metadata are schema-validated across both harnesses; the terminal verdict remains a parity-safe exact sentinel because only one supported CLI supplies native output-schema enforcement. See §12. |
| [Checkpoint](https://aipatternbook.com/checkpoint) | Step 0b preflight; the three-signal gate; Step 7; Step 8 | Four pause-verify-proceed points. The preflight is the strongest: it aborts *before any phase state is mutated*. |
| [Verification Loop](https://aipatternbook.com/verification-loop) | Step 7's classify-and-route fix loop | Failures are classified (coder error / plan error / environment error) and routed to the role that can fix them, rather than thrown back undifferentiated. |
| [Back-Pressure (Agent)](https://aipatternbook.com/back-pressure) | `policies/role-timeouts.md`; `bin/kickoff-config watch` | Three clocks per invocation (first-event 120 s, per-role idle, per-role hard) plus a Claude-only `claude_max_turns` circuit breaker, plus the 10-cycle runaway backstop, plus `briefs/cross-agent-invocation.md` §4's "bounded calls only; never unbounded polling loops." |
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
| [Feedforward](https://aipatternbook.com/feedforward) | `policies/`, `briefs/`, `CLAUDE.md` | The entire `policies/` directory is a feedforward surface: rules that constrain the first attempt rather than grade the result. |
| [Instruction File](https://aipatternbook.com/instruction-file) | `CLAUDE.md` + `AGENTS.md` symlink | **Extended beyond the corpus entry.** Three structural moves the corpus doesn't describe: (a) a **Hard rules** section above both zones, placed there explicitly because "an agent reads them before doing anything irreversible" — i.e. defending against top-down readers who stop early; (b) a **two-zone split** (Project Context / Methodology Contract) with HTML comment markers so `stamp` can rewrite one zone and copy the other verbatim; (c) inlined **catalogs** of every policy so agents see the index without an extra Read. |
| [Coding Convention](https://aipatternbook.com/coding-convention) | `CLAUDE.md` §Project conventions; §Universal conventions | Written, agreed, agent-readable — including format-level ones ("one executable command per fenced code block"). |
| [Invariant](https://aipatternbook.com/invariant) | `CLAUDE.md` §Architectural invariants | Named invariants marked "load-bearing — do not violate," inherited by every derived project. |
| [Skill](https://aipatternbook.com/skill) | `.claude/skills/{kickoff,methodology,learn,teach,roles,sweep,stamp}/SKILL.md` | Seven packaged workflows. `roles` is a thin intelligence wrapper over a deterministic script; `sweep` is the user-gated maintenance half of the lessons flywheel. |
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
| [Feedback Sensor](https://aipatternbook.com/feedback-sensor) | `bin/check`; verdicts; `bin/kickoff-evidence` | Both classes present: one repository-owned machine-oracle entry point (locked lint/format/tests/policy checks), two judgment critics, and a deterministic sensor that rejects stale-candidate findings and gates. |
| [Acceptance Criteria](https://aipatternbook.com/acceptance-criteria) | `policies/acceptance-empirical.md` | "'It compiles' is not acceptance." Every phase lists executable commands or *named* manual checks; ambiguous criteria are treated as manual and flagged. |
| [Code Review](https://aipatternbook.com/code-review) | `.claude/agents/code-critic.md`; `policies/review-lanes.md` | Runs on every initial implementation; repeat review on follow-up corrections is required when risk is high or the diff is large/cross-cutting. |
| [Shift-Left Feedback](https://aipatternbook.com/shift-left-feedback) | Plan review before code exists; Step 0b preflight before phase state exists | Both are the pattern's shape: move the check as close to creation as possible. The preflight is the sharper one — it validates the *upstream infrastructure* before a single marker flips. |
| [Fail Fast and Loud](https://aipatternbook.com/fail-fast-and-loud) | Step 0b: "Any failure aborts `kickoff` immediately" | And explicitly refuses the soft landing: "Do not fall back to native, identify or decompose the phase, change `plan/INDEX.md`, append a START/END block, or invoke an agent." |
| [Silent Failure](https://aipatternbook.com/silent-failure) (guarded) | Three independent watcher signals; evidence validation | Child status, fresh artifact, and terminal stream completeness are recorded independently. Ordinary success requires all three; exit 66 preserves but does not trust a valid fresh artifact from an incomplete stream, while missing/stale evidence stays an error. |
| [Architecture Fitness Function](https://aipatternbook.com/architecture-fitness-function) | `bin/check policy`; `bin/check-catalogs`; `tests/test_check.py`; `tests/test_check_catalogs.py`; `tests/test_kickoff_config.py` | The canonical policy mode enforces public-repo and configuration invariants; `bin/check-catalogs` mechanizes bidirectional catalogs, tracked internal links, and lifecycle-aware phase-ledger structure; behavioral tests prove the gate wrapper itself cannot hide prerequisite or child-command failures. |
| [Test](https://aipatternbook.com/test) / [Harness](https://aipatternbook.com/harness) | `project/tests/`, `tests/`; `bin/check` | The repo ships a real build target and a cwd-independent, lockfile-backed harness so gates are neither hypothetical nor copied prompt text. |
| [Hook](https://aipatternbook.com/hook) | `.githooks/pre-push`; `bin/install-hooks` | The tracked hook delegates to the same canonical full gate. Installation is explicit, idempotent, and conflict-refusing rather than silently rewriting local Git configuration. |
| [Metric](https://aipatternbook.com/metric) / [Agent Trace](https://aipatternbook.com/agent-trace) | `.kickoff/role-timings.jsonl`; run-scoped evidence ledgers | Timing telemetry retains its calibrated p95 discipline. Evidence adds directly observed packet bytes/hashes, candidate/path counts, finding states/reopenings/classifications, gate results, and the three protocol signals; unavailable causal timing is recorded as unknown rather than inferred. |

---

## 7. Governance and provenance

| Pattern | Where it lives | Notes |
|---|---|---|
| [Human in the Loop](https://aipatternbook.com/human-in-the-loop) | `policies/human-in-the-loop.md`; Hard Rule 1 | Not a value statement — a **typed boundary**. A criterion is objective only if it is executable, independently reviewed, gate-proved, and candidate-bound; everything subjective, perceptual, product-shaped, or custody-bearing parks for the human no matter how green the gate is. The loop's cost is spent where judgment is actually required, not on a `git commit` the human has no basis to refuse. The **restriction protocol** (explicit, scoped, logged, one-shot) and "authorization stands for the scope specified" keep approval from extrapolating forward. |
| [Agent Provenance](https://aipatternbook.com/agent-provenance) | `kickoff` Step 10 END block | **The strongest single match in the repo, and rare in practice.** Every END block records, per role: resolved model, effort, venue, fallback annotation, duration, first-event, longest idle, and outcome. And it goes further than the corpus asks — a role that fell back to native after a successful preflight raises a **🚨 disconnect line** stating what was configured, what actually ran, and why: *"coder configured for opus but ran native (call timed out) — output was NOT produced by opus."* That is provenance defended against its own most likely lie. |
| [Delegation Chain](https://aipatternbook.com/delegation-chain) | `KICKOFF_DELEGATION_DEPTH=1` recursion guard | Named as such in `briefs/cross-agent-invocation.md` §4: Claude's `CLAUDECODE` guard only stops claude→claude nesting, so cross-vendor chains need an explicit depth marker. A delegated role never re-delegates. |
| [Agent Registry](https://aipatternbook.com/agent-registry) | `policies/four-canonical-agents.md` | A four-row catalog with canonical file, tool stance, write capability, and job — plus rules for adding a fifth. **Partial:** no ownership field, no last-reviewed date. |
| [Runtime Governance](https://aipatternbook.com/runtime-governance) | `bin/kickoff-config watch` | Partial and mechanical rather than model-driven: the watchdog verifies the child's actual CLI/model/effort flags against its own routing metadata **before it spawns**, and refuses on mismatch. Interception on the action path, ruled allow/block. |

---

## 8. Context engineering and knowledge compounding

| Pattern | Where it lives | Notes |
|---|---|---|
| [Progressive Disclosure](https://aipatternbook.com/progressive-disclosure) | `plan/INDEX.md` §Reading protocol; `CLAUDE.md` §Reading protocol | Stated as a prohibition, which is what makes it work: **"Do **not** slurp every `phase-*.md`. `depends_on` is the contract for which predecessors actually matter."** Plus a deliberate guard against a missing `depends_on` (also read the last ✅ phase). |
| [Context Engineering](https://aipatternbook.com/context-engineering) | `kickoff` Steps 4 and 6; `bin/kickoff-evidence packet` | The first pass gets authoritative sources and a map. Later rounds get a deterministic causal packet: unresolved stable findings, path/hash or plan delta, authority/risk drift, selected checks, prior gates, and explicit omission rules; reviewers may still pull original files on demand. |
| [Context Rot](https://aipatternbook.com/context-rot) (guarded) | `kickoff` Step 4 item 2 | A recorded war story made into a rule: an unbounded "read all the sources the plan touches" mandate exhausted an external reviewer's own context and tripped a failed internal compaction *before it reached a verdict*. The fix is a **scoped reading mandate** naming the load-bearing files. |
| [Handoff](https://aipatternbook.com/handoff) | `briefs/cross-agent-invocation.md` §§1–4 | The most developed pattern instance in the repo. Session-id capture for resume (`thread_id` / `session_id`), resume-specific flag surfaces, large context via temp files, self-assessment redaction, and the explicitly named failure to avoid: computing `git diff \| wc -c`, seeing hundreds of KB, and falling back to native *without ever making the external call* — "conflating an on-disk artifact with tokens-in-the-context-window." |
| [Thread-per-Task](https://aipatternbook.com/thread-per-task) | `kickoff`: "Orchestrate a single phase per session" | One coherent unit of work, one session, one START/END pair. |
| [Compound Engineering](https://aipatternbook.com/compound-engineering) | `CLAUDE.md` invariants: **"Rules, not memory"** + **"Lessons compound"**; `kickoff` Step 9c; `policies/lessons.md` | The corpus asks that every closed unit of work codify its lesson onto a durable surface. This repo makes surface *selection* a hard invariant ("capture it in the repo, not in memory") and, as of 2026-08-10, makes the closing condition **mechanical**: `kickoff` Step 9c asks the lessons question at every phase close, the END block's `Lessons:` field may not be omitted, and candidate lessons land in the `lessons/` ledger scope-classified for graduation. Of the corpus's five canonical surfaces, the repo uses four — instruction file, skills, subagents, tests. It still declines hooks as a codification surface (§9); deterministic enforcement routes to `bin/` gates instead. |
| [Feedback Flywheel](https://aipatternbook.com/feedback-flywheel) | `.claude/skills/learn/SKILL.md`; `LOG.md`; `policies/lessons.md`; `bin/lessons` | Not aspirational — **instrumented and dated.** `LOG.md`'s 2026-06-14 LEARN entry records the whole loop: a donor repo's convention was observed, distilled into `policies/mechanistic-vs-intelligence.md` and a `CLAUDE.md` invariant, and the old `scripts/` directory migrated to `bin/` in the same pass. The corpus's "three occurrences before codifying" caution — previously the one unenforced part — is now mechanical: `bin/lessons candidates` lists graduation-ready lessons only at ≥3 occurrences, and graduation is human-ratified per `policies/lessons.md`. |
| [Reference Repository](https://aipatternbook.com/reference-repository) | The repo itself; `stamp` / `learn` / `teach` | The corpus describes giving an agent an exemplar repo to study. This template *is* that exemplar, plus a bidirectional transfer mechanism the corpus entry doesn't contemplate: `learn` pulls patterns in (donor read-only), `teach` pushes them out (this repo read-only), both plan-first with user approval. |
| [Garbage Collection](https://aipatternbook.com/garbage-collection) | `.claude/skills/sweep/SKILL.md`; `policies/phase-ripple.md`; `teach`'s stale-migration pass | Formerly this map's "gap most worth closing"; closed 2026-08-10 by the `sweep` skill — the corpus's recurring sweep over accumulated rules: policies, briefs, skills (`last-reviewed` cadence), the lessons ledger, and catalogs (`bin/check-catalogs`), plan-first and user-gated, with a hub-only duty over the methodology corpus in template repos. Ripple remains the forward-aimed complement (drift-prevention into drafted plans); `teach`'s stale pass remains transfer-scoped. |
| [Question Generation](https://aipatternbook.com/question-generation) | `stamp`; `plan-reviewer`'s `AskUserQuestion` | `stamp` interviews only when the description leaves an answer non-obvious. The plan reviewer is the sole role permitted to escalate a product decision to the human — and when it runs in an external venue where `AskUserQuestion` is unreachable, the unresolved question becomes a `REVISE` verdict stating the question. Graceful degradation of an escalation channel. |

---

## 9. Patterns the repo deliberately declines

Naming these matters as much as naming the ones it uses. Each refusal is traceable to a stated reason.

| Declined pattern | Where the refusal is recorded | Reason |
|---|---|---|
| [Worktree Isolation](https://aipatternbook.com/worktree-isolation) | `kickoff` Step 5 item 3 | The corpus's problem — two writers on one tree — is solved by **serialization instead**: "`kickoff` is sequential, so during this stage no native writer touches the tree." The single-writer guarantee is obtained without the worktree's setup cost and cleanup risk. |
| [Parallelization](https://aipatternbook.com/parallelization) / [Agent Teams](https://aipatternbook.com/agent-teams) | `briefs/methodology.md` §"What this methodology gives up" | The methodology trades throughput for a reviewable artifact per phase. Peer coordination has no place in a chain whose stopping condition is a human. |
| [Dark Factory](https://aipatternbook.com/dark-factory) | `policies/human-in-the-loop.md` § "Why this is the trade" | **Deliberately partial, and the line is drawn by criterion type rather than by activity.** Objective work runs lights-out through delivery; the parked set — manual, perceptual, product, custody, owner-only, and any unrun demo — never does. Explicit: "A project that wants no human judgment at all wants a different methodology; this one is wrong for that." The interesting claim is that autonomy and human judgment are separable at the *criterion*, not at the phase. |
| [Ralph Wiggum Loop](https://aipatternbook.com/ralph-wiggum-loop) | Convergence judgment + 10-cycle backstop | The corpus frames Ralph Wiggum as what happens when self-review has no teeth. Every loop here terminates on a *judged trend*, not on restart-until-it-looks-done. |
| [Continuous Deployment](https://aipatternbook.com/continuous-deployment) | Hard Rule 1; `policies/human-in-the-loop.md` | The pipeline runs to a commit and a fast-forward push, and stops. Deployment, release, tagging, and every other outward-facing act are out of scope by construction — as is the whole destructive git surface. |
| [Migration](https://aipatternbook.com/migration) / [Deprecation](https://aipatternbook.com/deprecation) / [Parallel Change](https://aipatternbook.com/parallel-change) | `policies/greenfield-until-released.md` | Suspended, not rejected — the policy has an explicit end condition. Pre-release, wrong shapes get replaced directly and every call site updated in the same phase. |

---

## 10. Antipatterns the repo structurally guards against

| Antipattern | The guard |
|---|---|
| [Approval Fatigue](https://aipatternbook.com/approval-fatigue) | Deliberately designed against: `policies/human-in-the-loop.md` — "each phase is small enough that reviewing it is fast; each END block is structured enough that the review is grep-able." One judgment per phase, not per action — and it is spent on the demo and the END block rather than on a commit whose evidence the human already has. |
| [Vibe Coding](https://aipatternbook.com/vibe-coding) | Every initial implementation gets independent code review; follow-up review may be skipped only after explicit risk/size classification, and acceptance remains empirical on every route. |
| [Shadow Agent](https://aipatternbook.com/shadow-agent) | Every role is registered in `policies/four-canonical-agents.md`, and every non-native venue is live-preflighted before use. An unregistered agent cannot enter the loop. |
| [Tool Sprawl](https://aipatternbook.com/tool-sprawl) | Each role has a minimal, fixed tool stance — the critic gets exactly Read, Grep, Glob. |
| [Cargo Cult Programming](https://aipatternbook.com/cargo-cult-programming) | `learn` and `teach` are plan-first with explicit tiering, and the 2026-06-14 LEARN entry records what was *skipped* as out-of-scope: "only the convention and the principle generalize." |
| [Speculative Generality](https://aipatternbook.com/speculative-generality) | `briefs/methodology.md` §6: sub-phases are JIT because "pre-decomposed sub-phases lock in premature assumptions." |
| [Benchmark Mirage](https://aipatternbook.com/benchmark-mirage) | Timeout calibration refuses vendor guidance and anecdote in favor of local p95 tails from `.kickoff/` telemetry. |
| [Big Ball of Mud](https://aipatternbook.com/big-ball-of-mud) | `policies/project-isolation.md`: nothing inside `project/` references anything above it, keeping the deliverable submodule-ready. |

---

## 11. Where the repo extends the corpus

Six structures here have no corresponding EACP entry. Each is a candidate contribution back.

1. **Mechanistic-vs-Intelligence triage** (`policies/mechanistic-vs-intelligence.md`). A per-task routing rule between deterministic script and agent, with the seam-splitting corollary — "the agent decides *what*, a deterministic script does the mechanical *how*." The corpus has `tool`, `hook`, and `determinism` but no article naming the triage decision itself. This is the repo's most transferable original idea.
2. **Review Lanes and proportional follow-ups** (`policies/review-lanes.md`). Risk-adaptive initial review *intensity* with a declared lane, plus correction-scale routing among direct fix, coder only, and full coder → critic cycle based on both risk and diff size. The critic can still escalate `light → full` mid-phase, and failed lightweight corrections upgrade to the full cycle. The corpus has no article on varying review depth by risk.
3. **Phase Ripple** (`policies/phase-ripple.md`). Propagating a closing phase's pinned decisions into downstream *drafted but unexecuted* plan files, classified AUTO (apply now) vs DECIDE (surface as a named follow-up). Adjacent to Garbage Collection but aimed forward at plans rather than backward at accumulated rules.
4. **Cross-Harness Parity** (`policies/cross-harness-parity.md`). A canonical-plus-mirror contract with a documented onboarding procedure for a third harness. `A2A` addresses agent interop at runtime; this addresses *configuration-surface* portability, which is a different problem.
5. **Fail-closed venue preflight** (`kickoff` Step 0b). One live sentinel call per unique `(CLI, model, effort, access mode)` target, in an empty temp directory, using production credential scrubs and flags — because "CLI presence, auth-status output, and credential files do not prove that precedence, entitlement, network, and the headless invocation all work together." A named pattern for *proving a delegation target is live before mutating any state* is missing from the corpus.
6. **Candidate-bound incremental assurance** (`briefs/incremental-orchestration.md`; `policies/orchestration-evidence.md`). A complete first review establishes stable findings; revision reviews consume causal packets and fail-closed rebase triggers; focused verification accelerates convergence; an implementation-candidate gate proves the unchanged approved candidate, and a second handoff gate proves the post-bookkeeping tree. The corpus contains the component patterns but not this assurance-preserving composition.

---

## 12. Gaps — patterns the corpus names and this repo does not show

Ordered by how actionable each one is here.

1. **[Architecture Fitness Function](https://aipatternbook.com/architecture-fitness-function) — closed 2026-08-10.** The document/ledger assertions `briefs/BRIEF.md` §7 specified are now encoded: `bin/check-catalogs` (registered as the `policy-catalogs` gate in `bin/check`, covered by `tests/test_check_catalogs.py`) enforces briefs/policies catalog sync, tracked internal-link integrity, and the lifecycle-aware phase-ledger state machine; `bin/lessons validate` (`policy-lessons` gate) enforces the lessons schema.
2. **[Eval](https://aipatternbook.com/eval) / [LLM-as-Judge](https://aipatternbook.com/llm-as-judge) — absent.** The repo tests its *machinery* (`tests/test_kickoff_config.py`) but never measures whether the four-role loop actually outperforms a single agent, or whether cross-vendor review outperforms same-vendor. The one quantitative claim in the repo (9.4 vs 2.4–4.0 findings) is cited from an external report, not measured locally. `briefs/BRIEF.md` §8 declares this out of scope — a defensible line, worth revisiting once telemetry accumulates.
3. **[Skill Fitness](https://aipatternbook.com/skill-fitness) — partially closed 2026-08-10.** Every skill now carries `last-reviewed:` frontmatter, and `sweep` re-reviews skills on cadence and can propose retirement. The corpus's *measured lift* discipline (with/without pass-rate comparison against a real oracle) remains deliberately declined at this scale — it requires an eval harness the template doesn't carry; `briefs/harness-self-improvement.md` §5 records the reasoning.
4. **[AgentOps](https://aipatternbook.com/agentops) — seeded, not built.** `.kickoff/role-timings.jsonl` is gitignored and per-repo. There is no aggregation across repos or over time, so the recalibration discipline has nothing to feed on until a single repo accrues 30 samples per target.
5. **[Structured Outputs](https://aipatternbook.com/structured-outputs) — partial schema adoption.** Findings and coder change metadata now use parity-safe fenced JSON validated by `bin/kickoff-evidence`. The terminal `## Verdict:` remains an exact sentinel because Claude lacks Codex's native output-schema facility; role-shape validation compensates but does not make the whole report schema-native.
6. **[Codebase Map](https://aipatternbook.com/codebase-map) — partial.** `plan/INDEX.md`'s critical-files map and `CLAUDE.md`'s layout section cover the *methodology* surfaces well; nothing maps the deliverable under `project/`. This gets worse as a derived project's deliverable grows.
7. **[Agentic Pull Request](https://aipatternbook.com/agentic-pull-request) — absent by design.** Work lands in the working tree with an END block; there is no branch, no PR, no session link. Hard Rule 1 makes this deliberate, but the END block already carries most of a PR body, so the gap is smaller than it looks.
8. **[Reflexion](https://aipatternbook.com/reflexion) — closed 2026-08-10.** Every revision round now requires the coder's failure analysis — *why* the previous attempt produced the findings, root cause not restatement — enforced fail-closed by `bin/kickoff-evidence capture-change`, carried in the revision packet's `## Failure analysis` section for the next review, and read by `kickoff` Step 9c as lessons-harvest sensor input.
9. **[MCP](https://aipatternbook.com/mcp) / [Retrieval](https://aipatternbook.com/retrieval) — absent, appropriately.** The planner has `WebSearch`/`WebFetch`; nothing else reaches outside the repo. Nothing in the methodology needs it.

---

## 13. Sources

- Encyclopedia of Agentic Coding Patterns, Wolf McNally, `https://aipatternbook.com` — retrieved 2026-07-23 via the `eacp` MCP server (295 articles, 292 draft; no pinned corpus revision available). Individual entries cited inline.
- Read in full before citation: `orchestrator-workers`, `generator-evaluator`, `prompt-chaining`, `externalized-state`, `compound-engineering`, `harness-engineering`, plus the `intent-and-scope` section overview.
- Repo evidence: `CLAUDE.md`, `briefs/methodology.md`, `briefs/BRIEF.md`, `briefs/cross-agent-invocation.md`, `briefs/incremental-orchestration.md`, `.claude/skills/kickoff/SKILL.md`, `kickoff.yaml`, `bin/README.md`, `bin/kickoff-tree-id`, `bin/kickoff-evidence`, `plan/INDEX.md`, `LOG.md`, and all 22 files under `policies/`.

## 14. Related briefs

- [`methodology.md`](methodology.md) — the eleven steps this map is a pattern-level reading of.
- [`BRIEF.md`](BRIEF.md) — the product brief whose §7 acceptance criteria gap 2 above proposes mechanizing.
- [`cross-agent-invocation.md`](cross-agent-invocation.md) — the source for nearly every Handoff, Bounded Autonomy, and Back-Pressure claim.
- [`incremental-orchestration.md`](incremental-orchestration.md) — candidate identity, stable findings, revision packets, the verification ladder, and protocol recovery.
- [`deterministic-orchestration.md`](deterministic-orchestration.md) — draft; the Prompt Chaining reading in §3 is the argument for why `kickoff`'s loop is a good candidate for deterministic encoding.
- [`harness-self-improvement.md`](harness-self-improvement.md) — the two-tier improvement flywheel that closed gap 1, partially closed gap 3, closed gap 8, and converted the Garbage Collection row in §8 from partial to implemented.
