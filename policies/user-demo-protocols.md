# Policy: User Demo Protocols

When a phase introduces or materially changes a **user-facing surface** *and* there is something a human could meaningfully try by hand, its Acceptance section includes an explicit, **interactive** try-it-yourself protocol — distinct from any deterministic acceptance check. Automated tests verify that the code is correct; a user demo lets the human verify that the *feature* is right. They are not substitutes.

The Acceptance section always addresses this policy explicitly — either with a `User Demo:` block or with a one-line `User Demo: N/A` declaration that names the reason (see "When a phase has nothing meaningful to demo" below). Silence is not acceptable; an empty or padded demo block is also not acceptable.

## What counts as a "user-facing surface"

A surface is user-facing when a human directly interacts with it during normal use. Examples:

- A CLI subcommand or flag the user types.
- A GUI screen, panel, dialog, or component.
- An HTTP endpoint, websocket, or RPC method exposed for direct human or third-party use (not one called only by other internal code).
- An IDE extension, editor command, slash command, REPL command, or shortcut.
- A configuration file the user hand-edits (its schema, its validation messages).
- A rendered artifact a human inspects (a report, a generated document, an audio file, an image).
- An error message, log line, or progress display the user is expected to read.

Not user-facing (this policy does not trigger):

- An internal library API consumed only by other code in the same project.
- A private helper, a refactor, a build-tool tweak, a CI pipeline edit, infra glue.
- A schema change to data the user never reads or writes by hand.
- A policy, brief, plan, or doc edit. (Document quality is governed by the brief/policy review process, not this policy.)

When in doubt, treat the surface as user-facing. The cost of a missing demo is a missed regression; the cost of an unnecessary demo is a paragraph of throwaway text.

## What a demo protocol must contain

A demo protocol is a short, ordered script a human follows in a live session — not a test plan, not a wall of prose. At minimum:

- **Entry point.** The exact command, URL, button, or invocation the user starts with (repo-relative paths only — see [`repo-relative-paths.md`](repo-relative-paths.md)).
- **Suggested inputs.** Two or three concrete inputs to try, chosen to exercise different code paths (the happy path, an edge case, an error case). Inputs the user picks themselves count: "type a question of your own" is a legitimate suggestion alongside "try `What is 2+2?`".
- **What to look for.** Named, observable outcomes — output content, UI state, timing, sounds, file artifacts. Specific enough that the user knows whether the feature passed ("the response streams token-by-token, completes in under 3s, and ends with a citation block") and vague enough to invite the user's own judgment ("try a long prompt and see whether the streaming stays smooth").
- **Variations to explore.** One or two open-ended invitations to deviate from the script — questions the user can answer only by trying things ("what happens with an empty input?", "does cancelling mid-stream leave the state clean?"). This is the *interactive* part: the user is encouraged to poke at the feature, not just replay a recipe.

A demo protocol is **not**:

- A deterministic check ("`curl /api/foo` returns 200" is an empirical acceptance criterion, not a demo).
- A test in disguise ("run `pytest tests/test_foo.py`" belongs in the build gate, not the demo).
- A bare instruction ("try the new feature") — that's a wish, not a protocol.
- A reproduction of the automated test list. The point of a demo is to surface the things tests *cannot* check: feel, latency, layout, surprise behavior.

## How the protocol flows through the pipeline

- **Phase author / planner.** When drafting Acceptance, decide whether a meaningful interactive demo is possible (see "When a phase has nothing meaningful to demo" below). If yes, include a `User Demo:` block following the structure above. If no, include a `User Demo: N/A` line with the reason. Either way, address the policy explicitly.
- **Plan reviewer.** Treat silence on this policy as a blocking issue. Treat a `User Demo:` block that lacks an entry point, suggested inputs, or observable outcomes as a blocking issue. Treat a padded or contrived demo (one that exists only to fill the slot) as a blocking issue — push back with `REVISE` and a recommendation to declare `N/A` honestly. Approve when the chosen path (real protocol or honest N/A) is appropriate to the phase.
- **Coder.** Implement the surface so the demo is actually runnable. If the demo's entry point depends on setup the user doesn't already have (a seeded database, sample data, a config file), provide the setup explicitly — a one-line bootstrap command, a fixture file under `project/`, or a clear `Notes` entry explaining how to satisfy it.
- **Code critic.** Verify the demo as written would actually work against the merged code: the entry point exists, the suggested inputs are valid, the observable outcomes are reachable. Block if the demo is stale relative to the implementation.
- **Orchestrator (`/kickoff`).** Surface every `User Demo:` block verbatim in the phase's END block under "Manual checks for user:", with the entry-point command on its own line so the user can copy-paste it. Do not claim to have run the demo — the orchestrator cannot demo a user-facing feature. If the phase declared `User Demo: N/A`, restate the line in the END block so the human sees the planner's reasoning.

## What a `User Demo:` block looks like

A minimal, well-formed protocol for a hypothetical CLI subcommand:

```
User Demo: `kiln render` subcommand

Entry point:
  cd project && uv run kiln render score-bump-small

Suggested inputs:
- `score-bump-small` — the canonical happy-path recipe; should render in ~2s.
- `score-bump-tiny --duration 0.5` — exercises the short-tail branch; listen for a clean cutoff.
- `nonexistent-recipe` — exercises the error path; the message should name the recipe and suggest `kiln list`.

What to look for:
- A `renders/<recipe>/vNNN/<recipe>__vNNN.aiff` file appears with a non-empty size and a sensible duration.
- The CLI prints the output path and exits 0.
- On the error case, exit code is non-zero and the message is a single line (no Python traceback).

Variations to explore:
- Try `--peak -3` on the happy-path recipe. Does the rendered peak actually move to −3 dBTP?
- Cancel mid-render with Ctrl-C. Is the partial file cleaned up?
```

The same template adapts to GUIs ("click the new button, enter your own prompt, look for streaming output"), HTTP APIs ("hit the endpoint with `curl`, then with a malformed payload, then with a payload your own app would send"), etc.

## When a phase has nothing meaningful to demo

A phase can honestly declare `User Demo: N/A` in any of these cases:

- **No user-facing surface touched.** The phase changes only internal library code, build glue, infra, CI, briefs, plans, policies, or docs.
- **Behavior-preserving change to a user-facing surface.** A refactor, rename, dependency bump, or internal restructuring that leaves the observable behavior identical. (If a refactor *could* introduce a regression a human would notice — e.g. a rewrite of the rendering path — that's worth demoing, even though the behavior is "supposed to" be identical.)
- **Trivially verifiable bug fix or copy change.** A typo correction, a one-line bug fix, or a small message tweak whose entire verification is "the new string appears" or "the bug no longer reproduces" — already covered by a deterministic acceptance check or by inspection of the diff. Forcing a demo here would be theater.
- **Deferred surface.** The phase scaffolds infrastructure for a future user-facing feature but does not yet expose it (e.g. wiring up a backend route whose UI lands in a later phase). Demo lands with the phase that exposes the surface.

In each case, the Acceptance section carries a single line:

```
User Demo: N/A — <one-line reason from the list above, or an equivalent>.
```

That line is the planner's affirmative claim that the policy was considered and does not apply. A phase that is silent on the policy when it touches a user-facing surface gets a `REVISE` from the plan reviewer, the same as a missing build gate. A phase that bolts on a contrived demo just to fill the slot also gets a `REVISE` — declare `N/A` honestly instead.

The rule is: address the policy explicitly, but only write a real protocol when there's a real interactive experience worth exercising.

## Why "interactive, not deterministic"

Automated tests answer *did the code do the thing I told it to do?* User demos answer *is the thing the right thing?* A regression in feel, latency, error-message tone, layout, or sequencing slips past green tests every time. The demo protocol is the cheapest mechanism for catching that class of regression: it costs the planner a paragraph, the user a minute, and it preserves the human-in-the-loop value proposition that this methodology rests on (see [`human-in-the-loop.md`](human-in-the-loop.md)).

A protocol that the user can run as a deterministic shell command without thinking is not pulling its weight — that's an automated test wearing a costume. Always give the user *something to decide*.

## Per-phase waiver

The human may waive this policy for a named phase ("Phase 3.2 is a pure refactor — skip the demo block"). Waivers are explicit, scoped, logged in the END block, and one-shot. The next phase reverts to the default. See [`human-in-the-loop.md`](human-in-the-loop.md#exception-clause).
