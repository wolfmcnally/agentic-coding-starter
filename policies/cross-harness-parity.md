# Policy: Cross-Harness Parity

This repo's agent surfaces (skills, agent definitions, top-level instructions) must work identically whether the user runs Claude Code, Codex CLI, or any other supported agent host. Drift between harnesses is the failure mode this policy exists to prevent.

## Principle

Every cross-harness capability has **one canonical source** and **N harness-specific wrappers**. A change to a capability touches all wrappers in the same commit. Drift is detected by inspection; it is repaired by editing the canonical source and refreshing the mirrors.

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
   - Skill changes go in `.claude/skills/<name>/SKILL.md`.
   - Agent role body changes go in `.claude/agents/<role>.md`.
   - Never edit `AGENTS.md`, the contents of any `.agents/skills/<name>/` (those files live in the canonical `.claude/skills/<name>/` and are reached through a directory symlink), or any `.codex/agents/<role>.toml` body directly without making the corresponding canonical change in the same commit.

2. **Keep compatibility paths as symlinks where possible.**
   - `AGENTS.md` is a symlink to `CLAUDE.md`. Verify with `readlink AGENTS.md`.
   - If a harness can follow symlinks for skill directories, prefer that to maintaining a separate mirror.

3. **Codex agent wrappers mirror Claude Code agent definitions.**
   - A `.codex/agents/<role>.toml` file's `developer_instructions` field carries the same instructional body as `.claude/agents/<role>.md`'s post-frontmatter content.
   - The TOML `description` field mirrors the Markdown `description:` frontmatter field.
   - The TOML `tools` (when the harness honors it) mirrors the Markdown `tools:` frontmatter.
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
# Top-level: AGENTS.md is a symlink to CLAUDE.md
test -L AGENTS.md && [ "$(readlink AGENTS.md)" = "CLAUDE.md" ] && echo "AGENTS.md OK"

# Codex native skills: each .agents/skills/<name> is a DIRECTORY symlink to ../../.claude/skills/<name>
for d in .claude/skills/*/; do
  skill=$(basename "$d")
  link=".agents/skills/${skill}"
  expected="../../.claude/skills/${skill}"
  if [ ! -L "$link" ]; then echo "not a symlink: $link"
  elif [ "$(readlink "$link")" != "$expected" ]; then echo "wrong target: $link → $(readlink "$link") (expected $expected)"
  elif [ ! -d "$link" ]; then echo "symlink does not resolve to a directory: $link"
  fi
done

# Agent roles: each .claude/agents/<role>.md has a .codex/agents/<role>.toml peer (thin wrapper, not symlink)
for f in .claude/agents/*.md; do
  role=$(basename "$f" .md)
  [ -f ".codex/agents/${role}.toml" ] || echo "missing .codex/agents/${role}.toml"
done
```

A clean repo prints `AGENTS.md OK` and nothing else.
