---
name: learn
description: >-
  Explore another repository to assess what techniques, patterns, or
  specializations should be considered for adoption into THIS starter
  template. Produces a structured plan ranked by generality, awaits user
  approval, then applies approved changes to this repo. Use when another
  repo contains agentic-coding patterns, brief or policy ideas, build-gate
  idioms, or domain specializations worth absorbing here. Invoke as
  /learn <donor-dir> [<desc>].
argument-hint: "<donor-dir> [<desc>]"
---

# /learn — Absorb patterns from another repo into this repo

This skill is **universal**. It runs inside any project that follows the agentic methodology — the starter template and every project derived from it. It treats *this* repository (whichever one is invoking `/learn`) as the destination and `<donor-dir>` as the source of ideas. The user approves a plan before any change is made.

Three-stage skill-acquisition pipeline (inspired by the 2026 work on automated skill mining from agentic repositories): **structural analysis → semantic identification → translation**. Updates use a Copier-style discipline: the donor is read-only, conflicts are surfaced for the user, and template-controlled vs. user-controlled files are distinguished before any write.

The donor is **read-only** for the entire skill. We never modify the donor.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- `<donor-dir>` — the directory to learn from. May be absolute, tilde-expanded, or relative to the CWD. Must exist and be readable.
- `<desc>` (optional) — narrows intent ("focus on the testing setup", "Unity specialization", "just policies"). When absent, do the broader assessment described in Stage 2 with **generality preference enabled**.

If `<donor-dir>` is missing or not a readable directory, refuse with `Usage: /learn <donor-dir> [<desc>]` and exit.

## Pre-flight checks

1. **This repo follows the methodology.** Verify the universal invariants:
   - `AGENTS.md` is a symlink to `CLAUDE.md` (or both files exist and have identical content).
   - `.claude/agents/` contains the four canonical roles (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`).
   - `.claude/skills/kickoff/SKILL.md` exists.
   - `.claude/skills/methodology/SKILL.md` exists.
   - `briefs/`, `policies/`, `plan/` directories are present and non-empty.
   - `LOG.md` exists.
   If any fail, refuse with a specific error and exit. (If you arrived here by running `/learn` in a repo that hasn't been bootstrapped, run the bootstrap procedure in [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) first, or invoke `/starter` from the starter template.)

2. **Donor is reachable.** `ls <donor-dir>` succeeds. If the donor is a git repo, capture its `HEAD` SHA for the audit trail; otherwise capture an mtime fingerprint of its top-level files. We don't require the donor to be a git repo.

3. **Working tree clean** (if this repo is a git repo). `/learn` produces commits' worth of changes; running it on a dirty tree mixes the learning with other work. If unclean, list the uncommitted files and ask the user to stash or commit first.

## Stage 1 — Explore (read-only)

Build a structural map of the donor. **Do not** open every file; do targeted reads.

1. **Top-level inventory.** `ls -la <donor-dir>`. Note root files (READMEs, AGENTS.md, CLAUDE.md, language metadata) and directory shape.
2. **Methodology surfaces.** Check for `briefs/`, `policies/`, `plan/`, `LOG.md`, `.claude/`, `.codex/`. Their presence — or absence of structure where this template has structure — is the first signal.
3. **Skills & agents.** `ls <donor>/.claude/skills/` and `ls <donor>/.claude/agents/`. Read the `SKILL.md` and agent files whose names are *not* in the canonical set (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`, `kickoff`, `methodology`, `starter`, `learn`, `teach`). The novel ones are the candidates for learning.
4. **Briefs & policies.** `ls <donor>/briefs/` and `ls <donor>/policies/`. Read each one whose name doesn't already exist here. For names that *do* exist, do a structural diff (head + section list + line count) so the assessment knows whether the donor's version supersedes ours, diverges, or just paraphrases.
5. **Phase plan shape.** If `<donor>/plan/INDEX.md` exists, read it. Look for cross-cutting concerns or critical-files-map patterns we don't have.
6. **Language conventions.** Read `<donor>/CLAUDE.md` (or `AGENTS.md`) section by section. Note any architectural invariants, glossary entries, or conventions the donor pins that this starter doesn't.
7. **Build gates.** Read the donor's language metadata (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.). Note pinned tooling, lockfile presence, gate command idioms.
8. **Anti-patterns.** Note where the donor *violates* something the template considers a load-bearing invariant (status field in phase frontmatter; absolute paths; LOG.md hand-edits). Those are not for learning; mention them as confirmation the starter's rules are correct.

Output of Stage 1 is internal. The user sees Stage 3's plan.

## Stage 2 — Assess (categorize and tier)

For each candidate surfaced in Stage 1, classify on two axes.

### Transfer mode

- **Verbatim** — universal pattern that can be copied with name substitution. Example: a new policy file the donor wrote that obviously applies to every agentic project.
- **Shape-only** — the structure transfers; the content needs rewriting for the starter's audience. Example: a brief that documents donor-specific decisions whose *shape* (sections, frontmatter, voice) is reusable.
- **Inspiration** — worth a mention in this repo's briefs or comments, but not a direct file transfer. Example: a clever build-gate trick that doesn't apply here yet.
- **Out of scope** — donor-specific; doesn't belong in a general-purpose template. Example: domain logic, internal hooks, organization-specific allowlists.
- **Conflicts** — overlaps with an existing file or invariant here; surfaces a choice for the user.

### Generality tier (lower number = more general = higher priority)

- **Tier 1 — Methodology-level.** Orchestrator patterns, agent role definitions, policy structures, brief shapes, the briefs/policies/plan triplet itself. Improvements here help *every* downstream project.
- **Tier 2 — Universal template content.** `.gitignore` patterns, build-gate idioms common across languages, log discipline rules, status-marker conventions.
- **Tier 3 — Language or platform specializations.** Python-specific lint rules, TypeScript-specific tsconfig defaults, Rust workspace patterns. These specialize the template for a language family.
- **Tier 4 — Domain specializations.** Unity game project structure, ML/data-science project structure, CDK-backed AWS project structure. These narrow the template to a niche.

### Selection rule

- **No `<desc>` given**: select candidates from Tier 1, then Tier 2. Only offer Tier 3 if those tiers have less than three actionable items. Only offer Tier 4 if Tier 3 also has less than three actionable items. This implements the user's directive: prioritize general improvements; specialize only when the general well is dry.
- **`<desc>` given**: use it to narrow. If the desc names a tier explicitly ("Unity specialization" → Tier 4), focus there. If the desc names a topic ("testing setup"), pull candidates across all tiers that touch that topic.

## Stage 3 — Plan (present to user)

Produce a structured plan inline in the conversation. Use this exact format:

```markdown
# Learning Plan: <donor-name>

**Donor**: `<absolute-or-relative-donor-path>` (git SHA `<sha>` | mtime fingerprint `<fp>`)
**Generality preference**: <enabled (no desc) | narrowed by "<desc>">
**This repo's HEAD**: `<sha or "untracked">`

## Summary

<One paragraph: what's in this donor that's worth learning, what's not.>

## Proposals (ranked by tier, then by impact)

### Tier 1 — Methodology-level

#### 1. <Short name>
- **Transfer mode**: Verbatim | Shape-only | Inspiration | Conflicts
- **Donor source**: `<donor-relative-path>`
- **This-repo target**: `<this-repo-relative-path>` (NEW | MODIFY | CONFLICTS-WITH-<path>)
- **Why it generalizes**: <one or two sentences>
- **Risk**: <none | low | medium | high — what could go wrong>
- **Estimated change**: <line count or file count>

#### 2. ...

### Tier 2 — Universal template content
(same structure)

### Tier 3 — Language/platform specializations
(only if Tier 1+2 yielded fewer than three items, or `<desc>` requested)

### Tier 4 — Domain specializations
(only if Tier 1+2+3 are exhausted, or `<desc>` explicitly requested)

## Skipped (for the audit trail)

- `<donor file>` — <reason: out of scope | donor-specific | already present | violates an invariant>
- ...

## Conflicts requiring user decision

- `<this-repo file>`: donor's version <describes-the-divergence>. Options:
  - **Keep ours.**
  - **Replace with donor's.**
  - **Merge** (skill produces a unified version).

## Proposed write set (will only be applied after approval)

- `<this-repo file>` — NEW | MODIFY (diff size)
- ...

## Proposed LOG.md entry (after apply)

```
## <YYYY-MM-DD HH:MM> — LEARN
Donor: <donor-name> @ <sha or fp>
Items absorbed: <count>, by tier T1=<n>/T2=<n>/T3=<n>/T4=<n>
Files touched: <count>
```
```

End the plan with one line: **"Approve this plan to apply, ask for revisions, or reject."**

## Stage 4 — Approve (gate)

Do not write a single byte to disk in this repo until the user clearly approves. Acceptable approval signals: "approved", "go ahead", "apply it", "yes", or specific opt-in like "apply items 1, 3, and 5 only."

If the user asks for revisions, return to Stage 3 with the new constraints. If the user rejects, write nothing; do not even create the LOG entry.

If the user partially approves (a subset of items), the apply step honors the subset exactly. Track which items were dropped for the LOG entry.

## Stage 5 — Apply

Once approved, apply the approved items. Order:

1. Add NEW files (policies first, then briefs, then skills/agents/prompts, then plan files, then code).
2. MODIFY existing files (smallest diffs first; one logical change per Edit call).
3. Resolve every cross-harness parity obligation that the changes create:
   - If a `.claude/agents/<role>.md` body changed, refresh `.codex/agents/<role>.toml` (the wrapper body changes only if the description line changed; the pointer stays the same).
   - If a new `.claude/skills/<name>/SKILL.md` was added, add the matching `.codex/prompts/<name>.md` pointer wrapper.
   - See [`policies/cross-harness-parity.md`](../../../policies/cross-harness-parity.md).
4. Update `CLAUDE.md`'s catalogs (briefs catalog, policies catalog) so every new file is indexed.
5. Run the build gates (the same ones the template's `/kickoff` would run) to confirm nothing regressed. Currently for this repo: `uv run ruff check example tests`, `uv run ruff format --check example tests`, `uv run pytest -q`.
6. Append the LEARN entry to `LOG.md`. Format as proposed in the plan.

**Do not auto-commit.** Per [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md), the human owns commits. Report the file list, the build-gate status, and any unresolved manual steps so the user can review and commit.

## Rules

- **The donor is read-only.** Never write to `<donor-dir>` under any circumstances. If the user wants to push improvements back to the donor, that is a separate `/teach <donor-dir>` invocation.
- **Generality first.** Default to Tier 1+2 transfers. Specialize only when those are exhausted or the user's `<desc>` requested it.
- **Approval is mandatory.** No bytes change in this repo before explicit approval.
- **Cross-harness parity is non-negotiable.** Any change touching `.claude/` or `.codex/` updates both surfaces in the same apply step.
- **Catalog drift is forbidden.** `CLAUDE.md`'s catalogs reflect every file in `briefs/` and `policies/` after the apply finishes. Verify before reporting done.
- **Skip donor-specific PII, secrets, and proprietary content** wholesale during Stage 1. If a donor file contains real names, emails, API keys, or internal company names, do not read its body beyond confirming the type; never transfer such content, even in inspiration form.
- **One LOG entry per `/learn` run.** Not per item. The aggregate entry preserves the audit trail without flooding the log.
- **Skill-exclusion list.** `/starter` and the starter template's `example/` Python project are starter-only and never transferred. `/learn` and `/teach` themselves are universal — if the donor has a more evolved version, treat it like any other candidate; if this repo lacks them and the donor has them, propose adding them (the bootstrap procedure expects them in every methodology-following project).
