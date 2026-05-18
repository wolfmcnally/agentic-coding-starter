---
name: teach
description: >-
  Explore another repository to assess what techniques, patterns, or
  template content from THIS starter should be applied to it. Produces a
  structured plan ranked by generality, awaits user approval, then applies
  approved changes to the target repo. Use to push template improvements
  outward to projects that were stamped from an older version, or to
  retrofit an existing project with the agentic methodology. Invoke as
  /teach <target-dir> [<desc>].
argument-hint: "<target-dir> [<desc>]"
---

# /teach — Apply patterns from this repo to another repo

This skill is **universal**. It runs inside any project that follows the agentic methodology — the starter template and every project derived from it. It treats *this* repository (whichever one is invoking `/teach`) as the source of patterns and `<target-dir>` as the destination. The user approves a plan before any change is made to the target.

The pipeline is the same three-stage shape as `/learn` (structural analysis → semantic identification → translation), inverted: we read both repos but only write to the target. Updates use a Copier-style discipline — the target's customizations are preserved by default; files that exist verbatim in the target may be overwritten; conflicts are surfaced for the user.

`/teach` is **improvement-only**. It never replaces target content with source content that is less elaborated, less specialized, or less capable than what the target already has. When the target has surpassed the source in some area — a richer skill body, a custom step in `/kickoff`, a more detailed policy — that area is surfaced as a candidate for a future `/learn` invocation in the reverse direction, not pulled backward. The bar for any proposed change is *strict improvement to the target*; everything else is preserved or noted as a reverse-direction `/learn` candidate.

This repo is **read-only** for the entire skill. We never modify the teaching repo while teaching.

## When `/teach` makes sense versus `/starter`

- **`/starter`** (available only in the starter template) stamps out a *brand-new* project from the template. Use when the target directory is empty or doesn't exist.
- **`/teach`** retrofits or upgrades an *existing* project. Use when the target already has work in it — either a previously stamped project that has fallen behind, or a project that didn't start from the template but wants to adopt parts of the methodology, or a project that should adopt a particular pattern this repo has evolved.

If you're invoking from the starter template and the target is empty or doesn't exist, refuse and suggest `/starter` instead. If you're invoking from a non-starter repo and the target is empty, refuse and tell the user that the right starting point is `/starter` from the starter template — `/teach` retrofits existing projects, it does not bootstrap new ones from scratch.

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- `<target-dir>` — the directory to teach. May be absolute, tilde-expanded, or relative to the CWD. Must exist and have content.
- `<desc>` (optional) — narrows intent ("just bring the policies up to date", "add the kickoff skill", "modernize the four agents"). When absent, do the broader assessment with **generality preference enabled**.

If `<target-dir>` is missing or is an empty/non-existent directory, refuse with `Usage: /teach <target-dir> [<desc>]` (and, if non-existent, suggest `/starter` instead) and exit.

## Pre-flight checks

1. **This repo follows the methodology.** Verify the universal invariants:
   - `AGENTS.md` is a symlink to `CLAUDE.md` (or both files exist and have identical content).
   - `.claude/agents/` contains the four canonical roles (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`).
   - `.claude/skills/kickoff/SKILL.md` exists.
   - `.claude/skills/methodology/SKILL.md` exists.
   - `briefs/`, `policies/`, `plan/` directories are present and non-empty.
   - `LOG.md` exists.
   If any fail, refuse before touching anything.

2. **Target is reachable and non-empty.** `ls -la <target-dir>` returns at least one substantive file (anything beyond `.git/`, `.DS_Store`, or empty marker files).

3. **Target's working tree clean** (if it is a git repo). `/teach` produces commits' worth of changes; running it on a dirty tree mixes the upgrade with other work. If unclean, refuse and ask the user to stash or commit in the target first.

4. **Target's harness compatibility.** Note which agent harnesses the target appears to use (`CLAUDE.md` / `AGENTS.md` at root; `.claude/` and/or `.codex/` directories). Some teachings only apply if a particular harness is in use.

## Stage 1 — Explore (read-only)

Build a structural map of the target. Mirror Stage 1 of `/learn`, but from the opposite vantage:

1. **Top-level inventory.** `ls -la <target-dir>`. Note root files (READMEs, AGENTS.md, CLAUDE.md, language metadata) and directory shape.
2. **Methodology surfaces.** Check for `briefs/`, `policies/`, `plan/`, `LOG.md`, `.claude/`, `.codex/`. Their absence vs. partial presence vs. divergent presence is the first signal.
3. **What the target already has from the template.** If any file in the target matches (by name and content shape) a file in this starter, mark it as "in sync," "diverged," or "absent." This is the structural diff that drives the plan.
4. **What the target has that the starter doesn't.** Custom skills, custom agents, project-specific briefs and policies, domain conventions. **These are the target's specializations.** Treat them as load-bearing: never propose to remove or flatten them.
5. **Phase plan shape.** If the target has a `plan/INDEX.md`, read it. Note which phase is `⬅️` (in-flight work the teaching must not stomp on).
6. **Language & build gates.** Read the target's language metadata. The teaching's apply step will adapt build-gate commands to whatever the target's primary language is, not to Python defaults.
7. **Active work signals.** Read the target's `LOG.md` if present. A phase in `🚧` is a clear "do not stomp" signal — the teaching apply step waits for that phase or limits itself to additive, non-conflicting changes.

Output of Stage 1 is internal. The user sees Stage 3's plan.

## Stage 2 — Assess (categorize and tier)

For each file or pattern in *this* starter, evaluate against the target. Use the same two-axis classification as `/learn`:

### Transfer mode

For each candidate file or pattern, compare bidirectionally: starter → target *and* target → starter. The improvement-only rule means the source's version must be strictly better than the target's for any change to be proposed; otherwise the divergence either stays untouched or flips into the "Surface for `/learn`" bucket.

- **Verbatim** — copy from this starter into the target with name substitution (`Agentic Coding Starter Template` → target project name). Use only when the target lacks the file entirely. Example: a policy file the target does not have.
- **Shape-only** — bring the structure but write project-specific content. Use only when the target lacks the file entirely. Example: `briefs/BRIEF.md` shape with the target's actual thesis (rare in `/teach`; `/starter` already does this for new projects).
- **Update-in-place** — propose only when the starter's version is **strictly an improvement** over the target's: it has every meaningful section, step, example, or rule the target's version has, plus genuine additions; no regressions; no loss of target-specific elaboration. If the target's version is more elaborated, more specialized, or has features the starter's lacks (extra steps, project-specific examples, richer error handling, deeper structure), do **not** propose an update; flip to "Surface for `/learn`" instead. When in doubt, prefer non-action.
- **Surface for `/learn`** — the target has innovations the *source* lacks. Name them in the plan as candidates for a future `/learn` invocation against this target. No file change in either repo during `/teach`. Examples: a custom orchestrator step, a richer agent body, a policy this starter does not have.
- **Inspiration** — surface in the plan as a written suggestion to the target's owner, not a file change. Different from "Surface for `/learn`": Inspiration is a nudge to the *target's* owner to consider doing something new; Surface for `/learn` is a nudge to the *source's* maintainer to consider adopting what the target has.
- **Out of scope** — donor-specific (starter-specific meta-skills like `/starter`, the template's `example/` project, and any policy explicitly marked starter-only — currently `policies/anonymize-log-references.md`). Do not transfer.
- **Conflicts** — would override target customizations *and* the source's version isn't a strict improvement; surfaces a choice for the user. If the source's version were a strict improvement, it would be "Update-in-place" instead.

### Generality tier

Same tiers as `/learn`:

- **Tier 1 — Methodology-level.** The four canonical agents, the orchestrator skill, the briefs/policies/plan triplet, the LOG.md contract.
- **Tier 2 — Universal template content.** Every file under `policies/`, `methodology.md`, `agentic-bootstrap.md`, the `AGENTS.md` symlink convention, the `.codex/prompts/<name>.md` file-symlink convention, and the `.agents/skills/<name>` directory-symlink convention (Codex CLI's native skill-discovery path, per [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills); directory-symlink shape because of [openai/codex#11314](https://github.com/openai/codex/issues/11314)).
- **Tier 3 — Language/platform specializations.** Build-gate command lists for the target's language.
- **Tier 4 — Domain specializations.** Only if a domain-specific extension lives in this starter (uncommon; this template aims to stay general).

### Selection rule

Same as `/learn`:

- **No `<desc>` given**: select from Tier 1, then Tier 2. Only offer Tier 3 if those have less than three actionable items.
- **`<desc>` given**: use it to narrow.

### Stale-in-light-of-teaching sweep

Adding a new policy, brief, or skill to a target rarely lands in isolation. The teaching makes parts of the *existing* target stale — files that pre-dated the new content and used a shape, name, path, or convention the new content now supersedes. **Identifying and migrating those stale items is part of `/teach`'s acceptance, not a follow-up task.**

For each proposed addition or update, ask:

- **Catalog drift.** Does the target's `CLAUDE.md` carry a briefs catalog, policies catalog, or critical-files map? Every new brief, policy, or anchor file added by this teach pass must be indexed there. Missing catalogs (target lacks them entirely) → add the catalog as part of the apply, not as a follow-up.
- **Convention drift.** Does the new content (typically a policy) establish a richer shape than the target's pre-existing files of the same kind? Common cases: a new `user-blockers.md` policy that formalizes a richer shape than the target's existing `user-blockers.md` file; a new `phase-status.md` policy that the target's existing `plan/INDEX.md` doesn't yet enforce. Migrate the target's file to the new shape *as part of the apply* when the migration is mechanical (header text, section structure, file format); surface for user decision when the migration would touch live content.
- **Description drift.** Does the target's `CLAUDE.md` (or any other top-level doc) describe behavior the new policy now codifies more thoroughly? Augment the existing description to point at the new policy and pick up its richer conventions. Do not duplicate the policy body — link to it.
- **Cross-reference drift.** Does the target's `plan/INDEX.md` "Critical-Files Map" (or equivalent) reference policies and briefs? Every new universal policy and brief added by this teach pass should appear there.
- **Naming drift.** Does the target use a name or path the new content replaces? Update every call site.

Each stale item gets one of three classifications:

- **Auto-migrate**: mechanical change with no judgment call (catalog entry, link addition, header restructure). Apply as part of the same teach run.
- **Surface for user decision**: touches live content (e.g., real entries in a queue file) or requires a project-specific value the skill cannot guess. List in the plan's "Stale-in-light-of-teaching" section; carry to the LOG entry as a manual follow-up.
- **Defer with reason**: the migration depends on later phases (e.g., naming a thing Phase 0 hasn't decided yet). List with the deferral reason.

### Critical "do not stomp" rules during assessment

- **Improvements only.** Never propose replacing target content with source content that is less elaborated, less specialized, or less capable. If a target file has extra sections, extra steps, custom examples, or richer structure compared to its starter counterpart, that file is a target specialization — leave it alone and surface it as a `/learn` candidate instead. The bar for any proposed file change is *strict improvement to the target*.
- **Provenance can flip the classification.** A target file that looks like a specialization (extra sections, project-specific examples) may instead be a naive earlier copy from a *different* donor repo that the target's owner never refined — in which case the source's version *is* a strict improvement and update-in-place is correct. Content alone cannot distinguish the two cases. When a candidate update-in-place is blocked because the target's version *looks* more elaborated, surface it in the plan with both readings explicitly — *"target specialization, preserve"* AND *"earlier copy from another donor, update"* — and let the user disambiguate at approval time. Default to preserve when no provenance signal is available; only update when the user (or a clear repo signal — e.g., a `# Imported verbatim from <other-donor>` header) confirms naive-copy provenance.
- **Never propose removing a target's custom skill, agent, brief, or policy.** Those are the target's specializations.
- **Never propose modifying a file the target marks as `⬅️` or `🚧` in its plan.** Active phase work belongs to the target's `/kickoff`, not to a teaching pass.
- **Skill-exclusion list during transfer.** `/starter` and the starter template's `example/` Python project are starter-only — they are never taught from anywhere. `/learn` and `/teach` themselves are universal — if the teaching repo has them and the target lacks them, they may be transferred like any other skill.
- **Honor the target's primary language.** If the target is a Node project, do not propose adding `pyproject.toml` from this template. Adapt commands and references accordingly.

## Stage 3 — Plan (present to user)

Produce a structured plan inline in the conversation. Use this exact format:

```markdown
# Teaching Plan: <this-repo> → <target-name>

**Target**: `<absolute-or-relative-target-path>` (git SHA `<sha>` | mtime fingerprint `<fp>`)
**This repo's HEAD**: `<sha or "untracked">`
**Generality preference**: <enabled (no desc) | narrowed by "<desc>">
**Target's primary language**: <python | typescript | rust | go | other | mixed>
**Target's in-flight phase**: <Phase X.Y (🚧) | none>

## Summary

<One paragraph: what the target is missing, what it has that we won't touch, what we'll propose to apply.>

## Proposals (ranked by tier, then by impact)

### Tier 1 — Methodology-level

#### 1. <Short name>
- **Transfer mode**: Verbatim | Shape-only | Update-in-place | Inspiration | Conflicts
- **Source in this repo**: `<this-repo-relative-path>`
- **Target path**: `<target-relative-path>` (NEW | MODIFY | CONFLICTS-WITH-<path>)
- **Why it generalizes**: <one or two sentences>
- **Risk to target's existing work**: <none | low | medium | high — what could go wrong>
- **Estimated change**: <line count or file count>

#### 2. ...

### Tier 2 — Universal template content
(same structure)

### Tier 3 — Language/platform specializations
(only if Tier 1+2 yielded fewer than three items, or `<desc>` requested)

### Tier 4 — Domain specializations
(only if Tier 1+2+3 are exhausted, or `<desc>` explicitly requested)

## Target preservations (will NOT touch)

- `<target-only file>` — <reason: target's custom skill | active phase | language-specific | proprietary content>
- ...

## Patterns to feed back via `/learn` (target → source)

Areas where the target has surpassed this source. List each as a candidate for a future `/learn` invocation against the target. No file change in either repo from this `/teach` run; the goal is to make sure the source's maintainer sees what they could absorb. Empty section is fine — declare "None identified" rather than omit.

- `<target path>` — <one-line description of what the target does better and why it generalizes>
- ...

## Stale-in-light-of-teaching (will be migrated or surfaced)

Items in the *existing* target that go stale because of this teach pass's additions. **These are part of the apply, not follow-up work.** Each entry is classified:

- **AUTO** `<target file>` — <one-line: what changes and why the new content makes it stale>. Mechanical; applied as part of this teach run.
- **DECIDE** `<target file>` — <one-line: what would change>. Touches live content or requires a project-specific decision; surfaced here for user choice.
- **DEFER** `<target file>` — <one-line: what would change once <condition> is met>. Migration depends on a later phase or external event.

If nothing in the target goes stale because of this pass, declare "None identified" rather than omit the section.

## Conflicts requiring user decision

- `<target file>`: target's version <describes-the-divergence>. Options:
  - **Keep target's.** (default-safe; this is a target specialization)
  - **Replace with this starter's.** (target's version is a naive earlier copy from another donor or a stale fork — update-in-place is the strict improvement)
  - **Merge** (target has innovations on top of a stale base — graft target's additions onto this starter's current shape).

## Proposed write set (will only be applied after approval)

- `<target file>` — NEW | MODIFY (diff size)
- ...

## Proposed target-LOG.md entry (after apply)

```
## <YYYY-MM-DD HH:MM> — TAUGHT FROM TEMPLATE
Source: <this-repo-name> @ <sha or fp>
Items applied: <count>, by tier T1=<n>/T2=<n>/T3=<n>/T4=<n>
Files touched in target: <count>
```
```

End the plan with one line: **"Approve this plan to apply to the target, ask for revisions, or reject."**

## Stage 4 — Approve (gate)

Do not write a single byte to the target until the user clearly approves. Acceptable approval signals: "approved", "go ahead", "apply it", "yes", or specific opt-in like "apply items 1, 3, and 5 only."

If the user asks for revisions, return to Stage 3 with the new constraints. If the user rejects, write nothing.

If the user partially approves, the apply step honors the subset exactly.

## Stage 5 — Apply

Once approved, apply the approved items to the target. Order:

1. Add NEW files in the target (policies first, then briefs, then skills/agents/prompts, then plan files, then any other infrastructure).
2. MODIFY existing target files (smallest diffs first; one logical change per Edit call).
3. Resolve cross-harness parity in the target across **all four parity surfaces** (per `policies/cross-harness-parity.md`). Default to intra-repo symlinks whenever formats match; drop to a wrapper file only when the parser would reject the symlinked content:
   - **Top-level instructions** — `CLAUDE.md` ↔ `AGENTS.md` (symlink — formats match). Edits to `CLAUDE.md` propagate automatically through the symlink. Verify: `test -L <target>/AGENTS.md && [ "$(readlink <target>/AGENTS.md)" = "CLAUDE.md" ]`. If the target's `AGENTS.md` is a file rather than a symlink, replace it: `rm <target>/AGENTS.md && ln -s CLAUDE.md <target>/AGENTS.md`.
   - **Skills — Codex slash-command surface** — `.claude/skills/<name>/SKILL.md` ↔ `.codex/prompts/<name>.md` (symlink — formats match). For every skill added or modified, create or refresh the symlink: `ln -s ../../.claude/skills/<name>/SKILL.md <target>/.codex/prompts/<name>.md`. If a pointer file or inline-duplicated wrapper is already in place, replace it with the symlink — both are deprecated parity-violation shapes.
   - **Skills — Codex native skill-discovery surface** — `.claude/skills/<name>/` ↔ `.agents/skills/<name>` (*directory* symlink). For every universal skill added or modified (kickoff, methodology, learn, teach — *not* `/starter`, which is starter-only): `mkdir -p <target>/.agents/skills && ln -s ../../.claude/skills/<name> <target>/.agents/skills/<name>`. **Directory-level, not file-level** — Codex CLI does not follow file-level symlinks inside a skill directory ([openai/codex#11314](https://github.com/openai/codex/issues/11314)), but does traverse a symlinked skill directory. If the target has the old, broken file-level shape (`.agents/skills/<name>/SKILL.md` as a file symlink) or a non-symlink directory (likely from the Codex desktop "import settings" prompt, which produces buggy copies), `rm -rf <target>/.agents/skills/<name>` and replace with the directory-level symlink. Verify with `test -L <target>/.agents/skills/<name> && test -d <target>/.agents/skills/<name>` and `test -f <target>/.agents/skills/<name>/SKILL.md` (reaching SKILL.md through the symlink).
   - **Agent roles** — `.claude/agents/<role>.md` ↔ `.codex/agents/<role>.toml` (thin wrapper TOML — symlink not possible because TOML ≠ Markdown). For every agent .md added or modified, add or refresh the .toml as a thin pointer: a `description` field plus a `developer_instructions` body that just says "Read .claude/agents/<role>.md and follow it." Full-body inline TOMLs are the parity-violation shape to repair on sight.
   - After all edits, run the parity verification sweep from `policies/cross-harness-parity.md` §Verification against the target. A clean target prints `AGENTS.md OK` and nothing else. Any "not a symlink" / "wrong target" / "missing peer" line is a parity violation introduced (or left unrepaired) by this apply pass and must be fixed before reporting completion.
4. Update the target's `CLAUDE.md` catalogs (briefs catalog, policies catalog, critical-files map) so every new file is indexed. Add the catalog as a new section when the target lacks it.
5. Substitute names in transferred files: `Agentic Coding Starter Template` → target's project name; `agentic-coding-starter-template` → target's slug; references to this template's `example/` package → target's primary surface.
6. **Adapt build-gate commands** in the target's `.claude/skills/kickoff/SKILL.md` (and the four canonical agents) to the target's primary language, replacing this template's Python defaults wherever they leaked through verbatim transfers.
7. **Apply the stale-in-light-of-teaching migrations.** Walk the "Stale-in-light-of-teaching" section of the approved plan and execute every AUTO item (catalog entries, link additions, header restructures, file-shape migrations to richer conventions established by newly-added policies). DECIDE items get listed in the LOG entry as a manual follow-up for the target's owner. DEFER items get listed with their deferral condition.
8. Run the parity verification sweep (per step 3) **and** the stale-sweep check — i.e., re-confirm that every newly-added brief and policy is now indexed in the target's catalogs, and that every convention-drift item flagged in the plan has either been migrated or surfaced. A teach run is not "done" until the stale sweep is reported.
9. Run the target's own build gates (whatever the target's `pyproject.toml` / `package.json` / `Cargo.toml` declares) to confirm nothing regressed. If the target has no gates yet, skip — but flag in the report.
10. Append the TAUGHT FROM TEMPLATE entry to the target's `LOG.md` (create the file with the standard header if it doesn't exist). The entry lists the transferred items, the stale items migrated, the stale items surfaced for user decision, and the patterns to feed back via `/learn`.

**Do not auto-commit in the target.** The target's owner owns commits. Report the file list, build-gate status, and any unresolved manual steps.

**Do not write anything to *this* repo.** This skill is read-only against the starter. If the user wants to capture a learning here as a result of the teaching exchange, that's a separate `/learn` invocation against the target afterward.

## Rules

- **Improvements only.** Every proposed change must be a strict improvement to the target. Never replace target content with source content that is less elaborated, less specialized, or less capable. When the target has surpassed the source, the right move is to surface it for a future `/learn`, not to drag the target backward.
- **Stale sweep is acceptance, not follow-up.** A `/teach` run is not done when the new files have been copied in. It is done when every file in the target that went stale *because of* the apply has been migrated (AUTO), surfaced for a user decision (DECIDE), or named with a deferral reason (DEFER). Empty catalogs, orphan policies, and existing-file shapes that the new policies supersede are all stale-sweep targets.
- **This repo is read-only.** Never write to this repository during `/teach`. The starter learns via `/learn`, not as a side effect of `/teach`.
- **Generality first.** Default to Tier 1+2 transfers. Specialize only when those are exhausted or the user's `<desc>` requested it.
- **Approval is mandatory.** No bytes change in the target before explicit approval.
- **Target preservations are inviolate.** A custom skill, agent, brief, or policy that exists only in the target stays. The plan's "Target preservations" section is enumerated; the apply step honors it.
- **Cross-harness parity carries to the target.** Any agent or skill transfer updates both surfaces in the target's tree.
- **Adapt to the target's language.** Build-gate commands, language metadata, surface names — all get rewritten to the target's stack before the apply finishes.
- **Catalog drift is forbidden.** Target's `CLAUDE.md` catalogs reflect every file in the target's `briefs/` and `policies/` after apply.
- **One LOG entry per `/teach` run.** Aggregate, in the target's `LOG.md`. This repo's `LOG.md` is not touched.
- **Refuse on active-phase conflicts.** If a proposed change touches a file the target's plan marks `🚧`, drop it from the apply set and report it as a manual follow-up the target's owner should resolve via `/kickoff` first.
- **`/starter` and the starter template's `example/` are never taught.** They live only in the starter template. The corresponding `.codex/prompts/starter.md` and `.agents/skills/starter` mirrors are also starter-only — if a target somehow acquired `.agents/skills/starter` (e.g., from a buggy Codex import), remove it as part of the apply. `/learn` and `/teach` are universal and may be transferred to a target that lacks them, with the user's approval.
