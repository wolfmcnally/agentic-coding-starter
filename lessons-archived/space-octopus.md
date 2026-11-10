---
slug: space-octopus
title: Parallel test workers race the first build of a script tool's cached environment
status: codified
closed: '2026-11-10'
graduated_to: lib/agentic_starter/test_runner.py
scope: methodology
proposed_surface: bin
filed: '2026-11-10'
source: user
occurrences:
- date: '2026-11-10'
  ref: a recipient — its first full gate in its own checkout failed seven proofs when parallel workers started a tool whose dependency environment was being built for the first time; the unchanged tree passed on the next run
---

The supervised runner builds each script tool's environment once, serially, before starting workers.
