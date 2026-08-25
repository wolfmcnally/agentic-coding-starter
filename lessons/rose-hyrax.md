---
slug: rose-hyrax
title: Moving an artifact root silently changes the environmental properties its old location supplied for free
status: candidate
scope: methodology
proposed_surface: invariant
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-20
    ref: "Donor A — a 1.7 GB evidence tree written inside a cloud-synced working copy carried none of the exclusion attributes that would keep it out of sync. The sync client burned a full core on the churn; the repo's own store code enforces exactly that discipline, and the phase's own evidence root violated it"
  - date: 2026-08-20
    ref: "Donor A — same incident, the cause: earlier runs assembled the same artifacts under system temp directories, unsynced BY NATURE. The gap appeared when the root moved into the working copy, and nothing about that move announced that the artifact's sync posture had changed. Detected by the operator noticing his fan, not by any check"
---

An artifact root inherits properties from where it lives: whether it is synced,
backed up, indexed, ignored, or reachable. Those properties are **invisible while
they hold**, because nothing reports a property you are getting for free.
Relocate the root and they vanish silently — no check fires, because no check was
ever written for a guarantee the filesystem was providing.

Two rules:

1. **Any code that creates a root inside a potentially synced tree applies the
   exclusion attributes at creation** — the from-birth discipline, extended to
   evidence assemblies and generated output, not only to the stores that already
   have it.
2. **A relocation of any artifact root asks what environmental properties the old
   location was supplying**, and states which of them the new location must now
   supply explicitly.

Note the readback limit, which belongs beside the check: setting the attributes
proves local policy state, **not** that the sync client has honored it remotely.

Directly live in this repo. This working copy sits inside a cloud-synced
directory, and `.kickoff/` run directories, gate logs, and receipts are generated
here every phase. It is also the environmental half of the existing invariant
that verification captures go to a scratch path rather than a bare filename
([`CLAUDE.md`](../CLAUDE.md)): that rule protects the *candidate id* from stray
files; this one protects the *machine* from artifacts the tree was never meant to
carry.
