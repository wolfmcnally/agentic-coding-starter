---
title: Session context compaction and long orchestration runs
date: 2026-09-04
status: methodology
scope: Dated harness instruction-loading facts, evidence continuity across compaction, historical arc measurements and the limits of structural verification.
---

Long orchestration runs need durable state that survives a conversation summary. Instruction discovery, instruction injection, explicit retrieval and available context capacity are different properties. This brief records the documentation inspected for those distinctions; it does not certify the live context of any session.

## 1. Harness facts

**As of 2026-09-04; Retrieved 2026-09-04.** These are official documentation claims, not live injection observations. Recheck against the selected harness version when behavior matters.

- **Codex root instructions.** The combined project-instruction budget is controlled by `project_doc_max_bytes`, documented with a 32 KiB default. A repository file’s byte size is only one contribution to the combined instruction chain. [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- **Codex skills.** Skill metadata is discovered before the complete skill body is loaded on selection. This progressive disclosure is separate from the project-instruction budget. [Codex skills](https://learn.chatgpt.com/docs/build-skills).
- **Claude startup and direct reads.** Ancestor/root instructions load at startup; nested instructions load when relevant files are read. Imports expand at startup, so moving text into an import does not reduce injected volume. Block HTML comments are removed during injection but remain visible to a direct Read. After compaction, root instructions are loaded again; nested instructions and scoped rules reload when relevant. [Claude memory](https://code.claude.com/docs/en/memory).
- **Claude supporting resources.** Skills can link adjacent supporting files and specify when to read them; `$ARGUMENTS` is the documented invocation-argument placeholder. Their existence does not imply every resource is loaded with the entry. [Claude skills](https://code.claude.com/docs/en/skills#add-supporting-files).
- **Claude compaction hooks.** `PreCompact` distinguishes manual and automatic compaction and can block; blocking at a hard context limit can fail the current request. `PostCompact` is a reaction event without decision control and discards `systemMessage` and `continue`, so those fields cannot restore instructions. `SessionStart` with the `compact` matcher can supply additional context. [Claude hooks](https://code.claude.com/docs/en/hooks).

The repository therefore uses a compact root and kickoff entry with explicit resource reads. Byte size measures file budget, links measure reachability, and load directives measure instruction form. Literal token checks can reject equivalent wording or approve contradictory prose; independent review must judge the instruction’s meaning. These checks do not establish live loading, adherence, effective context capacity or comparative model performance. An API context specification or settings pin does not establish CLI entitlement, remaining capacity or enabled harness features.

No blanket cross-harness claim is made about a model’s ability to invoke compaction or inspect its fill level. Use the selected harness’s actually exposed tools and measured telemetry; absent measurements are unknown. This refresh does not install hooks, tune thresholds, change permissions or introduce a context platform. Concise findings and dated links are retained without copying vendor-document bodies.

## 2. Why uncontrolled auto-compaction threatens evidence-bound work

Compaction replaces the conversation with a summary; what survives is what the summarizer judges important. If it fires at an arbitrary token count it can land mid-arc, where the orchestrator holds fine-grained verbatim state — candidate and instrument digests, exact critic findings, a live write-enabled coder. Summaries garble or drop exactly this class of detail, and the failure is silent: the orchestrator continues confidently with a slightly wrong hash or a forgotten invalidation. In a methodology whose value is claims bound to the exact candidate they describe, a mid-arc lossy event severs bindings invisibly — a green close whose chain of custody has a hole. The defense is not avoiding compaction; it is ensuring compaction only happens where the disk record (`LOG.md`, the run-scoped evidence store, the execution trace) fully carries resumption, so the conversation is disposable.

## 3. Historical session economics

**As of 2026-08; recorded in the earlier brief dated 2026-08-11.** Donor supervision recorded approximately 400K tokens for an implementation arc and 360K for a planning arc on a reported 1,000,000-token window. Two capacity pauses had mistakenly assumed a 200K window; a third omitted its arithmetic. These are historical observations from those runs, not current measurements, model rankings or universal phase-size rules. Do not scale them proportionally to another harness or infer that a phase requires two compactions. Measure a comparable local arc before projecting capacity.

## 4. Operating protocol

- Pause at externalized-state boundaries where the approved plan, candidate identity, findings, run directory and actual lifecycle are recoverable from disk. Do not deliberately pause mid-atomic operation or start one that measured capacity cannot accommodate.
- A capacity pause shows current measured usage, the nearest comparable measured arc cost and the projected end state against the known session limit. If any input is unavailable, state it as unknown; do not invent a reassuring capacity value.
- Before continuation, read the durable resume record, re-read the active behavioral instructions and required stage resource, and verify the carried plan, candidate and outstanding findings against their original authorities. A summary or surviving filename is not custody evidence.
- Loss of trustworthy review continuity requires a complete rebase. Authority changes follow truthful park and fresh capture, never edited hashes. Completed phases retain their history.

## 5. Automation option remains unimplemented

Any future compaction automation would need version-specific qualification of its trigger, veto, restoration channel and hard-limit failure behavior. The former proposal’s unsupported threshold override and `PostCompact` reinjection assumptions are withdrawn. `SessionStart` is a documented context channel, but documentation alone does not establish that a hook is installed, trusted, invoked or effective in a selected session. A stale veto could block useful compaction until a request fails; any future design must prove its own failure controls. This phase adds no hook or lifecycle machinery.
