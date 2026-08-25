---
title: Session context compaction and long orchestration runs
date: 2026-08-11
status: methodology
scope: Managing harness context compaction during multi-hour orchestration sessions — what the harness permits, what the model can and cannot observe or trigger, measured per-arc token costs, the safe-boundary pause protocol, and a hook-based automation option.
---

Long `kickoff` phases can outlast a single conversational context, and production runs in a donor repo surfaced a repeating failure mode: the orchestrator pausing on a wrong belief about its own capacity, and the operator lacking a shared vocabulary for when a pause is justified. This brief pins the harness facts (verified against Claude Code documentation in 2026-08; re-verify before relying on them), the measured economics, the operating protocol that works today, and an unimplemented automation option.

## 1. Harness facts

- **The model cannot invoke `/compact`.** Slash commands are parsed from the user input loop before anything reaches the model; no output the model produces can trigger a compaction.
- **The model cannot see its own context fill level.** No meter or warning is exposed in-band. Auto-compaction fires silently at roughly 95% of the window. Consequence: any capacity estimate the orchestrator produces is folklore unless the operator injects ground truth — which is exactly how phantom pauses happen (§3).
- **The auto-compact threshold is tunable** via the `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` environment variable (1–100; third-party-documented, re-verify before relying on it).
- **A `PreCompact` hook can block a compaction** (exit code 2 or `{"decision": "block"}`), with separate matchers for `manual` and `auto` triggers. It cannot *start* one.
- **A `PostCompact` hook runs after compaction completes** and can re-inject context (e.g. resumption pointers); it cannot block.
- **The Agent SDK exposes no compaction API**; headless runs inherit the same harness behavior.

## 2. Why uncontrolled auto-compaction threatens evidence-bound work

Compaction replaces the conversation with a summary; what survives is what the summarizer judges important. If it fires at an arbitrary token count it can land mid-arc, where the orchestrator holds fine-grained verbatim state — candidate and instrument digests, exact critic findings, a live write-enabled coder. Summaries garble or drop exactly this class of detail, and the failure is silent: the orchestrator continues confidently with a slightly wrong hash or a forgotten invalidation. In a methodology whose value is claims bound to the exact candidate they describe, a mid-arc lossy event severs bindings invisibly — a green close whose chain of custody has a hole. The defense is not avoiding compaction; it is ensuring compaction only happens where the disk record (`LOG.md`, the run-scoped evidence store, the execution trace) fully carries resumption, so the conversation is disposable.

## 3. Measured session economics

Measured in a donor project during out-of-band supervision of two consecutive phases, on a 1,000,000-token window:

- **An implementation arc** (baseline retake → coder dispatch → two critic rounds → post-change evidence → acceptance close) consumed ≈ **400K tokens**.
- **A planning arc** (JIT decomposition plus three plan/review rounds) consumed ≈ **360K tokens**.
- **Pause history:** two pre-implementation pauses cited "session capacity remaining" — both phantom, calibrated to a 200K window the session was not running. A third pause was arithmetically sound but its report said only "more than was left," which is unauditable.

Rule of thumb pending better data: **a full implementation arc costs ~400–600K tokens; a planning arc ~300–400K; one phase ≈ two compaction cycles** (plan arc, compact, implement arc). Scale proportionally on smaller windows.

## 4. Operating protocol (current, works)

- **Pause only at externalized-state boundaries** — plan approved, phase closed — where the disk record fully carries resumption and the conversation is disposable. Never pause inside an atomic block (baseline capture, coder watch, acceptance close); conversely, never *start* an atomic block that projected arithmetic says will not fit in the remaining window.
- **A capacity pause must show its arithmetic**: current usage, the measured cost of the nearest comparable completed arc, and the projected end state against the window. "More than was left" is not a pause justification.
- **The operator relays `/compact` at the boundary**, then re-invokes with a short directive naming the resumption anchors (approved-plan hash, candidate id, run directory). Observed to be lossless when the resumed run re-verifies the carried-forward plan against the tree rather than trusting memory.

## 5. Automation option (unimplemented)

The primitives in §1 compose into "compact only at safe places" without granting the model any new authority — the workflow declares when compaction is *unsafe* rather than the model choosing when it happens:

- The orchestrator drops a marker file on entering an atomic block and removes it at each safe boundary (the stage machinery in `bin/kickoff-evidence` already knows these transitions).
- A `PreCompact` hook with the `auto` matcher blocks auto-compaction while the marker exists.
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is lowered (~80) so, past the threshold, compaction fires at the first safe boundary rather than at 95% mid-arc.
- A `PostCompact` hook re-injects the resumption pointers (run directory, candidate and plan hashes) as insurance against any compaction that does land.

**Caveat:** blocking auto-compaction borrows against a hard ceiling. A long atomic block while blocked can reach the true limit with no escape valve; the pattern requires the lowered-threshold margin and strict marker cleanup (a stale marker wedges the session at the limit).

## Sources

- Claude Code tools, hooks, and context-window documentation (code.claude.com/docs) — re-verify §1 against current docs before implementing §5.
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`: third-party documentation; re-verify against official docs before implementing §5.
- Arc measurements: out-of-band supervision records from a donor project's production orchestration runs, 2026-08. Refresh §3's rule of thumb as local phases add arc-cost data points.
