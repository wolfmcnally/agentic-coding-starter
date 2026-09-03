---
name: ask
description: >-
  Surface every open loop, unresolved decision, deferred choice, or unconfirmed
  assumption in the current work and put them to the operator through the
  harness's structured ask-user-question tool, batched into one interaction
  with concrete options. Use when the operator types /ask (Claude Code) or
  $ask (Codex), asks "what do you need from me," "anything you need decided,"
  or "ask me whatever you're stuck on." Operator-invoked only; the model never
  triggers it, so it can never fire while the work is unattended.
disable-model-invocation: true
argument-hint: "[optional topic to scope the questions]"
---

# Ask Skill

Collect the decision points in the current work that genuinely require the operator, and put them back as concrete, answerable questions through the harness's interactive ask-user-question tool — rather than guessing, silently assuming, or stalling.

The operator's optional scope: `$ARGUMENTS` — if present, restrict the inventory to open loops touching that topic; if empty, sweep the whole current context.

## Who invokes it, and what that settles

This skill runs only when the operator types it. That fact does two jobs. It means the operator is present and asking to be interrupted, so raising the harness's interactive question control is the right response even in a session that otherwise runs unattended and would park its questions in an artifact. And it means the skill cannot be the thing that blocks unattended work: a model-initiated escalation goes through the repo's own route for operator decisions (in this methodology, `kickoff`'s operator-input park and the `plan-reviewer`'s `blocked-owner` finding), not through this skill.

## What counts as an open loop

Include only items where the operator's answer changes what happens next:

- A decision deferred or postponed earlier in the session ("we can decide this later").
- A fork between two or more valid approaches, where the right one depends on the operator's preference, priorities, or context the work can't supply.
- An assumption already acted on that should be confirmed before it compounds (a default chosen, a name picked, a scope guessed).
- A blocker that only the operator can clear (credentials, access, an external action, an owner-only call — the kind of item the work would otherwise file in the repo's human-only action queue, `user-actions/` under this methodology).
- A piece of missing information without a sensible default.

**Exclude** anything resolvable from the request, the code, the repo's policies, or an obvious convention. Those you decide yourself and mention in passing — never manufacture a question to fill the list. Where the repo states how autonomous an agent should be (in this methodology, `policies/human-in-the-loop.md`), that setting governs how much reaches this list; absent one, only genuinely ambiguous calls with real consequences belong here.

## Process

1. **Inventory.** Scan the current working context (and the scope argument, if given) for open loops matching the definition above. Deduplicate and merge near-identical items. Where the repo keeps a human-only action queue, read its open items too: an open item that the current work depends on is an open loop even if this session never mentioned it.

2. **If there are none**, say so plainly in one line — e.g. "No open decisions; nothing blocking. Proceeding." — and stop. Do not invoke the ask-user tool with invented questions.

3. **Formulate.** Turn each open loop into one self-contained question:
   - A clear question ending in a question mark, understandable without re-reading the whole session.
   - 2–4 concrete, mutually exclusive options (unless the choices genuinely combine — then allow multiple selection).
   - When you have a recommendation, make it the **first** option and append "(Recommended)" to its label; give a one-line rationale per option covering the trade-off.
   - A short header label (≤12 chars) naming the decision.
   - Compose it in the repo's operator register where one is defined. In this methodology that is `plain`, whose "Shape of a decision" and "Batching" sections govern the form: the explanation goes in the message before the control, because option labels are a few words wide and cannot carry the consequence of a wrong call. The rules below are the minimum that holds anywhere.

4. **Ask, batched.** Present the questions through the harness's structured ask-user-question tool in as few interactions as the tool allows (Claude Code's `AskUserQuestion` takes up to 4 questions per call; batch the rest into follow-up calls). If the active harness has no structured ask-user tool, or has one that is unavailable in the current mode (check before calling: for example, a tool that exists only in a planning mode while the session is in its default mode), present the same numbered questions as plain text and wait for the answers. The operator can always answer "Other" / free-text, so phrase options to leave that room.

5. **Order by leverage.** When there are more questions than one batch holds, ask the highest-consequence and most-blocking ones first.

6. **Act on the answers.** Apply each answer to the work. If an answer opens a new fork, you may ask one follow-up round — but converge; don't interrogate. Record any answer that is an owner-only call wherever this repo tracks such decisions, so it isn't lost: under this methodology a ruling on the work lands in the governing phase file or brief, and an action only the operator can perform is filed in `user-actions/` per `policies/user-actions.md`. Elsewhere, find the surface rather than assuming a filename: repos differ, and a note written to a path that does not exist is the same as no note.

## Rules

- **Never fabricate questions.** An empty inventory is a valid, good result.
- **Decide what you can; ask only what you must.** Default reflex is to resolve it yourself; escalate to the operator only for genuine, consequential ambiguity.
- **One concept per question.** Don't bundle two decisions into one prompt.
- **Lead with a recommendation** whenever you have a defensible one — the operator should be able to ratify a default in one click, not author a plan.
- **Batch, don't drip.** Gather the full inventory first, then ask; don't fire one question, act, and discover the next mid-stream when they were all visible up front.
- **Harness-neutral.** This skill names no harness-specific tool as a requirement; it uses whatever interactive ask-user mechanism the running harness provides, and falls back to numbered plain text when none is usable.
- **Repo-neutral.** Every path named above is a citation of this methodology's surfaces, not an instruction to write there. In a repo that lacks them, the skill still runs; only the recording step has to locate its surface first.
