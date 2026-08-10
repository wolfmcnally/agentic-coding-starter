---
name: learn
description: >-
  Explore another repository to assess what techniques, patterns, or
  specializations should be considered for adoption into THIS starter
  template. Produces a structured plan ranked by generality, awaits user
  approval, then applies approved changes to this repo. Use when another
  repo contains agentic-coding patterns, brief or policy ideas, build-gate
  idioms, or domain specializations worth absorbing here. Invoke as
  /learn <donor-dir> [<desc>] in Claude Code or $learn <donor-dir> [<desc>]
  in Codex.
argument-hint: "<donor-dir> [<desc>]"
last-reviewed: 2026-08-10
---

# Learn — Absorb patterns from another repo into this repo

This skill is **universal**. It runs inside any project that follows the agentic methodology — the starter template and every project derived from it. It treats *this* repository (whichever one invokes the skill) as the destination and `<donor-dir>` as the source of ideas. The user approves a plan before any change is made.

Three-stage skill-acquisition pipeline (inspired by the 2026 work on automated skill mining from agentic repositories): **structural analysis → semantic identification → translation**. Updates use a Copier-style discipline: the donor is read-only, conflicts are surfaced for the user, and template-controlled vs. user-controlled files are distinguished before any write.

The donor is **read-only** for the entire skill. We never modify the donor.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- `<donor-dir>` — the directory to learn from. May be absolute, tilde-expanded, or relative to the CWD. Must exist and be readable.
- `<desc>` (optional) — narrows intent ("focus on the testing setup", "Unity specialization", "just policies"). When absent, do the broader assessment described in Stage 2 with **generality preference enabled**.

If `<donor-dir>` is missing or not a readable directory, refuse with `Usage: /learn <donor-dir> [<desc>] (Claude Code) or $learn <donor-dir> [<desc>] (Codex)` and exit.

## Pre-flight checks

1. **This repo follows the methodology.** Verify the universal invariants:
   - `AGENTS.md` is a symlink to `CLAUDE.md` (or both files exist and have identical content).
   - `.claude/agents/` contains the four canonical roles (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`).
   - `.claude/skills/kickoff/SKILL.md` exists.
   - `.claude/skills/methodology/SKILL.md` exists.
   - `bin/kickoff-config` and `kickoff.yaml` exist; `show` validates both config sections.
   - If `policies/orchestration-evidence.md` exists, `bin/kickoff-tree-id`,
     `bin/kickoff-evidence`, and their behavioral tests exist and the scripts
     are executable.
   - `briefs/`, `policies/`, `plan/` directories are present and non-empty.
   - `LOG.md` exists.
   If any fail, refuse with a specific error and exit. (If this skill was invoked in a repo that hasn't been bootstrapped, run the bootstrap procedure in [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) first, or invoke `/stamp` in Claude Code or `$stamp` in Codex from the starter template.)

2. **Donor is reachable.** `ls <donor-dir>` succeeds. If the donor is a git repo, capture its `HEAD` SHA for the audit trail; otherwise capture an mtime fingerprint of its top-level files. We don't require the donor to be a git repo.

3. **Working tree clean** (if this repo is a git repo). `learn` produces commits' worth of changes; running it on a dirty tree mixes the learning with other work. If unclean, list the uncommitted files and ask the user to stash or commit first.

## Plan-mode lifecycle (Stages 1–4)

Stages 1, 2, and 3 are read-only against both repos; Stage 4 surfaces the plan to the user; Stage 5 is the only stage that writes. This maps cleanly onto the harness's plan-mode contract — enter at the start of Stage 1, exit at Stage 4.

- **If the current harness exposes an `EnterPlanMode`-like tool** (Claude Code does today; Codex does not yet — see [openai/codex#11180](https://github.com/openai/codex/issues/11180)), **call it now** before starting Stage 1. The harness then enforces no-write through Stages 1–3; the bespoke "do not write to disk" rule below becomes belt-and-braces.
- **If the harness does not expose programmatic plan-mode entry**, proceed without calling anything — the bespoke read-only discipline through Stages 1–3 carries the contract. The user may have entered plan mode interactively (Codex CLI's `/plan`; the Codex desktop app's plan mode); that's fine and orthogonal to this skill.
- **At Stage 4**, if you entered plan mode in Stage 1 (or detected the user did so interactively and the harness exposes `ExitPlanMode`), call `ExitPlanMode` with the Stage 3 plan body — that becomes the plan content the harness surfaces for approval. The user's accept / revise / reject from the plan-mode UI is the Stage 4 approval signal. If `ExitPlanMode` is not available, fall back to the free-text approval described in Stage 4.
- **Stage 5 (Apply) always runs outside plan mode.** Either the harness has handed control back after `ExitPlanMode`, or no plan mode was entered. Either way, edits to this repo are permitted only after the user has approved.

The skill's bespoke Stage 3 plan template stays the canonical plan body in both paths. Plan mode is a harness affordance layered on top, not a replacement for the structured plan.

## Stage 1 — Explore (read-only)

Build a structural map of the donor. **Do not** open every file; do targeted reads.

1. **Top-level inventory.** `ls -la <donor-dir>`. Note root files (READMEs, AGENTS.md, CLAUDE.md, language metadata) and directory shape.
2. **Methodology surfaces.** Check for `briefs/`, `policies/`, `plan/`, `LOG.md`, `.claude/`, `.codex/`, `.agents/`. Their presence — or absence of structure where this template has structure — is the first signal.
3. **Skills & agents.** `ls <donor>/.claude/skills/` and `ls <donor>/.claude/agents/`. Also `ls -la <donor>/.agents/skills/` (Codex CLI's native skill-discovery path — expected to be **directory-level symlinks** back to `<donor>/.claude/skills/<name>` per the workaround for [openai/codex#11314](https://github.com/openai/codex/issues/11314); surface novelty only if the *target* of the symlink is novel, or if an entry there is *not* a directory symlink — the latter typically indicates a stray from the Codex desktop "import settings" prompt and is not a learning candidate). Read the `SKILL.md` and agent files whose names are *not* in the canonical set (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`, `kickoff`, `methodology`, `stamp`, `learn`, `teach`, `roles`, `sweep`). The novel ones are the candidates for learning.
4. **Briefs & policies.** `ls <donor>/briefs/` and `ls <donor>/policies/`. Read each one whose name doesn't already exist here. For names that *do* exist, do a structural diff (head + section list + line count) so the assessment knows whether the donor's version supersedes ours, diverges, or just paraphrases.
5. **Phase plan shape.** If `<donor>/plan/INDEX.md` exists, read it. Look for cross-cutting concerns or critical-files-map patterns we don't have.
6. **Language conventions.** Read `<donor>/CLAUDE.md` (or `AGENTS.md`) section by section. Note any architectural invariants, glossary entries, or conventions the donor pins that this starter doesn't.
7. **Repository-owned toolchain contract.** Inspect the donor's `bin/setup`,
   `bin/test`, `bin/check`, any runtime wrapper (`bin/python` or equivalent),
   runtime-version file, language metadata, lockfile, behavioral tests, policy,
   hooks, and workflow callers as one bundle. Note generalizable interface and
   failure-handling mechanics, including whether an explicit runtime override
   is authoritative and whether candidate selection is proven by a real
   dependency-chain load/run probe. Inventory dependency-bearing operational
   callers, generated commands, tracked hooks, and active instructions; verify
   that format coverage includes staged, unstaged, and nonignored untracked
   candidates; and identify hot loops, mutation gates, and detached processes
   that must resolve the repository interpreter once rather than reprobe per
   call. Treat donor
   language/version/package-manager choices as donor state, not defaults to
   copy.
8. **Anti-patterns.** Note where the donor *violates* something the template considers a load-bearing invariant (status field in phase frontmatter; absolute paths; LOG.md hand-edits). Those are not for learning; mention them as confirmation the starter's rules are correct.
9. **Unified kickoff configuration.** Inspect the donor's schema shape, round-trip manager, behavioral tests, both role policies, `roles`, `kickoff` call sites, invocation brief, gitignore, and reporting contract as one bundle. Learn only generalizable mechanics, schema, algorithms, and defensible universal defaults. Never read, copy, or summarize raw telemetry, percentiles, model/effort choices, calibrated values, comments, `extensions` data, or project overrides.
10. **Candidate-bound orchestration evidence.** Inspect the donor's candidate
    identity implementation, authority/change/finding/gate schemas, revision
    packets, reviewer/coder evidence blocks, verification ladder,
    final-candidate checks, watcher outcome classification, policy, brief,
    docs, and behavioral tests as one bundle. Separate general mechanics from
    project-specific risk tags, thresholds, dependency selectors, assurance
    profiles, and private run artifacts.
11. **Lessons ledger.** Read `<donor>/lessons/` and `<donor>/lessons-archived/`
    (per the ledger contract in `policies/lessons.md`). Entries with
    `scope: methodology` are **first-class harvest input** — pre-digested,
    provenance-carrying learnings the donor's own phase work already
    distilled, far cheaper than rediscovering the same patterns from raw
    files. Archived `codified` entries point (via `graduated_to:`) at rules
    the donor already ratified — check whether those rules themselves are
    transfer candidates. Ignore `scope: local` entries beyond confirming the
    ledger's health. A donor with no ledger is itself a finding: it predates
    the lessons contract and is a `teach` candidate.

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

- **Tier 1 — Methodology-level.** Orchestrator patterns, agent role definitions, policy structures, brief shapes, the briefs/policies/plan triplet itself, cross-harness orchestration machinery, role-timeout enforcement/calibration contracts, and review-intensity machinery. Improvements here help *every* downstream project. A donor lesson with `scope: methodology` maps here (or to Tier 2) by construction — the donor already made the generality call.
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

## Stale-in-light-of-learning (will be migrated or surfaced)

For every approved learning, identify existing files in this repo made stale by the new convention. Classify each item as:

- **AUTO** `<this-repo file>` — mechanical migration applied in the same run.
- **DECIDE** `<this-repo file>` — requires a project-specific or policy choice; ask during approval.
- **DEFER** `<this-repo file>` — depends on a named later condition.

If none, declare "None identified." A learned timeout improvement must list
every member of the atomic timeout bundle here or in the proposal write set;
importing a single donor file is not complete. The same rule applies to the
repository-owned toolchain contract: any proposal touching setup, tests,
gates, runtime selection, metadata, or locking must enumerate the complete
bundle and classify partial existing adoption as stale.
The proposed tests must execute the adapted entry points with controlled
toolchain stubs; source-text assertions alone do not satisfy the behavioral
coverage floor.

## Proposed write set (will only be applied after approval)

- `<this-repo file>` — NEW | MODIFY (diff size)
- ...

## Proposed LOG.md entry (after apply)

```
## <YYYY-MM-DD HH:MM> — LEARN
Donor: <donor-name> @ <sha or fp>
Items absorbed: <count>, by tier T1=<n>/T2=<n>/T3=<n>/T4=<n>
Donor lessons harvested: <count> (<count> absorbed as rule proposals; <count> filed to lessons/)
Application-found return candidates: <count> filed to lessons/
Stale-in-light-of-learning migrations: <count> (AUTO); <count> DECIDE; <count> DEFER
Files touched: <count>
```
```

When this repo has an external-reference anonymization policy, render the
proposed committed entry through it at plan time: use `Donor A` (or the
policy's equivalent), replace the external SHA with `<sha withheld>` or an
allowed fingerprint, and omit proprietary donor paths and identifiers. The
conversation plan may identify the donor for the user; the committed LOG entry
may not violate the destination's publication policy.

End the plan with one line: **"Approve this plan to apply, ask for revisions, or reject."**

## Stage 4 — Approve (gate)

Do not write a single byte to disk in this repo until the user clearly approves.

**Two paths, by harness capability** (per the Plan-mode lifecycle section above):

- **Plan-mode path.** If you entered plan mode at Stage 1 (or the user did interactively), call `ExitPlanMode` with the Stage 3 plan body. The harness presents accept / revise / reject affordances; the user's choice is the approval signal. A plain accept maps to "approved (all items)"; revise routes back to Stage 3 with the user's constraints; reject means write nothing and no LOG entry.
- **Free-text path** (when plan mode is unavailable in the current harness). Wait for a clear approval signal in chat: "approved", "go ahead", "apply it", "yes", or specific opt-in like "apply items 1, 3, and 5 only." Revisions return to Stage 3; rejections mean write nothing and no LOG entry.

If the user partially approves (a subset of items, whether via plan-mode revise-with-constraints or free-text opt-in), the apply step honors the subset exactly. Track which items were dropped for the LOG entry.

## Stage 5 — Apply

Once approved, apply the approved items. Order:

1. Add NEW files (policies first, then briefs, then skills/agents, then plan files, then code).
2. MODIFY existing files (smallest diffs first; one logical change per Edit call).
3. Apply every approved AUTO item from "Stale-in-light-of-learning"; carry DECIDE/DEFER items into the LOG entry with their decision or condition.
4. Resolve every cross-harness parity obligation that the changes create:
   - If a `.claude/agents/<role>.md` body changed, refresh `.codex/agents/<role>.toml` (the wrapper body changes only if the description line changed; the pointer stays the same).
   - If a new `.claude/skills/<name>/SKILL.md` was added, add the matching `.agents/skills/<name>` directory symlink for Codex discovery.
   - See [`policies/cross-harness-parity.md`](../../../policies/cross-harness-parity.md).
5. Update `CLAUDE.md`'s catalogs (briefs catalog, policies catalog) so every new file is indexed.
6. File harvested donor lessons that were approved as ledger entries rather
   than immediate rule changes: write each to this repo's `lessons/<slug>.md`
   with `source: learn`, anonymized per this repo's publication policy, and
   run `./bin/lessons validate`. A donor lesson approved as a direct rule
   change lands as its rule edit instead (steps 1–2) — not both.
7. Run focused wrapper tests through `./bin/test
   tests/test_toolchain_entrypoints.py tests/test_check.py -q`. If an older
   methodology-following destination lacks the atomic toolchain contract, run
   the exact focused commands declared by its current metadata and `kickoff`,
   and flag every missing contract member as a learning candidate.
8. Re-run the caller inventory and verify that format checking covers staged,
   unstaged, and nonignored untracked candidates. For any repeated,
   mutation-sensitive, generated, or detached workflow, prove that the
   underlying repository interpreter is resolved once and reused.
9. **Harvest the application return path.** Review defects and improvements
   discovered while translating, applying, and validating the approved bundle
   that were not already donor-ledger inputs. Applying a donor pattern is an
   empirical test of that pattern's contract. For each generalizable finding,
   check both destination lesson directories, append an occurrence to a match
   or file a new `scope: methodology`, `source: learn` candidate, and preserve
   the donor as read-only. Do not turn the finding directly into another rule
   edit in this step: application-found candidates enter the ledger for later
   human ratification. Run `./bin/lessons validate` and
   `./bin/lessons candidates`; count these separately from donor lessons.
10. Append the LEARN entry to `LOG.md`. Format as proposed in the plan,
    report donor-ledger and application-found lesson counts separately, and
    apply this repository's anonymization policy because this write lands in
    Starter.
11. Run `./bin/check all` against the complete unchanged candidate after all
    rule, lesson, stale-migration, and LOG writes. This is the authoritative
    final gate; any subsequent candidate change invalidates it.

**Do not auto-commit.** Per [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md), the human owns commits. Report the file list, the build-gate status, and any unresolved manual steps so the user can review and commit.

## Rules

- **The donor is read-only.** Never write to `<donor-dir>` under any circumstances. If the user wants to push improvements back to the donor, that is a separate `/teach <donor-dir>` invocation in Claude Code or `$teach <donor-dir>` invocation in Codex.
- **Generality first.** Default to Tier 1+2 transfers. Specialize only when those are exhausted or the user's `<desc>` requested it.
- **Approval is mandatory.** No bytes change in this repo before explicit approval.
- **Cross-harness parity is non-negotiable.** Any change touching `.claude/` or `.codex/` updates both surfaces in the same apply step.
- **Catalog drift is forbidden.** `CLAUDE.md`'s catalogs reflect every file in `briefs/` and `policies/` after the apply finishes. Verify before reporting done.
- **Skip donor-specific PII, secrets, and proprietary content** wholesale during Stage 1. If a donor file contains real names, emails, API keys, or internal company names, do not read its body beyond confirming the type; never transfer such content, even in inspiration form.
- **One LOG entry per `learn` run.** Not per item. The aggregate entry preserves the audit trail without flooding the log.
- **The return path is mandatory.** After application and focused validation,
  harvest new generalizable defects exposed by the adaptation as destination
  `scope: methodology` candidates. Keep their count distinct from lessons
  that already existed in the donor.
- **Stale sweep is acceptance.** Every file made stale by an approved learning is migrated (AUTO), decided (DECIDE), or deferred with a named condition (DEFER) in the same plan and LOG entry.
- **Kickoff-config learning is atomic and privacy-preserving.** Adopt generalizable policy/schema/round-trip manager/test/invocation/reporting improvements together. Never ingest donor raw telemetry, percentiles, values, comments, `extensions` data, overrides, model choices, or efforts; validate the local bundle with `bin/kickoff-config show`, the behavioral suite, scoped-update preservation tests, and a bounded watchdog smoke test.
- **Orchestration-evidence learning is atomic and privacy-preserving.** Never
  learn only a packet shape, candidate hash, finding block, watcher status, or
  final-gate rule. Adopt the policy, brief, deterministic managers,
  role/orchestrator contracts, docs/catalogs, and behavioral tests together.
  Preserve this repository's risk vocabulary and never ingest donor run
  directories, source copies, findings, hashes, gate artifacts, or telemetry.
  Candidate mismatches and indeterminate impact fail closed; the
  authoritative final gate remains mandatory.
- **Toolchain learning is atomic and target-owned.** Never learn only a gate
  wrapper or a raw command. Assess `bin/setup`, `bin/test`, `bin/check`,
  runtime wrappers, the runtime pin, manifest, lockfile, behavioral tests,
  policy, hooks, and callers together. Adopt generalizable mechanics while
  preserving this repository's language, supported runtime range, selected
  default runtime, package manager, dependency set, and lockfile resolution.
  Explicit overrides are authoritative and candidate runtimes are validated
  through the target's real dependency chain, not a version or existence
  check. Every dependency-bearing operational caller, generated command,
  tracked hook, and active instruction uses the repository runtime. Format
  coverage includes staged, unstaged, and nonignored untracked candidates.
  Hot loops, mutation gates, and detached processes resolve the underlying
  interpreter once and reuse it. Behavioral entrypoint tests are the minimum
  coverage floor; source-text checks may supplement but never replace them.
  Partial adoption is stale and blocking.
- **Skill-exclusion list.** `stamp` and the starter template's `example/` Python project are starter-only and never transferred. `learn` and `teach` themselves are universal — if the donor has a more evolved version, treat it like any other candidate; if this repo lacks them and the donor has them, propose adding them (the bootstrap procedure expects them in every methodology-following project).
