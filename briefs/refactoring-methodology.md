---
title: "Refactoring: Method, Evidence, and the Size of the Skill"
date: 2026-10-01
status: implemented
scope: Why the `refactor` skill says what it says and no more — the method it rests on, the published evidence about agents and refactoring, the vendors' guidance for the current models, and the evaluation that sized its instructions.
---

# Refactoring: Method, Evidence, and the Size of the Skill

This brief is the reasoning behind [`.claude/skills/refactor/SKILL.md`](../.claude/skills/refactor/SKILL.md). It records what refactoring means in this methodology, why a skill is warranted when the models already know how to refactor, how much instruction the current models were found to need, and what was considered and left out. Every external claim carries the date the source bears and the date it was read, because most of this evidence will age quickly.

All sources were retrieved 2026-10-01. Paper findings are from abstracts unless noted.

## 1. What refactoring means here

Refactoring changes the internal structure of working code and nothing a caller can observe. The term and its first catalog of behavior-preserving transformations are Opdyke's (1992); Fowler's *Refactoring* (1999, second edition 2018) supplied the working vocabulary of named moves and the discipline of small verified steps [1][2]. The Encyclopedia of Agentic Coding Patterns states the consequence for agents: because behavior must not change, "the existing tests *are* the acceptance criteria," and a vague request to "clean this up" is the one that produces surprising changes [3].

Three commitments follow, and the skill keeps all three.

- **Structure and behavior never share a change.** Beck's rules for an agent say "Never mix structural and behavioral changes in the same commit" and "Refactor only when tests are passing" [4]. A study of 3,691 agent patches found that refactoring tangled into other work is strongly associated with reduced compilability [5].
- **A bug found on the way is reported, not fixed.** Fixing it changes behavior, which is a different task with a different reviewer's eye.
- **The tests pass as they were.** A refactoring that needs an assertion edited to pass has changed behavior [6].

## 2. Why a skill is warranted

**Agent-written code degrades as it grows.** Across 36 problems that agents extended repeatedly, structural erosion rose in 77% of trajectories and verbosity in 75.5%; agent code was 2.3 times more verbose than a sample of human repositories, and explicit quality guidance improved the starting point without changing the rate of decay [7]. A commit-level study of 623 million changes reports duplicated blocks per million changed lines rising from 40.3 in 2023 to 73.0 in 2026 to date, while moved code, its proxy for refactoring, fell from 21% of changed lines in 2022 to 3.8% [8]. A practitioner's account of building an application with agents found the agent "was definitely compounding inadvertent technical debt" when neither a person nor a separate review looked at structure, and that it re-implemented behavior it could have reused [9]. Cleanup has to be asked for.

**On an ordinary task the current models are told to leave neighboring code alone.** Anthropic's guidance for Fable 5.1 is that when the model finds "a pre-existing bug, a performance concern, or behavior the task doesn't mention," it should not fix it in that change and should report it as a follow-up; its guidance for Opus 5 is "Deliver what was asked, at the scope intended" [10][11]. That is the right default, and it is why refactoring needs its own invocation: the skill is an explicit grant to do what the default withholds, so it has to say how far the grant goes.

**The existing tools each cover part of the ground.**

| Tool | What it contributes | What it leaves open |
|---|---|---|
| Claude Code's bundled `simplify` [12] | Four review angles for the current change: reuse of existing helpers, simplification, efficiency, and whether the change is at the right level of abstraction. It names the simpler form and skips a finding it would have to argue for. | One harness. The current change only. No rule for what may be applied without asking. |
| Anthropic's `code-simplifier` agent [13] | Clarity over brevity, and an explicit warning against over-simplifying. | Hard-codes one stack's conventions. |
| Osmani's `code-simplification` [6] | The rule that tests pass without modification; refactoring kept apart from feature work. | Thirteen kilobytes of tables and examples the current models do not need. |
| Pocock's `improve-codebase-architecture` [14] | The deletion test — if removing a module makes complexity vanish, it was a pass-through — and looking first where the code changes most. | It is a discovery and discussion tool; it does not apply or deliver changes. |
| Cursor's `deslop` [15] | A list of generated-code residue: unnecessary comments, abnormal defensive checks, type escapes. | It permits fixing "a clear bug" in the same pass. |
| desloppify [16] | Nothing adopted. | It depends on an installed scanner and optimizes a score, which its own notes say is not comparable between code bases. |
| OpenAI's Codex refactoring guidance [17] | "Pick one cleanup theme at a time"; keep "stack changes, dependency migrations, and architecture moves as separate tasks." | It is guidance for a prompt, not a shipped skill. |

None of them states an authority boundary, and none runs the same way under both harnesses this methodology supports.

## 3. How much instruction the current models need

The first design for this skill prescribed a verification procedure for every step. The published evidence invited it: a bare model produced compiling, test-passing refactorings 8.7% of the time against 82.8% for a system with retrieval, review and repair [18]; static repair followed by test-guided repair reached a 94.2% cumulative pass rate [19]; 13 of 176 suggested refactorings in an earlier study changed behavior or broke syntax [20]. Those studies measured older models, or models with no ability to run anything.

The vendors' guidance for the current models points the other way, and both vendors say so in nearly the same words.

- Anthropic, on Opus 5, whose guide Opus 5.5 inherits as its starting point: the model "verifies its own work without being told to. If your prompt contains explicit verification instructions ... remove them: instructions like these cause over-verification," and "the same applies to legacy harness scaffolding that adds separate verification steps" [11][21]. For all current models: "Prefer general instructions over prescriptive steps" [22]. For skills: "Default assumption: Claude is already very smart. Only add context Claude doesn't already have," establish a baseline without the skill, and "write minimal instructions" for the gaps that baseline shows [23].
- OpenAI, on the GPT-6 family: "Run tests appropriate to the change and complete required checks. Once those pass, broaden or repeat testing only when new changes, failures, or unresolved concerns justify it." It adds that the model "can be more sensitive to instructions contained in skills and other files," and recommends auditing them [24].

Independent evidence still shows frontier models failing at refactoring, but at a different scale from this skill's. On whole-repository migrations only 28 of 520 runs passed a migration audit, a fixed test suite and independently generated tests for hidden differences; the best model scored 47 of 100 [25]. On multi-file refactorings averaging 11.4 files the best result was a 41.2% resolve rate [26]. Agents left alone refactor small and local — renames and type changes dominate [27], or annotation edits [28] — and the best agent removed about half of a set of seeded smells for lack of cross-file understanding [29]. One well-informed agent beat a delegating configuration on multi-file refactoring, 86% to 66% [30].

Vendor guidance is not independent of the vendor, and no published result measures these models on small, local refactorings with and without added instruction. So the question was put to the models directly.

## 4. The evaluation

The pack and its scoring rules are in `tests/fixtures/refactor_evaluation/`; its README is the authority on how to run it. In short: a thirteen-file package is seeded with one problem per thing the skill looks for, three decoys that look like problems and are not, three traps where the obvious simplification changes behavior no shipped test covers, and two tempting changes that are not local. A held-out probe compares 73 observable outcomes between the original and the candidate. The instruments were proven first: a correct reference refactoring passes, and a deliberately wrong one passes the shipped tests while failing 13 probes.

Each of the four models the methodology names was run once with a bare request — "Refactor and simplify the code in `shop/` without changing its behavior." — and then with the skill in each of four wordings, ending with the one shipped. Every run was at the effort this repository starts that model at. Claude Code's `simplify` was run once on the lead Claude model. The bare runs came first, and the skill was written from what they showed.

### Bare runs, 2026-10-01

| Arm | Behavior | Local seeds addressed, of 8 | Decoys | Traps | Non-local change |
|---|---|---|---|---|---|
| Opus 5.5, medium | One probe differs | 8 | Intact | Intact | Deleted the forwarding module, and said so |
| Fable 5.1, high | Preserved | 8 | Intact | Intact | Kept the module and proposed deleting it |
| GPT-6.1 Sol, medium | Preserved | 4 | Intact | Intact | None |
| GPT-6 Astra, high | Preserved | 3 | Intact | Intact | None |
| `simplify` on Opus 5.5 | One probe differs | 8 | Intact | Intact | Deleted the forwarding module, and said so |

Every bare model avoided every trap and every decoy, and the Claude models said why: the rounding function that only looks like a duplicate, the broad exception handler whose narrowing would change results, the checks documented as belonging to different owners. Each verified its own work without being asked — the Claude models by comparing outputs before and after, the Codex models by adding tests that pin boundaries before changing code. Nothing in the bare runs supports adding instruction about technique, verification, or what to leave alone.

Two things did go wrong, and they are the two things the skill addresses.

- **Authority.** The lead Claude model, with and without `simplify`, deleted a public module because nothing inside the package still needed it. It reported the deletion plainly, but it made it. That is a change another caller can observe, and whether to make it is the operator's call.
- **Reach.** The two Codex models stopped after the most visible problems and left dead code, write-only state, repeated work and a duplicated special case in place.

### Runs with the skill

| Arm | Behavior | Local seeds addressed, of 8 | Decoys and traps | Forwarding module |
|---|---|---|---|---|
| Opus 5.5 | Preserved | 8, 8, 8, 8 | Intact | Kept; deletion proposed |
| Fable 5.1 | Preserved | 8, 7, 8, 8 | Intact | Kept; deletion proposed |
| GPT-6.1 Sol | Preserved | 6, 6, 6, 7 | Intact | Kept; deletion proposed |
| GPT-6 Astra | Preserved | 7, 7, 7, 7 | Intact | Kept; deletion proposed |

The four figures are the skill as first written, after one revision of its wording, with two sentences of that revision removed, and as shipped. No arm with the skill did worse than the same model without it on behavior, tests or decoys, and none touched the test file.

- **Authority closed.** Every arm kept the public module and proposed its removal. None changed what the pricing function returns for the special-cased product; the arms that raised it proposed it.
- **Reach improved.** Sol went from 4 seeds to 7 and Astra from 3 to 7. The Claude models were already at 8.
- **A first revision made three changes, and one of them worked.** Run with the first wording, the lead Claude model created a branch for its commit; naming the current branch stopped that. Sol declined to hoist a repeated computation because it changes how often an overridable method is called, and proposed it instead; a sentence saying that the amount of work is not something a caller observes did not change its reading. Neither Codex model named a repeated special case once inside the module, and a sentence saying to apply the local part of a fix did not change that either. On the operator's ruling those two sentences were removed and the four arms run again; nothing regressed.
- **The sentence that failed had answered the wrong objection.** Sol never argued about the amount of work. Its stated reason, three times, was that an override of the method might notice being called less often. One sentence aimed at that reason — what can be observed is judged by the callers, subclasses and overrides that exist, not by ones that could be written, except where the project documents a class as an extension point — was added and the four arms run again. Sol applied the change, and no arm regressed: each still kept the public module and left the interface with two implementations alone. The lesson is general: when an instruction does not take, read the model's stated reason before writing the next one.
- **Under the shipped wording the harnesses agree on every finding.** The shipped skill is the first wording, the clause naming the current branch, and that sentence.

Fable's count went from 8 to 7 and back to 8 across the wordings on one run each, which is within what chance alone could produce.

### Limits of this evaluation

One small package and one run per arm and wording, twenty-one sessions in all: it can show that a skill does harm or that a bare model has a gap, and it cannot rank models or measure rates. Claude Code arms ran with the operator's own instructions and skills excluded. Codex has no equivalent switch for its machine-wide instruction file, so the Codex arms ran with the operator's instructions loaded, which include verification discipline; a recipient without such a file may see weaker bare behavior from those models than is recorded here. The package is Python and the problems are the common ones; nothing here speaks to a large or unfamiliar code base.

## 5. The design that resulted

Each statement in the skill is one of three things: a fact about this repository that a model cannot know, a boundary of scope or authority, or the answer to a failure a run showed. Two sentences that were tried against such failures and did not cure them were taken out again (§4). Nothing else is in it.

- **Scope** is a boundary. The default is the current change, as with `simplify`; a named target and a whole-project survey extend it. The survey proposes only, because the evidence on decay argues for a periodic look [7][9] and the evidence on large refactorings argues against applying one unreviewed [25][26].
- **What to look for** answers the reach failure. Naming the kinds of problem is the cheapest instruction with evidence behind it: naming the refactoring type and narrowing the search raised one model's detection of refactoring opportunities from 15.6% to 86.7% [20]. The list includes fixes at the wrong depth and modules that hide nothing, because agents left alone stay at the level of names and types [27][28][29]. The tests for needless structure are cited from the repository's existing simplicity rule, not restated.
- **Who decides** answers the authority failure. A change is applied when it stays inside one module and alters nothing another module, an outside caller, or a stored format can observe, judged by the callers, subclasses and overrides that exist; anything else is proposed; cross-cutting work becomes a phase sketch and is not started.
- **Done** is the definition in §1.
- **Delivery** is repository fact: during a phase the pass belongs to that phase and makes no commits; outside one, refactoring is committed on the current branch, apart from behavior changes, under the repository's ordinary commit and gate rules; undo means reversing one's own edits, never the destructive git commands reserved to the operator.

The skill uses what both harnesses read — a name, a description within the open skill format's 1,024 characters [31], and plain instructions — plus an argument hint that only Claude Code displays. It depends on no subagent, planning mode or harness-specific tool.

## 6. Considered and left out

Recorded so they are not rediscovered as omissions. Each returns only as the answer to an observed failure.

- **A per-step verification procedure, a step ledger, and a closing re-read of the diff.** Every bare model verified its own work, and both vendors say such instructions cost tokens and add nothing on these models.
- **Proving the tests cover the target before editing it.** Tests that pass do not prove behavior was preserved when nothing tests the target [9][25]. The bare models handled this unprompted, by differential checks or by pinning behavior first.
- **Warnings about look-alikes and deliberate code.** No bare model touched a decoy.
- **A catalog of smells and named refactorings.** The models know it; the six lines in the skill were enough.
- **Deterministic refactoring engines for mechanical edits.** The case for them is real — re-applying a model's proposal through a tested engine removes unsafe cases [20], and large migrations pair a model with automated discovery of the places to change [32] — but nothing at this scale called for it, and the engines have defects of their own [33].
- **Parallel reviewers.** `simplify` uses four; the evidence on delegation for refactoring is unfavorable for edits [30] and silent on finding, and a single path keeps both harnesses identical.
- **A health score or new detector dependencies.** A score invites optimizing the number.
- **Wiring into `kickoff`.** The coder's existing removal and indirection passes are unchanged. Revisit when the review-loop sweeps show critics still finding what this pass would have caught.

## 7. When to revisit

Re-run the evaluation pack when a model the methodology names is replaced, and before adding any instruction to the skill. The lead model changed on both sides in the ten days before this brief was written. An instruction that a newer model no longer needs should be removed, not kept for safety: on these models an unneeded instruction is a cost, not a margin.

## Sources

1. William Opdyke, *Refactoring Object-Oriented Frameworks*, PhD thesis, University of Illinois, 1992. As of 1992.
2. Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 1999; second edition 2018. As of 2018.
3. Encyclopedia of Agentic Coding Patterns, "Refactor", https://aipatternbook.com/refactor, and "Garbage Collection", https://aipatternbook.com/garbage-collection. As of 2026-08-31 (corpus date).
4. Kent Beck, agent rules published in the BPlusTree3 repository, `rust/docs/CLAUDE.md`, https://github.com/KentBeck/BPlusTree3. As of 2025-09 (last push). The same rules are described in his "Augmented Coding: Beyond the Vibes", https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes, 2025-06-25.
5. Tian et al., "'Refactoring Runaway': Understanding and Mitigating Tangled Refactorings in Coding Agents for Issue Resolution", arXiv:2605.22526. As of 2026-05-21.
6. Addy Osmani, `code-simplification` skill, https://github.com/addyosmani/agent-skills. As of 2026-09 (last push).
7. Orlanski et al., "SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks", arXiv:2603.24755. As of 2026-05-07 (second version).
8. GitClear, "The Maintainability Gap: AI Code Quality in 2026", https://www.gitclear.com/the_ai_code_quality_maintainability_gap. As of 2026; the page carries no single date and reports data through the first half of 2026.
9. Birgitta Böckeler, "Maintainability sensors for coding agents", https://martinfowler.com/articles/sensors-for-coding-agents.html. As of 2026-05-27.
10. Anthropic, "Prompting Claude Fable 5.1", https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1. As of 2026-10-01 (living page).
11. Anthropic, "Prompting Claude Opus 5", https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5. As of 2026-10-01 (living page).
12. Anthropic, Claude Code commands reference, `/simplify`, https://code.claude.com/docs/en/commands. As of 2026-10-01 (living page). The absence of a verification step was observed in the prompt of the locally installed Claude Code 2.1.287; that prompt is proprietary and is described here, not reproduced.
13. Anthropic, `code-simplifier` agent, https://github.com/anthropics/claude-plugins-official. As of 2026-09 (last push).
14. Matt Pocock, `improve-codebase-architecture` and `codebase-design` skills, https://github.com/mattpocock/skills. As of 2026-09 (last push).
15. Cursor, `deslop` skill, https://github.com/cursor/plugins. As of 2026-09 (last push).
16. desloppify, skill and scoring notes, https://github.com/peteromallet/desloppify. As of 2026-05 (last push).
17. OpenAI, "Refactor your codebase", https://learn.chatgpt.com/use-cases/refactor-your-codebase. As of 2026-10-01 (living page).
18. Xu et al., "MANTRA: Enhancing Automated Method-Level Refactoring with Contextual RAG and Multi-Agent LLM Collaboration", arXiv:2503.14340. As of 2025-03-27.
19. Cordeiro, Noei and Zou, "RefactorAssist: Agentic Refinement for Reliable Code Refactoring", arXiv:2608.00924. As of 2026-08-02.
20. Liu et al., "An Empirical Study on the Potential of LLMs in Automated Software Refactoring", arXiv:2411.04444. As of 2024-11-07.
21. Anthropic, "Prompting Claude Opus 5.5", https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5. As of 2026-10-01 (living page).
22. Anthropic, "Prompting best practices", https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices. As of 2026-10-01 (living page).
23. Anthropic, "Skill authoring best practices", https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices. As of 2026-10-01 (living page).
24. OpenAI, "Using GPT-6", https://developers.openai.com/api/docs/guides/latest-model. As of 2026-10-01 (living page). The page says its prompts "address behavior observed with GPT-6 Astra."
25. "SWE Refactor Bench: Can Coding Agents Complete a Long-Horizon, Whole-Repository Stack Migration?", arXiv:2608.23564. As of 2026-08-24.
26. Shi et al., "SWE-Bench ProMax: Benchmarking Agents on Large-Scale Multilingual Code Refactoring", arXiv:2608.09802. As of 2026-08-10.
27. Horikawa et al., "Agentic Refactoring: An Empirical Study of AI Coding Agents", arXiv:2511.04824. As of 2025-11-06.
28. Ottenhof et al., "How do Agents Refactor: An Empirical Study", arXiv:2601.20160. As of 2026-05-24 (second version).
29. Lin et al., "SmellBench: Towards Fine-Grained Evaluation of Code Agents on Refactoring Tasks", arXiv:2606.05574. As of 2026-06-04.
30. Ben Amor et al., "RefactorPlatform: An Open-Source Harness for Controlled Evaluation of Repository-Scale Refactoring Agents", arXiv:2609.04898. As of 2026-09-04.
31. Agent Skills specification, https://agentskills.io/specification. As of 2026-10-01 (living page).
32. Ziftci et al., "Migrating Code At Scale With LLMs At Google", arXiv:2504.09691. As of 2025-04-13.
33. Oliveira et al., "Detecting Behavioral Changes in Python Refactoring Implementations with Foundation Models", arXiv:2608.09919. As of 2026-08-10.
