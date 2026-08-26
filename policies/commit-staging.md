# Policy: Commit Staging Integrity

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
     are not silently omitted.
4. **Inspect the staged candidate and the resulting commit.** Read the staged
   diff before committing. Afterward, compare `git show --stat --oneline HEAD`
   with the intended file list. A successful exit proves that Git created a
   commit, not that the commit contains what was intended.

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
