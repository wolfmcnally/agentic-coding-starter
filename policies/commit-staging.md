# Policy: Commit Staging Integrity

Authority mode follows [four-canonical-agents.md](four-canonical-agents.md). Product primary mode uses independent advice and primary acceptance; delegated product mode retains approval verdicts and bounded revision loops. References below to reviewer assent or mandatory re-review govern delegated work only. Required objective gates and truthful evidence apply in both modes. All methodology work, including teach/learn, follows [review-lanes.md](review-lanes.md): one-shot by the primary, no delegated production or review, and commit/fast-forward-push authority after required checks.

A staging list is a set of assertions about the repository. Re-verify every
assertion against the tree as it exists at staging time, not as it existed when
the list was composed.

## The rule

1. **Re-check the tree immediately before every commit.** Run
   `git status --porcelain` and read every row. Unexpected `R`, `M`, `A`, or
   `??` entries—and expected entries that are absent—are failures. A path list
   composed earlier in the session is stale by default.
2. **Stage explicit paths.** Never use `git add -A` or `git add .` in a checkout
   another session may share.
3. **Treat explicit paths as necessary, not sufficient.** They have two known
   blind spots:
   - **Shared file.** When two sessions edit one file, staging that path carries
     both sessions' hunks. Partition the file's hunks and identify their owners
     before committing; if that cannot be established safely, park delivery.
   - **Moved path.** A rename or archive move invalidates a path list that names
     the source. Stage and verify the destination path so later content edits
     are not silently omitted. `git add` is **atomic over its pathspec list**:
     one path that matches nothing aborts the whole invocation and stages none
     of the others, so a single stale entry silently leaves every intended file
     unstaged. `git mv` and `git rm` stage their own halves; re-naming them in a
     later `git add` is what triggers the abort. Verify staging by the index —
     `git diff --cached --name-only` — never by the `git status` file list,
     which prints a path whether it is staged or not. **A name is still not
     content.** When `git mv` staged a rename and the moved file was edited
     afterward, the path appears in `--name-only` while the index holds the
     pre-edit bytes; only `git diff --cached --stat` or the staged diff itself
     distinguishes them, which is why rule 4's read is not optional. A commit
     that ships a rename without its content is the silent direction of this
     defect: it succeeds, its file list matches the intent exactly, and the
     working tree keeps the edits that never left it. *(Graduated from
     `puzzling-unicorn`, 3 occurrences — `lessons-archived/puzzling-unicorn.md`;
     the name-is-not-content clause added the same day, after it recurred.)*
4. **Inspect the staged candidate and the resulting commit.** Read the staged
   diff before committing. Afterward, compare `git show --stat --oneline HEAD`
   with the intended file list. A successful exit proves that Git created a
   commit, not that the commit contains what was intended.
5. **Verify before the push, in its own block.** The post-commit checks —
   `git show --stat`, a clean `git status`, residual-dirt inspection — decide
   whether the commit is fit to publish, so chaining them behind the push in one
   command block runs them after the irreversible step and turns a catchable
   mistake into a published one. Residual modification on a path the commit just
   claimed means the commit is short. This is the delivery case of the rule that
   a command whose refusal or result must be read gets its own block
   (`verification-discipline.md`).

## Corollaries

- A preservation hold is not self-enforcing. Re-check live tree identity before
  acting on an earlier snapshot.
- Moving or deleting a required contract member updates every independent
  inventory that names it, in the same change.
- If a staging defect reaches history, fix forward with an ordinary commit.
  History rewriting remains on the destructive Git surface owned by the user.

Delivery authority and its park conditions remain governed by
[`human-in-the-loop.md`](human-in-the-loop.md). This policy governs the
integrity of any commit that authority permits.
