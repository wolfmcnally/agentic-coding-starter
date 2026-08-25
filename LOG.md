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
