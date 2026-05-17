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

- **Verbatim** — copy from this starter into the target with name substitution (`Agentic Coding Starter Template` → target project name). Example: a policy file the target lacks.
- **Shape-only** — bring the structure but write project-specific content. Example: `briefs/BRIEF.md` shape with the target's actual thesis (rare in `/teach`; `/starter` already does this for new projects).
- **Update-in-place** — the target has an older or diverged version of a file this starter ships; bring it up to current. Example: an evolved policy whose latest version supersedes the target's copy.
- **Inspiration** — surface in the plan as a written suggestion, not a file change. Example: a brief topic the target should consider authoring.
- **Out of scope** — donor-specific (starter-specific meta-skills like `/learn`, `/teach`, `/starter` itself, and the template's `example/` Python project). Do not transfer.
- **Conflicts** — would override target customizations; surfaces a choice for the user.

### Generality tier

Same tiers as `/learn`:

- **Tier 1 — Methodology-level.** The four canonical agents, the orchestrator skill, the briefs/policies/plan triplet, the LOG.md contract.
- **Tier 2 — Universal template content.** Every file under `policies/`, `methodology.md`, `agentic-bootstrap.md`, the `AGENTS.md` symlink convention.
- **Tier 3 — Language/platform specializations.** Build-gate command lists for the target's language.
- **Tier 4 — Domain specializations.** Only if a domain-specific extension lives in this starter (uncommon; this template aims to stay general).

### Selection rule

Same as `/learn`:

- **No `<desc>` given**: select from Tier 1, then Tier 2. Only offer Tier 3 if those have less than three actionable items.
- **`<desc>` given**: use it to narrow.

### Critical "do not stomp" rules during assessment

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

## Conflicts requiring user decision

- `<target file>`: target's version <describes-the-divergence>. Options:
  - **Keep target's.** (default-safe)
  - **Replace with this starter's.**
  - **Merge** (skill produces a unified version preserving both).

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
3. Resolve cross-harness parity in the target:
   - If a `.claude/agents/<role>.md` is added or its body changed, add or refresh the matching `.codex/agents/<role>.toml` in the target.
   - If a `.claude/skills/<name>/SKILL.md` is added, add the matching `.codex/prompts/<name>.md` pointer wrapper in the target.
4. Update the target's `CLAUDE.md` catalogs (briefs catalog, policies catalog) so every new file is indexed.
5. Substitute names in transferred files: `Agentic Coding Starter Template` → target's project name; `agentic-coding-starter-template` → target's slug; references to this template's `example/` package → target's primary surface.
6. **Adapt build-gate commands** in the target's `.claude/skills/kickoff/SKILL.md` (and the four canonical agents) to the target's primary language, replacing this template's Python defaults wherever they leaked through verbatim transfers.
7. Run the target's own build gates (whatever the target's `pyproject.toml` / `package.json` / `Cargo.toml` declares) to confirm nothing regressed. If the target has no gates yet, skip — but flag in the report.
8. Append the TAUGHT FROM TEMPLATE entry to the target's `LOG.md` (create the file with the standard header if it doesn't exist).

**Do not auto-commit in the target.** The target's owner owns commits. Report the file list, build-gate status, and any unresolved manual steps.

**Do not write anything to *this* repo.** This skill is read-only against the starter. If the user wants to capture a learning here as a result of the teaching exchange, that's a separate `/learn` invocation against the target afterward.

## Rules

- **This repo is read-only.** Never write to this repository during `/teach`. The starter learns via `/learn`, not as a side effect of `/teach`.
- **Generality first.** Default to Tier 1+2 transfers. Specialize only when those are exhausted or the user's `<desc>` requested it.
- **Approval is mandatory.** No bytes change in the target before explicit approval.
- **Target preservations are inviolate.** A custom skill, agent, brief, or policy that exists only in the target stays. The plan's "Target preservations" section is enumerated; the apply step honors it.
- **Cross-harness parity carries to the target.** Any agent or skill transfer updates both surfaces in the target's tree.
- **Adapt to the target's language.** Build-gate commands, language metadata, surface names — all get rewritten to the target's stack before the apply finishes.
- **Catalog drift is forbidden.** Target's `CLAUDE.md` catalogs reflect every file in the target's `briefs/` and `policies/` after apply.
- **One LOG entry per `/teach` run.** Aggregate, in the target's `LOG.md`. This repo's `LOG.md` is not touched.
- **Refuse on active-phase conflicts.** If a proposed change touches a file the target's plan marks `🚧`, drop it from the apply set and report it as a manual follow-up the target's owner should resolve via `/kickoff` first.
- **`/starter` and the starter template's `example/` are never taught.** They live only in the starter template. `/learn` and `/teach` are universal and may be transferred to a target that lacks them, with the user's approval.
