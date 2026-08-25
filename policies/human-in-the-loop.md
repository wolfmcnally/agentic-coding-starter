# Policy: Human In The Loop

The methodology assumes a human's judgment governs the work. This policy says exactly where that judgment binds — and, because it does not bind everywhere, where the orchestrator proceeds without asking.

The human gate lives at the **seam**: the phase boundary, where the human reads the END block, runs the demo protocol, and decides whether the work is right. It does not live on the commit. A clerical Git handoff is not judgment; it is the place judgment used to be parked.

## The acceptance boundary

Every acceptance criterion is one of two kinds, and the kind decides who closes it.

**Objective criteria close autonomously.** A criterion is objective when all four hold:

- It is **executable** — a shell command, a named test, an analyzer output — with a success condition defined before it was run.
- It was **independently reviewed** — the implementing role did not review its own work (`four-canonical-agents.md`).
- A **complete gate** proved it (`build-gates.md`), against the exact candidate the review approved (`orchestration-evidence.md`).
- Its result is **recorded** and candidate-bound, not asserted.

**Subjective and owner-only criteria always park.** No amount of green closes them:

- Named manual checks (`acceptance-empirical.md` § When acceptance can't be automated).
- Perceptual, aesthetic, UX, and readability judgment.
- Product decisions — whether this is the right feature, not whether it works.
- Custody: credentials, billing, third-party accounts, anything behind a console, dashboard, or GUI the orchestrator cannot reach.
- An unrun `User Demo:` protocol (`user-demo-protocols.md`). The demo is the human's acceptance surface; the orchestrator surfaces it and never answers it.

**Delivery is not acceptance, and it does not wait on acceptance.** A commit is bookkeeping that follows the handoff gate; it changes no tracked content and settles no judgment. A phase whose gates are green is delivered even though its parked criteria are still open — that is the normal state at a seam, not an anomaly. Being committed does not mean the phase was liked. If the user judges it wrong afterward, the correction is an ordinary follow-up commit; nothing about delivery makes a rejection harder, because the destructive git surface stayed with the user the whole time.

**What blocks a phase is an unresolved gate, not an open judgment.** A failed build gate, an unmet executable criterion, or an open `DECIDE` ripple stops the phase from closing at all — so nothing is delivered. A parked manual, perceptual, product, or custody criterion is not a gate: it is judgment the user has not yet exercised, and the phase closes and delivers around it. Conflating the two is what made the old posture expensive: it charged the user's attention for a `git commit` in order to collect it for a demo.

## What the orchestrator does

- **Delivers gate-proved work.** After the phase closes with every gate green, `kickoff` re-reads `git status` and the complete final diff, stages **only the phase's explicit paths**, creates an ordinary factual commit with no agent credit and never `--no-verify`, and makes a non-force push only when the branch has exactly one unambiguous configured upstream and the update is a fast-forward. It then fetches and proves that `HEAD`, the tracking ref, and the remote tip agree and the tree is clean. This authority is **orchestrator-only**: delegated roles never commit or push.
- **Never advances past unresolved gates.** A failed build gate, an unmet empirical criterion, or an unresolved `DECIDE` ripple stops the phase. Convergence-bounded revision loops escalate to the human rather than spinning.
- **Never claims subjective acceptance.** It surfaces manual criteria and demo protocols verbatim; it does not say "I listened and it sounds great" — it cannot.
- **Never adds work the plan doesn't authorize.** Drift is contained to the plan that was actually approved. Anything extra is reported as a Note.
- **Never silently reopens closed phases.** A `✅` phase keeps its status and its historical blocks. A concrete user-requested correction amends the code under [`review-lanes.md`](review-lanes.md) and appends an `END (correction)` block; new scope gets a new phase.
- **Never modifies `policies/` or top-level `CLAUDE.md` without explicit instruction.** Those are the rules of the road; the orchestrator and the four canonical agents serve them, they do not amend them.

## What parks delivery

Any of these stops the commit or the push, is reported truthfully, and is never worked around:

- An **unexpected path** in `git status` — this checkout may be shared with a concurrent session, so `git add -A` and `git add .` are forbidden outright.
- A **hook refusal**. Never retried around, never bypassed.
- A **missing or ambiguous upstream**, a **rejected push**, **divergence**, or **residual dirt** after the push.

An open parked criterion is **not** on that list. It does not park delivery; it stays open for the user after the phase is delivered, and the END block records it as such.

None of those authorizes the orchestrator to select a remote, create an upstream, force, tag, reconcile history, or bypass a hook. Those are destructive or custody-bearing Git boundaries and they belong to the human, always.

## What the human does

- **Judges the phase at the seam.** Reads the END block, runs the `User Demo:` protocol, audits the diff and artifacts, and either accepts, asks for revisions, or rejects the phase wholesale.
- **Owns the parked criteria.** Nothing closes them but the human.
- **Authors and amends briefs.** Briefs document the human's intent. Agents propose in their reports; the human is the editor of record.
- **Authors and amends policies.** Agents propose policies; humans approve them.
- **Owns the destructive and custody-bearing Git surface** — force, history rewrite, tags, remotes, branch deletion.
- **Decides when to break a phase, merge phases, or abandon a phase.** Methodology step 11 ("stay agile") belongs to the human.

## Why this is the trade

The methodology's value proposition is that the human's judgment is in the loop *cheaply*. Each phase is small enough to review fast; each END block is structured enough to be grep-able. Spending that attention on a `git commit` the human has no basis to refuse — the gate is green, the review is independent, the evidence is candidate-bound — buys nothing and costs the reviewer's attention at exactly the moment the demo needs it.

So the attention moves rather than disappearing. This is not unattended code generation: every phase still terminates at a seam where a human decides whether the work was right, and the parked set above is deliberately large. A project that wants no human judgment at all wants a different methodology; this one is wrong for that.

## "Authorization stands for the scope specified"

When the human approves a phase, the approval is for *that phase*. The orchestrator does not extrapolate ("the human approved Phase 2.3, so they probably want 2.4 as well") — it closes, delivers, and stops. The next phase requires the next `kickoff` invocation.

Similarly, when the human asks `kickoff` to "run all the remaining phases," that is a one-shot escalation, not a permanent policy change. The next session starts back at single-phase orchestration.

## When the human is away

Gate-proved work continues to its seam and delivers; that is the point of the boundary above. Parked criteria queue for the human's return, and the orchestrator does not interpret silence as approval, does not downgrade a subjective criterion to an objective one, and does not run a demo on the human's behalf. A phase closes `✅` on its gates; the queued judgment is recorded, not converted. What stops at `🚧` with a pause reason is a phase whose *gates* did not close.

## Restriction clause

The human may restrict delivery for a named scope: "don't push this one," "keep Phase 3 local," "hand me the diff for this run." Restrictions are:

- **Explicit.** Stated in the current session, not inferred.
- **Scoped.** They apply to a named phase or a named action.
- **Logged.** The orchestrator records the restriction in the END block ("Delivery: local-only per user").
- **One-shot.** They do not amend the policy. The next phase reverts to the default unless the human restricts again.

A restriction narrows delivery only. It never relaxes a gate, and it never closes a parked criterion.
