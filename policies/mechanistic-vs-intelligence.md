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

## Ties to other rules

- **Cross-harness parity** (`policies/cross-harness-parity.md`). Scripts are the harness-invariant layer: a `bin/` executable runs identically under every CLI, while agent prose must be mirrored per harness. When a capability must behave the same everywhere, that is a strong signal to make it mechanistic.
- **Acceptance is empirical** (`policies/acceptance-empirical.md`). Deterministic scripts give exact, checkable gates — a clean exit code is acceptance you can trust. Prefer a script when a phase needs a repeatable pass/fail check rather than a subjective read.
- **Deterministic orchestration** (`briefs/deterministic-orchestration.md`). That brief is one *application* of this principle — encoding `/kickoff`'s delegate→verdict→route-back loop as a deterministic program where the mechanics (caps, timeouts, fallbacks, schema-validated verdicts) are scripted while the four roles' judgment stays intelligence. This policy is the general rule; that brief is the specific case.

## Acceptance

- When a phase introduces or changes a capability, its plan **names which side of the triage the capability falls on and why** (one line is enough). "It's a deterministic check, so it's a `bin/` script" or "it needs to read intent, so it's an agent."
- The plan reviewer and code critic **flag misrouting**: agent/model work that should be a deterministic script (and would be cheaper and more reliable as one), and scripted heuristics standing in for work that actually needs judgment. Either is a revision request, not a nitpick.
