---
slug: lovely-mastodon
title: Proving a program resolves by executing it makes the verification a side-effect engine
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — an entrypoint-resolution sweep ran every bin/ executable argless from a fresh worktree; one entrypoint's argless form is its 'provision everything' form, so the test suite re-downloaded private content the repository's own firewall policy keeps out of engine-visible trees, three times over"
---

A hostile sweep enumerated every Python executable in `bin/` and ran each
argless to prove it resolves the managed interpreter rather than an ambient
one — a good, fail-closed check the donor was right to build. It proves it
*by running them*. Proving a program starts correctly by starting it executes
whatever that program does; one entrypoint's documented argless behavior was
"provision every missing item, from the network."

**Why this is firewall-class.** A containment boundary that was understood to
hold by *absence* does not hold at all when a supported command recreates the
thing. And the sweep fired only in fresh worktrees (a populated tree makes
provisioning a no-op), so it was invisible in ordinary runs.

**The dangerous ingredient is three legs, each harmless alone:** discovery +
execution + captured output. Enumeration lets blast radius grow silently every
time `bin/` grows; execution has real effects; capture swallows the evidence.

**Acceptance bar: safe-by-construction, not safe-by-attention.** The reference
shape: an explicit hardcoded allowlist (no globbing, so blast radius cannot
grow on its own); entrypoints copied into an isolated fixture root with
synthetic inputs and cwd inside it, never the live checkout; and side-effect
carriers stubbed on PATH with assertions against a call log.

**Rule:** before proving a property of a program by executing it, ask what
that execution *does*. A probe must reach the property and stop short of the
behavior. Where it cannot, the program is not probeable by execution and needs
a different proof.
