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
