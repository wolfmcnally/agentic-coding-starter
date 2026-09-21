---
slug: fearless-nautilus
title: The accepted close can queue a next marker only where none exists, so it cannot move a stale one
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-09-20
source: learn
occurrences:
  - date: 2026-09-20
    ref: "Found while adding the child-close next-marker guard to bin/check-catalogs: _close_transition in bin/kickoff-evidence admits one ⏳→⬅️ change and rejects every other row edit, so the ⬅️→⏳ half of a move refuses and the prospective ledger cannot relocate the marker"
---

`_close_transition` binds the prospective ledger to a status-only diff: at most one ⏳→⬅️ queueing change, plus the 🚧→✅ completions it was authorized for. Any other changed row — including clearing the ⬅️ the marker is being moved *off* — fails as "close transition may change only the closing phase status". A close that inherits a marker sitting on an unrelated phase therefore has exactly two legal outcomes: leave it stranded, or add a second marker that `check_phase_ledger` then refuses for exceeding one.

That is the mechanism behind the donor's three consecutive closes recording that the marker "stays where the ledger already had it." The reasoning error was real, and the transition rule made the correct edit unrepresentable.

This matters now because the new guard in `bin/check-catalogs --closing-phase` refuses a stranded marker. On the direct close path the orchestrator edits `plan/INDEX.md` and can satisfy it. On the accepted prospective-ledger path it cannot, and `--next-marker-reason` is not plumbed through `kickoff-evidence`, so the refusal would park with no in-run remedy.

**The rule candidate:** admit one paired marker move in `_close_transition` — exactly one ⬅️→⏳ alongside exactly one ⏳→⬅️, leaving at most one marker in the result — and pass a close-supplied reason through to the catalog check for a deliberate queue outside the parent's subtree. Both touch the accepted-close binding, which is why this is filed for ratification rather than changed inside a learn.
