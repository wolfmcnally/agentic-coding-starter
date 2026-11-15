---
title: A release's transfer list omitted two changed methodology briefs and nothing
  compared the list with the release's own changes
scope: methodology
proposed_surface: bin
source: teach
slug: humongous-bandicoot
status: candidate
filed: '2026-11-14'
occurrences:
- date: '2026-11-14'
  ref: release 1.7.0; the open-source releases brief and the transfer management brief
    both changed between the two tags and neither appears in the release entry's transfer
    list; three recipients were upgraded without them before a fourth recipient's worker
    noticed one and asked
---

The release entry's transfer list is what a transfer worker treats as scope, and the hub's worker brief repeats it. For 1.7.0 the list was written by hand from the capabilities and left out two briefs that the methodology contract catalogs and that the release changed. One of them now trails the policy sentence that was transferred, so each upgraded recipient carries a policy that says more than its own brief. Authority direction keeps that harmless, since the policy prevails, but the recipients differ from the template in a file a later transfer will have to reconcile.

Nothing executable compares the list with the difference between the two tags. The hub wrote the list and also wrote the brief from it, so the same omission passed through both.

Candidate correction: a release check that takes every path changed between the previous tag and the candidate, removes the paths the release policy says never transfer, and refuses the release unless each remaining path is named in the transfer list or in an explicit not-transferred note. Until then, the next release carries both briefs, and a worker brief gives the tag-to-tag file list as the scope rather than a summary of it.
