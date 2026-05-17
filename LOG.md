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

