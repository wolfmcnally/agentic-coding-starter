---
slug: pragmatic-baboon
title: A catch-up that both retires and admits proofs cannot follow the prescribed order
status: candidate
scope: methodology
proposed_surface: bin
filed: '2026-11-12'
source: user
occurrences:
- date: '2026-11-11'
  ref: a recipient catching up eleven releases — the one-step admission could not record the retirements the releases required, and the authoring command refused while proofs awaited admission; the worker authored the retirements on a copy of the base commit and carried the ledger rows over
- date: '2026-11-12'
  ref: a recipient migrating from the earlier layout — publishing only the retirements was refused while arriving proofs were unadmitted, and one-step admission was refused while the retirements were unpublished; the worker witnessed each proof with the older witness commands and published everything in one authoring call
- date: '2026-11-12'
  ref: a second recipient migrating the same day — the validator refused any retirement while arriving proofs existed on disk; the worker recorded the retirements in a scratch tree whose inventory was the old estate minus the retired proofs and carried the rows in
---

Three transfers hit the same wall and each found a different way round it. The one-step admission should accept retirement records in the same batch, or the tools should allow retirements to be published while arrivals await admission. Until then the transfer skill should name one sanctioned route, so workers stop inventing their own.
