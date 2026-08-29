# Policy: Mechanistic vs. Intelligence

Agentic methodology makes it tempting to solve every problem with a model. That is a mistake. Half the work in any real engine is mechanical — exact, repeatable, judgment-free — and mechanical work belongs in deterministic code, not in an agent. This policy is the triage rule: for every recurring task, decide consciously which kind of work it is, and route it accordingly.

## Principle

**Triage every repeatable task into one of two kinds, and route it to the matching tool.**

- **Mechanistic** — when *consistency, determinism, exactness, repeatability, or harness-portability* are paramount. Write a **deterministic script**. Its home is [`bin/`](../bin/README.md).
- **Intelligence** — when *synthesis, creativity, judgment, generativity, or open-ended interpretation* are paramount. Use a **skill** or the four-canonical-agents loop (`policies/four-canonical-agents.md`).

The two are not ranked; they are different tools for different jobs. The failure mode this policy prevents is reaching for intelligence by reflex — spending a model (and its nondeterminism, cost, and per-harness drift) on work a fifteen-line script would do exactly the same way every time.

## Corollaries

1. **Don't burn a model on mechanics.** A deterministic script is cheaper, exact, idempotent, unit-testable, and *byte-identical across harnesses* (Claude Code, Codex, and any other). Reconcilers, parity audits, leak scans, file/identifier sweeps, index and manifest generators, format checks — these are mechanics. A model asked to do them will sometimes get them subtly wrong; a script will not.

2. **Don't script judgment.** Planning a phase, reviewing a plan, authoring prose, weighing trade-offs, classifying genuinely ambiguous input — these are intelligence. A brittle script that fakes judgment with keyword heuristics is worse than an agent: it fails silently and confidently. When the task needs a reader who understands context, use one.

3. **Split mixed tasks at the seam.** Most real tasks have both halves. The pattern is: the **agent decides _what_** (which proposals to act on, which files are in scope, what the change should be), and a **deterministic script does the _mechanical how_** (apply the rename across every call site, merge the results in a fixed order, regenerate the manifest). A donor project building exactly this seam describes its post-fan-out reconciler as *"a script, not a subagent — pure mechanics, no prose model, deterministic and harness-portable."* That sentence is the whole policy in one line. Keep the judgment in the agent and the mechanics in the script; don't let either bleed into the other.

4. **Treat every automation classifier as a proxy boundary.** A filter,
   score, bucket, or heuristic does not measure the property the project cares
   about directly; it measures a stand-in. Before routing that judgment into
   deterministic code, name (a) the real property, (b) the observable proxy,
   (c) innocent inputs that trigger it, and (d) whether those false positives
   can invert the sign — systematically selecting the best material as the
   worst. Apply the falsification procedure in
   [`verification-discipline.md` § Test proxies for sign inversion](verification-discipline.md#test-proxies-for-sign-inversion).
   If inversion is plausible and context or speaker identification resolves
   it, keep classification in intelligence. Scripts may still enforce the
   resulting schema, thresholds, and mechanical consequences.

5. **Notice high-leverage wall-clock opportunities.** Human operators feel
   elapsed waiting more directly than agents do. When a deterministic
   operation materially dominates the work or is repeatedly paid, make one
   bounded assessment of whether its time can be reduced substantially with a
   clear, low-risk change: isolate and parallelize genuinely independent
   units, hoist invariant setup, use focused iteration, or reuse results only
   when their complete inputs are unchanged. This is an ambient priority, not
   a fixed timer or an invitation to optimize everything. Do not spend heroic
   effort shaving marginal time, weaken the operation's guarantees, or expand
   the active phase to pursue a tangent. Use an existing safe acceleration
   when available; otherwise surface one concrete opportunity and continue.

## Ties to other rules

- **Cross-harness parity** (`policies/cross-harness-parity.md`). Scripts are the harness-invariant layer: a `bin/` executable runs identically under every CLI, while agent prose must be mirrored per harness. When a capability must behave the same everywhere, that is a strong signal to make it mechanistic.
- **Acceptance is empirical** (`policies/acceptance-empirical.md`). Deterministic scripts give exact, checkable gates — a clean exit code is acceptance you can trust. Prefer a script when a phase needs a repeatable pass/fail check rather than a subjective read.
- **Deterministic orchestration** (`briefs/deterministic-orchestration.md`). That brief is one *application* of this principle — encoding `kickoff`'s delegate→verdict→route-back loop as a deterministic program where the mechanics (caps, timeouts, fallbacks, schema-validated verdicts) are scripted while the four roles' judgment stays intelligence. This policy is the general rule; that brief is the specific case.

## Acceptance

- When a phase introduces or changes a capability, its plan **names which side of the triage the capability falls on and why** (one line is enough). "It's a deterministic check, so it's a `bin/` script" or "it needs to read intent, so it's an agent."
- The plan reviewer and code critic **flag misrouting**: agent/model work that should be a deterministic script (and would be cheaper and more reliable as one), and scripted heuristics standing in for work that actually needs judgment. Either is a revision request, not a nitpick.
- Any proposed filter, score, bucket, or classifier carries the four-part
  proxy analysis above. A context-sensitive proxy that can invert the sign is
  not admitted as deterministic judgment.
- Plans, reviews, and implementation reports flag a conspicuous avoidable
  wall-clock cost only when a substantial, effectiveness-preserving
  improvement is reasonably apparent. They do not invent numeric thresholds,
  demand speculative optimization, or treat microseconds saved as progress.
