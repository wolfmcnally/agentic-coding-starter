---
name: demo
description: >-
  Walk a human through an approved user-demo protocol one visible action at a
  time. Explain the purpose of the next action, let the user perform or observe
  it, answer questions without advancing, and preserve a durable resume point.
  Use when the user asks to run, try, or work through a phase demo interactively.
last-reviewed: 2026-08-23
---

# Demo — Interactive human evaluation

Run an existing `User Demo:` protocol as a conversation. This skill evaluates
the delivered surface; it does not implement or repair it.

## Authority

Read [`policies/user-demo-protocols.md`](../../../policies/user-demo-protocols.md)
in full, then locate the approved demo in the phase file, END block, or report.
If no approved protocol exists, stop and identify the missing authority rather
than inventing a new acceptance contract.

Every turn of a demo is addressed to the operator, so narrate in the [`plain`](../../../.claude/skills/plain/SKILL.md)
register: say what the next action is for and what to look for, not how the
code underneath it works.

## One visible action per turn

For each protocol action:

1. Perform every safe, invisible prerequisite the user does not need to see.
2. Explain plainly what the next visible action tests and what the user should
   notice.
3. Give exactly one action for the user to perform or one observation for the
   user to judge.
4. Stop. Answer questions about that action without advancing.
5. Advance only after the user reports the result or explicitly asks to move
   on.

Never batch several interactive steps into one response. The user must be able
to distinguish which action produced which observation.

## Classify disagreement before acting

When the observed result differs from the protocol, classify it before
proposing a response:

- **Product:** the delivered behavior appears wrong.
- **Demo:** the protocol, expectation, or explanation appears wrong or stale.
- **Environment:** setup, permissions, data, hardware, or venue prevented a
  valid observation.

State the evidence and uncertainty. Suspect the measuring tool before
overruling a repeated direct user observation. A single observation that fits
multiple causes does not identify the mechanism; say what next visible action
would distinguish them.

## Durable resume

At every stop, keep a compact resume record in the conversation: protocol
source, last completed action, observed result, classification if any, and the
next action. If the session must end mid-demo, write that record to the
project's designated continuation surface without recording secrets or private
input.

## Boundaries

- Do not edit code, policies, plans, tests, or demo text during the demo.
- Do not commit, push, deploy, publish, or mutate external state beyond the
  protocol's explicitly approved action.
- Record defects and proposed corrections for routing after the demo.
- A user question pauses progression; answer it, then re-present the same next
  action unless the user changes the decision.

At completion, summarize the observed outcomes, unresolved classifications,
and any follow-up work. Do not claim subjective acceptance for the user.
