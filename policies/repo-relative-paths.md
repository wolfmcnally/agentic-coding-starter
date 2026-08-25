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
- Tilde-prefixed home-relative paths (`~/Library/Logs/...`, `~/.config/...`) in **operator-run commands** — demo protocols, hot-state checks, acceptance recipes the human pastes into their own shell. These are portable across users precisely because the shell expands `~` per operator; spelling them absolute would break that.

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

`bin/check-anonymization.sh` enforces this rule mechanically over every tracked
file, and `./bin/check all` runs it:

```bash
bin/check-anonymization.sh
```

Its first pass is this policy's check: it matches real `/Users/<user>/`,
`/home/<user>/`, `C:\Users\<user>\`, and home-relative forms, excludes the
placeholder spellings this policy itself recommends (`/Users/me/`, `<your-clone>/`),
and reports a hit against this policy by name.

**Do not hand-write a `grep` for this rule.** The token it would search for is the
token this policy, its catalog entry, the code critic's checklist, the sanitizer
that strips such paths, and the tests asserting their absence all legitimately
contain — so such a grep reports hits on a clean repository and can never print a
clean result. That is the detector defect
[`verification-discipline.md`](verification-discipline.md) § "A grep lead is not a
finding" names: never key a detector solely on a token the subject itself
legitimately emits. The checker's exclusion list is what makes the same question
answerable.

## Exception: documented scratch roots

A project may declare a documented scratch root (e.g., `/tmp/<project-name>/auditions/`) for ephemeral artifacts. References to that root in committed files are allowed *only* when:

- The scratch root is documented in `CLAUDE.md`'s conventions section.
- Nothing under the scratch root is ever committed.
- The path is conventional (not user-specific): `/tmp/<project-name>/...` is acceptable; `/Users/<name>/scratch/...` is not.

## Adjacent rule: tilde-expanded paths

`~/path/to/something` is technically relative (to the user's home), but it has the same portability problems as an absolute path: the agent's home directory is not the user's home directory. Treat `~` paths as absolute for this policy's purposes — keep them out of committed files unless they refer to a conventional location (`~/.config/<project>/`) documented in the project's conventions.
