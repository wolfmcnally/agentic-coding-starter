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
last-reviewed: 2026-09-04
---

# Learn — Absorb patterns from another repo into this repo

This skill is **universal**. It runs inside any project that follows the agentic methodology — the starter template and every project derived from it. It treats *this* repository (whichever one invokes the skill) as the destination and `<donor-dir>` as the source of ideas. The user approves a plan before any change is made.

Three-stage skill-acquisition pipeline (inspired by the 2026 work on automated skill mining from agentic repositories): **structural analysis → semantic identification → translation**. Updates use a Copier-style discipline: the donor is read-only, conflicts are surfaced for the user, and template-controlled vs. user-controlled files are distinguished before any write.

The donor is **read-only** for the entire skill. We never modify the donor.

## Parse arguments

Raw arguments: `$ARGUMENTS`

- `<donor-dir>` — the directory to learn from. May be absolute, tilde-expanded, or relative to the CWD. Must exist and be readable.
- `<desc>` (optional) — narrows intent ("focus on the testing setup", "Unity specialization", "just policies"). When absent, do the broader assessment described in Stage 2 with **generality preference enabled**.

If `<donor-dir>` is missing or not a readable directory, refuse with `Usage: /learn <donor-dir> [<desc>] (Claude Code) or $learn <donor-dir> [<desc>] (Codex)` and exit.

## Pre-flight checks

1. **This repo follows the methodology.** Verify the universal invariants:
   - `AGENTS.md` is a symlink to `CLAUDE.md` (or both files exist and have identical content).
   - `.claude/agents/` contains the four canonical roles (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`).
   - `.claude/skills/kickoff/SKILL.md`, `.claude/skills/methodology/SKILL.md`, `.claude/skills/rule-one/SKILL.md`, and `briefs/rule-one-diagnostic-learning.md` exist. Rule One's skill and brief are one required methodology pair; either missing member fails pre-flight.
   - `bin/kickoff-config` and `kickoff.yaml` exist; `show` validates both config sections.
   - If `policies/orchestration-evidence.md` exists, `bin/kickoff-tree-id`, `bin/kickoff-evidence`, and their behavioral tests exist and the scripts are executable.
   - `briefs/`, `policies/`, `plan/` directories are present and non-empty.
   - `LOG.md` exists. If any fail, refuse with a specific error and exit. (If this skill was invoked in a repo that hasn't been bootstrapped, run the bootstrap procedure in [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) first, or invoke `/stamp` in Claude Code or `$stamp` in Codex from the starter template.)

2. **Donor is reachable.** `ls <donor-dir>` succeeds. If the donor is a git repo, capture its `HEAD` SHA for the audit trail; otherwise capture an mtime fingerprint of its top-level files. We don't require the donor to be a git repo.

3. **Working tree clean** (if this repo is a git repo). `learn` produces commits' worth of changes; running it on a dirty tree mixes the learning with other work. If unclean, list the uncommitted files and ask the user to stash or commit first.

## Plan-mode lifecycle (Stages 1–4)

Stages 1, 2, and 3 are read-only against both repos; Stage 4 surfaces the plan to the user; Stage 5 is the only stage that writes. This maps cleanly onto the harness's plan-mode contract — enter at the start of Stage 1, exit at Stage 4.

- **If the current harness exposes an `EnterPlanMode`-like tool** (Claude Code does today; Codex does not yet — see [openai/codex#11180](https://github.com/openai/codex/issues/11180)), **call it now** before starting Stage 1. The harness then enforces no-write through Stages 1–3; the bespoke "do not write to disk" rule below becomes belt-and-braces.
- **If the harness does not expose programmatic plan-mode entry**, proceed without calling anything — the bespoke read-only discipline through Stages 1–3 carries the contract. The user may have entered plan mode interactively (Codex CLI's `/plan`; the Codex desktop app's plan mode); that's fine and orthogonal to this skill.
- **At Stage 4**, if you entered plan mode in Stage 1 (or detected the user did so interactively and the harness exposes `ExitPlanMode`), place the Stage 3 plan body where the harness's plan-mode contract specifies — Claude Code names a plan file to write; other harnesses may differ — and then call `ExitPlanMode`. That plan body is the content the harness surfaces for approval. The user's accept / revise / reject from the plan-mode UI is the Stage 4 approval signal. If `ExitPlanMode` is not available, fall back to the free-text approval described in Stage 4.
- **Stage 5 (Apply) always runs outside plan mode.** Either the harness has handed control back after `ExitPlanMode`, or no plan mode was entered. Either way, edits to this repo are permitted only after the user has approved.

The skill's bespoke Stage 3 plan template stays the canonical plan body in both paths. Plan mode is a harness affordance layered on top, not a replacement for the structured plan.

## Stage 1 — Explore (read-only)

Build a structural map of the donor. **Do not** open every file; do targeted reads.

1. **Top-level inventory.** `ls -la <donor-dir>`. Note root files (READMEs, AGENTS.md, CLAUDE.md, language metadata) and directory shape.
2. **Methodology surfaces.** Check for `briefs/`, `policies/`, `plan/`, `LOG.md`, `.claude/`, `.codex/`, `.agents/`. Their presence — or absence of structure where this template has structure — is the first signal.
3. **Skills & agents.** `ls <donor>/.claude/skills/` and `ls <donor>/.claude/agents/`. Also `ls -la <donor>/.agents/skills/` (Codex CLI's native skill-discovery path — expected to be **directory-level symlinks** back to `<donor>/.claude/skills/<name>` per the workaround for [openai/codex#11314](https://github.com/openai/codex/issues/11314); surface novelty only if the *target* of the symlink is novel, or if an entry there is *not* a directory symlink — the latter typically indicates a stray from the Codex desktop "import settings" prompt and is not a learning candidate). Read the `SKILL.md` and agent files whose names are *not* in the canonical set (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`, `kickoff`, `methodology`, `rule-one`, `demo`, `stamp`, `learn`, `teach`, `treatise`, `roles`, `sweep`, `sweep-planning`, `sweep-coding`, `plain`). The novel ones are the candidates for learning. When a novel skill is thin and delegates its rules to a policy or brief, read that owning authority in full before classifying the skill; the wrapper alone is not the behavior being assessed.
4. **Briefs & policies.** `ls <donor>/briefs/` and `ls <donor>/policies/`. Read each one whose name doesn't already exist here. For names that *do* exist, do a structural diff (head + section list + line count) so the assessment knows whether the donor's version supersedes ours, diverges, or just paraphrases. **Rule One exception:** if the donor contains either a Rule One skill or a diagnostic-learning brief, inspect both surfaces as a single candidate. Record an absent mate as an incomplete donor pair; never treat the present member as a standalone import.
5. **Phase plan shape.** If `<donor>/plan/INDEX.md` exists, read it. Look for cross-cutting concerns or critical-files-map patterns we don't have.
6. **Language conventions.** Read `<donor>/CLAUDE.md` (or `AGENTS.md`) section by section. Note any architectural invariants, glossary entries, or conventions the donor pins that this starter doesn't.
7. **Repository-owned toolchain contract.** Inspect the donor's `bin/setup`, `bin/test`, `bin/check`, full-gate receipt manager, any runtime wrapper (`bin/python` or equivalent), runtime-version file, language metadata, lockfile, behavioral tests, policy, hooks, and workflow callers as one bundle. Note generalizable interface and failure-handling mechanics, including whether an explicit runtime override is authoritative and whether candidate selection is proven by a real dependency-chain load/run probe. Inventory dependency-bearing operational callers, generated commands, tracked hooks, and active instructions; verify that format coverage includes staged, unstaged, and nonignored untracked candidates; and identify hot loops, mutation gates, and detached processes that must resolve the repository interpreter once rather than reprobe per call. Verify that any durable full-gate reuse is bound to the exact candidate and environment fingerprint, preserves a complete log and terminal metadata, and fails closed to the full gate on every miss or query error. For a Python target, verify that the fingerprint is emitted through the repository-selected runtime path and includes the actual implementation, version, resolved executable and base-executable identities and file digests, machine, platform, and uv version—not the receipt helper's runtime or a version-file proxy. Keep candidate hashing separate from the venv and external runtime tree. Treat donor language/version/package-manager choices as donor state, not defaults to copy.
8. **Anti-patterns.** Note where the donor *violates* something the template considers a load-bearing invariant (status field in phase frontmatter; absolute paths; LOG.md hand-edits). Those are not for learning; mention them as confirmation the starter's rules are correct.
9. **Unified kickoff configuration.** Inspect the donor's schema shape, round-trip manager, behavioral tests, both role policies, `roles`, `kickoff` call sites, invocation brief, gitignore, and reporting contract as one bundle. Learn only generalizable mechanics, schema, algorithms, and defensible universal defaults. Never read, copy, or summarize raw telemetry, percentiles, model/effort choices, calibrated values, comments, `extensions` data, or project overrides.
10. **Candidate-bound orchestration evidence.** Inspect the donor's candidate identity implementation, authority/change/finding/gate schemas, revision packets, reviewer/coder evidence blocks, verification ladder, final-candidate checks, watcher outcome classification, policy, brief, docs, and behavioral tests as one bundle. Separate general mechanics from project-specific risk tags, thresholds, dependency selectors, assurance profiles, and private run artifacts.
11. **Lessons ledger.** Read `<donor>/lessons/` and `<donor>/lessons-archived/` (per the ledger contract in `policies/lessons.md`). Entries with `scope: methodology` are **first-class harvest input** — pre-digested, provenance-carrying learnings the donor's own phase work already distilled, far cheaper than rediscovering the same patterns from raw files. Archived `codified` entries point (via `graduated_to:`) at rules the donor already ratified — check whether those rules themselves are transfer candidates. Ignore `scope: local` entries beyond confirming the ledger's health. A donor with no ledger is itself a finding: it predates the lessons contract and is a `teach` candidate.

Output of Stage 1 is internal. The user sees Stage 3's plan.

### Instruction capabilities include their resources

Inspect each relevant skill entry and every directly linked execution resource as one capability, including same-named skills already present here. For kickoff, read `SKILL.md` plus `preflight.md`, `dispatch.md`, `planning.md`, `implementation.md`, `acceptance.md`, `close.md` and `recovery.md`, then their named authorities before judging adoption. A short entry or relocated Step is not missing behavior. Check the actual stage’s instructions and navigation, not a concatenation searched for required tokens. If approved for transfer, enumerate the complete directory, canonical owners and existing directory symlink; preserve relative link depth and update real consumers of moved locations. Apply `policies/cross-harness-parity.md`’s byte, marker, catalog and explicit-loading contract. Donor runtime choices, proof judgments and local authorities remain donor state.

## Stage 2 — Assess (categorize and tier)

For each candidate surfaced in Stage 1, classify on two axes.

### Transfer mode

- **Verbatim** — universal pattern that can be copied with name substitution. Example: a new policy file the donor wrote that obviously applies to every agentic project.
- **Shape-only** — the structure transfers; the content needs rewriting for the starter's audience. Example: a brief that documents donor-specific decisions whose *shape* (sections, frontmatter, voice) is reusable.
- **Inspiration** — worth a mention in this repo's briefs or comments, but not a direct file transfer. Example: a clever build-gate trick that doesn't apply here yet.
- **Out of scope** — donor-specific; doesn't belong in a general-purpose template. Example: domain logic, internal hooks, organization-specific allowlists.
- **Conflicts** — overlaps with an existing file or invariant here; surfaces a choice for the user.

### Generality tier (lower number = more general = higher priority)

- **Tier 1 — Methodology-level.** Orchestrator patterns, agent role definitions, policy structures, brief shapes, the briefs/policies/plan triplet itself, the Rule One skill-plus-diagnostic-brief pair, cross-harness orchestration machinery, role-timeout enforcement/calibration contracts, and review-intensity machinery. Improvements here help *every* downstream project. A donor lesson with `scope: methodology` maps here (or to Tier 2) by construction — the donor already made the generality call.
- **Tier 2 — Universal template content.** `.gitignore` patterns, build-gate idioms common across languages, log discipline rules, status-marker conventions.
- **Tier 3 — Language or platform specializations.** Python-specific lint rules, TypeScript-specific tsconfig defaults, Rust workspace patterns. These specialize the template for a language family.
- **Tier 4 — Domain specializations.** Unity game project structure, ML/data-science project structure, CDK-backed AWS project structure. These narrow the template to a niche.

### Selection rule

- **No `<desc>` given**: select candidates from Tier 1, then Tier 2. Only offer Tier 3 if those tiers have less than three actionable items. Only offer Tier 4 if Tier 3 also has less than three actionable items. This implements the user's directive: prioritize general improvements; specialize only when the general well is dry.
- **`<desc>` given**: use it to narrow. If the desc names a tier explicitly ("Unity specialization" → Tier 4), focus there. If the desc names a topic ("testing setup"), pull candidates across all tiers that touch that topic.

### Decision dialogue before the final plan

Identify every proposal, conflict, stale migration, or user-added request that requires judgment. Work through them **one at a time**:

1. Explain one decision in the [`plain`](../../../.claude/skills/plain/SKILL.md) register: what changes, why it matters, what breaks if the call is wrong, the realistic options, and your recommendation.
2. Stop for the user's decision. Answer questions about that decision without advancing to the next one.
3. Advance only after the user gives an explicit decision.
4. If a rendered question appears to have been swallowed, interrupted, or answered ambiguously, re-present the entire decision—including its context, options, and recommendation—rather than referring to a missing question.

User-added requests during the dialogue join the same queue and are decided before the plan. If no judgment calls exist, skip directly to the final plan. The dialogue remains read-only; an individual "yes" adopts that decision, not the write set.

## Stage 3 — Plan (present to user)

Immediately before composing the final plan, re-read the donor's git HEAD (or mtime fingerprint). If it changed since preflight, inspect the delta and reopen every affected decision; do not silently bind the plan to a moving source. Then regenerate the **complete** plan from the resolved decisions. Do not offer an incremental patch or assume the user can reconstruct it from the dialogue.

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
gates, durable full-gate receipts, runtime selection, metadata, or locking must enumerate the complete
bundle and classify partial existing adoption as stale.
The proposed tests must execute the adapted entry points with controlled
toolchain stubs; source-text assertions alone do not satisfy the behavioral
coverage floor. A Rule One proposal must name both
`.claude/skills/rule-one/SKILL.md` and
`briefs/rule-one-diagnostic-learning.md`, including an explicit `UNCHANGED`
compatibility finding when one member requires no write.

## Proposed write set (will only be applied after approval)

- `<this-repo file>` — NEW | MODIFY (diff size)
- ...

## Proposed LOG.md entry (after apply)

```
## <YYYY-MM-DD HH:MM> — LEARN
Donor: <donor-name> @ <sha or fp> Items absorbed: <count>, by tier T1=<n>/T2=<n>/T3=<n>/T4=<n> Donor lessons harvested: <count> (<count> absorbed as rule proposals; <count> filed to lessons/) Application-found return candidates: <count> filed to lessons/ Stale-in-light-of-learning migrations: <count> (AUTO); <count> DECIDE; <count> DEFER Files touched: <count>
```
```

When this repo has an external-reference anonymization policy, render the proposed committed entry through it at plan time: use `Donor A` (or the policy's equivalent), replace the external SHA with `<sha withheld>` or an allowed fingerprint, and omit proprietary donor paths and identifiers. The conversation plan may identify the donor for the user; the committed LOG entry may not violate the destination's publication policy.

End the plan with one line: **"Approve this plan to apply, ask for revisions, or reject."**

## Stage 4 — Approve (gate)

Do not write a single byte to disk in this repo until the user clearly approves.

**Two paths, by harness capability** (per the Plan-mode lifecycle section above):

- **Plan-mode path.** If you entered plan mode at Stage 1 (or the user did interactively), place the Stage 3 plan body where the harness's plan-mode contract specifies (Claude Code names a plan file to write), then call `ExitPlanMode`. The harness presents accept / revise / reject affordances; the user's choice is the approval signal. A plain accept maps to "approved (all items)"; revise routes back to Stage 3 with the user's constraints; reject means write nothing and no LOG entry.
- **Free-text path** (when plan mode is unavailable in the current harness). Wait for a clear approval signal in chat: "approved", "go ahead", "apply it", "yes", or specific opt-in like "apply items 1, 3, and 5 only." Revisions return to Stage 3; rejections mean write nothing and no LOG entry.

If the user partially approves (a subset of items, whether via plan-mode revise-with-constraints or free-text opt-in), the apply step honors the subset exactly. Track which items were dropped for the LOG entry.

## Stage 5 — Apply

Once approved, apply the approved items. Before importing any donor remedy for a defect — a hardening, a guard, an error-handling change — verify the defect actually **reproduces in this repo**: shared lineage makes the donor's diagnosis plausible, never established, and the destination may already have solved the same incident differently (sometimes more strictly, so the donor's "fix" would be a regression here). When the defect does not reproduce, record the divergence in the LOG entry instead of importing the remedy. This verification is per item, hunk by hunk — an atomic bundle can be half genuine gap, half regression-wearing-the-shape-of-a-fix. Order:

1. Add NEW files (policies first, then briefs, then skills/agents, then plan files, then code).
2. MODIFY existing files (smallest diffs first; one logical change per Edit call). If Rule One is approved, apply its skill and diagnostic brief as one transaction: the resulting candidate must contain both, and an update to either includes a compatibility check and any required update to the other.
3. Apply every approved AUTO item from "Stale-in-light-of-learning"; carry DECIDE/DEFER items into the LOG entry with their decision or condition.
4. Resolve every cross-harness parity obligation that the changes create:
   - If a `.claude/agents/<role>.md` body changed, refresh `.codex/agents/<role>.toml` (the wrapper body changes only if the description line changed; the pointer stays the same).
   - If a new `.claude/skills/<name>/SKILL.md` was added, add the matching `.agents/skills/<name>` directory symlink for Codex discovery.
   - See [`policies/cross-harness-parity.md`](../../../policies/cross-harness-parity.md).
5. Update `CLAUDE.md`'s catalogs (briefs catalog, policies catalog) so every new file is indexed.
6. File harvested donor lessons that were approved as ledger entries rather than immediate rule changes: write each to this repo's `lessons/<slug>.md` with `source: learn`, anonymized per this repo's publication policy, and run `./bin/lessons validate`. A donor lesson approved as a direct rule change lands as its rule edit instead (steps 1–2) — not both.
7. Run focused wrapper tests through `./bin/test tests/test_toolchain_entrypoints.py tests/test_check.py tests/test_check_receipt.py -q`. If an older methodology-following destination lacks the atomic toolchain contract, run the exact focused commands declared by its current metadata and `kickoff`, and flag every missing contract member as a learning candidate.
8. Re-run the caller inventory and verify that format checking covers staged, unstaged, and nonignored untracked candidates. For any repeated, mutation-sensitive, generated, or detached workflow, prove that the underlying repository interpreter is resolved once and reused.
9. **Harvest the application return path.** Review defects and improvements discovered while translating, applying, and validating the approved bundle that were not already donor-ledger inputs. Applying a donor pattern is an empirical test of that pattern's contract. For each generalizable finding, check both destination lesson directories, append an occurrence to a match or file a new `scope: methodology`, `source: learn` candidate, and preserve the donor as read-only. Do not turn the finding directly into another rule edit in this step: application-found candidates enter the ledger for later human ratification. Run `./bin/lessons validate` and `./bin/lessons candidates`; count these separately from donor lessons.
10. Construct the complete LEARN entry in a temporary file and append it at true EOF with `./bin/log-append < <block-file>`. Format it as proposed in the plan, report donor-ledger and application-found lesson counts separately, and apply this repository's anonymization policy before the write because it lands in Starter.
11. Run `./bin/check all` against the complete unchanged candidate after all rule, lesson, stale-migration, and LOG writes. This is the authoritative final gate; any subsequent candidate change invalidates it.

**Deliver the approved learning.** Per [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md) and [`policies/commit-staging.md`](../../../policies/commit-staging.md), once the complete unchanged candidate passes `./bin/check all`, re-check the live tree, stage only the explicit apply paths, inspect the staged diff, create an ordinary factual commit, verify its file set, and make a non-force push to one unambiguous configured upstream, then verify clean aligned tips. Park delivery on any unexpected path, unresolved shared-file ownership, unresolved gate, hook refusal, missing or ambiguous upstream, divergence, or destructive Git need — and report it. Either way, report the file list, the build-gate status, and any unresolved manual steps: the user still judges whether the learning was the right one to absorb, and that judgment is not what the commit settles.

## Rules

- **The donor is read-only.** Never write to `<donor-dir>` under any circumstances. If the user wants to push improvements back to the donor, that is a separate `/teach <donor-dir>` invocation in Claude Code or `$teach <donor-dir>` invocation in Codex.
- **Generality first.** Default to Tier 1+2 transfers. Specialize only when those are exhausted or the user's `<desc>` requested it.
- **Direction of advance is established per item, never per repo.** A donor being "ahead" overall proves nothing about any one file, hunk, or fix. Before replacing a shared file, classify every hunk by direction (destination-ahead hunks are re-applied on top); before importing a donor remedy, verify its defect reproduces in the destination and record the divergence when it does not. Both failure modes are silent: reverting a stronger assertion or relaxing a stricter guard cannot fail any gate.
- **Approval is mandatory.** No bytes change in this repo before explicit approval.
- **Cross-harness parity is non-negotiable.** Any change touching `.claude/` or `.codex/` updates both surfaces in the same apply step.
- **Catalog drift is forbidden.** `CLAUDE.md`'s catalogs reflect every file in `briefs/` and `policies/` after the apply finishes, and `docs/README.md` links every entry under `docs/`. Verify before reporting done.
- **A donor's `docs/` is donor state.** Pinned third-party documents are the donor's dependencies; never transfer them. What may transfer is the `docs/` *contract* itself when the donor's version of `policies/docs.md`, its catalog shape, or its `check-catalogs` enforcement improves on ours.
- **Skip donor-specific PII, secrets, and proprietary content** wholesale during Stage 1. If a donor file contains real names, emails, API keys, or internal company names, do not read its body beyond confirming the type; never transfer such content, even in inspiration form.
- **One LOG entry per `learn` run.** Not per item. The aggregate entry preserves the audit trail without flooding the log.
- **The return path is mandatory.** After application and focused validation, harvest new generalizable defects exposed by the adaptation as destination `scope: methodology` candidates. Keep their count distinct from lessons that already existed in the donor.
- **Stale sweep is acceptance.** Every file made stale by an approved learning is migrated (AUTO), decided (DECIDE), or deferred with a named condition (DEFER) in the same plan and LOG entry.
- **Rule One learning is atomic.** `.claude/skills/rule-one/SKILL.md` is the portable prescription and `briefs/rule-one-diagnostic-learning.md` is its diagnostic rationale. Assess both whenever a donor exposes either one; import or update them only as a compatible pair, maintain the Codex skill symlink and both catalogs, and never accept a candidate that leaves one member absent.
- **Kickoff-config learning is atomic and privacy-preserving.** Adopt generalizable policy/schema/round-trip manager/test/invocation/reporting improvements together. Never ingest donor raw telemetry, percentiles, values, comments, `extensions` data, overrides, model choices, or efforts; validate the local bundle with `bin/kickoff-config show`, the behavioral suite, scoped-update preservation tests, and a bounded watchdog smoke test.
- **Orchestration-evidence learning is atomic and privacy-preserving.** Never learn only a packet shape, candidate hash, finding block, watcher status, or final-gate rule. Adopt the policy, brief, deterministic managers, role/orchestrator contracts, docs/catalogs, and behavioral tests together. Preserve this repository's risk vocabulary and never ingest donor run directories, source copies, findings, hashes, gate artifacts, or telemetry. Candidate mismatches and indeterminate impact fail closed; the authoritative final gate remains mandatory.
- **Deterministic orchestration-control learning is atomic and recipient-owned.** Assess and transfer `briefs/deterministic-orchestration-control-plane.md`, `policies/orchestration-control-plane.md`, `bin/kickoff-command-zero`, `bin/check-log`, `bin/check-log-prefix`, `bin/check-log-monotonic`, `bin/log-append`, `bin/log-relocate`, `bin/normalize-final-newline`, `lib/agentic_starter/candidate_boundaries.py`, `lib/agentic_starter/kickoff_runbook.py`, `lib/agentic_starter/log_blocks.py`, `tests/test_kickoff_control_plane.py`, and `tests/test_log_control_plane.py` with their `kickoff-config`, `kickoff-evidence`, `kickoff-tree-id`, `bin/check`, hook, skill, catalog, bootstrap, and proof-estate integration. Transfer the obligation and procedure, never donor command rows, selector choices, venue inventory, inert-path judgments, manifests, receipts, logs, or repair history. The recipient defines and proves those locally. Partial adoption is stale and blocking.
- **Toolchain learning is atomic and target-owned.** Never learn only a gate wrapper or a raw command. Assess `bin/setup`, `bin/test`, `bin/check`, runtime wrappers, the runtime pin, manifest, lockfile, behavioral tests, policy, hooks, and callers together. Adopt generalizable mechanics while preserving this repository's language, supported runtime range, selected default runtime, package manager, dependency set, and lockfile resolution. Explicit overrides are authoritative and candidate runtimes are validated through the target's real dependency chain, not a version or existence check. Every dependency-bearing operational caller, generated command, tracked hook, and active instruction uses the repository runtime. Format coverage includes staged, unstaged, and nonignored untracked candidates. Shell entry points resolve their own symlink chains before deriving the repository root; working-directory independence is not symlink independence. Hot loops, mutation gates, and detached processes resolve the underlying interpreter once and reuse it. Behavioral entrypoint tests are the minimum coverage floor; source-text checks may supplement but never replace them. Partial adoption is stale and blocking.
- **Test-governance learning is atomic and recipient-owned.** When a donor has proof-estate value governance, assess `briefs/test-suite-value-governance.md`, `policies/test-suite-governance.md`, `tests/proof-estate.yaml`, `bin/test-governance`, `lib/agentic_starter/test_governance.py`, `tests/test_test_governance.py`, `tests/test_pre_commit.py`, and `reports/test-governance/README.md` with the lane/gate/hook callers, deterministic inventory/validation/selection/report manager, lane and gate integration, hook check, behavioral fixtures, effectiveness-evidence shape, catalogs, transfer rules, and lessons together. Adopt the generalized machinery or none of it. Never copy donor family choices, selectors, risk labels, timing values, thresholds, defect corpus, mutation corpus, survivors, reports, or audit judgments. Initial adoption freezes this repository's whole estate, performs its own Pareto assay, physically removes dominated proofs, and dispositions every baseline proof. The recipient targets at most 20% of both frozen family and leaf counts while preserving at least 80% historical and held-out recall plus direct proof for every applicable critical risk; an unsatisfied conjunction parks for the owner. Zero-net-growth, complete removal, post-reset retirement-before-admission replay, and executable periodic reassessment transfer with the machinery. Invalid or unmapped selection widens to full; both close gates remain full.
- **Skill-exclusion list.** `stamp` and the starter template's `example/` Python project are starter-only and never transferred. `learn` and `teach` themselves are universal — if the donor has a more evolved version, treat it like any other candidate; if this repo lacks them and the donor has them, propose adding them (the bootstrap procedure expects them in every methodology-following project).


## Candidate declaration transfer

The candidate boundary transfers atomically: `candidate-partition.yaml`, `bin/check-candidate-partition`, `lib/agentic_starter/candidate_boundaries.py`, candidate/evidence managers, the staged hook, gate inventory, and their behavioral fixtures. Generate the recipient's explicit active inventory and retain only its approved bookkeeping exclusions; never copy the donor's path judgments. The declaration remains active, unclassified tracked files refuse, unclassified nonignored untracked files remain included, and complete-tree delivery receipts remain mandatory. Verify the staged checker by actually tripping it in an isolated fixture. The tiny supported YAML subset and pattern syntax are defined in `policies/orchestration-evidence.md`.
