---
slug: crimson-shrew
title: Link checkers that validate paths but not fragments let dead anchors live indefinitely
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-08-25
source: sweep
occurrences:
  - date: 2026-08-25
    ref: "sweep (briefs only) — user-actions-archived/perfect-sloth.md finding A1"
  - date: 2026-08-25
    ref: "citation-direction + fragment enforcement — policies/user-demo-protocols.md linked human-in-the-loop.md#exception-clause after that section was renamed Restriction clause"
---

`bin/check-catalogs` verifies that every tracked internal link resolves to a
file that exists. It does not verify the `#fragment` half of a link against the
target file's headings. A link can therefore be simultaneously green and dead.

The live instance: `briefs/BRIEF.md` pointed readers at
`../CLAUDE.md#briefs-catalog` for the index of sibling briefs. `CLAUDE.md`
exists, so the checker passed it on every run. But `CLAUDE.md` has no "Briefs
catalog" heading — the index is split across `## Project briefs` and
`## Methodology briefs` — so the anchor had been silently landing readers at the
top of the file. Every reference in the repo to that catalog was one link, and
the one link was broken.

The shape generalizes past this checker: **a validator that checks the cheap
half of a compound reference reports on the half it checked, in language that
sounds like it covered the whole thing.** "Link integrity: OK" is read as "the
links work," not as "the paths resolve." That gap is invisible precisely because
the check is green.

Why this is a `bin` candidate rather than a prose rule: fragment resolution is
mechanically decidable. Markdown heading anchors are derived from heading text
by a known slug transform, so a checker can enumerate every `](...#frag)` in a
tracked file, resolve the target, slugify its headings, and refuse an
unmatched fragment. That is exactly the mechanistic half of
[`policies/mechanistic-vs-intelligence.md`](../policies/mechanistic-vs-intelligence.md)
— no judgment involved, and a written reminder to "check your anchors" would be
a rule wired to nothing.

Counting note: two occurrences. The first was filed rather than graduated
because a single instance cannot say whether anchors are a recurring defect
here or a one-off. The second arrived the same day, from the other direction:
building the fragment check surfaced a *second* dead anchor nobody had looked
for — `policies/user-demo-protocols.md` pointed at
`human-in-the-loop.md#exception-clause` long after that section was renamed
**Restriction clause**. Two of the repo's four fragment links were dead. The
weak-evidence caveat in the first row is therefore answered: fragments rot
whenever a heading is renamed, and nothing was watching.

Status note (2026-08-25): the `bin` guard this lesson proposed now exists —
`bin/check-catalogs` derives each Markdown document's anchor set from its
headings and refuses an unmatched fragment, and both dead anchors above were
caught by it rather than by reading. Whether that closes the lesson is the
operator's call; this entry stays open until they make it.
