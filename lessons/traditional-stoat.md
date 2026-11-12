---
title: A clean merge can miss a recipient-only call of a function whose signature
  the release extended
scope: methodology
proposed_surface: skill
source: teach
slug: traditional-stoat
status: candidate
filed: '2026-11-12'
occurrences:
- date: '2026-11-12'
  ref: a recipient's 1.6.0 transfer; the release gave a validation function an optional
    third parameter, and the one call that existed only in the recipient kept two
    arguments with no conflict, a clean two-way line audit and no failing test, until
    the coordinator's approval condition asked for every call site to be listed
---

The two-way line audit proves no recipient line was dropped and no donor line was missed. It cannot see a recipient-own line that needed to change because the code around it changed meaning. An optional parameter makes this silent: the old call still runs and quietly takes the default.

Candidate correction for the teach skill and the release notes: when a release changes a function's signature or adds a parameter, name the function in the release's transfer notes, and have the recipient list every call site, own lines included, before calling a merge complete. Where a recipient call validates a record from another run, the new argument must come from that other run. A recipient reported its own cross-run carry of never-launched attempts as a reverse-direction learn candidate; a proof that an owner-directed attempt survives that carry belongs with it.