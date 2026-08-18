---
slug: delightful-whale
title: After adapting imported prose, sweep the destination for donor-domain vocabulary
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-17
    ref: "LEARN apply — this repo's orchestration-evidence policy still said ignored runtime state excluded 'standalone book checkouts' and 'nested engine repositories' from 'the engine candidate': donor-domain vocabulary left behind by an earlier wholesale port, describing surfaces this repository does not have"
---

A wholesale or near-wholesale prose import carries the donor's domain
vocabulary with it, and adaptation passes reliably catch the load-bearing
parts (paths, tool names, commands) while missing the descriptive prose —
which then tells the destination's readers about surfaces that do not exist
here. In a public template the residue is worse than confusing: it is a
provenance leak in slow motion, naming another project's internal domain in a
committed file.

The remedy is mechanical and cheap: after adapting an imported file, grep it
for the donor's domain nouns (the words the donor's CLAUDE.md glossary owns
and this repo's does not) before declaring the adaptation complete. The
anonymization checker cannot do this — it hunts identifiers and SHAs, not
ordinary words like a donor's product-domain vocabulary — so the sweep is the
importing agent's job, per file, at adaptation time.
