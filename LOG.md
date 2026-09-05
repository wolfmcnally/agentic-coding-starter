# Activity Log

This log is **append-only** and owned by `/kickoff`. Do not hand-edit historical entries.

`/kickoff` writes a `## <YYYY-MM-DD HH:MM> — START` block when a phase enters `🚧 In Progress`, and a `## <YYYY-MM-DD HH:MM> — END` block when it leaves `🚧` (either `✅ Completed` or a paused-state END block that documents why).

If a phase pauses mid-way, leave its row in `plan/INDEX.md` at `🚧` and note the pause reason in the END block. The next `/kickoff` resumes it.

See [`policies/log-discipline.md`](policies/log-discipline.md) for the full contract.

## 2026-05-17 17:23 — LEARN

Source: `/learn` cross-donor synthesis. Donors anonymized for distribution.

- Donor A — multi-domain platform repo with a two-tier `policies/user-blockers.md` (engine-level + per-domain), structured per-item fields (Priority / Blocked / Steps / Deliverables back / Unblocks), `[source]` tags, closure-in-place via strikethrough + ✅ DONE / CLOSED / SUPERSEDED, optional `**Disposition:**` line.
- Donor B — single-product repo with a lightweight repo-root `user-blockers.md`: checkbox lifecycle, stable two-word slugs (`coolname`) for conversational reference, strict agent-vs-human checkoff rules embedded in `CLAUDE.md`, sections by phase / date / deferred.
- Donor C — control, no `user-blockers.md` present; no contradicting evidence.

Items absorbed: 4 (T1 = 3, T2 = 1, T3 = 0, T4 = 0).

Files touched:
- `policies/user-blockers.md` — NEW. Synthesis: Donor B's lightweight shape (repo-root file, checkbox + slug + sections, agent-vs-human checkoff) as the default, plus Donor A's structured-fields-on-demand template, source tags, and strikethrough-in-place closure. Donor A's two-tier engine/per-domain variant kept as an optional "Extension pattern" paragraph, not built into the universal template.
- `user-blockers.md` — NEW. Empty repo-root stub every derived project inherits.
- `CLAUDE.md` — MODIFY. Methodology Contract zone only: added policy-catalog entry; added repo-layout entry; added "User blockers" subsection under "Phase work and the `kickoff` skill" with the six-rule agent contract.
- `policies/log-discipline.md` — MODIFY. Added one bullet under "What `LOG.md` is not" cross-linking to `user-blockers.md`.

Build gates: `ruff check` OK, `ruff format --check` OK, `pytest -q` 7 passed.
Cross-harness parity: no `.codex/` mirrors required (documentation/policy only; `AGENTS.md` symlink propagates `CLAUDE.md` edits).
Manual checks for user: review the new policy's voice against the rest of `policies/`; confirm the optional Extension pattern paragraph is the right scope; decide whether `policies/log-discipline.md` should also broaden its "owned by `/kickoff`" line to acknowledge that engine-level skills (`/learn`, future `/teach`) append their own entries.

## 2026-05-17 18:30 — LEARN
Donor: Donor D — a single-product repo with an authored phase plan and a `kickoff/SKILL.md` that had been merged from an earlier donor plus two locally-authored orchestrator step additions.
Items absorbed: 3 (T1=3 / T2=0 / T3=0 / T4=0)
Files touched: 3

Refinements absorbed (all reshaped — no verbatim transfers):

- T1.1 Just-in-time, one-at-a-time sub-phase decomposition. `briefs/methodology.md` §6 strengthened. `.claude/skills/kickoff/SKILL.md` gains Step 1a (decompose only `phase-N.1` at parent entry) and Step 9a (draft `phase-N.(M+1)` at sub-phase close, with the previous sub-phase's outcomes in hand). The donor had a Step 1a that inspired the structure; the donor's eager-decomposition shape was rejected per the principle that later sub-phases benefit from earlier outcomes.
- T1.2 Brief-before-major-phase explicit rule. `briefs/methodology.md` §5 gains a closing sentence: major phases are written after the brief and architecture exist; without those, the phase plan is speculation.
- T1.3 Hot-state checks as optional addendum. `policies/user-demo-protocols.md` gains an "Optional addendum: Hot-state checks for operational surfaces" subsection — 2–5 deterministic commands, additive to the interactive demo block, only for operational surfaces. Donor's `kickoff/SKILL.md` had a seven-section user-testing-protocol step; only §1 (Hot-state checks) was salvaged. §§2–7 were rejected as too heavy for the universal template (would overwhelm post-turn output for most projects).

Skipped (rejected during the design discussion):
- Donor's `kickoff/SKILL.md` Step 1a verbatim — eager full-decomposition at parent entry violates just-in-time. Kernel adopted, shape rejected.
- Donor's `kickoff/SKILL.md` Step 11 §§2–7 — the seven-section close-time output is too heavy; readers tune out. Only §1 (Hot-state checks) salvaged, as an optional addendum.

Build gates after apply: `ruff check` OK, `ruff format --check` OK, `pytest -q` 7 passed.
Cross-harness parity: not affected (canonical edits only; mirrors are symlinks or static content).

## 2026-05-18 09:59 — LEARN
Donor: Donor D (`<desc>` = "briefs policy")
Items absorbed: 1, by tier T1=0/T2=1/T3=0/T4=0
Stale-in-light-of-learning migrations: 2 AUTO (`policies/briefs-and-policies.md` opening cross-reference; `CLAUDE.md` `briefs/` description + policies catalog entry); `policies/README.md` is a no-op (defers to the `CLAUDE.md` catalog rather than enumerating policies in-place).
Files touched: 2 MODIFY (`policies/briefs-and-policies.md`, `CLAUDE.md`), 1 NEW (`policies/briefs.md`).

Absorbed: `policies/briefs.md` — brief-file lifecycle policy. Frontmatter schema (`title` / `date` / `status` / `scope`), four-status flow (`draft` → `methodology` → `implemented` → `historical`), filename conventions (kebab-case, no dates), when-to-write vs. don't-write criteria, retire-vs-update guidance (prefer marking `historical` over deletion), cross-reference discipline, decay/maintenance principle. The donor authored this during its own bootstrap. Starter had no equivalent — `briefs-and-policies.md` covers the contract *between* the three directories but said nothing about the lifecycle *within* `briefs/`.

Transfer mode: Verbatim with one substitution on line 7 (a project-specific descriptor → a template-neutral one) to make the policy applicable to any derived project. Audit confirmed no other donor-specific terms anywhere in the file.

Stale-in-light-of-learning detail:
- `policies/briefs-and-policies.md` gained an opening cross-reference paragraph pointing at the new sibling policy (matching the shape the donor uses in its own `briefs-and-policies.md`).
- `CLAUDE.md` `briefs/` description in the universal repo layout section enriched to mention the frontmatter schema and link to `policies/briefs.md`. Policies catalog gained a `briefs.md` bullet inserted between `briefs-and-policies.md` and `cross-harness-parity.md`.

Build gates after apply: `ruff check` All checks passed, `ruff format --check` 4 files already formatted, `pytest -q` 7 passed.
Cross-harness parity: not affected (canonical edits only; `AGENTS.md` and `.codex/` mirrors unchanged).

Closes the DECIDE follow-up surfaced in the donor's most recent TAUGHT FROM TEMPLATE entry ("`policies/briefs.md` — donor-specific; evaluate for universality"). Verdict: universal, absorbed.

Skipped (out of scope for `<desc> = "briefs policy"`):
- The donor's project-specific briefs (an infrastructure snapshot, a phased-build design rationale, an access-log BCP brief, a seed-script evaluation) — all four are durably tied to the donor's domain and not template content.
- The donor's `.claude/skills/kickoff/SKILL.md` specializations (an `--force-out-of-order` flag, a separate user-testing-protocol step, a sub-phase-only terminology choice) — interesting future candidates for a separate scoped `/learn` invocation against the donor's kickoff specifically, not this run.

## 2026-06-01 — TAUGHT FROM TEMPLATE (Donor E)
Source: Donor E — a downstream project stamped from this template, now feeding its evolution of the user-actions pattern back upstream.
Pattern: user blockers → single-file-per-user-action — `user-actions/<slug>.md` (open) + `user-actions-archived/<slug>.md` (closed), all metadata in YAML frontmatter, **no index**. Per-file removes the single-file contention point when multiple agents edit the queue concurrently; YAML frontmatter is machine-legible.
Items applied: 2 (T2=2)
- `policies/user-actions.md` — genericized rewrite, replacing `policies/user-blockers.md` (DELETE).
- `user-actions/` + `user-actions-archived/` — directory structure replacing `user-blockers.md` (DELETE). `user-actions/.gitkeep` keeps the empty open queue tracked.
Genericization vs. source: dropped Donor E's domain-specific "Relationship to engine blockers" section; `category` is a freeform short label (not a domain enum); kept the sub-domain "Extension pattern" adapted to per-`DOMAIN_ROOT`/`user-actions/`; verification greps switched to directory-glob form.
Parity heals applied: 0 AUTO; 0 DECIDE (AGENTS.md symlink, `.codex/prompts/*` file-symlinks, `.agents/skills/*` directory-symlinks excluding `/starter`, and all four `.codex/agents/*.toml` already clean).
Stale-in-light-of-teaching migrations: 4 AUTO; 0 DECIDE; 0 DEFER
- `CLAUDE.md` — policies-catalog entry, universal-repo-layout bullet, and the `### User blockers` section rewritten to `### User actions (user-actions/)` with the per-file lifecycle.
- `policies/log-discipline.md` — repointed to `user-actions/` + `policies/user-actions.md`.
- `policies/anonymize-log-references.md` — illustrative phrase "a lightweight `user-blockers.md`" → "a lightweight `user-actions/` queue".
- `.claude/skills/teach/SKILL.md` — convention-drift example updated to `user-actions.md`.
Backfilled actions: 2 closed (`blazing-salmon`, `dancing-locust`) → `user-actions-archived/` with frontmatter (filed 2026-05-17, closed 2026-05-18 from git history), dispositions preserved verbatim. No open or deferred items existed.
Build gates after apply (`project/`): `ruff check` All checks passed; `ruff format --check` 4 files already formatted; `pytest -q` 7 passed (markdown/policy only — zero code touched).
Cross-harness parity: not affected (canonical `CLAUDE.md` + skill edits; `.codex/prompts/teach.md` and `.agents/skills/teach` are symlinks to the canonical, auto-updated).
Patterns to feed back via `/learn`: none identified — starter is upstream of Donor E.
Files touched in target: 11 (5 NEW incl. `.gitkeep`, 2 DELETE, 4 MODIFY).

## 2026-06-14 — LEARN

Source: `/learn <donor-dir>` — Donor A, a large multi-domain content/MCP knowledge engine in a sibling workspace. Donor name, path, and SHA withheld (this repo is public; `bin/check-anonymization.sh` flags the path and SHA classes).
Desc: "how projects use the `bin/` directory; carry forward the principle — mechanistic code where consistency/determinism/repeatability are paramount, intelligence where synthesis/creativity/generativity are paramount; always triage."

Donor A routes all deterministic, repeatable mechanics through a documented `bin/` of plain executables and reserves model/agent work for synthesis and judgment. Its post-fan-out reconciler is described in its own briefs as "a script, not a subagent — pure mechanics, no prose model, deterministic and harness-portable" — the triage principle in one line. The template already had the raw material (a `scripts/` dir, one enforcement script) but no named home convention, no operator README, and no codified triage rule.

Items absorbed: 3 (T1 = 2, T2 = 1, T3 = 0, T4 = 0).

User decisions (AskUserQuestion): adopt `bin/` and migrate `scripts/` into it; codify the triage as policy **plus** a CLAUDE.md architectural invariant.

Files touched:
- `policies/mechanistic-vs-intelligence.md` — NEW (T1). The triage law: route each repeatable task to a deterministic script in `bin/` or to intelligence; three corollaries (don't burn a model on mechanics; don't script judgment; split mixed tasks at the seam); ties to cross-harness-parity, acceptance-empirical, and the deterministic-orchestration brief; acceptance hook for reviewers/critics.
- `bin/README.md` — NEW (T2). Operator index for the deterministic-script home: convention preamble (universal, propagates) + a starter-only `check-anonymization.sh` entry that `/starter` drops downstream.
- `bin/check-anonymization.sh`, `bin/anonymization-denylist.local.example` — RENAMED from `scripts/` via `git mv`; internal `SELF`/`DENYLIST`/usage-comment paths and the example header repointed to `bin/`.
- `CLAUDE.md` — MODIFY (T1). New architectural invariant ("Mechanistic vs. intelligence"); `bin/` entry in Universal repo layout; policies-catalog line for the new policy; two glossary entries ("Mechanistic vs. intelligence triage", "`bin/`"); the two hard-rule/catalog `scripts/check-anonymization.sh` refs repointed to `bin/`.
- `policies/anonymize-log-references.md` (4 path edits), `.claude/agents/code-critic.md` (1), `.claude/skills/starter/SKILL.md` (exclusion list + new bin/README-adaptation note), `.claude/skills/teach/SKILL.md` (1), `.gitignore` (1) — all `scripts/` → `bin/`.

Skipped (out of scope): Donor A's actual `bin/` scripts (deploy, render, MCP serve/bundle/deploy, slug/section sweeps, generators) — domain-specific to a content engine; only the convention and the principle generalize. Donor README operator detail (refusal rules, port pairs, pipelines) — shape borrowed, content not. Donor pre-commit hook wiring — inspiration only, noted in the policy's "ties".

Verification: `bin/check-anonymization.sh` exits 0 (dog-food: the relocated gate scans clean); no `scripts/` references remain (`grep` clean across CLAUDE.md, policies/, .claude/, .gitignore, bin/); every `policies/*.md` indexed in CLAUDE.md's catalog.
Build gates (`project/`): `ruff check` All checks passed; `ruff format --check` 4 files already formatted; `pytest -q` 7 passed (markdown/policy + script-rename only — zero deliverable code touched).
Cross-harness parity: `.codex/agents/code-critic.toml` unchanged (thin pointer, no anonymization bullet to update); `AGENTS.md`, `.codex/prompts/*`, `.agents/skills/*` symlinks intact and auto-propagate the canonical edits.
Manual checks for user: review the new policy's voice against the rest of `policies/`; confirm `bin/` (vs. `scripts/`) is the name you want every derived project to inherit; the exec bit on `bin/check-anonymization.sh` survived the rename.

## 2026-06-20 05:30 — TAUGHT FROM TEMPLATE
Source: winifred @ <commit>

Items applied: 1, by tier T1=0/T2=1/T3=0/T4=0.
Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE — parity surfaces already clean (AGENTS.md symlink, all .codex/prompts file-symlinks, all .agents/skills dir-symlinks, cross-harness-review token present and enabled).
Stale-in-light-of-teaching migrations: 0 (AUTO); 0 DECIDE; 0 DEFER — the redirect is additive to existing recipes; no catalog/convention/naming drift.

1. **cross-harness-review stdin-redirect fix** (T2; winifred). `codex exec` / `codex exec resume` (and `claude -p`) read stdin even with the prompt passed as an argument; when the call is backgrounded/detached with an open non-TTY stdin they block on `Reading additional input from stdin...` until the wall-clock timeout discards the call. A foreground shell closes stdin and hides the bug — which is why winifred's first cut survived several review rounds before a backgrounded Phase 10.3 code review hung at the 900 s guard. Fix: add the unconditional `</dev/null` redirect to every recipe + rationale. Applied to: policies/cross-harness-review.md (codex-exec, claude-p, and codex-resume recipes + both Non-negotiable paragraphs), briefs/cross-agent-invocation.md (§2 codex-exec + resume recipes + a stdin-trap BCP bullet; §3 claude-p recipe + bullet), .claude/skills/kickoff/SKILL.md (Step-4 recipe sketch + mandatory-redirect note).

Patterns to feed back via /learn (target → source): None identified — the starter was behind winifred on this surface.
Files touched in target: 3 (policies/cross-harness-review.md, briefs/cross-agent-invocation.md, .claude/skills/kickoff/SKILL.md).
Verification: parity sweep clean (AGENTS.md OK only); all 6 recipe lines + the kickoff Step-4 sketch carry `</dev/null`. Not committed — starter's owner drives commits.

## 2026-07-05 12:00 — TAUGHT FROM TEMPLATE
Source: deicto @ working-tree
Items applied: 3, by tier T1=0/T2=3/T3=0/T4=0
Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE
Stale-in-light-of-teaching migrations: 0 (AUTO); 0 DECIDE; 0 DEFER
Files touched in target: 3

Teaching: cross-harness review handoff is a *map, not a payload*. Applied one improvement across three files:
- policies/cross-harness-review.md — Handoff hygiene gains four rules (reviewer explores its read-only checkout; never pre-materialize a monolithic diff and reject on window size; flag machine-regenerated blobs; scope the reading mandate); the Role-sourcing input-passing paragraph now hands Step 6 the changed-file list + `git diff --stat`.
- .claude/skills/kickoff/SKILL.md — Step 4 item 2 gains the scoped-reading-mandate sentence; Step 6 item 1 rewritten to the file-list-first handoff.
- briefs/cross-agent-invocation.md — §4 reworded the redact bullet and added the "map not payload / never reject on diff size" pattern.
Observed war-story generalized (no source-repo-specific byte counts) to match the template's style. Codex mirrors (.codex/prompts/kickoff.md, .agents/skills/kickoff) are symlinks to the edited canonical — auto-reflected. Parity surfaces clean; no heals needed. No commit made — target owner owns commits.

## 2026-07-24 20:02 — TAUGHT FROM DONOR A
Source: Donor A @ <sha withheld>
Items applied: 1, by tier T1=1/T2=0/T3=0/T4=0
Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE
Stale migrations: 0 (AUTO); 0 DECIDE; 0 DEFER
Files touched in target: 2

Teaching: added the Monotonic Progress architectural invariant to `CLAUDE.md`.
Patterns to feed back via `/learn`: none identified.

## 2026-07-26 17:47 — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 4, by tier T1=3/T2=1/T3=0/T4=0
Stale-in-light-of-learning migrations: 19 AUTO; 0 DECIDE; 0 DEFER
Files touched: 26

## 2026-07-26 18:44 — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 1, by tier T1=0/T2=1/T3=0/T4=0
Stale-in-light-of-learning migrations: 16 AUTO; 0 DECIDE; 0 DEFER
Files touched: 17

## 2026-07-26 20:36 — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 1, by tier T1=1/T2=0/T3=0/T4=0
Stale-in-light-of-learning migrations: 5 AUTO; 0 DECIDE; 0 DEFER
Files touched: 7

Generalized correction: atomic toolchain adoption now has an explicit
behavioral coverage floor; inventories every dependency-bearing operational
caller, generated command, tracked hook, and active instruction; checks staged,
unstaged, and nonignored untracked candidates; and resolves the selected
interpreter once for hot loops, mutation gates, generated multi-command
workflows, and detached processes. The three transfer skills carry the same
requirements. Starter-only anonymization is now explicitly scoped by write
destination so a target's approved LOG provenance remains target-owned.

## 2026-07-27 02:00 — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 3, by tier T1=3/T2=0/T3=0/T4=0
Stale-in-light-of-learning migrations: 17 AUTO; 0 DECIDE; 0 DEFER
Files touched: 36

Generalized improvements: candidate-bound authority, change, finding, and gate
evidence with deterministic revision packets; a focused-to-final verification
ladder; and independent child, artifact, and stream supervision with explicit
exit-66 recovery. Deliberately excluded the lower-ROI universal context
compiler, nested critical-path spans, conditional role removal, and
language-agnostic dependency/mutation selection pending direct evidence.

## 2026-07-27 22:10 — TAUGHT FROM DONOR A
Source: Donor A @ <sha withheld>
Items applied: 1, by tier T1=1/T2=0/T3=0/T4=0
Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE
Stale-in-light-of-teaching migrations: 0 (AUTO); 0 DECIDE; 0 DEFER
Files touched in target: 11

Teaching: made human wall-clock efficiency an ambient methodology priority.
Agents now notice material latency in gates and other deterministic operations
and make one bounded assessment when a substantial, low-risk reduction is
reasonably apparent. The preferred seams are focused iteration, one-time
invariant setup, safe parallel execution of genuinely independent units, and
reuse backed by complete input identity.

Explicit exclusions: no fixed time threshold, automatic hotspot classifier,
telemetry without a decision, general ROI-learning loop, speculative
parallelism, heroic micro-optimization, phase expansion, or reduction in
correctness, coverage, determinism, review independence, diagnostics, failure
propagation, candidate binding, or the complete final gate.

Patterns to feed back via /learn: effectiveness-preserving operator-latency
awareness as an architectural invariant and proportional duty shared by the
planner, plan reviewer, coder, critic, and orchestrator.

## 2026-08-01 15:25 — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 3, by tier T1=2/T2=1/T3=0/T4=0
Stale-in-light-of-learning migrations: 16 AUTO; 2 DECIDE resolved; 0 DEFER
Files touched: 47

Generalized improvements: one trace-bound execution-evidence plane now carries
exact monotonic timing across stages, roles, waits, tools, and gates; generated
cross-harness commands and immutable attempt records fail closed against that
trace; deterministic parity and repository-caller checks guard integration.
Every completed phase now produces a sanitized, responsive, fully offline HTML
report and aggregate archive after acceptance. The report uses overlap-safe
interval unions, explicit gaps and retries, a pinned chart asset, deterministic
regeneration, and browser-verified desktop/mobile presentation.

## 2026-08-04 00:27 — TAUGHT FROM DONOR
Source: the donor @ <sha withheld> — a private production repo built with this methodology, feeding back one day's fail-closed orchestration learnings (nine diagnosed halts → seven runtime rules).
Items applied: 1, by tier T1=1/T2=0/T3=0/T4=0
Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE
Stale-in-light-of-teaching migrations: 2 (AUTO); 0 DECIDE; 1 DEFER
Files touched in target: 4

Teaching: the orchestration runtime doctrine — seven rules for the fail-closed kickoff loop running unattended: (1) fail-closed park with diagnosed self-resume under a novelty ledger and a small budget, recurring cause classes always stopping for the human; (2) deterministic work never round-trips a model — orchestrator-performed byte-diff-proven transforms with the displaced role as reviewer; (3) no artifact larger than one model response travels a single-message channel — large documents revise by delta plus deterministic merge; (4) instruments qualify outside the evidentiary run with aim proofs and falsification controls; (5) contracts embed verbatim in dispatch prompts, rendered from the enforcing source; (6) designed human checkpoints are satisfying stops, and every other stop is classified before it is cured; (7) an out-of-band supervisor verifies claims against ground truth and compiles incidents into standing rules.

Applied across: briefs/methodology.md (new § Orchestration runtime doctrine + honest revision of the "Autonomy" gives-up bullet — unattended stretches between designed checkpoints are now doctrine-supported; date bump), .claude/skills/methodology/SKILL.md (mirrored section; Codex surface auto-reflected via the .agents/skills/methodology directory symlink), CLAUDE.md (methodology-briefs catalog line extended), LOG.md (this entry).

DEFER: the prescriptive/enforcement layer — a fail-closed-resume policy, kickoff self-resume mechanics and budget knobs, delta-merge tooling, instrument-qualification harnesses, four-canonical-agents/review-lanes integration — awaits the donor's vetted mechanics (its own engine phase); transfer via a future teach, refinements return via learn. Doctrine section carries an explicit enforcement-status note so brief and mechanics cannot silently diverge.

Patterns to feed back via /learn (target → source): None identified within this run's narrow scope.
Verification: anonymization check clean; parity surfaces clean (no heals needed); brief and skill sections content-identical. Not committed — starter's owner drives commits.

## 2026-08-04 13:51 — TAUGHT FROM DONOR
Source: the donor @ <sha withheld> — second transfer of the day, carrying the doctrine ratified since the morning's seven-rule teach.
Items applied: 1, by tier T1=1/T2=0/T3=0/T4=0
Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE
Stale-in-light-of-teaching migrations: 2 (AUTO); 0 DECIDE; 1 DEFER (unchanged: enforcement mechanics await the donor's vetted engine phase)
Files touched in target: 4

Teaching, part 1 — four doctrine rules appended to briefs/methodology.md § Orchestration runtime doctrine: instrument altitude (weakest falsifying instrument; retire instruments whose defect class a design change eliminated; ratchet warning); falsification-control satisfiability (a control must be provably able to succeed, checked at specification time); advisory-when-human-shadowed (machine checks fully shadowed by a designed human gate earn recording rights, not parking rights); orientation-first ratification artifacts (density-induced approval collapse — "approval snow blindness" — mitigated by plain-language beats first, fixed decision-payload geography, producer-owned legibility, receiver read-back).

Teaching, part 2 — new § Run-lifecycle vocabulary: finalized / sealed / frozen / parked as a set. Sealed is presented as working shorthand for supply-chain attestation (digest-bound subject plus acceptance predicate), with git commits as the substrate (a commit seals what; a seal adds why you may rely on it) and working-state tree hashes — this template's own bin/kickoff-tree-id — sealing the uncommitted interval; usage rule is seal-at-every-trust-boundary with a sealer cheap enough that ubiquity is free. Parked cross-references the doctrine's stop discipline and is contrasted with interrupt/pause, checkpoint, and halt. Note: the template already carried the full candidate-identity mechanism from earlier transfers; this teach adds the conceptual layer the mechanism lacked.

Mirrored in .claude/skills/methodology/SKILL.md (Codex surface auto-reflects via directory symlink); CLAUDE.md methodology-briefs catalog line updated to the eleven-rule count and the vocabulary.
Patterns to feed back via /learn (target → source): the donor's own methodology brief has not yet absorbed this doctrine — the return transfer is the donor's deferred phase, by design.
Verification: anonymization check clean; parity clean; brief and skill sections content-aligned. Not committed — starter's owner drives commits.

## 2026-08-05 09:20 — TAUGHT FROM DONOR
Source: the donor @ <sha withheld> — third transfer, carrying the doctrine ratified during an overnight one-shot implementation run and its supervision.
Items applied: 1, by tier T1=1/T2=0/T3=0/T4=0
Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE
Stale-in-light-of-teaching migrations: 1 (AUTO: CLAUDE.md catalog rule count eleven → fourteen with the three new rule names); 0 DECIDE; 1 DEFER (unchanged: enforcement mechanics await the donor's engine phase)
Files touched in target: 4

Doctrine growth, 11 → 14 rules in briefs/methodology.md § Orchestration
runtime doctrine, mirrored in the methodology skill: (1) the instrument-
altitude rule gains its time axis — before any repair or new machinery,
check the roadmap for a scheduled change that obsoletes the repaired
surface; a fix for what the plan deletes is the ratchet in a new coat
(motivating case: a validator exception proposed for one legacy ledger
row in a store already scheduled for reset). (2) New rule: preflight the
environment before staking an unattended run on it — a fail-closed probe
ladder before the tasking prompt; barriers surface one layer per round
(observed: three distinct sandbox boundaries in three successive rounds);
fixes land as durable config; a green authoritative baseline classifies
every later failure as the run's own. (3) New rule: well-specified
isolated tasks may run as goal-armed one-shots instead of the four-role
loop — operator-reviewed spec substitutes for plan review, new-files-only
write set, designed parks as satisfying stops, durable goal carrying
outcome + printed proof + park clause, independent verification before
push; goal durability is harness-specific (one harness persists goals as
database state across compaction, another silently clears them). (4) New
rule: authoritative gates run in the native execution context — sandboxed
gate output can contain phantom failures in either direction; one native
baseline classifies; a gate that could not run is "not run," never
"passed." Feed-back note: the donor's own methodology brief receives the
full fourteen-rule doctrine by /learn immediately after this teach, per
operator direction.

## 2026-08-10 02:46 MDT — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 4, by tier T1=4/T2=0/T3=0/T4=0
Donor lessons harvested: 4 (4 absorbed as rule proposals; 0 filed to lessons/)
Application-found return candidates: 0 filed to lessons/
Stale-in-light-of-learning migrations: 18 AUTO; 1 DECIDE resolved by approval; 0 DEFER
Files touched: 23

Generalized improvements: phase-ledger validation now models idle, active,
decomposed, and complete lifecycles instead of requiring a next marker in every
state; the catalog checker also verifies tracked repository-internal Markdown
links. The self-improvement machinery now propagates as an explicit atomic
bundle across executable and manual bootstrap paths, methodology and role
contracts carry lessons and root-cause analysis consistently, and `learn`
harvests defects exposed by applying a donor bundle before its final unchanged-
candidate gate.

The application return-path review found no additional generalizable candidate
beyond the four approved donor lessons. Focused validation did expose and close
two incomplete applications of the approved propagation and corpus-reconciliation
changes before the final gate.

## 2026-08-10 14:45 MDT — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 8, by tier T1=7/T2=1/T3=0/T4=0
Donor lessons harvested: 1 (1 absorbed as rule proposal; 0 filed to lessons/)
Application-found return candidates: 2 filed to lessons/
Stale-in-light-of-learning migrations: 3 AUTO; 2 DECIDE resolved by approval; 0 DEFER
Files touched: 20

Generalized improvements: `kickoff-evidence` now checks gate-artifact
preconditions before the gated command runs and records an artifact absent
afterward with no digest instead of stranding the closed span, and
`ingest-findings` requires `--review-span-id` with an owned, recorded
`--no-review-span` opt-out — adopted atomically with six behavioral tests, the
kickoff skill's Steps 4/6 and operating notes, and the orchestration-evidence
policy. The kickoff skill gained Step 10a (a structured close-time user testing
protocol, cross-referenced from the user-demo policy). The donor's standing
methodology lesson landed as a direct fix: the catalog checker now exempts
inline code spans from link scanning the way fences are exempt. The same
checker also gained the phase-status checks the policy had claimed without
implementing (frontmatter `status:` and body status declarations in per-phase
files), with the policy's Verification section rewritten to describe what
actually runs. CLAUDE.md gained a Lessons operating section; the policies
README gained the authority-precedence ladder, the expanded not-a-policy list,
and the policy-evolution lifecycle; smaller lifts landed in the lessons,
briefs, and repo-relative-paths policies, the self-improvement brief, and
plan/INDEX.md's conventions. The example project gained a network-egress
tripwire with an arming test.

The application return-path review filed two candidates: wholesale donor-file
copies can silently revert destination-ahead hunks, and mechanizing a policy's
verification can silently narrow the contract when the prose delegation lands
ahead of the gate's implementation.

## 2026-08-11 14:18 MDT — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 13, by tier T1=11/T2=2/T3=0/T4=0
Donor lessons harvested: 2 (1 absorbed as rule proposal; 1 filed to lessons/)
Application-found return candidates: 1 filed to lessons/ (a required contract
member must be swept across every independent fixture inventory — three
inventories carried the evidence-init call; two were caught only by the gate)
Stale-in-light-of-learning migrations: 4 AUTO; 0 DECIDE; 1 DEFER (agent-actionable work queue — revisit when a bounded maintenance loop exists to consume it)
Files touched: 35

Doctrine gained its fifteenth rule — ceremony and doctrine grow only against
incidents, and every review prunes — wired into the sweep skill's policy audit
and the self-improvement brief as the ceremony-audit pattern. The learn skill
gained the direction-verification rule graduated from the donor's ledger: a
donor's fix must be shown to reproduce in the destination before its remedy is
imported, hunk by hunk within atomic bundles. The donor's second methodology
lesson (an instrument whose production firings are all comparator false
positives is measuring its model, not the work) was filed as a new ledger
candidate rather than codified.

Mechanized bundles: the fail-closed park/resume policy landed with
`kickoff.yaml`'s `run_budgets.self_resume` key, manager support
(`show budgets` / `set-budgets` / `reset budgets`), and behavioral tests —
closing the doctrine's largest doctrine-to-mechanics gap. Review lanes gained
the invocation-only one-shot lane and the orthogonal evidence-lane axis:
`kickoff-evidence init` now requires both lane declarations, derives role and
stage requirements from them (one-shot drops the planner attempt and planning
stage), and demotes light-lane existence requirements to validated-if-present
while the close seal stays mandatory in every lane. Role-models absorbed four
operationally hardened sections (tool-stance enforcement is venue-dependent;
native fallback carries the resolved tier; credential precedence and
spawn-point scrubs; cold-artifact review handoff with plumbing-first
diagnosis). Log discipline gained trace/baseline START fields, suffixed
multi-session blocks, and the finalized-trace-only exact-timing rule;
acceptance gained baseline-as-a-commit semantics. New surfaces: the
session-context-compaction brief, the editorial-parity section of the
cross-harness policy, three CLAUDE.md conventions (scratch-path captures,
the five-surface rules-not-memory routing ladder, product-vs-methodology
routing), the plan-INDEX typed-note taxonomy, and two bin utilities
(`check-shell-syntax` gate member, `new-name` slug generator) with tests.

Declined on inspection, per the new direction-verification rule: the donor's
thin-persona refactor (this repo's mirrors already read one canonical body),
its log-rotation rule and structured-output-at-generation and trace-bound
attempt sections (already present here), and its review-handoff measurements
(already carried by the invocation brief, which cites the published source).
The donor's monolithic owner queue, unrotated logs, and inline dated owner
directives were recorded as confirmations of existing rules, not learnings.

## 2026-08-17 21:11 MDT — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 9, by tier T1=7/T2=2/T3=0/T4=0
Donor lessons harvested: 19 (9 absorbed as rule proposals; 10 filed to lessons/)
Application-found return candidates: 2 filed to lessons/
Stale-in-light-of-learning migrations: 15 AUTO; 0 DECIDE; 0 DEFER
Files touched: 41

Scoped to the donor's evolution since the 2026-08-11 harvest. The evidence
plane gained three fail-closed recoveries as one atomic bundle
(policy + `bin/kickoff-evidence` + `bin/kickoff-config` + kickoff skill +
behavioral tests): an unconditional unmeasured-review-pass latch in `validate`
that surfaces a missing convergence measurement while a one-command re-ingest
can still repair it; an append-only ingest journal plus a derived-metrics
overlay for a review pass whose batch was structurally refused — both integers
recomputed from artifacts on every validation, never operator-supplied, with
supersession for the honest re-ingest; and candidate-drift handling for a tree
that moves under an in-flight dispatch — an append-then-amend dispatch
lifecycle whose open/return candidate pair brackets the child (the watcher
captures the open side immediately before spawn; teardown failures degrade to
diagnostics and cannot skip the terminal amendment), a write-once
content-addressed candidate manifest store, and `accept-candidate-drift` with
three independent fail-closed checks against a partition vocabulary the policy
file itself owns. The drift partition was adapted to this repository's six
bookkeeping candidate-movers (logs, plan index, both lessons directories, both
user-action directories). Gate rows gained exact-argv canonicalization in
`record-gate` with a precise legacy-row refusal.

Doctrine gained its sixteenth rule — loop-extension grants are scoped by
convergence invariants, not cycle counts — with the runaway backstop raised
5 → 10 per the operator's directive in the donor (a circuit breaker, not a
work quota) and the convergence-lease contract mechanized in the four-agents
policy; every cycle-count reference swept. Four donor-graduated rule sets
landed as policy text: instrument-trust hardening (vacuous green, vacuous
uniformity, the one-reachable-answer unifying rule, and "one truth, one fold")
plus the cross-tree leads-not-findings rule in acceptance-empirical; the
five-entry containment-claim review checklist in review-lanes; the
one-row-per-instance counting rule and named families in the lessons policy
(with the sweep skill's ref-vs-body audit as its only working enforcement, the
donor's three cut lexical detectors recorded as the negative result); and two
session operating rules in CLAUDE.md (a turn ends by dispatching or stating a
hold, with the own-block rule for refusable commands; route on the
authoritative property, not a stand-in).

Tier 2: `bin/check-hooks-installed` landed as an opt-in-aware liveness witness
(adapted from the donor's mandatory form: unset hooks path passes as healthy
not-opted-in state; set-but-wrong fails as silent disablement; tracked hooks
must stay executable regardless), wired into the `check` policy lane. Ten
donor ledger candidates were filed with `source: learn` (gate wrappers own
preconditions; clock-then-write for measured record fields; silent timeout
clamping; the harness command ceiling's silent-death signature; the
last-message sink clobbering a role's own artifact; fail-fast batteries
reporting partial results in a complete grammar; execution-as-verification as
a side-effect engine; grep-the-suite before untestability claims; positive
window-entry assertions for timing tests; `git -C` for verification commands).

Direction-verification notes: the destination was ahead on gate-argv
canonicalization for `run-gate` (already shipped `shlex.join`; only
`record-gate` needed the donor hunk), and the donor's entry-point self-defence
remedy was declined because its defect does not reproduce here — this repo's
`bin/` entrypoints are self-provisioning script wrappers already swept by the
toolchain entrypoint tests. Two destination defects surfaced by the
hunk-by-hunk check were fixed as part of the bundle: both enforcement call
sites of the review-metrics check lacked the light-lane demotion guard the
review-lanes policy promises, and the orchestration-evidence policy carried
donor-domain vocabulary from an earlier wholesale port. Both were filed as the
run's two application-found return candidates. The fixture-inventory lesson
already in this ledger recurred live during the apply — wiring the new witness
into the gate's required-executable preflight broke ten cases across three
independent inventories inside the gate's own test file, caught by the
authoritative gate — and the occurrence was appended to the standing entry,
which now sits at two. Declined as donor-scale or
domain-specific: the isolated resolution sweep and working-tree tripwire
partition, the donor's mutation-battery row-strength prose, the serial check
lane (this repo's gate runner has no parallel lanes), and the donor's
calibrated timeout values (never ingested, per the kickoff-config privacy
rule).

## 2026-08-23 00:56 MDT — TAUGHT FROM TEMPLATE

Source: castle (state retrieved 2026-08-23)

Items applied: 1, by tier T1=0/T2=1/T3=0/T4=0

Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE

Stale-in-light-of-teaching migrations: 14 (AUTO); 0 DECIDE; 0 DEFER

Unharvested methodology lessons surfaced for `learn`: 15

Files touched in target: 17

Installed durable, candidate-bound full-gate receipts as one atomic toolchain
contract. `bin/check all` now retains a complete log and terminal run metadata,
and a successful run creates a receipt bound to the exact candidate,
environment fingerprint, and log digest. The optional pre-push hook reuses the
result only for a clean current `HEAD`; every absence, mismatch, corruption, or
query error runs the authoritative full gate. Behavioral coverage exercises
success, failure, drift, dirty-tree, non-HEAD, environment-change, tampering,
corruption, and hook hit/miss paths. Learn, Teach, Stamp, bootstrap, policy,
catalog, and operator documentation now propagate the complete bundle while
preserving Starter's Python example and starter-only anonymization lane.

## 2026-08-23 01:30 MDT — TAUGHT FROM TEMPLATE

Source: the source project (state retrieved 2026-08-23)

Items applied: 2, by tier T1=0/T2=1/T3=1/T4=0

Parity heals applied: 0 (AUTO); 0 surfaced as DECIDE

Stale-in-light-of-teaching migrations: 8 (AUTO); 0 DECIDE; 0 DEFER

Unharvested methodology lessons surfaced for `learn`: 15

Files touched in target: 11

Corrected durable full-gate receipts so their environment fingerprint now
describes the repository-selected runtime that actually executes the gate, not
the standalone receipt helper. Python descriptors are emitted through
`bin/python` and bind the implementation, actual version, resolved executable
and base-executable identities and file digests, machine, platform, and uv
version while candidate hashing remains separate from the venv and external
runtime tree. Behavioral coverage proves selected-runtime provenance,
managed-runtime changes with an unchanged candidate, replacement behind a
stable authoritative override path, and fail-closed fallback through the
pre-push hook on probe or descriptor errors. Learn, Teach, Stamp, bootstrap,
policy, catalog, and operator documentation propagate the correction while
preserving the template's Python example, anonymization lane, policy-failure
propagation, configuration, and target-owned state.

## 2026-08-23 12:42 MDT — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 9, by tier T1=9/T2=0/T3=0/T4=0
Donor lessons harvested: 6 (6 absorbed as rule proposals; 0 filed to lessons/)
Application-found return candidates: 0 filed to lessons/
Stale-in-light-of-learning migrations: 7 AUTO; 0 DECIDE; 0 DEFER
Files touched: 58

Scoped to methodology changes made since the prior harvest. The four canonical
roles now carry explicit, configurable research authority: planner and reviewer
may search and retrieve within budgets; coder and critic may retrieve resources
already identified by the approved plan or briefs, including a same-host
structural neighbor, without originating new searches. MCP servers and plugins
are allowed by default when available and within role authority, with no
assumption that any particular research server exists. The manager validates
the matrix, preserves project and phase overrides, and live-preflights the
resolved venue capability before phase mutation.

Two universal operator-facing skills landed. `demo` presents one visible
instruction at a time and waits for the human's observation before advancing.
`treatise` turns completed work into a source-grounded publication only after
the governing policy's readiness, evidence, adaptation, privacy, and review
gates pass. Learn and Teach now use the same one-decision-at-a-time dialogue:
plain explanation, questions until resolved, explicit adoption, then the next
decision; swallowed questions are re-presented in full, and a complete revised
plan is offered for approval only after every decision is closed. Both transfer
paths recheck source and destination identity immediately before applying.

Verification gained an independent discipline policy, material-count
reproduction and attribution requirements, and a two-gate phase close. The
reviewed implementation candidate must pass its complete gate before close
writes; after evidence finalization and tracked close bookkeeping, a second
bare full gate runs against the actual handoff tree. No tracked write may follow
that handoff gate, and a failure reopens the close rather than leaving a sealed
false success.

Phase telemetry now records operator-input parks in a dedicated external
ledger, unions overlapping spans, reports every interval and the total, uses
same-boot monotonic timing when exact, labels cross-boot recovery visibly as
non-exact, protects question content, and fails closed on open or malformed
intervals. Dashboard schema v4 adds the phase-level total and interval table;
responsive rendering keeps those tables readable on narrow screens. Finally,
the template sets background worktree isolation to `none` while preserving
explicit worktrees, and Stamp and Teach propagate or deliberately reconcile
that setting alongside the expanded universal skill and research contracts.

## 2026-08-24 17:25 MDT — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 5, by tier T1=5/T2=0/T3=0/T4=0
Donor lessons harvested: 30 (0 absorbed as rule proposals; 28 filed to lessons/; 2 declined as non-reproducing)
Application-found return candidates: 1 filed to lessons/
Stale-in-light-of-learning migrations: 26 (AUTO); 0 DECIDE; 0 DEFER
Files touched: 56

**Delivery posture inverted, by four ratified decisions.** The donor replaced its
invocation-line `commit`/`push` grant tokens with a standing default: fully
accepted work is committed and fast-forward-pushed without asking. The user
adopted it for this template — *"Human demo and review at seams is now more
important than commit and push authority"* — and additionally ruled that the
compensating judgment surface be strengthened rather than inherited, that the new
default propagate universally (Starter, every stamped project, every `teach`
target — no fork in the rule text), and that every skill deliver per its own gate.

Hard Rule 1 now reads *deliver gate-proved work; the user owns judgment and the
destructive git surface*. `policies/human-in-the-loop.md` was rewritten around an
explicit **acceptance boundary**: a criterion is objective only if it is
executable, independently reviewed, proved by a complete gate, and candidate-bound;
manual, perceptual, product, custody, and owner-only criteria — and an unrun
`User Demo:` protocol — always park. The two are deliberately decoupled: **an open
parked criterion does not hold the commit.** What blocks a phase from closing at
all is an unresolved *gate*, not an open judgment; conflating the two is what made
the old posture expensive, since it charged the user's attention for a `git commit`
in order to collect it for a demo. `kickoff` gains Step 13 (re-read the tree, stage
explicit paths, ordinary factual commit, non-force push to one unambiguous
upstream, prove aligned tips) and Step 14, whose report now **leads with the demo
protocol** as the user's next action instead of ending on a commit instruction. The
END block gains mandatory `Acceptance:` (both halves, even when one is `None`) and
`Delivery:` fields; `Manual checks for user:` was replaced by the former rather than
kept beside it.

**Strengthening the seam gate, which the donor does not have.** The code critic
gains a blocking check on the acceptance *split* — a subjective criterion typed as
objective is the one defect that would let a phase claim evidence that does not
exist, and the critic is now the last independent reviewer before delivery.
`user-demo-protocols.md` gains a section making the demo the user's acceptance
surface, with a padded or unreachable demo blocking rather than noted.
`briefs/eacp-pattern-map.md` was re-derived honestly across four rows: **Human in
the Loop** is now a typed boundary rather than a list of prohibitions; **Dark
Factory** is deliberately partial, with the line drawn by criterion type rather
than by activity; **Continuous Deployment** stops at a push; **Approval Fatigue**
spends one judgment per phase on the demo rather than on a commit.

**Two coherence hunks the prior harvest missed** landed with it:
`acceptance-empirical.md` gains the candidate-bound acceptance section it never
had (verified absent — the rule lived only in the glossary and the evidence
policy), and `four-canonical-agents.md` now states the two orchestrator-owned close
gates and the orchestrator-only delivery authority.

**Ledger harvest.** 33 donor `scope: methodology` entries carry two or more
occurrence rows; three were already represented here, leaving 30 assessed
individually. 28 were filed with fresh Starter slugs, `source: learn`, and
anonymized occurrence rows — spanning git staging discipline, the
absence-vs-ignorance conflation, ledger-mechanism skepticism, guard-class
conversion, cross-repository evidence, conformance-vs-validity checks, progress
instrumentation, throughput normalization, cost classes at loop seams, inert test
doubles, and the failure-replacement boundary. None reached the graduation
threshold, so the ledger gained no DECIDE items. The 66 single-occurrence donor
entries were left for a later run.

**Direction-verification notes.** Two declined because the defect does not
reproduce here: the donor's undocumented close ordering (this repo's `kickoff`
documents the same order explicitly, including validating while the trace is open),
and its worktree-population incident (this repo's entrypoint sweep already uses the
hardcoded allowlist that is the donor's own prescribed fix). Two places where this
repo now stands ahead, recorded for a later `teach`: the donor's own delivery sweep
missed its `roles` skill (still asserting the operator owns commits, citing a policy
that no longer says so) and its `treatise` skill (gating a push on an authority its
same commit dissolved) — both swept here; and the seam-gate strengthening has no
donor counterpart. The donor's uncommitted expected-warning-multiset contract was
left for a later run as in-flight source.

**One application-found return candidate.** Porting the donor's text carried its
conditioning clause — "…and every named manual or subjective criterion is closed" —
into six surfaces before the contradiction with the ratified looser variant was
caught by read-back. No gate can see a mismatch between prose and a decision made
in conversation, so the lesson is filed against the transfer skills themselves.

## 2026-08-25 09:02 MDT — SWEEP (lessons)

First lessons-focused maintenance pass over the ledger. 45 open candidates read,
each occurrence row checked against its own body. Mechanical checks green
throughout (`check-catalogs`, `lessons validate`); `lessons candidates` listed one
entry, and the pass found two more the ledger's own bookkeeping was hiding.

**Two graduations.** `macho-collie` absorbed `fractal-beetle` — the two prescribe
the same fix for opposite halves of one move (adding a required contract member;
relaxing an enforcement for one mode), and fractal-beetle's own body said so — and
graduated at four occurrences into `policies/verification-discipline.md`
§ "Sweep every embodiment of a changed contract". The surface was widened from its
recorded `proposed_surface: skill`, which predated two sightings that involved no
cross-repo transfer at all. The graduated rule keeps the asymmetry between the two
directions: an addition fails loudly at the gate, while a relaxation implemented at
N−1 of N enforcement sites reads as implemented everywhere, because only the
demoted mode's rare path ever reaches the unguarded one.

`banana-macaw` absorbed `wisteria-termite`, reached three, and graduated into
`policies/role-timeouts.md` § "The harness ceiling bounds every budget". That
policy's own shipped-budget table declares 1,800 s, 7,200 s, and 2,700 s hard
deadlines, none of which a foreground command call can reach: the orchestrating
harness caps below all three and silently clamps a larger request rather than
refusing it. The rule now states the ceiling, the four-part silent-death signature
(exit 143, a zero-byte artifact, a stopped stream, no dispatch row) with its
empty-mid-run discriminator, the tracked-background dispatch requirement, and
wisteria-termite's contribution as its own step — diagnose at the caller before
the venue, because the caller is the thing doing the looking.

**One under-count corrected.** `russet-mole` was recorded as seen twice while its
body enumerated the instances individually and stated that nine occurred in one
phase. The rows now match the body, at eight — one more than first estimated,
because the "truncated field read as whole" member names two distinct cuts. This is
the batched filing `policies/lessons.md` forbids, and it had kept the entry
invisible to `bin/lessons candidates` since the day it was filed. Graduation was
considered and **held**: the only rule broad enough to cover the family risks being
too abstract to fire, and several of its members are already graduated here as
narrower rules. The hold is recorded in the entry so a later sweep does not reopen
a settled question.

**Three rows examined and left as written.** `gigantic-puma` (its "five instances"
belong to a family the donor had already graduated, cited as background),
`rugged-gharial` (one run, one diagnosis, one moment of noticing — the closest call
in the ledger, and splitting it would reach the threshold), and `blazing-cicada`
(an ordering corollary from the same incident, not a second sighting). Reasoning
recorded so it is not re-derived.

**One new candidate.** `lean-meerkat` — the `sweep` skill's plan template ends with
a `Proposed LOG.md entry` section while `policies/log-discipline.md` assigns
`LOG.md` to `kickoff`. The first sweep resolved this silently by writing nothing;
this one writes an entry on the precedent of the existing `LEARN` and
`TAUGHT FROM TEMPLATE` entries. Two sweeps, two answers, neither recorded until
now. One occurrence, nothing proposed.

**Nothing retired.** No policy was found contradicted, orphaned, or dead, and no
lesson had a remedy already codified in the repo. The remaining 39 open candidates
are schema-clean and below the threshold.

---

## 2026-08-25 10:09 MDT — SWEEP (policies)

First sweep of `policies/`. All 28 files read against what they actually govern;
every shipped verification recipe was run rather than read. `check-catalogs`,
`lessons validate`, and `check-anonymization.sh` were clean going in.

**One anonymization repair.** Two policies taught by example using a real private
project by name, quoting its CLI, a real recipe name, and its real versioned
output-path shape. Replaced with an invented tool throughout
(`policies/acceptance-empirical.md`, `policies/user-demo-protocols.md`).
`policies/anonymize-log-references.md` now states that "external" means "not this
repository," the operator's own private projects included, and that examples reach
for a familiar project precisely because it is familiar — which is what makes them
identifying. No mechanical check could have caught this; the policy's own
Verification section says so.

**Three deletions.**

- `policies/repo-relative-paths.md` § Verification — a grep that could never print
  its own declared clean result. It matched the policy's text, the catalog line
  describing it, the critic's checklist quoting it, the sanitizer's regex, and two
  tests asserting absence: fifteen hits on a clean tree. Replaced with a pointer to
  `bin/check-anonymization.sh`, whose first pass is this policy's check, excludes
  the placeholder spellings, names the policy in its output, and runs in the full
  gate. The section now also says why not to hand-write the grep.
- `policies/phase-ripple.md` § Verification — two greps matching `- AUTO ` and
  `- DECIDE ` with a trailing space, while the END-block template writes them with a
  colon. One branch could never fire; the other printed "clean" on every run. Also
  removed the block's pre-reversal committing language. The honest manual sweep
  survives as prose, with the reason the greps went.
- `policies/user-actions.md` — a slug-collision snippet duplicated verbatim between
  § Slug discipline and § Verification. One copy kept.

**Four cross-reference contradictions resolved by precedence.** `CLAUDE.md` Hard
Rule 1 and `policies/human-in-the-loop.md` say delivery is *not* acceptance and
covers gate-proved work; four files said the orchestrator delivers "fully accepted
work" — `policies/execution-telemetry.md`, `policies/orchestration-evidence.md`,
`briefs/methodology.md`, `.claude/skills/kickoff/SKILL.md`. All now say
gate-proved. `policies/fail-closed-resume.md`'s standing-bound clause still listed
the ordinary commit and push among things the human owns; it now names what the
human actually owns (the destructive and custody-bearing Git surface, subjective
acceptance) and states the real constraint — a parked run has not closed, so it
delivers nothing.

**Two smaller corrections.** `policies/project-isolation.md` used bare `./bin/check`
where the canonical form is `./bin/check all`. `policies/greenfield-until-released.md`
had a verification grep with no success branch, so a clean run said nothing at all.

**Ledger.** `lean-meerkat` graduated → `policies/log-discipline.md`. The deciding
evidence was the file: `LOG.md` holds 26 entries and none is a phase entry — 25 from
`learn`/`teach`, one from the previous sweep — so the "owned by `kickoff`" sentence
described none of its contents. The policy now carries an entry-kind table naming
which skill writes which heading, states that a skill absent from the table does not
write to the log, and Rule 2 became "Skills write; humans read." `sweep`'s template
records that its entry is authorized.

`crimson-shrew` graduated → `bin/check-catalogs`; the fragment guard it proposed
shipped and caught both instances. Its disposition records the blind spot that
remains: anchors resolve only inside tracked Markdown.

`russet-mole` stays open, with one member carved off and graduated: *never reason
over output you truncated yourself* is now a section in
`policies/verification-discipline.md`, citing all three incidents inline and
distinguished from the pipe-status rule in `acceptance-empirical.md` — there the
exit status is lost, here the status is fine and the content is missing. The family
sentence was reconsidered and held again, with the reason recorded so the next sweep
does not re-litigate it.

Two candidates filed. `magenta-ferret` — the policy corpus's own Verification blocks
are not subject to the verification rules the corpus states, and nothing runs them;
two occurrences, both found here, failing in opposite directions.
`green-markhor` — the END block's `Ripple:` field is the only one with no
independent witness; filed rather than built because this repo has never run a phase
to develop the checker against.

**Left open, deliberately.** Multi-command fenced blocks in three policies, where
the one-command-per-block convention's scope is genuinely ambiguous. The
user-actions queue has no frontmatter validator. The demo example's entry point
bypasses `./bin/`.

## 2026-08-26 11:26 MDT — SWEEP-PLANNING (plan)

Window: 2026-07-26 → 2026-08-26 (31 days; set by the operator's request —
the skill did not yet exist, this run codified it). Harvest: an ad-hoc
predecessor of `bin/review-verdicts` over `~/.claude/projects` (1,507 traces)
and `~/.codex/sessions` (3,840 traces) — 82 genuine plan verdicts (53 REVISE /
29 APPROVED) across four derived projects (Donor A 64, Donor B 8, Donor C 7,
Donor D 3); 112 `PLAN-F` finding records collapsing to ~50 root findings.
Re-run with the shipped harvester at close for the next run's baseline:
`./bin/review-verdicts --since-days 31 --kind plan` — 32 id-bearing plan
verdicts (19 REVISE / 13 APPROVED), 112 unclassified legacy verdicts (no
finding ids; pre-evidence-plane narratives, not hand-sorted this run), 122
finding records, 17 re-aimed ids. Blind spots: verdicts before the finding
schema carry no ids and are under-counted by kind; the genuine-filter is a
proxy; only traces on this machine are visible.

Approval rate by week (hand harvest): 2026-07-w4 20%, w5 6%, 2026-08-w1 60%,
w2 80%, w3 50%, w4 37%. Rounds per phase where stated in END blocks: 2–5, not
falling over the window — the mix moved, the round count did not.

| Category | Root findings | Share | Blocking | Rounds survived | Attribution | vs. last sweep |
|---|---|---|---|---|---|---|
| Cites what it never read | ~18 | 35% | most | 1–3 | planner | new |
| Underspecified / self-contradictory design | ~12 | 25% | mixed | 1–4 | planner | new |
| Acceptance that cannot run | ~10 | 20% | most | 1–3 | planner (mechanizable) | new |
| Scope, authority, inventory | ~5 | 10% | some | 1 | planner | new |
| Owner decision | ~5 | 10% | all | every round | structural | new |
| Verification-discipline nit | ~5 | — | none | 1 | reviewer (non-blocking) | new |

Reviewer-side findings: a stable id carrying a different objection in each of
four rounds, every round classified `initial` (Donor A, three ids × four
rounds); one refuted premise (a manifest count asserted without its command);
owner decisions returned to the planner as `REVISE`; 44% of finding records
`blocking` where the tier is reserved for policy/invariant violations. Genuine
over-engineering asks: two, both `low`, neither drove a round; the reviewer
struck redundant state more often than it demanded mechanism.

Corrections applied: `.claude/agents/phase-planner.md` — required
`## Definitions Read` table, no deferral to the coder, surgical revision,
owner-decision marking; `bin/check-plan-concreteness` + tests — mechanical
pre-review wired into `kickoff` Step 3; `.claude/agents/plan-reviewer.md` —
complete first pass, never re-aim a finding, `evidence` immutable while
actionable, `blocked-owner` routing, severity tiers; `bin/kickoff-evidence` —
`evidence-substituted` ingest refusal + test; `kickoff` Step 4 —
`blocked-owner` park and re-emission on refusal; `policies/four-canonical-agents.md`,
`policies/orchestration-evidence.md`. Declined: a rule for the two
over-engineering asks (count does not justify one). Open (DECIDE): none.
Delivered as 08d0df5; the skill, harvester, and this entry follow in the next
commit.

## 2026-08-26 12:10 MDT — SWEEP-CODING (code)

Over the last month the code critic sent implementations back mostly for
things the coder could have caught alone: tests that could not fail, items
the approved plan named that were never written, prose left describing the
old behavior, and error paths that fall back to a reassuring answer. The
critic was usually right; its one expensive mistake was demanding defenses
against an adversary no authority had named, which cost five rounds before
the owner ruled it out. The rounds that were wasted came less from wrong
findings than from four leaks in the loop itself — code reaching the critic
with its gate never run, partial delivery, fixes applied at one site while
the pattern lived at three, and revisions that broke a neighbor. The coder
had never once refused a finding with evidence. The corrections below make
the coder name each test's falsifier and its gate status, check its own
delivery against the plan, and push back when it can; make the critic cite
the authority that names an adversary; and make the orchestrator run the
focused gate itself before any review when the coder's venue could not.

Window: 2026-07-26 → 2026-08-26 (31 days; set by the operator's request —
the skill did not yet exist, this run codified it). Harvest:
`./bin/review-verdicts --since-days 31 --kind code` (pre-fix harvester) —
113 genuine id-bearing code verdicts (60 REVISE / 53 APPROVED) across four
derived projects (Donor A 80, Donor B 11, Donor C 9, Donor D 2); 89
unclassified legacy verdicts (30 REVISE with `Required Changes`, hand-read);
328 unique `CODE-F` finding records; 129 coder Failure Analysis statements
harvested separately. Blind spots: the running session's own transcript
contaminated the corpus (11 spurious rows, since fixed by excluding the
running session); re-aim detection conflated phases because ids restart per
phase (25 reported, 9 within one session; since keyed by session); legacy
verdicts without ids are under-counted by kind.

Approval rate by week: 2026-07-w4 25%, w5 64%, 2026-08-w1 75%, w2 50%, w3
50%, w4 34% — the w4 drop is two phases (one at attempt 9 under the
threat-model overreach, one 17-finding phase at 3 rounds), weather not trend.
Rounds per phase where stated: 2–4 typical, 5–9 on the outliers. State usage:
`rejected-with-evidence` 0 of 328; `superseded` 21 (all the owner amendment);
`introduced-by-revision` 11; `newly-exposed-by-resolution` 11.

| Category | Root findings | Share | Blocking | Rounds survived | Attribution | vs. last sweep |
|---|---|---|---|---|---|---|
| Real correctness defect | ~80 | 25% | most | 1–3 | coder (legitimate) | new |
| A test that cannot fail | ~80 | 25% | half | 1–3 | coder — proxies; self-diagnosed in 40% of failure analyses | new |
| Planned item not delivered | ~50 | 15% | most | 1–2 | coder — mechanizable | new |
| Prose out of sync with changed behavior | ~50 | 15% | rarely | 1 | coder | new |
| Reassuring default on an error path | ~30 | 10% | most | 1–2 | coder | new |
| Scope / style nit | ~25 | 7% | no | 1 | rides along | new |
| Environment / orchestrator | ~10 | 3% | blocked-owner | — | structural | new |

Critic-side: threat-model overreach (five blocking findings superseded by an
owner amendment after attempts up to 9); non-findings entered as `open`
("none required", "optional", "outside this phase" ×4); nine placeholder
carry-forward findings ("text not supplied to this pass") from a pass
dispatched without the ledger; one correctly marked `SUSPECTED` claim; 34%
`blocking`; a critic re-verifying fifteen untouched findings on every delta
round. Coder-side, in its own words: "scored a stand-in for the property",
"verification followed the implementation's shape", "third consecutive phase
in which full-gate coverage found a reachable regression absent from focused
selection", "the delegated sandbox could not execute the repository wrappers".

Corrections applied: `.claude/agents/phase-coder.md` — falsifiers and
`gate_status` in Change Evidence, plan-matrix verification with
`bin/check-plan-delivery`, class-before-site, revision re-anchoring, push-back
with evidence; `.claude/agents/code-critic.md` — threat-model boundary
(`blocked-owner`), non-findings excluded, `SUSPECTED` cap, falsifier check,
delta-round scope, severity tiers; `bin/check-plan-delivery` + tests, sharing
`lib/agentic_starter/plan_artifact.py` with `check-plan-concreteness`;
`bin/kickoff-evidence` — `falsifiers`/`gate_status` change metadata,
`evidence-placeholder` and `suspected-not-blocking` ingest refusals, packet
rendering; `bin/kickoff-config` — coder toolchain probe at preflight
(non-aborting warning); `kickoff` Step 0b/5/6 — unverified-handoff guard,
delivery pre-review, push-back route, `SUSPECTED` probe, `blocked-owner` park;
`bin/review-verdicts` — running-session exclusion, per-session re-aims,
`--coder-evidence`; `policies/four-canonical-agents.md`,
`policies/orchestration-evidence.md`, `policies/acceptance-empirical.md`,
`policies/log-discipline.md`; the `sweep-coding` skill and the shared
lifecycle in `sweep-planning` (plan mode first, plain-register head).
Declined: none. Open (DECIDE): none. Delivered in the commit that carries
this entry.

## 2026-08-26 15:40 MDT — LEARN

Donor: Donor A @ <sha withheld>

Items absorbed: 20, by tier T1=14/T2=6/T3=0/T4=0.
Donor lessons harvested: 18 (1 absorbed as a rule proposal; 17 filed to
`lessons/`). Application-found return candidates: 0 filed to `lessons/`.
Stale-in-light-of-learning migrations: 4 AUTO; 0 DECIDE; 0 DEFER.
Files touched: 25.

Direct improvements: role dispatch now selects an execution surface that stays
observable for the configured budget instead of assuming every harness silently
clamps foreground work; the review-verdict fixture clears ambient Codex session
identity; and catalog validation ignores indexed Markdown sources deleted from
the candidate worktree while surviving inbound links remain checked.

Destination proofs preceded each hardening. The review-verdict test failed
because the live Codex session joined its expected exclusion set; the new
catalog test failed by trying to read the deleted source; and a yielded Codex
command returned a durable session handle that remained pollable through its
terminal exit. The two focused regression tests then passed, followed by 241
focused bundle tests. The seventeen new lessons preserve donor observations as
anonymized, non-binding candidates for later human-ratified graduation.

## 2026-08-26 16:17 MDT — LEARN

Donor: Donor A @ <sha withheld>

Items absorbed: 27, by tier T1=26/T2=1/T3=0/T4=0.
Donor lessons harvested: 27 (3 absorbed directly into approved rule or
mechanism changes; 21 filed as new candidates; 3 appended as recurrences).
Application-found return candidates: 1 recurrence appended to an existing
methodology lesson. Stale-in-light-of-learning migrations: 21 AUTO; 0 DECIDE;
3 DEFER. Files touched: 52.

Direct improvements: commit delivery now treats every staging list as
live-tree assertions and verifies both staged and committed file sets;
Markdown-link validation checks the complete current candidate, including
nonignored untracked files; every canonical transfer inventory names all
eleven universal skills; user demos begin after gate-proved delivery rather
than implying prior acceptance; and the four shell toolchain entry points
resolve launch-symlink chains before selecting their repository.

Destination proofs preceded both executable changes. New single-hop and
chained-symlink tests failed because the launcher's directory was mistaken for
the repository, and an untracked Markdown fixture with a dead link passed
because only indexed files were scanned. After repair, the focused contract
battery passed 150 tests. The application itself exposed one further
wrong-repository probe: an absolute manager path selected the executable but
not the cwd-rooted tree it measured. That recurrence was returned to the
lessons ledger rather than promoted directly into another rule.

Deferred from the donor: domain-specific briefs, product and data policies,
local runtime stores, and project-only lessons; older categorical wording for
role dispatch; and hardening whose named defects did not reproduce against
Starter's newer evidence and configuration managers.

## 2026-08-27 06:05 MDT — LEARN

Donor: Donor A @ <sha withheld>

Items absorbed: 6, by tier T1=5/T2=1/T3=0/T4=0.
Donor lessons harvested: 1 (0 absorbed directly; 1 filed to `lessons/`).
Application-found return candidates: 1 filed to `lessons/`.
Stale-in-light-of-learning migrations: 21 AUTO; 0 DECIDE; 2 DEFER.
Files touched: 39.

Starter now governs its tests as a local proof estate. A deterministic manager
inventories 522 test definitions plus the named check and pre-commit surfaces,
requires one owning family per proof, binds reports and effectiveness evidence
to the live estate, unions legitimate changed-path mappings, and widens any
invalid or unmapped selection to full. Four locally admitted families form the
vital lane; a local historical-defect case and an out-of-routine holdout mutant
were both detected before activation. All 522 pre-existing and newly added
proof definitions were retained.

The repository exposes `bin/test` and `bin/check` vital/changed lanes for
iteration while preserving both candidate-bound `bin/check all` close gates and
pre-push custody. Structural estate validation joins the policy gate and
pre-commit hook. The brief, policy, catalogs, kickoff instructions, bootstrap,
and learn/teach/stamp transfer rules carry the generalized machinery while
explicitly withholding every donor family, selector, timing, threshold, defect
or mutation corpus, report, and audit judgment. The recipient-local YAML parser
is pinned in the project lockfile.

Focused evidence: both explicit effectiveness assays passed; the 109-test
vital selection passed with one deliberately dormant holdout; the changed-path
union selected 19 families and passed 432 tests with that same holdout dormant.
The application also exposed and corrected one argument-parser regression: the
new two-argument mode initially relaxed old one-argument modes, so a new
methodology lesson records mode-local arity validation. Deferred: any future
proof consolidation or deletion requires a separate reviewed local audit; any
derived-project adoption requires an explicit future `teach` run.

## 2026-08-27 08:26 MDT — LEARN

Donor: Donor A @ <sha withheld>

Items absorbed: 5, by tier T1=4/T2=1/T3=0/T4=0.
Donor lessons harvested: 2 (1 absorbed directly into the corrective bundle;
1 already represented in Starter's methodology). Application-found return
candidates: 1 recurrence appended to an existing methodology lesson.
Stale-in-light-of-learning migrations: 10 AUTO; 0 DECIDE; 0 DEFER. Files
touched: 83.

The corrective adoption replaces the earlier retain-all result with a measured
whole-estate reset. Starter froze a baseline of 541 proof families and 690
expanded leaves, then dispositioned every proof with contract, oracle,
red-witness, overlap, replacement, and rationale evidence. Dominated proofs
and their dead support were physically removed. The retained estate contains
108 families and 126 leaves: 19.96% and 18.26% of the frozen baseline,
respectively. Eleven post-baseline admissions each carry a compensating
retirement, and the default forward budget is zero net growth.

The effectiveness corpora are local to Starter. A frozen twelve-case
historical-defect assay detected ten cases for 83.33% recall. Only after that
selection was frozen, a twelve-case held-out mutant assay ran once and detected
eleven cases for 91.67% kill recall. Every applicable critical-risk class keeps
direct proof; deploy is explicitly inapplicable until Starter acquires a deploy
surface. The three surviving assay misses remain recorded rather than being
hidden by post-holdout tuning.

A pre-delivery assay result was superseded before delivery when staged-diff
preflight exposed that corpus-byte binding and six manager-mutant hunk contexts
were not yet final. The retained inventory and selection did not change. The
same six semantic mutations were mechanically rebased, all twenty-four patch
digests were frozen, and both corpora reran against the final manager. The final
run reproduced the same ten-of-twelve and eleven-of-twelve recalls; only that
digest-bound result is authoritative.

The manager now validates the frozen denominator, append-only dispositions,
complete physical removal, replacement evidence, both reset ceilings, both
recall floors, digest-bound corpus patches, direct critical-risk coverage,
compensated admissions, and the selection freeze. Governed vital and changed
lanes operate only over that validated retained estate; the full close gate
still exercises the entire retained estate. `sweep` carries an executable
reassessment and shrinkage obligation, and learn, teach, stamp, and bootstrap
require every recipient to perform its own reset without inheriting Starter's
survivors or judgments.

## 2026-08-28 16:13 — LEARN

Donor: Donor A @ <sha withheld>

Items absorbed: 1 atomic control-plane and proof-lifecycle bundle.
Donor lessons absorbed into the approved bundle: 5.
Application-found return candidates: 1 methodology lesson filed.
Files touched: 62.

Starter now carries a deterministic orchestration control plane: immutable
exact-command manifests, command-zero admission before substantive execution,
real-read venue receipts bound to live configuration, separate product and
full-tree candidate identities, append-only log custody, and one bounded
bookkeeping repair that parks on ambiguity, repetition, or substantive change.
The kickoff, learn, teach, stamp, bootstrap, briefs, policies, managers,
catalogs, hooks, and tests transfer the complete generalized machinery while
requiring each recipient to supply its own venue inventory, commands, and audit
judgments.

The proof estate remains at 108 retained families and 126 retained leaves
against the frozen 541-family and 690-leaf baseline: 19.96% and 18.26%. Four
physically removed post-reset proofs fund four new control-plane proofs through
an append-only retirement-before-admission lifecycle, leaving zero unspent
retirement budget. Later growth now requires a unique preceding retirement;
the frozen reset surplus cannot be spent again.

A fresh whole-corpus assay recalled eleven of twelve historical defects
(91.67%) and killed all twelve held-out mutants (100%). Every applicable
critical-risk class retains direct proof. Vital, changed, and full lanes all
operate over the retained estate, while the full retained close gate remains
authoritative. The donor's project-specific commands, selectors, venue
inventory, inert-path judgments, manifests, receipts, logs, timings, and audit
judgments were not copied.

The application exposed one methodology lesson: a reset budget is not a
continuing zero-growth budget unless later retirements are replayed. That
lesson is filed as boisterous-adder for future recurrence or graduation.

## 2026-08-29 12:33 MDT — LEARN

Donor: Donor A @ <sha withheld>

Items absorbed: 3, by tier T1=3/T2=0/T3=0/T4=0.
Donor lessons harvested: 0 (0 absorbed as rule proposals; 0 filed to
`lessons/`). Application-found return candidates: 0 filed to `lessons/`.
Stale-in-light-of-learning migrations: 11 AUTO; 0 DECIDE; 0 DEFER. Files
touched: 19.

Starter now stops plan review before apparent convergence can conceal scope
growth. The mechanical pre-review refuses plans over 600 lines, a one-round
increase greater than one third, and the second growth event in an exact
artifact history. Reviewers route out-of-phase mechanisms to the operator for
decomposition or re-scoping. These plan-only bounds leave the existing
code-review convergence lease and runaway backstop unchanged.

Run evidence now distinguishes integrity from acceptance. Integrity validates
only facts that actually exist; acceptance additionally requires the complete
role, convergence, finding, telemetry, manifest, and final-gate conjunction.
`status` names missing acceptance roles, and one locked, idempotent `close`
operation records exactly one accepted, parked, or failed terminal outcome.
Non-accepted close requires a complete failure signature and cannot manufacture
success evidence. A child phase close must complete its parent or leave that
parent in progress with another drafted incomplete direct child. Starter's
separate implementation-candidate and post-bookkeeping handoff gates remain
authoritative.

The mechanistic-versus-intelligence boundary now requires every proposed
filter, score, bucket, or classifier to name the real property, its observable
proxy, innocent triggers, and whether false positives can invert the sign. A
context-sensitive proxy that can systematically select the best material as
the worst remains intelligence; deterministic code may enforce only the
resulting mechanical contract.

The donor's domain machinery, fixed two-pass review cap, stall-specific
lifecycle, project-specific test parallelization, and redundant instruction
surfaces were not imported. Focused tool, lifecycle, catalog, plan, log, and
toolchain tests passed. The retained proof estate remains exactly 108 families
and 126 leaves with no new budget. The authoritative full gate passed 105 tests
before this append; it is rerun against this complete logged candidate below.

## 2026-08-29 18:51 MDT — LEARN
Donor: Donor A @ <sha withheld>
Items absorbed: 1, by tier T1=1/T2=0/T3=0/T4=0
Stale-in-light-of-learning migrations: 11 AUTO; 0 DECIDE; 0 DEFER
Lessons: 0 from the donor ledger; 0 return-path (source: learn)
Files touched: 15

## 2026-09-04 20:01 — LEARN

Donor: Donor A @ <sha withheld>
Items absorbed: 4, by tier T1=4/T2=0/T3=0/T4=0
Donor lessons harvested: 1 absorbed as a direct rule; 0 copied into the ledger.
Destination findings: 1 assessment candidate; 1 application-found recurrence on an existing codified lesson.
Stale-in-light-of-learning: the approved candidate-boundary consumers, gate and hook inventories, test fixtures, instructions, catalogs, transfer contracts, and proof reports migrated together; 0 unresolved DECIDE items. Model-specific prompting changes remain deferred to the separate research assessment.
Files touched: 45

Approved focused research freshness in existing plan sections, dependent-edit searches before finalizing a plan, reuse of existing proof before adding a test or guard, and one root active/bookkeeping declaration. Unknown tracked paths refuse; unknown nonignored untracked paths stay active. Review identity excludes only declared bookkeeping, while full-tree gate and delivery custody remain intact. Removed the special drift-acceptance mechanism; declared authority and explicitly reviewed bookkeeping remain independently protected. The bounded newline repair retains its original three-path scope.

The new gate and staged hook were exercised with a real refusal in an isolated fixture. Two overlapping evidence-test entries were physically consolidated into the retained change-manifest proof, preserving their assertions and funding the two lifecycle admissions. The suite remains at 108 families and 126 leaves. The unchanged local effectiveness corpus detects 11 of 12 historical defects and 12 of 12 held-out mutations. Focused behavioral, toolchain, transfer, receipt, lint, format, and policy checks passed; the authoritative full gate runs against this complete logged candidate before delivery.

Lessons: [smoky-jackrabbit](lessons/smoky-jackrabbit.md) records the assessment's omitted configuration dependency; [macho-collie](lessons-archived/macho-collie.md) records the application recurrence involving independent gate and hook fixture inventories. No new rule was derived from these destination findings. The Rule One diagnostic brief and Codex pointer wrappers remain compatible without edits. Donor-specific operational settings, private evidence, proof judgments, and domain code were not transferred; the donor remained read-only.

Final-gate correction: the first full run exposed a stale per-kind test inventory assertion. It now names 85 behavioral families and 103 behavioral leaves, plus 23 gate/hook proofs, preserving the 108-family and 126-leaf totals. The full gate is rerun against this corrected uncommitted close per the handoff rule.

## 2026-09-04 20:56 — END (correction)
Preflight read-access challenge repair before Astra-era implementation

Follow-up route:
- Bounded user-authorized repair after the configured reviewer preflight failed; the improvement phases had not started. The operator instructed: "Proceed to diagnose and fix, then commit and restart."

Diagnosis:
- The retained provider response reported that the binary file could not be recovered exactly by Read and the requested SHA-256 shell command was denied. The challenge required capabilities outside the role's tool stance.
- The repair uses unpredictable ASCII readback; the host validates exact content and computes the receipt hash. Read-only permissions and receipt schema remain unchanged.

Role model/venue:
- Planner review, coder, and code critic: independent native contexts; these artifacts were not produced by the configured Opus review venue.
- Live repaired preflight: configured Opus high reviewer and critic both passed. No phase-role execution or model-performance comparison is claimed.

Files changed:
- bin/kickoff-config — readable challenge and host-side verification.
- tests/test_kickoff_config.py — strengthened retained proof across both provider paths.
- policies/role-models.md and policies/orchestration-control-plane.md — corrected read-access contract.
- briefs/cross-agent-invocation.md, briefs/deterministic-orchestration-control-plane.md, briefs/eacp-pattern-map.md, and .claude/skills/kickoff/SKILL.md — matching probe documentation.
- lessons/divided-magpie.md — recorded the tool-capability contradiction recurrence.

Build status:
- Focused configuration tests: 8 passed, warning-free; explicit-config lint and format passed.
- Independent plan review and code critique: APPROVED; no blocking findings.
- Product reviewed: 25fe0ce8066c7bdd97b2792e5bc78d375938933bae7928ee72afc19ae52d527d.
- Implementation full gate: 103 tests passed; lint, format, policy, and anonymization passed without warnings. Receipt binds the reviewed implementation tree.
- Proof estate remains 108 families and 126 leaves; no new proof family was admitted. Existing effectiveness report validated; no new effectiveness assay is claimed.
- Handoff gate: runs after this tracked block; completion is contingent on the final bare full-gate receipt.

Acceptance:
- Objective: exact readback rejects incorrect challenges, obsolete digest responses, malformed or extra-text replies, and prompt echoes; failure prevents toolchain continuation and receipt creation. Host receipt digest and stale-configuration refusal are exercised.
- Parked for the user: None for this repair. The approved improvement plan remains to be implemented, and paid experiments remain separately budgeted.

Delivery:
- default — commit + fast-forward push after the handoff gate.

Lessons:
- divided-magpie recurred: qualify a role's challenge using the capabilities actually granted to it.
- The diagnostic wrapper initially selected an unsupported ambient Python; rerunning with the declared supported runtime corrected it. Existing toolchain guidance already covers the failure; no duplicate rule added.
- graduation DECIDE: none.

Remaining:
- Restart the approved Astra-era improvement work after delivery.

## 2026-09-04 21:01 — START
Phase 2 — Model support and portable role presets

Execution trace: 9d1eee00b7ea4b31a18edc6898264759

Planned work:
- Add explicit Astra routing and model/venue effort validation across initial and resumed commands.
- Provide inspectable quality, balanced, and economy presets with explicit cross-vendor review selection and portable quality defaults.
- Preserve routing authority and permission posture; report requested and observed execution metadata honestly and prevent silent substitution.
- Update role documentation, reset/stamp behavior, fixtures, and existing behavioral proofs together.

## 2026-09-04 21:46 — PARK
Phase 2 — Model support and portable role presets (preparation)

The plan is independently approved and governing documentation is prepared. Executable preset support, configuration, fixtures, behavioral tests and final review remain pending. No phase acceptance or delivery is claimed.

Execution trace: 9d1eee00b7ea4b31a18edc6898264759
Candidate lineage: 461ca15ede338c2a50e7a46aa8b38aff3915948e1630f002462668863b188f54 → 5f87e088d008b7a146e4cf25aaac18b76f3c8815697acc7ceaeee4fb44896d0b. Prepared changes are retained; restoration would discard approved work.

Park reason: declared authority changed; re-review is required in a fresh run. The instrument freezes whole-file authority before the required startup marker and this phase's approved governing-document edits. The correction is to capture final authority bytes and the already-in-progress marker before genuine remaining implementation, retaining the unchanged original role configuration throughout that fresh run. This is the first recorded occurrence of that generator in this phase; no previous signature ledger exists.

Evidence is preserved in the finalized local preparation run. Both external reviewer processes exited successfully; the native planner and preparation coder completed. No delegated work or process remains active. The preparation trace ended interrupted because it cannot establish acceptance. Under the approved plan and policies/fail-closed-resume.md, the fresh run consumes one of three self-resume units, leaving two. It will record genuine planning, review, implementation and critique against the complete phase diff. No authority guard or role requirement is waived.

Preparation checks: catalogs, cross-harness parity, anonymization and whitespace passed. Runtime tests and both full close gates remain pending. Requested reviewers were Opus/high through Claude; their streams reported claude-opus-5 and Claude Code 2.1.261, with effort unreported. Native planner/coder settings were inherited rather than provider-observed.

Lessons:
- Filed lessons/classy-kangaroo.md: test lifecycle transitions with the production authority inventory; bookkeeping exclusion does not exempt declared authority.
- The existing citation-direction rule covered the preparation citation correction; no duplicate rule added.

## 2026-09-04 21:48 — START
Phase 2 — Model support and portable role presets (resumed)

Execution trace: e30ed101de844ad0bfae70b19efec1ce

Planned work:
- Rebind independent planning and review to the final prepared requirements.
- Implement preset expansion, explicit Astra routing, qualified observations and existing behavioral proofs.
- Review the complete phase change, then run both full close gates. The preparation run remains parked; two self-resume units remain.

## 2026-09-04 22:37 — END
Phase 2 — Model support and portable role presets

Quality, balanced and economy now expand into inspectable role choices for both harnesses. Quality defaults to Astra in Codex and Fable in Claude Code, with high effort and same-harness independent review. Cross-vendor review remains an explicit choice. Requested settings survive resumes; unsupported observations remain unreported and qualified explicit terminal errors remain failures. The implementation is independently approved and its full gate passed. Final delivery remains contingent on the post-bookkeeping handoff gate below.

Files changed:
- .claude/skills/kickoff/SKILL.md
- .claude/skills/roles/SKILL.md
- .claude/skills/stamp/SKILL.md
- CLAUDE.md
- EXECUTION_LOG.jsonl
- LOG.md
- bin/README.md
- bin/kickoff-config
- briefs/astra-era-development.md
- briefs/cross-agent-invocation.md
- briefs/eacp-pattern-map.md
- docs/README.md
- docs/openai-astra-model-settings.md
- kickoff.yaml
- lessons/classy-kangaroo.md
- plan/INDEX.md
- plan/phase-2.md
- plan/phase-3.md
- plan/phase-4.md
- policies/four-canonical-agents.md
- policies/review-lanes.md
- policies/role-models.md
- policies/role-timeouts.md
- tests/fixtures/kickoff_config_seed.yaml
- tests/test_kickoff_config.py
- reports/execution/ — sanitized offline phase report and aggregate index generated after this entry.

Build status:
- Focused configuration and adjacent evidence checks: passed (1, 8 and 14 tests in the approved sequence); lint, format and policy checks passed.
- Implementation full gate: `./bin/check all` passed, 103 tests; all diagnostics inspected. Proof estate remains 108 families / 126 leaves, measured by the full gate's governance report.
- Handoff gate: runs after this tracked END block and dashboard; completion is contingent on its ignored full-tree receipt.
- Optional gate attachment: digest absent because the orchestrator supplied an uncreated attachment path. The required full-gate receipt and complete captured log exist; acceptance validation passed. This is a capture-argument mistake, not a suppressed test warning. No evidence was rewritten.

Review lane: full. Evidence lane: full. Follow-up route: initial implementation with one bounded coder/critic revision.

Role model/venue — orchestrated by Codex:
- Preflight: passed for the frozen original routing configuration. The new pins start on the next run; this run does not establish Astra/Fable entitlement.
- Planner: requested model=default effort=default venue=native; harness_version=unreported, observed_model=unreported, observed_effort=unreported; observation_errors=native provider metadata unavailable.
- Reviewer: requested model=opus effort=high venue=claude; harness_version=2.1.261, observed_model=claude-opus-5, observed_effort=unreported; observation_errors=effort not exposed by qualified primary metadata.
- Coder: requested model=default effort=default venue=native; harness_version=unreported, observed_model=unreported, observed_effort=unreported; observation_errors=native provider metadata unavailable.
- Critic: requested model=opus effort=high venue=claude; harness_version=2.1.261, observed_model=claude-opus-5, observed_effort=unreported; observation_errors=effort not exposed by qualified primary metadata.
- Observed Claude values came from each role's system/init stream. No configured-versus-dispatched difference or protocol recovery occurred in the accepted run.

Role timing:
- Planning: 1 attempt(s), 161.848 s measured, success; native first-event/idle telemetry unavailable where applicable.
- Plan Review: 1 attempt(s), 237.434 s measured, success; native first-event/idle telemetry unavailable where applicable.
- Implementation: 2 attempt(s), 825.260 s measured, success; native first-event/idle telemetry unavailable where applicable.
- Code Review: 2 attempt(s), 816.275 s measured, success; native first-event/idle telemetry unavailable where applicable.

Execution timing:
- Accepted run active makespan: 2875.040464417 s; calendar window: 2875.040464417 s. Preparation remains a separate interrupted trace in the phase report.
- Exclusive measured roles: Planning 161.847820917 s; Plan Review 237.433647875 s; Implementation 825.260449666 s; Code Review 816.275335125 s. Role spans are sequential; peak role concurrency is 1.
- Automated checks: 49.946037375 s; reconciliation: 777.706343876 s; unmeasured gaps: 6.570829583 s. Wait mirrors are excluded from work totals.
- Failed work: 0.000000000 s; retry work: 383.200329917 s.
- Awaiting user input: none in the phase park ledger, zero recorded duration; no open park.
- Timing validation: finalized trace, exact monotonic joins and both JSON/Markdown timing summaries passed. Counts and durations derive from `kickoff-evidence timing-summary`, finalized spans and the dashboard's overlap-safe projection, not wall-clock guesses.

Candidate-bound evidence:
- Product: prepared=5f87e088d008b7a146e4cf25aaac18b76f3c8815697acc7ceaeee4fb44896d0b; approved=632b2e0b96f08ebedf617a990990bc5b723a31730dbe5eb1a7a875e0d7786dc5; final implementation=632b2e0b96f08ebedf617a990990bc5b723a31730dbe5eb1a7a875e0d7786dc5.
- Implementation full tree: 6a5c35e9440158aecab2657a7d8554bc9931fa323f35724e701734724ce81180; active command manifest: 250b591a81eada6da01e17548b21c58dadc2f098afe32f25f97496a58a845c45.
- Revision packets: 1, 16077 bytes, source hashes recorded in the run packet ledger.
- Findings: open=0, addressed=0, verified=5, rejected-with-evidence=3, closed=0, blocked=0; reopened=0. The independent delta review verified three fixes and accepted three refutations without new scope.
- Implementation-final gates: 1, bound to the approved product. Focused checks are recorded in coder change evidence; they are not miscounted as separately measured gate spans.
- Evidence acceptance validation passed with required command `./bin/check all`. The original authority-preparation PARK remains truthful; the accepted major-phase close precedes the status marker update without relaxing authority hashes.

Wall-clock observations:
- Separable command properties now use 27 manager renders instead of 65 in the revised test block, retaining model/resume/max, venue/effort and rejection coverage. Counts were independently recounted from literal loops; no comparative model-performance claim follows.

Acceptance:
- Objective: preset matrices, atomic configuration edits and reset behavior, Astra/effort routing and resume preservation, qualified observation/null behavior, explicit-error precedence, permissions, receipts and repository checks closed on independently reviewed executable evidence.
- Parked for the user: judge preset-table clarity and run the disposable User Demo. Local fixtures do not prove account entitlement, comparative cost, speed or defect escape rates.

Delivery:
- Default — explicit-path commit and fast-forward push after the handoff gate. No delivery outcome is claimed by this pre-handoff entry.

Ripple:
- AUTO: none; Phase 3 and Phase 4 already cite the approved contract and correct remaining scope.
- DECIDE: none blocking. Codex primary field qualification remains in Phase 4's authorized qualification work; no invented provider field was added.

Lessons:
- Filed during preparation: classy-kangaroo — production lifecycle tests must use real authority inventories and status transitions; methodology scope, one occurrence.
- Existing verification discipline covers the critic's authority overreads and the orchestrator's optional capture-argument mistake; corrected interpretation, no duplicate rule.
- Existing graduation candidates from `bin/lessons candidates`: deft-puffin (3, operation names as schema keys); greedy-ammonite (3, report/output path collision); merciful-cicada (4, explicit repository selection); russet-mole (8, success claims proving too little). No graduation is applied or required for this phase.
- Recalibration: insufficient samples; no target reaches the required 30 successful samples. Configuration unchanged by the recommendation.

User Demo:
- Entry point: the commands below create and edit only a disposable configuration. No live model call occurs.
- Suggested inputs: apply balanced with omitted review mode, show models, apply quality with cross-vendor review, then reset models. Each operation is `./bin/kickoff-config` with that disposable config override.
- What to look for: judge whether the stored two-harness tables and current-harness resolution make the change in coder cost and review venue clear enough to choose intentionally.
- Variations: compare economy and a scoped explicit role edit; confirm the other operational budgets and comments are retained. No preflight or paid role invocation is part of this demo.

```sh
astra_demo_dir=$(mktemp -d)
cp kickoff.yaml "$astra_demo_dir/kickoff.yaml"
env KICKOFF_CONFIG_FILE="$astra_demo_dir/kickoff.yaml" ./bin/kickoff-config apply-preset balanced
env KICKOFF_CONFIG_FILE="$astra_demo_dir/kickoff.yaml" ./bin/kickoff-config show models
env KICKOFF_CONFIG_FILE="$astra_demo_dir/kickoff.yaml" ./bin/kickoff-config apply-preset quality --review cross-vendor
env KICKOFF_CONFIG_FILE="$astra_demo_dir/kickoff.yaml" ./bin/kickoff-config reset models
```


Remaining:
- Phase 3: coherent phases and reliable instruction delivery. Phase 4: integrated qualification and bounded evaluation.
- The live comparative batch remains unrun and requires separate pricing and operator authorization. The broader approved implementation remains authorized.

## 2026-09-04 22:44 — START
Phase 3 — Coherent phases and reliable instruction delivery

Execution trace: f9bfeb964e6b47ae88961e1c488d423d

Planned work:
- Make decomposition conditional on real acceptance or decision boundaries and preserve larger coherent implementation assignments.
- Deliver concise root and kickoff entry points with explicit stage resources, canonical authority, and cross-harness/stamp parity.
- Improve planner, coder, reviewer, and critic guidance while preserving review independence, evidence continuity, and both close gates.
- Qualify structural instruction budgets and phase-selection behavior with retained proofs.

The operator approved phases 2–4 together. Phase 3 stays monolithic. Full review and evidence lanes, both full close gates, and explicit-path delivery remain required. Following the already-diagnosed lifecycle ordering, the in-progress ledger marker is set before capturing its authority hash. Governing prose is prepared under review before a fresh capture for remaining executable qualification; this separates editable requirements from frozen acceptance authority without waiving either.

Environment preflight: the old Codex CLI 0.151.0 was rejected by the provider because Astra requires a newer CLI. The CLI's own updater installed 0.153.4, and fresh Astra/high real-read probes passed for all roles. The coder's sandbox cannot reach the managed Python cache; the orchestrator will run every required focused sequence on coder return under the existing unverified-handoff guard. No model or effort substitution occurred. As of and retrieved 2026-09-04: the official changelog at https://learn.chatgpt.com/docs/changelog records Astra support in the 0.153 series. No phase state was created by the failed preflight.

## 2026-09-04 23:33 — PARK
Phase 3 — Coherent phases and reliable instruction delivery (preparation)

The independently approved preparation is complete: root instructions and kickoff entry meet their budgets, stage resources are explicitly linked, and role and transfer guidance is updated. Executable enforcement, retained test updates, independent whole-phase critique and both full gates remain pending. No phase acceptance or delivery is claimed.

Execution trace: f9bfeb964e6b47ae88961e1c488d423d
Candidate lineage: e9867b6d90a5fe3168ec0c01198aff36cab8314a6f74bfd79a85b1f0d8532a3c → 4f3c7f613c2e8b96c5024d9f369f8fa7b6361547edc618330f6df143f038497b. Prepared changes remain in the tree; restoration would discard approved work. The watcher-owned planner, reviewer and coder artifacts and the run directory are preserved.

The preparation cannot pass acceptance because its approved governing-prose changes alter captured whole-file authority. The diagnosed correction is fresh capture of the final authority and already-in-progress status, followed by genuine remaining checker, fixture and test work. This is the first signature recorded in this phase. Under the approved plan and policies/fail-closed-resume.md, the fresh run consumes one of three self-resume units, leaving two. The root and implementation spans ended interrupted; the trace is finalized. All three delegated roles exited successfully, the focused runner exited with recorded test failures, and no delegated process remains active. No permission or authority guard was weakened.

Focused verification: eight of nine commands passed. The instruction-contract group reported three failures and six passes; all three failures inspect the old single-file layout. The research and material-count obligations remain in directly linked resources, and bootstrap transfers the complete directory. The separate regression group passed sixteen tests; the smoke passed one. Catalogs, harness parity, toolchain callers, formatting, lint and proof governance passed without warnings. Full diagnostics are retained in the local preparation artifacts. Root size is 16,342 bytes and kickoff entry 7,833 bytes; the saved hard-rule text is unchanged. These structural observations do not establish live instruction loading or model adherence.

Fresh independent planning and review will bind to the prepared requirements. Final critique will cover the complete phase diff, including this preparation. Both full gates and the user clarity demo remain pending; the existing separate child-close refusal remains unchanged.

Lessons:
- The production-authority lifecycle diagnosis remains recorded in lessons/classy-kangaroo.md; this planned preparation transition is not a new incident or graduation.
- The coder corrected a scratch verifier against the real source and repeated its checks. Existing verification-discipline rules cover the observation; no duplicate rule was added.

## 2026-09-04 23:34 — START
Phase 3 — Coherent phases and reliable instruction delivery (resumed)

Execution trace: d4bcc4b9d98f456e968d21cd05ee44f2

Planned work:
- Make decomposition conditional on real acceptance or decision boundaries and preserve larger coherent implementation assignments.
- Deliver concise root and kickoff entry points with explicit stage resources, canonical authority, and cross-harness/stamp parity.
- Improve planner, coder, reviewer, and critic guidance while preserving review independence, evidence continuity, and both close gates.
- Qualify structural instruction budgets and phase-selection behavior with retained proofs.

Prepared governing instructions are captured as final authority with the phase already in progress. Fresh planning and review precede genuine remaining enforcement and test work. Final critique covers the complete phase diff. The prior preparation remains parked; this diagnosed fresh run leaves two self-resume units. Astra/high and the successful topology receipt remain unchanged.

## 2026-09-04 23:47 — PARK
Phase 3 — Coherent phases and reliable instruction delivery (qualification prerequisite)

Fresh planning found that incidental reformatting broke the operative context of a frozen mutation patch. The required effectiveness assay cannot run on that candidate. No implementation, independent plan approval, full gate or accepted close occurred in this run.

Execution trace: d4bcc4b9d98f456e968d21cd05ee44f2
Candidate lineage: unchanged product 4f3c7f613c2e8b96c5024d9f369f8fa7b6361547edc618330f6df143f038497b. The planner exited successfully; its exact plan and probe evidence remain preserved. No delegated process remains active. The planning and root spans ended interrupted and the trace is finalized.

Diagnosis: only line wrapping differs between the prepared stamp preflight paragraph and its existing HEAD form. In a disposable copy, the frozen required-gate-inventory patch fails against the prepared form and applies against an exact restoration of the original paragraph. Words are identical and every byte outside that paragraph is unchanged. All twenty-four frozen patches were checked; only this patch failed against the prepared tree. The corpus and its digests remain untouched.

Correction: remove the incidental formatting change by restoring that pre-existing paragraph exactly, then verify every frozen patch applies before fresh authority capture. This restores existing content rather than authors new wrapped prose or introduces a formatting rule. The planner proposed treating that restoration as a new formatting exception; the orchestrator resolved it as removal of its own unnecessary edit within the operator's diagnose-and-fix authorization. Independent review will receive the complete containment proof. No test, source requirement, corpus or permission is waived.

This signature is novel for the phase and distinct from the planned governing-prose preparation boundary. The qualified correction is inside the approved file set and substance. Under policies/fail-closed-resume.md, the next fresh run consumes the second of three self-resume units, leaving one. Final whole-phase planning/review, real checker/test work, assay regeneration, independent critique and both full gates remain pending. Any recurrence of this generator requires the operator.

Lessons:
- The existing changed-contract sweep in policies/verification-discipline.md already covers mutation-patch context. It was not applied before declaring prepared authority ready. The corrected sequence checks all frozen patches before recapture, rather than adding a duplicate rule.
- The planner's read-only shell probe failure was corrected without changing the repository; existing shell guidance covers the local execution detail.

## 2026-09-04 23:47 — START
Phase 3 — Coherent phases and reliable instruction delivery (resumed)

Execution trace: 21542b44814f4fcd95d09a5a7f70c65e

Planned work:
- Make decomposition conditional on real acceptance or decision boundaries and preserve larger coherent implementation assignments.
- Deliver concise root and kickoff entry points with explicit stage resources, canonical authority, and cross-harness/stamp parity.
- Improve planner, coder, reviewer, and critic guidance while preserving review independence, evidence continuity, and both close gates.
- Qualify structural instruction budgets and phase-selection behavior with retained proofs.

Prepared governing instructions are captured as final authority with the phase already in progress. Fresh planning and review precede genuine remaining enforcement and test work. Final critique covers the complete phase diff. The prior preparation remains parked; this diagnosed fresh run leaves one self-resume unit. Astra/high and the successful topology receipt remain unchanged.

## 2026-09-05 00:03 — PARK
Phase 3 — Coherent phases and reliable instruction delivery (glossary correction)

Independent review found one blocking documentation defect: relocated glossary definitions still cite governing policies. Those citations were valid in root instructions but violate the destination brief's citation direction. The planned checker and retained qualification work are otherwise implementable; no implementation or acceptance gate ran here.

Execution trace: 21542b44814f4fcd95d09a5a7f70c65e
Candidate lineage: unchanged product 133ffba0de84e3200441835ea5113559c4f539f515ecc1fe19e5d4e52065cd1b. The planner and reviewer exited successfully. The exact REVISE verdict and PLAN-F001 remain preserved with the measured review span; the reviewed plan is bound. No delegated process remains active. The planning and root spans ended interrupted and the trace is finalized.

Correction is a bounded deletion of governing-policy citation clauses in the relocated Glossary only, retaining its definitions and constraints. The original root policy catalog remains the navigation authority. The exact before/after transform and unchanged-prefix proof are retained for independent review. Governing bytes change only after this truthful park and are captured in a fresh run. Earlier mutation-context repair and all frozen corpus files remain intact.

The signature is novel and causally distinct from prior phase parks. The operator's intervening progress request restored the configured three-unit budget under policies/fail-closed-resume.md; this fresh corrective run consumes one, leaving two. Scope, model/effort, permissions, proof identities, review independence and both full gates remain unchanged. Preserve PLAN-F001 across rebinding; only independent review may verify the correction. Checker/test implementation, actual assay, final whole-phase critique, both gates and the user demo remain pending.

Lessons:
- Existing policies/briefs-and-policies.md expressly distinguishes governing citations from inventory/evidence mentions, including bare filenames. The correction applies that existing rule to the moved prose; no new rule or weaker token filter is added.

## 2026-09-05 00:04 — START
Phase 3 — Coherent phases and reliable instruction delivery (resumed)

Execution trace: 050f162f4cd344f49e5b23bc834b5360

Planned work:
- Make decomposition conditional on real acceptance or decision boundaries and preserve larger coherent implementation assignments.
- Deliver concise root and kickoff entry points with explicit stage resources, canonical authority, and cross-harness/stamp parity.
- Improve planner, coder, reviewer, and critic guidance while preserving review independence, evidence continuity, and both close gates.
- Qualify structural instruction budgets and phase-selection behavior with retained proofs.

Prepared governing instructions are captured as final authority with the phase already in progress. Fresh planning and review precede genuine remaining enforcement and test work. Final critique covers the complete phase diff. The prior preparation remains parked; this diagnosed fresh run leaves two self-resume units. Astra/high and the successful topology receipt remain unchanged.

## 2026-09-05 00:36 — PARK
Phase 3 — Coherent phases and reliable instruction delivery (methodology routing decision)

The operator ratified direct implementation of approved methodology improvements, followed by one independent review of the complete change and required checks, as the future default. The full phase workflow remains an explicit option. The invoking agent's earlier choice of the full workflow contributed repeated planning and authority recapture overhead while changing that workflow's own instructions.

The coder exited successfully with the six assigned checker and test files changed. Its report records syntax checks and frozen patch applicability; the focused behavioral sequence, actual assay, final independent critique, both full gates and human demo remain unrun. No acceptance or delivery is claimed. The implementation and root spans ended interrupted at this operator-directed transition; earlier successful role spans and their artifacts remain unchanged. Execution trace: 050f162f4cd344f49e5b23bc834b5360.

Preserve all completed implementation and historical evidence. Record the approved routing rule in the shared policy and root instructions. Further verification must review the complete current change, including this decision, without treating an earlier review as approval of new authority. Phase status remains in progress; the approved improvement plan remains unfinished.

Lessons:
- The operator explicitly approved a permanent methodology-routing correction: direct implementation after scope approval, one independent review, focused corrections and required full gates. Persist it at policies/review-lanes.md and link it from entry instructions; do not add a new orchestration mechanism to implement this routing decision.
