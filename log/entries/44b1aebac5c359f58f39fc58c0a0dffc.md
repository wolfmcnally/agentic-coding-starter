---
{"at": "import", "body_sha256": "0f1fff0bcbb954e4fcbb11d59407dd63e96e5efdb233c4749cfa486720072212", "id": "44b1aebac5c359f58f39fc58c0a0dffc", "previous": "ede361679a0e505d91874df15323cb51", "sequence": 6, "source_offset": 16298, "writer": "unattributed-import"}
---
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

