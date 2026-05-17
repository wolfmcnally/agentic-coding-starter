# Policy: Repo-Relative Paths Only

Every path embedded in a committed file is **repo-relative**. Absolute paths (`/Users/...`, `/home/...`, `C:\Users\...`) never appear in committed files.

## What this rule covers

- Source code that names file paths.
- Configuration files (`pyproject.toml`, `package.json`, `tsconfig.json`, etc.).
- Markdown documents (briefs, policies, plan files, README, CLAUDE.md, LOG.md, etc.).
- Sample data, fixtures, test inputs.
- Test scripts and shell scripts checked into the repo.

## What this rule does *not* cover

- Shell command invocations from a session (`Bash` tool calls) may use absolute paths. The agent's working directory is conventional but the agent host may pass absolute paths internally.
- The output of tools that emit absolute paths into a transient log or scratch file is fine if the scratch file is gitignored or ephemeral.
- Symlink targets in `.gitignore`d state directories are not subject to this rule.

## Why this rule exists

- **Portability.** The repo must build on a fresh clone in any user's home directory.
- **Auditability.** Absolute paths leak information about the original author's environment. For projects that may be distributed, that is a privacy and security concern.
- **Tooling.** Most lint and grep workflows operate on relative paths. Absolute paths fail those workflows silently.

## Common offenders to watch for

- A test fixture that imports `/Users/<name>/projects/<repo>/data/sample.csv` instead of `data/sample.csv` (or a path computed from the test file's location).
- A pasted example from an interactive session that includes the original session's CWD.
- A README quickstart that says `cd /Users/me/myrepo`. Use `<your-clone>/` or just omit the prefix.
- A markdown file referencing `/Users/.../briefs/foo.md` instead of `briefs/foo.md` (or `../briefs/foo.md` from a sub-directory).

## Verification

A quick sweep, runnable from the repo root:

```bash
# Find absolute Unix-style paths in committed text files (excluding state dirs)
grep -RIn '/Users/\|/home/\|/var/\|/etc/' \
  --include='*.md' --include='*.py' --include='*.toml' \
  --include='*.json' --include='*.yaml' --include='*.yml' \
  --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules \
  . | grep -v '^.claude/scheduled_tasks.lock' || echo "no absolute paths found"
```

A clean repo prints `no absolute paths found`.

## Exception: documented scratch roots

A project may declare a documented scratch root (e.g., `/tmp/<project-name>/auditions/`) for ephemeral artifacts. References to that root in committed files are allowed *only* when:

- The scratch root is documented in `CLAUDE.md`'s conventions section.
- Nothing under the scratch root is ever committed.
- The path is conventional (not user-specific): `/tmp/<project-name>/...` is acceptable; `/Users/<name>/scratch/...` is not.

## Adjacent rule: tilde-expanded paths

`~/path/to/something` is technically relative (to the user's home), but it has the same portability problems as an absolute path: the agent's home directory is not the user's home directory. Treat `~` paths as absolute for this policy's purposes — keep them out of committed files unless they refer to a conventional location (`~/.config/<project>/`) documented in the project's conventions.
