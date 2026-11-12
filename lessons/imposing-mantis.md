---
title: A serial test run can still race a cold script environment
scope: methodology
proposed_surface: test
source: teach
slug: imposing-mantis
status: candidate
filed: '2026-11-12'
occurrences:
- date: '2026-11-12'
  ref: a recipient's 1.6.0 transfer; a serial focused run of the unchanged evidence
    test file failed one case whose two concurrent calls of the pinned tool raced
    the first build of its script environment, then passed in the parallel run
---

Release 1.5.0 builds script tool environments before parallel workers start, and 1.5.1 lets a worker with a private cache do the same. Neither runs for a serial invocation. A test that itself starts two concurrent calls of a script tool can therefore still meet a cold environment and fail on a half-installed import.

Observed once; the mechanism is inferred from the import error and the install notice in the failing call's output. Two candidate corrections: prepare script environments for serial runs as well, or have the test warm the pinned tool once before its concurrent calls. Check whether other tests start concurrent tool calls before choosing.