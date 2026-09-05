# Policy: Cross-Harness Parity

This repo's agent surfaces (skills, agent definitions, top-level instructions) must work identically whether the user runs Claude Code, Codex CLI, or any other supported agent host. Drift between harnesses is the failure mode this policy exists to prevent.

## Principle

Every cross-harness capability has **one canonical source** and **N harness-specific wrappers**. A change to a capability touches all wrappers in the same commit. `bin/check-harness-parity` detects drift deterministically in the full policy gate and the opt-in pre-commit hook.

## Cross-harness surfaces

| Surface | Canonical source | Harness mirrors |
|---|---|---|
| Project instructions | `CLAUDE.md` | `AGENTS.md` → symlink to `CLAUDE.md` |
| Skills | `.claude/skills/<name>/` (skill directory) | `.agents/skills/<name>` → **directory** symlink to `../../.claude/skills/<name>` |
| Agent roles | `.claude/agents/<role>.md` | `.codex/agents/<role>.toml` (thin wrapper TOML — symlink not possible because formats differ) |
| Static context (briefs, policies, plan) | The files themselves | (none — both harnesses read the same files directly) |

Surface choice is dictated by harness mechanics, and **the canonical form for each surface is the most drift-proof shape the formats permit**:

- **Symlinked** whenever both harnesses accept the same file format. The mirror is a real filesystem symlink to the canonical, intra-repo, using a relative path. Symlinks cannot drift; there is nothing to maintain.
- **Wrapped** only when formats genuinely differ (agent roles — Claude Code wants Markdown with YAML frontmatter, Codex wants TOML). The wrapper is a real file in the mirror's native format, kept as thin as possible — typically a `description` field and a `developer_instructions` body that just says *"Read the canonical .md and follow it."* Wrappers carry the format-specific shell so the harness's parser stays happy; they should never carry an inline copy of the instruction body.
- **Shared verbatim** when the file is content rather than instruction (briefs, policies, plan files). Both harnesses read the same files directly.

The default is symlink. Drop to wrapper only when the symlink would feed the mirror's parser a file format it cannot read.

This shape follows the harnesses' discovery contracts: Claude Code reads `CLAUDE.md`, `.claude/skills/`, and `.claude/agents/`; Codex reads `AGENTS.md`, `.codex/agents/` (agent definitions), and `.agents/skills/` (native project-skill discovery, per [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)). Repo-level Codex skills are invoked with `$name` (or selected through `/skills`), not `/name`. Deprecated custom prompts live only under the user's `~/.codex/prompts/` and are not a repo-level mirror surface.

## Skill invocation syntax

- **Claude Code:** `/name [arguments]`
- **Codex:** `$name [arguments]`

Committed documentation must use the bare skill name in harness-neutral prose (for example, "the `kickoff` skill") and show both forms whenever it gives an invocation the user should type. Never present `/name` as a universal command.

**Important: `.agents/skills/` uses *directory*-level symlinks, not file-level ones.** Codex's native skill loader does not follow symlinks for files inside a skill directory (see [openai/codex#11314](https://github.com/openai/codex/issues/11314)). It does follow a symlinked skill *directory*. So `.agents/skills/<name>` is a symlink whose target is the canonical skill directory `../../.claude/skills/<name>` — Codex then sees `SKILL.md` and any sidecar files as if they lived inside `.agents/skills/<name>` directly. Empirically validated in a sibling project of the author's (its "Restore Codex skill discovery" change).

## Rules

1. **Edit canonical files only.**
   - Top-level instruction changes go in `CLAUDE.md`.
   - Skill changes go in `.claude/skills/<name>/SKILL.md` and its canonical adjacent resources.
   - Agent role body changes go in `.claude/agents/<role>.md`.
   - Never edit `AGENTS.md`, the contents of any `.agents/skills/<name>/` (those files live in the canonical `.claude/skills/<name>/` and are reached through a directory symlink), or any `.codex/agents/<role>.toml` body directly without making the corresponding canonical change in the same commit.

2. **Keep compatibility paths as symlinks where possible.**
   - `AGENTS.md` is a symlink to `CLAUDE.md`. Verify with `readlink AGENTS.md`.
   - If a harness can follow symlinks for skill directories, prefer that to maintaining a separate mirror.

3. **Codex agent wrappers mirror Claude Code agent definitions.**
   - A `.codex/agents/<role>.toml` file's `developer_instructions` field is a thin exact pointer telling the role to read `.claude/agents/<role>.md`; it never duplicates the Markdown body.
   - The TOML `description` field mirrors the Markdown `description:` frontmatter field.
   - Update both in the same commit.

4. **Codex skill mirrors are directory symlinks to canonical skill content.**
   - `.agents/skills/<name>` is a *directory* symlink whose target is `../../.claude/skills/<name>` (the canonical skill directory, not the SKILL.md file inside it). Verify with `readlink .agents/skills/<name>` and `test -L .agents/skills/<name> && test -d .agents/skills/<name>`. Codex's native skill loader does **not** follow file-level symlinks inside a skill directory (#11314), but does traverse a symlinked skill directory — so the directory-level shape is the only one that works for this surface.
   - All symlinks because formats match (all Markdown with the same SKILL.md schema). Pointer-file wrappers ("Read X and follow it") and inline duplication of the body are both deprecated — replace them with symlinks on sight.
   - Never write Codex-specific behavior into any file under `.agents/skills/<name>/` that the canonical skill doesn't also describe. (With a symlink in place this is impossible anyway, which is the point.)
   - Template-only skills such as `stamp` are mirrored in this starter repo because the template itself must expose them in every supported harness. `stamp` is omitted only when stamping ordinary derived projects, unless the destination is explicitly intended to be a template too.

5. **No harness-specific rewrites in mirrored content.**
   - Write canonical skill and agent instructions in harness-neutral terms where practical. Reference tools by their canonical Claude Code name (e.g., "Read", "Edit", "Grep") and trust the Codex equivalent to be obvious; or reference both surfaces explicitly when ambiguity matters.
   - Do not maintain a Codex-specific copy with substituted `.codex/` paths. That is the drift failure this policy forbids.

6. **Briefs, policies, and plan files are not duplicated.**
   - Both harnesses read the same files. There is no `.codex/briefs/` mirror; both `claude` and `codex` invocations read `briefs/`, `policies/`, and `plan/` directly.

## Instruction delivery

`CLAUDE.md` must not exceed 16384 UTF-8 bytes and `.claude/skills/kickoff/SKILL.md` must not exceed 8192 UTF-8 bytes. Preserve the root hard-rule clauses and restriction/waiver paragraph, essential invariants, complete concise brief/policy/skill/role catalogs, reading order and toolchain/delivery boundaries. Its four zone markers occur exactly once in order: `PROJECT_CONTEXT_START`, `PROJECT_CONTEXT_END`, `METHODOLOGY_CONTRACT_START`, `METHODOLOGY_CONTRACT_END`, each in an HTML comment. Remove repetition before moving extended explanations to existing canonical owners; a byte ceiling never authorizes deleting an obligation.

The kickoff entry directly links all seven adjacent resources and explicitly orders reading each before executing its branch:

| Resource | Read before |
|---|---|
| `preflight.md` | phase selection, lane decisions, startup and evidence initialization |
| `dispatch.md` | every role registration or invocation |
| `planning.md` | planning and independent plan review |
| `implementation.md` | coding and independent code review |
| `acceptance.md` | acceptance, implementation-candidate gate and accepted major close |
| `close.md` | preparing END, status/ripple/lessons/report bookkeeping, handoff gate and delivery |
| `recovery.md` | operator decisions, refusals, recovery, continuity and follow-ups |

A skill discovery event, root injection, canonical role retrieval and stage-resource retrieval are distinct. A link supplies navigation, not proof of retrieval. Every branch, including recovery and follow-up paths, must explicitly load its directly linked resource before execution. Generated research directives, access controls, schemas and invocation settings retain their executable owners; do not recreate them from memory or add a loader, router or automatic permission change.

`stamp`, `learn` and `teach` transfer the complete canonical kickoff directory and its directory symlink, preserving resource-relative link depth and updating actual consumers of moved sections. Codex role wrappers remain thin; directory symlinks already expose the resources.

The existing catalog checker owns structural enforcement of byte ceilings, unique ordered markers, required resources, direct live links and explicit load-before-use entries. Structural verification measures file budgets, reachability and instruction form; it cannot prove that a model read or followed the content. Qualify its proxies with missing, oversized, broken-link and malformed-entry controls and review their meaning independently. Dated harness facts and evidence limits live in [the context brief](../briefs/session-context-compaction.md).

## Editorial parity

Structural parity — every mirror present, symlinked, and pointing at the canonical file — is necessary but not sufficient. **Structural parity without editorial parity ships matched skeletons that produce mismatched output**: both harnesses read the same instruction text, yet make different operational decisions wherever that text leaves judgment underdetermined. Three authoring failure modes cause this, and any instruction surface both harnesses execute (skills, agent definitions, orchestration steps) is written to avoid them:

- **Impressionistic standards.** "Keep it concise", "use good judgment", "when appropriate" — each harness's model resolves the impression differently. Replace with a decidable criterion or an explicit example of each side of the line.
- **Advisory bands.** Ranges offered without a selection rule ("2–4 subagents", "roughly 100–200 lines") make the choice harness-dependent. State the default and the condition that moves off it.
- **Missing compare-against.** An instruction to improve, shorten, or align something without naming the reference it is measured against lets each harness pick its own baseline. Name the comparand explicitly.

The stability test is the **two-harness exercise**: run the same instruction surface under both harnesses on the same inputs and diff the operational decisions — not the prose style. A surface whose two runs diverge on a decision that matters has an editorial-parity defect in one of the three forms above; fix the instruction text at the canonical source, not the harness. Apply the exercise when authoring a new orchestration-bearing surface, and when a cross-harness behavioral difference is reported against an existing one.

## Onboarding a new harness

When this template adopts a third harness (e.g., aider, OpenHands, Cursor, Continue):

1. **Declare the canonical-source convention** for the new harness here. Add a row to the surfaces table.
2. **Choose wrapper directory naming.** Use the pattern `.<harness-name>/` (mirroring `.claude/`, `.codex/`). Skills go under `.<harness-name>/skills/` or wherever the harness scans; agents go under `.<harness-name>/agents/`.
3. **Decide which mirror surfaces are needed.** Top-level instructions usually need only a symlink (most harnesses read `AGENTS.md` or one of several common files). Agent definitions usually need a real wrapper file in the harness's preferred format.
4. **Audit existing surfaces for divergence** by reading each canonical file and its mirrors side by side. Resolve any drift before the new harness goes live.

## Repair procedure

When you discover drift between a canonical file and a mirror:

1. Identify which file is canonical. (Hint: `.claude/` for agent definitions; the repo root `CLAUDE.md` for top-level instructions.)
2. Apply the fix at the canonical level.
3. Re-generate (or hand-update) each mirror to match.
4. Commit the repair with a message that names the surface that was out of parity and what the fix was.

## Verification

Run the deterministic checker from any directory:

```bash
./bin/check-harness-parity
```

It fails on a copied or misdirected `AGENTS.md`, missing/orphan/wrong-target skill symlinks, missing/orphan agent wrappers, mismatched names or descriptions, and wrappers without the exact canonical pointer. `./bin/check policy` and the opt-in pre-commit hook invoke it automatically.
