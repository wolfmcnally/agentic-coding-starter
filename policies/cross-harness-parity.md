# Policy: Cross-Harness Parity

This repo's agent surfaces (skills, agent definitions, top-level instructions) must work identically whether the user runs Claude Code, Codex CLI, or any other supported agent host. Drift between harnesses is the failure mode this policy exists to prevent.

## Principle

Every cross-harness capability has **one canonical source** and **N harness-specific wrappers**. A change to a capability touches all wrappers in the same commit. Drift is detected by inspection; it is repaired by editing the canonical source and refreshing the mirrors.

## Cross-harness surfaces

| Surface | Canonical source | Harness mirrors |
|---|---|---|
| Project instructions | `CLAUDE.md` | `AGENTS.md` (symlink → `CLAUDE.md`) |
| Skills (slash commands) | `.claude/skills/<name>/SKILL.md` | `.codex/prompts/<name>.md` (thin wrapper that points at the canonical instructions; or symlinked, depending on harness) |
| Agent roles | `.claude/agents/<role>.md` | `.codex/agents/<role>.toml` (TOML thin wrapper carrying identical `developer_instructions`) |
| Static context (briefs, policies, plan) | The files themselves | (none — both harnesses read the same files directly) |

Surface choice is dictated by harness mechanics:

- **Symlinked** when both harnesses accept the same file format (top-level instructions).
- **Wrapped** when formats genuinely differ (agent roles — Claude Code wants Markdown with YAML frontmatter, Codex wants TOML). Wrappers are independently maintained but carry the same instructional body so any inspection reveals divergence at a glance.
- **Shared verbatim** when the file is content rather than instruction (briefs, policies, plan files).

This shape follows the harnesses' discovery contracts: Claude Code reads `CLAUDE.md`, `.claude/skills/`, and `.claude/agents/`; Codex reads `AGENTS.md`, `.codex/prompts/`, and `.codex/agents/`.

## Rules

1. **Edit canonical files only.**
   - Top-level instruction changes go in `CLAUDE.md`.
   - Skill changes go in `.claude/skills/<name>/SKILL.md`.
   - Agent role body changes go in `.claude/agents/<role>.md`.
   - Never edit `AGENTS.md`, `.codex/prompts/<name>.md`, or any `.codex/agents/<role>.toml` body directly without making the corresponding canonical change in the same commit.

2. **Keep compatibility paths as symlinks where possible.**
   - `AGENTS.md` is a symlink to `CLAUDE.md`. Verify with `readlink AGENTS.md`.
   - If a harness can follow symlinks for skill directories, prefer that to maintaining a separate mirror.

3. **Codex agent wrappers mirror Claude Code agent definitions.**
   - A `.codex/agents/<role>.toml` file's `developer_instructions` field carries the same instructional body as `.claude/agents/<role>.md`'s post-frontmatter content.
   - The TOML `description` field mirrors the Markdown `description:` frontmatter field.
   - The TOML `tools` (when the harness honors it) mirrors the Markdown `tools:` frontmatter.
   - Update both in the same commit.

4. **Codex prompts are thin wrappers around canonical skill content.**
   - A `.codex/prompts/<name>.md` may point at `.claude/skills/<name>/SKILL.md` via a one-line directive ("Read `.claude/skills/<name>/SKILL.md` and follow it") or duplicate the body verbatim. The pointer form is preferred — it cannot drift.
   - Never write Codex-specific behavior into a `.codex/prompts/<name>.md` that the canonical SKILL doesn't also describe.

5. **No harness-specific rewrites in mirrored content.**
   - Write canonical skill and agent instructions in harness-neutral terms where practical. Reference tools by their canonical Claude Code name (e.g., "Read", "Edit", "Grep") and trust the Codex equivalent to be obvious; or reference both surfaces explicitly when ambiguity matters.
   - Do not maintain a Codex-specific copy with substituted `.codex/` paths. That is the drift failure this policy forbids.

6. **Briefs, policies, and plan files are not duplicated.**
   - Both harnesses read the same files. There is no `.codex/briefs/` mirror; both `claude` and `codex` invocations read `briefs/`, `policies/`, and `plan/` directly.

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

A quick manual sweep, runnable in any shell from the repo root:

```bash
# Symlink check
test -L AGENTS.md && [ "$(readlink AGENTS.md)" = "CLAUDE.md" ] && echo "AGENTS.md OK"

# Agent role parity: each .claude/agents/*.md has a .codex/agents/*.toml peer
for f in .claude/agents/*.md; do
  role=$(basename "$f" .md)
  [ -f ".codex/agents/${role}.toml" ] || echo "missing .codex/agents/${role}.toml"
done

# Prompt parity: each .claude/skills/*/SKILL.md has a .codex/prompts/*.md peer
for d in .claude/skills/*/; do
  skill=$(basename "$d")
  [ -f ".codex/prompts/${skill}.md" ] || echo "missing .codex/prompts/${skill}.md"
done
```

A clean repo prints `AGENTS.md OK` and nothing else.
